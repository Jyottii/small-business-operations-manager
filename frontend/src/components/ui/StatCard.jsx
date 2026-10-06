import { Card, CardBody } from './Card';

export function StatCard({ title, value, icon: Icon, trend, trendValue, color = 'blue' }) {
  const colorMap = {
    blue: 'bg-blue-100 text-blue-600',
    green: 'bg-green-100 text-green-600',
    red: 'bg-red-100 text-red-600',
    yellow: 'bg-yellow-100 text-yellow-600',
    purple: 'bg-purple-100 text-purple-600',
  };

  const trendColor = trend === 'up' ? 'text-green-600' : trend === 'down' ? 'text-red-600' : 'text-gray-500';

  return (
    <Card>
      <CardBody className="p-5 flex items-start justify-between">
        <div>
          <p className="text-sm font-medium text-gray-500 mb-1">{title}</p>
          <h4 className="text-2xl font-bold text-gray-900">{value}</h4>
          {trendValue && (
            <p className={`text-xs mt-2 font-medium ${trendColor}`}>
              {trend === 'up' ? '↑ ' : trend === 'down' ? '↓ ' : ''}
              {trendValue}
            </p>
          )}
        </div>
        <div className={`p-3 rounded-lg ${colorMap[color]}`}>
          <Icon size={24} />
        </div>
      </CardBody>
    </Card>
  );
}
