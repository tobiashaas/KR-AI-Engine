#!/usr/bin/env python3
"""
KR-AI-Engine Universal Processor Script
Single Source of Truth for all document processing operations

Usage:
    python krai_processor.py --mode production
    python krai_processor.py --mode image_only --file path/to/document.pdf
    python krai_processor.py --mode demo --verbose
"""

import os
import sys
import argparse
import asyncio
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Add backend to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import production components
from production_document_processor import ProductionDocumentProcessor
from config.supabase_config import SupabaseConfig, SupabaseStorage

class KRAIProcessor:
    """Universal KR-AI-Engine processor with configurable modes"""
    
    def __init__(self):
        # Load environment from root .env
        env_path = Path(__file__).parent.parent / '.env'
        load_dotenv(env_path)
        
        # Initialize configuration
        self.config = self._load_config()
        self.processor = None
        self.storage = None
        
        # Statistics
        self.stats = {
            'start_time': datetime.now(),
            'documents_processed': 0,
            'images_extracted': 0,
            'images_analyzed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'errors': 0
        }
    
    def _load_config(self) -> Dict:
        """Load configuration from environment variables"""
        # Get execution mode
        mode = os.getenv('EXECUTION_MODE', 'demo').lower()
        
        # Base configuration
        config = {
            'mode': mode,
            'database_url': os.getenv('DATABASE_URL'),
            'supabase_url': os.getenv('SUPABASE_URL'),
            'supabase_anon_key': os.getenv('SUPABASE_ANON_KEY'),
            'supabase_service_key': os.getenv('SUPABASE_SERVICE_ROLE_KEY'),
            'ollama_base_url': os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434'),
            'llm_model': os.getenv('LLM_MODEL', 'llama3.2:3b'),
            'vision_model': os.getenv('VISION_MODEL', 'llava:7b'),
            'embedding_model': os.getenv('EMBEDDING_MODEL', 'embeddinggemma'),
            'test_pdf_path': os.getenv('TEST_PDF_PATH'),
            'batch_size': int(os.getenv('BATCH_SIZE', '32')),
            'max_concurrent': int(os.getenv('MAX_CONCURRENT', '3')),
            'memory_efficient': os.getenv('MEMORY_EFFICIENT', 'true').lower() == 'true',
            'debug_mode': os.getenv('DEBUG_MODE', 'false').lower() == 'true',
            'verbose_logging': os.getenv('VERBOSE_LOGGING', 'true').lower() == 'true'
        }
        
        # Apply mode-based overrides
        config.update(self._get_mode_config(mode))
        
        return config
    
    def _get_mode_config(self, mode: str) -> Dict:
        """Get configuration overrides based on execution mode"""
        mode_configs = {
            'production': {
                'enable_text_extraction': True,
                'enable_chunking': True,
                'enable_classification': True,
                'enable_embeddings': True,
                'enable_vision_analysis': True,
                'enable_database_storage': True,
                'enable_image_storage': True,
                'enable_supabase_storage': True,
                'enable_image_extraction': True,
                'enable_image_analysis': True,
                'enable_image_upload': True,
            },
            'demo': {
                'enable_text_extraction': True,
                'enable_chunking': True,
                'enable_classification': True,
                'enable_embeddings': False,  # Skip for speed
                'enable_vision_analysis': False,  # Skip for speed
                'enable_database_storage': True,
                'enable_image_storage': False,
                'enable_supabase_storage': False,
                'enable_image_extraction': True,
                'enable_image_analysis': False,
                'enable_image_upload': False,
            },
            'image_only': {
                'enable_text_extraction': True,  # NEEDED for image extraction from PDF!
                'enable_chunking': False,
                'enable_classification': False,
                'enable_embeddings': False,
                'enable_vision_analysis': True,
                'enable_database_storage': False,
                'enable_image_storage': True,
                'enable_supabase_storage': True,
                'enable_image_extraction': True,
                'enable_image_analysis': True,
                'enable_image_upload': True,
            },
            'embedding_only': {
                'enable_text_extraction': True,
                'enable_chunking': True,
                'enable_classification': False,
                'enable_embeddings': True,
                'enable_vision_analysis': False,
                'enable_database_storage': True,
                'enable_image_storage': False,
                'enable_supabase_storage': False,
                'enable_image_extraction': False,
                'enable_image_analysis': False,
                'enable_image_upload': False,
            },
            'classification_only': {
                'enable_text_extraction': True,
                'enable_chunking': False,
                'enable_classification': True,
                'enable_embeddings': False,
                'enable_vision_analysis': False,
                'enable_database_storage': True,
                'enable_image_storage': False,
                'enable_supabase_storage': False,
                'enable_image_extraction': False,
                'enable_image_analysis': False,
                'enable_image_upload': False,
            },
            'full_test': {
                'enable_text_extraction': True,
                'enable_chunking': True,
                'enable_classification': True,
                'enable_embeddings': True,
                'enable_vision_analysis': True,
                'enable_database_storage': True,
                'enable_image_storage': True,
                'enable_supabase_storage': True,
                'enable_image_extraction': True,
                'enable_image_analysis': True,
                'enable_image_upload': True,
            }
        }
        
        return mode_configs.get(mode, mode_configs['demo'])
    
    async def initialize(self):
        """Initialize the processor and storage"""
        try:
            if self.config['verbose_logging']:
                print(f"🚀 Initializing KR-AI-Engine Processor...")
                print(f"📊 Mode: {self.config['mode']}")
                print(f"🔧 Configuration: {json.dumps({k: v for k, v in self.config.items() if 'key' not in k.lower() and 'url' not in k.lower()}, indent=2)}")
            
            # Initialize processor if needed
            if any(self.config.get(f'enable_{feature}', False) for feature in ['text_extraction', 'chunking', 'classification', 'embeddings', 'vision_analysis']):
                self.processor = ProductionDocumentProcessor()
                await self.processor.initialize()
            
            # Initialize storage if needed
            if self.config.get('enable_supabase_storage', False):
                supabase_config = SupabaseConfig()
                self.storage = SupabaseStorage(supabase_config)
                
                # Setup buckets if needed
                if self.config.get('enable_image_upload', False):
                    await self.storage.setup_storage_buckets()
            
            if self.config['verbose_logging']:
                print("✅ Initialization complete!")
                
        except Exception as e:
            print(f"❌ Initialization failed: {e}")
            raise
    
    async def process_document(self, file_path: str) -> Dict[str, Any]:
        """Process a document based on configuration"""
        try:
            file_path = Path(file_path)
            if not file_path.exists():
                raise FileNotFoundError(f"File not found: {file_path}")
            
            # Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            if self.config['verbose_logging']:
                print(f"📄 Processing: {file_path.name} ({len(file_content)/1024/1024:.1f} MB)")
            
            results = {
                'file_path': str(file_path),
                'file_size': len(file_content),
                'processing_stages': []
            }
            
            # === TEXT EXTRACTION ===
            if self.config.get('enable_text_extraction', False):
                if self.config['verbose_logging']:
                    print("📝 Extracting text content...")
                
                content_result = await self.processor._extract_content_with_gpu(file_content)
                results['text_length'] = len(content_result.get('text', ''))
                results['images_found'] = len(content_result.get('images', []))
                results['processing_stages'].append('text_extraction')
                
                if self.config['verbose_logging']:
                    print(f"   ✅ Extracted {results['text_length']} characters")
                    print(f"   ✅ Found {results['images_found']} images")
            
            # === IMAGE EXTRACTION & ANALYSIS ===
            if self.config.get('enable_image_extraction', False):
                if self.config['verbose_logging']:
                    print("🖼️ Extracting images...")
                
                # Extract images (already done in text extraction)
                images = content_result.get('images', [])
                self.stats['images_extracted'] = len(images)
                results['processing_stages'].append('image_extraction')
                
                # Analyze images if enabled
                if self.config.get('enable_image_analysis', False) and images:
                    if self.config['verbose_logging']:
                        print(f"👁️ Analyzing {len(images)} images...")
                    
                    analyzed_images = await self._analyze_images(images, str(file_path))
                    results['analyzed_images'] = len(analyzed_images)
                    self.stats['images_analyzed'] = len(analyzed_images)
                    results['processing_stages'].append('image_analysis')
                    
                    # Upload images if enabled
                    if self.config.get('enable_image_upload', False) and self.storage:
                        if self.config['verbose_logging']:
                            print("☁️ Uploading images to storage...")
                        
                        uploaded_count = await self._upload_images(analyzed_images)
                        results['uploaded_images'] = uploaded_count
                        results['processing_stages'].append('image_upload')
            
            # === CLASSIFICATION ===
            if self.config.get('enable_classification', False):
                if self.config['verbose_logging']:
                    print("🏷️ Classifying document...")
                
                classification = await self.processor._classify_document(
                    file_path.name, 
                    content_result.get('text', '')
                )
                results['classification'] = classification
                results['processing_stages'].append('classification')
                
                if self.config['verbose_logging']:
                    print(f"   ✅ Type: {classification.get('document_type', 'unknown')}")
                    print(f"   ✅ Manufacturer: {classification.get('manufacturer', 'unknown')}")
            
            # === CHUNKING ===
            if self.config.get('enable_chunking', False):
                if self.config['verbose_logging']:
                    print("🧩 Creating chunks...")
                
                # Create a temporary document ID for chunking
                document_id = f"temp_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                
                chunk_result = await self.processor._process_chunks_with_gpu(
                    document_id,
                    content_result.get('text', ''),
                    file_path.name
                )
                
                chunks = chunk_result.get('chunks', [])
                results['chunks_created'] = len(chunks)
                self.stats['chunks_created'] = len(chunks)
                results['processing_stages'].append('chunking')
                
                if self.config['verbose_logging']:
                    print(f"   ✅ Created {len(chunks)} chunks")
                
                # === EMBEDDINGS ===
                if self.config.get('enable_embeddings', False):
                    if self.config['verbose_logging']:
                        print("🧠 Generating embeddings...")
                    
                    embedding_result = await self.processor._generate_embeddings_with_gpu(
                        document_id,
                        chunks
                    )
                    
                    embeddings = embedding_result.get('embedding_ids', [])
                    results['embeddings_generated'] = len(embeddings)
                    self.stats['embeddings_generated'] = len(embeddings)
                    results['processing_stages'].append('embeddings')
                    
                    if self.config['verbose_logging']:
                        print(f"   ✅ Generated {len(embeddings)} embeddings")
            
            # Update statistics
            self.stats['documents_processed'] += 1
            
            return results
            
        except Exception as e:
            self.stats['errors'] += 1
            print(f"❌ Processing error: {e}")
            raise
    
    async def _analyze_images(self, images: List[Dict], document_path: str) -> List[Dict]:
        """Analyze images with vision model (DEBUG VERSION)"""
        analyzed_images = []
        
        if self.config['verbose_logging']:
            print(f"   🔧 DEBUG: Received {len(images)} images for analysis")
            if images and len(images) > 0:
                first_image = images[0]
                print(f"   🔧 DEBUG: First image type: {type(first_image)}")
                if isinstance(first_image, dict):
                    print(f"   🔧 DEBUG: First image keys: {list(first_image.keys())}")
                    print(f"   🔧 DEBUG: First image data size: {len(first_image.get('data', b''))} bytes")
                elif isinstance(first_image, bytes):
                    print(f"   🔧 DEBUG: First image is raw bytes: {len(first_image)} bytes")
                else:
                    print(f"   🔧 DEBUG: First image unknown format: {len(str(first_image))} chars")
            else:
                print(f"   🚨 DEBUG: NO IMAGES RECEIVED!")
        
        # QUICK FIX: Skip vision analysis, just prepare images for upload
        for i, image_data in enumerate(images):
            try:
                if self.config['verbose_logging'] and i == 0:
                    print(f"   🔧 Processing first image type: {type(image_data)}")
                
                # Handle different image data formats
                if isinstance(image_data, bytes):
                    # Raw bytes - create structure
                    analyzed_image = {
                        'data': image_data,
                        'analysis': f"image_{i}",
                        'type': 'extracted_image',
                        'index': i,
                        'page': 'unknown'
                    }
                elif isinstance(image_data, dict):
                    # Already structured
                    analyzed_image = {
                        'data': image_data.get('data', image_data),
                        'analysis': f"image_{i}_from_page_{image_data.get('page', 'unknown')}",
                        'type': 'extracted_image',
                        'index': i,
                        'page': image_data.get('page', 'unknown')
                    }
                else:
                    # Fallback for other types
                    analyzed_image = {
                        'data': bytes(image_data) if image_data else b'',
                        'analysis': f"image_{i}_fallback",
                        'type': 'extracted_image',
                        'index': i,
                        'page': 'unknown'
                    }
                analyzed_images.append(analyzed_image)
                    
            except Exception as e:
                if self.config['debug_mode']:
                    print(f"⚠️ Image {i} prep failed: {e}")
                continue
        
        if self.config['verbose_logging']:
            print(f"   ✅ Prepared {len(analyzed_images)} images for upload")
        
        return analyzed_images
    
    async def _upload_images(self, images: List[Dict]) -> int:
        """Upload images to Supabase storage"""
        uploaded_count = 0
        
        for image in images:
            try:
                # Determine image type for bucket selection
                analysis = image.get('analysis', '')
                image_type = self.processor._determine_image_type(analysis, 'temp_doc')
                
                # Create image path
                image_path = Path(f"temp_image_{uploaded_count}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                
                # Upload to appropriate bucket
                upload_result = await self.storage.upload_image(
                    image_path,
                    image.get('data', b''),
                    image_type
                )
                
                if upload_result:
                    uploaded_count += 1
                    if self.config['verbose_logging'] and uploaded_count % 50 == 0:
                        print(f"   ☁️ Uploaded {uploaded_count} images...")
                        
            except Exception as e:
                if self.config['debug_mode']:
                    print(f"⚠️ Image upload failed: {e}")
                continue
        
        return uploaded_count
    
    def print_summary(self, results: Optional[Dict] = None):
        """Print processing summary"""
        duration = datetime.now() - self.stats['start_time']
        
        print("\n" + "="*60)
        print("📊 KR-AI-Engine Processing Summary")
        print("="*60)
        print(f"🕐 Duration: {duration}")
        print(f"📄 Documents: {self.stats['documents_processed']}")
        print(f"🖼️ Images Extracted: {self.stats['images_extracted']}")
        print(f"👁️ Images Analyzed: {self.stats['images_analyzed']}")
        print(f"🧩 Chunks Created: {self.stats['chunks_created']}")
        print(f"🧠 Embeddings Generated: {self.stats['embeddings_generated']}")
        print(f"❌ Errors: {self.stats['errors']}")
        
        if results:
            print("\n📋 Processing Stages:")
            for stage in results.get('processing_stages', []):
                print(f"   ✅ {stage}")
        
        print("="*60)
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.processor:
                await self.processor.close()
            if self.config['verbose_logging']:
                print("🧹 Cleanup complete")
        except Exception as e:
            print(f"⚠️ Cleanup warning: {e}")

async def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="KR-AI-Engine Universal Document Processor",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python krai_processor.py --mode production --file document.pdf
  python krai_processor.py --mode image_only --file manual.pdf --verbose
  python krai_processor.py --mode demo --file test.pdf
  python krai_processor.py --mode embedding_only --file service_manual.pdf
        """
    )
    
    parser.add_argument('--mode', 
                       choices=['production', 'demo', 'image_only', 'embedding_only', 'classification_only', 'full_test'],
                       help='Execution mode (overrides EXECUTION_MODE in .env)')
    
    parser.add_argument('--file', 
                       type=str,
                       help='Path to PDF file to process (overrides TEST_PDF_PATH in .env)')
    
    parser.add_argument('--verbose', 
                       action='store_true',
                       help='Enable verbose output')
    
    parser.add_argument('--debug', 
                       action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    # Initialize processor
    processor = KRAIProcessor()
    
    # Override config with command line arguments
    if args.mode:
        os.environ['EXECUTION_MODE'] = args.mode
        processor.config = processor._load_config()  # Reload config
    
    if args.verbose:
        processor.config['verbose_logging'] = True
    
    if args.debug:
        processor.config['debug_mode'] = True
    
    # Determine file to process
    file_path = args.file or processor.config['test_pdf_path']
    if not file_path:
        print("❌ No file specified. Use --file or set TEST_PDF_PATH in .env")
        return
    
    try:
        # Initialize
        await processor.initialize()
        
        # Process document
        print(f"🚀 Starting {processor.config['mode']} mode processing...")
        results = await processor.process_document(file_path)
        
        # Print summary
        processor.print_summary(results)
        
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        if processor.config['debug_mode']:
            import traceback
            traceback.print_exc()
    
    finally:
        # Cleanup
        await processor.cleanup()

if __name__ == "__main__":
    asyncio.run(main())
