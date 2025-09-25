"""
Supabase Document API endpoints for KRAI Engine
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from supabase_document_processor import SupabaseDocumentProcessor
from config.supabase_config import SupabaseConfig

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/supabase/documents", tags=["supabase-documents"])

# Global processor instance
processor = None

# Pydantic models
class SupabaseDocumentUploadResponse(BaseModel):
    document_id: str
    status: str
    message: str
    storage_url: Optional[str] = None
    processing_time: Optional[float] = None
    stats: Optional[Dict] = None

class SupabaseDocumentInfo(BaseModel):
    id: str
    file_name: str
    document_type: str
    manufacturer: str
    version: str
    models: List[str]
    pages: int
    chunks: int
    images: int
    storage_url: str
    created_at: datetime
    processing_status: str

class SupabaseDocumentSearchRequest(BaseModel):
    query: str
    document_types: Optional[List[str]] = None
    manufacturers: Optional[List[str]] = None
    models: Optional[List[str]] = None
    include_images: bool = True
    limit: int = 10

class SupabaseDocumentSearchResponse(BaseModel):
    results: List[Dict]
    total_results: int
    query: str
    processing_time: float

class SupabaseProcessingStats(BaseModel):
    documents_processed: int
    chunks_created: int
    embeddings_generated: int
    images_processed: int
    errors: int
    uptime: str

# Dependency to get processor instance
async def get_supabase_processor():
    """Get or create Supabase processor instance"""
    global processor
    
    if processor is None:
        try:
            processor = SupabaseDocumentProcessor()
            await processor.initialize()
            logger.info("✅ Supabase document processor initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize Supabase processor: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize Supabase document processor")
    
    return processor

# API Endpoints

@router.post("/upload", response_model=SupabaseDocumentUploadResponse)
async def upload_document_to_supabase(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Upload and process a document with Supabase storage
    
    Args:
        file: PDF document file
        background_tasks: FastAPI background tasks
        processor: Supabase document processor instance
    
    Returns:
        Document upload response with Supabase storage information
    """
    try:
        # Validate file type
        if not file.filename.endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Create upload directory if it doesn't exist
        upload_dir = Path("uploads")
        upload_dir.mkdir(exist_ok=True)
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        file_path = upload_dir / f"{file_id}_{file.filename}"
        
        # Save uploaded file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        logger.info(f"🚀 Processing uploaded document with Supabase: {file.filename}")
        
        # Process document with Supabase storage
        result = await processor.process_document(file_path)
        
        # Clean up uploaded file
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"⚠️ Failed to clean up uploaded file: {e}")
        
        if result['status'] == 'success':
            return SupabaseDocumentUploadResponse(
                document_id=result['document_id'],
                status='success',
                message='Document processed and stored in Supabase successfully',
                storage_url=result['storage_url'],
                processing_time=result['processing_time'],
                stats=result['stats']
            )
        elif result['status'] == 'duplicate':
            return SupabaseDocumentUploadResponse(
                document_id=result['document_id'],
                status='duplicate',
                message='Document already exists in Supabase storage'
            )
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {result['error']}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Supabase document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/list", response_model=List[SupabaseDocumentInfo])
async def list_supabase_documents(
    limit: int = 50,
    offset: int = 0,
    document_type: Optional[str] = None,
    manufacturer: Optional[str] = None,
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    List documents with Supabase storage information
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        document_type: Filter by document type
        manufacturer: Filter by manufacturer
        processor: Supabase document processor instance
    
    Returns:
        List of document information with Supabase URLs
    """
    try:
        # Build query with filters
        query = """
            SELECT 
                d.id,
                d.file_name,
                d.document_type,
                m.name as manufacturer,
                d.cpmd_version as version,
                d.metadata,
                d.total_pages as pages,
                d.created_at,
                d.processing_status,
                d.storage_url,
                COUNT(DISTINCT c.id) as chunks,
                COUNT(DISTINCT i.id) as images
            FROM krai_core.documents d
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN krai_intelligence.chunks c ON d.id = c.document_id
            LEFT JOIN krai_content.images i ON d.id = i.document_id
            WHERE 1=1
        """
        
        params = []
        param_count = 0
        
        if document_type:
            param_count += 1
            query += f" AND d.document_type = ${param_count}"
            params.append(document_type)
        
        if manufacturer:
            param_count += 1
            query += f" AND m.name = ${param_count}"
            params.append(manufacturer)
        
        query += """
            GROUP BY d.id, m.name, d.storage_url
            ORDER BY d.created_at DESC
            LIMIT ${} OFFSET ${}
        """.format(param_count + 1, param_count + 2)
        
        params.extend([limit, offset])
        
        # Execute query
        async with processor.db_pool.acquire() as conn:
            rows = await conn.fetch(query, *params)
        
        # Convert to response format
        documents = []
        for row in rows:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            documents.append(SupabaseDocumentInfo(
                id=str(row['id']),
                file_name=row['file_name'],
                document_type=row['document_type'],
                manufacturer=row['manufacturer'],
                version=row['version'],
                models=metadata.get('models', []),
                pages=row['pages'],
                chunks=row['chunks'],
                images=row['images'],
                storage_url=row['storage_url'],
                created_at=row['created_at'],
                processing_status=row['processing_status']
            ))
        
        return documents
    
    except Exception as e:
        logger.error(f"❌ Supabase document listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.post("/search", response_model=SupabaseDocumentSearchResponse)
async def search_supabase_documents(
    request: SupabaseDocumentSearchRequest,
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Search documents using semantic search with Supabase storage
    
    Args:
        request: Search request with query and filters
        processor: Supabase document processor instance
    
    Returns:
        Search results with Supabase storage URLs and image information
    """
    try:
        start_time = datetime.now()
        
        # Generate embedding for search query
        query_embedding = processor.embedding_model.encode(request.query)
        
        # Build search query with image information
        search_query = """
            SELECT 
                d.id,
                d.file_name,
                d.document_type,
                m.name as manufacturer,
                d.cpmd_version as version,
                d.storage_url,
                c.text_chunk,
                c.page_start,
                c.page_end,
                c.section_title,
                1 - (e.embedding_vector <=> %s) as similarity_score,
                CASE 
                    WHEN %s THEN json_agg(
                        json_build_object(
                            'url', i.storage_url,
                            'page', i.page_number,
                            'index', i.image_index,
                            'width', i.width,
                            'height', i.height
                        )
                    ) FILTER (WHERE i.id IS NOT NULL)
                    ELSE NULL
                END as images
            FROM krai_intelligence.embeddings e
            JOIN krai_intelligence.chunks c ON e.chunk_id = c.id
            JOIN krai_core.documents d ON c.document_id = d.id
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN krai_content.images i ON d.id = i.document_id
            WHERE 1 - (e.embedding_vector <=> %s) > 0.7
        """
        
        params = [query_embedding.tolist(), request.include_images, query_embedding.tolist()]
        param_count = 3
        
        # Add filters
        if request.document_types:
            for doc_type in request.document_types:
                param_count += 1
                search_query += f" AND d.document_type = ${param_count}"
                params.append(doc_type)
        
        if request.manufacturers:
            for manufacturer in request.manufacturers:
                param_count += 1
                search_query += f" AND m.name = ${param_count}"
                params.append(manufacturer)
        
        search_query += f" GROUP BY d.id, c.id, e.id ORDER BY similarity_score DESC LIMIT ${param_count + 1}"
        params.append(request.limit)
        
        # Execute search
        async with processor.db_pool.acquire() as conn:
            rows = await conn.fetch(search_query, *params)
        
        # Convert results
        results = []
        for row in rows:
            result_dict = dict(row)
            if result_dict['images']:
                result_dict['images'] = [img for img in result_dict['images'] if img is not None]
            results.append(result_dict)
        
        # Get total count
        count_query = """
            SELECT COUNT(DISTINCT c.id) as total
            FROM krai_intelligence.embeddings e
            JOIN krai_intelligence.chunks c ON e.chunk_id = c.id
            JOIN krai_core.documents d ON c.document_id = d.id
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            WHERE 1 - (e.embedding_vector <=> %s) > 0.7
        """
        
        count_params = [query_embedding.tolist()]
        count_param_count = 1
        
        if request.document_types:
            for doc_type in request.document_types:
                count_param_count += 1
                count_query += f" AND d.document_type = ${count_param_count}"
                count_params.append(doc_type)
        
        if request.manufacturers:
            for manufacturer in request.manufacturers:
                count_param_count += 1
                count_query += f" AND m.name = ${count_param_count}"
                count_params.append(manufacturer)
        
        async with processor.db_pool.acquire() as conn:
            count_rows = await conn.fetch(count_query, *count_params)
        
        total_results = count_rows[0]['total'] if count_rows else 0
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return SupabaseDocumentSearchResponse(
            results=results,
            total_results=total_results,
            query=request.query,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"❌ Supabase document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{document_id}", response_model=SupabaseDocumentInfo)
async def get_supabase_document(
    document_id: str,
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Get detailed information about a specific document with Supabase storage
    
    Args:
        document_id: Document UUID
        processor: Supabase document processor instance
    
    Returns:
        Detailed document information with Supabase URLs
    """
    try:
        query = """
            SELECT 
                d.id,
                d.file_name,
                d.document_type,
                m.name as manufacturer,
                d.cpmd_version as version,
                d.metadata,
                d.total_pages as pages,
                d.created_at,
                d.processing_status,
                d.storage_url,
                COUNT(DISTINCT c.id) as chunks,
                COUNT(DISTINCT i.id) as images
            FROM krai_core.documents d
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN krai_intelligence.chunks c ON d.id = c.document_id
            LEFT JOIN krai_content.images i ON d.id = i.document_id
            WHERE d.id = $1
            GROUP BY d.id, m.name, d.storage_url
        """
        
        async with processor.db_pool.acquire() as conn:
            row = await conn.fetchrow(query, document_id)
        
        if not row:
            raise HTTPException(status_code=404, detail="Document not found")
        
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        
        return SupabaseDocumentInfo(
            id=str(row['id']),
            file_name=row['file_name'],
            document_type=row['document_type'],
            manufacturer=row['manufacturer'],
            version=row['version'],
            models=metadata.get('models', []),
            pages=row['pages'],
            chunks=row['chunks'],
            images=row['images'],
            storage_url=row['storage_url'],
            created_at=row['created_at'],
            processing_status=row['processing_status']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Supabase document retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.get("/{document_id}/images")
async def get_document_images(
    document_id: str,
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Get all images for a specific document
    
    Args:
        document_id: Document UUID
        processor: Supabase document processor instance
    
    Returns:
        List of image information with Supabase URLs
    """
    try:
        query = """
            SELECT 
                id,
                page_number,
                image_index,
                storage_url,
                width,
                height,
                colorspace,
                size_bytes,
                image_hash
            FROM krai_content.images
            WHERE document_id = $1
            ORDER BY page_number, image_index
        """
        
        async with processor.db_pool.acquire() as conn:
            rows = await conn.fetch(query, document_id)
        
        images = []
        for row in rows:
            images.append({
                'id': str(row['id']),
                'page_number': row['page_number'],
                'image_index': row['image_index'],
                'storage_url': row['storage_url'],
                'width': row['width'],
                'height': row['height'],
                'colorspace': row['colorspace'],
                'size_bytes': row['size_bytes'],
                'image_hash': row['image_hash']
            })
        
        return {
            'document_id': document_id,
            'image_count': len(images),
            'images': images
        }
    
    except Exception as e:
        logger.error(f"❌ Document images retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve images: {str(e)}")

@router.delete("/{document_id}")
async def delete_supabase_document(
    document_id: str,
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Delete a document and all associated data from Supabase
    
    Args:
        document_id: Document UUID
        processor: Supabase document processor instance
    
    Returns:
        Success message
    """
    try:
        # Note: In a real implementation, you would also delete files from Supabase storage
        # For now, we only delete from the database
        
        query = "DELETE FROM krai_core.documents WHERE id = $1"
        async with processor.db_pool.acquire() as conn:
            result = await conn.execute(query, document_id)
        
        # Check if any rows were affected
        if "DELETE 0" in result:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully from Supabase"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Supabase document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/stats/processing", response_model=SupabaseProcessingStats)
async def get_supabase_processing_stats(
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Get processing statistics for Supabase documents
    
    Args:
        processor: Supabase document processor instance
    
    Returns:
        Processing statistics including image processing
    """
    try:
        stats = processor.get_stats()
        
        # Calculate uptime (simplified)
        uptime = "Unknown"  # In production, you'd track start time
        
        return SupabaseProcessingStats(
            documents_processed=stats['documents_processed'],
            chunks_created=stats['chunks_created'],
            embeddings_generated=stats['embeddings_generated'],
            images_processed=stats['images_processed'],
            errors=stats['errors'],
            uptime=uptime
        )
    
    except Exception as e:
        logger.error(f"❌ Supabase stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

@router.get("/storage/info")
async def get_supabase_storage_info(
    processor: SupabaseDocumentProcessor = Depends(get_supabase_processor)
):
    """
    Get Supabase storage information
    
    Args:
        processor: Supabase document processor instance
    
    Returns:
        Storage bucket information and statistics
    """
    try:
        # Get storage statistics
        async with processor.db_pool.acquire() as conn:
            # Document count
            doc_count_query = "SELECT COUNT(*) as count FROM krai_core.documents"
            doc_count_row = await conn.fetchrow(doc_count_query)
            
            # Image count
            image_count_query = "SELECT COUNT(*) as count FROM krai_content.images"
            image_count_row = await conn.fetchrow(image_count_query)
            
            # Total storage size
            size_query = """
                SELECT 
                    SUM(size_bytes) as total_size,
                    AVG(size_bytes) as avg_size
                FROM krai_core.documents
            """
            size_row = await conn.fetchrow(size_query)
        
        return {
            'storage_buckets': {
                'documents': processor.supabase_config.config['storage_bucket'],
                'images': processor.supabase_config.config['image_bucket']
            },
            'statistics': {
                'total_documents': doc_count_row['count'],
                'total_images': image_count_row['count'],
                'total_size_bytes': size_row['total_size'] or 0,
                'average_size_bytes': size_row['avg_size'] or 0
            },
            'supabase_url': processor.supabase_config.supabase_url
        }
    
    except Exception as e:
        logger.error(f"❌ Supabase storage info retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get storage info: {str(e)}")
