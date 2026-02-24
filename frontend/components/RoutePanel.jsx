'use client';

import { useState } from 'react';

export default function RoutePanel({ routes }) {
  const [selectedVehicle, setSelectedVehicle] = useState(null);

  if (!routes || routes.length === 0) {
    return (
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-xl font-bold text-gray-800 mb-4">Routes</h2>
        <p className="text-gray-500">No routes available</p>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 h-full overflow-auto">
      <h2 className="text-xl font-bold text-gray-800 mb-4">Vehicle Routes</h2>
      
      <div className="space-y-3">
        {routes.map((vehicle, idx) => {
          const isExpanded = selectedVehicle === vehicle.vehicle_id;
          
          return (
            <div
              key={vehicle.vehicle_id}
              className="border border-gray-200 rounded-lg overflow-hidden"
            >
              {/* Vehicle Header */}
              <button
                onClick={() => setSelectedVehicle(isExpanded ? null : vehicle.vehicle_id)}
                className="w-full px-4 py-3 bg-gray-50 hover:bg-gray-100 transition-colors flex items-center justify-between"
              >
                <div className="flex items-center space-x-3">
                  <div className="w-3 h-3 rounded-full bg-primary-500"></div>
                  <div className="text-left">
                    <h3 className="font-semibold text-gray-800">{vehicle.vehicle_id}</h3>
                    <p className="text-sm text-gray-600">
                      {vehicle.assigned_employees.length} employee{vehicle.assigned_employees.length !== 1 ? 's' : ''} • {vehicle.total_distance_km} km • {Math.round(vehicle.total_time_min)} min
                    </p>
                  </div>
                </div>
                <svg
                  className={`w-5 h-5 text-gray-500 transition-transform ${isExpanded ? 'rotate-180' : ''}`}
                  fill="none"
                  stroke="currentColor"
                  viewBox="0 0 24 24"
                >
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                </svg>
              </button>

              {/* Vehicle Details */}
              {isExpanded && (
                <div className="px-4 py-3 space-y-3">
                  {/* Employee List */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Assigned Employees</h4>
                    <div className="flex flex-wrap gap-2">
                      {vehicle.assigned_employees.map(empId => (
                        <span
                          key={empId}
                          className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full"
                        >
                          {empId}
                        </span>
                      ))}
                    </div>
                  </div>

                  {/* Route Timeline */}
                  <div>
                    <h4 className="text-sm font-semibold text-gray-700 mb-2">Route Timeline</h4>
                    <div className="space-y-2">
                      {vehicle.route.map((point, pointIdx) => (
                        <div
                          key={pointIdx}
                          className="flex items-start space-x-3"
                        >
                          {/* Timeline dot */}
                          <div className="flex flex-col items-center">
                            <div
                              className={`w-3 h-3 rounded-full ${
                                point.type === 'pickup' ? 'bg-blue-500' : 'bg-red-500'
                              }`}
                            ></div>
                            {pointIdx < vehicle.route.length - 1 && (
                              <div className="w-0.5 h-8 bg-gray-300"></div>
                            )}
                          </div>

                          {/* Point info */}
                          <div className="flex-1 pb-4">
                            <div className="flex items-center justify-between">
                              <div>
                                <span className={`text-xs font-semibold ${
                                  point.type === 'pickup' ? 'text-blue-700' : 'text-red-700'
                                }`}>
                                  {point.type === 'pickup' ? 'PICKUP' : 'DROPOFF'}
                                </span>
                                <p className="text-sm font-medium text-gray-800">
                                  {point.emp_id}
                                </p>
                                <p className="text-xs text-gray-500">
                                  {point.lat.toFixed(4)}, {point.lng.toFixed(4)}
                                </p>
                              </div>
                              <div className="text-right">
                                <p className="text-sm font-semibold text-gray-800">{point.eta}</p>
                              </div>
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Stats */}
                  <div className="pt-2 border-t border-gray-200">
                    <div className="grid grid-cols-2 gap-3 text-sm">
                      <div>
                        <p className="text-gray-600">Total Distance</p>
                        <p className="font-semibold text-gray-800">{vehicle.total_distance_km} km</p>
                      </div>
                      <div>
                        <p className="text-gray-600">Total Time</p>
                        <p className="font-semibold text-gray-800">{Math.round(vehicle.total_time_min)} min</p>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          );
        })}
      </div>
    </div>
  );
}
