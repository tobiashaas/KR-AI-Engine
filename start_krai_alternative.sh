#!/bin/bash

# KR-AI-Engine Alternative Stack Startup Script
# Für PCs mit AWS ECR Image-Problemen

set -e

echo "🚀 KR-AI-Engine Alternative Stack wird gestartet..."
echo "   Verwendet Standard Docker Images statt AWS ECR"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker ist nicht verfügbar. Bitte Docker starten."
    exit 1
fi

echo "✅ Docker ist verfügbar"

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "⚠️  .env Datei nicht gefunden. Erstelle Standard-Konfiguration..."
    cat > .env << 'EOF'
# KR-AI-Engine Alternative Configuration
EXECUTION_MODE=production
ENABLE_TEXT_EXTRACTION=true
ENABLE_CHUNKING=true
ENABLE_CLASSIFICATION=true
ENABLE_IMAGE_EXTRACTION=true
ENABLE_IMAGE_ANALYSIS=true
ENABLE_IMAGE_UPLOAD=true
ENABLE_EMBEDDINGS=true
ENABLE_DATABASE_STORAGE=true
ENABLE_SUPABASE_STORAGE=true
VERBOSE_LOGGING=true
DEBUG_LOGGING=false

# Database Config (Simplified)
DATABASE_URL=postgresql://postgres:postgres@localhost:54322/postgres
POSTGRES_PASSWORD=postgres

# Ollama Config
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2:3b
VISION_MODEL=llava:7b
EMBEDDING_MODEL=embeddinggemma

# Storage Config (Minio)
MINIO_ROOT_USER=minioadmin
MINIO_ROOT_PASSWORD=minioadmin123
EOF
    echo "✅ .env Datei erstellt"
fi

# Pull alternative images first (more reliable)
echo "📦 Ziehe alternative Docker Images..."
docker pull postgres:15
docker pull minio/minio:latest
docker pull redis:7-alpine
docker pull ollama/ollama:latest
docker pull ghcr.io/open-webui/open-webui:main

echo "✅ Alle Images erfolgreich geladen"

# Start the stack
echo "🐳 Starte KR-AI-Engine Alternative Stack..."
docker compose -f docker-compose.alternative.yml up -d

# Wait a moment for services to start
echo "⏳ Warte auf Service-Initialisierung..."
sleep 10

# Check service health
echo "🏥 Prüfe Service-Status..."

# Check database
if docker compose -f docker-compose.alternative.yml exec -T supabase-db pg_isready -U postgres > /dev/null 2>&1; then
    echo "✅ Database: Verfügbar"
else
    echo "⚠️  Database: Noch nicht bereit"
fi

# Check Ollama
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama: Verfügbar"
else
    echo "⚠️  Ollama: Noch nicht bereit"
fi

# Check Minio Storage
if curl -s http://localhost:54321/minio/health/live > /dev/null 2>&1; then
    echo "✅ Storage (Minio): Verfügbar"
else
    echo "⚠️  Storage: Noch nicht bereit"
fi

echo ""
echo "🎉 KR-AI-Engine Alternative Stack gestartet!"
echo ""
echo "📋 Service URLs:"
echo "   🗄️  Database:     http://localhost:54322"
echo "   🤖 Ollama API:   http://localhost:11434"
echo "   ☁️  Storage:      http://localhost:54321 (minioadmin/minioadmin123)"
echo "   💬 Chat UI:      http://localhost:8080"
echo "   📊 Minio Admin:  http://localhost:54324"
echo ""
echo "🔧 Nächste Schritte:"
echo "   1. Warte bis alle Services bereit sind (ca. 2-3 Minuten)"
echo "   2. Initialisiere die Datenbank:"
echo "      cd database_migrations && ./run_krai_migration.sh"
echo "   3. Lade AI Models:"
echo "      docker exec -it \$(docker compose -f docker-compose.alternative.yml ps -q ollama) ollama pull llama3.2:3b"
echo ""
echo "📄 Logs anzeigen:"
echo "   docker compose -f docker-compose.alternative.yml logs -f"
echo ""
