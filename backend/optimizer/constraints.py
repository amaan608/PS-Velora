"""
Constraint validation functions for vehicle-employee assignment.
All constraints must be satisfied for a valid optimization solution.
"""


def check_capacity_constraint(vehicle, employee):
    """
    Check if adding employee to vehicle would exceed capacity.
    
    Args:
        vehicle: Vehicle dictionary with 'capacity' and 'current_capacity_used'
        employee: Employee dictionary
    
    Returns:
        True if capacity constraint is satisfied, False otherwise
    """
    return vehicle['current_capacity_used'] < vehicle['capacity']


def check_vehicle_category_preference(vehicle, employee):
    """
    Check if vehicle category matches employee's vehicle preference.
    
    Args:
        vehicle: Vehicle dictionary with 'category' (premium/normal)
        employee: Employee dictionary with 'vehicle_preference' (premium/normal)
    
    Returns:
        True if preference is satisfied, False otherwise
    """
    vehicle_category = vehicle.get('category', 'normal')
    employee_preference = employee.get('vehicle_preference', 'normal')
    
    # If employee wants premium, vehicle must be premium
    if employee_preference == 'premium':
        return vehicle_category == 'premium'
    
    # If employee wants normal or any, any vehicle is fine
    return True


def check_sharing_preference_constraint(vehicle, employee):
    """
    Check if employee's sharing preference is compatible with current vehicle occupancy.
    
    Sharing preferences:
    - single: Must be alone in vehicle
    - double: Maximum 2 people including self
    - triple: Maximum 3 people including self
    
    Args:
        vehicle: Vehicle dictionary with 'assigned_employees' list
        employee: Employee dictionary with 'sharing_preference'
    
    Returns:
        True if sharing preference is satisfied, False otherwise
    """
    current_count = vehicle['current_capacity_used']
    new_count = current_count + 1
    
    sharing_pref = employee['sharing_preference']
    
    if sharing_pref == 'single':
        # Must be alone
        return current_count == 0
    elif sharing_pref == 'double':
        # Maximum 2 people
        return new_count <= 2
    elif sharing_pref == 'triple':
        # Maximum 3 people
        return new_count <= 3
    else:
        # Default to allowing sharing
        return True


def check_existing_passengers_sharing_constraint(vehicle, employee):
    """
    Check if existing passengers in vehicle have sharing preferences that allow new employee.
    
    Args:
        vehicle: Vehicle dictionary with 'assigned_employees' list
        employee: Employee dictionary (not used but kept for consistency)
    
    Returns:
        True if all existing passengers' sharing preferences allow additional passenger
    """
    current_count = vehicle['current_capacity_used']
    
    if current_count == 0:
        return True
    
    # Check each assigned employee's sharing preference
    for assigned_emp in vehicle['assigned_employees']:
        sharing_pref = assigned_emp.get('sharing_preference', 'triple')
        
        if sharing_pref == 'single':
            # Single preference violated if anyone else joins
            return False
        elif sharing_pref == 'double' and current_count >= 2:
            # Double preference violated if 3rd person joins
            return False
        elif sharing_pref == 'triple' and current_count >= 3:
            # Triple preference violated if 4th person joins
            return False
    
    return True


def check_time_window_feasibility(employee, pickup_eta):
    """
    Check if pickup can happen within employee's time window.
    Applies different tolerance based on priority.
    
    High priority: max 5 minutes late
    Normal priority: max 15 minutes late
    
    Args:
        employee: Employee dictionary with time window and priority
        pickup_eta: Estimated time of arrival in minutes since midnight
    
    Returns:
        True if time window constraint is satisfied, False otherwise
    """
    time_start = employee['time_window_start_min']
    time_end = employee['time_window_end_min']
    priority = employee.get('priority', 'normal')
    
    # Allow arriving early
    if pickup_eta < time_start:
        return True
    
    # Check lateness tolerance
    if priority == 'high':
        max_delay = 5  # 5 minutes
    else:
        max_delay = 15  # 15 minutes
    
    return pickup_eta <= (time_end + max_delay)


def check_vehicle_availability(vehicle, required_time):
    """
    Check if vehicle is available at the required time.
    
    Args:
        vehicle: Vehicle dictionary with 'available_from_min'
        required_time: Required availability time in minutes since midnight
    
    Returns:
        True if vehicle is available, False otherwise
    """
    return required_time >= vehicle['available_from_min']


def validate_assignment(vehicle, employee, pickup_eta):
    """
    Validate all constraints for assigning employee to vehicle.
    
    Args:
        vehicle: Vehicle dictionary
        employee: Employee dictionary
        pickup_eta: Estimated pickup time in minutes since midnight
    
    Returns:
        Tuple of (is_valid, reason)
    """
    # Check capacity
    if not check_capacity_constraint(vehicle, employee):
        return False, "Vehicle capacity exceeded"
    
    # Check new employee's sharing preference
    if not check_sharing_preference_constraint(vehicle, employee):
        return False, "Employee sharing preference not satisfied"
    
    # Check existing passengers' sharing preferences
    if not check_existing_passengers_sharing_constraint(vehicle, employee):
        return False, "Existing passengers' sharing preferences violated"
    
    # Check time window
    if not check_time_window_feasibility(employee, pickup_eta):
        return False, "Time window constraint violated"
    
    # Check vehicle availability
    if not check_vehicle_availability(vehicle, pickup_eta):
        return False, "Vehicle not available at required time"
    
    return True, ""


def get_max_sharing_capacity(employee):
    """
    Get maximum sharing capacity based on employee preference.
    
    Args:
        employee: Employee dictionary with 'sharing_preference'
    
    Returns:
        Maximum number of passengers allowed
    """
    sharing_pref = employee.get('sharing_preference', 'triple')
    
    if sharing_pref == 'single':
        return 1
    elif sharing_pref == 'double':
        return 2
    elif sharing_pref == 'triple':
        return 3
    else:
        return 3


def calculate_delay_penalty(employee, pickup_eta):
    """
    Calculate penalty score for time window violation.
    Higher penalty for high priority employees.
    
    Args:
        employee: Employee dictionary with time window and priority
        pickup_eta: Estimated pickup time in minutes since midnight
    
    Returns:
        Penalty score (0 if no violation, higher values for worse violations)
    """
    time_end = employee['time_window_end_min']
    priority = employee.get('priority', 'normal')
    
    if pickup_eta <= time_end:
        return 0
    
    delay = pickup_eta - time_end
    
    if priority == 'high':
        # High priority: each minute of delay is heavily penalized
        return delay * 10
    else:
        # Normal priority: less penalty per minute
        return delay * 3
