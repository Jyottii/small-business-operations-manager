import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Link, Navigate } from 'react-router-dom';
import { AuthProvider } from './context/AuthContext';
import ProtectedRoute from './components/auth/ProtectedRoute';
import RoleRoute from './components/auth/RoleRoute';
import MainLayout from './layouts/MainLayout';

// Lazy-loaded pages for optimal bundle splitting
const Login = lazy(() => import('./pages/Auth/Login'));
const Register = lazy(() => import('./pages/Auth/Register'));
const Dashboard = lazy(() => import('./pages/Dashboard'));
const InventoryOverview = lazy(() => import('./pages/Inventory/Overview'));
const ProductDetails = lazy(() => import('./pages/Inventory/ProductDetails'));
const StockMovement = lazy(() => import('./pages/Inventory/StockMovement'));
const SalesPos = lazy(() => import('./pages/Sales/Pos'));
const OrderDetails = lazy(() => import('./pages/Sales/OrderDetails'));
const PurchaseOrderDetails = lazy(() => import('./pages/Purchases/PurchaseOrderDetails'));
const ProfitLoss = lazy(() => import('./pages/Finance/ProfitLoss'));
const CashFlow = lazy(() => import('./pages/Finance/CashFlow'));
const Reports = lazy(() => import('./pages/Management/Reports'));
const Branches = lazy(() => import('./pages/Management/Branches'));
const Warehouses = lazy(() => import('./pages/Management/Warehouses'));
const Settings = lazy(() => import('./pages/System/Settings'));
const Notifications = lazy(() => import('./pages/System/Notifications'));
const Documents = lazy(() => import('./pages/System/Documents'));
const AuditLog = lazy(() => import('./pages/System/AuditLog'));
const Users = lazy(() => import('./pages/System/Users'));
const CustomerDetails = lazy(() => import('./pages/Entities/CustomerDetails'));
const SupplierDetails = lazy(() => import('./pages/Entities/SupplierDetails'));
const SmartInsights = lazy(() => import('./pages/Insights/SmartInsights'));

import {
  ProductsPage, OrdersPage, CustomersPage, SuppliersPage,
  PurchaseOrdersPage, PaymentsPage, ExpensesPage,
  EmployeesPage
} from './pages/pageConfigs';

// Loading fallback component
const PageLoader = () => (
  <div className="flex items-center justify-center min-h-[350px] w-full">
    <div className="inline-block animate-spin rounded-full h-8 w-8 border-4 border-primary-200 border-t-primary-600"></div>
  </div>
);

// For non-implemented drilldowns
const ComingSoon = ({ title }) => (
  <div className="flex flex-col items-center justify-center h-full text-center py-20 bg-white rounded-lg border border-gray-200">
    <h1 className="text-2xl font-bold text-gray-900 mb-2">{title}</h1>
    <p className="text-gray-500 mb-4 max-w-md">This view is structured and ready for future development.</p>
    <Link to="/" className="text-blue-600 hover:underline">Return to Dashboard</Link>
  </div>
);

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <Suspense fallback={<PageLoader />}>
          <Routes>
            {/* Public Auth Routes */}
            <Route path="/login" element={<Login />} />
            <Route path="/register" element={<Register />} />

            {/* Protected Application Routes */}
            <Route
              path="/"
              element={
                <ProtectedRoute>
                  <MainLayout />
                </ProtectedRoute>
              }
            >
              {/* General Access (All authenticated roles) */}
              <Route index element={<Dashboard />} />
              
              {/* Operations: Sales & Orders */}
              <Route path="sales" element={<SalesPos />} />
              <Route path="orders" element={<OrdersPage />} />
              <Route path="orders/:id" element={<OrderDetails />} />
              
              {/* Operations: Inventory */}
              <Route path="inventory" element={<InventoryOverview />} />
              <Route path="products" element={<ProductsPage />} />
              <Route path="products/:id" element={<ProductDetails />} />
              <Route path="inventory/movement" element={<StockMovement />} />
              
              {/* Operations: Customers */}
              <Route path="customers" element={<CustomersPage />} />
              <Route path="customers/:id" element={<CustomerDetails />} />

              {/* Notifications */}
              <Route path="notifications" element={<Notifications />} />

              {/* Manager+ Access (Owner, Admin, Manager) */}
              <Route
                path="purchase-orders"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <PurchaseOrdersPage />
                  </RoleRoute>
                }
              />
              <Route
                path="purchase-orders/:id"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <PurchaseOrderDetails />
                  </RoleRoute>
                }
              />
              <Route
                path="suppliers"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <SuppliersPage />
                  </RoleRoute>
                }
              />
              <Route
                path="suppliers/:id"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <SupplierDetails />
                  </RoleRoute>
                }
              />
              <Route
                path="payments"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <PaymentsPage />
                  </RoleRoute>
                }
              />
              <Route
                path="expenses"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <ExpensesPage />
                  </RoleRoute>
                }
              />
              <Route
                path="profit-loss"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <ProfitLoss />
                  </RoleRoute>
                }
              />
              <Route
                path="cash-flow"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <CashFlow />
                  </RoleRoute>
                }
              />
              <Route
                path="analytics"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <ComingSoon title="Business Analytics" />
                  </RoleRoute>
                }
              />
              <Route
                path="smart-insights"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <SmartInsights />
                  </RoleRoute>
                }
              />
              <Route
                path="employees"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <EmployeesPage />
                  </RoleRoute>
                }
              />
              <Route
                path="warehouses"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <Warehouses />
                  </RoleRoute>
                }
              />
              <Route
                path="branches"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <Branches />
                  </RoleRoute>
                }
              />
              <Route
                path="reports"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <Reports />
                  </RoleRoute>
                }
              />
              <Route
                path="documents"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <Documents />
                  </RoleRoute>
                }
              />
              <Route
                path="audit-log"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin', 'Manager']}>
                    <AuditLog />
                  </RoleRoute>
                }
              />

              {/* Owner & Admin Only Access */}
              <Route
                path="users"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin']}>
                    <Users />
                  </RoleRoute>
                }
              />
              <Route
                path="settings"
                element={
                  <RoleRoute allowedRoles={['Owner', 'Admin']}>
                    <Settings />
                  </RoleRoute>
                }
              />
            </Route>

            {/* Catch-all route */}
            <Route path="*" element={<Navigate to="/" replace />} />
          </Routes>
        </Suspense>
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
