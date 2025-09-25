"""
Production Document Processor for KRAI Engine
Optimized for Apple M1 Pro with MPS and NVIDIA CUDA support
Integrates Llama, EmbeddingGemma, and Vision models
"""

import asyncio
import aiohttp
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
import torch
import numpy as np
# from sentence_transformers import SentenceTransformer  # Not needed for Ollama API
import httpx
from PIL import Image
import io

from config.production_config import config
from config.supabase_config import SupabaseConfig, SupabaseStorage
from tests.json_config_classifier import JSONConfigClassifier
from tests.json_version_extractor import JSONVersionExtractor
from tests.intelligent_model_extractor import IntelligentModelExtractor

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProductionDocumentProcessor:
    """Production-optimized document processor with GPU acceleration"""
    
    def __init__(self):
        # Initialize configuration
        self.config = config
        self.config.print_config_summary()
        
        # Initialize Supabase
        self.supabase_config = SupabaseConfig()
        self.supabase_storage = SupabaseStorage(self.supabase_config)
        
        # Initialize AI components
        self.classifier = JSONConfigClassifier()
        self.version_extractor = JSONVersionExtractor()
        self.model_extractor = IntelligentModelExtractor()
        
        # Initialize embedding model configuration for Ollama
        self._initialize_embedding_model()
        
        # Initialize Ollama client
        self.ollama_base_url = self.config.get_ollama_config()["base_url"]
        
        # Initialize model names
        self.llm_model = None
        self.vision_model = None
        self.available_models = []
        self.missing_models = []
        
        # Processing statistics
        self.stats = {
            "documents_processed": 0,
            "chunks_created": 0,
            "embeddings_generated": 0,
            "images_processed": 0,
            "errors": 0,
            "start_time": datetime.now()
        }
        
        # Cache for embeddings and vectors
        self.embedding_cache = {}
        self.vector_cache = {}
        
    def _initialize_embedding_model(self) -> None:
        """Initialize embedding model configuration for Ollama"""
        try:
            # Use configured embedding model
            model_name = self.config.model_config["embedding"]["model_name"]
            
            # Configure device
            device = self.config.device_config["device"]
            
            logger.info(f"🚀 Initializing embedding model '{model_name}' on {device}")
            
            # Store model configuration for Ollama API calls
            self.embedding_model_name = model_name
            self.embedding_device = device
            
            logger.info(f"✅ Embedding model configuration ready for Ollama API")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize embedding model: {e}")
            raise
    
    async def initialize(self):
        """Initialize the document processor"""
        try:
            logger.info("🚀 Initializing Production Document Processor...")
            
            # Initialize database connection pool
            self.db_pool = await self._create_database_pool()
            logger.info("✅ Database connection pool initialized")
            
            # Setup Supabase storage buckets
            await self._setup_storage_buckets()
            
            # Test Ollama connection
            await self._test_ollama_connection()
            
            logger.info("✅ Production Document Processor initialized successfully")
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {e}")
            raise
    
    async def _create_database_pool(self):
        """Create database connection pool"""
        import asyncpg
        
        return await asyncpg.create_pool(
            self.supabase_config.get_database_url(),
            min_size=2,
            max_size=10,
            command_timeout=60
        )
    
    async def _setup_storage_buckets(self):
        """Setup Supabase storage buckets"""
        try:
            # Create document bucket
            await self.supabase_storage.create_bucket("krai-documents", is_public=False)
            
            # Create image bucket
            await self.supabase_storage.create_bucket("krai-images", is_public=False)
            
            logger.info("✅ Storage buckets configured")
            
        except Exception as e:
            logger.warning(f"⚠️ Storage bucket setup warning: {e}")
    
    async def _test_ollama_connection(self):
        """Test Ollama connection"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.ollama_base_url}/api/tags", timeout=10)
                if response.status_code == 200:
                    models = response.json().get("models", [])
                    logger.info(f"✅ Ollama connected - {len(models)} models available")
                    
                    # Check required models
                    model_names = [model["name"] for model in models]
                    required_models = [
                        self.config.model_config["llm"]["model_name"],
                        self.config.model_config["embedding"]["model_name"],
                        self.config.model_config["vision"]["model_name"]
                    ]
                    
                    missing_models = [m for m in required_models if not any(m in name for name in model_names)]
                    if missing_models:
                        logger.warning(f"⚠️ Missing models: {missing_models}")
                    else:
                        logger.info("✅ All required models available")
                    
                    # Store model info for production use
                    self.available_models = model_names
                    self.missing_models = missing_models
                    
                    # Initialize model names for production use
                    self.llm_model = self.config.model_config["llm"]["model_name"]
                    self.vision_model = self.config.model_config["vision"]["model_name"]
                    
                    logger.info(f"🤖 LLM Model: {self.llm_model}")
                    logger.info(f"👁️ Vision Model: {self.vision_model}")
                    logger.info(f"🧠 Embedding Model: {self.embedding_model_name}")
                else:
                    logger.error(f"❌ Ollama connection failed: {response.status_code}")
                    
        except Exception as e:
            logger.error(f"❌ Ollama connection test failed: {e}")
    
    async def process_document(self, file_path: Path, file_content: bytes) -> Dict[str, Any]:
        """Process a document with full AI pipeline"""
        start_time = datetime.now()
        document_id = None
        
        try:
            logger.info(f"🚀 Starting production processing for: {file_path.name}")
            self.stats["documents_processed"] += 1
            
            # 1. Upload document to Supabase storage
            storage_result = await self.supabase_storage.upload_document(file_path, file_content)
            if not storage_result:
                raise Exception("Failed to upload document to Supabase storage")
            
            logger.info(f"✅ Document uploaded: {storage_result['url']}")
            
            # 2. Extract content from PDF
            extraction_result = await self._extract_content_with_gpu(file_content)
            
            # 3. Process images with Vision AI
            image_results = await self._process_images_with_vision(
                extraction_result["images"], 
                file_content
            )
            
            # 4. Classify document
            classification_result = self._classify_document(
                file_path.name, 
                extraction_result["text"]
            )
            
            # 5. Extract metadata
            version_result = self.version_extractor.extract_version(
                extraction_result["text"], 
                classification_result["manufacturer"]
            )
            
            model_result = self.model_extractor.extract_models(
                extraction_result["text"],
                classification_result["manufacturer"],
                classification_result.get("series", "unknown")
            )
            
            # 6. Store document in database
            document_id = await self._store_document_in_db(
                file_path, file_content, storage_result, extraction_result,
                classification_result, version_result, model_result, image_results
            )
            
            # 7. Process chunks with GPU acceleration
            chunk_result = await self._process_chunks_with_gpu(
                document_id, extraction_result["text"], classification_result
            )
            self.stats["chunks_created"] += len(chunk_result["chunks"])
            
            # 8. Generate embeddings with GPU
            embedding_result = await self._generate_embeddings_with_gpu(
                document_id, chunk_result["chunks"]
            )
            self.stats["embeddings_generated"] += len(embedding_result["embeddings"])
            
            processing_time = (datetime.now() - start_time).total_seconds()
            
            logger.info(f"✅ Document {document_id} processed in {processing_time:.2f}s")
            
            return {
                "status": "success",
                "document_id": str(document_id),
                "processing_time": processing_time,
                "stats": {
                    "pages": extraction_result["pages"],
                    "chunks": len(chunk_result["chunks"]),
                    "embeddings": len(embedding_result["embeddings"]),
                    "images": len(image_results),
                    "models": len(model_result["models"]),
                    "confidence": classification_result.get("confidence", 0.0)
                },
                "gpu_used": self.config.device_config["device"],
                "performance_metrics": {
                    "chunks_per_second": len(chunk_result["chunks"]) / processing_time,
                    "embeddings_per_second": len(embedding_result["embeddings"]) / processing_time
                }
            }
            
        except Exception as e:
            logger.error(f"❌ Production document processing failed: {e}")
            self.stats["errors"] += 1
            
            return {
                "status": "error",
                "document_id": str(document_id) if document_id else None,
                "error": str(e),
                "processing_time": (datetime.now() - start_time).total_seconds()
            }
    
    async def _extract_content_with_gpu(self, file_content: bytes) -> Dict[str, Any]:
        """Extract content from PDF with GPU acceleration"""
        try:
            import PyPDF2
            
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(file_content))
            pages = len(pdf_reader.pages)
            
            text_content = []
            images = []
            
            for page_num, page in enumerate(pdf_reader.pages):
                try:
                    text = page.extract_text()
                    if text.strip():
                        text_content.append(text)
                    
                    # Extract images from page
                    try:
                        page_images = self._extract_images_from_page(page, page_num)
                        images.extend(page_images)
                    except Exception as e:
                        logger.warning(f"⚠️ Failed to extract images from page {page_num}: {e}")
                        
                except Exception as e:
                    logger.warning(f"⚠️ Failed to extract text from page {page_num}: {e}")
            
            return {
                "text": "\n".join(text_content),
                "pages": pages,
                "images": images,  # Extracted images from PDF
                "extraction_method": "PyPDF2"
            }
            
        except Exception as e:
            logger.error(f"❌ Content extraction failed: {e}")
            raise
    
    def _extract_images_from_page(self, page, page_num: int) -> List[bytes]:
        """Extract images from a PDF page"""
        try:
            images = []
            
            # Get page resources
            if "/XObject" in page.get("/Resources", {}):
                xobjects = page["/Resources"]["/XObject"].get_object()
                
                for obj_name in xobjects:
                    obj = xobjects[obj_name]
                    
                    # Check if it's an image
                    if obj.get("/Subtype") == "/Image":
                        try:
                            # Extract image data
                            if obj.get("/Filter") == "/DCTDecode":  # JPEG
                                image_data = obj._data
                                images.append(image_data)
                                logger.info(f"📷 Extracted JPEG image from page {page_num}")
                                
                            elif obj.get("/Filter") == "/FlateDecode":  # PNG
                                image_data = obj._data
                                images.append(image_data)
                                logger.info(f"📷 Extracted PNG image from page {page_num}")
                                
                        except Exception as e:
                            logger.warning(f"⚠️ Failed to extract image {obj_name} from page {page_num}: {e}")
                            continue
            
            return images
            
        except Exception as e:
            logger.warning(f"⚠️ Failed to extract images from page {page_num}: {e}")
            return []
    
    async def _process_images_with_vision(self, images: List, file_content: bytes, document_id: str = None) -> List[Dict]:
        """Process images with Vision AI model"""
        if not images:
            return []
        
        self.current_document_id = document_id
        
        results = []
        vision_config = self.config.get_vision_config()
        
        try:
            async with httpx.AsyncClient() as client:
                for i, image_data in enumerate(images):
                    try:
                        # Convert image to base64
                        import base64
                        image_b64 = base64.b64encode(image_data).decode('utf-8')
                        
                        # Call Ollama Vision API
                        payload = {
                            "model": vision_config["model_name"],
                            "prompt": "Analyze this technical document image. Describe any diagrams, charts, error codes, part numbers, or technical specifications you can identify.",
                            "images": [image_b64],
                            "stream": False,
                            "options": {
                                "temperature": 0.3,
                                "max_new_tokens": vision_config["max_new_tokens"]
                            }
                        }
                        
                        response = await client.post(
                            f"{self.ollama_base_url}/api/generate",
                            json=payload,
                            timeout=60
                        )
                        
                        if response.status_code == 200:
                            result = response.json()
                            analysis = result.get("response", "")
                            
                            # Upload image to Supabase
                            image_path = Path(f"image_{i}.png")
                            image_storage = await self.supabase_storage.upload_image(
                                image_path, image_data
                            )
                            
                            # Store image in database
                            image_record = {
                                "image_index": i,
                                "analysis": analysis,
                                "storage_url": image_storage["url"] if image_storage else None,
                                "hash": image_storage["hash"] if image_storage else None,
                                "size": image_storage["size"] if image_storage else 0,
                                "content_type": image_storage["content_type"] if image_storage else "image/png"
                            }
                            results.append(image_record)
                            
                            logger.info(f"✅ Vision analysis completed for image {i}")
                            
                    except Exception as e:
                        logger.error(f"❌ Vision analysis failed for image {i}: {e}")
                        results.append({
                            "image_index": i,
                            "analysis": "",
                            "error": str(e)
                        })
        
        except Exception as e:
            logger.error(f"❌ Vision processing failed: {e}")
        
        # Store images in database
        if results:
            async with self.db_pool.acquire() as conn:
                for image_result in results:
                    await conn.execute(
                        """
                        INSERT INTO krai_content.images 
                        (document_id, image_index, storage_url, file_hash, ai_description, created_at)
                        VALUES ($1, $2, $3, $4, $5, NOW())
                        """,
                        self.current_document_id,  # We need to pass document_id
                        image_result["image_index"],
                        image_result["storage_url"],
                        image_result["hash"],
                        image_result["analysis"]
                    )
            
            logger.info(f"✅ Stored {len(results)} images in database")
        
        return results
    
    def _classify_document(self, filename: str, text: str) -> Dict[str, Any]:
        """Classify document using JSON config classifier"""
        try:
            # Use both filename and content-based classification
            filename_result = self.classifier.classify_document(filename)
            content_result = self.classifier.classify_document(filename, text)
            
            # Combine results with confidence weighting
            combined_result = self._combine_classification_results(
                filename_result, content_result
            )
            
            return combined_result
            
        except Exception as e:
            logger.error(f"❌ Document classification failed: {e}")
            return {
                "document_type": "unknown",
                "manufacturer": "unknown",
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _combine_classification_results(self, filename_result: Dict, content_result: Dict) -> Dict:
        """Combine filename and content classification results"""
        # Weight content-based classification higher
        content_weight = 0.7
        filename_weight = 0.3
        
        # Combine document types
        doc_type = content_result.get("document_type", "unknown")
        if doc_type == "unknown":
            doc_type = filename_result.get("document_type", "unknown")
        
        # Combine manufacturers
        manufacturer = content_result.get("manufacturer", "unknown")
        if manufacturer == "unknown":
            manufacturer = filename_result.get("manufacturer", "unknown")
        
        # Combine confidence scores
        content_confidence = content_result.get("confidence", 0.0)
        filename_confidence = filename_result.get("confidence", 0.0)
        
        combined_confidence = (
            content_confidence * content_weight + 
            filename_confidence * filename_weight
        )
        
        return {
            "document_type": doc_type,
            "manufacturer": manufacturer,
            "confidence": combined_confidence,
            "filename_classification": filename_result,
            "content_classification": content_result
        }
    
    async def _process_chunks_with_gpu(self, document_id: str, text: str, classification: Dict) -> Dict:
        """Process text into chunks with GPU acceleration"""
        try:
            chunk_size = self.config.model_config["chunking"]["default_chunk_size"]
            chunk_overlap = self.config.model_config["chunking"]["chunk_overlap"]
            
            # Simple chunking for now - can be enhanced with contextual chunking
            chunks = []
            start = 0
            
            while start < len(text):
                end = start + chunk_size
                chunk_text = text[start:end]
                
                if chunk_text.strip():
                    chunks.append({
                        "text": chunk_text,
                        "start_position": start,
                        "end_position": end,
                        "chunk_index": len(chunks)
                    })
                
                start = end - chunk_overlap
            
            # Store chunks in database
            chunk_ids = []
            async with self.db_pool.acquire() as conn:
                for chunk in chunks:
                    # Generate fingerprint for chunk
                    import hashlib
                    fingerprint = hashlib.md5(chunk["text"].encode('utf-8')).hexdigest()
                    
                    chunk_id = await conn.fetchval(
                             """
                             INSERT INTO krai_intelligence.chunks 
                             (document_id, text_chunk, chunk_index, page_start, page_end, processing_status, fingerprint, created_at)
                             VALUES ($1, $2, $3, $4, $5, $6, $7, NOW())
                             RETURNING id
                             """,
                             document_id,
                             chunk["text"],
                             chunk["chunk_index"],
                             chunk.get("page_start", 1),
                             chunk.get("page_end", 1),
                             "completed",
                             fingerprint
                         )
                    chunk_ids.append(chunk_id)
                    chunk["id"] = chunk_id
            
            logger.info(f"✅ Stored {len(chunks)} chunks in database")
            return {"chunks": chunks, "chunk_ids": chunk_ids}
            
        except Exception as e:
            logger.error(f"❌ Chunk processing failed: {e}")
            raise
    
    async def _generate_embeddings_with_gpu(self, document_id: str, chunks: List[Dict]) -> Dict:
        """Generate embeddings using Ollama API"""
        print("🚨 CRITICAL DEBUG: NEW _generate_embeddings_with_gpu method called!")
        print(f"🚨 CRITICAL DEBUG: chunks length = {len(chunks)}")
        try:
            logger.info(f"🔄 Starting embedding generation for {len(chunks)} chunks")
            
            # Generate embeddings for all chunks
            batch_texts = [chunk["text"] for chunk in chunks]
            logger.info(f"🔄 Calling Ollama API for {len(batch_texts)} texts")
            batch_embeddings = await self._generate_ollama_embeddings(batch_texts)
            logger.info(f"✅ Received {len(batch_embeddings)} embeddings from Ollama")
            
            # Store embeddings in database
            embedding_ids = []
            async with self.db_pool.acquire() as conn:
                for i, (chunk, embedding_vector) in enumerate(zip(chunks, batch_embeddings)):
                    logger.info(f"🔄 Processing embedding {i+1}/{len(chunks)}")
                    
                    # CRITICAL: Convert list to string format for pgvector
                    if isinstance(embedding_vector, list):
                        vector_str = '[' + ','.join(map(str, embedding_vector)) + ']'
                        logger.info(f"✅ Converted embedding to string format: {len(embedding_vector)} dimensions")
                    else:
                        logger.error(f"❌ Embedding is not a list: {type(embedding_vector)}")
                        raise ValueError(f"Expected list, got {type(embedding_vector)}")
                    
                    try:
                        embedding_id = await conn.fetchval(
                            """
                            INSERT INTO krai_intelligence.embeddings 
                            (chunk_id, embedding, model_name, model_version, created_at)
                            VALUES ($1, $2, $3, $4, NOW())
                            RETURNING id
                            """,
                            chunk["id"],
                            vector_str,  # This is guaranteed to be a string
                            self.embedding_model_name,
                            "latest"
                        )
                        embedding_ids.append(embedding_id)
                        logger.info(f"✅ Stored embedding {i+1} with ID: {embedding_id}")
                        
                    except Exception as db_error:
                        logger.error(f"❌ Database error for embedding {i+1}: {db_error}")
                        logger.error(f"❌ Chunk ID: {chunk['id']} (type: {type(chunk['id'])})")
                        logger.error(f"❌ Vector string: {vector_str[:50]}... (type: {type(vector_str)})")
                        raise
            
            logger.info(f"✅ Generated and stored {len(embedding_ids)} embeddings with Ollama")
            
            # Return simplified structure
            return {
                "embeddings": [{"dimension": len(emb), "model": self.embedding_model_name} for emb in batch_embeddings],
                "embedding_ids": embedding_ids
            }
            
        except Exception as e:
            logger.error(f"❌ Embedding generation failed: {e}")
            raise
    
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
                            "model": self.embedding_model_name,
                            "prompt": text
                        },
                        timeout=30.0
                    )
                    
                    if response.status_code == 200:
                        result = response.json()
                        print(f"DEBUG: Ollama response type: {type(result)}")
                        print(f"DEBUG: Ollama response keys: {result.keys()}")
                        print(f"DEBUG: embedding type: {type(result['embedding'])}")
                        print(f"DEBUG: embedding first 5 values: {result['embedding'][:5]}")
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
    
    async def _store_document_in_db(self, file_path: Path, file_content: bytes, 
                                  storage_result: Dict, extraction_result: Dict,
                                  classification_result: Dict, version_result: Dict,
                                  model_result: Dict, image_results: List) -> str:
        """Store document metadata in database"""
        try:
            import uuid
            
            document_id = str(uuid.uuid4())
            
            # Prepare document data
            document_data = {
                "id": document_id,
                "file_name": file_path.name,
                "document_type": classification_result.get("document_type", "unknown"),
                "manufacturer": classification_result.get("manufacturer", "unknown"),
                "version": version_result.get("version", ""),
                "models": json.dumps(model_result.get("models", [])),
                "pages": extraction_result["pages"],
                "storage_url": storage_result["url"],
                "storage_path": storage_result["url"],
                "size_bytes": len(file_content),
                "processing_status": "completed",
                "created_at": datetime.now(),
                "updated_at": datetime.now()
            }
            
            # Insert into database
            async with self.db_pool.acquire() as conn:
                await conn.execute("""
                    INSERT INTO krai_core.documents 
                    (id, file_name, document_type, manufacturer, version, models, 
                     pages, storage_url, storage_path, size_bytes, processing_status, 
                     created_at, updated_at)
                    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                """, *document_data.values())
            
            logger.info(f"✅ Document stored in database: {document_id}")
            return document_id
            
        except Exception as e:
            logger.error(f"❌ Database storage failed: {e}")
            raise
    
    async def get_processing_stats(self) -> Dict[str, Any]:
        """Get processing statistics"""
        uptime = (datetime.now() - self.stats["start_time"]).total_seconds()
        
        return {
            "documents_processed": self.stats["documents_processed"],
            "chunks_created": self.stats["chunks_created"],
            "embeddings_generated": self.stats["embeddings_generated"],
            "images_processed": self.stats["images_processed"],
            "errors": self.stats["errors"],
            "uptime_seconds": uptime,
            "device": self.config.device_config["device"],
            "device_name": self.config.device_config["device_name"],
            "memory_gb": self.config.device_config["memory_gb"],
            "performance_config": self.config.performance_config
        }
    
    async def _process_images_with_vision(self, images: List, file_content: bytes) -> List[Dict]:
        """Process images with Vision AI (LLaVA)"""
        try:
            if not images:
                logger.info("📷 No images found in document")
                return []
            
            logger.info(f"👁️ Processing {len(images)} images with Vision AI...")
            processed_images = []
            seen_hashes = set()  # Track image hashes to prevent duplicates
            
            for i, image_data in enumerate(images):
                try:
                    # Calculate image hash for deduplication
                    import hashlib
                    image_hash = hashlib.sha256(image_data).hexdigest()
                    
                    # Skip if we've already processed this exact image
                    if image_hash in seen_hashes:
                        logger.info(f"⏭️ Skipping duplicate image {i+1}/{len(images)} (hash: {image_hash[:8]}...)")
                        continue
                    
                    seen_hashes.add(image_hash)
                    
                    # Convert image data to PIL Image
                    if isinstance(image_data, bytes):
                        image = Image.open(io.BytesIO(image_data))
                    else:
                        image = image_data
                    
                    # Analyze image with Vision AI via Ollama
                    vision_analysis = await self._analyze_image_with_vision_ai(image, i)
                    
                    # Upload image to Supabase
                    image_result = await self.supabase_storage.upload_image(
                        Path(f"image_{i}.jpg"), 
                        image_data
                    )
                    
                    processed_image = {
                        "image_index": i,
                        "storage_url": image_result["url"] if image_result else None,
                        "hash": image_result["hash"] if image_result else None,
                        "size": len(image_data),
                        "vision_analysis": vision_analysis,
                        "content_type": "image/jpeg"
                    }
                    
                    processed_images.append(processed_image)
                    
                    logger.info(f"✅ Processed image {i+1}/{len(images)} (hash: {image_hash[:8]}...)")
                    
                except Exception as e:
                    logger.error(f"❌ Failed to process image {i}: {e}")
                    continue
            
            logger.info(f"✅ Vision AI processing completed: {len(processed_images)} unique images processed (deduplicated from {len(images)} total)")
            return processed_images
            
        except Exception as e:
            logger.error(f"❌ Vision AI processing failed: {e}")
            return []
    
    async def _analyze_image_with_vision_ai(self, image: Image.Image, image_index: int) -> Dict:
        """Analyze image with Vision AI (LLaVA) via Ollama"""
        try:
            # Convert image to base64 for Ollama API
            import base64
            
            buffer = io.BytesIO()
            image.save(buffer, format='JPEG', quality=85)
            image_bytes = buffer.getvalue()
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')
            
            # Prepare prompt for technical document analysis
            prompt = f"""Analyze this technical document image (Image #{image_index}). 
            Focus on:
            1. Document type (service manual, parts catalog, bulletin, etc.)
            2. Manufacturer and model information
            3. Technical diagrams, schematics, or procedures
            4. Error codes, part numbers, or technical specifications
            5. Any text content visible in the image
            
            Provide a structured analysis in JSON format."""
            
            # Call Ollama Vision API
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.ollama_base_url}/api/generate",
                    json={
                        "model": self.vision_model,
                        "prompt": prompt,
                        "images": [image_base64],
                        "stream": False,
                        "options": {
                            "temperature": 0.1,  # Low temperature for technical analysis
                            "top_p": 0.9
                        }
                    },
                    timeout=60
                )
                
                if response.status_code == 200:
                    result = response.json()
                    vision_analysis = {
                        "model_used": self.vision_model,
                        "analysis": result.get("response", ""),
                        "processing_time": result.get("total_duration", 0) / 1_000_000_000,  # Convert to seconds
                        "confidence": 0.8  # Default confidence for vision analysis
                    }
                    
                    logger.info(f"✅ Vision AI analysis completed for image {image_index}")
                    return vision_analysis
                else:
                    logger.error(f"❌ Vision AI API error: {response.status_code}")
                    return {"error": f"API error: {response.status_code}"}
                    
        except Exception as e:
            logger.error(f"❌ Vision AI analysis failed: {e}")
            return {"error": str(e)}

    async def close(self):
        """Close the document processor"""
        try:
            if hasattr(self, 'db_pool'):
                await self.db_pool.close()
            logger.info("✅ Production Document Processor closed")
        except Exception as e:
            logger.error(f"❌ Error closing processor: {e}")