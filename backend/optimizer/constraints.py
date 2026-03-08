"""
Constraint validation functions for vehicle-employee assignment.
All constraints must be satisfied for a valid optimization solution.
"""

def check_vehicle_category_preference(vehicle, employee):
    """
    Check if vehicle category matches employee's vehicle preference.
    """
    vehicle_category = vehicle.get('category', 'normal')
    employee_preference = employee.get('vehicle_preference', 'normal')
    
    if employee_preference == 'premium':
        return vehicle_category == 'premium'
    return True

def validate_route_capacity(route, vehicle_capacity):
    """
    Check if the route ever exceeds the vehicle's maximum capacity concurrently.
    """
    current_occupancy = 0
    for point in route:
        if point['type'] == 'pickup':
            current_occupancy += 1
        elif point['type'] == 'dropoff':
            current_occupancy -= 1
            
        if current_occupancy > vehicle_capacity:
            return False
    return True

def validate_route_sharing(route):
    """
    Check if the route violates any concurrent sharing preferences.
    Sharing preferences:
    - single: Must be alone in vehicle
    - double: Maximum 2 people including self
    - triple: Maximum 3 people including self
    """
    # Map employee ID to sharing preference
    sharing_prefs = {}
    for point in route:
        emp_id = point['emp_id']
        if 'employee' in point:
            sharing_prefs[emp_id] = point['employee'].get('sharing_preference', 'triple')
    
    current_passengers = set()
    
    for point in route:
        emp_id = point['emp_id']
        
        if point['type'] == 'pickup':
            current_passengers.add(emp_id)
        elif point['type'] == 'dropoff':
            if emp_id in current_passengers:
                current_passengers.remove(emp_id)
                
        count = len(current_passengers)
        
        # Check constraints for all currently in the vehicle
        for p_id in current_passengers:
            pref = sharing_prefs.get(p_id, 'triple')
            if pref == 'single' and count > 1:
                return False
            elif pref == 'double' and count > 2:
                return False
            elif pref == 'triple' and count > 3:
                return False
                
    return True

def check_time_window_feasibility(employee, pickup_eta):
    """
    Check if pickup can happen within employee's time window.
    """
    time_start = employee['time_window_start_min']
    time_end = employee['time_window_end_min']
    priority = employee.get('priority', 'normal')
    
    if pickup_eta < time_start:
        return True
    
    if priority == 'high':
        max_delay = 5
    else:
        max_delay = 15
        
    return pickup_eta <= (time_end + max_delay)

def calculate_delay_penalty(employee, pickup_eta):
    """
    Calculate penalty score for time window violation.
    """
    time_end = employee['time_window_end_min']
    priority = employee.get('priority', 'normal')
    
    if pickup_eta <= time_end:
        return 0
    
    delay = pickup_eta - time_end
    
    if priority == 'high':
        return delay * 10
    else:
        return delay * 3

def validate_route_time_windows(route):
    """
    Check if all time windows and lateness tolerances are respected in the sequence.
    """
    for point in route:
        if point['type'] == 'pickup':
            if 'eta_min' in point and 'employee' in point:
                if not check_time_window_feasibility(point['employee'], point['eta_min']):
                    return False
    return True
