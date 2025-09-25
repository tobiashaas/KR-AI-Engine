#!/usr/bin/env python3
"""
Test JSON version extractor with real PDF documents
"""

import fitz
from pathlib import Path
import sys
sys.path.append('.')
from json_version_extractor import JSONVersionExtractor

def test_with_real_pdfs():
    """Test JSON version extractor with real PDF documents"""
    
    print("🔍 JSON VERSION EXTRACTOR - REAL PDF TEST")
    print("=" * 60)
    
    extractor = JSONVersionExtractor()
    
    # Test cases with expected versions
    test_cases = [
        ('HP_E786_SM.pdf', 'Edition 3, 5/2024'),
        ('Lexmark_CX825_CX860_XC8155_XC8160.pdf', 'November 2024'),
        ('HP_E786_CPMD.pdf', 'Edition 4.0, 04/2025'),
        ('KM_4750i_4050i_4751i_4051i_SM.pdf', '2024/12/25'),
        ('KM_C658_C558_C458_C368_C308_C258_SM_EN.pdf', '2022/09/29')
    ]
    
    results = []
    
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
                
                # Extract version using JSON config
                extracted = extractor.extract_version(text)
                detected_version = extracted['version']
                
                print(f"   Detected: {detected_version}")
                print(f"   Pattern: {extracted['pattern_category']}")
                print(f"   Confidence: {extracted['confidence']:.2f}")
                
                # Check if detected version matches expected
                success = (expected_version.lower() in detected_version.lower() or 
                          detected_version.lower() in expected_version.lower())
                
                if success:
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
                
                results.append({
                    'filename': filename,
                    'expected': expected_version,
                    'detected': detected_version,
                    'success': success,
                    'pattern': extracted['pattern_category'],
                    'confidence': extracted['confidence']
                })
                
                print()
                
            except Exception as e:
                print(f"❌ Error with {filename}: {e}")
                print()
        else:
            print(f"❌ File not found: {filename}")
    
    # Summary
    successful = sum(1 for r in results if r['success'])
    total = len(results)
    success_rate = successful / total if total > 0 else 0
    
    print("📊 SUMMARY:")
    print(f"   Total Tests: {total}")
    print(f"   Successful: {successful}")
    print(f"   Failed: {total - successful}")
    print(f"   Success Rate: {success_rate:.1%}")
    print()
    
    # Show pattern usage
    pattern_usage = {}
    for result in results:
        pattern = result['pattern']
        pattern_usage[pattern] = pattern_usage.get(pattern, 0) + 1
    
    print("📋 PATTERN USAGE:")
    for pattern, count in pattern_usage.items():
        print(f"   {pattern}: {count} times")
    
    return results

if __name__ == "__main__":
    test_with_real_pdfs()
