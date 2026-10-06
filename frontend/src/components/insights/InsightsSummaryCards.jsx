import { AlertCircle, AlertTriangle, Info, Sparkles, CheckCircle2 } from 'lucide-react';

export function InsightsSummaryCards({ summary, selectedFilter = 'all', onSelectFilter }) {
  const { total = 0, critical = 0, warning = 0, info = 0 } = summary || {};

  const cards = [
    {
      id: 'all',
      title: 'Total Insights',
      value: total,
      label: 'All Active Signals',
      icon: Sparkles,
      color: 'blue',
      activeRing: 'ring-2 ring-blue-500',
      bg: 'bg-white',
      badgeBg: 'bg-blue-50 text-blue-700',
    },
    {
      id: 'critical',
      title: 'Critical Actions',
      value: critical,
      label: 'Urgent Intervention',
      icon: AlertCircle,
      color: 'red',
      activeRing: 'ring-2 ring-red-500',
      bg: critical > 0 ? 'bg-red-50/50' : 'bg-white',
      badgeBg: 'bg-red-100 text-red-800',
      textColor: critical > 0 ? 'text-red-700' : 'text-gray-900',
    },
    {
      id: 'warning',
      title: 'Operational Warnings',
      value: warning,
      label: 'Risks & Inefficiencies',
      icon: AlertTriangle,
      color: 'amber',
      activeRing: 'ring-2 ring-amber-500',
      bg: warning > 0 ? 'bg-amber-50/40' : 'bg-white',
      badgeBg: 'bg-amber-100 text-amber-800',
      textColor: warning > 0 ? 'text-amber-800' : 'text-gray-900',
    },
    {
      id: 'info',
      title: 'Informational Signals',
      value: info,
      label: 'Optimization Opportunities',
      icon: Info,
      color: 'sky',
      activeRing: 'ring-2 ring-sky-500',
      bg: 'bg-white',
      badgeBg: 'bg-sky-100 text-sky-800',
      textColor: 'text-gray-900',
    },
  ];

  return (
    <div className="grid grid-cols-2 lg:grid-cols-4 gap-3 sm:gap-4">
      {cards.map((card) => {
        const Icon = card.icon;
        const isSelected = selectedFilter === card.id;

        return (
          <button
            key={card.id}
            type="button"
            onClick={() => onSelectFilter && onSelectFilter(card.id)}
            className={`p-4 rounded-xl border text-left transition-all ${card.bg} ${
              isSelected ? `${card.activeRing} shadow-sm border-transparent` : 'border-gray-200 hover:border-gray-300'
            }`}
          >
            <div className="flex items-center justify-between mb-2">
              <span className="text-xs font-medium text-gray-500 uppercase tracking-wider">
                {card.title}
              </span>
              <span className={`p-1.5 rounded-lg ${card.badgeBg}`}>
                <Icon size={16} />
              </span>
            </div>
            <div className="flex items-baseline gap-2">
              <span className={`text-2xl sm:text-3xl font-extrabold ${card.textColor || 'text-gray-900'}`}>
                {card.value}
              </span>
              {card.id === 'critical' && card.value === 0 && (
                <span className="inline-flex items-center text-xs font-medium text-emerald-600 gap-0.5">
                  <CheckCircle2 size={13} /> Clear
                </span>
              )}
            </div>
            <p className="text-xs text-gray-500 mt-1 truncate">
              {card.label}
            </p>
          </button>
        );
      })}
    </div>
  );
}
