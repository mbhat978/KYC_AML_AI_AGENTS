"""
Test script to verify passport risk PDF files match expected behavior from RISK_SAMPLES_GUIDE.md
"""
import os
import fitz  # PyMuPDF
import re
from orchestrator.kyc_orchestrator import KYCOrchestrator

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from PDF"""
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text.strip()
    except Exception as e:
        print(f"PDF text extraction failed: {e}")
        return ""

def parse_passport_data(text: str) -> dict:
    """Parse extracted text from passport"""
    extracted_fields = {
        "document_type": "PASSPORT",
        "raw_text": text,
        "confidence": 0.85
    }
    
    lines = [line.strip() for line in text.split('\n') if line.strip()]
    
    # Extract name from passport format
    for i, line in enumerate(lines):
        if "Surname" in line and i + 1 < len(lines):
            surname = lines[i + 1]
            extracted_fields["surname"] = surname
        if "Given Names" in line and i + 1 < len(lines):
            given_names = lines[i + 1]
            extracted_fields["given_names"] = given_names
        if "Passport No" in line and i + 1 < len(lines):
            passport_no = lines[i + 1]
            extracted_fields["id_number"] = passport_no
        if "Date of Birth" in line and i + 1 < len(lines):
            dob = lines[i + 1]
            extracted_fields["date_of_birth"] = dob
        if "Nationality" in line and i + 1 < len(lines):
            nationality = lines[i + 1]
            extracted_fields["nationality"] = nationality
    
    # Build full name
    if "surname" in extracted_fields and "given_names" in extracted_fields:
        extracted_fields["name"] = f"{extracted_fields['given_names']} {extracted_fields['surname']}"
    elif "surname" in extracted_fields:
        extracted_fields["name"] = extracted_fields["surname"]
    elif "given_names" in extracted_fields:
        extracted_fields["name"] = extracted_fields["given_names"]
    else:
        extracted_fields["name"] = "Unknown"
    
    return extracted_fields

def test_passport_risk_files():
    """Test all passport risk PDF files"""
    orchestrator = KYCOrchestrator()
    
    # Expected values from RISK_SAMPLES_GUIDE.md (corrected to 0-10 scale)
    test_files = [
        ("samples/pdf/passport/passport_risk60_1.pdf", "risk60", "ESCALATE", (3.0, 4.0)),
        ("samples/pdf/passport/passport_risk70_1.pdf", "risk70", "REJECT", (6.5, 7.5)),
        ("samples/pdf/passport/passport_risk85_1.pdf", "risk85", "REJECT", (8.0, 9.0)),
    ]
    
    print("=" * 80)
    print("TESTING PASSPORT RISK PDF FILES")
    print("=" * 80)
    
    results = []
    
    for file_path, risk_level, expected_decision, expected_score_range in test_files:
        print(f"\n{'='*80}")
        print(f"Testing: {file_path}")
        print(f"Expected Risk Level: {risk_level}")
        print(f"Expected Decision: {expected_decision}")
        print(f"Expected Score Range: {expected_score_range[0]}-{expected_score_range[1]}")
        print(f"{'='*80}\n")
        
        try:
            # Read PDF file as bytes
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            
            # Extract text from PDF
            extracted_text = extract_text_from_pdf(pdf_bytes)
            print(f"Extracted text ({len(extracted_text)} chars):")
            print(extracted_text[:500] if len(extracted_text) > 500 else extracted_text)
            print()
            
            # Parse the extracted text
            extracted_fields = parse_passport_data(extracted_text)
            print(f"Parsed fields: {extracted_fields.get('name', 'Unknown')}")
            print()
            
            # Build document dictionary (like the backend does)
            document = {
                "document_type": "PASSPORT",
                "extracted_fields": extracted_fields,
                "metadata": {
                    "filename": os.path.basename(file_path),
                    "content_type": "application/pdf"
                }
            }
            
            # Process through orchestrator
            result = orchestrator.process_document(document)
            
            # Extract key information
            actual_risk = result.get('risk_score', 0)
            actual_decision = result.get('decision', 'N/A')
            actual_category = result.get('risk_category', 'N/A')
            confidence = result.get('confidence', 0)
            explanation = result.get('explanation', '')
            
            print(f"✓ File processed successfully")
            print(f"\nACTUAL RESULTS:")
            print(f"  Risk Score: {actual_risk}")
            print(f"  Risk Category: {actual_category}")
            print(f"  Decision: {actual_decision}")
            print(f"  Confidence: {confidence}")
            print(f"\nExplanation: {explanation}")
            
            # Check if results match expectations
            decision_matches = actual_decision == expected_decision
            score_in_range = expected_score_range[0] <= actual_risk <= expected_score_range[1]
            
            print(f"\n{'✓' if decision_matches else '✗'} Decision Match: {decision_matches}")
            if not decision_matches:
                print(f"  Expected: {expected_decision}")
                print(f"  Got: {actual_decision}")
            
            print(f"{'✓' if score_in_range else '✗'} Risk Score in Expected Range ({expected_score_range[0]}-{expected_score_range[1]}): {score_in_range}")
            
            test_passed = decision_matches and score_in_range
            results.append({
                'file': file_path,
                'passed': test_passed,
                'decision_match': decision_matches,
                'score_match': score_in_range
            })
            
        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'file': file_path,
                'passed': False,
                'error': str(e)
            })
        
        print(f"\n{'='*80}\n")
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for result in results:
        status = '✅ PASS' if result['passed'] else '❌ FAIL'
        print(f"{status}: {os.path.basename(result['file'])}")
        if not result['passed'] and 'error' not in result:
            if not result.get('decision_match'):
                print(f"      Decision mismatch")
            if not result.get('score_match'):
                print(f"      Score out of range")
    
    all_passed = all(r['passed'] for r in results)
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Results match RISK_SAMPLES_GUIDE.md")
    else:
        print("❌ SOME TESTS FAILED! Please review the results above.")
    print("="*80)
    
    return all_passed

if __name__ == "__main__":
    test_passport_risk_files()
