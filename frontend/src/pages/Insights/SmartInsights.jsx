import { useState } from 'react';
import { 
  Sparkles, 
  RefreshCw, 
  Filter, 
  AlertCircle, 
  Calendar,
  Package,
  DollarSign,
  BarChart2,
  Users,
  Truck,
  Database
} from 'lucide-react';
import { useInsights, INSIGHT_PERIOD_OPTIONS } from '../../api/insights';
import { InsightsSummaryCards } from '../../components/insights/InsightsSummaryCards';
import { InsightsList } from '../../components/insights/InsightsList';
import { LoadingState, ErrorState, EmptyState } from '../../components/ui/States';

export default function SmartInsights() {
  const [period, setPeriod] = useState('last_30_days');
  const [startDate, setStartDate] = useState('');
  const [endDate, setEndDate] = useState('');
  const [dateError, setDateError] = useState(null);
  const [selectedSeverity, setSelectedSeverity] = useState('all');
  const [selectedCategory, setSelectedCategory] = useState('all');

  const {
    insightsData,
    summary,
    insights,
    periodInfo,
    loading,
    error,
    refetch,
  } = useInsights({ period, startDate, endDate });

  const handlePeriodChange = (newPeriod) => {
    setPeriod(newPeriod);
    if (newPeriod !== 'custom') {
      setDateError(null);
    }
  };

  const handleApplyCustomDates = () => {
    if (!startDate || !endDate) {
      setDateError('Please provide both start and end dates');
      return;
    }
    if (new Date(startDate) > new Date(endDate)) {
      setDateError('Start date must be before or equal to End date');
      return;
    }
    setDateError(null);
    refetch();
  };

  const categories = [
    { id: 'all', label: 'All Domains', icon: Sparkles },
    { id: 'inventory', label: 'Inventory', icon: Package },
    { id: 'finance', label: 'Finance', icon: DollarSign },
    { id: 'sales', label: 'Sales', icon: BarChart2 },
    { id: 'customer', label: 'Customers', icon: Users },
    { id: 'supplier', label: 'Suppliers', icon: Truck },
    { id: 'data_quality', label: 'Data Quality', icon: Database },
  ];

  // Filter insights by category and severity
  const filteredInsights = insights.filter((item) => {
    const matchesSev = selectedSeverity === 'all' || item.severity?.toLowerCase() === selectedSeverity.toLowerCase();
    const matchesCat = selectedCategory === 'all' || item.category?.toLowerCase() === selectedCategory.toLowerCase();
    return matchesSev && matchesCat;
  });

  return (
    <div className="space-y-6 max-w-7xl mx-auto pb-12">
      {/* ------------------------------------------------------------- */}
      {/* HEADER & CONTROLS */}
      {/* ------------------------------------------------------------- */}
      <div className="bg-white p-5 rounded-xl border border-gray-200 shadow-sm flex flex-col lg:flex-row lg:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-2">
            <h1 className="text-2xl font-bold text-gray-900">Smart Business Insights</h1>
            <span className="px-2.5 py-0.5 rounded-full text-xs font-semibold bg-purple-100 text-purple-800 border border-purple-200 flex items-center gap-1">
              <Sparkles size={12} />
              Deterministic Rules Engine
            </span>
          </div>
          <p className="text-xs text-gray-500 mt-1">
            Explainable signals detecting operational risks, capital bottlenecks, and margin health with actionable guidance.
          </p>
        </div>

        {/* Period Selector & Refresh */}
        <div className="flex flex-wrap items-center gap-2">
          <div className="inline-flex rounded-lg border border-gray-200 bg-gray-50 p-1">
            {INSIGHT_PERIOD_OPTIONS.map((opt) => (
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
            onClick={() => refetch()}
            disabled={loading}
            className="p-2 border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-600 transition-colors"
            title="Refresh Insights"
          >
            <RefreshCw size={16} className={loading ? 'animate-spin text-blue-600' : ''} />
          </button>
        </div>
      </div>

      {/* Custom Date Range Picker */}
      {period === 'custom' && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-4 flex flex-wrap items-center gap-4 text-xs">
          <div className="flex items-center gap-2">
            <label className="font-semibold text-gray-700">Start Date:</label>
            <input 
              type="date" 
              value={startDate} 
              onChange={(e) => setStartDate(e.target.value)}
              className="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-gray-800"
            />
          </div>
          <div className="flex items-center gap-2">
            <label className="font-semibold text-gray-700">End Date:</label>
            <input 
              type="date" 
              value={endDate} 
              onChange={(e) => setEndDate(e.target.value)}
              className="px-2.5 py-1.5 border border-gray-300 rounded bg-white text-gray-800"
            />
          </div>
          <button
            onClick={handleApplyCustomDates}
            className="px-3 py-1.5 bg-blue-600 text-white font-medium rounded hover:bg-blue-700 transition-colors"
          >
            Apply Range
          </button>
          {dateError && (
            <span className="text-red-600 font-medium flex items-center gap-1">
              <AlertCircle size={14} /> {dateError}
            </span>
          )}
        </div>
      )}

      {/* Error State */}
      {error && (
        <ErrorState
          title="Unable to load Smart Business Insights"
          description={error}
          onRetry={() => refetch()}
        />
      )}

      {/* Loading State */}
      {loading && !insightsData && (
        <LoadingState message="Analyzing operational data and evaluating business rules..." />
      )}

      {/* Loaded Insights Content */}
      {!error && insightsData && (
        <>
          {/* Summary Cards */}
          <InsightsSummaryCards
            summary={summary}
            selectedFilter={selectedSeverity}
            onSelectFilter={setSelectedSeverity}
          />

          {/* Domain Category Filter Tabs */}
          <div className="flex flex-wrap items-center gap-2 pt-2 border-b border-gray-200 pb-3">
            <span className="text-xs font-semibold text-gray-500 uppercase tracking-wider mr-2 flex items-center gap-1">
              <Filter size={13} />
              Filter Domain:
            </span>
            {categories.map((cat) => {
              const Icon = cat.icon;
              const isSelected = selectedCategory === cat.id;
              const countInCat = cat.id === 'all' 
                ? insights.length 
                : insights.filter(i => i.category?.toLowerCase() === cat.id).length;

              return (
                <button
                  key={cat.id}
                  onClick={() => setSelectedCategory(cat.id)}
                  className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium transition-all ${
                    isSelected
                      ? 'bg-blue-600 text-white shadow-sm'
                      : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                  }`}
                >
                  <Icon size={13} />
                  <span>{cat.label}</span>
                  <span className={`text-[10px] px-1.5 py-0.2 rounded-full ${isSelected ? 'bg-white/20 text-white' : 'bg-gray-100 text-gray-600'}`}>
                    {countInCat}
                  </span>
                </button>
              );
            })}
          </div>

          {/* Filter Status Badge if active */}
          {(selectedSeverity !== 'all' || selectedCategory !== 'all') && (
            <div className="flex items-center justify-between text-xs text-gray-500 bg-gray-50 p-2.5 rounded-lg border border-gray-200">
              <div>
                Showing <strong>{filteredInsights.length}</strong> of <strong>{insights.length}</strong> insights
                {selectedSeverity !== 'all' && <span> • Severity: <strong className="capitalize">{selectedSeverity}</strong></span>}
                {selectedCategory !== 'all' && <span> • Domain: <strong className="capitalize">{selectedCategory}</strong></span>}
              </div>
              <button
                onClick={() => { setSelectedSeverity('all'); setSelectedCategory('all'); }}
                className="text-blue-600 hover:text-blue-800 font-semibold"
              >
                Clear Filters
              </button>
            </div>
          )}

          {/* Insights List or Empty State */}
          {summary.total === 0 ? (
            <EmptyState
              icon={Sparkles}
              title="No Issues Detected"
              description="Your business is currently operating without any detected critical bottlenecks, stockouts, or margin compression for this period."
            />
          ) : (
            <InsightsList
              insights={filteredInsights}
              selectedSeverity="all"
            />
          )}
        </>
      )}
    </div>
  );
}
