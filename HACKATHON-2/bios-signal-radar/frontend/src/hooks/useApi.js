import { useState, useEffect, useCallback } from 'react';
import { fetchApi } from '../lib/api';

export function useArticles(filters, page = 1) {
  const [data, setData] = useState({ articles: [], pagination: {}, summary: {} });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchArticles = useCallback(async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (filters.scoreMin) params.append('min_score', filters.scoreMin);
      if (filters.scoreMax < 100) params.append('max_score', filters.scoreMax);
      if (filters.eventType && filters.eventType !== 'all') params.append('event_type', filters.eventType);
      if (filters.sourceId && filters.sourceId !== 'all') params.append('source_id', filters.sourceId);
      if (filters.searchQuery) params.append('search', filters.searchQuery);
      if (filters.companyQuery) params.append('company', filters.companyQuery);
      if (filters.sectorQuery) params.append('sector', filters.sectorQuery);
      if (filters.sortBy) params.append('sort_by', filters.sortBy);
      if (filters.sortOrder) params.append('sort_order', filters.sortOrder);
      params.append('include_failed', 'true');

      if (filters.dateRange && filters.dateRange !== 'all') {
        const now = new Date();
        const from = new Date(now);
        if (filters.dateRange === '24h') from.setHours(from.getHours() - 24);
        if (filters.dateRange === '7d') from.setDate(from.getDate() - 7);
        params.append('date_from', from.toISOString());
      }
      params.append('page', page);
      params.append('limit', 100);

      const res = await fetchApi(`/articles?${params.toString()}`);
      setData(res);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, [filters, page]);

  useEffect(() => {
    fetchArticles();
  }, [fetchArticles]);

  return { ...data, loading, error, refetch: fetchArticles };
}

export function useRSSSources() {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchSources = useCallback(async () => {
    try {
      const res = await fetchApi('/rss');
      setSources(res.sources || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchSources();
  }, [fetchSources]);

  const addSource = async (url, name) => {
    await fetchApi('/rss', {
      method: 'POST',
      body: JSON.stringify({ url, name })
    });
    await fetchSources();
  };

  const removeSource = async (id) => {
    await fetchApi(`/rss/${id}`, { method: 'DELETE' });
    await fetchSources();
  };

  return { sources, loading, addSource, removeSource, refetch: fetchSources };
}

export function useStats() {
  const [stats, setStats] = useState(null);
  
  const fetchStats = useCallback(async () => {
    try {
      const res = await fetchApi('/stats');
      setStats(res);
    } catch (err) {
      console.error(err);
    }
  }, []);

  useEffect(() => {
    fetchStats();
  }, [fetchStats]);

  return { stats, refetch: fetchStats };
}
