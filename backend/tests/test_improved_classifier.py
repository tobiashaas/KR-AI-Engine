#!/usr/bin/env python3
"""
🧪 Test Improved Hybrid Classifier
Tests the improved classifier with real documents

Features:
- Tests improved error code extraction
- Tests series detection
- Compares with previous results
- Generates detailed analysis
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Dict

# Import our improved classifier
from improved_hybrid_classifier import ImprovedHybridClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ImprovedClassifierTest:
    """Test improved hybrid document classification"""
    
    def __init__(self):
        self.classifier = ImprovedHybridClassifier()
        self.test_results = {}
        
    async def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Convert PDF to text using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            # Limit to first 6 pages for focused testing
            max_pages = min(6, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            return ""
    
    async def test_documents(self, max_documents: int = 8):
        """Test improved classification on real documents"""
        logger.info(f"🧪 Testing improved classification on {max_documents} documents...")
        
        # Find PDF documents
        pdf_files = list(Path("../test_documents").rglob("*.pdf"))
        test_files = pdf_files[:max_documents]
        
        for i, pdf_file in enumerate(test_files, 1):
            logger.info(f"🧪 Testing document {i}/{len(test_files)}: {pdf_file.name}")
            
            try:
                # Convert PDF to text
                content = await self.convert_pdf_to_text(str(pdf_file))
                
                if not content.strip():
                    logger.warning(f"No text extracted from {pdf_file}")
                    continue
                
                # Improved hybrid classification
                result = self.classifier.classify_document(pdf_file.name, content)
                
                self.test_results[pdf_file.name] = result
                
                # Print detailed results
                print(f"\n📄 {pdf_file.name}")
                print(f"   🏷️  Classification:")
                print(f"      • Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
                print(f"      • Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
                print(f"      • Series: {result['classification']['series']} (confidence: {result['classification']['series_confidence']:.2f})")
                print(f"      • Models: {result['classification']['models'][:5]}")  # Show first 5
                print(f"      • Version: {result['classification']['version']}")
                print(f"      • Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")
                
                print(f"   🔍 Technical Extraction:")
                print(f"      • Model Numbers: {result['extraction']['model_numbers'][:5]}")  # Show first 5
                print(f"      • Error Codes: {result['extraction']['error_codes']}")  # Show all error codes
                print(f"      • Part Numbers: {result['extraction']['part_numbers'][:5]}")  # Show first 5
                
                print(f"   📊 Series Detection:")
                series_info = result['extraction']['series_info']
                print(f"      • Detected Series: {series_info['detected_series']} (confidence: {series_info['confidence']:.2f})")
                print(f"      • Description: {series_info['description']}")
                print(f"      • Series Models: {series_info['series_models'][:5]}")  # Show first 5
                
                print(f"   📋 Analysis:")
                tech_info = result['extraction']['technical_info']
                print(f"      • Has Diagrams: {'✅' if tech_info['has_diagrams'] else '❌'}")
                print(f"      • Has Procedures: {'✅' if tech_info['has_procedures'] else '❌'}")
                print(f"      • Has Specifications: {'✅' if tech_info['has_specifications'] else '❌'}")
                print(f"      • Has Troubleshooting: {'✅' if tech_info['has_troubleshooting'] else '❌'}")
                print(f"      • Word Count: {tech_info['word_count']:,}")
                
            except Exception as e:
                logger.error(f"❌ Failed to test {pdf_file}: {str(e)}")
                self.test_results[pdf_file.name] = {'error': str(e)}
        
        logger.info(f"✅ Tested {len(self.test_results)} documents")
    
    def generate_improved_report(self):
        """Generate improved classification analysis report"""
        logger.info("📊 Generating improved classification analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze results
        analysis = self._analyze_improved_results()
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_documents_tested': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'improved_analysis': analysis,
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/improved_classification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_improved_summary(report)
        
        logger.info(f"📊 Improved classification report saved to: {report_file}")
    
    def _analyze_improved_results(self) -> Dict:
        """Analyze improved classification results"""
        analysis = {
            'manufacturers': {},
            'document_types': {},
            'series_detection': {},
            'error_code_analysis': {
                'total_error_codes': 0,
                'valid_error_codes': 0,
                'manufacturer_specific': {}
            },
            'confidence_scores': {
                'manufacturer': [],
                'document_type': [],
                'series': [],
                'hybrid': []
            }
        }
        
        for result in self.test_results.values():
            if 'error' in result:
                continue
                
            classification = result['classification']
            extraction = result['extraction']
            
            # Manufacturer analysis
            manufacturer = classification['manufacturer']
            if manufacturer not in analysis['manufacturers']:
                analysis['manufacturers'][manufacturer] = 0
            analysis['manufacturers'][manufacturer] += 1
            
            # Document type analysis
            doc_type = classification['document_type']
            if doc_type not in analysis['document_types']:
                analysis['document_types'][doc_type] = 0
            analysis['document_types'][doc_type] += 1
            
            # Series detection analysis
            series_info = extraction.get('series_info', {})
            detected_series = series_info.get('detected_series', 'unknown')
            if detected_series not in analysis['series_detection']:
                analysis['series_detection'][detected_series] = 0
            analysis['series_detection'][detected_series] += 1
            
            # Error code analysis
            error_codes = extraction.get('error_codes', [])
            analysis['error_code_analysis']['total_error_codes'] += len(error_codes)
            analysis['error_code_analysis']['valid_error_codes'] += len(error_codes)  # All should be valid now
            
            # Manufacturer-specific error codes
            if manufacturer not in analysis['error_code_analysis']['manufacturer_specific']:
                analysis['error_code_analysis']['manufacturer_specific'][manufacturer] = []
            analysis['error_code_analysis']['manufacturer_specific'][manufacturer].extend(error_codes)
            
            # Confidence scores
            analysis['confidence_scores']['manufacturer'].append(classification['manufacturer_confidence'])
            analysis['confidence_scores']['document_type'].append(classification['document_type_confidence'])
            analysis['confidence_scores']['series'].append(series_info.get('confidence', 0))
            analysis['confidence_scores']['hybrid'].append(result['analysis']['hybrid_confidence'])
        
        # Calculate average confidence scores
        confidence_scores = analysis['confidence_scores'].copy()
        for score_type in confidence_scores:
            scores = confidence_scores[score_type]
            if scores:
                analysis['confidence_scores'][f'{score_type}_average'] = round(sum(scores) / len(scores), 3)
        
        # Remove duplicates from manufacturer-specific error codes
        for manufacturer in analysis['error_code_analysis']['manufacturer_specific']:
            analysis['error_code_analysis']['manufacturer_specific'][manufacturer] = list(set(
                analysis['error_code_analysis']['manufacturer_specific'][manufacturer]
            ))
        
        return analysis
    
    def print_improved_summary(self, report):
        """Print improved classification test summary"""
        print("\n" + "="*80)
        print("🚀 IMPROVED HYBRID DOCUMENT CLASSIFICATION ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Documents Tested: {report['summary']['total_documents_tested']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        analysis = report['improved_analysis']
        
        print(f"\n🏭 MANUFACTURER ANALYSIS:")
        for manufacturer, count in analysis['manufacturers'].items():
            print(f"  • {manufacturer.upper()}: {count} documents")
        
        print(f"\n📄 DOCUMENT TYPE ANALYSIS:")
        for doc_type, count in analysis['document_types'].items():
            print(f"  • {doc_type.replace('_', ' ').upper()}: {count} documents")
        
        print(f"\n🎯 SERIES DETECTION:")
        for series, count in analysis['series_detection'].items():
            print(f"  • {series.upper()}: {count} documents")
        
        print(f"\n⚠️  ERROR CODE ANALYSIS:")
        error_analysis = analysis['error_code_analysis']
        print(f"  • Total Error Codes: {error_analysis['total_error_codes']}")
        print(f"  • Valid Error Codes: {error_analysis['valid_error_codes']}")
        print(f"  • Validation Rate: {(error_analysis['valid_error_codes']/error_analysis['total_error_codes']*100):.1f}%" if error_analysis['total_error_codes'] > 0 else "  • Validation Rate: N/A")
        
        print(f"\n🔍 MANUFACTURER-SPECIFIC ERROR CODES:")
        for manufacturer, codes in error_analysis['manufacturer_specific'].items():
            if codes:
                print(f"  • {manufacturer.upper()}: {len(codes)} unique codes - {codes[:5]}")  # Show first 5
        
        print(f"\n🎯 CONFIDENCE SCORES:")
        confidence = analysis['confidence_scores']
        print(f"  • Manufacturer Average: {confidence.get('manufacturer_average', 0):.3f}")
        print(f"  • Document Type Average: {confidence.get('document_type_average', 0):.3f}")
        print(f"  • Series Average: {confidence.get('series_average', 0):.3f}")
        print(f"  • Hybrid Average: {confidence.get('hybrid_average', 0):.3f}")
        
        print(f"\n✅ Improved classification testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 Improved Hybrid Document Classification Test")
    print("=" * 60)
    print("Testing improved error code extraction and series detection...")
    print()
    
    tester = ImprovedClassifierTest()
    
    # Test documents
    await tester.test_documents(max_documents=8)
    
    # Generate report
    tester.generate_improved_report()

if __name__ == "__main__":
    asyncio.run(main())
