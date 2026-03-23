"""
Verification Agent - LangGraph ReAct Agent with Tool-Calling
Phase 3: Dynamic Autonomous Verification using LangGraph ReAct Pattern
"""
from typing import Dict, Any, List
import json
import os
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
def search_government_db(name: str, id_number: str) -> dict:
    """Search the Government Database for identity verification. Use this to verify if a person's identity exists in official records. Args: name (full name), id_number (government ID). Returns dict with found, record, match_confidence, note."""
    mock_data_dir = os.path.join(os.path.dirname(__file__), '..', 'mock_data')
    db_path = os.path.join(mock_data_dir, 'government_db.json')
    
    try:
        with open(db_path, 'r') as f:
            db = json.load(f)
            for record in db.get('records', []):
                if (record.get('name', '').lower() == name.lower() and record.get('id_number', '') == id_number):
                    logger.info(f"✅ Government DB: Exact match for {name}")
                    return {'found': True, 'record': record, 'match_confidence': 1.0, 'note': 'Exact match'}
            for record in db.get('records', []):
                if record.get('id_number', '') == id_number:
                    logger.info(f"⚠️ Government DB: ID matched but name differs")
                    return {'found': True, 'record': record, 'match_confidence': 0.9, 'note': f"ID matched, name differs: '{record.get('name')}' vs '{name}'"}
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
    verification_status: str = Field(description="Overall status: VERIFIED, FAILED, FLAGGED, PARTIAL")
    confidence: float = Field(description="Confidence score 0.0-1.0")
    matches: Dict[str, Any] = Field(description="Results from government_db, sanctions, pep")
    discrepancies: List[str] = Field(description="List of issues found")
    agent: str = Field(default="VerificationAgent")
    status: str = Field(default="success")


# ============================================================================
# REACT AGENT CLASS
# ============================================================================

class VerificationResult(BaseModel):
    verification_status: str = Field(description="Must be exactly 'VERIFIED' or 'FAILED'")
    confidence: float = Field(default=1.0)
    matches: Dict[str, Any] = Field(default_factory=dict)
    discrepancies: List[str] = Field(default_factory=list)


class VerificationAgent:
    """LangGraph ReAct Agent for autonomous multi-source verification"""
    
    def __init__(self):
        self.llm = get_llm_client()._client
        self.tools = [search_government_db, search_sanctions_list, search_pep_list]
        logger.info("Verification ReAct Agent initialized with tools")
    
    def verify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Verify extracted data using autonomous ReAct agent with tool-calling
        
        Args:
             Dictionary containing extracted identity data (name, id_number, etc.)
            
        Returns:
            Dictionary with verification_status, confidence, matches, discrepancies
        """
        logger.info("🤖 Starting ReAct Agent verification")
        
        try:
            # Build the ReAct agent with tools
            agent = create_react_agent(self.llm, self.tools)
            
            # System prompt for autonomous verification
            system_prompt = """You are an autonomous KYC Verification Agent. You MUST:
1. Use search_government_db to verify the identity in official records
2. Use search_sanctions_list to check for sanctions/watchlist matches  
3. Use search_pep_list to check for Politically Exposed Person status

Be thorough and autonomous. If a search returns 'Not Found', try variations before concluding.

After using all three tools, provide a final summary with:
- verification_status: "VERIFIED" if gov DB found and no sanctions/PEP issues, "FAILED" if not in gov DB, "FLAGGED" if sanctions/PEP hit
- confidence: 0.0-1.0 based on match quality
- Summary of findings from all three databases"""
            
            # Prepare the input message
            user_message = f"""Verify this identity:
Name: {data.get('name', 'Unknown')}
ID Number: {data.get('id_number', 'Unknown')}
DOB: {data.get('date_of_birth', 'Unknown')}

Use ALL three tools to complete verification."""
            
            # Invoke the agent
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
            # LangGraph stores tool results in ToolMessage objects
            for message in result["messages"]:
                # Check if this is a ToolMessage (has 'name' attribute)
                if hasattr(message, 'name'):
                    tool_name = message.name
                    # Content is the tool result (already a dict)
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
                        matches_dict['government_db'] = {
                            'status': 'match' if tool_result.get('match_confidence', 0) == 1.0 else 'mismatch',
                            'confidence': tool_result.get('match_confidence', 0.0),
                            'record': tool_result.get('record', {}),
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
            if matches_dict['government_db']['status'] == 'mismatch':
                discrepancies.append(matches_dict['government_db'].get('note', 'Name mismatch'))
            if not gov_db_match and not has_sanctions and not has_pep:
                discrepancies.append('Identity not found in government database')

            # Return the perfectly formatted dictionary for the Orchestrator
            return {
                'verification_status': verification_status,
                'confidence': confidence,
                'matches': matches_dict,
                'discrepancies': discrepancies
            }
            
        except Exception as e:
            logger.error(f"❌ Verification failed: {str(e)}")
            return {
                "verification_status": "ERROR",
                "confidence": 0.0,
                "matches": {},
                "discrepancies": [f"Verification error: {str(e)}"],
                "agent": "VerificationAgent",
                "status": "error"
            }
