"""
Transaction Analysis Agent for AML (Anti-Money Laundering) Detection

This agent analyzes transaction data in CSV format to identify suspicious activities,
AML red flags, and calculates risk scores based on transaction patterns.
"""

from typing import List, Optional
from pydantic import BaseModel, Field
from loguru import logger

from utils.llm_client import get_llm_client


class AMLFlags(BaseModel):
    """Schema for AML red flags"""
    sanctions_hit: bool = Field(default=False, description="Transaction involves sanctioned entity")
    pep_match: bool = Field(default=False, description="Transaction involves PEP")
    high_velocity: bool = Field(default=False, description="High velocity transaction pattern detected")
    structuring_detected: bool = Field(default=False, description="Potential structuring detected")
    smurfing_detected: bool = Field(default=False, description="Smurfing pattern detected")
    unusual_amount: bool = Field(default=False, description="Unusual transaction amounts detected")


class TransactionAnalysisResult(BaseModel):
    """Schema for transaction analysis results"""
    suspicious_activity: bool = Field(
        description="Whether suspicious activity was detected in the transactions"
    )
    aml_flags: AMLFlags = Field(
        default_factory=AMLFlags,
        description="Structured AML red flags identified"
    )
    risk_score: float = Field(
        ge=1.0,
        le=10.0,
        description="AML risk score from 1.0 (low risk) to 10.0 (high risk)"
    )
    risk_level: str = Field(
        default="LOW",
        description="Risk level: LOW, MEDIUM, HIGH"
    )
    summary: str = Field(
        description="Summary of the transaction analysis and findings"
    )


class TransactionAnalysisAgent:
    """
    Agent responsible for analyzing transaction data for AML compliance.
    
    This agent examines transaction patterns to identify:
    - Smurfing (breaking large transactions into smaller ones)
    - Structuring (avoiding reporting thresholds)
    - Large unusual transfers
    - Other suspicious financial activities
    """
    
    def __init__(self):
        """Initialize the transaction analysis agent with LLM client"""
        self.llm = get_llm_client()
        logger.info("TransactionAnalysisAgent initialized")
    
    def analyze(self, csv_data: str) -> dict:
        """
        Analyze transaction data for AML red flags and suspicious patterns.
        
        Args:
            csv_ Transaction data in CSV format as a string
            
        Returns:
            dict: Analysis results containing suspicious_activity, aml_flags, 
                  risk_score, and summary
        """
        # Handle empty or None input
        if not csv_data or csv_data.strip() == "":
            logger.info("No transaction data provided, returning default safe result")
            return {
                "suspicious_activity": False,
                "aml_flags": {
                    "sanctions_hit": False,
                    "pep_match": False,
                    "high_velocity": False,
                    "structuring_detected": False,
                    "smurfing_detected": False,
                    "unusual_amount": False
                },
                "risk_score": 1.0,
                "risk_level": "LOW",
                "summary": "No transaction data provided for analysis."
            }
        
        try:
            logger.info("Analyzing transaction data for AML patterns")
            
            # Construct the analysis prompt
            system_prompt = """You are an expert AML (Anti-Money Laundering) analyst. Analyze transaction data in CSV format and identify any suspicious activities or red flags.

Look specifically for:
1. **Smurfing**: Multiple small transactions designed to avoid detection thresholds
2. **Structuring**: Transactions deliberately structured to avoid reporting requirements (e.g., just under $10,000)
3. **Large Transfers**: Unusually large or frequent transfers that deviate from normal patterns
4. **Rapid Movement**: Money moved quickly through multiple accounts
5. **Round Numbers**: Unusual use of round numbers that may indicate layering
6. **Geographic Patterns**: Transactions to/from high-risk jurisdictions

Provide a comprehensive analysis including:
- Whether suspicious activity was detected (suspicious_activity: true/false)
- Specific AML red flags (aml_flags with boolean indicators for each type)
- A risk score from 1.0 (very low risk) to 10.0 (very high risk)
- A risk level: LOW, MEDIUM, or HIGH
- A summary of your findings

Be thorough but also consider that legitimate business transactions may sometimes appear unusual. Balance false positives with genuine risk detection."""

            user_message = f"""Transaction Data:
{csv_data}"""

            # Use generate_structured method instead of with_structured_output
            result = self.llm.generate_structured(
                system_prompt=system_prompt,
                user_message=user_message,
                schema=TransactionAnalysisResult
            )
            
            logger.info(f"Transaction analysis completed. Risk score: {result.risk_score}, Risk level: {result.risk_level}")
            
            # Return as dictionary
            return result.model_dump()
            
        except Exception as e:
            logger.error(f"Error during transaction analysis: {str(e)}")
            # Return a safe default result on error with proper structure
            return {
                "suspicious_activity": False,
                "aml_flags": {
                    "sanctions_hit": False,
                    "pep_match": False,
                    "high_velocity": False,
                    "structuring_detected": False,
                    "smurfing_detected": False,
                    "unusual_amount": False
                },
                "risk_score": 5.0,
                "risk_level": "MEDIUM",
                "summary": f"Error occurred during transaction analysis: {str(e)}"
            }
