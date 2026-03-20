"""
Configuration settings for the KYC/AML Multi-Agent System
"""
from pydantic_settings import BaseSettings
from typing import Literal


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # LLM Configuration
    openai_api_key: str = ""
    openai_model: str = "gpt-4-turbo-preview"
    anthropic_api_key: str = ""
    anthropic_model: str = "claude-3-opus-20240229"
    default_llm_provider: Literal["openai", "anthropic"] = "openai"
    
    # System Configuration
    log_level: str = "INFO"
    environment: str = "development"
    
    # Risk Thresholds (DEPRECATED - for reference only)
    # These were on 0.0-1.0 scale, now using 1-10 scale below
    low_risk_threshold: float = 3.0
    medium_risk_threshold: float = 6.0
    high_risk_threshold: float = 8.0
    
    # Agent Configuration
    max_reasoning_loops: int = 3
    
    # Decision Thresholds (1-10 scale to match AssessmentAgent risk_score)
    # Risk score ranges: 1-2.5=LOW, 2.5-5.0=MEDIUM, 5.0-7.5=HIGH, 7.5-10.0=CRITICAL
    auto_approve_threshold: float = 2.5  # Approve if risk_score <= 2.5 (LOW)
    auto_reject_threshold: float = 7.5   # Reject if risk_score >= 7.5 (HIGH/CRITICAL)
    confidence_threshold: float = 0.85    # Confidence threshold (still 0.0-1.0 scale)
    
    # Mock Database Configuration
    use_mock_databases: bool = True
    mock_db_delay: float = 0.5
    
    # Feature Flags
    enable_explainability: bool = True
    enable_audit_trail: bool = True
    strict_mode: bool = False
    
    class Config:
        env_file = ".env"
        case_sensitive = False


# Global settings instance
settings = Settings()