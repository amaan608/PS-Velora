"""
Route improvement using 2-opt algorithm.
Optimizes route sequences to reduce total distance.
"""

from optimizer.utils import haversine, calculate_travel_time, format_time


def two_opt_swap(route, i, j):
    """
    Perform 2-opt swap: reverse the order of route points between indices i and j.
    
    Args:
        route: List of route points
        i: Start index
        j: End index
    
    Returns:
        New route with swapped segment
    """
    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
    return new_route


def calculate_segment_distance(route, vehicle_start_lat, vehicle_start_lng):
    """
    Calculate total distance for a route segment.
    
    Args:
        route: List of route points
        vehicle_start_lat: Starting latitude
        vehicle_start_lng: Starting longitude
    
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


def is_valid_swap(route, i, j):
    """
    Check if a 2-opt swap maintains pickup-before-dropoff constraint.
    
    For each employee, their pickup must come before their dropoff.
    
    Args:
        route: List of route points
        i: Start index of swap
        j: End index of swap
    
    Returns:
        True if swap is valid, False otherwise
    """
    # Create employee pickup tracking
    pickup_positions = {}
    dropoff_positions = {}
    
    # Simulate the swap
    test_route = two_opt_swap(route, i, j)
    
    for idx, point in enumerate(test_route):
        emp_id = point['emp_id']
        
        if point['type'] == 'pickup':
            pickup_positions[emp_id] = idx
        elif point['type'] == 'dropoff':
            dropoff_positions[emp_id] = idx
    
    # Check that all pickups come before dropoffs
    for emp_id in pickup_positions:
        if emp_id in dropoff_positions:
            if pickup_positions[emp_id] >= dropoff_positions[emp_id]:
                return False
    
    return True


def two_opt_improve(route, vehicle_start_lat, vehicle_start_lng, max_iterations=100):
    """
    Improve route using 2-opt algorithm.
    
    The 2-opt algorithm repeatedly tries to swap segments of the route
    to find improvements in total distance.
    
    Args:
        route: List of route points
        vehicle_start_lat: Vehicle starting latitude
        vehicle_start_lng: Vehicle starting longitude
        max_iterations: Maximum number of improvement iterations
    
    Returns:
        Improved route
    """
    if len(route) < 4:
        # 2-opt requires at least 4 points to be meaningful
        return route
    
    best_route = route.copy()
    best_distance = calculate_segment_distance(best_route, vehicle_start_lat, vehicle_start_lng)
    
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        for i in range(len(best_route) - 1):
            for j in range(i + 2, len(best_route)):
                # Try swapping segment from i to j
                if not is_valid_swap(best_route, i, j):
                    continue
                
                new_route = two_opt_swap(best_route, i, j)
                new_distance = calculate_segment_distance(new_route, vehicle_start_lat, vehicle_start_lng)
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break
            
            if improved:
                break
    
    return best_route


def recalculate_etas(route, vehicle):
    """
    Recalculate ETAs for all points in route after optimization.
    
    Args:
        route: List of route points
        vehicle: Vehicle dictionary with speed and availability
    
    Returns:
        Route with updated ETAs
    """
    if not route:
        return route
    
    current_lat = vehicle['current_lat']
    current_lng = vehicle['current_lng']
    current_time = vehicle['available_from_min']
    
    updated_route = []
    
    for point in route:
        # Calculate distance and travel time to this point
        distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
        travel_time = calculate_travel_time(distance, vehicle['avg_speed'])
        
        # Update time
        current_time += travel_time
        
        # Create updated point
        updated_point = point.copy()
        updated_point['eta'] = format_time(current_time)
        updated_point['eta_min'] = current_time
        
        updated_route.append(updated_point)
        
        # Update current position
        current_lat = point['lat']
        current_lng = point['lng']
    
    return updated_route


def improve_all_routes(routes, vehicles):
    """
    Apply 2-opt improvement to all routes.
    
    Args:
        routes: Dict mapping vehicle_id to route information
        vehicles: List of vehicle dictionaries
    
    Returns:
        Updated routes dict with improved routes
    """
    vehicle_map = {v['id']: v for v in vehicles}
    improved_routes = {}
    
    for vehicle_id, route_info in routes.items():
        vehicle = vehicle_map[vehicle_id]
        route = route_info['route']
        
        # Convert route to internal format for processing
        route_points = []
        for point in route:
            route_points.append({
                'type': point['type'],
                'emp_id': point['emp_id'],
                'lat': point['lat'],
                'lng': point['lng'],
                'eta': point.get('eta', ''),
            })
        
        # Apply 2-opt improvement
        improved_route_points = two_opt_improve(
            route_points,
            vehicle['current_lat'],
            vehicle['current_lng']
        )
        
        # Recalculate ETAs
        improved_route_points = recalculate_etas(improved_route_points, vehicle)
        
        # Calculate new metrics
        total_distance = calculate_segment_distance(
            improved_route_points,
            vehicle['current_lat'],
            vehicle['current_lng']
        )
        
        total_time = 0
        if improved_route_points:
            start_time = vehicle['available_from_min']
            end_time = improved_route_points[-1]['eta_min']
            total_time = end_time - start_time
        
        # Clean route points
        clean_route = []
        for point in improved_route_points:
            clean_route.append({
                'type': point['type'],
                'emp_id': point['emp_id'],
                'lat': point['lat'],
                'lng': point['lng'],
                'eta': point['eta']
            })
        
        improved_routes[vehicle_id] = {
            'vehicle_id': vehicle_id,
            'assigned_employees': route_info['assigned_employees'],
            'route': clean_route,
            'total_distance_km': round(total_distance, 2),
            'total_time_min': round(total_time, 2)
        }
    
    return improved_routes
