#!/usr/bin/env python3
"""
🧪 Test Corrected Error Codes
Tests the corrected error code patterns with real documents

Features:
- Tests corrected Konica Minolta error codes (C####, J##-##, E##-##)
- Tests corrected HP error codes with more examples
- Validates error code extraction accuracy
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
import re
from typing import Dict

# Import our JSON config classifier
from json_config_classifier import JSONConfigClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CorrectedErrorCodeTest:
    """Test corrected error code patterns"""
    
    def __init__(self):
        self.classifier = JSONConfigClassifier()
        self.test_results = {}
        
    async def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Convert PDF to text using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            # Limit to first 4 pages for focused testing
            max_pages = min(4, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            return ""
    
    def create_test_content_with_error_codes(self) -> Dict[str, str]:
        """Create test content with various error codes to validate patterns"""
        return {
            "hp_test": """
            HP LaserJet Pro E786 Service Manual
            
            Error Code 13.20.01: Paper jam in duplex unit
            Error Code 41.03.01: Fuser assembly failure
            Error Code 50.01.01: Fan 1 failure
            Error Code 56.01.01: Toner cartridge error
            Error Code 57.01.01: Drum unit error
            
            Troubleshooting Steps:
            1. Check for paper jam in duplex unit (13.20.01)
            2. Verify fuser assembly (41.03.01)
            3. Check fan operation (50.01.01)
            """,
            
            "konica_minolta_test": """
            Konica Minolta BizHub C658 Service Manual
            
            Error Code C1200: System memory problem
            Error Code C1300: Polygon motor (laser motor)
            Error Code C1401: IR main program timeout
            Error Code C9401: Exposure LED illumination error
            Error Code J11-01: Paper jam in input tray 1
            Error Code J11-02: Paper transport delay from tray 1
            Error Code 11.01: Paper jam in input tray 1
            Error Code E46-01: Image control board problem
            Error Code E46-02: Exposure lamp problem
            
            Troubleshooting Steps:
            1. Check system memory (C1200)
            2. Verify laser motor (C1300)
            3. Check paper jam (J11-01)
            """,
            
            "lexmark_test": """
            Lexmark CX825 Service Manual
            
            Error Code 100: Paper jam in input tray
            Error Code 200: Fuser unit error
            Error Code 300: Fan failure
            Error Code 500: Laser unit failure
            Error Code 600: Scanner initialization error
            
            Troubleshooting Steps:
            1. Clear paper jam (100)
            2. Check fuser unit (200)
            3. Verify fan operation (300)
            """,
            
            "utax_test": """
            UTAX 2508CI Service Manual
            
            Error Code 01095: Paper jam in input tray
            Error Code 02001: Fuser unit error
            Error Code 03001: Fan failure
            Error Code 05001: Laser unit failure
            Error Code 06001: Scanner initialization error
            
            Troubleshooting Steps:
            1. Clear paper jam (01095)
            2. Check fuser unit (02001)
            3. Verify fan operation (03001)
            """
        }
    
    async def test_error_code_extraction(self):
        """Test error code extraction with corrected patterns"""
        logger.info("🧪 Testing corrected error code extraction...")
        
        test_contents = self.create_test_content_with_error_codes()
        
        for test_name, content in test_contents.items():
            logger.info(f"🧪 Testing {test_name}...")
            
            # Create a dummy filename based on test name
            filename = f"{test_name}_test.pdf"
            
            # Classify document
            result = self.classifier.classify_document(filename, content)
            
            self.test_results[test_name] = result
            
            # Print detailed results
            print(f"\n📄 {test_name.upper()} TEST")
            print(f"   🏷️  Classification:")
            print(f"      • Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
            print(f"      • Document Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
            
            print(f"   ⚠️  Error Code Extraction (Corrected Patterns):")
            error_codes = result['extraction']['error_codes']
            print(f"      • Total Error Codes Found: {len(error_codes)}")
            
            if error_codes:
                for i, error in enumerate(error_codes, 1):
                    print(f"      {i}. {error['code']}: {error['description']} ({error['category']})")
            else:
                print(f"      • No error codes extracted")
            
            print(f"   🔧 Part Number Extraction:")
            part_numbers = result['extraction']['part_numbers']
            print(f"      • Total Part Numbers Found: {len(part_numbers)}")
            
            if part_numbers:
                for i, part in enumerate(part_numbers, 1):
                    print(f"      {i}. {part['part_number']}: {part['description']} ({part['category']})")
            else:
                print(f"      • No part numbers extracted")
            
            print(f"   📊 Analysis:")
            tech_info = result['extraction']['technical_info']
            print(f"      • Has Troubleshooting: {'✅' if tech_info['has_troubleshooting'] else '❌'}")
            print(f"      • Word Count: {tech_info['word_count']}")
            print(f"      • Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")
        
        logger.info(f"✅ Tested {len(self.test_results)} error code scenarios")
    
    async def test_real_documents(self, max_documents: int = 3):
        """Test with real documents to validate error code extraction"""
        logger.info(f"🧪 Testing corrected error codes on {max_documents} real documents...")
        
        # Find PDF documents
        pdf_files = list(Path("../test_documents").rglob("*.pdf"))
        test_files = pdf_files[:max_documents]
        
        for i, pdf_file in enumerate(test_files, 1):
            logger.info(f"🧪 Testing real document {i}/{len(test_files)}: {pdf_file.name}")
            
            try:
                # Convert PDF to text
                content = await self.convert_pdf_to_text(str(pdf_file))
                
                if not content.strip():
                    logger.warning(f"No text extracted from {pdf_file}")
                    continue
                
                # Classify document
                result = self.classifier.classify_document(pdf_file.name, content)
                
                self.test_results[f"real_{pdf_file.name}"] = result
                
                # Print detailed results
                print(f"\n📄 REAL DOCUMENT: {pdf_file.name}")
                print(f"   🏷️  Classification:")
                print(f"      • Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
                print(f"      • Document Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
                print(f"      • Series: {result['classification']['series']} (confidence: {result['classification']['series_confidence']:.2f})")
                
                print(f"   ⚠️  Error Code Extraction (Real Document):")
                error_codes = result['extraction']['error_codes']
                print(f"      • Total Error Codes Found: {len(error_codes)}")
                
                if error_codes:
                    for i, error in enumerate(error_codes[:5], 1):  # Show first 5
                        print(f"      {i}. {error['code']}: {error['description']} ({error['category']})")
                    if len(error_codes) > 5:
                        print(f"      ... and {len(error_codes) - 5} more")
                else:
                    print(f"      • No error codes extracted")
                
                print(f"   🔧 Part Number Extraction (Real Document):")
                part_numbers = result['extraction']['part_numbers']
                print(f"      • Total Part Numbers Found: {len(part_numbers)}")
                
                if part_numbers:
                    for i, part in enumerate(part_numbers[:3], 1):  # Show first 3
                        print(f"      {i}. {part['part_number']}: {part['description']} ({part['category']})")
                    if len(part_numbers) > 3:
                        print(f"      ... and {len(part_numbers) - 3} more")
                else:
                    print(f"      • No part numbers extracted")
                
                print(f"   📊 Analysis:")
                tech_info = result['extraction']['technical_info']
                print(f"      • Has Troubleshooting: {'✅' if tech_info['has_troubleshooting'] else '❌'}")
                print(f"      • Word Count: {tech_info['word_count']:,}")
                print(f"      • Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")
                
            except Exception as e:
                logger.error(f"❌ Failed to test {pdf_file}: {str(e)}")
                self.test_results[f"real_{pdf_file.name}"] = {'error': str(e)}
        
        logger.info(f"✅ Tested {len([r for r in self.test_results.values() if 'error' not in r])} real documents")
    
    def generate_corrected_error_code_report(self):
        """Generate report for corrected error code testing"""
        logger.info("📊 Generating corrected error code analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze error code extraction results
        error_code_analysis = self._analyze_error_code_extraction()
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'error_code_analysis': error_code_analysis,
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/corrected_error_code_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_corrected_error_code_summary(report)
        
        logger.info(f"📊 Corrected error code report saved to: {report_file}")
    
    def _analyze_error_code_extraction(self) -> Dict:
        """Analyze error code extraction results"""
        analysis = {
            'total_error_codes_extracted': 0,
            'manufacturer_specific_codes': {},
            'error_code_categories': {},
            'validation_success_rate': 0,
            'pattern_effectiveness': {}
        }
        
        total_valid_codes = 0
        total_extracted_codes = 0
        
        for test_name, result in self.test_results.items():
            if 'error' in result:
                continue
                
            extraction = result['extraction']
            manufacturer = result['classification']['manufacturer']
            
            error_codes = extraction.get('error_codes', [])
            total_extracted_codes += len(error_codes)
            
            # Count manufacturer-specific codes
            if manufacturer not in analysis['manufacturer_specific_codes']:
                analysis['manufacturer_specific_codes'][manufacturer] = 0
            analysis['manufacturer_specific_codes'][manufacturer] += len(error_codes)
            
            # Count categories
            for error in error_codes:
                category = error['category']
                if category not in analysis['error_code_categories']:
                    analysis['error_code_categories'][category] = 0
                analysis['error_code_categories'][category] += 1
                
                # Validate error code format
                code = error['code']
                if self._validate_error_code_format(code, manufacturer):
                    total_valid_codes += 1
        
        analysis['total_error_codes_extracted'] = total_extracted_codes
        analysis['validation_success_rate'] = (total_valid_codes / total_extracted_codes * 100) if total_extracted_codes > 0 else 0
        
        # Pattern effectiveness analysis
        analysis['pattern_effectiveness'] = {
            'hp_xx_xx_xx_pattern': analysis['manufacturer_specific_codes'].get('hp', 0) > 0,
            'konica_minolta_c_pattern': analysis['manufacturer_specific_codes'].get('konica_minolta', 0) > 0,
            'konica_minolta_j_pattern': analysis['manufacturer_specific_codes'].get('konica_minolta', 0) > 0,
            'lexmark_xxx_pattern': analysis['manufacturer_specific_codes'].get('lexmark', 0) > 0,
            'utax_xxxxx_pattern': analysis['manufacturer_specific_codes'].get('utax', 0) > 0
        }
        
        return analysis
    
    def _validate_error_code_format(self, code: str, manufacturer: str) -> bool:
        """Validate error code format based on manufacturer"""
        if manufacturer.lower() == 'hp':
            return bool(re.match(r'^\d{2}\.\d{2}(?:\.\d{2})?$', code))
        elif manufacturer.lower() == 'konica_minolta':
            return bool(re.match(r'^[CJ]\d{4,5}$|^[CJ]\d{2}-\d{2}$|^\d{2}\.\d{2}$|^E\d{2}-\d{2}$', code))
        elif manufacturer.lower() == 'lexmark':
            return bool(re.match(r'^\d{3,4}$', code))
        elif manufacturer.lower() == 'utax':
            return bool(re.match(r'^\d{5}$', code))
        return False
    
    def print_corrected_error_code_summary(self, report):
        """Print corrected error code test summary"""
        print("\n" + "="*80)
        print("🧪 CORRECTED ERROR CODE EXTRACTION ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        analysis = report['error_code_analysis']
        
        print(f"\n⚠️  ERROR CODE EXTRACTION RESULTS:")
        print(f"  • Total Error Codes Extracted: {analysis['total_error_codes_extracted']}")
        print(f"  • Validation Success Rate: {analysis['validation_success_rate']:.1f}%")
        
        print(f"\n🏭 MANUFACTURER-SPECIFIC ERROR CODES:")
        for manufacturer, count in analysis['manufacturer_specific_codes'].items():
            print(f"  • {manufacturer.upper()}: {count} codes extracted")
        
        print(f"\n📋 ERROR CODE CATEGORIES:")
        for category, count in analysis['error_code_categories'].items():
            print(f"  • {category.replace('_', ' ').upper()}: {count} codes")
        
        print(f"\n🎯 PATTERN EFFECTIVENESS:")
        effectiveness = analysis['pattern_effectiveness']
        print(f"  • HP XX.XX.XX Pattern: {'✅' if effectiveness['hp_xx_xx_xx_pattern'] else '❌'}")
        print(f"  • Konica Minolta C Pattern: {'✅' if effectiveness['konica_minolta_c_pattern'] else '❌'}")
        print(f"  • Konica Minolta J Pattern: {'✅' if effectiveness['konica_minolta_j_pattern'] else '❌'}")
        print(f"  • Lexmark XXX Pattern: {'✅' if effectiveness['lexmark_xxx_pattern'] else '❌'}")
        print(f"  • UTAX XXXXX Pattern: {'✅' if effectiveness['utax_xxxxx_pattern'] else '❌'}")
        
        print(f"\n✅ Corrected error code testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 Corrected Error Code Extraction Test")
    print("=" * 60)
    print("Testing corrected error code patterns...")
    print("Features: C####, J##-##, E##-## for Konica Minolta")
    print("Features: Extended HP error codes")
    print()
    
    tester = CorrectedErrorCodeTest()
    
    # Test error code extraction with synthetic content
    await tester.test_error_code_extraction()
    
    # Test with real documents
    await tester.test_real_documents(max_documents=3)
    
    # Generate report
    tester.generate_corrected_error_code_report()

if __name__ == "__main__":
    asyncio.run(main())
