"""
Extraction Agent - Intelligent Document Understanding
Extracts structured identity data from documents (PAN, Passport, DL)
"""
from typing import Dict, Any
import json
from loguru import logger
from utils.llm_client import get_llm_client
from utils.validators import validate_extracted_data


class ExtractionAgent:
    """
    Extraction Agent with intelligent document understanding capabilities
    
    Role: Parse mock documents and extract structured identity data
    Thinking: Like a compliance officer reviewing documents for completeness and accuracy
    """
    
    SYSTEM_PROMPT = """You are an expert KYC Compliance Officer specialized in document verification.

Your role is to extract identity information from documents with extreme precision.

When reviewing a document:
1. Extract ALL relevant fields (Name, DOB, ID Number, Address, etc.)
2. Normalize dates to YYYY-MM-DD format
3. Standardize name formats (proper capitalization)
4. Flag any unclear or ambiguous information
5. Assess document quality and completeness

Think like a compliance officer: Be thorough, precise, and flag anything suspicious.

Return your analysis as valid JSON with this structure:
{
  "extracted_data": {
    "name": "Full Name",
    "date_of_birth": "YYYY-MM-DD",
    "id_number": "ID123456",
    "document_type": "PAN|PASSPORT|DRIVERS_LICENSE",
    "address": "Full Address"
  },
  "confidence": 0.0-1.0,
  "flags": ["any concerns or ambiguities"],
  "reasoning": "Your analysis of the document"
}
"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        logger.info("Extraction Agent initialized")
    
    def extract(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from a document
        
        Args:
            document: Document data with OCR text or extracted fields
            
        Returns:
            Extraction result with structured data and confidence
        """
        logger.info(f"Extracting data from {document.get('document_type', 'unknown')} document")
        
        try:
            # If document already has extracted_fields, use them as a starting point
            if 'extracted_fields' in document:
                extracted_data = document['extracted_fields']
                logger.info("Using pre-extracted fields from document")
                
                # Validate the extracted data
                is_valid, errors = validate_extracted_data(extracted_data)
                
                result = {
                    "extracted_data": extracted_data,
                    "confidence": document.get('metadata', {}).get('confidence_score', 0.85),
                    "flags": errors if not is_valid else [],
                    "reasoning": "Extracted from structured document fields with validation checks",
                    "agent": "ExtractionAgent",
                    "status": "success" if is_valid else "needs_review"
                }
                
                logger.info(f"Extraction completed with confidence: {result['confidence']}")
                return result
            
            # Otherwise, use LLM to extract from OCR text
            elif 'ocr_text' in document:
                logger.info("Extracting from OCR text using LLM")
                
                user_message = f"""Extract identity information from this document:

Document Type: {document.get('document_type', 'Unknown')}
OCR Text:
{document['ocr_text']}

Extract all identity fields and return as JSON."""
                
                response = self.llm_client.generate(
                    system_prompt=self.SYSTEM_PROMPT,
                    user_message=user_message
                )
                
                # Parse LLM response
                result = json.loads(response)
                result['agent'] = 'ExtractionAgent'
                result['status'] = 'success'
                
                logger.info(f"LLM extraction completed with confidence: {result.get('confidence', 0.0)}")
                return result
            
            else:
                error_msg = "Document has no extracted_fields or ocr_text"
                logger.error(error_msg)
                return {
                    "extracted_data": {},
                    "confidence": 0.0,
                    "flags": [error_msg],
                    "reasoning": "Unable to extract data from document",
                    "agent": "ExtractionAgent",
                    "status": "error"
                }
                
        except Exception as e:
            logger.error(f"Extraction failed: {str(e)}")
            return {
                "extracted_data": {},
                "confidence": 0.0,
                "flags": [f"Extraction error: {str(e)}"],
                "reasoning": "Extraction process encountered an error",
                "agent": "ExtractionAgent",
                "status": "error"
            }