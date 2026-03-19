"""
Assessment Agent - Context-Aware Risk Scoring
"""
from typing import Dict, Any
from loguru import logger
from config.settings import settings


class AssessmentAgent:
    """Assessment Agent for dynamic risk scoring"""
    
    def __init__(self):
        logger.info("Assessment Agent initialized")
    
    def assess(self, reasoning_result: Dict[str, Any], verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """Assign context-aware risk score"""
        logger.info("Starting risk assessment")
        
        try:
            base_score = self._calculate_base_score(reasoning_result, verification_result)
            risk_category = self._categorize_risk(base_score)
            risk_factors = self._identify_risk_factors(reasoning_result, verification_result)
            
            result = {
                "risk_score": base_score,
                "risk_category": risk_category,
                "risk_factors": risk_factors,
                "agent": "AssessmentAgent",
                "status": "success"
            }
            
            logger.info(f"Assessment completed: {risk_category} ({base_score:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Assessment failed: {str(e)}")
            return {
                "risk_score": 10.0,
                "risk_category": "CRITICAL",
                "risk_factors": [f"Assessment error: {str(e)}"],
                "agent": "AssessmentAgent",
                "status": "error"
            }
    
    def _calculate_base_score(self, reasoning: Dict, verification: Dict) -> float:
        """Calculate base risk score (1-10 scale, higher=riskier)"""
        score = 5.0  # Start neutral (middle of 1-10)
        
        # Sanctions/PEP flags = maximum risk
        matches = verification.get('matches', {})
        if matches.get('sanctions', {}).get('status') == 'flagged':
            return 10.0
        if matches.get('pep', {}).get('status') == 'flagged':
            score += 3.0
        
        # Verification status
        ver_status = verification.get('verification_status')
        if ver_status == 'VERIFIED':
            score -= 3.0
        elif ver_status == 'PARTIAL':
            score += 1.0
        elif ver_status == 'FAILED':
            score += 4.0
        
        # Reasoning confidence
        confidence = reasoning.get('confidence', 0.5)
        score += (1 - confidence) * 3.0
        
        return max(1.0, min(10.0, score))
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level (1-10 scale)"""
        if score <= 2.5:
            return "LOW"
        elif score <= 5.0:
            return "MEDIUM"
        elif score <= 7.5:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _identify_risk_factors(self, reasoning: Dict, verification: Dict) -> list:
        """Identify specific risk factors"""
        factors = []
        factors.extend(reasoning.get('risk_factors', []))
        factors.extend(verification.get('discrepancies', []))
        return list(set(factors))  # Remove duplicates