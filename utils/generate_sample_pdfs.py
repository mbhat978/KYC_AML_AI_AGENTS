"""
Generate sample PDF documents for testing KYC system
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

def main():
    """Generate sample PDFs"""
    # Ensure samples directory exists
    os.makedirs('samples/pdf', exist_ok=True)
    
    # Sample PAN cards
    pan_cards = [
        {
            'name': 'RAJESH KUMAR SHARMA',
            'father_name': 'VIJAY KUMAR SHARMA',
            'dob': '15/03/1985',
            'pan_number': 'ABCDE1234F'
        },
        {
            'name': 'PRIYA SINGH',
            'father_name': 'RAVI SINGH',
            'dob': '22/07/1992',
            'pan_number': 'FGHIJ5678K'
        },
        {
            'name': 'AMIT PATEL',
            'father_name': 'MAHESH PATEL',
            'dob': '10/11/1988',
            'pan_number': 'KLMNO9012P'
        }
    ]
    
    # Sample passports
    passports = [
        {
            'country': 'INDIA',
            'type': 'P',
            'passport_number': 'M1234567',
            'surname': 'SHARMA',
            'given_names': 'RAJESH KUMAR',
            'nationality': 'INDIAN',
            'dob': '15/03/1985',
            'sex': 'M',
            'place_of_birth': 'DELHI, INDIA',
            'issue_date': '10/06/2019',
            'expiry_date': '09/06/2029',
            'mrz_line1': 'P<INDSHARMA<<RAJESH<KUMAR<<<<<<<<<<<<<<<<',
            'mrz_line2': 'M1234567<0IND8503155M2906099<<<<<<<<<<<<06'
        },
        {
            'country': 'INDIA',
            'type': 'P',
            'passport_number': 'N7654321',
            'surname': 'SINGH',
            'given_names': 'PRIYA',
            'nationality': 'INDIAN',
            'dob': '22/07/1992',
            'sex': 'F',
            'place_of_birth': 'MUMBAI, INDIA',
            'issue_date': '15/03/2020',
            'expiry_date': '14/03/2030',
            'mrz_line1': 'P<INDSINGH<<PRIYA<<<<<<<<<<<<<<<<<<<<<<<',
            'mrz_line2': 'N7654321<8IND9207222F3003149<<<<<<<<<<<<04'
        },
        {
            'country': 'INDIA',
            'type': 'P',
            'passport_number': 'K9876543',
            'surname': 'PATEL',
            'given_names': 'AMIT',
            'nationality': 'INDIAN',
            'dob': '10/11/1988',
            'sex': 'M',
            'place_of_birth': 'AHMEDABAD, INDIA',
            'issue_date': '20/01/2021',
            'expiry_date': '19/01/2031',
            'mrz_line1': 'P<INDPATEL<<AMIT<<<<<<<<<<<<<<<<<<<<<<<<',
            'mrz_line2': 'K9876543<2IND8811100M3101199<<<<<<<<<<<<08'
        }
    ]
    
    # Generate PAN card PDFs
    for i, data in enumerate(pan_cards, 1):
        filename = f'samples/pdf/pan_card_sample_{i}.pdf'
        create_pan_card_pdf(filename, data)
    
    # Generate passport PDFs
    for i, data in enumerate(passports, 1):
        filename = f'samples/pdf/passport_sample_{i}.pdf'
        create_passport_pdf(filename, data)
    
    print("\n✓ Sample PDF generation complete!")
    print(f"✓ Created {len(pan_cards)} PAN card PDFs")
    print(f"✓ Created {len(passports)} passport PDFs")
    print("✓ Files saved in: samples/pdf/")

if __name__ == "__main__":
    main()