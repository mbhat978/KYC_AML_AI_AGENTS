# Sample Files Testing Guide

This guide provides detailed information about all generated sample files for testing the KYC/AML AI Agents system.

## 📋 Overview

This testing suite includes:
- **8 Document Images** (4 PAN cards, 4 Passports) in both .jpg and .PNG formats
- **7 Transaction CSV Files** with varying risk profiles

---

## 🆔 PAN Card Samples

### 1. PAN Card Clean Sample 1 - RAJESH KUMAR

**Document Files:**
- `samples/pan_card_clean_1.jpg` (800x500px, JPEG)
- `samples/pan_card_clean_1.PNG` (800x500px, PNG)

**Document Details:**
- PAN Number: ABCDE1234F
- Name: RAJESH KUMAR
- Father's Name: SURESH KUMAR
- Date of Birth: 15/05/1985

**Transaction File:**
- `samples/pan_card_clean_1_transactions.csv`
- **25 transactions**
- **Risk Level:** CLEAN (No AML flags)
- **Transaction Types:** Salary credits, ATM withdrawals, UPI payments, online shopping, bill payments
- **Amount Range:** ₹1,568 - ₹24,514
- **Expected Risk Score:** Low (0-20%)

**Test Case:**
```
Purpose: Test clean profile with normal transaction patterns
Expected Outcome: APPROVED or LOW RISK
AML Flags Expected: None
```

---

### 2. PAN Card Clean Sample 2 - PRIYA SHARMA

**Document Files:**
- `samples/pan_card_clean_2.jpg` (800x500px, JPEG)
- `samples/pan_card_clean_2.PNG` (800x500px, PNG)

**Document Details:**
- PAN Number: XYZPQ5678M
- Name: PRIYA SHARMA
- Father's Name: VIJAY SHARMA
- Date of Birth: 22/08/1990

**Transaction File:**
- `samples/pan_card_clean_2_transactions.csv`
- **30 transactions**
- **Risk Level:** CLEAN (No AML flags)
- **Transaction Types:** Normal banking activities
- **Amount Range:** ₹100 - ₹25,000
- **Expected Risk Score:** Low (0-20%)

**Test Case:**
```
Purpose: Test clean profile with higher transaction volume
Expected Outcome: APPROVED or LOW RISK
AML Flags Expected: None
```

---

### 3. PAN Card Sample 1 - Standard Profile

**Transaction File:**
- `samples/pan_card_sample_1_transactions.csv`
- **20 transactions**
- **Risk Level:** CLEAN/STANDARD
- **Transaction Types:** Salary, ATM, UPI, shopping, bills, medical, retail
- **Amount Range:** ₹500 - ₹35,000
- **Expected Risk Score:** Low (0-20%)

**Test Case:**
```
Purpose: Test standard profile with slightly elevated amounts
Expected Outcome: APPROVED or LOW RISK
AML Flags Expected: None
```

---

## 🛂 Passport Samples

### 1. Passport Clean Sample 1 - AMIT PATEL

**Document Files:**
- `samples/passport_clean_1.jpg` (800x600px, JPEG)
- `samples/passport_clean_1.PNG` (800x600px, PNG)

**Document Details:**
- Passport Number: K1234567
- Name: AMIT PATEL
- Date of Birth: 10/03/1988
- Nationality: INDIAN
- Issue Date: 15/01/2020
- Expiry Date: 14/01/2030

**Transaction File:**
- `samples/passport_clean_1_transactions.csv`
- **28 transactions**
- **Risk Level:** CLEAN (No AML flags)
- **Transaction Types:** Standard banking activities
- **Amount Range:** ₹100 - ₹25,000
- **Expected Risk Score:** Low (0-20%)

**Test Case:**
```
Purpose: Test clean international travel document
Expected Outcome: APPROVED or LOW RISK
AML Flags Expected: None
```

---

### 2. Passport Clean Sample 2 - SNEHA REDDY

**Document Files:**
- `samples/passport_clean_2.jpg` (800x600px, JPEG)
- `samples/passport_clean_2.PNG` (800x600px, PNG)

**Document Details:**
- Passport Number: M9876543
- Name: SNEHA REDDY
- Date of Birth: 05/11/1992
- Nationality: INDIAN
- Issue Date: 20/06/2021
- Expiry Date: 19/06/2031

**Transaction File:**
- `samples/passport_clean_2_transactions.csv`
- **22 transactions**
- **Risk Level:** CLEAN (No AML flags)
- **Transaction Types:** Normal transaction patterns
- **Amount Range:** ₹100 - ₹25,000
- **Expected Risk Score:** Low (0-20%)

**Test Case:**
```
Purpose: Test clean profile with recent passport
Expected Outcome: APPROVED or LOW RISK
AML Flags Expected: None
```

---

### 3. Passport Risk 60 - Moderate Risk Profile

**Transaction File:**
- `samples/passport_risk60_1_transactions.csv`
- **25 transactions**
- **Risk Level:** MODERATE (60% risk score)
- **Risky Transactions:** ~40% (10 transactions)
- **Transaction Types:** 
  - Normal: Salary, UPI, ATM, bills
  - Risky: Wire transfers, cash deposits, international transfers, large withdrawals
- **Amount Range:** 
  - Normal: ₹2,311 - ₹29,654
  - Risky: ₹51,762 - ₹194,547
- **AML Flags:** 10 transactions flagged
- **Risk Indicators:** 
  - Large amounts
  - Frequent large transactions
  - High-risk jurisdictions (Dubai, Singapore, Hong Kong)
  - Structuring patterns detected

**Test Case:**
```
Purpose: Test moderate risk profile with some suspicious activities
Expected Outcome: REQUIRES ENHANCED DUE DILIGENCE (EDD)
AML Flags Expected: Multiple flags for large amounts and high-risk jurisdictions
Risk Score Expected: 55-65%
```

---

### 4. Passport Risk 70 - High Risk Profile

**Transaction File:**
- `samples/passport_risk70_1_transactions.csv`
- **30 transactions**
- **Risk Level:** HIGH (70% risk score)
- **Risky Transactions:** ~60% (18 transactions)
- **Transaction Types:**
  - Normal: UPI, bill payments, online shopping
  - Risky: Wire transfers, cash deposits, international transfers, crypto exchanges
- **Amount Range:**
  - Normal: ₹1,000 - ₹25,000
  - Risky: ₹100,000 - ₹500,000
- **AML Flags:** 18 transactions flagged
- **Risk Indicators:**
  - Very large amounts
  - High-risk jurisdictions (Dubai, Cayman Islands, Panama, Switzerland)
  - PEP involvement
  - Offshore accounts
  - Sanctioned countries
  - Cryptocurrency transactions
  - Structuring and layering detected
  - Rapid fund movement

**Test Case:**
```
Purpose: Test high-risk profile with multiple red flags
Expected Outcome: REJECTED or REQUIRES INTENSIVE REVIEW
AML Flags Expected: Multiple serious flags
Risk Score Expected: 65-75%
```

---

## 🧪 Testing Instructions

### Quick Test - Single File

1. **Select a sample:**
   ```bash
   # For PAN Card
   Document: samples/pan_card_clean_1.jpg
   Transactions: samples/pan_card_clean_1_transactions.csv
   ```

2. **Upload to system:**
   - Upload the document image (.jpg or .PNG)
   - Upload the corresponding transaction CSV file

3. **Verify results:**
   - Check document extraction accuracy
   - Verify transaction analysis
   - Confirm risk scoring matches expected level

### Comprehensive Test - All Samples

1. **Test all clean profiles first:**
   ```
   - pan_card_clean_1 (both .jpg and .PNG)
   - pan_card_clean_2 (both .jpg and .PNG)
   - passport_clean_1 (both .jpg and .PNG)
   - passport_clean_2 (both .jpg and .PNG)
   ```
   **Expected:** All should be APPROVED/LOW RISK

2. **Test standard profile:**
   ```
   - pan_card_sample_1_transactions.csv
   ```
   **Expected:** APPROVED/LOW RISK

3. **Test moderate risk:**
   ```
   - passport_risk60_1_transactions.csv
   ```
   **Expected:** EDD REQUIRED, Risk Score 55-65%

4. **Test high risk:**
   ```
   - passport_risk70_1_transactions.csv
   ```
   **Expected:** REJECTED/INTENSIVE REVIEW, Risk Score 65-75%

---

## 📊 Expected Results Summary

| Sample | Document Type | Transactions | Expected Risk | Expected Outcome | AML Flags |
|--------|--------------|--------------|---------------|------------------|-----------|
| pan_card_clean_1 | PAN | 25 | Low (0-20%) | APPROVED | 0 |
| pan_card_clean_2 | PAN | 30 | Low (0-20%) | APPROVED | 0 |
| pan_card_sample_1 | - | 20 | Low (0-20%) | APPROVED | 0 |
| passport_clean_1 | Passport | 28 | Low (0-20%) | APPROVED | 0 |
| passport_clean_2 | Passport | 22 | Low (0-20%) | APPROVED | 0 |
| passport_risk60_1 | - | 25 | Moderate (60%) | EDD REQUIRED | 10 |
| passport_risk70_1 | - | 30 | High (70%) | REJECTED | 18 |

---

## 🔍 Validation Checklist

### Document Extraction Test
- [ ] PAN number extracted correctly
- [ ] Name extracted correctly
- [ ] Date of birth extracted correctly
- [ ] Document validity verified
- [ ] Image quality acceptable

### Transaction Analysis Test
- [ ] All transactions parsed correctly
- [ ] AML flags detected accurately
- [ ] Risk indicators identified
- [ ] Amount calculations correct
- [ ] Date range validated

### Risk Scoring Test
- [ ] Clean profiles score low (0-20%)
- [ ] Risk60 profiles score moderate (55-65%)
- [ ] Risk70 profiles score high (65-75%)
- [ ] Risk factors properly weighted
- [ ] Final decision aligns with risk score

### System Integration Test
- [ ] Both .jpg and .PNG formats accepted
- [ ] CSV files parsed without errors
- [ ] Results displayed correctly
- [ ] Audit trail recorded
- [ ] Performance acceptable

---

## 🐛 Troubleshooting

### Images Not Loading
- Verify files exist in `samples/` directory
- Check file permissions
- Confirm PIL/Pillow library installed

### CSV Parsing Errors
- Verify CSV headers match expected format
- Check for encoding issues (should be UTF-8)
- Ensure no missing commas or quotes

### Incorrect Risk Scores
- Review transaction analysis logic
- Verify AML flag detection
- Check risk indicator weights