import { useState, useCallback } from 'react';
import { UploadZone } from './components/UploadZone';
import { LiveFeed } from './components/LiveFeed';
import { RiskMeter } from './components/RiskMeter';
import { Dashboard } from './components/Dashboard';
import { api } from './services/api';
import { sseClient } from './services/sse';
import type { StreamEvent, FinalDecision, AgentEvent } from './types';

function App() {
  const [isProcessing, setIsProcessing] = useState(false);
  const [events, setEvents] = useState<StreamEvent[]>([]);
  const [finalDecision, setFinalDecision] = useState<FinalDecision | null>(null);
  const [sessionId, setSessionId] = useState<string>('');

  const handleFileUpload = useCallback(async (documentData: any) => {
    try {
      // Reset state
      setIsProcessing(true);
      setEvents([]);
      setFinalDecision(null);
      setSessionId('');

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

      // Connect to SSE stream
      sseClient.connect(
        response.session_id,
        (agentEvent: AgentEvent) => {
          // Skip heartbeat events - they're for connection maintenance only
          // (Already filtered in sse.ts, but double-check here for safety)
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
          // The decision data comes in TWO events:
          // 1. step === 'decision' with data containing the result directly
          // 2. step === 'complete' with data.final_result containing the result
          if (agentEvent.step === 'decision' && agentEvent.data) {
            // Extract decision from 'decision' step
            const decisionData = agentEvent.data as FinalDecision;
            setFinalDecision(decisionData);
          } else if (agentEvent.step === 'complete' && agentEvent.data?.final_result) {
            // Extract decision from 'complete' step (wrapped in final_result)
            const decisionData = agentEvent.data.final_result as FinalDecision;
            setFinalDecision(decisionData);
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 via-white to-purple-50">
      {/* Header */}
      <header className="bg-white shadow-sm border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 py-6">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-4xl">🛡️</span>
              <div>
                <h1 className="text-2xl font-bold text-gray-900">
                  Multi-Agent KYC/AML System
                </h1>
                <p className="text-sm text-gray-500">
                  AI-Powered Identity Verification & Risk Assessment
                </p>
              </div>
            </div>
            {sessionId && (
              <div className="text-right">
                <div className="text-xs text-gray-500">Session ID</div>
                <div className="text-sm font-mono text-gray-700">{sessionId}</div>
              </div>
            )}
          </div>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-8">
        <div className="space-y-8">
          {/* Upload Zone */}
          <section>
            <UploadZone onFileUpload={handleFileUpload} isProcessing={isProcessing} />
          </section>

          {/* Processing Indicator */}
          {isProcessing && (
            <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
              <div className="flex items-center gap-3">
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
                <span className="text-blue-800 font-medium">
                  Processing KYC document through multi-agent system...
                </span>
              </div>
            </div>
          )}

          {/* Results Grid */}
          {(events.length > 0 || finalDecision) && (
            <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
              {/* Live Feed - Takes 2 columns */}
              <div className="lg:col-span-2">
                <LiveFeed events={events} isActive={isProcessing} />
              </div>

              {/* Risk Meter - Takes 1 column */}
              <div>
                {finalDecision ? (
                  <RiskMeter
                    score={finalDecision.risk_score}
                    category={finalDecision.risk_category}
                  />
                ) : (
                  <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-8 text-center h-full flex items-center justify-center">
                    <div>
                      <div className="text-gray-400 text-3xl mb-2">📊</div>
                      <p className="text-gray-500 text-sm">Risk score pending...</p>
                    </div>
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Dashboard */}
          {(events.length > 0 || finalDecision) && (
            <section>
              <Dashboard decision={finalDecision} />
            </section>
          )}
        </div>
      </main>

      {/* Footer */}
      <footer className="mt-16 border-t border-gray-200 bg-white">
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
  );
}

export default App;