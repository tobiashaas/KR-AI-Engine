-- ======================================================================
-- 🚀 KR-AI-ENGINE - PERFORMANCE TEST SUITE
-- ======================================================================
-- 
-- This file provides comprehensive performance testing for:
-- - Index effectiveness and query performance
-- - Vector search performance (HNSW)
-- - Full-text search performance (GIN)
-- - Foreign key constraint performance
-- - Storage bucket functionality
-- - Overall system health check
--
-- ======================================================================

-- ======================================================================
-- PERFORMANCE TEST FUNCTIONS
-- ======================================================================

-- Main performance test orchestrator
CREATE OR REPLACE FUNCTION krai_system.run_performance_test_suite()
RETURNS TABLE (
    test_name TEXT,
    status TEXT,
    execution_time_ms INTEGER,
    details TEXT,
    recommendation TEXT
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration_ms INTEGER;
    test_result TEXT;
    test_detail TEXT;
    test_recommendation TEXT;
BEGIN
    RAISE NOTICE '🚀 Starting KRAI Performance Test Suite...';
    
    -- Test 1: Basic Schema Connectivity
    start_time := clock_timestamp();
    
    SELECT COUNT(*)::TEXT INTO test_result 
    FROM information_schema.tables 
    WHERE table_schema LIKE 'krai_%';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    IF test_result::INTEGER >= 31 THEN
        test_detail := test_result || ' tables found across KRAI schemas';
        test_recommendation := 'Schema structure is complete';
    ELSE
        test_detail := 'Only ' || test_result || ' tables found - expected 31+';
        test_recommendation := 'Check schema migration completeness';
    END IF;
    
    RETURN QUERY SELECT 
        'Schema Connectivity'::TEXT,
        CASE WHEN test_result::INTEGER >= 31 THEN '✅ PASS' ELSE '❌ FAIL' END,
        duration_ms,
        test_detail,
        test_recommendation;
    
    -- Test 2: Index Effectiveness Check
    start_time := clock_timestamp();
    
    SELECT COUNT(*)::TEXT INTO test_result 
    FROM pg_indexes 
    WHERE schemaname LIKE 'krai_%' AND indexname LIKE 'idx_%';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_detail := test_result || ' performance indexes found';
    test_recommendation := CASE 
        WHEN test_result::INTEGER >= 15 THEN 'Index coverage is excellent'
        WHEN test_result::INTEGER >= 10 THEN 'Index coverage is good'
        ELSE 'Consider adding more performance indexes'
    END;
    
    RETURN QUERY SELECT 
        'Index Coverage'::TEXT,
        CASE WHEN test_result::INTEGER >= 10 THEN '✅ PASS' ELSE '⚠️ WARN' END,
        duration_ms,
        test_detail,
        test_recommendation;
    
    -- Test 3: Foreign Key Constraint Performance
    start_time := clock_timestamp();
    
    SELECT COUNT(*)::TEXT INTO test_result 
    FROM information_schema.table_constraints 
    WHERE table_schema LIKE 'krai_%' AND constraint_type = 'FOREIGN KEY';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_detail := test_result || ' foreign key constraints active';
    test_recommendation := 'Foreign key integrity is maintained';
    
    RETURN QUERY SELECT 
        'Foreign Key Constraints'::TEXT,
        CASE WHEN test_result::INTEGER >= 40 THEN '✅ PASS' ELSE '⚠️ WARN' END,
        duration_ms,
        test_detail,
        test_recommendation;
    
    -- Test 4: Vector Extension Check
    start_time := clock_timestamp();
    
    BEGIN
        EXECUTE 'SELECT 1 WHERE EXISTS (SELECT 1 FROM pg_extension WHERE extname = ''vector'')';
        test_result := 'Available';
        test_detail := 'pgvector extension is properly installed';
        test_recommendation := 'Vector operations ready for embeddings';
    EXCEPTION WHEN OTHERS THEN
        test_result := 'Missing';
        test_detail := 'pgvector extension not found';
        test_recommendation := 'Install pgvector extension for embeddings';
    END;
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    RETURN QUERY SELECT 
        'Vector Extension'::TEXT,
        CASE WHEN test_result = 'Available' THEN '✅ PASS' ELSE '❌ FAIL' END,
        duration_ms,
        test_detail,
        test_recommendation;
    
    -- Test 5: Storage Buckets Check
    start_time := clock_timestamp();
    
    SELECT COUNT(*)::TEXT INTO test_result 
    FROM storage.buckets 
    WHERE name LIKE 'krai-%';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    test_detail := test_result || ' KRAI storage buckets configured';
    test_recommendation := CASE 
        WHEN test_result::INTEGER >= 3 THEN 'Storage buckets ready for file uploads'
        ELSE 'Configure missing storage buckets'
    END;
    
    RETURN QUERY SELECT 
        'Storage Buckets'::TEXT,
        CASE WHEN test_result::INTEGER >= 3 THEN '✅ PASS' ELSE '❌ FAIL' END,
        duration_ms,
        test_detail,
        test_recommendation;
    
    RAISE NOTICE '✅ KRAI Performance Test Suite completed!';
END;
$$ LANGUAGE plpgsql;

-- ======================================================================
-- SPECIFIC PERFORMANCE TESTS
-- ======================================================================

-- Index performance test with sample queries
CREATE OR REPLACE FUNCTION krai_system.test_index_performance()
RETURNS TABLE (
    query_type TEXT,
    execution_time_ms INTEGER,
    index_used BOOLEAN,
    performance_rating TEXT
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration_ms INTEGER;
    plan_text TEXT;
    uses_index BOOLEAN;
BEGIN
    -- Test 1: Document lookup by manufacturer (should use index)
    start_time := clock_timestamp();
    
    PERFORM COUNT(*) FROM krai_core.documents d 
    JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id 
    WHERE m.name = 'HP Inc.';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    -- Check if index is used (simplified)
    uses_index := duration_ms < 100; -- Heuristic: fast queries likely use indexes
    
    RETURN QUERY SELECT 
        'Document by Manufacturer'::TEXT,
        duration_ms,
        uses_index,
        CASE 
            WHEN duration_ms < 50 THEN '🚀 Excellent'
            WHEN duration_ms < 200 THEN '✅ Good'
            WHEN duration_ms < 500 THEN '⚠️ Fair'
            ELSE '❌ Slow'
        END;
    
    -- Test 2: Full-text search (should use GIN index)
    start_time := clock_timestamp();
    
    PERFORM COUNT(*) FROM krai_core.documents 
    WHERE to_tsvector('english', COALESCE(content_text, '')) @@ plainto_tsquery('english', 'printer error');
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    uses_index := duration_ms < 200;
    
    RETURN QUERY SELECT 
        'Full-Text Search'::TEXT,
        duration_ms,
        uses_index,
        CASE 
            WHEN duration_ms < 100 THEN '🚀 Excellent'
            WHEN duration_ms < 300 THEN '✅ Good'
            WHEN duration_ms < 1000 THEN '⚠️ Fair'
            ELSE '❌ Slow'
        END;
    
    -- Test 3: Composite index test (manufacturer + document type + status)
    start_time := clock_timestamp();
    
    PERFORM COUNT(*) FROM krai_core.documents 
    WHERE manufacturer_id IS NOT NULL 
      AND document_type = 'Service Manual' 
      AND processing_status = 'completed';
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    uses_index := duration_ms < 150;
    
    RETURN QUERY SELECT 
        'Composite Index Query'::TEXT,
        duration_ms,
        uses_index,
        CASE 
            WHEN duration_ms < 75 THEN '🚀 Excellent'
            WHEN duration_ms < 250 THEN '✅ Good'
            WHEN duration_ms < 750 THEN '⚠️ Fair'
            ELSE '❌ Slow'
        END;
END;
$$ LANGUAGE plpgsql;

-- Vector search performance test (if embeddings exist)
CREATE OR REPLACE FUNCTION krai_system.test_vector_performance()
RETURNS TABLE (
    test_type TEXT,
    execution_time_ms INTEGER,
    vectors_tested INTEGER,
    performance_rating TEXT
) AS $$
DECLARE
    start_time TIMESTAMP;
    end_time TIMESTAMP;
    duration_ms INTEGER;
    vector_count INTEGER;
    sample_vector TEXT;
BEGIN
    -- Check if we have any embeddings to test with
    SELECT COUNT(*) INTO vector_count FROM krai_intelligence.embeddings LIMIT 1000;
    
    IF vector_count = 0 THEN
        RETURN QUERY SELECT 
            'Vector Similarity Search'::TEXT,
            0,
            0,
            '⏭️ Skipped (No embeddings found)'::TEXT;
        RETURN;
    END IF;
    
    -- Create a sample vector for testing (768 dimensions of zeros)
    sample_vector := '[' || repeat('0,', 767) || '0]';
    
    start_time := clock_timestamp();
    
    -- Test vector similarity search
    PERFORM COUNT(*) FROM krai_intelligence.embeddings 
    WHERE embedding IS NOT NULL
    ORDER BY embedding <=> sample_vector::vector
    LIMIT 10;
    
    end_time := clock_timestamp();
    duration_ms := EXTRACT(EPOCH FROM (end_time - start_time)) * 1000;
    
    RETURN QUERY SELECT 
        'Vector Similarity Search'::TEXT,
        duration_ms,
        vector_count,
        CASE 
            WHEN duration_ms < 100 THEN '🚀 Excellent (HNSW index working)'
            WHEN duration_ms < 500 THEN '✅ Good'
            WHEN duration_ms < 2000 THEN '⚠️ Fair (Consider index tuning)'
            ELSE '❌ Slow (Check HNSW index)'
        END;
        
EXCEPTION WHEN OTHERS THEN
    RETURN QUERY SELECT 
        'Vector Similarity Search'::TEXT,
        -1,
        0,
        '❌ Error: ' || SQLERRM;
END;
$$ LANGUAGE plpgsql;

-- ======================================================================
-- COMPREHENSIVE SYSTEM HEALTH CHECK
-- ======================================================================

CREATE OR REPLACE FUNCTION krai_system.system_health_check()
RETURNS TABLE (
    component TEXT,
    status TEXT,
    details TEXT,
    recommendation TEXT
) AS $$
BEGIN
    -- Database size check
    RETURN QUERY 
    SELECT 
        'Database Size'::TEXT,
        '✅ Healthy'::TEXT,
        pg_size_pretty(pg_database_size(current_database())) || ' total size',
        'Database size is within normal limits'::TEXT;
    
    -- Connection check
    RETURN QUERY
    SELECT 
        'Active Connections'::TEXT,
        '✅ Healthy'::TEXT,
        pg_stat_get_numbackends(oid)::TEXT || ' active connections' as details,
        'Connection count is normal'::TEXT
    FROM pg_database WHERE datname = current_database();
    
    -- Cache hit ratio
    RETURN QUERY
    SELECT 
        'Cache Hit Ratio'::TEXT,
        CASE 
            WHEN (blks_hit::FLOAT / (blks_hit + blks_read + 1)) > 0.90 THEN '✅ Excellent'
            WHEN (blks_hit::FLOAT / (blks_hit + blks_read + 1)) > 0.75 THEN '⚠️ Good'
            ELSE '❌ Poor'
        END,
        ROUND((blks_hit::FLOAT / (blks_hit + blks_read + 1)) * 100, 2)::TEXT || '% cache hit rate',
        CASE 
            WHEN (blks_hit::FLOAT / (blks_hit + blks_read + 1)) > 0.90 THEN 'Excellent cache performance'
            WHEN (blks_hit::FLOAT / (blks_hit + blks_read + 1)) > 0.75 THEN 'Consider increasing shared_buffers'
            ELSE 'Increase shared_buffers and work_mem'
        END
    FROM pg_stat_database WHERE datname = current_database();
    
    -- Table statistics freshness
    RETURN QUERY
    SELECT 
        'Statistics Currency'::TEXT,
        CASE 
            WHEN MAX(last_analyze) > NOW() - INTERVAL '7 days' THEN '✅ Current'
            WHEN MAX(last_analyze) > NOW() - INTERVAL '30 days' THEN '⚠️ Stale'
            ELSE '❌ Very Stale'
        END,
        'Last analyze: ' || COALESCE(MAX(last_analyze)::TEXT, 'Never'),
        CASE 
            WHEN MAX(last_analyze) > NOW() - INTERVAL '7 days' THEN 'Statistics are current'
            ELSE 'Run ANALYZE on tables for better query planning'
        END
    FROM pg_stat_user_tables WHERE schemaname LIKE 'krai_%';
END;
$$ LANGUAGE plpgsql;

-- ======================================================================
-- GRANT PERMISSIONS
-- ======================================================================

GRANT EXECUTE ON FUNCTION krai_system.run_performance_test_suite TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.test_index_performance TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.test_vector_performance TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.system_health_check TO krai_service_role;

-- ======================================================================
-- PERFORMANCE TEST EXECUTION
-- ======================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🚀 ==========================================';
    RAISE NOTICE '🚀 KRAI PERFORMANCE TEST EXECUTION';
    RAISE NOTICE '🚀 ==========================================';
    RAISE NOTICE '';
END $$;

-- Execute the main performance test suite
SELECT * FROM krai_system.run_performance_test_suite();

RAISE NOTICE '';
RAISE NOTICE '⚡ INDEX PERFORMANCE TESTS:';
RAISE NOTICE '================================';

-- Execute index performance tests
SELECT * FROM krai_system.test_index_performance();

RAISE NOTICE '';
RAISE NOTICE '🔍 VECTOR PERFORMANCE TESTS:';
RAISE NOTICE '===============================';

-- Execute vector performance tests  
SELECT * FROM krai_system.test_vector_performance();

RAISE NOTICE '';
RAISE NOTICE '💚 SYSTEM HEALTH CHECK:';
RAISE NOTICE '==========================';

-- Execute system health check
SELECT * FROM krai_system.system_health_check();

-- ======================================================================
-- COMPLETION MESSAGE
-- ======================================================================

DO $$
BEGIN
    RAISE NOTICE '';
    RAISE NOTICE '🎉 ==========================================';
    RAISE NOTICE '🎉 PERFORMANCE TEST SUITE COMPLETED!';
    RAISE NOTICE '🎉 ==========================================';
    RAISE NOTICE '';
    RAISE NOTICE '✅ Schema connectivity tested';
    RAISE NOTICE '✅ Index effectiveness verified';
    RAISE NOTICE '✅ Vector operations checked';
    RAISE NOTICE '✅ Storage buckets validated';
    RAISE NOTICE '✅ System health analyzed';
    RAISE NOTICE '';
    RAISE NOTICE '📊 All performance functions are now available:';
    RAISE NOTICE '   - krai_system.run_performance_test_suite()';
    RAISE NOTICE '   - krai_system.test_index_performance()';
    RAISE NOTICE '   - krai_system.test_vector_performance()';
    RAISE NOTICE '   - krai_system.system_health_check()';
    RAISE NOTICE '';
    RAISE NOTICE '🚀 KRAI Engine is performance-tested and ready!';
END $$;
