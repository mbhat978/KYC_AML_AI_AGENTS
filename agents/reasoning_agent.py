"""
Reasoning Agent - Intelligent Conflict Resolution & Risk Intelligence
"""
from typing import Dict, Any
from loguru import logger
from utils.validators import calculate_name_similarity
from config.settings import settings


class ReasoningAgent:
    """Reasoning Agent for intelligent conflict resolution"""
    
    def __init__(self):
        logger.info("Reasoning Agent initialized")
    
    def reason(self, extraction_result: Dict[str, Any], verification_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze verification results and make intelligent decisions
        
        Args:
            extraction_result: Results from extraction agent
            verification_result: Results from verification agent
            
        Returns:
            Reasoning analysis with recommendations
        """
        logger.info("Starting reasoning analysis")
        # CRITICAL FIX: Use local variable per-document, not instance variable
        reasoning_loops = 1  # Each document starts fresh
        
        try:
            extracted_data = extraction_result.get('extracted_data', {})
            verification_status = verification_result.get('verification_status')
            discrepancies = verification_result.get('discrepancies', [])
            matches = verification_result.get('matches', {})
            
            # Analyze the situation
            risk_factors = []
            should_reverify = False
            additional_sources_needed = []
            
            # Check sanctions/PEP flags (CRITICAL)
            if matches.get('sanctions', {}).get('status') == 'flagged':
                risk_factors.append("CRITICAL: Sanctions list match")
                conclusion = "REJECT"
                confidence = 0.1
            elif matches.get('pep', {}).get('status') == 'flagged':
                risk_factors.append("HIGH RISK: PEP match detected")
                conclusion = "ESCALATE"
                confidence = 0.4
            # Handle name mismatches intelligently
            elif verification_status == "PARTIAL":
                gov_match = matches.get('government_db', {})
                if gov_match.get('status') == 'mismatch':
                    confidence_score = gov_match.get('confidence', 0.0)
                    
                    # Intelligent reasoning: distinguish typos from real mismatches
                    if confidence_score > 0.75:
                        # Likely a variation (Jon vs Jonathan)
                        risk_factors.append(f"Minor name variation detected (similarity: {confidence_score:.2f})")
                        conclusion = "ACCEPT"
                        confidence = 0.75
                    elif confidence_score > 0.6:
                        # Ambiguous - need more data
                        risk_factors.append(f"Name mismatch requires review (similarity: {confidence_score:.2f})")
                        should_reverify = reasoning_loops < settings.max_reasoning_loops
                        conclusion = "REQUEST_MORE_DATA" if should_reverify else "ESCALATE"
                        confidence = 0.5
                    else:
                        # Significant mismatch
                        risk_factors.append("Significant name mismatch detected")
                        conclusion = "ESCALATE"
                        confidence = 0.3
                else:
                    risk_factors.append("Partial verification")
                    conclusion = "ESCALATE"
                    confidence = 0.5
            elif verification_status == "FAILED":
                risk_factors.append("ID not found in government database")
                conclusion = "REJECT"
                confidence = 0.2
            elif verification_status == "VERIFIED":
                confidence = verification_result.get('confidence', 0.9)
                conclusion = "ACCEPT"
            else:
                risk_factors.append("Unknown verification status")
                conclusion = "ESCALATE"
                confidence = 0.3
            
            result = {
                "reasoning_conclusion": conclusion,
                "confidence": confidence,
                "should_reverify": should_reverify,
                "additional_sources_needed": additional_sources_needed,
                "analysis": self._generate_analysis(extracted_data, verification_result, conclusion),
                "risk_factors": risk_factors,
                "reasoning_loops_used": reasoning_loops,
                "agent": "ReasoningAgent",
                "status": "success"
            }
            
            logger.info(f"Reasoning completed: {conclusion} (confidence: {confidence:.2f})")
            return result
            
        except Exception as e:
            logger.error(f"Reasoning failed: {str(e)}")
            return {
                "reasoning_conclusion": "ERROR",
                "confidence": 0.0,
                "should_reverify": False,
                "additional_sources_needed": [],
                "analysis": f"Reasoning error: {str(e)}",
                "risk_factors": ["Processing error"],
                "agent": "ReasoningAgent",
                "status": "error"
            }
    
    def _generate_analysis(self, extracted_data: Dict, verification_result: Dict, conclusion: str) -> str:
        """Generate human-readable analysis"""
        name = extracted_data.get('name', 'Unknown')
        id_num = extracted_data.get('id_number', 'Unknown')
        verification_status = verification_result.get('verification_status')
        
        analysis = f"Analysis for {name} (ID: {id_num}):\n"
        analysis += f"- Verification Status: {verification_status}\n"
        analysis += f"- Recommendation: {conclusion}\n"
        
        matches = verification_result.get('matches', {})
        if matches.get('government_db', {}).get('status') == 'match':
            analysis += "- Government DB: ✓ Verified\n"
        elif matches.get('government_db', {}).get('status') == 'mismatch':
            analysis += "- Government DB: ⚠ Name variation detected\n"
        else:
            analysis += "- Government DB: ✗ Not found\n"
        
        analysis += f"- Sanctions: {matches.get('sanctions', {}).get('status', 'unknown').upper()}\n"
        analysis += f"- PEP: {matches.get('pep', {}).get('status', 'unknown').upper()}\n"
        
        return analysis