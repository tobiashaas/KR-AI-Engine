#!/usr/bin/env python3
"""
Direct test of production processing without Supabase Storage
"""

import asyncio
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
        
            # Store document
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
                processor._calculate_file_hash(file_content),
                f"local://documents/{pdf_path.name}",
                {'models': classification.get('models', []), 'analysis': classification}
            )
            
        print(f"   ✅ Document stored: {document_id}")
        
        # 4. Create chunks
        print("📝 4. Creating chunks...")
        chunks = await processor._chunk_document(content_result['text'], classification)
        print(f"   ✅ Created {len(chunks)} chunks")
        
        # 5. Store chunks in database
        print("💾 5. Storing chunks in database...")
        chunk_ids = []
        async with processor.db_pool.acquire() as conn:
            for i, chunk_data in enumerate(chunks):
                chunk_id = await conn.fetchval(
                    """
                    INSERT INTO krai_intelligence.chunks 
                    (document_id, text_chunk, chunk_index, page_start, page_end, processing_status, fingerprint)
                    VALUES ($1, $2, $3, $4, $5, 'completed', $6)
                    RETURNING id
                    """,
                    document_id,
                    chunk_data['text'],
                    i,
                    chunk_data.get('page_start', 0),
                    chunk_data.get('page_end', 0),
                    processor._calculate_text_hash(chunk_data['text'])
                )
                chunk_ids.append(chunk_id)
        
        print(f"   ✅ Stored {len(chunk_ids)} chunks")
        
        # 6. Generate embeddings  
        print("🧠 6. Generating embeddings...")
        embeddings = await processor._generate_ollama_embeddings([chunk['text'] for chunk in chunks])
        print(f"   ✅ Generated {len(embeddings)} embeddings")
        
        # 7. Store embeddings
        print("💾 7. Storing embeddings...")
        async with processor.db_pool.acquire() as conn:
            for chunk_id, embedding in zip(chunk_ids, embeddings):
                vector_str = '[' + ','.join(map(str, embedding)) + ']'
                await conn.execute(
                    """
                    INSERT INTO krai_intelligence.embeddings 
                    (chunk_id, embedding, model_name, model_version)
                    VALUES ($1, $2::vector, $3, $4)
                    """,
                    chunk_id,
                    vector_str,
                    processor.embedding_model_name,
                    "latest"
                )
        
        print(f"   ✅ Stored {len(embeddings)} embeddings")
        
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
