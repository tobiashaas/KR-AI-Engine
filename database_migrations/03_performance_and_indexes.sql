-- ======================================================================
-- ⚡ KR-AI-ENGINE - PERFORMANCE OPTIMIZATIONS
-- ======================================================================
-- This file consolidates: 07_performance_optimizations + 11_performance_optimization
--
-- Applies:
-- - Advanced performance indexes (GIN, HNSW, Composite)
-- - Query optimization functions
-- - Materialized views for analytics
-- - Performance monitoring functions
-- ======================================================================

-- ======================================================================
-- ADVANCED PERFORMANCE INDEXES
-- ======================================================================

-- Vector similarity search indexes (HNSW for embeddings)
CREATE INDEX IF NOT EXISTS idx_embeddings_vector_hnsw 
    ON krai_intelligence.embeddings 
    USING hnsw (embedding vector_cosine_ops);

-- Full-text search indexes
CREATE INDEX IF NOT EXISTS idx_documents_content_fts 
    ON krai_core.documents 
    USING gin (to_tsvector('english', content_text));

CREATE INDEX IF NOT EXISTS idx_chunks_text_fts 
    ON krai_intelligence.chunks 
    USING gin (to_tsvector('english', text_chunk));

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer_type_status 
    ON krai_core.documents (manufacturer_id, document_type, processing_status);

CREATE INDEX IF NOT EXISTS idx_products_manufacturer_series_type 
    ON krai_core.products (manufacturer_id, series_id, product_type);

CREATE INDEX IF NOT EXISTS idx_chunks_document_status_index 
    ON krai_intelligence.chunks (document_id, processing_status, chunk_index);

-- Time-series indexes for analytics
CREATE INDEX IF NOT EXISTS idx_search_analytics_created_at_desc 
    ON krai_intelligence.search_analytics (created_at DESC);

CREATE INDEX IF NOT EXISTS idx_audit_log_changed_at_desc 
    ON krai_system.audit_log (changed_at DESC);

-- Partial indexes for active/pending records
CREATE INDEX IF NOT EXISTS idx_documents_pending_processing 
    ON krai_core.documents (id) 
    WHERE processing_status = 'pending';

CREATE INDEX IF NOT EXISTS idx_processing_queue_pending 
    ON krai_system.processing_queue (priority, created_at) 
    WHERE status = 'pending';

-- JSON/JSONB indexes for metadata queries
CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin 
    ON krai_core.documents 
    USING gin (extracted_metadata);

CREATE INDEX IF NOT EXISTS idx_products_features_gin 
    ON krai_core.products 
    USING gin (option_dependencies);

-- Hash indexes for exact lookups
CREATE INDEX IF NOT EXISTS idx_documents_file_hash 
    ON krai_core.documents (file_hash);

-- Removed duplicate: idx_images_file_hash_btree (already exists as idx_images_hash in 01_krai_complete_schema.sql)

-- ======================================================================
-- PERFORMANCE OPTIMIZATION FUNCTIONS
-- ======================================================================

-- Document search optimization function
CREATE OR REPLACE FUNCTION krai_intelligence.search_documents_optimized(
    search_query TEXT,
    manufacturer_filter UUID DEFAULT NULL,
    document_type_filter VARCHAR(100) DEFAULT NULL,
    limit_results INTEGER DEFAULT 50
)
RETURNS TABLE (
    document_id UUID,
    title TEXT,
    relevance_score REAL,
    manufacturer_name VARCHAR(100),
    document_type VARCHAR(100)
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        d.id,
        d.filename,
        ts_rank(to_tsvector('english', d.content_text), plainto_tsquery('english', search_query)) as relevance,
        m.name,
        d.document_type
    FROM krai_core.documents d
    JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
    WHERE 
        to_tsvector('english', d.content_text) @@ plainto_tsquery('english', search_query)
        AND (manufacturer_filter IS NULL OR d.manufacturer_id = manufacturer_filter)
        AND (document_type_filter IS NULL OR d.document_type = document_type_filter)
        AND d.processing_status = 'completed'
    ORDER BY relevance DESC
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Vector similarity search function
CREATE OR REPLACE FUNCTION krai_intelligence.find_similar_chunks(
    query_embedding vector(768),
    similarity_threshold DECIMAL(3,2) DEFAULT 0.7,
    limit_results INTEGER DEFAULT 20
)
RETURNS TABLE (
    chunk_id UUID,
    document_id UUID,
    similarity_score DECIMAL(5,4),
    text_preview TEXT
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        c.id,
        c.document_id,
        (1 - (e.embedding <=> query_embedding))::DECIMAL(5,4) as similarity,
        LEFT(c.text_chunk, 200) as preview
    FROM krai_intelligence.chunks c
    JOIN krai_intelligence.embeddings e ON c.id = e.chunk_id
    WHERE 
        c.processing_status = 'completed'
        AND (1 - (e.embedding <=> query_embedding)) >= similarity_threshold
    ORDER BY e.embedding <=> query_embedding
    LIMIT limit_results;
END;
$$ LANGUAGE plpgsql;

-- Analytics aggregation function
CREATE OR REPLACE FUNCTION krai_system.get_processing_statistics(
    date_from DATE DEFAULT CURRENT_DATE - INTERVAL '30 days',
    date_to DATE DEFAULT CURRENT_DATE
)
RETURNS TABLE (
    total_documents INTEGER,
    completed_documents INTEGER,
    pending_documents INTEGER,
    failed_documents INTEGER,
    avg_processing_time_hours DECIMAL(8,2),
    total_chunks INTEGER,
    total_images INTEGER
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        COUNT(*)::INTEGER as total,
        COUNT(CASE WHEN processing_status = 'completed' THEN 1 END)::INTEGER as completed,
        COUNT(CASE WHEN processing_status = 'pending' THEN 1 END)::INTEGER as pending,
        COUNT(CASE WHEN processing_status = 'failed' THEN 1 END)::INTEGER as failed,
        AVG(EXTRACT(EPOCH FROM (updated_at - created_at)) / 3600)::DECIMAL(8,2) as avg_hours,
        (SELECT COUNT(*) FROM krai_intelligence.chunks WHERE created_at BETWEEN date_from AND date_to + INTERVAL '1 day')::INTEGER,
        (SELECT COUNT(*) FROM krai_content.images WHERE created_at BETWEEN date_from AND date_to + INTERVAL '1 day')::INTEGER
    FROM krai_core.documents 
    WHERE created_at BETWEEN date_from AND date_to + INTERVAL '1 day';
END;
$$ LANGUAGE plpgsql;

-- Database maintenance function
CREATE OR REPLACE FUNCTION krai_system.optimize_database_performance()
RETURNS TEXT AS $$
DECLARE
    result_text TEXT := '';
BEGIN
    -- Update table statistics
    ANALYZE krai_core.documents;
    ANALYZE krai_intelligence.chunks;
    ANALYZE krai_intelligence.embeddings;
    ANALYZE krai_content.images;
    
    result_text := result_text || 'Table statistics updated. ';
    
    -- Reindex critical indexes if needed
    REINDEX INDEX CONCURRENTLY idx_embeddings_vector_hnsw;
    result_text := result_text || 'Vector index reindexed. ';
    
    -- Vacuum analyze for performance
    VACUUM ANALYZE krai_core.documents;
    VACUUM ANALYZE krai_intelligence.chunks;
    
    result_text := result_text || 'Vacuum analyze completed.';
    
    RETURN result_text;
END;
$$ LANGUAGE plpgsql;

-- ======================================================================
-- MATERIALIZED VIEWS FOR ANALYTICS
-- ======================================================================

-- Document processing summary view
CREATE MATERIALIZED VIEW IF NOT EXISTS krai_intelligence.document_processing_summary AS
SELECT 
    d.manufacturer_id,
    m.name as manufacturer_name,
    d.document_type,
    COUNT(*) as total_documents,
    COUNT(CASE WHEN d.processing_status = 'completed' THEN 1 END) as completed_documents,
    COUNT(CASE WHEN d.processing_status = 'pending' THEN 1 END) as pending_documents,
    COUNT(CASE WHEN d.processing_status = 'failed' THEN 1 END) as failed_documents,
    AVG(d.page_count) as avg_page_count,
    AVG(d.word_count) as avg_word_count,
    SUM(d.file_size) as total_file_size,
    MAX(d.updated_at) as last_updated
FROM krai_core.documents d
JOIN krai_core.manufacturers m ON d.manufacturer_id = m.id
GROUP BY d.manufacturer_id, m.name, d.document_type;

CREATE INDEX IF NOT EXISTS idx_document_processing_summary_manufacturer 
    ON krai_intelligence.document_processing_summary (manufacturer_id);

-- Refresh function for materialized view
CREATE OR REPLACE FUNCTION krai_intelligence.refresh_document_processing_summary()
RETURNS VOID AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY krai_intelligence.document_processing_summary;
END;
$$ LANGUAGE plpgsql;

-- ======================================================================
-- QUERY OPTIMIZATION SETTINGS
-- ======================================================================

-- Optimize for vector operations
SET maintenance_work_mem = '1GB';
SET max_parallel_workers_per_gather = 4;
SET random_page_cost = 1.1;  -- Optimized for SSD storage

-- ======================================================================
-- PERFORMANCE MONITORING
-- ======================================================================

-- Performance monitoring function
CREATE OR REPLACE FUNCTION krai_system.get_performance_metrics()
RETURNS TABLE (
    metric_name TEXT,
    metric_value DECIMAL(15,6),
    metric_unit TEXT,
    collected_at TIMESTAMP WITH TIME ZONE
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'active_connections'::TEXT,
        pg_stat_get_numbackends(oid)::DECIMAL(15,6),
        'count'::TEXT,
        NOW()
    FROM pg_database WHERE datname = current_database()
    
    UNION ALL
    
    SELECT 
        'cache_hit_ratio'::TEXT,
        (blks_hit::DECIMAL / (blks_hit + blks_read + 1)) * 100,
        'percentage'::TEXT,
        NOW()
    FROM pg_stat_database WHERE datname = current_database()
    
    UNION ALL
    
    SELECT 
        'total_documents'::TEXT,
        COUNT(*)::DECIMAL(15,6),
        'count'::TEXT,
        NOW()
    FROM krai_core.documents
    
    UNION ALL
    
    SELECT 
        'total_embeddings'::TEXT,
        COUNT(*)::DECIMAL(15,6),
        'count'::TEXT,
        NOW()
    FROM krai_intelligence.embeddings;
END;
$$ LANGUAGE plpgsql;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION krai_intelligence.search_documents_optimized TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_intelligence.find_similar_chunks TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.get_processing_statistics TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.optimize_database_performance TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_intelligence.refresh_document_processing_summary TO krai_service_role;
GRANT EXECUTE ON FUNCTION krai_system.get_performance_metrics TO krai_service_role;

-- ======================================================================
-- PERFORMANCE INDEX CLEANUP (from 11_performance_optimization.sql)  
-- ======================================================================

-- Drop any redundant or unused indexes
DROP INDEX IF EXISTS idx_images_ai_confidence;
DROP INDEX IF EXISTS idx_images_manually_reviewed;
DROP INDEX IF EXISTS idx_images_view_count;
DROP INDEX IF EXISTS idx_videos_quality_rating;
DROP INDEX IF EXISTS idx_videos_view_count;
DROP INDEX IF EXISTS idx_videos_manually_reviewed;
DROP INDEX IF EXISTS idx_manufacturers_competitor;
DROP INDEX IF EXISTS idx_products_option_dependencies_gin;
DROP INDEX IF EXISTS idx_documents_review_needed;
DROP INDEX IF EXISTS idx_documents_video_relation;
DROP INDEX IF EXISTS idx_error_codes_requires_technician;
DROP INDEX IF EXISTS idx_error_codes_requires_parts;

-- Create optimized replacement indexes
CREATE INDEX IF NOT EXISTS idx_images_processing_status 
    ON krai_content.images (ai_confidence DESC) 
    WHERE ai_confidence IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_error_codes_severity_manufacturer 
    ON krai_intelligence.error_codes (manufacturer_id, severity_level) 
    WHERE severity_level IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_manufacturers_is_competitor 
    ON krai_core.manufacturers (is_competitor, market_share_percent DESC) 
    WHERE is_competitor = true;

-- ======================================================================
-- COMPLETION MESSAGE
-- ======================================================================

-- ======================================================================
-- FOREIGN KEY PERFORMANCE INDEXES  
-- ======================================================================
-- Critical indexes for foreign key constraints identified by DB linter

-- HIGH-PRIORITY: Production-critical tables
CREATE INDEX IF NOT EXISTS idx_images_chunk_id ON krai_content.images(chunk_id);
CREATE INDEX IF NOT EXISTS idx_error_codes_chunk_id ON krai_intelligence.error_codes(chunk_id);
CREATE INDEX IF NOT EXISTS idx_error_codes_document_id ON krai_intelligence.error_codes(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_document_id ON krai_system.processing_queue(document_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_chunk_id ON krai_system.processing_queue(chunk_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_image_id ON krai_system.processing_queue(image_id);
CREATE INDEX IF NOT EXISTS idx_processing_queue_video_id ON krai_system.processing_queue(video_id);

-- CORE RELATIONSHIPS
CREATE INDEX IF NOT EXISTS idx_document_relationships_primary_document_id ON krai_core.document_relationships(primary_document_id);
CREATE INDEX IF NOT EXISTS idx_document_relationships_secondary_document_id ON krai_core.document_relationships(secondary_document_id);
CREATE INDEX IF NOT EXISTS idx_product_series_manufacturer_id ON krai_core.product_series(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_products_series_id ON krai_core.products(series_id);

-- ANALYTICS & CONFIG SCHEMAS
CREATE INDEX IF NOT EXISTS idx_search_analytics_manufacturer_filter ON krai_intelligence.search_analytics(manufacturer_filter);
CREATE INDEX IF NOT EXISTS idx_search_analytics_product_filter ON krai_intelligence.search_analytics(product_filter);
CREATE INDEX IF NOT EXISTS idx_competition_analysis_our_product_id ON krai_config.competition_analysis(our_product_id);
CREATE INDEX IF NOT EXISTS idx_competition_analysis_competitor_manufacturer_id ON krai_config.competition_analysis(competitor_manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_option_groups_manufacturer_id ON krai_config.option_groups(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_product_compatibility_base_product_id ON krai_config.product_compatibility(base_product_id);
CREATE INDEX IF NOT EXISTS idx_product_compatibility_option_product_id ON krai_config.product_compatibility(option_product_id);
CREATE INDEX IF NOT EXISTS idx_product_features_product_id ON krai_config.product_features(product_id);
CREATE INDEX IF NOT EXISTS idx_product_features_feature_id ON krai_config.product_features(feature_id);

-- CONTENT, ML, PARTS, SERVICE & USER SCHEMAS  
CREATE INDEX IF NOT EXISTS idx_instructional_videos_manufacturer_id ON krai_content.instructional_videos(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_manufacturer_id ON krai_content.print_defects(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_product_id ON krai_content.print_defects(product_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_original_image_id ON krai_content.print_defects(original_image_id);
CREATE INDEX IF NOT EXISTS idx_model_performance_history_model_id ON krai_ml.model_performance_history(model_id);
CREATE INDEX IF NOT EXISTS idx_inventory_levels_part_id ON krai_parts.inventory_levels(part_id);
CREATE INDEX IF NOT EXISTS idx_parts_catalog_manufacturer_id ON krai_parts.parts_catalog(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_service_calls_manufacturer_id ON krai_service.service_calls(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_service_calls_product_id ON krai_service.service_calls(product_id);
CREATE INDEX IF NOT EXISTS idx_service_history_service_call_id ON krai_service.service_history(service_call_id);
CREATE INDEX IF NOT EXISTS idx_user_sessions_user_id ON krai_users.user_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_users_preferred_manufacturer_id ON krai_users.users(preferred_manufacturer_id);

DO $$
BEGIN
    RAISE NOTICE '⚡ KR-AI-Engine Performance Optimization completed!';
    RAISE NOTICE '🚀 Advanced indexes created (HNSW, GIN, Composite, Foreign Keys)';
    RAISE NOTICE '📊 Analytics functions and materialized views ready';  
    RAISE NOTICE '🔧 Performance monitoring functions deployed';
    RAISE NOTICE '✅ Ready for Extensions & Storage (Step 4)';
END $$;
