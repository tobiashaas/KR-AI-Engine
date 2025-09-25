#!/usr/bin/env python3
"""
Test script for the complete KRAI Engine production system
"""

import asyncio
import json
import logging
from datetime import datetime
from pathlib import Path

from production_document_processor import DocumentProcessor, DatabaseManager
from openwebui_integration import OpenWebUIIntegration, setup_openwebui_environment
from config.database_config import db_config

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_system():
    """Test the complete KRAI Engine system"""
    
    logger.info("🚀 Starting KRAI Engine Production System Test")
    logger.info("=" * 60)
    
    # Initialize components
    db_manager = None
    processor = None
    openwebui_integration = None
    
    try:
        # 1. Test Database Connection
        logger.info("📊 Testing Database Connection...")
        db_manager = DatabaseManager(db_config.get_connection_string())
        await db_manager.initialize_pool()
        logger.info("✅ Database connection successful")
        
        # 2. Test Document Processor
        logger.info("🔧 Testing Document Processor...")
        processor = DocumentProcessor(db_manager)
        logger.info("✅ Document processor initialized")
        
        # 3. Test Document Processing
        test_documents = [
            "HP_E786_SM.pdf",
            "i-series remedies to fix pale, light, or faint images (RFKM_BT2511234EN).pdf",
            "Lexmark_CX825_CX860_XC8155_XC8160.pdf"
        ]
        
        test_results = []
        
        for doc_name in test_documents:
            doc_path = Path(f"../test_documents/{doc_name}")
            if doc_path.exists():
                logger.info(f"📄 Processing: {doc_name}")
                
                result = await processor.process_document(doc_path)
                test_results.append({
                    "document": doc_name,
                    "result": result
                })
                
                if result["status"] == "success":
                    logger.info(f"✅ {doc_name} processed successfully")
                    logger.info(f"   Document ID: {result['document_id']}")
                    logger.info(f"   Processing Time: {result['processing_time']:.2f}s")
                    logger.info(f"   Stats: {result['stats']}")
                else:
                    logger.warning(f"⚠️ {doc_name} processing failed: {result.get('error', 'Unknown error')}")
            else:
                logger.warning(f"⚠️ Test document not found: {doc_name}")
        
        # 4. Test Open WebUI Integration
        logger.info("🤖 Testing Open WebUI Integration...")
        try:
            openwebui_setup = await setup_openwebui_environment()
            openwebui_integration = openwebui_setup["integration"]
            
            logger.info("✅ Open WebUI integration successful")
            logger.info(f"   Test Results: {json.dumps(openwebui_setup['test_results'], indent=2)}")
            
        except Exception as e:
            logger.warning(f"⚠️ Open WebUI integration failed: {e}")
        
        # 5. Test Chat Functionality
        if openwebui_integration:
            logger.info("💬 Testing Chat Functionality...")
            
            test_queries = [
                "What error codes are mentioned in the HP documents?",
                "How do I fix paper jam issues?",
                "What models are supported by the Konica Minolta i-series?"
            ]
            
            for query in test_queries:
                logger.info(f"🤔 Testing query: {query}")
                try:
                    response = await openwebui_integration.process_chat_query(query)
                    logger.info(f"✅ Response generated: {response['response'][:100]}...")
                except Exception as e:
                    logger.warning(f"⚠️ Chat query failed: {e}")
        
        # 6. Test API Endpoints (if server is running)
        logger.info("🌐 Testing API Endpoints...")
        try:
            import httpx
            async with httpx.AsyncClient() as client:
                # Test health endpoint
                response = await client.get("http://localhost:8000/health")
                if response.status_code == 200:
                    logger.info("✅ API health check successful")
                else:
                    logger.warning(f"⚠️ API health check failed: {response.status_code}")
                
                # Test document list endpoint
                response = await client.get("http://localhost:8000/api/documents/list?limit=5")
                if response.status_code == 200:
                    docs = response.json()
                    logger.info(f"✅ API document list successful: {len(docs)} documents")
                else:
                    logger.warning(f"⚠️ API document list failed: {response.status_code}")
        
        except Exception as e:
            logger.warning(f"⚠️ API testing failed (server may not be running): {e}")
        
        # 7. Generate Test Report
        logger.info("📊 Generating Test Report...")
        
        test_report = {
            "test_timestamp": datetime.now().isoformat(),
            "database_connection": True,
            "document_processor": True,
            "openwebui_integration": openwebui_integration is not None,
            "documents_processed": len([r for r in test_results if r["result"]["status"] == "success"]),
            "processing_stats": processor.get_stats(),
            "test_results": test_results
        }
        
        # Save test report
        report_path = Path("test_report.json")
        with open(report_path, 'w') as f:
            json.dump(test_report, f, indent=2)
        
        logger.info(f"✅ Test report saved to: {report_path}")
        
        # 8. Summary
        logger.info("🎯 TEST SUMMARY")
        logger.info("=" * 40)
        logger.info(f"✅ Database Connection: {'Success' if db_manager else 'Failed'}")
        logger.info(f"✅ Document Processor: {'Success' if processor else 'Failed'}")
        logger.info(f"✅ Open WebUI Integration: {'Success' if openwebui_integration else 'Failed'}")
        logger.info(f"📄 Documents Processed: {test_report['documents_processed']}")
        logger.info(f"📈 Total Stats: {processor.get_stats()}")
        
        logger.info("🚀 KRAI Engine Production System Test Complete!")
        
    except Exception as e:
        logger.error(f"❌ System test failed: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        # Cleanup
        if db_manager:
            await db_manager.close_pool()
        logger.info("✅ Cleanup completed")

async def test_specific_document():
    """Test processing of a specific document"""
    
    doc_path = Path("../test_documents/HP_E786_SM.pdf")
    if not doc_path.exists():
        logger.error(f"❌ Test document not found: {doc_path}")
        return
    
    logger.info(f"🔍 Testing specific document: {doc_path.name}")
    
    # Initialize processor
    db_manager = DatabaseManager(db_config.get_connection_string())
    await db_manager.initialize_pool()
    processor = DocumentProcessor(db_manager)
    
    try:
        # Process document
        result = await processor.process_document(doc_path)
        
        logger.info("📊 Processing Result:")
        logger.info(f"   Status: {result['status']}")
        logger.info(f"   Document ID: {result.get('document_id', 'N/A')}")
        logger.info(f"   Processing Time: {result.get('processing_time', 0):.2f}s")
        
        if result['status'] == 'success':
            logger.info(f"   Pages: {result['stats']['pages']}")
            logger.info(f"   Chunks: {result['stats']['chunks']}")
            logger.info(f"   Embeddings: {result['stats']['embeddings']}")
            logger.info(f"   Models: {result['stats']['models']}")
            logger.info(f"   Confidence: {result['stats']['confidence']:.2f}")
        
        # Test search functionality
        if result['status'] == 'success':
            logger.info("🔍 Testing search functionality...")
            
            # This would test the semantic search
            # For now, just log that it would be tested
            logger.info("   Semantic search would be tested here")
        
    except Exception as e:
        logger.error(f"❌ Document test failed: {e}")
    
    finally:
        await db_manager.close_pool()

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "specific":
        asyncio.run(test_specific_document())
    else:
        asyncio.run(test_complete_system())
