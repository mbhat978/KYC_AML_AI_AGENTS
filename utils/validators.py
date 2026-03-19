"""
Validation utilities for KYC/AML data
"""
import re
from typing import Dict, Any, Tuple
from datetime import datetime
from difflib import SequenceMatcher
from loguru import logger


def validate_name(name: str) -> Tuple[bool, str]:
    """Validate name format"""
    if not name or len(name.strip()) < 2:
        return False, "Name too short"
    
    if not re.match(r'^[a-zA-Z\s\.\-]+$', name):
        return False, "Name contains invalid characters"
    
    return True, "Valid"


def validate_date_of_birth(dob: str) -> Tuple[bool, str]:
    """Validate date of birth"""
    try:
        date_obj = datetime.strptime(dob, "%Y-%m-%d")
        age = (datetime.now() - date_obj).days / 365.25
        
        if age < 18:
            return False, "Applicant must be 18 or older"
        if age > 120:
            return False, "Invalid age"
        
        return True, "Valid"
    except ValueError:
        return False, "Invalid date format (expected YYYY-MM-DD)"


def validate_pan(pan: str) -> Tuple[bool, str]:
    """Validate Indian PAN card number"""
    pattern = r'^[A-Z]{5}[0-9]{4}[A-Z]$'
    if re.match(pattern, pan):
        return True, "Valid"
    return False, "Invalid PAN format"


def validate_passport(passport: str) -> Tuple[bool, str]:
    """Validate passport number"""
    pattern = r'^[A-Z]{1}[0-9]{7}$'
    if re.match(pattern, passport):
        return True, "Valid"
    return False, "Invalid passport format"


def validate_drivers_license(dl: str) -> Tuple[bool, str]:
    """Validate driver's license"""
    if len(dl) >= 8 and len(dl) <= 16:
        return True, "Valid"
    return False, "Invalid driver's license format"


def calculate_name_similarity(name1: str, name2: str) -> float:
    """Calculate similarity score between two names"""
    name1_clean = name1.lower().strip()
    name2_clean = name2.lower().strip()
    
    if name1_clean == name2_clean:
        return 1.0
    
    similarity = SequenceMatcher(None, name1_clean, name2_clean).ratio()
    
    name1_parts = set(name1_clean.split())
    name2_parts = set(name2_clean.split())
    
    if name1_parts.issubset(name2_parts) or name2_parts.issubset(name1_parts):
        similarity = max(similarity, 0.85)
    
    return similarity


def normalize_address(address: str) -> str:
    """Normalize address for comparison"""
    normalized = re.sub(r'\s+', ' ', address.lower().strip())
    
    abbreviations = {
        r'\bst\b': 'street',
        r'\brd\b': 'road',
        r'\bave\b': 'avenue',
        r'\bapt\b': 'apartment',
        r'\bfl\b': 'floor',
    }
    
    for abbr, full in abbreviations.items():
        normalized = re.sub(abbr, full, normalized)
    
    return normalized


def validate_extracted_data(data: Dict[str, Any]) -> Tuple[bool, list]:
    """Validate extracted document data"""
    errors = []
    
    required_fields = ['name', 'date_of_birth', 'id_number', 'document_type']
    
    for field in required_fields:
        if field not in data or not data[field]:
            errors.append(f"Missing required field: {field}")
    
    if 'name' in data and data['name']:
        is_valid, msg = validate_name(data['name'])
        if not is_valid:
            errors.append(f"Name validation failed: {msg}")
    
    if 'date_of_birth' in data and data['date_of_birth']:
        is_valid, msg = validate_date_of_birth(data['date_of_birth'])
        if not is_valid:
            errors.append(f"DOB validation failed: {msg}")
    
    return len(errors) == 0, errors