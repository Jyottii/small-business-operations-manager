import { useState } from 'react';
import GenericList from './GenericList';
import { Link, useNavigate } from 'react-router-dom';
import { StatusBadge } from '../components/ui/TabsAndBadges';
import CreatePOModal from '../components/workflows/CreatePOModal';

export const ProductsPage = () => (
  <GenericList 
    title="Products" 
    description="Manage product catalog."
    endpoint="/products"
    columns={[
      { header: 'Product Name', cell: (row) => <Link to={`/products/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'SKU', accessorKey: 'sku' },
      { header: 'Price', cell: (row) => `$${row.selling_price ? Number(row.selling_price).toFixed(2) : '0.00'}` },
      { header: 'Cost', cell: (row) => `$${row.cost_price ? Number(row.cost_price).toFixed(2) : '0.00'}` },
      { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    ]}
  />
);

export const OrdersPage = () => {
  const navigate = useNavigate();
  return (
    <GenericList 
      title="Orders" 
      description="Manage customer orders and their status."
      primaryAction="New Sale (POS)"
      onPrimaryAction={() => navigate('/sales')}
      endpoint="/orders"
      columns={[
        { header: 'Order ID', cell: (row) => <Link to={`/orders/${row.id}`} className="font-medium text-blue-600 hover:underline">{row.order_number}</Link> },
        { header: 'Date', cell: (row) => row.order_date ? new Date(row.order_date).toLocaleDateString() : '' },
        { header: 'Amount', cell: (row) => `$${row.total ? Number(row.total).toFixed(2) : '0.00'}` },
        { header: 'Paid', cell: (row) => `$${row.amount_paid ? Number(row.amount_paid).toFixed(2) : '0.00'}` },
        { header: 'Balance', cell: (row) => (
          <span className={Number(row.balance_due) > 0 ? 'text-red-600 font-semibold' : 'text-gray-500'}>
            ${row.balance_due ? Number(row.balance_due).toFixed(2) : '0.00'}
          </span>
        )},
        { header: 'Payment', cell: (row) => <StatusBadge status={row.payment_status} /> },
        { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
      ]}
    />
  );
};

export const CustomersPage = () => (
  <GenericList 
    title="Customers" 
    description="Manage your customer relationships and credit limits."
    endpoint="/customers"
    columns={[
      { header: 'Name', cell: (row) => <Link to={`/customers/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'Phone', accessorKey: 'phone' },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Credit Limit', cell: (row) => `$${row.credit_limit ? Number(row.credit_limit).toFixed(2) : '0.00'}` },
      { header: 'Outstanding Balance', cell: (row) => (
        <span className={Number(row.outstanding_balance) > 0 ? 'text-red-600 font-bold' : 'text-gray-500'}>
          ${row.outstanding_balance ? Number(row.outstanding_balance).toFixed(2) : '0.00'}
        </span>
      )},
    ]}
  />
);

export const SuppliersPage = () => (
  <GenericList 
    title="Suppliers" 
    description="Manage your suppliers and procurement accounts."
    endpoint="/suppliers"
    columns={[
      { header: 'Name', cell: (row) => <Link to={`/suppliers/${row.id}`} className="font-medium text-gray-900 hover:text-blue-600">{row.name}</Link> },
      { header: 'Company', accessorKey: 'company_name' },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Outstanding Payable', cell: (row) => (
        <span className={Number(row.outstanding_balance) > 0 ? 'text-red-600 font-bold' : 'text-gray-500'}>
          ${row.outstanding_balance ? Number(row.outstanding_balance).toFixed(2) : '0.00'}
        </span>
      )},
    ]}
  />
);

export const PurchaseOrdersPage = () => {
  const [poModalOpen, setPoModalOpen] = useState(false);
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <div>
      <GenericList 
        key={refreshKey}
        title="Purchase Orders" 
        description="Manage orders sent to suppliers and inventory procurement."
        primaryAction="Create Purchase Order"
        onPrimaryAction={() => setPoModalOpen(true)}
        endpoint="/purchase-orders"
        columns={[
          { header: 'PO Number', cell: (row) => <Link to={`/purchase-orders/${row.id}`} className="font-medium text-blue-600 hover:underline">{row.purchase_order_number}</Link> },
          { header: 'Date', cell: (row) => row.order_date ? new Date(row.order_date).toLocaleDateString() : '' },
          { header: 'Total Value', cell: (row) => `$${row.total ? Number(row.total).toFixed(2) : '0.00'}` },
          { header: 'Balance Due', cell: (row) => (
            <span className={Number(row.balance_due) > 0 ? 'text-red-600 font-semibold' : 'text-gray-500'}>
              ${row.balance_due ? Number(row.balance_due).toFixed(2) : '0.00'}
            </span>
          )},
          { header: 'Status', cell: (row) => <StatusBadge status={row.status} /> },
        ]}
      />
      <CreatePOModal 
        isOpen={poModalOpen}
        onClose={() => setPoModalOpen(false)}
        onSuccess={() => setRefreshKey(k => k + 1)}
      />
    </div>
  );
};

export const PaymentsPage = () => (
  <GenericList 
    title="Payments" 
    description="Track receivables and payables ledger."
    endpoint="/payments"
    columns={[
      { header: 'Reference', accessorKey: 'transaction_reference' },
      { header: 'Amount', cell: (row) => `$${row.amount ? Number(row.amount).toFixed(2) : '0.00'}` },
      { header: 'Date', cell: (row) => row.payment_date ? new Date(row.payment_date).toLocaleDateString() : '' },
      { header: 'Method', accessorKey: 'payment_method' },
      { header: 'Order Ref', accessorKey: 'order_id' },
      { header: 'PO Ref', accessorKey: 'purchase_order_id' },
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
      { header: 'Amount', cell: (row) => `$${row.amount ? Number(row.amount).toFixed(2) : '0.00'}` },
      { header: 'Date', cell: (row) => row.expense_date ? new Date(row.expense_date).toLocaleDateString() : '' },
    ]}
  />
);

export const EmployeesPage = () => (
  <GenericList 
    title="Employees" 
    description="Manage staff members and roles."
    endpoint="/employees"
    columns={[
      { header: 'Name', cell: (row) => <span className="font-medium text-gray-900">{row.first_name} {row.last_name}</span> },
      { header: 'Role', accessorKey: 'role' },
      { header: 'Email', accessorKey: 'email' },
      { header: 'Status', cell: (row) => <StatusBadge status={row.is_active ? 'Active' : 'Inactive'} /> },
    ]}
  />
);
