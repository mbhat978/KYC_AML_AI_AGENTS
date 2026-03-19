"""
KYC/AML Multi-Agent Orchestrator
Coordinates the flow between agents with cyclic reasoning capability
"""
from typing import Dict, Any
from loguru import logger
from agents import (
    ExtractionAgent,
    VerificationAgent,
    ReasoningAgent,
    AssessmentAgent,
    DecisionAgent
)
from config.settings import settings


class KYCOrchestrator:
    """Orchestrator for Multi-Agent KYC/AML System"""
    
    def __init__(self):
        self.extraction_agent = ExtractionAgent()
        self.verification_agent = VerificationAgent()
        self.reasoning_agent = ReasoningAgent()
        self.assessment_agent = AssessmentAgent()
        self.decision_agent = DecisionAgent()
        logger.info("KYC Orchestrator initialized")
    
    def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Process a document through the multi-agent system"""
        logger.info("=" * 60)
        logger.info("Starting KYC/AML processing")
        logger.info("=" * 60)
        
        workflow_log = []
        
        try:
            # STEP 1: EXTRACT
            logger.info("\n[STEP 1] EXTRACTION")
            extraction_result = self.extraction_agent.extract(document)
            workflow_log.append({"step": "extraction", "result": extraction_result})
            
            if extraction_result['status'] == 'error':
                return self._create_error_response("Extraction failed", workflow_log)
            
            extracted_data = extraction_result['extracted_data']
            logger.info(f"Extracted: {extracted_data.get('name')} - {extracted_data.get('id_number')}")
            
            # STEP 2: VERIFY
            logger.info("\n[STEP 2] VERIFICATION")
            verification_result = self.verification_agent.verify(extracted_data)
            workflow_log.append({"step": "verification", "result": verification_result})
            logger.info(f"Verification Status: {verification_result['verification_status']}")
            
            # STEP 3: REASON
            logger.info("\n[STEP 3] REASONING")
            reasoning_result = self.reasoning_agent.reason(extraction_result, verification_result)
            workflow_log.append({"step": "reasoning", "result": reasoning_result})
            logger.info(f"Conclusion: {reasoning_result['reasoning_conclusion']}")
            
            # STEP 4: ASSESS
            logger.info("\n[STEP 4] ASSESSMENT")
            assessment_result = self.assessment_agent.assess(reasoning_result, verification_result)
            workflow_log.append({"step": "assessment", "result": assessment_result})
            logger.info(f"Risk: {assessment_result['risk_category']} ({assessment_result['risk_score']:.2f})")
            
            # STEP 5: DECIDE
            logger.info("\n[STEP 5] DECISION")
            decision_result = self.decision_agent.decide(assessment_result, reasoning_result)
            workflow_log.append({"step": "decision", "result": decision_result})
            logger.info(f"Final Decision: {decision_result['decision']}")
            
            # Compile final response
            final_response = {
                "decision": decision_result['decision'],
                "risk_score": decision_result['risk_score'],
                "risk_category": decision_result['risk_category'],
                "confidence": decision_result['confidence'],
                "explanation": decision_result['explanation'],
                "recommendation": decision_result['recommendation'],
                "audit_trail": decision_result['audit_trail'],
                "workflow_log": workflow_log,
                "extracted_data": extracted_data,
                "timestamp": decision_result['timestamp']
            }
            
            logger.info("\n" + "=" * 60)
            logger.info(f"FINAL DECISION: {decision_result['decision']}")
            logger.info("=" * 60)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            return self._create_error_response(f"System error: {str(e)}", workflow_log)
    
    def _create_error_response(self, error_msg: str, workflow_log: list) -> Dict[str, Any]:
        """Create error response"""
        return {
            "decision": "ERROR",
            "risk_score": 1.0,
            "risk_category": "HIGH",
            "confidence": 0.0,
            "explanation": error_msg,
            "recommendation": "System error - manual review required",
            "audit_trail": {},
            "workflow_log": workflow_log,
            "error": error_msg
        }