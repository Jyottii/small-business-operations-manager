import { Package, AlertTriangle, TrendingDown, Layers } from 'lucide-react';
import { StatCard } from '../../components/ui/StatCard';
import { DataTable } from '../../components/ui/DataTable';

const mockInventory = [
  { id: 1, product: 'Wireless Mouse', sku: 'WM-001', category: 'Electronics', stock: 145, reorder: 50, price: 29.99, status: 'In Stock' },
  { id: 2, product: 'Mechanical Keyboard', sku: 'MK-023', category: 'Electronics', stock: 12, reorder: 20, price: 89.99, status: 'Low Stock' },
  { id: 3, product: 'USB-C Hub', sku: 'UH-112', category: 'Accessories', stock: 0, reorder: 30, price: 45.00, status: 'Out of Stock' },
  { id: 4, product: 'Laptop Stand', sku: 'LS-099', category: 'Accessories', stock: 68, reorder: 25, price: 34.50, status: 'In Stock' },
  { id: 5, product: '27" Monitor', sku: 'MN-270', category: 'Electronics', stock: 5, reorder: 10, price: 299.00, status: 'Low Stock' },
  { id: 6, product: 'Webcam 1080p', sku: 'WC-108', category: 'Electronics', stock: 43, reorder: 15, price: 59.99, status: 'In Stock' },
];

const columns = [
  { header: 'Product', cell: (row) => <div className="font-medium text-gray-900">{row.product}</div> },
  { header: 'SKU', accessorKey: 'sku' },
  { header: 'Category', cell: (row) => <span className="inline-flex items-center px-2 py-0.5 rounded text-xs font-medium bg-gray-100 text-gray-800">{row.category}</span> },
  { header: 'Stock', accessorKey: 'stock' },
  { header: 'Reorder Level', accessorKey: 'reorder' },
  { header: 'Price', cell: (row) => `$${row.price.toFixed(2)}` },
  { header: 'Status', cell: (row) => {
      let colorClass = 'bg-green-100 text-green-800';
      if (row.status === 'Low Stock') colorClass = 'bg-yellow-100 text-yellow-800';
      if (row.status === 'Out of Stock') colorClass = 'bg-red-100 text-red-800';
      return <span className={`inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>{row.status}</span>;
    }
  },
  { header: 'Actions', cell: () => <button className="text-blue-600 hover:text-blue-900 text-sm font-medium">Edit</button> }
];

export default function InventoryOverview() {
  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Inventory Overview</h1>
          <p className="text-sm text-gray-500">Manage your products and track stock levels.</p>
        </div>
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-blue-700">
          Add New Product
        </button>
      </div>

      {/* Overview Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        <StatCard title="Total Products" value="248" icon={Package} color="blue" />
        <StatCard title="Total Units" value="3,492" icon={Layers} color="purple" />
        <StatCard title="Low Stock" value="12" icon={AlertTriangle} color="yellow" />
        <StatCard title="Out of Stock" value="3" icon={TrendingDown} color="red" />
      </div>

      {/* Inventory Table */}
      <div>
        <h2 className="text-lg font-semibold text-gray-800 mb-4">All Inventory</h2>
        <DataTable columns={columns} data={mockInventory} searchPlaceholder="Search products by name or SKU..." />
      </div>
    </div>
  );
}
