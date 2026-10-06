import { useState } from 'react';
import { PackageCheck, X, Loader2 } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function ReceiveGoodsModal({ isOpen, onClose, po, onSuccess }) {
  if (!isOpen || !po) return null;

  const [receiveQtys, setReceiveQtys] = useState(() => {
    const initial = {};
    (po.purchase_items || []).forEach(item => {
      const remaining = Math.max(0, (item.quantity_ordered || 0) - (item.quantity_received || 0));
      initial[item.product_id] = remaining > 0 ? remaining : 0;
    });
    return initial;
  });

  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleQtyChange = (productId, val) => {
    setReceiveQtys(prev => ({
      ...prev,
      [productId]: parseFloat(val) || 0
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const itemsToReceive = {};
    let totalToReceive = 0;

    (po.purchase_items || []).forEach(item => {
      const qty = parseFloat(receiveQtys[item.product_id]) || 0;
      const remaining = Math.max(0, (item.quantity_ordered || 0) - (item.quantity_received || 0));
      if (qty > remaining) {
        setError(`Cannot receive ${qty} for item. Only ${remaining} units remaining.`);
        return;
      }
      if (qty > 0) {
        itemsToReceive[item.product_id] = qty;
        totalToReceive += qty;
      }
    });

    if (totalToReceive <= 0) {
      setError('Please specify at least one item quantity to receive.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await apiClient(`/purchase-orders/${po.id}/receive`, {
        method: 'POST',
        body: {
          items: itemsToReceive,
          notes: notes || undefined
        }
      });

      if (onSuccess) onSuccess();
      onClose();
    } catch (err) {
      setError(err.message || String(err));
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="fixed inset-0 z-50 overflow-y-auto" role="dialog" aria-modal="true">
      <div className="flex items-center justify-center min-h-screen px-4 pt-4 pb-20 text-center sm:p-0">
        <div className="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity" onClick={onClose}></div>
        <div className="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-xl sm:w-full z-10 p-6">
          <div className="flex justify-between items-center pb-3 border-b">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <PackageCheck className="mr-2 text-blue-600" size={20} />
              Receive Goods - {po.purchase_order_number}
            </h3>
            <button onClick={onClose} className="text-gray-400 hover:text-gray-600">
              <X size={20} />
            </button>
          </div>

          {error && (
            <div className="my-3 p-3 bg-red-50 text-red-700 text-sm rounded-md border border-red-200">
              {error}
            </div>
          )}

          <form onSubmit={handleSubmit} className="mt-4 space-y-4">
            <p className="text-sm text-gray-500">
              Specify the quantities received for each line item. Inventory will increase automatically upon confirmation.
            </p>

            <div className="overflow-x-auto border rounded-md">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-4 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Product</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Ordered</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Received</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Remaining</th>
                    <th className="px-4 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Receive Now</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {(po.purchase_items || []).map(item => {
                    const remaining = Math.max(0, (item.quantity_ordered || 0) - (item.quantity_received || 0));
                    return (
                      <tr key={item.product_id}>
                        <td className="px-4 py-2 font-medium text-gray-900">{item.product_id}</td>
                        <td className="px-4 py-2 text-right text-gray-500">{item.quantity_ordered}</td>
                        <td className="px-4 py-2 text-right text-blue-600 font-medium">{item.quantity_received || 0}</td>
                        <td className="px-4 py-2 text-right font-medium">{remaining}</td>
                        <td className="px-4 py-2 text-right">
                          <input 
                            type="number" 
                            min="0"
                            max={remaining}
                            disabled={remaining === 0}
                            value={receiveQtys[item.product_id] ?? 0}
                            onChange={(e) => handleQtyChange(item.product_id, e.target.value)}
                            className="w-20 border border-gray-300 rounded px-2 py-1 text-right text-sm focus:ring-blue-500 focus:border-blue-500"
                          />
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Receipt Notes (Optional)</label>
              <textarea 
                rows="2"
                placeholder="e.g. Delivery batch 1 from carrier"
                value={notes} 
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div className="pt-3 flex justify-end space-x-2 border-t">
              <button 
                type="button" 
                onClick={onClose}
                className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50"
              >
                Cancel
              </button>
              <button 
                type="submit" 
                disabled={submitting}
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {submitting && <Loader2 size={16} className="animate-spin mr-2" />}
                Confirm Receipt
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
