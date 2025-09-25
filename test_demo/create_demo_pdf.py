#!/usr/bin/env python3
"""
Create a demo PDF for KRAI Engine Live Processing Demo
"""

from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
import os

def create_demo_pdf():
    filename = "HP_LaserJet_Demo.pdf"
    c = canvas.Canvas(filename, pagesize=letter)
    width, height = letter
    
    # Page 1: Title and basic info
    c.setFont("Helvetica-Bold", 20)
    c.drawString(100, height - 100, "HP LaserJet Pro M404dn Service Manual")
    
    c.setFont("Helvetica", 12)
    c.drawString(100, height - 150, "Edition 1, 03/2023")
    c.drawString(100, height - 170, "Product Family: LaserJet Pro M400 Series")
    c.drawString(100, height - 190, "Models: M404n, M404dn, M404dw")
    
    c.drawString(100, height - 230, "Error Codes:")
    c.drawString(120, height - 250, "• 13.01 - Paper jam in input tray")
    c.drawString(120, height - 270, "• 49.XX.YY - Critical firmware error")  
    c.drawString(120, height - 290, "• 59.XY - Motor error")
    
    c.drawString(100, height - 330, "Part Numbers:")
    c.drawString(120, height - 350, "• CF258A - Black toner cartridge")
    c.drawString(120, height - 370, "• RM2-5582 - Fuser assembly")
    c.drawString(120, height - 390, "• RM2-5583 - Transfer roller")
    
    # Page 2: Technical details
    c.showPage()
    c.setFont("Helvetica-Bold", 16)
    c.drawString(100, height - 100, "Technical Specifications")
    
    c.setFont("Helvetica", 10)
    c.drawString(100, height - 140, "Print Speed: Up to 38 ppm (A4), 40 ppm (Letter)")
    c.drawString(100, height - 160, "First Page Out: As fast as 7.3 seconds")
    c.drawString(100, height - 180, "Monthly Duty Cycle: Up to 80,000 pages")
    c.drawString(100, height - 200, "Memory: 256 MB (standard)")
    
    c.drawString(100, height - 240, "Common Error Resolution:")
    c.drawString(120, height - 260, "1. Check paper path for obstructions")
    c.drawString(120, height - 280, "2. Verify toner cartridge installation")
    c.drawString(120, height - 300, "3. Clean transfer path components")
    c.drawString(120, height - 320, "4. Update firmware to latest version")
    
    c.drawString(100, height - 360, "Version Information:")
    c.drawString(120, height - 380, "• Firmware Version: 2404.001.00.004")
    c.drawString(120, height - 400, "• Document Version: v2.1")
    c.drawString(120, height - 420, "• Last Updated: March 2023")
    
    c.save()
    print(f"✅ Created demo PDF: {filename}")
    return filename

if __name__ == "__main__":
    create_demo_pdf()
