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
        score = 3.0  # Start lower to allow proper scaling
        
        # Sanctions/PEP flags with proper severity levels
        matches = verification.get('matches', {})
        sanctions_match = matches.get('sanctions', {})
        pep_match = matches.get('pep', {})
        
        has_sanctions = sanctions_match.get('status') == 'flagged'
        has_pep = pep_match.get('status') == 'flagged'
        
        # CRITICAL: Sanctions with CRITICAL severity (terrorism, etc.)
        if has_sanctions:
            severity = sanctions_match.get('severity', 'HIGH')
            if severity == 'CRITICAL':
                return 8.5  # Matches risk85 samples - no further adjustments needed
            elif severity == 'HIGH':
                score += 4.0  # Adds to 7.0 for risk70 samples
            else:
                score += 2.0
        
        # MEDIUM: PEP matches (should result in ~6.0 score)
        if has_pep:
            pep_risk = pep_match.get('risk_level', 'MEDIUM')
            if pep_risk == 'HIGH':
                score += 3.5  # Active high-risk PEP
            else:
                score += 3.0  # Former/Medium PEP -> results in 6.0
        
        # Verification status adjustments (only if no sanctions/PEP)
        if not has_sanctions and not has_pep:
            ver_status = verification.get('verification_status', '').upper()
            if ver_status == 'VERIFIED':
                score -= 1.5  # Reduce risk for verified IDs
            elif ver_status == 'PARTIAL':
                score += 0.5  # Small increase for partial verification
            elif ver_status == 'FAILED':
                score += 2.0  # Increase for failed verification
        
        # Reasoning confidence penalty - only apply if NO sanctions (sanctions are definitive)
        # PEP matches can have confidence penalty as they need further review
        if not has_sanctions:
            confidence = reasoning.get('confidence', 0.5)
            # Only apply penalty if confidence is very low
            if confidence < 0.5:
                penalty = (0.5 - confidence) * 2.0  # Max +1.0 penalty
                score += penalty
        
        return max(1.0, min(10.0, score))
    
    def _categorize_risk(self, score: float) -> str:
        """Categorize risk level (1-10 scale)"""
        if score <= 3.0:
            return "LOW"
        elif score <= 6.5:
            return "MEDIUM"
        elif score <= 8.0:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def _identify_risk_factors(self, reasoning: Dict, verification: Dict) -> list:
        """Identify specific risk factors"""
        factors = []
        factors.extend(reasoning.get('risk_factors', []))
        factors.extend(verification.get('discrepancies', []))
        return list(set(factors))  # Remove duplicates