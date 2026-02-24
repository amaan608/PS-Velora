"""
Route generation using Nearest Neighbor Heuristic.
Generates optimal pickup and dropoff sequences for each vehicle.
"""

from optimizer.utils import haversine, calculate_travel_time, format_time


def create_route_point(point_type, employee, lat, lng):
    """
    Create a route point dictionary.
    
    Args:
        point_type: 'pickup' or 'dropoff'
        employee: Employee dictionary
        lat: Latitude
        lng: Longitude
    
    Returns:
        Route point dictionary
    """
    return {
        'type': point_type,
        'emp_id': employee['id'],
        'lat': lat,
        'lng': lng,
        'eta': None,  # To be calculated
        'employee': employee  # Keep reference for routing
    }


def nearest_neighbor_route(vehicle, employees):
    """
    Generate route using Nearest Neighbor Heuristic.
    
    Strategy:
    1. Start from vehicle's current location
    2. Pick up all employees in nearest-first order
    3. Drop off all employees in nearest-first order from last pickup
    
    Args:
        vehicle: Vehicle dictionary with current location
        employees: List of employee dictionaries assigned to this vehicle
    
    Returns:
        List of route points in order
    """
    if not employees:
        return []
    
    route = []
    current_lat = vehicle['current_lat']
    current_lng = vehicle['current_lng']
    current_time = vehicle['available_from_min']
    
    # Create pickup points for all employees
    pickup_points = [
        create_route_point('pickup', emp, emp['pickup_lat'], emp['pickup_lng'])
        for emp in employees
    ]
    
    # Phase 1: Pick up all employees using nearest neighbor
    remaining_pickups = pickup_points.copy()
    
    while remaining_pickups:
        # Find nearest pickup point
        nearest_point = None
        nearest_distance = float('inf')
        
        for point in remaining_pickups:
            distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point
        
        # Travel to pickup point
        travel_time = calculate_travel_time(nearest_distance, vehicle['avg_speed'])
        current_time += travel_time
        
        # Update ETA for this pickup
        nearest_point['eta'] = format_time(current_time)
        nearest_point['eta_min'] = current_time
        
        # Add to route
        route.append(nearest_point)
        
        # Update current position
        current_lat = nearest_point['lat']
        current_lng = nearest_point['lng']
        
        # Remove from remaining
        remaining_pickups.remove(nearest_point)
    
    # Phase 2: Drop off all employees using nearest neighbor
    dropoff_points = [
        create_route_point('dropoff', emp, emp['dest_lat'], emp['dest_lng'])
        for emp in employees
    ]
    
    remaining_dropoffs = dropoff_points.copy()
    
    while remaining_dropoffs:
        # Find nearest dropoff point
        nearest_point = None
        nearest_distance = float('inf')
        
        for point in remaining_dropoffs:
            distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
            if distance < nearest_distance:
                nearest_distance = distance
                nearest_point = point
        
        # Travel to dropoff point
        travel_time = calculate_travel_time(nearest_distance, vehicle['avg_speed'])
        current_time += travel_time
        
        # Update ETA for this dropoff
        nearest_point['eta'] = format_time(current_time)
        nearest_point['eta_min'] = current_time
        
        # Add to route
        route.append(nearest_point)
        
        # Update current position
        current_lat = nearest_point['lat']
        current_lng = nearest_point['lng']
        
        # Remove from remaining
        remaining_dropoffs.remove(nearest_point)
    
    return route


def calculate_route_distance(route, vehicle_start_lat, vehicle_start_lng):
    """
    Calculate total distance for a route.
    
    Args:
        route: List of route points
        vehicle_start_lat: Vehicle starting latitude
        vehicle_start_lng: Vehicle starting longitude
    
    Returns:
        Total distance in kilometers
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
    
    Args:
        route: List of route points with eta_min
        vehicle: Vehicle dictionary
    
    Returns:
        Total time in minutes
    """
    if not route:
        return 0
    
    start_time = vehicle['available_from_min']
    end_time = route[-1]['eta_min']
    
    return end_time - start_time


def generate_routes_for_all_vehicles(assignments, vehicles):
    """
    Generate routes for all vehicles with assignments.
    
    Args:
        assignments: Dict mapping vehicle_id to list of employees
        vehicles: List of vehicle dictionaries
    
    Returns:
        Dict mapping vehicle_id to route information
    """
    vehicle_map = {v['id']: v for v in vehicles}
    routes = {}
    
    for vehicle_id, employees in assignments.items():
        vehicle = vehicle_map[vehicle_id]
        
        # Generate route using nearest neighbor
        route = nearest_neighbor_route(vehicle, employees)
        
        # Calculate metrics
        total_distance = calculate_route_distance(
            route,
            vehicle['current_lat'],
            vehicle['current_lng']
        )
        total_time = calculate_route_time(route, vehicle)
        
        # Clean up route points (remove employee reference)
        clean_route = []
        for point in route:
            clean_route.append({
                'type': point['type'],
                'emp_id': point['emp_id'],
                'lat': point['lat'],
                'lng': point['lng'],
                'eta': point['eta']
            })
        
        routes[vehicle_id] = {
            'vehicle_id': vehicle_id,
            'assigned_employees': [emp['id'] for emp in employees],
            'route': clean_route,
            'total_distance_km': round(total_distance, 2),
            'total_time_min': round(total_time, 2)
        }
    
    return routes
