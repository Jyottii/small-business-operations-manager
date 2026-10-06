import React, { useState } from 'react';
import { 
  FileText, Download, ArrowUpRight, Loader2, Eye, 
  TrendingUp, Package, Truck, Users, DollarSign, Table
} from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardBody } from '../../components/ui/Card';
import { apiClient } from '../../api/client';

const reports = [
  { id: 'sales', title: 'Sales Report', desc: 'Detailed view of sales volume, revenue, and order breakdown.', type: 'sales', icon: TrendingUp, color: 'text-blue-600 bg-blue-100' },
  { id: 'inventory', title: 'Inventory Report', desc: 'Current stock levels, inventory value, and low-stock alerts.', type: 'inventory', icon: Package, color: 'text-indigo-600 bg-indigo-100' },
  { id: 'purchases', title: 'Purchase Report', desc: 'Summary of purchase orders, supplier spend, and order statuses.', type: 'purchases', icon: Truck, color: 'text-purple-600 bg-purple-100' },
  { id: 'expenses', title: 'Expense Report', desc: 'Breakdown of operating expenses by category over time.', type: 'expenses', icon: DollarSign, color: 'text-red-600 bg-red-100' },
  { id: 'customers', title: 'Customer Report', desc: 'Customer accounts, total orders, and lifetime revenue generated.', type: 'customers', icon: Users, color: 'text-pink-600 bg-pink-100' },
];

export default function Reports() {
  const [exportingType, setExportingType] = useState(null);
  const [previewReport, setPreviewReport] = useState(null);
  const [previewLoading, setPreviewLoading] = useState(false);
  const [previewData, setPreviewData] = useState(null);

  const handleExport = async (type) => {
    try {
      setExportingType(type);
      const res = await apiClient.get(`/reports/export?report_type=${type}&format=csv`, {
        responseType: 'blob'
      });
      const url = window.URL.createObjectURL(new Blob([res.data], { type: 'text/csv' }));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `${type}_report_${new Date().toISOString().slice(0, 10)}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (err) {
      alert('Failed to export report CSV: ' + (err?.message || 'Server error'));
    } finally {
      setExportingType(null);
    }
  };

  const handlePreview = async (rep) => {
    try {
      setPreviewReport(rep);
      setPreviewLoading(true);
      const res = await apiClient.get(`/reports/${rep.type}`);
      setPreviewData(res.data?.data);
    } catch (err) {
      alert('Failed to load report preview');
    } finally {
      setPreviewLoading(false);
    }
  };

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Reports Center & Data Export</h1>
        <p className="text-sm text-gray-500 mt-1">
          Generate live operational reports, inspect metrics, and export data in standard CSV format.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {reports.map((report) => (
          <Card key={report.id} className="flex flex-col h-full hover:shadow-md transition-shadow border border-gray-200">
            <CardBody className="flex flex-col flex-1 p-5">
              <div className={`w-10 h-10 rounded-lg flex items-center justify-center mb-4 ${report.color}`}>
                <report.icon size={20} />
              </div>
              <h3 className="text-lg font-bold text-gray-900 mb-2">{report.title}</h3>
              <p className="text-sm text-gray-500 mb-6 flex-1">{report.desc}</p>
              
              <div className="flex items-center space-x-2 mt-auto">
                <button 
                  onClick={() => handlePreview(report)}
                  className="flex-1 py-2 bg-white border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 flex items-center justify-center gap-1 transition-colors"
                >
                  <Eye size={14} /> Preview
                </button>
                <button 
                  onClick={() => handleExport(report.type)}
                  disabled={exportingType === report.type}
                  className="flex-1 py-2 bg-blue-50 text-blue-700 border border-transparent rounded-md text-sm font-medium hover:bg-blue-100 flex items-center justify-center transition-colors disabled:opacity-50"
                >
                  {exportingType === report.type ? (
                    <Loader2 size={14} className="animate-spin mr-1" />
                  ) : (
                    <Download size={14} className="mr-1" />
                  )}
                  Export CSV
                </button>
              </div>
            </CardBody>
          </Card>
        ))}
      </div>

      {/* Live Preview Modal */}
      {previewReport && (
        <div className="fixed inset-0 z-50 bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-4xl w-full max-h-[85vh] flex flex-col">
            <div className="p-5 border-b border-gray-200 flex items-center justify-between">
              <div>
                <h2 className="text-lg font-bold text-gray-900">{previewReport.title} (Live Data)</h2>
                <p className="text-xs text-gray-500">Real-time aggregate calculations from current business ledger</p>
              </div>
              <div className="flex items-center gap-2">
                <button
                  onClick={() => handleExport(previewReport.type)}
                  className="px-3 py-1.5 text-xs font-semibold bg-blue-600 text-white rounded hover:bg-blue-700 flex items-center gap-1"
                >
                  <Download size={13} /> Export CSV
                </button>
                <button
                  onClick={() => { setPreviewReport(null); setPreviewData(null); }}
                  className="text-gray-400 hover:text-gray-600 text-xl font-bold ml-2"
                >
                  ×
                </button>
              </div>
            </div>

            <div className="p-5 overflow-y-auto flex-1">
              {previewLoading ? (
                <div className="flex justify-center items-center py-20 text-gray-500">
                  <Loader2 className="animate-spin mr-2" size={24} /> Loading report calculations...
                </div>
              ) : previewData ? (
                <div className="space-y-6">
                  {/* Top Summary Cards */}
                  <div className="grid grid-cols-2 sm:grid-cols-4 gap-3">
                    {previewReport.type === 'sales' && (
                      <>
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-blue-600">Total Revenue</p>
                          <p className="text-lg font-bold text-blue-900 mt-0.5">${previewData.total_revenue?.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-indigo-600">Orders Count</p>
                          <p className="text-lg font-bold text-indigo-900 mt-0.5">{previewData.order_count}</p>
                        </div>
                        <div className="p-3 bg-emerald-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-emerald-600">Avg Order Value</p>
                          <p className="text-lg font-bold text-emerald-900 mt-0.5">${previewData.average_order_value}</p>
                        </div>
                      </>
                    )}

                    {previewReport.type === 'inventory' && (
                      <>
                        <div className="p-3 bg-blue-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-blue-600">Total Valuation</p>
                          <p className="text-lg font-bold text-blue-900 mt-0.5">${previewData.total_valuation?.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-indigo-600">Total Units</p>
                          <p className="text-lg font-bold text-indigo-900 mt-0.5">{previewData.total_stock}</p>
                        </div>
                        <div className="p-3 bg-amber-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-amber-600">Low Stock SKUs</p>
                          <p className="text-lg font-bold text-amber-900 mt-0.5">{previewData.low_stock_count}</p>
                        </div>
                        <div className="p-3 bg-red-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-red-600">Out of Stock</p>
                          <p className="text-lg font-bold text-red-900 mt-0.5">{previewData.out_of_stock_count}</p>
                        </div>
                      </>
                    )}

                    {previewReport.type === 'purchases' && (
                      <>
                        <div className="p-3 bg-purple-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-purple-600">Total Spend</p>
                          <p className="text-lg font-bold text-purple-900 mt-0.5">${previewData.total_spend?.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-indigo-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-indigo-600">PO Count</p>
                          <p className="text-lg font-bold text-indigo-900 mt-0.5">{previewData.po_count}</p>
                        </div>
                      </>
                    )}

                    {previewReport.type === 'expenses' && (
                      <>
                        <div className="p-3 bg-red-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-red-600">Total Expenses</p>
                          <p className="text-lg font-bold text-red-900 mt-0.5">${previewData.total_expense?.toLocaleString()}</p>
                        </div>
                        <div className="p-3 bg-amber-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-amber-600">Expense Count</p>
                          <p className="text-lg font-bold text-amber-900 mt-0.5">{previewData.expense_count}</p>
                        </div>
                      </>
                    )}

                    {previewReport.type === 'customers' && (
                      <>
                        <div className="p-3 bg-pink-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-pink-600">Total Customers</p>
                          <p className="text-lg font-bold text-pink-900 mt-0.5">{previewData.total_customers}</p>
                        </div>
                        <div className="p-3 bg-red-50 rounded-lg">
                          <p className="text-[10px] uppercase font-bold text-red-600">Receivables</p>
                          <p className="text-lg font-bold text-red-900 mt-0.5">${previewData.total_receivables?.toLocaleString()}</p>
                        </div>
                      </>
                    )}
                  </div>

                  {/* Summary Raw Table */}
                  <div className="border border-gray-200 rounded-lg overflow-hidden">
                    <div className="p-3 bg-gray-50 border-b border-gray-200 text-xs font-semibold text-gray-700">
                      Sample Report Rows ({previewData.items?.length || previewData.orders?.length || previewData.expenses?.length || previewData.customers?.length || 0} rows)
                    </div>
                    <div className="max-h-60 overflow-y-auto text-xs">
                      {previewReport.type === 'sales' && (
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left">Order #</th>
                              <th className="px-4 py-2 text-left">Status</th>
                              <th className="px-4 py-2 text-right">Amount</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {previewData.orders?.map((o) => (
                              <tr key={o.id}>
                                <td className="px-4 py-2 font-mono">{o.order_number}</td>
                                <td className="px-4 py-2">{o.status}</td>
                                <td className="px-4 py-2 text-right">${Number(o.total_amount).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}

                      {previewReport.type === 'inventory' && (
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left">Product</th>
                              <th className="px-4 py-2 text-left">SKU</th>
                              <th className="px-4 py-2 text-left">Warehouse</th>
                              <th className="px-4 py-2 text-right">Qty</th>
                              <th className="px-4 py-2 text-right">Valuation</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {previewData.items?.map((it, idx) => (
                              <tr key={idx}>
                                <td className="px-4 py-2 font-medium">{it.product_name}</td>
                                <td className="px-4 py-2 font-mono text-gray-500">{it.sku}</td>
                                <td className="px-4 py-2">{it.warehouse_name}</td>
                                <td className="px-4 py-2 text-right font-semibold">{it.quantity}</td>
                                <td className="px-4 py-2 text-right">${Number(it.valuation).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}

                      {previewReport.type === 'customers' && (
                        <table className="min-w-full divide-y divide-gray-200">
                          <thead className="bg-gray-50">
                            <tr>
                              <th className="px-4 py-2 text-left">Customer</th>
                              <th className="px-4 py-2 text-left">Email</th>
                              <th className="px-4 py-2 text-right">Orders</th>
                              <th className="px-4 py-2 text-right">Total Spent</th>
                            </tr>
                          </thead>
                          <tbody className="divide-y divide-gray-100">
                            {previewData.customers?.map((c) => (
                              <tr key={c.id}>
                                <td className="px-4 py-2 font-medium">{c.name}</td>
                                <td className="px-4 py-2 text-gray-500">{c.email || 'N/A'}</td>
                                <td className="px-4 py-2 text-right">{c.total_orders}</td>
                                <td className="px-4 py-2 text-right font-semibold">${Number(c.total_spent).toFixed(2)}</td>
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      )}
                    </div>
                  </div>
                </div>
              ) : null}
            </div>

            <div className="p-4 border-t border-gray-200 flex justify-end">
              <button
                onClick={() => { setPreviewReport(null); setPreviewData(null); }}
                className="px-4 py-2 bg-gray-100 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-200"
              >
                Close Preview
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
