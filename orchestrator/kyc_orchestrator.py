"""
KYC/AML Multi-Agent Orchestrator with LangGraph StateGraph
Coordinates the flow between agents with shared state management
"""
from langgraph.graph import StateGraph, START, END
from typing import TypedDict, Dict, Any, Optional
from loguru import logger
from agents import (
    ExtractionAgent,
    VerificationAgent,
    ReasoningAgent,
    AssessmentAgent,
    DecisionAgent
)
from config.settings import settings


class KYCState(TypedDict):
    """Global state for the KYC pipeline workflow."""
    document: Dict[str, Any]
    extraction_result: Dict[str, Any]
    extracted_data: Dict[str, Any]
    verification_result: Dict[str, Any]
    reasoning_result: Dict[str, Any]
    assessment_result: Dict[str, Any]
    decision_result: Dict[str, Any]
    workflow_log: list


class KYCOrchestrator:
    """Orchestrator for Multi-Agent KYC/AML System with LangGraph StateGraph"""
    
    def __init__(self):
        self.extraction_agent = ExtractionAgent()
        self.verification_agent = VerificationAgent()
        self.reasoning_agent = ReasoningAgent()
        self.assessment_agent = AssessmentAgent()
        self.decision_agent = DecisionAgent()
        logger.info("KYC Orchestrator initialized")
        
        # Build the LangGraph StateGraph
        self._build_graph()
        logger.info("LangGraph StateGraph compiled successfully")
    
    def extract_node(self, state: KYCState) -> Dict[str, Any]:
        """Node wrapper for extraction agent."""
        logger.info("\n[STEP 1] EXTRACTION")
        extraction_result = self.extraction_agent.extract(state["document"])
        
        workflow_log = state.get("workflow_log", [])
        workflow_log.append({"step": "extraction", "result": extraction_result})
        
        extracted_data = extraction_result.get('extracted_data', {})
        logger.info(f"Extracted: {extracted_data.get('name')} - {extracted_data.get('id_number')}")
        
        return {
            "extraction_result": extraction_result,
            "extracted_data": extracted_data,
            "workflow_log": workflow_log
        }
    
    def verify_node(self, state: KYCState) -> Dict[str, Any]:
        """Node wrapper for verification agent."""
        logger.info("\n[STEP 2] VERIFICATION")
        extracted_data = state["extracted_data"]
        verification_result = self.verification_agent.verify(extracted_data)
        
        workflow_log = state.get("workflow_log", [])
        workflow_log.append({"step": "verification", "result": verification_result})
        
        logger.info(f"Verification Status: {verification_result['verification_status']}")
        
        return {
            "verification_result": verification_result,
            "workflow_log": workflow_log
        }
    
    def reason_node(self, state: KYCState) -> Dict[str, Any]:
        """Node wrapper for reasoning agent."""
        logger.info("\n[STEP 3] REASONING")
        extraction_result = state["extraction_result"]
        verification_result = state["verification_result"]
        reasoning_result = self.reasoning_agent.reason(extraction_result, verification_result)
        
        workflow_log = state.get("workflow_log", [])
        workflow_log.append({"step": "reasoning", "result": reasoning_result})
        
        logger.info(f"Conclusion: {reasoning_result['reasoning_conclusion']}")
        
        return {
            "reasoning_result": reasoning_result,
            "workflow_log": workflow_log
        }
    
    def assess_node(self, state: KYCState) -> Dict[str, Any]:
        """Node wrapper for assessment agent."""
        logger.info("\n[STEP 4] ASSESSMENT")
        reasoning_result = state["reasoning_result"]
        verification_result = state["verification_result"]
        assessment_result = self.assessment_agent.assess(reasoning_result, verification_result)
        
        workflow_log = state.get("workflow_log", [])
        workflow_log.append({"step": "assessment", "result": assessment_result})
        
        logger.info(f"Risk: {assessment_result['risk_category']} ({assessment_result['risk_score']:.2f})")
        
        return {
            "assessment_result": assessment_result,
            "workflow_log": workflow_log
        }
    
    def decide_node(self, state: KYCState) -> Dict[str, Any]:
        """Node wrapper for decision agent."""
        logger.info("\n[STEP 5] DECISION")
        assessment_result = state["assessment_result"]
        reasoning_result = state["reasoning_result"]
        decision_result = self.decision_agent.decide(assessment_result, reasoning_result)
        
        workflow_log = state.get("workflow_log", [])
        workflow_log.append({"step": "decision", "result": decision_result})
        
        logger.info(f"Final Decision: {decision_result['decision']}")
        
        return {
            "decision_result": decision_result,
            "workflow_log": workflow_log
        }
    
    def _build_graph(self):
        """Build the LangGraph StateGraph for the KYC pipeline."""
        # Initialize the StateGraph
        workflow = StateGraph(KYCState)
        
        # Add all nodes to the workflow
        workflow.add_node("extract", self.extract_node)
        workflow.add_node("verify", self.verify_node)
        workflow.add_node("reason", self.reason_node)
        workflow.add_node("assess", self.assess_node)
        workflow.add_node("decide", self.decide_node)
        
        # Add linear edges: START -> extract -> verify -> reason -> assess -> decide -> END
        workflow.add_edge(START, "extract")
        workflow.add_edge("extract", "verify")
        workflow.add_edge("verify", "reason")
        workflow.add_edge("reason", "assess")
        workflow.add_edge("assess", "decide")
        workflow.add_edge("decide", END)
        
        # Compile the graph
        self.graph = workflow.compile()
    
    def process_document(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process a document through the complete KYC pipeline using LangGraph StateGraph.
        
        Args:
            document: Dictionary containing the document data (type, content, etc.)
            
        Returns:
            Dictionary containing results from all pipeline stages
        """
        logger.info("=" * 60)
        logger.info("Starting KYC/AML processing")
        logger.info("=" * 60)
        
        try:
            # Initialize the state and invoke the LangGraph StateGraph
            initial_state: KYCState = {
                "document": document,
                "workflow_log": []
            }
            final_state = self.graph.invoke(initial_state)
            
            # Extract results from final state
            extraction_result = final_state.get("extraction_result", {})
            extracted_data = final_state.get("extracted_data", {})
            decision_result = final_state.get("decision_result", {})
            workflow_log = final_state.get("workflow_log", [])
            
            # Handle extraction errors
            if extraction_result.get('status') == 'error':
                return self._create_error_response("Extraction failed", workflow_log)
            
            # Include extraction confidence in extracted_data for UI display
            # Remove any existing 'confidence' field to avoid duplication
            extracted_data_clean = {k: v for k, v in extracted_data.items() if k != 'confidence'}
            extracted_data_with_confidence = {
                **extracted_data_clean,
                "extraction_confidence": extraction_result.get('confidence', 0.85)
            }
            
            # Compile final response in the same format as before for backward compatibility
            final_response = {
                "decision": decision_result.get('decision'),
                "risk_score": decision_result.get('risk_score'),
                "risk_category": decision_result.get('risk_category'),
                "confidence": decision_result.get('confidence'),
                "explanation": decision_result.get('explanation'),
                "recommendation": decision_result.get('recommendation'),
                "audit_trail": decision_result.get('audit_trail', {}),
                "workflow_log": workflow_log,
                "extracted_data": extracted_data_with_confidence,
                "timestamp": decision_result.get('timestamp')
            }
            
            logger.info("\n" + "=" * 60)
            logger.info(f"FINAL DECISION: {decision_result.get('decision')}")
            logger.info("=" * 60)
            
            return final_response
            
        except Exception as e:
            logger.error(f"Orchestration failed: {str(e)}")
            return self._create_error_response(f"System error: {str(e)}", [])
    
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