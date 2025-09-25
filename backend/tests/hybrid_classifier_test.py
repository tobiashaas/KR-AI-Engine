#!/usr/bin/env python3
"""
🚀 Hybrid Document Classifier Test
Tests the hybrid approach on real documents

Features:
- Tests hybrid classification on real documents
- Extracts models, versions, and technical information
- Generates comprehensive analysis reports
- Compares with previous classification methods
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Dict

# Import our classifiers
from hybrid_document_classifier import HybridDocumentClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class HybridClassifierTest:
    """Test hybrid document classification on real documents"""
    
    def __init__(self):
        self.classifier = HybridDocumentClassifier()
        self.test_results = {}
        
    async def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Convert PDF to text using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            # Limit to first 8 pages for comprehensive analysis
            max_pages = min(8, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            return ""
    
    async def test_documents(self, max_documents: int = 12):
        """Test hybrid classification on real documents"""
        logger.info(f"🚀 Testing hybrid classification on {max_documents} documents...")
        
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
                
                # Hybrid classification
                result = self.classifier.classify_document(pdf_file.name, content)
                
                self.test_results[pdf_file.name] = result
                
                # Print detailed results
                print(f"\n📄 {pdf_file.name}")
                print(f"   🏷️  Classification:")
                print(f"      • Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
                print(f"      • Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
                print(f"      • Models: {result['classification']['models']}")
                print(f"      • Version: {result['classification']['version']}")
                print(f"      • Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")
                
                print(f"   🔍 Technical Extraction:")
                print(f"      • Model Numbers: {result['extraction']['model_numbers'][:5]}")  # Show first 5
                print(f"      • Error Codes: {result['extraction']['error_codes'][:5]}")  # Show first 5
                print(f"      • Part Numbers: {result['extraction']['part_numbers'][:5]}")  # Show first 5
                
                print(f"   📊 Analysis:")
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
    
    def generate_hybrid_report(self):
        """Generate comprehensive hybrid classification report"""
        logger.info("📊 Generating hybrid classification analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze classification results
        classification_stats = self._analyze_classification_results()
        extraction_stats = self._analyze_extraction_results()
        technical_stats = self._analyze_technical_content()
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_documents_tested': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'classification_analysis': classification_stats,
            'extraction_analysis': extraction_stats,
            'technical_analysis': technical_stats,
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/hybrid_classification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_hybrid_summary(report)
        
        logger.info(f"📊 Hybrid classification report saved to: {report_file}")
    
    def _analyze_classification_results(self) -> Dict:
        """Analyze classification accuracy and patterns"""
        stats = {
            'manufacturers': {},
            'document_types': {},
            'confidence_scores': {
                'manufacturer': [],
                'document_type': [],
                'hybrid': []
            },
            'version_detection': {
                'documents_with_versions': 0,
                'version_sources': {'filename': 0, 'content': 0, 'both': 0}
            }
        }
        
        for result in self.test_results.values():
            if 'error' in result:
                continue
                
            classification = result['classification']
            
            # Manufacturer analysis
            manufacturer = classification['manufacturer']
            if manufacturer not in stats['manufacturers']:
                stats['manufacturers'][manufacturer] = 0
            stats['manufacturers'][manufacturer] += 1
            
            # Document type analysis
            doc_type = classification['document_type']
            if doc_type not in stats['document_types']:
                stats['document_types'][doc_type] = 0
            stats['document_types'][doc_type] += 1
            
            # Confidence scores
            stats['confidence_scores']['manufacturer'].append(classification['manufacturer_confidence'])
            stats['confidence_scores']['document_type'].append(classification['document_type_confidence'])
            stats['confidence_scores']['hybrid'].append(result['analysis']['hybrid_confidence'])
            
            # Version detection analysis
            if classification['version']:
                stats['version_detection']['documents_with_versions'] += 1
                
                # Determine version source
                filename_version = result['analysis']['filename_analysis'].get('version', '')
                content_version = result['analysis']['content_analysis'].get('version', '')
                
                if filename_version and content_version:
                    stats['version_detection']['version_sources']['both'] += 1
                elif filename_version:
                    stats['version_detection']['version_sources']['filename'] += 1
                elif content_version:
                    stats['version_detection']['version_sources']['content'] += 1
        
        # Calculate average confidence scores
        confidence_scores = stats['confidence_scores'].copy()
        for score_type in confidence_scores:
            scores = confidence_scores[score_type]
            if scores:
                stats['confidence_scores'][f'{score_type}_average'] = round(sum(scores) / len(scores), 3)
        
        return stats
    
    def _analyze_extraction_results(self) -> Dict:
        """Analyze information extraction results"""
        stats = {
            'total_model_numbers': 0,
            'unique_model_numbers': set(),
            'total_error_codes': 0,
            'unique_error_codes': set(),
            'total_part_numbers': 0,
            'unique_part_numbers': set(),
            'extraction_success': {
                'models': 0,
                'error_codes': 0,
                'part_numbers': 0
            }
        }
        
        for result in self.test_results.values():
            if 'error' in result:
                continue
                
            extraction = result['extraction']
            
            # Model numbers
            models = extraction.get('model_numbers', [])
            stats['total_model_numbers'] += len(models)
            stats['unique_model_numbers'].update(models)
            if models:
                stats['extraction_success']['models'] += 1
            
            # Error codes
            error_codes = extraction.get('error_codes', [])
            stats['total_error_codes'] += len(error_codes)
            stats['unique_error_codes'].update(error_codes)
            if error_codes:
                stats['extraction_success']['error_codes'] += 1
            
            # Part numbers
            part_numbers = extraction.get('part_numbers', [])
            stats['total_part_numbers'] += len(part_numbers)
            stats['unique_part_numbers'].update(part_numbers)
            if part_numbers:
                stats['extraction_success']['part_numbers'] += 1
        
        # Convert sets to lists for JSON serialization
        stats['unique_model_numbers'] = list(stats['unique_model_numbers'])
        stats['unique_error_codes'] = list(stats['unique_error_codes'])
        stats['unique_part_numbers'] = list(stats['unique_part_numbers'])
        
        # Calculate success rates
        total_docs = len([r for r in self.test_results.values() if 'error' not in r])
        if total_docs > 0:
            stats['extraction_success_rate'] = {
                'models': f"{(stats['extraction_success']['models']/total_docs*100):.1f}%",
                'error_codes': f"{(stats['extraction_success']['error_codes']/total_docs*100):.1f}%",
                'part_numbers': f"{(stats['extraction_success']['part_numbers']/total_docs*100):.1f}%"
            }
        
        return stats
    
    def _analyze_technical_content(self) -> Dict:
        """Analyze technical content characteristics"""
        stats = {
            'content_characteristics': {
                'has_diagrams': 0,
                'has_procedures': 0,
                'has_specifications': 0,
                'has_troubleshooting': 0
            },
            'document_sizes': {
                'total_words': 0,
                'average_words': 0,
                'min_words': float('inf'),
                'max_words': 0
            },
            'page_indicators': 0
        }
        
        word_counts = []
        
        for result in self.test_results.values():
            if 'error' in result:
                continue
                
            tech_info = result['extraction'].get('technical_info', {})
            
            # Content characteristics
            for characteristic in stats['content_characteristics']:
                if tech_info.get(characteristic, False):
                    stats['content_characteristics'][characteristic] += 1
            
            # Document sizes
            word_count = tech_info.get('word_count', 0)
            stats['document_sizes']['total_words'] += word_count
            word_counts.append(word_count)
            stats['document_sizes']['min_words'] = min(stats['document_sizes']['min_words'], word_count)
            stats['document_sizes']['max_words'] = max(stats['document_sizes']['max_words'], word_count)
            
            # Page indicators
            stats['page_indicators'] += tech_info.get('page_indicators', 0)
        
        # Calculate averages
        if word_counts:
            stats['document_sizes']['average_words'] = round(sum(word_counts) / len(word_counts))
            stats['document_sizes']['min_words'] = stats['document_sizes']['min_words'] if stats['document_sizes']['min_words'] != float('inf') else 0
        
        # Calculate percentages
        total_docs = len([r for r in self.test_results.values() if 'error' not in r])
        if total_docs > 0:
            content_characteristics = stats['content_characteristics'].copy()
            for characteristic in content_characteristics:
                count = content_characteristics[characteristic]
                stats['content_characteristics'][f'{characteristic}_percentage'] = f"{(count/total_docs*100):.1f}%"
        
        return stats
    
    def print_hybrid_summary(self, report):
        """Print hybrid classification test summary"""
        print("\n" + "="*80)
        print("🚀 HYBRID DOCUMENT CLASSIFICATION ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Documents Tested: {report['summary']['total_documents_tested']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        print(f"\n🏭 MANUFACTURER ANALYSIS:")
        for manufacturer, count in report['classification_analysis']['manufacturers'].items():
            print(f"  • {manufacturer.upper()}: {count} documents")
        
        print(f"\n📄 DOCUMENT TYPE ANALYSIS:")
        for doc_type, count in report['classification_analysis']['document_types'].items():
            print(f"  • {doc_type.replace('_', ' ').upper()}: {count} documents")
        
        print(f"\n🎯 CONFIDENCE SCORES:")
        confidence = report['classification_analysis']['confidence_scores']
        print(f"  • Manufacturer Average: {confidence.get('manufacturer_average', 0):.3f}")
        print(f"  • Document Type Average: {confidence.get('document_type_average', 0):.3f}")
        print(f"  • Hybrid Average: {confidence.get('hybrid_average', 0):.3f}")
        
        print(f"\n🔍 INFORMATION EXTRACTION:")
        extraction = report['extraction_analysis']
        print(f"  • Unique Model Numbers: {len(extraction['unique_model_numbers'])}")
        print(f"  • Unique Error Codes: {len(extraction['unique_error_codes'])}")
        print(f"  • Unique Part Numbers: {len(extraction['unique_part_numbers'])}")
        
        if 'extraction_success_rate' in extraction:
            success_rate = extraction['extraction_success_rate']
            print(f"  • Model Extraction Success: {success_rate['models']}")
            print(f"  • Error Code Extraction Success: {success_rate['error_codes']}")
            print(f"  • Part Number Extraction Success: {success_rate['part_numbers']}")
        
        print(f"\n📋 VERSION DETECTION:")
        version_info = report['classification_analysis']['version_detection']
        print(f"  • Documents with Versions: {version_info['documents_with_versions']}")
        print(f"  • Version Sources: Filename: {version_info['version_sources']['filename']}, "
              f"Content: {version_info['version_sources']['content']}, "
              f"Both: {version_info['version_sources']['both']}")
        
        print(f"\n✅ Hybrid classification testing completed successfully!")

async def main():
    """Main function"""
    print("🚀 Hybrid Document Classification Test")
    print("=" * 60)
    print("Testing hybrid approach on real documents...")
    print("Extracting: Type, Manufacturer, Models, Version, Technical Info")
    print()
    
    tester = HybridClassifierTest()
    
    # Test documents
    await tester.test_documents(max_documents=12)
    
    # Generate report
    tester.generate_hybrid_report()

if __name__ == "__main__":
    asyncio.run(main())
