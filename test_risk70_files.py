#!/usr/bin/env python3
"""
Test script to verify pan_card_risk70_1.pdf and pan_card_risk70_2.pdf
"""

import sys
import os
sys.path.insert(0, os.path.dirname(__file__))

import fitz  # PyMuPDF
from orchestrator.kyc_orchestrator import KYCOrchestrator

def pdf_to_document(pdf_path: str) -> dict:
    """Convert PDF to document dictionary expected by orchestrator"""
    doc = fitz.open(pdf_path)
    page = doc[0]
    text = page.get_text()
    doc.close()
    
    document = {
        "document_type": "PAN",
        "ocr_text": text,
        "metadata": {
            "file_name": os.path.basename(pdf_path),
            "confidence_score": 0.80
        }
    }
    
    return document

def test_pdf(pdf_path: str, expected_name: str, expected_severity: str):
    """Test a single PDF file"""
    
    print("\n" + "=" * 80)
    print(f"Testing: {os.path.basename(pdf_path)}")
    print(f"Expected: {expected_name}, Severity: {expected_severity}")
    print("=" * 80)
    
    orchestrator = KYCOrchestrator()
    
    try:
        document = pdf_to_document(pdf_path)
        print(f"✓ Document prepared\n")
        
        result = orchestrator.process_document(document)
        
        print("\n" + "=" * 80)
        print("RESULTS:")
        print("=" * 80)
        
        print(f"\n🎯 Risk Score: {result.get('risk_score', 'N/A')}")
        print(f"📊 Risk Category: {result.get('risk_category', 'N/A')}")
        print(f"✅ Decision: {result.get('decision', 'N/A')}")
        print(f"🔍 Overall Confidence: {result.get('confidence', 'N/A')}")
        
        # Extract data
        extracted_data = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'extraction':
                    extraction_result = log_entry.get('result', {})
                    extracted_data = extraction_result.get('extracted_data', {})
                    break
        
        if not extracted_data and 'extracted_data' in result:
            extracted_data = result['extracted_data']
        
        print(f"\n📝 Extracted Data:")
        print(f"   - Name: {extracted_data.get('name', 'N/A')}")
        print(f"   - ID Number: {extracted_data.get('id_number', 'N/A')}")
        print(f"   - DOB: {extracted_data.get('date_of_birth', 'N/A')}")
        
        # Verification
        matches = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'verification':
                    verification_result = log_entry.get('result', {})
                    matches = verification_result.get('matches', {})
                    break
        
        print(f"\n🔎 Verification Results:")
        print(f"   - Sanctions Status: {matches.get('sanctions', {}).get('status', 'N/A')}")
        if matches.get('sanctions', {}).get('status') == 'flagged':
            sanctions_details = matches.get('sanctions', {}).get('details', {})
            if isinstance(sanctions_details, dict):
                print(f"   - Sanctions Name: {sanctions_details.get('name', 'N/A')}")
                print(f"   - Sanctions Offense: {sanctions_details.get('offense', 'N/A')}")
                print(f"   - Sanctions Country: {sanctions_details.get('country', 'N/A')}")
                print(f"   - Sanctions Severity: {sanctions_details.get('severity', 'N/A')}")
        
        # Reasoning
        reasoning_result = {}
        if 'workflow_log' in result:
            for log_entry in result['workflow_log']:
                if log_entry.get('step') == 'reasoning':
                    reasoning_result = log_entry.get('result', {})
                    break
        
        reasoning_confidence = reasoning_result.get('confidence', 'N/A')
        print(f"\n💭 Reasoning:")
        print(f"   - Conclusion: {reasoning_result.get('reasoning_conclusion', 'N/A')}")
        print(f"   - ⚠️  REASONING CONFIDENCE: {reasoning_confidence}")
        
        risk_factors = reasoning_result.get('risk_factors', [])
        if risk_factors:
            print(f"   - Risk Factors:")
            for factor in risk_factors:
                print(f"     • {factor}")
        
        # Highlight the issue
        print("\n" + "=" * 80)
        print("ANALYSIS:")
        print("=" * 80)
        
        sanctions_details = matches.get('sanctions', {}).get('details', {})
        actual_severity = sanctions_details.get('severity', 'N/A') if isinstance(sanctions_details, dict) else 'N/A'
        
        print(f"\nSanctions Severity: {actual_severity}")
        print(f"Reasoning Confidence: {reasoning_confidence}")
        
        if actual_severity == "HIGH" and reasoning_confidence == 0.1:
            print("\n⚠️  ISSUE DETECTED:")
            print("   - Severity is HIGH (money laundering/financial crimes)")
            print("   - But reasoning confidence is 0.1 (10%)")
            print("   - Expected confidence for HIGH severity: 0.28-0.30 (28-30%)")
            print("   - Confidence of 0.1 is typically for CRITICAL severity (terrorism)")
        elif actual_severity == "CRITICAL" and reasoning_confidence == 0.1:
            print("\n✅ CORRECT:")
            print("   - Severity is CRITICAL")
            print("   - Reasoning confidence is 0.1 (10%) - as expected")
        
        return result
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    print("=" * 80)
    print("Testing HIGH RISK (Risk 70) Samples")
    print("Investigating reasoning confidence issue")
    print("=" * 80)
    
    # Test both files
    test_pdf("samples/pdf/pan_card/pan_card_risk70_1.pdf", "Maria Santos", "HIGH")
    test_pdf("samples/pdf/pan_card/pan_card_risk70_2.pdf", "Victor Petrov", "HIGH")