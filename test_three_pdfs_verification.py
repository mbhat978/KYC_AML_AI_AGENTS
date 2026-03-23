"""
Test script to verify three specific PDF files against RISK_SAMPLES_GUIDE.md
Tests: pan_card_risk60_2.pdf, pan_card_risk70_1.pdf, pan_card_risk85_1.pdf

NOTE: Risk scores are on a 0-10 scale in the system
"""

import json
import os
import re
from pathlib import Path
from orchestrator.kyc_orchestrator import KYCOrchestrator
import fitz  # PyMuPDF

def extract_text_from_pdf(pdf_path: str) -> str:
    """Extract text from PDF using PyMuPDF"""
    try:
        doc = fitz.open(pdf_path)
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"Error extracting text from PDF: {e}")
        return ""

def parse_document_data(text: str) -> dict:
    """Parse extracted text to identify document fields"""
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
    
    # Extract basic fields
    extracted_fields = {
        "document_type": doc_type,
        "raw_text": text,
        "confidence": 0.85
    }
    
    # Extract name
    lines = text.split('\n')
    for i, line in enumerate(lines):
        line_upper = line.upper()
        if "NAME" in line_upper and i + 1 < len(lines):
            potential_name = lines[i + 1].strip()
            if len(potential_name) > 3 and potential_name.replace(' ', '').replace('.', '').isalpha():
                extracted_fields["name"] = potential_name.title()
                break
    
    # Extract PAN number
    pan_pattern = r'[A-Z]{5}[0-9]{4}[A-Z]'
    pan_match = re.search(pan_pattern, text)
    if pan_match:
        extracted_fields["id_number"] = pan_match.group()
        extracted_fields["document_type"] = "PAN"
    
    # Extract dates
    date_pattern = r'\d{2}[/-]\d{2}[/-]\d{4}'
    date_matches = re.findall(date_pattern, text)
    if date_matches:
        extracted_fields["date_of_birth"] = date_matches[0].replace('/', '-')
    
    # Fallback name
    if "name" not in extracted_fields:
        extracted_fields["name"] = "Extracted from PDF"
    
    return extracted_fields

def test_pdf_against_expected(pdf_path: str, expected_results: dict):
    """
    Test a single PDF and verify against expected results
    """
    print(f"\n{'='*80}")
    print(f"Testing: {pdf_path}")
    print(f"{'='*80}")
    
    # Initialize orchestrator
    orchestrator = KYCOrchestrator()
    
    try:
        # Extract text from PDF
        extracted_text = extract_text_from_pdf(pdf_path)
        print(f"\nExtracted {len(extracted_text)} characters from PDF")
        
        # Parse the text
        extracted_fields = parse_document_data(extracted_text)
        
        # Create document structure (same as backend upload_routes.py)
        document = {
            "document_type": extracted_fields.get("document_type", "UNKNOWN"),
            "extracted_fields": extracted_fields,
            "metadata": {
                "filename": os.path.basename(pdf_path),
                "content_type": "application/pdf"
            }
        }
        
        # Process the document
        result = orchestrator.process_document(document)
        
        # Check if result is an error
        if isinstance(result, str) or result.get('decision') == 'ERROR':
            print(f"\n❌ ERROR: {result.get('explanation', result)}")
            return False, None
        
        # Extract actual values from the orchestrator result
        actual_risk_score = result.get('risk_score', 0)
        actual_risk_category = result.get('risk_category', 'Unknown')
        actual_reasoning_confidence = result.get('confidence', 0) * 100  # Convert to percentage
        actual_decision = result.get('decision', 'Unknown')
        
        # Expected values
        expected_risk_score = expected_results['risk_score']
        expected_risk_category = expected_results['risk_category']
        expected_reasoning_confidence = expected_results['reasoning_confidence']
        expected_decision = expected_results['expected_decision']
        
        # Print comparison
        print("\n📊 VERIFICATION RESULTS:")
        print("-" * 80)
        
        # Risk Score (on 0-10 scale)
        risk_score_match = abs(actual_risk_score - expected_risk_score) <= 1.0
        print(f"\n1. RISK SCORE (0-10 scale):")
        print(f"   Expected: {expected_risk_score}/10")
        print(f"   Actual:   {actual_risk_score}/10")
        print(f"   Status:   {'✅ PASS' if risk_score_match else '❌ FAIL'}")
        
        # Risk Category
        risk_category_match = actual_risk_category.upper() == expected_risk_category.upper()
        print(f"\n2. RISK CATEGORY:")
        print(f"   Expected: {expected_risk_category}")
        print(f"   Actual:   {actual_risk_category}")
        print(f"   Status:   {'✅ PASS' if risk_category_match else '❌ FAIL'}")
        
        # Reasoning Confidence
        confidence_match = abs(actual_reasoning_confidence - expected_reasoning_confidence) <= 20
        print(f"\n3. REASONING CONFIDENCE:")
        print(f"   Expected: {expected_reasoning_confidence}%")
        print(f"   Actual:   {actual_reasoning_confidence:.1f}%")
        print(f"   Status:   {'✅ PASS' if confidence_match else '❌ FAIL'}")
        
        # Expected Decision
        decision_match = actual_decision.upper() == expected_decision.upper()
        print(f"\n4. EXPECTED DECISION:")
        print(f"   Expected: {expected_decision}")
        print(f"   Actual:   {actual_decision}")
        print(f"   Status:   {'✅ PASS' if decision_match else '❌ FAIL'}")
        
        # Overall result
        all_pass = risk_score_match and risk_category_match and confidence_match and decision_match
        print(f"\n{'='*80}")
        print(f"OVERALL: {'✅ ALL CHECKS PASSED' if all_pass else '❌ SOME CHECKS FAILED'}")
        print(f"{'='*80}")
        
        # Print detailed information
        print(f"\n📝 DETAILED INFORMATION:")
        print(f"   Explanation: {result.get('explanation', 'N/A')}")
        print(f"   Recommendation: {result.get('recommendation', 'N/A')}")
        
        # Print extracted data
        print(f"\n📄 EXTRACTED DATA:")
        extracted = result.get('extracted_data', {})
        print(f"   Name: {extracted.get('name', 'N/A')}")
        print(f"   Document Number: {extracted.get('id_number', extracted.get('document_number', 'N/A'))}")
        print(f"   Document Type: {extracted.get('document_type', 'N/A')}")
        
        return all_pass, result
        
    except Exception as e:
        print(f"\n❌ ERROR processing {pdf_path}: {str(e)}")
        import traceback
        traceback.print_exc()
        return False, None

def main():
    """
    Main test function
    """
    print("\n" + "="*80)
    print("TESTING THREE PDF FILES AGAINST RISK_SAMPLES_GUIDE.md")
    print("Note: Risk scores are on 0-10 scale")
    print("="*80)
    
    # Define test cases based on RISK_SAMPLES_GUIDE.md
    # Risk scores on 0-10 scale: 6.0 = MEDIUM, 7.0 = HIGH, 8.5 = CRITICAL
    test_cases = [
        {
            'file': 'samples/pdf/pan_card/pan_card_risk60_2.pdf',
            'name': 'Elena Rodriguez - Active PEP',
            'expected': {
                'risk_score': 6.0,  # MEDIUM risk on 0-10 scale
                'risk_category': 'MEDIUM',
                'reasoning_confidence': 60,
                'expected_decision': 'ESCALATE'
            }
        },
        {
            'file': 'samples/pdf/pan_card/pan_card_risk70_1.pdf',
            'name': 'Maria Santos - HIGH Sanctions',
            'expected': {
                'risk_score': 7.0,  # HIGH risk on 0-10 scale
                'risk_category': 'HIGH',
                'reasoning_confidence': 30,
                'expected_decision': 'REJECT'
            }
        },
        {
            'file': 'samples/pdf/pan_card/pan_card_risk85_1.pdf',
            'name': 'Ahmed Hassan - CRITICAL Sanctions',
            'expected': {
                'risk_score': 8.5,  # CRITICAL risk on 0-10 scale
                'risk_category': 'CRITICAL',
                'reasoning_confidence': 10,
                'expected_decision': 'REJECT'
            }
        }
    ]
    
    results = []
    
    # Test each PDF
    for test_case in test_cases:
        pdf_path = test_case['file']
        expected = test_case['expected']
        
        # Check if file exists
        if not os.path.exists(pdf_path):
            print(f"\n❌ File not found: {pdf_path}")
            results.append({
                'name': test_case['name'],
                'passed': False,
                'error': 'File not found'
            })
            continue
        
        passed, result = test_pdf_against_expected(pdf_path, expected)
        results.append({
            'name': test_case['name'],
            'passed': passed
        })
    
    # Final summary
    print("\n" + "="*80)
    print("FINAL SUMMARY")
    print("="*80)
    
    for i, result in enumerate(results):
        status = "✅ PASSED" if result['passed'] else "❌ FAILED"
        print(f"{i+1}. {result['name']}: {status}")
    
    total_passed = sum(1 for r in results if r['passed'])
    total_tests = len(results)
    print(f"\nTotal: {total_passed}/{total_tests} tests passed")
    
    if total_passed == total_tests:
        print("\n🎉 ALL TESTS PASSED! System is working as expected.")
        print("All risk scores, categories, confidence levels, and decisions match RISK_SAMPLES_GUIDE.md")
    else:
        print(f"\n⚠️  {total_tests - total_passed} test(s) failed. Please review the results above.")
    
    return total_passed == total_tests

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)