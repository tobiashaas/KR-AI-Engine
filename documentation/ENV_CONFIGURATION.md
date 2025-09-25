# KRAI Engine Environment Configuration

## 🎯 Single Source of Truth

Die `.env` Datei im Root-Verzeichnis ist die **einzige** Quelle für alle Konfigurationseinstellungen der KRAI Engine.

## 📋 Setup

1. **Template kopieren:**
   ```bash
   cp .env.template .env
   ```

2. **Konfiguration anpassen:**
   - Öffnen Sie `.env` in einem Editor
   - Passen Sie die Werte nach Bedarf an

3. **KRAI Engine starten:**
   ```bash
   ./start_krai_api.sh
   ```

## 🔧 Konfigurationskategorien

### 🔗 Supabase Lokale Konfiguration
```env
SUPABASE_URL=http://127.0.0.1:54321
SUPABASE_ANON_KEY=eyJhbGciOiJI...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOiJI...
SUPABASE_STORAGE_URL=http://127.0.0.1:54321/storage/v1
```

### 🗄️ PostgreSQL Database
```env
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=54322
POSTGRES_DB=postgres
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres
```

### 🚀 KRAI API Einstellungen
```env
KRAI_API_HOST=0.0.0.0
KRAI_API_PORT=8001
KRAI_API_DEBUG=false
KRAI_API_WORKERS=6
```

### 🤖 Ollama AI-Modelle
```env
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_LLM_MODEL=llama3.2:3b
OLLAMA_VISION_MODEL=llava:7b
OLLAMA_EMBEDDING_MODEL=embeddinggemma
OLLAMA_TIMEOUT=300
```

### 🧠 AI/ML Konfiguration
```env
ML_DEVICE=mps                     # "mps" für Apple Silicon, "cuda" für NVIDIA, "cpu" für CPU
ML_DEVICE_NAME=Apple Metal Performance Shaders
ML_MEMORY_GB=16
ML_BATCH_SIZE=32
ML_CONCURRENT_DOCUMENTS=3
```

### 📄 Dokumentenverarbeitung
```env
MAX_DOCUMENT_SIZE_MB=500
SUPPORTED_FORMATS=pdf,docx,txt
DEFAULT_CHUNKING_STRATEGY=paragraph_based
CHUNK_SIZE=512
CHUNK_OVERLAP=50
DOCUMENTS_BUCKET=krai-documents
IMAGES_BUCKET=krai-images
```

### 📊 Logging
```env
LOG_LEVEL=INFO
LOG_FORMAT=%(asctime)s - %(levelname)s - %(message)s
LOG_FILE_MAX_SIZE=10MB
LOG_FILE_BACKUP_COUNT=5
```

### 🔐 Security
```env
SECRET_KEY=your-secret-key-change-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=30
ALLOWED_ORIGINS=http://localhost:3000,http://localhost:8001,http://127.0.0.1:54323
```

### 🚢 Development/Production
```env
ENVIRONMENT=development
DEBUG=true
ENABLE_CORS=true
ENABLE_SWAGGER_UI=true
```

## ✅ Vorteile

1. **Single Source of Truth:** Alle Einstellungen an einem Ort
2. **Keine Hardcoding:** Keine hartcodierten Values im Code
3. **Environment-spezifisch:** Verschiedene .env für dev/staging/prod
4. **Sicherheit:** Sensible Daten nicht im Git
5. **Einfache Wartung:** Änderungen ohne Code-Deployment

## 🔧 Verwendung in den Komponenten

### Python Code
```python
from dotenv import load_dotenv
import os

load_dotenv()
api_port = int(os.getenv("KRAI_API_PORT", 8001))
```

### Startup Script
```bash
# Alle Environment-Variablen aus .env laden
export $(cat .env | grep -v '^#' | grep -v '^\s*$' | xargs)
```

## ⚠️ Wichtige Hinweise

- **`.env` nie committen:** Die Datei ist in `.gitignore`
- **`.env.template`:** Template für neue Environments
- **Validierung:** `start_krai_api.sh` prüft kritische Variablen
- **Defaults:** Alle Komponenten haben sinnvolle Fallback-Werte

## 🐛 Debugging

Wenn Environment-Variablen nicht geladen werden:

1. **Prüfen Sie die .env Datei:**
   ```bash
   cat .env | grep SUPABASE_URL
   ```

2. **Testen Sie das Script:**
   ```bash
   ./start_krai_api.sh
   ```

3. **Direkte Variable prüfen:**
   ```bash
   source .env && echo $SUPABASE_URL
   ```
