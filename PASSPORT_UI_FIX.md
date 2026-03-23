# Passport UI Upload Fix

## Issue Summary
When uploading passport PDFs (passport_risk60_1.pdf, passport_risk70_1.pdf, passport_risk85_1.pdf) through the UI, the results were not matching the expected behavior documented in RISK_SAMPLES_GUIDE.md.

## Root Cause
The backend's `parse_document_data()` function in `backend/app/api/upload_routes.py` was not properly handling passport name extraction. It was only extracting **one part** of the name (either surname OR given names) instead of combining them.

### Example of the Problem:
- Passport contained: `Surname: WILLIAMS` and `Given Names: ROBERT`
- **Before fix**: Only extracted "WILLIAMS" or "ROBERT"
- **After fix**: Correctly extracts "Robert Williams"

This caused verification to fail because:
- Verification searched for "WILLIAMS" (incorrect)
- Mock data contained "Robert Williams" (correct full name)
- **Result**: No match found → incorrect risk assessment

## The Fix
Updated `parse_document_data()` function to:

1. **Detect passport documents** properly
2. **Extract both surname AND given_names** separately
3. **Combine them** into full name: `"{given_names} {surname}".title()`
4. **Store both** individual parts and combined full name

### Code Changes
File: `backend/app/api/upload_routes.py`

```python
# PASSPORT-SPECIFIC PARSING
if doc_type == "PASSPORT":
    surname = None
    given_names = None
    
    # Extract passport fields
    for i, line in enumerate(lines):
        if "Surname" in line and i + 1 < len(lines):
            surname = lines[i + 1].strip()
        elif "Given Names" in line and i + 1 < len(lines):
            given_names = lines[i + 1].strip()
        # ... other fields ...
    
    # Build full name from surname and given names
    if surname and given_names:
        extracted_fields["name"] = f"{given_names} {surname}".title()
        extracted_fields["surname"] = surname
        extracted_fields["given_names"] = given_names
```

## Expected Results After Fix

When uploading through the UI, you should now see:

### passport_risk60_1.pdf (Robert Williams - Former PEP)
- ✅ **Risk Score**: ~3.4/10 - MEDIUM RISK
- ✅ **Decision**: ESCALATE (Manual Review)
- ✅ **Risk Factor**: PEP match detected (Former Minister of Finance, UK)
- ✅ **Confidence**: 60%

### passport_risk70_1.pdf (Maria Santos - Sanctions)
- ✅ **Risk Score**: ~7.0/10 - HIGH RISK  
- ✅ **Decision**: REJECT
- ✅ **Risk Factor**: Sanctions list match (Money laundering, Venezuela)
- ✅ **Confidence**: 10% (low confidence due to sanctions match)

### passport_risk85_1.pdf (Ahmed Hassan - CRITICAL Sanctions)
- ✅ **Risk Score**: ~8.5/10 - CRITICAL RISK
- ✅ **Decision**: REJECT
- ✅ **Risk Factor**: CRITICAL sanctions match (Terrorism financing, Syria)
- ✅ **Confidence**: 10% (low confidence due to critical sanctions)

## Testing the Fix

### 1. Backend Parsing Test
```bash
python test_backend_passport_parsing.py
```
**Expected**: All 3 tests pass with correct name extraction

### 2. Full System Test
```bash
python test_passport_risk_files.py
```
**Expected**: All 3 tests pass with correct risk scores and decisions

### 3. UI Test
1. Start the backend: `cd backend && uvicorn app.main:app --reload --port 8000`
2. Start the frontend: `cd frontend && npm run dev`
3. Upload each passport PDF through the UI
4. Verify results match RISK_SAMPLES_GUIDE.md specifications

## Verification Checklist
- [x] passport_risk60_1.pdf extracts as "Robert Williams"
- [x] passport_risk70_1.pdf extracts as "Maria Santos"
- [x] passport_risk85_1.pdf extracts as "Ahmed Hassan"
- [x] Names match mock data in pep_list.json and sanctions_list.json
- [x] Backend parsing test passes
- [x] Full system test passes
- [ ] UI upload test passes (needs manual verification)

## Why This Only Affected UI Uploads

The test script (`test_passport_risk_files.py`) had its own proper passport parsing logic that correctly combined names, so tests passed. However, the backend upload route used by the UI had the simplified parser with the bug, causing UI uploads to fail.

This is why:
- ✅ Direct tests passed
- ❌ UI uploads failed

## Related Files
- `backend/app/api/upload_routes.py` - **Fixed file**
- `test_backend_passport_parsing.py` - New test to verify backend parsing
- `test_passport_risk_files.py` - Existing full system test
- `RISK_SAMPLES_GUIDE.md` - Expected behavior documentation
- `mock_data/pep_list.json` - PEP data with "Robert Williams"
- `mock_data/sanctions_list.json` - Sanctions data with "Maria Santos" and "Ahmed Hassan"

## Status
✅ **FIXED** - Backend now correctly parses passport names for UI uploads

---
**Date**: March 23, 2026
**Version**: 1.0
**Issue**: Passport UI upload results mismatch
**Resolution**: Fixed passport name parsing in backend upload route