#!/bin/bash
# KRAI Database Import Script
# Auto-generated: 2025-09-21T14:55:51.773Z

echo "🚀 KRAI Database Import Starting..."
echo "=================================="

# Check if Supabase CLI is installed
if ! command -v supabase &> /dev/null; then
    echo "❌ Supabase CLI not found. Please install it first:"
    echo "npm install -g supabase"
    exit 1
fi

# Check for .env file
if [ ! -f .env ]; then
    echo "❌ .env file not found. Please create it with:"
    echo "SUPABASE_URL=your_project_url"
    echo "SUPABASE_SERVICE_KEY=your_service_key"
    exit 1
fi

echo "📊 1. Creating database schema..."
supabase db reset --db-url "${DATABASE_URL:-postgresql://postgres:[password]@localhost:5432/postgres}"

echo "🔧 2. Running schema creation..."
psql "${DATABASE_URL}" -f database_export/01_schema.sql

echo "🚀 3. Creating optimized indexes..."
psql "${DATABASE_URL}" -f database_export/03_indexes.sql

echo "📊 4. Importing data..."
psql "${DATABASE_URL}" -f database_export/02_data.sql

echo "✅ Database import completed!"
echo "🎯 Your KRAI database is ready for use."
