# KYC/AML Multi-Agent System Architecture

## System Architecture Diagram

```mermaid
graph TB
    User[User] --> Frontend[React Frontend]
    Frontend --> API[FastAPI Backend]
    API --> Orchestrator[KYC Orchestrator]
    Orchestrator --> Agent1[Extraction Agent]
    Agent1 --> Agent2[Verification Agent]
    Agent2 --> Agent3[Transaction Agent]
    Agent3 --> Agent4[Reasoning Agent]
    Agent4 --> Agent5[Assessment Agent]
    Agent5 --> Agent6[Decision Agent]
    Agent1 & Agent2 & Agent3 & Agent4 & Agent5 & Agent6 --> LLM[LLM Client]
    LLM --> OpenAI[OpenAI GPT-4o]
    OpenAI --> LLM
    Agent2 --> GovDB[Government DB]
    Agent2 --> Sanctions[Sanctions List]
    Agent2 --> PEP[PEP Database]
    Agent6 --> Orchestrator
    Orchestrator --> API
    API --> Frontend
    Frontend --> User
```
```mermaid
flowchart LR
    %% Modern Color Palette
    classDef user fill:#6366f1,stroke:#4f46e5,stroke-width:2px,color:#fff
    classDef frontend fill:#3b82f6,stroke:#2563eb,stroke-width:2px,color:#fff
    classDef backend fill:#10b981,stroke:#059669,stroke-width:2px,color:#fff
    classDef orchestrator fill:#f59e0b,stroke:#d97706,stroke-width:2px,color:#fff
    classDef agent fill:#8b5cf6,stroke:#6d28d9,stroke-width:2px,color:#fff
    classDef external fill:#ef4444,stroke:#dc2626,stroke-width:2px,color:#fff
    classDef db fill:#64748b,stroke:#475569,stroke-width:2px,color:#fff

    %% Nodes and Subgraphs
    User([👤 Compliance Officer]):::user

    subgraph "Presentation Layer"
        UI[⚛️ React + Vite UI]:::frontend
    end

    subgraph "Application Layer"
        API[⚡ FastAPI Gateway]:::backend
        Audit[📝 Audit Service]:::backend
    end

    subgraph "AI & Orchestration Layer (LangGraph)"
        Orch{🧠 KYC Orchestrator}:::orchestrator
        
        %% Agents
        Ext[📄 Extraction Agent]:::agent
        Ver[✅ Verification Agent]:::agent
        Trx[💰 Transaction Agent]:::agent
        Rea[🤔 Reasoning Agent]:::agent
        Ass[📊 Assessment Agent]:::agent
        Dec[⚖️ Decision Agent]:::agent
    end

    subgraph "Data & Integrations"
        LLM[🤖 OpenAI / Vision]:::external
        Mock[(External Watchlists)]:::db
        SQL[(SQLite Audit DB)]:::db
    end

    %% Execution Flow
    User -->|Uploads EDD| UI
    UI -->|Multipart POST| API
    API -->|SSE Live Updates| UI
    
    API -->|Triggers StateGraph| Orch
    Orch -->|Data Extraction| Ext
    Orch -->|Data Verify| Ver
    Orch -->|Check Transaction| Trx
    Orch -->|Analyze Logic| Rea
    Orch -->|Risk Analysis| Ass 
    Orch -->|Final Verdict| Dec
    
    %% Agent Dependencies
    Ext & Ver & Ass & Trx & Rea & Dec <-->|API Calls| LLM
    Ver <-->|Validate| Mock
    
    %% Audit Flow
    Orch -->|Log Immutable State| Audit
    Audit -->|Commit| SQL

    %% Styling configurations
    linkStyle default stroke:#94a3b8,stroke-width:2px,color:#475569
```

## Data Flow

**User to OpenAI API and Back**

1. User uploads document via React frontend
2. Frontend sends HTTP POST to FastAPI
3. API initializes KYC Orchestrator
4. Orchestrator executes LangGraph workflow
5. Six agents process sequentially
6. Each agent calls OpenAI GPT-4o via LLM Client
7. Verification queries external databases
8. OpenAI returns structured JSON
9. Results stream back via SSE
10. Frontend displays real-time updates

## Technology Stack

- Frontend: React, TypeScript, Vite
- API: FastAPI, Python, SSE
- Orchestration: LangGraph, LangChain
- LLM: OpenAI GPT-4o
- Database: SQLite
- Agents: 6 specialized agents

## Key Features

- Real-time SSE streaming
- Human-in-the-Loop (HITL)
- State checkpointing
- Audit trail
- Vision API support
- Structured output validation
