import { useState, useEffect } from 'react';
import { 
  Users as UsersIcon, 
  UserPlus, 
  X, 
  Loader2, 
  Shield, 
  CheckCircle, 
  AlertCircle,
  ToggleLeft,
  ToggleRight,
  Search,
  RefreshCw
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import { apiClient } from '../../api/client';

export default function Users() {
  const { currentUser, role: userRole } = useAuth();
  const [users, setUsers] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [searchTerm, setSearchTerm] = useState('');
  const [page, setPage] = useState(1);
  const [pagination, setPagination] = useState({ total: 0, total_pages: 1 });

  // Modal State
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [formError, setFormError] = useState(null);
  const [actionInProgress, setActionInProgress] = useState(null);

  // New User Form State
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    role: 'Staff',
    employee_id: '',
  });

  const fetchUsers = async () => {
    setLoading(true);
    setError(null);
    try {
      const query = `/users?page=${page}&page_size=15${searchTerm ? `&search=${encodeURIComponent(searchTerm)}` : ''}`;
      const res = await apiClient.get(query);
      setUsers(res.data || []);
      if (res.pagination) {
        setPagination(res.pagination);
      }
    } catch (err) {
      setError(err.message || 'Failed to fetch business users');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, [page, searchTerm]);

  const handleOpenModal = () => {
    setFormData({
      name: '',
      email: '',
      password: '',
      role: 'Staff',
      employee_id: '',
    });
    setFormError(null);
    setIsModalOpen(true);
  };

  const handleCreateUser = async (e) => {
    e.preventDefault();
    setFormError(null);

    if (!formData.name.trim() || !formData.email.trim() || !formData.password.trim()) {
      setFormError('Please fill in all required fields.');
      return;
    }
    if (formData.password.length < 8) {
      setFormError('Password must be at least 8 characters long.');
      return;
    }

    setSubmitting(true);
    try {
      const payload = {
        name: formData.name.trim(),
        email: formData.email.trim(),
        password: formData.password,
        role: formData.role,
        employee_id: formData.employee_id.trim() || null,
      };
      await apiClient.post('/users', payload);
      setIsModalOpen(false);
      await fetchUsers();
    } catch (err) {
      setFormError(err.message || 'Failed to create user');
    } finally {
      setSubmitting(false);
    }
  };

  const handleToggleActive = async (targetUser) => {
    if (targetUser.id === currentUser?.id) {
      return; // Cannot deactivate oneself
    }
    setActionInProgress(targetUser.id);
    try {
      await apiClient.patch(`/users/${targetUser.id}`, {
        is_active: !targetUser.is_active,
      });
      await fetchUsers();
    } catch (err) {
      alert(err.message || 'Failed to update user status');
    } finally {
      setActionInProgress(null);
    }
  };

  const getRoleBadge = (roleName) => {
    const styles = {
      Owner: 'bg-purple-100 text-purple-800 border-purple-200',
      Admin: 'bg-blue-100 text-blue-800 border-blue-200',
      Manager: 'bg-emerald-100 text-emerald-800 border-emerald-200',
      Staff: 'bg-gray-100 text-gray-800 border-gray-200',
    };
    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-semibold border ${styles[roleName] || styles.Staff}`}>
        {roleName}
      </span>
    );
  };

  // Roles available for creation based on current user role
  const availableRoles = userRole === 'Owner' 
    ? ['Admin', 'Manager', 'Staff']
    : ['Manager', 'Staff']; // Admin cannot create Owner or Admin

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
            <UsersIcon className="h-7 w-7 text-blue-600" />
            User Management
          </h1>
          <p className="text-sm text-gray-500 mt-1">
            Manage your team, assign security roles, and control access permissions.
          </p>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={fetchUsers}
            disabled={loading}
            className="p-2 text-gray-600 hover:text-gray-900 border border-gray-300 rounded-md bg-white hover:bg-gray-50 transition-colors"
            title="Refresh list"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? 'animate-spin' : ''}`} />
          </button>
          <button
            onClick={handleOpenModal}
            className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md shadow-sm text-sm font-medium hover:bg-blue-700 transition-colors"
          >
            <UserPlus size={16} />
            Add User
          </button>
        </div>
      </div>

      {/* Search and Filters */}
      <div className="bg-white p-4 rounded-lg border border-gray-200 shadow-sm flex items-center justify-between gap-4">
        <div className="relative flex-1 max-w-md">
          <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
            <Search className="h-4 w-4 text-gray-400" />
          </div>
          <input
            type="text"
            value={searchTerm}
            onChange={(e) => { setSearchTerm(e.target.value); setPage(1); }}
            placeholder="Search users by name or email..."
            className="block w-full pl-9 pr-3 py-2 border border-gray-300 rounded-md text-sm placeholder-gray-400 focus:outline-none focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
          />
        </div>
        <div className="text-sm text-gray-500">
          Total Users: <span className="font-semibold text-gray-800">{pagination.total || users.length}</span>
        </div>
      </div>

      {/* Error state */}
      {error && (
        <div className="bg-red-50 border border-red-200 text-red-700 px-4 py-3 rounded-md flex items-center gap-3">
          <AlertCircle className="h-5 w-5 flex-shrink-0" />
          <span className="text-sm">{error}</span>
        </div>
      )}

      {/* Users Table */}
      <div className="bg-white rounded-lg border border-gray-200 shadow-sm overflow-hidden">
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200 text-left text-sm">
            <thead className="bg-gray-50 text-gray-600 uppercase text-xs tracking-wider">
              <tr>
                <th className="px-6 py-3 font-semibold">User</th>
                <th className="px-6 py-3 font-semibold">Role</th>
                <th className="px-6 py-3 font-semibold">Status</th>
                <th className="px-6 py-3 font-semibold">Created</th>
                <th className="px-6 py-3 font-semibold text-right">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white">
              {loading ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                    <Loader2 className="h-6 w-6 animate-spin mx-auto text-blue-600 mb-2" />
                    Loading team members...
                  </td>
                </tr>
              ) : users.length === 0 ? (
                <tr>
                  <td colSpan="5" className="px-6 py-12 text-center text-gray-500">
                    No users found matching your criteria.
                  </td>
                </tr>
              ) : (
                users.map((u) => {
                  const isCurrent = u.id === currentUser?.id;
                  const isAdminEditingHighRole = userRole === 'Admin' && ['Owner', 'Admin'].includes(u.role);
                  const canModify = !isCurrent && !isAdminEditingHighRole;

                  return (
                    <tr key={u.id} className="hover:bg-gray-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap">
                        <div className="flex items-center">
                          <div className="h-10 w-10 flex-shrink-0 rounded-full bg-blue-100 text-blue-700 font-bold flex items-center justify-center">
                            {u.name?.charAt(0)?.toUpperCase() || 'U'}
                          </div>
                          <div className="ml-4">
                            <div className="font-medium text-gray-900 flex items-center gap-2">
                              {u.name}
                              {isCurrent && (
                                <span className="bg-blue-50 text-blue-600 text-[10px] font-semibold px-2 py-0.5 rounded border border-blue-200">
                                  You
                                </span>
                              )}
                            </div>
                            <div className="text-gray-500 text-xs">{u.email}</div>
                          </div>
                        </div>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        {getRoleBadge(u.role)}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap">
                        <span className={`inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full text-xs font-medium ${
                          u.is_active 
                            ? 'bg-green-50 text-green-700 border border-green-200' 
                            : 'bg-red-50 text-red-700 border border-red-200'
                        }`}>
                          <span className={`h-1.5 w-1.5 rounded-full ${u.is_active ? 'bg-green-500' : 'bg-red-500'}`} />
                          {u.is_active ? 'Active' : 'Inactive'}
                        </span>
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-gray-500 text-xs">
                        {u.created_at ? new Date(u.created_at).toLocaleDateString() : 'N/A'}
                      </td>
                      <td className="px-6 py-4 whitespace-nowrap text-right">
                        {canModify ? (
                          <button
                            onClick={() => handleToggleActive(u)}
                            disabled={actionInProgress === u.id}
                            className={`inline-flex items-center gap-1.5 text-xs font-medium px-3 py-1.5 rounded-md border transition-colors ${
                              u.is_active
                                ? 'text-red-700 bg-red-50 border-red-200 hover:bg-red-100'
                                : 'text-green-700 bg-green-50 border-green-200 hover:bg-green-100'
                            }`}
                          >
                            {actionInProgress === u.id ? (
                              <Loader2 className="h-3.5 w-3.5 animate-spin" />
                            ) : u.is_active ? (
                              <>
                                <ToggleLeft size={16} />
                                Deactivate
                              </>
                            ) : (
                              <>
                                <ToggleRight size={16} />
                                Activate
                              </>
                            )}
                          </button>
                        ) : (
                          <span className="text-xs text-gray-400 italic">
                            {isCurrent ? 'Protected' : 'No Permission'}
                          </span>
                        )}
                      </td>
                    </tr>
                  );
                })
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination */}
        {pagination.total_pages > 1 && (
          <div className="px-6 py-3 bg-gray-50 border-t border-gray-200 flex items-center justify-between text-sm text-gray-600">
            <div>
              Showing page {pagination.page} of {pagination.total_pages}
            </div>
            <div className="flex gap-2">
              <button
                disabled={pagination.page <= 1}
                onClick={() => setPage((p) => Math.max(1, p - 1))}
                className="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs"
              >
                Previous
              </button>
              <button
                disabled={pagination.page >= pagination.total_pages}
                onClick={() => setPage((p) => p + 1)}
                className="px-3 py-1 rounded border border-gray-300 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed text-xs"
              >
                Next
              </button>
            </div>
          </div>
        )}
      </div>

      {/* Add User Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 z-50 overflow-y-auto bg-black bg-opacity-50 flex items-center justify-center p-4">
          <div className="bg-white rounded-xl shadow-2xl max-w-md w-full overflow-hidden">
            {/* Modal Header */}
            <div className="flex items-center justify-between px-6 py-4 border-b border-gray-200 bg-gray-50">
              <div className="flex items-center gap-2">
                <Shield className="h-5 w-5 text-blue-600" />
                <h3 className="font-semibold text-gray-900">Add New Team Member</h3>
              </div>
              <button
                onClick={() => setIsModalOpen(false)}
                className="text-gray-400 hover:text-gray-600 transition-colors"
              >
                <X size={20} />
              </button>
            </div>

            {/* Modal Form */}
            <form onSubmit={handleCreateUser} className="p-6 space-y-4">
              {formError && (
                <div className="bg-red-50 border border-red-200 text-red-700 px-3 py-2 rounded-md text-xs flex items-center gap-2">
                  <AlertCircle className="h-4 w-4 flex-shrink-0" />
                  <span>{formError}</span>
                </div>
              )}

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Full Name *
                </label>
                <input
                  type="text"
                  required
                  value={formData.name}
                  onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                  placeholder="e.g. Alex Mercer"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Email Address *
                </label>
                <input
                  type="email"
                  required
                  value={formData.email}
                  onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                  placeholder="alex@company.com"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Initial Password *
                </label>
                <input
                  type="password"
                  required
                  minLength={8}
                  value={formData.password}
                  onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                  placeholder="Minimum 8 characters"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Role Assignment *
                </label>
                <select
                  value={formData.role}
                  onChange={(e) => setFormData({ ...formData, role: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500 bg-white"
                >
                  {availableRoles.map((r) => (
                    <option key={r} value={r}>
                      {r}
                    </option>
                  ))}
                </select>
                <p className="text-[11px] text-gray-500 mt-1">
                  {formData.role === 'Admin' && 'Full system control except business deletion and Owner account tampering.'}
                  {formData.role === 'Manager' && 'Full access to operations, purchases, inventory, finance, and reporting.'}
                  {formData.role === 'Staff' && 'Standard access to POS, orders, customers, and product viewing.'}
                </p>
              </div>

              <div>
                <label className="block text-xs font-semibold text-gray-700 uppercase tracking-wider mb-1">
                  Employee ID (Optional)
                </label>
                <input
                  type="text"
                  value={formData.employee_id}
                  onChange={(e) => setFormData({ ...formData, employee_id: e.target.value })}
                  placeholder="e.g. EMP-1042"
                  className="w-full px-3 py-2 border border-gray-300 rounded-md text-sm focus:ring-1 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>

              {/* Modal Actions */}
              <div className="flex items-center justify-end gap-3 pt-4 border-t border-gray-200 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  disabled={submitting}
                  className="px-4 py-2 border border-gray-300 rounded-md text-sm font-medium text-gray-700 hover:bg-gray-50 transition-colors"
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  disabled={submitting}
                  className="inline-flex items-center gap-2 px-4 py-2 bg-blue-600 text-white rounded-md text-sm font-medium hover:bg-blue-700 transition-colors disabled:opacity-50"
                >
                  {submitting ? (
                    <>
                      <Loader2 className="h-4 w-4 animate-spin" />
                      Creating...
                    </>
                  ) : (
                    'Create User'
                  )}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
}
