"""
Open WebUI Integration for KRAI Engine
Chat Agent with Document Processing Capabilities
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path

import httpx
from fastapi import HTTPException

logger = logging.getLogger(__name__)

class OpenWebUIIntegration:
    """Integration with Open WebUI for chat functionality"""
    
    def __init__(self, ollama_url: str = "http://localhost:11434", openwebui_url: str = "http://localhost:8080"):
        self.ollama_url = ollama_url
        self.openwebui_url = openwebui_url
        self.client = httpx.AsyncClient(timeout=30.0)
    
    async def setup_ollama_models(self):
        """Setup required Ollama models"""
        try:
            # Check if Ollama is running
            response = await self.client.get(f"{self.ollama_url}/api/tags")
            if response.status_code != 200:
                logger.error("❌ Ollama is not running or not accessible")
                return False
            
            models = response.json().get("models", [])
            model_names = [model["name"] for model in models]
            
            # Required models for KRAI Engine
            required_models = [
                "llama3.1:latest",
                "mistral:latest", 
                "codellama:latest"
            ]
            
            missing_models = [model for model in required_models if model not in model_names]
            
            if missing_models:
                logger.info(f"📥 Pulling missing models: {missing_models}")
                
                for model in missing_models:
                    logger.info(f"🔄 Pulling {model}...")
                    try:
                        # Pull model
                        pull_response = await self.client.post(
                            f"{self.ollama_url}/api/pull",
                            json={"name": model}
                        )
                        
                        if pull_response.status_code == 200:
                            logger.info(f"✅ Successfully pulled {model}")
                        else:
                            logger.warning(f"⚠️ Failed to pull {model}")
                    
                    except Exception as e:
                        logger.error(f"❌ Error pulling {model}: {e}")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Ollama setup failed: {e}")
            return False
    
    async def create_krai_chat_agent(self, agent_config: Dict = None) -> Dict:
        """Create a KRAI-specific chat agent in Open WebUI"""
        try:
            if not agent_config:
                agent_config = self._get_default_agent_config()
            
            # Create agent via Open WebUI API (if available)
            # This is a placeholder - actual implementation depends on Open WebUI API
            
            agent_data = {
                "name": "KRAI Document Assistant",
                "description": agent_config["description"],
                "system_prompt": agent_config["system_prompt"],
                "model": agent_config["model"],
                "tools": agent_config["tools"],
                "created_at": datetime.now().isoformat()
            }
            
            logger.info("✅ KRAI chat agent created")
            return agent_data
            
        except Exception as e:
            logger.error(f"❌ Failed to create chat agent: {e}")
            raise
    
    def _get_default_agent_config(self) -> Dict:
        """Get default configuration for KRAI chat agent"""
        return {
            "name": "KRAI Document Assistant",
            "description": "AI assistant for technical document processing and analysis",
            "model": "llama3.1:latest",
            "system_prompt": """You are KRAI, an AI assistant specialized in technical document processing and analysis for printer and copier service environments.

Your capabilities include:
- Analyzing service manuals, bulletins, and parts catalogs
- Identifying error codes and troubleshooting steps
- Extracting model numbers and version information
- Providing technical guidance based on document content

When users ask questions:
1. Search relevant documents in the knowledge base
2. Provide accurate, technical information
3. Cite sources and page references when possible
4. Suggest related documents or procedures
5. Ask clarifying questions if needed

Always be helpful, accurate, and professional in your responses.""",
            "tools": [
                "document_search",
                "error_code_lookup", 
                "model_information",
                "troubleshooting_guide"
            ]
        }
    
    async def process_chat_query(self, query: str, context: Dict = None) -> Dict:
        """Process a chat query with document context"""
        try:
            # This would integrate with the document search and Ollama
            # For now, return a structured response
            
            response = {
                "query": query,
                "response": f"I understand you're asking about: {query}. Let me search the technical documents for relevant information.",
                "sources": [],
                "confidence": 0.8,
                "timestamp": datetime.now().isoformat()
            }
            
            # Add context if available
            if context:
                response["context"] = context
            
            return response
            
        except Exception as e:
            logger.error(f"❌ Chat query processing failed: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    async def search_documents_for_chat(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search documents for chat context"""
        try:
            # This would use the document search API
            # For now, return mock results
            
            mock_results = [
                {
                    "document": "HP LaserJet Pro 400 Service Manual",
                    "relevance": 0.95,
                    "snippet": "Troubleshooting paper jam issues in HP LaserJet Pro 400...",
                    "page": 45,
                    "section": "Paper Handling",
                    "error_codes": ["13.01", "13.02"],
                    "models": ["HP LaserJet Pro 400"]
                }
            ]
            
            return mock_results
            
        except Exception as e:
            logger.error(f"❌ Document search failed: {e}")
            return []
    
    async def generate_response_with_ollama(self, prompt: str, context: List[Dict] = None) -> str:
        """Generate response using Ollama"""
        try:
            # Prepare the prompt with context
            full_prompt = self._prepare_prompt_with_context(prompt, context)
            
            # Call Ollama API
            ollama_request = {
                "model": "llama3.1:latest",
                "prompt": full_prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "top_p": 0.9,
                    "max_tokens": 1000
                }
            }
            
            response = await self.client.post(
                f"{self.ollama_url}/api/generate",
                json=ollama_request
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get("response", "No response generated")
            else:
                logger.error(f"❌ Ollama API error: {response.status_code}")
                return "I'm sorry, I'm having trouble generating a response right now."
                
        except Exception as e:
            logger.error(f"❌ Ollama integration failed: {e}")
            return "I'm sorry, I'm having trouble connecting to the AI model right now."
    
    def _prepare_prompt_with_context(self, query: str, context: List[Dict] = None) -> str:
        """Prepare prompt with document context"""
        prompt = f"User Query: {query}\n\n"
        
        if context:
            prompt += "Relevant Document Context:\n"
            for i, doc in enumerate(context, 1):
                prompt += f"{i}. {doc['document']} (Page {doc.get('page', 'N/A')})\n"
                prompt += f"   {doc['snippet']}\n"
                if doc.get('error_codes'):
                    prompt += f"   Error Codes: {', '.join(doc['error_codes'])}\n"
                prompt += "\n"
        
        prompt += "\nPlease provide a helpful, accurate response based on the context above. "
        prompt += "If you reference specific information, please cite the source document and page number."
        
        return prompt
    
    async def test_integration(self) -> Dict:
        """Test the Open WebUI integration"""
        try:
            results = {
                "ollama_connection": False,
                "openwebui_connection": False,
                "models_available": [],
                "agent_created": False,
                "test_query": None
            }
            
            # Test Ollama connection
            try:
                response = await self.client.get(f"{self.ollama_url}/api/tags")
                if response.status_code == 200:
                    results["ollama_connection"] = True
                    models = response.json().get("models", [])
                    results["models_available"] = [model["name"] for model in models]
            except:
                pass
            
            # Test Open WebUI connection
            try:
                response = await self.client.get(f"{self.openwebui_url}/api/health")
                if response.status_code == 200:
                    results["openwebui_connection"] = True
            except:
                pass
            
            # Test query processing
            if results["ollama_connection"]:
                test_response = await self.process_chat_query("What is the KRAI Engine?")
                results["test_query"] = test_response
            
            return results
            
        except Exception as e:
            logger.error(f"❌ Integration test failed: {e}")
            return {"error": str(e)}

# Chat Agent Class for direct integration
class KRAIChatAgent:
    """Direct chat agent implementation"""
    
    def __init__(self, document_processor, openwebui_integration):
        self.document_processor = document_processor
        self.openwebui = openwebui_integration
        self.conversation_history = []
    
    async def chat(self, user_message: str, conversation_id: str = None) -> Dict:
        """Process a chat message"""
        try:
            # Search relevant documents
            search_results = await self.openwebui.search_documents_for_chat(user_message)
            
            # Generate response with Ollama
            response = await self.openwebui.generate_response_with_ollama(
                user_message, 
                search_results
            )
            
            # Store in conversation history
            self.conversation_history.append({
                "user": user_message,
                "assistant": response,
                "sources": search_results,
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "response": response,
                "sources": search_results,
                "conversation_id": conversation_id,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"❌ Chat processing failed: {e}")
            return {
                "response": "I'm sorry, I encountered an error processing your request.",
                "error": str(e),
                "conversation_id": conversation_id
            }
    
    async def get_conversation_history(self, conversation_id: str = None) -> List[Dict]:
        """Get conversation history"""
        return self.conversation_history
    
    async def clear_history(self):
        """Clear conversation history"""
        self.conversation_history = []

# Utility functions for Open WebUI setup
async def setup_openwebui_environment():
    """Setup the complete Open WebUI environment"""
    try:
        logger.info("🚀 Setting up Open WebUI environment...")
        
        # Initialize integration
        integration = OpenWebUIIntegration()
        
        # Setup Ollama models
        ollama_ready = await integration.setup_ollama_models()
        if not ollama_ready:
            logger.warning("⚠️ Ollama setup incomplete, but continuing...")
        
        # Create chat agent
        agent = await integration.create_krai_chat_agent()
        
        # Test integration
        test_results = await integration.test_integration()
        
        logger.info("✅ Open WebUI environment setup complete")
        return {
            "integration": integration,
            "agent": agent,
            "test_results": test_results
        }
        
    except Exception as e:
        logger.error(f"❌ Open WebUI setup failed: {e}")
        raise

if __name__ == "__main__":
    # Test the integration
    async def test():
        setup_result = await setup_openwebui_environment()
        print("Setup Results:", json.dumps(setup_result["test_results"], indent=2))
    
    asyncio.run(test())
