#!/usr/bin/env python3
"""
Quick fix: Temporär Supabase Storage für den Demo umgehen
"""

import asyncio
from pathlib import Path
import sys
sys.path.append(str(Path(__file__).parent.parent / "test" / "backend-tests"))

from production_document_processor import ProductionDocumentProcessor

async def process_hp_document():
    """Process HP X580 Service Manual ohne Supabase Storage"""
    
    # Load the HP X580 Service Manual
    pdf_path = Path("../HP_X580_SM.pdf")
    if not pdf_path.exists():
        print(f"❌ File not found: {pdf_path}")
        return
    
    print(f"📄 Processing: {pdf_path.name} ({pdf_path.stat().st_size / 1024 / 1024:.1f} MB)")
    
    # Read file content
    with open(pdf_path, 'rb') as f:
        file_content = f.read()
    
    # Initialize processor
    processor = ProductionDocumentProcessor()
    await processor.initialize()
    
    print("🚀 Starting processing pipeline...")
    
    try:
        # Temporarily skip storage upload
        result = await processor._extract_content_with_gpu(file_content)
        print(f"📄 Extracted {len(result['text'])} characters")
        print(f"🖼️ Found {len(result['images'])} images") 
        
        # Continue with classification
        classification = processor._classify_document(pdf_path.name, result['text'])
        print(f"🏷️ Classification: {classification}")
        
        # Version extraction
        version_result = processor.version_extractor.extract_version(result['text'], classification['manufacturer'])
        print(f"📋 Version: {version_result}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        await processor.close()

if __name__ == "__main__":
    asyncio.run(process_hp_document())
