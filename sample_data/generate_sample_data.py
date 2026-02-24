"""
Script to generate sample Excel files for testing Velora.
Creates employees.xlsx and vehicles.xlsx with realistic Bangalore coordinates.
"""

import pandas as pd
import random

# Set random seed for reproducibility
random.seed(42)

# Bangalore coordinates range
# Central Bangalore area
LAT_MIN, LAT_MAX = 12.85, 13.05
LNG_MIN, LNG_MAX = 77.50, 77.70

# Common destinations (tech parks, business areas in Bangalore)
DESTINATIONS = [
    {'name': 'Manyata Tech Park', 'lat': 13.0358, 'lng': 77.6158},
    {'name': 'Electronic City', 'lat': 12.8450, 'lng': 77.6653},
    {'name': 'Whitefield', 'lat': 12.9698, 'lng': 77.7499},
    {'name': 'Koramangala', 'lat': 12.9352, 'lng': 77.6245},
    {'name': 'Indiranagar', 'lat': 12.9716, 'lng': 77.6412},
]

def random_coordinate(min_val, max_val):
    """Generate random coordinate within range."""
    return round(random.uniform(min_val, max_val), 6)

def generate_employees_data(num_employees=20):
    """Generate employee data with realistic Bangalore coordinates."""
    employees = []
    
    for i in range(1, num_employees + 1):
        # Random pickup location
        pickup_lat = random_coordinate(LAT_MIN, LAT_MAX)
        pickup_lng = random_coordinate(LNG_MIN, LNG_MAX)
        
        # Destination - pick a common destination
        dest = random.choice(DESTINATIONS)
        dest_lat = dest['lat'] + random.uniform(-0.01, 0.01)  # Add small variation
        dest_lng = dest['lng'] + random.uniform(-0.01, 0.01)
        
        # Time window - morning commute (8 AM - 9:30 AM)
        hour = random.choice([8, 9])
        minute = random.choice([0, 15, 30, 45])
        time_start = f"{hour:02d}:{minute:02d}"
        
        # End time is 30-60 minutes later
        end_minutes = minute + random.choice([30, 45, 60])
        end_hour = hour
        if end_minutes >= 60:
            end_minutes -= 60
            end_hour += 1
        time_end = f"{end_hour:02d}:{end_minutes:02d}"
        
        # Priority - numeric 1-5, with 30% high priority (1-2)
        priority = random.choice([1, 2]) if random.random() < 0.3 else random.choice([3, 4, 5])
        
        # Vehicle preference - 20% premium
        vehicle_pref = 'premium' if random.random() < 0.2 else random.choice(['normal', 'any'])
        
        # Sharing preference - distribution
        sharing_choice = random.choices(
            ['single', 'double', 'triple'],
            weights=[0.1, 0.3, 0.6]  # 10% single, 30% double, 60% triple
        )[0]
        
        employee = {
            'employee_id': f'E{i:03d}',
            'priority': priority,
            'pickup_lat': pickup_lat,
            'pickup_lng': pickup_lng,
            'drop_lat': dest_lat,
            'drop_lng': dest_lng,
            'earliest_pickup': time_start,
            'latest_drop': time_end,
            'vehicle_preference': vehicle_pref,
            'sharing_preference': sharing_choice
        }
        
        employees.append(employee)
    
    return pd.DataFrame(employees)

def generate_vehicles_data(num_vehicles=8):
    """Generate vehicle data with realistic specifications."""
    vehicles = []
    
    fuel_types = ['petrol', 'diesel', 'electric']
    modes = ['sedan', 'suv', 'van']
    
    for i in range(1, num_vehicles + 1):
        fuel_type = random.choice(fuel_types)
        mode = random.choice(modes)
        
        # Capacity based on mode
        if mode == 'sedan':
            capacity = random.choice([3, 4])
        elif mode == 'suv':
            capacity = random.choice([5, 6])
        else:  # van
            capacity = random.choice([6, 7, 8])
        
        # Cost per km based on mode and fuel
        if mode == 'sedan':
            cost_per_km = round(random.uniform(8, 12), 2)
        elif mode == 'suv':
            cost_per_km = round(random.uniform(10, 14), 2)
        else:  # van
            cost_per_km = round(random.uniform(12, 16), 2)
        
        # Adjust for electric (slightly cheaper)
        if fuel_type == 'electric':
            cost_per_km *= 0.8
            cost_per_km = round(cost_per_km, 2)
        
        # Average speed (km/h) - Bangalore traffic
        avg_speed = round(random.uniform(25, 35), 1)
        
        # Mileage
        if fuel_type == 'electric':
            avg_mileage = round(random.uniform(4, 6), 1)  # km/kWh
        elif fuel_type == 'diesel':
            avg_mileage = round(random.uniform(15, 20), 1)  # km/l
        else:  # petrol
            avg_mileage = round(random.uniform(12, 16), 1)  # km/l
        
        # Vehicle age
        vehicle_age = round(random.uniform(0.5, 5), 1)
        
        # Current location - random in Bangalore
        current_lat = random_coordinate(LAT_MIN, LAT_MAX)
        current_lng = random_coordinate(LNG_MIN, LNG_MAX)
        
        # Available from - early morning
        hour = random.choice([6, 7])
        minute = random.choice([0, 15, 30, 45])
        available_from = f"{hour:02d}:{minute:02d}"
        
        # Category - 30% premium
        category = 'premium' if random.random() < 0.3 else 'normal'
        
        vehicle = {
            'vehicle_id': f'V{i:03d}',
            'fuel_type': fuel_type,
            'vehicle_type': mode,
            'capacity': capacity,
            'cost_per_km': cost_per_km,
            'avg_speed_kmph': avg_speed,
            'current_lat': current_lat,
            'current_lng': current_lng,
            'available_from': available_from,
            'category': category
        }
        
        vehicles.append(vehicle)
    
    return pd.DataFrame(vehicles)

def main():
    """Generate and save sample Excel files."""
    print("Generating sample data...")
    
    # Generate data
    employees_df = generate_employees_data(20)
    vehicles_df = generate_vehicles_data(8)
    
    # Save to Excel
    employees_file = 'employees.xlsx'
    vehicles_file = 'vehicles.xlsx'
    
    employees_df.to_excel(employees_file, index=False, engine='openpyxl')
    vehicles_df.to_excel(vehicles_file, index=False, engine='openpyxl')
    
    print(f"✓ Generated {employees_file} with {len(employees_df)} employees")
    print(f"✓ Generated {vehicles_file} with {len(vehicles_df)} vehicles")
    
    # Print summary (1-2): {len(employees_df[employees_df['priority'] <= 2])}")
    print(f"  Normal Priority (3-5): {len(employees_df[employees_df['priority'] >= 3])}")
    print(f"  Single: {len(employees_df[employees_df['sharing_preference'] == 'single'])}")
    print(f"  Double: {len(employees_df[employees_df['sharing_preference'] == 'double'])}")
    print(f"  Triple: {len(employees_df[employees_df['sharing_preference'] == 'triple'])}")
    
    print("\nVehicles Summary:")
    print(f"  Total Capacity: {vehicles_df['capacity'].sum()}")
    print(f"  Sedans: {len(vehicles_df[vehicles_df['vehicle_type'] == 'sedan'])}")
    print(f"  SUVs: {len(vehicles_df[vehicles_df['vehicle_type'] == 'suv'])}")
    print(f"  Vans: {len(vehicles_df[vehicles_df['vehicle_type'] == 'van'])}")
    print(f"  Premium: {len(vehicles_df[vehicles_df['category'] == 'premium'])}")
    print(f"  Normal: {len(vehicles_df[vehicles_df['category'] == 'normaledan'])}")
    print(f"  SUVs: {len(vehicles_df[vehicles_df['mode'] == 'suv'])}")
    print(f"  Vans: {len(vehicles_df[vehicles_df['mode'] == 'van'])}")

if __name__ == '__main__':
    main()
