import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, User, Phone, Mail, DollarSign, ShoppingBag } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';

export default function CustomerDetails() {
  const { id } = useParams();
  const { data: customer, loading, error } = useApi(`/customers/${id}`);
  const { data: orders } = useApi(`/customers/${id}/orders`);

  if (loading) return (
    <div className="flex justify-center items-center h-64">
      <Loader2 className="h-8 w-8 animate-spin text-gray-500" />
    </div>
  );

  if (error || !customer) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading customer</p>
      <p className="text-sm mt-1">{error?.message || 'Customer not found'}</p>
    </div>
  );

  const totalSpent = (orders || []).reduce((acc, o) => acc + (parseFloat(o.total) || 0), 0);
  const outstanding = parseFloat(customer.outstanding_balance) || 0;
  const creditLimit = parseFloat(customer.credit_limit) || 0;
  const availableCredit = creditLimit > 0 ? Math.max(0, creditLimit - outstanding) : 0;

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div className="flex items-center space-x-4 mb-4">
        <Link to="/customers" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
          <ArrowLeft size={18} />
        </Link>
        <div>
          <h1 className="text-2xl font-bold text-gray-900">{customer.name}</h1>
          <p className="text-sm text-gray-500">Customer Profile & Account History</p>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader title="Contact Information" />
          <CardBody className="space-y-3">
            <div className="flex items-center text-sm text-gray-700">
              <Mail size={16} className="text-gray-400 mr-2" />
              <span>{customer.email || 'No email provided'}</span>
            </div>
            <div className="flex items-center text-sm text-gray-700">
              <Phone size={16} className="text-gray-400 mr-2" />
              <span>{customer.phone || 'No phone provided'}</span>
            </div>
            <div className="text-sm text-gray-500 pt-2 border-t">
              {customer.address ? `${customer.address}, ${customer.city || ''}` : 'No address on file'}
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financial Ledger" />
          <CardBody className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Spent</span>
              <span className="font-bold text-gray-900">${totalSpent.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Outstanding Balance</span>
              <span className={`font-bold ${outstanding > 0 ? 'text-red-600' : 'text-green-600'}`}>
                ${outstanding.toFixed(2)}
              </span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Credit Limit</span>
              <span className="font-medium">${creditLimit.toFixed(2)}</span>
            </div>
            <div className="flex justify-between text-sm pt-2 border-t">
              <span className="text-gray-500">Available Credit</span>
              <span className="font-semibold text-blue-600">${availableCredit.toFixed(2)}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Activity Overview" />
          <CardBody className="space-y-3">
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Total Orders</span>
              <span className="font-bold text-gray-900">{orders?.length || 0}</span>
            </div>
            <div className="flex justify-between text-sm">
              <span className="text-gray-500">Customer Type</span>
              <span className="font-medium text-gray-900">{customer.customer_type || 'Retail'}</span>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Orders List */}
      <Card>
        <CardHeader title="Customer Order History" />
        <CardBody className="p-0">
          {(!orders || orders.length === 0) ? (
            <div className="p-6 text-center text-sm text-gray-500">
              No orders recorded for this customer yet.
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">Order Number</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3 text-right">Total</th>
                  <th className="px-6 py-3 text-right">Balance Due</th>
                  <th className="px-6 py-3 text-center">Status</th>
                  <th className="px-6 py-3 text-center">Payment</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {orders.map(o => (
                  <tr key={o.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium">
                      <Link to={`/orders/${o.id}`} className="text-blue-600 hover:underline">
                        {o.order_number}
                      </Link>
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-600">
                      {o.order_date ? new Date(o.order_date).toLocaleDateString() : 'N/A'}
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-bold text-gray-900">
                      ${Number(o.total).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-right font-medium text-red-600">
                      ${Number(o.balance_due).toFixed(2)}
                    </td>
                    <td className="px-6 py-4 text-sm text-center">
                      <StatusBadge status={o.status} />
                    </td>
                    <td className="px-6 py-4 text-sm text-center">
                      <StatusBadge status={o.payment_status} />
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
