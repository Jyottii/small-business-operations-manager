import { useState } from 'react';
import { RotateCcw, X, Loader2 } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function ReturnModal({ isOpen, onClose, order, onSuccess }) {
  if (!isOpen || !order) return null;

  const [returnQtys, setReturnQtys] = useState({});
  const [reasons, setReasons] = useState({});
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleQtyChange = (productId, val) => {
    setReturnQtys(prev => ({
      ...prev,
      [productId]: parseFloat(val) || 0
    }));
  };

  const handleReasonChange = (productId, val) => {
    setReasons(prev => ({
      ...prev,
      [productId]: val
    }));
  };

  // Compute estimated refund
  const estimatedRefund = (order.order_items || []).reduce((acc, item) => {
    const qty = parseFloat(returnQtys[item.product_id]) || 0;
    return acc + (qty * parseFloat(item.unit_price || 0));
  }, 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const items = [];

    (order.order_items || []).forEach(item => {
      const qty = parseFloat(returnQtys[item.product_id]) || 0;
      if (qty > item.quantity) {
        setError(`Cannot return more than the sold quantity (${item.quantity}).`);
        return;
      }
      if (qty > 0) {
        items.push({
          product_id: item.product_id,
          quantity: qty,
          reason: reasons[item.product_id] || "Customer Return"
        });
      }
    });

    if (items.length === 0) {
      setError('Please select at least one item quantity to return.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await apiClient(`/orders/${order.id}/return`, {
        method: 'POST',
        body: {
          items,
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
              <RotateCcw className="mr-2 text-red-600" size={20} />
              Process Sales Return - {order.order_number}
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
              Select items to return. Restored inventory will be credited and refund calculated automatically.
            </p>

            <div className="overflow-x-auto border rounded-md">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Product</th>
                    <th className="px-3 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Sold</th>
                    <th className="px-3 py-2 text-right text-xs font-semibold text-gray-500 uppercase">Return Qty</th>
                    <th className="px-3 py-2 text-left text-xs font-semibold text-gray-500 uppercase">Reason</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {(order.order_items || []).map(item => (
                    <tr key={item.product_id}>
                      <td className="px-3 py-2 font-medium text-gray-900">{item.product_id}</td>
                      <td className="px-3 py-2 text-right text-gray-500">{item.quantity}</td>
                      <td className="px-3 py-2 text-right">
                        <input 
                          type="number" 
                          min="0"
                          max={item.quantity}
                          value={returnQtys[item.product_id] ?? 0}
                          onChange={(e) => handleQtyChange(item.product_id, e.target.value)}
                          className="w-16 border border-gray-300 rounded px-2 py-1 text-right text-sm focus:ring-blue-500"
                        />
                      </td>
                      <td className="px-3 py-2">
                        <select
                          value={reasons[item.product_id] || "Customer Return"}
                          onChange={(e) => handleReasonChange(item.product_id, e.target.value)}
                          className="border border-gray-300 rounded px-2 py-1 text-xs focus:ring-blue-500"
                        >
                          <option value="Customer Return">Customer Return</option>
                          <option value="Damaged">Damaged Goods</option>
                          <option value="Wrong Item">Wrong Item Shipped</option>
                          <option value="Other">Other</option>
                        </select>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>

            <div className="p-3 bg-gray-50 rounded-md flex justify-between items-center">
              <span className="text-sm font-medium text-gray-700">Estimated Total Refund:</span>
              <span className="text-lg font-bold text-red-600">${estimatedRefund.toFixed(2)}</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Return Notes (Optional)</label>
              <textarea 
                rows="2"
                placeholder="Reason or customer feedback..."
                value={notes} 
                onChange={(e) => setNotes(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
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
                className="px-4 py-2 bg-red-600 text-white rounded-md text-sm font-medium hover:bg-red-700 disabled:opacity-50 flex items-center"
              >
                {submitting && <Loader2 size={16} className="animate-spin mr-2" />}
                Confirm Return
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
