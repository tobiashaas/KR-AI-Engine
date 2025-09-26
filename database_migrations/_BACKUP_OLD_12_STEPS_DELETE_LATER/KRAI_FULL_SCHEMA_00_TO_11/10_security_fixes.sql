-- =====================================
-- KRAI ENGINE - SECURITY FIXES
-- Fix function search path and extension issues
-- =====================================

-- =====================================
-- 1. FIX FUNCTION SEARCH PATH ISSUES
-- =====================================

-- Fix all functions to have secure search_path
ALTER FUNCTION krai_intelligence.optimized_comprehensive_search(text, uuid, uuid, text, integer) SET search_path = krai_intelligence, krai_core, krai_content, krai_config, krai_system, public;
ALTER FUNCTION krai_system.get_system_health_overview() SET search_path = krai_system, public;
ALTER FUNCTION krai_config.ai_get_available_options(uuid) SET search_path = krai_config, krai_core, public;
ALTER FUNCTION krai_system.get_performance_stats(text, integer) SET search_path = krai_system, public;
ALTER FUNCTION krai_intelligence.normalize_error_code(text) SET search_path = krai_intelligence, public;
ALTER FUNCTION krai_intelligence.refresh_document_search_cache() SET search_path = krai_intelligence, public;
ALTER FUNCTION krai_config.ai_validate_configuration(uuid, text[]) SET search_path = krai_config, krai_core, public;
ALTER FUNCTION krai_core.update_updated_at_column() SET search_path = krai_core, public;
ALTER FUNCTION krai_config.refresh_product_configuration_cache() SET search_path = krai_config, public;
ALTER FUNCTION krai_core.get_hp_documentation_set(uuid, text) SET search_path = krai_core, krai_intelligence, public;
ALTER FUNCTION krai_config.optimized_validate_option_configuration(uuid, uuid[]) SET search_path = krai_config, krai_core, public;
ALTER FUNCTION krai_intelligence.check_user_permissions(text, text) SET search_path = krai_intelligence, public;
ALTER FUNCTION krai_system.get_queue_status() SET search_path = krai_system, public;
ALTER FUNCTION krai_content.get_defect_patterns_by_category(text) SET search_path = krai_content, public;
ALTER FUNCTION krai_content.get_images_for_part_numbers(text[]) SET search_path = krai_content, public;

-- =====================================
-- 2. MOVE EXTENSIONS OUT OF PUBLIC SCHEMA
-- =====================================

-- Create dedicated schema for extensions
CREATE SCHEMA IF NOT EXISTS extensions;

-- Move extensions to dedicated schema
ALTER EXTENSION pg_trgm SET SCHEMA extensions;
ALTER EXTENSION unaccent SET SCHEMA extensions;
ALTER EXTENSION vector SET SCHEMA extensions;

-- =====================================
-- 3. ADD MISSING FOREIGN KEY INDEX
-- =====================================

-- Add index for products.parent_id foreign key
CREATE INDEX IF NOT EXISTS idx_products_parent_id_fkey ON krai_core.products(parent_id) WHERE parent_id IS NOT NULL;

-- =====================================
-- 4. GRANT PERMISSIONS ON EXTENSIONS SCHEMA
-- =====================================

-- Grant usage on extensions schema
GRANT USAGE ON SCHEMA extensions TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;

-- =====================================
-- 5. UPDATE SEARCH PATH FOR ROLES
-- =====================================

-- Update search paths to include extensions schema
ALTER ROLE krai_service_role SET search_path = krai_core, krai_intelligence, krai_content, krai_config, krai_system, extensions, public;
ALTER ROLE krai_admin_role SET search_path = krai_core, krai_config, extensions, public;
ALTER ROLE krai_analyst_role SET search_path = krai_intelligence, krai_content, extensions, public;
ALTER ROLE krai_technician_role SET search_path = krai_core, krai_content, extensions, public;
