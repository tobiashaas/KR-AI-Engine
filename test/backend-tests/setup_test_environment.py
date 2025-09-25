#!/usr/bin/env python3
"""
🔧 KRAI Test Environment Setup
Sets up the testing environment for document analysis

Features:
- Virtual environment setup
- Dependencies installation
- NLTK data download
- Test directory creation
"""

import subprocess
import sys
import os
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def run_command(command: str, description: str):
    """Run a command and handle errors"""
    try:
        logger.info(f"🔧 {description}...")
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        logger.info(f"✅ {description} completed")
        return result
    except subprocess.CalledProcessError as e:
        logger.error(f"❌ {description} failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return None

def setup_test_environment():
    """Setup the test environment"""
    logger.info("🚀 Setting up KRAI Test Environment...")
    
    # Create test directories (already created, but ensure they exist)
    test_dirs = ['test_documents', 'analysis_reports', 'logs']
    for dir_name in test_dirs:
        Path(dir_name).mkdir(exist_ok=True)
        logger.info(f"📁 Directory ready: {dir_name}")
    
    # Install required packages for testing
    test_packages = [
        'nltk',
        'matplotlib',
        'seaborn',
        'PyMuPDF',
        'pdfplumber',
        'pytesseract',
        'Pillow'
    ]
    
    for package in test_packages:
        run_command(f"pip install {package}", f"Installing {package}")
    
    # Download NLTK data
    try:
        import nltk
        logger.info("📥 Downloading NLTK data...")
        nltk.download('punkt', quiet=True)
        nltk.download('stopwords', quiet=True)
        nltk.download('punkt_tab', quiet=True)
        logger.info("✅ NLTK data downloaded")
    except Exception as e:
        logger.warning(f"NLTK download failed: {e}")
    
    logger.info("🎉 Test environment setup completed!")
    logger.info("📄 You can now upload test documents to the 'test_documents' folder")

def create_sample_test_script():
    """Create a sample test script"""
    sample_script = '''#!/usr/bin/env python3
"""
🧪 Sample Test Script for Document Analysis
"""

import asyncio
from test_document_analyzer import DocumentAnalyzer

async def test_document():
    """Test document analysis"""
    analyzer = DocumentAnalyzer()
    
    # Replace with your test document path
    document_path = "test_documents/your_test_document.pdf"
    
    try:
        report = await analyzer.analyze_document(document_path)
        
        print("\\n📊 Analysis Results:")
        print(f"Document Type: {report['document_type']['detected_type']}")
        print(f"Best Chunking Strategy: {report['recommendations']['best_strategy']}")
        
        # Save report
        analyzer.save_analysis_report(report, "analysis_reports/test_report.json")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    asyncio.run(test_document())
'''
    
    with open('run_test.py', 'w') as f:
        f.write(sample_script)
    
    logger.info("📝 Created sample test script: run_test.py")

if __name__ == "__main__":
    setup_test_environment()
    create_sample_test_script()
    
    print("\n" + "="*60)
    print("🎯 NEXT STEPS:")
    print("="*60)
    print("1. 📄 Upload your test document to: test_documents/")
    print("2. 🧪 Run analysis: python test_document_analyzer.py test_documents/your_document.pdf")
    print("3. 📊 Check results in: analysis_reports/")
    print("4. 🔧 Modify chunking strategies based on results")
    print("\n💡 Tip: Start with a small PDF (few pages) for testing!")
