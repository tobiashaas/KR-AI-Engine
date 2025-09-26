#!/bin/bash

# 🚀 KRAI COMPLETE SCHEMA MIGRATION SCRIPT
# 
# This script MUST execute ALL 12 files in order (00-11)
# NEVER run partial migrations!

set -e  # Exit on any error

echo "🚀 KRAI COMPLETE SCHEMA MIGRATION - ALL 12 STEPS"
echo "================================================="

# Check if we're in the correct directory
if [ ! -f "00_schema_architecture.sql" ]; then
    echo "❌ ERROR: Please run this script from the KRAI_FULL_SCHEMA_00_TO_11 directory"
    exit 1
fi

# Function to execute SQL file
execute_sql() {
    local step_num=$1
    local filename=$2
    local description=$3
    
    echo "🚀 Step $step_num: $description"
    echo "   Executing: $filename"
    
    docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < "$filename"
    
    if [ $? -eq 0 ]; then
        echo "✅ Step $step_num completed successfully"
    else
        echo "❌ Step $step_num failed"
        exit 1
    fi
    echo ""
}

# Execute all 12 steps in order
execute_sql "01" "00_schema_architecture.sql" "Schema Architecture"
execute_sql "02" "01_krai_core_tables.sql" "KRAI Core Tables"
execute_sql "03" "02_krai_intelligence_tables.sql" "KRAI Intelligence Tables"
execute_sql "04" "03_krai_content_tables.sql" "KRAI Content Tables"
execute_sql "05" "04_krai_config_tables.sql" "KRAI Config Tables"
execute_sql "06" "05_krai_system_tables.sql" "KRAI System Tables"
execute_sql "07" "06_security_rls_policies.sql" "Security RLS Policies"
execute_sql "08" "07_performance_optimizations.sql" "Performance Optimizations"
execute_sql "09" "08_future_extensions.sql" "Future Extensions"
execute_sql "10" "09_option_validation_examples.sql" "Validation Examples"
execute_sql "11" "10_security_fixes.sql" "Security Fixes"
execute_sql "12" "11_performance_optimization.sql" "Final Performance Optimizations"

echo "🎉 SUCCESS! ALL 12 STEPS COMPLETED!"
echo "=================================="

# Verify the final schema
echo "📊 Verifying final schema..."
docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "
SELECT 
  'SCHEMAS' as type,
  COUNT(DISTINCT schemaname) as count
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'
UNION ALL
SELECT 
  'TABLES' as type,
  COUNT(*) as count
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'
UNION ALL
SELECT 
  'COLUMNS' as type,
  SUM((SELECT count(*) FROM information_schema.columns 
       WHERE table_schema = schemaname AND table_name = tablename))::INTEGER as count
FROM pg_tables 
WHERE schemaname LIKE 'krai_%';
"

echo "✅ KRAI Schema Migration Complete!"
echo "📝 Expected: 10 schemas, 31+ tables, 400+ columns"
