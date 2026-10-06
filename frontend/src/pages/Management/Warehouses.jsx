import React, { useState, useEffect } from 'react';
import { 
  Building, Plus, ArrowLeftRight, Package, AlertTriangle, 
  CheckCircle2, Clock, Truck, Loader2, DollarSign, Eye 
} from 'lucide-react';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Card, CardBody } from '../../components/ui/Card';

export default function Warehouses() {
  const { role } = useAuth();
  const [activeTab, setActiveTab] = useState('warehouses'); // 'warehouses' | 'transfers'

  // Warehouses state
  const [warehouses, setWarehouses] = useState([]);
  const [branches, setBranches] = useState([]);
  const [loadingWh, setLoadingWh] = useState(true);
  const [selectedWhSummary, setSelectedWhSummary] = useState(null);
  const [loadingSummary, setLoadingSummary] = useState(false);

  // Transfers state
  const [transfers, setTransfers] = useState([]);
  const [loadingTrf, setLoadingTrf] = useState(false);

  // Modals state
  const [showWhModal, setShowWhModal] = useState(false);
  const [showTrfModal, setShowTrfModal] = useState(false);
  const [products, setProducts] = useState([]);
  const [submitting, setSubmitting] = useState(false);
  const [errorMsg, setErrorMsg] = useState(null);

  // Form states
  const [whForm, setWhForm] = useState({ name: '', code: '', address: '', branch_id: '' });
  const [trfForm, setTrfForm] = useState({
    source_warehouse_id: '',
    destination_warehouse_id: '',
    product_id: '',
    quantity: 1,
    notes: ''
  });

  const canManage = ['Owner', 'Admin', 'Manager'].includes(role);

  const fetchWarehouses = async () => {
    try {
      setLoadingWh(true);
      const [whRes, brRes] = await Promise.all([
        apiClient.get('/warehouses?page_size=50'),
        apiClient.get('/branches?page_size=50')
      ]);
      setWarehouses(whRes.data?.data || []);
      setBranches(brRes.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingWh(false);
    }
  };

  const fetchTransfers = async () => {
    try {
      setLoadingTrf(true);
      const res = await apiClient.get('/stock-transfers?page_size=50');
      setTransfers(res.data?.data || []);
    } catch (err) {
      console.error(err);
    } finally {
      setLoadingTrf(false);
    }
  };

  const fetchProducts = async () => {
    try {
      const res = await apiClient.get('/products?page_size=100');
      setProducts(res.data?.data || []);
    } catch (err) {
      console.error(err);
    }
  };

  useEffect(() => {
    fetchWarehouses();
    fetchProducts();
  }, []);

  useEffect(() => {
    if (activeTab === 'transfers') {
      fetchTransfers();
    }
  }, [activeTab]);

  const viewWarehouseSummary = async (whId) => {
    try {
      setLoadingSummary(true);
      const res = await apiClient.get(`/warehouses/${whId}/summary`);
      setSelectedWhSummary(res.data?.data);
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to load summary');
    } finally {
      setLoadingSummary(false);
    }
  };

  const handleCreateWarehouse = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setErrorMsg(null);
      await apiClient.post('/warehouses', {
        name: whForm.name,
        code: whForm.code,
        address: whForm.address || undefined,
        branch_id: whForm.branch_id || undefined
      });
      setShowWhModal(false);
      setWhForm({ name: '', code: '', address: '', branch_id: '' });
      fetchWarehouses();
    } catch (err) {
      setErrorMsg(err?.response?.data?.detail || err?.message || 'Failed to create warehouse');
    } finally {
      setSubmitting(false);
    }
  };

  const handleCreateTransfer = async (e) => {
    e.preventDefault();
    if (trfForm.source_warehouse_id === trfForm.destination_warehouse_id) {
      setErrorMsg('Source and Destination warehouses must be different.');
      return;
    }
    try {
      setSubmitting(true);
      setErrorMsg(null);
      await apiClient.post('/stock-transfers', {
        source_warehouse_id: trfForm.source_warehouse_id,
        destination_warehouse_id: trfForm.destination_warehouse_id,
        notes: trfForm.notes,
        items: [
          {
            product_id: trfForm.product_id,
            quantity: parseFloat(trfForm.quantity)
          }
        ]
      });
      setShowTrfModal(false);
      setTrfForm({
        source_warehouse_id: '',
        destination_warehouse_id: '',
        product_id: '',
        quantity: 1,
        notes: ''
      });
      fetchTransfers();
    } catch (err) {
      setErrorMsg(err?.response?.data?.detail || err?.message || 'Failed to create transfer');
    } finally {
      setSubmitting(false);
    }
  };

  const handleTransitionTransfer = async (trfId, newStatus) => {
    if (!confirm(`Are you sure you want to mark this transfer as "${newStatus}"?`)) return;
    try {
      await apiClient.post(`/stock-transfers/${trfId}/status`, { status: newStatus });
      fetchTransfers();
      fetchWarehouses();
    } catch (err) {
      alert(err?.response?.data?.detail || 'Failed to update transfer status');
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Top Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Building className="h-7 w-7 text-blue-600" />
            Warehouse Management & Logistics
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Monitor inventory locations, valuation by facility, and warehouse-to-warehouse stock transfers.
          </p>
        </div>

        {canManage && (
          <div className="flex items-center gap-2">
            {activeTab === 'warehouses' ? (
              <button
                onClick={() => { setErrorMsg(null); setShowWhModal(true); }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm"
              >
                <Plus size={16} /> Add Warehouse
              </button>
            ) : (
              <button
                onClick={() => { setErrorMsg(null); setShowTrfModal(true); }}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm"
              >
                <ArrowLeftRight size={16} /> New Stock Transfer
              </button>
            )}
          </div>
        )}
      </div>

      {/* Tabs */}
      <div className="border-b border-gray-200">
        <nav className="flex space-x-8">
          <button
            onClick={() => setActiveTab('warehouses')}
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === 'warehouses'
                ? 'border-blue-600 text-blue-600 font-semibold'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <Building size={16} />
            Warehouses ({warehouses.length})
          </button>
          <button
            onClick={() => setActiveTab('transfers')}
            className={`py-3 px-1 border-b-2 font-medium text-sm flex items-center gap-2 ${
              activeTab === 'transfers'
                ? 'border-blue-600 text-blue-600 font-semibold'
                : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
            }`}
          >
            <ArrowLeftRight size={16} />
            Stock Transfers
          </button>
        </nav>
      </div>

      {/* WAREHOUSES TAB */}
      {activeTab === 'warehouses' && (
        <div className="space-y-6">
          {loadingWh ? (
            <div className="flex justify-center items-center py-20 text-gray-500">
              <Loader2 className="animate-spin mr-2" size={24} /> Loading warehouses...
            </div>
          ) : warehouses.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <Building className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No Warehouses Found</h3>
              <p className="mt-1 text-sm text-gray-500">Add a warehouse facility to start tracking inventory distribution.</p>
            </div>
          ) : (
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {warehouses.map((wh) => {
                const assignedBranch = branches.find(b => b.id === wh.branch_id);
                return (
                  <Card key={wh.id} className="hover:shadow-md transition-shadow border border-gray-200">
                    <CardBody className="p-5 flex flex-col justify-between h-full">
                      <div>
                        <div className="flex items-start justify-between">
                          <div>
                            <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded bg-blue-100 text-blue-800 mb-2">
                              {wh.code}
                            </span>
                            <h3 className="text-lg font-bold text-gray-900">{wh.name}</h3>
                          </div>
                          <span
                            className={`inline-flex items-center px-2 py-0.5 rounded text-xs font-medium ${
                              wh.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                            }`}
                          >
                            {wh.is_active ? 'Active' : 'Inactive'}
                          </span>
                        </div>

                        <div className="mt-4 space-y-2 text-sm text-gray-600">
                          {assignedBranch && (
                            <p className="text-xs font-medium text-blue-600 bg-blue-50 px-2 py-1 rounded inline-block">
                              Branch: {assignedBranch.name} ({assignedBranch.code})
                            </p>
                          )}
                          {wh.address && <p className="text-xs text-gray-500">{wh.address}</p>}
                        </div>
                      </div>

                      <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between">
                        <button
                          onClick={() => viewWarehouseSummary(wh.id)}
                          className="text-xs font-semibold text-blue-600 hover:text-blue-800 flex items-center gap-1.5 py-1 px-2.5 rounded bg-blue-50 hover:bg-blue-100 transition-colors"
                        >
                          <Eye size={14} /> View Stock Summary
                        </button>
                      </div>
                    </CardBody>
                  </Card>
                );
              })}
            </div>
          )}

          {/* Modal / Panel for Warehouse Summary */}
          {selectedWhSummary && (
            <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
              <div className="bg-white rounded-xl shadow-xl max-w-lg w-full p-6">
                <div className="flex items-center justify-between pb-4 border-b border-gray-200">
                  <div>
                    <h2 className="text-lg font-bold text-gray-900">
                      {selectedWhSummary.warehouse.name} ({selectedWhSummary.warehouse.code})
                    </h2>
                    <p className="text-xs text-gray-500">Facility Valuation & Inventory Status</p>
                  </div>
                  <button
                    onClick={() => setSelectedWhSummary(null)}
                    className="text-gray-400 hover:text-gray-600 text-xl font-bold"
                  >
                    ×
                  </button>
                </div>

                <div className="grid grid-cols-2 gap-4 my-6">
                  <div className="p-4 bg-blue-50 rounded-lg">
                    <p className="text-xs font-semibold text-blue-700 uppercase">Total Valuation</p>
                    <p className="text-2xl font-bold text-blue-900 mt-1">
                      ${Number(selectedWhSummary.total_valuation || 0).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </p>
                  </div>
                  <div className="p-4 bg-indigo-50 rounded-lg">
                    <p className="text-xs font-semibold text-indigo-700 uppercase">Stock Units</p>
                    <p className="text-2xl font-bold text-indigo-900 mt-1">
                      {selectedWhSummary.total_stock}
                    </p>
                  </div>
                  <div className="p-4 bg-amber-50 rounded-lg">
                    <p className="text-xs font-semibold text-amber-700 uppercase">Low Stock SKUs</p>
                    <p className="text-2xl font-bold text-amber-900 mt-1">
                      {selectedWhSummary.low_stock_count}
                    </p>
                  </div>
                  <div className="p-4 bg-red-50 rounded-lg">
                    <p className="text-xs font-semibold text-red-700 uppercase">Out of Stock</p>
                    <p className="text-2xl font-bold text-red-900 mt-1">
                      {selectedWhSummary.out_of_stock_count}
                    </p>
                  </div>
                </div>

                <div className="flex justify-end pt-4 border-t border-gray-100">
                  <button
                    onClick={() => setSelectedWhSummary(null)}
                    className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
                  >
                    Close
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      )}

      {/* STOCK TRANSFERS TAB */}
      {activeTab === 'transfers' && (
        <div className="space-y-6">
          {loadingTrf ? (
            <div className="flex justify-center items-center py-20 text-gray-500">
              <Loader2 className="animate-spin mr-2" size={24} /> Loading stock transfers...
            </div>
          ) : transfers.length === 0 ? (
            <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
              <ArrowLeftRight className="mx-auto h-12 w-12 text-gray-300" />
              <h3 className="mt-2 text-sm font-semibold text-gray-900">No Stock Transfers Recorded</h3>
              <p className="mt-1 text-sm text-gray-500">Initiate transfers between warehouses to rebalance stock.</p>
            </div>
          ) : (
            <div className="overflow-x-auto bg-white rounded-xl border border-gray-200 shadow-sm">
              <table className="min-w-full divide-y divide-gray-200 text-sm">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left font-semibold text-gray-600">Transfer #</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-600">Route</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-600">Items</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-600">Status</th>
                    <th className="px-6 py-3 text-left font-semibold text-gray-600">Date</th>
                    <th className="px-6 py-3 text-right font-semibold text-gray-600">Action</th>
                  </tr>
                </thead>
                <tbody className="divide-y divide-gray-200">
                  {transfers.map((trf) => {
                    const statusColor = {
                      Pending: 'bg-yellow-100 text-yellow-800',
                      'In Transit': 'bg-blue-100 text-blue-800',
                      Completed: 'bg-green-100 text-green-800',
                      Cancelled: 'bg-red-100 text-red-800'
                    }[trf.status] || 'bg-gray-100 text-gray-800';

                    return (
                      <tr key={trf.id} className="hover:bg-gray-50">
                        <td className="px-6 py-4 font-mono font-medium text-gray-900">{trf.transfer_number}</td>
                        <td className="px-6 py-4">
                          <div className="flex items-center gap-1.5 text-xs text-gray-700">
                            <span className="font-semibold text-gray-900">{trf.source_warehouse_name || 'Source'}</span>
                            <span className="text-gray-400">→</span>
                            <span className="font-semibold text-gray-900">{trf.destination_warehouse_name || 'Dest'}</span>
                          </div>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-600">
                          {trf.items?.map((it, idx) => (
                            <div key={idx}>
                              {it.product_name || 'Product'} × <strong>{it.quantity}</strong>
                            </div>
                          ))}
                        </td>
                        <td className="px-6 py-4">
                          <span className={`px-2.5 py-0.5 rounded-full text-xs font-medium ${statusColor}`}>
                            {trf.status}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-xs text-gray-500">
                          {trf.created_at ? new Date(trf.created_at).toLocaleDateString() : 'N/A'}
                        </td>
                        <td className="px-6 py-4 text-right">
                          {canManage && trf.status === 'Pending' && (
                            <button
                              onClick={() => handleTransitionTransfer(trf.id, 'In Transit')}
                              className="px-2.5 py-1 text-xs font-semibold bg-blue-50 text-blue-700 rounded hover:bg-blue-100"
                            >
                              Dispatch (Ship)
                            </button>
                          )}
                          {canManage && trf.status === 'In Transit' && (
                            <button
                              onClick={() => handleTransitionTransfer(trf.id, 'Completed')}
                              className="px-2.5 py-1 text-xs font-semibold bg-emerald-50 text-emerald-700 rounded hover:bg-emerald-100"
                            >
                              Receive (Complete)
                            </button>
                          )}
                          {trf.status === 'Completed' && (
                            <span className="text-xs text-emerald-600 font-medium">✓ Finalized</span>
                          )}
                        </td>
                      </tr>
                    );
                  })}
                </tbody>
              </table>
            </div>
          )}
        </div>
      )}

      {/* CREATE WAREHOUSE MODAL */}
      {showWhModal && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Add Warehouse Facility</h2>
            {errorMsg && <p className="mb-4 text-xs text-red-600 bg-red-50 p-2 rounded">{errorMsg}</p>}
            <form onSubmit={handleCreateWarehouse} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Warehouse Code *</label>
                <input
                  type="text"
                  required
                  placeholder="WH-NORTH"
                  value={whForm.code}
                  onChange={(e) => setWhForm({ ...whForm, code: e.target.value.toUpperCase() })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Warehouse Name *</label>
                <input
                  type="text"
                  required
                  placeholder="Northern Distribution Depot"
                  value={whForm.name}
                  onChange={(e) => setWhForm({ ...whForm, name: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Assign to Branch (Optional)</label>
                <select
                  value={whForm.branch_id}
                  onChange={(e) => setWhForm({ ...whForm, branch_id: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">No Branch Assigned (Central)</option>
                  {branches.map(b => (
                    <option key={b.id} value={b.id}>{b.name} ({b.code})</option>
                  ))}
                </select>
              </div>
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Address</label>
                <input
                  type="text"
                  placeholder="45 Industrial Park"
                  value={whForm.address}
                  onChange={(e) => setWhForm({ ...whForm, address: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowWhModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700"
                >
                  {submitting ? 'Creating...' : 'Create Warehouse'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* CREATE STOCK TRANSFER MODAL */}
      {showTrfModal && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Create Stock Transfer</h2>
            {errorMsg && <p className="mb-4 text-xs text-red-600 bg-red-50 p-2 rounded">{errorMsg}</p>}
            <form onSubmit={handleCreateTransfer} className="space-y-4">
              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Source Warehouse *</label>
                <select
                  required
                  value={trfForm.source_warehouse_id}
                  onChange={(e) => setTrfForm({ ...trfForm, source_warehouse_id: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">Select Origin...</option>
                  {warehouses.map(w => (
                    <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Destination Warehouse *</label>
                <select
                  required
                  value={trfForm.destination_warehouse_id}
                  onChange={(e) => setTrfForm({ ...trfForm, destination_warehouse_id: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">Select Destination...</option>
                  {warehouses.map(w => (
                    <option key={w.id} value={w.id}>{w.name} ({w.code})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Product Item *</label>
                <select
                  required
                  value={trfForm.product_id}
                  onChange={(e) => setTrfForm({ ...trfForm, product_id: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                  <option value="">Select Product...</option>
                  {products.map(p => (
                    <option key={p.id} value={p.id}>{p.name} ({p.sku})</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Transfer Quantity *</label>
                <input
                  type="number"
                  min="1"
                  required
                  value={trfForm.quantity}
                  onChange={(e) => setTrfForm({ ...trfForm, quantity: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Transfer Notes</label>
                <textarea
                  rows="2"
                  placeholder="e.g. Weekly store restocking"
                  value={trfForm.notes}
                  onChange={(e) => setTrfForm({ ...trfForm, notes: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                />
              </div>

              <div className="flex justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowTrfModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700"
                >
                  {submitting ? 'Creating...' : 'Initiate Transfer'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
