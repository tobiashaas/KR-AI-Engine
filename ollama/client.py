"""
🤖 Ollama Integration for KRAI
Local AI model management and interaction
"""

import httpx
import asyncio
import json
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class OllamaClient:
    """Ollama API client for local AI models"""
    
    def __init__(self, base_url: str = "http://localhost:11434"):
        self.base_url = base_url
        self.client = httpx.AsyncClient(timeout=300.0)  # 5 minutes for model operations
        
    async def check_connection(self) -> bool:
        """Check if Ollama is running and accessible"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            return response.status_code == 200
        except Exception as e:
            logger.error(f"Ollama connection failed: {str(e)}")
            return False
    
    async def list_models(self) -> List[Dict[str, Any]]:
        """Get list of available models"""
        try:
            response = await self.client.get(f"{self.base_url}/api/tags")
            response.raise_for_status()
            return response.json().get("models", [])
        except Exception as e:
            logger.error(f"Failed to list models: {str(e)}")
            return []
    
    async def generate_text(self, model: str, prompt: str, **kwargs) -> str:
        """Generate text using specified model"""
        try:
            data = {
                "model": model,
                "prompt": prompt,
                "stream": False,
                **kwargs
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Text generation failed: {str(e)}")
            raise
    
    async def analyze_image(self, model: str, image_path: str, prompt: str) -> str:
        """Analyze image using vision model"""
        try:
            # Read image as base64
            import base64
            with open(image_path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
            
            data = {
                "model": model,
                "prompt": prompt,
                "images": [image_data],
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/generate",
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("response", "")
            
        except Exception as e:
            logger.error(f"Image analysis failed: {str(e)}")
            raise
    
    async def generate_embeddings(self, model: str, text: str) -> List[float]:
        """Generate embeddings using embedding model"""
        try:
            data = {
                "model": model,
                "prompt": text
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/embeddings",
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("embedding", [])
            
        except Exception as e:
            logger.error(f"Embedding generation failed: {str(e)}")
            raise
    
    async def pull_model(self, model_name: str) -> bool:
        """Download/pull a model"""
        try:
            data = {"name": model_name}
            
            async with self.client.stream(
                "POST",
                f"{self.base_url}/api/pull",
                json=data
            ) as response:
                async for line in response.aiter_lines():
                    if line.strip():
                        status = json.loads(line)
                        logger.info(f"Pull status: {status}")
            
            return True
            
        except Exception as e:
            logger.error(f"Model pull failed: {str(e)}")
            return False
    
    async def chat(self, model: str, messages: List[Dict[str, str]]) -> str:
        """Chat interface for conversation models"""
        try:
            data = {
                "model": model,
                "messages": messages,
                "stream": False
            }
            
            response = await self.client.post(
                f"{self.base_url}/api/chat",
                json=data
            )
            response.raise_for_status()
            
            result = response.json()
            return result.get("message", {}).get("content", "")
            
        except Exception as e:
            logger.error(f"Chat failed: {str(e)}")
            raise
    
    async def get_model_info(self, model_name: str) -> Dict[str, Any]:
        """Get detailed information about a model"""
        try:
            response = await self.client.post(
                f"{self.base_url}/api/show",
                json={"name": model_name}
            )
            response.raise_for_status()
            return response.json()
            
        except Exception as e:
            logger.error(f"Failed to get model info: {str(e)}")
            return {}
    
    async def cleanup(self):
        """Close HTTP client"""
        await self.client.aclose()

# Global Ollama client instance
ollama_client = OllamaClient()

# Model configurations
MODELS = {
    "text": {
        "primary": "llama3.1:8b",
        "fast": "mistral:7b"
    },
    "vision": {
        "general": "llava:7b",
        "technical": "bakllava:7b"
    },
    "embeddings": {
        "default": "nomic-embed-text:latest"
    }
}

async def get_default_text_model() -> str:
    """Get the default text model"""
    return MODELS["text"]["primary"]

async def get_default_vision_model() -> str:
    """Get the default vision model"""
    return MODELS["vision"]["general"]

async def get_default_embedding_model() -> str:
    """Get the default embedding model"""
    return MODELS["embeddings"]["default"]