"""
REST API views for Velora transportation optimization.
"""

import os
import tempfile
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status

from optimizer.parser import parse_employees_file, parse_vehicles_file, validate_parsed_data
from optimizer.assignor import assign_employees_to_vehicles, get_assignment_summary
from optimizer.router import generate_routes_for_all_vehicles
from optimizer.improver import improve_all_routes
from optimizer.metrics import calculate_all_metrics, get_vehicle_metrics


# In-memory storage for demo purposes
# In production, use database or cache
OPTIMIZATION_RESULTS = {}


@api_view(['POST'])
def upload_files(request):
    """
    Upload and validate employee and vehicle Excel files.
    
    Expected files:
    - employees_file: Excel file with employee data
    - vehicles_file: Excel file with vehicle data
    
    Returns:
    - success: Boolean
    - message: Status message
    - data: Parsed data summary
    """
    try:
        # Get uploaded files
        employees_file = request.FILES.get('employees_file')
        vehicles_file = request.FILES.get('vehicles_file')
        
        if not employees_file:
            return Response({
                'success': False,
                'message': 'Employees file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if not vehicles_file:
            return Response({
                'success': False,
                'message': 'Vehicles file is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Save files temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as emp_temp:
            for chunk in employees_file.chunks():
                emp_temp.write(chunk)
            emp_temp_path = emp_temp.name
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xlsx') as veh_temp:
            for chunk in vehicles_file.chunks():
                veh_temp.write(chunk)
            veh_temp_path = veh_temp.name
        
        try:
            # Parse files
            employees = parse_employees_file(emp_temp_path)
            vehicles = parse_vehicles_file(veh_temp_path)
            
            # Validate data
            is_valid, error_msg = validate_parsed_data(employees, vehicles)
            
            if not is_valid:
                return Response({
                    'success': False,
                    'message': f'Validation failed: {error_msg}'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Store in memory
            OPTIMIZATION_RESULTS['employees'] = employees
            OPTIMIZATION_RESULTS['vehicles'] = vehicles
            OPTIMIZATION_RESULTS['optimized'] = False
            
            return Response({
                'success': True,
                'message': 'Files uploaded and validated successfully',
                'data': {
                    'num_employees': len(employees),
                    'num_vehicles': len(vehicles),
                    'total_capacity': sum(v['capacity'] for v in vehicles)
                }
            }, status=status.HTTP_200_OK)
        
        finally:
            # Clean up temp files
            if os.path.exists(emp_temp_path):
                os.unlink(emp_temp_path)
            if os.path.exists(veh_temp_path):
                os.unlink(veh_temp_path)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error processing files: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def optimize(request):
    """
    Run the optimization algorithm on uploaded data.
    
    Returns:
    - success: Boolean
    - message: Status message
    - data: Optimization results with routes and metrics
    """
    try:
        # Check if data is uploaded
        if 'employees' not in OPTIMIZATION_RESULTS or 'vehicles' not in OPTIMIZATION_RESULTS:
            return Response({
                'success': False,
                'message': 'Please upload employee and vehicle files first'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        employees = OPTIMIZATION_RESULTS['employees']
        vehicles = OPTIMIZATION_RESULTS['vehicles']
        
        # Make copies to avoid modifying original data
        employees_copy = [emp.copy() for emp in employees]
        vehicles_copy = [veh.copy() for veh in vehicles]
        
        # Re-initialize vehicle assignment tracking
        for vehicle in vehicles_copy:
            vehicle['assigned_employees'] = []
            vehicle['current_capacity_used'] = 0
        
        # Step 1: Assign employees to vehicles
        assignments, unassigned = assign_employees_to_vehicles(employees_copy, vehicles_copy)
        
        # If NO employees were assigned, return error
        if not assignments:
            return Response({
                'success': False,
                'message': f'Could not assign any employees to vehicles. Please check vehicle capacity and preferences.',
                'data': {
                    'unassigned_employee_ids': [emp['id'] for emp in unassigned]
                }
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 2: Generate routes using Nearest Neighbor
        routes = generate_routes_for_all_vehicles(assignments, vehicles_copy)
        
        # Step 3: Improve routes using 2-opt
        improved_routes = improve_all_routes(routes, vehicles_copy)
        
        # Step 4: Calculate metrics
        metrics = calculate_all_metrics(improved_routes, vehicles_copy, employees_copy)
        vehicle_metrics = get_vehicle_metrics(improved_routes, vehicles_copy)
        
        # Prepare final results with unassigned info
        # Clean up route objects before serialization
        final_vehicles = []
        for v in improved_routes.values():
            clean_routes = []
            for point in v['route']:
                clean_pt = point.copy()
                if 'employee' in clean_pt:
                    del clean_pt['employee']
                clean_routes.append(clean_pt)
            v_copy = v.copy()
            v_copy['route'] = clean_routes
            final_vehicles.append(v_copy)

        results = {
            'vehicles': final_vehicles,
            'metrics': metrics,
            'vehicle_metrics': vehicle_metrics,
            'unassigned_employees': len(unassigned),
            'unassigned_employee_ids': [emp['id'] for emp in unassigned] if unassigned else []
        }
        
        # Store results
        OPTIMIZATION_RESULTS['results'] = results
        OPTIMIZATION_RESULTS['optimized'] = True
        
        # Build message
        message = 'Optimization completed successfully'
        if unassigned:
            message += f' ({len(unassigned)} employees could not be assigned due to constraints)'
        
        return Response({
            'success': True,
            'message': message,
            'data': results
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': f'Error during optimization: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_results(request):
    """
    Retrieve optimization results.
    
    Returns:
    - success: Boolean
    - message: Status message
    - data: Optimization results
    """
    try:
        if not OPTIMIZATION_RESULTS.get('optimized'):
            return Response({
                'success': False,
                'message': 'No optimization results available. Please run optimization first.'
            }, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': 'Results retrieved successfully',
            'data': OPTIMIZATION_RESULTS['results']
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({
            'success': False,
            'message': f'Error retrieving results: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def health_check(request):
    """
    Health check endpoint.
    """
    return Response({
        'success': True,
        'message': 'Velora API is running',
        'version': '1.0.0'
    }, status=status.HTTP_200_OK)
