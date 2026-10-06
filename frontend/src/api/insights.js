import { useState, useEffect, useCallback, useRef } from 'react';
import { apiClient } from './client';

export const INSIGHT_PERIOD_OPTIONS = [
  { label: 'Today', value: 'today' },
  { label: 'Last 7 Days', value: 'last_7_days' },
  { label: 'Last 30 Days', value: 'last_30_days' },
  { label: 'This Month', value: 'current_month' },
  { label: 'Last Month', value: 'previous_month' },
  { label: 'All Time', value: 'all_time' },
  { label: 'Custom', value: 'custom' },
];

/**
 * Fetch insights data directly from backend /api/v1/insights
 */
export async function getInsights({ period = 'last_30_days', startDate, endDate } = {}) {
  const params = { period };
  if (period === 'custom' && startDate && endDate) {
    params.start_date = startDate;
    params.end_date = endDate;
  }
  const response = await apiClient('/insights', { params });
  return response?.data || response;
}

/**
 * Custom React hook for fetching and refreshing business insights
 */
export function useInsights({ period = 'last_30_days', startDate = '', endDate = '', enabled = true } = {}) {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(enabled);
  const [error, setError] = useState(null);
  const activeRequestId = useRef(0);

  const fetchInsights = useCallback(async () => {
    if (!enabled) {
      setLoading(false);
      return;
    }

    // If custom date range, only trigger when both dates are provided
    if (period === 'custom' && (!startDate || !endDate)) {
      setLoading(false);
      return;
    }

    const currentReq = ++activeRequestId.current;
    setLoading(true);
    setError(null);

    try {
      const result = await getInsights({ period, startDate, endDate });
      if (currentReq === activeRequestId.current) {
        setData(result);
        setError(null);
        setLoading(false);
      }
    } catch (err) {
      if (currentReq === activeRequestId.current) {
        setError(err?.message || 'Failed to load business insights');
        setLoading(false);
      }
    }
  }, [period, startDate, endDate, enabled]);

  useEffect(() => {
    fetchInsights();
  }, [fetchInsights]);

  return {
    insightsData: data,
    summary: data?.summary || { total: 0, critical: 0, warning: 0, info: 0 },
    insights: data?.insights || [],
    periodInfo: data?.period || null,
    generatedAt: data?.generated_at || null,
    loading,
    error,
    refetch: fetchInsights,
  };
}

/**
 * Resolve actionable module route from an insight item
 */
export function getInsightNavigationTarget(insight) {
  if (!insight) return null;

  const { id, category, evidence } = insight;

  // Specific entity deep-links
  if (evidence?.customer_id) {
    return { path: `/customers/${evidence.customer_id}`, label: 'View Customer' };
  }
  if (evidence?.supplier_id) {
    return { path: `/suppliers/${evidence.supplier_id}`, label: 'View Supplier' };
  }
  if (evidence?.product_id) {
    return { path: `/products/${evidence.product_id}`, label: 'View Product' };
  }

  // Domain / Category level links to existing verified routes
  if (id.includes('oos') || id.includes('out_of_stock')) {
    return { path: '/inventory', label: 'Check Inventory' };
  }
  if (id.includes('low') || id.includes('stock')) {
    return { path: '/inventory', label: 'Restock Inventory' };
  }
  if (id.includes('slow')) {
    return { path: '/inventory', label: 'Inspect Stagnant Stock' };
  }
  if (id.includes('inv_concentration')) {
    return { path: '/inventory', label: 'View Inventory' };
  }
  if (id.includes('profit') || id.includes('margin') || category === 'finance') {
    if (id.includes('receivable')) {
      return { path: '/customers', label: 'Review Receivables' };
    }
    if (id.includes('payable')) {
      return { path: '/suppliers', label: 'Review Payables' };
    }
    return { path: '/profit-loss', label: 'View Profit & Loss' };
  }
  if (category === 'sales') {
    return { path: '/orders', label: 'View Orders' };
  }
  if (category === 'customer') {
    return { path: '/customers', label: 'View Customers' };
  }
  if (category === 'supplier') {
    if (id.includes('pending_pos')) {
      return { path: '/purchase-orders', label: 'View Purchase Orders' };
    }
    return { path: '/suppliers', label: 'View Suppliers' };
  }
  if (category === 'data_quality') {
    return { path: '/products', label: 'Update Product Costs' };
  }

  return null;
}
