import { useState } from 'react';
import { DataTable } from '../../components/ui/DataTable';
import { useApi } from '../../api/hooks';
import { StatusBadge } from '../../components/ui/TabsAndBadges';
import StockAdjustmentModal from '../../components/workflows/StockAdjustmentModal';

export default function StockMovement() {
  const [page, setPage] = useState(1);
  const [searchTerm, setSearchTerm] = useState('');
  const [modalOpen, setModalOpen] = useState(false);

  const queryEndpoint = `/inventory/movements?page=${page}&page_size=15${searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''}`;
  const { data, loading, error, pagination, refetch } = useApi(queryEndpoint);

  const columns = [
    { header: 'Product ID', accessorKey: 'product_id' },
    { header: 'Movement Type', cell: (row) => <StatusBadge status={row.movement_type} /> },
    { header: 'Qty Change', cell: (row) => {
        const qty = parseFloat(row.quantity);
        return (
          <span className={qty > 0 ? 'text-green-600 font-bold' : 'text-red-600 font-bold'}>
            {qty > 0 ? '+' : ''}{qty}
          </span>
        );
      } 
    },
    { header: 'Prev Qty', cell: (row) => Number(row.previous_quantity || 0) },
    { header: 'New Qty', cell: (row) => Number(row.resulting_quantity || 0) },
    { header: 'Reference', cell: (row) => (
        <span className="text-xs text-gray-500 font-mono">
          {row.reference_type ? `${row.reference_type} (${row.reference_id?.slice(0, 8)})` : 'Manual'}
        </span>
      )
    },
    { header: 'Notes', accessorKey: 'notes' },
    { header: 'Date', cell: (row) => row.created_at ? new Date(row.created_at).toLocaleDateString() : 'N/A' },
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Stock Movements</h1>
          <p className="text-sm text-gray-500">Authoritative audit ledger of all inventory adjustments, sales, and receipts.</p>
        </div>
        <button 
          onClick={() => setModalOpen(true)}
          className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-blue-700 transition-colors"
        >
          Manual Adjustment
        </button>
      </div>

      <DataTable 
        columns={columns} 
        data={data || []} 
        loading={loading}
        error={error}
        pagination={pagination}
        searchPlaceholder="Search stock movements..." 
        searchValue={searchTerm}
        onSearchChange={(v) => { setSearchTerm(v); setPage(1); }}
        onPageChange={(p) => setPage(p)}
      />

      <StockAdjustmentModal 
        isOpen={modalOpen} 
        onClose={() => setModalOpen(false)}
        onSuccess={() => refetch()}
      />
    </div>
  );
}
