import { useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { ArrowLeft, Loader2, DollarSign, PackageCheck, Ban, CheckCircle } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { StatusBadge } from '../../components/ui/TabsAndBadges';
import { ConfirmationDialog } from '../../components/ui/States';
import PaymentModal from '../../components/workflows/PaymentModal';
import ReceiveGoodsModal from '../../components/workflows/ReceiveGoodsModal';

export default function PurchaseOrderDetails() {
  const { id } = useParams();
  const { data: po, loading, error, refetch } = useApi(`/purchase-orders/${id}`);
  const { data: payments, refetch: refetchPayments } = useApi(`/purchase-orders/${id}/payments`);

  const [receiveModalOpen, setReceiveModalOpen] = useState(false);
  const [paymentModalOpen, setPaymentModalOpen] = useState(false);
  const [cancelDialogOpen, setCancelDialogOpen] = useState(false);
  const [actionError, setActionError] = useState(null);
  const [actionSuccess, setActionSuccess] = useState(null);
  const [cancelling, setCancelling] = useState(false);

  const handleRefresh = () => {
    refetch();
    refetchPayments();
  };

  const handleCancelPO = async () => {
    setCancelling(true);
    setActionError(null);
    setActionSuccess(null);
    try {
      await apiClient(`/purchase-orders/${id}/cancel`, { method: 'POST' });
      setActionSuccess('Purchase Order cancelled successfully.');
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

  if (error || !po) return (
    <div className="text-red-500 bg-red-50 p-4 rounded-md inline-block">
      <p className="font-medium">Error loading PO details</p>
      <p className="text-sm mt-1">{error?.message || 'PO not found'}</p>
    </div>
  );

  const isCancelled = po.status === 'Cancelled';
  const isFullyReceived = po.status === 'Received';
  const hasBalance = parseFloat(po.balance_due || 0) > 0;
  const canReceive = !isCancelled && !isFullyReceived;
  const canCancel = !isCancelled && po.status === 'Ordered';

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div className="flex items-center space-x-4">
          <Link to="/purchase-orders" className="p-2 bg-white border border-gray-200 rounded-md hover:bg-gray-50 text-gray-600">
            <ArrowLeft size={18} />
          </Link>
          <div>
            <div className="flex items-center space-x-3">
              <h1 className="text-2xl font-bold text-gray-900">PO {po.purchase_order_number}</h1>
              <StatusBadge status={po.status} />
            </div>
            <p className="text-sm text-gray-500 mt-1">
              Ordered on {po.order_date ? new Date(po.order_date).toLocaleDateString() : 'N/A'}
            </p>
          </div>
        </div>

        {/* Action Buttons */}
        {!isCancelled && (
          <div className="flex flex-wrap items-center gap-2">
            {canReceive && (
              <button 
                onClick={() => setReceiveModalOpen(true)}
                className="px-3 py-2 bg-blue-600 hover:bg-blue-700 text-white rounded-md text-sm font-medium flex items-center shadow-sm"
              >
                <PackageCheck size={16} className="mr-1" /> Receive Goods
              </button>
            )}
            {hasBalance && (
              <button 
                onClick={() => setPaymentModalOpen(true)}
                className="px-3 py-2 bg-green-600 hover:bg-green-700 text-white rounded-md text-sm font-medium flex items-center shadow-sm"
              >
                <DollarSign size={16} className="mr-1" /> Record Supplier Payment
              </button>
            )}
            {canCancel && (
              <button 
                onClick={() => setCancelDialogOpen(true)}
                className="px-3 py-2 bg-white border border-red-200 hover:bg-red-50 text-red-600 rounded-md text-sm font-medium flex items-center"
              >
                <Ban size={16} className="mr-1" /> Cancel PO
              </button>
            )}
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
          <CardHeader title="Procurement Summary" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Supplier ID</span>
              <span className="font-medium text-gray-900">{po.supplier_id}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Destination Warehouse</span>
              <span className="font-medium">{po.warehouse_id}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Expected Delivery</span>
              <span className="font-medium">{po.expected_date ? new Date(po.expected_date).toLocaleDateString() : 'N/A'}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Notes</span>
              <span className="text-gray-700 text-sm">{po.notes || 'No notes'}</span>
            </div>
          </CardBody>
        </Card>

        <Card>
          <CardHeader title="Financial Status" />
          <CardBody className="space-y-4">
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-500">Subtotal</span>
              <span className="font-medium">${Number(po.subtotal || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-gray-900 font-bold">Total Ordered Value</span>
              <span className="font-bold text-gray-900">${Number(po.total || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between border-b pb-2">
              <span className="text-green-600 font-medium">Amount Paid</span>
              <span className="font-medium text-green-600">${Number(po.amount_paid || 0).toFixed(2)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-red-600 font-bold">Supplier Balance Due</span>
              <span className="font-bold text-red-600">${Number(po.balance_due || 0).toFixed(2)}</span>
            </div>
          </CardBody>
        </Card>
      </div>

      {/* PO Items Table */}
      <Card>
        <CardHeader title="Line Items & Receiving Status" />
        <CardBody className="p-0">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr className="text-left text-xs font-semibold text-gray-500 uppercase">
                <th className="px-6 py-3">Product ID</th>
                <th className="px-6 py-3 text-right">Ordered</th>
                <th className="px-6 py-3 text-right">Received</th>
                <th className="px-6 py-3 text-right">Remaining</th>
                <th className="px-6 py-3 text-right">Unit Cost</th>
                <th className="px-6 py-3 text-right">Total</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-200">
              {(po.purchase_items || []).map((item, i) => {
                const ordered = Number(item.quantity_ordered);
                const received = Number(item.quantity_received || 0);
                const remaining = Math.max(0, ordered - received);
                return (
                  <tr key={i} className="hover:bg-gray-50">
                    <td className="px-6 py-4 text-sm font-medium text-gray-900">{item.product_id}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-600">{ordered}</td>
                    <td className="px-6 py-4 text-sm text-right font-medium text-blue-600">{received}</td>
                    <td className="px-6 py-4 text-sm text-right font-medium text-gray-900">{remaining}</td>
                    <td className="px-6 py-4 text-sm text-right text-gray-600">${Number(item.unit_cost).toFixed(2)}</td>
                    <td className="px-6 py-4 text-sm text-right font-semibold text-gray-900">${Number(item.line_total).toFixed(2)}</td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </CardBody>
      </Card>

      {/* Supplier Payment History */}
      <Card>
        <CardHeader title="Supplier Payment History" />
        <CardBody className="p-0">
          {(!payments || payments.length === 0) ? (
            <div className="p-6 text-center text-sm text-gray-500">
              No payments recorded for this purchase order yet.
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

      {/* Workflow Modals */}
      <ReceiveGoodsModal 
        isOpen={receiveModalOpen} 
        onClose={() => setReceiveModalOpen(false)}
        po={po}
        onSuccess={() => {
          setActionSuccess('Goods received and inventory increased successfully.');
          handleRefresh();
        }}
      />

      <PaymentModal 
        isOpen={paymentModalOpen} 
        onClose={() => setPaymentModalOpen(false)}
        targetType="po"
        targetId={po.id}
        balanceDue={po.balance_due}
        onSuccess={() => {
          setActionSuccess('Supplier payment recorded successfully.');
          handleRefresh();
        }}
      />

      <ConfirmationDialog 
        isOpen={cancelDialogOpen} 
        title="Cancel Purchase Order" 
        description="Are you sure you want to cancel this purchase order? Outstanding supplier balance will be adjusted."
        confirmText={cancelling ? "Cancelling..." : "Yes, Cancel PO"}
        type="danger"
        onConfirm={handleCancelPO}
        onCancel={() => setCancelDialogOpen(false)}
      />
    </div>
  );
}
