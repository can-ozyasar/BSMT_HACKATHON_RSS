import React from 'react';
import { Link } from 'react-router-dom';
import { Badge } from './ui/badge';
import { MapPin, Building2, Factory, ExternalLink, Calendar, Zap, AlertTriangle } from 'lucide-react';

const EVENT_TYPE_MAP = {
  'relocation': { label: 'Taşınma', color: 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-400' },
  'closure':    { label: 'Kapanış', color: 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-400' },
  'expansion':  { label: 'Genişleme', color: 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-400' },
  'new_plant':  { label: 'Yeni Tesis', color: 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-400' },
  'tender':     { label: 'İhale', color: 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-400' },
  'other':      { label: 'Diğer', color: 'bg-gray-100 text-gray-800 dark:bg-gray-800 dark:text-gray-400' },
};

const SCORE_COLORS = {
  'green':  'bg-green-500 text-white',
  'blue':   'bg-blue-500 text-white',
  'yellow': 'bg-yellow-500 text-white',
  'gray':   'bg-gray-500 text-white',
};

export default function ArticleCard({ article }) {
  const bios = article.bios_fit || {};
  const score = bios.score_final || 0;
  const synapseScore = article.synapse_score || 10;
  const eventType = EVENT_TYPE_MAP[article.event_type] || EVENT_TYPE_MAP.other;
  const scoreColor = SCORE_COLORS[bios.color] || SCORE_COLORS.gray;
  const failed = article.analysis_status === 'failed';

  // Format date
  const dateStr = article.published_at || article.fetched_at;
  const date = dateStr ? new Date(dateStr).toLocaleDateString('tr-TR', { day: 'numeric', month: 'short', year: 'numeric' }) : '';

  return (
    <Link 
      to={`/article/${article.id}`}
      className={`block group relative backdrop-blur-sm border rounded-2xl p-5 md:p-6 transition-all duration-300 ${
        failed
          ? 'bg-muted/50 border-muted-foreground/20 hover:border-muted-foreground/40'
          : 'bg-card/60 border-border/60 hover:bg-card hover:border-primary/40 hover:shadow-[0_8px_30px_rgb(0,0,0,0.08)]'
      }`}
    >
      {/* Anomaly Badge */}
      {article.has_anomaly && (
        <div className="absolute -top-3 -right-3">
          <span className="flex items-center gap-1 bg-red-500 text-white text-xs font-bold px-2 py-1 rounded-full shadow-lg">
            <AlertTriangle className="w-3 h-3" />
            Spike: {article.anomaly_multiplier?.toFixed(1)}x
          </span>
        </div>
      )}

      <div className="flex flex-col md:flex-row gap-4 md:gap-6">
        
        {/* Sol Taraf: Skorlar */}
        <div className="flex-shrink-0 flex flex-col items-center gap-2">
          <div className={`w-16 h-16 md:w-20 md:h-20 rounded-[1.25rem] flex flex-col items-center justify-center shadow-lg transform group-hover:scale-105 transition-transform duration-300 ${scoreColor} bg-gradient-to-br opacity-90 group-hover:opacity-100`}>
            <span className="text-2xl md:text-3xl font-extrabold tracking-tighter">{score}</span>
            <span className="text-[10px] md:text-xs font-bold uppercase tracking-widest opacity-80 mt-0.5">Synapse</span>
          </div>
          <div className="bg-muted border border-border/60 px-3 py-1.5 rounded-xl shadow-inner flex flex-col items-center">
            <span className="text-xs font-black text-foreground">{synapseScore}</span>
            <span className="text-[8px] uppercase tracking-widest font-bold text-muted-foreground mt-0.5">Synapse</span>
          </div>
        </div>

        {/* Orta: İçerik */}
        <div className="flex-1 min-w-0">
          <div className="flex flex-wrap items-center gap-2.5 mb-3">
            <span className={`px-3 py-1 rounded-full text-[11px] font-bold uppercase tracking-wide shadow-sm ${eventType.color}`}>
              {eventType.label}
            </span>
            {failed && (
              <Badge variant="outline" className="uppercase text-[10px] tracking-wider border-muted-foreground/30 text-muted-foreground bg-muted/30">
                Analiz tamamlanamadı
              </Badge>
            )}
            <span className="text-xs font-medium text-muted-foreground/80 flex items-center gap-1.5 bg-muted/50 px-2 py-1 rounded-md">
              <Calendar className="w-3.5 h-3.5" /> {date}
            </span>
            <span className="text-xs font-semibold text-muted-foreground/90 flex items-center gap-1.5 bg-muted/50 px-2 py-1 rounded-md">
              <ExternalLink className="w-3.5 h-3.5" /> {article.source_name || article.source_url}
            </span>
            
            {article.signal_type === 'positive' && <Badge variant="outline" className="text-green-600 border-green-200 bg-green-50/50 uppercase text-[10px] tracking-wider">Pozitif</Badge>}
            {article.signal_type === 'negative' && <Badge variant="outline" className="text-red-600 border-red-200 bg-red-50/50 uppercase text-[10px] tracking-wider">Negatif</Badge>}
          </div>
          
          <h3 className="text-xl md:text-2xl font-extrabold text-foreground mb-3 leading-tight group-hover:text-primary transition-colors line-clamp-2">
            {article.title}
          </h3>
          
          <p className="text-sm md:text-base text-muted-foreground/90 font-medium mb-5 line-clamp-2 leading-relaxed">
            {failed
              ? (article.error ? `Analiz hatası: ${article.error}` : 'Analiz tamamlanamadı.')
              : (article.summary_tr || 'Türkçe özet üretilemedi.')}
          </p>

          <div className="flex flex-wrap gap-4 text-sm font-semibold text-foreground/80">
            {article.company && (
              <div className="flex items-center gap-1.5">
                <Building2 className="w-4 h-4 text-muted-foreground" />
                {article.company}
              </div>
            )}
            
            {(article.from_location || article.to_location) && (
              <div className="flex items-center gap-1.5">
                <MapPin className="w-4 h-4 text-muted-foreground" />
                <span className="flex items-center gap-1">
                  {article.from_location && <span className={article.event_type === 'relocation' || article.event_type === 'closure' ? 'line-through text-muted-foreground' : ''}>{article.from_location}</span>}
                  {article.from_location && article.to_location && <span>→</span>}
                  {article.to_location && <span className="text-primary font-bold">{article.to_location}</span>}
                </span>
              </div>
            )}

            {article.sector && (
              <div className="flex items-center gap-1.5">
                <Factory className="w-4 h-4 text-muted-foreground" />
                {article.sector}
              </div>
            )}
          </div>
        </div>

      </div>
    </Link>
  );
}
