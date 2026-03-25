import { useState, useCallback } from 'react';
import './App.css';
import { UploadZone } from './components/UploadZone';
import EDDUploadZone from './components/EDDUploadZone';
import { LiveFeed } from './components/LiveFeed';
import { RiskMeter } from './components/RiskMeter';
import { Dashboard } from './components/Dashboard';
import { api } from './services/api';
import { sseClient } from './services/sse';
import type { StreamEvent, FinalDecision, AgentEvent } from './types';

type ViewMode = 'upload' | 'dashboard' | 'live-feed';
type TabMode = 'KYC' | 'AML';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [finalDecision, setFinalDecision] = useState<FinalDecision | null>(null);
  const [sessionId, setSessionId] = useState<string>('');
  const [activeView, setActiveView] = useState<ViewMode>('upload');
  const [hasNewDecision, setHasNewDecision] = useState(false);
  const [activeTab, setActiveTab] = useState<TabMode>('KYC');

  const handleFileUpload = useCallback(async (documentData: any) => {
    try {
      setIsProcessing(true);
      setEvents([]);
      setFinalDecision(null);
      setSessionId('');
      setHasNewDecision(false);

      let response;
      if (documentData instanceof File) {
        response = await api.uploadFile(documentData);
      } else {
        response = await api.processDocument(documentData);
      }
      setSessionId(response.session_id);
      setActiveView('live-feed');

      sseClient.connect(
        response.session_id,
        (agentEvent: AgentEvent) => {
          if (agentEvent.step === 'heartbeat') return;
          
          const streamEvent: StreamEvent = {
            type: agentEvent.step || 'info',
            agent: agentEvent.agent,
            message: agentEvent.message,
            details: agentEvent.data,
            timestamp: agentEvent.timestamp
          };

          setEvents((prev) => [...prev, streamEvent]);

          // Handle decision events
          if (agentEvent.step === 'decision' && agentEvent.data) {
            console.log('📊 [Dashboard] Received DECISION event:', agentEvent.data);
            const decisionData = agentEvent.data as FinalDecision;
            console.log('📊 [Dashboard] Setting final decision:', decisionData);
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            setTimeout(() => {
              console.log('📊 [Dashboard] Switching to dashboard view');
              setActiveView('dashboard');
            }, 1000);
          } else if (agentEvent.step === 'complete' && agentEvent.data?.final_result) {
            console.log('✅ [Dashboard] Received COMPLETE event:', agentEvent.data.final_result);
            const decisionData = agentEvent.data.final_result as FinalDecision;
            console.log('✅ [Dashboard] Setting final decision from complete:', decisionData);
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            setTimeout(() => {
              console.log('✅ [Dashboard] Switching to dashboard view');
              setActiveView('dashboard');
            }, 1000);
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
          setIsProcessing(false);
        }
      );
    } catch (error: any) {
      console.error('Error processing document:', error);
      alert(`Error: ${error.message || 'Failed to process document'}`);
      setIsProcessing(false);
    }
  }, []);

  const handleEDDProcessingComplete = useCallback((result: any) => {
    setSessionId(result.session_id);
    setActiveView('live-feed');
    
      sseClient.connect(
        result.session_id,
        (agentEvent: AgentEvent) => {
          if (agentEvent.step === 'heartbeat') return;
          
          const streamEvent: StreamEvent = {
            type: agentEvent.step || 'info',
            agent: agentEvent.agent,
            message: agentEvent.message,
            details: agentEvent.data,
            timestamp: agentEvent.timestamp
          };

          setEvents((prev) => [...prev, streamEvent]);

          // Handle decision events (EDD)
          if (agentEvent.step === 'decision' && agentEvent.data) {
            console.log('📊 [EDD Dashboard] Received DECISION event:', agentEvent.data);
            const decisionData = agentEvent.data as FinalDecision;
            console.log('📊 [EDD Dashboard] Setting final decision:', decisionData);
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            setTimeout(() => {
              console.log('📊 [EDD Dashboard] Switching to dashboard view');
              setActiveView('dashboard');
            }, 1000);
          } else if (agentEvent.step === 'complete' && agentEvent.data?.final_result) {
            console.log('✅ [EDD Dashboard] Received COMPLETE event:', agentEvent.data.final_result);
            const decisionData = agentEvent.data.final_result as FinalDecision;
            console.log('✅ [EDD Dashboard] Setting final decision from complete:', decisionData);
            setFinalDecision(decisionData);
            setHasNewDecision(true);
            setTimeout(() => {
              console.log('✅ [EDD Dashboard] Switching to dashboard view');
              setActiveView('dashboard');
            }, 1000);
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
        setIsProcessing(false);
      }
    );
  }, []);

  const handleViewChange = (view: ViewMode) => {
    setActiveView(view);
    if (view === 'dashboard') {
      setHasNewDecision(false);
    }
  };

  const handleTabChange = (tab: TabMode) => {
    setActiveTab(tab);
    setEvents([]);
    setFinalDecision(null);
    setSessionId('');
    setHasNewDecision(false);
    setIsProcessing(false);
    setActiveView('upload');
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
        <header className="bg-white/95 backdrop-blur-sm shadow-lg border-b border-indigo-100 sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-5">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="text-4xl animate-pulse">🛡️</span>
                <div>
                  <h1 className="text-2xl font-bold text-gray-900">Multi-Agent KYC/AML System</h1>
                  <p className="text-sm text-gray-500">AI-Powered Identity Verification & Risk Assessment</p>
                </div>
              </div>
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

          <div className="max-w-7xl mx-auto px-4 mt-4">
            <div className="flex gap-3 pb-3 border-b-2 border-gray-200">
              <button onClick={() => handleTabChange('KYC')} className={`flex items-center gap-3 px-8 py-3 rounded-t-lg font-bold text-base transition-all duration-300 ${
                activeTab === 'KYC' ? 'bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg transform scale-105' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}>
                <span className="text-2xl">👤</span>
                <div className="text-left">
                  <div className="font-bold">Customer Onboarding</div>
                  <div className="text-xs opacity-90">(KYC)</div>
                </div>
              </button>
              <button onClick={() => handleTabChange('AML')} className={`flex items-center gap-3 px-8 py-3 rounded-t-lg font-bold text-base transition-all duration-300 ${
                activeTab === 'AML' ? 'bg-gradient-to-r from-purple-600 to-pink-600 text-white shadow-lg transform scale-105' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}>
                <span className="text-2xl">💰</span>
                <div className="text-left">
                  <div className="font-bold">Transaction Monitoring</div>
                  <div className="text-xs opacity-90">(AML)</div>
                </div>
              </button>
            </div>
          </div>
          
          {(events.length > 0 || finalDecision) && (
            <div className="max-w-7xl mx-auto px-4">
              <nav className="flex gap-2 mt-4 border-b border-gray-200">
                <button onClick={() => handleViewChange('upload')} className={`flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                  activeView === 'upload' ? 'border-blue-600 text-blue-600 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}>
                  <span className="text-xl">📤</span>
                  <span>Upload</span>
                </button>
                <button onClick={() => handleViewChange('dashboard')} className={`relative flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                  activeView === 'dashboard' ? 'border-blue-600 text-blue-600 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}>
                  <span className="text-xl">📊</span>
                  <span>Dashboard</span>
                  {hasNewDecision && activeView !== 'dashboard' && (
                    <span className="absolute top-2 right-2 flex h-3 w-3">
                      <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75"></span>
                      <span className="relative inline-flex rounded-full h-3 w-3 bg-red-500"></span>
                    </span>
                  )}
                </button>
                <button onClick={() => handleViewChange('live-feed')} className={`flex items-center gap-2 px-6 py-3 font-semibold transition-all duration-300 border-b-3 ${
                  activeView === 'live-feed' ? 'border-blue-600 text-blue-600 bg-blue-50' : 'border-transparent text-gray-600 hover:text-gray-900 hover:bg-gray-50'
                }`}>
                  <span className="text-xl">🎯</span>
                  <span>Live Feed</span>
                  {isProcessing && <span className="w-2 h-2 bg-green-500 rounded-full animate-pulse"></span>}
                </button>
              </nav>
            </div>
          )}
        </header>

        <main className="max-w-7xl mx-auto px-4 py-8">
          <div className={`transition-all duration-500 ${activeView === 'upload' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'}`}>
            {activeTab === 'KYC' ? (
              <UploadZone onFileUpload={handleFileUpload} isProcessing={isProcessing} />
            ) : (
              <EDDUploadZone onProcessingComplete={handleEDDProcessingComplete} />
            )}
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
                    <span className="text-blue-900 font-bold text-lg block">Processing {activeTab} Analysis</span>
                    <span className="text-blue-700 text-sm">Multi-agent system analyzing your data...</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className={`transition-all duration-500 ${activeView === 'dashboard' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'}`}>
            {activeTab === 'KYC' ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2">
                  <Dashboard decision={finalDecision} />
                </div>
                <div>
                  {finalDecision ? (
                    <RiskMeter score={finalDecision.risk_score} category={finalDecision.risk_category} />
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
            ) : (
              <div className="monitoring-container">
                {/* Header Section */}
                <div className="monitoring-header-section">
                  <div className="header-content">
                    <h1 className="monitoring-title">Transaction Monitoring</h1>
                    <p className="monitoring-subtitle">Real-time AML surveillance & compliance tracking</p>
                  </div>
                  <div className="header-actions">
                    <button className="action-btn primary">
                      <span className="btn-icon">📥</span>
                      Export Report
                    </button>
                    <button className="action-btn secondary">
                      <span className="btn-icon">⚙️</span>
                      Settings
                    </button>
                  </div>
                </div>

                {/* Stats Dashboard */}
                <div className="stats-grid">
                  <div className="stat-card-modern primary">
                    <div className="stat-icon-wrapper">
                      <div className="stat-icon">🔔</div>
                    </div>
                    <div className="stat-info">
                      <div className="stat-value">0</div>
                      <div className="stat-label">Active Alerts</div>
                      <div className="stat-trend neutral">
                        <span className="trend-text">No active alerts</span>
                      </div>
                    </div>
                  </div>

                  <div className="stat-card-modern warning">
                    <div className="stat-icon-wrapper">
                      <div className="stat-icon">⚠️</div>
                    </div>
                    <div className="stat-info">
                      <div className="stat-value">0</div>
                      <div className="stat-label">Flagged Transactions</div>
                      <div className="stat-trend neutral">
                        <span className="trend-text">All clear</span>
                      </div>
                    </div>
                  </div>

                  <div className="stat-card-modern success">
                    <div className="stat-icon-wrapper">
                      <div className="stat-icon">✅</div>
                    </div>
                    <div className="stat-info">
                      <div className="stat-value">0</div>
                      <div className="stat-label">Cleared Today</div>
                      <div className="stat-trend neutral">
                        <span className="trend-text">Ready to monitor</span>
                      </div>
                    </div>
                  </div>

                  <div className="stat-card-modern info">
                    <div className="stat-icon-wrapper">
                      <div className="stat-icon">📊</div>
                    </div>
                    <div className="stat-info">
                      <div className="stat-value">--</div>
                      <div className="stat-label">Detection Rate</div>
                      <div className="stat-trend neutral">
                        <span className="trend-text">Awaiting data</span>
                      </div>
                    </div>
                  </div>
                </div>

                {/* Filter & Search Section */}
                <div className="filter-section">
                  <div className="search-wrapper">
                    <span className="search-icon">🔍</span>
                    <input 
                      type="text" 
                      className="search-input" 
                      placeholder="Search transactions, accounts, or alerts..."
                    />
                  </div>
                  <div className="filter-buttons">
                    <button className="filter-btn active">All</button>
                    <button className="filter-btn">High Risk</button>
                    <button className="filter-btn">Medium Risk</button>
                    <button className="filter-btn">Low Risk</button>
                    <button className="filter-btn">Cleared</button>
                  </div>
                </div>

                {/* Transaction Feed - Empty State */}
                <div className="transaction-feed">
                  <div className="feed-header">
                    <h2>Recent Activity</h2>
                    <div className="live-indicator">
                      <span className="live-dot"></span>
                      <span>Live</span>
                    </div>
                  </div>

                  {/* Empty State */}
                  <div className="empty-state">
                    <div className="empty-state-icon">📊</div>
                    <h3 className="empty-state-title">No Transactions to Display</h3>
                    <p className="empty-state-description">
                      Transaction monitoring system is active and ready. Transactions will appear here once data is received.
                    </p>
                  </div>
                </div>
              </div>
            )}
          </div>

          <div className={`transition-all duration-500 ${activeView === 'live-feed' ? 'opacity-100 scale-100' : 'opacity-0 scale-95 h-0 overflow-hidden absolute'}`}>
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
                    <button onClick={() => handleViewChange('dashboard')} className="modern-button px-6 py-3 bg-blue-600 text-white font-semibold rounded-lg shadow-md hover:bg-blue-700 hover:shadow-xl">
                      View Dashboard →
                    </button>
                  </div>
                </div>
              )}
            </div>
          </div>
        </main>

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