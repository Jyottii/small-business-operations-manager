import { Tabs } from '../../components/ui/TabsAndBadges';
import { Card, CardBody, CardHeader } from '../../components/ui/Card';
import { Save } from 'lucide-react';

export default function Settings() {
  
  const BusinessTab = () => (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader title="Business Information" />
        <CardBody className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Business Name</label>
            <input type="text" defaultValue="TechHaven Electronics" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
          </div>
          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Owner Name</label>
              <input type="text" defaultValue="Sarah Connor" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
            </div>
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">Tax ID / GST</label>
              <input type="text" defaultValue="TX-1928374" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
            </div>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Address</label>
            <textarea rows="3" defaultValue="123 Commerce St, Tech District" className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2"></textarea>
          </div>
        </CardBody>
      </Card>
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md flex items-center font-medium hover:bg-blue-700"><Save size={16} className="mr-2"/> Save Changes</button>
      </div>
    </div>
  );

  const OperationsTab = () => (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader title="Inventory Preferences" />
        <CardBody className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Low Stock Threshold</label>
            <input type="number" defaultValue="20" className="w-32 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
            <p className="text-xs text-gray-500 mt-1">Alert when product stock falls below this number (if not set individually).</p>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Warehouse</label>
            <select className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2">
              <option>Main Warehouse</option>
              <option>Retail Store Front</option>
            </select>
          </div>
        </CardBody>
      </Card>
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md flex items-center font-medium hover:bg-blue-700"><Save size={16} className="mr-2"/> Save Changes</button>
      </div>
    </div>
  );

  const FinanceTab = () => (
    <div className="space-y-6 max-w-2xl">
      <Card>
        <CardHeader title="Finance & Currency" />
        <CardBody className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Currency</label>
            <select className="w-full border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2">
              <option>USD ($)</option>
              <option>EUR (€)</option>
              <option>GBP (£)</option>
            </select>
          </div>
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">Default Tax Rate (%)</label>
            <input type="number" defaultValue="8" className="w-32 border-gray-300 rounded-md shadow-sm focus:ring-blue-500 focus:border-blue-500 border p-2" />
          </div>
        </CardBody>
      </Card>
      <div className="flex justify-end">
        <button className="px-4 py-2 bg-blue-600 text-white rounded-md flex items-center font-medium hover:bg-blue-700"><Save size={16} className="mr-2"/> Save Changes</button>
      </div>
    </div>
  );

  return (
    <div className="space-y-6 max-w-5xl mx-auto">
      <div>
        <h1 className="text-2xl font-bold text-gray-900">System Settings</h1>
        <p className="text-sm text-gray-500">Manage your business preferences and system configurations.</p>
      </div>

      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-2">
        <Tabs 
          tabs={[
            { id: 'business', label: 'Business Profile', content: <BusinessTab /> },
            { id: 'operations', label: 'Operations & Inventory', content: <OperationsTab /> },
            { id: 'finance', label: 'Finance & Tax', content: <FinanceTab /> },
            { id: 'users', label: 'Users & Permissions', content: <div className="text-gray-500 p-4">User role management interface...</div> },
            { id: 'notifications', label: 'Notifications', content: <div className="text-gray-500 p-4">Notification preferences interface...</div> },
          ]}
        />
      </div>
    </div>
  );
}
