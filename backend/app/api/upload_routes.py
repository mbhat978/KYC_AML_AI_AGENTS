"""
File Upload Routes for KYC Document Processing
Handles PDF, JPG, PNG uploads and extracts text for processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional
import uuid
from loguru import logger
import sys
import os

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.pdf_converter import PDFConverter
from backend.app.models.schemas import ProcessingResponse
from backend.app.services.kyc_service import kyc_service

router = APIRouter()

# Simple OCR/text extraction using PyMuPDF
def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    import fitz
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        logger.error(f"PDF text extraction failed: {e}")
        return ""

def parse_document_data(text: str, file_type: str) -> dict:
    """
    Parse extracted text to identify document type and extract fields.
    This is a simplified parser - in production, you'd use an LLM vision model.
    """
    text_upper = text.upper()
    
    # Detect document type
    if "PAN" in text_upper or "PERMANENT ACCOUNT NUMBER" in text_upper:
        doc_type = "PAN"
    elif "PASSPORT" in text_upper:
        doc_type = "PASSPORT"
    elif "DRIVER" in text_upper or "LICENSE" in text_upper:
        doc_type = "DRIVERS_LICENSE"
    else:
        doc_type = "UNKNOWN"
    
    # Extract basic fields (simplified - would use NLP/Vision AI in production)
    extracted_fields = {
        "document_type": doc_type,
        "raw_text": text,
        "confidence": 0.85  # Placeholder confidence
    }
    
    # Try to extract name (look for common patterns)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if "NAME" in line_upper and i + 1 < len(lines):
            # Next line likely contains the name
            potential_name = lines[i + 1].strip()
            if len(potential_name) > 3 and potential_name.replace(' ', '').isalpha():
                extracted_fields["name"] = potential_name.title()
                break
    
    # Try to extract PAN number
    import re
    pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
    pan_match = re.search(pan_pattern, text)
    if pan_match:
        extracted_fields["id_number"] = pan_match.group()
        extracted_fields["document_type"] = "PAN"
    
    # Try to extract dates (DD/MM/YYYY or DD-MM-YYYY)
    date_pattern = r'\d{2}[/-]\d{2}[/-]\d{4}'
    date_matches = re.findall(date_pattern, text)
    if date_matches:
        extracted_fields["date_of_birth"] = date_matches[0].replace('/', '-')
    
    # If no name found, use a placeholder
    if "name" not in extracted_fields:
        extracted_fields["name"] = "Extracted from PDF"
    
    return extracted_fields


@router.post("/kyc/upload", response_model=ProcessingResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = None
):
    """
    Upload and process a KYC document (PDF, JPG, PNG)
    Extracts text and initiates KYC processing
    """
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"File upload for session {session_id}: {file.filename} ({file.content_type})")
        
        # Read file content
        file_content = await file.read()
        
        # Validate file type
        supported_types = ["application/pdf", "image/jpeg", "image/jpg", "image/png"]
        if file.content_type not in supported_types:
            raise HTTPException(
                status_code=400,
                detail=f"Unsupported file type: {file.content_type}. Supported: PDF, JPG, PNG"
            )
        
        # Extract text from document
        extracted_text = ""
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_content)
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        else:
            # For images, we'd need OCR (pytesseract, etc.)
            # For now, create a placeholder
            logger.info(f"Image upload detected: {file.content_type}")
            extracted_text = "IMAGE_DOCUMENT"
        
        # Parse the extracted text
        extracted_fields = parse_document_data(extracted_text, file.content_type)
        
        # Override document type if provided
        if document_type:
            extracted_fields["document_type"] = document_type
        
        # Create document structure
        document = {
            "document_type": extracted_fields.get("document_type", "UNKNOWN"),
            "extracted_fields": extracted_fields,
            "metadata": {
                "filename": file.filename,
                "content_type": file.content_type,
                "file_size": len(file_content),
                "session_id": session_id
            }
        }
        
        # Store document for processing
        kyc_service.store_document(session_id, document)
        logger.info(f"Document stored for session {session_id}")
        
        return ProcessingResponse(
            session_id=session_id,
            status="processing",
            message=f"Document uploaded successfully: {file.filename}",
            stream_url=f"/api/kyc/stream/{session_id}"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")