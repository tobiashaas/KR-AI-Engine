#!/usr/bin/env python3
"""
🧠 Content-Based Document Classifier Test
Tests intelligent classification on real documents

Features:
- Tests content-based classification vs filename-based
- Compares accuracy and confidence
- Generates detailed analysis reports
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
from typing import Dict

# Import our classifiers
from intelligent_document_classifier import IntelligentDocumentClassifier

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ContentBasedClassifierTest:
    """Test content-based document classification"""
    
    def __init__(self):
        self.content_classifier = IntelligentDocumentClassifier()
        self.test_results = {}
        
    async def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Convert PDF to text using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            # Limit to first 5 pages for testing
            max_pages = min(5, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            return ""
    
    def filename_based_classification(self, filename: str) -> Dict:
        """Simple filename-based classification (for comparison)"""
        filename_lower = filename.lower()
        
        # Manufacturer detection
        manufacturer = 'unknown'
        if filename_lower.startswith('hp_'):
            manufacturer = 'hp'
        elif filename_lower.startswith('km_'):
            manufacturer = 'konica_minolta'
        elif filename_lower.startswith('lexmark_'):
            manufacturer = 'lexmark'
        elif filename_lower.startswith('utax_'):
            manufacturer = 'utax'
        elif filename_lower.startswith('canon_'):
            manufacturer = 'canon'
        
        # Document type detection
        doc_type = 'unknown'
        if 'sm' in filename_lower:
            doc_type = 'service_manual'
        elif 'cpmd' in filename_lower:
            doc_type = 'cpmd_database'
        elif 'troubleshooting' in filename_lower:
            doc_type = 'technical_bulletin'
        elif 'parts' in filename_lower or 'catalog' in filename_lower:
            doc_type = 'parts_catalog'
        elif 'technical' in filename_lower or 'bt' in filename_lower:
            doc_type = 'technical_bulletin'
        
        return {
            'manufacturer': manufacturer,
            'document_type': doc_type,
            'confidence': 1.0,  # Filename-based is always 100% confident
            'method': 'filename_based'
        }
    
    async def test_documents(self, max_documents: int = 10):
        """Test content-based classification on real documents"""
        logger.info(f"🧠 Testing content-based classification on {max_documents} documents...")
        
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
                
                # Content-based classification
                content_result = self.content_classifier.classify_document(content, pdf_file.name)
                
                # Filename-based classification (for comparison)
                filename_result = self.filename_based_classification(pdf_file.name)
                
                # Compare results
                comparison = {
                    'filename': pdf_file.name,
                    'content_based': content_result,
                    'filename_based': filename_result,
                    'comparison': {
                        'manufacturer_match': content_result['manufacturer'] == filename_result['manufacturer'],
                        'document_type_match': content_result['document_type'] == filename_result['document_type'],
                        'content_confidence': content_result['document_type_confidence'],
                        'filename_confidence': filename_result['confidence']
                    }
                }
                
                self.test_results[pdf_file.name] = comparison
                
                # Print quick results
                print(f"\n📄 {pdf_file.name}")
                print(f"   📝 Content Analysis:")
                print(f"      • Type: {content_result['document_type']} (confidence: {content_result['document_type_confidence']:.2f})")
                print(f"      • Manufacturer: {content_result['manufacturer']} (confidence: {content_result['manufacturer_confidence']:.2f})")
                print(f"      • Model Numbers: {content_result['model_numbers'][:3]}")  # Show first 3
                print(f"      • Error Codes: {content_result['error_codes'][:3]}")  # Show first 3
                print(f"      • Part Numbers: {content_result['part_numbers'][:3]}")  # Show first 3
                
                print(f"   📂 Filename Analysis:")
                print(f"      • Type: {filename_result['document_type']} (confidence: {filename_result['confidence']:.2f})")
                print(f"      • Manufacturer: {filename_result['manufacturer']}")
                
                print(f"   🔍 Comparison:")
                manufacturer_match = "✅" if comparison['comparison']['manufacturer_match'] else "❌"
                type_match = "✅" if comparison['comparison']['document_type_match'] else "❌"
                print(f"      • Manufacturer Match: {manufacturer_match}")
                print(f"      • Document Type Match: {type_match}")
                
            except Exception as e:
                logger.error(f"❌ Failed to test {pdf_file}: {str(e)}")
                self.test_results[pdf_file.name] = {'error': str(e)}
        
        logger.info(f"✅ Tested {len(self.test_results)} documents")
    
    def generate_classification_report(self):
        """Generate detailed classification report"""
        logger.info("📊 Generating classification analysis report...")
        
        # Calculate statistics
        total_tests = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        if successful_tests == 0:
            logger.warning("No successful tests to analyze")
            return
        
        # Analyze accuracy
        manufacturer_matches = sum(1 for r in self.test_results.values() 
                                 if 'comparison' in r and r['comparison']['manufacturer_match'])
        type_matches = sum(1 for r in self.test_results.values() 
                          if 'comparison' in r and r['comparison']['document_type_match'])
        
        # Analyze confidence scores
        content_confidences = [r['content_based']['document_type_confidence'] 
                             for r in self.test_results.values() 
                             if 'content_based' in r]
        avg_content_confidence = sum(content_confidences) / len(content_confidences) if content_confidences else 0
        
        # Analyze detected information
        all_model_numbers = []
        all_error_codes = []
        all_part_numbers = []
        
        for result in self.test_results.values():
            if 'content_based' in result:
                all_model_numbers.extend(result['content_based']['model_numbers'])
                all_error_codes.extend(result['content_based']['error_codes'])
                all_part_numbers.extend(result['content_based']['part_numbers'])
        
        # Generate report
        report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'summary': {
                'total_documents_tested': total_tests,
                'successful_tests': successful_tests,
                'success_rate': f"{(successful_tests/total_tests*100):.1f}%" if total_tests > 0 else "0%"
            },
            'accuracy_analysis': {
                'manufacturer_accuracy': f"{(manufacturer_matches/successful_tests*100):.1f}%" if successful_tests > 0 else "0%",
                'document_type_accuracy': f"{(type_matches/successful_tests*100):.1f}%" if successful_tests > 0 else "0%",
                'average_content_confidence': round(avg_content_confidence, 3)
            },
            'content_analysis': {
                'unique_model_numbers': len(set(all_model_numbers)),
                'unique_error_codes': len(set(all_error_codes)),
                'unique_part_numbers': len(set(all_part_numbers)),
                'total_model_numbers': len(all_model_numbers),
                'total_error_codes': len(all_error_codes),
                'total_part_numbers': len(all_part_numbers)
            },
            'detailed_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/content_based_classification_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_classification_summary(report)
        
        logger.info(f"📊 Classification report saved to: {report_file}")
    
    def print_classification_summary(self, report):
        """Print classification test summary"""
        print("\n" + "="*80)
        print("🧠 CONTENT-BASED CLASSIFICATION ANALYSIS")
        print("="*80)
        
        print(f"📊 Total Documents Tested: {report['summary']['total_documents_tested']}")
        print(f"✅ Successful Tests: {report['summary']['successful_tests']}")
        print(f"📈 Success Rate: {report['summary']['success_rate']}")
        
        print(f"\n🎯 ACCURACY ANALYSIS:")
        print(f"  🏭 Manufacturer Accuracy: {report['accuracy_analysis']['manufacturer_accuracy']}")
        print(f"  📄 Document Type Accuracy: {report['accuracy_analysis']['document_type_accuracy']}")
        print(f"  🧠 Average Content Confidence: {report['accuracy_analysis']['average_content_confidence']}")
        
        print(f"\n📋 CONTENT EXTRACTION:")
        print(f"  🔢 Unique Model Numbers: {report['content_analysis']['unique_model_numbers']}")
        print(f"  ⚠️  Unique Error Codes: {report['content_analysis']['unique_error_codes']}")
        print(f"  🔧 Unique Part Numbers: {report['content_analysis']['unique_part_numbers']}")
        
        print(f"\n✅ Content-based classification testing completed!")

async def main():
    """Main function"""
    print("🧠 Content-Based Document Classification Test")
    print("=" * 60)
    print("Testing intelligent content-based classification...")
    print()
    
    tester = ContentBasedClassifierTest()
    
    # Test documents
    await tester.test_documents(max_documents=8)
    
    # Generate report
    tester.generate_classification_report()

if __name__ == "__main__":
    asyncio.run(main())
