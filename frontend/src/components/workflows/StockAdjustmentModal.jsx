import { useState } from 'react';
import { SlidersHorizontal, X, Loader2 } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';

export default function StockAdjustmentModal({ isOpen, onClose, onSuccess, initialProductId = null }) {
  if (!isOpen) return null;

  const { data: products } = useApi('/products?page_size=100');
  const { data: warehouses } = useApi('/warehouses?page_size=50');

  const [productId, setProductId] = useState(initialProductId || '');
  const [warehouseId, setWarehouseId] = useState('');
  const [movementType, setMovementType] = useState('Stock In');
  const [quantity, setQuantity] = useState('');
  const [notes, setNotes] = useState('');
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const selProd = productId || (products && products[0]?.id);
    const selWh = warehouseId || (warehouses && warehouses[0]?.id);

    if (!selProd) {
      setError('Please select a product.');
      return;
    }
    if (!selWh) {
      setError('Please select a warehouse.');
      return;
    }

    const numQty = parseFloat(quantity);
    if (!numQty || numQty <= 0) {
      setError('Please enter a valid positive quantity.');
      return;
    }

    // Determine sign based on movement type
    const isNegative = ['Stock Out', 'Damage', 'Loss'].includes(movementType);
    const finalChange = isNegative ? -numQty : numQty;

    setSubmitting(true);
    setError(null);

    try {
      await apiClient('/inventory/adjust', {
        method: 'POST',
        body: {
          product_id: selProd,
          warehouse_id: selWh,
          quantity_change: finalChange,
          movement_type: movementType,
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
              <SlidersHorizontal className="mr-2 text-blue-600" size={20} />
              Manual Stock Adjustment
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
              <label className="block text-sm font-medium text-gray-700">Select Product</label>
              <select
                value={productId || (products && products[0]?.id) || ''}
                onChange={(e) => setProductId(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
              >
                {(products || []).map(p => (
                  <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Select Warehouse</label>
              <select
                value={warehouseId || (warehouses && warehouses[0]?.id) || ''}
                onChange={(e) => setWarehouseId(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
              >
                {(warehouses || []).map(w => (
                  <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Adjustment Type</label>
              <select
                value={movementType}
                onChange={(e) => setMovementType(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
              >
                <option value="Stock In">Stock In (+)</option>
                <option value="Stock Out">Stock Out (-)</option>
                <option value="Correction">Correction (+)</option>
                <option value="Damage">Damage (-)</option>
                <option value="Loss">Loss (-)</option>
                <option value="Found">Found (+)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Quantity Units</label>
              <input
                type="number"
                step="1"
                min="0.01"
                required
                placeholder="e.g. 5"
                value={quantity}
                onChange={(e) => setQuantity(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
              />
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Reason / Notes</label>
              <textarea
                rows="2"
                placeholder="Reason for adjustment..."
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
                className="px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 disabled:opacity-50 flex items-center"
              >
                {submitting && <Loader2 size={16} className="animate-spin mr-2" />}
                Save Adjustment
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
