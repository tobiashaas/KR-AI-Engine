-- =====================================
-- KRAI ENGINE - PERFORMANCE OPTIMIZATIONS
-- Use-Case Specific Performance Improvements
-- =====================================

-- =====================================
-- 1. MATERIALIZED VIEWS FOR CROSS-SCHEMA QUERIES
-- =====================================

-- View: Complete Document Search Results (Cross-Schema Optimization)
CREATE MATERIALIZED VIEW krai_intelligence.document_search_cache AS
SELECT 
    c.id as chunk_id,
    c.document_id,
    c.text_chunk,
    c.extracted_error_codes,
    c.extracted_part_numbers,
    c.normalized_error_codes,
    d.file_name,
    d.document_type,
    d.manufacturer_id,
    m.name as manufacturer_name,
    d.product_ids,
    array_agg(DISTINCT p.display_name) as product_names,
    array_agg(DISTINCT e.error_code) as error_codes,
    c.created_at
FROM krai_intelligence.chunks c
JOIN krai_core.documents d ON d.id = c.document_id
JOIN krai_core.manufacturers m ON m.id = d.manufacturer_id
LEFT JOIN krai_core.products p ON p.id = ANY(d.product_ids)
LEFT JOIN krai_intelligence.error_codes e ON e.chunk_id = c.id
WHERE c.processing_status = 'completed'
  AND d.processing_status = 'completed'
GROUP BY c.id, c.document_id, c.text_chunk, c.extracted_error_codes, 
         c.extracted_part_numbers, c.normalized_error_codes, d.file_name, 
         d.document_type, d.manufacturer_id, m.name, d.product_ids, c.created_at;

-- Indexes for materialized view
CREATE INDEX idx_document_search_cache_text ON krai_intelligence.document_search_cache USING GIN (to_tsvector('english', text_chunk));
CREATE INDEX idx_document_search_cache_error_codes ON krai_intelligence.document_search_cache USING GIN (extracted_error_codes);
CREATE INDEX idx_document_search_cache_part_numbers ON krai_intelligence.document_search_cache USING GIN (extracted_part_numbers);
CREATE INDEX idx_document_search_cache_manufacturer ON krai_intelligence.document_search_cache(manufacturer_id);
CREATE INDEX idx_document_search_cache_document_type ON krai_intelligence.document_search_cache(document_type);

-- View: Product Configuration Cache (Option Validation Optimization)
CREATE MATERIALIZED VIEW krai_config.product_configuration_cache AS
SELECT 
    base.id as base_model_id,
    base.display_name as base_model_name,
    base.manufacturer_id,
    m.name as manufacturer_name,
    option.id as option_id,
    option.display_name as option_name,
    option.option_category,
    pc.is_compatible,
    pc.installation_notes,
    pc.mutually_exclusive_options,
    pc.performance_impact,
    og.group_name,
    og.group_type,
    og.max_selections,
    og.min_selections
FROM krai_core.products base
JOIN krai_core.manufacturers m ON m.id = base.manufacturer_id
JOIN krai_config.product_compatibility pc ON pc.base_product_id = base.id
JOIN krai_core.products option ON option.id = pc.option_product_id
LEFT JOIN krai_config.option_groups og ON og.option_product_ids @> ARRAY[option.id]
WHERE base.product_type = 'model'
  AND option.product_type = 'option'
  AND base.is_active = true
  AND option.is_active = true;

-- Indexes for product configuration cache
CREATE INDEX idx_product_config_cache_base_model ON krai_config.product_configuration_cache(base_model_id);
CREATE INDEX idx_product_config_cache_manufacturer ON krai_config.product_configuration_cache(manufacturer_id);
CREATE INDEX idx_product_config_cache_compatible ON krai_config.product_configuration_cache(base_model_id, is_compatible) WHERE is_compatible = true;
CREATE INDEX idx_product_config_cache_option_category ON krai_config.product_configuration_cache(option_category);
CREATE INDEX idx_product_config_cache_mutually_exclusive ON krai_config.product_configuration_cache USING GIN (mutually_exclusive_options);

-- =====================================
-- 2. OPTIMIZED SEARCH FUNCTIONS
-- =====================================

-- Optimized comprehensive search using materialized view
CREATE OR REPLACE FUNCTION krai_intelligence.optimized_comprehensive_search(
    search_query text,
    manufacturer_filter uuid DEFAULT NULL,
    product_filter uuid DEFAULT NULL,
    document_type_filter text DEFAULT NULL,
    max_results integer DEFAULT 50
)
RETURNS TABLE (
    result_type text,
    result_id uuid,
    title text,
    content text,
    similarity_score real,
    metadata jsonb
) AS $$
BEGIN
    -- Refresh materialized view if needed (can be done asynchronously)
    -- REFRESH MATERIALIZED VIEW CONCURRENTLY krai_intelligence.document_search_cache;
    
    RETURN QUERY
    SELECT 
        'chunk' as result_type,
        dsc.chunk_id as result_id,
        dsc.file_name as title,
        dsc.text_chunk as content,
        GREATEST(
            ts_rank(to_tsvector('english', dsc.text_chunk), plainto_tsquery('english', search_query)),
            similarity(dsc.text_chunk, search_query),
            CASE WHEN search_query = ANY(dsc.extracted_error_codes) THEN 1.0 ELSE 0.0 END,
            CASE WHEN krai_intelligence.normalize_error_code(search_query) = ANY(dsc.normalized_error_codes) THEN 1.0 ELSE 0.0 END
        ) as similarity_score,
        jsonb_build_object(
            'manufacturer_name', dsc.manufacturer_name,
            'document_type', dsc.document_type,
            'product_names', dsc.product_names,
            'error_codes', dsc.error_codes,
            'part_numbers', dsc.extracted_part_numbers
        ) as metadata
    FROM krai_intelligence.document_search_cache dsc
    WHERE 
        (manufacturer_filter IS NULL OR dsc.manufacturer_id = manufacturer_filter)
        AND (product_filter IS NULL OR product_filter = ANY(dsc.product_ids))
        AND (document_type_filter IS NULL OR dsc.document_type = document_type_filter)
        AND (
            to_tsvector('english', dsc.text_chunk) @@ plainto_tsquery('english', search_query)
            OR dsc.text_chunk % search_query
            OR search_query = ANY(dsc.extracted_error_codes)
            OR krai_intelligence.normalize_error_code(search_query) = ANY(dsc.normalized_error_codes)
            OR search_query = ANY(dsc.extracted_part_numbers)
        )
    ORDER BY similarity_score DESC
    LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Optimized option validation using cached data
CREATE OR REPLACE FUNCTION krai_config.optimized_validate_option_configuration(
    base_model_id uuid,
    selected_options uuid[]
)
RETURNS TABLE (
    is_valid boolean,
    validation_errors text[],
    suggested_additions uuid[],
    suggested_removals uuid[]
) AS $$
DECLARE
    errors text[] := '{}';
    additions uuid[] := '{}';
    removals uuid[] := '{}';
    config_record record;
    exclusive_violations uuid[] := '{}';
    group_violations text[] := '{}';
BEGIN
    -- Use cached configuration data for faster lookups
    FOR config_record IN 
        SELECT * FROM krai_config.product_configuration_cache
        WHERE base_model_id = config_record.base_model_id
          AND config_record.option_id = ANY(selected_options)
    LOOP
        -- Check compatibility
        IF NOT config_record.is_compatible THEN
            errors := array_append(errors, 
                'Option "' || config_record.option_name || '" is not compatible with this model');
            removals := array_append(removals, config_record.option_id);
        END IF;
        
        -- Check mutually exclusive options (using cached data)
        IF config_record.mutually_exclusive_options && selected_options THEN
            exclusive_violations := config_record.mutually_exclusive_options & selected_options;
            errors := array_append(errors, 
                'Option "' || config_record.option_name || '" conflicts with mutually exclusive options');
            removals := array_cat(removals, exclusive_violations);
        END IF;
        
        -- Check group rules (using cached data)
        IF config_record.group_name IS NOT NULL THEN
            CASE config_record.group_type
                WHEN 'exclusive' THEN
                    -- Count options in this group
                    DECLARE
                        options_in_group uuid[] := array(
                            SELECT option_id FROM krai_config.product_configuration_cache 
                            WHERE group_name = config_record.group_name 
                              AND option_id = ANY(selected_options)
                        );
                        group_count integer := array_length(options_in_group, 1);
                    BEGIN
                        IF group_count > 1 THEN
                            errors := array_append(errors, 
                                'Group "' || config_record.group_name || '" allows only one option');
                            removals := array_cat(removals, options_in_group[2:]);
                        END IF;
                    END;
                    
                WHEN 'max_limit' THEN
                    IF config_record.max_selections IS NOT NULL THEN
                        DECLARE
                            options_in_group uuid[] := array(
                                SELECT option_id FROM krai_config.product_configuration_cache 
                                WHERE group_name = config_record.group_name 
                                  AND option_id = ANY(selected_options)
                            );
                            group_count integer := array_length(options_in_group, 1);
                        BEGIN
                            IF group_count > config_record.max_selections THEN
                                errors := array_append(errors, 
                                    'Group "' || config_record.group_name || '" allows maximum ' || 
                                    config_record.max_selections || ' options');
                                removals := array_cat(removals, options_in_group[(config_record.max_selections+1):]);
                            END IF;
                        END;
                    END IF;
            END CASE;
        END IF;
    END LOOP;
    
    -- Return validation results
    is_valid := (array_length(errors, 1) IS NULL OR array_length(errors, 1) = 0);
    validation_errors := errors;
    suggested_additions := array_remove(additions, NULL);
    suggested_removals := array_remove(removals, NULL);
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 3. SPECIALIZED INDEXES FOR USE CASES
-- =====================================

-- HP-specific error code lookup optimization
CREATE INDEX CONCURRENTLY idx_error_codes_hp_optimized 
ON krai_intelligence.error_codes(manufacturer_id, normalized_code, severity_level) 
WHERE manufacturer_id = '550e8400-e29b-41d4-a716-446655440001'; -- HP Inc. ID

-- Canon-specific error code lookup optimization  
CREATE INDEX CONCURRENTLY idx_error_codes_canon_optimized 
ON krai_intelligence.error_codes(manufacturer_id, normalized_code, severity_level) 
WHERE manufacturer_id = '550e8400-e29b-41d4-a716-446655440002'; -- Canon Inc. ID

-- Active product hierarchy optimization
CREATE INDEX CONCURRENTLY idx_products_active_hierarchy 
ON krai_core.products(manufacturer_id, product_type, parent_id, is_active) 
WHERE is_active = true;

-- Document processing status optimization
CREATE INDEX CONCURRENTLY idx_documents_processing_optimized 
ON krai_core.documents(manufacturer_id, processing_status, document_type) 
WHERE processing_status = 'completed';

-- =====================================
-- 4. PERFORMANCE MONITORING FUNCTIONS
-- =====================================

-- Function: Get slow queries for optimization
CREATE OR REPLACE FUNCTION krai_system.get_slow_queries(
    min_execution_time_ms integer DEFAULT 100,
    hours_back integer DEFAULT 24
)
RETURNS TABLE (
    metric_name text,
    avg_execution_time_ms numeric,
    max_execution_time_ms integer,
    execution_count bigint,
    query_text text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pm.metric_name,
        AVG(pm.execution_time_ms)::numeric as avg_execution_time_ms,
        MAX(pm.execution_time_ms) as max_execution_time_ms,
        COUNT(*) as execution_count,
        pm.query_text
    FROM krai_system.performance_metrics pm
    WHERE pm.execution_time_ms >= min_execution_time_ms
      AND pm.recorded_at >= now() - interval '1 hour' * hours_back
      AND pm.metric_type = 'query'
    GROUP BY pm.metric_name, pm.query_text
    ORDER BY avg_execution_time_ms DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Refresh materialized views
CREATE OR REPLACE FUNCTION krai_system.refresh_search_cache()
RETURNS void AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY krai_intelligence.document_search_cache;
    REFRESH MATERIALIZED VIEW CONCURRENTLY krai_config.product_configuration_cache;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 5. AUTOMATIC REFRESH SCHEDULE
-- =====================================

-- Create function for automatic materialized view refresh
CREATE OR REPLACE FUNCTION krai_system.schedule_mv_refresh()
RETURNS void AS $$
BEGIN
    -- Refresh search cache every 5 minutes
    PERFORM krai_system.refresh_search_cache();
    
    -- Log the refresh
    INSERT INTO krai_system.performance_metrics (
        metric_name, 
        metric_type, 
        execution_time_ms,
        parameters
    ) VALUES (
        'materialized_view_refresh',
        'system',
        0,
        jsonb_build_object('timestamp', now())
    );
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 6. QUERY OPTIMIZATION HINTS
-- =====================================

-- Function: Get query execution plan with hints
CREATE OR REPLACE FUNCTION krai_system.analyze_query_performance(query_text text)
RETURNS TABLE (
    node_type text,
    relation_name text,
    cost_estimate numeric,
    rows_estimate numeric,
    index_used text
) AS $$
BEGIN
    RETURN QUERY
    EXECUTE 'EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON) ' || query_text;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- 7. PERFORMANCE COMMENTS
-- =====================================

COMMENT ON MATERIALIZED VIEW krai_intelligence.document_search_cache IS 'Cached cross-schema data for fast document search';
COMMENT ON MATERIALIZED VIEW krai_config.product_configuration_cache IS 'Cached product configuration data for fast option validation';
COMMENT ON FUNCTION krai_intelligence.optimized_comprehensive_search IS 'Optimized search function using materialized views';
COMMENT ON FUNCTION krai_config.optimized_validate_option_configuration IS 'Optimized option validation using cached configuration data';
