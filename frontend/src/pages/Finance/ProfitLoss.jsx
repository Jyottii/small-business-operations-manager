import { useState, useEffect, useCallback } from 'react';
import { 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  LineChart, 
  Line,
  Legend
} from 'recharts';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { LoadingState, ErrorState } from '../../components/ui/States';
import { apiClient } from '../../api/client';
import { RefreshCw, DollarSign, TrendingUp, AlertCircle } from 'lucide-react';

export default function ProfitLoss() {
  const [period, setPeriod] = useState('last_30_days');
  const [financial, setFinancial] = useState(null);
  const [summary, setSummary] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const fetchFinancialData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const [finRes, sumRes] = await Promise.all([
        apiClient(`/analytics/financial?period=${period}`),
        apiClient(`/analytics/summary?period=${period}`),
      ]);
      setFinancial(finRes?.data || finRes);
      setSummary(sumRes?.data || sumRes);
    } catch (err) {
      setError(err?.message || 'Failed to load Profit & Loss data');
    } finally {
      setLoading(false);
    }
  }, [period]);

  useEffect(() => {
    fetchFinancialData();
  }, [fetchFinancialData]);

  const formatCurrency = (val) => `$${Number(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatPercent = (val) => `${Number(val || 0).toFixed(1)}%`;

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <ErrorState title="Financial Analytics Error" description={error} onRetry={fetchFinancialData} />
      </div>
    );
  }

  const timeline = summary?.recent_trend || [];
  const chartData = timeline.map(t => ({
    date: t.date,
    revenue: t.revenue,
    expenses: t.expenses,
    profit: t.revenue - t.expenses
  }));

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-8">
      {/* Header and Controls */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Profit & Loss Statement</h1>
          <p className="text-sm text-gray-500">Authoritative income and expense analysis.</p>
        </div>
        <div className="flex items-center gap-2">
          <select 
            value={period} 
            onChange={(e) => setPeriod(e.target.value)}
            className="border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 text-xs sm:text-sm bg-white"
          >
            <option value="today">Today</option>
            <option value="last_7_days">Last 7 Days</option>
            <option value="last_30_days">Last 30 Days</option>
            <option value="current_month">Current Month</option>
            <option value="previous_month">Previous Month</option>
            <option value="all_time">All Time</option>
          </select>
          <button
            onClick={fetchFinancialData}
            disabled={loading}
            className="p-2 border border-gray-300 rounded-md hover:bg-gray-50 text-gray-600 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin text-blue-600' : ''} />
          </button>
        </div>
      </div>

      {/* KPI Highlights */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="bg-blue-50 border-blue-100">
          <CardBody className="p-4">
            <p className="text-xs font-semibold uppercase text-blue-800">Total Sales</p>
            {loading ? (
              <div className="h-8 w-28 bg-blue-200/50 animate-pulse rounded mt-1" />
            ) : (
              <h3 className="text-2xl font-bold text-blue-900 mt-1">{formatCurrency(financial?.total_sales)}</h3>
            )}
            <p className="text-xs text-blue-600 mt-1">Cash In: {formatCurrency(financial?.collected_payments)}</p>
          </CardBody>
        </Card>

        <Card className="bg-amber-50 border-amber-100">
          <CardBody className="p-4">
            <p className="text-xs font-semibold uppercase text-amber-800">Cost of Goods (COGS)</p>
            {loading ? (
              <div className="h-8 w-28 bg-amber-200/50 animate-pulse rounded mt-1" />
            ) : (
              <h3 className="text-2xl font-bold text-amber-900 mt-1">{formatCurrency(financial?.cogs)}</h3>
            )}
            <p className="text-xs text-amber-600 mt-1">Direct item purchase costs</p>
          </CardBody>
        </Card>

        <Card className="bg-emerald-50 border-emerald-100">
          <CardBody className="p-4">
            <p className="text-xs font-semibold uppercase text-emerald-800">Gross Profit</p>
            {loading ? (
              <div className="h-8 w-28 bg-emerald-200/50 animate-pulse rounded mt-1" />
            ) : (
              <h3 className="text-2xl font-bold text-emerald-900 mt-1">{formatCurrency(financial?.gross_profit)}</h3>
            )}
            <p className="text-xs text-emerald-600 mt-1">Margin: {formatPercent(financial?.gross_margin_percentage)}</p>
          </CardBody>
        </Card>

        <Card className="bg-purple-50 border-purple-100">
          <CardBody className="p-4">
            <p className="text-xs font-semibold uppercase text-purple-800">Net Profit</p>
            {loading ? (
              <div className="h-8 w-28 bg-purple-200/50 animate-pulse rounded mt-1" />
            ) : (
              <h3 className="text-2xl font-bold text-purple-900 mt-1">{formatCurrency(financial?.net_profit)}</h3>
            )}
            <p className="text-xs text-purple-600 mt-1">Net Margin: {formatPercent(financial?.net_margin_percentage)}</p>
          </CardBody>
        </Card>
      </div>

      {/* Visual Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Revenue vs Expenses" />
          <CardBody>
            {loading ? (
              <div className="h-72 flex items-center justify-center text-gray-400">
                <RefreshCw className="animate-spin h-6 w-6 mr-2" /> Loading chart...
              </div>
            ) : chartData.length === 0 ? (
              <div className="h-72 flex items-center justify-center text-gray-400 text-sm">
                No financial transactions recorded in this period.
              </div>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                    <XAxis dataKey="date" tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                    <YAxis tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                    <Tooltip 
                      formatter={(val) => [`$${Number(val).toFixed(2)}`]}
                      contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Bar dataKey="revenue" fill="#3B82F6" name="Revenue" radius={[4, 4, 0, 0]} />
                    <Bar dataKey="expenses" fill="#EF4444" name="Expenses" radius={[4, 4, 0, 0]} />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Net Profit Trend" />
          <CardBody>
            {loading ? (
              <div className="h-72 flex items-center justify-center text-gray-400">
                <RefreshCw className="animate-spin h-6 w-6 mr-2" /> Loading chart...
              </div>
            ) : chartData.length === 0 ? (
              <div className="h-72 flex items-center justify-center text-gray-400 text-sm">
                No financial transactions recorded in this period.
              </div>
            ) : (
              <div className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={chartData} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                    <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                    <XAxis dataKey="date" tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                    <YAxis tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                    <Tooltip 
                      formatter={(val) => [`$${Number(val).toFixed(2)}`]}
                      contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }}
                    />
                    <Legend wrapperStyle={{ fontSize: '12px' }} />
                    <Line type="monotone" dataKey="profit" stroke="#10B981" strokeWidth={2.5} name="Operating Profit" dot={{ r: 3 }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* Detailed Income Statement Structure */}
      <Card>
        <CardHeader 
          title="Income Statement Breakdown" 
          action={
            <span className="text-xs text-gray-500">
              {financial?.note || 'Authoritative backend calculations'}
            </span>
          }
        />
        <CardBody className="p-0">
          <div className="p-6 space-y-6">
            <div>
              <h3 className="text-sm font-bold text-gray-900 border-b pb-2 mb-3 uppercase tracking-wider">
                1. Gross Revenue
              </h3>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Product & Customer Sales</span>
                <span className="font-medium">{formatCurrency(financial?.total_sales)}</span>
              </div>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Customer Cash Collections</span>
                <span className="font-medium text-green-700">{formatCurrency(financial?.collected_payments)}</span>
              </div>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Outstanding Receivables</span>
                <span className="font-medium text-amber-700">{formatCurrency(financial?.outstanding_receivables)}</span>
              </div>
              <div className="flex justify-between py-2 text-sm font-bold border-t mt-2">
                <span className="text-gray-900">Total Net Recognized Revenue</span>
                <span className="text-gray-900">{formatCurrency(financial?.total_sales)}</span>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 border-b pb-2 mb-3 uppercase tracking-wider">
                2. Cost of Goods Sold (COGS)
              </h3>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Direct Product Inventory Purchase Costs</span>
                <span className="font-medium">{formatCurrency(financial?.cogs)}</span>
              </div>
              <div className="flex justify-between py-2 text-sm font-bold border-t mt-2">
                <span className="text-gray-900">Gross Operating Profit</span>
                <span className="text-emerald-700 font-bold">{formatCurrency(financial?.gross_profit)}</span>
              </div>
            </div>

            <div>
              <h3 className="text-sm font-bold text-gray-900 border-b pb-2 mb-3 uppercase tracking-wider">
                3. Operating Expenses & Returns
              </h3>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Recorded Business Expenses</span>
                <span className="font-medium">{formatCurrency(financial?.total_expenses)}</span>
              </div>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Processed Returns & Refunds</span>
                <span className="font-medium text-red-600">{formatCurrency(financial?.total_refunds)}</span>
              </div>
              <div className="flex justify-between py-1 text-sm">
                <span className="text-gray-600">Supplier Outstanding Payables</span>
                <span className="font-medium text-red-700">{formatCurrency(financial?.outstanding_payables)}</span>
              </div>
            </div>

            <div className="bg-gray-50 p-4 rounded-lg flex justify-between items-center border border-gray-200">
              <div>
                <span className="text-lg font-bold text-gray-900 block">Net Bottom-Line Profit</span>
                <span className="text-xs text-gray-500">Margin: {formatPercent(financial?.net_margin_percentage)}</span>
              </div>
              <span className={`text-2xl font-bold ${(financial?.net_profit || 0) >= 0 ? 'text-emerald-600' : 'text-red-600'}`}>
                {formatCurrency(financial?.net_profit)}
              </span>
            </div>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}
