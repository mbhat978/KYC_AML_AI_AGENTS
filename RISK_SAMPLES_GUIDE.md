# Risk Samples Guide - Complete Documentation

## Overview
This comprehensive guide documents all sample documents (JSON and PDF) available for testing the KYC/AML system. Each sample includes detailed information about risk scores, confidence levels, risk categories, and expected system behavior.

---

## Understanding Risk Assessment Metrics

### Risk Score Scale (0-10)
- **0 - 4.0**: LOW RISK - Document passes all checks
- **4.1 - 7.0**: MEDIUM RISK - Minor to moderate concerns detected
- **7.1 - 10**: HIGH/CRITICAL RISK - Significant issues, likely rejection

### Risk Categories
- **LOW**: Clean verification, no red flags
- **MEDIUM**: PEP matches, minor inconsistencies, requires review
- **HIGH**: Sanctions matches, financial crimes, multiple red flags
- **CRITICAL**: Terrorism financing, severe sanctions, immediate rejection

### Confidence Scores
The system uses TWO types of confidence:

1. **Extraction Confidence** (0.70-0.95): How accurately text was extracted from document
2. **Reasoning Confidence** (0.10-0.90): How certain the system is about the risk decision

**See `CONFIDENCE_SCORES_EXPLAINED.md` for detailed explanation**

### Decision Types
- **APPROVE**: Low risk, automatic approval
- **ESCALATE**: Medium risk, manual review required
- **REJECT**: High/Critical risk, automatic rejection

---

# JSON Samples

All JSON samples located in `samples/json/`

## 1. Valid PAN Card (`pan_card.json`)

### Document Information
- **Document Type**: PAN Card
- **Name**: Rajesh Kumar Sharma
- **Father's Name**: Mohan Lal Sharma
- **Date of Birth**: 15/06/1985
- **PAN Number**: ABCDE1234F
- **Address**: 123 MG Road, Bangalore, Karnataka 560001

### Risk Assessment
- **Risk Score**: ~1.5/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 95% (High quality document)
- **Reasoning Confidence**: 90% (Very confident in approval)
- **Expected Decision**: **APPROVE**

### Verification Results
- ✅ Government database: VERIFIED
- ✅ PAN format: VALID
- ✅ PEP check: CLEAR
- ✅ Sanctions check: CLEAR
- ✅ Data consistency: HIGH

### Use Case
Perfect for testing successful KYC verification flow with clean Indian identity document.

---

## 2. Rejected PAN Card (`pan_card_rejected.json`)

### Document Information
- **Document Type**: PAN Card
- **Name**: Ahmed Hassan
- **Father's Name**: Abdul Hassan
- **Date of Birth**: 30/01/1970
- **PAN Number**: AHXYZ9876K
- **Address**: 456 Nehru Place, New Delhi, Delhi 110019

### Risk Assessment
- **Risk Score**: ~8.5/10 - **CRITICAL RISK**
- **Risk Category**: CRITICAL
- **Extraction Confidence**: 92% (Good quality extraction)
- **Reasoning Confidence**: 10% (Very low - sanctions match triggers rejection)
- **Expected Decision**: **REJECT**

### Verification Results
- ❌ Sanctions list: **CRITICAL MATCH** - Terrorism financing (Syria)
- ❌ Risk level: CRITICAL
- ⚠️ High-risk jurisdiction
- ⚠️ Severe sanctions violations

### Risk Factors
1. **Terrorism Financing** (CRITICAL severity) - +60 points
2. **Sanctions list match** - Syria-based individual
3. **High-risk country** - +20 points
4. **Multiple red flags** - Automatic rejection

### Use Case
Tests the rejection flow for sanctioned individuals with critical risk factors.

---

## 3. Valid Passport (`passport.json`)

### Document Information
- **Document Type**: Passport
- **Name**: Jonathan David Miller
- **Nationality**: British
- **Date of Birth**: 30/11/1988
- **Passport Number**: K1234567
- **Sex**: M
- **Issue Date**: 15/01/2020
- **Expiry Date**: 15/01/2030
- **Address**: 789 Baker Street, London, UK SW1A 1AA

### Risk Assessment
- **Risk Score**: ~2.0/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 92% (Good quality passport scan)
- **Reasoning Confidence**: 90% (Very confident in approval)
- **Expected Decision**: **APPROVE**

### Verification Results
- ✅ Passport format: VALID
- ✅ Not expired: Valid until 2030
- ✅ MRZ validation: PASSED
- ✅ PEP check: CLEAR
- ✅ Sanctions check: CLEAR
- ✅ Country risk: LOW (UK)

### Use Case
Tests international document verification with Western passport standards.

---

## 4. Valid Driver's License (`drivers_license.json`)

### Document Information
- **Document Type**: California Driver's License
- **Name**: Sarah Johnson
- **Date of Birth**: 08/10/1992
- **License Number**: DL1234567890
- **Address**: 321 Oak Avenue, San Francisco, CA 94102
- **Issue Date**: 01/15/2022
- **Expiry Date**: 08/10/2027
- **License Class**: C

### Risk Assessment
- **Risk Score**: ~1.8/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 89% (Good quality US license)
- **Reasoning Confidence**: 88% (High confidence in approval)
- **Expected Decision**: **APPROVE**

### Verification Results
- ✅ License format: VALID (California DMV)
- ✅ Not expired: Valid until 2027
- ✅ State verification: PASSED
- ✅ PEP check: CLEAR
- ✅ Sanctions check: CLEAR
- ✅ Address verification: VALID

### Use Case
Tests US state-issued document processing and address verification.

---

# PDF Samples

All PDF samples located in `samples/pdf/`

## PAN Card PDF Samples

Location: `samples/pdf/pan_card/`

### Valid/Low Risk PAN Cards

#### 1. `pan_card_sample_1.pdf`

**Profile**: Clean Indian citizen with verified identity

- **Risk Score**: ~1.5/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 95%
- **Reasoning Confidence**: 90%
- **Expected Decision**: **APPROVE**

**Document Characteristics**:
- ✅ High-quality PDF scan
- ✅ All text clearly readable
- ✅ Proper PAN card format
- ✅ Valid data structure
- ✅ No signs of tampering
- ✅ Security features intact

**Typical Contents**:
- Valid PAN number format (e.g., ABCDE1234F)
- Indian citizen name
- Clear date of birth
- Father's name present
- Income Tax Department header

**Use Case**: Baseline test for clean, approved documents.

---

#### 2. `pan_card_sample_2.pdf`

**Profile**: Standard quality document with minor artifacts

- **Risk Score**: ~1.8/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 93%
- **Reasoning Confidence**: 88%
- **Expected Decision**: **APPROVE**

**Document Characteristics**:
- ✅ Good quality document
- ⚠️ Minor scanning artifacts (acceptable)
- ✅ Valid format maintained
- ✅ All verifications pass
- ✅ Data fully extractable

**Use Case**: Tests system tolerance for minor quality issues that don't affect verification.

---

#### 3. `pan_card_sample_3.pdf`

**Profile**: Acceptable quality with slight degradation

- **Risk Score**: ~2.2/10 - **LOW RISK**
- **Risk Category**: LOW
- **Extraction Confidence**: 90%
- **Reasoning Confidence**: 85%
- **Expected Decision**: **APPROVE**

**Document Characteristics**:
- ✅ Acceptable quality
- ⚠️ Slight image quality variations
- ✅ Data fully extractable
- ✅ No red flags
- ✅ Within acceptable thresholds

**Use Case**: Tests lower-bound of acceptable document quality for approval.

---

### Medium Risk PAN Cards

#### 4. `pan_card_risk60_1.pdf`

**Profile**: Robert Williams - Former UK Minister of Finance (PEP)

- **Risk Score**: ~3.4/10 - **MEDIUM RISK** (Note: Former PEP = lower than active PEP)
- **Risk Category**: MEDIUM
- **Extraction Confidence**: 85%
- **Reasoning Confidence**: 60%
- **Expected Decision**: **ESCALATE** (Manual Review)

**Risk Factors**:
- ⚠️ **PEP Match**: Former Minister of Finance, United Kingdom
- ⚠️ **Political Position**: Former high-ranking government official
- ⚠️ Risk Level: MEDIUM (former, not active)
- ℹ️ Status: Requires enhanced due diligence

**Document Characteristics**:
- Moderate image quality
- Some data fields partially obscured
- Minor inconsistencies in formatting
- Requires human verification

**Verification Results**:
- PEP Database: **MATCH FOUND**
- Position: Former Minister of Finance
- Country: United Kingdom
- Status: Former (not currently active)
- Risk Assessment: Enhanced due diligence required

**Why Medium Risk?**
- Former PEPs carry residual risk (+15-20 points)
- Need to verify source of funds
- Enhanced monitoring recommended
- Not automatic rejection but requires review

**Use Case**: Tests PEP detection and escalation workflows.

---

#### 5. `pan_card_risk60_2.pdf`

**Profile**: Elena Rodriguez - Active Senator, Mexico (PEP)

- **Risk Score**: ~6.0/10 - **MEDIUM RISK** (Active PEP = higher risk)
- **Risk Category**: MEDIUM
- **Extraction Confidence**: 83%
- **Reasoning Confidence**: 60%
- **Expected Decision**: **ESCALATE** (Manual Review)

**Risk Factors**:
- ⚠️ **PEP Match**: Active Senator, Mexico
- ⚠️ **Political Position**: Currently serving government official
- ⚠️ Risk Level: MEDIUM-HIGH (active position)
- ℹ️ Status: Requires enhanced due diligence

**Document Characteristics**:
- Compression artifacts present
- Date format anomalies
- Slight misalignment detected
- Verification confidence reduced

**Verification Results**:
- PEP Database: **MATCH FOUND**
- Position: Active Senator
- Country: Mexico
- Status: Currently serving
- Risk Assessment: Enhanced due diligence mandatory

**Why Medium Risk?**
- Active PEPs require careful scrutiny (+20 points)
- Potential for corruption or bribery concerns
- Source of wealth verification essential
- Not rejection but mandatory review

**Use Case**: Tests active PEP detection with international officials.

---

### High Risk PAN Cards

#### 6. `pan_card_risk70_1.pdf`

**Profile**: Maria Santos - Sanctions List Match (Money Laundering, Venezuela)

- **Risk Score**: ~7.0/10 - **HIGH RISK**
- **Risk Category**: HIGH
- **Extraction Confidence**: 80%
- **Reasoning Confidence**: 30%
- **Expected Decision**: **ESCALATE** or **REJECT**

**Risk Factors**:
- ❌ **Sanctions Match**: Money laundering activities
- ⚠️ Country: Venezuela (high-risk jurisdiction)
- ⚠️ Severity: HIGH (financial crimes)
- ⚠️ Multiple red flags present

**Document Characteristics**:
- Significant quality degradation
- Data extraction challenges
- Possible photocopied document
- Enhanced scrutiny required

**Verification Results**:
- Sanctions List: **MATCH FOUND**
- Offense: Money laundering
- Country: Venezuela
- Severity: HIGH
- Risk Assessment: Strong rejection candidate

**Why High Risk?**
- Sanctions matches are serious (+40 points)
- Financial crimes history
- High-risk country (+20 points)
- Likely requires rejection or intensive review

**Use Case**: Tests sanctions list detection for financial crimes.

---

#### 7. `pan_card_risk70_2.pdf`

**Profile**: Victor Petrov - Sanctions List Match (Financial Crimes, Russia)

- **Risk Score**: ~7.2/10 - **HIGH RISK**
- **Risk Category**: HIGH
- **Extraction Confidence**: 78%
- **Reasoning Confidence**: 28%
- **Expected Decision**: **ESCALATE** or **REJECT**

**Risk Factors**:
- ❌ **Sanctions Match**: Financial crimes
- ⚠️ Country: Russia (geopolitical concerns)
- ⚠️ Severity: HIGH
- ⚠️ Borderline rejection threshold

**Document Characteristics**:
- Poor scan quality
- Text readability issues
- Inconsistent metadata
- Careful review needed

**Verification Results**:
- Sanctions List: **MATCH FOUND**
- Offense: Financial crimes
- Country: Russia
- Severity: HIGH
- Risk Assessment: High probability of rejection

**Why High Risk?**
- Financial crimes sanctions (+40 points)
- Geopolitical risk factors
- Multiple verification concerns
- Strong rejection candidate

**Use Case**: Tests sanctions list detection with geopolitical context.

---

### Critical Risk PAN Cards

#### 8. `pan_card_risk85_1.pdf`

**Profile**: Ahmed Hassan - CRITICAL Sanctions Match (Terrorism Financing, Syria)

- **Risk Score**: ~8.5/10 - **CRITICAL RISK**
- **Risk Category**: CRITICAL
- **Extraction Confidence**: 85%
- **Reasoning Confidence**: 10%
- **Expected Decision**: **REJECT**

**Risk Factors**:
- ❌ **CRITICAL Sanctions Match**: Terrorism financing
- ❌ Country: Syria (high-risk jurisdiction)
- ❌ Severity: CRITICAL (most severe category)
- ❌ Automatic rejection trigger
- ⚠️ Listed since 2020-06-22

**Document Characteristics**:
- Severe quality issues
- Signs of potential tampering
- Data inconsistencies
- Failed multiple verification checks

**Verification Results**:
- Sanctions List: **CRITICAL MATCH FOUND**
- Offense: Terrorism financing
- Country: Syria
- Severity: CRITICAL
- Risk Assessment: Immediate rejection required

**Why Critical Risk?**
- Terrorism financing is the most severe category (+60 points)
- CRITICAL severity sanctions trigger automatic rejection
- No manual review option - must reject
- Highest possible risk factors
- Legal requirement to deny service

**Use Case**: Tests critical sanctions detection and mandatory rejection flow.

---

#### 9. `pan_card_risk85_2.pdf`

**Profile**: Ahmed H. - Alias of Sanctioned Individual (Terrorism)

- **Risk Score**: ~0
This will create:
- 3 MEDIUM risk documents (risk score 0.60)
- 3 HIGH risk documents (risk score 0.70)
- 3 CRITICAL risk documents (risk score 0.85)
- Total: 9 PAN card PDFs + 6 passport PDFs = 15 files

---

## Related Documentation

- **CONFIDENCE_SCORES_EXPLAINED.md** - Detailed explanation of confidence metrics
- **TESTING_GUIDE.md** - Comprehensive system testing procedures
- **PDF_UPLOAD_GUIDE.md** - PDF upload and troubleshooting
- **RISK_SCORING_FIX.md** - Recent fixes to risk scoring system

---

## Support & Troubleshooting

### Common Issues

1. **Document not processing**: Check file format (PDF only for PDFs, JSON for JSON)
2. **Risk score unexpected**: Verify name matches in mock data files
3. **Confidence scores confusing**: See CONFIDENCE_SCORES_EXPLAINED.md
4. **Backend errors**: Check logs in `logs/` directory

### For Issues or Questions:
- Review relevant documentation files
- Check backend logs for detailed error messages
- Verify mock data files are present and properly formatted
- Ensure all dependencies are installed

---

**Last Updated:** March 23, 2026
**Version:** 2.0 (Complete)
**Author:** KYC/AML Multi-Agent System
