# Quick Start Guide - Multi-Agent KYC/AML System

## ⚠️ PYTHON 3.12 COMPATIBILITY FIX

If you're using **Python 3.12** and encountered the error:
```
TypeError: ForwardRef._evaluate() missing 1 required keyword-only argument: 'recursive_guard'
```

**This has been FIXED!** The requirements.txt now uses Python 3.12-compatible versions.

## 🚀 Installation (Choose One Option)

### Option 1: Fresh Install (Recommended)

```bash
# Remove old virtual environment
rmdir /s /q venv  # Windows
rm -rf venv       # Linux/Mac

# Create new virtual environment
python -m venv venv

# Activate it
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Upgrade pip
pip install --upgrade pip

# Install with FIXED requirements
pip install -r requirements.txt
```

### Option 2: Use Python 3.11 Instead

If you prefer to use Python 3.11:

```bash
# Install Python 3.11 if needed, then:
python3.11 -m venv venv
venv\Scripts\activate
pip install -r requirements-py311.txt
```

### Option 3: Minimal Installation (No LLM)

If you just want to test without LLM dependencies:

```bash
pip install -r requirements-minimal.txt
```

## 📋 Quick Test

After installation, test immediately:

```bash
# Test imports
python -c "from agents import ExtractionAgent; print('✅ Agents OK')"
python -c "from orchestrator import KYCOrchestrator; print('✅ Orchestrator OK')"

# Run the system
python main.py
```

## 🎯 Expected Output

You should see:

```
============================================================
Starting KYC/AML processing
============================================================

[STEP 1] EXTRACTION
Extracted: Rajesh Kumar Sharma - ABCDE1234F

[STEP 2] VERIFICATION
Verification Status: VERIFIED

[STEP 3] REASONING
Conclusion: ACCEPT
Confidence: 0.95

[STEP 4] ASSESSMENT
Risk: LOW (0.20)

[STEP 5] DECISION
Final Decision: APPROVE
```

## 🔧 Still Having Issues?

### Issue: Import Errors After Fix

```bash
# Clean Python cache
python -c "import sys; import shutil; [shutil.rmtree(p/'__pycache__', ignore_errors=True) for p in [Path('.'), *Path('.').rglob('*')] if (p/'__pycache__').exists()]"

# Or manually delete all __pycache__ directories
```

### Issue: Pydantic Version Conflicts

```bash
# Force reinstall pydantic
pip uninstall pydantic pydantic-core pydantic-settings -y
pip install pydantic==2.8.0 pydantic-settings==2.3.0
```

### Issue: LangChain Import Errors

```bash
# Reinstall langchain packages
pip uninstall langchain langchain-core langchain-openai -y
pip install langchain==0.2.0 langchain-core==0.2.0 langchain-openai==0.1.8
```

## ✅ Verification Steps

Run these to verify everything works:

```bash
# 1. Check Python version
python --version
# Should show 3.12.x or 3.11.x

# 2. Check pydantic
python -c "import pydantic; print(f'Pydantic: {pydantic.VERSION}')"
# Should show 2.8.x or higher for Python 3.12

# 3. Check langchain
python -c "import langchain; print('LangChain: OK')"

# 4. Check all imports
python -c "from agents import *; from orchestrator import *; print('All imports: OK')"

# 5. Run the system
python main.py
```

## 🎉 Success!

If all checks pass, you're ready to use the system:

```bash
# Process different documents
python main.py --document samples/pan_card.json
python main.py --document samples/passport.json
python main.py --document samples/drivers_license.json

# Interactive mode
python main.py --interactive

# Save results
python main.py --output results.json
```

## 📖 More Information

- See **INSTALLATION_GUIDE.md** for detailed setup
- See **PROJECT_SUMMARY.md** for architecture details
- See **README.md** for project overview

---

**Note**: The system works without API keys for testing because sample documents already have extracted fields!