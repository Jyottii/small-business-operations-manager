import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from './client';

export function useApi(endpoint, optionsOrDeps = [], maybeDeps = []) {
  // Support both useApi(endpoint, dependencies) and useApi(endpoint, options, dependencies)
  const isOptions = typeof optionsOrDeps === 'object' && !Array.isArray(optionsOrDeps);
  const options = isOptions ? optionsOrDeps : {};
  const dependencies = isOptions ? maybeDeps : optionsOrDeps;

  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(Boolean(endpoint));
  const [error, setError] = useState(null);
  const [pagination, setPagination] = useState(null);

  // Keep track of the active request to avoid stale/out-of-order responses
  const activeRequestId = useRef(0);

  const fetchData = useCallback(async (overrideOptions = {}) => {
    if (!endpoint) {
      setLoading(false);
      return;
    }

    const currentRequestId = ++activeRequestId.current;
    setLoading(true);
    setError(null);

    try {
      const mergedOptions = { ...options, ...overrideOptions };
      const result = await apiClient(endpoint, mergedOptions);
      
      // Ignore if a newer request was dispatched in the meantime
      if (currentRequestId === activeRequestId.current) {
        setData(result?.data !== undefined ? result.data : result);
        if (result?.pagination) {
          setPagination(result.pagination);
        }
        setError(null);
        setLoading(false);
      }
    } catch (err) {
      if (currentRequestId === activeRequestId.current) {
        setError(err?.message || "Failed to load data");
        setLoading(false);
      }
    }
  }, [endpoint, JSON.stringify(options?.params)]);

  useEffect(() => {
    fetchData();
  }, [fetchData, ...dependencies]);

  return { data, loading, error, pagination, refetch: fetchData, setData };
}
