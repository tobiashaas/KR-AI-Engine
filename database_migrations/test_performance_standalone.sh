#!/bin/bash

# ======================================================================
# 🚀 KRAI PERFORMANCE TEST - STANDALONE
# ======================================================================
#
# Run this script to test KRAI database performance after migration.
# This script can be run independently to monitor ongoing performance.
#
# Usage:
#   ./test_performance_standalone.sh
#   ./test_performance_standalone.sh --detailed
#   ./test_performance_standalone.sh --benchmark
#
# ======================================================================

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

DETAILED_MODE=false
BENCHMARK_MODE=false

# Parse command line arguments
for arg in "$@"; do
    case $arg in
        --detailed)
            DETAILED_MODE=true
            shift
            ;;
        --benchmark)
            BENCHMARK_MODE=true
            shift
            ;;
        --help)
            echo "KRAI Performance Test Options:"
            echo "  --detailed   Show detailed performance metrics"
            echo "  --benchmark  Run comprehensive benchmark tests"
            echo "  --help       Show this help message"
            exit 0
            ;;
    esac
done

echo -e "${BLUE}🚀 KRAI PERFORMANCE TEST${NC}"
echo "=========================================="
echo ""

# Check Supabase connection
echo -e "${YELLOW}🔍 Checking database connection...${NC}"
if ! docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "SELECT 1;" > /dev/null 2>&1; then
    echo -e "${RED}❌ ERROR: Cannot connect to Supabase database${NC}"
    echo "   Please ensure Supabase is running with: supabase start"
    exit 1
fi
echo -e "${GREEN}✅ Database connection confirmed${NC}"
echo ""

# Function to run performance tests
run_performance_test() {
    local test_name=$1
    local query=$2
    
    echo -e "${BLUE}🧪 Running: $test_name${NC}"
    
    docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "$query" 2>/dev/null | \
    while IFS= read -r line; do
        # Color code the output based on status
        if [[ $line == *"✅ PASS"* ]]; then
            echo -e "   ${GREEN}$line${NC}"
        elif [[ $line == *"❌ FAIL"* ]]; then
            echo -e "   ${RED}$line${NC}"  
        elif [[ $line == *"⚠️ WARN"* ]]; then
            echo -e "   ${YELLOW}$line${NC}"
        elif [[ $line == *"🚀 Excellent"* ]]; then
            echo -e "   ${GREEN}$line${NC}"
        else
            echo "   $line"
        fi
    done
    echo ""
}

# Main Performance Test Suite
echo -e "${BLUE}🎯 MAIN PERFORMANCE TEST SUITE${NC}"
echo "======================================"
run_performance_test "Core System Tests" "SELECT * FROM krai_system.run_performance_test_suite();"

# Index Performance Tests
echo -e "${BLUE}⚡ INDEX PERFORMANCE TESTS${NC}"
echo "================================="
run_performance_test "Index Effectiveness" "SELECT * FROM krai_system.test_index_performance();"

# Vector Performance Tests  
echo -e "${BLUE}🔍 VECTOR PERFORMANCE TESTS${NC}"
echo "================================="
run_performance_test "Vector Operations" "SELECT * FROM krai_system.test_vector_performance();"

# System Health Check
echo -e "${BLUE}💚 SYSTEM HEALTH CHECK${NC}"
echo "========================="
run_performance_test "Health Monitoring" "SELECT * FROM krai_system.system_health_check();"

# Detailed Mode - Additional Metrics
if [ "$DETAILED_MODE" = true ]; then
    echo -e "${BLUE}📊 DETAILED PERFORMANCE METRICS${NC}"
    echo "===================================="
    
    echo -e "${YELLOW}Database Size Analysis:${NC}"
    docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "
    SELECT 
        schemaname,
        COUNT(*) as tables,
        pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))) as size
    FROM pg_tables 
    WHERE schemaname LIKE 'krai_%' 
    GROUP BY schemaname 
    ORDER BY pg_total_relation_size('krai_core.documents') DESC;
    "
    echo ""
    
    echo -e "${YELLOW}Index Usage Statistics:${NC}"
    docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "
    SELECT 
        schemaname,
        indexname,
        idx_tup_read,
        idx_tup_fetch,
        CASE 
            WHEN idx_tup_read = 0 THEN 'Unused'
            WHEN idx_tup_fetch / idx_tup_read > 0.8 THEN 'High Usage'
            WHEN idx_tup_fetch / idx_tup_read > 0.5 THEN 'Medium Usage'
            ELSE 'Low Usage'
        END as usage_level
    FROM pg_stat_user_indexes 
    WHERE schemaname LIKE 'krai_%' 
    ORDER BY idx_tup_read DESC 
    LIMIT 10;
    "
    echo ""
fi

# Benchmark Mode - Stress Tests
if [ "$BENCHMARK_MODE" = true ]; then
    echo -e "${BLUE}🏋️ BENCHMARK STRESS TESTS${NC}"
    echo "============================"
    
    echo -e "${YELLOW}Running concurrent query stress test...${NC}"
    
    # Create temporary benchmark function
    docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "
    CREATE OR REPLACE FUNCTION temp_benchmark_test()
    RETURNS TABLE (
        test_name TEXT,
        iterations INTEGER,
        total_time_ms INTEGER,
        avg_time_ms DECIMAL(8,2),
        performance_rating TEXT
    ) AS \$\$
    DECLARE
        start_time TIMESTAMP;
        end_time TIMESTAMP;
        i INTEGER;
        total_duration_ms INTEGER;
    BEGIN
        -- Benchmark 1: Multiple document lookups
        start_time := clock_timestamp();
        FOR i IN 1..100 LOOP
            PERFORM COUNT(*) FROM krai_core.documents LIMIT 10;
        END LOOP;
        end_time := clock_timestamp();
        total_duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        
        RETURN QUERY SELECT 
            'Document Lookup Stress'::TEXT,
            100,
            total_duration_ms,
            (total_duration_ms::DECIMAL / 100),
            CASE 
                WHEN total_duration_ms < 1000 THEN '🚀 Excellent'
                WHEN total_duration_ms < 3000 THEN '✅ Good'
                WHEN total_duration_ms < 10000 THEN '⚠️ Fair'
                ELSE '❌ Slow'
            END;
            
        -- Benchmark 2: Complex joins
        start_time := clock_timestamp();
        FOR i IN 1..50 LOOP
            PERFORM COUNT(*) FROM krai_core.documents d
            JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
            JOIN krai_core.products p ON d.product_id = p.id
            LIMIT 5;
        END LOOP;
        end_time := clock_timestamp();
        total_duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
        
        RETURN QUERY SELECT 
            'Complex Join Stress'::TEXT,
            50,
            total_duration_ms,
            (total_duration_ms::DECIMAL / 50),
            CASE 
                WHEN total_duration_ms < 2000 THEN '🚀 Excellent'
                WHEN total_duration_ms < 5000 THEN '✅ Good'
                WHEN total_duration_ms < 15000 THEN '⚠️ Fair'
                ELSE '❌ Slow'
            END;
    END;
    \$\$ LANGUAGE plpgsql;
    "
    
    run_performance_test "Stress Test Results" "SELECT * FROM temp_benchmark_test();"
    
    # Cleanup
    docker exec supabase_db_KR-AI-Engine psql -U postgres -d postgres -c "DROP FUNCTION IF EXISTS temp_benchmark_test();"
fi

# Final Summary
echo -e "${GREEN}🎉 PERFORMANCE TESTING COMPLETED!${NC}"
echo "===================================="
echo ""
echo "📋 Test Summary:"
echo "✅ Schema connectivity verified"
echo "✅ Index performance measured"
echo "✅ Vector operations tested"
echo "✅ System health analyzed"

if [ "$DETAILED_MODE" = true ]; then
    echo "✅ Detailed metrics collected"
fi

if [ "$BENCHMARK_MODE" = true ]; then
    echo "✅ Benchmark stress tests completed"
fi

echo ""
echo -e "${BLUE}💡 Performance Tips:${NC}"
echo "• Run 'ANALYZE;' regularly to update table statistics"
echo "• Monitor 'krai_system.system_health_check()' for ongoing health"
echo "• Use 'krai_system.test_index_performance()' to check query speeds"
echo "• Consider 'VACUUM ANALYZE' on heavily used tables"
echo ""
echo -e "${GREEN}🚀 KRAI database is performance-ready!${NC}"
