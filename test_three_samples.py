"""
Test Three Sample PDFs Against RISK_SAMPLES_GUIDE.md
Validates: Risk Score, Risk Category, Reasoning Confidence, Expected Decision
"""
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from orchestrator.kyc_orchestrator import KYCOrchestrator
from utils.pdf_converter import PDFConverter

def test_sample_pdf(pdf_path: str, expected_data: dict):
    """Test a single PDF and compare with expected results"""
    print("\n" + "="*80)
    print(f"Testing: {Path(pdf_path).name}")
    print("="*80)
    
    # Convert PDF to document format
    #document = PDFConverter.convert_pdf_to_base64(pdf_path)
    # Convert PDF to base64 image string
    base64_string, mime_type = PDFConverter.convert_pdf_to_base64(pdf_path)

# Build the document dictionary manually for the Orchestrator
    document = {
        "document_type": "PAN", # Update this if the test is for PASSPORT or DRIVERS_LICENSE
        "file_data": f"data:{mime_type};base64,{base64_string}",
        "filename": os.path.basename(pdf_path)
    }
    # Process through orchestrator
    orchestrator = KYCOrchestrator()
    result = orchestrator.process_document(document)
    
    # Extract results
    actual_risk_score = result.get('assessment', {}).get('risk_score', 0)
    actual_risk_category = result.get('assessment', {}).get('risk_category', 'UNKNOWN')
    actual_reasoning_confidence = result.get('reasoning', {}).get('confidence', 0)
    actual_decision = result.get('decision', {}).get('final_decision', 'UNKNOWN')
    
    # Display results
    print("\n📊 ACTUAL RESULTS:")
    print(f"   Risk Score: {actual_risk_score:.2f}")
    print(f"   Risk Category: {actual_risk_category}")
    print(f"   Reasoning Confidence: {actual_reasoning_confidence:.2f}")
    print(f"   Decision: {actual_decision}")
    
    print("\n📋 EXPECTED (from RISK_SAMPLES_GUIDE.md):")
    print(f"   Risk Score: {expected_data['risk_score']}")
    print(f"   Risk Category: {expected_data['risk_category']}")
    print(f"   Reasoning Confidence: {expected_data['reasoning_confidence']}")
    print(f"   Expected Decision: {expected_data['decision']}")
    
    # Validation
    print("\n✅ VALIDATION:")
    
    # Risk Score validation (with tolerance)
    risk_score_min, risk_score_max = expected_data['risk_score_range']
    risk_score_match = risk_score_min <= actual_risk_score <= risk_score_max
    print(f"   {'✅' if risk_score_match else '❌'} Risk Score: {actual_risk_score:.2f} "
          f"({'PASS' if risk_score_match else 'FAIL'} - expected {risk_score_min}-{risk_score_max})")
    
    # Risk Category validation
    category_match = actual_risk_category == expected_data['risk_category']
    print(f"   {'✅' if category_match else '❌'} Risk Category: {actual_risk_category} "
          f"({'PASS' if category_match else 'FAIL'} - expected {expected_data['risk_category']})")
    
    # Reasoning Confidence validation (with tolerance)
    conf_min, conf_max = expected_data['confidence_range']
    confidence_match = conf_min <= actual_reasoning_confidence <= conf_max
    print(f"   {'✅' if confidence_match else '❌'} Reasoning Confidence: {actual_reasoning_confidence:.2f} "
          f"({'PASS' if confidence_match else 'FAIL'} - expected {conf_min}-{conf_max})")
    
    # Decision validation
    decision_match = actual_decision == expected_data['decision']
    print(f"   {'✅' if decision_match else '❌'} Decision: {actual_decision} "
          f"({'PASS' if decision_match else 'FAIL'} - expected {expected_data['decision']})")
    
    # Overall result
    all_pass = risk_score_match and category_match and confidence_match and decision_match
    print(f"\n{'🎉 ALL VALIDATIONS PASSED!' if all_pass else '❌ SOME VALIDATIONS FAILED!'}")
    
    return all_pass

def main():
    """Test all three sample PDFs"""
    print("="*80)
    print("TESTING THREE SAMPLE PDFs AGAINST RISK_SAMPLES_GUIDE.md")
    print("="*80)
    
    # Expected data from RISK_SAMPLES_GUIDE.md
    test_cases = [
        {
            'pdf_path': 'samples/pdf/pan_card/pan_card_risk60_2.pdf',
            'name': 'pan_card_risk60_2.pdf (Elena Rodriguez - Active PEP)',
            'expected': {
                'risk_score': '~6.0/10',
                'risk_score_range': (5.8, 6.2),
                'risk_category': 'MEDIUM',
                'reasoning_confidence': '0.60',
                'confidence_range': (0.55, 0.65),
                'decision': 'ESCALATE'
            }
        },
        {
            'pdf_path': 'samples/pdf/pan_card/pan_card_risk70_1.pdf',
            'name': 'pan_card_risk70_1.pdf (Maria Santos - HIGH Sanctions)',
            'expected': {
                'risk_score': '~7.0/10',
                'risk_score_range': (6.8, 7.2),
                'risk_category': 'HIGH',
                'reasoning_confidence': '0.30',
                'confidence_range': (0.10, 0.40),
                'decision': 'REJECT'
            }
        },
        {
            'pdf_path': 'samples/pdf/pan_card/pan_card_risk85_1.pdf',
            'name': 'pan_card_risk85_1.pdf (Ahmed Hassan - CRITICAL Sanctions)',
            'expected': {
                'risk_score': '~8.5/10',
                'risk_score_range': (8.3, 8.7),
                'risk_category': 'CRITICAL',
                'reasoning_confidence': '0.10',
                'confidence_range': (0.05, 0.15),
                'decision': 'REJECT'
            }
        }
    ]
    
    results = []
    
    # Test each PDF
    for test_case in test_cases:
        try:
            passed = test_sample_pdf(test_case['pdf_path'], test_case['expected'])
            results.append({
                'name': test_case['name'],
                'passed': passed
            })
        except Exception as e:
            print(f"\n❌ ERROR processing {test_case['name']}: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append({
                'name': test_case['name'],
                'passed': False
            })
    
    # Summary
    print("\n" + "="*80)
    print("SUMMARY")
    print("="*80)
    
    for result in results:
        status = '✅ PASS' if result['passed'] else '❌ FAIL'
        print(f"{status}: {result['name']}")
    
    all_passed = all(r['passed'] for r in results)
    print("\n" + "="*80)
    if all_passed:
        print("🎉 ALL TESTS PASSED! Results match RISK_SAMPLES_GUIDE.md")
    else:
        print("❌ SOME TESTS FAILED! Please review the results above.")
    print("="*80)
    
    return all_passed

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ FATAL ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)