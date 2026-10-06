import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, Phone, Mail, Building, DollarSign } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';

export default function SupplierDetails() {
  const { id } = useParams();
  const { data: supplier, loading, error } = useApi(`/suppliers/${id}`);
  const { data: pos } = useApi(`/suppliers/${id}/purchase-orders`);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
    </div>
  );

  if (error || !supplier) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading supplier</p>
      <p className="text-sm mt-1">{error?.message || 'Supplier not found'}</p>
    </div>
  );

  const totalPurchased = (pos || []).reduce((acc, p) => acc + (parseFloat(p.total) || 0), 0);
  const outstanding = parseFloat(supplier.outstanding_balance) || 0;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Link to="/suppliers" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{supplier.name}</h1>
          <p className="text-sm text-gray-500">Supplier Vendor Profile & Procurement History</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader title="Company Info" />
          <CardBody className="space-y-3">
            <div className="flex items-center text-sm text-gray-700">
              <Building size={16} className="text-gray-400 mr-2" />
              <span>{supplier.company_name || 'Individual Supplier'}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700">
              <Mail size={16} className="text-gray-400 mr-2" />
              <span>{supplier.email || 'No email provided'}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700">
              <Phone size={16} className="text-gray-400 mr-2" />
              <span>{supplier.phone || 'No phone provided'}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financial Ledger" />
          <CardBody className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Procured</span>
              <span className="font-bold text-gray-900">${totalPurchased.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Outstanding Payable</span>
              <span className={`font-bold ${outstanding > 0 ? 'text-red-600' : 'text-gray-900'}`}>
                ${outstanding.toFixed(2)}
              </span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Procurement Overview" />
          <CardBody className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Purchase Orders</span>
              <span className="font-bold text-gray-900">{pos?.length || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Payment Terms</span>
              <span className="font-medium text-gray-900">{supplier.payment_terms || 'Net 30'}</span>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* PO History */}
      <Card>
        <CardHeader title="Purchase Order History" />
        <CardBody className="p-0">
          {(!pos || pos.length === 0) ? (
            <div className="p-6 text-center text-sm text-gray-500">
              No purchase orders recorded for this supplier yet.
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">PO Number</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3 text-right">Total</th>
                  <th className="px-6 py-3 text-right">Balance Due</th>
                  <th className="px-6 py-3 text-center">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {pos.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium">
                      <Link to={`/purchase-orders/${p.id}`} className="text-blue-600 hover:underline">
                        {p.purchase_order_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {p.order_date ? new Date(p.order_date).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-bold text-gray-900">
                      ${Number(p.total).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-medium text-red-600">
                      ${Number(p.balance_due).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-center">
                      <StatusBadge status={p.status} />
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
