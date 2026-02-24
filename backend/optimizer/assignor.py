"""
Employee-to-vehicle assignment engine.
Uses priority-first greedy algorithm with scoring based on distance and constraints.
"""

from optimizer.utils import haversine, calculate_travel_time
from optimizer.constraints import (
    validate_assignment,
    check_capacity_constraint,
    check_sharing_preference_constraint,
    check_existing_passengers_sharing_constraint,
    check_vehicle_category_preference
)


def calculate_assignment_score(vehicle, employee):
    """
    Calculate score for assigning employee to vehicle.
    Lower score is better (minimize distance).
    
    Args:
        vehicle: Vehicle dictionary with current location
        employee: Employee dictionary with pickup location
    
    Returns:
        Score (distance from vehicle to pickup point)
    """
    # Calculate distance from vehicle's current position to employee pickup
    distance = haversine(
        vehicle['current_lat'],
        vehicle['current_lng'],
        employee['pickup_lat'],
        employee['pickup_lng']
    )
    
    return distance


def find_best_vehicle_for_employee(employee, vehicles):
    """
    Find the best vehicle for an employee based on proximity and constraints.
    
    Args:
        employee: Employee dictionary
        vehicles: List of vehicle dictionaries
    
    Returns:
        Best vehicle dictionary or None if no suitable vehicle found
    """
    best_vehicle = None
    best_score = float('inf')
    
    for vehicle in vehicles:
        # Quick capacity check
        if not check_capacity_constraint(vehicle, employee):
            continue
        
        # Check vehicle category preference
        if not check_vehicle_category_preference(vehicle, employee):
            continue
        
        # Check sharing preferences
        if not check_sharing_preference_constraint(vehicle, employee):
            continue
        
        if not check_existing_passengers_sharing_constraint(vehicle, employee):
            continue
        
        # Calculate score (distance-based)
        score = calculate_assignment_score(vehicle, employee)
        
        if score < best_score:
            best_score = score
            best_vehicle = vehicle
    
    return best_vehicle


def assign_employees_to_vehicles(employees, vehicles):
    """
    Assign all employees to vehicles using priority-first greedy algorithm.
    
    Algorithm:
    1. Sort employees by priority (high priority first)
    2. For each employee, find the closest available vehicle that satisfies constraints
    3. Assign employee to that vehicle
    4. Update vehicle capacity and position
    
    Args:
        employees: List of employee dictionaries
        vehicles: List of vehicle dictionaries
    
    Returns:
        Tuple of (assignments, unassigned_employees)
        assignments: Dict mapping vehicle_id to list of assigned employees
        unassigned_employees: List of employees that couldn't be assigned
    """
    # Sort employees by priority (high first) then by time window start
    sorted_employees = sorted(
        employees,
        key=lambda e: (
            0 if e['priority'] == 'high' else 1,
            e['time_window_start_min']
        )
    )
    
    # Initialize assignment tracking
    assignments = {v['id']: [] for v in vehicles}
    unassigned_employees = []
    
    # Create vehicle lookup by ID
    vehicle_map = {v['id']: v for v in vehicles}
    
    for employee in sorted_employees:
        # Find best vehicle for this employee
        best_vehicle = find_best_vehicle_for_employee(employee, vehicles)
        
        if best_vehicle is None:
            unassigned_employees.append(employee)
            continue
        
        # Assign employee to vehicle
        best_vehicle['assigned_employees'].append(employee)
        best_vehicle['current_capacity_used'] += 1
        assignments[best_vehicle['id']].append(employee)
    
    # Filter out vehicles with no assignments
    assignments = {vid: emps for vid, emps in assignments.items() if emps}
    
    return assignments, unassigned_employees


def optimize_vehicle_utilization(assignments, vehicles):
    """
    Post-process assignments to improve vehicle utilization.
    Try to consolidate employees into fewer vehicles where possible.
    
    Args:
        assignments: Dict mapping vehicle_id to list of assigned employees
        vehicles: List of vehicle dictionaries
    
    Returns:
        Updated assignments dictionary
    """
    # This is a simple implementation - can be enhanced with more sophisticated algorithms
    # For now, we'll keep the greedy assignments as they prioritize proximity
    return assignments


def get_assignment_summary(assignments, vehicles):
    """
    Generate summary statistics for the assignment.
    
    Args:
        assignments: Dict mapping vehicle_id to list of assigned employees
        vehicles: List of vehicle dictionaries
    
    Returns:
        Dictionary with assignment statistics
    """
    vehicle_map = {v['id']: v for v in vehicles}
    
    total_vehicles_used = len(assignments)
    total_employees_assigned = sum(len(emps) for emps in assignments.values())
    
    utilization_rates = []
    for vid, emps in assignments.items():
        vehicle = vehicle_map[vid]
        utilization = len(emps) / vehicle['capacity'] * 100
        utilization_rates.append(utilization)
    
    avg_utilization = sum(utilization_rates) / len(utilization_rates) if utilization_rates else 0
    
    return {
        'total_vehicles_used': total_vehicles_used,
        'total_employees_assigned': total_employees_assigned,
        'average_utilization_percent': round(avg_utilization, 2),
        'vehicles_utilized': list(assignments.keys())
    }
