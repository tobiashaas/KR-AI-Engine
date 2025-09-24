-- =====================================
-- KRAI ENGINE - SECURITY & RLS POLICIES
-- Row Level Security Implementation for All Schemas
-- =====================================

-- =====================================
-- 1. ENABLE RLS ON ALL TABLES
-- =====================================

-- KRAI_CORE Schema
ALTER TABLE krai_core.manufacturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_core.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_core.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_core.document_relationships ENABLE ROW LEVEL SECURITY;

-- KRAI_INTELLIGENCE Schema
ALTER TABLE krai_intelligence.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_intelligence.embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_intelligence.error_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_intelligence.search_analytics ENABLE ROW LEVEL SECURITY;

-- KRAI_CONTENT Schema
ALTER TABLE krai_content.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_content.instructional_videos ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_content.print_defects ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_content.defect_patterns ENABLE ROW LEVEL SECURITY;

-- KRAI_CONFIG Schema
ALTER TABLE krai_config.product_compatibility ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_config.option_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_config.competitive_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_config.product_features ENABLE ROW LEVEL SECURITY;

-- KRAI_SYSTEM Schema
ALTER TABLE krai_system.processing_queue ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_system.performance_metrics ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_system.audit_log ENABLE ROW LEVEL SECURITY;
ALTER TABLE krai_system.system_health ENABLE ROW LEVEL SECURITY;

-- =====================================
-- 2. SERVICE ROLE POLICIES (Full Access)
-- =====================================

-- Service role has full access to all tables
CREATE POLICY service_role_full_access ON krai_core.manufacturers FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_core.products FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_core.documents FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_core.document_relationships FOR ALL TO krai_service_role USING (true);

CREATE POLICY service_role_full_access ON krai_intelligence.chunks FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_intelligence.embeddings FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_intelligence.error_codes FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_intelligence.search_analytics FOR ALL TO krai_service_role USING (true);

CREATE POLICY service_role_full_access ON krai_content.images FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_content.instructional_videos FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_content.print_defects FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_content.defect_patterns FOR ALL TO krai_service_role USING (true);

CREATE POLICY service_role_full_access ON krai_config.product_compatibility FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_config.option_groups FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_config.competitive_features FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_config.product_features FOR ALL TO krai_service_role USING (true);

CREATE POLICY service_role_full_access ON krai_system.processing_queue FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_system.performance_metrics FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_system.audit_log FOR ALL TO krai_service_role USING (true);
CREATE POLICY service_role_full_access ON krai_system.system_health FOR ALL TO krai_service_role USING (true);

-- =====================================
-- 3. ADMIN ROLE POLICIES (Core + Config Read/Write)
-- =====================================

-- Admin role: Full access to core and config, read-only to others
CREATE POLICY admin_core_access ON krai_core.manufacturers FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_core_access ON krai_core.products FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_core_access ON krai_core.documents FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_core_access ON krai_core.document_relationships FOR ALL TO krai_admin_role USING (true);

CREATE POLICY admin_config_access ON krai_config.product_compatibility FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_config_access ON krai_config.option_groups FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_config_access ON krai_config.competitive_features FOR ALL TO krai_admin_role USING (true);
CREATE POLICY admin_config_access ON krai_config.product_features FOR ALL TO krai_admin_role USING (true);

-- Admin role: Read-only access to intelligence, content, system
CREATE POLICY admin_intelligence_read ON krai_intelligence.chunks FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_intelligence_read ON krai_intelligence.embeddings FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_intelligence_read ON krai_intelligence.error_codes FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_intelligence_read ON krai_intelligence.search_analytics FOR SELECT TO krai_admin_role USING (true);

CREATE POLICY admin_content_read ON krai_content.images FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_content_read ON krai_content.instructional_videos FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_content_read ON krai_content.print_defects FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_content_read ON krai_content.defect_patterns FOR SELECT TO krai_admin_role USING (true);

CREATE POLICY admin_system_read ON krai_system.processing_queue FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_system_read ON krai_system.performance_metrics FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_system_read ON krai_system.audit_log FOR SELECT TO krai_admin_role USING (true);
CREATE POLICY admin_system_read ON krai_system.system_health FOR SELECT TO krai_admin_role USING (true);

-- =====================================
-- 4. ANALYST ROLE POLICIES (Intelligence + Content Read-Only)
-- =====================================

-- Analyst role: Read-only access to intelligence and content
CREATE POLICY analyst_intelligence_read ON krai_intelligence.chunks FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_intelligence_read ON krai_intelligence.embeddings FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_intelligence_read ON krai_intelligence.error_codes FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_intelligence_read ON krai_intelligence.search_analytics FOR SELECT TO krai_analyst_role USING (true);

CREATE POLICY analyst_content_read ON krai_content.images FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_content_read ON krai_content.instructional_videos FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_content_read ON krai_content.print_defects FOR SELECT TO krai_analyst_role USING (true);
CREATE POLICY analyst_content_read ON krai_content.defect_patterns FOR SELECT TO krai_analyst_role USING (true);

-- =====================================
-- 5. TECHNICIAN ROLE POLICIES (Core + Content Read-Only)
-- =====================================

-- Technician role: Read-only access to core and content
CREATE POLICY technician_core_read ON krai_core.manufacturers FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_core_read ON krai_core.products FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_core_read ON krai_core.documents FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_core_read ON krai_core.document_relationships FOR SELECT TO krai_technician_role USING (true);

CREATE POLICY technician_content_read ON krai_content.images FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_content_read ON krai_content.instructional_videos FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_content_read ON krai_content.print_defects FOR SELECT TO krai_technician_role USING (true);
CREATE POLICY technician_content_read ON krai_content.defect_patterns FOR SELECT TO krai_technician_role USING (true);

-- =====================================
-- 6. ANONYMOUS USER POLICIES (Limited Public Access)
-- =====================================

-- Anonymous users: Limited read access to public data
CREATE POLICY anonymous_manufacturers_read ON krai_core.manufacturers FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_products_read ON krai_core.products FOR SELECT TO anonymous USING (is_active = true);
CREATE POLICY anonymous_documents_read ON krai_core.documents FOR SELECT TO anonymous USING (processing_status = 'completed');
CREATE POLICY anonymous_document_relationships_read ON krai_core.document_relationships FOR SELECT TO anonymous USING (true);

CREATE POLICY anonymous_chunks_read ON krai_intelligence.chunks FOR SELECT TO anonymous USING (processing_status = 'completed');
CREATE POLICY anonymous_embeddings_read ON krai_intelligence.embeddings FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_error_codes_read ON krai_intelligence.error_codes FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_search_analytics_read ON krai_intelligence.search_analytics FOR SELECT TO anonymous USING (true);

CREATE POLICY anonymous_images_read ON krai_content.images FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_videos_read ON krai_content.instructional_videos FOR SELECT TO anonymous USING (is_official = true);
CREATE POLICY anonymous_print_defects_read ON krai_content.print_defects FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_defect_patterns_read ON krai_content.defect_patterns FOR SELECT TO anonymous USING (true);

CREATE POLICY anonymous_compatibility_read ON krai_config.product_compatibility FOR SELECT TO anonymous USING (is_compatible = true);
CREATE POLICY anonymous_option_groups_read ON krai_config.option_groups FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_competitive_features_read ON krai_config.competitive_features FOR SELECT TO anonymous USING (true);
CREATE POLICY anonymous_product_features_read ON krai_config.product_features FOR SELECT TO anonymous USING (verified = true);

-- Anonymous users: Can create search analytics (for public search)
CREATE POLICY anonymous_search_analytics_create ON krai_intelligence.search_analytics FOR INSERT TO anonymous WITH CHECK (true);

-- =====================================
-- 7. SECURITY FUNCTIONS
-- =====================================

-- Function: Check if user has access to manufacturer data
CREATE OR REPLACE FUNCTION krai_system.check_manufacturer_access(manufacturer_id uuid)
RETURNS boolean AS $$
DECLARE
    current_role text;
BEGIN
    -- Get current user role
    current_role := current_setting('role', true);
    
    -- Service role has full access
    IF current_role = 'krai_service_role' OR current_role = 'krai_admin_role' THEN
        RETURN true;
    END IF;
    
    -- Anonymous users can access all manufacturers
    IF current_role = 'anonymous' THEN
        RETURN true;
    END IF;
    
    -- Other roles need specific manufacturer access
    -- This could be extended with user-specific manufacturer permissions
    RETURN true; -- For now, allow access to all manufacturers
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function: Check if user can modify data
CREATE OR REPLACE FUNCTION krai_system.can_modify_data()
RETURNS boolean AS $$
DECLARE
    current_role text;
BEGIN
    current_role := current_setting('role', true);
    
    -- Only service and admin roles can modify data
    RETURN current_role IN ('krai_service_role', 'krai_admin_role');
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- 8. AUDIT TRIGGER SETUP
-- =====================================

-- Create audit triggers for critical tables
CREATE TRIGGER audit_manufacturers_trigger
    AFTER INSERT OR UPDATE OR DELETE ON krai_core.manufacturers
    FOR EACH ROW EXECUTE FUNCTION krai_system.create_audit_entry();

CREATE TRIGGER audit_products_trigger
    AFTER INSERT OR UPDATE OR DELETE ON krai_core.products
    FOR EACH ROW EXECUTE FUNCTION krai_system.create_audit_entry();

CREATE TRIGGER audit_documents_trigger
    AFTER INSERT OR UPDATE OR DELETE ON krai_core.documents
    FOR EACH ROW EXECUTE FUNCTION krai_system.create_audit_entry();

CREATE TRIGGER audit_error_codes_trigger
    AFTER INSERT OR UPDATE OR DELETE ON krai_intelligence.error_codes
    FOR EACH ROW EXECUTE FUNCTION krai_system.create_audit_entry();

CREATE TRIGGER audit_compatibility_trigger
    AFTER INSERT OR UPDATE OR DELETE ON krai_config.product_compatibility
    FOR EACH ROW EXECUTE FUNCTION krai_system.create_audit_entry();

-- =====================================
-- 9. SECURITY VIEWS
-- =====================================

-- View for public product information (limited data)
CREATE VIEW krai_core.public_products AS
SELECT 
    p.id,
    p.name,
    p.display_name,
    p.model_number,
    p.year_introduced,
    p.device_category,
    p.form_factor,
    m.name as manufacturer_name,
    m.display_name as manufacturer_display_name
FROM krai_core.products p
JOIN krai_core.manufacturers m ON m.id = p.manufacturer_id
WHERE p.is_active = true;

-- Grant access to public products view
GRANT SELECT ON krai_core.public_products TO anonymous, krai_technician_role, krai_analyst_role, krai_admin_role, krai_service_role;

-- View for public error codes (without sensitive information)
CREATE VIEW krai_intelligence.public_error_codes AS
SELECT 
    e.id,
    e.error_code,
    e.error_description,
    e.severity_level,
    e.device_categories,
    m.name as manufacturer_name
FROM krai_intelligence.error_codes e
JOIN krai_core.manufacturers m ON m.id = e.manufacturer_id;

-- Grant access to public error codes view
GRANT SELECT ON krai_intelligence.public_error_codes TO anonymous, krai_technician_role, krai_analyst_role, krai_admin_role, krai_service_role;

-- =====================================
-- 10. SECURITY COMMENTS
-- =====================================

COMMENT ON SCHEMA krai_core IS 'Core business data with role-based access control';
COMMENT ON SCHEMA krai_intelligence IS 'AI and intelligence data with restricted access';
COMMENT ON SCHEMA krai_content IS 'Media content with public read access';
COMMENT ON SCHEMA krai_config IS 'Configuration data with admin-only write access';
COMMENT ON SCHEMA krai_system IS 'System operations with service-role access only';

-- =====================================
-- 11. SECURITY VALIDATION
-- =====================================

-- Function to validate security setup
CREATE OR REPLACE FUNCTION krai_system.validate_security_setup()
RETURNS TABLE (
    check_name text,
    status text,
    details text
) AS $$
BEGIN
    -- Check if RLS is enabled on all tables
    RETURN QUERY
    SELECT 
        'RLS Enabled Check'::text as check_name,
        CASE WHEN COUNT(*) = 16 THEN 'PASS'::text ELSE 'FAIL'::text END as status,
        'RLS enabled on ' || COUNT(*) || ' out of 16 tables'::text as details
    FROM pg_class c
    JOIN pg_namespace n ON n.oid = c.relnamespace
    WHERE n.nspname LIKE 'krai_%'
      AND c.relkind = 'r'
      AND c.relrowsecurity = true;
    
    -- Check if roles exist
    RETURN QUERY
    SELECT 
        'Roles Check'::text as check_name,
        CASE WHEN COUNT(*) = 4 THEN 'PASS'::text ELSE 'FAIL'::text END as status,
        'Found ' || COUNT(*) || ' out of 4 required roles'::text as details
    FROM pg_roles
    WHERE rolname LIKE 'krai_%_role';
    
    -- Check if policies exist
    RETURN QUERY
    SELECT 
        'Policies Check'::text as check_name,
        CASE WHEN COUNT(*) >= 50 THEN 'PASS'::text ELSE 'FAIL'::text END as status,
        'Found ' || COUNT(*) || ' RLS policies'::text as details
    FROM pg_policies
    WHERE schemaname LIKE 'krai_%';
END;
$$ LANGUAGE plpgsql;

-- Grant access to security validation function
GRANT EXECUTE ON FUNCTION krai_system.validate_security_setup() TO krai_admin_role, krai_service_role;
