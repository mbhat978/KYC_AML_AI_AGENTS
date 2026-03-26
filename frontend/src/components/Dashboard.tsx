import React, { useState } from 'react';
import type { FinalDecision } from '../types';
import { resumeProcessing } from '../services/api';

interface DashboardProps {
  decision: FinalDecision | null;
  onDecisionUpdate?: (decision: FinalDecision) => void;
}

export const Dashboard: React.FC<DashboardProps> = ({ decision, onDecisionUpdate }) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'aml' | 'audit'>('overview');
  const [isResolving, setIsResolving] = useState(false);

  console.log('🎯 [Dashboard Component] Received decision prop:', decision);

  const handleOverride = async (overrideDecision: 'APPROVE' | 'REJECT') => {
    try {
      setIsResolving(true);
      // Pass the session_id as the thread_id to resume the correct workflow
      const threadId = decision?.session_id || decision?.audit_trail?.session_id || '1';
      console.log(`🔄 [Dashboard] Resuming workflow with thread_id: ${threadId}, decision: ${overrideDecision}`);
      const response = await resumeProcessing(threadId, overrideDecision);
      console.log('✅ [Dashboard] Resume response:', response);
      
      // Create updated decision with the override
      if (decision && onDecisionUpdate) {
        const updatedDecision: FinalDecision = {
          ...decision,
          decision: overrideDecision,
          explanation: `${decision.explanation}\n\n✋ MANUAL OVERRIDE: Decision manually overridden to ${overrideDecision} by human reviewer.`,
          recommendation: `Human reviewer has overridden the system recommendation to ${overrideDecision}.`,
          confidence: decision.confidence, // Keep original AI confidence
          audit_trail: {
            ...decision.audit_trail,
            manual_override: {
              original_decision: decision.decision,
              override_decision: overrideDecision,
              timestamp: new Date().toISOString(),
              reason: 'Human review and manual override'
            }
          }
        };
        onDecisionUpdate(updatedDecision);
      }
      setIsResolving(false);
    } catch (error) {
      console.error(error);
      alert('Failed to process override. Please try again.');
      setIsResolving(false);
    }
  };
  
  if (!decision) {
    return (
      <div className="w-full">
        <div className="flex items-center justify-between mb-4">
          <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
            <span className="text-2xl">📋</span>
            KYC Decision Dashboard
          </h2>
        </div>
        <div className="modern-card glass-effect bg-white/60 border-2 border-dashed border-gray-300 rounded-xl p-12 text-center hover:border-gray-400 transition-all duration-300">
          <div className="text-gray-400 text-4xl mb-4 animate-pulse">⏳</div>
          <p className="text-gray-600 font-medium text-lg">Waiting for final decision...</p>
          <p className="text-sm text-gray-500 mt-3">The results will appear here once processing is complete</p>
        </div>
      </div>
    );
  }

  const getDecisionColor = () => {
    switch (decision.decision) {
      case 'APPROVE':
        return {
          bg: 'bg-green-50',
          border: 'border-green-500',
          text: 'text-green-700',
          badge: 'bg-green-500',
          icon: '✅'
        };
      case 'REJECT':
        return {
          bg: 'bg-red-50',
          border: 'border-red-500',
          text: 'text-red-700',
          badge: 'bg-red-500',
          icon: '❌'
        };
      case 'ESCALATE':
        return {
          bg: 'bg-yellow-50',
          border: 'border-yellow-500',
          text: 'text-yellow-700',
          badge: 'bg-yellow-500',
          icon: '⚠️'
        };
      default:
        return {
          bg: 'bg-gray-50',
          border: 'border-gray-500',
          text: 'text-gray-700',
          badge: 'bg-gray-500',
          icon: '❓'
        };
    }
  };

  const colors = getDecisionColor();

  return (
    <div className="w-full">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          <span className="text-2xl">📋</span>
          KYC Decision Dashboard
        </h2>
      </div>


      {/* Tabs */}
      <div className="flex gap-2 border-b border-gray-200 mb-4">
        <button onClick={() => setActiveTab('overview')}
          className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 ${
            activeTab === 'overview' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}>
           Overview
        </button>
        <button onClick={() => setActiveTab('aml')}
          className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 ${
            activeTab === 'aml' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}>
           AML Monitoring
        </button>
        <button onClick={() => setActiveTab('audit')}
          className={`px-6 py-3 font-semibold transition-all duration-200 border-b-2 ${
            activeTab === 'audit' ? 'border-blue-600 text-blue-600' : 'border-transparent text-gray-600 hover:text-gray-900'
          }`}>
           Audit History
        </button>
      </div>

      <div className={`modern-card rounded-xl border-2 ${colors.border} ${colors.bg} overflow-hidden shadow-lg hover:shadow-xl transition-all duration-300`}>
        {/* Decision Header */}
        <div className={`px-6 py-5 ${colors.badge} text-white shadow-md`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-4">
              <span className="text-4xl animate-[slideIn_0.5s_ease-out]">{colors.icon}</span>
              <div>
                <h3 className="text-3xl font-bold tracking-tight">{decision.decision}</h3>
                <p className="text-sm opacity-90 font-medium">Risk Level: {decision.risk_category}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-4xl font-bold animate-[slideIn_0.5s_ease-out]">{((decision.confidence ?? 0) * 100).toFixed(0)}%</div>
              <div className="text-sm opacity-90 font-medium">Confidence</div>
            </div>
          </div>
        </div>

        {/* Decision Details */}
        <div className="p-6 space-y-5">
          {/* Explanation */}
          <div className="animate-[slideIn_0.6s_ease-out]">
            <h4 className={`text-sm font-bold ${colors.text} mb-3 flex items-center gap-2 uppercase tracking-wide`}>
              <span>💬</span>
              Explanation
            </h4>
            <div className="text-gray-700 text-sm leading-relaxed bg-white/80 p-5 rounded-lg border border-gray-200 whitespace-pre-wrap shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm">
              {decision.explanation}
            </div>
          </div>

          {/* Recommendation */}
          <div className="animate-[slideIn_0.7s_ease-out]">
            <h4 className={`text-sm font-bold ${colors.text} mb-3 flex items-center gap-2 uppercase tracking-wide`}>
              <span>📝</span>
              Recommendation
            </h4>
            <p className="text-gray-700 text-sm leading-relaxed bg-white/80 p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm">
              {decision.recommendation}
            </p>
          </div>

          {/* Human Override Section - ESCALATE */}
          {decision.decision === 'ESCALATE' && (
            <div className="mt-6 p-4 bg-orange-500/10 border border-orange-500/30 rounded-xl">
              <h4 className="text-orange-400 font-semibold mb-3 flex items-center gap-2">
                <span className="relative flex h-3 w-3">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-orange-400 opacity-75"></span>
                  <span className="relative inline-flex rounded-full h-3 w-3 bg-orange-500"></span>
                </span>
                Human Override Required
              </h4>
              <div className="flex gap-3">
                <button 
                  onClick={() => handleOverride('APPROVE')}
                  disabled={isResolving}
                  className="flex-1 py-2 bg-green-600/20 text-green-400 border border-green-500/30 rounded-lg hover:bg-green-600/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Force Approve
                </button>
                <button 
                  onClick={() => handleOverride('REJECT')}
                  disabled={isResolving}
                  className="flex-1 py-2 bg-red-600/20 text-red-400 border border-red-500/30 rounded-lg hover:bg-red-600/40 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  Final Reject
                </button>
              </div>
            </div>
          )}

          {/* Transaction Analysis Section */}
          {decision.transaction_analysis && (
            <div className="animate-[slideIn_0.75s_ease-out]">
              <h4 className={`text-sm font-bold ${colors.text} mb-3 flex items-center gap-2 uppercase tracking-wide`}>
                <span>🔍</span>
                AML Transaction Analysis
              </h4>
              <div className="bg-white/80 p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm">
                <dl className="grid grid-cols-3 gap-4 text-sm mb-4">
                  <div>
                    <dt className="text-gray-500 font-medium">Suspicious Activity:</dt>
                    <dd className={`text-lg font-bold mt-1 ${decision.transaction_analysis?.suspicious_activity ? 'text-red-600' : 'text-green-600'}`}>
                      {decision.transaction_analysis?.suspicious_activity ? 'YES ⚠️' : 'NO ✓'}
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-500 font-medium">AML Risk Score:</dt>
                    <dd className="text-lg font-bold mt-1 text-gray-900">
                      {decision.transaction_analysis?.risk_score?.toFixed(1) ?? 'N/A'}/10.0
                    </dd>
                  </div>
                  <div>
                    <dt className="text-gray-500 font-medium">Risk Level:</dt>
                    <dd className={`text-lg font-bold mt-1 ${
                      decision.transaction_analysis?.risk_level === 'HIGH' ? 'text-red-600' :
                      decision.transaction_analysis?.risk_level === 'MEDIUM' ? 'text-yellow-600' :
                      'text-green-600'
                    }`}>
                      {decision.transaction_analysis?.risk_level ?? 'N/A'}
                    </dd>
                  </div>
                </dl>
                {decision.transaction_analysis?.summary && (
                  <p className="text-sm text-gray-700 leading-relaxed mt-3">
                    {decision.transaction_analysis.summary}
                  </p>
                )}
              </div>
            </div>
          )}

          {/* Extracted Data */}
          {decision.extracted_data && (
            <div className="animate-[slideIn_0.8s_ease-out]">
              <h4 className={`text-sm font-bold ${colors.text} mb-3 flex items-center gap-2 uppercase tracking-wide`}>
                <span>🔍</span>
                Extracted Information
              </h4>
              <div className="bg-white/80 p-5 rounded-lg border border-gray-200 shadow-sm hover:shadow-md transition-all duration-200 backdrop-blur-sm">
                <dl className="grid grid-cols-2 gap-4 text-sm">
                  {Object.entries(decision.extracted_data).map(([key, value]) => {
                    // Format confidence values as percentages
                    let displayValue: string;
                    if (key.toLowerCase().includes('confidence') && typeof value === 'number' && value <= 1) {
                      displayValue = `${(value * 100).toFixed(0)}%`;
                    } else if (typeof value === 'object' && value !== null) {
                      displayValue = JSON.stringify(value);
                    } else {
                      displayValue = String(value ?? '');
                    }
                    
                    return (
                      <div key={key}>
                        <dt className="text-gray-500 font-medium capitalize">
                          {key.replace(/_/g, ' ')}:
                        </dt>
                        <dd className="text-gray-900 mt-1">
                          {displayValue}
                        </dd>
                      </div>
                    );
                  })}
                </dl>
              </div>
            </div>
          )}

          {/* Audit Trail */}
          {decision.audit_trail && (
            <details className="group animate-[slideIn_0.9s_ease-out]">
              <summary className={`text-sm font-bold ${colors.text} cursor-pointer hover:bg-white/50 p-3 rounded-lg transition-all duration-200 flex items-center gap-2 uppercase tracking-wide`}>
                <span>📊</span>
                <span>Audit Trail</span>
                <span className="text-xs text-gray-500 group-open:hidden font-normal normal-case">(click to expand)</span>
              </summary>
              <div className="mt-3 bg-gray-900 text-gray-300 p-5 rounded-lg font-mono text-xs overflow-x-auto shadow-inner">
                <pre>{JSON.stringify(decision.audit_trail, null, 2)}</pre>
              </div>
            </details>
          )}

          {/* Metadata */}
          <div className="pt-5 border-t border-gray-300 animate-[slideIn_1s_ease-out]">
            <div className="flex items-center justify-between text-xs text-gray-600 font-medium">
              <span className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 bg-blue-500 rounded-full"></span>
                Session ID: {decision.session_id || 'N/A'}
              </span>
              <span className="flex items-center gap-2">
                <span>🕐</span>
                {new Date(decision.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};