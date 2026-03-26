import { useEffect, useState } from 'react';
import { fetchAllAuditLogs } from '../services/api';

interface AuditRecord {
  id: number;
  session_id: string;
  timestamp: string;
  status: string;
  customer_name: string;
  document_type: string | null;
  risk_score: number | null;
  details: any;
}

export default function AuditHistory() {
  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadAuditLogs();
  }, []);

  const loadAuditLogs = async () => {
    try {
      setLoading(true);
      setError(null);
      const logs = await fetchAllAuditLogs();
      setAuditLogs(logs);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audit logs');
    } finally {
      setLoading(false);
    }
  };

  const getStatusBadge = (status: string) => {
    const statusColors: Record<string, string> = {
      'APPROVE': 'bg-green-100 text-green-800',
      'APPROVED': 'bg-green-100 text-green-800',
      'REJECT': 'bg-red-100 text-red-800',
      'REJECTED': 'bg-red-100 text-red-800',
      'ESCALATE': 'bg-orange-100 text-orange-800',
      'ESCALATED': 'bg-orange-100 text-orange-800',
      'AI_PROCESSING': 'bg-blue-100 text-blue-800',
      'AI_ANALYZING': 'bg-blue-100 text-blue-800',
      'PENDING': 'bg-gray-100 text-gray-800',
      'COMPLETED': 'bg-green-100 text-green-800',
    };

    const colorClass = statusColors[status.toUpperCase()] || 'bg-gray-100 text-gray-800';

    return (
      <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${colorClass}`}>
        {status}
      </span>
    );
  };

  const extractRiskScore = (log: AuditRecord): string => {
    // First check the direct risk_score field
    if (log.risk_score !== null && log.risk_score !== undefined) {
      return log.risk_score.toString();
    }
    // Fallback to details object
    if (log.details?.risk_score !== undefined) return log.details.risk_score.toString();
    if (log.details?.score !== undefined) return log.details.score.toString();
    if (log.details?.final_risk_score !== undefined) return log.details.final_risk_score.toString();
    return 'N/A';
  };

  const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
      second: '2-digit',
    });
  };

  const truncateSessionId = (sessionId: string): string => {
    return sessionId.substring(0, 8);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-red-50 border border-red-200 rounded-lg p-4">
        <p className="text-red-800">Error: {error}</p>
        <button
          onClick={loadAuditLogs}
          className="mt-2 px-4 py-2 bg-red-600 text-white rounded hover:bg-red-700 transition-colors"
        >
          Retry
        </button>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
        {/* Header */}
        <div className="px-6 py-4 border-b border-gray-200 bg-gradient-to-r from-blue-50 to-indigo-50">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-2xl font-bold text-gray-900">Audit History</h2>
              <p className="mt-1 text-sm text-gray-600">
                Global ledger of all processed documents ({auditLogs.length} records)
              </p>
            </div>
            <button
              onClick={loadAuditLogs}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors flex items-center gap-2"
            >
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
              </svg>
              Refresh
            </button>
          </div>
        </div>

        {/* Table */}
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Date/Time
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Session ID
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Customer Name
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Document
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Risk Score
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Status
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Details/Action
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {auditLogs.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-6 py-8 text-center text-gray-500">
                    No audit records found. Start processing documents to see audit logs here.
                  </td>
                </tr>
              ) : (
                auditLogs.map((log) => (
                  <tr key={log.id} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {formatTimestamp(log.timestamp)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600">
                      {truncateSessionId(log.session_id)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                      {log.customer_name || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">
                      {log.document_type || 'N/A'}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-sm">
                      <span className="font-semibold text-gray-900">
                        {extractRiskScore(log)}
                      </span>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap">
                      {getStatusBadge(log.status)}
                    </td>
                    <td className="px-6 py-4 text-sm text-gray-700">
                      <button
                        onClick={() => {
                          const detailsStr = JSON.stringify(log.details, null, 2);
                          alert(`Details for Session ${truncateSessionId(log.session_id)}:\n\n${detailsStr}`);
                        }}
                        className="text-blue-600 hover:text-blue-800 hover:underline font-medium"
                      >
                        View Details →
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}