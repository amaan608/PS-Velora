'use client';

import { useEffect, useState } from 'react';
import { MapContainer, TileLayer, Marker, Popup, Polyline, useMap } from 'react-leaflet';
import L from 'leaflet';

// Fix for default marker icons in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon-2x.png',
  iconUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-icon.png',
  shadowUrl: 'https://unpkg.com/leaflet@1.9.4/dist/images/marker-shadow.png',
});

// Custom marker icons
const createIcon = (color) => {
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 2px solid white; box-shadow: 0 2px 4px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const pickupIcon = createIcon('#3b82f6'); // Blue
const dropoffIcon = createIcon('#ef4444'); // Red

// Vehicle route colors
const vehicleColors = [
  '#8b5cf6', // Purple
  '#ec4899', // Pink
  '#f59e0b', // Amber
  '#10b981', // Green
  '#06b6d4', // Cyan
  '#6366f1', // Indigo
  '#f97316', // Orange
  '#14b8a6', // Teal
];

function MapBounds({ routes }) {
  const map = useMap();
  
  useEffect(() => {
    if (routes && routes.length > 0) {
      const allPoints = [];
      
      routes.forEach(vehicle => {
        vehicle.route.forEach(point => {
          allPoints.push([point.lat, point.lng]);
        });
      });
      
      if (allPoints.length > 0) {
        const bounds = L.latLngBounds(allPoints);
        map.fitBounds(bounds, { padding: [50, 50] });
      }
    }
  }, [routes, map]);
  
  return null;
}

export default function MapView({ routes }) {
  const [mounted, setMounted] = useState(false);
  const [showPickups, setShowPickups] = useState(true);
  const [showDropoffs, setShowDropoffs] = useState(true);

  useEffect(() => {
    setMounted(true);
  }, []);

  if (!mounted) {
    return (
      <div className="w-full h-full bg-gray-200 rounded-lg flex items-center justify-center">
        <p className="text-gray-600">Loading map...</p>
      </div>
    );
  }

  if (!routes || routes.length === 0) {
    return (
      <div className="w-full h-full bg-gray-200 rounded-lg flex items-center justify-center">
        <p className="text-gray-600">No routes to display. Run optimization first.</p>
      </div>
    );
  }

  // Default center (Bangalore)
  const center = [12.9716, 77.5946];

  return (
    <div className="relative w-full h-full">
      {/* Controls */}
      <div className="absolute top-4 right-4 z-[1000] bg-white rounded-lg shadow-md p-3 space-y-2">
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showPickups}
            onChange={(e) => setShowPickups(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Pickups</span>
          <div className="w-3 h-3 rounded-full bg-blue-500"></div>
        </label>
        <label className="flex items-center space-x-2 cursor-pointer">
          <input
            type="checkbox"
            checked={showDropoffs}
            onChange={(e) => setShowDropoffs(e.target.checked)}
            className="rounded"
          />
          <span className="text-sm">Dropoffs</span>
          <div className="w-3 h-3 rounded-full bg-red-500"></div>
        </label>
      </div>

      {/* Map */}
      <MapContainer
        center={center}
        zoom={12}
        className="w-full h-full rounded-lg"
        scrollWheelZoom={true}
      >
        <TileLayer
          attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        
        <MapBounds routes={routes} />

        {/* Render routes for each vehicle */}
        {routes.map((vehicle, vehicleIdx) => {
          const color = vehicleColors[vehicleIdx % vehicleColors.length];
          
          // Extract route coordinates
          const routeCoords = vehicle.route.map(point => [point.lat, point.lng]);
          
          return (
            <div key={vehicle.vehicle_id}>
              {/* Route polyline */}
              <Polyline
                positions={routeCoords}
                color={color}
                weight={3}
                opacity={0.7}
              />
              
              {/* Markers */}
              {vehicle.route.map((point, pointIdx) => {
                const isPickup = point.type === 'pickup';
                
                // Filter based on toggle
                if (isPickup && !showPickups) return null;
                if (!isPickup && !showDropoffs) return null;
                
                return (
                  <Marker
                    key={`${vehicle.vehicle_id}-${pointIdx}`}
                    position={[point.lat, point.lng]}
                    icon={isPickup ? pickupIcon : dropoffIcon}
                  >
                    <Popup>
                      <div className="text-sm">
                        <p className="font-semibold">{isPickup ? 'Pickup' : 'Dropoff'}</p>
                        <p>Employee: {point.emp_id}</p>
                        <p>Vehicle: {vehicle.vehicle_id}</p>
                        <p>ETA: {point.eta}</p>
                      </div>
                    </Popup>
                  </Marker>
                );
              })}
            </div>
          );
        })}
      </MapContainer>

      {/* Legend */}
      <div className="absolute bottom-4 left-4 z-[1000] bg-white rounded-lg shadow-md p-3">
        <h4 className="text-sm font-semibold mb-2">Vehicles</h4>
        <div className="space-y-1">
          {routes.slice(0, 5).map((vehicle, idx) => (
            <div key={vehicle.vehicle_id} className="flex items-center space-x-2 text-xs">
              <div
                className="w-4 h-1 rounded"
                style={{ backgroundColor: vehicleColors[idx % vehicleColors.length] }}
              ></div>
              <span>{vehicle.vehicle_id}</span>
            </div>
          ))}
          {routes.length > 5 && (
            <p className="text-xs text-gray-500">+{routes.length - 5} more</p>
          )}
        </div>
      </div>
    </div>
  );
}
