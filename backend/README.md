# KYC/AML Backend API

FastAPI backend with Server-Sent Events (SSE) for real-time agent streaming.

## 🚀 Quick Start

```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

## 📡 API Endpoints

### POST /api/kyc/process
Initiate KYC document processing

### GET /api/kyc/stream/{session_id}  
Stream real-time processing events via SSE

### GET /api/kyc/status/{session_id}
Get processing status

### GET /api/health
Health check

### GET /api/docs
Swagger documentation

## 🧪 Test the API

```bash
# Health check
curl http://localhost:8000/api/health

# Process document
curl -X POST http://localhost:8000/api/kyc/process \
  -H "Content-Type: application/json" \
  -d '{"document_type":"PAN","extracted_fields":{"name":"Test","id_number":"ABC123"}}'

# Connect to SSE stream
curl http://localhost:8000/api/kyc/stream/{session_id}
```

##  Real-Time Streaming

The backend streams agent events via SSE:
- 🚀 System initialization
- 📄 Extraction progress
- 🔍 Verification checks
- 🧠 Reasoning analysis
- 📊 Risk assessment
- ⚖️ Final decision

## 🏗️ Structure

```
backend/
├── app/
│   ├── main.py              # FastAPI app
│   ├── api/routes.py        # API endpoints
│   ├── services/kyc_service.py  # KYC orchestrator wrapper
│   ├── models/schemas.py    # Pydantic models
│   └── middleware/cors.py   # CORS config
└── requirements.txt
```

## ✅ Step 1 Complete!

Backend is ready with SSE streaming. Next: React frontend!