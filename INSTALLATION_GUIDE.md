# Installation Guide - Multi-Agent KYC/AML System

Complete installation and setup guide for the full-stack Multi-Agent KYC/AML System.

## 📋 Prerequisites

### Required Software:
1. **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
2. **Node.js 18+** - [Download Node.js](https://nodejs.org/)
3. **Git** - [Download Git](https://git-scm.com/downloads)

### Optional (but recommended):
- **VS Code** - [Download VS Code](https://code.visualstudio.com/)
- **Postman** or **cURL** for API testing

### API Keys (Required):
- **OpenAI API Key** or compatible LLM API key

---

## 🚀 Quick Installation (Recommended)

### Step 1: Clone the Repository
```bash
git clone <repository-url>
cd AI-AGENTS
```

### Step 2: Configure Environment
```bash
# Copy the environment template
cp .env.example .env

# Edit .env and add your API keys
# Windows: notepad .env
# Linux/Mac: nano .env
```

Add your API keys:
```env
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here  # Optional
```

### Step 3: Launch the Application

#### Windows:
```cmd
run_app.bat
```

#### Linux/Mac:
```bash
chmod +x run_app.sh
./run_app.sh
```

**That's it!** The script will:
- ✅ Check for Python and Node.js
- ✅ Create virtual environment (if needed)
- ✅ Install all dependencies
- ✅ Start both backend and frontend servers

### Step 4: Access the Application
- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

---

## 🔧 Manual Installation

If you prefer manual setup or the automated scripts don't work:

### Backend Setup

#### 1. Navigate to Backend Directory
```bash
cd backend
```

#### 2. Create Virtual Environment
**Windows:**
```cmd
python -m venv venv
venv\Scripts\activate
```

**Linux/Mac:**
```bash
python3 -m venv venv
source venv/bin/activate
```

#### 3. Install Backend Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

#### 4. Configure Environment Variables
```bash
# From the root directory
cp .env.example .env
```

Edit `.env` and add your API keys.

#### 5. Start Backend Server
```bash
# Make sure you're in the backend directory
uvicorn app.main:app --reload --port 8000
```

The backend will be available at: http://localhost:8000

### Frontend Setup

#### 1. Navigate to Frontend Directory
```bash
# Open a NEW terminal window
cd frontend
```

#### 2. Install Frontend Dependencies
```bash
npm install
```

#### 3. Start Frontend Development Server
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

---

## 📦 Dependencies

### Backend (Python)
- **FastAPI** - Web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation
- **OpenAI** - LLM integration
- **Python-dotenv** - Environment management
- **SSE-Starlette** - Server-Sent Events support

### Frontend (Node.js)
- **React 18** - UI library
- **TypeScript** - Type safety
- **Vite** - Build tool
- **Tailwind CSS** - Styling
- **ESLint** - Code linting

---

## 🔍 Verification Steps

### 1. Check Backend Health
```bash
curl http://localhost:8000/api/health
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-18T..."
}
```

### 2. Check API Documentation
Open in browser: http://localhost:8000/docs

You should see the interactive Swagger UI.

### 3. Check Frontend
Open in browser: http://localhost:5173

You should see the KYC/AML System UI with:
- 🛡️ Header with system title
- 📤 Upload zone with sample document buttons
- Modern gradient background

### 4. Test End-to-End
1. Click "🪪 PAN Card" button
2. Watch the Live Feed for real-time agent activities
3. See the Risk Meter update with score
4. View the final decision in the Dashboard

---

## 🐛 Troubleshooting

### Backend Issues

#### Issue: ModuleNotFoundError
**Problem**: Missing Python dependencies

**Solution**:
```bash
cd backend
pip install -r requirements.txt --upgrade
```

#### Issue: Port 8000 already in use
**Problem**: Another process is using port 8000

**Solution**:
```bash
# Find and kill the process (Windows)
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Find and kill the process (Linux/Mac)
lsof -ti:8000 | xargs kill -9

# Or use a different port
uvicorn app.main:app --reload --port 8001
```

#### Issue: OPENAI_API_KEY not found
**Problem**: Environment variables not loaded

**Solution**:
```bash
# Make sure .env file exists in root directory
# Check if it contains: OPENAI_API_KEY=your_key_here
# Restart the backend server
```

### Frontend Issues

#### Issue: npm install fails
**Problem**: Node.js version or network issues

**Solution**:
```bash
# Check Node.js version
node --version  # Should be 18+

# Clear npm cache and retry
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

#### Issue: Port 5173 already in use
**Problem**: Another Vite instance is running

**Solution**:
```bash
# Kill the process (Windows)
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Kill the process (Linux/Mac)
lsof -ti:5173 | xargs kill -9

# Or configure Vite to use different port in vite.config.ts
```

#### Issue: CORS errors in browser console
**Problem**: Backend CORS not configured

**Solution**:
Check `backend/app/middleware/cors.py` includes:
```python
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173"
]
```

Restart backend server.

### SSE Connection Issues

#### Issue: No real-time updates
**Problem**: SSE connection failing

**Solutions**:
1. Check backend is running on port 8000
2. Check browser console for errors
3. Verify CORS is enabled
4. Try in incognito/private browsing mode
5. Check browser supports EventSource API

### General Issues

#### Issue: Scripts won't run
**Problem**: Execution policy or permissions

**Solution (Windows)**:
```cmd
# Run PowerShell as Administrator
Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
```

**Solution (Linux/Mac)**:
```bash
chmod +x run_app.sh
```

---

## 🔐 Security Notes

### Development Environment:
- ✅ Use `.env` files (never commit to Git)
- ✅ Keep API keys secure
- ✅ Enable CORS only for localhost
- ✅ Use virtual environments

### Production Deployment:
- 🔒 Use environment variables (not .env files)
- 🔒 Enable HTTPS
- 🔒 Restrict CORS to specific domains
- 🔒 Use production ASGI server (Gunicorn + Uvicorn)
- 🔒 Implement rate limiting
- 🔒 Add authentication/authorization

---

## 📁 Project Structure

```
AI-AGENTS/
├── backend/                    # FastAPI Backend
│   ├── app/
│   │   ├── main.py            # Application entry
│   │   ├── api/               # API routes
│   │   ├── services/          # Business logic
│   │   ├── models/            # Data models
│   │   └── middleware/        # CORS, etc.
│   ├── requirements.txt       # Python dependencies
│   └── README.md
│
├── frontend/                   # React Frontend
│   ├── src/
│   │   ├── components/        # React components
│   │   ├── services/          # API clients
│   │   ├── types/             # TypeScript types
│   │   └── App.tsx            # Main app
│   ├── package.json           # Node dependencies
│   └── vite.config.ts         # Vite configuration
│
├── agents/                     # AI Agents
├── orchestrator/               # Orchestration
├── samples/                    # Test documents
├── mock_data/                  # Mock databases
├── .env.example                # Environment template
├── run_app.bat                 # Windows launcher
└── run_app.sh                  # Linux/Mac launcher
```

---

## 🎯 Next Steps After Installation

1. **Review Documentation**:
   - Read `README.md` for project overview
   - Check `TESTING_GUIDE.md` for testing instructions
   - Review `PROJECT_SUMMARY.md` for complete details

2. **Test the System**:
   - Upload sample documents
   - Watch real-time agent processing
   - Review risk assessments
   - Check final decisions

3. **Customize** (Optional):
   - Adjust risk thresholds in `.env`
   - Add custom mock data
   - Modify agent behavior
   - Customize UI styling

4. **Development**:
   - Explore the codebase
   - Add new features
   - Integrate with real databases
   - Deploy to production

---

## 🛠️ Development Tools

### Recommended VS Code Extensions:
- **Python** by Microsoft
- **Pylance** for Python IntelliSense
- **ESLint** for JavaScript/TypeScript
- **Tailwind CSS IntelliSense**
- **Prettier** for code formatting
- **Thunder Client** for API testing

### Useful Commands:

**Backend:**
```bash
# Run with auto-reload
uvicorn app.main:app --reload

# Run on specific port
uvicorn app.main:app --port 8001

# Run with custom host
uvicorn app.main:app --host 0.0.0.0
```

**Frontend:**
```bash
# Development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Lint code
npm run lint
```

---

## 📞 Support

If you encounter issues not covered here:

1. Check the **TESTING_GUIDE.md** for common issues
2. Review the **BACKEND_COMPLETE.md** for backend details
3. Check **FRONTEND_COMPLETE.md** for frontend specifics
4. Look at **PROJECT_SUMMARY.md** for architecture overview

---

## ✅ Installation Checklist

- [ ] Python 3.11+ installed
- [ ] Node.js 18+ installed
- [ ] Repository cloned
- [ ] .env file created and configured
- [ ] Backend dependencies installed
- [ ] Frontend dependencies installed
- [ ] Backend server running on port 8000
- [ ] Frontend server running on port 5173
- [ ] API health check passes
- [ ] Frontend loads successfully
- [ ] Sample document test works

---

**Installation Date**: _____________

**Status**: ⬜ Pending  ⬜ In Progress  ⬜ Complete

**System Ready**: ✅ Yes  ⬜ No

---

🎉 **Congratulations!** Your Multi-Agent KYC/AML System is now installed and ready to use!

Run `run_app.bat` (Windows) or `./run_app.sh` (Linux/Mac) to start both servers with one command.