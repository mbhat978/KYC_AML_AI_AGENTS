"""
Decision Agent - Smart Escalation with Explainability
"""
from typing import Dict, Any
from datetime import datetime
from loguru import logger
from config.settings import settings


class DecisionAgent:
    """Decision Agent for final determination with explainability"""
    
    def __init__(self):
        logger.info("Decision Agent initialized")
    
    def decide(self, assessment_result: Dict[str, Any], reasoning_result: Dict[str, Any]) -> Dict[str, Any]:
        """Make final decision with full audit trail"""
        logger.info("Making final decision")
        
        try:
            risk_score = assessment_result.get('risk_score', 5.0)  # Default to MEDIUM on 1-10 scale
            risk_category = assessment_result.get('risk_category', 'MEDIUM')
            reasoning_conclusion = reasoning_result.get('reasoning_conclusion', 'ESCALATE').upper()
            confidence = reasoning_result.get('confidence', 0.5)
            
            # Make decision based on rules and thresholds
            decision, recommendation = self._make_decision(
                risk_score,
                risk_category,
                reasoning_conclusion,
                confidence
            )
            
            # Generate audit trail
            audit_trail = self._generate_audit_trail(
                decision,
                assessment_result,
                reasoning_result
            )
            
            # Generate explanation
            explanation = self._generate_explanation(
                decision,
                risk_category,
                reasoning_conclusion,
                assessment_result
            )
            
            result = {
                "decision": decision,
                "recommendation": recommendation,
                "risk_score": risk_score,
                "risk_category": risk_category,
                "confidence": confidence,
                "explanation": explanation,
                "audit_trail": audit_trail,
                "timestamp": datetime.now().isoformat(),
                "agent": "DecisionAgent",
                "status": "success"
            }
            
            logger.info(f"Decision made: {decision} (risk_score: {risk_score:.2f}, category: {risk_category})")
            return result
            
        except Exception as e:
            logger.error(f"Decision making failed: {str(e)}")
            return {
                "decision": "ESCALATE",
                "recommendation": "System error - manual review required",
                "risk_score": 5.0,  # Default to MEDIUM on 1-10 scale
                "risk_category": "HIGH",
                "confidence": 0.0,
                "explanation": f"Decision error: {str(e)}",
                "audit_trail": {},
                "agent": "DecisionAgent",
                "status": "error"
            }
    
    def _make_decision(self, risk_score: float, risk_category: str, 
                       reasoning_conclusion: str, confidence: float) -> tuple:
        """
        Determine final decision using 1-10 risk score scale
        
        Risk Score Scale (1-10):
        - 1.0-2.5: LOW
        - 2.5-5.0: MEDIUM  
        - 5.0-7.5: HIGH
        - 7.5-10.0: CRITICAL
        
        Confidence Scale (0.0-1.0): unchanged
        
        Decision Priority:
        1. Auto-approve LOW risk first (prevents false rejections)
        2. Auto-reject CRITICAL risk or sanctions
        3. Escalate everything else
        """
        #print(f"DEBUG: Score: {settings.auto_approve_threshold}, Conf: {confidence}, Cat: {risk_category}, Reason: {reasoning_conclusion}")
        # PRIORITY 1: Auto-approve for LOW risk + high confidence
        # Check this FIRST to prevent LOW risk documents from being incorrectly rejected
        # risk_score <= 2.5 (LOW range) AND confidence > 0.85 AND category is LOW
        if (risk_score < settings.auto_approve_threshold and 
            confidence > settings.confidence_threshold and
            risk_category == "LOW"):
            return "APPROVE", "Application approved - low risk profile"
        
        # PRIORITY 2: Auto-reject for sanctions/critical issues or CRITICAL risk scores
        # Only reject for actual critical issues or very high risk scores
        if reasoning_conclusion == "REJECT" or risk_score >= settings.auto_reject_threshold:
            reason = "Application rejected due to sanctions/critical issues" if reasoning_conclusion == "REJECT" else f"Application rejected - critical risk profile (score: {risk_score:.2f}/10)"
            return "REJECT", reason
        
        # PRIORITY 3: Otherwise escalate for manual review
        return "ESCALATE", f"Manual review required - {risk_category} risk"
    
    def _generate_audit_trail(self, decision: str, assessment: Dict, reasoning: Dict) -> Dict:
        """Generate complete audit trail"""
        return {
            "decision": decision,
            "risk_assessment": {
                "score": assessment.get('risk_score'),
                "category": assessment.get('risk_category'),
                "factors": assessment.get('risk_factors', [])
            },
            "reasoning": {
                "conclusion": reasoning.get('reasoning_conclusion'),
                "confidence": reasoning.get('confidence'),
                "analysis": reasoning.get('analysis'),
                "loops_used": reasoning.get('reasoning_loops_used', 0)
            },
            "timestamp": datetime.now().isoformat(),
            "system_version": "1.0.0"
        }
    
    def _generate_explanation(self, decision: str, risk_category: str,
                             reasoning_conclusion: str, assessment: Dict) -> str:
        """Generate human-readable explanation"""
        explanation = f"DECISION: {decision}\n\n"
        explanation += f"Risk Level: {risk_category}\n"
        explanation += f"Risk Score: {assessment.get('risk_score', 0):.2f} (scale: 1-10)\n\n"
        
        explanation += "Key Factors:\n"
        for factor in assessment.get('risk_factors', []):
            explanation += f"- {factor}\n"
        
        explanation += f"\nRecommendation: {reasoning_conclusion}\n"
        
        if decision == "APPROVE":
            explanation += "\nThis application has been automatically approved."
        elif decision == "REJECT":
            explanation += "\nThis application has been rejected."
        else:
            explanation += "\nThis application requires manual review by a compliance officer."
        
        return explanation