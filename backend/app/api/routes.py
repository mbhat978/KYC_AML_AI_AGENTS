"""API Routes for KYC/AML System"""
from fastapi import APIRouter, HTTPException
from sse_starlette.sse import EventSourceResponse
import uuid
from loguru import logger

from backend.app.models.schemas import DocumentUpload, ProcessingResponse
from backend.app.services.kyc_service import kyc_service

router = APIRouter()


@router.post("/kyc/process", response_model=ProcessingResponse)
async def process_kyc_document(document: DocumentUpload):
    """Initiate KYC document processing"""
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"Processing KYC document for session: {session_id}")
        
        # Store the uploaded document for this session
        document_dict = document.dict()
        kyc_service.store_document(session_id, document_dict)
        logger.info(f"Stored document: {document_dict.get('extracted_fields', {}).get('name', 'N/A')}")
        
        return ProcessingResponse(
            session_id=session_id,
            status="processing",
            message="KYC processing initiated",
            stream_url=f"/api/kyc/stream/{session_id}"
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kyc/stream/{session_id}")
async def stream_kyc_processing(session_id: str):
    """Stream real-time processing events via SSE"""
    try:
        logger.info(f"SSE stream started for session: {session_id}")
        
        # Retrieve the uploaded document for this session
        document = kyc_service.get_document(session_id)
        
        if not document:
            # Fallback to sample document if no upload found
            logger.warning(f"No document found for session {session_id}, using sample")
            document = {
                "document_type": "PAN",
                "extracted_fields": {
                    "name": "Rajesh Kumar Sharma",
                    "date_of_birth": "1985-06-15",
                    "id_number": "ABCDE1234F",
                    "document_type": "PAN",
                    "address": "123 MG Road, Bangalore, Karnataka 560001"
                }
            }
        else:
            logger.info(f"Using uploaded document: {document.get('extracted_fields', {}).get('name', 'N/A')}")
        
        return EventSourceResponse(
            kyc_service.process_document_with_streaming(document, session_id)
        )
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/kyc/status/{session_id}")
async def get_processing_status(session_id: str):
    """Get current status of a processing session"""
    try:
        status = kyc_service.get_session_status(session_id)
        if status.get("status") == "not_found":
            raise HTTPException(status_code=404, detail="Session not found")
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/documents/samples")
async def list_sample_documents():
    """List available sample documents"""
    return {
        "samples": [
            {"id": "pan_card", "name": "PAN Card - Rajesh Kumar Sharma (APPROVED)", "type": "PAN", "expected": "APPROVE"},
            {"id": "pan_card_rejected", "name": "PAN Card - Ahmed Hassan (REJECTED - Sanctions List)", "type": "PAN", "expected": "REJECT"},
            {"id": "passport", "name": "Passport - Jonathan David Miller", "type": "PASSPORT", "expected": "APPROVE"},
            {"id": "drivers_license", "name": "Driver's License - Sarah Johnson", "type": "DRIVERS_LICENSE", "expected": "APPROVE"}
        ]
    }
