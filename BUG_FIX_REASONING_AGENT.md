"""
Test script to verify the reasoning agent state management fix
"""
import json
from agents import ReasoningAgent
from loguru import logger

def test_reasoning_agent_independence():
    """Test that reasoning agent processes each document independently"""
    
    logger.info("=" * 60)
    logger.info("Testing Reasoning Agent State Management Fix")
    logger.info("=" * 60)
    
    # Create a single agent instance (simulating service-level instantiation)
    agent = ReasoningAgent()
    
    # Mock extraction result
    extraction_result = {
        "extracted_data": {
            "name": "Test User",
            "id_number": "TEST123",
            "document_type": "PAN"
        },
        "status": "success"
    }
    
    # Mock verification result with partial match (triggers reasoning logic)
    verification_result = {
        "verification_status": "PARTIAL",
        "confidence": 0.7,
        "matches": {
            "government_db": {
                "status": "mismatch",
                "confidence": 0.7
            },
            "sanctions": {"status": "clear"},
            "pep": {"status": "clear"}
        },
        "discrepancies": []
    }
    
    # Process the same document 5 times
    results = []
    for i in range(1, 6):
        logger.info(f"\n--- Processing Document #{i} ---")
        result = agent.reason(extraction_result, verification_result)
        results.append(result)
        logger.info(f"Reasoning loops used: {result.get('reasoning_loops_used')}")
        logger.info(f"Conclusion: {result.get('reasoning_conclusion')}")
        logger.info(f"Confidence: {result.get('confidence')}")
    
    # Verify all results
    logger.info("\n" + "=" * 60)
    logger.info("VERIFICATION RESULTS")
    logger.info("=" * 60)
    
    all_same_loops = all(r.get('reasoning_loops_used') == 1 for r in results)
    all_consistent = all(
        r.get('reasoning_conclusion') == results[0].get('reasoning_conclusion') 
        for r in results
    )
    
    if all_same_loops:
        logger.info("✅ SUCCESS: All documents show reasoning_loops = 1")
        logger.info("   Each document is processed independently!")
    else:
        logger.error("❌ FAILURE: Reasoning loops are accumulating across documents")
        for i, r in enumerate(results, 1):
            logger.error(f"   Document {i}: loops = {r.get('reasoning_loops_used')}")
    
    if all_consistent:
        logger.info("✅ SUCCESS: All documents have consistent conclusions")
        logger.info(f"   Conclusion: {results[0].get('reasoning_conclusion')}")
    else:
        logger.warning("⚠️  WARNING: Conclusions vary across identical documents")
        for i, r in enumerate(results, 1):
            logger.warning(f"   Document {i}: {r.get('reasoning_conclusion')}")
    
    logger.info("=" * 60)
    
    # Print summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Documents Processed: 5")
    print(f"State Independence: {'PASS ✅' if all_same_loops else 'FAIL ❌'}")
    print(f"Consistency: {'PASS ✅' if all_consistent else 'WARN ⚠️'}")
    print("=" * 60)
    
    return all_same_loops

if __name__ == "__main__":
    success = test_reasoning_agent_independence()
    exit(0 if success else 1)