import React, { useState, useEffect } from 'react';
import { Building2, Plus, MapPin, Phone, Mail, CheckCircle2, XCircle, Loader2, Store } from 'lucide-react';
import { apiClient } from '../../api/client';
import { useAuth } from '../../context/AuthContext';
import { Card, CardBody } from '../../components/ui/Card';

export default function Branches() {
  const { role } = useAuth();
  const [branches, setBranches] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Modal state
  const [showModal, setShowModal] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formData, setFormData] = useState({
    code: '',
    name: '',
    address: '',
    city: '',
    state: '',
    postal_code: '',
    phone: '',
    email: '',
    is_active: true
  });

  const canManage = ['Owner', 'Admin', 'Manager'].includes(role);

  const fetchBranches = async () => {
    try {
      setLoading(true);
      setError(null);
      const res = await apiClient.get('/branches?page_size=100');
      setBranches(res.data?.data || []);
    } catch (err) {
      setError(err?.message || 'Failed to load branches');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchBranches();
  }, []);

  const handleCreate = async (e) => {
    e.preventDefault();
    try {
      setSubmitting(true);
      setError(null);
      await apiClient.post('/branches', formData);
      setShowModal(false);
      setFormData({
        code: '',
        name: '',
        address: '',
        city: '',
        state: '',
        postal_code: '',
        phone: '',
        email: '',
        is_active: true
      });
      fetchBranches();
    } catch (err) {
      setError(err?.response?.data?.detail || err?.message || 'Failed to create branch');
    } finally {
      setSubmitting(false);
    }
  };

  const activeCount = branches.filter(b => b.is_active).length;

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <Store className="h-7 w-7 text-blue-600" />
            Multi-Store & Branch Management
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage your retail stores, satellite outlets, and business locations.
          </p>
        </div>
        {canManage && (
          <button
            onClick={() => setShowModal(true)}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm transition-colors"
          >
            <Plus size={16} /> Add Store / Branch
          </button>
        )}
      </div>

      {/* KPI Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <Card>
          <CardBody className="p-5 flex items-center gap-4">
            <div className="p-3 bg-blue-50 text-blue-600 rounded-lg">
              <Store size={24} />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Total Locations</p>
              <p className="text-2xl font-bold text-gray-900 mt-0.5">{branches.length}</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="p-5 flex items-center gap-4">
            <div className="p-3 bg-emerald-50 text-emerald-600 rounded-lg">
              <CheckCircle2 size={24} />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Active Stores</p>
              <p className="text-2xl font-bold text-emerald-600 mt-0.5">{activeCount}</p>
            </div>
          </CardBody>
        </Card>
        <Card>
          <CardBody className="p-5 flex items-center gap-4">
            <div className="p-3 bg-purple-50 text-purple-600 rounded-lg">
              <Building2 size={24} />
            </div>
            <div>
              <p className="text-xs font-medium text-gray-500 uppercase tracking-wider">Multi-Store Status</p>
              <p className="text-base font-bold text-purple-700 mt-0.5">
                {branches.length > 1 ? 'Multi-Branch Active' : 'Single Location'}
              </p>
            </div>
          </CardBody>
        </Card>
      </div>

      {error && (
        <div className="p-4 bg-red-50 border-l-4 border-red-500 text-red-700 text-sm rounded">
          {error}
        </div>
      )}

      {/* Branch List */}
      {loading ? (
        <div className="flex justify-center items-center py-20 text-gray-500">
          <Loader2 className="animate-spin mr-2" size={24} /> Loading branch locations...
        </div>
      ) : branches.length === 0 ? (
        <div className="text-center py-16 bg-white rounded-xl border border-gray-200">
          <Store className="mx-auto h-12 w-12 text-gray-300" />
          <h3 className="mt-2 text-sm font-semibold text-gray-900">No Branches Configured</h3>
          <p className="mt-1 text-sm text-gray-500">Create your first branch or store location to enable multi-location tracking.</p>
          {canManage && (
            <div className="mt-6">
              <button
                onClick={() => setShowModal(true)}
                className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 shadow-sm"
              >
                <Plus size={16} /> Create First Branch
              </button>
            </div>
          )}
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {branches.map((b) => (
            <Card key={b.id} className="hover:shadow-md transition-shadow border border-gray-200">
              <CardBody className="p-5 flex flex-col justify-between h-full">
                <div>
                  <div className="flex items-start justify-between">
                    <div>
                      <span className="inline-block px-2 py-0.5 text-xs font-semibold rounded bg-blue-100 text-blue-800 mb-2">
                        {b.code}
                      </span>
                      <h3 className="text-lg font-bold text-gray-900">{b.name}</h3>
                    </div>
                    <span
                      className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                        b.is_active ? 'bg-green-100 text-green-800' : 'bg-gray-100 text-gray-800'
                      }`}
                    >
                      {b.is_active ? 'Active' : 'Inactive'}
                    </span>
                  </div>

                  <div className="mt-4 space-y-2 text-sm text-gray-600">
                    {(b.address || b.city) && (
                      <div className="flex items-center gap-2">
                        <MapPin size={16} className="text-gray-400 flex-shrink-0" />
                        <span>{[b.address, b.city, b.state, b.postal_code].filter(Boolean).join(', ')}</span>
                      </div>
                    )}
                    {b.phone && (
                      <div className="flex items-center gap-2">
                        <Phone size={16} className="text-gray-400 flex-shrink-0" />
                        <span>{b.phone}</span>
                      </div>
                    )}
                    {b.email && (
                      <div className="flex items-center gap-2">
                        <Mail size={16} className="text-gray-400 flex-shrink-0" />
                        <span>{b.email}</span>
                      </div>
                    )}
                  </div>
                </div>

                <div className="mt-6 pt-4 border-t border-gray-100 flex items-center justify-between text-xs text-gray-400">
                  <span>Registered: {b.created_at ? new Date(b.created_at).toLocaleDateString() : 'N/A'}</span>
                </div>
              </CardBody>
            </Card>
          ))}
        </div>
      )}

      {/* Create Modal */}
      {showModal && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-40 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-xl max-w-md w-full p-6">
            <h2 className="text-lg font-bold text-gray-900 mb-4">Add Store / Branch Location</h2>
            <form onSubmit={handleCreate} className="space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Code *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. BR-DOWNTOWN"
                    value={formData.code}
                    onChange={(e) => setFormData({ ...formData, code: e.target.value.toUpperCase() })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Branch Name *</label>
                  <input
                    type="text"
                    required
                    placeholder="e.g. Downtown Outlet"
                    value={formData.name}
                    onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase">Street Address</label>
                <input
                  type="text"
                  placeholder="123 Commerce Way"
                  value={formData.address}
                  onChange={(e) => setFormData({ ...formData, address: e.target.value })}
                  className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">City</label>
                  <input
                    type="text"
                    placeholder="New York"
                    value={formData.city}
                    onChange={(e) => setFormData({ ...formData, city: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">State / Province</label>
                  <input
                    type="text"
                    placeholder="NY"
                    value={formData.state}
                    onChange={(e) => setFormData({ ...formData, state: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Phone</label>
                  <input
                    type="text"
                    placeholder="+1 (555) 000-0000"
                    value={formData.phone}
                    onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
                <div>
                  <label className="block text-xs font-semibold text-gray-700 uppercase">Email</label>
                  <input
                    type="email"
                    placeholder="branch@company.com"
                    value={formData.email}
                    onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                    className="mt-1 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm focus:ring-blue-500 focus:border-blue-500"
                  />
                </div>
              </div>

              <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-100">
                <button
                  type="button"
                  onClick={() => setShowModal(false)}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg text-sm font-medium hover:bg-gray-50"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="px-4 py-2 bg-blue-600 text-white rounded-lg text-sm font-semibold hover:bg-blue-700 disabled:opacity-50 flex items-center gap-2"
                >
                  {submitting && <Loader2 size={16} className="animate-spin" />}
                  Create Branch
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
