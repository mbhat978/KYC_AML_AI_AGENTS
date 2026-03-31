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
python main.py --document samples/image/pan_card/pan_card_clean_1

# Or use the interactive mode
python main.py --interactive
```

## 🎓 How It Works

The system follows an agentic workflow:

1. **Extract**: Parse document and extract structured data
2. **Verify**: Cross-check against multiple sources
3. **Transaction Verify**: Analyze Transaction CSV if any and checkes for AML flags
3. **Reason**: Analyze discrepancies and decide if re-verification needed
4. **Assess**: Assign dynamic risk scores
5. **Decide**: Make final decision with full explainability

The key innovation is the **reasoning loop**: if mismatches are found, the system autonomously decides whether to query additional sources, adjust confidence scores, or escalate to human review.

## 🔒 Compliance & Security

- All decisions include complete audit trails
- PII handling follows best practices
- Explainable AI for regulatory compliance
- Configurable risk thresholds

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
