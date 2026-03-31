# Multi-Agent KYC/AML System

A production-ready, intelligent KYC/AML compliance system powered by multi-agent AI architecture. This system demonstrates true reasoning capabilities, not just sequential automation.

## 🎯 Team Members
- **Name**: Manisha Bhattacharjee
- **IBM Email ID**: Manisha.Bhattacharjee@ibm.com

## 🎯 Overview

This system implements an **Agentic AI approach** where multiple specialized agents collaborate, reason, and make intelligent decisions about identity verification and AML compliance. The agents can loop back, re-verify, and escalate based on their analysis—thinking like compliance officers, not just executing a pipeline.

## 🏗️ Architecture

- **FULLSTACK_ARCHITECTURE.md**: Project Folder Structure, Technology Stack and Architecture Explained

### Key Features

- ✅ **StateGraph Implementation**: Multi-agent AI workflow using LangGraph orchestration
- ✅ **Agent Live Feed**: Real-time processing updates via Server-Sent Events (SSE)
- ✅ **OCR Capabilities**: Document extraction (PDF, Images)
- ✅ **KYC**: Identity Verification
- ✅ **Enhanced Due Diligence**: Transaction monitoring and AML analysis
- ✅ **Human-In-Loop**: Automated decision-making with escalation paths
- ✅ **Modern Web Interface**: Interactive web interface with live agent feedback
- ✅ **Cyclic Reasoning**: Agents can loop back for additional verification
- ✅ **Intelligent Conflict Resolution**: Handles typos, variations, and mismatches
- ✅ **Explainable AI**: Comprehensive audit trail and history for every decision
- ✅ **Multi-Source Verification**: Cross-references multiple databases
- ✅ **Dynamic Risk Scoring**: Context-aware assessment, Risk scoring and categorization (1-10 scale)

## 🚀 Getting Started

### Prerequisites

- Python 3.11+
- OpenAI or Anthropic API key

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd KYC-AML-Multi-Agentic-AI-System

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Set up environment variables
cp .env.example .env
# Edit .env and add your API keys
```

### Usage

```bash
# Run the system with a mock document
python main.py --document samples/image/pan_card/pan_card_clean_1

# Or use the interactive mode
python main.py --interactive
```
### Running Tests

```bash
pytest tests/
```

## 🎓 How It Works

The system follows an agentic workflow:

1. **Extract**: Parse document and extract structured data
2. **Verify**: Cross-check against multiple sources
3. **Transactions Verify**: Analyze Transaction CSV if any and checkes for AML flags
3. **Reason**: Analyze discrepancies and decide if re-verification needed
4. **Assess**: Assign dynamic risk scores
5. **Decide**: Make final decision with full explainability

The key innovation is the **reasoning loop**: if mismatches are found, the system autonomously decides whether to query additional sources, adjust confidence scores, or escalate to human review.

## 🔒 Compliance & Security

- All decisions include complete audit trails
- PII handling follows best practices
- Explainable AI for regulatory compliance
- Configurable risk thresholds


## Component Descriptions

### 1. User Interface Layer
- **React Frontend**: Modern web interface built with Vite and TypeScript for document upload and result visualization

### 2. API Layer
- **FastAPI Backend**: RESTful API handling HTTP requests
- **main.py**: Application entry point that coordinates requests

### 3. Orchestration Layer
- **KYC Orchestrator**: Central coordinator that manages the workflow between all AI agents and ensures proper sequencing

### 4. AI Agents Layer
All agents communicate with OpenAI API through the LLM Client:

- **Extraction Agent**: Extracts structured data from documents (ID cards, passports, etc.)
- **Verification Agent**: Validates extracted data against external sources
- **Assessment Agent**: Performs risk assessment and compliance checks
- **Reasoning Agent**: Provides logical analysis and decision support
- **Transaction Agent**: Analyzes transaction patterns for AML compliance
- **Decision Agent**: Makes final KYC/AML approval decisions

### 5. Utility Layer
- **LLM Client**: Centralized interface for all OpenAI API communications
  - Manages API keys and configuration
  - Handles rate limiting and retries
  - Provides structured prompting
  - Parses JSON responses
- **PDF Converter**: Converts PDF documents to processable formats
- **Validators**: Data validation and sanitization utilities

### 6. External Services
- **OpenAI API**: GPT-4 and Vision models for AI-powered analysis

### 7. Data Layer
- **Configuration**: System settings and API credentials
- **Mock Data**: Government databases, PEP lists, sanctions lists for verification
- **Database**: SQLite database for audit trail and results storage
- **File Storage**: Sample documents for testing and processing

## Data Flow Summary

1. **User → Frontend → API**: User uploads documents through React UI
2. **API → Orchestrator**: Request is routed to KYC Orchestrator
3. **Orchestrator → Agents**: Sequential/parallel agent execution
4. **Agents → LLM Client → OpenAI**: Each agent makes structured API calls
5. **OpenAI → LLM Client → Agents**: AI responses are parsed and returned
6. **Agents → Orchestrator**: Results are aggregated
7. **Orchestrator → API → Frontend → User**: Final decision and analysis presented to user

## Key Design Patterns

- **Orchestration Pattern**: Central orchestrator coordinates multi-agent workflow
- **Agent Pattern**: Specialized agents handle specific KYC/AML tasks
- **Adapter Pattern**: LLM Client abstracts OpenAI API interactions
- **Repository Pattern**: Database layer for audit storage
- **Configuration Pattern**: Centralized settings management

## Technology Stack

- **Frontend**: React, TypeScript, Vite
- **Backend**: Python, FastAPI
- **AI**: OpenAI GPT-4/Vision API
- **Database**: SQLite
- **Document Processing**: PDF processing utilities
- **Configuration**: Environment-based settings

## 🤝 Contributing

Contributions welcome!

---

Built with ❤️ by Principal AI Engineers
