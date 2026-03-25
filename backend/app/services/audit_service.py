"""
Audit Service for logging KYC verification events to the database.
"""
from typing import Optional
from backend.app.database import SessionLocal
from backend.app.models.db_models import VerificationRecord


def log_audit_event(
    session_id: str,
    status: str,
    customer_name: str = "Unknown",
    document_type: Optional[str] = None,
    risk_score: Optional[float] = None,
    details: Optional[dict] = None
):
    """
    Log an audit event (AI decision or human override) to the database.
    
    Args:
        session_id: Unique identifier for the KYC session
        status: Status of the verification (e.g., "AI_APPROVE", "HUMAN_ESCALATE")
        customer_name: Name of the customer being verified
        document_type: Type of document being verified (e.g., "passport", "pan_card")
        risk_score: Calculated risk score (0-100)
        details: Additional details as a dictionary (reasoning, flags, etc.)
    """
    try:
        with SessionLocal() as db:
            new_record = VerificationRecord(
                session_id=session_id,
                status=status,
                customer_name=customer_name,
                document_type=document_type,
                risk_score=risk_score,
                details=details
            )
            db.add(new_record)
            db.commit()
            print(f"✅ Audit event logged: {status} for session {session_id}")
    except Exception as e:
        print(f"❌ Failed to log audit event: {str(e)}")
        raise