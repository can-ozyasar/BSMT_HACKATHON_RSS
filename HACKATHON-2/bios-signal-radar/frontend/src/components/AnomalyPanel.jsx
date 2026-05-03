import React from 'react';
import { AlertTriangle, TrendingUp } from 'lucide-react';
import { useAnomalies } from '../hooks/useAnomalies';
import { useAppStore } from '../store/useAppStore';

function AnomalyItem({ a, setFilters }) {
  if (!a.entity) return null;
  return (
    <button
      onClick={() => setFilters({ searchQuery: a.entity })}
      className="w-full text-left flex items-center justify-between px-3 py-2 rounded-xl border border-border/60 bg-card/40 hover:bg-card hover:border-red-500/30 transition-all"
      title="Filtrelemek için tıkla"
    >
      <div className="truncate flex-1 min-w-0 mr-2">
        <div className="text-sm font-bold text-foreground truncate">{a.entity}</div>
        <div className="text-[11px] font-semibold text-muted-foreground">
          Son {a.article_count_recent ?? '—'} haber · baz {a.article_count_baseline ?? '—'}
        </div>
      </div>
      <span className="text-xs font-black text-red-600 dark:text-red-400 bg-red-500/10 px-2 py-1 rounded-lg flex-shrink-0">
        {typeof a.multiplier === 'number' ? `${a.multiplier.toFixed(1)}×` : `${a.multiplier}×`}
      </span>
    </button>
  );
}

export default function AnomalyPanel() {
  const { anomalies, loading, error } = useAnomalies();
  const { setFilters } = useAppStore();

  const companyAnomalies = (anomalies || []).filter((a) => a.entity_type === 'company' && a.entity).slice(0, 5);
  const locationAnomalies = (anomalies || []).filter((a) => a.entity_type === 'location' && a.entity).slice(0, 4);

  return (
    <div className="flex flex-col space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-extrabold text-foreground flex items-center gap-2">
          <AlertTriangle className="w-4 h-4 text-red-500" />
          Hareketli Şirketler
        </h3>
        <span className="text-[10px] font-bold text-muted-foreground bg-muted px-2 py-0.5 rounded-md">
          {companyAnomalies.length}
        </span>
      </div>

      {loading ? (
        <div className="space-y-2">
          {[1, 2].map(i => (
            <div key={i} className="h-12 rounded-xl bg-muted/40 animate-pulse" />
          ))}
        </div>
      ) : error ? (
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/40 rounded-xl px-3 py-2">
          <AlertTriangle className="w-3.5 h-3.5 flex-shrink-0" />
          <span>Şirket verileri yüklenemedi.</span>
        </div>
      ) : companyAnomalies.length === 0 && locationAnomalies.length === 0 ? (
        <div className="flex items-center gap-2 text-xs text-muted-foreground bg-muted/30 border border-border/40 rounded-xl px-3 py-3">
          <TrendingUp className="w-3.5 h-3.5 flex-shrink-0 opacity-50" />
          <span>Şu an olağandışı hareketlilik yok.</span>
        </div>
      ) : (
        <div className="space-y-2">
          {companyAnomalies.map((a) => (
            <AnomalyItem key={`company:${a.entity}`} a={a} setFilters={setFilters} />
          ))}

          {locationAnomalies.length > 0 && (
            <div className="pt-2">
              <div className="text-[11px] font-extrabold text-muted-foreground uppercase tracking-wider mb-2">
                Lokasyon Ani Artış
              </div>
              <div className="space-y-2">
                {locationAnomalies.map((a) => (
                  <AnomalyItem key={`location:${a.entity}`} a={a} setFilters={setFilters} />
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
