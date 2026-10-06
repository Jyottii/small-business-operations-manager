import React, { useState, useEffect, useRef } from 'react';
import { Outlet, Link, useLocation, useNavigate } from 'react-router-dom';
import {
  LayoutDashboard,
  ShoppingCart,
  Package,
  Users as UsersIcon,
  CreditCard,
  BarChart3,
  Settings,
  Menu,
  Bell,
  Search,
  ChevronLeft,
  ChevronRight,
  TrendingUp,
  FileText,
  UserCheck,
  Building,
  Activity,
  Box,
  Truck,
  ArrowLeftRight,
  DollarSign,
  LogOut,
  Store,
  X,
  Sparkles
} from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { apiClient } from '../api/client';

const navigation = [
  { name: 'Dashboard', href: '/', icon: LayoutDashboard, section: 'Overview', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Sales', href: '/sales', icon: ShoppingCart, section: 'Operations', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Orders', href: '/orders', icon: FileText, section: 'Operations', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Inventory', href: '/inventory', icon: Package, section: 'Operations', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Products', href: '/products', icon: Box, section: 'Operations', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Purchase Orders', href: '/purchase-orders', icon: ArrowLeftRight, section: 'Operations', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Suppliers', href: '/suppliers', icon: Truck, section: 'Operations', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Customers', href: '/customers', icon: UsersIcon, section: 'Operations', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Payments', href: '/payments', icon: CreditCard, section: 'Finance', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Expenses', href: '/expenses', icon: DollarSign, section: 'Finance', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Profit & Loss', href: '/profit-loss', icon: TrendingUp, section: 'Finance', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Cash Flow', href: '/cash-flow', icon: Activity, section: 'Finance', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Analytics', href: '/analytics', icon: BarChart3, section: 'Insights', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Smart Insights', href: '/smart-insights', icon: Activity, section: 'Insights', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Branches', href: '/branches', icon: Store, section: 'Management', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Warehouses', href: '/warehouses', icon: Building, section: 'Management', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Employees', href: '/employees', icon: UserCheck, section: 'Management', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Reports', href: '/reports', icon: FileText, section: 'Management', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Users', href: '/users', icon: UsersIcon, section: 'Management', roles: ['Owner', 'Admin'] },
  { name: 'Notifications', href: '/notifications', icon: Bell, section: 'System', roles: ['Owner', 'Admin', 'Manager', 'Staff'] },
  { name: 'Documents', href: '/documents', icon: FileText, section: 'System', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Audit Log', href: '/audit-log', icon: Activity, section: 'System', roles: ['Owner', 'Admin', 'Manager'] },
  { name: 'Settings', href: '/settings', icon: Settings, section: 'System', roles: ['Owner', 'Admin'] },
];

export default function MainLayout() {
  const { currentUser, role, logout } = useAuth();
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const location = useLocation();
  const navigate = useNavigate();

  // Search state
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [showSearchPopover, setShowSearchPopover] = useState(false);
  const searchRef = useRef(null);

  // Branch selector state
  const [branches, setBranches] = useState([]);
  const [selectedBranchId, setSelectedBranchId] = useState(localStorage.getItem('selected_branch_id') || '');

  useEffect(() => {
    // Load branches for header selector
    apiClient.get('/branches?page_size=50')
      .then(res => setBranches(res.data?.data || []))
      .catch(() => {});
  }, []);

  const handleBranchChange = (e) => {
    const val = e.target.value;
    setSelectedBranchId(val);
    if (val) {
      localStorage.setItem('selected_branch_id', val);
    } else {
      localStorage.removeItem('selected_branch_id');
    }
  };

  // Debounced search
  useEffect(() => {
    if (!searchQuery.trim()) {
      setSearchResults([]);
      setShowSearchPopover(false);
      return;
    }

    const timer = setTimeout(async () => {
      try {
        setSearching(true);
        const res = await apiClient.get(`/search?q=${encodeURIComponent(searchQuery.trim())}`);
        setSearchResults(res.data?.data?.results || []);
        setShowSearchPopover(true);
      } catch (err) {
        console.error(err);
      } finally {
        setSearching(false);
      }
    }, 250);

    return () => clearTimeout(timer);
  }, [searchQuery]);

  // Close search popover on outside click
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (searchRef.current && !searchRef.current.contains(e.target)) {
        setShowSearchPopover(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleResultClick = (url) => {
    setShowSearchPopover(false);
    setSearchQuery('');
    navigate(url);
  };

  const userInitials = currentUser?.name
    ? currentUser.name
        .split(' ')
        .map((n) => n[0])
        .join('')
        .substring(0, 2)
        .toUpperCase()
    : 'U';

  const roleStyles = {
    Owner: 'bg-purple-100 text-purple-800 border-purple-200',
    Admin: 'bg-blue-100 text-blue-800 border-blue-200',
    Manager: 'bg-emerald-100 text-emerald-800 border-emerald-200',
    Staff: 'bg-gray-100 text-gray-800 border-gray-200',
  };

  const filteredNav = navigation.filter((item) => !item.roles || item.roles.includes(role));

  const groupedNav = filteredNav.reduce((acc, item) => {
    if (!acc[item.section]) acc[item.section] = [];
    acc[item.section].push(item);
    return acc;
  }, {});

  return (
    <div className="flex h-screen overflow-hidden bg-gray-50">
      {/* Sidebar */}
      <aside
        className={`bg-white border-r border-gray-200 transition-all duration-300 flex flex-col ${
          sidebarOpen ? 'w-64' : 'w-20'
        }`}
      >
        <div className="h-16 flex items-center justify-between px-4 border-b border-gray-200">
          {sidebarOpen ? (
            <div className="flex items-center gap-2">
              <Store className="h-6 w-6 text-blue-600" />
              <span className="font-bold text-lg text-gray-900 truncate">SmallBiz Mgr</span>
            </div>
          ) : (
            <Store className="h-6 w-6 text-blue-600 mx-auto" />
          )}
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-1 rounded-md hover:bg-gray-100 text-gray-500 hidden sm:block"
          >
            {sidebarOpen ? <ChevronLeft size={18} /> : <ChevronRight size={18} />}
          </button>
        </div>

        <div className="flex-1 overflow-y-auto py-4">
          {Object.entries(groupedNav).map(([section, items]) => (
            <div key={section} className="mb-6">
              {sidebarOpen && (
                <h3 className="px-4 text-xs font-semibold text-gray-400 uppercase tracking-wider mb-2">
                  {section}
                </h3>
              )}
              <ul className="space-y-1">
                {items.map((item) => {
                  const isActive = location.pathname === item.href;
                  return (
                    <li key={item.name}>
                      <Link
                        to={item.href}
                        className={`flex items-center px-4 py-2 text-sm font-medium transition-colors ${
                          isActive
                            ? 'text-blue-600 bg-blue-50 border-r-2 border-blue-600'
                            : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                        }`}
                        title={!sidebarOpen ? item.name : undefined}
                      >
                        <item.icon
                          className={`flex-shrink-0 ${sidebarOpen ? 'mr-3' : 'mx-auto'} ${
                            isActive ? 'text-blue-600' : 'text-gray-400'
                          }`}
                          size={20}
                        />
                        {sidebarOpen && <span>{item.name}</span>}
                      </Link>
                    </li>
                  );
                })}
              </ul>
            </div>
          ))}
        </div>
      </aside>

      {/* Main Content */}
      <div className="flex-1 flex flex-col min-w-0 overflow-hidden">
        {/* Top Navigation */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center justify-between px-4 sm:px-6">
          <div className="flex items-center flex-1 gap-3">
            <button
              onClick={() => setSidebarOpen(!sidebarOpen)}
              className="p-2 -ml-2 mr-1 rounded-md hover:bg-gray-100 text-gray-500 sm:hidden"
            >
              <Menu size={20} />
            </button>

            {/* Universal Search Box with Debounced Popover */}
            <div ref={searchRef} className="max-w-md w-full relative hidden sm:block">
              <div className="absolute inset-y-0 left-0 pl-3 flex items-center pointer-events-none">
                <Search className="h-4 w-4 text-gray-400" />
              </div>
              <input
                type="text"
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                onFocus={() => { if (searchResults.length > 0) setShowSearchPopover(true); }}
                className="block w-full pl-9 pr-8 py-1.5 border border-gray-300 rounded-lg leading-5 bg-gray-50 placeholder-gray-400 focus:outline-none focus:bg-white focus:border-blue-500 focus:ring-1 focus:ring-blue-500 text-sm"
                placeholder="Universal Search (products, orders, customers)..."
              />
              {searchQuery && (
                <button
                  onClick={() => { setSearchQuery(''); setSearchResults([]); setShowSearchPopover(false); }}
                  className="absolute inset-y-0 right-0 pr-2.5 flex items-center text-gray-400 hover:text-gray-600"
                >
                  <X size={14} />
                </button>
              )}

              {/* Floating Search Popover */}
              {showSearchPopover && (
                <div className="absolute left-0 right-0 mt-1.5 bg-white border border-gray-200 rounded-xl shadow-xl z-50 max-h-96 overflow-y-auto">
                  <div className="p-2 border-b border-gray-100 flex items-center justify-between text-xs text-gray-500">
                    <span>Matches for "{searchQuery}"</span>
                    <span>{searchResults.length} result{searchResults.length === 1 ? '' : 's'}</span>
                  </div>
                  {searchResults.length === 0 ? (
                    <div className="p-4 text-center text-xs text-gray-500">
                      No matching records found.
                    </div>
                  ) : (
                    <div className="divide-y divide-gray-50">
                      {searchResults.map((item) => (
                        <div
                          key={`${item.category}-${item.id}`}
                          onClick={() => handleResultClick(item.url)}
                          className="p-3 hover:bg-blue-50 cursor-pointer flex items-center justify-between transition-colors"
                        >
                          <div>
                            <p className="text-sm font-semibold text-gray-900">{item.title}</p>
                            {item.subtitle && (
                              <p className="text-xs text-gray-500">{item.subtitle}</p>
                            )}
                          </div>
                          <span className="text-[10px] uppercase font-bold px-2 py-0.5 rounded bg-gray-100 text-gray-600">
                            {item.badge || item.category}
                          </span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>

            {/* Branch Selector */}
            {branches.length > 0 && (
              <div className="hidden md:flex items-center gap-1.5 pl-2 border-l border-gray-200">
                <Store size={15} className="text-gray-400" />
                <select
                  value={selectedBranchId}
                  onChange={handleBranchChange}
                  className="text-xs font-medium text-gray-700 bg-gray-50 border border-gray-200 rounded-md py-1 px-2 focus:ring-blue-500 focus:border-blue-500"
                >
                  <option value="">All Branches</option>
                  {branches.map(b => (
                    <option key={b.id} value={b.id}>{b.name} ({b.code})</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <div className="flex items-center space-x-3">
            {/* Demo Mode Badge */}
            <div className="hidden lg:flex items-center gap-1.5 px-2.5 py-1 bg-amber-50 text-amber-800 border border-amber-200 rounded-full text-xs font-medium">
              <Sparkles size={12} className="text-amber-600" />
              <span>Demo Mode</span>
            </div>

            <Link
              to="/notifications"
              className="p-2 text-gray-400 hover:text-gray-500 relative rounded-md hover:bg-gray-100"
            >
              <span className="absolute top-1.5 right-1.5 h-2 w-2 bg-red-500 rounded-full"></span>
              <Bell size={20} />
            </Link>
            <div className="h-6 w-px bg-gray-200 mx-1 hidden sm:block" />
            <div className="flex items-center gap-2.5">
              <div className="h-8 w-8 rounded-full bg-blue-100 flex items-center justify-center text-blue-700 font-bold text-xs border border-blue-200">
                {userInitials}
              </div>
              <div className="hidden md:flex flex-col text-left">
                <span className="text-xs font-semibold text-gray-900 leading-tight">
                  {currentUser?.name || 'User'}
                </span>
                <div className="flex items-center gap-1 mt-0.5">
                  <span className={`text-[10px] px-1.5 py-0.2 rounded font-semibold border ${roleStyles[role] || roleStyles.Staff}`}>
                    {role || 'Staff'}
                  </span>
                </div>
              </div>
              <button
                onClick={logout}
                title="Sign Out"
                className="p-1.5 ml-1 text-gray-400 hover:text-red-600 rounded-md hover:bg-red-50 transition-colors"
              >
                <LogOut size={18} />
              </button>
            </div>
          </div>
        </header>

        {/* Page Content */}
        <main className="flex-1 overflow-y-auto bg-gray-50 p-4 sm:p-6 lg:p-8">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
