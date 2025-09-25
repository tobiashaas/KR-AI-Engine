# KRAI Engine - Project Structure

**Comprehensive Project Architecture Overview**

## Root Directory Structure

```
krai-engine/
├── .env                              # Single Source of Truth - Environment Configuration
├── .gitignore                        # Git ignore patterns
├── README.md                         # Main project documentation
├── API_DOCUMENTATION.md              # Complete API reference
├── CHUNKING_CONFIGURATION.md         # Chunking strategies guide
├── DEPLOYMENT_GUIDE.md               # Deployment instructions
├── PROJECT_STRUCTURE.md              # This file - project architecture
├── ENV_CONFIGURATION.md              # Environment setup guide
├── LICENSE                           # Project license
├── start_krai_api.sh                 # API startup script
└── LLM_INSTRUCTIONS.md               # AI model instructions
```

## Backend Directory

### Core Application
```
backend/
├── production_main.py                # Main FastAPI application entry point
├── production_document_processor.py  # Core document processing pipeline
├── supabase_main.py                  # Supabase-specific FastAPI app
├── supabase_document_processor.py    # Supabase document processor
├── openwebui_integration.py          # OpenWebUI integration logic
└── requirements.txt                  # Python dependencies
```

### Configuration Management
```
backend/config/
├── production_config.py              # Production environment configuration
├── database_config.py                # Database connection settings
├── supabase_config.py                # Supabase configuration and storage
├── chunk_settings.json               # Chunking strategies configuration
├── error_code_patterns.json          # Error code extraction patterns
├── version_patterns.json             # Version extraction patterns
├── model_placeholder_patterns.json   # Model placeholder expansion rules
├── document_update_strategies.md     # Document update methodology
├── version_extraction_results.md     # Version extraction analysis
├── json_version_config_summary.md    # JSON configuration summary
├── bulletin_analysis_report.md       # Bulletin analysis findings
└── intelligent_model_strategy.md     # Model extraction strategy
```

### API Layer
```
backend/api/
├── document_api.py                   # Document processing endpoints
└── supabase_document_api.py          # Supabase-specific endpoints
```

### Testing Framework
```
backend/tests/
├── README_TESTING.md                 # Testing documentation
├── comprehensive_test_runner.py      # Main test runner
├── setup_test_environment.py         # Test environment setup
├── real_document_tester.py          # Real document testing
├── simple_document_analyzer.py       # Basic document analysis
├── test_document_analyzer.py         # Document analysis tests
├── test_document_generator.py        # Test document generation
├── content_based_classifier_test.py  # Content classification tests
├── hybrid_classifier_test.py         # Hybrid classification tests
├── improved_hybrid_classifier.py     # Enhanced hybrid classifier
├── intelligent_document_classifier.py # AI-powered classifier
├── hybrid_document_classifier.py     # Hybrid document classifier
├── intelligent_model_extractor.py    # Model extraction logic
├── json_config_classifier.py         # JSON-based classifier
├── json_version_extractor.py         # JSON-based version extractor
├── test_json_config_classifier.py    # JSON classifier tests
├── test_json_version_with_pdfs.py    # PDF version extraction tests
├── test_improved_classifier.py       # Improved classifier tests
├── test_version_patterns.py          # Version pattern tests
├── test_corrected_version_patterns.py # Corrected version tests
├── test_corrected_error_codes.py     # Corrected error code tests
├── test_lexmark_corrected.py         # Lexmark-specific tests
├── pdf_to_text_converter.py          # PDF text extraction utility
├── test_documents/                   # Test document collection
│   ├── HP_Service_Manual_Test.txt
│   ├── Konica_Minolta_Test.txt
│   ├── Lexmark_Test.txt
│   ├── Mixed_Manufacturer_Test.txt
│   ├── UTAX_Test.txt
│   ├── Version_Test_Document.txt
│   └── Bulletin_Test.txt
├── analysis_reports/                 # Analysis result reports
│   ├── error_code_analysis_hp.json
│   ├── error_code_analysis_km.json
│   ├── error_code_analysis_lexmark.json
│   ├── filename_classification_report.json
│   ├── content_classification_report.json
│   ├── hybrid_classification_report.json
│   ├── improved_classification_report.json
│   ├── intelligent_classification_report.json
│   ├── json_config_classification_report.json
│   └── version_extraction_report.json
└── logs/                             # Test execution logs
```

### Storage and Uploads
```
backend/
├── static/                          # Static file serving
├── uploads/                         # Temporary file uploads
└── logs/                           # Application logs
```

## Database Management

### Schema Definitions
```
database_migrations/
├── init-postgres.sql               # PostgreSQL initialization
├── init-supabase.sql              # Supabase initialization
└── OPTIMIZED_SCHEMA/              # Optimized database schema
    ├── 00_schema_architecture.sql  # Schema structure definition
    ├── 01_krai_core_tables.sql     # Core business tables
    ├── 02_krai_intelligence_tables.sql # AI/ML tables
    ├── 03_krai_content_tables.sql  # Content and media tables
    ├── 04_krai_config_tables.sql   # Configuration tables
    ├── 05_krai_system_tables.sql   # System management tables
    ├── 06_security_rls_policies.sql # Row Level Security
    ├── 07_performance_optimizations.sql # Performance indexes
    ├── 08_future_extensions.sql    # Future extensibility
    ├── 09_option_validation_examples.sql # Validation examples
    ├── 10_security_fixes.sql       # Security patches
    ├── 11_performance_optimization.sql # Additional optimizations
    ├── add_missing_columns.sql     # Column additions
    ├── fix_core_tables.sql         # Core table fixes
    ├── fix_content_tables.sql      # Content table fixes
    ├── README_OPTIMIZED_SCHEMA.md  # Schema documentation
    ├── MIGRATION_SUMMARY.md        # Migration overview
    ├── API_DOCUMENTATION.md        # Database API docs
    ├── DOCUMENT_TYPES_GUIDE.md     # Document type guide
    └── OPTION_VALIDATION_GUIDE.md  # Validation guide
```

### Supabase Configuration
```
supabase/
├── config.toml                     # Supabase project configuration
├── kong.yml                        # Kong API gateway configuration
└── migrations/                     # Supabase migrations
    ├── 20250924214837_init_krai_schema.sql
    └── 20250924215000_create_storage_buckets.sql
```

## Frontend Dashboard

### Laravel Filament Interface
```
dashboard/
├── composer.json                   # PHP dependencies
├── config.php                      # Dashboard configuration
├── Dockerfile                      # Dashboard containerization
├── app/                           # Application logic
│   ├── Models/
│   │   └── Document.php           # Document model
│   └── Filament/
│       └── Resources/             # Filament resources
│           ├── DocumentResource.php
│           ├── ManufacturerResource.php
│           └── ProductResource.php
└── resources/
    └── views/
        └── filament/
            └── resources/
                └── document-resource.blade.php
```

## AI/ML Integration

### Ollama Configuration
```
ollama/
├── client.py                       # Ollama API client
├── config.yaml                     # Ollama configuration
└── setup.sh                       # Ollama setup script
```

## Testing and Development

### Test Environment
```
test/
├── README.md                       # Test documentation
├── documents/                      # Test document collection
│   ├── HP_LaserJet_Pro_M404n.pdf
│   ├── Konica_Minolta_bizhub_C308.pdf
│   ├── Lexmark_CX725de.pdf
│   ├── [70+ additional PDF files]
│   └── HP_Test_Document.docx
├── scripts/                        # Test automation scripts
│   ├── batch_test_documents.py
│   ├── generate_test_reports.py
│   ├── validate_classifications.py
│   ├── error_code_validation.txt
│   ├── model_extraction_tests.txt
│   └── version_pattern_tests.txt
└── docker/                        # Docker test configurations
    ├── docker-compose.complete.yml
    ├── docker-compose.krai.yml
    ├── docker-compose.local-postgres.yml
    ├── docker-compose.local-supabase.yml
    ├── docker-compose.local-supabase-simple.yml
    ├── docker-compose.local.yml
    ├── docker-compose.production.yml
    ├── docker-compose.simple.yml
    ├── docker-compose.supabase-no-nginx.yml
    ├── docker-compose.supabase.yml
    ├── Dockerfile.production
    ├── Dockerfile.simple
    └── Dockerfile.supabase
```

## Architecture Layers

### 1. Presentation Layer
- **FastAPI REST API**: Primary interface for document processing
- **Laravel Filament Dashboard**: Administrative interface
- **OpenWebUI Integration**: Chat interface for document queries

### 2. Business Logic Layer
- **Document Processing Pipeline**: Core document analysis engine
- **AI/ML Integration**: Ollama model orchestration
- **Classification System**: Multi-strategy document classification
- **Chunking Engine**: Intelligent text segmentation
- **Extraction System**: Error codes, part numbers, version detection

### 3. Data Access Layer
- **PostgreSQL Database**: Primary data storage with pgvector
- **Supabase Storage**: File and media storage
- **Embedding Management**: Vector storage and retrieval
- **Configuration Management**: JSON-based configuration system

### 4. Infrastructure Layer
- **Docker Containerization**: Service orchestration
- **Environment Management**: Single source of truth configuration
- **Monitoring and Logging**: Comprehensive observability
- **Security**: RLS policies and authentication

## Data Flow Architecture

### Document Processing Pipeline
```
1. Upload → 2. Classification → 3. Text Extraction → 4. Chunking
    ↓
8. Storage ← 7. Embedding ← 6. Image Analysis ← 5. Structure Analysis
```

### Detailed Flow:
1. **Document Upload**: PDF/DOCX file reception via API
2. **Classification**: Automatic detection of type, manufacturer, model
3. **Text Extraction**: PDF text and metadata extraction
4. **Chunking**: Intelligent text segmentation using configured strategies
5. **Structure Analysis**: Detection of sections, procedures, error codes
6. **Image Analysis**: Vision AI processing of embedded images
7. **Embedding Generation**: Vector embedding creation for semantic search
8. **Storage**: Persistent storage in PostgreSQL and Supabase

## Configuration Management

### Environment Configuration Hierarchy
1. **Root .env**: Master configuration file
2. **Production Config**: Runtime configuration management
3. **JSON Configs**: Dynamic pattern and strategy configurations
4. **Database Config**: Connection and performance settings

### Configuration Flow
```
.env (Root) → Production Config → Component Configs → Runtime Settings
```

## Security Architecture

### Authentication Flow
1. **API Authentication**: Token-based authentication (future)
2. **Database Security**: Row Level Security policies
3. **File Security**: Secure storage with access controls
4. **Environment Security**: Secure configuration management

### Data Protection
- **Input Validation**: Comprehensive request validation
- **SQL Injection Prevention**: Parameterized queries
- **File Upload Security**: Type and size validation
- **Storage Security**: Private bucket configurations

## Performance Optimization

### Caching Strategy
1. **Application Cache**: In-memory caching for frequent operations
2. **Database Cache**: Connection pooling and query optimization
3. **Model Cache**: AI model result caching
4. **Storage Cache**: File metadata caching

### Scaling Strategy
1. **Horizontal Scaling**: Multi-instance API deployment
2. **Database Scaling**: Read replicas and connection pooling
3. **Storage Scaling**: Distributed file storage
4. **AI Model Scaling**: GPU cluster support

## Monitoring and Observability

### Metrics Collection
- **Application Metrics**: Processing statistics and performance
- **Database Metrics**: Query performance and connection health
- **System Metrics**: Resource utilization and health
- **Business Metrics**: Document processing success rates

### Health Checks
- **API Health**: Endpoint availability and response times
- **Database Health**: Connection status and query performance
- **AI Model Health**: Model availability and processing times
- **Storage Health**: File system availability and performance

This project structure provides a comprehensive, scalable architecture for the KRAI Engine, supporting everything from local development to enterprise deployment.