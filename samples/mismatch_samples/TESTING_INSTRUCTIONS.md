# Testing Instructions for Mismatch Detection

## ✅ What Was Fixed

The verification agent now properly detects DOB and address mismatches by:
1. **Comparing DOB fields** - The extracted date from the PAN card is compared with the government database
2. **Comparing address fields** - The extracted address is compared (with fuzzy matching for format variations)
3. **Reporting discrepancies** - All mismatches are logged and included in the verification results

## 🧪 How to Test

### Step 1: Start the Application

```bash
# Make sure you're in the project root directory
python main.py
```

Or if using the frontend:
```bash
cd frontend
npm run dev
```

### Step 2: Upload Mismatch Sample PDFs

Upload one of these files from `samples/mismatch_samples/`:

1. **PAN_DOB_MISMATCH_1.pdf** - DOB off by 1 year
2. **PAN_ADDRESS_MISMATCH_1.pdf** - Different city  
3. **PAN_BOTH_MISMATCH_1.pdf** - Both DOB and address mismatch
4. **PAN_DOB_MISMATCH_2.pdf** - DOB off by 1 day
5. **PAN_ADDRESS_MISMATCH_2.pdf** - Same location, different format
6. **PAN_DOB_MISMATCH_3.pdf** - DOB off by 5 years

### Step 3: Check the Results

#### Expected Output for DOB Mismatch:

```json
{
  "verification_status": "PARTIAL",
  "confidence": 0.5,
  "matches": {
    "government_db": {
      "status": "mismatch",
      "confidence": 0.5,
      "discrepancies": [
        "DOB mismatch: DB has '1985-06-15' but document shows '15-08-1986'"
      ],
      "note": "ID matched but field mismatches detected"
    }
  },
  "discrepancies": [
    "DOB mismatch: DB has '1985-06-15' but document shows '15-08-1986'"
  ]
}
```

#### Expected Output for Address Mismatch:

```json
{
  "verification_status": "PARTIAL",
  "confidence": 0.5,
  "matches": {
    "government_db": {
      "status": "mismatch",
      "confidence": 0.5,
      "discrepancies": [
        "Address mismatch: DB has '789 Andheri West, Mumbai, Maharashtra 400058' but document shows '456 Connaught Place, New Delhi, Delhi - 110001'"
      ],
      "note": "ID matched but field mismatches detected"
    }
  },
  "discrepancies": [
    "Address mismatch: DB has '789 Andheri West, Mumbai...' but document shows '456 Connaught Place...'"
  ]
}
```

### Step 4: Check the Logs

Look for these log messages indicating mismatch detection:

```
⚠️ DOB MISMATCH: DB=1985-06-15 vs DOC=15-08-1986
⚠️ ADDRESS MISMATCH: DB=789 Andheri West, Mumbai... vs DOC=456 Connaught Place...
⚠️ Government DB: ID found but 2 discrepancies detected
```

## 🔍 What to Verify

### ✅ Successful Test Indicators:

1. **Verification Status**: Should be "PARTIAL" (not "VERIFIED")
2. **Confidence Score**: Should be low (around 0.5 or less)
3. **Discrepancies Array**: Should contain specific mismatch messages
4. **Government DB Status**: Should be "mismatch" (not "match")
5. **Risk Score**: Should be elevated due to discrepancies

### ❌ If Not Working:

1. **Check if extraction is working** - Verify the extraction agent is pulling DOB and address from the PDF
2. **Check government database** - Ensure the reference entries exist in `mock_data/government_db.json`
3. **Check date formats** - The normalization should handle DD-MM-YYYY and YYYY-MM-DD formats
4. **Check logs** - Look for warning messages starting with ⚠️

## 🐛 Troubleshooting

### Problem: All tests show "VERIFIED" status

**Solution**: The extraction agent might not be extracting DOB or address fields. Check:
```bash
# Look at the extraction output in logs
grep "Extracted data" logs/kyc_system.log
```

### Problem: No discrepancies are reported

**Solution**: The verification agent might not be passing DOB/address to the search tool. Check:
```bash
# Look for tool calls in logs
grep "search_government_db" logs/kyc_system.log
```

### Problem: Address mismatch not detected for format-only differences

**Expected**: Address format variations (like "567, Sector 15" vs "House No. 567, Sector 15") should pass with fuzzy matching. Only completely different addresses should fail.

## 📊 Expected Results Summary

| Sample File | DOB Match | Address Match | Expected Status | Expected Confidence |
|-------------|-----------|---------------|-----------------|-------------------|
| PAN_DOB_MISMATCH_1.pdf | ❌ (1 year off) | ✅ | PARTIAL | ~0.5 |
| PAN_ADDRESS_MISMATCH_1.pdf | ✅ | ❌ (Different city) | PARTIAL | ~0.5 |
| PAN_BOTH_MISMATCH_1.pdf | ❌ (1 year off) | ❌ (Different city) | PARTIAL | ~0.5 |
| PAN_DOB_MISMATCH_2.pdf | ❌ (1 day off) | ✅ | PARTIAL | ~0.5 |
| PAN_ADDRESS_MISMATCH_2.pdf | ✅ | ✅ (Format variation) | VERIFIED | ~0.8-1.0 |
| PAN_DOB_MISMATCH_3.pdf | ❌ (5 years off) | ✅ | PARTIAL | ~0.5 |

## 🔧 Advanced Testing

### Test with Custom Data:

1. Edit `mock_data/government_db.json` to add your own test entries
2. Run `python samples/create_mismatch_pan_samples.py` to regenerate PDFs
3. Upload and test

### Test Extraction Quality:

```python
# Run extraction only to check what's being extracted
from agents.extraction_agent import ExtractionAgent
agent = ExtractionAgent()
result = agent.extract("samples/mismatch_samples/PAN_DOB_MISMATCH_1.pdf")
print(result['extracted_data'])
```

### Test Verification Directly:

```python
# Test verification with known mismatched data
from agents.verification_agent import VerificationAgent
agent = VerificationAgent()
test_data = {
    'name': 'Rajesh Kumar Singh',
    'id_number': 'ABCDE1234F',
    'date_of_birth': '15-08-1986',  # Wrong - DB has 1985-06-15
    'address': '123 MG Road, Apartment 4B, Koramangala, Bangalore'
}
result = agent.verify(test_data)
print(result)
```

## 📞 Support

If mismatches still aren't being detected after following these steps:

1. Check the console output for errors
2. Review the logs in `logs/` directory
3. Verify the government database has the reference entries
4. Ensure the PDF files were created correctly (check creation timestamps)
5. Try running the extraction agent separately to see what data is being extracted

## ✨ Success Criteria

The fix is working correctly when:
- ✅ DOB mismatches are detected and reported
- ✅ Address mismatches are detected and reported  
- ✅ Verification status changes from "VERIFIED" to "PARTIAL"
- ✅ Confidence scores are reduced for mismatches
- ✅ Discrepancies array contains specific mismatch details
- ✅ Warning logs appear in the console/log files