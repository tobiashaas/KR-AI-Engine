"""
Production Main Application for KR-AI-Engine
Optimized for Apple M1 Pro with MPS and NVIDIA CUDA support
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from typing import Dict, Any, Optional
import json
from dotenv import load_dotenv

# Load environment variables from ROOT .env file (Single Source of Truth)
root_env_path = Path(__file__).parent.parent / '.env'
print(f"🔧 Loading environment from: {root_env_path}")
if root_env_path.exists():
    load_dotenv(root_env_path)
    print("✅ Environment loaded successfully")
else:
    print(f"❌ .env file not found at {root_env_path}")

from production_document_processor import ProductionDocumentProcessor
from config.production_config import config
from processing_status_manager import status_manager

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Global processor instance
processor: Optional[ProductionDocumentProcessor] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    global processor
    
    # Startup
    logger.info("🚀 Starting KR-AI-Engine Production API...")
    
    try:
        processor = ProductionDocumentProcessor()
        await processor.initialize()
        logger.info("✅ KR-AI-Engine Production API initialized successfully")
        yield
    except Exception as e:
        logger.error(f"❌ Failed to initialize KR-AI-Engine: {e}")
        raise
    finally:
        # Shutdown
        if processor:
            await processor.close()
        logger.info("✅ KR-AI-Engine Production API shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="KR-AI-Engine Production API",
    description="AI-powered document processing with GPU acceleration",
    version="2.0.0",
    lifespan=lifespan
)

# Mount static files for status monitor
app.mount("/static", StaticFiles(directory="static"), name="static")

# Add CORS middleware
allowed_origins = os.getenv("ALLOWED_ORIGINS", "http://localhost:3000,http://localhost:8001,http://127.0.0.1:54323").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins if not os.getenv("DEBUG", "false").lower() == "true" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "KR-AI-Engine Production API",
        "version": "2.0.0",
        "status": "running",
        "gpu_support": True
    }

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        stats = await processor.get_processing_stats()
        return {
            "status": "healthy",
            "service": "KR-AI-Engine Production",
            "version": "2.0.0",
            "gpu_device": config.device_config["device"],
            "device_name": config.device_config["device_name"],
            "memory_gb": config.device_config["memory_gb"],
            "stats": stats
        }
    except Exception as e:
        logger.error(f"❌ Health check failed: {e}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {e}")

@app.get("/config")
async def get_config():
    """Get production configuration"""
    return {
        "system_info": config.system_info,
        "device_config": config.device_config,
        "model_config": config.model_config,
        "performance_config": config.performance_config,
        "ollama_config": config.get_ollama_config()
    }

@app.post("/api/production/error-images/upload")
async def upload_error_image(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    manufacturer: Optional[str] = Form(None),
    product_model: Optional[str] = Form(None),
    technician_id: Optional[str] = Form(None)
):
    """Upload error/defect images for AI/ML training (DSGVO compliant)"""
    try:
        # Validate file type
        if not file.filename.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.webp')):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Read file content
        file_content = await file.read()
        
        logger.info(f"🚨 Processing error image upload: {file.filename}")
        
        # TODO: Implement DSGVO anonymization and storage
        # This would include:
        # 1. AI-based anonymization (blur faces, remove personal data)
        # 2. Store in krai-images bucket (schema-compliant)
        # 3. Log for ML training purposes
        
        return {
            "message": "Error image upload endpoint ready",
            "filename": file.filename,
            "size": len(file_content),
            "note": "DSGVO anonymization and AI/ML storage to be implemented"
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Error image upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@app.post("/api/production/documents/upload")
async def upload_document(
    file: UploadFile = File(...),
    document_type: Optional[str] = Form(None),
    manufacturer: Optional[str] = Form(None),
    models: Optional[str] = Form(None)
):
    """Upload and process a document with production pipeline"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        # Read file content
        file_content = await file.read()
        file_path = Path(file.filename)
        
        logger.info(f"🚀 Processing document: {file.filename}")
        
        # Process document with production pipeline
        result = await processor.process_document(file_path, file_content)
        
        if result["status"] == "error":
            raise HTTPException(status_code=500, detail=f"Processing failed: {result['error']}")
        
        return {
            "message": "Document processed successfully",
            "document_id": result["document_id"],
            "processing_time": result["processing_time"],
            "stats": result["stats"],
            "gpu_used": result["gpu_used"],
            "performance_metrics": result["performance_metrics"]
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Document upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {e}")

@app.get("/api/production/documents/stats")
async def get_processing_stats():
    """Get processing statistics"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        stats = await processor.get_processing_stats()
        return stats
    except Exception as e:
        logger.error(f"❌ Failed to get stats: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get stats: {e}")

@app.get("/api/production/processing/status")
async def get_all_processing_status():
    """Get all active processing statuses"""
    try:
        active_processes = await status_manager.get_all_active_processes()
        processing_summary = await status_manager.get_processing_summary()
        
        return {
            "active_processes": active_processes,
            "summary": processing_summary
        }
    except Exception as e:
        logger.error(f"❌ Failed to get processing status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing status: {e}")

@app.get("/api/production/processing/status/{process_id}")
async def get_processing_status(process_id: str):
    """Get status for a specific process"""
    try:
        status = await status_manager.get_process_status(process_id)
        if not status:
            raise HTTPException(status_code=404, detail="Process not found")
        
        return status
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Failed to get process status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get process status: {e}")

@app.get("/api/production/processing/summary")
async def get_processing_summary():
    """Get a summary of processing activities"""
    try:
        summary = await status_manager.get_processing_summary()
        return summary
    except Exception as e:
        logger.error(f"❌ Failed to get processing summary: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get processing summary: {e}")

@app.get("/status", response_class=HTMLResponse)
async def status_monitor():
    """Status monitoring page"""
    try:
        with open("static/status_monitor.html", "r", encoding="utf-8") as f:
            return HTMLResponse(content=f.read())
    except Exception as e:
        return HTMLResponse(content=f"<h1>Error loading status monitor: {e}</h1>", status_code=500)

@app.get("/api/production/models/status")
async def get_models_status():
    """Get status of AI models"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        import httpx
        
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{config.get_ollama_config()['base_url']}/api/tags")
            
            if response.status_code == 200:
                models = response.json().get("models", [])
                
                # Check required models
                required_models = [
                    config.model_config["llm"]["model_name"],
                    config.model_config["embedding"]["model_name"],
                    config.model_config["vision"]["model_name"]
                ]
                
                model_status = {}
                for required in required_models:
                    available = any(required in model["name"] for model in models)
                    model_status[required] = {
                        "available": available,
                        "status": "loaded" if available else "not_found"
                    }
                
                return {
                    "total_models": len(models),
                    "required_models": model_status,
                    "available_models": [model["name"] for model in models]
                }
            else:
                raise Exception(f"Ollama API returned {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Failed to get model status: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get model status: {e}")

@app.post("/api/production/chat")
async def chat_with_documents(
    query: str = Form(...),
    document_ids: Optional[str] = Form(None)
):
    """Chat with processed documents using Ollama"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        import httpx
        
        # Build context from documents if specified
        context = ""
        if document_ids:
            # TODO: Implement document context retrieval
            context = "Document context will be added here"
        
        # Prepare chat prompt
        system_prompt = """You are KR-AI, an AI assistant specialized in printer and technical document analysis. 
        You help users with troubleshooting, error codes, part numbers, and technical specifications.
        Always provide accurate, helpful information based on the provided context."""
        
        chat_prompt = f"{system_prompt}\n\nContext: {context}\n\nUser: {query}"
        
        # Call Ollama LLM API
        ollama_config = config.get_ollama_config()
        payload = {
            "model": config.model_config["llm"]["model_name"],
            "prompt": chat_prompt,
            "stream": False,
            "options": {
                "temperature": config.model_config["llm"]["temperature"],
                "max_tokens": config.model_config["llm"]["max_tokens"],
                "top_p": config.model_config["llm"]["top_p"],
                "repeat_penalty": config.model_config["llm"]["repeat_penalty"]
            }
        }
        
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ollama_config['base_url']}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "response": result.get("response", ""),
                    "model": config.model_config["llm"]["model_name"],
                    "processing_time": result.get("total_duration", 0) / 1e9,  # Convert to seconds
                    "tokens_generated": result.get("eval_count", 0)
                }
            else:
                raise Exception(f"Ollama API returned {response.status_code}")
                
    except Exception as e:
        logger.error(f"❌ Chat failed: {e}")
        raise HTTPException(status_code=500, detail=f"Chat failed: {e}")

@app.post("/api/production/vision/analyze")
async def analyze_image(
    file: UploadFile = File(...),
    prompt: str = Form("Analyze this technical document image. Describe any diagrams, charts, error codes, part numbers, or technical specifications you can identify.")
):
    """Analyze image with Vision AI"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        import httpx
        import base64
        
        # Validate file type
        if not file.content_type.startswith('image/'):
            raise HTTPException(status_code=400, detail="Only image files are supported")
        
        # Read and encode image
        image_content = await file.read()
        image_b64 = base64.b64encode(image_content).decode('utf-8')
        
        # Call Ollama Vision API
        payload = {
            "model": config.model_config["vision"]["model_name"],
            "prompt": prompt,
            "images": [image_b64],
            "stream": False,
            "options": {
                "temperature": 0.3,
                "max_new_tokens": config.model_config["vision"]["max_new_tokens"]
            }
        }
        
        ollama_config = config.get_ollama_config()
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{ollama_config['base_url']}/api/generate",
                json=payload,
                timeout=120
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "analysis": result.get("response", ""),
                    "model": config.model_config["vision"]["model_name"],
                    "processing_time": result.get("total_duration", 0) / 1e9,
                    "image_size": len(image_content),
                    "prompt_used": prompt
                }
            else:
                raise Exception(f"Vision API returned {response.status_code}")
                
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Vision analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"Vision analysis failed: {e}")

@app.get("/api/production/performance")
async def get_performance_metrics():
    """Get performance metrics"""
    if not processor:
        raise HTTPException(status_code=503, detail="Processor not initialized")
    
    try:
        stats = await processor.get_processing_stats()
        
        # Calculate performance metrics
        uptime = stats["uptime_seconds"]
        docs_per_hour = (stats["documents_processed"] / uptime) * 3600 if uptime > 0 else 0
        chunks_per_hour = (stats["chunks_created"] / uptime) * 3600 if uptime > 0 else 0
        embeddings_per_hour = (stats["embeddings_generated"] / uptime) * 3600 if uptime > 0 else 0
        
        return {
            "performance_metrics": {
                "documents_per_hour": docs_per_hour,
                "chunks_per_hour": chunks_per_hour,
                "embeddings_per_hour": embeddings_per_hour,
                "error_rate": stats["errors"] / max(stats["documents_processed"], 1),
                "uptime_hours": uptime / 3600
            },
            "system_metrics": {
                "device": config.device_config["device"],
                "device_name": config.device_config["device_name"],
                "memory_gb": config.device_config["memory_gb"],
                "batch_size": config.device_config["batch_size"],
                "workers": config.device_config["num_workers"]
            },
            "current_stats": stats
        }
        
    except Exception as e:
        logger.error(f"❌ Failed to get performance metrics: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to get performance metrics: {e}")

if __name__ == "__main__":
    import uvicorn
    
    # Print configuration
    config.print_config_summary()
    
    # Run the application
    uvicorn.run(
        "production_main:app",
        host=os.getenv("KRAI_API_HOST", "0.0.0.0"),
        port=int(os.getenv("KRAI_API_PORT", 8001)),
        reload=False,
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )
