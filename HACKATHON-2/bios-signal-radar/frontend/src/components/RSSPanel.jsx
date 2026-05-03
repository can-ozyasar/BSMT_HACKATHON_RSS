import React, { useState } from 'react';
import { useRSSSources } from '../hooks/useApi';
import { Button } from './ui/button';
import { Plus, Trash2, Rss, AlertCircle, Star, ChevronDown, ChevronUp } from 'lucide-react';
import { fetchApi } from '../lib/api';
import { toast } from 'sonner';

export default function RSSPanel() {
  const { sources, loading, addSource, removeSource, refetch } = useRSSSources();
  const [newUrl, setNewUrl] = useState('');
  const [newName, setNewName] = useState('');
  const [adding, setAdding] = useState(false);
  const [addError, setAddError] = useState('');
  const [showForm, setShowForm] = useState(false);

  const handleAdd = async (e) => {
    e.preventDefault();
    if (!newUrl) return;
    setAdding(true);
    setAddError('');
    try {
      await addSource(newUrl, newName.trim() || '');
      setNewUrl('');
      setNewName('');
      setShowForm(false);
      // Kaynak eklenir eklenmez haberlerini otomatik çek
      toast.promise(
        fetchApi('/refresh/sync', { method: 'POST', body: JSON.stringify({}) }),
        {
          loading: 'Yeni kaynak taranıyor...',
          success: 'Haberler güncellendi!',
          error: 'Tarama sırasında hata oluştu.',
        }
      );
    } catch (err) {
      const msg = err.message || 'RSS kaynağı eklenemedi.';
      setAddError(msg);
    } finally {
      setAdding(false);
    }
  };

  return (
    <div className="flex flex-col space-y-5">
      <div>
        <div className="flex items-center justify-between mb-1">
          <h2 className="text-lg font-bold text-foreground flex items-center gap-2">
            <Rss className="w-5 h-5 text-primary" />
            Veri Kaynakları
          </h2>
          <span className="bg-primary/10 text-primary text-xs font-bold px-2 py-0.5 rounded-md">
            {sources.length} Aktif
          </span>
        </div>
        <p className="text-xs font-medium text-muted-foreground leading-snug">
          Avrupa genelinde tarama yapılan endüstriyel haber ağları.
        </p>
      </div>

      {/* Add source toggle */}
      <button
        type="button"
        onClick={() => { setShowForm(s => !s); setAddError(''); }}
        className="flex items-center justify-between w-full px-3 py-2 rounded-xl border border-dashed border-primary/40 text-primary hover:bg-primary/5 transition-colors text-sm font-semibold"
      >
        <span className="flex items-center gap-2"><Plus className="w-4 h-4" /> Yeni RSS Kaynağı Ekle</span>
        {showForm ? <ChevronUp className="w-4 h-4" /> : <ChevronDown className="w-4 h-4" />}
      </button>

      {showForm && (
        <form onSubmit={handleAdd} className="flex flex-col gap-2 p-3 rounded-xl bg-secondary/30 border border-border/50">
          <input
            type="text"
            value={newName}
            onChange={(e) => setNewName(e.target.value)}
            placeholder="Kaynak adı (isteğe bağlı)"
            className="flex h-9 w-full rounded-lg border border-input bg-background/80 px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 transition-all"
          />
          <div className="flex gap-2">
            <input
              type="url"
              value={newUrl}
              onChange={(e) => { setNewUrl(e.target.value); setAddError(''); }}
              placeholder="https://...rss"
              className="flex h-9 w-full rounded-lg border border-input bg-background/80 px-3 py-2 text-sm placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary/50 transition-all"
              required
            />
            <Button type="submit" disabled={adding} size="sm" className="rounded-lg px-3 flex-shrink-0">
              {adding ? '...' : <Plus className="w-4 h-4" />}
            </Button>
          </div>
          {addError && (
            <div className="flex items-start gap-2 text-xs text-destructive bg-destructive/10 border border-destructive/20 rounded-lg px-3 py-2">
              <AlertCircle className="w-3.5 h-3.5 mt-0.5 flex-shrink-0" />
              <span>{addError}</span>
            </div>
          )}
        </form>
      )}

      {loading ? (
        <div className="text-sm font-medium text-muted-foreground animate-pulse text-center py-6">Kaynaklar yükleniyor...</div>
      ) : (
        <div className="bg-card/40 backdrop-blur border border-border/50 rounded-2xl overflow-hidden shadow-sm">
          <div className="max-h-[350px] overflow-y-auto p-2 space-y-1.5 custom-scrollbar">
            {sources.map(source => (
              <div key={source.id} className="group flex items-center justify-between p-2.5 rounded-xl hover:bg-card hover:shadow-sm border border-transparent hover:border-border/50 transition-all">
                <div className="overflow-hidden flex-1 mr-2">
                  <div className="text-sm font-semibold text-foreground truncate" title={source.name || source.url}>
                    {source.name || source.url.replace(/^https?:\/\/(www\.)?/, '')}
                  </div>
                  <div className="flex items-center gap-2 mt-0.5">
                    {source.status === 'error' ? (
                      <span className="text-[10px] font-bold text-destructive bg-destructive/10 px-1.5 rounded uppercase tracking-wider flex items-center gap-1"><AlertCircle className="w-2.5 h-2.5"/> Hata</span>
                    ) : (
                      <span className="text-[10px] font-bold text-green-500 bg-green-500/10 px-1.5 rounded uppercase tracking-wider">Aktif</span>
                    )}
                    <span className="text-[10px] font-semibold text-muted-foreground">
                      Son çekim: {source.last_fetched_at ? new Date(source.last_fetched_at).toLocaleString('tr-TR', { day: '2-digit', month: 'short', hour: '2-digit', minute: '2-digit' }) : '—'}
                    </span>
                  </div>
                  {source.status === 'error' && source.error_message && (
                    <div className="text-[11px] text-destructive/90 mt-1 line-clamp-2">
                      {source.error_message}
                    </div>
                  )}
                </div>
                <div className="flex items-center gap-1">
                  <Button
                    variant="ghost"
                    size="icon"
                    className={`h-8 w-8 opacity-0 group-hover:opacity-100 transition-all ${
                      source.starred ? 'text-yellow-500 hover:text-yellow-600' : 'text-muted-foreground hover:text-yellow-500'
                    }`}
                    onClick={async () => {
                      try {
                        await fetchApi(`/rss/${source.id}`, { method: 'PATCH', body: JSON.stringify({ starred: !source.starred }) });
                        await refetch();
                      } catch (e) {
                        alert('Bildirim işaretleme hatası: ' + e.message);
                      }
                    }}
                    title={source.starred ? 'Bildirim: Açık' : 'Bildirim: Kapalı'}
                  >
                    <Star className={`w-4 h-4 ${source.starred ? 'fill-current' : ''}`} />
                  </Button>
                  <Button 
                    variant="ghost" 
                    size="icon" 
                    className="h-8 w-8 text-muted-foreground opacity-0 group-hover:opacity-100 hover:text-destructive hover:bg-destructive/10 transition-all"
                    onClick={() => removeSource(source.id)}
                    title="Kaynağı Sil"
                  >
                    <Trash2 className="w-4 h-4" />
                  </Button>
                </div>
              </div>
            ))}
            {sources.length === 0 && (
              <div className="text-sm font-medium text-muted-foreground text-center py-8">
                Henüz kaynak eklenmedi.
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
