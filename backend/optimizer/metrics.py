"""
Metrics calculation for optimization results.
Calculates operational costs, baseline costs, and savings.
"""

from optimizer.utils import haversine


def calculate_optimized_cost(routes, vehicles):
    """
    Calculate total operational cost for optimized routes.
    
    Cost = distance × cost_per_km for each vehicle
    
    Args:
        routes: Dict mapping vehicle_id to route information
        vehicles: List of vehicle dictionaries
    
    Returns:
        Total optimized cost in rupees
    """
    vehicle_map = {v['id']: v for v in vehicles}
    total_cost = 0.0
    
    for vehicle_id, route_info in routes.items():
        vehicle = vehicle_map[vehicle_id]
        distance = route_info['total_distance_km']
        cost_per_km = vehicle['cost_per_km']
        
        total_cost += distance * cost_per_km
    
    return total_cost


def calculate_baseline_cost(employees, baseline_cost_per_km=15.0):
    """
    Calculate baseline cost assuming each employee takes individual cab.
    
    Baseline = sum of (pickup to destination distance × baseline_cost_per_km) for all employees
    
    Args:
        employees: List of employee dictionaries
        baseline_cost_per_km: Cost per km for individual cab (default ₹15/km)
    
    Returns:
        Total baseline cost in rupees
    """
    total_baseline_cost = 0.0
    
    for employee in employees:
        # Calculate direct distance from pickup to destination
        distance = haversine(
            employee['pickup_lat'],
            employee['pickup_lng'],
            employee['dest_lat'],
            employee['dest_lng']
        )
        
        total_baseline_cost += distance * baseline_cost_per_km
    
    return total_baseline_cost


def calculate_total_travel_time(routes):
    """
    Calculate total travel time across all routes.
    
    Args:
        routes: Dict mapping vehicle_id to route information
    
    Returns:
        Total travel time in minutes
    """
    total_time = 0.0
    
    for route_info in routes.values():
        total_time += route_info['total_time_min']
    
    return total_time


def calculate_total_distance(routes):
    """
    Calculate total distance across all routes.
    
    Args:
        routes: Dict mapping vehicle_id to route information
    
    Returns:
        Total distance in kilometers
    """
    total_distance = 0.0
    
    for route_info in routes.values():
        total_distance += route_info['total_distance_km']
    
    return total_distance


def calculate_savings(optimized_cost, baseline_cost):
    """
    Calculate cost savings from optimization.
    
    Args:
        optimized_cost: Total cost with optimization
        baseline_cost: Baseline cost without optimization
    
    Returns:
        Tuple of (savings_absolute, savings_percentage)
    """
    savings_absolute = baseline_cost - optimized_cost
    
    if baseline_cost > 0:
        savings_percentage = (savings_absolute / baseline_cost) * 100
    else:
        savings_percentage = 0.0
    
    return savings_absolute, savings_percentage


def calculate_all_metrics(routes, vehicles, employees):
    """
    Calculate all metrics for the optimization results.
    
    Args:
        routes: Dict mapping vehicle_id to route information
        vehicles: List of vehicle dictionaries
        employees: List of employee dictionaries
    
    Returns:
        Dictionary with all metrics
    """
    # Calculate costs
    optimized_cost = calculate_optimized_cost(routes, vehicles)
    baseline_cost = calculate_baseline_cost(employees)
    savings_absolute, savings_percentage = calculate_savings(optimized_cost, baseline_cost)
    
    # Calculate other metrics
    total_travel_time = calculate_total_travel_time(routes)
    total_distance = calculate_total_distance(routes)
    
    metrics = {
        'total_cost_optimized': round(float(optimized_cost), 2),
        'total_cost_baseline': round(float(baseline_cost), 2),
        'savings_absolute': round(float(savings_absolute), 2),
        'savings_percentage': round(float(savings_percentage), 2),
        'total_travel_time_min': round(float(total_travel_time), 2),
        'total_distance_km': round(float(total_distance), 2),
        'num_vehicles_used': len(routes),
        'num_employees': len(employees)
    }
    
    return metrics


def get_vehicle_metrics(routes, vehicles):
    """
    Get per-vehicle metrics breakdown.
    
    Args:
        routes: Dict mapping vehicle_id to route information
        vehicles: List of vehicle dictionaries
    
    Returns:
        List of vehicle metric dictionaries
    """
    vehicle_map = {v['id']: v for v in vehicles}
    vehicle_metrics = []
    
    for vehicle_id, route_info in routes.items():
        vehicle = vehicle_map[vehicle_id]
        
        max_cap_used = 0
        current_cap = 0
        for pt in route_info['route']:
            if pt.get('type') == 'pickup':
                current_cap += 1
                max_cap_used = max(max_cap_used, current_cap)
            elif pt.get('type') == 'dropoff':
                current_cap -= 1
                
        utilization = (max_cap_used / vehicle['capacity']) * 100 if vehicle['capacity'] else 0
        
        metrics = {
            'vehicle_id': vehicle_id,
            'distance_km': route_info['total_distance_km'],
            'travel_time_min': route_info['total_time_min'],
            'num_employees': len(route_info['assigned_employees']),
            'capacity': vehicle['capacity'],
            'utilization_percent': round(float(utilization), 2),
            'cost': round(float(route_info['total_distance_km'] * vehicle['cost_per_km']), 2)
        }
        
        vehicle_metrics.append(metrics)
    
    return vehicle_metrics
