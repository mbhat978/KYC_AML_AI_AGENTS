# Full-Stack KYC/AML System Architecture

## 📁 Proposed Folder Structure

```
AI-AGENTS/
├── backend/                          # FastAPI Backend
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app initialization
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # API endpoints
│   │   │   └── websocket.py         # WebSocket/SSE handlers
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   └── kyc_service.py       # Orchestrator wrapper
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   └── schemas.py           # Pydantic models for API
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── cors.py              # CORS configuration
│   ├── requirements.txt             # Backend-specific requirements
│   └── README.md
│
├── frontend/                         # React + Vite Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.tsx      # Drag-and-drop upload
│   │   │   ├── LiveFeed.tsx        # Real-time agent logs
│   │   │   ├── Dashboard.tsx       # Results display
│   │   │   └── RiskMeter.tsx       # Visual risk indicator
│   │   ├── services/
│   │   │   ├── api.ts              # API client
│   │   │   └── websocket.ts        # WebSocket client
│   │   ├── types/
│   │   │   └── index.ts            # TypeScript types
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   └── tsconfig.json
│
├── agents/                           # Core Agent Logic (UNCHANGED)
│   ├── __init__.py
│   ├── extraction_agent.py
│   ├── verification_agent.py
│   ├── reasoning_agent.py
│   ├── assessment_agent.py
│   └── decision_agent.py
│
├── orchestrator/                     # Core Orchestrator (UNCHANGED)
│   ├── __init__.py
│   └── kyc_orchestrator.py
│
├── utils/                            # Core Utils (UNCHANGED)
│   ├── __init__.py
│   ├── llm_client.py
│   └── validators.py
│
├── config/                           # Core Config (UNCHANGED)
│   ├── __init__.py
│   └── settings.py
│
├── mock_data/                        # Mock Databases (UNCHANGED)
│   ├── government_db.json
│   ├── sanctions_list.json
│   └── pep_list.json
│
├── samples/                          # Sample Documents (UNCHANGED)
│   ├── pan_card.json
│   ├── passport.json
│   └── drivers_license.json
│
├── scripts/                          # Helper Scripts
│   ├── start_dev.py                 # Start both backend & frontend
│   ├── start_dev.bat                # Windows version
│   └── start_dev.sh                 # Linux/Mac version
│
├── main.py                           # Original CLI (kept for reference)
├── requirements.txt                  # Root requirements
├── requirements-minimal.txt
├── .env.example
├── .gitignore
└── README.md
```

## 🎯 Architecture Overview

### Backend (FastAPI)

**Technology Stack:**
- FastAPI for REST API
- Server-Sent Events (SSE) for real-time streaming
- Pydantic for data validation
- AsyncIO for non-blocking operations

**Key Features:**
1. **POST /api/kyc/process** - Main processing endpoint
2. **GET /api/kyc/stream/{session_id}** - SSE endpoint for real-time logs
3. **WebSocket /ws/kyc** - Alternative WebSocket connection
4. **GET /api/health** - Health check endpoint
5. **GET /api/documents** - List sample documents

**Real-Time Streaming:**
- Each agent emits events during processing
- Events are streamed via SSE to the frontend
- Format: `{agent: "ExtractionAgent", status: "processing", message: "..."}`

### Frontend (React + Vite + Tailwind)

**Technology Stack:**
- React 18 with TypeScript
- Vite for fast dev server
- Tailwind CSS for styling
- Axios for HTTP requests
- EventSource for SSE connection

**Components:**

1. **UploadZone** 📤
   - Drag-and-drop interface
   - File validation
   - Preview uploaded document
   - Select from sample documents

2. **LiveFeed** 📡
   - Terminal-style scrolling output
   - Color-coded by agent type
   - Real-time updates via SSE
   - Auto-scroll to latest

3. **Dashboard** 📊
   - Final decision badge (Approve/Reject/Escalate)
   - Risk score meter (0-100)
   - Risk category indicator
   - Confidence percentage
   - Explainable AI section

4. **RiskMeter** 🎯
   - Visual gauge/progress bar
   - Color-coded (green/yellow/red)
   - Animated transitions

### Integration

**CORS Configuration:**
```python
origins = [
    "http://localhost:5173",  # Vite default
    "http://localhost:3000",  # Alternative
    "http://127.0.0.1:5173",
]
```

**API Communication:**
```typescript
// Upload document
POST http://localhost:8000/api/kyc/process

// Stream events
GET http://localhost:8000/api/kyc/stream/{sessionId}
```

### Development Workflow

```bash
# Start both servers
python scripts/start_dev.py

# Or manually:
# Terminal 1: Backend
cd backend
uvicorn app.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend
npm run dev
```

## 🔄 Data Flow

1. **User uploads document** → Frontend
2. **POST /api/kyc/process** → Backend receives document
3. **Generate session_id** → Backend creates unique ID
4. **Return session_id** → Frontend receives ID
5. **Connect to SSE** → Frontend opens `/api/kyc/stream/{sessionId}`
6. **Process document** → Backend runs KYCOrchestrator
7. **Stream events** → Each agent emits progress events
8. **Update UI** → Frontend displays real-time logs
9. **Final result** → Dashboard shows decision

## 🎨 UI Design Principles

- **Clean & Professional**: Corporate compliance aesthetic
- **Real-time Feedback**: Users see agents "thinking"
- **Data Visualization**: Charts, meters, badges
- **Responsive**: Works on desktop and tablet
- **Accessible**: Proper ARIA labels, keyboard navigation

## 🔒 Security Considerations

- CORS properly configured
- Input validation on both frontend and backend
- File size limits
- Rate limiting (future)
- API authentication (future)

---

**Ready to proceed with implementation?**