"""
Pydantic Schemas for API Request/Response
"""
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
from datetime import datetime


class DocumentUpload(BaseModel):
    """Schema for document upload"""
    document_type: str = Field(..., description="Type of document (PAN, PASSPORT, DRIVERS_LICENSE)")
    extracted_fields: Dict[str, Any] = Field(..., description="Extracted document fields")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Document metadata")
    
    class Config:
        json_schema_extra = {
            "example": {
                "document_type": "PAN",
                "extracted_fields": {
                    "name": "Rajesh Kumar Sharma",
                    "date_of_birth": "1985-06-15",
                    "id_number": "ABCDE1234F",
                    "document_type": "PAN",
                    "address": "123 MG Road, Bangalore, Karnataka 560001"
                },
                "metadata": {
                    "upload_timestamp": "2026-03-18T10:30:00Z",
                    "confidence_score": 0.95
                }
            }
        }


class ProcessingResponse(BaseModel):
    """Response after initiating processing"""
    session_id: str = Field(..., description="Unique session ID for tracking")
    status: str = Field(..., description="Processing status")
    message: str = Field(..., description="Status message")
    stream_url: str = Field(..., description="SSE stream URL for real-time updates")


class AgentEvent(BaseModel):
    """Event emitted by an agent during processing"""
    session_id: str
    agent: str = Field(..., description="Agent name")
    step: str = Field(..., description="Processing step")
    status: str = Field(..., description="Status (processing, completed, error)")
    message: str = Field(..., description="Event message")
    data: Optional[Dict[str, Any]] = Field(default=None, description="Additional data")
    timestamp: datetime = Field(default_factory=datetime.now)


class FinalDecision(BaseModel):
    """Final KYC decision"""
    session_id: str
    decision: str = Field(..., description="APPROVE, REJECT, or ESCALATE")
    risk_score: float = Field(..., description="Risk score (0.0-1.0)")
    risk_category: str = Field(..., description="LOW, MEDIUM, HIGH, or CRITICAL")
    confidence: float = Field(..., description="Confidence score (0.0-1.0)")
    explanation: str = Field(..., description="Human-readable explanation")
    recommendation: str = Field(..., description="Recommended action")
    extracted_data: Dict[str, Any] = Field(..., description="Extracted document data")
    audit_trail: Dict[str, Any] = Field(..., description="Complete audit trail")
    timestamp: datetime = Field(default_factory=datetime.now)


class HealthResponse(BaseModel):
    """Health check response"""
    status: str
    service: str
    agents: List[str]


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    session_id: Optional[str] = None