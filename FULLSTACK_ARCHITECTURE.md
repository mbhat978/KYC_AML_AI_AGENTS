# Full-Stack KYC/AML System Architecture

## 📋 Table of Contents
1. [Overview](#overview)
2. [Current Folder Structure](#current-folder-structure)
3. [System Architecture](#system-architecture)
4. [Technology Stack](#technology-stack)
5. [Component Details](#component-details)
6. [Data Flow](#data-flow)
7. [API Endpoints](#api-endpoints)
8. [Database Schema](#database-schema)
9. [Configuration](#configuration)
10. [Security](#security)
11. [Development Setup](#development-setup)

---

## 📖 Overview

The KYC/AML AI Agents system is a full-stack intelligent compliance platform that uses multiple AI agents to process KYC documents and analyze transactions for anti-money laundering compliance. The system features real-time processing feedback, risk assessment, and automated decision-making with human-in-the-loop capabilities.

**Key Features:**
- Multi-agent AI workflow using LangGraph orchestration
- Real-time processing updates via Server-Sent Events (SSE)
- Document extraction (PDF, Images)
- Transaction monitoring and AML analysis
- Risk scoring and categorization (1-10 scale)
- Automated decision-making with escalation paths
- Comprehensive audit trail and history
- Interactive web interface with live agent feedback

---

## 📁 Current Folder Structure

```
AI-AGENTS/
├── backend/                          # FastAPI Backend Application
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                  # FastAPI app initialization
│   │   ├── database.py              # SQLAlchemy database setup
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── routes.py            # Main KYC processing endpoints
│   │   │   └── upload_routes.py     # File upload & management
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── kyc_service.py       # KYC orchestration wrapper
│   │   │   └── audit_service.py     # Audit logging service
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── schemas.py           # Pydantic API models
│   │   │   └── db_models.py         # SQLAlchemy ORM models
│   │   └── middleware/
│   │       ├── __init__.py
│   │       └── cors.py              # CORS configuration
│   ├── kyc_audit.db                 # SQLite database file
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                         # React + TypeScript Frontend
│   ├── public/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadZone.tsx       # Document upload interface
│   │   │   ├── EDDUploadZone.tsx    # Enhanced Due Diligence upload
│   │   │   ├── LiveFeed.tsx         # Real-time agent activity feed
│   │   │   ├── Dashboard.tsx        # Results & analytics dashboard
│   │   │   ├── RiskMeter.tsx        # Visual risk score indicator
│   │   │   └── AuditHistory.tsx     # Historical audit records
│   │   ├── services/
│   │   │   ├── api.ts               # Axios API client
│   │   │   └── sse.ts               # Server-Sent Events client
│   │   ├── types/
│   │   │   └── index.ts             # TypeScript type definitions
│   │   ├── assets/                  # Images and static assets
│   │   ├── App.tsx                  # Main application component
│   │   ├── main.tsx                 # React entry point
│   │   ├── App.css                  # Application styles
│   │   └── index.css                # Global styles (Tailwind)
│   ├── package.json
│   ├── vite.config.ts               # Vite build configuration
│   ├── tailwind.config.js           # Tailwind CSS config
│   ├── tsconfig.json                # TypeScript configuration
│   └── README.md
│
├── agents/                           # AI Agent Implementations
│   ├── __init__.py
│   ├── extraction_agent.py          # Document data extraction (GPT-4o)
│   ├── verification_agent.py        # Data validation & DB checks
│   ├── reasoning_agent.py           # Logical analysis & conclusions
│   ├── assessment_agent.py          # Risk scoring & categorization
│   ├── decision_agent.py            # Final decision making
│   └── transaction_agent.py         # AML transaction analysis
│
├── orchestrator/                     # Workflow Orchestration
│   ├── __init__.py
│   └── kyc_orchestrator.py          # LangGraph-based workflow coordinator
│
├── utils/                            # Utility Functions
│   ├── __init__.py
│   ├── llm_client.py                # OpenAI API client wrapper
│   ├── pdf_converter.py             # PDF processing utilities
│   └── validators.py                # Input validation functions
│
├── config/                           # Configuration Management
│   ├── __init__.py
│   └── settings.py                  # Environment & system settings
│
├── mock_data/                        # Mock External Databases
│   ├── government_db.json           # Simulated government records
│   ├── sanctions_list.json          # Sanctions lists
│   └── pep_list.json                # Politically Exposed Persons
│
├── samples/                          # Sample Test Documents
│   ├── image/                       # Sample ID images
│   ├── pdf/                         # Sample PDF documents
│   └── Transaction/                 # Sample transaction CSVs
│
├── main.py                           # CLI interface (legacy)
├── requirements.txt                  # Python dependencies
├── requirements-minimal.txt          # Minimal installation
├── run_app.bat                       # Windows startup script
├── run_app.sh                        # Unix startup script
├── .env.example                      # Environment template
├── .gitignore
├── README.md                         # Main project documentation
├── QUICK_START.md
├── INSTALLATION_GUIDE.md
├── TESTING_GUIDE.md
├── CONFIDENCE_SCORES_EXPLAINED.md
├── RISK_SAMPLES_GUIDE.md
└── FULLSTACK_ARCHITECTURE.md        # This file
```

---

## 🏗️ System Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                    Frontend (React + TypeScript)                     │
│  ┌─────────────────┐  ┌─────────────────┐  ┌───────────────────┐  │
│  │ Document Upload │  │ Processing View │  │ Results Dashboard │  │
│  │   & EDD Upload  │  │  (Real-time SSE)│  │   & Audit History │  │
│  └─────────────────┘  └─────────────────┘  └───────────────────┘  │
└────────────────┬────────────────────────────────────────────────────┘
                 │ HTTP/REST API + Server-Sent Events (SSE)
                 │ CORS: localhost:5173, localhost:3000
┌────────────────┴────────────────────────────────────────────────────┐
│                    Backend (FastAPI + Python 3.11+)                  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  API Layer (FastAPI)                                          │  │
│  │  - POST /api/kyc/upload          : Document upload            │  │
│  │  - POST /api/kyc/process         : Process KYC document       │  │
│  │  - GET  /api/kyc/stream/{id}     : SSE real-time updates      │  │
│  │  - POST /api/transaction/analyze : Analyze transactions       │  │
│  │  - GET  /api/audit/history       : Audit trail retrieval      │  │
│  │  - GET  /api/health              : Health check               │  │
│  │  - GET  /api/metrics             : System metrics             │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Services Layer                                               │  │
│  │  - KYC Service        : Orchestrator integration              │  │
│  │  - Audit Service      : Logging & audit trail management      │  │
│  │  - File Management    : Upload, storage, validation           │  │
│  └──────────────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Data Layer (SQLAlchemy + SQLite)                             │  │
│  │  - KYC Records        : Processing results & metadata         │  │
│  │  - Audit Logs         : Complete audit trail                  │  │
│  │  - Processing Status  : Workflow state management             │  │
│  └──────────────────────────────────────────────────────────────┘  │
└────────────────┬────────────────────────────────────────────────────┘
                 │ Direct Service Calls
┌────────────────┴────────────────────────────────────────────────────┐
│              KYC Orchestrator (LangGraph State Machine)              │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │  Workflow Coordination & State Management                     │  │
│  │  - Graph-based workflow execution                             │  │
│  │  - Sequential & conditional agent routing                     │  │
│  │  - State persistence & recovery                               │  │
│  │  - Human-in-the-loop decision points                          │  │
│  │  - Result aggregation & validation                            │  │
│  └──────────────────────────────────────────────────────────────┘  │
│                                                                       │
│  Workflow Nodes:                                                     │
│  extract → verify → [transactions?] → reason → assess → decide       │
│                              ↓                              ↓        │
│                    [transaction_agent]              [human_review]   │
└────────────────┬────────────────────────────────────────────────────┘
                 │ Agent Invocation (OpenAI API)
┌────────────────┴────────────────────────────────────────────────────┐
│                      AI Agents Layer (GPT-4o)                        │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Extraction Agent │  │Verification Agent│  │ Transaction Agent│ │
│  │                  │  │                  │  │                  │ │
│  │ • PDF/Image OCR  │  │ • DB Validation  │  │ • CSV Analysis   │ │
│  │ • Data Parsing   │  │ • Sanctions Chk  │  │ • Pattern Detect │ │
│  │ • Structured Out │  │ • PEP Screening  │  │ • AML Flags      │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │ Reasoning Agent  │  │ Assessment Agent │  │  Decision Agent  │ │
│  │                  │  │                  │  │                  │ │
│  │ • Logic Analysis │  │ • Risk Scoring   │  │ • Approve/Reject │ │
│  │ • Pattern Match  │  │ • Risk Category  │  │ • Confidence     │ │
│  │ • Conclusions    │  │ • Risk Factors   │  │ • Explanations   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
                 │
┌────────────────┴────────────────────────────────────────────────────┐
│                  External Dependencies & Utilities                   │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐ │
│  │   OpenAI API     │  │  Mock Databases  │  │  PDF Processing  │ │
│  │    (GPT-4o)      │  │  (JSON Files)    │  │  (PyMuPDF/PIL)   │ │
│  └──────────────────┘  └──────────────────┘  └──────────────────┘ │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🔧 Technology Stack

### Frontend Technologies
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | React | 18.3.1 | UI component library |
| **Language** | TypeScript | 5.6.2 | Type-safe JavaScript |
| **Build Tool** | Vite | 6.0.1 | Fast development & bundling |
| **Styling** | Tailwind CSS | 3.4.17 | Utility-first CSS framework |
| **HTTP Client** | Axios | 1.7.9 | API communication |
| **Real-time** | EventSource | Native | SSE connection for live updates |
| **State** | React Hooks | Built-in | Local state management |

### Backend Technologies
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **Framework** | FastAPI | Latest | High-performance async API framework |
| **Language** | Python | 3.11+ | Backend programming language |
| **ORM** | SQLAlchemy | Latest | Database ORM |
| **Database** | SQLite | 3.x | Embedded SQL database |
| **Validation** | Pydantic | Latest | Data validation and settings |
| **Logging** | Loguru | Latest | Enhanced logging |
| **CORS** | FastAPI Middleware | Built-in | Cross-origin resource sharing |
| **SSE** | starlette.responses | Built-in | Server-sent events for real-time |

### AI/ML Technologies
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| **LLM Provider** | OpenAI GPT-4o | Latest | Primary AI agent reasoning |
| **Orchestration** | LangGraph | Latest | Agent workflow state machine |
| **PDF Processing** | PyMuPDF (fitz) | Latest | PDF document parsing |
| **Image Processing** | Pillow (PIL) | Latest | Image manipulation and OCR |
| **CSV Processing** | Pandas | Latest | Transaction data analysis |

---

## 📦 Component Details

### 1. Frontend Components

**Location:** `frontend/src/components/`

#### UploadZone.tsx
- Drag-and-drop file upload interface
- File type validation (PDF, PNG, JPG, JPEG)
- File size validation
- Preview capabilities
- Integration with backend upload API

#### EDDUploadZone.tsx
- Enhanced Due Diligence document upload
- Transaction CSV file upload
- Multi-file support
- Validation and error handling

#### LiveFeed.tsx
- Real-time agent activity display
- SSE connection management
- Color-coded agent messages
- Auto-scrolling terminal-style output
- Workflow stage indicators

#### Dashboard.tsx
- Final decision display (Approve/Reject/Escalate)
- Risk metrics visualization
- Extracted data presentation
- Verification results
- Assessment details
- Confidence scores

#### RiskMeter.tsx
- Visual risk score representation (1-10 scale)
- Color-coded indicators:
  - Green: LOW (1.0-2.5)
  - Yellow: MEDIUM (2.5-5.0)
  - Orange: HIGH (5.0-7.5)
  - Red: CRITICAL (7.5-10.0)
- Animated transitions

#### AuditHistory.tsx
- Historical KYC processing records
- Searchable and filterable
- Detailed audit trail
- Export capabilities

### 2. Backend API

**Location:** `backend/app/`

#### Main Application (main.py)
- FastAPI initialization
- CORS configuration
- Router registration
- Database initialization
- Startup/shutdown events
- Health check endpoints

#### Routes (api/routes.py)
- **POST /api/kyc/process**: Main KYC processing endpoint
- **GET /api/kyc/stream/{session_id}**: SSE streaming endpoint
- **GET /api/kyc/result/{session_id}**: Get processing results
- **POST /api/kyc/resume**: Resume interrupted workflow
- **GET /api/metrics**: System performance metrics

#### Upload Routes (api/upload_routes.py)
- **POST /api/upload**: File upload endpoint
- **GET /api/upload/samples**: List sample documents
- **GET /api/upload/{filename}**: Retrieve uploaded file

#### KYC Service (services/kyc_service.py)
- Wrapper around KYC Orchestrator
- Session management
- Error handling and recovery
- Result formatting

#### Audit Service (services/audit_service.py)
- Audit log creation and management
- Historical record retrieval
- Compliance trail maintenance

### 3. KYC Orchestrator

**Location:** `orchestrator/kyc_orchestrator.py`

#### LangGraph Workflow
The orchestrator uses LangGraph to create a state machine with the following nodes:

1. **extract_node**: Calls ExtractionAgent
2. **verify_node**: Calls VerificationAgent
3. **analyze_transactions_node**: Calls TransactionAgent (conditional)
4. **reason_node**: Calls ReasoningAgent
5. **assess_node**: Calls AssessmentAgent
6. **decide_node**: Calls DecisionAgent
7. **human_review_node**: Human-in-the-loop decision point

#### Conditional Routing
- After verification: Routes to transaction analysis if transaction data present
- After decision: Routes to human review if confidence < threshold or risk is high

#### State Management
- Maintains complete workflow state
- Enables workflow resumption
- Tracks all agent outputs
- Aggregates results

### 4. AI Agents

**Location:** `agents/`

#### ExtractionAgent
- **Input**: Document (PDF/Image with base64 data)
- **Process**: Uses GPT-4o vision to extract structured data
- **Output**: Extracted fields (name, DOB, ID numbers, etc.)

#### VerificationAgent
- **Input**: Extracted data
- **Process**: 
  - Validates against government database
  - Checks sanctions lists
  - Screens PEP lists
  - Validates data consistency
- **Output**: Verification results with flags

#### TransactionAgent
- **Input**: Transaction CSV data
- **Process**: Analyzes patterns for AML flags
- **Output**: AML risk indicators and patterns

#### ReasoningAgent
- **Input**: Extraction + Verification + Transaction results
- **Process**: Logical analysis and pattern matching
- **Output**: Conclusions and reasoning

#### AssessmentAgent
- **Input**: Reasoning + Verification results
- **Process**: 
  - Calculates risk score (1-10 scale)
  - Categorizes risk (LOW/MEDIUM/HIGH/CRITICAL)
  - Identifies risk factors
- **Output**: Risk assessment

#### DecisionAgent
- **Input**: Assessment + Reasoning results
- **Process**: Makes final decision based on thresholds
- **Output**: Decision (APPROVE/REJECT/ESCALATE) with explanation

---

## 🔄 Data Flow

### Complete Processing Pipeline

```
1. User uploads document → Frontend (UploadZone)
   ↓
2. POST /api/kyc/process → Backend API
   ↓
3. Generate session_id → Return to frontend
   ↓
4. Frontend opens SSE connection → GET /api/kyc/stream/{session_id}
   ↓
5. Backend invokes KYCOrchestrator.process_document()
   ↓
6. Orchestrator executes workflow:
   │
   ├─→ ExtractionAgent extracts data
   │   └─→ SSE: "Extraction complete"
   │
   ├─→ VerificationAgent validates
   │   └─→ SSE: "Verification complete"
   │
   ├─→ [Optional] TransactionAgent analyzes
   │   └─→ SSE: "Transaction analysis complete"
   │
   ├─→ ReasoningAgent analyzes
   │   └─→ SSE: "Reasoning complete"
   │
   ├─→ AssessmentAgent scores risk
   │   └─→ SSE: "Assessment complete"
   │
   ├─→ DecisionAgent makes final call
   │   └─→ SSE: "Decision complete"
   │
   └─→ [Optional] HumanReviewNode if needed
   ↓
7. Results stored in database
   ↓
8. Final result sent via SSE
   ↓
9. Frontend displays results in Dashboard
```

---

## 🔌 API Endpoints

### KYC Processing Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/kyc/process` | Process KYC document | `{document: {type, data}}` | `{session_id, status}` |
| GET | `/api/kyc/stream/{id}` | SSE stream | - | SSE events stream |
| GET | `/api/kyc/result/{id}` | Get results | - | Complete processing result |
| POST | `/api/kyc/resume` | Resume workflow | `{thread_id, decision}` | Updated result |

### Upload Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/upload` | Upload file | FormData | `{filename, path}` |
| GET | `/api/upload/samples` | List samples | - | Array of sample files |

### Transaction Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| POST | `/api/transaction/analyze` | Analyze transactions | `{csv_data}` | AML analysis result |

### System Endpoints

| Method | Endpoint | Description | Request | Response |
|--------|----------|-------------|---------|----------|
| GET | `/api/health` | Health check | - | `{status, service, agents}` |
| GET | `/api/metrics` | System metrics | - | Performance metrics |
| GET | `/api/audit/history` | Audit history | Query params | Audit records |

---

## 🗄️ Database Schema

### KYCRecord Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| session_id | String | Unique session identifier |
| document_type | String | Type of document processed |
| extracted_data | JSON | Extracted information |
| verification_result | JSON | Verification outcomes |
| risk_score | Float | Risk score (1-10) |
| risk_category | String | LOW/MEDIUM/HIGH/CRITICAL |
| decision | String | APPROVE/REJECT/ESCALATE |
| confidence | Float | Decision confidence (0-1) |
| created_at | DateTime | Processing timestamp |
| updated_at | DateTime | Last update timestamp |

### AuditLog Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| session_id | String | Related session |
| agent | String | Agent name |
| action | String | Action performed |
| input_data | JSON | Agent input |
| output_data | JSON | Agent output |
| timestamp | DateTime | Action timestamp |
| duration | Float | Processing time (seconds) |

---

## ⚙️ Configuration

### Environment Variables (.env)

```bash
# LLM Configuration
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-4o

# Alternative LLM (optional)
ANTHROPIC_API_KEY=your_anthropic_key
ANTHROPIC_MODEL=claude-3-opus-20240229
DEFAULT_LLM_PROVIDER=openai

# Application Settings
ENVIRONMENT=development
LOG_LEVEL=INFO

# Risk Thresholds (1-10 scale)
LOW_RISK_THRESHOLD=3.0
MEDIUM_RISK_THRESHOLD=6.0
HIGH_RISK_THRESHOLD=8.0

# Decision Thresholds
AUTO_APPROVE_THRESHOLD=3.0
AUTO_REJECT_THRESHOLD=8.0
CONFIDENCE_THRESHOLD=0.85

# Feature Flags
USE_MOCK_DATABASES=true
ENABLE_EXPLAINABILITY=true
ENABLE_AUDIT_TRAIL=true
STRICT_MODE=false
```

### Risk Score Scale

- **1.0 - 3.0**: LOW (Auto-approve eligible)
- **2.5 - 6.5**: MEDIUM (Review recommended)
- **6.5 - 8.0**: HIGH (Enhanced due diligence)
- **8.0 - 10.0**: CRITICAL (Auto-reject or escalate)

---

## 🔒 Security

### Data Security
- File validation and sanitization
- Secure temporary file storage
- SQL injection prevention (ORM)
- Input validation (Pydantic)

### API Security
- CORS configuration for allowed origins
- Rate limiting (recommended for production)
- API authentication (to be implemented)
- HTTPS in production

### Privacy & Compliance
- PII data handling
- Audit trail for compliance
- Data retention policies
- GDPR considerations

---

## 🚀 Development Setup

### Prerequisites
- Python 3.11+
- Node.js 18+
- OpenAI API key

### Backend Setup
```bash
# Navigate to backend
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Unix/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variable
# Create .env file with OPENAI_API_KEY

# Run server
uvicorn app.main:app --reload --port 8000
```

### Frontend Setup
```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Run development server
npm run dev
```

### Using Startup Scripts
```bash
# Windows
run_app.bat

# Unix/Mac
./run_app.sh
```

---

## 📚 Additional Documentation

- **README.md**: Project overview and quick start
- **INSTALLATION_GUIDE.md**: Detailed installation instructions
- **TESTING_GUIDE.md**: Testing procedures and examples
- **CONFIDENCE_SCORES_EXPLAINED.md**: Understanding confidence metrics
- **RISK_SAMPLES_GUIDE.md**: Sample documents and expected outcomes

---

**Last Updated**: March 31, 2026  
**Version**: 1.0.0  
**Repository**: https://github.ibm.com/Manisha-Bhattacharjee/KYC-AML-Multi-Agentic-AI-System.git