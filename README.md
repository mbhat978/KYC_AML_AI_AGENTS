# Multi-Agent KYC/AML System

A production-ready, intelligent KYC/AML compliance system powered by multi-agent AI architecture. This system demonstrates true reasoning capabilities, not just sequential automation.

## 🎯 Overview

This system implements an **Agentic AI approach** where multiple specialized agents collaborate, reason, and make intelligent decisions about identity verification and AML compliance. The agents can loop back, re-verify, and escalate based on their analysis—thinking like compliance officers, not just executing a pipeline.

## 🏗️ Architecture

### Core Agents

1. **Extraction Agent**: Intelligent document understanding and data extraction
2. **Verification Agent**: Multi-source verification orchestration
3. **Risk & Reasoning Agent**: Conflict resolution and intelligent analysis
4. **Assessment Agent**: Context-aware risk scoring
5. **Decision Agent**: Smart escalation with explainability

### Key Features

- ✅ **Cyclic Reasoning**: Agents can loop back for additional verification
- ✅ **Intelligent Conflict Resolution**: Handles typos, variations, and mismatches
- ✅ **Explainable AI**: Complete audit trail for every decision
- ✅ **Multi-Source Verification**: Cross-references multiple databases
- ✅ **Dynamic Risk Scoring**: Context-aware assessment

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- OpenAI or Anthropic API key

### Installation

```bash
# Clone the repository
git clone <repo-url>
cd AI-AGENTS

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
python main.py --document samples/pan_card.json

# Or use the interactive mode
python main.py --interactive
```

## 📁 Project Structure

```
AI-AGENTS/
├── agents/                 # Individual agent implementations
│   ├── extraction_agent.py
│   ├── verification_agent.py
│   ├── reasoning_agent.py
│   ├── assessment_agent.py
│   └── decision_agent.py
├── orchestrator/          # LangGraph orchestration
│   └── graph.py
├── mock_data/             # Mock databases and documents
│   ├── government_db.json
│   ├── sanctions_list.json
│   └── pep_list.json
├── samples/               # Sample documents for testing
│   ├── pan_card.json
│   ├── passport.json
│   └── drivers_license.json
├── utils/                 # Utility functions
│   ├── llm_client.py
│   └── validators.py
├── config/               # Configuration
│   └── settings.py
├── main.py               # Entry point
├── requirements.txt
├── .env.example
└── README.md
```

## 🎓 How It Works

The system follows an agentic workflow:

1. **Extract**: Parse document and extract structured data
2. **Verify**: Cross-check against multiple sources
3. **Reason**: Analyze discrepancies and decide if re-verification needed
4. **Assess**: Assign dynamic risk scores
5. **Decide**: Make final decision with full explainability

The key innovation is the **reasoning loop**: if mismatches are found, the system autonomously decides whether to query additional sources, adjust confidence scores, or escalate to human review.

## 🔒 Compliance & Security

- All decisions include complete audit trails
- PII handling follows best practices
- Explainable AI for regulatory compliance
- Configurable risk thresholds

## 📊 Example Output

```json
{
  "decision": "ESCALATE",
  "risk_score": "MEDIUM",
  "confidence": 0.72,
  "reasoning": [
    "Name mismatch detected: 'Jon Doe' vs 'Jonathan Doe'",
    "Queried 2 additional sources for verification",
    "Address partially verified",
    "No sanctions/PEP flags found"
  ],
  "recommendation": "Manual review recommended due to name variation",
  "audit_trail": "..."
}
```

## 🛠️ Development

### Running Tests

```bash
pytest tests/
```

### Adding New Agents

See `docs/adding_agents.md` for guidelines on extending the system.

## 📝 License

MIT License

## 🤝 Contributing

Contributions welcome! Please read CONTRIBUTING.md first.

---

Built with ❤️ by Principal AI Engineers
