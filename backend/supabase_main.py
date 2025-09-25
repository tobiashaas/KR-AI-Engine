"""
KRAI Engine - Supabase Main FastAPI Application
Production Document Processing with Supabase Integration
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

from api.supabase_document_api import router as supabase_document_router
from config.supabase_config import SupabaseConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global variables for app lifespan management
processor = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global processor
    
    logger.info("🚀 Starting KRAI Engine with Supabase...")
    
    try:
        # Initialize Supabase configuration
        supabase_config = SupabaseConfig()
        
        # Initialize Supabase document processor
        from supabase_document_processor import SupabaseDocumentProcessor
        
        processor = SupabaseDocumentProcessor()
        await processor.initialize()
        
        logger.info("✅ KRAI Engine with Supabase initialized successfully")
        
        yield
        
    except Exception as e:
        logger.error(f"❌ Failed to initialize KRAI Engine with Supabase: {e}")
        raise
    
    finally:
        # Cleanup
        if processor:
            await processor.close()
        logger.info("✅ KRAI Engine with Supabase shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="KRAI Engine - Supabase",
    description="AI-powered document processing system with Supabase integration for technical service environments",
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
app.include_router(supabase_document_router)

# Mount static files
static_dir = Path("static")
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint with Supabase status"""
    global processor
    
    supabase_config = SupabaseConfig()
    
    return {
        "status": "healthy",
        "service": "KRAI Engine - Supabase",
        "version": "1.0.0",
        "database": "connected" if processor else "disconnected",
        "supabase_url": supabase_config.supabase_url,
        "storage_buckets": {
            "documents": supabase_config.config['storage_bucket'],
            "images": supabase_config.config['image_bucket']
        }
    }

# Root endpoint
@app.get("/")
async def root():
    """Root endpoint with API information"""
    return {
        "message": "KRAI Engine API - Supabase Integration",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/health",
        "endpoints": {
            "supabase_documents": "/api/supabase/documents",
            "upload": "/api/supabase/documents/upload",
            "search": "/api/supabase/documents/search",
            "images": "/api/supabase/documents/{id}/images",
            "storage_info": "/api/supabase/documents/storage/info"
        }
    }

# Supabase-specific endpoints
@app.get("/supabase/info")
async def supabase_info():
    """Supabase integration information"""
    supabase_config = SupabaseConfig()
    
    return {
        "supabase_url": supabase_config.supabase_url,
        "storage_buckets": {
            "documents": supabase_config.config['storage_bucket'],
            "images": supabase_config.config['image_bucket']
        },
        "features": [
            "document_storage",
            "image_storage", 
            "hash_based_deduplication",
            "semantic_search",
            "technical_analysis",
            "model_extraction",
            "version_detection"
        ],
        "supported_formats": ["pdf"],
        "max_file_size": "100MB",
        "image_formats": ["jpeg", "png", "gif", "webp"]
    }

@app.get("/supabase/storage/buckets")
async def list_storage_buckets():
    """List Supabase storage buckets"""
    try:
        from config.supabase_config import SupabaseStorage
        
        supabase_config = SupabaseConfig()
        storage = SupabaseStorage(supabase_config)
        
        # This would list buckets via Supabase API
        # For now, return configured buckets
        return {
            "buckets": [
                {
                    "name": supabase_config.config['storage_bucket'],
                    "type": "documents",
                    "public": True,
                    "file_size_limit": "100MB"
                },
                {
                    "name": supabase_config.config['image_bucket'],
                    "type": "images", 
                    "public": True,
                    "file_size_limit": "50MB"
                }
            ]
        }
    
    except Exception as e:
        logger.error(f"❌ Failed to list storage buckets: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/supabase/storage/setup")
async def setup_storage_buckets():
    """Setup Supabase storage buckets"""
    try:
        from config.supabase_config import SupabaseStorage
        
        supabase_config = SupabaseConfig()
        storage = SupabaseStorage(supabase_config)
        
        success = await storage.setup_storage_buckets()
        
        if success:
            return {
                "status": "success",
                "message": "Storage buckets created successfully",
                "buckets": [
                    supabase_config.config['storage_bucket'],
                    supabase_config.config['image_bucket']
                ]
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to create storage buckets")
    
    except Exception as e:
        logger.error(f"❌ Storage setup failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/supabase/database/schema")
async def get_database_schema():
    """Get database schema information"""
    global processor
    
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        async with processor.db_pool.acquire() as conn:
            # Get table information
            tables_query = """
                SELECT 
                    schemaname,
                    tablename,
                    tableowner
                FROM pg_tables 
                WHERE schemaname LIKE 'krai_%'
                ORDER BY schemaname, tablename
            """
            tables = await conn.fetch(tables_query)
            
            # Get schema information
            schemas_query = """
                SELECT 
                    schema_name,
                    schema_owner
                FROM information_schema.schemata
                WHERE schema_name LIKE 'krai_%'
                ORDER BY schema_name
            """
            schemas = await conn.fetch(schemas_query)
        
        return {
            "schemas": [dict(row) for row in schemas],
            "tables": [dict(row) for row in tables],
            "total_schemas": len(schemas),
            "total_tables": len(tables)
        }
    
    except Exception as e:
        logger.error(f"❌ Database schema retrieval failed: {e}")
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
    port = int(os.getenv("PORT", 8001))  # Different port for Supabase version
    reload = os.getenv("RELOAD", "false").lower() == "true"
    
    logger.info(f"🚀 Starting KRAI Engine Supabase server on {host}:{port}")
    
    uvicorn.run(
        "supabase_main:app",
        host=host,
        port=port,
        reload=reload,
        log_level="info"
    )
