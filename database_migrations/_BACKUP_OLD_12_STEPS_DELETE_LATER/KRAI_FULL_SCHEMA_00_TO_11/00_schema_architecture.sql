-- =====================================
-- KRAI ENGINE - OPTIMIZED SCHEMA ARCHITECTURE
-- Professional Schema Separation & Security
-- =====================================

-- =====================================
-- 1. CREATE LOGICAL SCHEMAS
-- =====================================

-- Core business data schema
CREATE SCHEMA IF NOT EXISTS krai_core;
COMMENT ON SCHEMA krai_core IS 'Core business entities: manufacturers, products, documents';

-- AI and intelligence schema  
CREATE SCHEMA IF NOT EXISTS krai_intelligence;
COMMENT ON SCHEMA krai_intelligence IS 'AI processing: chunks, embeddings, error codes, analytics';

-- Content and media schema
CREATE SCHEMA IF NOT EXISTS krai_content;
COMMENT ON SCHEMA krai_content IS 'Media content: images, videos, print quality analysis';

-- Configuration and rules schema
CREATE SCHEMA IF NOT EXISTS krai_config;
COMMENT ON SCHEMA krai_config IS 'Business rules: compatibility, options, features';

-- System operations schema
CREATE SCHEMA IF NOT EXISTS krai_system;
COMMENT ON SCHEMA krai_system IS 'System operations: queue, monitoring, audit';

-- =====================================
-- 2. ROLE-BASED ACCESS CONTROL
-- =====================================

-- Create application roles
CREATE ROLE krai_service_role;        -- Full system access
CREATE ROLE krai_admin_role;          -- Administrative access
CREATE ROLE krai_analyst_role;        -- Read-only analytics access
CREATE ROLE krai_technician_role;     -- Limited technician access

-- =====================================
-- 3. SCHEMA PERMISSIONS
-- =====================================

-- Service role (Backend API) - Full access to all schemas
GRANT ALL ON ALL SCHEMAS IN DATABASE TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_core TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_intelligence TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_content TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_config TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_system TO krai_service_role;

-- Admin role (Dashboard) - Read/Write to core and config
GRANT USAGE ON SCHEMA krai_core, krai_config TO krai_admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA krai_core TO krai_admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA krai_config TO krai_admin_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_intelligence, krai_content, krai_system TO krai_admin_role;

-- Analyst role (Analytics) - Read-only access to intelligence and analytics
GRANT USAGE ON SCHEMA krai_intelligence TO krai_analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_intelligence TO krai_analyst_role;
GRANT USAGE ON SCHEMA krai_content TO krai_analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_content TO krai_analyst_role;

-- Technician role (Limited access) - Read-only to core and content
GRANT USAGE ON SCHEMA krai_core, krai_content TO krai_technician_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_core TO krai_technician_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_content TO krai_technician_role;

-- =====================================
-- 4. SET DEFAULT PRIVILEGES
-- =====================================

-- Ensure new tables inherit permissions
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_core GRANT ALL ON TABLES TO krai_service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_core GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO krai_admin_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_core GRANT SELECT ON TABLES TO krai_technician_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA krai_intelligence GRANT ALL ON TABLES TO krai_service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_intelligence GRANT SELECT ON TABLES TO krai_admin_role, krai_analyst_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA krai_content GRANT ALL ON TABLES TO krai_service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_content GRANT SELECT ON TABLES TO krai_admin_role, krai_analyst_role, krai_technician_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA krai_config GRANT ALL ON TABLES TO krai_service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_config GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO krai_admin_role;

ALTER DEFAULT PRIVILEGES IN SCHEMA krai_system GRANT ALL ON TABLES TO krai_service_role;
ALTER DEFAULT PRIVILEGES IN SCHEMA krai_system GRANT SELECT ON TABLES TO krai_admin_role;

-- =====================================
-- 5. SECURITY POLICIES
-- =====================================

-- Enable RLS on all tables (will be created in subsequent steps)
-- This ensures Row Level Security is enforced across all schemas

-- =====================================
-- 6. SEARCH PATH OPTIMIZATION
-- =====================================

-- Set default search path for different roles
ALTER ROLE krai_service_role SET search_path = krai_core, krai_intelligence, krai_content, krai_config, krai_system, public;
ALTER ROLE krai_admin_role SET search_path = krai_core, krai_config, public;
ALTER ROLE krai_analyst_role SET search_path = krai_intelligence, krai_content, public;
ALTER ROLE krai_technician_role SET search_path = krai_core, krai_content, public;

-- =====================================
-- 7. SCHEMA DOCUMENTATION
-- =====================================

-- Create schema documentation view
CREATE OR REPLACE VIEW krai_system.schema_overview AS
SELECT 
    schemaname,
    tablename,
    tableowner,
    CASE 
        WHEN schemaname = 'krai_core' THEN 'Core Business Data'
        WHEN schemaname = 'krai_intelligence' THEN 'AI & Intelligence'
        WHEN schemaname = 'krai_content' THEN 'Content & Media'
        WHEN schemaname = 'krai_config' THEN 'Configuration & Rules'
        WHEN schemaname = 'krai_system' THEN 'System Operations'
        ELSE 'Other'
    END as schema_category,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as table_size
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'
ORDER BY schemaname, tablename;

-- Grant access to schema overview
GRANT SELECT ON krai_system.schema_overview TO krai_admin_role, krai_analyst_role;

COMMENT ON VIEW krai_system.schema_overview IS 'Overview of all KRAI schemas and tables with size information';
