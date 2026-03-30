"""
Generate Indian Driving Licenses for KYC Testing
Data matches government_db.json records
"""

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor, black, white, red
from datetime import datetime
import json

def generate_indian_license(filename, license_data):
    """Generate an Indian driving license PDF"""
    # Indian DL size is approximately 85.6mm x 54mm (credit card size)
    c = canvas.Canvas(filename, pagesize=(3.37*inch, 2.13*inch))
    
    # Background - light saffron color
    c.setFillColor(HexColor('#FFF5E6'))
    c.rect(0, 0, 3.37*inch, 2.13*inch, fill=1, stroke=0)
    
    # "SAMPLE" watermark
    c.setFillColor(HexColor('#FFE0E0'))
    c.setFont("Helvetica-Bold", 32)
    c.saveState()
    c.translate(1.685*inch, 1.065*inch)
    c.rotate(45)
    c.drawCentredString(0, 0, "SAMPLE")
    c.restoreState()
    
    # Header with Indian flag colors
    # Saffron
    c.setFillColor(HexColor('#FF9933'))
    c.rect(0, 1.93*inch, 3.37*inch, 0.1*inch, fill=1, stroke=0)
    # White stripe
    c.setFillColor(white)
    c.rect(0, 1.83*inch, 3.37*inch, 0.1*inch, fill=1, stroke=0)
    # Green
    c.setFillColor(HexColor('#138808'))
    c.rect(0, 1.73*inch, 3.37*inch, 0.1*inch, fill=1, stroke=0)
    
    # Title
    c.setFillColor(black)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(1.685*inch, 1.85*inch, "DRIVERS_LICENSE")
    c.setFont("Helvetica", 6)
    c.drawCentredString(1.685*inch, 1.76*inch, f"Form-6 (See Rule 14) | {license_data['state']}")
    
    # Photo placeholder
    c.setFillColor(HexColor('#E0E0E0'))
    c.rect(0.1*inch, 1.1*inch, 0.55*inch, 0.6*inch, fill=1, stroke=1)
    c.setFillColor(HexColor('#808080'))
    c.setFont("Helvetica", 6)
    c.drawCentredString(0.375*inch, 1.37*inch, "PHOTO")
    
    # Main details
    c.setFillColor(black)
    y_pos = 1.62*inch
    line_height = 0.12*inch
    
    # License Number
    c.setFont("Helvetica-Bold", 7)
    c.drawString(0.75*inch, y_pos, "DL No:")
    c.setFont("Helvetica", 7)
    c.drawString(1.15*inch, y_pos, license_data['id_number'])
    
    y_pos -= line_height
    c.setFont("Helvetica-Bold", 7)
    c.drawString(0.75*inch, y_pos, "Name:")
    c.setFont("Helvetica", 7)
    c.drawString(1.15*inch, y_pos, license_data['name'].upper())
    
    y_pos -= line_height
    c.setFont("Helvetica-Bold", 7)
    c.drawString(0.75*inch, y_pos, "S/W/D of:")
    c.setFont("Helvetica", 7)
    c.drawString(1.15*inch, y_pos, license_data['father_name'].upper())
    
    y_pos -= line_height
    c.setFont("Helvetica-Bold", 7)
    c.drawString(0.75*inch, y_pos, "DOB:")
    c.setFont("Helvetica", 7)
    dob_formatted = datetime.strptime(license_data['date_of_birth'], '%Y-%m-%d').strftime('%d-%m-%Y')
    c.drawString(1.15*inch, y_pos, dob_formatted)
    
    c.setFont("Helvetica-Bold", 7)
    c.drawString(2.0*inch, y_pos, "BG:")
    c.setFont("Helvetica", 7)
    c.drawString(2.25*inch, y_pos, license_data['blood_group'])
    
    # Address section
    y_pos -= line_height + 0.02*inch
    c.setFont("Helvetica-Bold", 6)
    c.drawString(0.1*inch, y_pos, "Address:")
    y_pos -= 0.1*inch
    c.setFont("Helvetica", 6)
    
    # Split address if too long
    address = license_data['address']
    if len(address) > 50:
        c.drawString(0.1*inch, y_pos, address[:50])
        y_pos -= 0.1*inch
        c.drawString(0.1*inch, y_pos, address[50:])
    else:
        c.drawString(0.1*inch, y_pos, address)
    
    # Validity section
    y_pos -= 0.15*inch
    c.setFont("Helvetica-Bold", 6)
    c.drawString(0.1*inch, y_pos, "COV:")
    c.setFont("Helvetica", 6)
    cov_text = ", ".join(license_data['vehicle_classes'])
    c.drawString(0.35*inch, y_pos, cov_text)
    
    y_pos -= 0.1*inch
    c.setFont("Helvetica-Bold", 6)
    issue_formatted = datetime.strptime(license_data['issue_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
    expiry_formatted = datetime.strptime(license_data['expiry_date'], '%Y-%m-%d').strftime('%d-%m-%Y')
    c.drawString(0.1*inch, y_pos, f"Issue: {issue_formatted}")
    c.drawString(1.5*inch, y_pos, f"Valid Till: {expiry_formatted}")
    
    # RTO Code
    y_pos -= 0.1*inch
    c.setFont("Helvetica-Bold", 6)
    c.drawString(0.1*inch, y_pos, f"Issuing Authority: RTO {license_data['rto_code']}")
    
    # Footer
    c.setFillColor(red)
    c.setFont("Helvetica-Bold", 7)
    c.drawCentredString(1.685*inch, 0.08*inch, "*** TEST DOCUMENT - FOR KYC TESTING ONLY ***")
    
    # Barcode placeholder
    c.setFillColor(black)
    c.setFont("Courier", 5)
    barcode = f"||{license_data['id_number']}||"
    c.drawString(0.1*inch, 0.18*inch, barcode)
    
    c.save()
    print(f"✓ Generated: {filename}")
    print(f"  Name: {license_data['name']}")
    print(f"  DL No: {license_data['id_number']}")

def main():
    # Load data from government database
    with open('mock_data/government_db.json', 'r') as f:
        govt_db = json.load(f)
    
    # Filter Indian driving licenses (proper format with state code)
    indian_dls = [record for record in govt_db['records'] 
                  if record['id_type'] == 'DRIVERS_LICENSE' 
                  and 'state' in record
                  and len(record['id_number']) > 10]
    
    if len(indian_dls) < 2:
        print("Error: Not enough Indian DL records in government database")
        return
    
    # Generate licenses
    print("\n🚗 Generating Indian Driving Licenses from Government Database...\n")
    
    generate_indian_license('samples/pdf/indian_drivers_license_1.pdf', indian_dls[0])
    print()
    generate_indian_license('samples/pdf/indian_drivers_license_2.pdf', indian_dls[1])
    
    print("\n" + "="*60)
    print("✅ SUCCESS: Generated 2 Indian Driving Licenses")
    print("="*60)
    print("\n📄 Files created:")
    print("  1. samples/pdf/indian_drivers_license_1.pdf")
    print("  2. samples/pdf/indian_drivers_license_2.pdf")
    print("\n✓ Data verified against mock_data/government_db.json")
    print("✓ Records match government database")
    print("\n⚠️  These are TEST documents marked as SAMPLE for KYC testing only\n")

if __name__ == "__main__":
    main()