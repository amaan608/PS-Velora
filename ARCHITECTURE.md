# Velora System Architecture

## Data Flow

```
┌─────────────────────────────────────────────────────────────────┐
│                         USER BROWSER                             │
│                     (http://localhost:3000)                      │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                    NEXT.JS FRONTEND                              │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ Landing Page │  │  Dashboard   │  │   API Proxy  │          │
│  │  (Upload UI) │  │  (Results)   │  │   Routes     │          │
│  └──────────────┘  └──────────────┘  └──────┬───────┘          │
│         │                  ▲                  │                   │
│         │                  │                  │                   │
│  ┌──────▼──────────────────┴──────────────┐  │                   │
│  │         React Components                 │  │                   │
│  │  • FileUpload  • MapView                │  │                   │
│  │  • RoutePanel  • MetricsCard            │  │                   │
│  └──────────────────────────────────────────┘  │                   │
└────────────────────────────────────────────┬───┘                   │
                                             │                       │
                                             ▼                       │
┌─────────────────────────────────────────────────────────────────┐
│                   DJANGO BACKEND                                 │
│                 (http://localhost:8000)                          │
│                                                                  │
│  ┌─────────────────────────────────────────────────────┐       │
│  │              REST API (core/views.py)                │       │
│  │  POST /api/upload/    → Upload Excel files          │       │
│  │  POST /api/optimize/  → Run optimization            │       │
│  │  GET  /api/results/   → Retrieve results            │       │
│  └──────────────────┬──────────────────────────────────┘       │
│                     │                                            │
│                     ▼                                            │
│  ┌─────────────────────────────────────────────────────┐       │
│  │        OPTIMIZER MODULE (100% Pure Python)          │       │
│  │                                                       │       │
│  │  1. parser.py      → Read Excel (pandas)            │       │
│  │  2. assignor.py    → Assign employees to vehicles   │       │
│  │  3. router.py      → Generate routes (NN Heuristic) │       │
│  │  4. improver.py    → Optimize routes (2-opt)        │       │
│  │  5. metrics.py     → Calculate costs & savings      │       │
│  │  6. constraints.py → Validate all constraints       │       │
│  │  7. utils.py       → Haversine distance             │       │
│  └─────────────────────────────────────────────────────┘       │
└──────────────────────────────────────────────────────────────────┘
```

## Optimization Algorithm Flow

```
Excel Files
    │
    ▼
┌─────────────────────────────────────┐
│   1. PARSE & VALIDATE               │
│   • Read employees.xlsx             │
│   • Read vehicles.xlsx              │
│   • Validate data integrity         │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│   2. ASSIGN EMPLOYEES TO VEHICLES   │
│   • Sort by priority (high first)   │
│   • Greedy assignment algorithm     │
│   • Check constraints:              │
│     - Capacity                      │
│     - Sharing preferences           │
│     - Time windows                  │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│   3. GENERATE INITIAL ROUTES        │
│   • Nearest Neighbor Heuristic      │
│   • Phase 1: Pick up all employees  │
│   •   (nearest-first from current)  │
│   • Phase 2: Drop off all employees │
│   •   (nearest-first from last)     │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│   4. IMPROVE ROUTES                 │
│   • 2-opt algorithm                 │
│   • Swap route segments             │
│   • Reduce total distance           │
│   • Maintain pickup→dropoff order   │
└───────────────┬─────────────────────┘
                │
                ▼
┌─────────────────────────────────────┐
│   5. CALCULATE METRICS              │
│   • Optimized cost (Σ dist × cost) │
│   • Baseline cost (individual cabs) │
│   • Savings (absolute & %)          │
│   • Total distance & time           │
└───────────────┬─────────────────────┘
                │
                ▼
            JSON Results
```

## Component Hierarchy

```
App Layout
│
├── Landing Page (/)
│   ├── Hero Section
│   ├── Features Grid
│   ├── FileUpload Component
│   │   ├── Employee File Input
│   │   └── Vehicle File Input
│   ├── Optimize Button
│   └── How It Works Section
│
└── Dashboard (/dashboard)
    ├── Header with Navigation
    ├── MetricsCard Component
    │   ├── Cost Metrics Grid
    │   └── Savings Summary
    ├── MapView Component (Leaflet)
    │   ├── Map Container
    │   ├── Route Polylines (colored per vehicle)
    │   ├── Pickup Markers (blue)
    │   ├── Dropoff Markers (red)
    │   └── Controls & Legend
    └── RoutePanel Component
        └── Vehicle Cards (expandable)
            ├── Employee List
            ├── Route Timeline
            └── Vehicle Stats
```

## Key Files by Purpose

### Optimization Logic
- `backend/optimizer/assignor.py` - Who rides which vehicle?
- `backend/optimizer/router.py` - What route does each vehicle take?
- `backend/optimizer/improver.py` - How can we make routes better?
- `backend/optimizer/metrics.py` - How much are we saving?

### API & Data
- `backend/core/views.py` - Handle HTTP requests
- `backend/optimizer/parser.py` - Read Excel files
- `backend/optimizer/constraints.py` - Validate rules

### Frontend UI
- `frontend/app/page.jsx` - Upload interface
- `frontend/app/dashboard/page.jsx` - Results display
- `frontend/components/MapView.jsx` - Visual routes
- `frontend/components/MetricsCard.jsx` - Cost savings

## Constraint Priority

```
HARD CONSTRAINTS (Must satisfy)
├── Vehicle capacity cannot be exceeded
├── Sharing preferences must be honored
│   ├── single = alone
│   ├── double = max 2 people
│   └── triple = max 3 people
└── Pickup must come before dropoff

SOFT CONSTRAINTS (Penalized)
└── Time window violations
    ├── High priority: max 5 min delay
    └── Normal priority: max 15 min delay
```

## Technology Choices Explained

**Why Django?** - Fast REST API setup, great for data processing

**Why Next.js?** - Server-side rendering, built-in API routes, excellent DX

**Why Leaflet?** - Open-source, no API keys needed, lightweight

**Why pandas?** - Excel processing made simple, data manipulation tools

**Why pure Python?** - No external dependencies, full control, hackathon rules

**Why 2-opt?** - Fast local optimization, easy to implement, good results

**Why Nearest Neighbor?** - Simple, fast, creates reasonable initial routes

## Performance Characteristics

- **Assignment**: O(n × m) where n = employees, m = vehicles
- **Initial Routing**: O(n²) per vehicle
- **2-opt Improvement**: O(n² × iterations) per vehicle
- **Total Optimization**: ~2-5 seconds for 20 employees, 8 vehicles

## Scalability Considerations

**Current Scale**: 20-50 employees, 5-10 vehicles (~5 seconds)

**Medium Scale**: 100-200 employees, 20-30 vehicles (~30 seconds)
- Consider parallel processing per vehicle
- Limit 2-opt iterations

**Large Scale**: 500+ employees, 50+ vehicles
- Need more advanced algorithms (genetic, simulated annealing)
- Database-backed state management
- Background job queue (Celery)
- Caching optimization results

---

This architecture prioritizes:
✓ Simplicity over complexity
✓ Pure Python over external APIs
✓ Modularity over monoliths
✓ Hackathon speed over enterprise scale
