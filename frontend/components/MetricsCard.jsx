'use client';

export default function MetricsCard({ metrics }) {
  if (!metrics) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Metrics</h2>
        <p className="text-gray-500">No metrics available</p>
      </div>
    );
  }

  const metricCards = [
    {
      label: 'Optimized Cost',
      value: `₹${metrics.total_cost_optimized.toLocaleString()}`,
      icon: '💰',
      color: 'bg-blue-50 text-blue-700',
      borderColor: 'border-blue-200',
    },
    {
      label: 'Baseline Cost',
      value: `₹${metrics.total_cost_baseline.toLocaleString()}`,
      icon: '📊',
      color: 'bg-gray-50 text-gray-700',
      borderColor: 'border-gray-200',
    },
    {
      label: 'Cost Savings',
      value: `₹${metrics.savings_absolute.toLocaleString()}`,
      subvalue: `${metrics.savings_percentage.toFixed(1)}% saved`,
      icon: '✅',
      color: 'bg-green-50 text-green-700',
      borderColor: 'border-green-200',
      highlight: true,
    },
    {
      label: 'Total Distance',
      value: `${metrics.total_distance_km.toFixed(1)} km`,
      icon: '🚗',
      color: 'bg-purple-50 text-purple-700',
      borderColor: 'border-purple-200',
    },
    {
      label: 'Total Travel Time',
      value: `${Math.round(metrics.total_travel_time_min)} min`,
      subvalue: `${(metrics.total_travel_time_min / 60).toFixed(1)} hours`,
      icon: '⏱️',
      color: 'bg-orange-50 text-orange-700',
      borderColor: 'border-orange-200',
    },
    {
      label: 'Vehicles Used',
      value: `${metrics.num_vehicles_used}`,
      subvalue: `${metrics.num_employees} employees`,
      icon: '🚐',
      color: 'bg-cyan-50 text-cyan-700',
      borderColor: 'border-cyan-200',
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow-md p-6">
      <h2 className="text-xl font-bold text-gray-800 mb-6">Optimization Metrics</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {metricCards.map((card, idx) => (
          <div
            key={idx}
            className={`border-2 ${card.borderColor} ${card.color} rounded-lg p-4 ${
              card.highlight ? 'ring-2 ring-green-400 ring-offset-2' : ''
            }`}
          >
            <div className="flex items-start justify-between mb-2">
              <p className="text-sm font-medium opacity-80">{card.label}</p>
              <span className="text-2xl">{card.icon}</span>
            </div>
            <p className="text-2xl font-bold mb-1">{card.value}</p>
            {card.subvalue && (
              <p className="text-xs opacity-70">{card.subvalue}</p>
            )}
          </div>
        ))}
      </div>

      {/* Savings Summary */}
      {metrics.savings_percentage > 0 && (
        <div className="mt-6 p-4 bg-gradient-to-r from-green-50 to-blue-50 rounded-lg border border-green-200">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm font-medium text-gray-700">Total Savings</p>
              <p className="text-3xl font-bold text-green-600">
                ₹{metrics.savings_absolute.toLocaleString()}
              </p>
            </div>
            <div className="text-right">
              <p className="text-sm font-medium text-gray-700">Efficiency Gain</p>
              <p className="text-3xl font-bold text-blue-600">
                {metrics.savings_percentage.toFixed(1)}%
              </p>
            </div>
          </div>
          <p className="mt-3 text-sm text-gray-600">
            By optimizing routes and sharing vehicles, you save{' '}
            <span className="font-semibold">
              ₹{metrics.savings_absolute.toLocaleString()}
            </span>{' '}
            compared to individual cab rides for all employees.
          </p>
        </div>
      )}

      {/* Additional Stats */}
      <div className="mt-6 grid grid-cols-2 gap-4 pt-4 border-t border-gray-200">
        <div>
          <p className="text-sm text-gray-600">Average per employee</p>
          <p className="text-lg font-semibold text-gray-800">
            ₹{(metrics.total_cost_optimized / metrics.num_employees).toFixed(2)}
          </p>
        </div>
        <div>
          <p className="text-sm text-gray-600">Average per vehicle</p>
          <p className="text-lg font-semibold text-gray-800">
            {(metrics.num_employees / metrics.num_vehicles_used).toFixed(1)} employees
          </p>
        </div>
      </div>
    </div>
  );
}
