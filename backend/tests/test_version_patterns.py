#!/usr/bin/env python3
"""
Test script for enhanced version pattern recognition
"""

import re
from pathlib import Path
import fitz

def test_version_patterns():
    """Test version patterns with known examples"""
    
    print("🔍 TESTING VERSION PATTERNS")
    print("=" * 50)
    
    # Test cases with expected versions
    test_cases = [
        {
            'filename': 'HP_E786_SM.pdf',
            'expected': 'Edition 3, 5/2024',
            'test_text': 'Service Manual Edition 3, 5/2024'
        },
        {
            'filename': 'Lexmark_CX825_CX860_XC8155_XC8160.pdf', 
            'expected': 'November 2024',
            'test_text': 'November 2024 Service Manual'
        },
        {
            'filename': 'HP_E786_CPMD.pdf',
            'expected': 'Edition 4.0, 04/2025',
            'test_text': 'CPMD Database Edition 4.0, 04/2025'
        },
        {
            'filename': 'KM_4750i_4050i_4751i_4051i_SM.pdf',
            'expected': '2024/12/25',
            'test_text': 'Service Manual 2024/12/25'
        },
        {
            'filename': 'KM_C658_C558_C458_C368_C308_C258_SM_EN.pdf',
            'expected': '2022/09/29',
            'test_text': 'Service Manual 2022/09/29'
        }
    ]
    
    # Enhanced version patterns
    version_patterns = [
        # Edition patterns
        r'edition\s+([0-9]+(?:\\.[0-9]+)?)\\s*,?\\s*([0-9]+/[0-9]{4})',  # Edition 3, 5/2024
        r'edition\s+([0-9]+(?:\\.[0-9]+)?)',  # Edition 4.0
        
        # Date patterns
        r'([0-9]{4}/[0-9]{2}/[0-9]{2})',   # 2024/12/25
        r'([0-9]{2}/[0-9]{4})',            # 5/2024
        r'([a-z]+\\s+[0-9]{4})',           # November 2024
        
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
    
    def extract_version(text):
        """Extract version using enhanced patterns"""
        # Check edition + date patterns first (most specific)
        edition_date_pattern = r'edition\s+([0-9]+(?:\\.[0-9]+)?)\\s*,?\\s*([0-9]+/[0-9]{4})'
        match = re.search(edition_date_pattern, text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}, {match.group(2)}"
        
        # Check other patterns
        for pattern in version_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1:
                    return f"{match.group(1)}, {match.group(2)}"
                return match.group(1)
        
        return ''
    
    # Test each case
    for case in test_cases:
        print(f"📄 {case['filename']}")
        print(f"   Expected: {case['expected']}")
        
        detected = extract_version(case['test_text'])
        print(f"   Detected: {detected}")
        
        # Check if detected matches expected
        if case['expected'].lower() in detected.lower() or detected.lower() in case['expected'].lower():
            print(f"   ✅ MATCH!")
        else:
            print(f"   ❌ NO MATCH")
        print()
    
    # Test with real PDF content
    print("🔍 TESTING WITH REAL PDF CONTENT")
    print("=" * 50)
    
    pdf_files = list(Path('../test_documents').glob('*.pdf'))[:3]
    
    for pdf_file in pdf_files:
        try:
            doc = fitz.open(str(pdf_file))
            text = ''
            for page_num in range(min(2, len(doc))):
                text += doc[page_num].get_text() + '\n'
            doc.close()
            
            print(f"📄 {pdf_file.name}")
            
            # Look for version-related content
            lines = text.split('\n')
            version_lines = []
            for line in lines[:20]:  # First 20 lines
                if any(keyword in line.lower() for keyword in ['edition', 'version', 'rev', 'ver', 'date', '2024', '2025', '2022']):
                    version_lines.append(line.strip())
            
            if version_lines:
                print("   Version-related lines found:")
                for line in version_lines:
                    print(f"     {line}")
                    
                # Extract version from combined text
                detected = extract_version(text)
                print(f"   Detected version: {detected}")
            else:
                print("   No version-related content found in first 20 lines")
            
            print()
            
        except Exception as e:
            print(f"❌ Error with {pdf_file.name}: {e}")
            print()

if __name__ == "__main__":
    test_version_patterns()
