#!/usr/bin/env python3
"""
🧪 Comprehensive Test Runner
Tests all document types and generates comparison reports

Features:
- Tests multiple document types
- Compares chunking strategies
- Generates comprehensive reports
- Provides recommendations
"""

import asyncio
import sys
from pathlib import Path
import json
from datetime import datetime
import logging

# Import our test tools
from simple_document_analyzer import SimpleDocumentAnalyzer
from test_document_generator import TestDocumentGenerator

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ComprehensiveTestRunner:
    """Runs comprehensive tests on all document types"""
    
    def __init__(self):
        self.analyzer = SimpleDocumentAnalyzer()
        self.generator = TestDocumentGenerator()
        self.test_results = {}
        
    async def run_comprehensive_tests(self):
        """Run tests on all document types"""
        logger.info("🚀 Starting comprehensive document analysis...")
        
        # Generate test documents if they don't exist
        test_docs = [
            "HP_LaserJet_4000_Service_Manual.txt",
            "HP_LaserJet_4000_Parts_Catalog.txt", 
            "HP_X580_CPMD_Database.txt",
            "HP_TB_2024_001_Technical_Bulletin.txt",
            "Canon_imageRUNNER_4000i_Service_Manual.txt"
        ]
        
        # Check if test documents exist, generate if not
        for doc_name in test_docs:
            doc_path = Path("test_documents") / doc_name
            if not doc_path.exists():
                logger.info(f"📄 Generating missing test document: {doc_name}")
                if "Service_Manual" in doc_name and "HP" in doc_name:
                    self.generator.generate_hp_service_manual(doc_name)
                elif "Parts_Catalog" in doc_name:
                    self.generator.generate_parts_catalog(doc_name)
                elif "CPMD" in doc_name:
                    self.generator.generate_cpmd_database(doc_name)
                elif "Technical_Bulletin" in doc_name:
                    self.generator.generate_technical_bulletin(doc_name)
                elif "Canon" in doc_name:
                    self.generator.generate_canon_service_manual(doc_name)
        
        # Test each document type
        for doc_name in test_docs:
            doc_path = f"test_documents/{doc_name}"
            if Path(doc_path).exists():
                logger.info(f"🧪 Testing: {doc_name}")
                try:
                    result = await self.analyzer.analyze_document(doc_path)
                    self.test_results[doc_name] = result
                    
                    # Print quick summary
                    print(f"\n📄 {doc_name}")
                    print(f"   📝 Words: {result['text_analysis']['total_words']:,}")
                    print(f"   🏷️  Type: {result['document_type']['detected_type']} (confidence: {result['document_type']['confidence']:.2f})")
                    print(f"   🎯 Best Strategy: {result['recommendations']['best_strategy']}")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to analyze {doc_name}: {str(e)}")
                    self.test_results[doc_name] = {'error': str(e)}
        
        # Generate comprehensive report
        await self.generate_comprehensive_report()
        
        logger.info("✅ Comprehensive testing completed!")
    
    async def generate_comprehensive_report(self):
        """Generate comprehensive analysis report"""
        logger.info("📊 Generating comprehensive report...")
        
        # Analyze results by document type
        type_analysis = {}
        strategy_analysis = {}
        
        for doc_name, result in self.test_results.items():
            if 'error' in result:
                continue
                
            doc_type = result['document_type']['detected_type']
            best_strategy = result['recommendations']['best_strategy']
            
            # Group by document type
            if doc_type not in type_analysis:
                type_analysis[doc_type] = []
            type_analysis[doc_type].append({
                'document': doc_name,
                'words': result['text_analysis']['total_words'],
                'best_strategy': best_strategy,
                'chunk_count': result['chunking_results'][best_strategy]['chunk_count'],
                'avg_chunk_size': result['chunking_results'][best_strategy]['average_chunk_size']
            })
            
            # Group by strategy
            if best_strategy not in strategy_analysis:
                strategy_analysis[best_strategy] = []
            strategy_analysis[best_strategy].append({
                'document': doc_name,
                'doc_type': doc_type,
                'words': result['text_analysis']['total_words']
            })
        
        # Generate recommendations
        recommendations = self.generate_recommendations(type_analysis, strategy_analysis)
        
        # Create comprehensive report
        comprehensive_report = {
            'test_timestamp': datetime.utcnow().isoformat(),
            'total_documents_tested': len(self.test_results),
            'document_type_analysis': type_analysis,
            'strategy_analysis': strategy_analysis,
            'recommendations': recommendations,
            'individual_results': self.test_results
        }
        
        # Save report
        report_file = "analysis_reports/comprehensive_test_report.json"
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(comprehensive_report, f, indent=2, ensure_ascii=False)
        
        # Print summary
        self.print_comprehensive_summary(comprehensive_report)
        
        logger.info(f"📊 Comprehensive report saved to: {report_file}")
    
    def generate_recommendations(self, type_analysis, strategy_analysis):
        """Generate comprehensive recommendations"""
        recommendations = {
            'document_type_strategies': {},
            'optimal_chunk_sizes': {},
            'performance_insights': {},
            'production_config': {}
        }
        
        # Analyze by document type
        for doc_type, docs in type_analysis.items():
            if not docs:
                continue
                
            # Find most common strategy for this document type
            strategies = [doc['best_strategy'] for doc in docs]
            most_common_strategy = max(set(strategies), key=strategies.count)
            
            # Calculate average chunk size
            avg_chunk_size = sum(doc['avg_chunk_size'] for doc in docs) / len(docs)
            avg_chunk_count = sum(doc['chunk_count'] for doc in docs) / len(docs)
            
            recommendations['document_type_strategies'][doc_type] = {
                'recommended_strategy': most_common_strategy,
                'average_chunk_size': round(avg_chunk_size),
                'average_chunk_count': round(avg_chunk_count),
                'document_count': len(docs)
            }
            
            recommendations['optimal_chunk_sizes'][doc_type] = {
                'min_recommended': max(500, int(avg_chunk_size * 0.8)),
                'max_recommended': min(1500, int(avg_chunk_size * 1.2)),
                'target_size': round(avg_chunk_size)
            }
        
        # Generate production configuration
        recommendations['production_config'] = {
            'service_manual': {
                'strategy': recommendations['document_type_strategies'].get('service_manual', {}).get('recommended_strategy', 'sentence_based'),
                'chunk_size': recommendations['optimal_chunk_sizes'].get('service_manual', {}).get('target_size', 1000),
                'overlap': 100
            },
            'parts_catalog': {
                'strategy': recommendations['document_type_strategies'].get('parts_catalog', {}).get('recommended_strategy', 'structure_based'),
                'chunk_size': recommendations['optimal_chunk_sizes'].get('parts_catalog', {}).get('target_size', 800),
                'overlap': 50
            },
            'cpmd_database': {
                'strategy': recommendations['document_type_strategies'].get('cpmd_database', {}).get('recommended_strategy', 'paragraph_based'),
                'chunk_size': recommendations['optimal_chunk_sizes'].get('cpmd_database', {}).get('target_size', 900),
                'overlap': 75
            },
            'technical_bulletin': {
                'strategy': recommendations['document_type_strategies'].get('technical_bulletin', {}).get('recommended_strategy', 'paragraph_based'),
                'chunk_size': recommendations['optimal_chunk_sizes'].get('technical_bulletin', {}).get('target_size', 700),
                'overlap': 50
            }
        }
        
        # Performance insights
        total_docs = len([r for r in self.test_results.values() if 'error' not in r])
        successful_tests = total_docs
        recommendations['performance_insights'] = {
            'total_documents_tested': total_docs,
            'successful_tests': successful_tests,
            'success_rate': f"{(successful_tests/total_docs*100):.1f}%" if total_docs > 0 else "0%",
            'most_effective_strategy': max(strategy_analysis.keys(), key=lambda k: len(strategy_analysis[k])) if strategy_analysis else 'unknown',
            'average_document_size': sum(r['text_analysis']['total_words'] for r in self.test_results.values() if 'error' not in r) / total_docs if total_docs > 0 else 0
        }
        
        return recommendations
    
    def print_comprehensive_summary(self, report):
        """Print comprehensive test summary"""
        print("\n" + "="*80)
        print("🧪 COMPREHENSIVE DOCUMENT ANALYSIS SUMMARY")
        print("="*80)
        
        print(f"📊 Total Documents Tested: {report['total_documents_tested']}")
        print(f"⏰ Test Timestamp: {report['test_timestamp']}")
        
        print(f"\n📋 DOCUMENT TYPE ANALYSIS:")
        for doc_type, analysis in report['recommendations']['document_type_strategies'].items():
            print(f"  🏷️  {doc_type.upper()}:")
            print(f"     • Recommended Strategy: {analysis['recommended_strategy']}")
            print(f"     • Average Chunk Size: {analysis['average_chunk_size']} words")
            print(f"     • Average Chunks: {analysis['average_chunk_count']}")
            print(f"     • Documents Tested: {analysis['document_count']}")
        
        print(f"\n🎯 PRODUCTION CONFIGURATION:")
        for doc_type, config in report['recommendations']['production_config'].items():
            print(f"  📄 {doc_type.upper()}:")
            print(f"     • Strategy: {config['strategy']}")
            print(f"     • Chunk Size: {config['chunk_size']} words")
            print(f"     • Overlap: {config['overlap']} words")
        
        print(f"\n⚡ PERFORMANCE INSIGHTS:")
        insights = report['recommendations']['performance_insights']
        print(f"  📈 Success Rate: {insights['success_rate']}")
        print(f"  🏆 Most Effective Strategy: {insights['most_effective_strategy']}")
        print(f"  📊 Average Document Size: {insights['average_document_size']:.0f} words")
        
        print(f"\n✅ Comprehensive testing completed successfully!")

async def main():
    """Main function"""
    print("🧪 KRAI Comprehensive Document Testing")
    print("=" * 50)
    print("Testing multiple document types and chunking strategies...")
    print()
    
    runner = ComprehensiveTestRunner()
    await runner.run_comprehensive_tests()

if __name__ == "__main__":
    asyncio.run(main())
