"""
Document API endpoints for KRAI Engine
"""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import uuid

from fastapi import APIRouter, HTTPException, UploadFile, File, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from production_document_processor import DocumentProcessor, DatabaseManager
from config.database_config import db_config

# Configure logging
logger = logging.getLogger(__name__)

# Create API router
router = APIRouter(prefix="/api/documents", tags=["documents"])

# Global processor instance
processor = None
db_manager = None

# Pydantic models
class DocumentUploadResponse(BaseModel):
    document_id: str
    status: str
    message: str
    processing_time: Optional[float] = None

class DocumentInfo(BaseModel):
    id: str
    file_name: str
    document_type: str
    manufacturer: str
    version: str
    models: List[str]
    pages: int
    chunks: int
    created_at: datetime
    processing_status: str

class DocumentSearchRequest(BaseModel):
    query: str
    document_types: Optional[List[str]] = None
    manufacturers: Optional[List[str]] = None
    models: Optional[List[str]] = None
    limit: int = 10

class DocumentSearchResponse(BaseModel):
    results: List[Dict]
    total_results: int
    query: str
    processing_time: float

class ProcessingStats(BaseModel):
    documents_processed: int
    chunks_created: int
    embeddings_generated: int
    errors: int
    uptime: str

# Dependency to get processor instance
async def get_processor():
    """Get or create processor instance"""
    global processor, db_manager
    
    if processor is None:
        try:
            # Initialize database manager
            db_manager = DatabaseManager(db_config.get_connection_string())
            await db_manager.initialize_pool()
            
            # Initialize document processor
            processor = DocumentProcessor(db_manager)
            logger.info("✅ Document processor initialized")
            
        except Exception as e:
            logger.error(f"❌ Failed to initialize processor: {e}")
            raise HTTPException(status_code=500, detail="Failed to initialize document processor")
    
    return processor

# API Endpoints

@router.post("/upload", response_model=DocumentUploadResponse)
async def upload_document(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    Upload and process a document
    
    Args:
        file: PDF document file
        background_tasks: FastAPI background tasks
        processor: Document processor instance
    
    Returns:
        Document upload response with processing status
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
        
        logger.info(f"🚀 Processing uploaded document: {file.filename}")
        
        # Process document
        result = await processor.process_document(file_path)
        
        # Clean up uploaded file
        try:
            file_path.unlink()
        except Exception as e:
            logger.warning(f"⚠️ Failed to clean up uploaded file: {e}")
        
        if result['status'] == 'success':
            return DocumentUploadResponse(
                document_id=result['document_id'],
                status='success',
                message='Document processed successfully',
                processing_time=result['processing_time']
            )
        elif result['status'] == 'duplicate':
            return DocumentUploadResponse(
                document_id=result['document_id'],
                status='duplicate',
                message='Document already exists'
            )
        else:
            raise HTTPException(status_code=500, detail=f"Processing failed: {result['error']}")
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@router.get("/list", response_model=List[DocumentInfo])
async def list_documents(
    limit: int = 50,
    offset: int = 0,
    document_type: Optional[str] = None,
    manufacturer: Optional[str] = None,
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    List documents with optional filtering
    
    Args:
        limit: Maximum number of documents to return
        offset: Number of documents to skip
        document_type: Filter by document type
        manufacturer: Filter by manufacturer
        processor: Document processor instance
    
    Returns:
        List of document information
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
                COUNT(c.id) as chunks
            FROM krai_core.documents d
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN krai_intelligence.chunks c ON d.id = c.document_id
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
            GROUP BY d.id, m.name
            ORDER BY d.created_at DESC
            LIMIT ${} OFFSET ${}
        """.format(param_count + 1, param_count + 2)
        
        params.extend([limit, offset])
        
        # Execute query
        results = await processor.db.execute_query(query, tuple(params))
        
        # Convert to response format
        documents = []
        for row in results:
            metadata = json.loads(row['metadata']) if row['metadata'] else {}
            
            documents.append(DocumentInfo(
                id=row['id'],
                file_name=row['file_name'],
                document_type=row['document_type'],
                manufacturer=row['manufacturer'],
                version=row['version'],
                models=metadata.get('models', []),
                pages=row['pages'],
                chunks=row['chunks'],
                created_at=row['created_at'],
                processing_status=row['processing_status']
            ))
        
        return documents
    
    except Exception as e:
        logger.error(f"❌ Document listing failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@router.post("/search", response_model=DocumentSearchResponse)
async def search_documents(
    request: DocumentSearchRequest,
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    Search documents using semantic search
    
    Args:
        request: Search request with query and filters
        processor: Document processor instance
    
    Returns:
        Search results with relevance scores
    """
    try:
        start_time = datetime.now()
        
        # Generate embedding for search query
        query_embedding = processor.embedding_model.encode(request.query)
        
        # Build search query
        search_query = """
            SELECT 
                d.id,
                d.file_name,
                d.document_type,
                m.name as manufacturer,
                d.cpmd_version as version,
                c.text_chunk,
                c.page_start,
                c.page_end,
                c.section_title,
                1 - (e.embedding_vector <=> %s) as similarity_score
            FROM krai_intelligence.embeddings e
            JOIN krai_intelligence.chunks c ON e.chunk_id = c.id
            JOIN krai_core.documents d ON c.document_id = d.id
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            WHERE 1 - (e.embedding_vector <=> %s) > 0.7
        """
        
        params = [query_embedding.tolist(), query_embedding.tolist()]
        param_count = 2
        
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
        
        search_query += f" ORDER BY similarity_score DESC LIMIT ${param_count + 1}"
        params.append(request.limit)
        
        # Execute search
        results = await processor.db.execute_query(search_query, tuple(params))
        
        # Get total count
        count_query = """
            SELECT COUNT(*) as total
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
        
        count_results = await processor.db.execute_query(count_query, tuple(count_params))
        total_results = count_results[0]['total'] if count_results else 0
        
        processing_time = (datetime.now() - start_time).total_seconds()
        
        return DocumentSearchResponse(
            results=[dict(row) for row in results],
            total_results=total_results,
            query=request.query,
            processing_time=processing_time
        )
    
    except Exception as e:
        logger.error(f"❌ Document search failed: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@router.get("/{document_id}", response_model=DocumentInfo)
async def get_document(
    document_id: str,
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    Get detailed information about a specific document
    
    Args:
        document_id: Document UUID
        processor: Document processor instance
    
    Returns:
        Detailed document information
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
                COUNT(c.id) as chunks
            FROM krai_core.documents d
            LEFT JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            LEFT JOIN krai_intelligence.chunks c ON d.id = c.document_id
            WHERE d.id = $1
            GROUP BY d.id, m.name
        """
        
        results = await processor.db.execute_query(query, (document_id,))
        
        if not results:
            raise HTTPException(status_code=404, detail="Document not found")
        
        row = results[0]
        metadata = json.loads(row['metadata']) if row['metadata'] else {}
        
        return DocumentInfo(
            id=row['id'],
            file_name=row['file_name'],
            document_type=row['document_type'],
            manufacturer=row['manufacturer'],
            version=row['version'],
            models=metadata.get('models', []),
            pages=row['pages'],
            chunks=row['chunks'],
            created_at=row['created_at'],
            processing_status=row['processing_status']
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve document: {str(e)}")

@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    Delete a document and all associated data
    
    Args:
        document_id: Document UUID
        processor: Document processor instance
    
    Returns:
        Success message
    """
    try:
        # Delete document (CASCADE will handle chunks and embeddings)
        query = "DELETE FROM krai_core.documents WHERE id = $1"
        affected_rows = await processor.db.execute_update(query, (document_id,))
        
        if affected_rows == 0:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document deletion failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@router.get("/stats/processing", response_model=ProcessingStats)
async def get_processing_stats(
    processor: DocumentProcessor = Depends(get_processor)
):
    """
    Get processing statistics
    
    Args:
        processor: Document processor instance
    
    Returns:
        Processing statistics
    """
    try:
        stats = processor.get_stats()
        
        # Calculate uptime (simplified)
        uptime = "Unknown"  # In production, you'd track start time
        
        return ProcessingStats(
            documents_processed=stats['documents_processed'],
            chunks_created=stats['chunks_created'],
            embeddings_generated=stats['embeddings_generated'],
            errors=stats['errors'],
            uptime=uptime
        )
    
    except Exception as e:
        logger.error(f"❌ Stats retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {str(e)}")

# Configuration API endpoints for dashboard integration

@router.get("/config/patterns")
async def get_pattern_configs():
    """Get all pattern configurations for dashboard editing"""
    try:
        configs = {}
        
        # Load error code patterns
        error_patterns_path = Path("../config/error_code_patterns.json")
        if error_patterns_path.exists():
            with open(error_patterns_path, 'r') as f:
                configs['error_patterns'] = json.load(f)
        
        # Load version patterns
        version_patterns_path = Path("../config/version_patterns.json")
        if version_patterns_path.exists():
            with open(version_patterns_path, 'r') as f:
                configs['version_patterns'] = json.load(f)
        
        # Load model placeholder patterns
        model_patterns_path = Path("../config/model_placeholder_patterns.json")
        if model_patterns_path.exists():
            with open(model_patterns_path, 'r') as f:
                configs['model_patterns'] = json.load(f)
        
        # Load chunk settings
        chunk_settings_path = Path("../config/chunk_settings.json")
        if chunk_settings_path.exists():
            with open(chunk_settings_path, 'r') as f:
                configs['chunk_settings'] = json.load(f)
        
        return configs
    
    except Exception as e:
        logger.error(f"❌ Config retrieval failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get configs: {str(e)}")

@router.post("/config/patterns")
async def update_pattern_configs(configs: Dict):
    """Update pattern configurations from dashboard"""
    try:
        # Update error code patterns
        if 'error_patterns' in configs:
            error_patterns_path = Path("../config/error_code_patterns.json")
            with open(error_patterns_path, 'w') as f:
                json.dump(configs['error_patterns'], f, indent=2)
        
        # Update version patterns
        if 'version_patterns' in configs:
            version_patterns_path = Path("../config/version_patterns.json")
            with open(version_patterns_path, 'w') as f:
                json.dump(configs['version_patterns'], f, indent=2)
        
        # Update model patterns
        if 'model_patterns' in configs:
            model_patterns_path = Path("../config/model_placeholder_patterns.json")
            with open(model_patterns_path, 'w') as f:
                json.dump(configs['model_patterns'], f, indent=2)
        
        # Update chunk settings
        if 'chunk_settings' in configs:
            chunk_settings_path = Path("../config/chunk_settings.json")
            with open(chunk_settings_path, 'w') as f:
                json.dump(configs['chunk_settings'], f, indent=2)
        
        return {"message": "Configuration updated successfully"}
    
    except Exception as e:
        logger.error(f"❌ Config update failed: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update configs: {str(e)}")
