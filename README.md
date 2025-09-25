# KRAI Engine - AI-Powered Document Processing System

## 🚀 **Overview**

KRAI Engine is a comprehensive AI-powered document processing system designed for technical service environments, specifically optimized for printer manufacturers. The system provides intelligent document classification, content extraction, and AI-powered analysis using state-of-the-art machine learning models.

## ✨ **Key Features**

- **🤖 Multi-Model AI Integration**: LLM (Llama3.2), Embedding (EmbeddingGemma), Vision (LLaVA)
- **📄 Intelligent Document Processing**: PDF text extraction, image OCR, content analysis
- **🔍 Advanced Classification**: Hybrid filename + content-based document categorization
- **🧠 Smart Chunking**: Contextual chunking optimized for technical documents
- **📊 Vector Search**: Semantic search using 768D embeddings
- **🖼️ Image Analysis**: Computer vision for defect detection and diagram analysis
- **⚡ High Performance**: GPU/NPU acceleration with Apple Metal Performance Shaders
- **🗄️ Scalable Database**: PostgreSQL with pgvector for vector operations
- **☁️ Cloud Storage**: Supabase integration for document and image storage

## 🏗️ **Architecture**

### **Backend (Python FastAPI)**
- **Production API**: `backend/production_main.py`
- **Document Processor**: `backend/production_document_processor.py`
- **Configuration**: JSON-based patterns for error codes, chunking, versions
- **Database**: PostgreSQL with optimized schema (16 tables)
- **Storage**: Supabase for documents and images

### **Database Schema**
- **krai_core**: Documents, manufacturers, products
- **krai_intelligence**: Chunks, embeddings, search cache
- **krai_content**: Images, metadata, analysis results
- **krai_config**: Patterns, settings, configurations
- **krai_system**: Performance, monitoring, statistics

### **AI/ML Stack**
- **Ollama**: Local AI models (Llama3.2, EmbeddingGemma, LLaVA)
- **Embeddings**: 768D vectors for semantic search
- **Vision AI**: Defect detection, diagram analysis
- **GPU Acceleration**: Apple M1 Pro (MPS) support

## 🚀 **Quick Start**

### **Prerequisites**
- Python 3.12+
- Docker & Docker Compose
- Ollama (for AI models)
- Supabase (local or cloud)

### **Installation**

1. **Clone Repository**
```bash
git clone https://github.com/your-username/KR-AI-Engine.git
cd KR-AI-Engine
```

2. **Setup Environment**
```bash
cd backend
pip install -r requirements.txt
```

3. **Configure Database**
```bash
# Local Supabase
supabase start

# Or use existing PostgreSQL
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=krai_engine
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=your_password
```

4. **Setup AI Models**
```bash
# Install Ollama models
ollama pull llama3.2:3b
ollama pull embeddinggemma
ollama pull llava:7b
```

5. **Run Database Migrations**
```bash
# Execute schema migrations
psql -h localhost -U postgres -d krai_engine -f database_migrations/OPTIMIZED_SCHEMA/00_schema_architecture.sql
# ... (run all migration files in order)
```

6. **Start Production API**
```bash
cd backend
python production_main.py
```

## 📁 **Project Structure**

```
KR-AI-Engine/
├── backend/                    # Main application
│   ├── production_main.py      # Production API server
│   ├── production_document_processor.py  # Core processing logic
│   ├── config/                 # Configuration files
│   │   ├── production_config.py
│   │   ├── supabase_config.py
│   │   └── *.json              # Pattern configurations
│   ├── api/                    # API endpoints
│   └── tests/                  # Unit tests
├── database_migrations/        # Database schema
│   └── OPTIMIZED_SCHEMA/       # Production schema
├── test/                       # Test files and scripts
│   ├── docker/                 # Docker configurations
│   ├── scripts/                # Test scripts
│   └── documents/              # Test documents
├── dashboard/                  # Filament dashboard
└── supabase/                   # Supabase configuration
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
- `error_code_patterns.json`: Manufacturer-specific error code patterns
- `chunk_settings.json`: Document chunking strategies
- `version_patterns.json`: Version extraction patterns
- `model_placeholder_patterns.json`: Model placeholder expansion

## 🧪 **Testing**

### **Test Documents**
Test documents are located in `test/documents/` and include:
- HP Service Manuals
- Konica Minolta Documentation
- Lexmark Technical Guides
- Various PDF formats for testing

### **Run Tests**
```bash
cd backend
python -m pytest tests/
```

## 📊 **Performance**

- **Processing Speed**: ~2-3 seconds per document
- **Embedding Generation**: 768D vectors in ~100ms
- **Image Processing**: GPU-accelerated with MPS
- **Database**: Optimized with indexes and materialized views
- **Storage**: Deduplication with SHA256 hashing

## 🔒 **Security**

- **Row Level Security (RLS)** enabled
- **Role-based access control**
- **Audit logging** for all operations
- **Secure storage** with private buckets

## 🚀 **Deployment**

### **Production Deployment**
```bash
# Using Docker Compose
docker-compose -f test/docker/docker-compose.production.yml up -d

# Or manual deployment
python backend/production_main.py
```

### **Supabase Integration**
```bash
# Local Supabase
supabase start

# Cloud Supabase
# Configure environment variables for cloud instance
```

## 📈 **Monitoring**

- **Database Statistics**: Query performance and usage
- **Processing Metrics**: Document processing times
- **Storage Usage**: File storage and deduplication stats
- **AI Model Performance**: Embedding and vision processing

## 🤝 **Contributing**

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 **License**

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 **Support**

For support and questions:
- Create an issue on GitHub
- Check the documentation in `docs/`
- Review the test examples in `test/`

---

**KRAI Engine** - Intelligent Document Processing for Technical Service Environments