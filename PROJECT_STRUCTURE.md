# 📁 KRAI Engine - Project Structure

**Organized and Scalable Project Architecture**

---

## 🏗️ **ROOT DIRECTORY STRUCTURE**

```
KR-AI-Engine/
├── 📁 backend/                    # Python FastAPI Backend
├── 📁 dashboard/                  # Laravel Filament Admin Dashboard  
├── 📁 database_migrations/        # Database Schema & Migrations
├── 📁 docker/                     # Docker Configuration
├── 📁 ollama/                     # Local AI Model Integration
├── 📄 .gitignore                  # Git ignore rules
├── 📄 LICENSE                     # MIT License
├── 📄 LLM_INSTRUCTIONS.md         # AI Model Instructions
├── 📄 README.md                   # Project Overview & Documentation
└── 📄 PROJECT_STRUCTURE.md        # This file
```

---

## 🐍 **BACKEND** (`/backend/`)

**Python FastAPI Application**

```
backend/
├── 📄 app.py                      # Main FastAPI application
├── 📄 config.py                   # Configuration management
├── 📄 document_processor.py       # Document processing & AI integration
├── 📄 krai_interactive_processor.py # Interactive terminal processor
├── 📄 version_manager.py          # Version control system
├── 📄 requirements.txt            # Python dependencies
├── 📄 Dockerfile                  # Backend container configuration
├── 📄 README_INTERACTIVE_PROCESSOR.md
├── 📁 routes/                     # API route handlers
│   ├── 📄 admin_routes.py         # Admin API endpoints
│   ├── 📄 document_routes.py      # Document management endpoints
│   ├── 📄 search_routes.py        # Search & retrieval endpoints
│   └── 📄 version_api.py          # Version management API
└── 📁 tests/                      # Unit tests
    └── 📄 test_version_manager.py
```

**Key Features:**
- ✅ FastAPI with async support
- ✅ Supabase integration
- ✅ Document processing (PDF, DOCX, OCR)
- ✅ AI embeddings & semantic search
- ✅ Interactive terminal processor
- ✅ Version management system

---

## 🎛️ **DASHBOARD** (`/dashboard/`)

**Laravel Filament Admin Interface**

```
dashboard/
├── 📄 composer.json               # PHP dependencies
├── 📄 config.php                  # Dashboard configuration
├── 📄 Dockerfile                  # Dashboard container configuration
├── 📁 app/                        # Laravel application
│   ├── 📁 Filament/               # Filament resources
│   │   └── 📁 Resources/
│   │       └── 📁 DocumentResource/
│   │           ├── 📁 Pages/
│   │           │   ├── 📄 CompareDocumentVersions.php
│   │           │   └── 📄 NewDocumentVersion.php
│   │           └── 📄 DocumentResource.php
│   └── 📁 Models/
│       └── 📄 Document.php        # Document model
└── 📁 resources/
    └── 📁 views/
        └── 📁 filament/
            └── 📁 resources/
                └── 📁 document-resource/
                    └── 📁 pages/
                        └── 📄 compare-document-versions.blade.php
```

**Key Features:**
- ✅ Laravel Filament admin panel
- ✅ Document management interface
- ✅ Version comparison tools
- ✅ User-friendly dashboard

---

## 🗄️ **DATABASE MIGRATIONS** (`/database_migrations/`)

**Optimized Schema Architecture**

```
database_migrations/
└── 📁 OPTIMIZED_SCHEMA/           # Production-ready database schema
    ├── 📄 00_schema_architecture.sql     # Schema definitions & roles
    ├── 📄 01_krai_core_tables.sql        # Core business data
    ├── 📄 02_krai_intelligence_tables.sql # AI & intelligence data
    ├── 📄 03_krai_content_tables.sql     # Content & media
    ├── 📄 04_krai_config_tables.sql      # Configuration & rules
    ├── 📄 05_krai_system_tables.sql      # System operations
    ├── 📄 06_security_rls_policies.sql   # Security & RLS policies
    ├── 📄 07_performance_optimizations.sql # Performance enhancements
    ├── 📄 08_future_extensions.sql       # Scalability extensions
    ├── 📄 09_option_validation_examples.sql # Option validation logic
    ├── 📄 10_security_fixes.sql          # Security improvements
    ├── 📄 11_performance_optimization.sql # Performance fixes
    ├── 📄 README_OPTIMIZED_SCHEMA.md     # Migration guide
    ├── 📄 MIGRATION_SUMMARY.md           # Migration summary
    ├── 📄 API_DOCUMENTATION.md           # Function documentation
    ├── 📄 OPTION_VALIDATION_GUIDE.md     # Option validation guide
    └── 📄 DOCUMENT_TYPES_GUIDE.md        # Document types guide
```

**Schema Architecture:**
- ✅ **krai_core** - Core business data (manufacturers, products, documents)
- ✅ **krai_intelligence** - AI & intelligence (embeddings, search analytics)
- ✅ **krai_content** - Content & media (images, videos, defects)
- ✅ **krai_config** - Configuration & rules (compatibility, options)
- ✅ **krai_system** - System operations (queues, metrics, audit)

---

## 🐳 **DOCKER** (`/docker/`)

**Containerized Development Environment**

```
docker/
└── 📄 docker-compose.yml          # Multi-service Docker setup
```

**Services:**
- ✅ PostgreSQL with pgvector
- ✅ Python FastAPI backend
- ✅ Laravel Filament dashboard
- ✅ Ollama (local AI models)
- ✅ n8n (workflow automation)
- ✅ Redis (caching)
- ✅ Elasticsearch (search)

---

## 🤖 **OLLAMA** (`/ollama/`)

**Local AI Model Integration**

```
ollama/
├── 📄 client.py                   # Ollama client integration
├── 📄 config.yaml                 # Model configuration
└── 📄 setup.sh                    # Setup script
```

**Features:**
- ✅ Local AI model hosting
- ✅ Offline document processing
- ✅ Custom model configuration

---

## 📋 **KEY DOCUMENTATION FILES**

### **📄 README.md**
- Project overview and architecture
- Database schema documentation
- Setup and deployment instructions
- Feature descriptions

### **📄 LLM_INSTRUCTIONS.md**
- AI model configuration
- HP-specific intelligence functions
- Performance validation results
- Production database architecture

### **📄 PROJECT_STRUCTURE.md** (This file)
- Detailed project organization
- File and directory explanations
- Development workflow guidance

---

## 🚀 **DEVELOPMENT WORKFLOW**

### **1. Backend Development**
```bash
cd backend/
python -m venv venv
source venv/bin/activate  # Linux/Mac
# venv\Scripts\activate   # Windows
pip install -r requirements.txt
uvicorn app:app --reload
```

### **2. Database Setup**
```bash
# Apply migrations to Supabase
# Follow: database_migrations/OPTIMIZED_SCHEMA/README_OPTIMIZED_SCHEMA.md
```

### **3. Dashboard Development**
```bash
cd dashboard/
composer install
php artisan serve
```

### **4. Docker Development**
```bash
cd docker/
docker-compose up -d
```

---

## 🎯 **PROJECT GOALS**

### **✅ Achieved**
- ✅ **Optimized Database Schema** - 20+ tables across 5 logical schemas
- ✅ **Security Implementation** - RLS policies and role-based access
- ✅ **Performance Optimization** - Sub-150ms query performance
- ✅ **AI Integration** - Vector embeddings and semantic search
- ✅ **Document Processing** - Multi-format support with OCR
- ✅ **Scalable Architecture** - Easy extension for new features

### **🚧 In Progress**
- 🔄 **Python Backend Development** - Document processing pipeline
- 🔄 **Frontend Integration** - Dashboard enhancements
- 🔄 **AI Model Training** - HP-specific intelligence

### **📋 Planned**
- 📋 **Multi-Manufacturer Support** - Canon, Epson, Brother integration
- 📋 **Advanced Analytics** - Performance metrics and insights
- 📋 **Mobile App** - Technician mobile interface
- 📋 **API Documentation** - OpenAPI/Swagger integration

---

## 🔧 **TECHNOLOGY STACK**

### **Backend**
- **FastAPI** - Modern Python web framework
- **Supabase** - PostgreSQL database with real-time features
- **SentenceTransformers** - AI embeddings
- **PyMuPDF** - PDF processing
- **OpenCV** - Computer vision

### **Frontend**
- **Laravel Filament** - Admin dashboard
- **Blade Templates** - PHP templating
- **Tailwind CSS** - Utility-first CSS

### **Database**
- **PostgreSQL** - Primary database
- **pgvector** - Vector similarity search
- **Row Level Security** - Data security

### **Infrastructure**
- **Docker** - Containerization
- **Supabase** - Database hosting
- **Ollama** - Local AI models

---

## 📞 **SUPPORT & CONTRIBUTION**

### **Documentation**
- 📖 **README.md** - Quick start guide
- 📖 **API_DOCUMENTATION.md** - Function reference
- 📖 **OPTION_VALIDATION_GUIDE.md** - Complex validation examples
- 📖 **DOCUMENT_TYPES_GUIDE.md** - Document type specifications

### **Development**
- 🐛 **Issues** - Report bugs and feature requests
- 🔧 **Pull Requests** - Contribute code improvements
- 📝 **Documentation** - Help improve guides and examples

---

**🎯 This project structure is designed for scalability, maintainability, and easy collaboration!**
