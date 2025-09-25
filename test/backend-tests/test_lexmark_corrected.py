#!/usr/bin/env python3
"""
🧪 Test Corrected Lexmark Error Codes
Tests the corrected Lexmark error code patterns (XXX.XX format)

Features:
- Tests corrected Lexmark error codes (121.54, 200.03, 84.00, etc.)
- Validates XXX.XX pattern recognition
- Tests with real examples from user
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

class LexmarkCorrectedTest:
    """Test corrected Lexmark error code patterns"""
    
    def __init__(self):
        self.classifier = JSONConfigClassifier()
        self.test_results = {}
        
    def create_lexmark_test_content(self) -> Dict[str, str]:
        """Create test content with corrected Lexmark error codes"""
        return {
            "lexmark_corrected_test": """
            Lexmark CX825 CX860 Service Manual
            
            Error Code 121.54: The fuser secondary thermistor temperature is out of range.
            Error Code 121.00: Fuser has not reached required temperature during warm-up.
            Error Code 121.45: Service fuser error.
            Error Code 200.03: Paper jam in universal feeder.
            Error Code 200.04: Paper jam in tray 1.
            Error Code 84.00: Imaging unit low capacity warning.
            Error Code 88.00: Toner cartridge low warning.
            Error Code 92.00: Waste toner container full.
            Error Code 300.00: Fan failure.
            Error Code 500.00: Laser unit failure.
            
            Troubleshooting Steps:
            1. Check fuser temperature (121.54)
            2. Clear paper jam (200.03)
            3. Replace imaging unit (84.00)
            4. Check toner levels (88.00)
            """,
            
            "lexmark_mixed_test": """
            Lexmark CX825 Error Codes
            
            Some error codes: 121.54, 200.03, 84.00, 88.00
            Other codes: 121.00, 121.45, 92.00, 300.00
            
            The error 121.54 indicates fuser thermistor problem.
            Code 200.03 means paper jam in universal feeder.
            """
        }
    
    async def test_lexmark_error_code_extraction(self):
        """Test Lexmark error code extraction with corrected patterns"""
        logger.info("🧪 Testing corrected Lexmark error code extraction...")
        
        test_contents = self.create_lexmark_test_content()
        
        for test_name, content in test_contents.items():
            logger.info(f"🧪 Testing {test_name}...")
            
            # Create a dummy filename
            filename = f"{test_name}.pdf"
            
            # Classify document
            result = self.classifier.classify_document(filename, content)
            
            self.test_results[test_name] = result
            
            # Print detailed results
            print(f"\n📄 {test_name.upper()}")
            print(f"   🏷️  Classification:")
            print(f"      • Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
            print(f"      • Document Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
            
            print(f"   ⚠️  Lexmark Error Code Extraction (XXX.XX Format):")
            error_codes = result['extraction']['error_codes']
            print(f"      • Total Error Codes Found: {len(error_codes)}")
            
            if error_codes:
                # Group by category
                categories = {}
                for error in error_codes:
                    category = error['category']
                    if category not in categories:
                        categories[category] = []
                    categories[category].append(error)
                
                for category, codes in categories.items():
                    print(f"      📋 {category.upper()} ({len(codes)} codes):")
                    for error in codes:
                        print(f"        - {error['code']}: {error['description']}")
            else:
                print(f"      • No error codes extracted")
            
            print(f"   📊 Analysis:")
            tech_info = result['extraction']['technical_info']
            print(f"      • Has Troubleshooting: {'✅' if tech_info['has_troubleshooting'] else '❌'}")
            print(f"      • Word Count: {tech_info['word_count']}")
            print(f"      • Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")
        
        logger.info(f"✅ Tested {len(self.test_results)} Lexmark error code scenarios")
    
    def test_pattern_validation(self):
        """Test the XXX.XX pattern validation"""
        logger.info("🧪 Testing Lexmark XXX.XX pattern validation...")
        
        # Test valid patterns
        valid_codes = [
            "121.54", "121.00", "121.45", "200.03", "200.04", 
            "84.00", "88.00", "92.00", "300.00", "500.00"
        ]
        
        # Test invalid patterns (should not match)
        invalid_codes = [
            "121", "12154", "121-54", "12.54", "121.5", "121.545",
            "ABC.12", "121.AB", "12.1.54", "121.54.00"
        ]
        
        validation_regex = r'^\d{2,3}\.\d{2}$'
        
        print(f"\n🔍 PATTERN VALIDATION TEST:")
        print(f"   ✅ Valid Patterns (should match):")
        for code in valid_codes:
            match = bool(re.match(validation_regex, code))
            print(f"      {code}: {'✅' if match else '❌'}")
        
        print(f"   ❌ Invalid Patterns (should NOT match):")
        for code in invalid_codes:
            match = bool(re.match(validation_regex, code))
            print(f"      {code}: {'✅' if match else '❌'}")
    
    def generate_lexmark_report(self):
        """Generate Lexmark error code test report"""
        logger.info("📊 Generating Lexmark error code analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze results
        analysis = self._analyze_lexmark_results()
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_tests': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'lexmark_analysis': analysis,
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/lexmark_corrected_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_lexmark_summary(report)
        
        logger.info(f"📊 Lexmark error code report saved to: {report_file}")
    
    def _analyze_lexmark_results(self) -> Dict:
        """Analyze Lexmark error code extraction results"""
        analysis = {
            'total_error_codes_extracted': 0,
            'error_code_categories': {},
            'pattern_validation_success': 0,
            'unique_error_codes': set(),
            'format_validation': {
                'xxx_xx_format': 0,
                'invalid_formats': 0
            }
        }
        
        total_valid_codes = 0
        
        for test_name, result in self.test_results.items():
            if 'error' in result:
                continue
                
            extraction = result['extraction']
            error_codes = extraction.get('error_codes', [])
            analysis['total_error_codes_extracted'] += len(error_codes)
            
            # Count categories
            for error in error_codes:
                category = error['category']
                if category not in analysis['error_code_categories']:
                    analysis['error_code_categories'][category] = 0
                analysis['error_code_categories'][category] += 1
                
                # Validate format
                code = error['code']
                analysis['unique_error_codes'].add(code)
                
                if re.match(r'^\d{2,3}\.\d{2}$', code):
                    analysis['format_validation']['xxx_xx_format'] += 1
                    total_valid_codes += 1
                else:
                    analysis['format_validation']['invalid_formats'] += 1
        
        analysis['pattern_validation_success'] = (total_valid_codes / analysis['total_error_codes_extracted'] * 100) if analysis['total_error_codes_extracted'] > 0 else 0
        
        # Convert set to list for JSON serialization
        analysis['unique_error_codes'] = list(analysis['unique_error_codes'])
        
        return analysis
    
    def print_lexmark_summary(self, report):
        """Print Lexmark error code test summary"""
        print("\n" + "="*80)
        print("🧪 CORRECTED LEXMARK ERROR CODE ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Tests: {report['summary']['total_tests']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        analysis = report['lexmark_analysis']
        
        print(f"\n⚠️  LEXMARK ERROR CODE EXTRACTION:")
        print(f"  • Total Error Codes Extracted: {analysis['total_error_codes_extracted']}")
        print(f"  • Unique Error Codes: {len(analysis['unique_error_codes'])}")
        print(f"  • Pattern Validation Success: {analysis['pattern_validation_success']:.1f}%")
        
        print(f"\n📋 ERROR CODE CATEGORIES:")
        for category, count in analysis['error_code_categories'].items():
            print(f"  • {category.replace('_', ' ').upper()}: {count} codes")
        
        print(f"\n🎯 FORMAT VALIDATION:")
        format_validation = analysis['format_validation']
        print(f"  • XXX.XX Format: {format_validation['xxx_xx_format']} codes ✅")
        print(f"  • Invalid Formats: {format_validation['invalid_formats']} codes ❌")
        
        print(f"\n🔍 UNIQUE ERROR CODES FOUND:")
        for code in sorted(analysis['unique_error_codes']):
            print(f"  • {code}")
        
        print(f"\n✅ Lexmark error code correction testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 Corrected Lexmark Error Code Test")
    print("=" * 60)
    print("Testing corrected Lexmark error code patterns...")
    print("Format: XXX.XX (e.g., 121.54, 200.03, 84.00)")
    print()
    
    tester = LexmarkCorrectedTest()
    
    # Test pattern validation first
    tester.test_pattern_validation()
    
    # Test error code extraction with corrected patterns
    await tester.test_lexmark_error_code_extraction()
    
    # Generate report
    tester.generate_lexmark_report()

if __name__ == "__main__":
    asyncio.run(main())
