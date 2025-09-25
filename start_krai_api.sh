#!/bin/bash

# KRAI Engine Startup Script
# Single Source of Truth für Environment Configuration

echo "🚀 Starting KRAI Engine Production API..."
echo "🔧 Loading environment from .env file..."

# Check if .env file exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found!"
    echo "   Please copy .env.template to .env and configure your settings."
    exit 1
fi

# Load environment variables from .env
export $(cat .env | grep -v '^#' | grep -v '^\s*$' | xargs)

# Validate critical environment variables
if [ -z "$SUPABASE_URL" ]; then
    echo "❌ Error: SUPABASE_URL not set in .env"
    exit 1
fi

if [ -z "$POSTGRES_HOST" ]; then
    echo "❌ Error: POSTGRES_HOST not set in .env"
    exit 1
fi

# Print configuration summary
echo "🔧 Configuration loaded from .env:"
echo "   ├─ Supabase URL: $SUPABASE_URL"
echo "   ├─ PostgreSQL: $POSTGRES_HOST:$POSTGRES_PORT/$POSTGRES_DB"
echo "   ├─ Ollama: $OLLAMA_BASE_URL"
echo "   ├─ API Port: $KRAI_API_PORT"
echo "   ├─ Workers: $KRAI_API_WORKERS"
echo "   ├─ ML Device: $ML_DEVICE"
echo "   ├─ Memory: ${ML_MEMORY_GB}GB"
echo "   ├─ Batch Size: $ML_BATCH_SIZE"
echo "   └─ LLM: $OLLAMA_LLM_MODEL | Embedding: $OLLAMA_EMBEDDING_MODEL | Vision: $OLLAMA_VISION_MODEL"

echo ""
echo "🚀 Starting Production API..."

# Change to backend directory and start API
cd backend && python3 production_main.py
