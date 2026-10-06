import { useState } from 'react';
import { useApi } from '../../api/hooks';
import { apiClient } from '../../api/client';
import { Card, CardBody } from '../../components/ui/Card';
import { Bell, Package, CreditCard, ShoppingCart, Info, AlertTriangle, CheckCircle2, Loader2 } from 'lucide-react';

export default function Notifications() {
  const { data: notificationsData, loading, error, refetch } = useApi('/notifications?page_size=50');
  const notifications = notificationsData || [];

  const getIcon = (type) => {
    switch(type) {
      case 'WARNING': return <AlertTriangle size={20} className="text-yellow-600" />;
      case 'SUCCESS': return <CheckCircle2 size={20} className="text-green-600" />;
      case 'ERROR': return <AlertTriangle size={20} className="text-red-600" />;
      default: return <Info size={20} className="text-blue-600" />;
    }
  };

  const markRead = async (id) => {
    try {
      await apiClient(`/notifications/${id}/read`, { method: 'POST' });
      refetch();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="space-y-6 max-w-4xl mx-auto">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-gray-900">Notifications</h1>
          <p className="text-sm text-gray-500">Live operational events, low-stock warnings, and transaction receipts.</p>
        </div>
      </div>

      <Card>
        <CardBody className="p-0">
          {loading ? (
            <div className="p-12 text-center text-gray-500 flex justify-center items-center">
              <Loader2 className="animate-spin text-gray-400 mr-2" size={24} />
              Loading notifications...
            </div>
          ) : notifications.length === 0 ? (
            <div className="p-8 text-center text-gray-500">No notifications found.</div>
          ) : (
            <ul className="divide-y divide-gray-100">
              {notifications.map(notif => (
                <li key={notif.id} className={`p-4 hover:bg-gray-50 flex items-start space-x-4 ${!notif.is_read ? 'bg-blue-50/30' : ''}`}>
                  <div className={`p-2 rounded-full flex-shrink-0 ${!notif.is_read ? 'bg-white shadow-sm' : 'bg-gray-100'}`}>
                    {getIcon(notif.notification_type)}
                  </div>
                  <div className="flex-1">
                    <div className="flex justify-between items-start">
                      <h4 className={`text-sm font-semibold ${!notif.is_read ? 'text-gray-900' : 'text-gray-700'}`}>{notif.title}</h4>
                      <span className="text-xs text-gray-500 whitespace-nowrap ml-4">
                        {notif.created_at ? new Date(notif.created_at).toLocaleString() : ''}
                      </span>
                    </div>
                    <p className={`text-sm mt-1 ${!notif.is_read ? 'text-gray-700' : 'text-gray-500'}`}>{notif.message}</p>
                    <div className="flex items-center space-x-3 mt-2">
                      <span className="text-xs font-mono font-medium text-gray-500 px-2 py-0.5 bg-gray-100 rounded">
                        {notif.related_entity_type || 'System'}
                      </span>
                      {!notif.is_read && (
                        <button onClick={() => markRead(notif.id)} className="text-xs font-medium text-blue-600 hover:text-blue-800">
                          Mark as read
                        </button>
                      )}
                    </div>
                  </div>
                  {!notif.is_read && <div className="w-2 h-2 bg-blue-600 rounded-full flex-shrink-0 mt-2"></div>}
                </li>
              ))}
            </ul>
          )}
        </CardBody>
      </Card>
    </div>
  );
}
