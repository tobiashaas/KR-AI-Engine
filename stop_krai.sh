#!/bin/bash

# 🛑 KR-AI-Engine - Consolidated Stack Shutdown
# Stoppt alle Services der konsolidierten Docker-Compose-Datei

set -e

echo "🛑 Stopping KR-AI-Engine Consolidated Stack..."
echo "==============================================="

# Stop the consolidated stack
docker-compose down

echo ""
echo "🧹 Cleaning up containers and networks..."

# Remove orphaned containers
docker-compose down --remove-orphans

echo ""
echo "✅ KR-AI-Engine Consolidated Stack stopped!"
echo "==============================================="
echo ""
echo "📊 Container Status:"
docker ps --filter "name=krai-" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "💾 Volumes preserved:"
echo "   ├─ krai_logs (API logs)"
echo "   ├─ krai_uploads (Uploaded files)"
echo "   ├─ supabase_db_data (Database)"
echo "   ├─ supabase_storage_data (File storage)"
echo "   ├─ ollama_data (AI models)"
echo "   ├─ openwebui_data (Chat data)"
echo "   └─ redis_data (Cache)"
echo ""
echo "🗑️  To remove volumes: docker-compose down -v"
echo "🔄 To restart: ./start_krai.sh"
