"""
Test to verify backend passport parsing now works correctly
"""
import sys
import os
sys.path.insert(0, os.path.abspath('.'))

from backend.app.api.upload_routes import extract_text_from_pdf, parse_document_data

def test_passport_parsing():
    """Test that passport PDFs are parsed correctly for UI uploads"""
    
    test_files = [
        ("samples/pdf/passport/passport_risk60_1.pdf", "Robert Williams"),
        ("samples/pdf/passport/passport_risk70_1.pdf", "Maria Santos"),
        ("samples/pdf/passport/passport_risk85_1.pdf", "Ahmed Hassan"),
    ]
    
    print("=" * 80)
    print("TESTING BACKEND PASSPORT PARSING (UI Upload Path)")
    print("=" * 80)
    
    all_passed = True
    
    for file_path, expected_name in test_files:
        print(f"\nTesting: {file_path}")
        print(f"Expected name: {expected_name}")
        
        try:
            # Read PDF and extract text (like backend does)
            with open(file_path, 'rb') as f:
                pdf_bytes = f.read()
            
            extracted_text = extract_text_from_pdf(pdf_bytes)
            
            # Parse the data (like backend does)
            parsed_data = parse_document_data(extracted_text, "application/pdf")
            
            actual_name = parsed_data.get("name", "NOT FOUND")
            
            # Check if names match (case-insensitive)
            names_match = actual_name.lower() == expected_name.lower()
            
            if names_match:
                print(f"✅ PASS - Extracted name: {actual_name}")
            else:
                print(f"❌ FAIL - Extracted name: {actual_name} (expected: {expected_name})")
                all_passed = False
            
            # Show all parsed fields
            print(f"   Document type: {parsed_data.get('document_type')}")
            print(f"   ID number: {parsed_data.get('id_number', 'N/A')}")
            if 'surname' in parsed_data:
                print(f"   Surname: {parsed_data['surname']}")
            if 'given_names' in parsed_data:
                print(f"   Given names: {parsed_data['given_names']}")
                
        except Exception as e:
            print(f"❌ ERROR: {str(e)}")
            all_passed = False
    
    print("\n" + "=" * 80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Passport names are correctly parsed.")
        print("The UI should now show correct results matching RISK_SAMPLES_GUIDE.md")
    else:
        print("❌ SOME TESTS FAILED!")
    print("=" * 80)
    
    return all_passed

if __name__ == "__main__":
    test_passport_parsing()