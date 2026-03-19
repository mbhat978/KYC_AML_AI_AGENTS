# Testing Guide - Multi-Agent KYC/AML System

This guide provides step-by-step instructions for testing the complete full-stack application.

## 🚀 Quick Start

### Option 1: Automated Launch (Recommended)

#### Windows:
```cmd
run_app.bat
```

#### Linux/Mac:
```bash
chmod +x run_app.sh
./run_app.sh
```

### Option 2: Manual Launch

#### Terminal 1 - Backend:
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate
# Linux/Mac: source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

#### Terminal 2 - Frontend:
```bash
cd frontend
npm install
npm run dev
```

## 🧪 Test Scenarios

### Test 1: System Health Check

1. Open browser to http://localhost:8000/docs
2. Try the `/health` endpoint
3. Expected: `{"status": "healthy"}`

### Test 2: Upload Sample PAN Card

1. Open http://localhost:5173
2. Click "🪪 PAN Card" button
3. **Expected Results:**
   - File loaded confirmation
   - Processing starts automatically
   - Live Feed shows agent activities
   - Risk Meter displays score and category
   - Dashboard shows final decision

### Test 3: Upload Sample Passport

1. Click "🛂 Passport" button
2. **Expected Results:**
   - Different risk profile than PAN Card
   - All agents process sequentially
   - Final decision rendered

### Test 4: Drag-and-Drop Custom JSON

1. Create a custom JSON file with KYC data
2. Drag and drop onto upload zone
3. **Expected Results:**
   - Custom document processed
   - Risk assessment based on provided data

## 📊 What to Observe

### Live Feed Should Show:
- ▶️ Agent Start events
- 💭 Reasoning steps
- 🔍 Verification checks
- 📊 Assessment calculations
- ⚖️ Decision making
- ✅ Agent End events

### Risk Meter Should Display:
- Animated circular progress
- Color-coded categories (Low/Medium/High/Critical)

### Dashboard Should Show:
- Decision (APPROVE/REJECT/ESCALATE)
- Explanation and recommendations
- Extracted data summary
- Expandable audit trail

## 🐛 Troubleshooting

### Backend Won't Start
```bash
cd backend
pip install -r requirements.txt --upgrade
```

### Frontend Won't Start
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
```

### No Live Updates
- Check backend is running on port 8000
- Verify CORS is enabled
- Check browser console for errors

## ✅ Success Criteria

All tests pass if you see:
- ✅ Both servers start without errors
- ✅ Sample documents load successfully
- ✅ Real-time updates appear in Live Feed
- ✅ Risk Meter animates correctly
- ✅ Dashboard displays final decision
- ✅ No CORS or connection errors