import { useState } from 'react';
import { DollarSign, X, Loader2 } from 'lucide-react';
import { apiClient } from '../../api/client';

export default function PaymentModal({ isOpen, onClose, targetType = 'order', targetId, balanceDue, onSuccess }) {
  if (!isOpen) return null;

  const [amount, setAmount] = useState(balanceDue || '');
  const [method, setMethod] = useState(targetType === 'order' ? 'Cash' : 'Bank Transfer');
  const [reference, setReference] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const numAmount = parseFloat(amount);
    if (!numAmount || numAmount <= 0) {
      setError('Please enter a valid amount.');
      return;
    }
    if (balanceDue && numAmount > parseFloat(balanceDue)) {
      setError(`Amount cannot exceed the balance due of $${parseFloat(balanceDue).toFixed(2)}.`);
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      const endpoint = targetType === 'order' 
        ? `/orders/${targetId}/payments` 
        : `/purchase-orders/${targetId}/payments`;

      await apiClient(endpoint, {
        method: 'POST',
        body: {
          amount: numAmount,
          payment_method: method,
          transaction_reference: reference || undefined,
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
        <div className="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-md sm:w-full z-10 p-6">
          <div className="flex justify-between items-center pb-3 border-b">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <DollarSign className="mr-2 text-green-600" size={20} />
              Record {targetType === 'order' ? 'Customer' : 'Supplier'} Payment
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
            <div>
              <label className="block text-xs font-semibold text-gray-500 uppercase">Outstanding Balance</label>
              <p className="text-xl font-bold text-gray-900 mt-1">${parseFloat(balanceDue || 0).toFixed(2)}</p>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Amount ($)</label>
              <input 
                type="number" 
                step="0.01" 
                min="0.01"
                max={balanceDue}
                required
                value={amount} 
                onChange={(e) => setAmount(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Payment Method</label>
              <select 
                value={method} 
                onChange={(e) => setMethod(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="Cash">Cash</option>
                <option value="Card">Card</option>
                <option value="UPI">UPI</option>
                <option value="Bank Transfer">Bank Transfer</option>
                <option value="Check">Check</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Transaction Reference</label>
              <input 
                type="text" 
                placeholder="e.g. TXN-98472 or Cheque #"
                value={reference} 
                onChange={(e) => setReference(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
              <textarea 
                rows="2"
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
                Confirm Payment
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
