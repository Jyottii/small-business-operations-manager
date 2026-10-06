import os

pageConfigsContent = '''import GenericList from './GenericList';
import { Link } from 'react-router-dom';
import { StatusBadge } from '../components/ui/TabsAndBadges';

export const ProductsPage = () => (
  <GenericList 
    title="Products" 
    description="Manage product catalog."
    primaryAction="Add Product"
    endpoint="/products"
    columns={[
      { header: 'Product Name', cell: (row) => <Link to={`/products/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'SKU', accessorKey: 'sku' },
      { header: 'Price', cell: (row) => `$${row.selling_price ? row.selling_price.toFixed(2) : '0.00'}` },
      { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    ]}
  />
);

export const OrdersPage = () => (
  <GenericList 
    title="Orders" 
    description="Manage customer orders and their status."
    primaryAction="Create Order"
    endpoint="/orders"
    columns={[
      { header: 'Order ID', cell: (row) => <Link to={`/orders/${row.id}`} className="font-medium text-blue-600 hover:underline">{row.order_number}</Link> },
      { header: 'Date', cell: (row) => row.order_date ? new Date(row.order_date).toLocaleDateString() : '' },
      { header: 'Amount', cell: (row) => `$${row.total ? row.total.toFixed(2) : '0.00'}` },
      { header: 'Payment', cell: (row) => <StatusBadge status={row.payment_status} /> },
      { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
    ]}
  />
);

export const CustomersPage = () => (
  <GenericList 
    title="Customers" 
    description="Manage your customer relationships."
    primaryAction="Add Customer"
    endpoint="/customers"
    columns={[
      { header: 'Name', cell: (row) => <Link to={`/customers/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'Phone', accessorKey: 'phone' },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Outstanding Balance', cell: (row) => `$${row.outstanding_balance ? row.outstanding_balance.toFixed(2) : '0.00'}` },
    ]}
  />
);

export const SuppliersPage = () => (
  <GenericList 
    title="Suppliers" 
    description="Manage your suppliers and vendors."
    primaryAction="Add Supplier"
    endpoint="/suppliers"
    columns={[
      { header: 'Name', cell: (row) => <Link to={`/suppliers/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Outstanding', cell: (row) => <span className={row.outstanding_balance > 0 ? 'text-red-600 font-medium' : 'text-gray-500'}>${row.outstanding_balance ? row.outstanding_balance.toFixed(2) : '0.00'}</span> },
    ]}
  />
);

export const PurchaseOrdersPage = () => (
  <GenericList 
    title="Purchase Orders" 
    description="Manage orders sent to suppliers."
    primaryAction="Create PO"
    endpoint="/purchase-orders"
    columns={[
      { header: 'PO Number', cell: (row) => <Link to={`/purchase-orders/${row.id}`} className="font-medium text-blue-600 hover:underline">{row.purchase_order_number}</Link> },
      { header: 'Date', cell: (row) => row.order_date ? new Date(row.order_date).toLocaleDateString() : '' },
      { header: 'Amount', cell: (row) => `$${row.total ? row.total.toFixed(2) : '0.00'}` },
      { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
    ]}
  />
);

export const PaymentsPage = () => (
  <GenericList 
    title="Payments" 
    description="Track receivables and payables."
    primaryAction="Record Payment"
    endpoint="/payments"
    columns={[
      { header: 'Payment Ref', accessorKey: 'transaction_reference' },
      { header: 'Amount', cell: (row) => `$${row.amount ? row.amount.toFixed(2) : '0.00'}` },
      { header: 'Date', cell: (row) => row.payment_date ? new Date(row.payment_date).toLocaleDateString() : '' },
      { header: 'Method', accessorKey: 'payment_method' },
    ]}
  />
);

export const ExpensesPage = () => (
  <GenericList 
    title="Expenses" 
    description="Track business expenses."
    primaryAction="Add Expense"
    endpoint="/expenses"
    columns={[
      { header: 'Category', accessorKey: 'category' },
      { header: 'Description', accessorKey: 'description' },
      { header: 'Amount', cell: (row) => `$${row.amount ? row.amount.toFixed(2) : '0.00'}` },
      { header: 'Date', cell: (row) => row.expense_date ? new Date(row.expense_date).toLocaleDateString() : '' },
    ]}
  />
);

export const EmployeesPage = () => (
  <GenericList 
    title="Employees" 
    description="Manage staff members and roles."
    primaryAction="Add Employee"
    endpoint="/employees"
    columns={[
      { header: 'Name', cell: (row) => <span className="font-medium text-gray-900">{row.first_name} {row.last_name}</span> },
      { header: 'Role', accessorKey: 'role' },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    ]}
  />
);
'''
with open('src/pages/pageConfigs.jsx', 'w', encoding='utf-8') as f:
    f.write(pageConfigsContent)
