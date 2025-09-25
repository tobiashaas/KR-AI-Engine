#!/usr/bin/env python3
"""
📄 PDF to Text Converter
Converts PDF files to text for analysis

Usage:
    python pdf_to_text_converter.py <pdf_file> [output_file]
    
Example:
    python pdf_to_text_converter.py HP_X580_SM.pdf HP_X580_SM.txt
"""

import sys
import fitz  # PyMuPDF
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def convert_pdf_to_text(pdf_path: str, output_path: str = None):
    """Convert PDF to text file"""
    try:
        pdf_file = Path(pdf_path)
        
        if not pdf_file.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")
        
        # Generate output filename if not provided
        if output_path is None:
            output_path = pdf_file.with_suffix('.txt')
        
        logger.info(f"📄 Converting: {pdf_file.name}")
        logger.info(f"📏 Size: {pdf_file.stat().st_size / (1024*1024):.1f} MB")
        
        # Open PDF
        doc = fitz.open(pdf_path)
        
        logger.info(f"📚 Pages: {len(doc)}")
        
        # Extract text from all pages
        full_text = ""
        page_count = 0
        
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            
            if page_text.strip():  # Only add non-empty pages
                full_text += f"\n--- PAGE {page_num + 1} ---\n"
                full_text += page_text + "\n"
                page_count += 1
            
            # Progress indicator
            if (page_num + 1) % 50 == 0:
                logger.info(f"⏳ Processed {page_num + 1}/{len(doc)} pages...")
        
        doc.close()
        
        # Save to text file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_text)
        
        # Statistics
        word_count = len(full_text.split())
        char_count = len(full_text)
        
        logger.info(f"✅ Conversion completed!")
        logger.info(f"📝 Text extracted: {word_count:,} words, {char_count:,} characters")
        logger.info(f"📄 Output saved to: {output_path}")
        
        return {
            'success': True,
            'output_file': str(output_path),
            'pages_processed': page_count,
            'total_pages': len(doc),
            'word_count': word_count,
            'char_count': char_count,
            'file_size_mb': pdf_file.stat().st_size / (1024*1024)
        }
        
    except Exception as e:
        logger.error(f"❌ Conversion failed: {str(e)}")
        return {
            'success': False,
            'error': str(e)
        }

def main():
    """Main function"""
    if len(sys.argv) < 2:
        print("📄 PDF to Text Converter")
        print("=" * 40)
        print("Usage: python pdf_to_text_converter.py <pdf_file> [output_file]")
        print("\nExample:")
        print("  python pdf_to_text_converter.py HP_X580_SM.pdf HP_X580_SM.txt")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) > 2 else None
    
    result = convert_pdf_to_text(pdf_path, output_path)
    
    if result['success']:
        print(f"\n🎉 Conversion successful!")
        print(f"📄 Output: {result['output_file']}")
        print(f"📚 Pages: {result['pages_processed']}/{result['total_pages']}")
        print(f"📝 Words: {result['word_count']:,}")
        print(f"📏 Original size: {result['file_size_mb']:.1f} MB")
    else:
        print(f"\n❌ Conversion failed: {result['error']}")
        sys.exit(1)

if __name__ == "__main__":
    main()
