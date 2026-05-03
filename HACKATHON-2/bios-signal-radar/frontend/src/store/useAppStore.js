import { create } from 'zustand';
import { persist } from 'zustand/middleware';

export const useAppStore = create(
  persist(
    (set) => ({
      // Filters
      filters: {
        scoreMin: 0,
        scoreMax: 100,
        eventType: 'all',
        sourceId: 'all',
        searchQuery: '',
        companyQuery: '',
        sectorQuery: '',
        sortBy: 'score',
        sortOrder: 'desc',
        dateRange: 'all', // all | 24h | 7d
      },
      setFilters: (newFilters) => 
        set((state) => ({ 
          filters: { ...state.filters, ...newFilters } 
        })),
      resetFilters: () => 
        set({ 
          filters: {
            scoreMin: 0,
            scoreMax: 100,
            eventType: 'all',
            sourceId: 'all',
            searchQuery: '',
            companyQuery: '',
            sectorQuery: '',
            sortBy: 'score',
            sortOrder: 'desc',
            dateRange: 'all',
          } 
        }),
      
      // UI State
      sidebarOpen: false,
      toggleSidebar: () => set((state) => ({ sidebarOpen: !state.sidebarOpen })),
      
      // Data flags
      lastRefreshAt: null,
      setLastRefreshAt: (time) => set({ lastRefreshAt: time }),
    }),
    {
      name: 'bios-radar-app-storage',
      partialize: (state) => ({ filters: state.filters }),
    }
  )
);
