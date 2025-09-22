"""
KRAI Engine Configuration
========================

Configuration file for interactive processor and future Filament dashboard integration.
Contains database connection settings, AI model configurations, and processing parameters.
"""

import os
from pathlib import Path

# Database Configuration
DATABASE_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', 5432),
    'database': os.getenv('DB_NAME', 'krai_engine'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', 'your_password_here'),
    'sslmode': os.getenv('DB_SSLMODE', 'prefer'),
}

# AI/ML Configuration
AI_CONFIG = {
    # OpenAI for embeddings (optional)
    'openai_api_key': os.getenv('OPENAI_API_KEY', ''),
    
    # Computer Vision Models
    'vision_models': {
        'defect_detection': 'yolov8n.pt',  # YOLOv8 nano for speed
        'quality_assessment': 'mobilenet_v3_large',  # MobileNet for quality scoring
        'custom_defect_classifier': 'models/custom_print_defects.pt'
    },
    
    # Model Paths
    'model_base_path': Path(__file__).parent / 'models',
    'weights_path': Path(__file__).parent / 'models' / 'weights',
    
    # Processing Parameters
    'image_max_size': (2048, 2048),  # Max image size for processing
    'confidence_threshold': 0.5,  # Minimum confidence for defect detection
    'batch_size': 8,  # Batch size for AI processing
}

# File Processing Configuration
PROCESSING_CONFIG = {
    # Supported file types
    'supported_pdf_extensions': ['.pdf'],
    'supported_image_extensions': ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.webp'],
    
    # Processing limits
    'max_file_size_mb': 100,  # Maximum file size in MB
    'max_pdf_pages': 1000,    # Maximum PDF pages to process
    'max_batch_size': 50,     # Maximum files in batch processing
    
    # OCR Configuration
    'tesseract_config': '--oem 3 --psm 6',  # Tesseract OCR config
    'ocr_languages': ['eng', 'deu', 'fra', 'spa'],  # Supported OCR languages
    
    # Text chunking
    'chunk_size': 1000,       # Characters per chunk
    'chunk_overlap': 200,     # Overlap between chunks
}

# Manufacturer Configuration
MANUFACTURER_CONFIG = {
    'supported_manufacturers': [
        'HP', 'Canon', 'Epson', 'Brother', 'Xerox', 
        'Kyocera', 'Ricoh', 'Konica Minolta', 'Other'
    ],
    
    # Error code patterns by manufacturer
    'error_code_patterns': {
        'HP': [
            r'Error\s+(\d+)',
            r'Code\s+(\d+)',
            r'(\d{2}\.\d{2}\.\d{2})',  # HP specific format
        ],
        'Canon': [
            r'Error\s+Code\s+([EC]\d{3})',
            r'Support\s+Code\s+(\d{4})',
        ],
        'Epson': [
            r'Error\s+(\d{3})',
            r'(\d{6})',  # 6-digit error codes
        ],
        'Brother': [
            r'Error\s+Code\s+([A-Z]-\d{2})',
            r'(\d{2})',  # Simple 2-digit codes
        ],
        'Xerox': [
            r'Code\s+(\d{3}-\d{3})',
            r'Error\s+(\d{2}-\d{3})',
        ]
    },
    
    # Common printer models (for autocomplete)
    'common_models': {
        'HP': [
            'LaserJet Pro 4000 Series',
            'LaserJet Pro MFP 4300 Series', 
            'OfficeJet Pro 9000 Series',
            'DesignJet T200 Series',
            'LaserJet Enterprise M600 Series',
            'Color LaserJet Pro M400 Series'
        ],
        'Canon': [
            'PIXMA TR8500 Series',
            'imageCLASS MF740C Series',
            'imagePROGRAF PRO-300',
            'MAXIFY GX7000 Series',
            'imageRUNNER ADVANCE C3500 Series'
        ],
        'Epson': [
            'WorkForce Pro WF-4800 Series',
            'EcoTank ET-4850',
            'SureColor P800',
            'Expression Photo XP-8500',
            'WorkForce Enterprise WF-C20000'
        ],
        'Brother': [
            'HL-L3270CDW',
            'MFC-L8900CDW',
            'DCP-L2550DW',
            'QL-820NWB',
            'MFC-J6945DW'
        ],
        'Xerox': [
            'VersaLink C405',
            'WorkCentre 6515',
            'Phaser 6510',
            'AltaLink C8100 Series',
            'PrimeLink C9065'
        ]
    }
}

# Print Quality Analysis Configuration
PRINT_QUALITY_CONFIG = {
    # Defect categories for classification
    'defect_categories': [
        'Banding',           # Horizontal lines across print
        'Streaking',         # Vertical lines or smears
        'Color Issues',      # Wrong colors, color shift
        'Paper Jam',         # Paper jam damage
        'Misalignment',      # Text/image misalignment
        'Smudging',          # Ink/toner smears
        'Fading',            # Light or faded print
        'Ghosting',          # Ghost images
        'Spots/Dots',        # Unwanted spots or dots
        'Registration',      # Color registration issues
        'Density Variation', # Uneven print density
        'Other'              # Custom defects
    ],
    
    # Quality rating scale
    'quality_scale': {
        1: 'Sehr schlecht - Nicht verwendbar',
        2: 'Schlecht - Deutliche Mängel',
        3: 'Mittel - Kleinere Probleme',
        4: 'Gut - Geringe Mängel',
        5: 'Sehr gut - Perfekte Qualität'
    },
    
    # Image analysis parameters
    'analysis_params': {
        'resize_for_analysis': (1024, 1024),
        'color_threshold': 30,      # Threshold for color detection
        'line_detection_threshold': 50,  # For banding/streaking
        'spot_min_size': 5,         # Minimum spot size in pixels
        'save_annotated_images': True,  # Save images with detected defects marked
    }
}

# Filament Dashboard Integration (Phase 2)
FILAMENT_CONFIG = {
    # Dashboard settings for future integration
    'dashboard_url': os.getenv('FILAMENT_URL', 'http://localhost:8080'),
    'api_endpoint': '/api/documents',
    'upload_endpoint': '/api/upload',
    
    # File upload settings
    'max_upload_size': '100MB',
    'allowed_mime_types': [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'image/bmp',
        'image/tiff'
    ],
    
    # Processing workflow settings
    'auto_categorization_threshold': 0.8,  # Auto-categorize if confidence > 80%
    'require_manual_review': True,         # Always require manual review in Phase 1
    'batch_processing_enabled': True,      # Enable batch uploads
}

# Logging Configuration
LOGGING_CONFIG = {
    'level': os.getenv('LOG_LEVEL', 'INFO'),
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': 'logs/krai_processor.log',
    'max_file_size': 10 * 1024 * 1024,  # 10MB
    'backup_count': 5,
}

# Development/Production Settings
ENVIRONMENT = os.getenv('ENVIRONMENT', 'development')

if ENVIRONMENT == 'production':
    # Production overrides
    AI_CONFIG['batch_size'] = 16
    PROCESSING_CONFIG['max_batch_size'] = 100
    LOGGING_CONFIG['level'] = 'WARNING'
else:
    # Development settings
    AI_CONFIG['batch_size'] = 4
    PROCESSING_CONFIG['max_batch_size'] = 10
    LOGGING_CONFIG['level'] = 'DEBUG'


# Validation functions
def validate_config():
    """Validate configuration settings"""
    errors = []
    
    # Check required environment variables
    required_env_vars = ['DB_HOST', 'DB_NAME', 'DB_USER', 'DB_PASSWORD']
    for var in required_env_vars:
        if not os.getenv(var):
            errors.append(f"Missing environment variable: {var}")
    
    # Check file paths
    model_path = AI_CONFIG['model_base_path']
    if not model_path.exists():
        errors.append(f"Model path does not exist: {model_path}")
    
    # Check processing limits
    if PROCESSING_CONFIG['max_file_size_mb'] > 500:
        errors.append("Max file size too large (>500MB)")
    
    return errors


def get_database_url():
    """Get database URL for SQLAlchemy/asyncpg"""
    config = DATABASE_CONFIG
    return f"postgresql://{config['user']}:{config['password']}@{config['host']}:{config['port']}/{config['database']}"


if __name__ == "__main__":
    # Configuration validation
    errors = validate_config()
    if errors:
        print("Configuration errors:")
        for error in errors:
            print(f"  - {error}")
    else:
        print("✅ Configuration is valid")
        print(f"Environment: {ENVIRONMENT}")
        print(f"Database: {DATABASE_CONFIG['database']}@{DATABASE_CONFIG['host']}")
        print(f"Supported manufacturers: {len(MANUFACTURER_CONFIG['supported_manufacturers'])}")
        print(f"AI models path: {AI_CONFIG['model_base_path']}")