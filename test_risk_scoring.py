"""
Test Risk Scoring Fix
Tests that risk60, risk70, and risk85 samples return correct scores
"""
import sys
import json
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent))

from agents.assessment_agent import AssessmentAgent
from agents.reasoning_agent import ReasoningAgent
from agents.verification_agent import VerificationAgent

def test_risk_scoring():
    """Test risk scoring with different scenarios"""
    
    assessment_agent = AssessmentAgent()
    reasoning_agent = ReasoningAgent()
    verification_agent = VerificationAgent()
    
    print("=" * 70)
    print("TESTING RISK SCORING FIX")
    print("=" * 70)
    
    # Test Case 1: PEP Match (Robert Williams) - Should be ~6.0
    print("\n📋 Test Case 1: PEP Match (MEDIUM Risk)")
    print("-" * 70)
    
    test_data_pep = {
        'name': 'Robert Williams',
        'id_number': 'TEST001',
        'date_of_birth': '1955-07-20',
        'document_type': 'PAN'
    }
    
    verification_result_pep = verification_agent.verify(test_data_pep)
    reasoning_result_pep = reasoning_agent.reason({}, verification_result_pep)
    assessment_result_pep = assessment_agent.assess(reasoning_result_pep, verification_result_pep)
    
    print(f"Name: {test_data_pep['name']}")
    
    # Safely access PEP status
    matches = verification_result_pep.get('matches', {})
    pep_info = matches.get('pep', {})
    pep_status = pep_info.get('status', 'N/A')
    print(f"PEP Status: {pep_status}")
    if pep_status == 'flagged':
        print(f"PEP Risk Level: {pep_info.get('risk_level', 'N/A')}")
    
    print(f"Reasoning Confidence: {reasoning_result_pep['confidence']:.2f}")
    print(f"✅ Risk Score: {assessment_result_pep['risk_score']:.2f}")
    print(f"✅ Risk Category: {assessment_result_pep['risk_category']}")
    print(f"Expected: ~3.4 (MEDIUM) - Former PEP")
    
    result1_pass = 3.0 <= assessment_result_pep['risk_score'] <= 3.8
    print(f"{'✅ PASS' if result1_pass else '❌ FAIL'}: Score within expected range")
    
    # Test Case 2: Sanctions Match - HIGH severity (Maria Santos) - Should be ~7.0
    print("\n📋 Test Case 2: Sanctions Match - HIGH Severity")
    print("-" * 70)
    
    test_data_sanctions = {
        'name': 'Maria Santos',
        'id_number': 'TEST002',
        'date_of_birth': '1978-09-23',
        'document_type': 'PAN'
    }
    
    verification_result_sanctions = verification_agent.verify(test_data_sanctions)
    reasoning_result_sanctions = reasoning_agent.reason({}, verification_result_sanctions)
    assessment_result_sanctions = assessment_agent.assess(reasoning_result_sanctions, verification_result_sanctions)
    
    print(f"Name: {test_data_sanctions['name']}")
    
    # Safely access Sanctions status
    matches = verification_result_sanctions.get('matches', {})
    sanctions_info = matches.get('sanctions', {})
    sanctions_status = sanctions_info.get('status', 'N/A')
    print(f"Sanctions Status: {sanctions_status}")
    if sanctions_status == 'flagged':
        print(f"Sanctions Severity: {sanctions_info.get('severity', 'N/A')}")
    
    print(f"Reasoning Confidence: {reasoning_result_sanctions['confidence']:.2f}")
    print(f"✅ Risk Score: {assessment_result_sanctions['risk_score']:.2f}")
    print(f"✅ Risk Category: {assessment_result_sanctions['risk_category']}")
    print(f"Expected: ~7.0 (HIGH)")
    
    result2_pass = 6.5 <= assessment_result_sanctions['risk_score'] <= 7.5
    print(f"{'✅ PASS' if result2_pass else '❌ FAIL'}: Score within expected range")
    
    # Test Case 3: Sanctions Match - CRITICAL severity (Ahmed Hassan) - Should be ~8.5
    print("\n📋 Test Case 3: Sanctions Match - CRITICAL Severity")
    print("-" * 70)
    
    test_data_critical = {
        'name': 'Ahmed Hassan',
        'id_number': 'TEST003',
        'date_of_birth': '1970-01-30',
        'document_type': 'PASSPORT'
    }
    
    verification_result_critical = verification_agent.verify(test_data_critical)
    reasoning_result_critical = reasoning_agent.reason({}, verification_result_critical)
    assessment_result_critical = assessment_agent.assess(reasoning_result_critical, verification_result_critical)
    
    print(f"Name: {test_data_critical['name']}")
    
    # Safely access Sanctions status
    matches = verification_result_critical.get('matches', {})
    sanctions_info = matches.get('sanctions', {})
    sanctions_status = sanctions_info.get('status', 'N/A')
    print(f"Sanctions Status: {sanctions_status}")
    if sanctions_status == 'flagged':
        print(f"Sanctions Severity: {sanctions_info.get('severity', 'N/A')}")
    
    print(f"Reasoning Confidence: {reasoning_result_critical['confidence']:.2f}")
    print(f"✅ Risk Score: {assessment_result_critical['risk_score']:.2f}")
    print(f"✅ Risk Category: {assessment_result_critical['risk_category']}")
    print(f"Expected: ~8.5 (CRITICAL)")
    
    result3_pass = 8.0 <= assessment_result_critical['risk_score'] <= 9.0
    print(f"{'✅ PASS' if result3_pass else '❌ FAIL'}: Score within expected range")
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    all_pass = result1_pass and result2_pass and result3_pass
    print(f"Test Case 1 (PEP - MEDIUM): {'✅ PASS' if result1_pass else '❌ FAIL'}")
    print(f"Test Case 2 (Sanctions HIGH): {'✅ PASS' if result2_pass else '❌ FAIL'}")
    print(f"Test Case 3 (Sanctions CRITICAL): {'✅ PASS' if result3_pass else '❌ FAIL'}")
    print(f"\n{'🎉 ALL TESTS PASSED!' if all_pass else '❌ SOME TESTS FAILED'}")
    print("=" * 70)
    
    return all_pass

if __name__ == "__main__":
    try:
        success = test_risk_scoring()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)