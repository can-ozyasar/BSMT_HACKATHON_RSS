import { useCallback, useEffect, useState } from 'react';
import { fetchApi } from '../lib/api';

export function useAnomalies() {
  const [anomalies, setAnomalies] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchAnomalies = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchApi('/anomalies');
      setAnomalies(res.anomalies || []);
      setError(null);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchAnomalies();
  }, [fetchAnomalies]);

  return { anomalies, loading, error, refetch: fetchAnomalies };
}

