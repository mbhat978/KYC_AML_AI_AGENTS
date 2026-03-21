import React from 'react';
import type { FinalDecision } from '../types';

interface DashboardProps {
  decision: FinalDecision | null;
}

export const Dashboard: React.FC<DashboardProps> = ({ decision }) => {
  if (!decision) {
    return (
      <div className="w-full">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
            <span className="text-2xl">📋</span>
            KYC Decision Dashboard
          </h2>
        </div>
        <div className="bg-gray-50 border-2 border-dashed border-gray-300 rounded-lg p-12 text-center">
          <div className="text-gray-400 text-lg mb-2">⏳</div>
          <p className="text-gray-500">Waiting for final decision...</p>
          <p className="text-xs text-gray-400 mt-2">The results will appear here once processing is complete</p>
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
      <div className="flex items-center justify-between mb-3">
        <h2 className="text-lg font-semibold text-gray-800 flex items-center gap-2">
          <span className="text-2xl">📋</span>
          KYC Decision Dashboard
        </h2>
      </div>

      <div className={`rounded-lg border-2 ${colors.border} ${colors.bg} overflow-hidden`}>
        {/* Decision Header */}
        <div className={`px-6 py-4 ${colors.badge} text-white`}>
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <span className="text-3xl">{colors.icon}</span>
              <div>
                <h3 className="text-2xl font-bold">{decision.decision}</h3>
                <p className="text-sm opacity-90">Risk Level: {decision.risk_category}</p>
              </div>
            </div>
            <div className="text-right">
              <div className="text-3xl font-bold">{((decision.confidence ?? 0) * 100).toFixed(0)}%</div>
              <div className="text-sm opacity-90">Confidence</div>
            </div>
          </div>
        </div>

        {/* Decision Details */}
        <div className="p-6 space-y-4">
          {/* Explanation */}
          <div>
            <h4 className={`text-sm font-semibold ${colors.text} mb-2 flex items-center gap-2`}>
              <span>💬</span>
              Explanation
            </h4>
            <div className="text-gray-700 text-sm leading-relaxed bg-white p-4 rounded border border-gray-200 whitespace-pre-wrap">
              {decision.explanation}
            </div>
          </div>

          {/* Recommendation */}
          <div>
            <h4 className={`text-sm font-semibold ${colors.text} mb-2 flex items-center gap-2`}>
              <span>📝</span>
              Recommendation
            </h4>
            <p className="text-gray-700 text-sm leading-relaxed bg-white p-4 rounded border border-gray-200">
              {decision.recommendation}
            </p>
          </div>

          {/* Extracted Data */}
          {decision.extracted_data && (
            <div>
              <h4 className={`text-sm font-semibold ${colors.text} mb-2 flex items-center gap-2`}>
                <span>🔍</span>
                Extracted Information
              </h4>
              <div className="bg-white p-4 rounded border border-gray-200">
                <dl className="grid grid-cols-2 gap-3 text-sm">
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
            <details className="group">
              <summary className={`text-sm font-semibold ${colors.text} cursor-pointer hover:underline flex items-center gap-2`}>
                <span>📊</span>
                <span>Audit Trail</span>
                <span className="text-xs text-gray-500 group-open:hidden">(click to expand)</span>
              </summary>
              <div className="mt-2 bg-gray-900 text-gray-300 p-4 rounded font-mono text-xs overflow-x-auto">
                <pre>{JSON.stringify(decision.audit_trail, null, 2)}</pre>
              </div>
            </details>
          )}

          {/* Metadata */}
          <div className="pt-4 border-t border-gray-200">
            <div className="flex items-center justify-between text-xs text-gray-500">
              <span>Session ID: {decision.session_id || 'N/A'}</span>
              <span>
                {new Date(decision.timestamp).toLocaleString()}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};