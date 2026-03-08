# Velora Optimization Engine - Technical Documentation

## Table of Contents
1. [Overview](#overview)
2. [Optimization Pipeline](#optimization-pipeline)
3. [Algorithm Details](#algorithm-details)
4. [Constraint System](#constraint-system)
5. [Data Structures](#data-structures)
6. [Code Architecture](#code-architecture)
7. [Performance & Complexity](#performance--complexity)
8. [API Flow](#api-flow)

---

## Overview

Velora uses a **multi-stage optimization pipeline** to solve the employee transportation problem. The system minimizes costs while respecting real-world constraints like vehicle capacity, time windows, and employee preferences.

### Problem Statement
Given:
- **N employees** with pickup/dropoff locations, time windows, priority levels, and preferences
- **M vehicles** with capacity, location, cost per km, and availability

Find:
- Optimal assignment of employees to vehicles
- Optimal routes for each vehicle
- Minimize total distance/cost while satisfying all constraints

### Solution Approach
**4-Stage Pipeline:**
1. **Assignment** - Insertion Heuristic calculating real-time marginal routing costs assigning employees to valid vehicle sequences.
2. **Routing** - Pre-computed assignments processed, falling back to Interleaved Nearest Neighbor routing.
3. **Improvement** - 2-opt search constrained by dynamic capacity/ETA tracking.
4. **Metrics** - Calculate costs, savings, and performance statistics.

---

## Optimization Pipeline

### Stage 1: Employee-to-Vehicle Assignment
**File:** `backend/optimizer/assignor.py`

**Algorithm:** Cost-Based Insertion Heuristic
```
1. Sort employees by priority (high → normal) then by time_window_start
2. For each employee (in sorted order):
   a. Initialize tracked minimum cost variable
   b. For each vehicle, simulate inserting pickup/dropoff at every possible indices (i, j)
   c. Validate sequence constraints (capacity bounds, sharing max, ETAs) dynamically
   d. Calculate absolute insertion cost = (added_distance * cost_per_km) + delay_penalty
   e. Record vehicle and exact optimal route sequence producing lowest cost
3. Asssign and lock optimal route map to vehicle tracking
```

**Key Function:** `assign_employees_to_vehicles()`

**Scoring Logic:**
- **Objective function:** Minimizing actual operating cost `score = (added_dist * vehicle_cost) + delay_penalty`
- Naturally prefers high capacity, high efficiency vehicles instead of raw naive closest proximity.

**Constraint Checks:**
- ✅ Vehicle capacity strictly met *concurrently* across route segment history
- ✅ Vehicle category matches employee preference (premium/normal)
- ✅ Employee's sharing preference constrained against concurrent active riders
- ✅ Time window ETA delays rigorously simulated for new points

---

### Stage 2: Route Generation
**File:** `backend/optimizer/router.py`

**Algorithm:** Dynamic Interleaved Nearest Neighbor

```python
def nearest_neighbor_route(vehicle, employees):
    """
    Build route by interleaving pickups and dropoffs based on nearest viable stop.
    """
    route = []
    # Track unpicked and currently seated passengers
    
    while unpicked_employees or in_vehicle:
        valid_next_points = []
        
        # Add unpicked employees to valid pool IF capacity allows
        if len(in_vehicle) < vehicle['capacity']:
            valid_next_points.append(pickups)
            
        # Dropoffs for in_vehicle are always valid
        valid_next_points.append(dropoffs)
        
        # nearest = min(valid_next_points)
        # Advance vehicle to nearest, update ETA and capacity tracking
        ...
```

**Why Dynamic Interleaved?**
- ✅ Resolves massive detours caused by the legacy 2-phase approach (pickup all -> dropoff all).
- ✅ Adapts efficiently when assignment sequences are unavailable.

**Route Structure:**
```
Vehicle Start → Pickup E1 → Drop E1 → Pickup E2 → Drop E2 → ...
or
Vehicle Start → Pickup E1 → Pickup E2 → Drop E1 → Drop E2
```

---

### Stage 3: Route Improvement
**File:** `backend/optimizer/improver.py`

**Algorithm:** Constrained 2-opt Local Search

The 2-opt algorithm improves routes by reversing segments to eliminate crossing paths, rigorously validated against dynamic time windows, structural capacities, and pickup order integrity at every single experimental shift.

```python
def two_opt_improve(route, vehicle):
    """
    Try all pairs of edges and reverse segments if it improves distance.
    """
    improved = True
    best_route = route.copy()
    
    while improved:
        improved = False
        for i in range(len(best_route) - 1):
            for j in range(i + 2, len(best_route)):
                if not is_valid_swap(best_route, i, j):
                    continue
                # Calculate distances and update if improved
                # Valid swaps must protect ETAs, Capacity bounds, and Dropoff Order.
```

**Example Visualization:**
```
Before 2-opt:
  A → B → C → D
  └─────┐ ┌───┘  (crossing paths)
        │ │
        
After 2-opt (reverse B-C):
  A → C → B → D
  └────────────┘  (no crossings)
```

**Improvement Potential:**
- Can reduce distance natively generated routes by 5-20% on average.
- Never accepts an improvement that creates illegal routing behavior or violates time tolerances.

---

### Stage 4: Metrics Calculation
**File:** `backend/optimizer/metrics.py`

**Cost Model:**
```python
Total Cost = Σ (Route Distance × Vehicle Cost Per Km)

Individual Cab Cost = Σ (Direct Distance × Assumed Cab Rate)

Savings = Individual Cab Cost - Total Cost
Savings % = (Savings / Individual Cab Cost) × 100

CO2 Reduction = Distance Saved × Emission Factor
```

**Key Metrics:**
1. **Total Distance** - Sum of all vehicle route distances
2. **Total Cost** - Vehicle operating costs
3. **Cost Savings** - Compared to individual cabs (₹15/km assumed)
4. **Savings Percentage** - Typically 40-60% for shared rides
5. **Vehicles Used** - Number of vehicles actually deployed
6. **Average Utilization** - % of vehicle capacity used
7. **CO2 Reduction** - Environmental impact (0.12 kg/km factor)

---

## Constraint System

**File:** `backend/optimizer/constraints.py`

### 1. Capacity Constraint
```python
def validate_route_capacity(route, vehicle_capacity):
    # Tracks concurrent occupancy via pickups and dropoffs
```
- **Hard constraint** - Never exceeded concurrently.
- Replaces naive vehicle-wide tracking with precise node-to-node evaluation.

### 2. Vehicle Category Preference
```python
def check_vehicle_category_preference(vehicle, employee):
    if employee['vehicle_preference'] == 'premium':
        return vehicle['category'] == 'premium'
    return True  # normal/any can use any vehicle
```
- **Hard constraint** - Premium seekers only get premium vehicles
- Normal/any preferences are flexible

### 3. Sharing Preference Constraint
```python
def validate_route_sharing(route):
    # Tracks concurrent riders dynamically along the route
```
- **Hard constraint** - Respects comfort dynamically.
- Evaluates preferences like "single" only against passengers physically inside the vehicle *at the exact moment* the "single" preference rider is onboard.

### 4. Time Window Constraint
```python
def check_time_window_feasibility(employee, pickup_eta):
    time_start = employee['time_window_start_min']
    time_end = employee['time_window_end_min']
    
    if pickup_eta < time_start:
        return True  # Early is OK
    
    # Late tolerance based on priority
    max_delay = 5 if employee['priority'] == 'high' else 15
    return pickup_eta <= (time_end + max_delay)
```
- **Strictly Evaluated** - Time windows are thoroughly simulated via exact ETAs. 
- Assignments resulting in delays outside tolerances immediately fail validation during Insertion / 2-Opt.

### 6. Vehicle Availability
```python
def check_vehicle_availability(vehicle, required_time):
    return required_time >= vehicle['available_from_min']
```
- **Hard constraint** - Vehicle must be ready
- Currently not enforced in assignment (all vehicles assumed available at routing time)

---

## Data Structures

### Employee Object
```python
{
    'id': 'E001',                      # Employee ID
    'priority': 'high',                # high|normal (converted from 1-5)
    'pickup_lat': 12.9716,             # Pickup latitude
    'pickup_lng': 77.5946,             # Pickup longitude
    'dest_lat': 12.9352,               # Destination latitude
    'dest_lng': 77.6245,               # Destination longitude
    'time_window_start': '08:00',     # Earliest pickup (HH:MM or HH:MM:SS)
    'time_window_end': '09:00',       # Latest arrival
    'time_window_start_min': 480,     # Minutes since midnight
    'time_window_end_min': 540,       # Minutes since midnight
    'vehicle_preference': 'normal',   # premium|normal|any
    'sharing_preference': 'triple'    # single|double|triple
}
```

### Vehicle Object
```python
{
    'id': 'V001',                      # Vehicle ID
    'fuel_type': 'diesel',             # petrol|diesel|electric
    'mode': 'sedan',                   # sedan|suv|van|4W|2W
    'capacity': 4,                     # Max passengers
    'cost_per_km': 8.0,                # Operating cost (₹/km)
    'avg_speed': 30.0,                 # Average speed (km/h)
    'current_lat': 12.9698,            # Current location
    'current_lng': 77.7499,
    'available_from': '07:00',         # Availability time
    'available_from_min': 420,         # Minutes since midnight
    'category': 'normal',              # premium|normal
    'assigned_employees': [],          # List of assigned employee objects
    'current_capacity_used': 0         # Running count
}
```

### Route Object (Output)
```python
{
    'vehicle_id': 'V001',
    'route': [                         # Ordered list of stops
        {
            'type': 'pickup',
            'employee_id': 'E001',
            'lat': 12.9716,
            'lng': 77.5946,
            'sequence': 0
        },
        {
            'type': 'dropoff',
            'employee_id': 'E001',
            'lat': 12.9352,
            'lng': 77.6245,
            'sequence': 1
        },
        # ... more stops
    ],
    'total_distance': 15.7,            # km
    'total_cost': 125.6,               # ₹
    'employees_served': 3
}
```

---

## Code Architecture

### Backend Structure
```
backend/
├── optimizer/
│   ├── utils.py           # Haversine distance, time parsing
│   ├── parser.py          # Excel file parsing with pandas
│   ├── constraints.py     # Constraint validation functions
│   ├── assignor.py        # Employee-to-vehicle assignment
│   ├── router.py          # Route generation (Nearest Neighbor)
│   ├── improver.py        # Route optimization (2-opt)
│   └── metrics.py         # Cost calculations and statistics
├── core/
│   ├── views.py           # REST API endpoints
│   └── urls.py            # URL routing
└── velora/
    ├── settings.py        # Django configuration
    └── urls.py            # Root URL config
```

### Key Algorithms

**Haversine Distance** (`utils.py`):
```python
def haversine(lat1, lng1, lat2, lng2):
    """Great circle distance between two GPS points."""
    R = 6371  # Earth radius in km
    φ1, φ2 = radians(lat1), radians(lat2)
    Δφ = radians(lat2 - lat1)
    Δλ = radians(lng2 - lng1)
    
    a = sin(Δφ/2)² + cos(φ1) × cos(φ2) × sin(Δλ/2)²
    c = 2 × atan2(√a, √(1-a))
    
    return R × c
```
- Accurate for short distances (<500 km)
- Average error: <0.5% for Bangalore city scale

**Time Parsing**:
```python
def parse_time(time_str):
    """Convert HH:MM or HH:MM:SS to minutes since midnight."""
    parts = time_str.split(':')
    hours = int(parts[0])
    minutes = int(parts[1])
    return hours * 60 + minutes
```

---

## Performance & Complexity

### Time Complexity

| Stage | Algorithm | Complexity | Typical Time |
|-------|-----------|------------|--------------|
| Assignment | Cost-Based Insertion | O(N × M × K²) | <200ms for N=20, M=8 |
| Routing | Dynamic Interleaved nearest | O(M × K²) | <50ms |
| Improvement | Constrained 2-opt | O(M × K³) | <300ms |
| Metrics | Distance calculation | O(M × K) | <10ms |
| **Total** | - | **O(N×M×K² + M×K³)** | **<600ms** |

Where:
- N = total employees
- M = total vehicles
- K = employees per vehicle ≈ N/M

### Space Complexity
- **O(N + M)** for data storage
- **O(M × K)** for route structures
- Memory usage: <5 MB for typical datasets (100 employees, 20 vehicles)

### Scalability

| Dataset Size | Performance | Notes |
|--------------|-------------|-------|
| 10-50 employees | <500ms | Instant results |
| 50-200 employees | 1-3 seconds | Hackathon scale ✅ |
| 200-1000 employees | 5-30 seconds | May need optimization |
| 1000+ employees | Minutes | Consider advanced algorithms |

**Optimization Suggestions for Scale:**
1. **Clustering** - Divide employees into geographic clusters, solve separately
2. **Parallel Processing** - Run 2-opt on vehicles in parallel
3. **Metaheuristics** - Simulated Annealing or Genetic Algorithms for large instances
4. **Approximations** - Limit 2-opt iterations, use distance matrices

---

## API Flow

### 1. Upload Files
**Endpoint:** `POST /api/upload/`

```
Frontend → Next.js API Route → Django Backend
          ↓
    Parse Excel Files
          ↓
    Validate Data
          ↓
    Store in Memory
          ↓
    Return Summary
```

**Request:**
```javascript
FormData {
  employees_file: File,
  vehicles_file: File
}
```

**Response:**
```json
{
  "success": true,
  "message": "Files uploaded successfully",
  "data": {
    "num_employees": 12,
    "num_vehicles": 5,
    "total_capacity": 17
  }
}
```

### 2. Run Optimization
**Endpoint:** `POST /api/optimize/`

```
Frontend → Next.js API Route → Django Backend
          ↓
    Load Data from Memory
          ↓
    Stage 1: Assignment (assignor.py)
          ↓
    Stage 2: Routing (router.py)
          ↓
    Stage 3: Improvement (improver.py)
          ↓
    Stage 4: Metrics (metrics.py)
          ↓
    Store Results
          ↓
    Return Routes & Metrics
```

**Response:**
```json
{
  "success": true,
  "message": "Optimization completed (5 employees could not be assigned)",
  "data": {
    "vehicles": [...],
    "metrics": {
      "total_distance": 45.3,
      "total_cost": 362.4,
      "individual_cost": 678.0,
      "savings": 315.6,
      "savings_percentage": 46.5,
      "co2_reduction": 5.43
    },
    "unassigned_employees": 5,
    "unassigned_employee_ids": ["E008", "E009", ...]
  }
}
```

### 3. View Results
**Endpoint:** `GET /api/results/`

Returns cached optimization results for dashboard visualization.

---

## Frontend Integration

### Data Flow
```
app/page.jsx (Upload & Optimize)
    ↓
app/api/upload/route.js (Proxy to Django)
app/api/optimize/route.js (Proxy to Django)
    ↓
app/dashboard/page.jsx (Results)
    ↓
components/MapView.jsx (Leaflet map with routes)
components/RoutePanel.jsx (Route details)
components/MetricsCard.jsx (Statistics)
```

### Map Visualization
**Library:** Leaflet.js + react-leaflet

**Features:**
- 🗺️ Interactive OpenStreetMap base layer
- 📍 Markers for vehicle start, pickups, dropoffs
- 🛣️ Colored polylines for each vehicle route
- 🎨 Color-coded by vehicle (up to 10 distinct colors)
- 🔍 Zoom/pan controls

**Route Display:**
```javascript
{routes.map((route, idx) => (
  <Polyline
    key={idx}
    positions={route.coordinates}
    color={ROUTE_COLORS[idx % 10]}
    weight={3}
  />
))}
```

---

## Excel File Format

### Employees File (employees.xlsx)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| employee_id | String | E001 | Unique employee ID |
| priority | Integer | 1-5 | 1-2=high, 3-5=normal |
| pickup_lat | Float | 12.9716 | Pickup latitude |
| pickup_lng | Float | 77.5946 | Pickup longitude |
| drop_lat | Float | 12.9352 | Destination latitude |
| drop_lng | Float | 77.6245 | Destination longitude |
| earliest_pickup | Time | 08:00:00 | HH:MM or HH:MM:SS |
| latest_drop | Time | 09:30:00 | HH:MM or HH:MM:SS |
| vehicle_preference | String | normal | premium/normal/any |
| sharing_preference | String | triple | single/double/triple |

### Vehicles File (vehicles.xlsx)

| Column | Type | Example | Description |
|--------|------|---------|-------------|
| vehicle_id | String | V001 | Unique vehicle ID |
| fuel_type | String | diesel | petrol/diesel/electric |
| vehicle_type | String | sedan | sedan/suv/van/4W/2W |
| capacity | Integer | 4 | Max passengers |
| cost_per_km | Float | 8.0 | Operating cost (₹/km) |
| avg_speed_kmph | Float | 30.0 | Average speed |
| current_lat | Float | 12.9698 | Current latitude |
| current_lng | Float | 77.7499 | Current longitude |
| available_from | Time | 07:00:00 | Availability time |
| category | String | normal | premium/normal |

---

## Algorithm Comparison

### Why Not Use Advanced Algorithms?

| Algorithm | Pros | Cons | Verdict |
|-----------|------|------|---------|
| **Nearest Neighbor** | Fast, simple, good enough | Not optimal | ✅ **Used** |
| **Dijkstra/A*** | Optimal single-source | Doesn't handle multi-stop TSP | ❌ Not applicable |
| **Genetic Algorithm** | Can find near-optimal | Slow, complex, needs tuning | ❌ Overkill for hackathon |
| **Simulated Annealing** | Good for large problems | Slow, non-deterministic | ❌ Unnecessary complexity |
| **Branch & Bound** | Optimal solution | Exponential time | ❌ Too slow |
| **2-opt** | Simple, effective improvement | Local optimum only | ✅ **Used** |
| **Lin-Kernighan** | Better than 2-opt | Complex implementation | ❌ Diminishing returns |

**Decision:** Nearest Neighbor + 2-opt provides **80% of optimal quality in 5% of implementation time**.

---

## Edge Cases Handled

### 1. Unassigned Employees
- **Cause:** Insufficient capacity, conflicting preferences, no premium vehicles
- **Handling:** Partial optimization proceeds, warning shown to user
- **Example:** 12 employees, 5 vehicles (capacity 17), but 5 want "single" ride → only 5 assigned

### 2. Empty Vehicles
- **Cause:** No employees match vehicle category or all employees already assigned
- **Handling:** Vehicle excluded from routes, not counted in utilization
- **Example:** Only premium vehicle but all employees prefer normal

### 3. Time Format Variations
- **Cause:** Excel exports times as HH:MM or HH:MM:SS
- **Handling:** Parser accepts both formats
- **Implementation:** `parse_time()` splits on ':' and ignores seconds

### 4. Missing Data
- **Cause:** Incomplete Excel files
- **Handling:** Validation fails early with clear error message
- **Example:** Missing `capacity` column → "Missing required columns: ['capacity']"

### 5. Invalid Coordinates
- **Cause:** Lat/Lng outside valid ranges or non-numeric
- **Handling:** pandas type coercion + try/except
- **Example:** Non-float values raise ValueError during parsing

---

## Future Enhancements

### Algorithm Improvements
1. **Dynamic Time Window Enforcement** - Actually use time constraints in assignment
2. **3-opt Optimization** - Better than 2-opt, more complex
3. **Insertion Heuristics** - Try inserting unassigned employees into existing routes
4. **Demand-Based Clustering** - Group employees by destination zones first

### Features
1. **Real-time Traffic** - Integrate with Google Maps API for actual travel times
2. **Multi-shift Support** - Handle morning + evening commutes together
3. **Driver Assignment** - Track which driver operates which vehicle
4. **Historical Analysis** - Learn patterns from past data
5. **Live Tracking** - Real-time vehicle location updates

### Performance
1. **Database Storage** - Replace in-memory storage with PostgreSQL
2. **Caching** - Redis for frequently accessed routes
3. **Async Processing** - Celery for background optimization tasks
4. **Batch Processing** - Handle 1000+ employees efficiently

---

## Testing Recommendations

### Unit Tests
```python
# test_haversine.py
def test_haversine_known_distance():
    # Bangalore Airport to MG Road ≈ 30 km
    dist = haversine(13.1988, 77.7067, 12.9759, 77.6061)
    assert 29 < dist < 31

# test_constraints.py
def test_capacity_constraint():
    vehicle = {'capacity': 4, 'current_capacity_used': 3}
    employee = {'id': 'E001'}
    assert check_capacity_constraint(vehicle, employee) == True
    
    vehicle['current_capacity_used'] = 4
    assert check_capacity_constraint(vehicle, employee) == False
```

### Integration Tests
```python
def test_full_optimization_pipeline():
    employees = load_test_employees()
    vehicles = load_test_vehicles()
    
    assignments, unassigned = assign_employees_to_vehicles(employees, vehicles)
    routes = generate_routes_for_all_vehicles(assignments, vehicles)
    improved = improve_all_routes(routes, vehicles)
    metrics = calculate_all_metrics(improved, vehicles, employees)
    
    assert metrics['total_distance'] > 0
    assert metrics['savings_percentage'] > 0
```

### Performance Tests
```python
import time

def test_optimization_speed():
    employees = generate_random_employees(100)
    vehicles = generate_random_vehicles(20)
    
    start = time.time()
    optimize_pipeline(employees, vehicles)
    duration = time.time() - start
    
    assert duration < 5.0  # Must complete in <5 seconds
```

---

## Deployment Checklist

- [ ] Set Django `DEBUG=False` for production
- [ ] Configure proper CORS origins (not wildcard `*`)
- [ ] Use environment variables for secrets
- [ ] Enable HTTPS/SSL certificates
- [ ] Set up PostgreSQL database (replace in-memory storage)
- [ ] Configure Redis for caching
- [ ] Set up logging and monitoring
- [ ] Add rate limiting to API endpoints
- [ ] Implement user authentication
- [ ] Create database backups
- [ ] Set up CI/CD pipeline
- [ ] Load test with realistic datasets

---

## References

### Academic Papers
- **Vehicle Routing Problem (VRP):** Toth & Vigo (2014) - "Vehicle Routing: Problems, Methods, and Applications"
- **2-opt Algorithm:** Croes (1958) - "A Method for Solving Traveling-Salesman Problems"
- **Nearest Neighbor Heuristic:** Rosenkrantz et al. (1977) - "Approximate Algorithms for TSP"

### Libraries Used
- **Django REST Framework:** https://www.django-rest-framework.org/
- **pandas:** https://pandas.pydata.org/
- **Next.js:** https://nextjs.org/
- **Leaflet.js:** https://leafletjs.com/
- **Tailwind CSS:** https://tailwindcss.com/

### Similar Problems
- **Dial-a-Ride Problem (DARP)** - On-demand transportation with pickups/dropoffs
- **School Bus Routing** - Similar multi-stop optimization
- **Ride-sharing Optimization** - Uber/Lyft route matching

---

## License & Credits

**Project:** Velora - Corporate Employee Transportation Optimizer  
**Created for:** Hackathon Project  
**Tech Stack:** Django + Next.js + Python Optimization Algorithms  
**Date:** February 2026  

**Algorithms Implemented:**
- Priority-First Greedy Assignment
- Nearest Neighbor Heuristic (TSP approximation)
- 2-opt Local Search
- Haversine Distance Calculation

---

*For questions or issues, refer to README.md and QUICKSTART.md for setup instructions.*
