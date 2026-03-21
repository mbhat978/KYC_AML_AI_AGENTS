"""
KYC Service - Wrapper around KYC/AML Orchestrator with SSE streaming
"""
import asyncio
from typing import Dict, Any, AsyncGenerator
from datetime import datetime
import sys
import os
import json
from loguru import logger

# Add project root to sys.path for orchestrator and agents imports
# This file is at: backend/app/services/kyc_service.py
# Project root is: ../../../ (three levels up)
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Import orchestrator - will fail loudly if not found
from orchestrator import KYCOrchestrator

logger.info(f"Project root added to sys.path: {project_root}")
logger.info("KYCOrchestrator imported successfully")


class KYCServiceWithStreaming:
    """KYC Service with event streaming"""
    
    def __init__(self):
        self.active_sessions = {}
        self.session_documents = {}  # Store uploaded documents by session_id
        # Instantiate orchestrator - will fail loudly if there's an issue
        self.orchestrator = KYCOrchestrator()
        logger.info("KYC Service initialized with real orchestrator")
    
    def store_document(self, session_id: str, document: Dict[str, Any]) -> None:
        """Store uploaded document for a session"""
        self.session_documents[session_id] = document
        logger.info(f"Stored document for session {session_id}: {document.get('extracted_fields', {}).get('name', 'N/A')}")
    
    def get_document(self, session_id: str) -> Dict[str, Any]:
        """Retrieve stored document for a session"""
        return self.session_documents.get(session_id)
    
    async def process_document_with_streaming(self, document: Dict[str, Any], session_id: str) -> AsyncGenerator[str, None]:
        """Process document and yield SSE events"""
        try:
            self.active_sessions[session_id] = {"status": "processing", "started_at": datetime.now()}
            
            yield self._format_sse_event({"session_id": session_id, "agent": "System", "step": "initialization", "status": "processing", "message": "🚀 Starting KYC/AML processing...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            extracted_data = document.get('extracted_fields', {})
            
            yield self._format_sse_event({"session_id": session_id, "agent": "ExtractionAgent", "step": "extraction", "status": "processing", "message": "📄 Extracting identity information...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            yield self._format_sse_event({"session_id": session_id, "agent": "ExtractionAgent", "step": "extraction", "status": "completed", "message": f"✅ Extracted: {extracted_data.get('name', 'N/A')}", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            # Send heartbeat before potentially long operation
            yield self._format_sse_event({"session_id": session_id, "agent": "System", "step": "heartbeat", "status": "processing", "message": "🔄 Processing with AI agents...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            # Process document through real orchestrator in a thread to prevent blocking
            # CRITICAL FIX: Wrap synchronous orchestrator call in asyncio.to_thread()
            logger.info(f"Calling real orchestrator for {extracted_data.get('name', 'N/A')}")
            result = await asyncio.to_thread(self.orchestrator.process_document, document)
            logger.info(f"Orchestrator result: {result.get('decision')} - Risk: {result.get('risk_score')}")
            
            # Add session_id to the result for frontend tracking
            result['session_id'] = session_id
            
            # Send another heartbeat after processing
            yield self._format_sse_event({"session_id": session_id, "agent": "System", "step": "heartbeat", "status": "processing", "message": "✅ AI processing complete, compiling results...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            # Now send messages based on actual results
            yield self._format_sse_event({"session_id": session_id, "agent": "VerificationAgent", "step": "verification", "status": "processing", "message": "🔍 Cross-checking databases...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            # Check for sanctions/PEP flags
            ver_status = "completed"
            sanctions_flagged = False
            if 'workflow_log' in result:
                for log_entry in result['workflow_log']:
                    if log_entry.get('step') == 'verification':
                        ver_result = log_entry.get('result', {})
                        matches = ver_result.get('matches', {})
                        if matches.get('sanctions', {}).get('status') == 'flagged':
                            sanctions_flagged = True
                            ver_status = "⚠️ Sanctions list match detected!"
                        elif matches.get('pep', {}).get('status') == 'flagged':
                            ver_status = "⚠️ PEP match detected!"
                        else:
                            ver_status = "✅ Verification completed"
            
            yield self._format_sse_event({"session_id": session_id, "agent": "VerificationAgent", "step": "verification", "status": "completed", "message": ver_status, "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            yield self._format_sse_event({"session_id": session_id, "agent": "ReasoningAgent", "step": "reasoning", "status": "processing", "message": "🧠 Analyzing consistency...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            reasoning_msg = f"✅ Confidence: {result.get('confidence', 0.95)*100:.0f}%"
            yield self._format_sse_event({"session_id": session_id, "agent": "ReasoningAgent", "step": "reasoning", "status": "completed", "message": reasoning_msg, "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            yield self._format_sse_event({"session_id": session_id, "agent": "AssessmentAgent", "step": "assessment", "status": "processing", "message": "📊 Calculating risk score...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            # Dynamic risk message based on actual result
            risk_score = result.get('risk_score', 0.20)
            risk_cat = result.get('risk_category', 'LOW')
            risk_icon = "✅" if risk_cat == "LOW" else ("⚠️" if risk_cat == "MEDIUM" else ("🔴" if risk_cat == "HIGH" else "🚨"))
            risk_msg = f"{risk_icon} {risk_cat} risk ({risk_score:.2f})"
            yield self._format_sse_event({"session_id": session_id, "agent": "AssessmentAgent", "step": "assessment", "status": "completed", "message": risk_msg, "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.3)
            
            yield self._format_sse_event({"session_id": session_id, "agent": "DecisionAgent", "step": "decision", "status": "processing", "message": "⚖️ Making final determination...", "timestamp": datetime.now().isoformat()})
            await asyncio.sleep(0.2)
            
            yield self._format_sse_event({"session_id": session_id, "agent": "DecisionAgent", "step": "decision", "status": "completed", "message": f"🎯 Final Decision: {result.get('decision', 'APPROVE')}", "data": result, "timestamp": datetime.now().isoformat()})
            
            yield self._format_sse_event({"session_id": session_id, "agent": "System", "step": "complete", "status": "completed", "message": "✨ Processing complete!", "data": {"final_result": result}, "timestamp": datetime.now().isoformat()})
            
            self.active_sessions[session_id]["status"] = "completed"
            self.active_sessions[session_id]["result"] = result
            
        except Exception as e:
            logger.error(f"Streaming error: {str(e)}", exc_info=True)
            yield self._format_sse_event({"session_id": session_id, "agent": "System", "step": "error", "status": "error", "message": f"❌ Error: {str(e)}", "timestamp": datetime.now().isoformat()})
    
    def _format_sse_event(self,  data: Dict[str, Any]) -> str:
        """Format data as SSE event"""
        return f"data: {json.dumps(data)}\n\n"
    
    def get_session_status(self, session_id: str) -> Dict[str, Any]:
        """Get session status"""
        return self.active_sessions.get(session_id, {"status": "not_found"})


# Initialize service - will fail loudly if orchestrator cannot be loaded
kyc_service = KYCServiceWithStreaming()