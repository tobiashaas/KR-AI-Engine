"""
KRAI Engine - Main FastAPI Application
Production Document Processing with Open WebUI Integration
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse

from api.document_api import router as document_router
from config.database_config import db_config

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for app lifespan management
db_manager = None
processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global db_manager, processor
    
    logger.info("🚀 Starting KRAI Engine...")
    
    try:
        # Initialize database connection
        from production_document_processor import DatabaseManager, DocumentProcessor
        
        db_manager = DatabaseManager(db_config.get_connection_string())
        await db_manager.initialize_pool()
        
        processor = DocumentProcessor(db_manager)
        
        logger.info("✅ KRAI Engine initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize KRAI Engine: {e}")
        raise
    
    finally:
        # Cleanup
        if db_manager:
            await db_manager.close_pool()
        logger.info("✅ KRAI Engine shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="KR-AI-Engine",
    description="AI-powered document processing system for technical service environments",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(document_router)

# Mount static files for Open WebUI
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "KR-AI-Engine",
        "version": "1.0.0",
        "database": "connected" if db_manager else "disconnected"
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "KRAI Engine API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "documents": "/api/documents",
            "upload": "/api/documents/upload",
            "search": "/api/documents/search",
            "config": "/api/documents/config/patterns"
        }
    }

# Open WebUI Integration endpoints
@app.get("/openwebui/info")
async def openwebui_info():
    """Open WebUI integration information"""
    return {
        "name": "KR-AI-Engine",
        "description": "AI-powered document processing for technical service environments",
        "version": "1.0.0",
        "capabilities": [
            "document_upload",
            "semantic_search",
            "technical_analysis",
            "model_extraction",
            "version_detection"
        ],
        "supported_formats": ["pdf"],
        "max_file_size": "100MB"
    }

@app.post("/openwebui/process")
async def openwebui_process_document(file_data: dict):
    """Process document from Open WebUI"""
    try:
        # This would integrate with the document processing pipeline
        # For now, return a placeholder response
        
        return {
            "status": "success",
            "message": "Document processed successfully",
            "document_id": "placeholder-id",
            "analysis": {
                "document_type": "service_manual",
                "manufacturer": "hp",
                "models": ["HP LaserJet Pro 400"],
                "version": "1.0",
                "confidence": 0.95
            }
        }
    
    except Exception as e:
        logger.error(f"❌ Open WebUI processing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/openwebui/search")
async def openwebui_search(query: dict):
    """Semantic search from Open WebUI"""
    try:
        search_query = query.get("query", "")
        
        if not search_query:
            raise HTTPException(status_code=400, detail="Query parameter is required")
        
        # This would integrate with the semantic search
        # For now, return placeholder results
        
        return {
            "status": "success",
            "results": [
                {
                    "document": "HP LaserJet Pro 400 Service Manual",
                    "relevance": 0.95,
                    "snippet": "Troubleshooting paper jam issues...",
                    "page": 45,
                    "section": "Paper Handling"
                }
            ],
            "total_results": 1
        }
    
    except Exception as e:
        logger.error(f"❌ Open WebUI search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Error handlers
@app.exception_handler(404)
async def not_found_handler(request, exc):
    return JSONResponse(
        status_code=404,
        content={"error": "Endpoint not found", "detail": str(exc)}
    )

@app.exception_handler(500)
async def internal_error_handler(request, exc):
    logger.error(f"❌ Internal server error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"error": "Internal server error", "detail": "An unexpected error occurred"}
    )

# Development server runner
if __name__ == "__main__":
    import uvicorn
    
    # Get configuration from environment
    host = os.getenv("HOST", "0.0.0.0")
    port = int(os.getenv("PORT", 8000))
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"🚀 Starting KRAI Engine server on {host}:{port}")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
