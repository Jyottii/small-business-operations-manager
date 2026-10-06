import { useState, useEffect, useCallback } from 'react';
import { Link } from 'react-router-dom';
import { 
  DollarSign, 
  ShoppingCart, 
  TrendingUp, 
  Package, 
  Users, 
  Truck, 
  AlertTriangle, 
  RefreshCw, 
  Calendar, 
  CreditCard, 
  RotateCcw, 
  Building, 
  FileText,
  CheckCircle2,
  AlertCircle,
  HelpCircle,
  Clock,
  Sparkles,
  ArrowRight
} from 'lucide-react';
import { 
  ResponsiveContainer, 
  LineChart, 
  Line, 
  BarChart, 
  Bar, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  Legend 
} from 'recharts';
import { Card, CardHeader, CardBody } from '../components/ui/Card';
import { LoadingState, ErrorState, EmptyState } from '../components/ui/States';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../api/client';
import { InsightsSummaryCards } from '../components/insights/InsightsSummaryCards';
import { InsightsList } from '../components/insights/InsightsList';
import { GoalsAndCalendarWidget } from '../components/dashboard/GoalsAndCalendarWidget';

export default function Dashboard() {
  const { currentUser, role } = useAuth();

  // If Staff, render tailored operational Hub
  if (role === 'Staff') {
    return <StaffOperationalHub user={currentUser} />;
  }

  // Executive BI Dashboard for Owner, Admin, Manager
  return <ExecutiveBiDashboard user={currentUser} />;
}

// ----------------------------------------------------------------------------
// STAFF OPERATIONAL HUB (Role-Appropriate View)
// ----------------------------------------------------------------------------
function StaffOperationalHub({ user }) {
  const todayStr = new Date().toLocaleDateString('en-US', { 
    weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' 
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-indigo-700 rounded-xl p-6 text-white shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
          <div>
            <span className="inline-block px-2.5 py-0.5 rounded-full text-xs font-semibold bg-white/20 text-white mb-2">
              Staff Operational Station
            </span>
            <h1 className="text-2xl sm:text-3xl font-bold">Welcome back, {user?.name || 'Team Member'}!</h1>
            <p className="text-blue-100 text-sm mt-1">{todayStr}</p>
          </div>
          <Link
            to="/sales"
            className="inline-flex items-center justify-center gap-2 px-5 py-3 bg-white text-blue-700 font-bold rounded-lg shadow hover:bg-blue-50 transition-colors text-sm"
          >
            <ShoppingCart size={18} />
            Launch POS Register
          </Link>
        </div>
      </div>

      {/* Quick Action Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <Link 
          to="/sales"
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all group"
        >
          <div className="w-12 h-12 rounded-lg bg-blue-50 text-blue-600 flex items-center justify-center mb-4 group-hover:bg-blue-600 group-hover:text-white transition-colors">
            <ShoppingCart size={24} />
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-blue-600">New Sale (POS)</h3>
          <p className="text-xs text-gray-500 mt-1">Scan items, apply discounts, and complete customer sales.</p>
        </Link>

        <Link 
          to="/orders"
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all group"
        >
          <div className="w-12 h-12 rounded-lg bg-indigo-50 text-indigo-600 flex items-center justify-center mb-4 group-hover:bg-indigo-600 group-hover:text-white transition-colors">
            <FileText size={24} />
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-indigo-600">Customer Orders</h3>
          <p className="text-xs text-gray-500 mt-1">Search order status, print receipts, and manage customer orders.</p>
        </Link>

        <Link 
          to="/inventory"
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all group"
        >
          <div className="w-12 h-12 rounded-lg bg-amber-50 text-amber-600 flex items-center justify-center mb-4 group-hover:bg-amber-600 group-hover:text-white transition-colors">
            <Package size={24} />
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-amber-600">Check Inventory</h3>
          <p className="text-xs text-gray-500 mt-1">Verify current stock on hand across store and warehouses.</p>
        </Link>

        <Link 
          to="/customers"
          className="p-5 bg-white rounded-xl border border-gray-200 hover:border-blue-400 hover:shadow-md transition-all group"
        >
          <div className="w-12 h-12 rounded-lg bg-emerald-50 text-emerald-600 flex items-center justify-center mb-4 group-hover:bg-emerald-600 group-hover:text-white transition-colors">
            <Users size={24} />
          </div>
          <h3 className="font-semibold text-gray-900 group-hover:text-emerald-600">Customers Directory</h3>
          <p className="text-xs text-gray-500 mt-1">Lookup customer accounts, credit balances, and contact info.</p>
        </Link>
      </div>

      {/* Operational Guidelines */}
      <Card>
        <CardHeader title="Daily Shift Best Practices" />
        <CardBody className="space-y-3 text-sm text-gray-600">
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span>Always confirm customer details before completing sales with store credit.</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span>Ensure all received returns are recorded immediately with reason and quantity.</span>
          </div>
          <div className="flex items-start gap-3">
            <CheckCircle2 className="h-5 w-5 text-green-500 flex-shrink-0 mt-0.5" />
            <span>Report any low-stock alerts to your shift manager for replenishment.</span>
          </div>
        </CardBody>
      </Card>
    </div>
  );
}

// ----------------------------------------------------------------------------
// EXECUTIVE BI DASHBOARD (Owner, Admin, Manager)
// ----------------------------------------------------------------------------
function ExecutiveBiDashboard({ user }) {
  const [period, setPeriod] = useState('last_30_days');
  const [customStart, setCustomStart] = useState('');
  const [customEnd, setCustomEnd] = useState('');
  const [dateError, setDateError] = useState(null);

  // Analytics Datasets State
  const [summary, setSummary] = useState(null);
  const [salesData, setSalesData] = useState(null);
  const [prodData, setProdData] = useState(null);
  const [custData, setCustData] = useState(null);
  const [invData, setInvData] = useState(null);
  const [purchData, setPurchData] = useState(null);
  const [insightsData, setInsightsData] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState('all');

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Fetch all analytics datasets
  const fetchDashboardData = useCallback(async () => {
    setLoading(true);
    setError(null);
    setDateError(null);

    let queryParams = `period=${period}`;
    if (period === 'custom') {
      if (!customStart || !customEnd) {
        setLoading(false);
        return;
      }
      if (new Date(customStart) > new Date(customEnd)) {
        setDateError('Start date must be before or equal to End date');
        setLoading(false);
        return;
      }
      queryParams += `&start_date=${encodeURIComponent(customStart)}&end_date=${encodeURIComponent(customEnd)}`;
    }

    try {
      // Parallel fetch for optimal load performance
      const [sumRes, salesRes, prodRes, custRes, invRes, purchRes, insRes] = await Promise.all([
        apiClient(`/analytics/summary?${queryParams}`),
        apiClient(`/analytics/sales?${queryParams}`),
        apiClient(`/analytics/products?${queryParams}&limit=10`),
        apiClient(`/analytics/customers?${queryParams}&limit=5`),
        apiClient(`/analytics/inventory?days=30`),
        apiClient(`/analytics/purchases?${queryParams}`),
        apiClient(`/insights?${queryParams}`),
      ]);

      setSummary(sumRes?.data || sumRes);
      setSalesData(salesRes?.data || salesRes);
      setProdData(prodRes?.data || prodRes);
      setCustData(custRes?.data || custRes);
      setInvData(invRes?.data || invRes);
      setPurchData(purchRes?.data || purchRes);
      setInsightsData(insRes?.data || insRes);
    } catch (err) {
      setError(err?.message || 'Failed to load Business Intelligence data');
    } finally {
      setLoading(false);
    }
  }, [period, customStart, customEnd]);

  useEffect(() => {
    fetchDashboardData();
  }, [fetchDashboardData]);

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    if (newPeriod !== 'custom') {
      setDateError(null);
    }
  };

  const formatCurrency = (val) => `$${Number(val || 0).toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
  const formatNumber = (val) => Number(val || 0).toLocaleString('en-US');
  const formatPercent = (val) => `${Number(val || 0).toFixed(1)}%`;

  const periodOptions = [
    { label: 'Today', value: 'today' },
    { label: 'Last 7 Days', value: 'last_7_days' },
    { label: 'Last 30 Days', value: 'last_30_days' },
    { label: 'This Month', value: 'current_month' },
    { label: 'Last Month', value: 'previous_month' },
    { label: 'All Time', value: 'all_time' },
    { label: 'Custom', value: 'custom' },
  ];

  if (error) {
    return (
      <div className="max-w-7xl mx-auto py-8">
        <ErrorState 
          title="Analytics Service Unavailable" 
          description={error} 
          onRetry={fetchDashboardData} 
        />
      </div>
    );
  }

  const kpis = summary?.sales || {};
  const fin = summary?.financial || {};
  const inv = summary?.inventory || {};
  const returns = summary?.returns || {};
  const timeline = salesData?.timeline || summary?.recent_trend || [];

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* ------------------------------------------------------------- */}
      {/* TOP CONTROLS & DATE FILTER BAR */}
      {/* ------------------------------------------------------------- */}
      <div className="bg-white p-4 rounded-xl border border-gray-200 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Business Intelligence</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-blue-100 text-blue-800 border border-blue-200">
              Executive View
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-0.5">
            Real-time business performance, inventory health, and financial signals.
          </p>
        </div>

        {/* Date Period Selector */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1">
            {periodOptions.map((opt) => (
              <button
                key={opt.value}
                onClick={() => handlePeriodChange(opt.value)}
                className={`px-3 py-1 text-xs font-medium rounded-md transition-all ${
                  period === opt.value
                    ? 'bg-white text-blue-600 shadow-sm font-semibold'
                    : 'text-gray-600 hover:text-gray-900'
                }`}
              >
                {opt.label}
              </button>
            ))}
          </div>

          <button
            onClick={fetchDashboardData}
            disabled={loading}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors"
            title="Refresh Data"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin text-blue-600' : ''} />
          </button>
        </div>
      </div>

      {/* Custom Date Picker (if Custom selected) */}
      {period === 'custom' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <label className="font-semibold text-gray-700">Start Date:</label>
            <input 
              type="date" 
              value={customStart} 
              onChange={(e) => setCustomStart(e.target.value)}
              className="px-2.5 py-1.5 border border-gray-300 rounded bg-white"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="font-semibold text-gray-700">End Date:</label>
            <input 
              type="date" 
              value={customEnd} 
              onChange={(e) => setCustomEnd(e.target.value)}
              className="px-2.5 py-1.5 border border-gray-300 rounded bg-white"
            />
          </div>
          <button
            onClick={fetchDashboardData}
            className="px-3 py-1.5 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition-colors"
          >
            Apply Filter
          </button>
          {dateError && (
            <span className="text-red-600 font-medium flex items-center gap-1">
              <AlertCircle size={14} /> {dateError}
            </span>
          )}
        </div>
      )}

      {/* ------------------------------------------------------------- */}
      {/* 1. EXECUTIVE KPI METRIC CARDS (8 KPIs) */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <KpiCard
          title="Total Revenue"
          value={formatCurrency(kpis?.total_revenue)}
          subtitle={`${formatNumber(kpis?.total_orders)} orders in period`}
          icon={DollarSign}
          color="blue"
          loading={loading}
        />
        <KpiCard
          title="Total Orders"
          value={formatNumber(kpis?.total_orders)}
          subtitle={`${kpis?.completed_orders_count || 0} completed`}
          icon={ShoppingCart}
          color="indigo"
          loading={loading}
        />
        <KpiCard
          title="Average Order Value"
          value={formatCurrency(kpis?.average_order_value)}
          subtitle="Revenue per transaction"
          icon={TrendingUp}
          color="teal"
          loading={loading}
        />
        <KpiCard
          title="Inventory Value"
          value={formatCurrency(inv?.total_inventory_value)}
          subtitle={`${formatNumber(inv?.total_inventory_units)} units in stock`}
          icon={Package}
          color="amber"
          loading={loading}
        />
        <KpiCard
          title="Gross Profit"
          value={formatCurrency(fin?.gross_profit)}
          subtitle={`COGS: ${formatCurrency(fin?.cogs)}`}
          icon={DollarSign}
          color="emerald"
          loading={loading}
        />
        <KpiCard
          title="Gross Margin"
          value={formatPercent(fin?.gross_margin_percentage)}
          subtitle="Profitability before opex"
          icon={TrendingUp}
          color="emerald"
          loading={loading}
        />
        <KpiCard
          title="Net Profit"
          value={formatCurrency(fin?.net_profit)}
          subtitle={`Expenses: ${formatCurrency(fin?.total_expenses)}`}
          icon={TrendingUp}
          color="purple"
          loading={loading}
        />
        <KpiCard
          title="Net Margin"
          value={formatPercent(fin?.net_margin_percentage)}
          subtitle="Net return on sales"
          icon={TrendingUp}
          color="purple"
          loading={loading}
        />
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 2. SMART BUSINESS INSIGHTS */}
      {/* ------------------------------------------------------------- */}
      <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm space-y-4">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 border-b border-gray-100 pb-3">
          <div className="flex items-center gap-3">
            <span className="p-2.5 rounded-xl bg-purple-50 text-purple-600 flex-shrink-0">
              <Sparkles size={20} />
            </span>
            <div>
              <div className="flex items-center gap-2">
                <h2 className="text-lg font-bold text-gray-900">Smart Business Insights</h2>
                <span className="text-[10px] font-bold uppercase tracking-wider px-2 py-0.5 rounded-full bg-purple-100 text-purple-800 border border-purple-200">
                  Rules Engine
                </span>
              </div>
              <p className="text-xs text-gray-500">
                Automated detection of operational stockouts, margin compression, and working capital bottlenecks.
              </p>
            </div>
          </div>
          <Link
            to="/smart-insights"
            className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
          >
            <span>Explore All Insights</span>
            <ArrowRight size={14} />
          </Link>
        </div>

        {/* Insights Summary Cards */}
        <InsightsSummaryCards
          summary={insightsData?.summary}
          selectedFilter={selectedSeverity}
          onSelectFilter={setSelectedSeverity}
        />

        {/* Prioritized Insights List */}
        {loading ? (
          <div className="py-8 text-center text-gray-400 text-sm">
            <RefreshCw className="animate-spin inline h-5 w-5 mr-2" /> Evaluating business rules...
          </div>
        ) : (
          <InsightsList
            insights={insightsData?.insights || []}
            selectedSeverity={selectedSeverity}
            maxItems={4}
          />
        )}
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 2.5 OPERATIONAL GOALS & CALENDAR MILESTONES */}
      {/* ------------------------------------------------------------- */}
      <GoalsAndCalendarWidget />

      {/* ------------------------------------------------------------- */}
      {/* 3. SALES INTELLIGENCE & TIMELINE */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Revenue & Orders Over Time Chart */}
        <div className="lg:col-span-2">
          <Card className="h-full flex flex-col">
            <CardHeader 
              title="Sales Performance Over Time" 
              action={
                <span className="text-xs text-gray-500">
                  {timeline.length} recorded daily data points
                </span>
              } 
            />
            <CardBody className="flex-1">
              {loading ? (
                <div className="h-72 flex items-center justify-center text-gray-400">
                  <RefreshCw className="animate-spin h-6 w-6 mr-2" /> Loading chart...
                </div>
              ) : timeline.length === 0 ? (
                <div className="h-72 flex flex-col items-center justify-center text-gray-400">
                  <Calendar size={32} className="mb-2 text-gray-300" />
                  <p className="text-sm">No sales transactions recorded in this period</p>
                </div>
              ) : (
                <div className="h-72 w-full">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timeline} margin={{ top: 10, right: 30, left: 10, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#F3F4F6" />
                      <XAxis dataKey="date" tickLine={false} tick={{ fontSize: 11, fill: '#6B7280' }} />
                      <YAxis 
                        yAxisId="left" 
                        tickLine={false} 
                        tick={{ fontSize: 11, fill: '#6B7280' }} 
                        tickFormatter={(v) => `$${v >= 1000 ? `${(v/1000).toFixed(1)}k` : v}`} 
                      />
                      <YAxis 
                        yAxisId="right" 
                        orientation="right" 
                        tickLine={false} 
                        tick={{ fontSize: 11, fill: '#6B7280' }} 
                      />
                      <Tooltip 
                        formatter={(val, name) => name === 'Revenue' ? [`$${Number(val).toFixed(2)}`, name] : [val, name]}
                        contentStyle={{ backgroundColor: '#FFFFFF', borderRadius: '8px', border: '1px solid #E5E7EB', fontSize: '12px' }}
                      />
                      <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />
                      <Line 
                        yAxisId="left" 
                        type="monotone" 
                        dataKey="revenue" 
                        name="Revenue" 
                        stroke="#2563EB" 
                        strokeWidth={2.5} 
                        dot={{ r: 3 }} 
                        activeDot={{ r: 5 }} 
                      />
                      <Line 
                        yAxisId="right" 
                        type="monotone" 
                        dataKey="order_count" 
                        name="Orders" 
                        stroke="#10B981" 
                        strokeWidth={2} 
                        dot={{ r: 2 }} 
                      />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              )}
            </CardBody>
          </Card>
        </div>

        {/* Payment Methods Distribution */}
        <div>
          <Card className="h-full flex flex-col">
            <CardHeader title="Payment Methods" />
            <CardBody className="flex-1 flex flex-col justify-between">
              {salesData?.payment_methods?.length > 0 ? (
                <div className="space-y-4">
                  {salesData.payment_methods.map((pm) => {
                    const totalSales = kpis?.total_revenue || 1;
                    const pct = Math.min(100, Math.round((pm.total / totalSales) * 100));
                    return (
                      <div key={pm.method} className="space-y-1">
                        <div className="flex justify-between text-xs">
                          <span className="font-semibold text-gray-800">{pm.method}</span>
                          <span className="text-gray-500 font-mono">
                            {formatCurrency(pm.total)} ({pct}%)
                          </span>
                        </div>
                        <div className="w-full bg-gray-100 rounded-full h-2 overflow-hidden">
                          <div 
                            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
                            style={{ width: `${pct}%` }}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>
              ) : (
                <div className="py-12 text-center text-gray-400 text-xs">
                  <CreditCard size={28} className="mx-auto mb-2 text-gray-300" />
                  No payment data recorded in this period.
                </div>
              )}

              {/* Returns impact widget */}
              <div className="mt-6 pt-4 border-t border-gray-100 bg-gray-50 -mx-6 -mb-6 p-4 rounded-b-lg">
                <div className="flex items-center justify-between text-xs">
                  <span className="text-gray-600 flex items-center gap-1 font-medium">
                    <RotateCcw size={14} className="text-red-500" /> Returns & Refunds:
                  </span>
                  <span className="font-bold text-red-600">
                    {formatCurrency(returns?.total_refund_amount)} ({returns?.total_returns || 0} returned)
                  </span>
                </div>
              </div>
            </CardBody>
          </Card>
        </div>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 3. FINANCIAL INTELLIGENCE: P&L HIERARCHY */}
      {/* ------------------------------------------------------------- */}
      <Card>
        <CardHeader 
          title="Profit & Loss Breakdown (Income Statement)" 
          action={
            <span className="text-xs text-gray-500">
              Coverage: {fin?.cost_data_coverage_percentage || 100}% of sold items have cost data
            </span>
          }
        />
        <CardBody>
          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center text-center">
            {/* Revenue */}
            <div className="p-4 rounded-lg bg-blue-50 border border-blue-100">
              <span className="text-xs font-semibold uppercase text-blue-600">Revenue</span>
              <div className="text-xl font-bold text-blue-900 mt-1">{formatCurrency(fin?.total_sales)}</div>
              <span className="text-[11px] text-blue-700">Gross Sales</span>
            </div>

            <div className="hidden md:flex justify-center text-gray-400 font-bold text-lg">−</div>

            {/* COGS */}
            <div className="p-4 rounded-lg bg-amber-50 border border-amber-100">
              <span className="text-xs font-semibold uppercase text-amber-700">Cost of Goods (COGS)</span>
              <div className="text-xl font-bold text-amber-900 mt-1">{formatCurrency(fin?.cogs)}</div>
              <span className="text-[11px] text-amber-700">Direct Purchase Costs</span>
            </div>

            <div className="hidden md:flex justify-center text-gray-400 font-bold text-lg">=</div>

            {/* Gross Profit */}
            <div className="p-4 rounded-lg bg-emerald-50 border border-emerald-100">
              <span className="text-xs font-semibold uppercase text-emerald-700">Gross Profit</span>
              <div className="text-xl font-bold text-emerald-900 mt-1">{formatCurrency(fin?.gross_profit)}</div>
              <span className="text-[11px] text-emerald-700">Margin: {formatPercent(fin?.gross_margin_percentage)}</span>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-5 gap-3 items-center text-center mt-3 pt-3 border-t border-gray-100">
            {/* Gross Profit repeated */}
            <div className="p-4 rounded-lg bg-emerald-50/50 border border-emerald-100">
              <span className="text-xs font-semibold uppercase text-emerald-700">Gross Profit</span>
              <div className="text-lg font-bold text-emerald-900 mt-1">{formatCurrency(fin?.gross_profit)}</div>
            </div>

            <div className="hidden md:flex justify-center text-gray-400 font-bold text-lg">−</div>

            {/* Expenses */}
            <div className="p-4 rounded-lg bg-rose-50 border border-rose-100">
              <span className="text-xs font-semibold uppercase text-rose-700">Operating Expenses</span>
              <div className="text-xl font-bold text-rose-900 mt-1">{formatCurrency(fin?.total_expenses)}</div>
              <span className="text-[11px] text-rose-700">Utilities, Payroll, Ops</span>
            </div>

            <div className="hidden md:flex justify-center text-gray-400 font-bold text-lg">=</div>

            {/* Net Profit */}
            <div className="p-4 rounded-lg bg-purple-50 border border-purple-100">
              <span className="text-xs font-semibold uppercase text-purple-700">Net Profit</span>
              <div className="text-xl font-bold text-purple-900 mt-1">{formatCurrency(fin?.net_profit)}</div>
              <span className="text-[11px] text-purple-700">Net Margin: {formatPercent(fin?.net_margin_percentage)}</span>
            </div>
          </div>

          {/* Cash Flow Summary bar */}
          <div className="mt-4 pt-3 border-t border-gray-100 grid grid-cols-1 sm:grid-cols-3 gap-3 text-xs">
            <div className="bg-gray-50 p-2.5 rounded border border-gray-200 flex justify-between items-center">
              <span className="text-gray-600">Collected Cash:</span>
              <span className="font-semibold text-green-700">{formatCurrency(fin?.collected_payments)}</span>
            </div>
            <div className="bg-gray-50 p-2.5 rounded border border-gray-200 flex justify-between items-center">
              <span className="text-gray-600">Customer Receivables:</span>
              <span className="font-semibold text-amber-700">{formatCurrency(fin?.outstanding_receivables)}</span>
            </div>
            <div className="bg-gray-50 p-2.5 rounded border border-gray-200 flex justify-between items-center">
              <span className="text-gray-600">Supplier Payables:</span>
              <span className="font-semibold text-red-700">{formatCurrency(fin?.outstanding_payables)}</span>
            </div>
          </div>
        </CardBody>
      </Card>

      {/* ------------------------------------------------------------- */}
      {/* 4. PRODUCT PERFORMANCE & INVENTORY HEALTH */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top-Selling Products */}
        <Card>
          <CardHeader 
            title="Top Products by Revenue" 
            action={
              <Link to="/products" className="text-xs text-blue-600 hover:underline">
                View Catalog →
              </Link>
            }
          />
          <CardBody className="p-0 overflow-x-auto">
            {prodData?.top_by_revenue?.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-100 text-left text-xs">
                <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                  <tr>
                    <th className="px-4 py-3">Product</th>
                    <th className="px-3 py-3 text-right">Units Sold</th>
                    <th className="px-3 py-3 text-right">Revenue</th>
                    <th className="px-3 py-3 text-right">Velocity</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {prodData.top_by_revenue.slice(0, 5).map((p) => (
                    <tr key={p.product_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5">
                        <div className="font-semibold text-gray-900 truncate max-w-[180px]">{p.name}</div>
                        <div className="text-[10px] text-gray-400 font-mono">{p.sku}</div>
                      </td>
                      <td className="px-3 py-2.5 text-right font-medium">{formatNumber(p.quantity_sold)}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-gray-900">{formatCurrency(p.revenue)}</td>
                      <td className="px-3 py-2.5 text-right text-gray-500">{p.velocity_per_day}/day</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-400 text-xs">No product sales in this period.</div>
            )}
          </CardBody>
        </Card>

        {/* Actionable Low Stock & Out-of-Stock Products */}
        <Card>
          <CardHeader 
            title="Inventory Alerts (Stock Health)" 
            action={
              <Link to="/inventory" className="text-xs text-blue-600 hover:underline">
                Inventory Manager →
              </Link>
            }
          />
          <CardBody className="p-0 overflow-x-auto">
            {invData?.low_stock_products?.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-100 text-left text-xs">
                <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                  <tr>
                    <th className="px-4 py-3">Product</th>
                    <th className="px-3 py-3 text-right">Current Stock</th>
                    <th className="px-3 py-3 text-right">Reorder Point</th>
                    <th className="px-3 py-3 text-center">Status</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {invData.low_stock_products.slice(0, 5).map((p) => (
                    <tr key={p.product_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5">
                        <div className="font-semibold text-gray-900 truncate max-w-[180px]">{p.name}</div>
                        <div className="text-[10px] text-gray-400 font-mono">{p.sku}</div>
                      </td>
                      <td className="px-3 py-2.5 text-right font-bold text-red-600">{p.current_stock}</td>
                      <td className="px-3 py-2.5 text-right text-gray-500">{p.reorder_level}</td>
                      <td className="px-3 py-2.5 text-center">
                        <span className={`px-2 py-0.5 rounded-full text-[10px] font-semibold ${
                          p.status === 'Out of Stock' 
                            ? 'bg-red-100 text-red-800' 
                            : 'bg-amber-100 text-amber-800'
                        }`}>
                          {p.status}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-500 text-xs flex flex-col items-center">
                <CheckCircle2 size={24} className="text-green-500 mb-2" />
                All stock levels are above minimum reorder levels.
              </div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 5. CUSTOMER & SUPPLIER INTELLIGENCE */}
      {/* ------------------------------------------------------------- */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Customers by Spend */}
        <Card>
          <CardHeader 
            title="Top Customers by Spend" 
            action={
              <Link to="/customers" className="text-xs text-blue-600 hover:underline">
                All Customers →
              </Link>
            }
          />
          <CardBody className="p-0 overflow-x-auto">
            {custData?.top_customers?.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-100 text-left text-xs">
                <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                  <tr>
                    <th className="px-4 py-3">Customer</th>
                    <th className="px-3 py-3 text-right">Orders</th>
                    <th className="px-3 py-3 text-right">Total Spent</th>
                    <th className="px-3 py-3 text-right">Balance Due</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {custData.top_customers.map((c) => (
                    <tr key={c.customer_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5 font-medium text-gray-900 truncate max-w-[180px]">
                        {c.name}
                      </td>
                      <td className="px-3 py-2.5 text-right text-gray-500">{c.order_count}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-gray-900">{formatCurrency(c.total_spent)}</td>
                      <td className="px-3 py-2.5 text-right">
                        <span className={c.outstanding_balance > 0 ? 'text-red-600 font-semibold' : 'text-gray-400'}>
                          {formatCurrency(c.outstanding_balance)}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-400 text-xs">No customer orders recorded.</div>
            )}
          </CardBody>
        </Card>

        {/* Suppliers & Purchasing */}
        <Card>
          <CardHeader 
            title="Suppliers & Procurement Spend" 
            action={
              <Link to="/purchase-orders" className="text-xs text-blue-600 hover:underline">
                Purchase Orders →
              </Link>
            }
          />
          <CardBody className="p-0 overflow-x-auto">
            {purchData?.top_suppliers?.length > 0 ? (
              <table className="min-w-full divide-y divide-gray-100 text-left text-xs">
                <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                  <tr>
                    <th className="px-4 py-3">Supplier</th>
                    <th className="px-3 py-3 text-right">POs</th>
                    <th className="px-3 py-3 text-right">Total Spend</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-100">
                  {purchData.top_suppliers.map((s) => (
                    <tr key={s.supplier_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5 font-medium text-gray-900 truncate max-w-[200px]">
                        {s.name}
                      </td>
                      <td className="px-3 py-2.5 text-right text-gray-500">{s.po_count}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-gray-900">{formatCurrency(s.total_spend)}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            ) : (
              <div className="p-8 text-center text-gray-400 text-xs">No supplier purchases recorded.</div>
            )}
          </CardBody>
        </Card>
      </div>

      {/* ------------------------------------------------------------- */}
      {/* 6. INVENTORY VELOCITY: SLOW-MOVING / STAGNANT STOCK */}
      {/* ------------------------------------------------------------- */}
      <Card>
        <CardHeader 
          title="Stagnant & Slow-Moving Stock Analysis" 
          action={
            <span className="text-xs text-gray-500 flex items-center gap-1">
              <Clock size={12} /> Velocity &lt; 0.05 units/day with positive stock
            </span>
          }
        />
        <CardBody className="p-0 overflow-x-auto">
          {prodData?.slow_moving?.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-100 text-left text-xs">
              <thead className="bg-gray-50 text-gray-500 font-semibold uppercase">
                <tr>
                  <th className="px-4 py-3">Product Name</th>
                  <th className="px-3 py-3">SKU</th>
                  <th className="px-3 py-3 text-right">Units on Hand</th>
                  <th className="px-3 py-3 text-right">Units Sold in Period</th>
                  <th className="px-3 py-3 text-right">Capital Tied Up</th>
                  <th className="px-3 py-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-100">
                {prodData.slow_moving.map((p) => {
                  const tiedUp = p.current_stock * (p.cost_price || p.selling_price || 0);
                  return (
                    <tr key={p.product_id} className="hover:bg-gray-50">
                      <td className="px-4 py-2.5 font-medium text-gray-900">{p.name}</td>
                      <td className="px-3 py-2.5 font-mono text-gray-500">{p.sku}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-gray-800">{formatNumber(p.current_stock)}</td>
                      <td className="px-3 py-2.5 text-right text-gray-500">{formatNumber(p.quantity_sold)}</td>
                      <td className="px-3 py-2.5 text-right font-bold text-amber-700">{formatCurrency(tiedUp)}</td>
                      <td className="px-3 py-2.5 text-center">
                        <span className="px-2 py-0.5 rounded-full text-[10px] font-semibold bg-gray-100 text-gray-700">
                          Slow-Moving
                        </span>
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <div className="p-8 text-center text-gray-400 text-xs">
              No slow-moving inventory detected; healthy turnover across active products.
            </div>
          )}
        </CardBody>
      </Card>
    </div>
  );
}

// ----------------------------------------------------------------------------
// REUSABLE KPI CARD COMPONENT
// ----------------------------------------------------------------------------
function KpiCard({ title, value, subtitle, icon: Icon, color = 'blue', loading }) {
  const colorStyles = {
    blue: 'bg-blue-50 text-blue-600 border-blue-100',
    indigo: 'bg-indigo-50 text-indigo-600 border-indigo-100',
    teal: 'bg-teal-50 text-teal-600 border-teal-100',
    amber: 'bg-amber-50 text-amber-600 border-amber-100',
    emerald: 'bg-emerald-50 text-emerald-600 border-emerald-100',
    purple: 'bg-purple-50 text-purple-600 border-purple-100',
  };

  return (
    <Card className="hover:shadow-md transition-shadow">
      <CardBody className="p-4 flex items-start justify-between">
        <div className="flex-1 min-w-0 pr-2">
          <p className="text-xs font-semibold uppercase tracking-wider text-gray-500 truncate">{title}</p>
          {loading ? (
            <div className="h-7 w-24 bg-gray-200 animate-pulse rounded mt-1.5" />
          ) : (
            <h3 className="text-xl font-bold text-gray-900 mt-1 truncate">{value}</h3>
          )}
          {subtitle && (
            <p className="text-[11px] text-gray-400 mt-1 truncate">{subtitle}</p>
          )}
        </div>
        <div className={`p-2.5 rounded-xl border flex-shrink-0 ${colorStyles[color] || colorStyles.blue}`}>
          <Icon size={20} />
        </div>
      </CardBody>
    </Card>
  );
}
