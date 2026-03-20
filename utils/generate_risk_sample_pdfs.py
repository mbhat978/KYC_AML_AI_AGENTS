"""
Generate sample PDF and JPG documents with specific risk profiles
Creates documents that will trigger different risk scores in the KYC system
"""
from reportlab.lib.pagesizes import letter, A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
import os

def create_pan_card_pdf(filename, data):
    """Create a sample PAN card PDF"""
    c = canvas.Canvas(filename, pagesize=(3.5*inch, 2.25*inch))
    
    # Background
    c.setFillColor(HexColor('#E8F4F8'))
    c.rect(0, 0, 3.5*inch, 2.25*inch, fill=1, stroke=0)
    
    # Header
    c.setFillColor(HexColor('#003366'))
    c.rect(0, 1.85*inch, 3.5*inch, 0.4*inch, fill=1, stroke=0)
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 10)
    c.drawString(0.3*inch, 2.0*inch, "INCOME TAX DEPARTMENT")
    c.setFont("Helvetica", 7)
    c.drawString(0.3*inch, 1.9*inch, "GOVT. OF INDIA")
    
    # Photo placeholder
    c.setFillColor(HexColor('#CCCCCC'))
    c.rect(0.2*inch, 0.8*inch, 0.8*inch, 1.0*inch, fill=1, stroke=1)
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 6)
    c.drawString(0.35*inch, 1.25*inch, "PHOTO")
    
    # Details
    c.setFillColor(HexColor('#000000'))
    c.setFont("Helvetica-Bold", 8)
    c.drawString(1.2*inch, 1.65*inch, "Name")
    c.setFont("Helvetica", 8)
    c.drawString(1.2*inch, 1.5*inch, data.get('name', 'SAMPLE NAME'))
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(1.2*inch, 1.3*inch, "Father's Name")
    c.setFont("Helvetica", 8)
    c.drawString(1.2*inch, 1.15*inch, data.get('father_name', 'FATHER NAME'))
    
    c.setFont("Helvetica-Bold", 8)
    c.drawString(1.2*inch, 0.95*inch, "Date of Birth")
    c.setFont("Helvetica", 8)
    c.drawString(1.2*inch, 0.8*inch, data.get('dob', '01/01/1990'))
    
    # PAN Number (prominent)
    c.setFillColor(HexColor('#003366'))
    c.setFont("Helvetica-Bold", 12)
    c.drawString(0.2*inch, 0.45*inch, "Permanent Account Number")
    c.setFont("Helvetica-Bold", 14)
    c.drawString(0.4*inch, 0.2*inch, data.get('pan_number', 'XXXXX0000X'))
    
    # Signature
    c.setFont("Helvetica", 6)
    c.drawString(2.5*inch, 0.3*inch, "Signature")
    c.line(2.5*inch, 0.25*inch, 3.2*inch, 0.25*inch)
    
    c.save()
    print(f"Created: {filename}")

def create_passport_pdf(filename, data):
    """Create a sample passport PDF"""
    c = canvas.Canvas(filename, pagesize=(3.5*inch, 5*inch))
    
    # Cover page style
    c.setFillColor(HexColor('#1A237E'))
    c.rect(0, 4*inch, 3.5*inch, 1*inch, fill=1, stroke=0)
    
    c.setFillColor(HexColor('#FFFFFF'))
    c.setFont("Helvetica-Bold", 14)
    c.drawCentredString(1.75*inch, 4.6*inch, "PASSPORT")
    c.setFont("Helvetica", 10)
    c.drawCentredString(1.75*inch, 4.35*inch, data.get('country', 'INDIA'))
    
    # Photo placeholder
    c.setFillColor(HexColor('#CCCCCC'))
    c.rect(0.3*inch, 2.5*inch, 1.2*inch, 1.4*inch, fill=1, stroke=1)
    c.setFillColor(HexColor('#666666'))
    c.setFont("Helvetica", 8)
    c.drawString(0.6*inch, 3.15*inch, "PHOTO")
    
    # Personal details
    c.setFillColor(HexColor('#000000'))
    y_pos = 3.7*inch
    
    details = [
        ("Type", data.get('type', 'P')),
        ("Passport No.", data.get('passport_number', 'X0000000')),
        ("Surname", data.get('surname', 'SURNAME')),
        ("Given Names", data.get('given_names', 'GIVEN NAMES')),
        ("Nationality", data.get('nationality', 'INDIAN')),
        ("Date of Birth", data.get('dob', '01/01/1990')),
        ("Sex", data.get('sex', 'M')),
        ("Place of Birth", data.get('place_of_birth', 'CITY, INDIA')),
        ("Date of Issue", data.get('issue_date', '01/01/2020')),
        ("Date of Expiry", data.get('expiry_date', '01/01/2030'))
    ]
    
    for label, value in details:
        c.setFont("Helvetica-Bold", 7)
        c.drawString(1.7*inch, y_pos, f"{label}:")
        c.setFont("Helvetica", 7)
        c.drawString(1.7*inch, y_pos - 0.15*inch, value)
        y_pos -= 0.35*inch
    
    # MRZ (Machine Readable Zone)
    c.setFillColor(HexColor('#F5F5F5'))
    c.rect(0, 0.1*inch, 3.5*inch, 0.6*inch, fill=1, stroke=0)
    c.setFillColor(HexColor('#000000'))
    c.setFont("Courier", 7)
    mrz1 = data.get('mrz_line1', 'P<INDSURNAME<<GIVENNAMES<<<<<<<<<<<<<<<')
    mrz2 = data.get('mrz_line2', 'X00000000IND9001010M3001010<<<<<<<<<<<<00')
    c.drawString(0.1*inch, 0.5*inch, mrz1[:44])
    c.drawString(0.1*inch, 0.3*inch, mrz2[:44])
    
    c.save()
    print(f"Created: {filename}")

def pdf_to_jpg(pdf_path, jpg_path, dpi=150):
    """Convert PDF to JPG using PyMuPDF"""
    try:
        import fitz  # PyMuPDF
        
        # Open PDF
        doc = fitz.open(pdf_path)
        page = doc[0]
        
        # Render to pixmap
        zoom = dpi / 72.0
        mat = fitz.Matrix(zoom, zoom)
        pix = page.get_pixmap(matrix=mat)
        
        # Save as JPG
        pix.save(jpg_path)
        doc.close()
        
        print(f"Converted to JPG: {jpg_path}")
    except Exception as e:
        print(f"Error converting to JPG: {e}")

def main():
    """Generate sample PDFs with specific risk profiles"""
    # Ensure directories exist
    os.makedirs('samples/pdf', exist_ok=True)
    os.makedirs('samples/jpg', exist_ok=True)
    
    # RISK LEVEL 6.0 (0.60) - MEDIUM RISK
    # Characteristics: Similar to PEP names, minor inconsistencies
    medium_risk_docs = [
        {
            'type': 'pan',
            'name': 'ROBERT WILLIAMS',  # PEP list name (Former Minister)
            'father_name': 'JOHN WILLIAMS',
            'dob': '20/07/1955',
            'pan_number': 'BROBE6845M',
            'filename': 'pan_card_risk60_1'
        },
        {
            'type': 'passport',
            'country': 'UNITED KINGDOM',
            'passport_number': 'GB8765432',
            'surname': 'WILLIAMS',
            'given_names': 'ROBERT',
            'nationality': 'BRITISH',
            'dob': '20/07/1955',
            'sex': 'M',
            'place_of_birth': 'LONDON, UK',
            'issue_date': '10/01/2019',
            'expiry_date': '09/01/2029',
            'mrz_line1': 'P<GBRWILLIAMS<<ROBERT<<<<<<<<<<<<<<<<<<<',
            'mrz_line2': 'GB8765432<2GBR5507200M2901099<<<<<<<<<<<<04',
            'filename': 'passport_risk60_1'
        },
        {
            'type': 'pan',
            'name': 'ELENA RODRIGUEZ',  # PEP - Senator
            'father_name': 'CARLOS RODRIGUEZ',
            'dob': '14/03/1968',
            'pan_number': 'CELEN6234K',
            'filename': 'pan_card_risk60_2'
        }
    ]
    
    # RISK LEVEL 7.0 (0.70) - MEDIUM-HIGH RISK
    # Characteristics: Sanctions list match (not critical) + concerns
    medium_high_risk_docs = [
        {
            'type': 'pan',
            'name': 'MARIA SANTOS',  # Sanctions list - Money laundering
            'father_name': 'JUAN SANTOS',
            'dob': '23/09/1978',
            'pan_number': 'DMARI7432K',
            'filename': 'pan_card_risk70_1'
        },
        {
            'type': 'passport',
            'country': 'VENEZUELA',
            'passport_number': 'V1234567',
            'surname': 'SANTOS',
            'given_names': 'MARIA',
            'nationality': 'VENEZUELAN',
            'dob': '23/09/1978',
            'sex': 'F',
            'place_of_birth': 'CARACAS, VENEZUELA',
            'issue_date': '15/06/2018',
            'expiry_date': '14/06/2028',
            'mrz_line1': 'P<VENSANTOS<<MARIA<<<<<<<<<<<<<<<<<<<<<<<',
            'mrz_line2': 'V1234567<8VEN7809233F2806149<<<<<<<<<<<<06',
            'filename': 'passport_risk70_1'
        },
        {
            'type': 'pan',
            'name': 'VICTOR PETROV',  # Sanctions list - Financial crimes
            'father_name': 'DMITRI PETROV',
            'dob': '12/04/1965',
            'pan_number': 'EVICT7845P',
            'filename': 'pan_card_risk70_2'
        }
    ]
    
    # RISK LEVEL 8.5 (0.85) - HIGH/CRITICAL RISK
    # Characteristics: Critical sanctions match (terrorism, etc.)
    high_risk_docs = [
        {
            'type': 'pan',
            'name': 'AHMED HASSAN',  # Sanctions - Terrorism financing (CRITICAL)
            'father_name': 'MAHMOUD HASSAN',
            'dob': '30/01/1970',
            'pan_number': 'FAHMD8576K',
            'filename': 'pan_card_risk85_1'
        },
        {
            'type': 'passport',
            'country': 'SYRIA',
            'passport_number': 'S9876543',
            'surname': 'HASSAN',
            'given_names': 'AHMED',
            'nationality': 'SYRIAN',
            'dob': '30/01/1970',
            'sex': 'M',
            'place_of_birth': 'DAMASCUS, SYRIA',
            'issue_date': '01/01/2017',
            'expiry_date': '31/12/2026',
            'mrz_line1': 'P<SYRHASSAN<<AHMED<<<<<<<<<<<<<<<<<<<<<<<',
            'mrz_line2': 'S9876543<2SYR7001300M2612319<<<<<<<<<<<<08',
            'filename': 'passport_risk85_1'
        },
        {
            'type': 'pan',
            'name': 'AHMED H',  # Alias of sanctioned person
            'father_name': 'HASSAN ALI',
            'dob': '30/01/1970',
            'pan_number': 'GAHMD8512K',
            'filename': 'pan_card_risk85_2'
        }
    ]
    
    # Process all documents
    all_docs = medium_risk_docs + medium_high_risk_docs + high_risk_docs
    
    pdf_count = 0
    jpg_count = 0
    
    for doc in all_docs:
        doc_type = doc.pop('type')
        filename = doc.pop('filename')
        
        # Create PDF
        pdf_path = f'samples/pdf/{filename}.pdf'
        if doc_type == 'pan':
            create_pan_card_pdf(pdf_path, doc)
        else:
            create_passport_pdf(pdf_path, doc)
        pdf_count += 1
        
        # Convert to JPG
        jpg_path = f'samples/jpg/{filename}.jpg'
        pdf_to_jpg(pdf_path, jpg_path)
        jpg_count += 1
    
    print(f"\n✓ Sample generation complete!")
    print(f"✓ Created {pdf_count} PDF files")
    print(f"✓ Created {jpg_count} JPG files")
    print(f"\n📊 Risk Level Distribution:")
    print(f"   • MEDIUM (6.0/0.60):      {len(medium_risk_docs)} documents")
    print(f"   • MEDIUM-HIGH (7.0/0.70): {len(medium_high_risk_docs)} documents")
    print(f"   • HIGH (8.5/0.85):        {len(high_risk_docs)} documents")
    print(f"\n📁 Files saved in:")
    print(f"   • samples/pdf/ (PDF format)")
    print(f"   • samples/jpg/ (JPG format)")

if __name__ == "__main__":
    main()
