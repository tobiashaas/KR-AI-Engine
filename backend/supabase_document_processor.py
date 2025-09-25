#!/usr/bin/env python3
"""
Supabase Document Processor - KRAI Engine
Complete document processing pipeline with Supabase integration
"""

import asyncio
import logging
import hashlib
import json
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import uuid

import fitz  # PyMuPDF
import asyncpg
from sentence_transformers import SentenceTransformer
import numpy as np

# Import our custom modules
from tests.json_config_classifier import JSONConfigClassifier
from tests.json_version_extractor import JSONVersionExtractor
from tests.intelligent_model_extractor import IntelligentModelExtractor
from config.supabase_config import SupabaseConfig, SupabaseStorage

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SupabaseDocumentProcessor:
    """Document processor with Supabase integration"""
    
    def __init__(self):
        # Initialize Supabase configuration
        self.supabase_config = SupabaseConfig()
        self.supabase_storage = SupabaseStorage(self.supabase_config)
        
        # Initialize database connection
        self.db_pool = None
        
        # Initialize AI components with correct config path
        config_path = Path(__file__).parent / "config"
        self.classifier = JSONConfigClassifier(config_path=str(config_path))
        self.version_extractor = JSONVersionExtractor(config_path=str(config_path))
        self.model_extractor = IntelligentModelExtractor(config_path=str(config_path))
        
        # Initialize embedding model
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # Processing statistics
        self.stats = {
            'documents_processed': 0,
            'chunks_created': 0,
            'embeddings_generated': 0,
            'images_processed': 0,
            'errors': 0
        }
    
    async def initialize(self):
        """Initialize the processor"""
        try:
            # Initialize database pool
            self.db_pool = await asyncpg.create_pool(
                self.supabase_config.get_database_url(),
                min_size=5,
                max_size=20,
                command_timeout=60
            )
            logger.info("✅ Database connection pool initialized")
            
            # Setup storage buckets
            await self.supabase_storage.setup_storage_buckets()
            
            logger.info("✅ Supabase Document Processor initialized")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def close(self):
        """Close connections"""
        if self.db_pool:
            await self.db_pool.close()
        logger.info("✅ Supabase Document Processor closed")
    
    async def process_document(self, file_path: Path, metadata: Dict = None) -> Dict:
        """
        Main document processing pipeline with Supabase storage
        
        Args:
            file_path: Path to the document file
            metadata: Optional metadata dictionary
            
        Returns:
            Dictionary with processing results
        """
        start_time = datetime.now()
        document_id = None
        
        try:
            logger.info(f"🚀 Starting Supabase document processing: {file_path.name}")
            
            # 1. Read file content
            with open(file_path, 'rb') as f:
                file_content = f.read()
            
            # 2. Calculate file hash and check for duplicates
            file_hash = hashlib.sha256(file_content).hexdigest()
            existing_doc = await self._check_duplicate(file_hash)
            
            if existing_doc:
                logger.info(f"⚠️ Document already exists: {existing_doc['id']}")
                return {
                    'status': 'duplicate',
                    'document_id': existing_doc['id'],
                    'message': 'Document already processed'
                }
            
            # 3. Upload document to Supabase storage
            storage_result = await self.supabase_storage.upload_document(file_path, file_content)
            if not storage_result:
                raise Exception("Failed to upload document to Supabase storage")
            
            logger.info(f"✅ Document uploaded to Supabase: {storage_result['url']}")
            
            # 4. Extract text and images from PDF
            extraction_result = await self._extract_content(file_content)
            
            # 5. Process images and upload to Supabase
            image_results = await self._process_and_upload_images(
                extraction_result['images'], 
                file_content
            )
            
            # 6. Classify document using JSON config
            classification_result = await self._classify_document(
                file_path.name, 
                extraction_result['text']
            )
            
            # 7. Extract version information
            version_result = await self._extract_version(
                extraction_result['text'],
                classification_result['manufacturer']
            )
            
            # 8. Extract models with intelligent placeholder handling
            model_result = await self._extract_models(
                extraction_result['text'],
                classification_result['manufacturer']
            )
            
            # 9. Store document in database with Supabase URLs
            document_id = await self._store_document_with_storage(
                file_path, file_hash, storage_result,
                extraction_result, classification_result, 
                version_result, model_result, image_results
            )
            
            # 10. Process chunks with contextual chunking
            chunk_result = await self._process_chunks(
                document_id, extraction_result['text'],
                classification_result, model_result
            )
            
            # 11. Generate embeddings
            embedding_result = await self._generate_embeddings(
                document_id, chunk_result['chunks']
            )
            
            # 12. Store technical information
            await self._store_technical_info(
                document_id, classification_result, model_result
            )
            
            # Update statistics
            self.stats['documents_processed'] += 1
            self.stats['chunks_created'] += len(chunk_result['chunks'])
            self.stats['embeddings_generated'] += len(embedding_result['embeddings'])
            self.stats['images_processed'] += len(image_results)
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Supabase document processing completed: {document_id} ({processing_time:.2f}s)")
            
            return {
                'status': 'success',
                'document_id': document_id,
                'storage_url': storage_result['url'],
                'processing_time': processing_time,
                'stats': {
                    'pages': extraction_result['pages'],
                    'chunks': len(chunk_result['chunks']),
                    'embeddings': len(embedding_result['embeddings']),
                    'images': len(image_results),
                    'models': len(model_result['models']),
                    'confidence': classification_result.get('confidence', 0.0)
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Supabase document processing failed: {e}")
            self.stats['errors'] += 1
            
            return {
                'status': 'error',
                'document_id': document_id,
                'error': str(e),
                'processing_time': (datetime.now() - start_time).total_seconds()
            }
    
    async def _check_duplicate(self, file_hash: str) -> Optional[Dict]:
        """Check if document already exists in database"""
        async with self.db_pool.acquire() as conn:
            query = """
                SELECT id, file_name, created_at, storage_url
                FROM krai_core.documents 
                WHERE file_hash = $1
            """
            row = await conn.fetchrow(query, file_hash)
            return dict(row) if row else None
    
    async def _extract_content(self, file_content: bytes) -> Dict:
        """Extract text and images from PDF"""
        try:
            # Open PDF from bytes
            doc = fitz.open(stream=file_content, filetype="pdf")
            
            text_content = ""
            images = []
            total_pages = len(doc)
            
            for page_num in range(total_pages):
                page = doc[page_num]
                
                # Extract text
                page_text = page.get_text()
                text_content += f"\n--- PAGE {page_num + 1} ---\n{page_text}"
                
                # Extract images with metadata
                image_list = page.get_images()
                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        pix = fitz.Pixmap(doc, xref)
                        
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            img_data = pix.tobytes("png")
                            
                            images.append({
                                'page': page_num + 1,
                                'index': img_index,
                                'xref': xref,
                                'data': img_data,
                                'width': pix.width,
                                'height': pix.height,
                                'colorspace': pix.colorspace.name if pix.colorspace else 'unknown'
                            })
                        
                        pix = None
                        
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to extract image {img_index} from page {page_num + 1}: {e}")
            
            doc.close()
            
            return {
                'text': text_content,
                'images': images,
                'pages': total_pages
            }
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}")
            raise
    
    async def _process_and_upload_images(self, images: List[Dict], file_content: bytes) -> List[Dict]:
        """Process and upload images to Supabase storage"""
        image_results = []
        
        for image in images:
            try:
                # Generate unique filename
                image_hash = hashlib.sha256(image['data']).hexdigest()
                filename = f"page_{image['page']}_img_{image['index']}_{image_hash[:8]}.png"
                
                # Upload image to Supabase
                image_path = Path(filename)
                storage_result = await self.supabase_storage.upload_image(
                    image_path, 
                    image['data']
                )
                
                if storage_result:
                    image_results.append({
                        'page': image['page'],
                        'index': image['index'],
                        'hash': image_hash,
                        'url': storage_result['url'],
                        'width': image['width'],
                        'height': image['height'],
                        'colorspace': image['colorspace'],
                        'size': len(image['data'])
                    })
                    
                    logger.info(f"✅ Image uploaded: {filename}")
                else:
                    logger.warning(f"⚠️ Failed to upload image: {filename}")
            
            except Exception as e:
                logger.warning(f"⚠️ Image processing failed: {e}")
        
        return image_results
    
    async def _classify_document(self, filename: str, text: str) -> Dict:
        """Classify document using JSON config classifier"""
        try:
            result = self.classifier.classify_document(filename, text)
            
            return {
                'document_type': result['classification']['document_type'],
                'manufacturer': result['classification']['manufacturer'],
                'series': result['classification']['series'],
                'confidence': result['classification'].get('confidence', 0.0),
                'models': result['classification']['models'],
                'version': result['classification']['version']
            }
            
        except Exception as e:
            logger.error(f"❌ Document classification failed: {e}")
            raise
    
    async def _extract_version(self, text: str, manufacturer: str) -> Dict:
        """Extract version information using JSON config"""
        try:
            result = self.version_extractor.extract_version(text, manufacturer)
            
            return {
                'version': result['version'],
                'pattern_category': result['pattern_category'],
                'confidence': result.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"❌ Version extraction failed: {e}")
            raise
    
    async def _extract_models(self, text: str, manufacturer: str) -> Dict:
        """Extract models with intelligent placeholder handling"""
        try:
            result = self.model_extractor.extract_models(text, manufacturer)
            
            return {
                'models': result['models'],
                'placeholders': result['placeholders'],
                'series': result['series'],
                'confidence': result.get('confidence', 0.0)
            }
            
        except Exception as e:
            logger.error(f"❌ Model extraction failed: {e}")
            raise
    
    async def _store_document_with_storage(self, file_path: Path, file_hash: str,
                                         storage_result: Dict, extraction_result: Dict,
                                         classification_result: Dict, version_result: Dict,
                                         model_result: Dict, image_results: List[Dict]) -> str:
        """Store document in database with Supabase storage URLs"""
        try:
            # Get manufacturer ID
            manufacturer_id = await self._get_or_create_manufacturer(
                classification_result['manufacturer']
            )
            
            # Prepare document data with Supabase URLs
            document_data = {
                'file_name': file_path.name,
                'file_hash': file_hash,
                'storage_path': storage_result['url'],  # Supabase URL
                'storage_url': storage_result['url'],
                'size_bytes': storage_result['size'],
                'total_pages': extraction_result['pages'],
                'document_type': classification_result['document_type'],
                'manufacturer_id': manufacturer_id,
                'language': 'en',
                'processing_status': 'completed',
                'processing_progress': 100,
                'cpmd_version': version_result['version'],
                'metadata': json.dumps({
                    'version_pattern': version_result['pattern_category'],
                    'version_confidence': version_result.get('confidence', 0.0),
                    'classification_confidence': classification_result.get('confidence', 0.0),
                    'models': model_result['models'],
                    'series': model_result['series'],
                    'placeholders': model_result['placeholders'],
                    'images': image_results,
                    'supabase_storage': {
                        'document_url': storage_result['url'],
                        'document_hash': storage_result['hash'],
                        'image_count': len(image_results)
                    }
                })
            }
            
            # Insert document
            async with self.db_pool.acquire() as conn:
                query = """
                    INSERT INTO krai_core.documents (
                        file_name, file_hash, storage_path, storage_url, size_bytes, total_pages,
                        document_type, manufacturer_id, language, processing_status,
                        processing_progress, cpmd_version, metadata
                    ) VALUES (
                        $1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13
                    ) RETURNING id
                """
                
                document_id = await conn.fetchval(query, *[
                    document_data['file_name'], document_data['file_hash'],
                    document_data['storage_path'], document_data['storage_url'],
                    document_data['size_bytes'], document_data['total_pages'],
                    document_data['document_type'], document_data['manufacturer_id'],
                    document_data['language'], document_data['processing_status'],
                    document_data['processing_progress'], document_data['cpmd_version'],
                    document_data['metadata']
                ])
                
                logger.info(f"✅ Document stored in database with Supabase URLs: {document_id}")
                
                # Store images in database
                await self._store_images(document_id, image_results)
                
                return {
                    'document_id': str(document_id),
                    'status': 'success'
                }
            
        except Exception as e:
            logger.error(f"❌ Document storage failed: {e}")
            raise
    
    async def _store_images(self, document_id: str, image_results: List[Dict]):
        """Store image metadata in database"""
        try:
            async with self.db_pool.acquire() as conn:
                for image in image_results:
                    query = """
                        INSERT INTO krai_content.images (
                            document_id, page_number, image_index, storage_url,
                            width, height, colorspace, size_bytes, image_hash
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9
                        )
                    """
                    
                    await conn.execute(query, *[
                        document_id, image['page'], image['index'],
                        image['url'], image['width'], image['height'],
                        image['colorspace'], image['size'], image['hash']
                    ])
                
                logger.info(f"✅ Stored {len(image_results)} images for document {document_id}")
        
        except Exception as e:
            logger.error(f"❌ Image storage failed: {e}")
            raise
    
    async def _get_or_create_manufacturer(self, manufacturer_name: str) -> str:
        """Get or create manufacturer in database"""
        async with self.db_pool.acquire() as conn:
            # Try to get existing manufacturer
            query = """
                SELECT id FROM krai_core.manufacturers 
                WHERE name = $1
            """
            row = await conn.fetchrow(query, manufacturer_name)
            
            if row:
                return str(row['id'])
            
            # Create new manufacturer
            query = """
                INSERT INTO krai_core.manufacturers (name, display_name, country)
                VALUES ($1, $2, $3)
                RETURNING id
            """
            manufacturer_id = await conn.fetchval(query, manufacturer_name, manufacturer_name.title(), 'Unknown')
            
            logger.info(f"✅ Created new manufacturer: {manufacturer_name}")
            return str(manufacturer_id)
    
    async def _process_chunks(self, document_id: str, text: str, 
                            classification_result: Dict, model_result: Dict) -> Dict:
        """Process text into chunks using contextual chunking"""
        try:
            # Determine chunking strategy
            chunking_strategy = await self._determine_chunking_strategy(
                classification_result['document_type'],
                classification_result['manufacturer']
            )
            
            # Apply contextual chunking
            chunks = await self._apply_contextual_chunking(
                text, chunking_strategy, classification_result, model_result
            )
            
            # Store chunks in database
            chunk_ids = []
            async with self.db_pool.acquire() as conn:
                for chunk_index, chunk in enumerate(chunks):
                    query = """
                        INSERT INTO krai_intelligence.chunks (
                            document_id, chunk_index, page_start, page_end,
                            text_chunk, token_count, fingerprint, section_title,
                            processing_status
                        ) VALUES (
                            $1, $2, $3, $4, $5, $6, $7, $8, $9
                        ) RETURNING id
                    """
                    
                    chunk_id = await conn.fetchval(query, *[
                        document_id, chunk_index, chunk['page_start'],
                        chunk['page_end'], chunk['text'], chunk['token_count'],
                        chunk['fingerprint'], chunk['section_title'], 'completed'
                    ])
                    
                    chunk_ids.append(str(chunk_id))
            
            logger.info(f"✅ Created {len(chunks)} chunks for document {document_id}")
            
            return {
                'chunks': chunks,
                'chunk_ids': chunk_ids,
                'strategy': chunking_strategy
            }
            
        except Exception as e:
            logger.error(f"❌ Chunk processing failed: {e}")
            raise
    
    async def _determine_chunking_strategy(self, document_type: str, manufacturer: str) -> Dict:
        """Determine optimal chunking strategy"""
        # Load chunking settings from JSON config
        try:
            config_path = Path("../config/chunk_settings.json")
            with open(config_path, 'r') as f:
                config = json.load(f)
            
            settings = config.get('chunk_settings', {})
            strategies = settings.get('strategies', {})
            
            # Default strategy
            default_strategy = settings.get('default_strategy', 'contextual_chunking')
            
            # Check for manufacturer-specific settings
            manufacturer_settings = settings.get('manufacturer_specific', {}).get(manufacturer, {})
            if manufacturer_settings.get('default_strategy'):
                return manufacturer_settings
            
            # Check for document-type specific settings
            doc_type_settings = settings.get('document_type_specific', {}).get(document_type, {})
            if doc_type_settings.get('strategy'):
                return doc_type_settings
            
            # Return default strategy
            return strategies.get(default_strategy, {
                'chunk_size': 1000,
                'chunk_overlap': 150,
                'strategy': 'contextual_chunking'
            })
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to load chunking config, using defaults: {e}")
            return {
                'chunk_size': 1000,
                'chunk_overlap': 150,
                'strategy': 'contextual_chunking'
            }
    
    async def _apply_contextual_chunking(self, text: str, strategy: Dict, 
                                       classification_result: Dict, model_result: Dict) -> List[Dict]:
        """Apply contextual chunking based on strategy"""
        chunks = []
        chunk_size = strategy.get('chunk_size', 1000)
        chunk_overlap = strategy.get('chunk_overlap', 150)
        
        # Split text into pages
        pages = text.split('--- PAGE')
        
        for page_num, page_content in enumerate(pages):
            if not page_content.strip():
                continue
                
            # Clean page content
            page_content = page_content.replace(f' {page_num + 1} ---', '').strip()
            
            # Apply contextual chunking based on document type
            if classification_result['document_type'] == 'service_manual':
                page_chunks = self._chunk_service_manual(page_content, chunk_size, chunk_overlap)
            elif classification_result['document_type'] == 'technical_bulletin':
                page_chunks = self._chunk_bulletin(page_content, chunk_size, chunk_overlap)
            else:
                page_chunks = self._chunk_generic(page_content, chunk_size, chunk_overlap)
            
            # Add page information to chunks
            for chunk_index, chunk_text in enumerate(page_chunks):
                chunks.append({
                    'text': chunk_text,
                    'page_start': page_num + 1,
                    'page_end': page_num + 1,
                    'chunk_index': len(chunks),
                    'section_title': f"Page {page_num + 1}",
                    'token_count': len(chunk_text.split()),
                    'fingerprint': hashlib.md5(chunk_text.encode()).hexdigest()
                })
        
        return chunks
    
    def _chunk_service_manual(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk service manual with contextual awareness"""
        sections = re.split(r'\n(?=\d+\.\s+[A-Z])', text)
        
        chunks = []
        for section in sections:
            if len(section) <= chunk_size:
                chunks.append(section)
            else:
                words = section.split()
                for i in range(0, len(words), chunk_size - overlap):
                    chunk_words = words[i:i + chunk_size]
                    chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _chunk_bulletin(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Chunk bulletin with case awareness"""
        cases = re.split(r'\n(?=Case\d+:)', text)
        
        chunks = []
        for case in cases:
            if len(case) <= chunk_size:
                chunks.append(case)
            else:
                words = case.split()
                for i in range(0, len(words), chunk_size - overlap):
                    chunk_words = words[i:i + chunk_size]
                    chunks.append(' '.join(chunk_words))
        
        return chunks
    
    def _chunk_generic(self, text: str, chunk_size: int, overlap: int) -> List[str]:
        """Generic chunking for other document types"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), chunk_size - overlap):
            chunk_words = words[i:i + chunk_size]
            chunks.append(' '.join(chunk_words))
        
        return chunks
    
    async def _generate_embeddings(self, document_id: str, chunks: List[Dict]) -> Dict:
        """Generate embeddings for chunks"""
        try:
            embeddings = []
            embedding_ids = []
            
            async with self.db_pool.acquire() as conn:
                # Generate embeddings using Ollama API
                batch_texts = [chunk['text'] for chunk in chunks]
                batch_embeddings = await self._generate_ollama_embeddings(batch_texts)
                
                for i, chunk in enumerate(chunks):
                    # Get embedding for this chunk
                    embedding_vector = batch_embeddings[i]
                    
                    # Get chunk ID
                    chunk_id_query = """
                        SELECT id FROM krai_intelligence.chunks 
                        WHERE document_id = $1 AND chunk_index = $2
                    """
                    row = await conn.fetchrow(chunk_id_query, document_id, chunk['chunk_index'])
                    
                    if row:
                        chunk_id = row['id']
                        
                        # Store embedding
                        query = """
                            INSERT INTO krai_intelligence.embeddings (
                                chunk_id, embedding, model_name, model_version, created_at
                            ) VALUES (
                                $1, $2, $3, $4, NOW()
                            ) RETURNING id
                        """
                        
                        # Convert embedding to string format for pgvector
                        vector_str = '[' + ','.join(map(str, embedding_vector)) + ']'
                        embedding_id = await conn.fetchval(query, 
                            chunk_id, vector_str,
                            'embeddinggemma:300m', 'latest'
                        )
                        
                        embedding_ids.append(str(embedding_id))
                        
                        embeddings.append({
                            'chunk_id': str(chunk_id),
                            'embedding_vector': embedding_vector,
                            'model_name': 'all-MiniLM-L6-v2'
                        })
            
            logger.info(f"✅ Generated {len(embeddings)} embeddings for document {document_id}")
            
            return {
                'embeddings': embeddings,
                'embedding_ids': embedding_ids
            }
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
    async def _store_technical_info(self, document_id: str, classification_result: Dict, model_result: Dict):
        """Store technical information in database"""
        try:
            # Store models as products (if they don't exist)
            async with self.db_pool.acquire() as conn:
                for model_name in model_result['models']:
                    await self._get_or_create_product(conn, model_name, classification_result['manufacturer'])
            
            logger.info(f"✅ Stored technical information for document {document_id}")
            
        except Exception as e:
            logger.error(f"❌ Technical info storage failed: {e}")
            raise
    
    async def _get_or_create_product(self, conn, model_name: str, manufacturer: str) -> str:
        """Get or create product in database"""
        try:
            # Try to get existing product
            query = """
                SELECT p.id FROM krai_core.products p
                JOIN krai_core.manufacturers m ON p.manufacturer_id = m.id
                WHERE p.model_number = $1 AND m.name = $2
            """
            row = await conn.fetchrow(query, model_name, manufacturer)
            
            if row:
                return str(row['id'])
            
            # Create new product
            manufacturer_id = await self._get_or_create_manufacturer(manufacturer)
            
            query = """
                INSERT INTO krai_core.products (
                    model_number, display_name, manufacturer_id, product_type
                ) VALUES (
                    $1, $2, $3, $4
                ) RETURNING id
            """
            product_id = await conn.fetchval(query, model_name, model_name, manufacturer_id, 'printer')
            
            logger.info(f"✅ Created new product: {model_name}")
            return str(product_id)
            
        except Exception as e:
            logger.error(f"❌ Product handling failed: {e}")
            raise
    
    def get_stats(self) -> Dict:
        """Get processing statistics"""
        return self.stats.copy()
    
    async def _generate_ollama_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings using Ollama API"""
        try:
            import httpx
            
            embeddings = []
            
            async with httpx.AsyncClient() as client:
                for text in texts:
                    response = await client.post(
                        f"{self.ollama_base_url}/api/embeddings",
                        json={
                            "model": "embeddinggemma:300m",
                            "prompt": text
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        embeddings.append(result["embedding"])
                    else:
                        logger.error(f"❌ Ollama embedding failed: {response.status_code} - {response.text}")
                        # Fallback to zero vector
                        embeddings.append([0.0] * 768)
            
            return embeddings
            
        except Exception as e:
            logger.error(f"❌ Ollama embedding generation failed: {e}")
            # Fallback to zero vectors
            return [[0.0] * 768 for _ in texts]

# Main execution function
async def main():
    """Main function for testing the Supabase document processor"""
    
    processor = SupabaseDocumentProcessor()
    
    try:
        # Initialize processor
        await processor.initialize()
        
        # Test with a document
        test_document = Path("../test_documents/HP_E786_SM.pdf")
        
        if test_document.exists():
            logger.info(f"🚀 Processing test document: {test_document.name}")
            
            result = await processor.process_document(test_document)
            
            logger.info(f"📊 Processing result: {result}")
            logger.info(f"📈 Processor stats: {processor.get_stats()}")
        else:
            logger.warning(f"⚠️ Test document not found: {test_document}")
    
    except Exception as e:
        logger.error(f"❌ Main execution failed: {e}")
    
    finally:
        # Close processor
        await processor.close()

if __name__ == "__main__":
    asyncio.run(main())
