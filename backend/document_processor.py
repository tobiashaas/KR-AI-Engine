"""
📄 Document Processor
Advanced document processing with AI analysis and vector embeddings

Features:
- PDF text extraction
- Image OCR with vision models
- Text chunking and preprocessing
- Vector embeddings generation
- Supabase integration
- Metadata extraction
"""

import asyncio
import os
import hashlib
import mimetypes
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
import logging

# Document processing
import PyPDF2
import pytesseract
from PIL import Image
import docx
from io import BytesIO

# AI/ML
from sentence_transformers import SentenceTransformer
import numpy as np

# Database
from supabase import create_client, Client
import uuid

# Configuration
from dotenv import load_dotenv
load_dotenv()

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Advanced document processing with AI integration"""
    
    def __init__(self):
        self.supabase_url = os.getenv("SUPABASE_URL")
        self.supabase_key = os.getenv("SUPABASE_SERVICE_KEY")
        self.supabase: Client = None
        
        # AI Models
        self.embedding_model = None
        self.chunk_size = int(os.getenv("CHUNK_SIZE", "1000"))
        self.chunk_overlap = 200
        
        # File limits
        self.max_file_size = int(os.getenv("MAX_FILE_SIZE", "100000000"))  # 100MB
        
        # Supported formats
        self.supported_formats = {
            'application/pdf': 'pdf',
            'image/jpeg': 'image',
            'image/jpg': 'image', 
            'image/png': 'image',
            'text/plain': 'text',
            'application/msword': 'doc',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'docx'
        }

    async def initialize(self):
        """Initialize Supabase client and AI models"""
        try:
            # Initialize Supabase
            self.supabase = create_client(self.supabase_url, self.supabase_key)
            logger.info("✅ Supabase client initialized")
            
            # Load embedding model
            self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("✅ Embedding model loaded")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Initialization failed: {str(e)}")
            return False

    async def test_connection(self) -> bool:
        """Test database connection"""
        try:
            result = self.supabase.table("manufacturers").select("id").limit(1).execute()
            return True
        except Exception as e:
            logger.error(f"Connection test failed: {str(e)}")
            return False

    async def process_upload(self, file, manufacturer_id: Optional[str] = None, category: Optional[str] = None) -> Dict[str, Any]:
        """Process uploaded file and extract content"""
        try:
            # Read file content
            content = await file.read()
            file_size = len(content)
            
            # Validate file size
            if file_size > self.max_file_size:
                raise ValueError(f"File too large: {file_size} bytes (max: {self.max_file_size})")
            
            # Detect file type
            mime_type = mimetypes.guess_type(file.filename)[0]
            if mime_type not in self.supported_formats:
                raise ValueError(f"Unsupported file type: {mime_type}")
            
            file_type = self.supported_formats[mime_type]
            
            # Generate document ID and hash
            document_id = str(uuid.uuid4())
            content_hash = hashlib.md5(content).hexdigest()
            
            # Extract text based on file type
            extracted_text = await self._extract_text(content, file_type)
            
            if not extracted_text or len(extracted_text.strip()) < 10:
                raise ValueError("No meaningful text could be extracted from the document")
            
            # Create text chunks
            chunks = self._create_chunks(extracted_text)
            
            # Generate embeddings
            embeddings = self._generate_embeddings(chunks)
            
            # Save to database
            await self._save_document(
                document_id=document_id,
                filename=file.filename,
                content_hash=content_hash,
                file_size=file_size,
                file_type=file_type,
                extracted_text=extracted_text,
                chunks=chunks,
                embeddings=embeddings,
                manufacturer_id=manufacturer_id,
                category=category
            )
            
            logger.info(f"✅ Document processed: {file.filename} ({len(chunks)} chunks)")
            
            return {
                "document_id": document_id,
                "file_size": file_size,
                "file_type": file_type,
                "chunks": len(chunks),
                "embeddings": len(embeddings),
                "text_length": len(extracted_text)
            }
            
        except Exception as e:
            logger.error(f"❌ Document processing failed: {str(e)}")
            raise

    async def _extract_text(self, content: bytes, file_type: str) -> str:
        """Extract text from different file types"""
        try:
            if file_type == 'pdf':
                return await self._extract_pdf_text(content)
            elif file_type == 'image':
                return await self._extract_image_text(content)
            elif file_type == 'text':
                return content.decode('utf-8')
            elif file_type in ['doc', 'docx']:
                return await self._extract_docx_text(content)
            else:
                raise ValueError(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Text extraction failed: {str(e)}")
            raise

    async def _extract_pdf_text(self, content: bytes) -> str:
        """Extract text from PDF"""
        try:
            pdf_file = BytesIO(content)
            pdf_reader = PyPDF2.PdfReader(pdf_file)
            
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n"
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"PDF extraction failed: {str(e)}")
            raise

    async def _extract_image_text(self, content: bytes) -> str:
        """Extract text from image using OCR"""
        try:
            image = Image.open(BytesIO(content))
            text = pytesseract.image_to_string(image, lang='deu+eng')
            return text.strip()
            
        except Exception as e:
            logger.error(f"Image OCR failed: {str(e)}")
            raise

    async def _extract_docx_text(self, content: bytes) -> str:
        """Extract text from DOCX"""
        try:
            doc = docx.Document(BytesIO(content))
            text = ""
            for paragraph in doc.paragraphs:
                text += paragraph.text + "\n"
            return text.strip()
            
        except Exception as e:
            logger.error(f"DOCX extraction failed: {str(e)}")
            raise

    def _create_chunks(self, text: str) -> List[str]:
        """Split text into chunks for processing"""
        words = text.split()
        chunks = []
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk = " ".join(chunk_words)
            if len(chunk.strip()) > 50:  # Minimum chunk size
                chunks.append(chunk.strip())
        
        return chunks

    def _generate_embeddings(self, chunks: List[str]) -> List[List[float]]:
        """Generate vector embeddings for text chunks"""
        try:
            embeddings = self.embedding_model.encode(chunks)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise

    async def _save_document(self, document_id: str, filename: str, content_hash: str, 
                           file_size: int, file_type: str, extracted_text: str,
                           chunks: List[str], embeddings: List[List[float]],
                           manufacturer_id: Optional[str], category: Optional[str]):
        """Save document and embeddings to database"""
        try:
            # Save main document record
            document_data = {
                "id": document_id,
                "filename": filename,
                "file_type": file_type,
                "file_size": file_size,
                "content_hash": content_hash,
                "extracted_text": extracted_text,
                "manufacturer_id": manufacturer_id,
                "category": category or "general",
                "processing_status": "completed",
                "created_at": datetime.utcnow().isoformat()
            }
            
            # Insert document
            result = self.supabase.table("service_manuals").insert(document_data).execute()
            
            # Save chunks with embeddings
            for i, (chunk, embedding) in enumerate(zip(chunks, embeddings)):
                chunk_data = {
                    "id": str(uuid.uuid4()),
                    "document_id": document_id,
                    "chunk_index": i,
                    "content": chunk,
                    "embedding": embedding,
                    "created_at": datetime.utcnow().isoformat()
                }
                
                self.supabase.table("document_chunks").insert(chunk_data).execute()
            
            logger.info(f"✅ Saved document: {filename} with {len(chunks)} chunks")
            
        except Exception as e:
            logger.error(f"❌ Database save failed: {str(e)}")
            raise

    async def semantic_search(self, query: str, limit: int = 10, threshold: float = 0.7,
                            manufacturer_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """Perform semantic search using vector similarity"""
        try:
            # Generate query embedding
            query_embedding = self.embedding_model.encode([query])[0].tolist()
            
            # Build search query
            search_params = {
                "query_embedding": query_embedding,
                "similarity_threshold": threshold,
                "match_count": limit
            }
            
            if manufacturer_id:
                search_params["manufacturer_filter"] = manufacturer_id
            
            # Execute semantic search
            result = self.supabase.rpc("semantic_search", search_params).execute()
            
            return result.data if result.data else []
            
        except Exception as e:
            logger.error(f"❌ Semantic search failed: {str(e)}")
            raise

    async def get_manufacturers(self) -> List[Dict[str, Any]]:
        """Get all manufacturers"""
        try:
            result = self.supabase.table("manufacturers").select("*").execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get manufacturers: {str(e)}")
            raise

    async def get_dashboard_stats(self) -> Dict[str, Any]:
        """Get comprehensive dashboard statistics"""
        try:
            # Get document counts
            docs_result = self.supabase.table("service_manuals").select("id", count="exact").execute()
            doc_count = docs_result.count or 0
            
            # Get manufacturer count
            mfg_result = self.supabase.table("manufacturers").select("id", count="exact").execute()
            mfg_count = mfg_result.count or 0
            
            # Get recent activity
            recent_docs = self.supabase.table("service_manuals").select("*").order("created_at", desc=True).limit(5).execute()
            
            return {
                "document_count": doc_count,
                "manufacturer_count": mfg_count,
                "recent_documents": recent_docs.data if recent_docs.data else [],
                "system_status": "operational",
                "last_updated": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to get dashboard stats: {str(e)}")
            raise

    async def get_recent_documents(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get recently processed documents"""
        try:
            result = self.supabase.table("service_manuals").select("*").order("created_at", desc=True).limit(limit).execute()
            return result.data if result.data else []
        except Exception as e:
            logger.error(f"Failed to get recent documents: {str(e)}")
            raise

    async def cleanup(self):
        """Cleanup resources"""
        logger.info("🧹 Cleaning up document processor resources...")
        # Add cleanup logic if needed
