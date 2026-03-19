/**
 * API Client for KYC/AML Backend
 */
import type { DocumentData, ProcessingResponse } from '../types';

const API_BASE_URL = 'http://localhost:8000/api';

export const api = {
  /**
   * Initiate KYC document processing
   */
  async processDocument(document: DocumentData): Promise<ProcessingResponse> {
    const response = await fetch(`${API_BASE_URL}/kyc/process`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(document),
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