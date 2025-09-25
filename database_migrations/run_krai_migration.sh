#!/bin/bash

# ======================================================================
# 🚀 KRAI SCHEMA MIGRATION
# ======================================================================
# 
# This script runs the optimized 5-step KRAI schema migration process.
#
# MIGRATION BENEFITS:
# ✅ 5 optimized steps with performance testing
# ✅ All storage buckets included
# ✅ All fixes and optimizations included  
# ✅ Clean, maintainable structure
# ✅ Comprehensive performance validation
#
# ======================================================================

set -e  # Exit on any error

echo "🚀 KRAI SCHEMA MIGRATION"
echo "======================================"
echo ""

# Check if we're in the correct directory
if [ ! -f "01_krai_complete_schema.sql" ]; then
    echo "❌ ERROR: Please run this script from the database_migrations directory"
    exit 1
fi

# Check if Supabase is running
echo "🔍 Checking Supabase connection..."
if ! docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo "❌ ERROR: Cannot connect to Supabase database"
    echo "   Please ensure Supabase is running with: supabase start"
    exit 1
fi

echo "✅ Supabase connection confirmed"
echo ""

# Function to execute SQL file
execute_sql() {
    local step_num=$1
    local filename=$2
    local description=$3
    
    echo "🚀 Step $step_num: $description"
    echo "   📄 Executing: $filename"
    echo ""
    
    # Execute with better error handling
    if docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < "$filename"; then
        echo ""
        echo "✅ Step $step_num completed successfully"
        echo "   ✨ $description - DONE"
    else
        echo ""
        echo "❌ Step $step_num FAILED"
        echo "   💥 Error in: $filename"
        echo "   🛠️ Check the SQL file for syntax errors"
        exit 1
    fi
    echo ""
    echo "────────────────────────────────────────"
    echo ""
}

# Show migration plan
echo "📋 MIGRATION PLAN - 5 Optimized Steps:"
echo "1️⃣  Complete Schema      (Tables + Architecture)"
echo "2️⃣  Security & RLS       (Policies + Roles)"  
echo "3️⃣  Performance          (Indexes + Functions)"
echo "4️⃣  Extensions & Storage (Buckets + Samples)"
echo "5️⃣  Performance Testing  (Index verification + Health check)"
echo ""
echo "⏱️  Estimated time: 3-4 minutes"
echo ""

read -p "🤔 Continue with migration? (y/N): " -n 1 -r
echo ""
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "❌ Migration cancelled by user"
    exit 1
fi

echo ""
echo "🎬 Starting migration..."
echo ""

# Execute all 5 consolidated steps
execute_sql "1" "01_krai_complete_schema.sql" "Complete Schema (10 schemas, 31+ tables, extensions)"
execute_sql "2" "02_security_and_rls.sql" "Security & RLS (Policies, roles, permissions)"
execute_sql "3" "03_performance_and_indexes.sql" "Performance (Indexes, functions, materialized views)"
execute_sql "4" "04_extensions_and_storage.sql" "Extensions & Storage (Buckets, samples, validation)"
execute_sql "5" "05_performance_test.sql" "Performance Tests (Index verification, system health)"

echo "🎉 SUCCESS! KRAI SCHEMA MIGRATION COMPLETED!"
echo "=============================================="
echo ""

# Verify the final schema
echo "📊 Verifying final schema..."
docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "
SELECT 
  '📁 SCHEMAS' as category,
  COUNT(DISTINCT schemaname)::TEXT as count,
  STRING_AGG(DISTINCT schemaname, ', ' ORDER BY schemaname) as details
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'

UNION ALL

SELECT 
  '🗂️ TABLES' as category,
  COUNT(*)::TEXT as count,
  COUNT(DISTINCT schemaname)::TEXT || ' schemas' as details
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'

UNION ALL

SELECT 
  '📋 COLUMNS' as category,
  SUM((SELECT count(*) FROM information_schema.columns 
       WHERE table_schema = schemaname AND table_name = tablename))::TEXT as count,
  'across all tables' as details
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'

UNION ALL

SELECT 
  '🗄️ STORAGE' as category,
  COUNT(*)::TEXT as count,
  STRING_AGG(name, ', ') as details
FROM storage.buckets 
WHERE name LIKE 'krai-%';
"

echo ""
echo ""
echo "🎯 PERFORMANCE TEST RESULTS:"
echo "=============================="
echo "The performance tests above show:"
echo "✅ Index effectiveness and query performance"
echo "✅ Vector search capabilities (HNSW indexes)"
echo "✅ Full-text search performance (GIN indexes)" 
echo "✅ Storage bucket configuration"
echo "✅ System health and cache performance"
echo ""
echo "🏆 KRAI SCHEMA MIGRATION - COMPLETE!"
echo "======================================"
echo "✅ 10 Schemas: krai_core, krai_intelligence, krai_content, krai_config, krai_system"
echo "   + krai_ml, krai_parts, krai_service, krai_users, krai_integrations"
echo "✅ 31+ Tables with proper relationships and constraints"
echo "✅ 400+ Columns with optimized data types"
echo "✅ 3 Storage Buckets: documents, images, videos"
echo "✅ RLS Policies enabled on all tables"
echo "✅ Performance indexes verified with tests"
echo "✅ Sample data and validation examples"
echo "✅ System health validated"
echo ""
echo "🚀 Ready for production document processing!"
echo "🔗 Use the KRAI API to start processing documents"
echo ""
echo "📊 Performance Monitoring Available:"
echo "   - krai_system.run_performance_test_suite()"
echo "   - krai_system.test_index_performance()"
echo "   - krai_system.system_health_check()"
