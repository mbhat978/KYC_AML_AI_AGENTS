"""
File Upload Routes for KYC Document Processing
Handles PDF, JPG, PNG uploads and extracts text for processing
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Form
from fastapi.responses import JSONResponse
from typing import Optional
import uuid
from loguru import logger
import sys
import os
import base64

# Add project root to path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from utils.pdf_converter import PDFConverter
from backend.app.models.schemas import ProcessingResponse, HumanReviewPayload
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
    import re
    
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
    
    # Split text into lines for parsing
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # PASSPORT-SPECIFIC PARSING
    if doc_type == "PASSPORT":
        surname = None
        given_names = None
        passport_no = None
        dob = None
        nationality = None
        
        # Extract passport fields
        for i, line in enumerate(lines):
            if "Surname" in line and i + 1 < len(lines):
                surname = lines[i + 1].strip()
            elif "Given Names" in line and i + 1 < len(lines):
                given_names = lines[i + 1].strip()
            elif "Passport No" in line and i + 1 < len(lines):
                passport_no = lines[i + 1].strip()
                extracted_fields["id_number"] = passport_no
            elif "Date of Birth" in line and i + 1 < len(lines):
                dob = lines[i + 1].strip()
                extracted_fields["date_of_birth"] = dob
            elif "Nationality" in line and i + 1 < len(lines):
                nationality = lines[i + 1].strip()
                extracted_fields["nationality"] = nationality
        
        # Build full name from surname and given names
        if surname and given_names:
            extracted_fields["name"] = f"{given_names} {surname}".title()
            extracted_fields["surname"] = surname
            extracted_fields["given_names"] = given_names
        elif surname:
            extracted_fields["name"] = surname.title()
        elif given_names:
            extracted_fields["name"] = given_names.title()
    
    # PAN CARD SPECIFIC PARSING
    elif doc_type == "PAN":
        # Try to extract name (look for "Name" label)
        for i, line in enumerate(lines):
            line_upper = line.upper()
            if "NAME" in line_upper and "FATHER" not in line_upper and i + 1 < len(lines):
                # Next line likely contains the name
                potential_name = lines[i + 1].strip()
                if len(potential_name) > 3:
                    extracted_fields["name"] = potential_name.title()
                    break
        
        # Try to extract PAN number
        pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
        pan_match = re.search(pan_pattern, text)
        if pan_match:
            extracted_fields["id_number"] = pan_match.group()
        
        # Try to extract DOB
        date_pattern = r'\d{2}[/-]\d{2}[/-]\d{4}'
        date_matches = re.findall(date_pattern, text)
        if date_matches:
            extracted_fields["date_of_birth"] = date_matches[0].replace('/', '-')
    
    # GENERIC NAME EXTRACTION (fallback)
    else:
        for i, line in enumerate(lines):
            line_upper = line.upper()
            if "NAME" in line_upper and i + 1 < len(lines):
                # Next line likely contains the name
                potential_name = lines[i + 1].strip()
                if len(potential_name) > 3 and potential_name.replace(' ', '').isalpha():
                    extracted_fields["name"] = potential_name.title()
                    break
    
    # If no name found, return without name (let extraction agent handle it)
    # Removed hardcoded "Extracted from PDF" bug
    
    return extracted_fields



@router.post("/upload/resume")
async def resume_processing(payload: HumanReviewPayload):
    try:
        result = kyc_service.orchestrator.resume_graph(payload.thread_id, payload.decision)
        return JSONResponse(content={"status": "success", "result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/kyc/upload", response_model=ProcessingResponse)
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    transaction_csv_data: Optional[str] = Form(None),
    analysis_type: Optional[str] = Form(None)
):
    """
    Upload and process a KYC document (PDF, JPG, PNG)
    Extracts text and initiates KYC processing
    Optionally accepts transaction CSV data for AML analysis
    """
    try:
        session_id = str(uuid.uuid4())
        logger.info(f"File upload for session {session_id}: {file.filename} ({file.content_type})")
        
        # Log if transaction data is provided
        if transaction_csv_data:
            logger.info(f"Transaction CSV data provided for session {session_id} (length: {len(transaction_csv_data)} chars)")
        
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
        image_base64 = None
        
        if file.content_type == "application/pdf":
            extracted_text = extract_text_from_pdf(file_content)
            logger.info(f"Extracted {len(extracted_text)} characters from PDF")
        else:
            # For images (JPG/PNG), convert to base64 for GPT-4o Vision
            logger.info(f"Image upload detected: {file.content_type}")
            image_base64 = base64.b64encode(file_content).decode('utf-8')
            extracted_text = "[IMAGE PAYLOAD]"
            logger.info(f"Image converted to base64 (length: {len(image_base64)} chars)")
        
        # Parse the extracted text (only for PDFs, skip for images)
        if file.content_type == "application/pdf":
            extracted_fields = parse_document_data(extracted_text, file.content_type)
        else:
            # For images, don't parse - let extraction agent handle with vision
            extracted_fields = {
                "document_type": document_type if document_type else "UNKNOWN",
                "raw_text": extracted_text,
                "confidence": 0.0  # Will be determined by vision model
            }
        
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
        
        # Store base64 image if present (for GPT-4o Vision)
        if image_base64:
            document["image_base64"] = image_base64
            logger.info(f"✅ Image base64 stored in document for session {session_id}")
        
        # Include transaction CSV data if provided (for AML analysis)
        if transaction_csv_data:
            document["transaction_csv_data"] = transaction_csv_data
            logger.info(f"✅ Transaction data included in document for session {session_id}")
        
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