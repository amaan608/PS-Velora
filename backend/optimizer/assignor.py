"""
Employee-to-vehicle assignment engine.
Uses an Insertion Heuristic to assign employees based on overall route cost,
interleaving pickups and dropoffs while respecting capacity, time window, and sharing constraints.
"""

from optimizer.utils import haversine, calculate_travel_time, format_time
from optimizer.constraints import (
    check_vehicle_category_preference,
    validate_route_capacity,
    validate_route_sharing,
    validate_route_time_windows,
    calculate_delay_penalty,
    check_time_window_feasibility
)
from optimizer.router import create_route_point, calculate_route_distance

def recalculate_route_etas(route, vehicle):
    """
    Given a sequence of route points, compute ETAs from vehicle's start position.
    """
    if not route:
        return []
        
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

def calculate_insertion_cost(original_route, tentative_route, vehicle, employee):
    """
    Calculate the actual cost increase of inserting an employee into a route.
    Cost = (added_distance * cost_per_km) + delay_penalties
    """
    orig_dist = calculate_route_distance(original_route, vehicle['current_lat'], vehicle['current_lng'])
    new_dist = calculate_route_distance(tentative_route, vehicle['current_lat'], vehicle['current_lng'])
    added_dist = new_dist - orig_dist
    
    cost_per_km = vehicle.get('cost_per_km', 1.0)
    base_cost = added_dist * cost_per_km
    
    # Calculate delay penalty for the new pickup
    pickup_eta = 0
    for pt in tentative_route:
        if pt['type'] == 'pickup' and pt['emp_id'] == employee['id']:
            pickup_eta = pt.get('eta_min', 0)
            break
            
    delay_penalty = calculate_delay_penalty(employee, pickup_eta)
    
    return base_cost + delay_penalty

def find_best_insertion_for_employee(employee, vehicles):
    """
    Find the best vehicle and lowest-cost insertion positions for an employee.
    """
    best_vehicle = None
    best_cost = float('inf')
    best_route = None
    
    pickup_pt = create_route_point('pickup', employee, employee['pickup_lat'], employee['pickup_lng'])
    dropoff_pt = create_route_point('dropoff', employee, employee['dest_lat'], employee['dest_lng'])
    
    for vehicle in vehicles:
        if not check_vehicle_category_preference(vehicle, employee):
            continue
            
        current_route = vehicle.get('route', [])
        route_len = len(current_route)
        
        # Try every combination of i (pickup index) and j (dropoff index) where i <= j
        for i in range(route_len + 1):
            for j in range(i, route_len + 1):
                # Construct tentative route
                tentative = current_route[:i] + [pickup_pt] + current_route[i:j] + [dropoff_pt] + current_route[j:]
                
                # Verify basic logical capacities early before heavy ETA calcs
                if not validate_route_capacity(tentative, vehicle['capacity']):
                    continue
                if not validate_route_sharing(tentative):
                    continue
                    
                # Calculate ETAs to verify time windows
                tentative_with_etas = recalculate_route_etas(tentative, vehicle)
                
                # Check Vehicle availability simply based on first pickup ETA if needed, but ETAs start from vehicle availability anyway.
                if not validate_route_time_windows(tentative_with_etas):
                    continue
                    
                # Calculate True Cost
                cost = calculate_insertion_cost(current_route, tentative_with_etas, vehicle, employee)
                
                if cost < best_cost:
                    best_cost = cost
                    best_vehicle = vehicle
                    best_route = tentative_with_etas
                    
    return best_vehicle, best_route

def assign_employees_to_vehicles(employees, vehicles):
    """
    Assign all employees to vehicles using Insertion Heuristic.
    """
    # Sort employees by priority (high first) then by time window start
    sorted_employees = sorted(
        employees,
        key=lambda e: (
            0 if e.get('priority') == 'high' else 1,
            e['time_window_start_min']
        )
    )
    
    # Initialize empty routes and tracking
    for v in vehicles:
        v['route'] = []
        v['assigned_employees'] = []
        v['current_capacity_used'] = 0
        
    unassigned_employees = []
    assignments = {v['id']: [] for v in vehicles}
    
    for employee in sorted_employees:
        best_vehicle, best_route = find_best_insertion_for_employee(employee, vehicles)
        
        if best_vehicle is None:
            unassigned_employees.append(employee)
            continue
            
        # Lock in the insertion
        best_vehicle['route'] = best_route
        best_vehicle['assigned_employees'].append(employee)
        assignments[best_vehicle['id']].append(employee)
        
        # Update current capacity (max utilized) for legacy reasons if anywhere uses it
        max_cap = 0
        curr = 0
        for pt in best_route:
            if pt['type'] == 'pickup':
                curr += 1
            else:
                curr -= 1
            max_cap = max(max_cap, curr)
        best_vehicle['current_capacity_used'] = max_cap

    assignments = {vid: emps for vid, emps in assignments.items() if emps}
    
    return assignments, unassigned_employees


def optimize_vehicle_utilization(assignments, vehicles):
    return assignments


def get_assignment_summary(assignments, vehicles):
    vehicle_map = {v['id']: v for v in vehicles}
    
    total_vehicles_used = len(assignments)
    total_employees_assigned = sum(len(emps) for emps in assignments.values())
    
    utilization_rates = []
    for vid, emps in assignments.items():
        vehicle = vehicle_map[vid]
        # Max capacity utilized on the route
        max_cap_used = 0
        current_cap = 0
        route = vehicle.get('route', [])
        for pt in route:
            if pt['type'] == 'pickup':
                current_cap += 1
                max_cap_used = max(max_cap_used, current_cap)
            else:
                current_cap -= 1
                
        utilization = (max_cap_used / vehicle['capacity']) * 100 if vehicle['capacity'] else 0
        utilization_rates.append(utilization)
    
    avg_utilization = sum(utilization_rates) / len(utilization_rates) if utilization_rates else 0
    
    return {
        'total_vehicles_used': total_vehicles_used,
        'total_employees_assigned': total_employees_assigned,
        'average_utilization_percent': round(avg_utilization, 2),
        'vehicles_utilized': list(assignments.keys())
    }
