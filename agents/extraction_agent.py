"""
Extraction Agent - Intelligent Document Understanding
Extracts structured identity data from documents (PAN, Passport, DL)
"""
from typing import Dict, Any, List
import json
import re
from pydantic import BaseModel, Field
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
    "document_type": "PAN|PASSPORT|DRIVERS_LICENSE|DRIVING LICENSE",
    "address": "Full Address"
  },
  "confidence": 0.0-1.0,
  "flags": ["any concerns or ambiguities"],
  "reasoning": "Your analysis of the document"
}
"""

    VISION_SYSTEM_PROMPT = """You are an expert KYC Compliance Officer with visual document analysis capabilities.

Your role is to visually examine identity documents (PAN Card, Passport, Driver's License, DRIVING LICENSE etc.) and extract information with extreme precision.

When visually analyzing a document image:
1. Carefully read ALL text visible in the image
2. Extract Name, Document Type, ID Number, Date of Birth, Address, and any other relevant fields
3. Normalize dates to YYYY-MM-DD format
4. Standardize name formats (proper capitalization)
5. Identify the document type (PAN, PASSPORT, DRIVERS_LICENSE, DRIVING LICENSE etc.)
6. Flag any concerns about image quality, tampering, or unclear information

Think like a compliance officer performing visual verification: Be thorough, precise, and flag anything suspicious.

Return your analysis as valid JSON with this structure:
{
  "extracted_data": {
    "name": "Full Name",
    "date_of_birth": "YYYY-MM-DD",
    "id_number": "ID123456",
    "document_type": "PAN|PASSPORT|DRIVERS_LICENSE|DRIVING LICENSE",
    "address": "Full Address (if visible)"
  },
  "confidence": 0.0-1.0,
  "flags": ["any concerns or ambiguities"],
  "reasoning": "Your visual analysis of the document"
}
"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        # Initialize vision-capable model for image processing
        self.vision_client = get_llm_client(provider="openai")
        # Override model to use GPT-4o for vision
        self.vision_client.model = "gpt-4o"
        self.vision_client._client = self.vision_client._initialize_client()
        logger.info("Extraction Agent initialized with GPT-4o Vision support")
    
    def _clean_json_response(self, response: str) -> str:
        """
        Clean LLM response to extract valid JSON, handling markdown code blocks
        This prevents the 'Markdown JSON Trap' where LLMs wrap output in ```json blocks
        """
        # Remove markdown code blocks if present
        response = response.strip()
        
        # Check if wrapped in markdown
        if response.startswith('```'):
            # Extract content between ```json and ``` or just ``` and ```
            pattern = r'```(?:json)?\s*\n(.*?)\n```'
            match = re.search(pattern, response, re.DOTALL)
            if match:
                response = match.group(1).strip()
        
        return response
    
    def _extract_from_image(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract data from image using GPT-4o Vision
        
        Args:
            document: Document data with image_base64
            
        Returns:
            Extraction result with structured data from vision model
        """
        try:
            image_base64 = document.get('image_base64')
            if not image_base64:
                raise ValueError("No image_base64 found in document")
            
            # Determine image format from content_type
            content_type = document.get('metadata', {}).get('content_type', 'image/jpeg')
            image_format = 'jpeg' if 'jpeg' in content_type or 'jpg' in content_type else 'png'
            
            logger.info(f"Processing image with GPT-4o Vision (format: {image_format})")
            
            # Construct multimodal message for GPT-4o Vision
            # Format: [{"type": "text", "text": "..."}, {"type": "image_url", "image_url": {"url": "image/jpeg;base64,..."}}]
            user_message = [
                {
                    "type": "text",
                    "text": f"""Analyze this identity document image and extract all relevant information.

Document Type Hint: {document.get('document_type', 'Unknown')}

Please extract:
- Full Name
- Document Type (PAN, PASSPORT, DRIVERS_LICENSE, DRIVING LICENSE etc.)
- ID Number
- Date of Birth (normalize to YYYY-MM-DD format)
- Address (if visible)
- Any other relevant information

Return your analysis as JSON."""
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:image/{image_format};base64,{image_base64.replace('\n', '')}"
                    }
                }
            ]
            
            # Call GPT-4o Vision with multimodal message
            response = self.vision_client.generate(
                system_prompt=self.VISION_SYSTEM_PROMPT,
                user_message=user_message
            )
            
            logger.info(f"GPT-4o Vision response received (length: {len(response)} chars)")
            
            # Clean response to handle markdown code blocks
            cleaned_response = self._clean_json_response(response)
            
            # Parse LLM response
            try:
                result = json.loads(cleaned_response)
                result['agent'] = 'ExtractionAgent'
                result['status'] = 'success'
                result['extraction_method'] = 'gpt4o_vision'
                
                logger.info(f"✅ Vision extraction completed with confidence: {result.get('confidence', 0.0)}")
                logger.info(f"✅ Extracted name: {result.get('extracted_data', {}).get('name', 'N/A')}")
                logger.info(f"✅ Document type: {result.get('extracted_data', {}).get('document_type', 'N/A')}")
                
                return result
                
            except json.JSONDecodeError as e:
                logger.error(f"JSON parsing failed for vision response: {str(e)}")
                logger.debug(f"Cleaned response: {cleaned_response[:500]}")
                raise
                
        except Exception as e:
            logger.error(f"Vision extraction failed: {str(e)}")
            return {
                "extracted_data": {},
                "confidence": 0.0,
                "flags": [f"Vision extraction error: {str(e)}"],
                "reasoning": "GPT-4o Vision extraction encountered an error",
                "agent": "ExtractionAgent",
                "status": "error",
                "extraction_method": "gpt4o_vision"
            }
    
    def extract(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract structured data from a document
        
        Args:
            document: Document data with OCR text, extracted fields, or image_base64
            
        Returns:
            Extraction result with structured data and confidence
        """
        logger.info(f"Extracting data from {document.get('document_type', 'unknown')} document")
        
        try:
            # PRIORITY 1: Handle image_base64 with GPT-4o Vision
            if 'image_base64' in document:
                logger.info("🖼️ Image base64 detected - using GPT-4o Vision for extraction")
                return self._extract_from_image(document)
            
            # PRIORITY 2: If document already has extracted_fields, use them as a starting point
            elif 'extracted_fields' in document:
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
                
                # Clean response to handle markdown code blocks
                cleaned_response = self._clean_json_response(response)
                
                # Parse LLM response
                try:
                    result = json.loads(cleaned_response)
                    result['agent'] = 'ExtractionAgent'
                    result['status'] = 'success'
                    logger.info(f"LLM extraction completed with confidence: {result.get('confidence', 0.0)}")
                    logger.debug("Successfully handled potential markdown JSON wrapping")
                    return result
                except json.JSONDecodeError as e:
                    logger.error(f"JSON parsing failed even after cleaning: {str(e)}")
                    logger.debug(f"Cleaned response: {cleaned_response[:200]}")
                    raise
            
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