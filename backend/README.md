# KRAI Engine Backend

**AI-Powered Document Processing Engine**

## Overview

The KRAI Engine backend is a FastAPI-based application that provides intelligent document processing capabilities for technical service environments. It specializes in processing service manuals, parts catalogs, and technical documentation from printer and copier manufacturers.

## Core Features

- **Intelligent Document Classification** - Automatic detection of document type, manufacturer, and models
- **Advanced Text Processing** - Error code and part number extraction with manufacturer-specific patterns
- **AI-Powered Image Analysis** - Technical diagram and chart analysis using Vision AI
- **Semantic Search** - Vector-based search with embedding technology
- **Multi-Modal AI** - Integration with LLM, Vision, and Embedding models via Ollama
- **Scalable Architecture** - Async processing with GPU acceleration support

## Quick Start

### Prerequisites
- Python 3.12+
- PostgreSQL with pgvector extension
- Ollama with required AI models
- Supabase (local or cloud)

### Installation

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Environment**
   ```bash
   # Root .env file is automatically loaded
   # Ensure /.env exists with proper configuration
   ```

3. **Start Application**
   ```bash
   python3 production_main.py
   ```

The API will be available at `http://localhost:8001`

## Application Architecture

### Main Components

#### Production Document Processor (`production_document_processor.py`)
Core document processing pipeline with the following capabilities:
- Multi-format document ingestion (PDF, DOCX)
- Intelligent chunking with configurable strategies
- AI-powered content analysis and classification
- Image extraction and Vision AI processing
- Embedding generation for semantic search
- Comprehensive metadata extraction

#### Configuration System (`config/`)
Centralized configuration management:
- **Production Config**: Runtime environment configuration
- **Database Config**: Connection and pool management
- **Supabase Config**: Storage and API configuration
- **JSON Configs**: Dynamic pattern configurations for error codes, versions, and chunking

#### API Layer (`api/`)
RESTful API endpoints:
- Document upload and processing
- Real-time processing status
- Search and query interfaces
- AI model management
- Performance monitoring

### AI Integration

#### Ollama Models
- **LLM**: Llama 3.2:3b for text analysis and chat
- **Vision**: LLaVA:7b for image analysis and OCR
- **Embedding**: EmbeddingGemma for semantic vectorization

#### Device Support
- **Apple Silicon**: MPS (Metal Performance Shaders) 
- **NVIDIA GPU**: CUDA acceleration
- **CPU Fallback**: Intel/AMD processor support

## Configuration

### Environment Variables

The backend loads configuration from the root `.env` file:

```env
# Database Configuration
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres

# Supabase Configuration  
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_SERVICE_ROLE_KEY=your_service_role_key

# Ollama Configuration
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=llava:7b
OLLAMA_EMBEDDING_MODEL=embeddinggemma

# Performance Configuration
ML_DEVICE=mps
ML_BATCH_SIZE=32
ML_CONCURRENT_DOCUMENTS=3
```

### JSON Configuration Files

#### Chunking Strategies (`config/chunk_settings.json`)
Configures text chunking behavior:
- Strategy selection (contextual, structure-based, etc.)
- Document-type specific settings
- Manufacturer-specific optimizations

#### Error Code Patterns (`config/error_code_patterns.json`)
Manufacturer-specific error code extraction:
- HP: Alphanumeric patterns (C4-750, 13.05.00)
- Konica Minolta: C-series and E-series codes  
- Lexmark: Numeric patterns (XXX.XX format)

#### Version Patterns (`config/version_patterns.json`)
Document version extraction rules:
- Edition patterns
- Date patterns  
- Firmware version patterns
- Validation rules

## API Endpoints

### Core Processing
```http
POST /api/production/documents/upload
GET  /health
GET  /config
GET  /api/production/documents/stats
```

### AI Interaction
```http
POST /api/production/chat
POST /api/production/vision/analyze
GET  /api/production/models/status
```

### Performance Monitoring
```http
GET /api/production/performance
```

See `../API_DOCUMENTATION.md` for complete endpoint documentation.

## Document Processing Pipeline

### 1. Document Upload
- File validation (type, size)
- Temporary storage
- Initial metadata extraction

### 2. Classification
- Filename-based classification
- Content-based analysis
- Manufacturer detection
- Model identification

### 3. Text Processing
- PDF text extraction
- Structure analysis
- Error code detection
- Part number extraction
- Version identification

### 4. Chunking
- Strategy selection based on document type
- Intelligent boundary detection
- Context preservation
- Overlap optimization

### 5. Image Processing
- Image extraction from PDF
- Vision AI analysis
- Technical diagram interpretation
- OCR for text in images

### 6. Embedding Generation
- Text vectorization using EmbeddingGemma
- Semantic embedding creation
- Vector database storage

### 7. Database Storage
- Structured data storage in PostgreSQL
- File storage in Supabase Storage
- Metadata indexing
- Relationship mapping

## Testing Framework

### Test Structure
```
tests/
├── comprehensive_test_runner.py    # Main test orchestrator
├── real_document_tester.py        # Real PDF testing
├── *_classifier*.py              # Classification tests
├── *_extractor*.py               # Extraction tests
├── test_documents/               # Test data
└── analysis_reports/             # Test results
```

### Running Tests
```bash
# Run comprehensive tests
python tests/comprehensive_test_runner.py

# Test specific component
python tests/test_json_config_classifier.py

# Test with real documents
python tests/real_document_tester.py
```

## Performance Optimization

### Database Optimization
- Connection pooling with AsyncPG
- Prepared statements for frequent queries
- Composite indexes for search performance
- HNSW indexes for vector similarity

### AI Model Optimization
- GPU memory management
- Batch processing for efficiency
- Model result caching
- Async processing pipeline

### Storage Optimization
- File deduplication using SHA256 hashing
- Compressed storage for text content
- Lazy loading for large documents
- Efficient image processing

## Monitoring and Debugging

### Health Monitoring
The `/health` endpoint provides comprehensive system status:
- Database connectivity
- AI model availability  
- Processing statistics
- Performance metrics

### Logging
Structured logging with multiple levels:
- **INFO**: General processing information
- **DEBUG**: Detailed processing steps
- **ERROR**: Error conditions and exceptions
- **WARNING**: Non-critical issues

### Debug Mode
Enable debug logging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
```

## Deployment

### Local Development
```bash
# Start with local services
python3 production_main.py
```

### Docker Deployment
```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY . .
RUN pip install -r requirements.txt
EXPOSE 8001
CMD ["python3", "production_main.py"]
```

### Production Deployment
- Environment-based configuration
- Database connection pooling
- Load balancing support
- Health check endpoints
- Graceful shutdown handling

## Security Considerations

### Data Protection
- Input validation for all endpoints
- SQL injection prevention
- File upload security
- Secure storage configuration

### Access Control
- API authentication (configurable)
- Row Level Security in database
- Private storage buckets
- Environment variable protection

## Troubleshooting

### Common Issues

**Database Connection Failed**
```bash
# Check PostgreSQL connectivity
psql -h $POSTGRES_HOST -p $POSTGRES_PORT -U $POSTGRES_USER -d $POSTGRES_DB
```

**AI Models Not Available**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# Pull missing models
ollama pull llama3.2:3b
ollama pull llava:7b
ollama pull embeddinggemma
```

**API Not Responding**
```bash
# Check process
ps aux | grep production_main.py

# Check logs
tail -f logs/krai.log

# Check port availability
lsof -i :8001
```

### Debug Logging
Enable comprehensive debugging:
```env
DEBUG=true
LOG_LEVEL=DEBUG
DEBUG_CHUNKING=true
DEBUG_CLASSIFICATION=true
```

## Contributing

### Code Style
- Follow PEP 8 conventions
- Use type hints throughout
- Comprehensive docstrings
- Async/await for I/O operations

### Testing
- Add tests for new features
- Maintain test coverage above 80%
- Test with real documents
- Performance regression testing

### Documentation
- Update API documentation for new endpoints
- Document configuration changes
- Update deployment guides
- Maintain changelog

## Support

For backend-specific issues:
1. Check application logs
2. Verify configuration settings
3. Test individual components
4. Run diagnostic health checks
5. Contact development team with detailed error information