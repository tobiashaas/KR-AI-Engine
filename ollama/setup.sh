#!/bin/bash

# 🤖 Ollama Model Setup Script
# Downloads and configures AI models for KRAI

echo "🤖 KRAI Ollama Setup"
echo "=================="

# Check if Ollama is running
if ! pgrep -x "ollama" > /dev/null; then
    echo "❌ Ollama is not running. Please start Ollama first."
    exit 1
fi

echo "✅ Ollama is running"

# Download text models
echo ""
echo "📚 Downloading text models..."
ollama pull llama3.1:8b
ollama pull mistral:7b

# Download vision models
echo ""
echo "👁️ Downloading vision models..."
ollama pull llava:7b
ollama pull bakllava:7b

# Download embedding model
echo ""
echo "🔍 Downloading embedding model..."
ollama pull nomic-embed-text:latest

# Test models
echo ""
echo "🧪 Testing models..."

echo "Testing llama3.1:8b..."
ollama run llama3.1:8b "Hello, this is a test. Please respond with 'Model working correctly.'"

echo ""
echo "Testing embedding model..."
ollama run nomic-embed-text:latest "Generate embedding for: test document"

# Create model list
echo ""
echo "📋 Installed models:"
ollama list

echo ""
echo "✅ Ollama setup complete!"
echo "🎯 Models ready for KRAI integration"