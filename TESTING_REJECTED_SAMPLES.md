# Testing with Rejected Samples

## Overview
This document explains how to test the KYC/AML system with samples that will be rejected, allowing you to verify that the UI correctly displays rejection states.

## Rejected Sample: Ahmed Hassan PAN Card

### File Location
`samples/pan_card_rejected.json`

### Why This Gets Rejected
- **Name**: Ahmed Hassan
- **Date of Birth**: 1970-01-30
- **Reason**: This person appears on the **International Sanctions List**
- **Offense**: Terrorism financing
- **Severity**: CRITICAL

### Expected Results

When you upload this document, the system should:

1. **LiveFeed** should show all agent steps completing:
   - ✅ ExtractionAgent: Extracted Ahmed Hassan
   - ✅ VerificationAgent: Cross-checking databases
   - ⚠️ ReasoningAgent: Sanctions match detected
   - 🚨 AssessmentAgent: CRITICAL risk (0.95 score)
   - ❌ DecisionAgent: Final Decision: REJECT

2. **RiskMeter** should display:
   - Score: 95 (out of 100)
   - Category: CRITICAL
   - Red/critical color scheme
   - Icon: 🚨

3. **Dashboard** should show:
   - Decision Badge: ❌ REJECT (red background)
   - Risk Level: CRITICAL
   - Confidence: High (85-95%)
   - Explanation: "Application rejected due to sanctions list match"
   - Recommendation: "Do not proceed - refer to compliance team"

## Testing via Frontend

### Method 1: Manual Upload (Once UploadZone supports file selection)
1. Navigate to the frontend application
2. Click "Choose File" or drag-and-drop
3. Select `samples/pan_card_rejected.json`
4. Observe the rejection flow

### Method 2: Programmatic Testing
Currently, the backend uses a hardcoded sample document. To test the rejected sample:

**Option A: Modify Backend Temporarily**
Edit `backend/app/api/routes.py` line 28-37 to use the rejected sample:

```python
# In the stream_kyc_processing function, change:
sample_document = {
    "document_type": "PAN",
    "extracted_fields": {
        "name": "Ahmed Hassan",  # Changed
        "date_of_birth": "1970-01-30",  # Changed
        "id_number": "AHXYZ9876K",  # Changed
        "document_type": "PAN",
        "address": "456 Nehru Place, New Delhi, Delhi 110019"  # Changed
    }
}
```

**Option B: Use API Directly**
```bash
curl -X POST "http://localhost:8000/api/kyc/process" \
  -H "Content-Type: application/json" \
  -d @samples/pan_card_rejected.json
```

## Other Rejection Scenarios

### High-Risk PEP
Create a sample with:
- Name: "Elena Rodriguez" (Active Senator, HIGH risk)
- Expected: ESCALATE or HIGH risk

### Invalid/Inconsistent Data
Create a sample with:
- Mismatched dates
- Invalid ID format
- Inconsistent name spelling
- Expected: ERROR or ESCALATE

### Multiple Risk Factors
Create a sample with:
- PEP status + previous fraud indicators
- Expected: CRITICAL risk, REJECT

## Color Coding Reference

| Decision | Color | Icon | Risk Level |
|----------|-------|------|------------|
| APPROVE  | Green | ✅   | LOW        |
| ESCALATE | Yellow| ⚠️   | MEDIUM/HIGH|
| REJECT   | Red   | ❌   | CRITICAL   |

## Verification Checklist

When testing rejected samples, verify:

- [ ] RiskMeter shows correct score (80-100 for CRITICAL)
- [ ] RiskMeter has red/critical styling
- [ ] Dashboard shows REJECT badge in red
- [ ] Dashboard explanation mentions sanctions/reason
- [ ] LiveFeed shows all agent steps with warnings
- [ ] Recommendation advises against approval
- [ ] Audit trail is complete
- [ ] No JavaScript errors in console
- [ ] Animations work smoothly

## Notes

- The sanctions list is in `mock_data/sanctions_list.json`
- The PEP list is in `mock_data/pep_list.json`
- To add more rejected samples, add entries to these lists
- The system checks name and date of birth for matches

## Future Enhancements

- Add more granular risk categories
- Support partial name matching (fuzzy search)
- Add configurable risk thresholds
- Support multiple document cross-verification