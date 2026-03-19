"""
Verification Agent - Multi-Source Verification Orchestration
"""
from typing import Dict, Any
import json
import time
import os
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
        """Load mock databases using absolute paths"""
        try:
            # Get the directory where this Python file is located
            current_dir = os.path.dirname(os.path.abspath(__file__))
            
            # Navigate to project root (one level up from agents/)
            project_root = os.path.abspath(os.path.join(current_dir, ".."))
            
            # Build absolute paths to mock data files
            mock_data_dir = os.path.join(project_root, "mock_data")
            
            gov_db_path = os.path.join(mock_data_dir, "government_db.json")
            sanctions_path = os.path.join(mock_data_dir, "sanctions_list.json")
            pep_path = os.path.join(mock_data_dir, "pep_list.json")
            
            logger.info(f"Loading mock databases from: {mock_data_dir}")
            
            with open(gov_db_path, 'r') as f:
                gov_db = json.load(f)
                logger.info(f"✅ Loaded government DB: {len(gov_db.get('records', []))} records")
            
            with open(sanctions_path, 'r') as f:
                sanctions = json.load(f)
                logger.info(f"✅ Loaded sanctions list: {len(sanctions.get('entries', []))} entries")
            
            with open(pep_path, 'r') as f:
                pep = json.load(f)
                logger.info(f"✅ Loaded PEP list: {len(pep.get('entries', []))} entries")
            
            return {'government': gov_db, 'sanctions': sanctions, 'pep': pep}
            
        except Exception as e:
            logger.error(f"❌ Failed to load mock databases: {str(e)}")
            logger.error(f"   Current dir: {os.path.dirname(os.path.abspath(__file__))}")
            logger.error(f"   Expected mock_data at: {os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'mock_data')}")
            return {}
    
    def verify(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Verify extracted data against multiple sources"""
        logger.info("Starting multi-source verification")
        
        try:
            if settings.use_mock_databases:
                time.sleep(settings.mock_db_delay)
            
            gov_result = self._check_government_db(data)
            sanctions_result = self._check_sanctions(data)
            pep_result = self._check_pep(data)
            
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
    
    def _check_government_db(self,  data: Dict[str, Any]) -> Dict[str, Any]:
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
    
    def _check_pep(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Check PEP list"""
        entries = self.mock_databases.get('pep', {}).get('entries', [])
        
        name = data.get('name', '').strip()
        dob = data.get('date_of_birth', '')
        
        for entry in entries:
            name_similarity = calculate_name_similarity(name, entry['name'])
            
            # Check both name similarity and date of birth if available
            dob_match = (dob == entry.get('date_of_birth', '')) if dob else False
            
            if name_similarity > 0.8 or dob_match:
                logger.warning(f"⚠️ PEP MATCH: {entry['name']} (similarity: {name_similarity:.2f})")
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