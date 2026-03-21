import { useState, useCallback } from 'react';
import './App.css';
import { UploadZone } from './components/UploadZone';
import { LiveFeed } from './components/LiveFeed';
import { RiskMeter } from './components/RiskMeter';
import { Dashboard } from './components/Dashboard';
import { api } from './services/api';
import { sseClient } from './services/sse';
import type { StreamEvent, FinalDecision, AgentEvent } from './types';

type ViewMode = 'upload' | 'dashboard' | 'live-feed';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [finalDecision, setFinalDecision] = useState<FinalDecision | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [activeView, setActiveView] = useState<ViewMode>('upload');
  const [hasNewDecision, setHasNewDecision] = useState(false);

  const handleFileUpload = useCallback(async (documentData: any) => {
    try {
      // Reset state
      setIsProcessing(true);
      setEvents([]);
      setFinalDecision(null);
      setSessionId('');
      setHasNewDecision(false);

      // Check if documentData is a File object or JSON data
      let response;
      if (documentData instanceof File) {
        // Upload file (PDF, JPG, PNG)
        response = await api.uploadFile(documentData);
      } else {
        // Process JSON document data
        response = await api.processDocument(documentData);
      }
      setSessionId(response.session_id);

      // Auto-switch to live feed view
      setActiveView('live-feed');

      // Connect to SSE stream
      sseClient.connect(
        response.session_id,
        (agentEvent: AgentEvent) => {
          // Skip heartbeat events - they're for connection maintenance only
          if (agentEvent.step === 'heartbeat') {
            return;
          }
          
          // Convert AgentEvent to StreamEvent for display
          const streamEvent: StreamEvent = {
            type: agentEvent.step || 'info',
            agent: agentEvent.agent,
            message: agentEvent.message,
            details: agentEvent.data,
            timestamp: agentEvent.timestamp
          };

          setEvents((prev) => [...prev, streamEvent]);

          // Check if this is the final decision
          if (agentEvent.step === 'decision' && agentEvent.data) {
            const decisionData = agentEvent.data as FinalDecision;
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            // Auto-switch to dashboard view
            setTimeout(() => setActiveView('dashboard'), 1000);
          } else if (agentEvent.step === 'complete' && agentEvent.data?.final_result) {
            const decisionData = agentEvent.data.final_result as FinalDecision;
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            // Auto-switch to dashboard view
            setTimeout(() => setActiveView('dashboard'), 1000);
          }
        },
        (error) => {
          console.error('SSE Error:', error);
          const errorEvent: StreamEvent = {
            type: 'error',
            message: 'Stream connection error',
            timestamp: new Date().toISOString()
          };
          setEvents((prev) => [...prev, errorEvent]);
          setIsProcessing(false);
        },
        () => {
          // On complete
          setIsProcessing(false);
        }
      );
    } catch (error: any) {
      console.error('Error processing document:', error);
      alert(`Error: ${error.message || 'Failed to process document'}`);
      setIsProcessing(false);
    }
  }, []);

  const handleViewChange = (view: ViewMode) => {
    setActiveView(view);
    if (view === 'dashboard') {
      setHasNewDecision(false);
    }
  };

  const getDecisionStats = () => {
    if (!finalDecision) return null;
    
    const decision = finalDecision.decision;
    const emoji = decision === 'APPROVE' ? '✅' : decision === 'REJECT' ? '❌' : '⚠️';
    const color = decision === 'APPROVE' ? 'text-green-600' : decision === 'REJECT' ? 'text-red-600' : 'text-yellow-600';
    
    return { emoji, color, decision };
  };

  const stats = getDecisionStats();

  return (
    <div className="min-h-screen kyc-background">
      <div className="kyc-content">
        {/* Header */}
        <header className="bg-white/95 backdrop-blur-sm shadow-lg border-b border-indigo-100 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-4xl animate-pulse">🛡️</span>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">
                    Multi-Agent KYC/AML System
                  </h1>
                  <p className="text-sm text-gray-500">
                    AI-Powered Identity Verification & Risk Assessment
                  </p>
                </div>
              </div>
              
              {/* Quick Stats */}
              <div className="flex items-center gap-4">
                {sessionId && (
                  <div className="text-right">
                    <div className="text-xs text-gray-500">Session ID</div>
                    <div className="text-sm font-mono text-gray-700">{sessionId}</div>
                  </div>
                )}
                {stats && (
                  <div className={`flex items-center gap-2 px-4 py-2 rounded-lg bg-white border-2 ${
                    stats.decision === 'APPROVE' ? 'border-green-500' : 
                    stats.decision === 'REJECT' ? 'border-red-500' : 'border-yellow-500'
                  } shadow-md animate-[slideIn_0.5s_ease-out]`}>
                    <span className="text-2xl">{stats.emoji}</span>
                    <div className="text-right">
                      <div className="text-xs text-gray-500">Decision</div>
                      <div className={`text-sm font-bold ${stats.color}`}>{stats.decision}</div>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>
          
          {/* Tab Navigation */}
          {(events.length > 0 || finalDecision) && (
            <div className="max-w-7xl mx-auto px-4">
              <nav className="flex gap-2 mt-4 border-b border-gray-200">
                <button
                  onClick={() => handleViewChange('upload')}
                  className={`flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                    activeView === 'upload'
                      ? 'border-blue-600 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl">📤</span>
                  <span>Upload</span>
                </button>
                
                <button
                  onClick={() => handleViewChange('dashboard')}
                  className={`relative flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                    activeView === 'dashboard'
                      ? 'border-blue-600 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl">📊</span>
                  <span>Dashboard</span>
                  {hasNewDecision && activeView !== 'dashboard' && (
                    <span className="absolute top-2 right-2 flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                  )}
                </button>
                
                <button
                  onClick={() => handleViewChange('live-feed')}
                  className={`flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                    activeView === 'live-feed'
                      ? 'border-blue-600 text-blue-600 bg-blue-50'
                      : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                  }`}
                >
                  <span className="text-xl">🎯</span>
                  <span>Live Feed</span>
                  {isProcessing && (
                    <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  )}
                </button>
              </nav>
            </div>
          )}
        </header>

        {/* Main Content with Tab Panels */}
        <main className="max-w-7xl mx-auto px-4 py-8">
          {/* Upload View */}
          <div className={`transition-all duration-500 ${
            activeView === 'upload' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'
          }`}>
            <UploadZone onFileUpload={handleFileUpload} isProcessing={isProcessing} />
            
            {isProcessing && (
              <div className="mt-6 bg-gradient-to-r from-blue-50 to-indigo-50 border border-blue-200 rounded-xl p-6 shadow-lg animate-[slideIn_0.5s_ease-out]">
                <div className="flex items-center gap-4">
                  <div className="relative">
                    <div className="animate-spin rounded-full h-12 w-12 border-4 border-blue-200 border-t-blue-600"></div>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-xl">🤖</span>
                    </div>
                  </div>
                  <div>
                    <span className="text-blue-900 font-bold text-lg block">Processing KYC Document</span>
                    <span className="text-blue-700 text-sm">Multi-agent system analyzing your document...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Dashboard View */}
          <div className={`transition-all duration-500 ${
            activeView === 'dashboard' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'
          }`}>
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
              <div className="lg:col-span-2">
                <Dashboard decision={finalDecision} />
              </div>
              <div>
                {finalDecision ? (
                  <RiskMeter
                    score={finalDecision.risk_score}
                    category={finalDecision.risk_category}
                  />
                ) : (
                  <div className="modern-card glass-effect bg-white/60 border-2 border-dashed border-gray-300 rounded-xl p-12 text-center h-full flex items-center justify-center">
                    <div>
                      <div className="text-gray-400 text-4xl mb-2 animate-pulse">📊</div>
                      <p className="text-gray-500 text-sm font-medium">Risk score pending...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Live Feed View */}
          <div className={`transition-all duration-500 ${
            activeView === 'live-feed' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'
          }`}>
            <div className="grid grid-cols-1 gap-6">
              <LiveFeed events={events} isActive={isProcessing} />
              
              {finalDecision && (
                <div className="modern-card bg-gradient-to-r from-green-50 to-blue-50 border-2 border-blue-200 rounded-xl p-6 shadow-lg animate-[slideIn_0.5s_ease-out]">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                      <span className="text-4xl">{stats?.emoji}</span>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">Processing Complete!</h3>
                        <p className="text-sm text-gray-600">View the dashboard for detailed results</p>
                      </div>
                    </div>
                    <button
                      onClick={() => handleViewChange('dashboard')}
                      className="modern-button px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 hover:shadow-xl"
                    >
                      View Dashboard →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>

        {/* Footer */}
        <footer className="mt-16 border-t border-indigo-200 bg-white/90 backdrop-blur-sm">
          <div className="max-w-7xl mx-auto px-4 py-6">
            <div className="flex items-center justify-between text-sm text-gray-500">
              <p>© 2026 Multi-Agent KYC/AML System. All rights reserved.</p>
              <div className="flex items-center gap-4">
                <span className="flex items-center gap-2">
                  <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>
                  Backend Status: Active
                </span>
              </div>
            </div>
          </div>
        </footer>
      </div>
    </div>
  );
}

export default App;