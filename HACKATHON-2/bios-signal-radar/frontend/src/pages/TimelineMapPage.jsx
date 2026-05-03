import React, { useState, useEffect, useCallback } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { ComposableMap, Geographies, Geography, Marker, Line, ZoomableGroup } from 'react-simple-maps';
import topology from 'world-atlas/countries-110m.json';
import { fetchApi } from '../lib/api';
import { Clock, MapPin, Building2, ArrowRight, AlertCircle, ZoomIn, ZoomOut, RotateCcw, ExternalLink } from 'lucide-react';

// Gerçek koordinatlar [longitude, latitude]
const CITY_COORDS = {
  // Ülkeler (merkez)
  'germany': [10.0, 51.5], 'deutschland': [10.0, 51.5], 'almanya': [10.0, 51.5],
  'france': [2.3, 46.2], 'frankreich': [2.3, 46.2], 'fransa': [2.3, 46.2],
  'italy': [12.6, 42.5], 'italien': [12.6, 42.5], 'italya': [12.6, 42.5], 'italia': [12.6, 42.5],
  'spain': [-3.7, 40.4], 'spanien': [-3.7, 40.4], 'ispanya': [-3.7, 40.4],
  'poland': [19.1, 51.9], 'polen': [19.1, 51.9], 'polonya': [19.1, 51.9], 'polska': [19.1, 51.9],
  'uk': [-2.0, 54.0], 'united kingdom': [-2.0, 54.0], 'england': [-1.5, 52.0], 'ingiltere': [-2.0, 54.0],
  'turkey': [35.2, 39.0], 'türkiye': [35.2, 39.0], 'turkiye': [35.2, 39.0],
  'hungary': [19.5, 47.2], 'ungarn': [19.5, 47.2], 'macaristan': [19.5, 47.2],
  'czech republic': [15.5, 49.8], 'czechia': [15.5, 49.8], 'çekya': [15.5, 49.8],
  'slovakia': [19.7, 48.7], 'slowakei': [19.7, 48.7], 'slovakya': [19.7, 48.7],
  'romania': [24.9, 45.9], 'rumänien': [24.9, 45.9], 'romanya': [24.9, 45.9],
  'austria': [14.5, 47.5], 'österreich': [14.5, 47.5], 'avusturya': [14.5, 47.5],
  'netherlands': [5.3, 52.1], 'niederlande': [5.3, 52.1], 'hollanda': [5.3, 52.1],
  'belgium': [4.5, 50.5], 'belgien': [4.5, 50.5], 'belçika': [4.5, 50.5],
  'sweden': [17.0, 62.0], 'schweden': [17.0, 62.0], 'isveç': [17.0, 62.0],
  'serbia': [20.5, 44.0], 'serbien': [20.5, 44.0], 'sırbistan': [20.5, 44.0],
  'bulgaria': [25.5, 42.7], 'bulgarien': [25.5, 42.7], 'bulgaristan': [25.5, 42.7],
  'croatia': [15.2, 45.1], 'kroatien': [15.2, 45.1], 'hırvatistan': [15.2, 45.1],
  'portugal': [-8.2, 39.4], 'portekiz': [-8.2, 39.4],
  'greece': [22.0, 39.1], 'griechenland': [22.0, 39.1], 'yunanistan': [22.0, 39.1],
  'denmark': [9.5, 56.3], 'dänemark': [9.5, 56.3], 'danimarka': [9.5, 56.3],
  'finland': [25.7, 64.0], 'finnland': [25.7, 64.0], 'finlandiya': [25.7, 64.0],
  'norway': [8.5, 60.5], 'norwegen': [8.5, 60.5], 'norveç': [8.5, 60.5],
  'switzerland': [8.2, 46.8], 'schweiz': [8.2, 46.8], 'isviçre': [8.2, 46.8],
  'usa': [-98.0, 39.5], 'united states': [-98.0, 39.5], 'abd': [-98.0, 39.5], 'america': [-98.0, 39.5],
  'china': [104.0, 35.0], 'çin': [104.0, 35.0],
  'japan': [138.0, 37.0], 'japonya': [138.0, 37.0],
  'india': [78.0, 22.0], 'hindistan': [78.0, 22.0],
  'mexico': [-102.5, 24.0], 'meksika': [-102.5, 24.0],
  'brazil': [-51.9, -14.2], 'brezilya': [-51.9, -14.2],
  'south korea': [127.9, 36.5], 'güney kore': [127.9, 36.5],
  'vietnam': [108.0, 16.0], 'vietnam': [108.0, 16.0],
  'morocco': [-5.5, 31.8], 'fas': [-5.5, 31.8],
  'ukraine': [31.2, 48.4], 'ukrayna': [31.2, 48.4],
  // Şehirler
  'berlin': [13.4, 52.5], 'munich': [11.6, 48.1], 'münchen': [11.6, 48.1],
  'frankfurt': [8.7, 50.1], 'hamburg': [10.0, 53.6], 'cologne': [6.9, 50.9], 'köln': [6.9, 50.9],
  'stuttgart': [9.2, 48.8], 'düsseldorf': [6.8, 51.2], 'leipzig': [12.4, 51.3],
  'paris': [2.3, 48.9], 'lyon': [4.8, 45.7], 'marseille': [5.4, 43.3], 'bordeaux': [-0.6, 44.8],
  'milan': [9.2, 45.5], 'rome': [12.5, 41.9], 'roma': [12.5, 41.9], 'turin': [7.7, 45.1],
  'madrid': [-3.7, 40.4], 'barcelona': [2.2, 41.4], 'valencia': [-0.4, 39.5],
  'warsaw': [21.0, 52.2], 'wroclaw': [17.0, 51.1], 'krakow': [20.0, 50.1], 'gdansk': [18.6, 54.4],
  'london': [-0.1, 51.5], 'birmingham': [-1.9, 52.5], 'manchester': [-2.2, 53.5],
  'istanbul': [29.0, 41.0], 'ankara': [32.9, 39.9], 'izmir': [27.1, 38.4],
  'sakarya': [30.4, 40.8], 'adapazarı': [30.4, 40.8], 'adapazari': [30.4, 40.8],
  'kocaeli': [29.9, 40.8], 'izmit': [29.9, 40.8], 'bursa': [29.1, 40.2],
  'konya': [32.5, 37.9], 'kayseri': [35.5, 38.7], 'eskişehir': [30.5, 39.8], 'eskisehir': [30.5, 39.8],
  'budapest': [19.1, 47.5], 'debrecen': [21.6, 47.5], 'győr': [17.6, 47.7],
  'prague': [14.4, 50.1], 'brno': [16.6, 49.2],
  'bratislava': [17.1, 48.1],
  'bucharest': [26.1, 44.4], 'bucurești': [26.1, 44.4], 'cluj': [23.6, 46.8],
  'vienna': [16.4, 48.2], 'wien': [16.4, 48.2], 'graz': [15.4, 47.1],
  'amsterdam': [4.9, 52.4], 'rotterdam': [4.5, 51.9], 'eindhoven': [5.5, 51.4],
  'brussels': [4.3, 50.8], 'brüssel': [4.3, 50.8], 'antwerp': [4.4, 51.2],
  'stockholm': [18.1, 59.3], 'gothenburg': [12.0, 57.7],
  'belgrade': [20.5, 44.8], 'beograd': [20.5, 44.8],
  'sofia': [23.3, 42.7], 'zagreb': [15.9, 45.8],
  'lisbon': [-9.1, 38.7], 'lisboa': [-9.1, 38.7], 'porto': [-8.6, 41.2],
  'athens': [23.7, 38.0], 'copenhagen': [12.6, 55.7],
  'zurich': [8.5, 47.4], 'zürich': [8.5, 47.4], 'geneva': [6.1, 46.2],
  // Ek lokasyonlar
  'egypt': [30.8, 26.8], 'mısır': [30.8, 26.8], 'misir': [30.8, 26.8],
  'iran': [53.7, 32.4], 'i̇ran': [53.7, 32.4],
  'israel': [35.0, 31.5], 'i̇srail': [35.0, 31.5], 'israil': [35.0, 31.5],
  'taiwan': [121.0, 23.7],
  'philippines': [122.0, 12.9], 'filipinler': [122.0, 12.9],
  'malaysia': [109.7, 3.1], 'malezya': [109.7, 3.1],
  'kuala lumpur': [101.7, 3.1],
  'new york': [-74.0, 40.7],
  'san diego': [-117.2, 32.7],
  'california': [-119.4, 36.8],
  'oakland': [-122.3, 37.8],
  'omaha': [-95.9, 41.3],
  'nebraska': [-99.9, 41.5],
  'georgia': [-83.4, 32.7],
  'denizli': [29.1, 37.8],
  'kırklareli': [27.2, 41.7], 'kirklareli': [27.2, 41.7],
  'erzincan': [39.5, 39.7],
  'anadolu': [35.0, 39.0], 'iç anadolu': [33.5, 39.0], 'ic anadolu': [33.5, 39.0],
  'strait of hormuz': [56.5, 26.6],
  'novorossiysk': [37.8, 44.7],
  'russia': [60.0, 60.0], 'rusya': [60.0, 60.0],
  'georgia us': [-83.4, 32.7],
};

// Türkçe büyük İ harfini normalize et (JS toLowerCase sorunu)
function normalizeTr(s) {
  return s.replace(/İ/g, 'i').replace(/I/g, 'ı').toLowerCase().trim();
}

function getCoords(location) {
  if (!location) return null;
  const lower = normalizeTr(location);
  if (CITY_COORDS[lower]) return CITY_COORDS[lower];
  // İlk virgüle kadar olan kısmı da dene (ör: "Istanbul, Turkey")
  const firstPart = normalizeTr(lower.split(',')[0].trim());
  if (CITY_COORDS[firstPart]) return CITY_COORDS[firstPart];
  for (const [key, coords] of Object.entries(CITY_COORDS)) {
    if (lower.includes(key) || key.includes(firstPart)) {
      return coords;
    }
  }
  return null;
}

const EVENT_TYPE_COLORS = {
  relocation: '#6366f1',
  closure: '#ef4444',
  expansion: '#22c55e',
  new_plant: '#3b82f6',
  tender: '#f59e0b',
  other: '#64748b',
};
const EVENT_TYPE_LABELS = {
  relocation: 'Taşınma', closure: 'Kapanış', expansion: 'Genişleme',
  new_plant: 'Yeni Tesis', tender: 'İhale', other: 'Diğer',
};
const EVENT_TYPE_BADGE = {
  relocation: 'bg-indigo-100 text-indigo-800 dark:bg-indigo-900/30 dark:text-indigo-300',
  closure: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300',
  expansion: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300',
  new_plant: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300',
  tender: 'bg-amber-100 text-amber-800 dark:bg-amber-900/30 dark:text-amber-300',
  other: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-300',
};

// ── Timeline Bileşeni ──────────────────────────────────────────────────────────
function TimelineView({ companies }) {
  if (companies.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 border border-dashed rounded-2xl text-center gap-3">
        <Building2 className="w-12 h-12 text-muted-foreground opacity-30" />
        <p className="font-semibold text-foreground">Henüz şirket verisi yok</p>
        <p className="text-sm text-muted-foreground max-w-sm">
          Haberleri yenileyerek şirket bilgilerini çekin. Ardından burada zaman çizelgesi görünecek.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {companies.map(([company, arts]) => (
        <div key={company} className="bg-card border border-border rounded-2xl p-5 md:p-6">
          <div className="flex items-center gap-3 mb-5">
            <div className="bg-primary/10 p-2 rounded-xl flex-shrink-0">
              <Building2 className="w-5 h-5 text-primary" />
            </div>
            <div className="min-w-0">
              <h3 className="text-base font-extrabold text-foreground truncate">{company}</h3>
              <p className="text-xs text-muted-foreground">{arts.length} etkinlik</p>
            </div>
          </div>

          <div className="relative pl-7">
            <div className="absolute left-2.5 top-1 bottom-1 w-0.5 bg-border/60 rounded-full" />
            <div className="space-y-4">
              {arts.map((a) => {
                const dot = EVENT_TYPE_COLORS[a.event_type] || EVENT_TYPE_COLORS.other;
                const badge = EVENT_TYPE_BADGE[a.event_type] || EVENT_TYPE_BADGE.other;
                const label = EVENT_TYPE_LABELS[a.event_type] || 'Diğer';
                const dateStr = a.published_at || a.fetched_at;
                const date = dateStr
                  ? new Date(dateStr).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' })
                  : '';
                return (
                  <div key={a.id} className="relative">
                    <div
                      className="absolute -left-5 top-2 w-3.5 h-3.5 rounded-full border-2 border-card shadow-sm"
                      style={{ background: dot }}
                    />
                    <Link
                      to={`/article/${a.id}`}
                      className="block bg-background/60 border border-border/50 rounded-xl p-4 hover:border-primary/30 hover:bg-card transition-all"
                    >
                      <div className="flex flex-wrap items-center gap-2 mb-2">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold ${badge}`}>{label}</span>
                        {date && (
                          <span className="text-[11px] text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3 h-3" />{date}
                          </span>
                        )}
                        {(a.bios_fit?.score_final || 0) > 0 && (
                          <span className="text-[11px] font-bold text-primary ml-auto">
                            BIOS: {a.bios_fit.score_final}
                          </span>
                        )}
                      </div>
                      <p className="text-sm font-semibold text-foreground line-clamp-2 mb-2">{a.title}</p>
                      {(a.from_location || a.to_location) && (
                        <div className="flex items-center gap-1.5 text-xs text-muted-foreground flex-wrap">
                          <MapPin className="w-3 h-3 flex-shrink-0" />
                          <span className={a.event_type === 'relocation' || a.event_type === 'closure' ? 'line-through opacity-60' : ''}>
                            {a.from_location || '?'}
                          </span>
                          <ArrowRight className="w-3 h-3 flex-shrink-0 text-primary" />
                          <span className="text-primary font-semibold">{a.to_location || '?'}</span>
                        </div>
                      )}
                    </Link>
                  </div>
                );
              })}
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

// ── Dünya Haritası Bileşeni ────────────────────────────────────────────────────
function MapView({ articles }) {
  const navigate = useNavigate();
  const [hovered, setHovered] = useState(null);
  const [zoom, setZoom] = useState(1);
  const [center, setCenter] = useState([15, 30]);

  const mapArticles = articles.filter((a) => a.from_location || a.to_location);

  const handleZoomIn = useCallback(() => setZoom((z) => Math.min(z * 1.6, 12)), []);
  const handleZoomOut = useCallback(() => setZoom((z) => Math.max(z / 1.6, 1)), []);
  const handleReset = useCallback(() => { setZoom(1); setCenter([15, 30]); }, []);
  const goToArticle = useCallback((id) => navigate(`/article/${id}`), [navigate]);

  if (mapArticles.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-20 border border-dashed rounded-2xl text-center gap-3">
        <MapPin className="w-12 h-12 text-muted-foreground opacity-30" />
        <p className="font-semibold text-foreground">Hareket verisi bulunamadı</p>
        <p className="text-sm text-muted-foreground max-w-sm">
          "Taşınma", "Yeni Tesis" veya "Genişleme" haberleri analiz edildiğinde burada dünya haritasında gösterilecek.
        </p>
      </div>
    );
  }

  const entries = mapArticles.map((a) => ({
    article: a,
    fromCoords: getCoords(a.from_location),   // null ise kaynak bilinmiyor
    toCoords: getCoords(a.to_location),        // null ise hedef bilinmiyor
    hasFrom: !!a.from_location,               // metin var mı (koordinat çözülemese bile)
    hasTo: !!a.to_location,
  }));

  const hoveredEntry = entries.find((e) => e.article.id === hovered);

  return (
    <div className="space-y-4">
      <p className="text-sm text-muted-foreground">
        <span className="font-semibold text-foreground">{mapArticles.length}</span> hareket haritada gösteriliyor.
        Fare ile kaydırabilir, butonlarla büyütebilirsiniz.
      </p>

      <div className="relative border border-border rounded-2xl overflow-hidden bg-[#0f172a]" style={{ minHeight: 480 }}>
        {/* Zoom kontrolleri */}
        <div className="absolute top-3 left-3 z-20 flex flex-col gap-1">
          <button
            onClick={handleZoomIn}
            className="w-8 h-8 bg-card/90 backdrop-blur border border-border/60 rounded-lg flex items-center justify-center hover:bg-card shadow text-foreground transition-colors"
            title="Yakınlaştır"
          >
            <ZoomIn className="w-4 h-4" />
          </button>
          <button
            onClick={handleZoomOut}
            className="w-8 h-8 bg-card/90 backdrop-blur border border-border/60 rounded-lg flex items-center justify-center hover:bg-card shadow text-foreground transition-colors"
            title="Uzaklaştır"
          >
            <ZoomOut className="w-4 h-4" />
          </button>
          <button
            onClick={handleReset}
            className="w-8 h-8 bg-card/90 backdrop-blur border border-border/60 rounded-lg flex items-center justify-center hover:bg-card shadow text-foreground transition-colors"
            title="Sıfırla"
          >
            <RotateCcw className="w-3.5 h-3.5" />
          </button>
        </div>

        <ComposableMap
          projection="geoMercator"
          projectionConfig={{ scale: 140 }}
          style={{ width: '100%', height: 480 }}
        >
          <ZoomableGroup
            zoom={zoom}
            center={center}
            onMoveEnd={({ coordinates, zoom: z }) => { setCenter(coordinates); setZoom(z); }}
            minZoom={1}
            maxZoom={12}
          >
            <Geographies geography={topology}>
              {({ geographies }) =>
                geographies.map((geo) => (
                  <Geography
                    key={geo.rsmKey}
                    geography={geo}
                    fill="#1e293b"
                    stroke="#334155"
                    strokeWidth={0.4}
                    style={{
                      default: { outline: 'none' },
                      hover: { fill: '#273549', outline: 'none' },
                      pressed: { outline: 'none' },
                    }}
                  />
                ))
              }
            </Geographies>

            {/* Hareket çizgileri — ikisi de koordinat varsa */}
            {entries.map(({ article: a, fromCoords, toCoords }) => {
              if (!fromCoords || !toCoords) return null;
              const color = EVENT_TYPE_COLORS[a.event_type] || EVENT_TYPE_COLORS.other;
              const isHov = hovered === a.id;
              return (
                <Line
                  key={`line-${a.id}`}
                  from={fromCoords}
                  to={toCoords}
                  stroke={color}
                  strokeWidth={isHov ? 2 : 1}
                  strokeOpacity={isHov ? 1 : 0.6}
                  strokeLinecap="round"
                />
              );
            })}

            {/* Kaynak noktası (kırmızı) */}
            {entries.map(({ article: a, fromCoords }) => {
              if (!fromCoords) return null;
              const isHov = hovered === a.id;
              return (
                <Marker key={`from-${a.id}`} coordinates={fromCoords}>
                  <circle
                    r={isHov ? 6 : 4}
                    fill="#ef4444"
                    fillOpacity={0.9}
                    stroke="#fff"
                    strokeWidth={isHov ? 1.5 : 0.8}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHovered(a.id)}
                    onMouseLeave={() => setHovered(null)}
                    onClick={() => goToArticle(a.id)}
                  />
                </Marker>
              );
            })}

            {/* Hedef noktası (olay rengi) */}
            {entries.map(({ article: a, toCoords }) => {
              if (!toCoords) return null;
              const color = EVENT_TYPE_COLORS[a.event_type] || EVENT_TYPE_COLORS.other;
              const isHov = hovered === a.id;
              return (
                <Marker key={`to-${a.id}`} coordinates={toCoords}>
                  <circle
                    r={isHov ? 6 : 4}
                    fill={color}
                    fillOpacity={0.95}
                    stroke="#fff"
                    strokeWidth={isHov ? 1.5 : 0.8}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHovered(a.id)}
                    onMouseLeave={() => setHovered(null)}
                    onClick={() => goToArticle(a.id)}
                  />
                </Marker>
              );
            })}

            {/* Tek konum + ? işareti */}
            {entries.map(({ article: a, fromCoords, toCoords, hasFrom, hasTo }) => {
              if (fromCoords && toCoords) return null;
              const coords = fromCoords || toCoords;
              if (!coords) return null;
              const color = EVENT_TYPE_COLORS[a.event_type] || EVENT_TYPE_COLORS.other;
              const isHov = hovered === a.id;
              const showQuestion = (fromCoords && (!hasTo || !toCoords)) || (toCoords && (!hasFrom || !fromCoords));
              return (
                <Marker key={`single-${a.id}`} coordinates={coords}>
                  <circle
                    r={isHov ? 6 : 4}
                    fill={color}
                    fillOpacity={0.85}
                    stroke="#fff"
                    strokeWidth={isHov ? 1.5 : 0.8}
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() => setHovered(a.id)}
                    onMouseLeave={() => setHovered(null)}
                    onClick={() => goToArticle(a.id)}
                  />
                  {showQuestion && (
                    <text
                      textAnchor="middle"
                      y={-8}
                      style={{ fontSize: 8, fill: '#94a3b8', fontWeight: 'bold', pointerEvents: 'none' }}
                    >?</text>
                  )}
                </Marker>
              );
            })}
          </ZoomableGroup>
        </ComposableMap>

        {/* Tooltip */}
        {hoveredEntry && (
          <div
            className="absolute top-3 right-14 bg-card/97 backdrop-blur border border-border/60 rounded-xl p-3 shadow-xl max-w-[230px] z-10 cursor-pointer hover:border-primary/40 transition-colors"
            onClick={() => goToArticle(hoveredEntry.article.id)}
          >
            <p className="text-xs font-bold text-foreground truncate leading-snug">
              {hoveredEntry.article.company || hoveredEntry.article.title?.slice(0, 40)}
            </p>
            <div className="flex items-center gap-1 mt-1.5 text-[11px] text-muted-foreground flex-wrap">
              <span>{hoveredEntry.article.from_location || '?'}</span>
              <ArrowRight className="w-3 h-3 text-primary flex-shrink-0" />
              <span className="text-primary font-semibold">{hoveredEntry.article.to_location || '?'}</span>
            </div>
            <div className="flex items-center gap-1.5 mt-1.5">
              <span
                className="w-2 h-2 rounded-full flex-shrink-0"
                style={{ background: EVENT_TYPE_COLORS[hoveredEntry.article.event_type] || EVENT_TYPE_COLORS.other }}
              />
              <span className="text-[11px] text-muted-foreground">
                {EVENT_TYPE_LABELS[hoveredEntry.article.event_type] || 'Diğer'}
              </span>
              {(hoveredEntry.article.bios_fit?.score_final || 0) > 0 && (
                <span className="text-[11px] font-bold text-primary ml-auto">
                  {hoveredEntry.article.bios_fit.score_final} puan
                </span>
              )}
            </div>
            <div className="flex items-center gap-1 mt-2 text-[10px] font-semibold text-primary">
              <ExternalLink className="w-3 h-3" />
              Habere git
            </div>
          </div>
        )}

        {/* Renk açıklaması */}
        <div className="absolute bottom-3 right-3 bg-card/90 backdrop-blur border border-border/50 rounded-xl p-2.5 text-[11px] space-y-1 shadow-lg">
          <p className="font-bold text-foreground mb-1 text-xs">Açıklama</p>
          {Object.entries(EVENT_TYPE_COLORS).slice(0, 5).map(([type, color]) => (
            <div key={type} className="flex items-center gap-1.5">
              <span className="w-2.5 h-2.5 rounded-full flex-shrink-0" style={{ background: color }} />
              <span className="text-muted-foreground">{EVENT_TYPE_LABELS[type]}</span>
            </div>
          ))}
          <div className="flex items-center gap-1.5 mt-1 pt-1 border-t border-border/40 text-muted-foreground">
            <span className="w-2.5 h-2.5 rounded-full bg-red-500 flex-shrink-0" />
            <span>Kaynak konum</span>
          </div>
          <div className="flex items-center gap-1.5 text-muted-foreground">
            <span className="text-[10px] font-bold text-slate-400">?</span>
            <span>Bilinmeyen taraf</span>
          </div>
        </div>
      </div>

      {/* Hareket listesi tablosu */}
      <div className="bg-card border border-border rounded-2xl overflow-hidden">
        <div className="px-5 py-3 border-b border-border bg-muted/30">
          <h3 className="font-bold text-sm text-foreground">Hareket Listesi</h3>
        </div>
        <div className="divide-y divide-border/50 max-h-80 overflow-y-auto">
          {mapArticles.map((a) => (
            <Link
              key={a.id}
              to={`/article/${a.id}`}
              className="flex items-center gap-4 px-5 py-3 hover:bg-muted/40 transition-colors"
            >
              <span
                className="w-2.5 h-2.5 rounded-full flex-shrink-0"
                style={{ background: EVENT_TYPE_COLORS[a.event_type] || EVENT_TYPE_COLORS.other }}
              />
              <div className="flex-1 min-w-0">
                <p className="text-sm font-semibold text-foreground truncate">{a.company || a.title?.slice(0, 40)}</p>
                <p className="text-xs text-muted-foreground flex items-center gap-1 mt-0.5">
                  <span className={a.event_type === 'relocation' || a.event_type === 'closure' ? 'line-through' : ''}>
                    {a.from_location || '?'}
                  </span>
                  <ArrowRight className="w-3 h-3 text-primary flex-shrink-0" />
                  <span className="text-primary font-semibold">{a.to_location || '?'}</span>
                </p>
              </div>
              <span className={`px-2 py-0.5 rounded-full text-[10px] font-bold flex-shrink-0 ${EVENT_TYPE_BADGE[a.event_type] || EVENT_TYPE_BADGE.other}`}>
                {EVENT_TYPE_LABELS[a.event_type] || 'Diğer'}
              </span>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}

// ── Ana Sayfa ──────────────────────────────────────────────────────────────────
export default function TimelineMapPage() {
  const [articles, setArticles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('timeline');

  useEffect(() => {
    (async () => {
      try {
        const res = await fetchApi('/articles?limit=100');
        setArticles(res.articles || []);
      } catch (e) {
        setError('Veriler yüklenirken bir sorun oluştu. Lütfen sayfayı yenileyin.');
      } finally {
        setLoading(false);
      }
    })();
  }, []);

  const relevant = articles.filter((a) => a.company || a.from_location || a.to_location);
  const companiesMap = {};
  for (const a of relevant) {
    const company = a.company || 'Bilinmeyen Şirket';
    if (!companiesMap[company]) companiesMap[company] = [];
    companiesMap[company].push(a);
  }
  for (const c of Object.keys(companiesMap)) {
    companiesMap[c].sort((a, b) => {
      const da = a.published_at || a.fetched_at || '';
      const db = b.published_at || b.fetched_at || '';
      return da < db ? -1 : da > db ? 1 : 0;
    });
  }
  const companies = Object.entries(companiesMap).sort((a, b) => b[1].length - a[1].length);

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-extrabold tracking-tight text-foreground">Zaman Çizelgesi & Harita</h1>
        <p className="text-muted-foreground text-sm mt-1">
          Şirket bazlı etkinlik geçmişi ve dünya genelinde taşınma / yatırım haritası.
        </p>
      </div>

      {/* Sekmeler */}
      <div className="flex gap-1 bg-muted/40 rounded-xl p-1 w-fit border border-border/50">
        {[
          { id: 'timeline', icon: <Clock className="w-4 h-4" />, label: 'Zaman Çizelgesi' },
          { id: 'map', icon: <MapPin className="w-4 h-4" />, label: 'Hareket Haritası' },
        ].map((tab) => (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-semibold transition-all ${
              activeTab === tab.id
                ? 'bg-card text-foreground shadow-sm border border-border/50'
                : 'text-muted-foreground hover:text-foreground'
            }`}
          >
            {tab.icon}{tab.label}
          </button>
        ))}
      </div>

      {loading ? (
        <div className="space-y-4">
          {[1, 2, 3].map((i) => (
            <div key={i} className="h-40 bg-muted/30 rounded-2xl animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="flex items-center gap-3 bg-destructive/10 border border-destructive/20 text-destructive rounded-2xl px-5 py-4">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          <p className="text-sm font-medium">{error}</p>
        </div>
      ) : activeTab === 'timeline' ? (
        <TimelineView companies={companies} />
      ) : (
        <MapView articles={articles} />
      )}
    </div>
  );
}
