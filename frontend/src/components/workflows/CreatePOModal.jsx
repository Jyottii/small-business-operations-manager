import { useState } from 'react';
import { ShoppingBag, X, Plus, Trash2, Loader2 } from 'lucide-react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';

export default function CreatePOModal({ isOpen, onClose, onSuccess }) {
  if (!isOpen) return null;

  const { data: suppliers } = useApi('/suppliers?page_size=50');
  const { data: warehouses } = useApi('/warehouses?page_size=50');
  const { data: products } = useApi('/products?page_size=100');

  const [supplierId, setSupplierId] = useState('');
  const [warehouseId, setWarehouseId] = useState('');
  const [expectedDate, setExpectedDate] = useState('');
  const [notes, setNotes] = useState('');
  const [items, setItems] = useState([
    { product_id: '', quantity_ordered: 1, unit_cost: 0 }
  ]);
  const [submitting, setSubmitting] = useState(false);
  const [error, setError] = useState(null);

  const addItem = () => {
    setItems([...items, { product_id: products?.[0]?.id || '', quantity_ordered: 1, unit_cost: products?.[0]?.cost_price || 0 }]);
  };

  const removeItem = (idx) => {
    setItems(items.filter((_, i) => i !== idx));
  };

  const updateItem = (idx, field, val) => {
    const updated = [...items];
    if (field === 'product_id') {
      const prod = products?.find(p => p.id === val);
      updated[idx].product_id = val;
      if (prod && !updated[idx].unit_cost) {
        updated[idx].unit_cost = prod.cost_price || 0;
      }
    } else {
      updated[idx][field] = val;
    }
    setItems(updated);
  };

  const subtotal = items.reduce((acc, it) => acc + (parseFloat(it.quantity_ordered) || 0) * (parseFloat(it.unit_cost) || 0), 0);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const selSupp = supplierId || (suppliers && suppliers[0]?.id);
    const selWh = warehouseId || (warehouses && warehouses[0]?.id);

    if (!selSupp) {
      setError('Please select a supplier.');
      return;
    }
    if (!selWh) {
      setError('Please select a warehouse.');
      return;
    }

    const validItems = items.filter(it => it.product_id && parseFloat(it.quantity_ordered) > 0);
    if (validItems.length === 0) {
      setError('Please add at least one item with valid quantity.');
      return;
    }

    setSubmitting(true);
    setError(null);

    try {
      await apiClient('/purchase-orders', {
        method: 'POST',
        body: {
          supplier_id: selSupp,
          warehouse_id: selWh,
          expected_date: expectedDate ? new Date(expectedDate).toISOString() : undefined,
          notes: notes || undefined,
          items: validItems.map(it => ({
            product_id: it.product_id,
            quantity_ordered: parseFloat(it.quantity_ordered),
            unit_cost: parseFloat(it.unit_cost) || 0
          }))
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
        <div className="inline-block bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:max-w-2xl sm:w-full z-10 p-6">
          <div className="flex justify-between items-center pb-3 border-b">
            <h3 className="text-lg font-bold text-gray-900 flex items-center">
              <ShoppingBag className="mr-2 text-blue-600" size={20} />
              Create Purchase Order
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
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Supplier</label>
                <select
                  value={supplierId || (suppliers && suppliers[0]?.id) || ''}
                  onChange={(e) => setSupplierId(e.target.value)}
                  className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
                >
                  {(suppliers || []).map(s => (
                    <option key={s.id} value={s.id}>{s.name} ({s.company_name || 'Individual'})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Destination Warehouse</label>
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
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Expected Delivery Date (Optional)</label>
              <input 
                type="date"
                value={expectedDate}
                onChange={(e) => setExpectedDate(e.target.value)}
                className="mt-1 block w-full border border-gray-300 rounded-md px-3 py-2 text-sm focus:ring-blue-500"
              />
            </div>

            {/* PO Line Items */}
            <div>
              <div className="flex justify-between items-center mb-2">
                <label className="block text-sm font-semibold text-gray-800">Order Items</label>
                <button 
                  type="button" 
                  onClick={addItem}
                  className="text-xs bg-blue-50 text-blue-600 hover:bg-blue-100 font-medium px-2 py-1 rounded flex items-center"
                >
                  <Plus size={14} className="mr-1" /> Add Product
                </button>
              </div>

              <div className="space-y-2 border p-3 rounded-md max-h-56 overflow-y-auto">
                {items.map((it, idx) => (
                  <div key={idx} className="flex items-center space-x-2">
                    <select
                      value={it.product_id || (products?.[0]?.id || '')}
                      onChange={(e) => updateItem(idx, 'product_id', e.target.value)}
                      className="flex-1 border border-gray-300 rounded px-2 py-1 text-sm focus:ring-blue-500"
                    >
                      <option value="">Select product...</option>
                      {(products || []).map(p => (
                        <option key={p.id} value={p.id}>{p.name} (${p.cost_price})</option>
                      ))}
                    </select>
                    <input 
                      type="number"
                      min="1"
                      placeholder="Qty"
                      value={it.quantity_ordered}
                      onChange={(e) => updateItem(idx, 'quantity_ordered', e.target.value)}
                      className="w-20 border border-gray-300 rounded px-2 py-1 text-right text-sm"
                    />
                    <input 
                      type="number"
                      step="0.01"
                      min="0"
                      placeholder="Cost"
                      value={it.unit_cost}
                      onChange={(e) => updateItem(idx, 'unit_cost', e.target.value)}
                      className="w-24 border border-gray-300 rounded px-2 py-1 text-right text-sm"
                    />
                    <span className="text-sm font-medium w-20 text-right">
                      ${((parseFloat(it.quantity_ordered) || 0) * (parseFloat(it.unit_cost) || 0)).toFixed(2)}
                    </span>
                    {items.length > 1 && (
                      <button type="button" onClick={() => removeItem(idx)} className="text-red-500 hover:text-red-700 p-1">
                        <Trash2 size={16} />
                      </button>
                    )}
                  </div>
                ))}
              </div>
            </div>

            <div className="flex justify-between items-center p-3 bg-gray-50 rounded-md">
              <span className="font-semibold text-gray-700">Estimated Total:</span>
              <span className="text-xl font-bold text-gray-900">${subtotal.toFixed(2)}</span>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Notes (Optional)</label>
              <textarea 
                rows="2"
                placeholder="Shipping instructions or comments..."
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
                Submit Purchase Order
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
}
