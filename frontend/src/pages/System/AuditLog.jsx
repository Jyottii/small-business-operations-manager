import { useState } from 'react';
import { useApi } from '../../api/hooks';
import { DataTable } from '../../components/ui/DataTable';

export default function AuditLog() {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');

  const queryEndpoint = `/audit-logs?page=${page}&page_size=15${searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''}`;
  const { data, loading, error, pagination } = useApi(queryEndpoint);

  const columns = [
    { header: 'Action', cell: (row) => (
      <span className="font-mono text-xs font-semibold px-2 py-1 bg-blue-50 text-blue-700 rounded">
        {row.action}
      </span>
    )},
    { header: 'Entity Type', accessorKey: 'entity_type' },
    { header: 'Entity ID', cell: (row) => <span className="font-mono text-xs text-gray-500">{row.entity_id ? row.entity_id.slice(0, 8) : 'N/A'}</span> },
    { header: 'Description', accessorKey: 'description' },
    { header: 'User', cell: (row) => <span className="font-medium text-gray-900">{row.user_id || 'SYSTEM'}</span> },
    { header: 'Timestamp', cell: (row) => row.created_at ? new Date(row.created_at).toLocaleString() : 'N/A' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Audit Log</h1>
        <p className="text-sm text-gray-500">Immutable chronological ledger of all business actions and system events.</p>
      </div>

      <DataTable 
        columns={columns} 
        data={data || []} 
        loading={loading}
        error={error}
        pagination={pagination}
        searchPlaceholder="Search events or entities..." 
        searchValue={searchTerm}
        onSearchChange={(v) => { setSearchTerm(v); setPage(1); }}
        onPageChange={(p) => setPage(p)}
      />
    </div>
  );
}
