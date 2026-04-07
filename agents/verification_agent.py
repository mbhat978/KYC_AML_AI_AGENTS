"""
Verification Agent - LangGraph ReAct Agent with Tool-Calling
Phase 3: Dynamic Autonomous Verification using LangGraph ReAct Pattern
WITH ERROR HANDLING AND RETRY LOGIC
"""
from typing import Dict, Any, List
import json
import os
import time
import random
from datetime import datetime
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field
from loguru import logger
from utils.llm_client import get_llm_client


# ============================================================================
# TOOL DEFINITIONS
# ============================================================================

@tool
def search_government_db(name: str, id_number: str, dob: str = None, address: str = None) -> dict:
    """Search the Government Database for identity verification and compare fields. Use this to verify if a person's identity exists in official records and check for DOB/address mismatches. Args: name (full name), id_number (government ID), dob (date of birth), address (residential address). Returns dict with found, record, match_confidence, discrepancies, note."""
    mock_data_dir = os.path.join(os.path.dirname(__file__), '..', 'mock_data')
    db_path = os.path.join(mock_data_dir, 'government_db.json')
    
    def normalize_date(date_str):
        """Convert various date formats to YYYY-MM-DD for comparison"""
        if not date_str:
            return None
        # Handle DD-MM-YYYY format
        if '-' in date_str and len(date_str.split('-')[0]) <= 2:
            parts = date_str.split('-')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        # Handle DD/MM/YYYY format
        if '/' in date_str and len(date_str.split('/')[0]) <= 2:
            parts = date_str.split('/')
            if len(parts) == 3:
                return f"{parts[2]}-{parts[1].zfill(2)}-{parts[0].zfill(2)}"
        return date_str
    
    def compare_addresses(addr1, addr2):
        """Compare two addresses with fuzzy matching"""
        if not addr1 or not addr2:
            return True, 1.0  # If either missing, assume match
        
        addr1_norm = addr1.lower().replace(',', ' ').replace('  ', ' ').strip()
        addr2_norm = addr2.lower().replace(',', ' ').replace('  ', ' ').strip()
        
        # Exact match
        if addr1_norm == addr2_norm:
            return True, 1.0
        
        # Check if major components match (street, city, state, pin)
        addr1_words = set(addr1_norm.split())
        addr2_words = set(addr2_norm.split())
        common_words = addr1_words.intersection(addr2_words)
        
        if len(common_words) >= 3:  # At least 3 common words suggests same location
            similarity = len(common_words) / max(len(addr1_words), len(addr2_words))
            return True, similarity
        
        return False, 0.0
    
    try:
        with open(db_path, 'r') as f:
            db = json.load(f)
            
            # First try exact name and ID match
            for record in db.get('records', []):
                if record.get('id_number', '') == id_number:
                    discrepancies = []
                    
                    # Check name match
                    name_match = record.get('name', '').lower() == name.lower()
                    if not name_match:
                        discrepancies.append(f"Name mismatch: DB has '{record.get('name')}' but document shows '{name}'")
                    
                    # Check DOB if provided
                    dob_match = True
                    if dob and record.get('date_of_birth'):
                        db_dob_norm = normalize_date(record.get('date_of_birth'))
                        doc_dob_norm = normalize_date(dob)
                        if db_dob_norm != doc_dob_norm:
                            dob_match = False
                            discrepancies.append(f"DOB mismatch: DB has '{record.get('date_of_birth')}' but document shows '{dob}'")
                            logger.warning(f"⚠️ DOB MISMATCH: DB={record.get('date_of_birth')} vs DOC={dob}")
                    
                    # Check address if provided
                    address_match = True
                    address_confidence = 1.0
                    if address and record.get('address') and address != "none" and address != "Unknown":
                        address_match, address_confidence = compare_addresses(record.get('address'), address)
                        if not address_match:
                            discrepancies.append(f"Address mismatch: DB has '{record.get('address')}' but document shows '{address}'")
                            logger.warning(f"⚠️ ADDRESS MISMATCH: DB={record.get('address')} vs DOC={address}")
                        elif address_confidence < 1.0:
                            logger.info(f"✓ Address fuzzy match with {address_confidence:.2f} confidence")
                    
                    # Calculate overall match confidence
                    if discrepancies:
                        match_confidence = min(0.5, address_confidence * 0.5)  # Low confidence if discrepancies
                        logger.warning(f"⚠️ Government DB: ID found but {len(discrepancies)} discrepanc{'y' if len(discrepancies) == 1 else 'ies'} detected")
                        return {
                            'found': True,
                            'record': record,
                            'match_confidence': match_confidence,
                            'discrepancies': discrepancies,
                            'note': f"ID matched but field mismatches detected: {', '.join(discrepancies[:2])}"
                        }
                    else:
                        logger.info(f"✅ Government DB: Perfect match for {name}")
                        return {
                            'found': True,
                            'record': record,
                            'match_confidence': 1.0,
                            'discrepancies': [],
                            'note': 'All fields match perfectly'
                        }
            
    except Exception as e:
        logger.error(f"❌ Government DB error: {str(e)}")
        return {'found': False, 'error': str(e)}
    
    logger.info(f"❌ Government DB: No match for {name} / {id_number}")
    return {'found': False, 'note': 'No matching records found'}


@tool
def search_sanctions_list(name: str) -> dict:
    """Search International Sanctions Lists. CRITICAL for AML compliance. Use this to check if person is sanctioned. Args: name (full name). Returns dict with found, severity, reason, note."""
    mock_data_dir = os.path.join(os.path.dirname(__file__), '..', 'mock_data')
    sanctions_path = os.path.join(mock_data_dir, 'sanctions_list.json')
    
    try:
        with open(sanctions_path, 'r') as f:
            sanctions = json.load(f)
            for entry in sanctions.get('entries', []):
                if entry.get('name', '').lower() == name.lower():
                    logger.warning(f"🚨 SANCTIONS HIT: {entry.get('name')}")
                    return {'found': True, 'severity': entry.get('severity', 'HIGH'), 'reason': entry.get('reason'), 'note': 'CRITICAL: Sanctions match'}
            for entry in sanctions.get('entries', []):
                if any(alias.lower() == name.lower() for alias in entry.get('aliases', [])):
                    logger.warning(f"🚨 SANCTIONS HIT (alias): {entry.get('name')}")
                    return {'found': True, 'severity': entry.get('severity', 'HIGH'), 'reason': entry.get('reason'), 'note': 'CRITICAL: Matched via alias'}
    except Exception as e:
        logger.error(f"❌ Sanctions error: {str(e)}")
        return {'found': False, 'error': str(e)}
    
    logger.info(f"✅ Sanctions: Clear for {name}")
    return {'found': False, 'note': 'No sanctions matches - clear'}


@tool
def search_pep_list(name: str) -> dict:
    """Search Politically Exposed Persons (PEP) List. Use this to check if person holds/held political position. Requires enhanced due diligence. Args: name (full name). Returns dict with found, position, country, risk_level, note."""
    mock_data_dir = os.path.join(os.path.dirname(__file__), '..', 'mock_data')
    pep_path = os.path.join(mock_data_dir, 'pep_list.json')
    
    try:
        with open(pep_path, 'r') as f:
            pep_list = json.load(f)
            for entry in pep_list.get('entries', []):
                if entry.get('name', '').lower() == name.lower():
                    logger.warning(f"⚠️ PEP MATCH: {entry.get('name')} - {entry.get('position')}")
                    return {'found': True, 'position': entry.get('position'), 'country': entry.get('country'), 'risk_level': entry.get('risk_level', 'MEDIUM'), 'note': f"PEP: {entry.get('status')} - Enhanced Due Diligence required"}
    except Exception as e:
        logger.error(f"❌ PEP error: {str(e)}")
        return {'found': False, 'error': str(e)}
    
    logger.info(f"✅ PEP: Clear for {name}")
    return {'found': False, 'note': 'No PEP matches - clear'}


# ============================================================================
# OUTPUT SCHEMA
# ============================================================================

class VerificationOutput(BaseModel):
    """Structured output schema for verification results"""
    verification_status: str = Field(description="Overall status: VERIFIED, FAILED, FLAGGED, PARTIAL, ERROR")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    matches: Dict[str, Any] = Field(description="Results from government_db, sanctions, pep")
    discrepancies: List[str] = Field(description="List of issues found")
    agent: str = Field(default="VerificationAgent")
    status: str = Field(default="success")


class VerificationResult(BaseModel):
    verification_status: str = Field(description="Must be exactly 'VERIFIED', 'FAILED', 'FLAGGED', or 'ERROR'")
    confidence: float = Field(default=1.0)
    matches: Dict[str, Any] = Field(default_factory=dict)
    discrepancies: List[str] = Field(default_factory=list)


# ============================================================================
# REACT AGENT CLASS WITH RETRY LOGIC
# ============================================================================

class VerificationAgent:
    """LangGraph ReAct Agent for autonomous multi-source verification with retry logic"""
    
    def __init__(self):
        self.llm = get_llm_client()._client
        self.tools = [search_government_db, search_sanctions_list, search_pep_list]
        logger.info("Verification ReAct Agent initialized with tools and retry logic")
    
    def verify(self,  data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify extracted data using autonomous ReAct agent with tool-calling.
        Includes retry logic for API errors (503, 429, 500, timeouts).
        
        Args:
            data: Dictionary containing extracted identity data (name, id_number, etc.)
            
        Returns:
            Dictionary with verification_status, confidence, matches, discrepancies
        """
        logger.info("🤖 Starting ReAct Agent verification with retry logic")
        
        max_retries = 3
        initial_delay = 2.0
        
        for attempt in range(max_retries + 1):
            try:
                # Execute verification
                result = self._execute_verification(data)
                logger.info(f"✅ Verification completed successfully on attempt {attempt + 1}")
                return result
                
            except Exception as e:
                error_str = str(e).lower()
                
                # Check if error is retryable (503, 429, 500, timeout, connection errors)
                is_retryable = any(code in error_str for code in [
                    '503', '429', '500', 'timeout', 'timed out', 
                    'connection', 'server error', 'service unavailable',
                    'rate limit', 'too many requests'
                ])
                
                # If this was the last attempt or error is not retryable, return ERROR
                if attempt >= max_retries or not is_retryable:
                    logger.error(f"❌ Verification failed after {attempt + 1} attempts: {str(e)}")
                    return self._create_error_response(e)
                
                # Calculate sleep time with jitter to prevent thundering herd
                delay = initial_delay * (2 ** attempt)  # Exponential backoff: 2s, 4s, 8s
                jitter = random.uniform(0, 0.3 * delay)
                sleep_time = delay + jitter
                
                logger.warning(f"⚠️ Verification attempt {attempt + 1}/{max_retries + 1} failed: {str(e)[:150]}")
                logger.info(f"🔄 Retrying in {sleep_time:.2f}s...")
                time.sleep(sleep_time)
        
        # Should never reach here, but just in case
        return self._create_error_response(Exception("Maximum retries exceeded"))
    
    def _execute_verification(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Internal method that executes the actual verification logic.
        Can raise exceptions for retry mechanism.
        """
        # Build the ReAct agent with tools
        agent = create_react_agent(self.llm, self.tools)
        
        # System prompt for autonomous verification
        system_prompt = """You are an autonomous KYC Verification Agent. You MUST:
1. Use search_government_db to verify the identity in official records - IMPORTANT: Pass name, id_number, dob, AND address parameters to detect mismatches
2. Use search_sanctions_list to check for sanctions/watchlist matches  
3. Use search_pep_list to check for Politically Exposed Person status

Be thorough and autonomous. When calling search_government_db, ALWAYS include the dob and address parameters for field comparison.

After using all three tools, provide a final summary with:
- verification_status: "VERIFIED" if gov DB found with no field mismatches and no sanctions/PEP issues, "FAILED" if not in gov DB, "FLAGGED" if sanctions/PEP hit OR field mismatches detected
- confidence: 0.0-1.0 based on match quality and field discrepancies
- Summary of findings from all three databases"""
        
        # Prepare the input message with all available fields
        user_message = f"""Verify this identity:
Name: {data.get('name', 'Unknown')}
ID Number: {data.get('id_number', 'Unknown')}
DOB: {data.get('date_of_birth', 'Unknown')}
Address: {data.get('address', 'Unknown')}

IMPORTANT: When calling search_government_db, use ALL four parameters (name, id_number, dob, address) to check for field mismatches.

Use ALL three tools to complete verification."""
        
        # Invoke the agent (this can raise exceptions)
        input_state = {
            "messages": [
                HumanMessage(content=f"{system_prompt}\n\n{user_message}")
            ]
        }
        
        result = agent.invoke(input_state)
        
        # Extract tool call results from the agent's execution
        matches_dict = {
            'government_db': {'status': 'clear'},
            'sanctions': {'status': 'clear'},
            'pep': {'status': 'clear'}
        }
        
        # Parse through messages to find tool call results
        for message in result["messages"]:
            if hasattr(message, 'name'):
                tool_name = message.name
                tool_result = message.content
                if isinstance(tool_result, str):
                    try:
                        tool_result = json.loads(tool_result)
                    except:
                        continue
                if not isinstance(tool_result, dict):
                    continue
                
                # Process government DB results
                if tool_name == 'search_government_db' and tool_result.get('found'):
                    has_discrepancies = bool(tool_result.get('discrepancies', []))
                    matches_dict['government_db'] = {
                        'status': 'mismatch' if has_discrepancies else 'match',
                        'confidence': tool_result.get('match_confidence', 0.0),
                        'record': tool_result.get('record', {}),
                        'discrepancies': tool_result.get('discrepancies', []),
                        'note': tool_result.get('note', '')
                    }
                
                # Process sanctions results
                elif tool_name == 'search_sanctions_list' and tool_result.get('found'):
                    matches_dict['sanctions'] = {
                        'status': 'flagged',
                        'severity': tool_result.get('severity', 'HIGH'),
                        'reason': tool_result.get('reason', ''),
                        'note': tool_result.get('note', '')
                    }
                
                # Process PEP results
                elif tool_name == 'search_pep_list' and tool_result.get('found'):
                    matches_dict['pep'] = {
                        'status': 'flagged',
                        'risk_level': tool_result.get('risk_level', 'MEDIUM'),
                        'position': tool_result.get('position', ''),
                        'country': tool_result.get('country', ''),
                        'note': tool_result.get('note', '')
                    }
        
        # Determine overall verification status
        has_sanctions = matches_dict['sanctions']['status'] == 'flagged'
        has_pep = matches_dict['pep']['status'] == 'flagged'
        gov_db_match = matches_dict['government_db']['status'] in ['match', 'mismatch']
        
        if has_sanctions or has_pep:
            verification_status = "FLAGGED"
            confidence = 0.9
        elif gov_db_match:
            verification_status = "VERIFIED" if matches_dict['government_db']['status'] == 'match' else "PARTIAL"
            confidence = matches_dict['government_db'].get('confidence', 0.8)
        else:
            verification_status = "FAILED"
            confidence = 0.2
        
        # Build discrepancies list
        discrepancies = []
        
        # Add field-level discrepancies from government DB
        if matches_dict['government_db']['status'] == 'mismatch':
            gov_db_discrepancies = matches_dict['government_db'].get('discrepancies', [])
            discrepancies.extend(gov_db_discrepancies)
        
        if not gov_db_match and not has_sanctions and not has_pep:
            discrepancies.append('Identity not found in government database')

        # Return the perfectly formatted dictionary for the Orchestrator
        return {
            'verification_status': verification_status,
            'confidence': confidence,
            'matches': matches_dict,
            'discrepancies': discrepancies
        }
    
    def _create_error_response(self, error: Exception) -> Dict[str, Any]:        
        """Create standardized error response for verification failures."""
        error_msg = str(error)
        logger.error(f"Creating error response: {error_msg}")
        
        return {
            'verification_status': 'ERROR',
            'confidence': 0.0,
            'matches': {
                'government_db': {'status': 'error', 'note': 'Service unavailable'},
                'sanctions': {'status': 'error', 'note': 'Service unavailable'},
                'pep': {'status': 'error', 'note': 'Service unavailable'}
            },
            'discrepancies': [f'Verification service error: {error_msg}'],
            'agent': 'VerificationAgent',
            'status': 'error',
            'error': error_msg
        }
