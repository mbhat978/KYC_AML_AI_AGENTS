import { useState, useCallback } from 'react';
import './App.css';
import { UploadZone } from './components/UploadZone';
import EDDUploadZone from './components/EDDUploadZone';
import { LiveFeed } from './components/LiveFeed';
import { RiskMeter } from './components/RiskMeter';
import { Dashboard } from './components/Dashboard';
import AuditHistory from './components/AuditHistory';
import { api } from './services/api';
import { sseClient } from './services/sse';
import type { StreamEvent, FinalDecision, AgentEvent } from './types';
import jsPDF from 'jspdf';

type ViewMode = 'upload' | 'dashboard' | 'live-feed';
type TabMode = 'KYC' | 'AML' | 'AUDIT';

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
    setIsProcessing(true);
    setEvents([]);
    setFinalDecision(null);
    setSessionId(result.session_id);
    setActiveView('live-feed');
    setHasNewDecision(false);
    
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
    // For Audit History tab, automatically show dashboard view
    setActiveView(tab === 'AUDIT' ? 'dashboard' : 'upload');
  };

  const getDecisionStats = () => {
    if (!finalDecision) return null;
    const decision = finalDecision.decision;
    const emoji = decision === 'APPROVE' ? '✅' : decision === 'REJECT' ? '❌' : '⚠️';
    const color = decision === 'APPROVE' ? 'text-green-600' : decision === 'REJECT' ? 'text-red-600' : 'text-yellow-600';
    return { emoji, color, decision };
  };

  const handleExportReport = () => {
    if (!finalDecision) {
      alert('No report data available. Please process a transaction first.');
      return;
    }

    try {
      // Create new PDF document
      const doc = new jsPDF();
      const pageWidth = doc.internal.pageSize.getWidth();
      const pageHeight = doc.internal.pageSize.getHeight();
      let yPos = 20;

      // Helper function to add text with word wrap
      const addText = (text: string, x: number, fontSize: number = 10, maxWidth?: number, isBold: boolean = false) => {
        doc.setFontSize(fontSize);
        if (isBold) {
          doc.setFont('helvetica', 'bold');
        } else {
          doc.setFont('helvetica', 'normal');
        }
        
        if (maxWidth) {
          const lines = doc.splitTextToSize(text, maxWidth);
          doc.text(lines, x, yPos);
          yPos += (lines.length * fontSize * 0.5) + 2;
        } else {
          doc.text(text, x, yPos);
          yPos += fontSize * 0.5 + 2;
        }
      };

      // Check if we need a new page
      const checkNewPage = (requiredSpace: number = 30) => {
        if (yPos > pageHeight - requiredSpace) {
          doc.addPage();
          yPos = 20;
        }
      };

      // Header
      doc.setFillColor(99, 102, 241);
      doc.rect(0, 0, pageWidth, 40, 'F');
      doc.setTextColor(255, 255, 255);
      doc.setFontSize(24);
      doc.setFont('helvetica', 'bold');
      doc.text('AML TRANSACTION MONITORING REPORT', pageWidth / 2, 20, { align: 'center' });
      doc.setFontSize(10);
      doc.text('AI-Powered Risk Assessment & Compliance', pageWidth / 2, 30, { align: 'center' });
      
      yPos = 55;
      doc.setTextColor(0, 0, 0);

      // Report Metadata
      doc.setFillColor(240, 240, 240);
      doc.rect(15, yPos - 5, pageWidth - 30, 25, 'F');
      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      doc.text(`Report Generated: ${new Date().toLocaleString()}`, 20, yPos);
      yPos += 8;
      doc.text(`Session ID: ${sessionId}`, 20, yPos);
      yPos += 8;
      doc.text(`Report Version: 1.0`, 20, yPos);
      yPos += 15;

      // Executive Summary
      checkNewPage(50);
      doc.setFillColor(220, 252, 231);
      if (finalDecision.decision === 'REJECT') {
        doc.setFillColor(254, 226, 226);
      } else if (finalDecision.decision === 'ESCALATE') {
        doc.setFillColor(254, 243, 199);
      }
      doc.rect(15, yPos - 5, pageWidth - 30, 12, 'F');
      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.text('EXECUTIVE SUMMARY', 20, yPos + 3);
      yPos += 18;

      doc.setFontSize(11);
      doc.setFont('helvetica', 'bold');
      doc.text(`Final Decision: ${finalDecision.decision}`, 20, yPos);
      yPos += 8;
      doc.text(`Risk Category: ${finalDecision.risk_category}`, 20, yPos);
      yPos += 8;
      doc.text(`Risk Score: ${(finalDecision.risk_score ?? 0).toFixed(2)}`, 20, yPos);
      yPos += 8;
      doc.text(`Confidence: ${((finalDecision.confidence ?? 0) * 100).toFixed(0)}%`, 20, yPos);
      yPos += 12;

      doc.setFont('helvetica', 'normal');
      doc.setFontSize(10);
      addText('Recommendation:', 20, 10, undefined, true);
      addText(finalDecision.recommendation, 20, 10, pageWidth - 40);
      yPos += 5;

      // Transaction Analysis
      if (finalDecision.transaction_analysis) {
        checkNewPage(80);
        doc.setFillColor(239, 246, 255);
        doc.rect(15, yPos - 5, pageWidth - 30, 12, 'F');
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text('TRANSACTION ANALYSIS', 20, yPos + 3);
        yPos += 18;

        doc.setFontSize(11);
        doc.text(`Suspicious Activity: ${finalDecision.transaction_analysis.suspicious_activity ? 'YES' : 'NO'}`, 20, yPos);
        yPos += 8;
        doc.text(`AML Risk Score: ${(finalDecision.transaction_analysis.risk_score ?? 0).toFixed(1)}/10.0`, 20, yPos);
        yPos += 8;
        doc.text(`Risk Level: ${finalDecision.transaction_analysis.risk_level}`, 20, yPos);
        yPos += 12;

        // AML Flags
        doc.setFont('helvetica', 'bold');
        doc.setFontSize(12);
        doc.text('AML FLAGS DETECTED:', 20, yPos);
        yPos += 8;
        
        doc.setFont('helvetica', 'normal');
        doc.setFontSize(10);
        const flags = finalDecision.transaction_analysis.aml_flags;
        if (flags) {
          if (flags.sanctions_hit) { doc.text('• Sanctions List Match', 25, yPos); yPos += 6; }
          if (flags.pep_match) { doc.text('• Politically Exposed Person (PEP)', 25, yPos); yPos += 6; }
          if (flags.high_velocity) { doc.text('• High Velocity Transactions', 25, yPos); yPos += 6; }
          if (flags.structuring_detected) { doc.text('• Structuring Pattern Detected', 25, yPos); yPos += 6; }
          if (flags.smurfing_detected) { doc.text('• Smurfing Activity Detected', 25, yPos); yPos += 6; }
          if (flags.unusual_amount) { doc.text('• Unusual Transaction Amount', 25, yPos); yPos += 6; }
          
          if (!Object.values(flags).some(v => v)) {
            doc.text('• No AML flags detected', 25, yPos);
            yPos += 6;
          }
        }
        yPos += 6;

        // Transaction Summary
        if (finalDecision.transaction_analysis.summary) {
          doc.setFont('helvetica', 'bold');
          doc.setFontSize(10);
          doc.text('Summary:', 20, yPos);
          yPos += 6;
          doc.setFont('helvetica', 'normal');
          addText(finalDecision.transaction_analysis.summary, 20, 10, pageWidth - 40);
          yPos += 5;
        }
      }

      // Detailed Explanation
      checkNewPage(60);
      doc.setFillColor(254, 252, 232);
      doc.rect(15, yPos - 5, pageWidth - 30, 12, 'F');
      doc.setFontSize(16);
      doc.setFont('helvetica', 'bold');
      doc.text('DETAILED EXPLANATION', 20, yPos + 3);
      yPos += 18;

      doc.setFontSize(10);
      doc.setFont('helvetica', 'normal');
      addText(finalDecision.explanation, 20, 10, pageWidth - 40);
      yPos += 5;

      // Identity Information
      if (finalDecision.extracted_data) {
        checkNewPage(60);
        doc.setFillColor(240, 240, 240);
        doc.rect(15, yPos - 5, pageWidth - 30, 12, 'F');
        doc.setFontSize(16);
        doc.setFont('helvetica', 'bold');
        doc.text('IDENTITY INFORMATION', 20, yPos + 3);
        yPos += 18;

        doc.setFontSize(10);
        doc.setFont('helvetica', 'normal');
        Object.entries(finalDecision.extracted_data).forEach(([key, value]) => {
          checkNewPage();
          let displayValue = String(value ?? 'N/A');
          if (key.toLowerCase().includes('confidence') && typeof value === 'number' && value <= 1) {
            displayValue = `${(value * 100).toFixed(0)}%`;
          }
          doc.text(`${key.replace(/_/g, ' ').toUpperCase()}: ${displayValue}`, 20, yPos);
          yPos += 6;
        });
        yPos += 5;
      }

      // Footer
      const timestamp = new Date().toLocaleString();
      const pageCount = (doc as any).internal.getNumberOfPages();
      for (let i = 1; i <= pageCount; i++) {
        doc.setPage(i);
        doc.setFontSize(8);
        doc.setTextColor(128, 128, 128);
        doc.text(`Page ${i} of ${pageCount}`, pageWidth / 2, pageHeight - 10, { align: 'center' });
        doc.text(`Generated: ${timestamp}`, 20, pageHeight - 10);
        doc.text(`Confidential`, pageWidth - 20, pageHeight - 10, { align: 'right' });
      }

      // Save the PDF
      const fileName = `AML_Report_${sessionId.substring(0, 8)}_${new Date().toISOString().split('T')[0]}.pdf`;
      doc.save(fileName);

      // Show success message
      alert(`✅ Report exported successfully!\n\nFile: ${fileName}\n\nThe PDF report has been downloaded to your device.`);
      
    } catch (error) {
      console.error('Error generating PDF:', error);
      alert('❌ Error generating PDF report. Please try again.');
    }
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
            <div className="flex justify-center space-x-2 gap-3 pb-3 border-b-2 border-gray-200">
              <button onClick={() => handleTabChange('KYC')} className={`flex items-center gap-3 px-8 py-3 rounded-t-lg font-bold text-base transition-all duration-300 ${
                activeTab === 'KYC' ? 'bg-gradient-to-r from-sky-200 to-indigo-500 text-white shadow-lg transform scale-105' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}>
                <span className="text-2xl">👤</span>
                <div className="text-left">
                  <div className="font-bold">Customer Onboarding</div>
                  <div className="text-xs opacity-90">(KYC)</div>
                </div>
              </button>
              <button onClick={() => handleTabChange('AML')} className={`flex items-center gap-3 px-8 py-3 rounded-t-lg font-bold text-base transition-all duration-300 ${
                activeTab === 'AML' ? 'bg-gradient-to-r from-purple-300 to-blue-500 text-white shadow-lg transform scale-105' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}>
                <span className="text-2xl">💰</span>
                <div className="text-left">
                  <div className="font-bold">Transaction Monitoring</div>
                  <div className="text-xs opacity-90">(AML)</div>
                </div>
              </button>
              <button onClick={() => handleTabChange('AUDIT')} className={`flex items-center gap-3 px-8 py-3 rounded-t-lg font-bold text-base transition-all duration-300 ${
                activeTab === 'AUDIT' ? 'bg-gradient-to-r from-green-200 to-violet-600 text-white shadow-lg transform scale-105' : 'bg-gray-100 text-gray-600 hover:bg-gray-200 hover:text-gray-900'
              }`}>
                <span className="text-2xl">📋</span>
                <div className="text-left">
                  <div className="font-bold">Audit History</div>
                  <div className="text-xs opacity-90">(All Documents)</div>
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
            ) : activeTab === 'AML' ? (
              <EDDUploadZone onProcessingComplete={handleEDDProcessingComplete} />
            ) : (
              <div className="modern-card bg-white border-2 border-dashed border-gray-300 rounded-xl p-12 text-center">
                <div className="text-gray-400 text-5xl mb-4">📋</div>
                <p className="text-gray-600 font-medium text-lg">Audit History View</p>
                <p className="text-sm text-gray-500 mt-2">Click the Dashboard tab to view all processed documents</p>
              </div>
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
            {activeTab === 'AUDIT' ? (
              <div className="w-full">
                <AuditHistory />
              </div>
            ) : activeTab === 'KYC' ? (
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-6">
                <div className="lg:col-span-2">
                  <Dashboard decision={finalDecision} onDecisionUpdate={setFinalDecision} />
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
              <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                <div className="lg:col-span-2">
                  <div className="monitoring-container">
                    {/* Header Section */}
                    <div className="monitoring-header-section">
                      <div className="header-content">
                    <h1 className="monitoring-title">Transaction Monitoring</h1>
                    <p className="monitoring-subtitle">Real-time AML surveillance & compliance tracking</p>
                  </div>
                  <div className="header-actions">
                    <button 
                      onClick={handleExportReport}
                      disabled={!finalDecision}
                      className={`action-btn ${finalDecision ? 'primary' : 'disabled'}`}
                      title={finalDecision ? 'Export comprehensive AML report' : 'No data available to export'}
                    >
                      <span className="btn-icon">📥</span>
                      Export Report
                    </button>
                  </div>
                </div>

                {/* Stats Dashboard */}
                {finalDecision && finalDecision.transaction_analysis ? (
                  <div className="stats-grid">
                    {/* Active Alerts - Based on Suspicious Activity */}
                    <div className={`stat-card-modern ${finalDecision.transaction_analysis.suspicious_activity ? 'warning' : 'primary'}`}>
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">{finalDecision.transaction_analysis.suspicious_activity ? '�' : '�🔔'}</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">{finalDecision.transaction_analysis.suspicious_activity ? '1' : '0'}</div>
                        <div className="stat-label">Active Alerts</div>
                        <div className={`stat-trend ${finalDecision.transaction_analysis.suspicious_activity ? 'negative' : 'neutral'}`}>
                          <span className="trend-text">{finalDecision.transaction_analysis.suspicious_activity ? '⚠️ Alert triggered' : 'No active alerts'}</span>
                        </div>
                      </div>
                    </div>

                    {/* Flagged Transactions - Count AML flags */}
                    <div className="stat-card-modern warning">
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">⚠️</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">
                          {Object.values(finalDecision.transaction_analysis.aml_flags || {}).filter(Boolean).length}
                        </div>
                        <div className="stat-label">AML Flags Detected</div>
                        <div className="stat-trend negative">
                          <span className="trend-text">
                            {finalDecision.transaction_analysis.aml_flags?.sanctions_hit && '🚫 Sanctions | '}
                            {finalDecision.transaction_analysis.aml_flags?.pep_match && '👤 PEP | '}
                            {finalDecision.transaction_analysis.aml_flags?.high_velocity && '⚡ High Velocity | '}
                            {finalDecision.transaction_analysis.aml_flags?.structuring_detected && '📊 Structuring | '}
                            {finalDecision.transaction_analysis.aml_flags?.smurfing_detected && '🔄 Smurfing | '}
                            {finalDecision.transaction_analysis.aml_flags?.unusual_amount && '💰 Unusual Amount'}
                            {Object.values(finalDecision.transaction_analysis.aml_flags || {}).every(v => !v) && 'No flags'}
                          </span>
                        </div>
                      </div>
                    </div>

                    {/* AML Risk Level */}
                    <div className={`stat-card-modern ${
                      finalDecision.transaction_analysis.risk_level === 'HIGH' ? 'danger' : 
                      finalDecision.transaction_analysis.risk_level === 'MEDIUM' ? 'warning' : 'success'
                    }`}>
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">
                          {finalDecision.transaction_analysis.risk_level === 'HIGH' ? '🔴' : 
                           finalDecision.transaction_analysis.risk_level === 'MEDIUM' ? '🟡' : '🟢'}
                        </div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">{finalDecision.transaction_analysis.risk_level}</div>
                        <div className="stat-label">AML Risk Level</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Score: {(finalDecision.transaction_analysis.risk_score ?? 0).toFixed(1)}/10.0</span>
                        </div>
                      </div>
                    </div>

                    {/* Overall Decision */}
                    <div className={`stat-card-modern ${
                      finalDecision.decision === 'APPROVE' ? 'success' : 
                      finalDecision.decision === 'REJECT' ? 'danger' : 'warning'
                    }`}>
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">
                          {finalDecision.decision === 'APPROVE' ? '✅' : 
                           finalDecision.decision === 'REJECT' ? '❌' : '⚠️'}
                        </div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">{finalDecision.decision}</div>
                        <div className="stat-label">Final Decision</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Confidence: {((finalDecision.confidence ?? 0) * 100).toFixed(0)}%</span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="stats-grid">
                    <div className="stat-card-modern primary">
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">�</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">0</div>
                        <div className="stat-label">Active Alerts</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Awaiting transaction data</span>
                        </div>
                      </div>
                    </div>

                    <div className="stat-card-modern warning">
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">⚠️</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">--</div>
                        <div className="stat-label">AML Flags</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Awaiting transaction data</span>
                        </div>
                      </div>
                    </div>

                    <div className="stat-card-modern success">
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">📊</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">--</div>
                        <div className="stat-label">Risk Level</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Awaiting transaction data</span>
                        </div>
                      </div>
                    </div>

                    <div className="stat-card-modern info">
                      <div className="stat-icon-wrapper">
                        <div className="stat-icon">⚖️</div>
                      </div>
                      <div className="stat-info">
                        <div className="stat-value">--</div>
                        <div className="stat-label">Decision</div>
                        <div className="stat-trend neutral">
                          <span className="trend-text">Awaiting transaction data</span>
                        </div>
                      </div>
                    </div>
                  </div>
                )}

                {/* Transaction Analysis Summary */}
                {finalDecision && finalDecision.transaction_analysis && (
                  <div className="modern-card bg-white border border-gray-200 rounded-xl p-6 mt-6 shadow-lg">
                    <h3 className="text-lg font-bold text-gray-900 mb-4 flex items-center gap-2">
                      <span>📋</span>
                      Transaction Analysis Summary
                    </h3>
                    <p className="text-gray-700 leading-relaxed">
                      {finalDecision.transaction_analysis.summary}
                    </p>
                  </div>
                )}

                {/* Full Decision Details */}
                {finalDecision && (
                  <div className="mt-6">
                    <Dashboard decision={finalDecision} onDecisionUpdate={setFinalDecision} />
                  </div>
                )}
                </div>
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