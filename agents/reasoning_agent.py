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
    
    def reason(self, extraction_result: Dict[str, Any], verification_result: Dict[str, Any], transaction_analysis: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Analyze verification results and make intelligent decisions.
        Enhanced Due Diligence (EDD) - evaluates BOTH identity risk and financial risk.
        
        Args:
            extraction_result: Results from extraction agent
            verification_result: Results from verification agent
            transaction_analysis: Optional AML transaction analysis results
            
        Returns:
            Reasoning analysis with recommendations
        """
        logger.info("Starting reasoning analysis")
        # CRITICAL FIX: Use local variable per-document, not instance variable
        reasoning_loops = 1  # Each document starts fresh
        
        try:
            extracted_data = extraction_result.get('extracted_data', {})
            verification_status = verification_result.get('verification_status').upper()
            discrepancies = verification_result.get('discrepancies', [])
            matches = verification_result.get('matches', {})
            
            # Analyze the situation
            risk_factors = []
            should_reverify = False
            additional_sources_needed = []
            
            # Handle ERROR status from verification (service unavailable)
            if verification_status == "ERROR":
                error_msg = verification_result.get('error', 'Verification service unavailable')
                risk_factors.append(f"CRITICAL: Verification service error - {error_msg}")
                conclusion = "ESCALATE"
                confidence = 0.1
                logger.warning(f"Verification ERROR detected: {error_msg}")
                # Skip further analysis and return escalation immediately
                result = {
                    "reasoning_conclusion": conclusion,
                    "confidence": confidence,
                    "should_reverify": should_reverify,
                    "additional_sources_needed": additional_sources_needed,
                    "analysis": self._generate_analysis(extracted_data, verification_result, conclusion, transaction_analysis),
                    "risk_factors": risk_factors,
                    "reasoning_loops_used": reasoning_loops,
                    "agent": "ReasoningAgent",
                    "status": "success"
                }
                logger.info(f"Reasoning completed: {conclusion} (confidence: {confidence:.2f}) - Verification ERROR")
                return result
            
            # Check for AML transaction flags if present
            if transaction_analysis:
                aml_flags = transaction_analysis.get('aml_flags', {})
                if aml_flags.get('sanctions_hit'):
                    risk_factors.append("CRITICAL: Transaction involves sanctioned entity")
                if aml_flags.get('pep_match'):
                    risk_factors.append("HIGH RISK: Transaction involves PEP")
                if aml_flags.get('high_velocity'):
                    risk_factors.append("MEDIUM RISK: High velocity transaction pattern detected")
                if aml_flags.get('structuring_detected'):
                    risk_factors.append("HIGH RISK: Potential structuring detected")
            
            # Check sanctions/PEP flags (CRITICAL)
            if matches.get('sanctions', {}).get('status') == 'flagged':
                risk_factors.append("CRITICAL: Sanctions list match")
                conclusion = "REJECT"
                confidence = 0.1
            elif matches.get('pep', {}).get('status') == 'flagged':
                pep_risk_level = matches.get('pep', {}).get('risk_level', 'MEDIUM')
                if pep_risk_level == 'HIGH':
                    risk_factors.append("HIGH RISK: Active high-risk PEP match detected")
                    conclusion = "ESCALATE"
                    confidence = 0.5
                else:
                    risk_factors.append("MEDIUM RISK: PEP match detected")
                    conclusion = "ESCALATE"
                    confidence = 0.6  # Higher confidence for former/medium PEP
            # Handle mismatches intelligently (name, DOB, address)
            elif verification_status == "PARTIAL":
                gov_match = matches.get('government_db', {})
                if gov_match.get('status') == 'mismatch':
                    confidence_score = gov_match.get('confidence', 0.0)
                    
                    # Analyze specific discrepancies
                    has_name_mismatch = False
                    has_dob_mismatch = False
                    has_address_mismatch = False
                    
                    # Check discrepancies from government DB match
                    gov_discrepancies = gov_match.get('discrepancies', [])
                    for disc in gov_discrepancies:
                        disc_lower = str(disc).lower()
                        if 'name mismatch' in disc_lower:
                            has_name_mismatch = True
                        elif 'dob mismatch' in disc_lower or 'date of birth' in disc_lower:
                            has_dob_mismatch = True
                        elif 'address mismatch' in disc_lower:
                            has_address_mismatch = True
                    
                    # Also check top-level discrepancies
                    for disc in discrepancies:
                        disc_lower = str(disc).lower()
                        if 'dob mismatch' in disc_lower or 'date of birth' in disc_lower:
                            if not has_dob_mismatch:
                                has_dob_mismatch = True
                                risk_factors.append(f"DOB mismatch detected")
                        elif 'address mismatch' in disc_lower:
                            if not has_address_mismatch:
                                has_address_mismatch = True
                                risk_factors.append(f"Address mismatch detected")
                        elif 'name mismatch' in disc_lower:
                            if not has_name_mismatch:
                                has_name_mismatch = True
                                risk_factors.append(f"Name mismatch detected")
                    
                    # Determine severity based on type of mismatches
                    mismatch_count = sum([has_name_mismatch, has_dob_mismatch, has_address_mismatch])
                    
                    if mismatch_count >= 2:
                        # Multiple mismatches - high risk
                        conclusion = "REJECT"
                        confidence = 0.2
                        logger.warning(f"Multiple field mismatches detected ({mismatch_count} fields)")
                    elif has_dob_mismatch:
                        # DOB mismatch is critical
                        conclusion = "ESCALATE"
                        confidence = 0.3
                        logger.warning("DOB mismatch detected - escalating")
                    elif has_address_mismatch:
                        # Address mismatch - needs review
                        conclusion = "ESCALATE"
                        confidence = 0.4
                        logger.warning("Address mismatch detected - escalating")
                    elif has_name_mismatch:
                        # Name mismatch only - use confidence score
                        if confidence_score > 0.75:
                            # Likely a variation (Jon vs Jonathan)
                            conclusion = "ESCALATE"
                            confidence = 0.75
                        elif confidence_score > 0.6:
                            # Ambiguous - need more data
                            should_reverify = reasoning_loops < settings.max_reasoning_loops
                            conclusion = "REQUEST_MORE_DATA" if should_reverify else "ESCALATE"
                            confidence = 0.5
                        else:
                            # Significant name mismatch
                            conclusion = "ESCALATE"
                            confidence = 0.3
                    else:
                        # No specific mismatch identified but status is partial
                        risk_factors.append("Partial verification - unspecified discrepancy")
                        conclusion = "ESCALATE"
                        confidence = 0.5
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
                "analysis": self._generate_analysis(extracted_data, verification_result, conclusion, transaction_analysis),
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
    
    def _generate_analysis(self, extracted_data: Dict, verification_result: Dict, conclusion: str, transaction_analysis: Dict = None) -> str:
        """Generate human-readable analysis"""
        name = extracted_data.get('name', 'Unknown')
        id_num = extracted_data.get('id_number', 'Unknown')
        verification_status = verification_result.get('verification_status').upper()
        
        analysis = f"Enhanced Due Diligence (EDD) Analysis for {name} (ID: {id_num}):\n"
        analysis += f"- Verification Status: {verification_status}\n"
        analysis += f"- Recommendation: {conclusion}\n"
        
        # Add transaction analysis if present
        if transaction_analysis:
            analysis += "\n--- AML Transaction Analysis ---\n"
            aml_flags = transaction_analysis.get('aml_flags', {})
            risk_level = transaction_analysis.get('risk_level', 'UNKNOWN')
            analysis += f"- Transaction Risk Level: {risk_level}\n"
            analysis += f"- Sanctions Hit: {'YES' if aml_flags.get('sanctions_hit') else 'NO'}\n"
            analysis += f"- PEP Match: {'YES' if aml_flags.get('pep_match') else 'NO'}\n"
            analysis += f"- High Velocity: {'YES' if aml_flags.get('high_velocity') else 'NO'}\n"
            analysis += f"- Structuring: {'YES' if aml_flags.get('structuring_detected') else 'NO'}\n"
            analysis += "--------------------------------\n"
        
        matches = verification_result.get('matches', {})
        gov_match = matches.get('government_db', {})
        if gov_match.get('status') == 'match':
            analysis += "- Government DB: ✓ Verified\n"
        elif gov_match.get('status') == 'mismatch':
            analysis += "- Government DB: ⚠ Mismatches detected\n"
            # List specific discrepancies
            gov_discrepancies = gov_match.get('discrepancies', [])
            if gov_discrepancies:
                analysis += "  Discrepancies:\n"
                for disc in gov_discrepancies:
                    analysis += f"  • {disc}\n"
        else:
            analysis += "- Government DB: ✗ Not found\n"
        
        analysis += f"- Sanctions: {matches.get('sanctions', {}).get('status', 'unknown').upper()}\n"
        analysis += f"- PEP: {matches.get('pep', {}).get('status', 'unknown').upper()}\n"
        
        return analysis
