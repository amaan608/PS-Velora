"""
Excel file parsing for employee and vehicle data.
Uses pandas and openpyxl to read .xlsx files.
"""

import pandas as pd
from optimizer.utils import parse_time


def parse_employees_file(file_path):
    """
    Parse employees Excel file and return list of employee dictionaries.
    
    Expected columns:
    - employee_id: Employee ID (string)
    - priority: Priority level 1-5 (integer, 1=highest)
    - pickup_lat: Pickup latitude (float)
    - pickup_lng: Pickup longitude (float)
    - drop_lat: Drop-off latitude (float)
    - drop_lng: Drop-off longitude (float)
    - earliest_pickup: Earliest pickup time HH:MM (string)
    - latest_drop: Latest drop-off time HH:MM (string)
    - vehicle_preference: premium/normal/any (string)
    - sharing_preference: single/double/triple (string)
    
    Args:
        file_path: Path to employees Excel file
    
    Returns:
        List of employee dictionaries
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Validate required columns
        required_cols = ['employee_id', 'priority', 'pickup_lat', 'pickup_lng', 'drop_lat', 
                        'drop_lng', 'earliest_pickup', 'latest_drop', 
                        'vehicle_preference', 'sharing_preference']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in employees file: {missing_cols}")
        
        employees = []
        for _, row in df.iterrows():
            # Convert numeric priority to high/normal
            priority_num = int(row['priority'])
            priority = 'high' if priority_num <= 2 else 'normal'
            
            employee = {
                'id': str(row['employee_id']).strip(),
                'priority': priority,
                'pickup_lat': float(row['pickup_lat']),
                'pickup_lng': float(row['pickup_lng']),
                'dest_lat': float(row['drop_lat']),
                'dest_lng': float(row['drop_lng']),
                'time_window_start': str(row['earliest_pickup']).strip(),
                'time_window_end': str(row['latest_drop']).strip(),
                'vehicle_preference': str(row['vehicle_preference']).strip().lower(),
                'sharing_preference': str(row['sharing_preference']).strip().lower(),
            }
            
            # Parse time windows to minutes
            employee['time_window_start_min'] = parse_time(employee['time_window_start'])
            employee['time_window_end_min'] = parse_time(employee['time_window_end'])
            
            # Validate vehicle preference (allow 'any' as 'normal')
            if employee['vehicle_preference'] == 'any':
                employee['vehicle_preference'] = 'normal'
            elif employee['vehicle_preference'] not in ['premium', 'normal']:
                employee['vehicle_preference'] = 'normal'
            
            if employee['sharing_preference'] not in ['single', 'double', 'triple']:
                employee['sharing_preference'] = 'triple'
            
            employees.append(employee)
        
        return employees
    
    except Exception as e:
        raise ValueError(f"Error parsing employees file: {str(e)}")


def parse_vehicles_file(file_path):
    """
    Parse vehicles Excel file and return list of vehicle dictionaries.
    
    Expected columns:
    - vehicle_id: Vehicle ID (string)
    - fuel_type: petrol/diesel/electric (string)
    - vehicle_type: sedan/suv/van/4W/2W (string)
    - capacity: Maximum passenger capacity (int)
    - cost_per_km: Cost per kilometer in rupees (float)
    - avg_speed_kmph: Average speed in km/h (float)
    - current_lat: Current latitude (float)
    - current_lng: Current longitude (float)
    - available_from: Availability time HH:MM (string)
    - category: premium/normal (string)
    
    Args:
        file_path: Path to vehicles Excel file
    
    Returns:
        List of vehicle dictionaries
    """
    try:
        df = pd.read_excel(file_path, engine='openpyxl')
        
        # Validate required columns
        required_cols = ['vehicle_id', 'fuel_type', 'vehicle_type', 'capacity', 'cost_per_km', 
                        'avg_speed_kmph', 'current_lat', 'current_lng', 'available_from', 'category']
        
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns in vehicles file: {missing_cols}")
        
        vehicles = []
        for _, row in df.iterrows():
            vehicle = {
                'id': str(row['vehicle_id']).strip(),
                'fuel_type': str(row['fuel_type']).strip().lower(),
                'mode': str(row['vehicle_type']).strip().lower(),
                'capacity': int(row['capacity']),
                'cost_per_km': float(row['cost_per_km']),
                'avg_speed': float(row['avg_speed_kmph']),
                'avg_mileage': 15.0,  # Default value since not in file
                'vehicle_age': 2.0,  # Default value since not in file
                'current_lat': float(row['current_lat']),
                'current_lng': float(row['current_lng']),
                'available_from': str(row['available_from']).strip(),
                'category': str(row['category']).strip().lower(),
            }
            
            # Parse availability time to minutes
            vehicle['available_from_min'] = parse_time(vehicle['available_from'])
            
            # Initialize assignment tracking
            vehicle['assigned_employees'] = []
            vehicle['current_capacity_used'] = 0
            
            vehicles.append(vehicle)
        
        return vehicles
    
    except Exception as e:
        raise ValueError(f"Error parsing vehicles file: {str(e)}")


def validate_parsed_data(employees, vehicles):
    """
    Validate that parsed data is sufficient for optimization.
    
    Args:
        employees: List of employee dictionaries
        vehicles: List of vehicle dictionaries
    
    Returns:
        Tuple of (is_valid, error_message)
    """
    if not employees:
        return False, "No employees found in file"
    
    if not vehicles:
        return False, "No vehicles found in file"
    
    # Check total capacity
    total_capacity = sum(v['capacity'] for v in vehicles)
    total_employees = len(employees)
    
    if total_capacity < total_employees:
        return False, f"Insufficient vehicle capacity ({total_capacity}) for {total_employees} employees"
    
    # Validate coordinates
    for emp in employees:
        if not (-90 <= emp['pickup_lat'] <= 90) or not (-180 <= emp['pickup_lng'] <= 180):
            return False, f"Invalid pickup coordinates for employee {emp['id']}"
        if not (-90 <= emp['dest_lat'] <= 90) or not (-180 <= emp['dest_lng'] <= 180):
            return False, f"Invalid destination coordinates for employee {emp['id']}"
    
    for veh in vehicles:
        if not (-90 <= veh['current_lat'] <= 90) or not (-180 <= veh['current_lng'] <= 180):
            return False, f"Invalid current coordinates for vehicle {veh['id']}"
    
    return True, ""
