import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Edit, Trash, Package, Loader2 } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { Tabs, StatusBadge } from '../../components/ui/TabsAndBadges';

export default function ProductDetails() {
  const { id } = useParams();
  const { data, loading, error } = useApi(`/products/${id}`);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
    </div>
  );

  if (error || !data) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading product details</p>
      <p className="text-sm mt-1">{error?.message || 'Product not found'}</p>
    </div>
  );

  const product = data;
  const sellingPrice = Number(product.selling_price || 0);
  const costPrice = Number(product.cost_price || 0);
  const profit = sellingPrice - costPrice;
  const margin = sellingPrice > 0 ? ((profit / sellingPrice) * 100).toFixed(1) : '0.0';

  const OverviewTab = () => (
    <div className="space-y-6">
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Pricing & Profitability" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Purchase Cost</span>
              <span className="font-medium">${costPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Selling Price</span>
              <span className="font-medium">${sellingPrice.toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Profit per Unit</span>
              <span className="font-medium text-green-600">${profit.toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Profit Margin</span>
              <span className="font-medium">{margin}%</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Inventory Configuration" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Minimum Stock (Reorder Level)</span>
              <span className="font-medium">{product.reorder_level || 0} units</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Reorder Quantity</span>
              <span className="font-medium">{product.reorder_quantity || 0} units</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Barcode</span>
              <span className="font-mono text-gray-700">{product.barcode || 'N/A'}</span>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );

  const InventoryTab = () => {
    const { data: inventoryData, loading: invLoading } = useApi(`/products/${id}/inventory`);
    
    if (invLoading) return <div className="p-8 text-center"><Loader2 className="animate-spin inline" /></div>;
    
    return (
      <Card>
        <CardHeader title="Warehouse Inventory Breakdown" />
        <CardBody className="p-0">
          {inventoryData && inventoryData.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">Warehouse ID</th>
                  <th className="px-6 py-3 text-right">Available Stock</th>
                  <th className="px-6 py-3 text-right">Reorder Level</th>
                  <th className="px-6 py-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {inventoryData.map(inv => (
                  <tr key={inv.id}>
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{inv.warehouse_id}</td>
                    <td className="px-6 py-4 text-sm text-right font-bold text-gray-900">{inv.quantity} units</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-500">{inv.reorder_level}</td>
                    <td className="px-6 py-4 text-sm text-center">
                      <StatusBadge status={Number(inv.quantity) <= Number(inv.reorder_level) ? 'Low Stock' : 'In Stock'} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          ) : (
            <p className="p-6 text-gray-500 text-sm">No inventory records configured for this product.</p>
          )}
        </CardBody>
      </Card>
    );
  };

  const StockMovementsTab = () => {
    const { data: movements, loading: movLoading } = useApi(`/products/${id}/stock-movements`);

    if (movLoading) return <div className="p-8 text-center"><Loader2 className="animate-spin inline" /></div>;

    return (
      <Card>
        <CardHeader title="Recent Stock Movements (Audit Ledger)" />
        <CardBody className="p-0">
          {movements && movements.length > 0 ? (
            <table className="min-w-full divide-y divide-gray-200 text-sm">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Type</th>
                  <th className="px-6 py-3 text-right">Quantity</th>
                  <th className="px-6 py-3 text-right">Resulting Stock</th>
                  <th className="px-6 py-3">Reason / Reference</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {movements.map(m => {
                  const qty = Number(m.quantity);
                  return (
                    <tr key={m.id}>
                      <td className="px-6 py-3 text-gray-600">{m.created_at ? new Date(m.created_at).toLocaleDateString() : 'N/A'}</td>
                      <td className="px-6 py-3"><StatusBadge status={m.movement_type} /></td>
                      <td className={`px-6 py-3 text-right font-bold ${qty > 0 ? 'text-green-600' : 'text-red-600'}`}>
                        {qty > 0 ? `+${qty}` : qty}
                      </td>
                      <td className="px-6 py-3 text-right font-medium">{Number(m.resulting_quantity)}</td>
                      <td className="px-6 py-3 text-gray-500 text-xs">{m.notes || m.reference_type || 'Manual'}</td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          ) : (
            <p className="p-6 text-gray-500 text-sm">No recorded stock movements yet.</p>
          )}
        </CardBody>
      </Card>
    );
  };

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Link to="/products" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Product Details</h1>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 flex flex-col md:flex-row gap-6 items-start">
        <div className="w-28 h-28 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 border border-gray-200">
          <Package className="text-gray-400" size={40} />
        </div>
        <div className="flex-1 w-full">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">{product.name}</h2>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-4">
                <span>SKU: {product.sku}</span>
                <StatusBadge status={product.is_active ? 'Active' : 'Inactive'} />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-3 gap-4 mt-2">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Selling Price</p>
              <p className="font-semibold text-gray-900 text-lg">${sellingPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Cost Price</p>
              <p className="font-semibold text-gray-900 text-lg">${costPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Gross Margin</p>
              <p className="font-semibold text-green-600 text-lg">{margin}%</p>
            </div>
          </div>
        </div>
      </div>

      <Tabs 
        tabs={[
          { id: 'overview', label: 'Overview', content: <OverviewTab /> },
          { id: 'inventory', label: 'Live Inventory Breakdown', content: <InventoryTab /> },
          { id: 'movements', label: 'Stock Movement Ledger', content: <StockMovementsTab /> }
        ]}
      />
    </div>
  );
}
