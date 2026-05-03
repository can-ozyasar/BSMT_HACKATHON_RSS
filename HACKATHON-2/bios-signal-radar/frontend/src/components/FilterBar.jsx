import React from 'react';
import { useAppStore } from '../store/useAppStore';
import { Search, FilterX } from 'lucide-react';
import { Button } from './ui/button';
import { useRSSSources } from '../hooks/useApi';

export default function FilterBar() {
  const { filters, setFilters, resetFilters } = useAppStore();
  const { sources } = useRSSSources();

  const handleSearch = (e) => {
    setFilters({ searchQuery: e.target.value });
  };

  const handleCompany = (e) => {
    setFilters({ companyQuery: e.target.value });
  };

  const handleSector = (e) => {
    setFilters({ sectorQuery: e.target.value });
  };

  const handleScoreChange = (e) => {
    const val = e.target.value;
    if (val === "exact_0") {
      setFilters({ scoreMin: 0, scoreMax: 0 });
    } else {
      setFilters({ scoreMin: Number(val), scoreMax: 100 });
    }
  };

  const handleSortChange = (e) => {
    const [sortBy, sortOrder] = e.target.value.split("-");
    setFilters({ sortBy, sortOrder });
  };

  const handleEventChange = (e) => {
    setFilters({ eventType: e.target.value });
  };

  const handleSourceChange = (e) => {
    setFilters({ sourceId: e.target.value });
  };

  const handleDateRangeChange = (e) => {
    setFilters({ dateRange: e.target.value });
  };

  const selectCls = "bg-background border border-input rounded-md text-sm py-2 pl-3 pr-8 focus:outline-none focus:ring-2 focus:ring-primary/50 w-full";

  return (
    <div className="bg-card border border-border rounded-xl p-4 space-y-3">
      {/* Üst satır: Arama + Şirket + Sektör */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1 min-w-0">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-muted-foreground" />
          <input
            type="text"
            value={filters.searchQuery}
            onChange={handleSearch}
            placeholder="Şirket, başlık veya içerikte ara..."
            className="w-full pl-9 pr-4 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
          />
        </div>
        <input
          type="text"
          value={filters.companyQuery || ''}
          onChange={handleCompany}
          placeholder="Şirket"
          className="sm:w-36 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
        <input
          type="text"
          value={filters.sectorQuery || ''}
          onChange={handleSector}
          placeholder="Sektör"
          className="sm:w-36 px-3 py-2 bg-background border border-input rounded-md text-sm focus:outline-none focus:ring-2 focus:ring-primary/50"
        />
      </div>

      {/* Alt satır: Filtreler */}
      <div className="flex flex-wrap gap-3 items-center">
        <div className="flex items-center gap-1.5 min-w-0">
          <label className="text-xs font-semibold whitespace-nowrap text-muted-foreground">Skor:</label>
          <select
            value={filters.scoreMax === 0 ? "exact_0" : filters.scoreMin}
            onChange={handleScoreChange}
            className={selectCls + " !w-auto"}
          >
            <option value="0">Tümü</option>
            <option value="50">50+</option>
            <option value="65">65+</option>
            <option value="80">80+</option>
            <option value="exact_0">Yalnız 0</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs font-semibold whitespace-nowrap text-muted-foreground">Sırala:</label>
          <select
            value={`${filters.sortBy || 'score'}-${filters.sortOrder || 'desc'}`}
            onChange={handleSortChange}
            className={selectCls + " !w-auto"}
          >
            <option value="score-desc">En Yüksek</option>
            <option value="published_at-desc">En Yeni</option>
            <option value="published_at-asc">En Eski</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs font-semibold whitespace-nowrap text-muted-foreground">Kaynak:</label>
          <select
            value={filters.sourceId}
            onChange={handleSourceChange}
            className={selectCls + " !w-auto max-w-[140px]"}
          >
            <option value="all">Tümü</option>
            {(sources || []).map((s) => (
              <option key={s.id} value={s.id}>{(s.name || s.url).slice(0, 20)}</option>
            ))}
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs font-semibold whitespace-nowrap text-muted-foreground">Olay:</label>
          <select
            value={filters.eventType}
            onChange={handleEventChange}
            className={selectCls + " !w-auto"}
          >
            <option value="all">Tümü</option>
            <option value="relocation">Taşınma</option>
            <option value="expansion">Genişleme</option>
            <option value="new_plant">Yeni Tesis</option>
            <option value="closure">Kapanış</option>
            <option value="tender">İhale</option>
          </select>
        </div>

        <div className="flex items-center gap-1.5">
          <label className="text-xs font-semibold whitespace-nowrap text-muted-foreground">Tarih:</label>
          <select
            value={filters.dateRange || 'all'}
            onChange={handleDateRangeChange}
            className={selectCls + " !w-auto"}
          >
            <option value="all">Hepsi</option>
            <option value="24h">Son 24s</option>
            <option value="7d">Son 7g</option>
          </select>
        </div>

        <Button variant="ghost" size="icon" onClick={resetFilters} title="Filtreleri Temizle" className="flex-shrink-0">
          <FilterX className="w-4 h-4 text-muted-foreground" />
        </Button>
      </div>
    </div>
  );
}
