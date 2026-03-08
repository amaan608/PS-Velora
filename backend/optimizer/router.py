"""
Route generation.
Generates optimal pickup and dropoff sequences for each vehicle.
"""

from optimizer.utils import haversine, calculate_travel_time, format_time


def create_route_point(point_type, employee, lat, lng):
    """
    Create a route point dictionary.
    """
    return {
        'type': point_type,
        'emp_id': employee['id'],
        'lat': lat,
        'lng': lng,
        'eta': None,
        'eta_min': None,
        'employee': employee
    }


def nearest_neighbor_route(vehicle, employees):
    """
    Generate route using Nearest Neighbor Heuristic.
    
    Strategy:
    1. Start from vehicle's current location
    2. Interleave pickups and dropoffs dynamically based on nearest valid point
    """
    if not employees:
        return []
    
    route = []
    current_lat = vehicle['current_lat']
    current_lng = vehicle['current_lng']
    current_time = vehicle['available_from_min']
    
    unpicked_employees = employees.copy()
    in_vehicle = []
    
    capacity = vehicle['capacity']
    
    while unpicked_employees or in_vehicle:
        valid_next_points = []
        
        # We can pick up if we have capacity
        if len(in_vehicle) < capacity:
            for emp in unpicked_employees:
                valid_next_points.append(
                    create_route_point('pickup', emp, emp['pickup_lat'], emp['pickup_lng'])
                )
                
        # We can drop off anyone currently in the vehicle
        for emp in in_vehicle:
            valid_next_points.append(
                create_route_point('dropoff', emp, emp['dest_lat'], emp['dest_lng'])
            )
            
        if not valid_next_points:
            break
            
        nearest_point = None
        nearest_distance = float('inf')
        
        for point in valid_next_points:
            distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point
        
        travel_time = calculate_travel_time(nearest_distance, vehicle['avg_speed'])
        current_time += travel_time
        
        nearest_point['eta'] = format_time(current_time)
        nearest_point['eta_min'] = current_time
        
        route.append(nearest_point)
        
        current_lat = nearest_point['lat']
        current_lng = nearest_point['lng']
        
        if nearest_point['type'] == 'pickup':
            emp = nearest_point['employee']
            unpicked_employees = [e for e in unpicked_employees if e['id'] != emp['id']]
            in_vehicle.append(emp)
        elif nearest_point['type'] == 'dropoff':
            emp = nearest_point['employee']
            in_vehicle = [e for e in in_vehicle if e['id'] != emp['id']]
            
    return route


def calculate_route_distance(route, vehicle_start_lat, vehicle_start_lng):
    """
    Calculate total distance for a route.
    """
    if not route:
        return 0.0
    
    total_distance = 0.0
    current_lat = vehicle_start_lat
    current_lng = vehicle_start_lng
    
    for point in route:
        distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
        total_distance += distance
        current_lat = point['lat']
        current_lng = point['lng']
    
    return total_distance


def calculate_route_time(route, vehicle):
    """
    Calculate total time for a route from vehicle availability to last dropoff.
    """
    if not route:
        return 0
    
    start_time = vehicle['available_from_min']
    end_time = route[-1].get('eta_min', start_time)
    
    return end_time - start_time


def generate_routes_for_all_vehicles(assignments, vehicles):
    """
    Generate routes for all vehicles with assignments.
    Uses pre-computed route if available from assignment heuristic, 
    otherwise falls back to nearest neighbor interleaving.
    """
    vehicle_map = {v['id']: v for v in vehicles}
    routes = {}
    
    for vehicle_id, employees in assignments.items():
        vehicle = vehicle_map[vehicle_id]
        
        if 'route' in vehicle and vehicle['route']:
            route = vehicle['route']
        else:
            route = nearest_neighbor_route(vehicle, employees)
        
        total_distance = calculate_route_distance(
            route,
            vehicle['current_lat'],
            vehicle['current_lng']
        )
        total_time = calculate_route_time(route, vehicle)
        
        routes[vehicle_id] = {
            'vehicle_id': vehicle_id,
            'assigned_employees': [emp['id'] for emp in employees],
            'route': route,
            'total_distance_km': round(total_distance, 2),
            'total_time_min': round(total_time, 2)
        }
    
    return routes
