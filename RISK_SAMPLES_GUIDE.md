# Risk-Based Sample Documents Guide

## Overview
This guide documents the risk-based sample documents created for testing the KYC/AML system. Each document is designed to trigger specific risk scores based on sanctions lists, PEP matches, and other risk factors.

## Sample Documents by Risk Level

### 🟡 MEDIUM RISK (6.0 / 0.60)
**Trigger Factors:** PEP matches, minor inconsistencies

| File Name | Document Type | Name | Risk Factors |
|-----------|---------------|------|--------------|
| `pan_card_risk60_1` | PAN Card | Robert Williams | PEP match (Former Minister of Finance, UK) |
| `passport_risk60_1` | Passport | Robert Williams | PEP match, Former government official |
| `pan_card_risk60_2` | PAN Card | Elena Rodriguez | PEP match (Active Senator, Mexico) |

**Expected Behavior:**
- Risk Score: ~0.60 (60%)
- Risk Category: MEDIUM
- Decision: APPROVE or ESCALATE (depending on additional factors)
- Flags: PEP status detected

---

### 🟠 MEDIUM-HIGH RISK (7.0 / 0.70)
**Trigger Factors:** Sanctions list matches (HIGH severity), financial crimes

| File Name | Document Type | Name | Risk Factors |
|-----------|---------------|------|--------------|
| `pan_card_risk70_1` | PAN Card | Maria Santos | Sanctions match (Money laundering, Venezuela) |
| `passport_risk70_1` | Passport | Maria Santos | Sanctions list, Financial crimes |
| `pan_card_risk70_2` | PAN Card | Victor Petrov | Sanctions match (Financial crimes, Russia) |

**Expected Behavior:**
- Risk Score: ~0.70 (70%)
- Risk Category: HIGH
- Decision: ESCALATE or REJECT
- Flags: Sanctions list match, Financial crimes history

---

### 🔴 HIGH/CRITICAL RISK (8.5 / 0.85)
**Trigger Factors:** Critical sanctions matches (terrorism financing), severe red flags

| File Name | Document Type | Name | Risk Factors |
|-----------|---------------|------|--------------|
| `pan_card_risk85_1` | PAN Card | Ahmed Hassan | CRITICAL sanctions match (Terrorism financing, Syria) |
| `passport_risk85_1` | Passport | Ahmed Hassan | Terrorism financing, High-risk country |
| `pan_card_risk85_2` | PAN Card | Ahmed H | Alias of sanctioned individual |

**Expected Behavior:**
- Risk Score: ~0.85 (85%)
- Risk Category: CRITICAL
- Decision: REJECT
- Flags: Terrorism financing, Critical sanctions match, High-risk jurisdiction

---

## File Formats

Each sample is available in two formats:

### PDF Files (`samples/pdf/`)
- Full document layout with headers, fields, and formatting
- Can be uploaded directly to the KYC system
- Text extraction via PyMuPDF
- Realistic document appearance

### JPG Files (`samples/jpg/`)
- Converted from PDF at 150 DPI
- Can be uploaded as image documents
- Requires OCR for text extraction (future enhancement)
- Suitable for vision-based processing

---

## Risk Calculation Methodology

The KYC system calculates risk scores based on multiple factors:

### 1. Sanctions List Matches (Weight: 40%)
- **CRITICAL severity** (terrorism, etc.): +0.60 to risk
- **HIGH severity** (financial crimes): +0.40 to risk
- **MEDIUM severity**: +0.20 to risk

### 2. PEP Status (Weight: 25%)
- **Active PEP - HIGH risk**: +0.30 to risk
- **Active PEP - MEDIUM risk**: +0.20 to risk
- **Former PEP**: +0.15 to risk

### 3. Document Inconsistencies (Weight: 20%)
- Name mismatches: +0.15 to risk
- Date discrepancies: +0.10 to risk
- Missing fields: +0.05 to risk

### 4. Jurisdiction Risk (Weight: 15%)
- High-risk countries: +0.20 to risk
- Medium-risk countries: +0.10 to risk

---

## Testing Instructions

### 1. Upload a Sample Document
```bash
# Start backend (if not running)
python backend/app/main.py

# Access frontend
# Navigate to http://localhost:5173
# Upload one of the risk-based samples
```

### 2. Expected Results

#### For MEDIUM Risk (6.0)
```json
{
  "risk_score": 0.60,
  "risk_category": "MEDIUM",
  "decision": "APPROVE" or "ESCALATE",
  "flags": ["PEP_DETECTED"]
}
```

#### For MEDIUM-HIGH Risk (7.0)
```json
{
  "risk_score": 0.70,
  "risk_category": "HIGH",
  "decision": "ESCALATE",
  "flags": ["SANCTIONS_MATCH", "FINANCIAL_CRIMES"]
}
```

#### For HIGH Risk (8.5)
```json
{
  "risk_score": 0.85,
  "risk_category": "CRITICAL",
  "decision": "REJECT",
  "flags": ["CRITICAL_SANCTIONS", "TERRORISM_FINANCING"]
}
```

---

## Mock Data Sources

### Sanctions List (`mock_data/sanctions_list.json`)
- Victor Petrov (RU) - Financial crimes
- Maria Santos (VE) - Money laundering
- Ahmed Hassan (SY) - Terrorism financing (CRITICAL)

### PEP List (`mock_data/pep_list.json`)
- Robert Williams (UK) - Former Minister of Finance
- Elena Rodriguez (MX) - Active Senator
- Dr. Rajesh Mehta (IN) - Bank Director
- Liu Wei (CN) - Provincial Governor

---

## Regenerating Samples

To regenerate all risk-based samples:

```bash
python utils/generate_risk_sample_pdfs.py
```

This will create:
- 3 MEDIUM risk documents (6.0/0.60)
- 3 MEDIUM-HIGH risk documents (7.0/0.70)
- 3 HIGH/CRITICAL risk documents (8.5/0.85)
- Total: 8 documents × 2 formats = 16 files

---

## Customization

### Adding New Risk Profiles

Edit `utils/generate_risk_sample_pdfs.py` and add to the appropriate risk level list:

```python
custom_risk_docs = [
    {
        'type': 'pan' or 'passport',
        'name': 'FULL NAME',
        'father_name': 'FATHER NAME',
        'dob': 'DD/MM/YYYY',
        'pan_number': 'XXXXX0000X',
        'filename': 'custom_risk_sample_1'
    }
]
```

### Modifying Risk Scores

To achieve different risk scores, use names that match entries in:
- `mock_data/sanctions_list.json` - Higher risk
- `mock_data/pep_list.json` - Medium risk
- Clean names - Lower risk

---

## Integration with KYC Pipeline

These samples integrate with the full KYC pipeline:

1. **Upload** → `/api/kyc/upload` endpoint
2. **Text Extraction** → PyMuPDF extracts document text
3. **Field Parsing** → Identifies name, DOB, document number
4. **Verification** → Checks against sanctions/PEP lists
5. **Risk Assessment** → Calculates composite risk score
6. **Decision** → APPROVE / ESCALATE / REJECT

---

## Known Limitations

1. **Simplified Text Extraction**: Uses regex patterns, not AI vision
2. **Mock Lists**: Using sample sanctions/PEP data, not real databases
3. **Single Page**: Only processes first page of PDFs
4. **No OCR**: JPG files require OCR implementation
5. **Deterministic**: Risk scores are predictable based on name matches

---

## Future Enhancements

- [ ] AI Vision-based extraction (Claude Vision, GPT-4 Vision)
- [ ] Real sanctions list integration (OFAC, UN, EU)
- [ ] Real PEP database integration (World-Check, Dow Jones)
- [ ] Multi-page document processing
- [ ] OCR for scanned documents (pytesseract)
- [ ] Document authenticity verification
- [ ] Biometric analysis
- [ ] Behavioral risk modeling

---

## Support

For issues or questions:
- Check `PDF_UPLOAD_GUIDE.md` for upload troubleshooting
- Review `TESTING_GUIDE.md` for system testing
- Check backend logs in `logs/` directory

---

**Last Updated:** March 21, 2026
**Version:** 1.0
**Author:** KYC/AML Multi-Agent System