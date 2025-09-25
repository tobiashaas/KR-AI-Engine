#!/bin/bash

# KRAI Engine - Complete Stack Startup
# Starts all services in the correct order

set -e

echo "🚀 Starting KRAI Engine Complete Stack..."
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
echo "🐳 Starting Docker Stack..."

# Start all services
docker-compose up -d

echo ""
echo "⏳ Waiting for services to start..."
sleep 10

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
if docker exec -it $(docker ps -q -f name=redis) redis-cli ping > /dev/null 2>&1; then
    echo "✅ Running"
else
    echo "❌ Not ready"
fi

echo ""
echo "🎉 KRAI Engine Stack Started!"
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
if ! docker exec $(docker ps -q -f name=ollama) ollama list | grep -q "llama3.2:3b"; then
    echo "⬇️ Pulling llama3.2:3b..."
    docker exec $(docker ps -q -f name=ollama) ollama pull llama3.2:3b &
fi

if ! docker exec $(docker ps -q -f name=ollama) ollama list | grep -q "llava:7b"; then
    echo "⬇️ Pulling llava:7b..."
    docker exec $(docker ps -q -f name=ollama) ollama pull llava:7b &
fi

if ! docker exec $(docker ps -q -f name=ollama) ollama list | grep -q "embeddinggemma"; then
    echo "⬇️ Pulling embeddinggemma..."
    docker exec $(docker ps -q -f name=ollama) ollama pull embeddinggemma &
fi

wait

echo "✅ KRAI Engine Stack is fully operational!"
