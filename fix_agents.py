"""
Script to fix typing issues in agent files
Run this to fix the 'data:' parameter name issues
"""

# Fix verification_agent.py
verification_agent_fixed = '''"""
Verification Agent - Multi-Source Verification Orchestration
"""
from typing import Dict, Any
import json
import time
from loguru import logger
from utils.llm_client import get_llm_client
from utils.validators import calculate_name_similarity
from config.settings import settings


class VerificationAgent:
    """Verification Agent for multi-source data verification"""
    
    def __init__(self):
        self.llm_client = get_llm_client()
        self.mock_databases = self._load_mock_databases()
        logger.info("Verification Agent initialized")
    
    def _load_mock_databases(self) -> Dict[str, Any]:
        """Load mock databases"""
        try:
            with open('mock_data/government_db.json', 'r') as f:
                gov_db = json.load(f)
            with open('mock_data/sanctions_list.json', 'r') as f:
                sanctions = json.load(f)
            with open('mock_data/pep_list.json', 'r') as f:
                pep = json.load(f)
            return {'government': gov_db, 'sanctions': sanctions, 'pep': pep}
        except Exception as e:
            logger.error(f"Failed to load mock databases: {str(e)}")
            return {}
    
    def verify(self, extracted_ Dict[str, Any]) -> Dict[str, Any]:
        """Verify extracted data against multiple sources"""
        logger.info("Starting multi-source verification")
        
        try:
            if settings.use_mock_databases:
                time.sleep(settings.mock_db_delay)
            
            gov_result = self._check_government_db(extracted_data)
            sanctions_result = self._check_sanctions(extracted_data)
            pep_result = self._check_pep(extracted_data)
            
            verification_status = "VERIFIED"
            if sanctions_result['status'] == "flagged" or pep_result['status'] == "flagged":
                verification_status = "FLAGGED"
            elif gov_result['status'] == "not_found":
                verification_status = "FAILED"
            elif gov_result['status'] == "mismatch":
                verification_status = "PARTIAL"
            
            result = {
                "verification_status": verification_status,
                "confidence": gov_result.get('confidence', 0.5),
                "matches": {
                    "government_db": gov_result,
                    "sanctions": sanctions_result,
                    "pep": pep_result
                },
                "discrepancies": gov_result.get('discrepancies', []),
                "agent": "VerificationAgent",
                "status": "success"
            }
            
            logger.info(f"Verification completed: {verification_status}")
            return result
            
        except Exception as e:
            logger.error(f"Verification failed: {str(e)}")
            return {
                "verification_status": "ERROR",
                "confidence": 0.0,
                "matches": {},
                "discrepancies": [f"Verification error: {str(e)}"],
                "agent": "VerificationAgent",
                "status": "error"
            }
    
    def _check_government_db(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check government database"""
        records = self.mock_databases.get('government', {}).get('records', [])
        
        for record in records:
            if record['id_number'] == data.get('id_number'):
                name_similarity = calculate_name_similarity(
                    data.get('name', ''),
                    record['name']
                )
                
                if name_similarity > 0.9:
                    return {
                        "status": "match",
                        "confidence": name_similarity,
                        "details": "Exact match found in government database",
                        "record": record,
                        "discrepancies": []
                    }
                else:
                    return {
                        "status": "mismatch",
                        "confidence": name_similarity,
                        "details": f"ID found but name mismatch: {record['name']} vs {data.get('name')}",
                        "record": record,
                        "discrepancies": [f"Name mismatch: similarity {name_similarity:.2f}"]
                    }
        
        return {
            "status": "not_found",
            "confidence": 0.0,
            "details": "ID not found in government database",
            "record": None,
            "discrepancies": ["ID not found"]
        }
    
    def _check_sanctions(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check sanctions list"""
        entries = self.mock_databases.get('sanctions', {}).get('entries', [])
        
        for entry in entries:
            name_similarity = calculate_name_similarity(
                data.get('name', ''),
                entry['name']
            )
            
            if name_similarity > 0.8:
                return {
                    "status": "flagged",
                    "severity": entry.get('severity', 'HIGH'),
                    "details": f"SANCTIONS HIT: {entry['name']} - {entry['reason']}",
                    "match": entry
                }
        
        return {
            "status": "clear",
            "details": "No sanctions matches found"
        }
    
    def _check_pep(self,  Dict[str, Any]) -> Dict[str, Any]:
        """Check PEP list"""
        entries = self.mock_databases.get('pep', {}).get('entries', [])
        
        for entry in entries:
            name_similarity = calculate_name_similarity(
                data.get('name', ''),
                entry['name']
            )
            
            if name_similarity > 0.8:
                return {
                    "status": "flagged",
                    "risk_level": entry.get('risk_level', 'MEDIUM'),
                    "details": f"PEP MATCH: {entry['name']} - {entry['position']}",
                    "match": entry
                }
        
        return {
            "status": "clear",
            "details": "No PEP matches found"
        }
'''

# Fix reasoning_agent.py
reasoning_agent_fixed_part = '''
    def _generate_analysis(self, extracted_ Dict, verification_result: Dict, conclusion: str) -> str:
        """Generate human-readable analysis"""
        name = extracted_data.get('name', 'Unknown')
        id_num = extracted_data.get('id_number', 'Unknown')
        verification_status = verification_result.get('verification_status')
        
        analysis = f"Analysis for {name} (ID: {id_num}):\\n"
        analysis += f"- Verification Status: {verification_status}\\n"
        analysis += f"- Recommendation: {conclusion}\\n"
        
        matches = verification_result.get('matches', {})
        if matches.get('government_db', {}).get('status') == 'match':
            analysis += "- Government DB: ✓ Verified\\n"
        elif matches.get('government_db', {}).get('status') == 'mismatch':
            analysis += "- Government DB: ⚠ Name variation detected\\n"
        else:
            analysis += "- Government DB: ✗ Not found\\n"
        
        analysis += f"- Sanctions: {matches.get('sanctions', {}).get('status', 'unknown').upper()}\\n"
        analysis += f"- PEP: {matches.get('pep', {}).get('status', 'unknown').upper()}\\n"
        
        return analysis
'''

# Write fixed files
with open('agents/verification_agent.py', 'w') as f:
    f.write(verification_agent_fixed)

print("✅ Fixed agents/verification_agent.py")

# Note: reasoning_agent.py already has the correct signature, just missing the parameter name in _generate_analysis
# That's already been fixed in the current file

print("✅ All typing issues fixed!")
print("\nYou can now run: python main.py")