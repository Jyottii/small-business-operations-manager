import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { ArrowUpRight, ArrowDownRight, DollarSign } from 'lucide-react';
import { DataTable } from '../../components/ui/DataTable';

const cashFlowTransactions = [
  { id: 'TRX-001', date: '2023-10-25', description: 'Customer Payment (ORD-1024)', category: 'Sales', type: 'in', amount: 145.50 },
  { id: 'TRX-002', date: '2023-10-25', description: 'Supplier Payment (PO-2022)', category: 'Inventory', type: 'out', amount: 2500.00 },
  { id: 'TRX-003', date: '2023-10-24', description: 'Electricity Bill', category: 'Utilities', type: 'out', amount: 350.00 },
  { id: 'TRX-004', date: '2023-10-23', description: 'Customer Payment (ORD-1021)', category: 'Sales', type: 'in', amount: 890.00 },
  { id: 'TRX-005', date: '2023-10-22', description: 'Office Rent', category: 'Rent', type: 'out', amount: 2000.00 },
];

export default function CashFlow() {
  const summary = {
    openingBalance: 12500.00,
    cashIn: 15450.00,
    cashOut: 9800.00,
    netCashFlow: 5650.00,
    closingBalance: 18150.00
  };

  const columns = [
    { header: 'Date', accessorKey: 'date' },
    { header: 'Description', accessorKey: 'description' },
    { header: 'Category', accessorKey: 'category' },
    { header: 'Type', cell: (row) => (
      row.type === 'in' 
        ? <span className="inline-flex items-center text-green-600"><ArrowUpRight size={16} className="mr-1"/> Money In</span>
        : <span className="inline-flex items-center text-red-600"><ArrowDownRight size={16} className="mr-1"/> Money Out</span>
    )},
    { header: 'Amount', cell: (row) => (
      <span className={row.type === 'in' ? 'text-green-600 font-medium' : 'text-red-600 font-medium'}>
        {row.type === 'in' ? '+' : '-'}${row.amount.toFixed(2)}
      </span>
    )}
  ];

  return (
    <div className="space-y-6 max-w-7xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Cash Flow Statement</h1>
          <p className="text-sm text-gray-500">Track money moving in and out of your business.</p>
        </div>
        <select className="border border-gray-300 rounded-md shadow-sm py-2 px-3 focus:outline-none focus:ring-blue-500 focus:border-blue-500 sm:text-sm">
          <option>This Month (Oct 2023)</option>
          <option>Last Month</option>
          <option>Year to Date</option>
        </select>
      </div>

      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-5 gap-4">
        <Card>
          <CardBody className="p-4">
            <p className="text-sm font-medium text-gray-500 mb-1">Opening Balance</p>
            <h3 className="text-xl font-bold text-gray-900">${summary.openingBalance.toLocaleString()}</h3>
          </CardBody>
        </Card>
        <Card className="bg-green-50 border-green-100">
          <CardBody className="p-4">
            <p className="text-sm font-medium text-green-800 mb-1">Total Cash In</p>
            <h3 className="text-xl font-bold text-green-900">+${summary.cashIn.toLocaleString()}</h3>
          </CardBody>
        </Card>
        <Card className="bg-red-50 border-red-100">
          <CardBody className="p-4">
            <p className="text-sm font-medium text-red-800 mb-1">Total Cash Out</p>
            <h3 className="text-xl font-bold text-red-900">-${summary.cashOut.toLocaleString()}</h3>
          </CardBody>
        </Card>
        <Card className="bg-blue-50 border-blue-100">
          <CardBody className="p-4">
            <p className="text-sm font-medium text-blue-800 mb-1">Net Cash Flow</p>
            <h3 className="text-xl font-bold text-blue-900">${summary.netCashFlow.toLocaleString()}</h3>
          </CardBody>
        </Card>
        <Card className="bg-gray-900 text-white border-gray-800">
          <CardBody className="p-4">
            <p className="text-sm font-medium text-gray-400 mb-1">Closing Balance</p>
            <h3 className="text-xl font-bold text-white">${summary.closingBalance.toLocaleString()}</h3>
          </CardBody>
        </Card>
      </div>

      <Card>
        <CardHeader title="Recent Transactions" />
        <CardBody className="p-0">
          <DataTable columns={columns} data={cashFlowTransactions} searchPlaceholder="Search transactions..." />
        </CardBody>
      </Card>
    </div>
  );
}
