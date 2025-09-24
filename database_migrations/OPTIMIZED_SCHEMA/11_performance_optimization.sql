-- =====================================
-- KRAI ENGINE - PERFORMANCE OPTIMIZATION
-- Remove unused indexes and optimize critical queries
-- =====================================

-- =====================================
-- 1. REMOVE SOME UNUSED INDEXES
-- =====================================

-- Remove some unused indexes to reduce storage overhead
DROP INDEX IF EXISTS krai_content.idx_images_ai_confidence;
DROP INDEX IF EXISTS krai_content.idx_images_manually_reviewed;
DROP INDEX IF EXISTS krai_content.idx_images_view_count;

DROP INDEX IF EXISTS krai_content.idx_videos_quality_rating;
DROP INDEX IF EXISTS krai_content.idx_videos_view_count;
DROP INDEX IF EXISTS krai_content.idx_videos_manually_reviewed;

DROP INDEX IF EXISTS krai_core.idx_manufacturers_competitor;
DROP INDEX IF EXISTS krai_core.idx_products_model_number;
DROP INDEX IF EXISTS krai_core.idx_products_option_dependencies_gin;

DROP INDEX IF EXISTS krai_core.idx_documents_review_needed;
DROP INDEX IF EXISTS krai_core.idx_documents_video_relation;

DROP INDEX IF EXISTS krai_intelligence.idx_error_codes_requires_technician;
DROP INDEX IF EXISTS krai_intelligence.idx_error_codes_requires_parts;

-- =====================================
-- 2. ADD CRITICAL MISSING INDEXES
-- =====================================

-- Add composite index for common search patterns
CREATE INDEX IF NOT EXISTS idx_products_manufacturer_active ON krai_core.products(manufacturer_id, is_active) WHERE is_active = true;

-- Add index for document processing status
CREATE INDEX IF NOT EXISTS idx_documents_processing_status_created ON krai_core.documents(processing_status, created_at) WHERE processing_status IN ('pending', 'processing');

-- Add index for error code search patterns
CREATE INDEX IF NOT EXISTS idx_error_codes_manufacturer_severity ON krai_intelligence.error_codes(manufacturer_id, severity_level) WHERE severity_level >= 3;

-- =====================================
-- 3. CREATE FUNCTION FOR STATISTICS UPDATE
-- =====================================

-- Create function to update table statistics
CREATE OR REPLACE FUNCTION krai_system.update_table_statistics()
RETURNS void AS $$
BEGIN
    -- Update statistics for all KRAI tables
    ANALYZE krai_core.manufacturers;
    ANALYZE krai_core.products;
    ANALYZE krai_core.documents;
    ANALYZE krai_core.document_relationships;
    
    ANALYZE krai_intelligence.chunks;
    ANALYZE krai_intelligence.embeddings;
    ANALYZE krai_intelligence.error_codes;
    ANALYZE krai_intelligence.search_analytics;
    
    ANALYZE krai_content.images;
    ANALYZE krai_content.instructional_videos;
    ANALYZE krai_content.print_defects;
    ANALYZE krai_content.defect_patterns;
    
    ANALYZE krai_config.product_compatibility;
    ANALYZE krai_config.option_groups;
    ANALYZE krai_config.competitive_features;
    ANALYZE krai_config.product_features;
    
    ANALYZE krai_system.processing_queue;
    ANALYZE krai_system.performance_metrics;
    ANALYZE krai_system.audit_log;
    ANALYZE krai_system.system_health;
    
    RAISE NOTICE 'Table statistics updated successfully';
END;
$$ LANGUAGE plpgsql SET search_path = krai_system, public;

-- Grant execute permission
GRANT EXECUTE ON FUNCTION krai_system.update_table_statistics TO krai_service_role, krai_admin_role;
