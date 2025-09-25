# Backend - KRAI Engine

The backend of KRAI Engine is a high-performance Python FastAPI application that provides AI-powered document processing capabilities.

## 🚀 **Core Components**

### **Production API**
- **`production_main.py`** - Main FastAPI application
- **`production_document_processor.py`** - Core document processing logic
- **`supabase_main.py`** - Supabase-integrated API
- **`supabase_document_processor.py`** - Supabase document processor

### **Configuration**
- **`config/production_config.py`** - Production configuration
- **`config/supabase_config.py`** - Supabase integration
- **`config/database_config.py`** - Database configuration
- **`config/*.json`** - JSON-based pattern configurations

### **API Endpoints**
- **`api/document_api.py`** - Document processing endpoints
- **`api/supabase_document_api.py`** - Supabase document API

## 🏗️ **Architecture**

### **Document Processing Pipeline**
1. **Document Upload** → PDF validation and storage
2. **Text Extraction** → PyPDF2-based content extraction
3. **Image Processing** → Computer vision with LLaVA
4. **Classification** → Hybrid filename + content-based
5. **Chunking** → Contextual chunking for technical documents
6. **Embedding Generation** → 768D vectors with EmbeddingGemma
7. **Database Storage** → PostgreSQL with pgvector
8. **Search Indexing** → Vector search capabilities

### **AI/ML Integration**
- **LLM**: Llama3.2 for text analysis
- **Embeddings**: EmbeddingGemma for semantic search
- **Vision**: LLaVA for image analysis
- **GPU Acceleration**: Apple Metal Performance Shaders (MPS)

## 📁 **File Structure**

```
backend/
├── production_main.py              # Main FastAPI application
├── production_document_processor.py # Core processing logic
├── supabase_main.py               # Supabase API
├── supabase_document_processor.py # Supabase processor
├── config/                        # Configuration files
│   ├── production_config.py       # Production settings
│   ├── supabase_config.py         # Supabase integration
│   ├── database_config.py         # Database configuration
│   ├── error_code_patterns.json   # Error code patterns
│   ├── chunk_settings.json        # Chunking strategies
│   ├── version_patterns.json     # Version extraction
│   └── model_placeholder_patterns.json # Model placeholders
├── api/                          # API endpoints
│   ├── document_api.py           # Document API
│   └── supabase_document_api.py  # Supabase API
├── tests/                        # Unit tests
│   ├── test_*.py                 # Test files
│   └── *.json                    # Test configurations
├── requirements.txt              # Python dependencies
└── logs/                         # Application logs
```

## 🔧 **Configuration**

### **Environment Variables**
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=krai_engine
POSTGRES_USER=postgres
POSTGRES_PASSWORD=your_password

# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=your_anon_key
SUPABASE_SERVICE_ROLE_KEY=your_service_key

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### **JSON Configuration Files**

#### **Error Code Patterns** (`error_code_patterns.json`)
```json
{
  "manufacturers": {
    "hp": {
      "patterns": ["C####", "J##-##", "E##-##"],
      "validation_regex": "^(C|J|E)\\d{2,4}$"
    },
    "konica_minolta": {
      "patterns": ["C####", "J##-##", "E##-##", "##.##"],
      "validation_regex": "^(C|J|E)\\d{2,4}$|^\\d{2}\\.\\d{2}$"
    }
  }
}
```

#### **Chunk Settings** (`chunk_settings.json`)
```json
{
  "default": {
    "chunk_size": 512,
    "chunk_overlap": 50,
    "strategy": "contextual"
  },
  "document_types": {
    "service_manual": {
      "chunk_size": 768,
      "chunk_overlap": 100,
      "strategy": "structure_based"
    }
  }
}
```

#### **Version Patterns** (`version_patterns.json`)
```json
{
  "pattern_categories": {
    "edition_patterns": {
      "patterns": [
        {
          "regex": "edition\\s+([0-9]+(?:\\.[0-9]+)?)\\s*,?\\s*([0-9]+/[0-9]{4})",
          "output_format": "Edition {edition}, {date}",
          "confidence": 1.0
        }
      ]
    }
  }
}
```

## 🚀 **Running the Backend**

### **Development Mode**
```bash
cd backend
pip install -r requirements.txt
python production_main.py
```

### **Production Mode**
```bash
# Using Docker
docker build -f Dockerfile -t krai-backend .
docker run -p 8001:8001 krai-backend

# Or directly
python production_main.py
```

### **Supabase Integration**
```bash
# Start local Supabase
supabase start

# Run Supabase API
python supabase_main.py
```

## 🧪 **Testing**

### **Unit Tests**
```bash
cd backend
python -m pytest tests/
```

### **Integration Tests**
```bash
# Test production system
python test_production_system.py

# Test Supabase integration
python test_supabase_system.py
```

### **API Testing**
```bash
# Test API endpoints
curl -X POST http://localhost:8001/api/production/documents/upload \
  -F "file=@test_documents/HP_E778_SM.pdf"
```

## 📊 **Performance**

### **Optimization Features**
- **Async Processing**: Non-blocking I/O operations
- **GPU Acceleration**: Apple M1 Pro MPS support
- **Connection Pooling**: Database connection optimization
- **Caching**: Redis-based caching for embeddings
- **Batch Processing**: Efficient batch operations

### **Performance Metrics**
- **Document Processing**: 2-3 seconds per document
- **Embedding Generation**: 100ms per chunk
- **Image Analysis**: 500ms per image
- **Database Queries**: < 50ms average

## 🔒 **Security**

### **Authentication**
- **API Keys**: Secure API key management
- **Row Level Security**: Database-level access control
- **Audit Logging**: Comprehensive operation logging

### **Data Protection**
- **Encryption**: Data encryption at rest and in transit
- **Access Control**: Role-based permissions
- **Privacy**: Personal data redaction with Presidio

## 📈 **Monitoring**

### **Logging**
- **Application Logs**: `backend/logs/`
- **Database Logs**: PostgreSQL query logging
- **Performance Metrics**: Processing time tracking

### **Health Checks**
- **API Health**: `/health` endpoint
- **Database Health**: Connection status
- **AI Models**: Ollama model availability

## 🐛 **Debugging**

### **Common Issues**
1. **Database Connection**: Check PostgreSQL is running
2. **Ollama Models**: Ensure models are available
3. **Supabase**: Verify local instance is running
4. **File Permissions**: Check document access

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python production_main.py --debug
```

## 📚 **API Documentation**

### **Endpoints**
- **POST** `/api/production/documents/upload` - Upload document
- **GET** `/api/production/documents` - List documents
- **GET** `/api/production/documents/{id}` - Get document details
- **POST** `/api/production/documents/{id}/process` - Process document
- **GET** `/health` - Health check

### **Request/Response Examples**
```bash
# Upload document
curl -X POST http://localhost:8001/api/production/documents/upload \
  -F "file=@document.pdf" \
  -F "metadata={\"manufacturer\":\"HP\"}"

# Response
{
  "document_id": "uuid",
  "status": "processing",
  "message": "Document uploaded successfully"
}
```

## 🔄 **Deployment**

### **Docker Deployment**
```bash
# Build image
docker build -f Dockerfile -t krai-backend .

# Run container
docker run -p 8001:8001 \
  -e POSTGRES_HOST=localhost \
  -e POSTGRES_PORT=5432 \
  krai-backend
```

### **Production Deployment**
```bash
# Using Docker Compose
docker-compose -f test/docker/docker-compose.production.yml up -d

# Or manual deployment
python production_main.py
```

---

**Backend** - High-performance AI-powered document processing
