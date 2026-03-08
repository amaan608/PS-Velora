"""
Route improvement using 2-opt algorithm.
Optimizes route sequences to reduce total distance while respecting constraints.
"""

from optimizer.utils import haversine, calculate_travel_time, format_time
from optimizer.constraints import (
    validate_route_capacity,
    validate_route_sharing,
    validate_route_time_windows
)


def two_opt_swap(route, i, j):
    """
    Perform 2-opt swap: reverse the order of route points between indices i and j.
    """
    new_route = route[:i] + route[i:j+1][::-1] + route[j+1:]
    return new_route


def calculate_segment_distance(route, vehicle_start_lat, vehicle_start_lng):
    """
    Calculate total distance for a route segment.
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


def recalculate_etas(route, vehicle):
    """
    Recalculate ETAs for all points in route after optimization.
    """
    if not route:
        return route
    
    current_lat = vehicle['current_lat']
    current_lng = vehicle['current_lng']
    current_time = vehicle['available_from_min']
    
    updated_route = []
    
    for point in route:
        distance = haversine(current_lat, current_lng, point['lat'], point['lng'])
        travel_time = calculate_travel_time(distance, vehicle['avg_speed'])
        
        current_time += travel_time
        
        updated_point = point.copy()
        updated_point['eta'] = format_time(current_time)
        updated_point['eta_min'] = current_time
        
        updated_route.append(updated_point)
        
        current_lat = point['lat']
        current_lng = point['lng']
    
    return updated_route


def is_valid_swap(route, i, j, vehicle):
    """
    Check if a 2-opt swap maintains all constraints.
    """
    # Simulate the swap
    test_route = two_opt_swap(route, i, j)
    
    # 1. Check pickup before dropoff constraint
    pickup_positions = {}
    dropoff_positions = {}
    for idx, point in enumerate(test_route):
        emp_id = point['emp_id']
        if point['type'] == 'pickup':
            pickup_positions[emp_id] = idx
        elif point['type'] == 'dropoff':
            dropoff_positions[emp_id] = idx
            
    for emp_id in pickup_positions:
        if emp_id in dropoff_positions:
            if pickup_positions[emp_id] >= dropoff_positions[emp_id]:
                return False
                
    # 2. Check Capacity Constraint
    if not validate_route_capacity(test_route, vehicle['capacity']):
        return False
        
    # 3. Check Sharing Constraint
    if not validate_route_sharing(test_route):
        return False
        
    # 4. Check Time Windows Constraint
    test_route_with_etas = recalculate_etas(test_route, vehicle)
    if not validate_route_time_windows(test_route_with_etas):
        return False
        
    return True


def two_opt_improve(route, vehicle, max_iterations=100):
    """
    Improve route using 2-opt algorithm.
    """
    if len(route) < 4:
        return route
    
    best_route = list(route.copy())
    best_distance = float(calculate_segment_distance(best_route, vehicle['current_lat'], vehicle['current_lng']))
    
    improved = True
    iteration = 0
    
    while improved and iteration < max_iterations:
        improved = False
        iteration += 1
        
        n = len(best_route)
        for i in range(n - 1):
            for j in range(int(i) + 2, n):
                if not is_valid_swap(best_route, i, j, vehicle):
                    continue
                
                new_route = two_opt_swap(best_route, i, j)
                new_distance = float(calculate_segment_distance(new_route, vehicle['current_lat'], vehicle['current_lng']))
                
                if new_distance < best_distance:
                    best_route = new_route
                    best_distance = new_distance
                    improved = True
                    break
            
            if improved:
                break
    
    return best_route


def improve_all_routes(routes, vehicles):
    """
    Apply 2-opt improvement to all routes.
    """
    vehicle_map = {v['id']: v for v in vehicles}
    improved_routes = {}
    
    for vehicle_id, route_info in routes.items():
        vehicle = vehicle_map[vehicle_id]
        route = route_info['route']
        
        # Apply 2-opt improvement
        improved_route_points = two_opt_improve(
            route,
            vehicle
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
            end_time = improved_route_points[-1].get('eta_min', start_time)
            total_time = end_time - start_time
            
        improved_routes[vehicle_id] = {
            'vehicle_id': vehicle_id,
            'assigned_employees': route_info['assigned_employees'],
            'route': improved_route_points,
            'total_distance_km': round(float(total_distance), 2),
            'total_time_min': round(float(total_time), 2)
        }
    
    return improved_routes
