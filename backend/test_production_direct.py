#!/usr/bin/env python3
"""
Direct test of production processing without Supabase Storage
"""

import asyncio
import json
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent / "test" / "backend-tests"))

from production_document_processor import ProductionDocumentProcessor

async def test_direct_processing():
    """Test direct processing without Supabase Storage"""
    
    pdf_path = Path("../HP_X580_SM.pdf")
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"📄 Testing: {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    processor = ProductionDocumentProcessor()
    await processor.initialize()
    
    print(f"🤖 LLM Model: {processor.llm_model}")
    print(f"👁️ Vision Model: {processor.vision_model}")  
    print(f"🧠 Embedding Model: {processor.embedding_model_name}")
    print(f"💾 Database: {'✅ Connected' if processor.db_pool else '❌ Not connected'}")
    
    try:
        # Read file content
        with open(pdf_path, 'rb') as f:
            file_content = f.read()
        
        print("\n🚀 Starting direct processing pipeline...")
        
        # 1. Extract content
        print("📄 1. Extracting content...")
        content_result = await processor._extract_content_with_gpu(file_content)
        print(f"   ✅ Extracted {len(content_result['text'])} characters")
        print(f"   ✅ Found {len(content_result['images'])} images")
        
        # 2. Classification
        print("🏷️ 2. Classifying document...")
        classification = processor._classify_document(pdf_path.name, content_result['text'])
        print(f"   ✅ Manufacturer: {classification['manufacturer']}")
        print(f"   ✅ Type: {classification['document_type']}")
        print(f"   ✅ Models: {len(classification.get('models', []))} detected")
        
        # 3. Store in database (bypass storage)
        print("💾 3. Storing in database...")
        
        # Check for duplicates by hash first!
        file_hash = processor._calculate_file_hash(file_content)
        
        async with processor.db_pool.acquire() as conn:
            existing_doc = await conn.fetchval(
                "SELECT id FROM krai_core.documents WHERE file_hash = $1 LIMIT 1",
                file_hash
            )
            if existing_doc:
                print(f"   🔄 Document with hash {file_hash[:16]}... already exists: {existing_doc}")
                print(f"   ⏭️ Skipping duplicate document processing!")
                return
        
        # Get manufacturer ID  
        manufacturer_name = classification['manufacturer']
        async with processor.db_pool.acquire() as conn:
            manufacturer_id = await conn.fetchval(
                "SELECT id FROM krai_core.manufacturers WHERE name = $1",
                manufacturer_name
            )
            if not manufacturer_id:
                print(f"   ⚠️ Creating manufacturer: {manufacturer_name}")
                manufacturer_id = await conn.fetchval(
                    "INSERT INTO krai_core.manufacturers (name, display_name) VALUES ($1, $2) RETURNING id",
                    manufacturer_name, manufacturer_name.upper()
                )
        
            # Store document (only if not duplicate!)
            document_id = await conn.fetchval(
                """
                INSERT INTO krai_core.documents 
                (manufacturer_id, title, document_type, version, file_size, file_hash, storage_url, processing_status, metadata)
                VALUES ($1, $2, $3, $4, $5, $6, $7, 'processing', $8)
                RETURNING id
                """,
                manufacturer_id,
                pdf_path.name,
                classification['document_type'],
                classification.get('version', ''),
                len(file_content),
                file_hash,
                f"local://documents/{pdf_path.name}",
                json.dumps({'models': classification.get('models', []), 'analysis': classification})
            )
            
        print(f"   ✅ Document stored: {document_id}")
        
        # 4. Create chunks
        print("📝 4. Creating chunks...")
        chunk_result = await processor._process_chunks_with_gpu(str(document_id), content_result['text'], classification)
        chunks = chunk_result.get('chunks', [])
        chunk_ids = chunk_result.get('chunk_ids', [])
        print(f"   ✅ Created & stored {len(chunks)} chunks")
        
        # 6. Generate embeddings (with deduplication check)
        print("🧠 6. Generating embeddings...")
        embedding_result = await processor._generate_embeddings_with_gpu(str(document_id), chunks)
        
        if embedding_result.get('skipped', False):
            print(f"   🔄 Found {embedding_result['existing_count']} existing embeddings, skipped generation")
        else:
            print(f"   ✅ Generated and stored {len(embedding_result.get('embedding_ids', []))} new embeddings")
        
        # Update document status
        async with processor.db_pool.acquire() as conn:
            await conn.execute(
                "UPDATE krai_core.documents SET processing_status = 'completed', processed_at = NOW() WHERE id = $1",
                document_id
            )
        
        print(f"\n🎉 SUCCESS! Complete processing finished!")
        print(f"📊 Document ID: {document_id}")
        print(f"📄 {len(content_result['text'])} characters processed")
        print(f"🖼️ {len(content_result['images'])} images extracted") 
        print(f"📝 {len(chunks)} chunks created")
        print(f"🧠 {len(embeddings)} embeddings generated")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await processor.close()

if __name__ == "__main__":
    asyncio.run(test_direct_processing())
