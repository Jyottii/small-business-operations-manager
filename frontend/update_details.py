import os

content = '''import { useParams, Link } from 'react-router-dom';
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
          <CardHeader title="Pricing" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Purchase Price</span>
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
              <span className="text-gray-500">Margin</span>
              <span className="font-medium">{margin}%</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Inventory Setup" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Minimum Stock</span>
              <span className="font-medium">{product.reorder_level || 0} units</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Reorder Quantity</span>
              <span className="font-medium">{product.reorder_quantity || 0} units</span>
            </div>
          </CardBody>
        </Card>
      </div>
    </div>
  );

  const InventoryTab = () => {
    const { data: inventoryData, loading: invLoading } = useApi(`/products/${id}/inventory`);
    
    if (invLoading) return <Loader2 className="animate-spin" />;
    
    return (
      <Card>
        <CardHeader title="Inventory Locations" />
        <CardBody>
          {inventoryData && inventoryData.length > 0 ? (
            inventoryData.map(inv => (
              <div key={inv.id} className="flex justify-between py-2 border-b last:border-0">
                <span>Warehouse: {inv.warehouse_id}</span>
                <span className="font-bold">{inv.quantity} units</span>
              </div>
            ))
          ) : (
            <p className="text-gray-500">No inventory records found.</p>
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
        <div className="w-32 h-32 bg-gray-100 rounded-lg flex items-center justify-center flex-shrink-0 border border-gray-200">
          <Package className="text-gray-400" size={48} />
        </div>
        <div className="flex-1 w-full">
          <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-4">
            <div>
              <h2 className="text-2xl font-bold text-gray-900 mb-1">{product.name}</h2>
              <div className="flex flex-wrap items-center gap-4 text-sm text-gray-500 mb-4">
                <span>SKU: {product.sku}</span>
                <span>Category: {product.category_id || 'N/A'}</span>
                <StatusBadge status={product.is_active ? 'Active' : 'Inactive'} />
              </div>
            </div>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mt-4">
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Price</p>
              <p className="font-semibold text-gray-900">${sellingPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Cost</p>
              <p className="font-semibold text-gray-900">${costPrice.toFixed(2)}</p>
            </div>
            <div>
              <p className="text-xs text-gray-500 uppercase tracking-wider">Margin</p>
              <p className="font-semibold text-green-600">{margin}%</p>
            </div>
          </div>
        </div>
      </div>

      <Tabs 
        tabs={[
          { id: 'overview', label: 'Overview', content: <OverviewTab /> },
          { id: 'inventory', label: 'Live Inventory', content: <InventoryTab /> }
        ]}
      />
    </div>
  );
}
'''
with open('src/pages/Inventory/ProductDetails.jsx', 'w', encoding='utf-8') as f:
    f.write(content)

order_content = '''import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, DollarSign } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';

export default function OrderDetails() {
  const { id } = useParams();
  const { data: order, loading, error } = useApi(`/orders/${id}`);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
    </div>
  );

  if (error || !order) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading order details</p>
      <p className="text-sm mt-1">{error?.message || 'Order not found'}</p>
    </div>
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Link to="/sales" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">Order {order.order_number}</h1>
        <StatusBadge status={order.status} />
        <StatusBadge status={order.payment_status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Order Summary" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Customer ID</span>
              <span className="font-medium">{order.customer_id}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Date</span>
              <span className="font-medium">{new Date(order.order_date).toLocaleDateString()}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financials" />
          <CardBody className="space-y-4">
             <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Subtotal</span>
              <span className="font-medium">${Number(order.subtotal).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Tax</span>
              <span className="font-medium">${Number(order.tax).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500 font-bold text-lg">Total</span>
              <span className="font-bold text-lg">${Number(order.total).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-red-600">
              <span className="font-bold">Balance Due</span>
              <span className="font-bold">${Number(order.balance_due).toFixed(2)}</span>
            </div>
          </CardBody>
        </Card>
      </div>
      
      <Card>
        <CardHeader title="Order Items" />
        <CardBody>
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="pb-3">Product ID</th>
                <th className="pb-3 text-right">Qty</th>
                <th className="pb-3 text-right">Unit Price</th>
                <th className="pb-3 text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {order.order_items?.map((item, i) => (
                <tr key={i}>
                  <td className="py-3 text-sm">{item.product_id}</td>
                  <td className="py-3 text-sm text-right">{Number(item.quantity)}</td>
                  <td className="py-3 text-sm text-right">${Number(item.unit_price).toFixed(2)}</td>
                  <td className="py-3 text-sm text-right font-medium">${Number(item.line_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
'''
with open('src/pages/Sales/OrderDetails.jsx', 'w', encoding='utf-8') as f:
    f.write(order_content)

po_content = '''import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, DollarSign } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';

export default function PurchaseOrderDetails() {
  const { id } = useParams();
  const { data: po, loading, error } = useApi(`/purchase-orders/${id}`);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
    </div>
  );

  if (error || !po) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading PO details</p>
      <p className="text-sm mt-1">{error?.message || 'PO not found'}</p>
    </div>
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Link to="/purchases" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <h1 className="text-2xl font-bold text-gray-900">PO {po.purchase_order_number}</h1>
        <StatusBadge status={po.status} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Summary" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Supplier ID</span>
              <span className="font-medium">{po.supplier_id}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Date</span>
              <span className="font-medium">{new Date(po.order_date).toLocaleDateString()}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financials" />
          <CardBody className="space-y-4">
             <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500 font-bold text-lg">Total</span>
              <span className="font-bold text-lg">${Number(po.total).toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-red-600">
              <span className="font-bold">Balance Due</span>
              <span className="font-bold">${Number(po.balance_due).toFixed(2)}</span>
            </div>
          </CardBody>
        </Card>
      </div>
      
      <Card>
        <CardHeader title="Items" />
        <CardBody>
          <table className="min-w-full divide-y divide-gray-200">
            <thead>
              <tr className="text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                <th className="pb-3">Product ID</th>
                <th className="pb-3 text-right">Ordered</th>
                <th className="pb-3 text-right">Received</th>
                <th className="pb-3 text-right">Unit Cost</th>
                <th className="pb-3 text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {po.purchase_items?.map((item, i) => (
                <tr key={i}>
                  <td className="py-3 text-sm">{item.product_id}</td>
                  <td className="py-3 text-sm text-right">{Number(item.quantity_ordered)}</td>
                  <td className="py-3 text-sm text-right font-medium text-blue-600">{Number(item.quantity_received)}</td>
                  <td className="py-3 text-sm text-right">${Number(item.unit_cost).toFixed(2)}</td>
                  <td className="py-3 text-sm text-right font-medium">${Number(item.line_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>
    </div>
  );
}
'''
with open('src/pages/Purchases/PurchaseOrderDetails.jsx', 'w', encoding='utf-8') as f:
    f.write(po_content)
