# PDF Upload Feature Guide

## Overview
The KYC/AML system now supports uploading PDF, JPG, and PNG documents directly. The system automatically extracts text and processes the documents through the multi-agent pipeline.

## How It Works

### 1. Frontend Upload
- User uploads PDF/image file through the UploadZone component
- File is sent to `/api/kyc/upload` endpoint via FormData

### 2. Backend Processing
- **File Validation**: Checks if file type is supported (PDF, JPG, PNG)
- **Text Extraction**: Extracts text from PDF using PyMuPDF (fitz)
- **Field Parsing**: Identifies document type and extracts key fields:
  - Name
  - PAN number (XXXXX0000X format)
  - Date of birth
  - Document type (PAN, PASSPORT, DRIVERS_LICENSE)
- **Document Storage**: Stores processed document for session
- **Returns**: Session ID and stream URL for real-time processing

### 3. Real-Time Processing
- Same SSE streaming as JSON uploads
- Multi-agent processing pipeline
- Live feed of agent activities
- Final decision with risk assessment

## API Endpoints

### Upload File
```
POST /api/kyc/upload
Content-Type: multipart/form-data

Parameters:
- file: File (PDF, JPG, PNG)
- document_type: Optional[str] - Override detected document type

Response:
{
  "session_id": "uuid",
  "status": "processing",
  "message": "Document uploaded successfully",
  "stream_url": "/api/kyc/stream/{session_id}"
}
```

### Process JSON Document
```
POST /api/kyc/process
Content-Type: application/json

Body:
{
  "document_type": "PAN",
  "extracted_fields": {...},
  "metadata": {...}
}
```

## Sample PDFs

Sample PDF documents are available in `samples/pdf/`:
- `pan_card_sample_1.pdf` - Rajesh Kumar Sharma (ABCDE1234F)
- `pan_card_sample_2.pdf` - Priya Singh (FGHIJ5678K)
- `pan_card_sample_3.pdf` - Amit Patel (KLMNO9012P)
- `passport_sample_1.pdf` - Rajesh Kumar Sharma (M1234567)
- `passport_sample_2.pdf` - Priya Singh (N7654321)
- `passport_sample_3.pdf` - Amit Patel (K9876543)

## Text Extraction

### PDF Processing
Uses PyMuPDF (fitz) to extract text from PDF pages:
```python
import fitz
doc = fitz.open(stream=pdf_bytes, filetype="pdf")
text = doc[0].get_text()  # Extract text from first page
```

### Field Parsing
Simple regex-based parsing (can be enhanced with LLM vision):
- **PAN Number**: `[A-Z]{5}[0-9]{4}[A-Z]` pattern
- **Date**: `DD/MM/YYYY` or `DD-MM-YYYY` format
- **Name**: Lines following "Name:" pattern
- **Document Type**: Keywords (PAN, PASSPORT, DRIVER)

## Future Enhancements

1. **OCR for Images**: Add pytesseract for image text extraction
2. **LLM Vision**: Use Claude Vision or GPT-4 Vision for better extraction
3. **Multi-page PDFs**: Process all pages, not just first page
4. **Field Validation**: Enhanced validation using AI models
5. **Document Quality Check**: Assess image quality and readability

## Error Handling

- **422 Unprocessable Entity**: Invalid file format or missing data
- **400 Bad Request**: Unsupported file type
- **500 Internal Server Error**: Processing failure

## Testing

To test PDF upload:
1. Start backend: `python backend/app/main.py`
2. Start frontend: `cd frontend && npm run dev`
3. Upload one of the sample PDFs from `samples/pdf/`
4. Watch real-time processing in the Live Feed
5. View final decision and risk assessment

## Dependencies

- **Backend**: PyMuPDF (fitz) for PDF processing
- **Frontend**: Native File API and FormData
- **Optional**: pytesseract for OCR (future enhancement)

## Notes

- Currently only processes first page of PDFs
- Text extraction quality depends on PDF format (scanned vs. digital)
- For production, consider using LLM vision models for better accuracy
- Supported file types: PDF, JPG, JPEG, PNG
- Maximum file size: Limited by FastAPI settings (default: 2MB)