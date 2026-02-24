# Velora - Quick Start Guide

## Fast Setup (5 minutes)

### 1. Backend Setup
```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # Linux/Mac
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```
Backend runs at: http://localhost:8000

### 2. Frontend Setup (New Terminal)
```bash
cd frontend
npm install
npm run dev
```
Frontend runs at: http://localhost:3000

### 3. Generate Sample Data (New Terminal)
```bash
cd sample_data
python generate_sample_data.py
```
Creates employees.xlsx and vehicles.xlsx

### 4. Test the System
1. Open http://localhost:3000
2. Upload both Excel files from sample_data/
3. Click "Run Optimization"
4. View results dashboard

## Common Issues

**Missing pandas/openpyxl error:**
```bash
pip install pandas openpyxl
```

**Port already in use:**
- Backend: `python manage.py runserver 8001`
- Frontend: Change port in package.json or use `npm run dev -- -p 3001`

**CORS errors:**
- Ensure backend is running
- Check NEXT_PUBLIC_BACKEND_URL in frontend/.env.local

## Project Structure Summary

```
backend/
  optimizer/     → All optimization algorithms (standalone)
  core/          → REST API views and URLs
  velora/        → Django settings and configuration

frontend/
  app/           → Next.js pages and API routes
  components/    → React components (Map, Routes, Metrics)

sample_data/     → Sample Excel files and generator
```

## API Flow

1. Upload files → POST /api/upload/
2. Run optimization → POST /api/optimize/
3. Get results → GET /api/results/

All frontend calls go through Next.js proxy at /api/*

## Optimization Algorithm

1. **Assign**: Priority-first greedy (assignor.py)
2. **Route**: Nearest Neighbor (router.py)
3. **Improve**: 2-opt algorithm (improver.py)
4. **Calculate**: Costs, savings, metrics (metrics.py)

## Customization Tips

- Modify constraints: backend/optimizer/constraints.py
- Change assignment scoring: backend/optimizer/assignor.py
- Adjust map colors: frontend/components/MapView.jsx
- Update metrics cards: frontend/components/MetricsCard.jsx

## Success Criteria

✓ Files upload successfully
✓ Optimization completes without errors
✓ Map shows route polylines
✓ Metrics show cost savings
✓ All vehicles have assigned employees

Happy hacking! 🚀
