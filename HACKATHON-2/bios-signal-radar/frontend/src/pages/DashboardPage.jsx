import React, { useEffect, useRef, useState } from 'react';
import { useArticles } from '../hooks/useApi';
import { useRSSSources } from '../hooks/useApi';
import { useAppStore } from '../store/useAppStore';
import ArticleCard from '../components/ArticleCard';
import FilterBar from '../components/FilterBar';
import { Button } from '../components/ui/button';
import { RefreshCw, Download, Clock } from 'lucide-react';
import { fetchApi } from '../lib/api';
import { toast } from 'sonner';

const AUTO_REFRESH_MINUTES = 3;

export default function DashboardPage() {
  const { filters, lastRefreshAt, setLastRefreshAt } = useAppStore();
  const { articles, summary, loading, refetch } = useArticles(filters, 1);
  const { sources } = useRSSSources();
  const [refreshing, setRefreshing] = useState(false);
  const [nextRefreshIn, setNextRefreshIn] = useState(AUTO_REFRESH_MINUTES * 60);
  const seenIdsRef = useRef(new Set());

  const downloadCsv = () => {
    const headers = [
      'id','title','source','score','event_type','company','from','to','sector','published_at'
    ];
    const escape = (v) => {
      const s = String(v ?? '');
      if (/[\",\\n]/.test(s)) return `"${s.replace(/\"/g, '""')}"`;
      return s;
    };
    const rows = (articles || []).map((a) => ([
      a.id,
      a.title,
      a.source_name || a.source_url,
      (a.bios_fit && a.bios_fit.score_final) ? a.bios_fit.score_final : 0,
      a.event_type || 'other',
      a.company || '',
      a.from_location || '',
      a.to_location || '',
      a.sector || '',
      a.published_at || a.fetched_at || '',
    ].map(escape).join(',')));

    const csv = '\uFEFF' + headers.join(',') + '\n' + rows.join('\n');
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    const date = new Date().toISOString().slice(0, 10);
    a.href = url;
    a.download = `articles_${date}.csv`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  };

  const handleRefresh = async ({ silent = false } = {}) => {
    setRefreshing(true);
    try {
      // Background task başlat (veya sync çağırabiliriz MVP için)
      await fetchApi('/refresh/sync', { method: 'POST', body: JSON.stringify({}) });
      setLastRefreshAt(new Date().toISOString());
      await refetch();
      if (!silent) toast.success('Yenileme tamamlandı');
    } catch (err) {
      if (!silent) toast.error(`Yenileme hatası: ${err.message}`);
    } finally {
      setRefreshing(false);
    }
  };

  // Otomatik yenileme sayaç ve tetikleyici
  useEffect(() => {
    setNextRefreshIn(AUTO_REFRESH_MINUTES * 60);
    const countdown = setInterval(() => {
      setNextRefreshIn((prev) => {
        if (prev <= 1) {
          if (!refreshing) handleRefresh({ silent: true });
          return AUTO_REFRESH_MINUTES * 60;
        }
        return prev - 1;
      });
    }, 1000);
    return () => clearInterval(countdown);
  }, [refreshing]); // eslint-disable-line react-hooks/exhaustive-deps

  // Notifications for starred feeds and high-score articles when new articles arrive
  useEffect(() => {
    const currentIds = new Set((articles || []).map((a) => a.id));
    if (seenIdsRef.current.size === 0) {
      seenIdsRef.current = currentIds;
      return;
    }

    const starredIds = new Set((sources || []).filter((s) => s.starred).map((s) => s.id));
    const newlyAdded = (articles || []).filter((a) => !seenIdsRef.current.has(a.id));

    // Yüksek fırsat bildirimi (BIOS >= 80)
    const highScore = newlyAdded
      .filter((a) => (a.bios_fit?.score_final || 0) >= 80)
      .slice(0, 2);
    for (const a of highScore) {
      toast.success(`Yüksek Fırsat: ${a.company || a.title?.slice(0, 40) || 'Yeni haber'}`, {
        description: `BIOS Skoru: ${a.bios_fit?.score_final} — ${a.summary_tr?.slice(0, 80) || a.title}`,
        duration: 6000,
      });
    }

    // Yıldızlı kaynak bildirimi
    const starredNotify = newlyAdded
      .filter((a) => starredIds.has(a.source_id) && (a.bios_fit?.score_final || 0) < 80)
      .slice(0, 2);
    for (const a of starredNotify) {
      toast(`Yeni haber: ${(a.source_name || '').slice(0, 30) || 'Kaynak'}`, {
        description: a.title,
      });
    }

    seenIdsRef.current = currentIds;
  }, [articles, sources]);

  return (
    <div className="space-y-6">
      {/* Üst Bar: Başlık ve Yenile */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl md:text-4xl font-extrabold tracking-tight bg-gradient-to-r from-foreground to-foreground/70 bg-clip-text text-transparent mb-1">
            Synapse — Endüstriyel Fırsat Radarı
          </h1>
          <p className="text-muted-foreground text-sm md:text-base font-medium">
            Avrupa genelinde relokasyon ve endüstriyel tesis hareketleri analizi.
          </p>
          <div className="flex items-center gap-3 mt-1 flex-wrap">
            <p className="text-muted-foreground text-xs font-semibold">
              Son güncelleme: {lastRefreshAt ? new Date(lastRefreshAt).toLocaleTimeString('tr-TR', { hour: '2-digit', minute: '2-digit' }) : '—'}
            </p>
            <span className="flex items-center gap-1 text-[10px] font-semibold text-primary/70 bg-primary/5 border border-primary/15 rounded-full px-2 py-0.5">
              <Clock className="w-3 h-3" />
              {Math.floor(nextRefreshIn / 60)}:{String(nextRefreshIn % 60).padStart(2, '0')} sonra otomatik yenileme
            </span>
          </div>
        </div>
        <div className="flex items-center gap-2">
          <Button variant="outline" onClick={downloadCsv} disabled={loading || (articles || []).length === 0} className="gap-2">
            <Download className="w-4 h-4" />
            CSV
          </Button>
          <Button onClick={() => handleRefresh({ silent: false })} disabled={refreshing} className="gap-2">
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} />
            {refreshing ? 'Taranıyor...' : 'Tümünü Yenile'}
          </Button>
        </div>
      </div>

      {/* İstatistikler */}
      {summary && (
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <div className="p-5 rounded-2xl border bg-card/60 backdrop-blur-sm hover:shadow-lg transition-all duration-300">
            <div className="text-xs font-semibold text-muted-foreground uppercase tracking-wider mb-1">Toplam Haber</div>
            <div className="text-3xl font-extrabold text-foreground">{summary.total_articles || 0}</div>
          </div>
          <div className="p-5 rounded-2xl border bg-gradient-to-br from-green-500/10 to-emerald-500/5 border-green-500/20 hover:shadow-[0_0_20px_rgba(34,197,94,0.15)] transition-all duration-300">
            <div className="text-xs font-semibold text-green-600 dark:text-green-400 uppercase tracking-wider mb-1">Yüksek Fırsat (80+)</div>
            <div className="text-3xl font-extrabold text-green-700 dark:text-green-300">{summary.high_opportunity || 0}</div>
          </div>
          <div className="p-5 rounded-2xl border bg-gradient-to-br from-blue-500/10 to-indigo-500/5 border-blue-500/20 hover:shadow-[0_0_20px_rgba(59,130,246,0.15)] transition-all duration-300">
            <div className="text-xs font-semibold text-blue-600 dark:text-blue-400 uppercase tracking-wider mb-1">İzlenecek (65-79)</div>
            <div className="text-3xl font-extrabold text-blue-700 dark:text-blue-300">{summary.watchlist || 0}</div>
          </div>
          <div className="p-5 rounded-2xl border bg-gradient-to-br from-amber-500/10 to-orange-500/5 border-amber-500/20 hover:shadow-[0_0_20px_rgba(245,158,11,0.15)] transition-all duration-300">
            <div className="text-xs font-semibold text-amber-600 dark:text-amber-400 uppercase tracking-wider mb-1">Şartlı İlgi (50-64)</div>
            <div className="text-3xl font-extrabold text-amber-700 dark:text-amber-300">{summary.conditional || 0}</div>
          </div>
        </div>
      )}

      {/* Filtreler */}
      <FilterBar />

      {/* Liste */}
      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-36 bg-muted/30 rounded-2xl animate-pulse border border-border/30" />
          ))}
        </div>
      ) : articles.length === 0 ? (
        <div className="flex flex-col items-center justify-center py-20 border border-dashed rounded-2xl gap-4 text-center">
          <div className="w-16 h-16 rounded-full bg-muted/40 flex items-center justify-center">
            <RefreshCw className="w-7 h-7 text-muted-foreground opacity-40" />
          </div>
          <div>
            <p className="font-semibold text-foreground mb-1">Haber bulunamadı</p>
            <p className="text-sm text-muted-foreground max-w-sm">
              {sources.length === 0
                ? 'Sol panelden RSS kaynağı ekleyin, ardından "Tümünü Yenile" butonuna basın.'
                : 'Seçili filtrelere uyan haber yok. Filtreleri sıfırlayın veya yeni haberler için yenileyin.'}
            </p>
          </div>
        </div>
      ) : (
        <div className="grid gap-4">
          {articles.map((article) => (
            <ArticleCard key={article.id} article={article} />
          ))}
        </div>
      )}
    </div>
  );
}
