import { useState } from 'react';
import { Link } from 'react-router-dom';
import { 
  AlertCircle, 
  AlertTriangle, 
  Info, 
  ChevronDown, 
  ChevronUp, 
  ArrowRight, 
  Lightbulb,
  CheckCircle2,
  ExternalLink,
  Package,
  DollarSign,
  Users,
  Truck,
  Database,
  BarChart2
} from 'lucide-react';
import { getInsightNavigationTarget } from '../../api/insights';

export function InsightsList({ insights = [], selectedSeverity = 'all', maxItems }) {
  const [expandedIds, setExpandedIds] = useState(new Set());

  const toggleExpand = (id) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) {
        next.delete(id);
      } else {
        next.add(id);
      }
      return next;
    });
  };

  // Filter by severity if specified
  let filtered = insights;
  if (selectedSeverity && selectedSeverity !== 'all') {
    filtered = insights.filter((item) => item.severity?.toLowerCase() === selectedSeverity.toLowerCase());
  }

  // Limit display if maxItems passed
  const displayItems = maxItems ? filtered.slice(0, maxItems) : filtered;

  if (displayItems.length === 0) {
    return (
      <div className="p-8 text-center bg-gray-50 rounded-xl border border-dashed border-gray-200">
        <div className="w-10 h-10 rounded-full bg-emerald-100 text-emerald-600 flex items-center justify-center mx-auto mb-3">
          <CheckCircle2 size={20} />
        </div>
        <h4 className="text-sm font-semibold text-gray-900">No signals matching filter</h4>
        <p className="text-xs text-gray-500 mt-1 max-w-sm mx-auto">
          {selectedSeverity !== 'all' 
            ? `There are currently 0 active ${selectedSeverity} insights for this period.`
            : 'No business intelligence signals detected for the selected period.'}
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3 sm:space-y-4">
      {displayItems.map((insight) => (
        <InsightCard
          key={insight.id}
          insight={insight}
          isExpanded={expandedIds.has(insight.id)}
          onToggle={() => toggleExpand(insight.id)}
        />
      ))}
    </div>
  );
}

function InsightCard({ insight, isExpanded, onToggle }) {
  const { id, category, severity, title, message, metric, current_value, threshold, recommendation, evidence } = insight;

  const severityConfig = {
    critical: {
      border: 'border-red-200 hover:border-red-300',
      badge: 'bg-red-100 text-red-800 border-red-200',
      accent: 'border-l-4 border-l-red-500',
      icon: AlertCircle,
      iconColor: 'text-red-600',
      bg: 'bg-white',
    },
    warning: {
      border: 'border-amber-200 hover:border-amber-300',
      badge: 'bg-amber-100 text-amber-800 border-amber-200',
      accent: 'border-l-4 border-l-amber-500',
      icon: AlertTriangle,
      iconColor: 'text-amber-600',
      bg: 'bg-white',
    },
    info: {
      border: 'border-sky-200 hover:border-sky-300',
      badge: 'bg-sky-100 text-sky-800 border-sky-200',
      accent: 'border-l-4 border-l-sky-500',
      icon: Info,
      iconColor: 'text-sky-600',
      bg: 'bg-white',
    },
  };

  const categoryIcons = {
    inventory: Package,
    finance: DollarSign,
    sales: BarChart2,
    customer: Users,
    supplier: Truck,
    data_quality: Database,
  };

  const currentSev = severityConfig[severity?.toLowerCase()] || severityConfig.info;
  const SeverityIcon = currentSev.icon;
  const CategoryIcon = categoryIcons[category?.toLowerCase()] || BarChart2;
  const navTarget = getInsightNavigationTarget(insight);

  return (
    <div
      className={`rounded-xl border shadow-sm transition-all overflow-hidden ${currentSev.bg} ${currentSev.border} ${currentSev.accent}`}
    >
      <div className="p-4 sm:p-5">
        {/* Top Badges & Category Header */}
        <div className="flex flex-wrap items-center justify-between gap-2 mb-2.5">
          <div className="flex items-center gap-2">
            <span
              className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-bold uppercase tracking-wider border ${currentSev.badge}`}
            >
              <SeverityIcon size={13} className={currentSev.iconColor} />
              {severity}
            </span>
            <span className="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-xs font-medium bg-gray-100 text-gray-700">
              <CategoryIcon size={12} className="text-gray-500" />
              <span className="capitalize">{category?.replace('_', ' ')}</span>
            </span>
          </div>

          {/* Metric & Value indicator if available */}
          {metric && current_value !== null && current_value !== undefined && (
            <div className="text-xs text-gray-600 bg-gray-50 px-2.5 py-1 rounded border border-gray-100 font-mono">
              <span className="text-gray-400 font-sans mr-1">{metric.replace(/_/g, ' ')}:</span>
              <span className="font-semibold text-gray-900">{formatMetricValue(current_value)}</span>
              {threshold !== null && threshold !== undefined && (
                <span className="text-gray-400 text-[10px] ml-1">
                  (limit: {formatMetricValue(threshold)})
                </span>
              )}
            </div>
          )}
        </div>

        {/* Title & Core Message */}
        <h3 className="text-base sm:text-lg font-bold text-gray-900 mb-1.5">
          {title}
        </h3>
        <p className="text-sm text-gray-600 leading-relaxed mb-3">
          {message}
        </p>

        {/* Actionable Recommendation Box */}
        {recommendation && (
          <div className="bg-amber-50/70 border border-amber-200/60 rounded-lg p-3 text-xs sm:text-sm text-amber-950 flex items-start gap-2.5 mb-3.5">
            <Lightbulb size={16} className="text-amber-600 flex-shrink-0 mt-0.5" />
            <div className="flex-1">
              <strong className="font-semibold text-amber-900 block sm:inline mr-1">
                Recommendation:
              </strong>
              <span>{recommendation}</span>
            </div>
          </div>
        )}

        {/* Footer Actions: Module Link & Evidence Drawer Toggle */}
        <div className="flex flex-wrap items-center justify-between gap-3 pt-2 border-t border-gray-100">
          <div className="flex items-center gap-2">
            {navTarget && (
              <Link
                to={navTarget.path}
                className="inline-flex items-center gap-1.5 text-xs sm:text-sm font-semibold text-blue-600 hover:text-blue-800 hover:underline transition-colors"
              >
                <span>{navTarget.label}</span>
                <ArrowRight size={14} />
              </Link>
            )}
          </div>

          {evidence && Object.keys(evidence).length > 0 && (
            <button
              type="button"
              onClick={onToggle}
              className="inline-flex items-center gap-1 px-2.5 py-1 text-xs font-medium text-gray-600 hover:text-gray-900 bg-gray-50 hover:bg-gray-100 rounded-md border border-gray-200 transition-colors"
            >
              <span>{isExpanded ? 'Hide Details' : 'View Evidence'}</span>
              {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
          )}
        </div>
      </div>

      {/* Expanded Evidence Drawer */}
      {isExpanded && evidence && (
        <div className="bg-gray-50/80 border-t border-gray-200 px-4 py-3 sm:px-5 sm:py-4">
          <h4 className="text-xs font-bold uppercase tracking-wider text-gray-500 mb-2.5">
            Supporting Evidence & Operational Data
          </h4>
          <EvidenceRenderer evidence={evidence} category={category} />
        </div>
      )}
    </div>
  );
}

function EvidenceRenderer({ evidence, category }) {
  if (!evidence || Object.keys(evidence).length === 0) {
    return <p className="text-xs text-gray-500 italic">No additional evidence logged.</p>;
  }

  // 1. Array of products (depleted items, low stock items, slow-moving items)
  if (Array.isArray(evidence.products) || Array.isArray(evidence.depleted_products) || Array.isArray(evidence.top_stagnant)) {
    const items = evidence.products || evidence.depleted_products || evidence.top_stagnant || [];
    return (
      <div className="overflow-x-auto">
        <table className="min-w-full text-xs divide-y divide-gray-200 bg-white rounded-lg border border-gray-200">
          <thead className="bg-gray-50 font-semibold text-gray-600">
            <tr>
              <th className="px-3 py-2 text-left">Product Name</th>
              <th className="px-3 py-2 text-left">SKU</th>
              {items[0]?.stock !== undefined && <th className="px-3 py-2 text-right">Stock</th>}
              {items[0]?.reorder !== undefined && <th className="px-3 py-2 text-right">Reorder Level</th>}
              {items[0]?.tied_up_capital !== undefined && <th className="px-3 py-2 text-right">Tied-Up Capital</th>}
              {items[0]?.velocity !== undefined && <th className="px-3 py-2 text-right">Velocity</th>}
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-100 text-gray-700">
            {items.map((prod, idx) => (
              <tr key={prod.id || prod.sku || idx} className="hover:bg-gray-50">
                <td className="px-3 py-2 font-medium text-gray-900">{prod.name}</td>
                <td className="px-3 py-2 font-mono text-gray-500">{prod.sku || '—'}</td>
                {prod.stock !== undefined && (
                  <td className="px-3 py-2 text-right font-bold">{prod.stock}</td>
                )}
                {prod.reorder !== undefined && (
                  <td className="px-3 py-2 text-right text-gray-500">{prod.reorder}</td>
                )}
                {prod.tied_up_capital !== undefined && (
                  <td className="px-3 py-2 text-right font-semibold text-amber-700">
                    ${Number(prod.tied_up_capital).toFixed(2)}
                  </td>
                )}
                {prod.velocity !== undefined && (
                  <td className="px-3 py-2 text-right font-mono text-gray-600">
                    {prod.velocity} /day
                  </td>
                )}
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    );
  }

  // 2. Structured Key-Value List
  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2.5">
      {Object.entries(evidence).map(([k, v]) => {
        if (typeof v === 'object' && v !== null && !Array.isArray(v)) {
          return null; // Skip deeply nested objects or render separately
        }
        return (
          <div key={k} className="p-2.5 bg-white rounded border border-gray-200">
            <span className="text-[11px] font-medium uppercase tracking-wider text-gray-400 block truncate">
              {k.replace(/_/g, ' ')}
            </span>
            <span className="text-xs sm:text-sm font-semibold text-gray-900 break-words">
              {formatEvidenceValue(v)}
            </span>
          </div>
        );
      })}
    </div>
  );
}

function formatMetricValue(val) {
  if (typeof val === 'number') {
    if (Number.isInteger(val)) return val.toLocaleString();
    return val.toFixed(1);
  }
  return String(val);
}

function formatEvidenceValue(val) {
  if (typeof val === 'number') {
    return val.toLocaleString(undefined, { maximumFractionDigits: 2 });
  }
  if (Array.isArray(val)) {
    return val.join(', ');
  }
  return String(val);
}
