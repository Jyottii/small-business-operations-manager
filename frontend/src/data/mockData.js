export const mockSuppliers = [
  { id: 'SUP-001', name: 'Global Electronics', contact: 'John Doe', phone: '(555) 123-1111', email: 'sales@globalelectronics.com', products: 45, outstanding: 2500.00, status: 'Active' },
  { id: 'SUP-002', name: 'Office Supplies Inc', contact: 'Jane Smith', phone: '(555) 123-2222', email: 'orders@officesupplies.com', products: 120, outstanding: 0.00, status: 'Active' },
  { id: 'SUP-003', name: 'Tech Components Ltd', contact: 'Sam Wilson', phone: '(555) 123-3333', email: 'b2b@techcomp.com', products: 15, outstanding: 1250.00, status: 'Active' },
];

export const mockProducts = [
  { id: 1, name: 'Wireless Mouse', sku: 'WM-001', category: 'Electronics', stock: 145, minStock: 50, reorderQty: 100, purchasePrice: 15.00, sellingPrice: 29.99, status: 'In Stock', supplierId: 'SUP-001', supplierName: 'Global Electronics', warehouse: 'Main Warehouse' },
  { id: 2, name: 'Mechanical Keyboard', sku: 'MK-023', category: 'Electronics', stock: 12, minStock: 20, reorderQty: 30, purchasePrice: 45.00, sellingPrice: 89.99, status: 'Low Stock', supplierId: 'SUP-001', supplierName: 'Global Electronics', warehouse: 'Main Warehouse' },
  { id: 3, name: 'USB-C Hub', sku: 'UH-112', category: 'Accessories', stock: 0, minStock: 30, reorderQty: 50, purchasePrice: 20.00, sellingPrice: 45.00, status: 'Out of Stock', supplierId: 'SUP-003', supplierName: 'Tech Components Ltd', warehouse: 'Retail Store' },
  { id: 4, name: 'Laptop Stand', sku: 'LS-099', category: 'Accessories', stock: 68, minStock: 25, reorderQty: 40, purchasePrice: 12.50, sellingPrice: 34.50, status: 'In Stock', supplierId: 'SUP-002', supplierName: 'Office Supplies Inc', warehouse: 'Main Warehouse' },
  { id: 5, name: '27" Monitor', sku: 'MN-270', category: 'Electronics', stock: 5, minStock: 10, reorderQty: 15, purchasePrice: 180.00, sellingPrice: 299.00, status: 'Low Stock', supplierId: 'SUP-001', supplierName: 'Global Electronics', warehouse: 'Main Warehouse' },
];

export const mockCustomers = [
  { id: 'CUST-001', name: 'Alice Smith', phone: '(555) 123-4567', email: 'alice@example.com', orders: 12, totalSpent: 1450.00, status: 'VIP' },
  { id: 'CUST-002', name: 'Bob Johnson', phone: '(555) 987-6543', email: 'bob@example.com', orders: 3, totalSpent: 150.00, status: 'Active' },
  { id: 'CUST-003', name: 'Tech Corp', phone: '(555) 555-5555', email: 'billing@techcorp.com', orders: 45, totalSpent: 12500.00, status: 'VIP' },
  { id: 'CUST-004', name: 'Walk-in Customer', phone: 'N/A', email: 'N/A', orders: 1, totalSpent: 45.00, status: 'Active' },
];

export const mockOrders = [
  { id: 'ORD-1024', customerId: 'CUST-001', customer: 'Alice Smith', date: '2023-10-24', items: 3, amount: 145.50, payment: 'Paid', status: 'Completed' },
  { id: 'ORD-1025', customerId: 'CUST-002', customer: 'Bob Johnson', date: '2023-10-24', items: 1, amount: 29.99, payment: 'Pending', status: 'Processing' },
  { id: 'ORD-1026', customerId: 'CUST-004', customer: 'Walk-in Customer', date: '2023-10-25', items: 5, amount: 450.00, payment: 'Paid', status: 'Completed' },
  { id: 'ORD-1027', customerId: 'CUST-003', customer: 'Tech Corp', date: '2023-10-25', items: 12, amount: 1250.00, payment: 'Unpaid', status: 'Pending' },
];

export const mockOrderDetails = {
  'ORD-1024': {
    id: 'ORD-1024',
    customer: mockCustomers[0],
    date: '2023-10-24 14:30',
    status: 'Completed',
    paymentStatus: 'Paid',
    paymentMethod: 'Credit Card',
    items: [
      { product: mockProducts[0], qty: 2, price: 29.99, total: 59.98 },
      { product: mockProducts[3], qty: 1, price: 34.50, total: 34.50 }
    ],
    subtotal: 94.48,
    tax: 7.56,
    total: 102.04
  }
};

export const mockPurchaseOrders = [
  { id: 'PO-2023', supplierId: 'SUP-001', supplier: 'Global Electronics', date: '2023-10-20', expected: '2023-10-28', amount: 4500.00, status: 'Ordered' },
  { id: 'PO-2024', supplierId: 'SUP-002', supplier: 'Office Supplies Inc', date: '2023-10-25', expected: '2023-10-27', amount: 850.00, status: 'Draft' },
  { id: 'PO-2025', supplierId: 'SUP-003', supplier: 'Tech Components Ltd', date: '2023-10-15', expected: '2023-10-18', amount: 1200.00, status: 'Partially Received' },
];

export const mockPODetails = {
  'PO-2023': {
    id: 'PO-2023',
    supplier: mockSuppliers[0],
    date: '2023-10-20',
    expected: '2023-10-28',
    status: 'Ordered',
    paymentStatus: 'Unpaid',
    items: [
      { product: mockProducts[4], qty: 20, received: 0, price: 180.00, total: 3600.00 },
      { product: mockProducts[1], qty: 20, received: 0, price: 45.00, total: 900.00 }
    ],
    total: 4500.00
  }
};

export const mockPayments = [
  { id: 'PAY-100', ref: 'ORD-1024', type: 'Money In', entity: 'Alice Smith', amount: 145.50, date: '2023-10-24', method: 'Credit Card', status: 'Completed' },
  { id: 'PAY-101', ref: 'PO-2022', type: 'Money Out', entity: 'Global Electronics', amount: 2500.00, date: '2023-10-25', method: 'Bank Transfer', status: 'Completed' },
  { id: 'PAY-102', ref: 'ORD-1026', type: 'Money In', entity: 'Walk-in Customer', amount: 450.00, date: '2023-10-25', method: 'Cash', status: 'Completed' },
];

export const mockExpenses = [
  { id: 'EXP-501', category: 'Rent', description: 'Monthly Office Rent', amount: 2000.00, date: '2023-10-01', status: 'Paid' },
  { id: 'EXP-502', category: 'Utilities', description: 'Electricity Bill', amount: 350.00, date: '2023-10-15', status: 'Paid' },
  { id: 'EXP-503', category: 'Marketing', description: 'Google Ads', amount: 500.00, date: '2023-10-20', status: 'Pending' },
];

export const mockEmployees = [
  { id: 'EMP-01', name: 'Sarah Connor', role: 'Owner', email: 'sarah@example.com', joined: '2022-01-15', status: 'Active' },
  { id: 'EMP-02', name: 'John Smith', role: 'Manager', email: 'john@example.com', joined: '2023-03-01', status: 'Active' },
  { id: 'EMP-03', name: 'Mike Ross', role: 'Sales Staff', email: 'mike@example.com', joined: '2023-06-10', status: 'Active' },
];

export const mockInventoryMovements = [
  { id: 'MOV-001', product: 'USB-C Hub', type: 'Sale', qty: -5, prevStock: 5, newStock: 0, reason: 'Order ORD-1024', user: 'John Smith', date: '2023-10-24 14:35' },
  { id: 'MOV-002', product: 'Wireless Mouse', type: 'Purchase', qty: 100, prevStock: 45, newStock: 145, reason: 'PO-2021 Received', user: 'Mike Ross', date: '2023-10-23 09:10' },
  { id: 'MOV-003', product: 'Mechanical Keyboard', type: 'Adjustment', qty: -2, prevStock: 14, newStock: 12, reason: 'Damaged in transit', user: 'Sarah Connor', date: '2023-10-22 11:20' },
];

export const mockNotifications = [
  { id: 1, category: 'Inventory', title: 'Low Stock Alert', message: 'Mechanical Keyboard is below minimum stock level.', time: '10 mins ago', read: false, severity: 'warning' },
  { id: 2, category: 'Payments', title: 'Payment Overdue', message: 'Invoice for Tech Corp is 5 days overdue.', time: '2 hours ago', read: false, severity: 'danger' },
  { id: 3, category: 'Purchases', title: 'Delivery Expected', message: 'PO-2023 from Global Electronics is arriving tomorrow.', time: '1 day ago', read: true, severity: 'info' },
  { id: 4, category: 'System', title: 'System Update', message: 'Maintenance scheduled for tonight at 2 AM.', time: '2 days ago', read: true, severity: 'info' },
];

export const mockAuditLogs = [
  { id: 1, user: 'John Smith', action: 'Created Order', entity: 'ORD-1027', module: 'Sales', timestamp: '2023-10-25 10:45 AM' },
  { id: 2, user: 'Sarah Connor', action: 'Updated Stock', entity: 'Mechanical Keyboard', module: 'Inventory', timestamp: '2023-10-24 02:15 PM' },
  { id: 3, user: 'Mike Ross', action: 'Added Supplier', entity: 'Tech Components Ltd', module: 'Purchases', timestamp: '2023-10-23 09:30 AM' },
  { id: 4, user: 'John Smith', action: 'Recorded Payment', entity: 'PAY-100', module: 'Finance', timestamp: '2023-10-22 11:20 AM' },
];

export const mockDocuments = [
  { id: 1, name: 'Invoice_TechCorp_Oct.pdf', category: 'Invoices', size: '2.4 MB', date: '2023-10-25', type: 'pdf' },
  { id: 2, name: 'Receipt_OfficeRent.jpg', category: 'Receipts', size: '850 KB', date: '2023-10-01', type: 'image' },
  { id: 3, name: 'Supplier_Agreement_GE.docx', category: 'Supplier Documents', size: '1.2 MB', date: '2023-09-15', type: 'doc' },
  { id: 4, name: 'Q3_Financial_Report.xlsx', category: 'Business Documents', size: '3.1 MB', date: '2023-10-05', type: 'sheet' },
];
