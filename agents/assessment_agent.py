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
    
    def assess(self, reasoning_result: Dict[str, Any], verification_result: Dict[str, Any], transaction_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """Assign context-aware risk score including AML transaction risk if available"""
        logger.info("Starting risk assessment")
        
        try:
            base_score = self._calculate_base_score(reasoning_result, verification_result, transaction_analysis)
            risk_category = self._categorize_risk(base_score)
            risk_factors = self._identify_risk_factors(reasoning_result, verification_result, transaction_analysis)
            
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
    
    def _calculate_base_score(self, reasoning: Dict, verification: Dict, transaction_analysis: Dict = None) -> float:
        """Calculate base risk score (1-10 scale, higher=riskier) including AML transaction risk"""
        score = 3.0  # Start lower to allow proper scaling
        
        # CRITICAL: Check AML transaction flags first - they can override identity scores
        if transaction_analysis:
            aml_flags = transaction_analysis.get('aml_flags', {})
            risk_level = transaction_analysis.get('risk_level', 'LOW')
            
            # Severe AML flags significantly elevate risk
            if aml_flags.get('sanctions_hit'):
                # Sanctions hit in transactions is CRITICAL
                return 8.5  # Override all other scores
            
            if aml_flags.get('structuring_detected'):
                # Structuring is high risk
                score += 3.5  # Brings base to 6.5
            
            if aml_flags.get('high_velocity') and risk_level == 'HIGH':
                score += 2.0
            elif aml_flags.get('high_velocity'):
                score += 1.0
            
            if aml_flags.get('pep_match'):
                score += 1.5
        
        # Sanctions/PEP flags with proper severity levels
        matches = verification.get('matches', {})
        sanctions_match = matches.get('sanctions', {})
        pep_match = matches.get('pep', {})
        
        has_sanctions = sanctions_match.get('status') == 'flagged'
        has_pep = pep_match.get('status') == 'flagged'
        
        # CRITICAL: Sanctions with CRITICAL severity (terrorism, etc.)
        if has_sanctions:
            severity = sanctions_match.get('severity', 'HIGH')
            reason = sanctions_match.get('reason', '')
            
            if severity == 'CRITICAL':
                return 8.5  # no further adjustments needed
            elif severity == 'HIGH':
                # Base HIGH sanctions = 7.0, with slight variation based on reason
                score += 4.0  
                # Add small variation for different types of financial crimes
                if 'financial' in reason.lower():
                    score += 0.2  
            else:
                score += 2.0
        
        # MEDIUM: PEP matches - distinguish between Former and Active
        if has_pep:
            pep_note = pep_match.get('note', '')
            pep_risk = pep_match.get('risk_level', 'MEDIUM')
            
            # Check if Former PEP (lower risk) or Active PEP (higher risk)
            is_former = 'former' in pep_note.lower()
            
            if is_former and pep_risk == 'MEDIUM':
                # Former PEP with MEDIUM risk → ~3.4 score
                score += 0.4  # 3.0 + 0.4 = 3.4
            elif pep_risk == 'HIGH':
                # Active PEP with HIGH risk → ~6.0 score
                score += 3.0  # 3.0 + 3.0 = 6.0
            elif pep_risk == 'MEDIUM':
                # Active PEP with MEDIUM risk → ~5.0-5.5 score
                score += 2.5
            else:
                # Default PEP handling
                score += 2.0
        
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
    
    def _identify_risk_factors(self, reasoning: Dict, verification: Dict, transaction_analysis: Dict = None) -> list:
        """Identify specific risk factors including transaction-based risks"""
        factors = []
        factors.extend(reasoning.get('risk_factors', []))
        factors.extend(verification.get('discrepancies', []))
        
        # Add transaction-based risk factors if present
        if transaction_analysis:
            aml_flags = transaction_analysis.get('aml_flags', {})
            if aml_flags.get('sanctions_hit'):
                factors.append("AML: Transaction involves sanctioned entity")
            if aml_flags.get('pep_match'):
                factors.append("AML: Transaction involves PEP")
            if aml_flags.get('high_velocity'):
                factors.append("AML: High velocity transaction pattern")
            if aml_flags.get('structuring_detected'):
                factors.append("AML: Potential structuring detected")
        
        return list(set(factors))  # Remove duplicates
