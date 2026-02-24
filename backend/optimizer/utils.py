"""
Utility functions for the Velora optimization engine.
"""

import math


def haversine(lat1, lng1, lat2, lng2):
    """
    Calculate the great circle distance in kilometers between two points 
    on the earth (specified in decimal degrees).
    
    Args:
        lat1: Latitude of point 1
        lng1: Longitude of point 1
        lat2: Latitude of point 2
        lng2: Longitude of point 2
    
    Returns:
        Distance in kilometers
    """
    R = 6371  # Radius of earth in kilometers
    
    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lng2 - lng1)
    
    a = math.sin(dphi/2)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(dlambda/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_travel_time(distance_km, avg_speed_kmh):
    """
    Calculate travel time in minutes given distance and average speed.
    
    Args:
        distance_km: Distance in kilometers
        avg_speed_kmh: Average speed in km/h
    
    Returns:
        Travel time in minutes
    """
    if avg_speed_kmh <= 0:
        return 0
    return (distance_km / avg_speed_kmh) * 60


def parse_time(time_str):
    """
    Parse time string in HH:MM or HH:MM:SS format to minutes since midnight.
    
    Args:
        time_str: Time string in format "HH:MM", "H:MM", or "HH:MM:SS"
    
    Returns:
        Minutes since midnight as integer
    """
    if isinstance(time_str, (int, float)):
        return int(time_str)
    
    parts = str(time_str).strip().split(':')
    if len(parts) < 2 or len(parts) > 3:
        raise ValueError(f"Invalid time format: {time_str}")
    
    hours = int(parts[0])
    minutes = int(parts[1])
    # Ignore seconds if present
    
    return hours * 60 + minutes


def format_time(minutes):
    """
    Format minutes since midnight to HH:MM string.
    
    Args:
        minutes: Minutes since midnight
    
    Returns:
        Time string in format "HH:MM"
    """
    hours = int(minutes // 60)
    mins = int(minutes % 60)
    return f"{hours:02d}:{mins:02d}"
