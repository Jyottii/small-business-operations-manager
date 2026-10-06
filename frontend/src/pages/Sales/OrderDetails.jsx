import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, DollarSign, RotateCcw, Ban, CheckCircle } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';
import { ConfirmationDialog } from '../../components/ui/States';
import PaymentModal from '../../components/workflows/PaymentModal';
import ReturnModal from '../../components/workflows/ReturnModal';

export default function OrderDetails() {
  const { id } = useParams();
  const { data: order, loading, error, refetch } = useApi(`/orders/${id}`);
  const { data: payments, refetch: refetchPayments } = useApi(`/orders/${id}/payments`);
  const { data: returns, refetch: refetchReturns } = useApi(`/orders/${id}/returns`);

  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [returnModalOpen, setReturnModalOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [cancelling, setCancelling] = useState(false);

  const handleRefresh = () => {
    refetch();
    refetchPayments();
    refetchReturns();
  };

  const handleCancelOrder = async () => {
    setCancelling(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      await apiClient(`/orders/${id}/cancel`, { method: 'POST' });
      setActionSuccess('Order cancelled successfully and inventory restored.');
      handleRefresh();
      setCancelDialogOpen(false);
    } catch (err) {
      setActionError(err.message || String(err));
      setCancelDialogOpen(false);
    } finally {
      setCancelling(false);
    }
  };

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

  const isCancelled = order.status === 'Cancelled';
  const hasBalance = parseFloat(order.balance_due || 0) > 0;
  const isPaid = order.payment_status === 'Paid';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header & Navigation */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <Link to="/orders" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">Order {order.order_number}</h1>
              <StatusBadge status={order.status} />
              <StatusBadge status={order.payment_status} />
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Placed on {order.order_date ? new Date(order.order_date).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        {!isCancelled && (
          <div className="flex flex-wrap items-center gap-2">
            {hasBalance && (
              <button 
                onClick={() => setPaymentModalOpen(true)}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium flex items-center shadow-sm"
              >
                <DollarSign size={16} className="mr-1" /> Record Payment
              </button>
            )}
            <button 
              onClick={() => setReturnModalOpen(true)}
              className="px-3 py-2 bg-white border border-gray-300 hover:bg-gray-50 text-gray-700 rounded-md text-sm font-medium flex items-center"
            >
              <RotateCcw size={16} className="mr-1 text-red-600" /> Return Items
            </button>
            <button 
              onClick={() => setCancelDialogOpen(true)}
              className="px-3 py-2 bg-white border border-red-200 hover:bg-red-50 text-red-600 rounded-md text-sm font-medium flex items-center"
            >
              <Ban size={16} className="mr-1" /> Cancel Order
            </button>
          </div>
        )}
      </div>

      {actionSuccess && (
        <div className="p-4 bg-green-50 text-green-700 rounded-md border border-green-200 flex items-center">
          <CheckCircle size={18} className="mr-2" />
          <span>{actionSuccess}</span>
        </div>
      )}

      {actionError && (
        <div className="p-4 bg-red-50 text-red-700 rounded-md border border-red-200">
          <span>{actionError}</span>
        </div>
      )}

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card>
          <CardHeader title="Order Information" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Customer ID</span>
              <span className="font-medium text-gray-900">{order.customer_id || 'Walk-in Customer'}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Status</span>
              <span className="font-medium">{order.status}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Notes</span>
              <span className="text-gray-700 text-sm">{order.notes || 'No notes provided'}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financial Summary" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Subtotal</span>
              <span className="font-medium">${Number(order.subtotal || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Tax</span>
              <span className="font-medium">${Number(order.tax || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-900 font-bold">Total Amount</span>
              <span className="font-bold text-gray-900">${Number(order.total || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-green-600 font-medium">Amount Paid</span>
              <span className="font-medium text-green-600">${Number(order.amount_paid || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-600 font-bold">Balance Due</span>
              <span className="font-bold text-red-600">${Number(order.balance_due || 0).toFixed(2)}</span>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* Order Line Items */}
      <Card>
        <CardHeader title="Order Items" />
        <CardBody className="p-0">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                <th className="px-6 py-3">Product ID</th>
                <th className="px-6 py-3 text-right">Qty</th>
                <th className="px-6 py-3 text-right">Unit Price</th>
                <th className="px-6 py-3 text-right">Tax</th>
                <th className="px-6 py-3 text-right">Line Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {(order.order_items || []).map((item, i) => (
                <tr key={i} className="hover:bg-gray-50">
                  <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_id}</td>
                  <td className="px-6 py-4 text-sm text-right text-gray-600">{Number(item.quantity)}</td>
                  <td className="px-6 py-4 text-sm text-right text-gray-600">${Number(item.unit_price).toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm text-right text-gray-600">${Number(item.tax_amount || 0).toFixed(2)}</td>
                  <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">${Number(item.line_total).toFixed(2)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardBody>
      </Card>

      {/* Payment History */}
      <Card>
        <CardHeader title="Payment History" />
        <CardBody className="p-0">
          {(!payments || payments.length === 0) ? (
            <div className="p-6 text-center text-sm text-gray-500">
              No payments recorded for this order yet.
            </div>
          ) : (
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Method</th>
                  <th className="px-6 py-3">Reference</th>
                  <th className="px-6 py-3 text-right">Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {payments.map(p => (
                  <tr key={p.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm text-gray-600">{p.payment_date ? new Date(p.payment_date).toLocaleDateString() : 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-gray-900 font-medium">{p.payment_method}</td>
                    <td className="px-6 py-4 text-sm text-gray-500">{p.transaction_reference || 'N/A'}</td>
                    <td className="px-6 py-4 text-sm text-right font-bold text-green-600">${Number(p.amount).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          )}
        </CardBody>
      </Card>

      {/* Return History */}
      {returns && returns.length > 0 && (
        <Card>
          <CardHeader title="Processed Returns" />
          <CardBody className="p-0">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gray-50">
                <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                  <th className="px-6 py-3">Return #</th>
                  <th className="px-6 py-3">Date</th>
                  <th className="px-6 py-3">Status</th>
                  <th className="px-6 py-3 text-right">Refund Amount</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-gray-200">
                {returns.map(r => (
                  <tr key={r.id} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{r.return_number}</td>
                    <td className="px-6 py-4 text-sm text-gray-600">{r.return_date ? new Date(r.return_date).toLocaleDateString() : 'N/A'}</td>
                    <td className="px-6 py-4 text-sm"><StatusBadge status={r.status} /></td>
                    <td className="px-6 py-4 text-sm text-right font-bold text-red-600">${Number(r.refund_amount).toFixed(2)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </CardBody>
        </Card>
      )}

      {/* Modals & Dialogs */}
      <PaymentModal 
        isOpen={paymentModalOpen} 
        onClose={() => setPaymentModalOpen(false)}
        targetType="order"
        targetId={order.id}
        balanceDue={order.balance_due}
        onSuccess={() => {
          setActionSuccess('Payment recorded successfully.');
          handleRefresh();
        }}
      />

      <ReturnModal 
        isOpen={returnModalOpen} 
        onClose={() => setReturnModalOpen(false)}
        order={order}
        onSuccess={() => {
          setActionSuccess('Return processed and inventory restored.');
          handleRefresh();
        }}
      />

      <ConfirmationDialog 
        isOpen={cancelDialogOpen} 
        title="Cancel Order" 
        description="Are you sure you want to cancel this order? Any deducted inventory will be automatically restored to the warehouse."
        confirmText={cancelling ? "Cancelling..." : "Yes, Cancel Order"}
        type="danger"
        onConfirm={handleCancelOrder}
        onCancel={() => setCancelDialogOpen(false)}
      />
    </div>
  );
}
