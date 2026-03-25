/**
 * API Client for KYC/AML Backend
 */
import type { DocumentData, ProcessingResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  /**
   * Upload a file (PDF, JPG, PNG) for KYC processing
   */
  async uploadFile(file: File, transactionCsvData?: string, analysisType?: string): Promise<ProcessingResponse> {
    const formData = new FormData();
    formData.append('file', file);
    
    // Add optional fields for AML processing
    if (transactionCsvData) {
      formData.append('transaction_csv_data', transactionCsvData);
    }
    if (analysisType) {
      formData.append('analysis_type', analysisType);
    }

    const response = await fetch(`${API_BASE_URL}/kyc/upload`, {
      method: 'POST',
      body: formData,
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Initiate KYC document processing (JSON format)
   */
  async processDocument(document: DocumentData, transactionCsvData?: string, analysisType?: string): Promise<ProcessingResponse> {
    const payload: any = {
      ...document,
    };
    
    // Add optional fields for AML processing
    if (transactionCsvData) {
      payload.transaction_csv_data = transactionCsvData;
    }
    if (analysisType) {
      payload.analysis_type = analysisType;
    }

    const response = await fetch(`${API_BASE_URL}/kyc/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(payload),
    });

    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get session status
   */
  async getSessionStatus(sessionId: string): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/kyc/status/${sessionId}`);
    
    if (!response.ok) {
      throw new Error(`API Error: ${response.statusText}`);
    }

    return response.json();
  },

  /**
   * Get health status
   */
  async getHealth(): Promise<any> {
    const response = await fetch(`${API_BASE_URL}/health`);
    return response.json();
  },
};

/**
 * Resume processing after human override decision
 */
export const resumeProcessing = async (threadId: string, decision: 'APPROVE' | 'REJECT') => {
  const response = await fetch(`${API_BASE_URL}/upload/resume`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ thread_id: threadId, decision })
  });
  if (!response.ok) throw new Error('Failed to resume processing');
  return response.json();
};
