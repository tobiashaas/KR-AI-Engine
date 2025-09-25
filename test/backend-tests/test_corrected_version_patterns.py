#!/usr/bin/env python3
"""
Test corrected version patterns with real PDF content
"""

import re
from pathlib import Path
import fitz

def extract_version_enhanced(text):
    """Extract version using corrected patterns"""
    
    # Corrected version patterns (without double backslashes)
    patterns = [
        # Edition patterns
        r'edition\s+([0-9]+(?:\.[0-9]+)?)\s*,?\s*([0-9]+/[0-9]{4})',  # Edition 3, 5/2024
        r'edition\s+([0-9]+(?:\.[0-9]+)?)',  # Edition 4.0
        
        # Date patterns
        r'([0-9]{4}/[0-9]{2}/[0-9]{2})',   # 2024/12/25
        r'([0-9]{2}/[0-9]{4})',            # 5/2024
        r'([a-z]+\s+[0-9]{4})',            # November 2024
        
        # Standard version patterns
        r'version\s+([0-9\.]+)',
        r'ver\s+([0-9\.]+)',
        r'v\s*([0-9\.]+)',
        r'rev\s+([0-9\.]+)',
        r'revision\s+([0-9\.]+)',
        r'fw\s+([0-9\.]+)',
        r'firmware\s+([0-9\.]+)',
        r'function\s+version\s+([0-9\.]+)',
        r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)',  # Standard version format
        r'([0-9]+\.[0-9]+[A-Z]?)',         # Version with letter
        r'([A-Z]\d+\.\d+)',                # Letter prefix version
    ]
    
    # Check edition + date patterns first (most specific)
    edition_date_pattern = r'edition\s+([0-9]+(?:\.[0-9]+)?)\s*,?\s*([0-9]+/[0-9]{4})'
    match = re.search(edition_date_pattern, text, re.IGNORECASE)
    if match:
        return f"{match.group(1)}, {match.group(2)}"
    
    # Check other patterns
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            if len(match.groups()) > 1:
                return f"{match.group(1)}, {match.group(2)}"
            return match.group(1)
    
    return ''

def test_with_real_pdfs():
    """Test version extraction with real PDF documents"""
    
    print("🔍 TESTING CORRECTED VERSION PATTERNS WITH REAL PDFS")
    print("=" * 60)
    
    # Test cases with expected versions
    test_cases = [
        ('HP_E786_SM.pdf', 'Edition 3, 5/2024'),
        ('Lexmark_CX825_CX860_XC8155_XC8160.pdf', 'November 2024'),
        ('HP_E786_CPMD.pdf', 'Edition 4.0, 04/2025'),
        ('KM_4750i_4050i_4751i_4051i_SM.pdf', '2024/12/25'),
        ('KM_C658_C558_C458_C368_C308_C258_SM_EN.pdf', '2022/09/29')
    ]
    
    for filename, expected_version in test_cases:
        pdf_path = Path('../test_documents') / filename
        if pdf_path.exists():
            try:
                # Extract text from first few pages
                doc = fitz.open(str(pdf_path))
                text = ''
                for page_num in range(min(3, len(doc))):
                    text += doc[page_num].get_text() + '\n'
                doc.close()
                
                print(f"📄 {filename}")
                print(f"   Expected: {expected_version}")
                
                # Extract version
                detected_version = extract_version_enhanced(text)
                print(f"   Detected: {detected_version}")
                
                # Check if detected version matches expected
                if expected_version.lower() in detected_version.lower() or detected_version.lower() in expected_version.lower():
                    print(f"   ✅ MATCH!")
                else:
                    print(f"   ❌ NO MATCH")
                    
                    # Debug: Show version-related content
                    lines = text.split('\n')
                    version_lines = []
                    for line in lines[:30]:
                        if any(keyword in line.lower() for keyword in ['edition', 'version', 'rev', 'ver', 'date', '2024', '2025', '2022']):
                            version_lines.append(line.strip())
                    
                    if version_lines:
                        print("   Version-related lines found:")
                        for line in version_lines:
                            print(f"     {line}")
                
                print()
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                print()
        else:
            print(f"❌ File not found: {filename}")

if __name__ == "__main__":
    test_with_real_pdfs()
