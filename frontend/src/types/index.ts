/**
 * TypeScript Type Definitions for KYC/AML System
 */

export interface DocumentData {
  document_type: string;
  extracted_fields: {
    name: string;
    date_of_birth?: string;
    id_number: string;
    document_type: string;
    address?: string;
    [key: string]: any;
  };
  metadata?: {
    upload_timestamp?: string;
    confidence_score?: number;
  };
}

export interface AgentEvent {
  session_id: string;
  agent: string;
  step: string;
  status: 'processing' | 'completed' | 'error';
  message: string;
  data?: any;
  timestamp: string;
}

// StreamEvent for UI display (extends AgentEvent with type field)
export interface StreamEvent {
  type: string;
  agent?: string;
  message: string;
  details?: any;
  timestamp: string;
}

export interface FinalDecision {
  session_id?: string;
  decision: 'APPROVE' | 'REJECT' | 'ESCALATE' | 'ERROR';
  risk_score: number;
  risk_category: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  confidence: number;
  explanation: string;
  recommendation: string;
  extracted_data: any;
  audit_trail: any;
  timestamp: string;
}

export interface ProcessingResponse {
  session_id: string;
  status: string;
  message: string;
  stream_url: string;
}

export type RiskCategory = 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
export type Decision = 'APPROVE' | 'REJECT' | 'ESCALATE' | 'ERROR';