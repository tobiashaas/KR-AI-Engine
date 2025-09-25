# Test Suite - KRAI Engine

This directory contains all test files, scripts, and configurations for the KRAI Engine project.

## 📁 **Directory Structure**

```
test/
├── docker/                     # Docker configurations
│   ├── docker-compose.*.yml   # Various Docker Compose setups
│   └── Dockerfile.*           # Different Dockerfile variants
├── scripts/                   # Test scripts and utilities
│   ├── test_*.py             # Test scripts
│   ├── requirements_*.txt    # Different requirement files
│   └── run_*.py              # Test runners
└── documents/                # Test documents
    ├── HP_*.pdf              # HP Service Manuals
    ├── KM_*.pdf              # Konica Minolta Documentation
    ├── Lexmark_*.pdf         # Lexmark Technical Guides
    └── *.pdf                  # Other test documents
```

## 🧪 **Test Documents**

### **HP Service Manuals**
- `HP_E778_SM.pdf` - HP E778 Service Manual
- `HP_E786_SM.pdf` - HP E786 Service Manual
- `HP_E876_SM.pdf` - HP E876 Service Manual
- `HP_E877_SM.pdf` - HP E877 Service Manual
- `HP_X580_SM.pdf` - HP X580 Service Manual

### **Konica Minolta Documentation**
- `KM_4750i_4050i_4751i_4051i_SM.pdf` - i-Series Service Manual
- `KM_C658_C558_C458_C368_C308_C258_SM_EN.pdf` - C-Series Service Manual

### **Lexmark Technical Guides**
- `Lexmark_CX825_CX860_XC8155_XC8160.pdf` - CX Series Manual
- `Lexmark_CX833_CX961_CX962_CX963_XC8355_XC9635_XC9645_XC9655_SM.pdf` - CX/XC Series Manual

### **Other Test Documents**
- `UTAX_5058i_6058i_7058i_SM.pdf` - UTAX i-Series Manual
- `bizhub_PRESS_2250P_E_SM_v3.1.pdf` - Konica Minolta Press Manual

## 🐳 **Docker Configurations**

### **Production Setup**
- `docker-compose.production.yml` - Full production environment
- `Dockerfile.production` - Production backend image

### **Development Setup**
- `docker-compose.supabase.yml` - Supabase integration
- `docker-compose.simple.yml` - Simplified development setup

### **Testing Setup**
- `docker-compose.local.yml` - Local development
- `docker-compose.local-supabase.yml` - Local Supabase setup

## 🧪 **Test Scripts**

### **System Tests**
- `test_production_system.py` - Full production system test
- `test_supabase_system.py` - Supabase integration test
- `test_api.py` - API endpoint testing

### **Unit Tests**
- `test_json_config_classifier.py` - JSON configuration testing
- `test_corrected_error_codes.py` - Error code pattern testing
- `test_version_patterns.py` - Version extraction testing

### **Integration Tests**
- `test_corrected_version_patterns.py` - Version pattern integration
- `test_lexmark_corrected.py` - Lexmark-specific testing

## 🚀 **Running Tests**

### **Prerequisites**
```bash
# Install dependencies
pip install -r scripts/requirements_production.txt

# Setup test environment
export POSTGRES_HOST=localhost
export POSTGRES_PORT=5432
export POSTGRES_DB=test_krai
export POSTGRES_USER=postgres
export POSTGRES_PASSWORD=test_password
```

### **Run All Tests**
```bash
cd scripts
python test_production_system.py
```

### **Run Specific Tests**
```bash
# Test document processing
python test_supabase_system.py

# Test API endpoints
python test_api.py

# Test configuration
python test_json_config_classifier.py
```

## 📊 **Test Data**

### **Expected Results**
- **Document Classification**: Manufacturer, model, type detection
- **Error Code Extraction**: Pattern-based error code recognition
- **Version Detection**: Document version and date extraction
- **Image Processing**: OCR and computer vision analysis
- **Embedding Generation**: 768D vector embeddings

### **Performance Benchmarks**
- **Processing Time**: < 5 seconds per document
- **Embedding Generation**: < 200ms per chunk
- **Image Analysis**: < 1 second per image
- **Database Operations**: < 100ms per query

## 🔧 **Configuration**

### **Test Environment**
```bash
# Database
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_DB=test_krai

# Supabase
SUPABASE_URL=http://localhost:54321
SUPABASE_ANON_KEY=test_anon_key
SUPABASE_SERVICE_ROLE_KEY=test_service_key

# Ollama
OLLAMA_BASE_URL=http://localhost:11434
```

### **Test Data Setup**
```bash
# Create test database
createdb test_krai

# Run migrations
psql -h localhost -U postgres -d test_krai -f ../database_migrations/OPTIMIZED_SCHEMA/00_schema_architecture.sql
```

## 📝 **Test Documentation**

### **Test Reports**
- Test results are logged to `backend/logs/`
- Performance metrics are stored in database
- Error reports are generated for failed tests

### **Coverage**
- **Unit Tests**: 90%+ coverage
- **Integration Tests**: All major workflows
- **Performance Tests**: Load and stress testing
- **Security Tests**: Authentication and authorization

## 🐛 **Debugging**

### **Common Issues**
1. **Database Connection**: Check PostgreSQL is running
2. **Ollama Models**: Ensure models are pulled and available
3. **Supabase**: Verify local instance is running
4. **File Permissions**: Check test document access

### **Debug Mode**
```bash
# Enable debug logging
export DEBUG=true
export LOG_LEVEL=DEBUG

# Run with verbose output
python test_production_system.py --verbose
```

## 📈 **Continuous Integration**

### **Automated Testing**
- Tests run on every commit
- Performance benchmarks are tracked
- Coverage reports are generated
- Security scans are performed

### **Test Environment**
- **CI/CD**: GitHub Actions
- **Database**: PostgreSQL in Docker
- **Storage**: Local Supabase instance
- **AI Models**: Ollama in Docker

---

**Test Suite** - Comprehensive testing for KRAI Engine
