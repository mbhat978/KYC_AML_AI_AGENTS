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
    
    # Risk Thresholds
    low_risk_threshold: float = 0.3
    medium_risk_threshold: float = 0.6
    high_risk_threshold: float = 0.8
    
    # Agent Configuration
    max_reasoning_loops: int = 3
    auto_approve_threshold: float = 0.9
    auto_reject_threshold: float = 0.2
    
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
