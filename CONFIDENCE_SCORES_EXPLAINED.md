# Confidence Scores Explained

## Overview
The KYC system uses **TWO different confidence scores** that measure completely different things. Users often see both and wonder why they're different.

---

## 1. Extraction Confidence (0.85 / 85%)

### What It Measures
- **How accurately the system extracted text from the PDF/document**
- Quality of OCR (Optical Character Recognition)
- Confidence that name, ID number, date of birth were read correctly

### Where It Comes From
- **Source**: `agents/extraction_agent.py` (line 74)
- **Default Value**: 0.85 (85%)
- **Can vary**: 0.70-0.95 depending on document quality

### Code Reference
```python
# agents/extraction_agent.py, line 74
"confidence": document.get('metadata', {}).get('confidence_score', 0.85)
```

### What It Means
- **0.85 (85%)**: "We're 85% confident we correctly read all text from the document"
- **High (>0.90)**: Clear, high-quality PDF with perfect text extraction
- **Medium (0.70-0.85)**: Standard quality, minor ambiguities
- **Low (<0.70)**: Poor scan quality, potential OCR errors

### Example
```json
{
  "agent": "ExtractionAgent",
  "extracted_data": {
    "name": "Robert Williams",
    "id_number": "TEST001",
    "date_of_birth": "1955-07-20"
  },
  "confidence": 0.85  ← EXTRACTION CONFIDENCE
}
```

**This means**: "We're 85% sure we read 'Robert Williams' correctly from the PDF"

---

## 2. Reasoning Confidence (0.60 / 60%)

### What It Measures
- **How confident the system is in its risk assessment decision**
- Certainty about the recommendation (APPROVE/ESCALATE/REJECT)
- Based on PEP/sanctions matches and verification results

### Where It Comes From
- **Source**: `agents/reasoning_agent.py`
- **Varies by scenario**: 0.10 (sanctions) to 0.90 (verified clean)
- **For PEP MEDIUM matches**: 0.60 (60%)

### Code Reference
```python
# agents/reasoning_agent.py, lines 47-53
elif matches.get('pep', {}).get('status') == 'flagged':
    pep_risk_level = matches.get('pep', {}).get('risk_level', 'MEDIUM')
    if pep_risk_level == 'HIGH':
        confidence = 0.5   # 50% for active high-risk PEP
    else:
        confidence = 0.6   # 60% for former/medium PEP
```

### What It Means
- **0.60 (60%)**: "We're moderately confident this assessment is correct"
- **High (>0.80)**: Clear decision (clean record or definitive match)
- **Medium (0.50-0.80)**: Needs review (PEP match, name variations)
- **Low (<0.50)**: High uncertainty, requires manual review

### Example Scenarios

| Scenario | Reasoning Confidence | Why? |
|----------|---------------------|------|
| Clean verified record | 0.90 | Very confident - no issues found |
| PEP MEDIUM match | 0.60 | Moderate confidence - needs review |
| PEP HIGH match | 0.50 | Lower confidence - active high-risk |
| Sanctions match | 0.10 | Very low - automatic reject |
| Name mismatch | 0.30-0.75 | Varies by similarity score |

### Example
```json
{
  "agent": "ReasoningAgent",
  "reasoning_conclusion": "ESCALATE",
  "confidence": 0.60,  ← REASONING CONFIDENCE
  "risk_factors": ["MEDIUM RISK: PEP match detected"]
}
```

**This means**: "We found a PEP match (former official). We're 60% confident this requires manual review, not automatic approval."

---

## Why Two Different Scores?

### They Measure Different Stages

```
Document Upload
     ↓
┌─────────────────────────────────┐
│ EXTRACTION STAGE                │
│ Confidence: 0.85 (85%)          │ ← "Can we read the text?"
│ "Text extraction quality"       │
└─────────────────────────────────┘
     ↓
┌─────────────────────────────────┐
│ REASONING STAGE                 │
│ Confidence: 0.60 (60%)          │ ← "What should we do?"
│ "Risk assessment certainty"     │
└─────────────────────────────────┘
     ↓
Final Decision
```

### Real-World Analogy

Think of it like a medical test:

1. **Extraction Confidence (0.85)**: 
   - "How clear is the X-ray image?"
   - Can we see all the details clearly?

2. **Reasoning Confidence (0.60)**:
   - "How certain are we about the diagnosis?"
   - Based on what we see, what's our assessment?

You can have a perfectly clear X-ray (high extraction confidence) but still be uncertain about the diagnosis (lower reasoning confidence).

---

## Common Scenarios

### Scenario 1: High Extraction, Low Reasoning
```
Extraction Confidence: 0.90 (90%)
Reasoning Confidence: 0.10 (10%)
```
**Meaning**: "We clearly read 'Ahmed Hassan' from the PDF (90% sure about text), but we found a CRITICAL sanctions match for terrorism financing (very uncertain about approval - 10%)."

### Scenario 2: Medium Extraction, Medium Reasoning
```
Extraction Confidence: 0.85 (85%)
Reasoning Confidence: 0.60 (60%)
```
**Meaning**: "We read 'Robert Williams' with good confidence (85%), and we found a PEP match that requires review (60% confident in escalation decision)."

### Scenario 3: High Both
```
Extraction Confidence: 0.95 (95%)
Reasoning Confidence: 0.90 (90%)
```
**Meaning**: "Perfect text extraction, clean verified record with no issues. Very confident in auto-approval."

---

## Which Confidence Matters More?

### For Users/Compliance Officers
- **Reasoning Confidence is MORE IMPORTANT**
- It tells you how certain the AI is about the risk decision
- Low reasoning confidence (<0.50) → Manual review needed

### For Developers/System Admins
- **Both matter equally**
- Extraction confidence indicates data quality issues
- Reasoning confidence indicates decision uncertainty
- Both should be logged for auditing

---

## In The UI

### What Users See

```
┌─────────────────────────────────────────┐
│ Risk Assessment                         │
│                                         │
│ Risk Score: 6.0/10                      │
│ Risk Category: MEDIUM                   │
│ Confidence: 60% ← REASONING CONFIDENCE  │
│                                         │
│ ─────────────────────────────────────── │
│                                         │
│ Extraction Information                  │
│ Name: Robert Williams                   │
│ ID: TEST001                             │
│ Extraction Quality: 85% ← EXTRACTION    │
│                                         │
└─────────────────────────────────────────┘
```

### Recommended Labeling
To avoid confusion, consider labeling them explicitly:
- **"Decision Confidence: 60%"** instead of just "Confidence"
- **"Extraction Quality: 85%"** or "OCR Confidence: 85%"

---

## API Response Structure

### Full Response Example
```json
{
  "decision": "ESCALATE",
  "risk_score": 6.0,
  "risk_category": "MEDIUM",
  "confidence": 0.60,  ← Reasoning confidence (decision certainty)
  "explanation": "PEP match detected - manual review required",
  
  "extraction_result": {
    "extracted_data": {
      "name": "Robert Williams",
      "id_number": "TEST001"
    },
    "confidence": 0.85  ← Extraction confidence (text quality)
  },
  
  "reasoning_result": {
    "confidence": 0.60  ← Same as top-level confidence
  }
}
```

---

## FAQ

### Q: Why is extraction confidence always 0.85?
**A**: It's a default value for standard-quality PDFs. In production, this would vary based on actual OCR quality metrics.

### Q: Can reasoning confidence be higher than extraction confidence?
**A**: Yes! You can have poor text quality (0.70 extraction) but still be very confident about the decision (0.90 reasoning) if, for example, the ID clearly matches a sanctions list.

### Q: What happens if extraction confidence is very low (<0.60)?
**A**: The system should flag the document for manual data entry or request a higher-quality scan.

### Q: For risk60 samples, why is reasoning confidence 0.60 and not 0.40?
**A**: This was recently fixed. PEP MEDIUM matches now correctly use 0.60 confidence to indicate "moderate certainty - needs review" rather than the old 0.40 which was too pessimistic.

---

## Summary

| Confidence Type | Measures | Source | Typical Values |
|----------------|----------|--------|----------------|
| **Extraction** | Text extraction quality | ExtractionAgent | 0.70-0.95 |
| **Reasoning** | Decision certainty | ReasoningAgent | 0.10-0.90 |

**Key Takeaway**: These are independent metrics. High extraction confidence means we read the document well. High reasoning confidence means we're sure about the risk decision.

---

**Last Updated:** March 21, 2026  
**Related Files:**
- `agents/extraction_agent.py` - Extraction confidence
- `agents/reasoning_agent.py` - Reasoning confidence
- `RISK_SCORING_FIX.md` - Recent fixes to scoring system