import React, { useEffect, useState, useRef, useCallback } from 'react';
import { useNavigate } from 'react-router-dom';
import ForceGraph2D from 'react-force-graph-2d';
import { Network, ZoomIn, ZoomOut, Maximize2, RefreshCw, AlertCircle, MapPin, ExternalLink, Info } from 'lucide-react';
import { fetchApi } from '../lib/api';
import { useAppStore } from '../store/useAppStore';

const EVENT_COLORS = {
  relocation:    '#6366f1', // indigo
  closure:       '#ef4444', // red
  expansion:     '#22c55e', // green
  new_plant:     '#3b82f6', // blue
  tender:        '#f59e0b', // amber
  layoff:        '#ec4899', // pink
  acquisition:   '#8b5cf6', // violet
  restructuring: '#f97316', // orange
  supply_chain:  '#14b8a6', // teal
  other:         '#64748b', // slate
};

const SIGNAL_COLORS = {
  positive: '#22c55e',
  negative: '#ef4444',
  neutral:  '#94a3b8',
};

function ScoreBadge({ score }) {
  const color =
    score >= 80 ? '#22c55e' :
    score >= 65 ? '#3b82f6' :
    score >= 50 ? '#f59e0b' : '#64748b';
  return (
    <span style={{ background: color + '22', color, border: `1px solid ${color}44` }}
      className="px-2 py-0.5 rounded-full text-xs font-bold">
      {score}
    </span>
  );
}

const EVENT_TYPE_TR = {
  relocation:    'Taşınma',
  closure:       'Kapanış',
  expansion:     'Genişleme',
  new_plant:     'Yeni Tesis',
  tender:        'İhale',
  layoff:        'İşten Çıkarma',
  acquisition:   'Satın Alma',
  restructuring: 'Yeniden Yapılanma',
  supply_chain:  'Tedarik Zinciri',
  other:         'Diğer',
};

const SIGNAL_COLORS_TR = {
  positive: 'Pozitif',
  negative: 'Negatif',
  neutral:  'Nötr',
};

function Legend({ onClose }) {
  return (
    <div className="absolute bottom-4 left-4 md:bottom-6 md:left-4 bg-card/90 backdrop-blur-md border border-border/50 rounded-2xl p-4 text-xs space-y-3 w-56 shadow-2xl max-h-[60vh] overflow-y-auto">
      <div className="flex items-center justify-between">
        <p className="font-extrabold text-foreground text-sm uppercase tracking-wider">Graf Açıklaması</p>
        {onClose && (
          <button onClick={onClose} className="text-muted-foreground hover:text-foreground text-base leading-none">✕</button>
        )}
      </div>
      <div>
        <p className="text-muted-foreground font-semibold mb-1.5">Olay Türü (Düğüm Rengi)</p>
        {Object.entries(EVENT_COLORS).slice(0, 6).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2 py-0.5">
            <span className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: color }} />
            <span className="text-foreground">{EVENT_TYPE_TR[type] || type}</span>
          </div>
        ))}
      </div>
      <div>
        <p className="text-muted-foreground font-semibold mb-1.5">Sinyal Tipi (Kenar)</p>
        {Object.entries(SIGNAL_COLORS).map(([type, color]) => (
          <div key={type} className="flex items-center gap-2 py-0.5">
            <span className="w-6 h-0.5 rounded flex-shrink-0" style={{ background: color }} />
            <span className="text-foreground">{SIGNAL_COLORS_TR[type] || type}</span>
          </div>
        ))}
      </div>
      <div>
        <p className="text-muted-foreground font-semibold mb-1">Düğüm Boyutu</p>
        <p className="text-foreground">= BIOS Skoru (0–100)</p>
      </div>
    </div>
  );
}

function clamp(val, min, max) {
  return Math.max(min, Math.min(max, val));
}

function NodeTooltip({ node, x, y, sidebarOpen, canvasWidth }) {
  if (!node) return null;

  // Keep the tooltip inside viewport to avoid covering the top-right controls.
  const tooltipWidth = node.group === 'sector' || node.group === 'company' ? 320 : 380;
  const tooltipHeight = node.group === 'sector' || node.group === 'company' ? 120 : 220;
  const padding = 16;
  const topSafe = 84;      // reserve top overlay
  const leftSafe = sidebarOpen && (canvasWidth || 0) >= 768 ? 304 : 16;

  const vw = window.innerWidth || 1200;
  const vh = window.innerHeight || 800;

  const preferredLeft = x + 20;
  const preferredTop = y - 20;

  // Flip to left/up when close to edges.
  const left = clamp(
    preferredLeft + tooltipWidth > vw - padding ? x - tooltipWidth - 20 : preferredLeft,
    Math.max(padding, leftSafe),
    vw - tooltipWidth - padding
  );
  const top = clamp(
    preferredTop < padding ? y + 20 : preferredTop,
    Math.max(padding, topSafe),
    vh - tooltipHeight - padding
  );
  
  if (node.group === 'sector' || node.group === 'company') {
    return (
      <div className="fixed z-50 pointer-events-none transition-all duration-150 ease-out" style={{ left, top }}>
        <div className="bg-card/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-2xl p-4 max-w-[320px]">
           <p className="text-[11px] font-extrabold uppercase tracking-wider text-muted-foreground">
             {node.group === 'sector' ? 'Sektör' : 'Şirket'}
           </p>
           <p className="text-primary text-lg font-black mt-1 leading-snug">{node.label}</p>
        </div>
      </div>
    );
  }

  return (
    <div
      className="fixed z-50 pointer-events-none transition-all duration-150 ease-out"
      style={{ left, top }}
    >
      <div className="bg-card/95 backdrop-blur-xl border border-border/50 rounded-2xl shadow-[0_10px_40px_-10px_rgba(0,0,0,0.3)] p-4 max-w-[380px]">
        <p className="font-extrabold text-foreground text-base leading-snug">{node.title || node.label}</p>
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          {node.company && <span className="text-primary text-xs font-bold bg-primary/10 px-2 py-0.5 rounded-md">{node.company}</span>}
          {node.location && <span className="text-muted-foreground font-medium text-xs flex items-center gap-1"><MapPin className="w-3 h-3"/> {node.location}</span>}
        </div>
        <div className="flex items-center gap-2 mt-2 flex-wrap">
          <span
            className="px-2.5 py-1 rounded-full text-[10px] font-bold uppercase tracking-wider"
            style={{ background: (EVENT_COLORS[node.event_type] || EVENT_COLORS.other) + '20', color: EVENT_COLORS[node.event_type] || EVENT_COLORS.other }}
          >
            {(node.event_type || 'other').replace('_', ' ')}
          </span>
          <ScoreBadge score={node.score || 0} />
          {node.sector && <span className="text-muted-foreground text-[10px] font-semibold uppercase tracking-wider">{node.sector}</span>}
        </div>
        <div className="mt-3">
          <p className="text-[11px] font-extrabold uppercase tracking-wider text-muted-foreground mb-1">AI Özeti (TR)</p>
          <p className="text-muted-foreground/90 text-sm line-clamp-4 leading-relaxed font-medium">
            {node.summary_tr || "Özet yok."}
          </p>
        </div>
        <div className="mt-3 pt-3 border-t border-border/50 flex justify-between items-center">
          <p className="text-blue-500 font-semibold text-xs flex items-center gap-1">Tıkla ve Detayları Gör <ExternalLink className="w-3 h-3" /></p>
        </div>
      </div>
    </div>
  );
}

export default function GraphPage() {
  const [graphData, setGraphData] = useState({ nodes: [], links: [] });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [tooltip, setTooltip] = useState({ node: null, x: 0, y: 0 });
  const [stats, setStats] = useState({ nodes: 0, edges: 0 });
  const fgRef = useRef();
  const containerRef = useRef(null);
  const navigate = useNavigate();
  const [dims, setDims] = useState({ width: 0, height: 0 });
  const { sidebarOpen } = useAppStore();
  const [showLegend, setShowLegend] = useState(true);

  const fetchGraph = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await fetchApi('/graph');

      const nodes = (data.nodes || []).map(n => ({
        ...n,
        val: Math.max(2, (n.score || 30) / 10), // node size by score
      }));

      // Map edges: source/target must match node ids
      const nodeIds = new Set(nodes.map(n => n.id));
      const links = (data.edges || [])
        .filter(e => nodeIds.has(e.source) && nodeIds.has(e.target))
        .map(e => ({
          source: e.source,
          target: e.target,
          relationship: e.relationship || '',
          reasons: e.reasons || [],
          signal_source: e.signal_source || 'neutral',
        }));

      setGraphData({ nodes, links });
      setStats({ nodes: nodes.length, edges: links.length });
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchGraph();
  }, [fetchGraph]);

  useEffect(() => {
    if (!containerRef.current) return;
    const el = containerRef.current;

    const update = () => {
      const rect = el.getBoundingClientRect();
      setDims({
        width: Math.max(320, Math.floor(rect.width)),
        height: Math.max(320, Math.floor(rect.height)),
      });
    };

    update();
    const ro = new ResizeObserver(update);
    ro.observe(el);
    window.addEventListener('resize', update);
    return () => {
      ro.disconnect();
      window.removeEventListener('resize', update);
    };
  }, []);

  // Mobile defaults: hide legend to avoid clutter
  useEffect(() => {
    if (!dims.width) return;
    if (dims.width < 640) setShowLegend(false);
    else setShowLegend(true);
  }, [dims.width]);

  const handleNodeClick = useCallback((node) => {
    if (node.group === 'article' || !node.group) {
      navigate(`/article/${node.id}`);
    }
  }, [navigate]);

  const handleNodeHover = useCallback((node, prevNode) => {
    // node is null when hover ends
  }, []);

  const paintNode = useCallback((node, ctx, globalScale) => {
    const isDark = document.documentElement.classList.contains('dark');
    const labelColor = isDark ? 'rgba(255,255,255,0.85)' : 'rgba(15,23,42,0.9)';
    const borderColor = isDark ? 'rgba(255,255,255,0.13)' : 'rgba(0,0,0,0.12)';

    let color = '#64748b';
    let r = 5;

    if (node.group === 'sector') {
      color = '#f59e0b';
      r = 10;
    } else if (node.group === 'company') {
      color = '#3b82f6';
      r = 8;
    } else {
      color = EVENT_COLORS[node.event_type] || EVENT_COLORS.other;
      r = Math.max(3, (node.score || 30) / 10);

      if (node.score >= 80) {
        ctx.beginPath();
        ctx.arc(node.x, node.y, r + 3, 0, 2 * Math.PI);
        ctx.fillStyle = color + '33';
        ctx.fill();
      }
    }

    ctx.beginPath();
    ctx.arc(node.x, node.y, r, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();

    ctx.strokeStyle = borderColor;
    ctx.lineWidth = 0.5;
    ctx.stroke();

    if (globalScale > 1.5 || node.group === 'sector') {
      const label = node.label || node.company || '';
      ctx.font = node.group === 'sector'
        ? `bold ${Math.max(5, 14 / globalScale)}px Sans-Serif`
        : `${Math.max(3, 10 / globalScale)}px Sans-Serif`;
      ctx.fillStyle = labelColor;
      ctx.textAlign = 'center';
      ctx.textBaseline = 'middle';
      ctx.fillText(label.substring(0, 20), node.x, node.y + r + 5 / globalScale);
    }
  }, []);

  const linkColor = useCallback((link) => {
    return SIGNAL_COLORS[link.signal_source] || SIGNAL_COLORS.neutral;
  }, []);

  const linkWidth = useCallback((link) => {
    return link.reasons?.length > 1 ? 2 : 1;
  }, []);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <div className="text-center space-y-4">
          <div className="w-12 h-12 border-4 border-primary border-t-transparent rounded-full animate-spin mx-auto" />
          <p className="text-muted-foreground">Bilgi grafiği yükleniyor…</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <div className="text-center space-y-3">
          <AlertCircle className="w-12 h-12 text-destructive mx-auto" />
          <p className="text-destructive font-medium">Graf yüklenemedi</p>
          <p className="text-muted-foreground text-sm">{error}</p>
          <button onClick={fetchGraph} className="px-4 py-2 bg-primary text-primary-foreground rounded-lg text-sm">
            Tekrar Dene
          </button>
        </div>
      </div>
    );
  }

  if (graphData.nodes.length === 0) {
    return (
      <div className="flex items-center justify-center h-full min-h-[60vh]">
        <div className="text-center space-y-3">
          <Network className="w-16 h-16 text-muted-foreground mx-auto opacity-40" />
          <p className="text-foreground font-semibold text-lg">Henüz haber grafiği yok</p>
          <p className="text-muted-foreground text-sm max-w-sm">
            Dashboard'dan "Tümünü Yenile" butonuna tıklayarak haberler analiz edilsin, ardından bu sayfa otomatik dolacak.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div ref={containerRef} className="relative w-full overflow-hidden" style={{ height: 'calc(100vh - 80px)' }}>
      {/* Header */}
      <div className="absolute top-4 left-4 right-4 md:top-6 md:left-6 md:right-6 z-20 flex flex-col md:flex-row md:items-center md:justify-between gap-3 pointer-events-none">
        <div className="bg-card/85 backdrop-blur-md border border-border/50 shadow-lg rounded-2xl px-4 py-3 flex items-center gap-3">
          <div className="bg-primary/10 p-2 rounded-xl">
            <Network className="w-6 h-6 text-primary" />
          </div>
          <div>
            <p className="font-extrabold text-foreground text-base tracking-tight">Sinyal Graf</p>
            <p className="text-muted-foreground text-xs font-medium mt-0.5">
              {stats.nodes} haber düğümü · {stats.edges} bağlantı
            </p>
          </div>
        </div>

        <div className="flex items-center gap-2 pointer-events-auto bg-card/85 backdrop-blur-md border border-border/50 p-1.5 rounded-2xl shadow-lg self-end md:self-auto">
          <button
            onClick={() => fgRef.current?.zoomToFit(400)}
            className="rounded-xl p-2.5 text-muted-foreground hover:text-foreground hover:bg-foreground/5 transition-colors"
            title="Tümünü Göster"
          >
            <Maximize2 className="w-5 h-5" />
          </button>
          <button
            onClick={() => fgRef.current?.zoom(fgRef.current.zoom() * 1.3, 200)}
            className="rounded-xl p-2.5 text-muted-foreground hover:text-foreground hover:bg-foreground/5 transition-colors"
            title="Yakınlaş"
          >
            <ZoomIn className="w-5 h-5" />
          </button>
          <button
            onClick={() => fgRef.current?.zoom(fgRef.current.zoom() / 1.3, 200)}
            className="rounded-xl p-2.5 text-muted-foreground hover:text-foreground hover:bg-foreground/5 transition-colors"
            title="Uzaklaş"
          >
            <ZoomOut className="w-5 h-5" />
          </button>
          <div className="w-px h-6 bg-border mx-1"></div>
          <button
            onClick={() => setShowLegend((s) => !s)}
            className={`rounded-xl p-2.5 transition-colors ${showLegend ? 'text-primary bg-primary/10' : 'text-muted-foreground hover:text-foreground hover:bg-foreground/5'}`}
            title="Açıklama"
          >
            <Info className="w-5 h-5" />
          </button>
          <button
            onClick={fetchGraph}
            className="rounded-xl p-2.5 text-primary hover:bg-primary/10 transition-colors"
            title="Yenile"
          >
            <RefreshCw className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Force Graph */}
      <ForceGraph2D
        ref={fgRef}
        graphData={graphData}
        nodeId="id"
        linkSource="source"
        linkTarget="target"
        backgroundColor="var(--color-background)"

        nodeCanvasObject={paintNode}
        nodeCanvasObjectMode={() => 'replace'}
        linkColor={linkColor}
        linkWidth={linkWidth}
        linkDirectionalParticles={2}
        linkDirectionalParticleSpeed={0.005}
        linkDirectionalParticleWidth={linkWidth}
        onNodeClick={handleNodeClick}
        onNodeHover={(node, prevNode, evt) => {
          setTooltip(node ? { node, x: evt?.clientX || 0, y: evt?.clientY || 0 } : { node: null, x: 0, y: 0 });
          document.body.style.cursor = node ? 'pointer' : 'default';
        }}
        cooldownTicks={100}
        onEngineStop={() => fgRef.current?.zoomToFit(400, 40)}
        width={dims.width || (window.innerWidth - 100)}
        height={dims.height || (window.innerHeight - 80)}
      />

      {/* Tooltip */}
      {tooltip.node && (
        <NodeTooltip
          node={tooltip.node}
          x={tooltip.x}
          y={tooltip.y}
          sidebarOpen={sidebarOpen}
          canvasWidth={dims.width}
        />
      )}

      {/* Legend */}
      {showLegend && <Legend onClose={() => setShowLegend(false)} />}

      {/* Mobile hint */}
      <div className="md:hidden absolute bottom-4 right-4 pointer-events-none text-[11px] font-semibold text-muted-foreground bg-card/80 backdrop-blur border border-border/50 rounded-full px-3 py-1.5 shadow">
        İpucu: Yakınlaş/uzaklaş için pinch, düğüme dokun.
      </div>
    </div>
  );
}
