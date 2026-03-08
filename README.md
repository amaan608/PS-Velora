# Velora - Employee Transportation Optimization System

**Velora** is a comprehensive corporate employee transportation optimization system built for hackathons. It uses AI-powered routing algorithms to minimize costs, optimize routes, and improve efficiency for employee commutes.

## 🚀 Features

- **Smart Route Optimization**: Advanced Insertion Heuristics with interleaved dynamic Nearest Neighbor and 2-opt search processing.
- **Cost Savings**: Reduce total transportation expenses by optimizing for comprehensive operational factors rather than simple distance.
- **Priority-Based Assignment**: High-priority employees get preferential treatment with stricter dynamic time window constraints.
- **Concurrent Constraint Validation**: Respects precise vehicle capacity, concurrent sharing preferences dynamically on route interleaving, and real-time ETAs.
- **Interactive Dashboard**: Real-time map visualization with route polylines and detailed metrics.
- **Pure Python Implementation**: No third-party optimization APIs - all algorithms built from scratch.

## 🛠️ Tech Stack

### Backend
- **Django 4.2** + **Django REST Framework** - API server
- **pandas** + **openpyxl** - Excel file processing
- **Pure Python** - All optimization algorithms (no OR-Tools, no Google APIs)

### Frontend
- **Next.js 14** (App Router) - React framework
- **Tailwind CSS** - Styling
- **Leaflet.js** + **react-leaflet** - Interactive maps
- **Dynamic routing** - Client-side navigation

## 📁 Project Structure

```
velora/
├── backend/
│   ├── velora/              # Django project settings
│   │   ├── settings.py      # CORS, REST framework config
│   │   ├── urls.py          # Root URL routing
│   │   └── ...
│   ├── core/                # API app
│   │   ├── views.py         # Upload, optimize, results endpoints
│   │   └── urls.py          # API URL patterns
│   ├── optimizer/           # Optimization engine (standalone module)
│   │   ├── utils.py         # Haversine distance calculation
│   │   ├── parser.py        # Excel file parsing
│   │   ├── constraints.py   # Constraint validation logic
│   │   ├── assignor.py      # Employee-to-vehicle assignment
│   │   ├── router.py        # Route generation (Nearest Neighbor)
│   │   ├── improver.py      # Route improvement (2-opt algorithm)
│   │   └── metrics.py       # Cost, savings, time calculations
│   ├── manage.py
│   └── requirements.txt
├── frontend/
│   ├── app/
│   │   ├── api/             # Next.js API proxy routes
│   │   │   ├── upload/      # File upload endpoint
│   │   │   └── optimize/    # Optimization endpoint
│   │   ├── dashboard/       # Results dashboard page
│   │   ├── page.jsx         # Landing page
│   │   └── layout.jsx       # Root layout
│   ├── components/
│   │   ├── FileUpload.jsx   # Excel file upload UI
│   │   ├── MapView.jsx      # Leaflet map with routes
│   │   ├── RoutePanel.jsx   # Vehicle assignment panel
│   │   └── MetricsCard.jsx  # Cost savings dashboard
│   ├── package.json
│   └── tailwind.config.js
└── sample_data/
    ├── generate_sample_data.py  # Sample data generator
    ├── employees.xlsx           # Sample employee data (20 employees)
    └── vehicles.xlsx            # Sample vehicle data (8 vehicles)
```

## 🧮 Optimization Approach

### 1. Employee-to-Vehicle Assignment
- **Cost-Based Insertion Heuristic**
- High-priority and earliest scheduled employees processed first.
- Simulates exact routing scenarios to insert pickups and dropoffs precisely into available valid route configurations.
- Selects assignment producing lowest marginal cost: `(added_dist * cost_per_km) + delay_penalty`.
- Strongly enforced concurrent constraint checking built-in via time-window simulation.

### 2. Route Generation
- **Dynamic Interleaved Nearest Neighbor Approach**
- Processes predefined sequences sourced from the optimal assignment insertion.
- When generating fallbacks, interleaves unpicked employee pickups against dropoffs dynamically evaluating capacity thresholds in real-time.

### 3. Route Improvement
- **Constrained 2-opt algorithm**
- Iteratively swaps route segments to reduce total distance.
- Strictly validates experimental segment loops against capacities, sharing limits, and priority time windows using precise simulated ETAs to preserve validity.
- Converges to tight local optimums preserving route legality.

### 4. Metrics Calculation
- **Optimized cost** = Σ(distance × cost_per_km) for all vehicles
- **Baseline cost** = Σ(direct_distance × ₹15/km) for individual cabs
- **Savings** = Baseline - Optimized
- **Time calculation** using average vehicle speed

## 📋 Input Data Format

### Employees Excel File (employees.xlsx)
| Column | Type | Description |
|--------|------|-------------|
| id | string | Employee ID (e.g., "E001") |
| priority | string | "high" or "normal" |
| pickup_lat | float | Pickup latitude |
| pickup_lng | float | Pickup longitude |
| dest_lat | float | Destination latitude |
| dest_lng | float | Destination longitude |
| time_window_start | string | Start time "HH:MM" |
| time_window_end | string | End time "HH:MM" |
| vehicle_preference | string | "premium" or "normal" |
| sharing_preference | string | "single", "double", or "triple" |

### Vehicles Excel File (vehicles.xlsx)
| Column | Type | Description |
|--------|------|-------------|
| id | string | Vehicle ID (e.g., "V001") |
| fuel_type | string | "petrol", "diesel", or "electric" |
| mode | string | "sedan", "suv", or "van" |
| capacity | int | Maximum passengers |
| cost_per_km | float | Operating cost per km (₹) |
| avg_speed | float | Average speed (km/h) |
| avg_mileage | float | Fuel efficiency (km/l or km/kWh) |
| vehicle_age | float | Age in years |
| current_lat | float | Current latitude |
| current_lng | float | Current longitude |
| available_from | string | Availability time "HH:MM" |

## 🚦 Getting Started

### Prerequisites
- **Python 3.8+**
- **Node.js 18+**
- **npm** or **yarn**

### Backend Setup

1. **Navigate to backend directory**
   ```bash
   cd backend
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux/Mac
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**
   ```bash
   python manage.py migrate
   ```

5. **Start Django server**
   ```bash
   python manage.py runserver
   ```
   Backend will run at `http://localhost:8000`

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install dependencies**
   ```bash
   npm install
   # or
   yarn install
   ```

3. **Start Next.js development server**
   ```bash
   npm run dev
   # or
   yarn dev
   ```
   Frontend will run at `http://localhost:3000`

### Generate Sample Data (Optional)

1. **Navigate to sample_data directory**
   ```bash
   cd sample_data
   ```

2. **Run data generator**
   ```bash
   python generate_sample_data.py
   ```
   This creates `employees.xlsx` and `vehicles.xlsx` with 20 employees and 8 vehicles using realistic Bangalore coordinates.

## 📊 API Endpoints

### Backend (Django)
- `POST /api/upload/` - Upload employee and vehicle Excel files
- `POST /api/optimize/` - Run optimization algorithm
- `GET /api/results/` - Retrieve optimization results
- `GET /api/health/` - Health check

### Frontend (Next.js Proxy)
- `POST /api/upload` - Proxy to Django upload endpoint
- `POST /api/optimize` - Proxy to Django optimize endpoint
- `GET /api/optimize` - Proxy to Django results endpoint

## 🎯 Constraints & Rules

### Hard Constraints (Must Satisfy)
1. **Capacity**: Vehicle capacity cannot be exceeded
2. **Sharing Preference**:
   - `single`: Employee must be alone in vehicle
   - `double`: Maximum 2 people including employee
   - `triple`: Maximum 3 people including employee
3. **Pickup Before Dropoff**: Each employee must be picked up before being dropped off
4. **Vehicle Availability**: Vehicle must be available at required time

### Soft Constraints (Penalty-Based)
1. **Time Windows**:
   - **High Priority**: Max 5 minutes late (heavy penalty)
   - **Normal Priority**: Max 15 minutes late (light penalty)

## 🎨 UI Features

- **File Upload**: Drag-and-drop Excel file upload with validation
- **Interactive Map**: Leaflet-based map with:
  - Blue markers for pickups
  - Red markers for dropoffs
  - Colored polylines for each vehicle route
  - Toggle controls for markers
  - Vehicle legend
- **Metrics Dashboard**:
  - Optimized vs baseline cost comparison
  - Total savings (absolute + percentage)
  - Distance and time metrics
  - Vehicle utilization stats
- **Route Panel**: Expandable vehicle cards with:
  - Assigned employee list
  - Timeline view of pickups and dropoffs
  - Distance and time per vehicle
- **Vehicle Performance Table**: Detailed per-vehicle metrics

## 🔧 Development Notes

### Testing the System

1. Start both backend and frontend servers
2. Open `http://localhost:3000` in browser
3. Upload `sample_data/employees.xlsx` and `sample_data/vehicles.xlsx`
4. Click "Run Optimization"
5. View results on dashboard with map, routes, and metrics

### Customizing the Algorithm

- **Assignment logic**: Modify `backend/optimizer/assignor.py`
- **Routing algorithm**: Modify `backend/optimizer/router.py`
- **Route improvement**: Modify `backend/optimizer/improver.py`
- **Constraints**: Modify `backend/optimizer/constraints.py`
- **Cost calculations**: Modify `backend/optimizer/metrics.py`

## 📦 Production Deployment

### Backend
- Use production-grade WSGI server (Gunicorn, uWSGI)
- Configure production database (PostgreSQL recommended)
- Set `DEBUG=False` in settings.py
- Configure proper CORS origins
- Use environment variables for secrets

### Frontend
- Build optimized production bundle: `npm run build`
- Deploy to Vercel, Netlify, or similar
- Set `NEXT_PUBLIC_BACKEND_URL` environment variable

## 🏆 Key Differentiators

1. **No Third-Party APIs**: All optimization logic built from scratch in Python
2. **Standalone Optimizer**: `optimizer/` module has zero Django dependencies - can be used independently
3. **Production-Ready**: Complete error handling, validation, and user feedback
4. **Hackathon-Optimized**: Fast to understand, easy to extend, well-documented

## 📝 License

This project is built for hackathon purposes. Feel free to use and modify as needed.

## 👥 Support

For questions or issues, please refer to the code comments or create an issue in the repository.

---

**Built with ❤️ using pure Python algorithms and modern web technologies**
