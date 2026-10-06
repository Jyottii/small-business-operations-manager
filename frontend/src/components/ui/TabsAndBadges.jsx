import { useState } from 'react';

export function Tabs({ tabs, defaultTab }) {
  const [activeTab, setActiveTab] = useState(defaultTab || tabs[0].id);

  const currentTab = tabs.find(t => t.id === activeTab);

  return (
    <div>
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex space-x-8" aria-label="Tabs">
          {tabs.map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`
                whitespace-nowrap py-4 px-1 border-b-2 font-medium text-sm
                ${activeTab === tab.id
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }
              `}
            >
              {tab.label}
            </button>
          ))}
        </nav>
      </div>
      <div className="py-6">
        {currentTab?.content}
      </div>
    </div>
  );
}

export function StatusBadge({ status }) {
  let bg = 'bg-gray-100';
  let text = 'text-gray-800';

  const s = status ? status.toLowerCase() : '';

  if (['completed', 'paid', 'active', 'vip', 'in stock', 'received', 'delivered'].includes(s)) {
    bg = 'bg-green-100';
    text = 'text-green-800';
  } else if (['pending', 'processing', 'ordered', 'shipped'].includes(s)) {
    bg = 'bg-blue-100';
    text = 'text-blue-800';
  } else if (['draft', 'unpaid', 'low stock', 'partially received'].includes(s)) {
    bg = 'bg-yellow-100';
    text = 'text-yellow-800';
  } else if (['cancelled', 'out of stock', 'overdue', 'damaged', 'returned'].includes(s)) {
    bg = 'bg-red-100';
    text = 'text-red-800';
  }

  return (
    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${bg} ${text}`}>
      {status}
    </span>
  );
}
