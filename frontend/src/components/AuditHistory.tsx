import { useEffect, useState, useMemo } from 'react';
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

type SortField = 'timestamp' | 'customer_name' | 'risk_score' | 'status';

export default function AuditHistory() {
  const [auditLogs, setAuditLogs] = useState<AuditRecord[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [currentPage, setCurrentPage] = useState(1);
  const recordsPerPage = 10;
  
  const [searchTerm, setSearchTerm] = useState('');
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [riskFilter, setRiskFilter] = useState<string>('all');
  const [sortField, setSortField] = useState<SortField>('timestamp');
  const [sortOrder, setSortOrder] = useState<'asc' | 'desc'>('desc');

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
    const statusConfig: Record<string, { color: string; icon: string }> = {
      'APPROVE': { color: 'bg-green-100 text-green-800 border-green-200', icon: '✓' },
      'APPROVED': { color: 'bg-green-100 text-green-800 border-green-200', icon: '✓' },
      'REJECT': { color: 'bg-red-100 text-red-800 border-red-200', icon: '✗' },
      'REJECTED': { color: 'bg-red-100 text-red-800 border-red-200', icon: '✗' },
      'ESCALATE': { color: 'bg-orange-100 text-orange-800 border-orange-200', icon: '⚠' },
      'ESCALATED': { color: 'bg-orange-100 text-orange-800 border-orange-200', icon: '⚠' },
      'AI_PROCESSING': { color: 'bg-blue-100 text-blue-800 border-blue-200', icon: '⚡' },
      'AI_ANALYZING': { color: 'bg-blue-100 text-blue-800 border-blue-200', icon: '🔍' },
      'PENDING': { color: 'bg-yellow-100 text-yellow-800 border-yellow-200', icon: '⏱' },
      'COMPLETED': { color: 'bg-green-100 text-green-800 border-green-200', icon: '✓' },
    };
    const config = statusConfig[status.toUpperCase()] || { color: 'bg-gray-100 text-gray-800 border-gray-200', icon: '•' };
    return (
      <span className={`inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border ${config.color}`}>
        <span className="mr-1">{config.icon}</span>{status}
      </span>
    );
  };

  const getRiskBadge = (score: number | null) => {
    if (score === null || score === undefined) return <span className="text-gray-400 text-sm">N/A</span>;
    let colorClass = '', label = '';
    if (score >= 7) { colorClass = 'bg-red-100 text-red-800 border-red-300'; label = 'HIGH'; }
    else if (score >= 5) { colorClass = 'bg-orange-100 text-orange-800 border-orange-300'; label = 'MEDIUM'; }
    else { colorClass = 'bg-green-100 text-green-800 border-green-300'; label = 'LOW'; }
    return (
      <div className="flex items-center gap-2">
        <span className={`px-2 py-1 rounded text-xs font-bold border ${colorClass}`}>{label}</span>
        <span className="font-semibold text-gray-900">{score}</span>
      </div>
    );
  };

  const extractRiskScore = (log: AuditRecord): number | null => {
    if (log.risk_score !== null && log.risk_score !== undefined) return log.risk_score;
    if (log.details?.risk_score !== undefined) return log.details.risk_score;
    if (log.details?.score !== undefined) return log.details.score;
    if (log.details?.final_risk_score !== undefined) return log.details.final_risk_score;
    return null;
  };

  const formatTimestamp = (timestamp: string): string => {
    return new Date(timestamp).toLocaleString('en-US', { year: 'numeric', month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  };

  const stats = useMemo(() => {
    const approved = auditLogs.filter(log => log.status.toUpperCase().includes('APPROVE')).length;
    const rejected = auditLogs.filter(log => log.status.toUpperCase().includes('REJECT')).length;
    const pending = auditLogs.filter(log => log.status.toUpperCase().includes('PENDING')).length;
    const highRisk = auditLogs.filter(log => { const score = extractRiskScore(log); return score !== null && score >= 7; }).length;
    return { total: auditLogs.length, approved, rejected, pending, highRisk };
  }, [auditLogs]);

  const filteredLogs = useMemo(() => {
    let filtered = auditLogs.filter(log => {
      const searchLower = searchTerm.toLowerCase();
      const matchesSearch = log.customer_name?.toLowerCase().includes(searchLower) || log.session_id.toLowerCase().includes(searchLower) || log.document_type?.toLowerCase().includes(searchLower) || log.status.toLowerCase().includes(searchLower);
      if (!matchesSearch) return false;
      if (statusFilter !== 'all' && !log.status.toUpperCase().includes(statusFilter.toUpperCase())) return false;
      if (riskFilter !== 'all') {
        const score = extractRiskScore(log);
        if (score === null) return riskFilter === 'none';
        if (riskFilter === 'high' && score < 7) return false;
        if (riskFilter === 'medium' && (score < 5 || score >= 7)) return false;
        if (riskFilter === 'low' && score >= 5) return false;
      }
      return true;
    });
    filtered.sort((a, b) => {
      let comparison = 0;
      if (sortField === 'timestamp') comparison = new Date(a.timestamp).getTime() - new Date(b.timestamp).getTime();
      else if (sortField === 'customer_name') comparison = (a.customer_name || '').localeCompare(b.customer_name || '');
      else if (sortField === 'risk_score') comparison = (extractRiskScore(a) || 0) - (extractRiskScore(b) || 0);
      else if (sortField === 'status') comparison = a.status.localeCompare(b.status);
      return sortOrder === 'asc' ? comparison : -comparison;
    });
    return filtered;
  }, [auditLogs, searchTerm, statusFilter, riskFilter, sortField, sortOrder]);

  // Pagination logic
  const totalPages = Math.ceil(filteredLogs.length / recordsPerPage);
  
  const paginatedLogs = useMemo(() => {
    const startIndex = (currentPage - 1) * recordsPerPage;
    const endIndex = startIndex + recordsPerPage;
    return filteredLogs.slice(startIndex, endIndex);
  }, [filteredLogs, currentPage]);

  // Reset to page 1 when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [searchTerm, statusFilter, riskFilter]);

  const handlePageChange = (page: number) => {
    setCurrentPage(page);
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const handlePrevious = () => setCurrentPage(prev => Math.max(prev - 1, 1));
  const handleNext = () => setCurrentPage(prev => Math.min(prev + 1, totalPages));

  const handleSort = (field: SortField) => {
    if (sortField === field) setSortOrder(sortOrder === 'asc' ? 'desc' : 'asc');
    else { setSortField(field); setSortOrder('desc'); }
  };

  const SortIcon = ({ field }: { field: SortField }) => {
    if (sortField !== field) return <span className="text-gray-400">↕</span>;
    return <span className="text-blue-600">{sortOrder === 'asc' ? '↑' : '↓'}</span>;
  };

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center h-96">
        <div className="animate-spin rounded-full h-16 w-16 border-4 border-blue-500 border-t-transparent"></div>
        <p className="mt-4 text-gray-600 font-medium">Loading audit history...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-2xl mx-auto mt-8">
        <div className="bg-red-50 border-2 border-red-200 rounded-xl p-6 shadow-lg">
          <div className="flex items-center gap-3 mb-3">
            <span className="text-3xl">⚠️</span>
            <h3 className="text-lg font-semibold text-red-900">Error Loading Data</h3>
          </div>
          <p className="text-red-700 mb-4">{error}</p>
          <button onClick={loadAuditLogs} className="px-6 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition-all transform hover:scale-105 font-medium shadow-md">🔄 Retry</button>
        </div>
      </div>
    );
  }

  return (
    <div className="w-full min-h-screen bg-gradient-to-br from-gray-50 to-blue-50 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 p-6 mb-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">📋 Audit History</h1>
              <p className="mt-2 text-gray-600">Complete audit trail of all KYC verifications</p>
            </div>
            <button onClick={loadAuditLogs} className="px-5 py-3 bg-gradient-to-r from-blue-600 to-blue-700 text-white rounded-xl hover:from-blue-700 hover:to-blue-800 transition-all transform hover:scale-105 shadow-lg flex items-center gap-2 font-semibold">
              <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" /></svg>
              Refresh
            </button>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4 mb-6">
          <div className="bg-white rounded-xl shadow-lg p-5 border-l-4 border-blue-500 hover:shadow-xl transition-shadow">
            <div className="text-sm font-medium text-gray-600 mb-1">Total Records</div>
            <div className="text-3xl font-bold text-gray-900">{stats.total}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-5 border-l-4 border-green-500 hover:shadow-xl transition-shadow">
            <div className="text-sm font-medium text-gray-600 mb-1">✓ Approved</div>
            <div className="text-3xl font-bold text-green-600">{stats.approved}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-5 border-l-4 border-red-500 hover:shadow-xl transition-shadow">
            <div className="text-sm font-medium text-gray-600 mb-1">✗ Rejected</div>
            <div className="text-3xl font-bold text-red-600">{stats.rejected}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-5 border-l-4 border-yellow-500 hover:shadow-xl transition-shadow">
            <div className="text-sm font-medium text-gray-600 mb-1">⏱ Pending</div>
            <div className="text-3xl font-bold text-yellow-600">{stats.pending}</div>
          </div>
          <div className="bg-white rounded-xl shadow-lg p-5 border-l-4 border-red-500 hover:shadow-xl transition-shadow">
            <div className="text-sm font-medium text-gray-600 mb-1">🔴 High Risk</div>
            <div className="text-3xl font-bold text-red-600">{stats.highRisk}</div>
          </div>
        </div>

        <div className="bg-white rounded-2xl shadow-xl border border-gray-200 overflow-hidden">
          <div className="p-6 space-y-4">
            <div className="relative">
              <input type="text" placeholder="🔍 Search by customer name, session ID, document type, or status..." value={searchTerm} onChange={(e) => setSearchTerm(e.target.value)} className="w-full px-5 py-3 pl-12 border-2 border-gray-300 rounded-xl focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all" />
              <span className="absolute left-4 top-1/2 transform -translate-y-1/2 text-gray-400 text-xl">🔍</span>
              {searchTerm && <button onClick={() => setSearchTerm('')} className="absolute right-4 top-1/2 transform -translate-y-1/2 text-gray-400 hover:text-gray-600">✕</button>}
            </div>

            <div className="flex flex-wrap gap-4">
              <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)} className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-medium">
                <option value="all">All Statuses</option>
                <option value="approve">Approved</option>
                <option value="reject">Rejected</option>
                <option value="pending">Pending</option>
              </select>
              <select value={riskFilter} onChange={(e) => setRiskFilter(e.target.value)} className="px-4 py-2 border-2 border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-blue-500 font-medium">
                <option value="all">All Risk Levels</option>
                <option value="high">High Risk (≥7)</option>
                <option value="medium">Medium Risk (5-6)</option>
                <option value="low">Low Risk (&lt;5)</option>
              </select>
              <div className="ml-auto text-sm text-gray-600 flex items-center gap-2">
                <span className="font-semibold">Showing:</span>
                <span className="px-3 py-1 bg-blue-100 text-blue-800 rounded-full font-bold">
                  {filteredLogs.length > 0 
                    ? `${(currentPage - 1) * recordsPerPage + 1}-${Math.min(currentPage * recordsPerPage, filteredLogs.length)}`
                    : '0'}
                </span>
                <span>of {auditLogs.length} records</span>
              </div>
            </div>
          </div>

          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-200">
              <thead className="bg-gradient-to-r from-gray-50 to-gray-100">
                <tr>
                  <th onClick={() => handleSort('timestamp')} className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200 transition-colors">
                    <div className="flex items-center gap-2">Date/Time <SortIcon field="timestamp" /></div>
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Session ID</th>
                  <th onClick={() => handleSort('customer_name')} className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200 transition-colors">
                    <div className="flex items-center gap-2">Customer <SortIcon field="customer_name" /></div>
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Document</th>
                  <th onClick={() => handleSort('risk_score')} className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200 transition-colors">
                    <div className="flex items-center gap-2">Risk <SortIcon field="risk_score" /></div>
                  </th>
                  <th onClick={() => handleSort('status')} className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider cursor-pointer hover:bg-gray-200 transition-colors">
                    <div className="flex items-center gap-2">Status <SortIcon field="status" /></div>
                  </th>
                  <th className="px-6 py-4 text-left text-xs font-bold text-gray-700 uppercase tracking-wider">Details</th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {paginatedLogs.length === 0 ? (
                  <tr>
                    <td colSpan={7} className="px-6 py-12 text-center">
                      <div className="flex flex-col items-center gap-3">
                        <span className="text-5xl">🔍</span>
                        <p className="text-gray-500 font-medium">No records found matching your filters</p>
                        <button onClick={() => { setSearchTerm(''); setStatusFilter('all'); setRiskFilter('all'); }} className="mt-2 px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors">Clear Filters</button>
                      </div>
                    </td>
                  </tr>
                ) : (
                  paginatedLogs.map((log) => (
                    <tr key={log.id} className="hover:bg-blue-50 transition-colors">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-medium">{formatTimestamp(log.timestamp)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm font-mono text-gray-600 bg-gray-50">{log.session_id.substring(0, 8)}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900 font-semibold">{log.customer_name || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-700">{log.document_type || 'N/A'}</td>
                      <td className="px-6 py-4 whitespace-nowrap text-sm">{getRiskBadge(extractRiskScore(log))}</td>
                      <td className="px-6 py-4 whitespace-nowrap">{getStatusBadge(log.status)}</td>
                      <td className="px-6 py-4 text-sm">
                        <button onClick={() => alert(`Details:\n\n${JSON.stringify(log.details, null, 2)}`)} className="text-blue-600 hover:text-blue-800 hover:underline font-semibold">
                          View Details →
                        </button>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>

          {/* Pagination Controls */}
          {filteredLogs.length > 0 && totalPages > 1 && (
            <div className="bg-gradient-to-r from-gray-50 to-gray-100 px-6 py-4 border-t border-gray-200">
              <div className="flex items-center justify-between">
                <div className="text-sm text-gray-700">
                  Showing <span className="font-bold text-blue-600">{(currentPage - 1) * recordsPerPage + 1}</span> - <span className="font-bold text-blue-600">{Math.min(currentPage * recordsPerPage, filteredLogs.length)}</span> of <span className="font-bold text-gray-900">{filteredLogs.length}</span> records
                </div>
                <div className="flex items-center gap-2">
                  <button
                    onClick={handlePrevious}
                    disabled={currentPage === 1}
                    className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-blue-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-gray-300 transition-all font-medium shadow-sm"
                  >
                    ← Previous
                  </button>
                  <div className="flex items-center gap-1">
                    {Array.from({ length: Math.min(totalPages, 7) }, (_, i) => {
                      let pageNumber;
                      if (totalPages <= 7) {
                        pageNumber = i + 1;
                      } else if (currentPage <= 4) {
                        pageNumber = i + 1;
                      } else if (currentPage >= totalPages - 3) {
                        pageNumber = totalPages - 6 + i;
                      } else {
                        pageNumber = currentPage - 3 + i;
                      }
                      return (
                        <button
                          key={pageNumber}
                          onClick={() => handlePageChange(pageNumber)}
                          className={`w-10 h-10 rounded-lg font-bold transition-all shadow-sm ${
                            currentPage === pageNumber
                              ? 'bg-blue-600 text-white border-2 border-blue-600 transform scale-110'
                              : 'bg-white text-gray-700 border-2 border-gray-300 hover:bg-blue-50 hover:border-blue-400'
                          }`}
                        >
                          {pageNumber}
                        </button>
                      );
                    })}
                  </div>
                  <button
                    onClick={handleNext}
                    disabled={currentPage === totalPages}
                    className="px-4 py-2 bg-white border-2 border-gray-300 text-gray-700 rounded-lg hover:bg-blue-50 hover:border-blue-400 disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-white disabled:hover:border-gray-300 transition-all font-medium shadow-sm"
                  >
                    Next →
                  </button>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}