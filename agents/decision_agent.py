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
            risk_score = assessment_result.get('risk_score', 0.5)
            risk_category = assessment_result.get('risk_category', 'MEDIUM')
            reasoning_conclusion = reasoning_result.get('reasoning_conclusion', 'ESCALATE')
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
            
            logger.info(f"Decision made: {decision}")
            return result
            
        except Exception as e:
            logger.error(f"Decision making failed: {str(e)}")
            return {
                "decision": "ESCALATE",
                "recommendation": "System error - manual review required",
                "risk_score": 1.0,
                "risk_category": "HIGH",
                "confidence": 0.0,
                "explanation": f"Decision error: {str(e)}",
                "audit_trail": {},
                "agent": "DecisionAgent",
                "status": "error"
            }
    
    def _make_decision(self, risk_score: float, risk_category: str, 
                       reasoning_conclusion: str, confidence: float) -> tuple:
        """Determine final decision"""
        
        # Auto-reject for sanctions
        if reasoning_conclusion == "REJECT":
            return "REJECT", "Application rejected due to sanctions/critical issues"
        
        # Auto-approve for low risk + high confidence
        if (risk_score < settings.auto_approve_threshold and 
            confidence > settings.auto_approve_threshold and
            risk_category == "LOW"):
            return "APPROVE", "Application approved - low risk profile"
        
        # Auto-reject for very high risk
        if risk_score > (1 - settings.auto_reject_threshold):
            return "REJECT", "Application rejected - high risk profile"
        
        # Otherwise escalate
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
        explanation += f"Risk Score: {assessment.get('risk_score', 0):.2f}\n\n"
        
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