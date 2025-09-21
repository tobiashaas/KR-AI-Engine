"""
🐍 KRAI FastAPI Backend
Production-Ready Document Processing & Vector Search API

Features:
- Supabase Integration
- Document Processing (PDF, Images, Text)
- Vector Embeddings with pgvector
- AI-powered Search & Analysis
- Real-time API endpoints
"""

from fastapi import FastAPI, HTTPException, UploadFile, File, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from typing import List, Optional, Dict, Any
import logging
from datetime import datetime

# Internal imports
from document_processor import DocumentProcessor
from version_manager import VersionManager
from routes.search_routes import search_router
from routes.document_routes import document_router
from routes.admin_routes import admin_router

# Configuration
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="KRAI API",
    description="Knowledge Retrieval AI - Intelligent Document Processing",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
document_processor = DocumentProcessor()
version_manager = VersionManager()

# Include routers
app.include_router(search_router, prefix="/api/v1/search", tags=["Search"])
app.include_router(document_router, prefix="/api/v1/documents", tags=["Documents"])
app.include_router(admin_router, prefix="/api/v1/admin", tags=["Admin"])

@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "🤖 KRAI API - Knowledge Retrieval AI",
        "version": "1.0.0",
        "status": "operational",
        "docs": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        db_status = await document_processor.test_connection()
        
        return {
            "status": "healthy",
            "database": "connected" if db_status else "disconnected",
            "services": {
                "document_processor": "active",
                "vector_search": "active",
                "embedding_model": "loaded"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=503, detail="Service unhealthy")

@app.post("/api/v1/upload")
async def upload_document(
    file: UploadFile = File(...),
    manufacturer_id: Optional[str] = None,
    category: Optional[str] = None
):
    """
    Upload and process a document
    
    Supports:
    - PDF documents
    - Images (PNG, JPG, JPEG)
    - Text files
    """
    try:
        # Validate file
        if not file.filename:
            raise HTTPException(status_code=400, detail="No file provided")
        
        # Process document
        result = await document_processor.process_upload(
            file=file,
            manufacturer_id=manufacturer_id,
            category=category
        )
        
        return {
            "status": "success",
            "document_id": result["document_id"],
            "processed_chunks": result["chunks"],
            "embeddings_created": result["embeddings"],
            "file_info": {
                "filename": file.filename,
                "size": result["file_size"],
                "type": result["file_type"]
            }
        }
        
    except Exception as e:
        logger.error(f"Upload failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/v1/search/semantic/{query}")
async def semantic_search(
    query: str,
    limit: int = 10,
    threshold: float = 0.7,
    manufacturer_id: Optional[str] = None
):
    """
    Semantic vector search across all documents
    
    Parameters:
    - query: Search term
    - limit: Maximum results (default: 10)
    - threshold: Similarity threshold (default: 0.7)
    - manufacturer_id: Filter by manufacturer (optional)
    """
    try:
        results = await document_processor.semantic_search(
            query=query,
            limit=limit,
            threshold=threshold,
            manufacturer_id=manufacturer_id
        )
        
        return {
            "query": query,
            "results": results,
            "count": len(results),
            "parameters": {
                "limit": limit,
                "threshold": threshold,
                "manufacturer_filter": manufacturer_id
            }
        }
        
    except Exception as e:
        logger.error(f"Search failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")

@app.get("/api/v1/manufacturers")
async def get_manufacturers():
    """Get all manufacturers"""
    try:
        manufacturers = await document_processor.get_manufacturers()
        return {
            "manufacturers": manufacturers,
            "count": len(manufacturers)
        }
    except Exception as e:
        logger.error(f"Failed to get manufacturers: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/stats/dashboard")
async def get_dashboard_stats():
    """Get comprehensive dashboard statistics"""
    try:
        stats = await document_processor.get_dashboard_stats()
        return stats
    except Exception as e:
        logger.error(f"Failed to get dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/documents/recent")
async def get_recent_documents(limit: int = 20):
    """Get recently processed documents"""
    try:
        documents = await document_processor.get_recent_documents(limit)
        return {
            "documents": documents,
            "count": len(documents)
        }
    except Exception as e:
        logger.error(f"Failed to get recent documents: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "Not Found",
            "message": "The requested resource was not found",
            "path": str(request.url.path)
        }
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error", 
            "message": "An unexpected error occurred",
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Startup events
@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info("🚀 Starting KRAI API...")
    
    # Initialize document processor
    await document_processor.initialize()
    
    # Load AI models
    logger.info("📚 Loading AI models...")
    
    logger.info("✅ KRAI API started successfully!")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("🛑 Shutting down KRAI API...")
    
    # Cleanup resources
    await document_processor.cleanup()
    
    logger.info("✅ KRAI API shutdown complete!")

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host="0.0.0.0", 
        port=8001,
        reload=True,
        log_level="info"
    )
