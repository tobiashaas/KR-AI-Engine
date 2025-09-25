#!/usr/bin/env python3
"""
🧪 Simple Document Analyzer - No External Dependencies
Basic document analysis for testing chunking strategies

Features:
- Text file analysis
- Simple chunking strategies
- Document type detection
- Basic recommendations
"""

import asyncio
import os
import sys
from pathlib import Path
from typing import List, Dict, Any, Optional
import logging
from datetime import datetime
import json
import re
from collections import Counter

# Configuration
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SimpleDocumentAnalyzer:
    """Simple document analysis without external dependencies"""
    
    def __init__(self):
        self.supported_formats = {
            '.txt': 'text',
            '.md': 'markdown'
        }
        
        # Chunking strategies to test
        self.chunking_strategies = {
            'simple_word_chunking': self._simple_word_chunking,
            'sentence_based': self._sentence_based_chunking,
            'paragraph_based': self._paragraph_based_chunking,
            'structure_based': self._structure_based_chunking
        }
    
    async def analyze_document(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive document analysis"""
        try:
            file_path = Path(file_path)
            
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Basic file info
            file_info = {
                'filename': file_path.name,
                'size_mb': file_path.stat().st_size / (1024 * 1024),
                'extension': file_path.suffix.lower(),
                'created_at': datetime.fromtimestamp(file_path.stat().st_ctime).isoformat()
            }
            
            logger.info(f"📄 Analyzing: {file_info['filename']} ({file_info['size_mb']:.2f} MB)")
            
            # Extract text
            text_data = await self._extract_text_file(file_path)
            
            # Analyze text structure
            structure_analysis = self._analyze_text_structure(text_data['text'])
            
            # Test different chunking strategies
            chunking_results = {}
            for strategy_name, strategy_func in self.chunking_strategies.items():
                logger.info(f"🧪 Testing chunking strategy: {strategy_name}")
                chunks = strategy_func(text_data['text'])
                chunking_results[strategy_name] = self._analyze_chunks(chunks)
            
            # Document type detection
            doc_type = self._detect_document_type(text_data['text'], file_info['filename'])
            
            # Generate analysis report
            analysis_report = {
                'file_info': file_info,
                'text_analysis': {
                    'total_characters': len(text_data['text']),
                    'total_words': len(text_data['text'].split()),
                    'total_sentences': len(self._simple_sent_tokenize(text_data['text'])),
                    'total_paragraphs': len([p for p in text_data['text'].split('\n\n') if p.strip()])
                },
                'structure_analysis': structure_analysis,
                'chunking_results': chunking_results,
                'document_type': doc_type,
                'recommendations': self._generate_recommendations(chunking_results, structure_analysis),
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("✅ Document analysis completed!")
            return analysis_report
            
        except Exception as e:
            logger.error(f"❌ Document analysis failed: {str(e)}")
            raise
    
    async def _extract_text_file(self, file_path: Path) -> Dict[str, Any]:
        """Extract text from plain text file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text_content = f.read()
            
            return {
                'text': text_content.strip(),
                'total_pages': 1,
                'total_images': 0,
                'total_tables': 0,
                'page_data': [{'page_number': 1, 'text_length': len(text_content)}],
                'extraction_method': 'text_file'
            }
            
        except Exception as e:
            logger.error(f"Text file extraction failed: {str(e)}")
            raise
    
    def _simple_sent_tokenize(self, text: str) -> List[str]:
        """Simple sentence tokenization"""
        sentences = re.split(r'[.!?]+', text)
        return [s.strip() for s in sentences if s.strip()]
    
    def _analyze_text_structure(self, text: str) -> Dict[str, Any]:
        """Analyze text structure and patterns"""
        try:
            # Split into paragraphs
            paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
            
            # Analyze headings and structure
            headings = []
            for paragraph in paragraphs:
                # Simple heading detection (lines that are short and might be titles)
                if len(paragraph) < 100 and len(paragraph.split('\n')) == 1:
                    headings.append(paragraph)
            
            # Analyze sentence length distribution
            sentences = self._simple_sent_tokenize(text)
            sentence_lengths = [len(s.split()) for s in sentences]
            
            # Analyze word frequency
            words = re.findall(r'\b\w+\b', text.lower())
            word_freq = Counter(words)
            common_words = word_freq.most_common(20)
            
            # Detect technical terms
            technical_terms = []
            stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}
            for word, freq in word_freq.items():
                if (freq > 5 and 
                    len(word) > 4 and 
                    word.isalpha() and 
                    word not in stop_words):
                    technical_terms.append((word, freq))
            
            return {
                'paragraph_count': len(paragraphs),
                'sentence_count': len(sentences),
                'average_sentence_length': sum(sentence_lengths) / len(sentence_lengths) if sentence_lengths else 0,
                'max_sentence_length': max(sentence_lengths) if sentence_lengths else 0,
                'heading_count': len(headings),
                'headings': headings[:10],  # First 10 headings
                'common_words': common_words,
                'technical_terms': technical_terms[:20],
                'text_density': len(text.split()) / len(paragraphs) if paragraphs else 0
            }
            
        except Exception as e:
            logger.error(f"Structure analysis failed: {str(e)}")
            return {}
    
    def _simple_word_chunking(self, text: str, chunk_size: int = 1000, overlap: int = 200) -> List[str]:
        """Simple word-based chunking"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunk = " ".join(chunk_words)
            if len(chunk.strip()) > 50:
                chunks.append(chunk.strip())
        
        return chunks
    
    def _sentence_based_chunking(self, text: str, target_words: int = 1000) -> List[str]:
        """Sentence-aware chunking"""
        sentences = self._simple_sent_tokenize(text)
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for sentence in sentences:
            sentence_words = len(sentence.split())
            
            if current_word_count + sentence_words > target_words and current_chunk:
                chunks.append(" ".join(current_chunk))
                current_chunk = [sentence]
                current_word_count = sentence_words
            else:
                current_chunk.append(sentence)
                current_word_count += sentence_words
        
        if current_chunk:
            chunks.append(" ".join(current_chunk))
        
        return chunks
    
    def _paragraph_based_chunking(self, text: str, target_words: int = 1000) -> List[str]:
        """Paragraph-aware chunking"""
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip()]
        chunks = []
        current_chunk = []
        current_word_count = 0
        
        for paragraph in paragraphs:
            paragraph_words = len(paragraph.split())
            
            if current_word_count + paragraph_words > target_words and current_chunk:
                chunks.append("\n\n".join(current_chunk))
                current_chunk = [paragraph]
                current_word_count = paragraph_words
            else:
                current_chunk.append(paragraph)
                current_word_count += paragraph_words
        
        if current_chunk:
            chunks.append("\n\n".join(current_chunk))
        
        return chunks
    
    def _structure_based_chunking(self, text: str) -> List[str]:
        """Structure-aware chunking (chapters, sections, etc.)"""
        # Split by common document structure markers
        structure_patterns = [
            r'\n\s*Chapter\s+\d+',
            r'\n\s*Section\s+\d+',
            r'\n\s*\d+\.\s+[A-Z]',
            r'\n\s*[A-Z][A-Z\s]{10,}:\s*$',  # Headings in caps
            r'\n\s*[A-Z][a-z]+.*:\s*$'        # Headings with colon
        ]
        
        chunks = []
        current_chunk = ""
        
        lines = text.split('\n')
        for line in lines:
            # Check if line matches structure pattern
            is_structure_break = any(re.match(pattern, '\n' + line) for pattern in structure_patterns)
            
            if is_structure_break and current_chunk.strip():
                chunks.append(current_chunk.strip())
                current_chunk = line + '\n'
            else:
                current_chunk += line + '\n'
        
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        return chunks
    
    def _analyze_chunks(self, chunks: List[str]) -> Dict[str, Any]:
        """Analyze chunking results"""
        if not chunks:
            return {'chunk_count': 0}
        
        chunk_lengths = [len(chunk.split()) for chunk in chunks]
        
        return {
            'chunk_count': len(chunks),
            'average_chunk_size': sum(chunk_lengths) / len(chunk_lengths),
            'min_chunk_size': min(chunk_lengths),
            'max_chunk_size': max(chunk_lengths),
            'chunk_size_distribution': {
                'small_chunks': len([c for c in chunk_lengths if c < 500]),
                'medium_chunks': len([c for c in chunk_lengths if 500 <= c < 1500]),
                'large_chunks': len([c for c in chunk_lengths if c >= 1500])
            }
        }
    
    def _detect_document_type(self, text: str, filename: str) -> Dict[str, Any]:
        """Detect document type based on content and filename"""
        text_lower = text.lower()
        filename_lower = filename.lower()
        
        # Service Manual indicators
        service_manual_indicators = [
            'service manual', 'maintenance manual', 'repair manual',
            'chapter', 'section', 'procedure', 'troubleshooting',
            'disassembly', 'assembly', 'calibration'
        ]
        
        # Parts Catalog indicators
        parts_catalog_indicators = [
            'parts catalog', 'parts list', 'spare parts',
            'part number', 'quantity', 'price', 'supplier'
        ]
        
        # Technical Bulletin indicators
        bulletin_indicators = [
            'bulletin', 'notice', 'field notice', 'service bulletin',
            'tb-', 'update', 'revision', 'important'
        ]
        
        # CPMD indicators (HP specific)
        cpmd_indicators = [
            'cpmd', 'customer parts', 'maintenance data',
            'hp', 'hewlett packard'
        ]
        
        scores = {
            'service_manual': sum(1 for indicator in service_manual_indicators if indicator in text_lower),
            'parts_catalog': sum(1 for indicator in parts_catalog_indicators if indicator in text_lower),
            'technical_bulletin': sum(1 for indicator in bulletin_indicators if indicator in text_lower),
            'cpmd_database': sum(1 for indicator in cpmd_indicators if indicator in text_lower)
        }
        
        # Filename-based detection
        if 'service' in filename_lower and 'manual' in filename_lower:
            scores['service_manual'] += 3
        elif 'parts' in filename_lower and 'catalog' in filename_lower:
            scores['parts_catalog'] += 3
        elif 'bulletin' in filename_lower or 'tb-' in filename_lower:
            scores['technical_bulletin'] += 3
        elif 'cpmd' in filename_lower:
            scores['cpmd_database'] += 3
        
        detected_type = max(scores, key=scores.get)
        confidence = scores[detected_type] / sum(scores.values()) if sum(scores.values()) > 0 else 0
        
        return {
            'detected_type': detected_type,
            'confidence': confidence,
            'all_scores': scores
        }
    
    def _generate_recommendations(self, chunking_results: Dict, structure_analysis: Dict) -> Dict[str, Any]:
        """Generate recommendations for optimal chunking strategy"""
        recommendations = {
            'best_strategy': None,
            'optimal_chunk_size': 1000,
            'reasoning': []
        }
        
        # Analyze chunking results
        best_strategy = None
        best_score = 0
        
        for strategy, results in chunking_results.items():
            if results['chunk_count'] == 0:
                continue
            
            # Score based on chunk size distribution
            score = 0
            
            # Prefer strategies with good chunk size distribution
            if results['average_chunk_size'] > 500 and results['average_chunk_size'] < 1500:
                score += 2
            
            # Prefer strategies with reasonable chunk count
            if 10 < results['chunk_count'] < 100:
                score += 1
            
            # Prefer strategies with low variance
            if results['max_chunk_size'] - results['min_chunk_size'] < results['average_chunk_size'] * 0.5:
                score += 1
            
            if score > best_score:
                best_score = score
                best_strategy = strategy
        
        recommendations['best_strategy'] = best_strategy
        recommendations['reasoning'] = [
            f"Strategy '{best_strategy}' provides optimal chunk distribution",
            f"Average chunk size: {chunking_results[best_strategy]['average_chunk_size']:.0f} words",
            f"Total chunks: {chunking_results[best_strategy]['chunk_count']}"
        ]
        
        return recommendations
    
    def save_analysis_report(self, report: Dict[str, Any], output_path: str):
        """Save analysis report to JSON file"""
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            
            logger.info(f"📊 Analysis report saved to: {output_path}")
            
        except Exception as e:
            logger.error(f"Failed to save report: {str(e)}")
            raise

async def main():
    """Main function for testing"""
    if len(sys.argv) != 2:
        print("Usage: python simple_document_analyzer.py <document_path>")
        print("Example: python simple_document_analyzer.py test_documents/sample_manual.txt")
        sys.exit(1)
    
    document_path = sys.argv[1]
    
    analyzer = SimpleDocumentAnalyzer()
    
    try:
        # Analyze document
        report = await analyzer.analyze_document(document_path)
        
        # Print summary
        print("\n" + "="*60)
        print("📄 DOCUMENT ANALYSIS SUMMARY")
        print("="*60)
        
        print(f"📁 File: {report['file_info']['filename']}")
        print(f"📏 Size: {report['file_info']['size_mb']:.2f} MB")
        print(f"📝 Words: {report['text_analysis']['total_words']:,}")
        print(f"📄 Paragraphs: {report['text_analysis']['total_paragraphs']}")
        print(f"🏷️  Type: {report['document_type']['detected_type']} (confidence: {report['document_type']['confidence']:.2f})")
        
        print(f"\n🧪 CHUNKING STRATEGIES TESTED:")
        for strategy, results in report['chunking_results'].items():
            if results['chunk_count'] > 0:
                print(f"  • {strategy}: {results['chunk_count']} chunks, avg {results['average_chunk_size']:.0f} words")
        
        print(f"\n🎯 RECOMMENDATION:")
        print(f"  Best strategy: {report['recommendations']['best_strategy']}")
        for reason in report['recommendations']['reasoning']:
            print(f"  • {reason}")
        
        # Save detailed report
        output_file = f"analysis_reports/analysis_{Path(document_path).stem}.json"
        analyzer.save_analysis_report(report, output_file)
        
        print(f"\n📊 Detailed report saved to: {output_file}")
        
    except Exception as e:
        logger.error(f"Analysis failed: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
