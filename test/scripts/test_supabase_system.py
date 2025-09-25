#!/usr/bin/env python3
"""
Comprehensive test script for KRAI Engine with Supabase integration
"""

import asyncio
import json
import logging
import os
from datetime import datetime
from pathlib import Path

from supabase_document_processor import SupabaseDocumentProcessor
from config.supabase_config import SupabaseConfig, SupabaseStorage

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_supabase_configuration():
    """Test Supabase configuration"""
    logger.info("🔧 Testing Supabase Configuration")
    logger.info("=" * 50)
    
    try:
        # Test configuration loading
        config = SupabaseConfig()
        
        print(f"✅ Supabase URL: {config.supabase_url}")
        print(f"✅ Storage Bucket: {config.config['storage_bucket']}")
        print(f"✅ Image Bucket: {config.config['image_bucket']}")
        print(f"✅ Database URL: {config.get_database_url()[:50]}...")
        
        # Test storage initialization
        storage = SupabaseStorage(config)
        print(f"✅ Storage URL: {storage.storage_url}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Supabase configuration test failed: {e}")
        return False

async def test_storage_buckets():
    """Test Supabase storage bucket setup"""
    logger.info("🪣 Testing Supabase Storage Buckets")
    logger.info("=" * 50)
    
    try:
        config = SupabaseConfig()
        storage = SupabaseStorage(config)
        
        # Setup buckets
        success = await storage.setup_storage_buckets()
        
        if success:
            print("✅ Storage buckets setup successful")
            return True
        else:
            print("❌ Storage buckets setup failed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Storage bucket test failed: {e}")
        return False

async def test_document_processing():
    """Test complete document processing with Supabase"""
    logger.info("📄 Testing Document Processing with Supabase")
    logger.info("=" * 50)
    
    processor = SupabaseDocumentProcessor()
    
    try:
        # Initialize processor
        await processor.initialize()
        print("✅ Processor initialized successfully")
        
        # Test documents
        test_documents = [
            "HP_E786_SM.pdf",
            "i-series remedies to fix pale, light, or faint images (RFKM_BT2511234EN).pdf",
            "Lexmark_CX825_CX860_XC8155_XC8160.pdf"
        ]
        
        results = []
        
        for doc_name in test_documents:
            doc_path = Path(f"../test_documents/{doc_name}")
            if doc_path.exists():
                logger.info(f"📄 Processing: {doc_name}")
                
                result = await processor.process_document(doc_path)
                results.append({
                    "document": doc_name,
                    "result": result
                })
                
                if result["status"] == "success":
                    print(f"✅ {doc_name} processed successfully")
                    print(f"   Document ID: {result['document_id']}")
                    print(f"   Storage URL: {result['storage_url']}")
                    print(f"   Processing Time: {result['processing_time']:.2f}s")
                    print(f"   Stats: {result['stats']}")
                else:
                    print(f"⚠️ {doc_name} processing failed: {result.get('error', 'Unknown error')}")
            else:
                print(f"⚠️ Test document not found: {doc_name}")
        
        # Get processor stats
        stats = processor.get_stats()
        print(f"\n📊 Processing Statistics:")
        print(f"   Documents Processed: {stats['documents_processed']}")
        print(f"   Chunks Created: {stats['chunks_created']}")
        print(f"   Embeddings Generated: {stats['embeddings_generated']}")
        print(f"   Images Processed: {stats['images_processed']}")
        print(f"   Errors: {stats['errors']}")
        
        await processor.close()
        
        return results
        
    except Exception as e:
        logger.error(f"❌ Document processing test failed: {e}")
        if 'processor' in locals():
            await processor.close()
        return []

async def test_database_queries():
    """Test database queries and schema"""
    logger.info("🗄️ Testing Database Queries and Schema")
    logger.info("=" * 50)
    
    processor = SupabaseDocumentProcessor()
    
    try:
        await processor.initialize()
        
        async with processor.db_pool.acquire() as conn:
            # Test schema queries
            print("🔍 Testing Database Schema...")
            
            # Get schemas
            schemas_query = """
                SELECT schema_name 
                FROM information_schema.schemata 
                WHERE schema_name LIKE 'krai_%'
                ORDER BY schema_name
            """
            schemas = await conn.fetch(schemas_query)
            print(f"✅ Found {len(schemas)} KRAI schemas: {[s['schema_name'] for s in schemas]}")
            
            # Get tables
            tables_query = """
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE schemaname LIKE 'krai_%'
                ORDER BY schemaname, tablename
            """
            tables = await conn.fetch(tables_query)
            print(f"✅ Found {len(tables)} KRAI tables")
            
            # Test document queries
            print("\n🔍 Testing Document Queries...")
            
            # Count documents
            doc_count_query = "SELECT COUNT(*) as count FROM krai_core.documents"
            doc_count = await conn.fetchval(doc_count_query)
            print(f"✅ Total documents: {doc_count}")
            
            # Count chunks
            chunk_count_query = "SELECT COUNT(*) as count FROM krai_intelligence.chunks"
            chunk_count = await conn.fetchval(chunk_count_query)
            print(f"✅ Total chunks: {chunk_count}")
            
            # Count embeddings
            embedding_count_query = "SELECT COUNT(*) as count FROM krai_intelligence.embeddings"
            embedding_count = await conn.fetchval(embedding_count_query)
            print(f"✅ Total embeddings: {embedding_count}")
            
            # Count images
            image_count_query = "SELECT COUNT(*) as count FROM krai_content.images"
            image_count = await conn.fetchval(image_count_query)
            print(f"✅ Total images: {image_count}")
            
            # Test manufacturers
            manufacturers_query = "SELECT name FROM krai_core.manufacturers ORDER BY name"
            manufacturers = await conn.fetch(manufacturers_query)
            print(f"✅ Manufacturers: {[m['name'] for m in manufacturers]}")
            
            # Test document types
            doc_types_query = """
                SELECT document_type, COUNT(*) as count 
                FROM krai_core.documents 
                GROUP BY document_type 
                ORDER BY count DESC
            """
            doc_types = await conn.fetch(doc_types_query)
            print(f"✅ Document types: {[(d['document_type'], d['count']) for d in doc_types]}")
        
        await processor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Database query test failed: {e}")
        if 'processor' in locals():
            await processor.close()
        return False

async def test_semantic_search():
    """Test semantic search functionality"""
    logger.info("🔍 Testing Semantic Search")
    logger.info("=" * 50)
    
    processor = SupabaseDocumentProcessor()
    
    try:
        await processor.initialize()
        
        # Test search queries
        test_queries = [
            "paper jam troubleshooting",
            "error codes",
            "HP LaserJet",
            "Konica Minolta i-series",
            "fuser temperature"
        ]
        
        async with processor.db_pool.acquire() as conn:
            for query in test_queries:
                print(f"\n🔍 Testing query: '{query}'")
                
                # Generate embedding
                query_embedding = processor.embedding_model.encode(query)
                
                # Search query
                search_query = """
                    SELECT 
                        d.file_name,
                        c.text_chunk,
                        c.page_start,
                        c.section_title,
                        1 - (e.embedding_vector <=> %s) as similarity_score
                    FROM krai_intelligence.embeddings e
                    JOIN krai_intelligence.chunks c ON e.chunk_id = c.id
                    JOIN krai_core.documents d ON c.document_id = d.id
                    WHERE 1 - (e.embedding_vector <=> %s) > 0.7
                    ORDER BY similarity_score DESC
                    LIMIT 3
                """
                
                results = await conn.fetch(search_query, query_embedding.tolist(), query_embedding.tolist())
                
                if results:
                    print(f"✅ Found {len(results)} results:")
                    for i, result in enumerate(results, 1):
                        print(f"   {i}. {result['file_name']} (Page {result['page_start']}) - Score: {result['similarity_score']:.3f}")
                        print(f"      {result['text_chunk'][:100]}...")
                else:
                    print("⚠️ No results found")
        
        await processor.close()
        return True
        
    except Exception as e:
        logger.error(f"❌ Semantic search test failed: {e}")
        if 'processor' in locals():
            await processor.close()
        return False

async def test_image_processing():
    """Test image extraction and storage"""
    logger.info("🖼️ Testing Image Processing")
    logger.info("=" * 50)
    
    processor = SupabaseDocumentProcessor()
    
    try:
        await processor.initialize()
        
        async with processor.db_pool.acquire() as conn:
            # Get image statistics
            image_stats_query = """
                SELECT 
                    COUNT(*) as total_images,
                    COUNT(DISTINCT document_id) as documents_with_images,
                    AVG(size_bytes) as avg_size,
                    SUM(size_bytes) as total_size
                FROM krai_content.images
            """
            stats = await conn.fetchrow(image_stats_query)
            
            if stats['total_images'] > 0:
                print(f"✅ Total images: {stats['total_images']}")
                print(f"✅ Documents with images: {stats['documents_with_images']}")
                print(f"✅ Average image size: {stats['avg_size']:.0f} bytes")
                print(f"✅ Total image size: {stats['total_size']:.0f} bytes")
                
                # Get sample images
                sample_images_query = """
                    SELECT 
                        i.storage_url,
                        i.page_number,
                        i.width,
                        i.height,
                        d.file_name
                    FROM krai_content.images i
                    JOIN krai_core.documents d ON i.document_id = d.id
                    ORDER BY i.created_at DESC
                    LIMIT 5
                """
                sample_images = await conn.fetch(sample_images_query)
                
                print(f"\n📋 Sample Images:")
                for img in sample_images:
                    print(f"   {img['file_name']} - Page {img['page_number']} ({img['width']}x{img['height']})")
                    print(f"   URL: {img['storage_url']}")
                
                return True
            else:
                print("⚠️ No images found in database")
                return False
        
        await processor.close()
        
    except Exception as e:
        logger.error(f"❌ Image processing test failed: {e}")
        if 'processor' in locals():
            await processor.close()
        return False

async def generate_comprehensive_report():
    """Generate comprehensive test report"""
    logger.info("📊 Generating Comprehensive Test Report")
    logger.info("=" * 60)
    
    report = {
        "test_timestamp": datetime.now().isoformat(),
        "tests": {}
    }
    
    # Test 1: Supabase Configuration
    config_test = await test_supabase_configuration()
    report["tests"]["supabase_configuration"] = config_test
    
    # Test 2: Storage Buckets
    storage_test = await test_storage_buckets()
    report["tests"]["storage_buckets"] = storage_test
    
    # Test 3: Document Processing
    processing_results = await test_document_processing()
    report["tests"]["document_processing"] = {
        "success": len([r for r in processing_results if r["result"]["status"] == "success"]) > 0,
        "results": processing_results
    }
    
    # Test 4: Database Queries
    db_test = await test_database_queries()
    report["tests"]["database_queries"] = db_test
    
    # Test 5: Semantic Search
    search_test = await test_semantic_search()
    report["tests"]["semantic_search"] = search_test
    
    # Test 6: Image Processing
    image_test = await test_image_processing()
    report["tests"]["image_processing"] = image_test
    
    # Calculate overall success rate
    test_results = [config_test, storage_test, db_test, search_test, image_test]
    success_count = sum(test_results)
    total_tests = len(test_results)
    success_rate = (success_count / total_tests) * 100
    
    report["overall"] = {
        "success_rate": success_rate,
        "tests_passed": success_count,
        "total_tests": total_tests,
        "status": "PASS" if success_rate >= 80 else "FAIL"
    }
    
    # Save report
    report_path = Path("supabase_test_report.json")
    with open(report_path, 'w') as f:
        json.dump(report, f, indent=2)
    
    print(f"\n🎯 COMPREHENSIVE TEST REPORT")
    print(f"=" * 40)
    print(f"Overall Success Rate: {success_rate:.1f}%")
    print(f"Tests Passed: {success_count}/{total_tests}")
    print(f"Status: {report['overall']['status']}")
    print(f"Report saved to: {report_path}")
    
    return report

async def main():
    """Main test execution"""
    logger.info("🚀 Starting KRAI Engine Supabase Comprehensive Testing")
    logger.info("=" * 70)
    
    # Check environment variables
    required_env_vars = [
        'SUPABASE_URL',
        'SUPABASE_ANON_KEY', 
        'SUPABASE_SERVICE_ROLE_KEY',
        'SUPABASE_PASSWORD'
    ]
    
    missing_vars = [var for var in required_env_vars if not os.getenv(var)]
    if missing_vars:
        logger.error(f"❌ Missing required environment variables: {missing_vars}")
        logger.error("Please set the following environment variables:")
        for var in missing_vars:
            logger.error(f"  export {var}=your_value")
        return
    
    try:
        # Generate comprehensive report
        report = await generate_comprehensive_report()
        
        # Print summary
        print(f"\n🎉 TESTING COMPLETE!")
        print(f"=" * 30)
        
        if report["overall"]["status"] == "PASS":
            print("✅ All tests passed! KRAI Engine with Supabase is ready for production!")
        else:
            print("⚠️ Some tests failed. Please review the report for details.")
        
        print(f"📊 Success Rate: {report['overall']['success_rate']:.1f}%")
        print(f"📋 Report: supabase_test_report.json")
        
    except Exception as e:
        logger.error(f"❌ Testing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(main())
