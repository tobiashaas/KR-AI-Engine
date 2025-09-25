#!/usr/bin/env python3
"""
🧪 Test JSON Config Classifier
Tests the JSON configuration-based classifier with real documents

Features:
- Tests JSON-based error code extraction
- Tests JSON-based part number extraction
- Tests JSON-based chunking strategy selection
- Generates detailed analysis with examples
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Dict

# Import our JSON config classifier
from json_config_classifier import JSONConfigClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONConfigClassifierTest:
    """Test JSON configuration-based document classification"""
    
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
    
    async def test_documents(self, max_documents: int = 6):
        """Test JSON config classification on real documents"""
        logger.info(f"🧪 Testing JSON config classification on {max_documents} documents...")
        
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
                
                # JSON config classification
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
                
                print(f"   🔍 Technical Extraction (JSON Config):")
                print(f"      • Model Numbers: {result['extraction']['model_numbers'][:5]}")  # Show first 5
                print(f"      • Error Codes: {len(result['extraction']['error_codes'])} found")
                for error in result['extraction']['error_codes'][:3]:  # Show first 3
                    print(f"        - {error['code']}: {error['description']} ({error['category']})")
                print(f"      • Part Numbers: {len(result['extraction']['part_numbers'])} found")
                for part in result['extraction']['part_numbers'][:3]:  # Show first 3
                    print(f"        - {part['part_number']}: {part['description']} ({part['category']})")
                
                print(f"   📊 Series Detection:")
                series_info = result['extraction']['series_info']
                print(f"      • Detected Series: {series_info['detected_series']} (confidence: {series_info['confidence']:.2f})")
                print(f"      • Description: {series_info['description']}")
                
                print(f"   🧩 Chunking Strategy (JSON Config):")
                chunking = result['chunking']
                print(f"      • Strategy: {chunking['recommended_strategy']}")
                print(f"      • Chunk Size: {chunking['chunk_size']}")
                print(f"      • Chunk Overlap: {chunking['chunk_overlap']}")
                
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
    
    def generate_json_config_report(self):
        """Generate JSON config classification analysis report"""
        logger.info("📊 Generating JSON config classification analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze results
        analysis = self._analyze_json_config_results()
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_documents_tested': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'json_config_analysis': analysis,
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/json_config_classification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_json_config_summary(report)
        
        logger.info(f"📊 JSON config classification report saved to: {report_file}")
    
    def _analyze_json_config_results(self) -> Dict:
        """Analyze JSON config classification results"""
        analysis = {
            'manufacturers': {},
            'document_types': {},
            'series_detection': {},
            'error_code_analysis': {
                'total_error_codes': 0,
                'unique_error_codes': set(),
                'manufacturer_specific': {},
                'categories': {}
            },
            'part_number_analysis': {
                'total_part_numbers': 0,
                'unique_part_numbers': set(),
                'manufacturer_specific': {},
                'categories': {}
            },
            'chunking_strategies': {},
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
            chunking = result['chunking']
            
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
            for error in error_codes:
                analysis['error_code_analysis']['unique_error_codes'].add(error['code'])
                category = error['category']
                if category not in analysis['error_code_analysis']['categories']:
                    analysis['error_code_analysis']['categories'][category] = 0
                analysis['error_code_analysis']['categories'][category] += 1
                
                # Manufacturer-specific error codes
                if manufacturer not in analysis['error_code_analysis']['manufacturer_specific']:
                    analysis['error_code_analysis']['manufacturer_specific'][manufacturer] = []
                analysis['error_code_analysis']['manufacturer_specific'][manufacturer].append({
                    'code': error['code'],
                    'description': error['description'],
                    'category': error['category']
                })
            
            # Part number analysis
            part_numbers = extraction.get('part_numbers', [])
            analysis['part_number_analysis']['total_part_numbers'] += len(part_numbers)
            for part in part_numbers:
                analysis['part_number_analysis']['unique_part_numbers'].add(part['part_number'])
                category = part['category']
                if category not in analysis['part_number_analysis']['categories']:
                    analysis['part_number_analysis']['categories'][category] = 0
                analysis['part_number_analysis']['categories'][category] += 1
                
                # Manufacturer-specific part numbers
                if manufacturer not in analysis['part_number_analysis']['manufacturer_specific']:
                    analysis['part_number_analysis']['manufacturer_specific'][manufacturer] = []
                analysis['part_number_analysis']['manufacturer_specific'][manufacturer].append({
                    'part_number': part['part_number'],
                    'description': part['description'],
                    'category': part['category'],
                    'models': part['models']
                })
            
            # Chunking strategy analysis
            strategy = chunking.get('recommended_strategy', 'unknown')
            if strategy not in analysis['chunking_strategies']:
                analysis['chunking_strategies'][strategy] = 0
            analysis['chunking_strategies'][strategy] += 1
            
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
        
        # Convert sets to lists for JSON serialization
        analysis['error_code_analysis']['unique_error_codes'] = list(analysis['error_code_analysis']['unique_error_codes'])
        analysis['part_number_analysis']['unique_part_numbers'] = list(analysis['part_number_analysis']['unique_part_numbers'])
        
        # Remove duplicates from manufacturer-specific data
        for manufacturer in analysis['error_code_analysis']['manufacturer_specific']:
            codes = analysis['error_code_analysis']['manufacturer_specific'][manufacturer]
            unique_codes = []
            seen_codes = set()
            for code in codes:
                if code['code'] not in seen_codes:
                    unique_codes.append(code)
                    seen_codes.add(code['code'])
            analysis['error_code_analysis']['manufacturer_specific'][manufacturer] = unique_codes
        
        for manufacturer in analysis['part_number_analysis']['manufacturer_specific']:
            parts = analysis['part_number_analysis']['manufacturer_specific'][manufacturer]
            unique_parts = []
            seen_parts = set()
            for part in parts:
                if part['part_number'] not in seen_parts:
                    unique_parts.append(part)
                    seen_parts.add(part['part_number'])
            analysis['part_number_analysis']['manufacturer_specific'][manufacturer] = unique_parts
        
        return analysis
    
    def print_json_config_summary(self, report):
        """Print JSON config classification test summary"""
        print("\n" + "="*80)
        print("🚀 JSON CONFIG DOCUMENT CLASSIFICATION ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Documents Tested: {report['summary']['total_documents_tested']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        analysis = report['json_config_analysis']
        
        print(f"\n🏭 MANUFACTURER ANALYSIS:")
        for manufacturer, count in analysis['manufacturers'].items():
            print(f"  • {manufacturer.upper()}: {count} documents")
        
        print(f"\n📄 DOCUMENT TYPE ANALYSIS:")
        for doc_type, count in analysis['document_types'].items():
            print(f"  • {doc_type.replace('_', ' ').upper()}: {count} documents")
        
        print(f"\n🎯 SERIES DETECTION:")
        for series, count in analysis['series_detection'].items():
            print(f"  • {series.upper()}: {count} documents")
        
        print(f"\n⚠️  ERROR CODE ANALYSIS (JSON Config):")
        error_analysis = analysis['error_code_analysis']
        print(f"  • Total Error Codes: {error_analysis['total_error_codes']}")
        print(f"  • Unique Error Codes: {len(error_analysis['unique_error_codes'])}")
        print(f"  • Categories: {list(error_analysis['categories'].keys())}")
        
        print(f"\n🔍 MANUFACTURER-SPECIFIC ERROR CODES:")
        for manufacturer, codes in error_analysis['manufacturer_specific'].items():
            if codes:
                print(f"  • {manufacturer.upper()}: {len(codes)} unique codes")
                for code in codes[:3]:  # Show first 3
                    print(f"    - {code['code']}: {code['description']} ({code['category']})")
        
        print(f"\n🔧 PART NUMBER ANALYSIS (JSON Config):")
        part_analysis = analysis['part_number_analysis']
        print(f"  • Total Part Numbers: {part_analysis['total_part_numbers']}")
        print(f"  • Unique Part Numbers: {len(part_analysis['unique_part_numbers'])}")
        print(f"  • Categories: {list(part_analysis['categories'].keys())}")
        
        print(f"\n🔍 MANUFACTURER-SPECIFIC PART NUMBERS:")
        for manufacturer, parts in part_analysis['manufacturer_specific'].items():
            if parts:
                print(f"  • {manufacturer.upper()}: {len(parts)} unique parts")
                for part in parts[:3]:  # Show first 3
                    print(f"    - {part['part_number']}: {part['description']} ({part['category']})")
        
        print(f"\n🧩 CHUNKING STRATEGIES:")
        for strategy, count in analysis['chunking_strategies'].items():
            print(f"  • {strategy.replace('_', ' ').upper()}: {count} documents")
        
        print(f"\n🎯 CONFIDENCE SCORES:")
        confidence = analysis['confidence_scores']
        print(f"  • Manufacturer Average: {confidence.get('manufacturer_average', 0):.3f}")
        print(f"  • Document Type Average: {confidence.get('document_type_average', 0):.3f}")
        print(f"  • Series Average: {confidence.get('series_average', 0):.3f}")
        print(f"  • Hybrid Average: {confidence.get('hybrid_average', 0):.3f}")
        
        print(f"\n✅ JSON config classification testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 JSON Config Document Classification Test")
    print("=" * 60)
    print("Testing JSON configuration-based classification...")
    print("Features: Error Codes, Part Numbers, Chunking Strategies")
    print()
    
    tester = JSONConfigClassifierTest()
    
    # Test documents
    await tester.test_documents(max_documents=6)
    
    # Generate report
    tester.generate_json_config_report()

if __name__ == "__main__":
    asyncio.run(main())
