# 🤖 KRAI Makefile
# Simplified commands for development and deployment

.PHONY: help setup install dev test clean docker

# Default target
help:
	@echo "🤖 KRAI - Available Commands:"
	@echo ""
	@echo "📦 Setup & Installation:"
	@echo "  make install    - Install all dependencies (Node.js + Python)"
	@echo "  make setup      - Full project setup including database"
	@echo "  make venv       - Create Python virtual environment"
	@echo ""
	@echo "🚀 Development:"
	@echo "  make dev        - Start development servers"
	@echo "  make dev-api    - Start only Python backend"
	@echo "  make dev-admin  - Start only Laravel admin"
	@echo ""
	@echo "🧪 Testing:"
	@echo "  make test       - Run all tests"
	@echo "  make test-api   - Test Python backend"
	@echo "  make test-db    - Test database connection"
	@echo ""
	@echo "🐳 Docker:"
	@echo "  make docker-up      - Start Docker stack"
	@echo "  make docker-down    - Stop Docker stack"
	@echo "  make docker-rebuild - Rebuild and restart containers"
	@echo "  make docker-logs    - View Docker logs"
	@echo ""
	@echo "🤖 AI Models:"
	@echo "  make ollama-setup   - Download Ollama models"
	@echo "  make ollama-list    - List installed models"
	@echo ""
	@echo "🧹 Maintenance:"
	@echo "  make clean      - Clean temporary files"
	@echo "  make reset      - Reset to clean state"

# Installation targets
install:
	@echo "📦 Installing dependencies..."
	npm install
	pip install -r requirements.txt
	@echo "✅ Installation complete!"

setup: install
	@echo "🔧 Setting up KRAI project..."
	npm run setup
	@echo "✅ Setup complete!"

venv:
	@echo "🐍 Creating Python virtual environment..."
	python -m venv .venv
	@echo "✅ Virtual environment created!"
	@echo "💡 Activate with: source .venv/bin/activate"

# Development targets
dev:
	@echo "🚀 Starting development servers..."
	npm run dev

dev-api:
	@echo "🐍 Starting Python API server..."
	npm run dev:backend

dev-admin:
	@echo "🖥️ Starting Laravel admin..."
	npm run dev:frontend

# Testing targets
test:
	@echo "🧪 Running all tests..."
	npm test
	npm run test:python

test-api:
	@echo "🧪 Testing Python backend..."
	npm run test:python

test-db:
	@echo "🧪 Testing database connection..."
	npm run test:supabase

# Docker targets
docker-up:
	@echo "🐳 Starting Docker stack..."
	npm run docker:up

docker-down:
	@echo "🐳 Stopping Docker stack..."
	npm run docker:down

docker-rebuild:
	@echo "🐳 Rebuilding Docker containers..."
	npm run docker:rebuild

docker-logs:
	@echo "🐳 Viewing Docker logs..."
	npm run docker:logs

# AI Model targets
ollama-setup:
	@echo "🤖 Setting up Ollama models..."
	./ollama/setup.sh

ollama-list:
	@echo "🤖 Listing Ollama models..."
	ollama list

# Maintenance targets
clean:
	@echo "🧹 Cleaning temporary files..."
	rm -rf __pycache__/
	rm -rf .pytest_cache/
	rm -rf node_modules/.cache/
	rm -rf backend/__pycache__/
	rm -rf *.log
	find . -name "*.pyc" -delete
	find . -name ".DS_Store" -delete
	@echo "✅ Cleanup complete!"

reset: clean
	@echo "🔄 Resetting to clean state..."
	rm -rf node_modules/
	rm -rf .venv/
	@echo "✅ Reset complete! Run 'make setup' to reinstall."

# Health check
health:
	@echo "🏥 Checking system health..."
	npm run health

# Quick status
status:
	@echo "📊 KRAI System Status:"
	@echo "Node.js version: $$(node --version)"
	@echo "Python version: $$(python --version)"
	@echo "Docker status: $$(docker --version 2>/dev/null || echo 'Not installed')"
	@echo "Ollama status: $$(ollama --version 2>/dev/null || echo 'Not installed')"