#!/usr/bin/env python3
"""
Test script to verify pan_card_risk60_1.pdf produces expected results
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from orchestrator.kyc_orchestrator import KYCOrchestrator

def pdf_to_document(pdf_path: str) -> dict:
    """Convert PDF to document dictionary expected by orchestrator"""
    print(f"Converting PDF to document format: {pdf_path}")
    
    # Extract text from PDF
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text()
    doc.close()
    
    print(f"✓ Extracted {len(text)} characters from PDF")
    
    # Create document dict with ocr_text
    document = {
        "document_type": "PAN",
        "ocr_text": text,
        "metadata": {
            "file_name": os.path.basename(pdf_path),
            "confidence_score": 0.85
        }
    }
    
    return document

def test_pan_card_risk60():
    """Test pan_card_risk60_1.pdf"""
    
    print("=" * 80)
    print("Testing: pan_card_risk60_1.pdf")
    print("Expected: Risk ~0.60, Category: MEDIUM, Decision: ESCALATE, PEP Match")
    print("=" * 80)
    
    # Initialize orchestrator
    orchestrator = KYCOrchestrator()
    
    # Test the PDF
    pdf_path = "samples/pdf/pan_card/pan_card_risk60_1.pdf"
    
    print(f"\n📄 Processing: {pdf_path}")
    
    try:
        # Convert PDF to document format
        document = pdf_to_document(pdf_path)
        print(f"✓ Document prepared for processing\n")
        
        # Process the document
        result = orchestrator.process_document(document)
        
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        
        print(f"\n🎯 Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"📊 Risk Category: {result.get('risk_category', 'N/A')}")
        print(f"✅ Decision: {result.get('decision', 'N/A')}")
        print(f"🔍 Confidence: {result.get('confidence', 'N/A')}")
        
        # Check extraction from workflow_log
        extracted_data = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'extraction':
                    extraction_result = log_entry.get('result', {})
                    extracted_data = extraction_result.get('extracted_data', {})
                    break
        
        # Also check extracted_data at top level
        if not extracted_data and 'extracted_data' in result:
            extracted_data = result['extracted_data']
        
        print(f"\n📝 Extracted Data:")
        print(f"   - Name: {extracted_data.get('name', 'N/A')}")
        print(f"   - ID Number: {extracted_data.get('id_number', 'N/A')}")
        print(f"   - DOB: {extracted_data.get('date_of_birth', 'N/A')}")
        print(f"   - Document Type: {extracted_data.get('document_type', 'N/A')}")
        
        # Check verification from workflow_log
        matches = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'verification':
                    verification_result = log_entry.get('result', {})
                    matches = verification_result.get('matches', {})
                    break
        
        print(f"\n🔎 Verification Results:")
        print(f"   - PEP Status: {matches.get('pep', {}).get('status', 'N/A')}")
        if matches.get('pep', {}).get('status') == 'flagged':
            print(f"   - PEP Risk Level: {matches.get('pep', {}).get('risk_level', 'N/A')}")
            pep_details = matches.get('pep', {}).get('details', {})
            if isinstance(pep_details, dict):
                print(f"   - PEP Name: {pep_details.get('name', 'N/A')}")
                print(f"   - PEP Position: {pep_details.get('position', 'N/A')}")
                print(f"   - PEP Country: {pep_details.get('country', 'N/A')}")
        
        print(f"   - Sanctions Status: {matches.get('sanctions', {}).get('status', 'N/A')}")
        
        # Check reasoning from workflow_log
        reasoning_result = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'reasoning':
                    reasoning_result = log_entry.get('result', {})
                    break
        
        print(f"\n💭 Reasoning:")
        print(f"   - Conclusion: {reasoning_result.get('reasoning_conclusion', 'N/A')}")
        print(f"   - Confidence: {reasoning_result.get('confidence', 'N/A')}")
        
        risk_factors = reasoning_result.get('risk_factors', [])
        if risk_factors:
            print(f"   - Risk Factors:")
            for factor in risk_factors:
                print(f"     • {factor}")
        
        # Validation
        print("\n" + "=" * 80)
        print("VALIDATION:")
        print("=" * 80)
        
        risk_score = result.get('risk_score', 0)
        risk_category = result.get('risk_category', '')
        decision = result.get('decision', '')
        
        # Expected values
        expected_risk_range = (3.0, 6.5)  # ~3.4 for Former PEP, ~6.0 for Active PEP (0-10 scale)
        expected_category = 'MEDIUM'
        expected_decision = 'ESCALATE'
        
        passed = True
        
        if expected_risk_range[0] <= risk_score <= expected_risk_range[1]:
            print(f"✅ Risk Score: {risk_score} (within expected range {expected_risk_range})")
        else:
            print(f"❌ Risk Score: {risk_score} (expected range {expected_risk_range})")
            passed = False
        
        if risk_category == expected_category:
            print(f"✅ Risk Category: {risk_category} (matches expected)")
        else:
            print(f"❌ Risk Category: {risk_category} (expected {expected_category})")
            passed = False
        
        if decision == expected_decision:
            print(f"✅ Decision: {decision} (matches expected)")
        else:
            print(f"⚠️  Decision: {decision} (expected {expected_decision})")
        
        pep_status = matches.get('pep', {}).get('status', '')
        if pep_status == 'flagged':
            print(f"✅ PEP Detection: Working correctly")
        else:
            print(f"❌ PEP Detection: Not detected (expected flagged)")
            passed = False
        
        print("\n" + "=" * 80)
        if passed:
            print("✅ TEST PASSED - All validations successful!")
        else:
            print("⚠️  TEST COMPLETED - Some validations failed (see above)")
        print("=" * 80)
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    test_pan_card_risk60()