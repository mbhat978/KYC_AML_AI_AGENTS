# KYC/AML Frontend

Modern React + TypeScript + Tailwind CSS frontend for the Multi-Agent KYC/AML System.

## 🎯 Features

- **Upload Zone**: Drag-and-drop interface for KYC document upload
- **Live Feed**: Real-time agent activity streaming via SSE
- **Risk Meter**: Visual risk score gauge with category display
- **Dashboard**: Comprehensive decision and audit trail display

## 🚀 Quick Start

### From Root Directory (Recommended)

#### Windows:
```cmd
run_app.bat
```

#### Linux/Mac:
```bash
chmod +x run_app.sh
./run_app.sh
```

### Manual Start

1. **Install Dependencies:**
```bash
npm install
```

2. **Start Development Server:**
```bash
npm run dev
```

The frontend will be available at: http://localhost:5173

## 📁 Project Structure

```
frontend/
├── src/
│   ├── components/       # React components
│   │   ├── UploadZone.tsx    # File upload component
│   │   ├── LiveFeed.tsx      # SSE event stream display
│   │   ├── RiskMeter.tsx     # Risk visualization
│   │   └── Dashboard.tsx     # Results dashboard
│   ├── services/         # API & SSE clients
│   │   ├── api.ts           # REST API client
│   │   └── sse.ts           # Server-Sent Events client
│   ├── types/            # TypeScript definitions
│   │   └── index.ts
│   ├── App.tsx           # Main application component
│   └── main.tsx          # Application entry point
├── public/               # Static assets
└── index.html            # HTML template
```

## 🔧 Configuration

### Backend URL
The API base URL is configured in `src/services/api.ts` and `src/services/sse.ts`:
```typescript
const API_BASE_URL = 'http://localhost:8000/api';
```

Update these if your backend runs on a different port or domain.

## 🎨 Tech Stack

- **React 18** - UI library
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Build tool and dev server
- **EventSource API** - SSE client for real-time updates

## 📡 API Integration

The frontend communicates with the FastAPI backend using:

1. **REST API** (`api.ts`):
   - POST `/api/kyc/process` - Submit KYC documents
   - GET `/api/kyc/status/:sessionId` - Get session status

2. **Server-Sent Events** (`sse.ts`):
   - GET `/api/kyc/stream/:sessionId` - Real-time agent updates

## 🧪 Sample Documents

Three sample documents are available for testing:
- PAN Card
- Passport
- Driver's License

These are loaded from the `/samples/` directory in the root project.

## 🛠️ Available Scripts

- `npm run dev` - Start development server
- `npm run build` - Build for production
- `npm run preview` - Preview production build
- `npm run lint` - Run ESLint

## 📝 Component Details

### UploadZone
- Drag-and-drop file upload
- JSON file validation
- Sample document quick-load buttons

### LiveFeed
- Terminal-style event display
- Auto-scroll to latest events
- Color-coded agent activities
- Expandable event details

### RiskMeter
- Circular progress indicator
- Color-coded risk categories (Low/Medium/High/Critical)
- Animated score transitions
- Risk scale legend

### Dashboard
- Final decision display
- Explanation and recommendations
- Extracted data summary
- Audit trail viewer
- Session metadata

## 🐛 Troubleshooting

### CORS Issues
Ensure the backend CORS middleware allows:
```python
origins = ["http://localhost:5173"]
```

### SSE Connection Fails
- Check backend is running on port 8000
- Verify session ID is correct
- Check browser console for errors

### Build Errors
```bash
# Clear node_modules and reinstall
rm -rf node_modules package-lock.json
npm install
```

## 📚 Learn More

- [React Documentation](https://react.dev/)
- [TypeScript Documentation](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)
- [Vite Documentation](https://vitejs.dev/)