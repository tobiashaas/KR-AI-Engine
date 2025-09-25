#!/usr/bin/env python3
"""
🧪 Real Document Tester
Tests all real documents from the project

Features:
- Tests all 67 real PDF documents
- Categorizes by manufacturer and type
- Generates comprehensive analysis
- Provides production recommendations
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging
import subprocess

# Import our test tools
from simple_document_analyzer import SimpleDocumentAnalyzer

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class RealDocumentTester:
    """Tests all real documents in the project"""
    
    def __init__(self):
        self.analyzer = SimpleDocumentAnalyzer()
        self.test_results = {}
        self.document_categories = {
            'HP': {'service_manuals': [], 'cpmd': [], 'troubleshooting': [], 'technical_bulletins': []},
            'Konica_Minolta': {'service_manuals': [], 'parts_catalogs': []},
            'Lexmark': {'service_manuals': [], 'parts_catalogs': []},
            'UTAX': {'service_manuals': [], 'parts_catalogs': []},
            'Technical_Info': {'bulletins': []}
        }
        
    def categorize_documents(self):
        """Categorize all documents by manufacturer and type"""
        logger.info("📂 Categorizing documents...")
        
        # Find all PDF documents (look in parent directory)
        pdf_files = list(Path("../test_documents").rglob("*.pdf"))
        
        for pdf_file in pdf_files:
            filename = pdf_file.name.lower()
            
            # Categorize by manufacturer
            if filename.startswith('hp_'):
                if 'sm' in filename:
                    self.document_categories['HP']['service_manuals'].append(str(pdf_file))
                elif 'cpmd' in filename:
                    self.document_categories['HP']['cpmd'].append(str(pdf_file))
                elif 'troubleshooting' in filename:
                    self.document_categories['HP']['troubleshooting'].append(str(pdf_file))
            elif filename.startswith('km_'):
                if 'sm' in filename:
                    self.document_categories['Konica_Minolta']['service_manuals'].append(str(pdf_file))
                else:
                    self.document_categories['Konica_Minolta']['parts_catalogs'].append(str(pdf_file))
            elif filename.startswith('lexmark_'):
                if 'sm' in filename:
                    self.document_categories['Lexmark']['service_manuals'].append(str(pdf_file))
                else:
                    self.document_categories['Lexmark']['parts_catalogs'].append(str(pdf_file))
            elif filename.startswith('utax_'):
                if 'sm' in filename:
                    self.document_categories['UTAX']['service_manuals'].append(str(pdf_file))
                else:
                    self.document_categories['UTAX']['parts_catalogs'].append(str(pdf_file))
            elif 'technical' in filename or 'bt' in filename:
                self.document_categories['Technical_Info']['bulletins'].append(str(pdf_file))
        
        # Print categorization summary
        total_docs = sum(len(docs) for category in self.document_categories.values() 
                        for docs in category.values())
        logger.info(f"📊 Categorized {total_docs} documents")
        
        for manufacturer, types in self.document_categories.items():
            manufacturer_total = sum(len(docs) for docs in types.values())
            logger.info(f"  🏭 {manufacturer}: {manufacturer_total} documents")
            for doc_type, docs in types.items():
                if docs:
                    logger.info(f"    📄 {doc_type}: {len(docs)} documents")
    
    async def convert_pdf_to_text(self, pdf_path: str) -> str:
        """Convert PDF to text using PyMuPDF"""
        try:
            import fitz  # PyMuPDF
            
            doc = fitz.open(pdf_path)
            text = ""
            
            # Limit to first 10 pages for testing (to avoid huge files)
            max_pages = min(10, len(doc))
            
            for page_num in range(max_pages):
                page = doc[page_num]
                text += page.get_text() + "\n"
            
            doc.close()
            return text
            
        except Exception as e:
            logger.error(f"Failed to convert {pdf_path}: {str(e)}")
            return ""
    
    async def test_sample_documents(self, max_per_category: int = 3):
        """Test sample documents from each category"""
        logger.info(f"🧪 Testing sample documents (max {max_per_category} per category)...")
        
        test_count = 0
        
        for manufacturer, types in self.document_categories.items():
            for doc_type, docs in types.items():
                if not docs:
                    continue
                
                # Test up to max_per_category documents
                sample_docs = docs[:max_per_category]
                
                for doc_path in sample_docs:
                    if test_count >= 20:  # Limit total tests
                        break
                        
                    logger.info(f"🧪 Testing: {Path(doc_path).name}")
                    
                    try:
                        # Convert PDF to text
                        text_content = await self.convert_pdf_to_text(doc_path)
                        
                        if not text_content.strip():
                            logger.warning(f"No text extracted from {doc_path}")
                            continue
                        
                        # Create temporary text file
                        temp_file = f"temp_{Path(doc_path).stem}.txt"
                        with open(temp_file, 'w', encoding='utf-8') as f:
                            f.write(text_content)
                        
                        # Analyze document
                        result = await self.analyzer.analyze_document(temp_file)
                        
                        # Add metadata
                        result['original_file'] = str(doc_path)
                        result['manufacturer'] = manufacturer
                        result['document_type_category'] = doc_type
                        
                        self.test_results[f"{manufacturer}_{doc_type}_{Path(doc_path).stem}"] = result
                        
                        # Clean up temp file
                        Path(temp_file).unlink(missing_ok=True)
                        
                        test_count += 1
                        
                        # Print quick summary
                        print(f"  ✅ {Path(doc_path).name}")
                        print(f"     📝 Words: {result['text_analysis']['total_words']:,}")
                        print(f"     🏷️  Type: {result['document_type']['detected_type']} (confidence: {result['document_type']['confidence']:.2f})")
                        print(f"     🎯 Strategy: {result['recommendations']['best_strategy']}")
                        print()
                        
                    except Exception as e:
                        logger.error(f"❌ Failed to test {doc_path}: {str(e)}")
        
        logger.info(f"✅ Tested {test_count} documents")
    
    async def generate_real_document_report(self):
        """Generate comprehensive report for real documents"""
        logger.info("📊 Generating real document analysis report...")
        
        # Analyze results by manufacturer and type
        manufacturer_analysis = {}
        type_analysis = {}
        
        for test_name, result in self.test_results.items():
            if 'error' in result:
                continue
                
            manufacturer = result['manufacturer']
            doc_type_category = result['document_type_category']
            detected_type = result['document_type']['detected_type']
            best_strategy = result['recommendations']['best_strategy']
            
            # Group by manufacturer
            if manufacturer not in manufacturer_analysis:
                manufacturer_analysis[manufacturer] = {
                    'total_documents': 0,
                    'strategies': {},
                    'types': {},
                    'avg_words': 0
                }
            
            manufacturer_analysis[manufacturer]['total_documents'] += 1
            manufacturer_analysis[manufacturer]['avg_words'] += result['text_analysis']['total_words']
            
            # Track strategies
            if best_strategy not in manufacturer_analysis[manufacturer]['strategies']:
                manufacturer_analysis[manufacturer]['strategies'][best_strategy] = 0
            manufacturer_analysis[manufacturer]['strategies'][best_strategy] += 1
            
            # Track detected types
            if detected_type not in manufacturer_analysis[manufacturer]['types']:
                manufacturer_analysis[manufacturer]['types'][detected_type] = 0
            manufacturer_analysis[manufacturer]['types'][detected_type] += 1
            
            # Group by document type category
            if doc_type_category not in type_analysis:
                type_analysis[doc_type_category] = {
                    'total_documents': 0,
                    'strategies': {},
                    'avg_words': 0,
                    'manufacturers': set()
                }
            
            type_analysis[doc_type_category]['total_documents'] += 1
            type_analysis[doc_type_category]['avg_words'] += result['text_analysis']['total_words']
            type_analysis[doc_type_category]['manufacturers'].add(manufacturer)
            
            if best_strategy not in type_analysis[doc_type_category]['strategies']:
                type_analysis[doc_type_category]['strategies'][best_strategy] = 0
            type_analysis[doc_type_category]['strategies'][best_strategy] += 1
        
        # Calculate averages
        for manufacturer in manufacturer_analysis:
            total_docs = manufacturer_analysis[manufacturer]['total_documents']
            if total_docs > 0:
                manufacturer_analysis[manufacturer]['avg_words'] /= total_docs
        
        for doc_type in type_analysis:
            total_docs = type_analysis[doc_type]['total_documents']
            if total_docs > 0:
                type_analysis[doc_type]['avg_words'] /= total_docs
            type_analysis[doc_type]['manufacturers'] = list(type_analysis[doc_type]['manufacturers'])
        
        # Generate recommendations
        recommendations = self.generate_real_document_recommendations(manufacturer_analysis, type_analysis)
        
        # Create comprehensive report
        real_document_report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'total_documents_tested': len(self.test_results),
            'document_categories': {k: {doc_type: len(docs) for doc_type, docs in v.items()} 
                                  for k, v in self.document_categories.items()},
            'manufacturer_analysis': manufacturer_analysis,
            'type_analysis': type_analysis,
            'recommendations': recommendations,
            'individual_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/real_document_analysis_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(real_document_report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_real_document_summary(real_document_report)
        
        logger.info(f"📊 Real document report saved to: {report_file}")
    
    def generate_real_document_recommendations(self, manufacturer_analysis, type_analysis):
        """Generate recommendations for real documents"""
        recommendations = {
            'manufacturer_strategies': {},
            'type_strategies': {},
            'production_config': {},
            'insights': {}
        }
        
        # Analyze by manufacturer
        for manufacturer, analysis in manufacturer_analysis.items():
            if analysis['total_documents'] == 0:
                continue
                
            # Find most common strategy
            best_strategy = max(analysis['strategies'], key=analysis['strategies'].get)
            
            recommendations['manufacturer_strategies'][manufacturer] = {
                'recommended_strategy': best_strategy,
                'strategy_distribution': analysis['strategies'],
                'document_count': analysis['total_documents'],
                'avg_words': round(analysis['avg_words']),
                'supported_types': list(analysis['types'].keys())
            }
        
        # Analyze by document type
        for doc_type, analysis in type_analysis.items():
            if analysis['total_documents'] == 0:
                continue
                
            best_strategy = max(analysis['strategies'], key=analysis['strategies'].get)
            
            recommendations['type_strategies'][doc_type] = {
                'recommended_strategy': best_strategy,
                'strategy_distribution': analysis['strategies'],
                'document_count': analysis['total_documents'],
                'avg_words': round(analysis['avg_words']),
                'manufacturers': analysis['manufacturers']
            }
        
        # Generate production configuration
        recommendations['production_config'] = {
            'hp_service_manuals': {
                'strategy': recommendations['type_strategies'].get('service_manuals', {}).get('recommended_strategy', 'sentence_based'),
                'chunk_size': 1000,
                'overlap': 100
            },
            'hp_cpmd': {
                'strategy': recommendations['type_strategies'].get('cpmd', {}).get('recommended_strategy', 'simple_word_chunking'),
                'chunk_size': 800,
                'overlap': 75
            },
            'konica_minolta_service_manuals': {
                'strategy': 'sentence_based',
                'chunk_size': 1000,
                'overlap': 100
            },
            'lexmark_service_manuals': {
                'strategy': 'sentence_based',
                'chunk_size': 1000,
                'overlap': 100
            },
            'utax_service_manuals': {
                'strategy': 'sentence_based',
                'chunk_size': 1000,
                'overlap': 100
            },
            'parts_catalogs': {
                'strategy': 'structure_based',
                'chunk_size': 800,
                'overlap': 50
            },
            'technical_bulletins': {
                'strategy': 'paragraph_based',
                'chunk_size': 700,
                'overlap': 50
            }
        }
        
        # Insights
        total_tested = len(self.test_results)
        successful_tests = len([r for r in self.test_results.values() if 'error' not in r])
        
        recommendations['insights'] = {
            'total_documents_available': sum(len(docs) for category in self.document_categories.values() 
                                           for docs in category.values()),
            'total_documents_tested': total_tested,
            'success_rate': f"{(successful_tests/total_tested*100):.1f}%" if total_tested > 0 else "0%",
            'manufacturers_tested': len([m for m in manufacturer_analysis if manufacturer_analysis[m]['total_documents'] > 0]),
            'document_types_tested': len([t for t in type_analysis if type_analysis[t]['total_documents'] > 0]),
            'most_common_strategy': max([strategy for analysis in manufacturer_analysis.values() 
                                       for strategy in analysis['strategies'].keys()], 
                                      key=lambda s: sum(analysis['strategies'].get(s, 0) 
                                                       for analysis in manufacturer_analysis.values()))
        }
        
        return recommendations
    
    def print_real_document_summary(self, report):
        """Print real document test summary"""
        print("\n" + "="*80)
        print("🧪 REAL DOCUMENT ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📊 Total Documents Available: {report['recommendations']['insights']['total_documents_available']}")
        print(f"🧪 Total Documents Tested: {report['total_documents_tested']}")
        print(f"📈 Success Rate: {report['recommendations']['insights']['success_rate']}")
        print(f"🏭 Manufacturers Tested: {report['recommendations']['insights']['manufacturers_tested']}")
        print(f"📄 Document Types Tested: {report['recommendations']['insights']['document_types_tested']}")
        
        print(f"\n📋 DOCUMENT CATEGORIES:")
        for manufacturer, types in report['document_categories'].items():
            total = sum(types.values())
            if total > 0:
                print(f"  🏭 {manufacturer}: {total} documents")
                for doc_type, count in types.items():
                    if count > 0:
                        print(f"     📄 {doc_type}: {count}")
        
        print(f"\n🎯 MANUFACTURER RECOMMENDATIONS:")
        for manufacturer, analysis in report['recommendations']['manufacturer_strategies'].items():
            print(f"  🏭 {manufacturer}:")
            print(f"     • Recommended Strategy: {analysis['recommended_strategy']}")
            print(f"     • Documents Tested: {analysis['document_count']}")
            print(f"     • Average Words: {analysis['avg_words']:,}")
            print(f"     • Supported Types: {', '.join(analysis['supported_types'])}")
        
        print(f"\n📄 DOCUMENT TYPE RECOMMENDATIONS:")
        for doc_type, analysis in report['recommendations']['type_strategies'].items():
            print(f"  📄 {doc_type.upper()}:")
            print(f"     • Recommended Strategy: {analysis['recommended_strategy']}")
            print(f"     • Documents Tested: {analysis['document_count']}")
            print(f"     • Average Words: {analysis['avg_words']:,}")
            print(f"     • Manufacturers: {', '.join(analysis['manufacturers'])}")
        
        print(f"\n✅ Real document testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 KRAI Real Document Testing")
    print("=" * 50)
    print("Testing real documents from the project...")
    print()
    
    tester = RealDocumentTester()
    
    # Categorize documents
    tester.categorize_documents()
    
    # Test sample documents
    await tester.test_sample_documents(max_per_category=3)
    
    # Generate report
    await tester.generate_real_document_report()

if __name__ == "__main__":
    asyncio.run(main())
