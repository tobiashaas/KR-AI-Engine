#!/bin/bash

# 🚀 KR-AI-Engine - Consolidated Stack Startup
# Single Source of Truth für alle Services
# Verwendet die konsolidierte Docker-Compose-Datei

set -e

echo "🚀 Starting KR-AI-Engine Consolidated Stack..."
echo "==============================================="

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.template to .env and configure your settings."
    exit 1
fi

# Load environment variables
export $(cat .env | grep -v '^#' | grep -v '^\s*$' | xargs)

echo "🔧 Environment Configuration:"
echo "   ├─ API Port: ${KRAI_API_PORT:-8001}"
echo "   ├─ Supabase: Port 54321 (API) & 54323 (Studio)"
echo "   ├─ Ollama: Port 11434"
echo "   ├─ OpenWebUI: Port 8080"
echo "   ├─ Redis: Port 6379"
echo "   └─ PostgreSQL: Port 54322"

echo ""
echo "🐳 Starting Consolidated Docker Stack..."

# Stop any existing stacks first
echo "🧹 Cleaning up existing containers..."
docker-compose down --remove-orphans 2>/dev/null || true

# Start the optimized stack
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 15

# Health checks
echo ""
echo "🔍 Checking service health..."

# Check Ollama
echo -n "   ├─ Ollama: "
if curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

# Check Supabase
echo -n "   ├─ Supabase API: "
if curl -s http://localhost:54321/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

# Check KRAI API
echo -n "   ├─ KRAI API: "
if curl -s http://localhost:${KRAI_API_PORT:-8001}/health > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready (may take a few more seconds)"
fi

# Check OpenWebUI  
echo -n "   ├─ OpenWebUI: "
if curl -s http://localhost:8080 > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

# Check Redis
echo -n "   └─ Redis: "
if docker exec krai-redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

echo ""
echo "🎉 KR-AI-Engine Consolidated Stack Started!"
echo "==============================================="
echo ""
echo "📡 Service URLs:"
echo "   ├─ 🚀 KRAI API:        http://localhost:${KRAI_API_PORT:-8001}"
echo "   ├─ 💬 Chat Interface:  http://localhost:8080" 
echo "   ├─ 🗄️  Supabase API:   http://localhost:54321"
echo "   ├─ 🎛️  Supabase Studio: http://localhost:54323"
echo "   ├─ 🤖 Ollama API:      http://localhost:11434"
echo "   └─ 🔴 Redis:           localhost:6379"
echo ""
echo "📊 Health Checks:"
echo "   ├─ 🚀 KRAI Health:     curl http://localhost:${KRAI_API_PORT:-8001}/health"
echo "   ├─ 🤖 Ollama Models:   curl http://localhost:11434/api/tags"  
echo "   └─ 🗄️  Supabase:       curl http://localhost:54321/health"
echo ""
echo "🛑 To stop the stack: docker-compose down"
echo "📜 To view logs:      docker-compose logs -f [service-name]"
echo ""

# Pull Ollama models if they don't exist
echo "🤖 Checking AI Models..."
sleep 5

# Check if models exist and pull if needed
if ! docker exec krai-ollama ollama list | grep -q "llama3.2:3b"; then
    echo "⬇️ Pulling llama3.2:3b..."
    docker exec krai-ollama ollama pull llama3.2:3b &
fi

if ! docker exec krai-ollama ollama list | grep -q "llava:7b"; then
    echo "⬇️ Pulling llava:7b..."
    docker exec krai-ollama ollama pull llava:7b &
fi

if ! docker exec krai-ollama ollama list | grep -q "embeddinggemma"; then
    echo "⬇️ Pulling embeddinggemma..."
    docker exec krai-ollama ollama pull embeddinggemma &
fi

wait

echo "✅ KR-AI-Engine Consolidated Stack is fully operational!"
echo ""
echo "🎯 Next Steps:"
echo "   1. Access KRAI API: http://localhost:${KRAI_API_PORT:-8001}"
echo "   2. Open Chat Interface: http://localhost:8080"
echo "   3. Check Supabase Studio: http://localhost:54323"
echo "   4. Upload documents via API or Chat Interface"
