from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from datetime import datetime
from app.database import Base


class VerificationRecord(Base):
    __tablename__ = "verification_records"
    __table_args__ = {'extend_existing': True}

    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(String, index=True)
    customer_name = Column(String, default="Unknown")
    document_type = Column(String, nullable=True)
    risk_score = Column(Float, nullable=True)
    status = Column(String)
    details = Column(JSON, nullable=True)
    timestamp = Column(DateTime, default=datetime.utcnow)