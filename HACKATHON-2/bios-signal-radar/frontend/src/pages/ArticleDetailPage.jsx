import React, { useState, useEffect } from 'react';
import { useParams, Link } from 'react-router-dom';
import { fetchApi } from '../lib/api';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { 
  ArrowLeft, ExternalLink, Calendar, Building2, MapPin, 
  Factory, ShieldAlert, ChevronDown, ChevronUp, Zap, FileText, Network, Sparkles
} from 'lucide-react';

const EVENT_TYPE_MAP = {
  'relocation': { label: 'Taşınma', color: 'bg-blue-100 text-blue-800' },
  'closure':    { label: 'Kapanış', color: 'bg-red-100 text-red-800' },
  'expansion':  { label: 'Genişleme', color: 'bg-green-100 text-green-800' },
  'new_plant':  { label: 'Yeni Tesis', color: 'bg-purple-100 text-purple-800' },
  'tender':     { label: 'İhale', color: 'bg-orange-100 text-orange-800' },
  'other':      { label: 'Diğer', color: 'bg-gray-100 text-gray-800' },
};

export default function ArticleDetailPage() {
  const { id } = useParams();
  const [article, setArticle] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [auditOpen, setAuditOpen] = useState(false);
  const [synapseOpen, setSynapseOpen] = useState(false);
  const [synapseAiOpen, setSynapseAiOpen] = useState(false);
  const [loadingSynapseAi, setLoadingSynapseAi] = useState(false);

  useEffect(() => {
    async function loadArticle() {
      try {
        setLoading(true);
        const data = await fetchApi(`/articles/${id}`);
        setArticle(data);
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    loadArticle();
  }, [id]);

  if (loading) return <div className="py-20 text-center animate-pulse">Yükleniyor...</div>;
  if (error) return <div className="py-20 text-center text-destructive">Hata: {error}</div>;
  if (!article) return <div className="py-20 text-center text-muted-foreground">Haber bulunamadı.</div>;

  const bios = article.bios_fit || {};
  const score = bios.score_final || 0;
  const synapseScore = article.synapse_score || 10;
  const synapseAi = article.synapse_ai || null;
  const eventType = EVENT_TYPE_MAP[article.event_type] || EVENT_TYPE_MAP.other;
  const failed = article.analysis_status === 'failed';
  const dateStr = article.published_at || article.fetched_at;
  const date = dateStr ? new Date(dateStr).toLocaleDateString('tr-TR', { day: 'numeric', month: 'long', year: 'numeric' }) : '';

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <Link to="/" className="inline-flex items-center text-sm text-muted-foreground hover:text-primary transition-colors">
        <ArrowLeft className="w-4 h-4 mr-1" />
        Geri Dön
      </Link>

      <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
        {/* Başlık Bölümü */}
        <div className="p-6 md:p-8 border-b border-border">
          <div className="flex flex-wrap items-center gap-3 mb-4">
            <span className={`px-3 py-1 rounded-full text-sm font-semibold ${eventType.color}`}>
              {eventType.label}
            </span>
            <span className="text-sm text-muted-foreground flex items-center gap-1">
              <Calendar className="w-4 h-4" /> {date}
            </span>
            <span className="text-sm text-muted-foreground">• {article.source_name || article.source_url}</span>
            <div className="ml-auto flex items-center gap-3">
              <Badge variant="outline" className="text-sm bg-background">
                Synapse: <strong className="ml-1 text-base text-indigo-500">{synapseScore}/100</strong>
              </Badge>
              <Badge variant="outline" className="text-sm">
                BIOS: <strong className="ml-1 text-base">{score}/100</strong>
              </Badge>
            </div>
          </div>
          
          <h1 className="text-2xl md:text-3xl font-bold text-foreground mb-4">
            {article.title}
          </h1>

          <div className="flex gap-4">
            <Button asChild variant="default" className="gap-2">
              <a
                href={(() => {
                  const raw = article.original_url || article.url || article.source_url || '';
                  if (!raw) return '#';
                  if (raw.startsWith('http://') || raw.startsWith('https://')) return raw;
                  return `https://${raw}`;
                })()}
                target="_blank"
                rel="noopener noreferrer"
              >
                Kaynağa Git <ExternalLink className="w-4 h-4" />
              </a>
            </Button>
            <Button
              variant="outline"
              className="gap-2"
              disabled={failed || loadingSynapseAi}
              onClick={async () => {
                if (synapseAi?.synapse_ai_score) {
                  setSynapseAiOpen((s) => !s);
                  return;
                }
                try {
                  setLoadingSynapseAi(true);
                  const enriched = await fetchApi(`/articles/${id}?include_synapse_ai=true`);
                  setArticle(enriched);
                  setSynapseAiOpen(true);
                } catch (e) {
                  alert('Synapse AI alınamadı: ' + e.message);
                } finally {
                  setLoadingSynapseAi(false);
                }
              }}
            >
              <Sparkles className="w-4 h-4" />
              {synapseAi?.synapse_ai_score ? 'Synapse AI' : (loadingSynapseAi ? 'Hesaplanıyor…' : 'Synapse AI Hesapla')}
            </Button>
          </div>
        </div>

        {/* İçerik ve AI Özeti */}
        <div className="p-6 md:p-8 grid md:grid-cols-3 gap-8">
          
          {/* Sol Kolon: Özet */}
          <div className="md:col-span-2 space-y-6">
            <section>
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <Zap className="w-5 h-5 text-yellow-500" />
                AI Özeti
              </h2>
              <div className="bg-muted/50 p-4 rounded-lg text-foreground leading-relaxed border border-border/50">
                {failed
                  ? (article.error ? `Analiz tamamlanamadı: ${article.error}` : "Analiz tamamlanamadı.")
                  : (article.summary_tr || "Özet bulunamadı.")}
              </div>
            </section>

            <section>
              <h2 className="text-lg font-semibold flex items-center gap-2 mb-3">
                <FileText className="w-5 h-5 text-muted-foreground" />
                Orijinal Metin (Önizleme)
              </h2>
              <div className="text-sm text-muted-foreground whitespace-pre-wrap leading-relaxed">
                {article.content_preview}...
              </div>
            </section>
          </div>

          {/* Synapse AI (optional) */}
          {synapseAiOpen && synapseAi?.synapse_ai_score != null && (
            <div className="md:col-span-3">
              <div className="bg-card border border-border rounded-xl p-5">
                <div className="flex items-center justify-between gap-3">
                  <div className="flex items-center gap-2">
                    <Sparkles className="w-5 h-5 text-indigo-500" />
                    <h2 className="text-lg font-extrabold text-foreground">Synapse AI Skoru</h2>
                  </div>
                  <Badge variant="outline" className="text-sm">
                    {synapseAi.synapse_ai_score}/100
                  </Badge>
                </div>
                {synapseAi.reasoning_tr && (
                  <p className="mt-3 text-sm text-muted-foreground leading-relaxed">{synapseAi.reasoning_tr}</p>
                )}
                {Array.isArray(synapseAi.key_factors) && synapseAi.key_factors.length > 0 && (
                  <ul className="mt-3 text-sm text-muted-foreground list-disc pl-5 space-y-1">
                    {synapseAi.key_factors.slice(0, 6).map((f, idx) => (
                      <li key={idx}>{f}</li>
                    ))}
                  </ul>
                )}
              </div>
            </div>
          )}

          {/* Sağ Kolon: Çıkarılan Veriler */}
          <div className="space-y-6">
            <div className="bg-gradient-to-b from-secondary/30 to-background border border-border/60 rounded-2xl p-6 shadow-sm">
              <h3 className="font-extrabold text-foreground border-b border-border/50 pb-3 mb-4 uppercase tracking-wider text-sm flex items-center gap-2">
                <Network className="w-4 h-4 text-primary" />
                Analiz Çıktıları
              </h3>
              
              <div className="space-y-5">
                {article.company && (
                  <div>
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1.5 flex items-center gap-1.5"><Building2 className="w-3.5 h-3.5"/> Aktör (Şirket)</div>
                    <div className="font-bold text-foreground text-base bg-background border border-border/50 px-3 py-2 rounded-xl shadow-inner">{article.company}</div>
                  </div>
                )}
                
                {(article.from_location || article.to_location) && (
                  <div>
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1.5 flex items-center gap-1.5"><MapPin className="w-3.5 h-3.5"/> Hareket Yönü</div>
                    <div className="flex items-center gap-2 bg-background border border-border/50 px-3 py-2 rounded-xl shadow-inner overflow-hidden">
                      {article.from_location ? (
                        <div className="font-medium text-destructive line-through truncate flex-1" title={article.from_location}>{article.from_location}</div>
                      ) : (
                        <div className="font-medium text-muted-foreground italic flex-1">Bilinmiyor</div>
                      )}
                      <ArrowLeft className="w-4 h-4 text-muted-foreground rotate-180 flex-shrink-0" />
                      {article.to_location ? (
                        <div className="font-bold text-green-600 dark:text-green-400 truncate flex-1" title={article.to_location}>{article.to_location}</div>
                      ) : (
                        <div className="font-medium text-muted-foreground italic flex-1">Bilinmiyor</div>
                      )}
                    </div>
                  </div>
                )}

                {article.sector && (
                  <div>
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1.5 flex items-center gap-1.5"><Factory className="w-3.5 h-3.5"/> Sektörel Etki</div>
                    <div className="font-bold text-foreground bg-background border border-border/50 px-3 py-2 rounded-xl shadow-inner">{article.sector}</div>
                  </div>
                )}

                {article.timeline && (
                  <div>
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground mb-1.5 flex items-center gap-1.5"><Calendar className="w-3.5 h-3.5"/> Gerçekleşme Zamanı</div>
                    <div className="font-bold text-foreground bg-background border border-border/50 px-3 py-2 rounded-xl shadow-inner">{article.timeline}</div>
                  </div>
                )}

                <div className="pt-4 border-t border-border/50 mt-2">
                  <div className="flex justify-between items-end mb-2">
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold flex items-center gap-1.5">
                      <Network className="w-3.5 h-3.5"/> Synapse Ağı Skoru
                    </div>
                    <span className="text-sm font-black text-indigo-500">{synapseScore}%</span>
                  </div>
                  <div className="w-full h-3 bg-secondary rounded-full overflow-hidden shadow-inner mb-4">
                    <div 
                      className="h-full bg-gradient-to-r from-indigo-400 to-purple-600 rounded-full" 
                      style={{ width: `${synapseScore}%` }}
                    />
                  </div>

                  <div className="flex justify-between items-end mb-2">
                    <div className="text-[10px] uppercase tracking-widest text-muted-foreground font-bold flex items-center gap-1.5">
                      <ShieldAlert className="w-3.5 h-3.5"/> Yapay Zeka Güven Skoru
                    </div>
                    <span className="text-sm font-black text-primary">{Math.round((article.ai_confidence || 0) * 100)}%</span>
                  </div>
                  <div className="w-full h-3 bg-secondary rounded-full overflow-hidden shadow-inner">
                    <div 
                      className="h-full bg-gradient-to-r from-blue-500 to-indigo-600 rounded-full" 
                      style={{ width: `${(article.ai_confidence || 0) * 100}%` }}
                    />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Audit Trail Accordion */}
      {bios.audit_trail && bios.audit_trail.length > 0 && (
        <div className="bg-card border border-border rounded-xl overflow-hidden shadow-sm">
          <button 
            onClick={() => setAuditOpen(!auditOpen)}
            className="w-full flex items-center justify-between p-6 bg-accent/30 hover:bg-accent/50 transition-colors text-left"
          >
            <div className="flex items-center gap-3">
              <ShieldAlert className="w-6 h-6 text-primary" />
              <div>
                <h3 className="text-lg font-bold">Açıklanabilirlik (Synapse Skor Özeti)</h3>
                <p className="text-sm text-muted-foreground font-normal">Sistemin {score} Synapse skoruna nasıl ulaştığının adım adım açıklaması.</p>
              </div>
            </div>
            {auditOpen ? <ChevronUp className="w-5 h-5" /> : <ChevronDown className="w-5 h-5" />}
          </button>
          
          {auditOpen && (
            <div className="p-6 border-t border-border space-y-4 bg-background">
              {bios.audit_trail.map((step, idx) => (
                <div key={idx} className="flex gap-4 p-4 rounded-lg border border-border/60 bg-card">
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-bold">
                    {step.step}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground">{step.title}</h4>
                    <p className="text-sm text-muted-foreground mt-1 font-mono">{step.detail}</p>
                    
                    {/* JSON tarzı ekstra detay gösterimi */}
                    {step.components && (
                      <div className="mt-2 text-xs flex gap-2">
                        {Object.entries(step.components).map(([k,v]) => (
                          <span key={k} className="bg-secondary px-2 py-1 rounded text-secondary-foreground">
                            {k}: {v}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              <div className="mt-6 p-4 rounded-lg bg-green-500/10 border border-green-500/20 flex items-center justify-between">
                <div>
                  <div className="text-sm font-medium text-green-700 dark:text-green-400">Nihai Karar: {bios.label}</div>
                  <div className="text-xs text-green-600/80 dark:text-green-500/80 mt-1">Sistem tavsiyesi: {bios.action}</div>
                </div>
                <div className="text-3xl font-black text-green-600 dark:text-green-400">{score}</div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Synapse Breakdown Accordion */}
      {article.synapse_breakdown && article.synapse_breakdown.length > 0 && (
        <div className="bg-card border border-indigo-500/30 rounded-xl overflow-hidden shadow-sm">
          <button 
            onClick={() => setSynapseOpen(!synapseOpen)}
            className="w-full flex items-center justify-between p-6 bg-indigo-500/5 hover:bg-indigo-500/10 transition-colors text-left"
          >
            <div className="flex items-center gap-3">
              <Network className="w-6 h-6 text-indigo-500" />
              <div>
                <h3 className="text-lg font-bold text-indigo-600 dark:text-indigo-400">Ağ Merkeziyeti (Synapse Skoru Detayları)</h3>
                <p className="text-sm text-muted-foreground font-normal">Bu haberin grafiğimize neden ve nasıl bağlandığı. Kazanılan puanlar ve kaynakları.</p>
              </div>
            </div>
            {synapseOpen ? <ChevronUp className="w-5 h-5 text-indigo-500" /> : <ChevronDown className="w-5 h-5 text-indigo-500" />}
          </button>
          
          {synapseOpen && (
            <div className="p-6 border-t border-indigo-500/20 space-y-4 bg-background">
              {article.synapse_breakdown.map((step, idx) => (
                <div key={idx} className="flex gap-4 p-4 rounded-lg border border-border/60 bg-card items-start">
                  <div className="flex-shrink-0 px-3 py-1.5 rounded-lg bg-indigo-500/10 text-indigo-600 dark:text-indigo-400 font-black text-sm">
                    +{step.points}
                  </div>
                  <div className="flex-1">
                    <h4 className="font-semibold text-foreground">{step.reason}</h4>
                    {step.neighbor && (
                      <p className="text-xs text-muted-foreground mt-1.5 font-mono bg-secondary/50 p-2 rounded-md border border-border/50">
                        Bağlı Düğüm ID: <span className="text-foreground">{step.neighbor}</span>
                      </p>
                    )}
                    <Badge variant="outline" className="mt-2 text-[10px] tracking-widest">{step.type}</Badge>
                  </div>
                </div>
              ))}
              <div className="mt-6 p-4 rounded-lg bg-indigo-500/10 border border-indigo-500/20 flex items-center justify-between">
                <div>
                  <div className="text-sm font-bold text-indigo-700 dark:text-indigo-400">Toplam Synapse Skoru</div>
                  <div className="text-xs text-indigo-600/80 dark:text-indigo-500/80 mt-1">Grafik ağındaki ağırlık</div>
                </div>
                <div className="text-3xl font-black text-indigo-600 dark:text-indigo-400">{synapseScore}</div>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
