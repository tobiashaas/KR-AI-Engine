-- ======================================================================
-- 🚀 KR-AI-ENGINE - COMPLETE SCHEMA
-- ======================================================================
-- Creates the complete KR-AI-Engine database schema including:
-- - All 10 specialized schemas for different functional areas
-- - 31+ optimized tables with proper relationships and constraints
-- - UUID extensions and pgvector support for AI/ML functionality
-- - Performance analysis extensions for query optimization
-- ======================================================================

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm"; 
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "vector" WITH SCHEMA extensions;

-- Performance Analysis Extensions (in secure extensions schema)
CREATE EXTENSION IF NOT EXISTS "hypopg" WITH SCHEMA extensions;        -- Hypothetical indexes simulation
CREATE EXTENSION IF NOT EXISTS "index_advisor" WITH SCHEMA extensions; -- Query index recommendations

-- ======================================================================
-- SCHEMA ARCHITECTURE
-- ======================================================================

-- Create all KRAI schemas
CREATE SCHEMA IF NOT EXISTS krai_core;
CREATE SCHEMA IF NOT EXISTS krai_intelligence; 
CREATE SCHEMA IF NOT EXISTS krai_content;
CREATE SCHEMA IF NOT EXISTS krai_config;
CREATE SCHEMA IF NOT EXISTS krai_system;
CREATE SCHEMA IF NOT EXISTS krai_ml;
CREATE SCHEMA IF NOT EXISTS krai_parts;
CREATE SCHEMA IF NOT EXISTS krai_service;
CREATE SCHEMA IF NOT EXISTS krai_users;
CREATE SCHEMA IF NOT EXISTS krai_integrations;

-- Schema comments
COMMENT ON SCHEMA krai_core IS 'Core business entities: manufacturers, products, documents';
COMMENT ON SCHEMA krai_intelligence IS 'AI/ML intelligence: chunks, embeddings, analytics';
COMMENT ON SCHEMA krai_content IS 'Media content: images, videos, defect patterns';
COMMENT ON SCHEMA krai_config IS 'Configuration: features, options, compatibility';
COMMENT ON SCHEMA krai_system IS 'System operations: audit, queue, health monitoring';
COMMENT ON SCHEMA krai_ml IS 'Machine learning models and training data';
COMMENT ON SCHEMA krai_parts IS 'Parts catalog and inventory management';
COMMENT ON SCHEMA krai_service IS 'Service management and technician workflows';
COMMENT ON SCHEMA krai_users IS 'User management and access control';
COMMENT ON SCHEMA krai_integrations IS 'External system integrations and APIs';

-- ======================================================================
-- KRAI_CORE TABLES
-- ======================================================================

-- Manufacturers table
CREATE TABLE IF NOT EXISTS krai_core.manufacturers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    short_name VARCHAR(10),
    country VARCHAR(50),
    founded_year INTEGER,
    website VARCHAR(255),
    support_email VARCHAR(255),
    support_phone VARCHAR(50),
    logo_url TEXT,
    is_competitor BOOLEAN DEFAULT false,
    market_share_percent DECIMAL(5,2),
    annual_revenue_usd BIGINT,
    employee_count INTEGER,
    headquarters_address TEXT,
    stock_symbol VARCHAR(10),
    primary_business_segment VARCHAR(100),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Product Series table  
CREATE TABLE IF NOT EXISTS krai_core.product_series (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    series_name VARCHAR(100) NOT NULL,
    series_code VARCHAR(50),
    launch_date DATE,
    end_of_life_date DATE,
    target_market VARCHAR(100),
    price_range VARCHAR(50),
    key_features JSONB DEFAULT '{}',
    series_description TEXT,
    marketing_name VARCHAR(150),
    successor_series_id UUID REFERENCES krai_core.product_series(id),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(manufacturer_id, series_name)
);

-- Products table
CREATE TABLE IF NOT EXISTS krai_core.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    parent_id UUID REFERENCES krai_core.products(id),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    series_id UUID REFERENCES krai_core.product_series(id),
    model_number VARCHAR(100) NOT NULL,
    model_name VARCHAR(200),
    product_type VARCHAR(50) NOT NULL DEFAULT 'printer',
    launch_date DATE,
    end_of_life_date DATE,
    msrp_usd DECIMAL(10,2),
    weight_kg DECIMAL(8,2),
    dimensions_mm JSONB,
    color_options TEXT[],
    connectivity_options TEXT[],
    print_technology VARCHAR(50),
    max_print_speed_ppm INTEGER,
    max_resolution_dpi INTEGER,
    max_paper_size VARCHAR(20),
    duplex_capable BOOLEAN DEFAULT false,
    network_capable BOOLEAN DEFAULT false,
    mobile_print_support BOOLEAN DEFAULT false,
    supported_languages TEXT[],
    energy_star_certified BOOLEAN DEFAULT false,
    warranty_months INTEGER DEFAULT 12,
    service_manual_url TEXT,
    parts_catalog_url TEXT,
    driver_download_url TEXT,
    firmware_version VARCHAR(50),
    option_dependencies JSONB DEFAULT '{}',
    replacement_parts JSONB DEFAULT '{}',
    common_issues JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Documents table
CREATE TABLE IF NOT EXISTS krai_core.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID REFERENCES krai_core.manufacturers(id),
    product_id UUID REFERENCES krai_core.products(id),
    filename VARCHAR(255) NOT NULL,
    original_filename VARCHAR(255),
    file_size BIGINT,
    file_hash VARCHAR(64),
    storage_path TEXT,
    storage_url TEXT,
    document_type VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    version VARCHAR(50),
    publish_date DATE,
    page_count INTEGER,
    word_count INTEGER,
    character_count INTEGER,
    content_text TEXT,
    content_summary TEXT,
    extracted_metadata JSONB DEFAULT '{}',
    processing_status VARCHAR(50) DEFAULT 'pending',
    confidence_score DECIMAL(3,2),
    manual_review_required BOOLEAN DEFAULT false,
    manual_review_completed BOOLEAN DEFAULT false,
    manual_review_notes TEXT,
    ocr_confidence DECIMAL(3,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    -- Add missing classification columns
    manufacturer VARCHAR(100),
    series VARCHAR(100),
    models TEXT[]
);

-- Document Relationships table
CREATE TABLE IF NOT EXISTS krai_core.document_relationships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    primary_document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    secondary_document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    relationship_type VARCHAR(50) NOT NULL,
    relationship_strength DECIMAL(3,2) DEFAULT 0.5,
    auto_discovered BOOLEAN DEFAULT true,
    manual_verification BOOLEAN DEFAULT false,
    verification_date TIMESTAMP WITH TIME ZONE,
    verified_by VARCHAR(100),
    notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(primary_document_id, secondary_document_id, relationship_type)
);

-- ======================================================================
-- KRAI_INTELLIGENCE TABLES
-- ======================================================================

-- Chunks table
CREATE TABLE IF NOT EXISTS krai_intelligence.chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    text_chunk TEXT NOT NULL,
    chunk_index INTEGER NOT NULL,
    page_start INTEGER,
    page_end INTEGER,
    processing_status VARCHAR(20) DEFAULT 'pending' CHECK (processing_status IN ('pending', 'completed', 'failed')),
    fingerprint VARCHAR(32) NOT NULL,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Embeddings table  
CREATE TABLE IF NOT EXISTS krai_intelligence.embeddings (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID NOT NULL REFERENCES krai_intelligence.chunks(id) ON DELETE CASCADE,
    embedding vector(768),
    model_name VARCHAR(100) NOT NULL,
    model_version VARCHAR(50) DEFAULT 'latest',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Error Codes table
CREATE TABLE IF NOT EXISTS krai_intelligence.error_codes (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    chunk_id UUID REFERENCES krai_intelligence.chunks(id) ON DELETE CASCADE,
    document_id UUID REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    manufacturer_id UUID REFERENCES krai_core.manufacturers(id),
    error_code VARCHAR(20) NOT NULL,
    error_description TEXT,
    solution_text TEXT,
    page_number INTEGER,
    confidence_score DECIMAL(3,2),
    extraction_method VARCHAR(50),
    requires_technician BOOLEAN DEFAULT false,
    requires_parts BOOLEAN DEFAULT false,
    estimated_fix_time_minutes INTEGER,
    severity_level VARCHAR(20),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Search Analytics table
CREATE TABLE IF NOT EXISTS krai_intelligence.search_analytics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    search_query TEXT NOT NULL,
    search_type VARCHAR(50),
    results_count INTEGER,
    click_through_rate DECIMAL(5,4),
    user_satisfaction_rating INTEGER CHECK (user_satisfaction_rating >= 1 AND user_satisfaction_rating <= 5),
    search_duration_ms INTEGER,
    result_relevance_scores JSONB,
    user_session_id VARCHAR(100),
    user_id UUID,
    manufacturer_filter UUID REFERENCES krai_core.manufacturers(id),
    product_filter UUID REFERENCES krai_core.products(id),
    document_type_filter VARCHAR(100),
    language_filter VARCHAR(10),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ======================================================================
-- KRAI_CONTENT TABLES
-- ======================================================================

-- Content Chunks table
CREATE TABLE IF NOT EXISTS krai_content.chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    content TEXT NOT NULL,
    chunk_type VARCHAR(50) DEFAULT 'text',
    chunk_index INTEGER NOT NULL,
    page_number INTEGER,
    section_title VARCHAR(255),
    confidence_score DECIMAL(3,2),
    language VARCHAR(10) DEFAULT 'en',
    processing_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Images table
CREATE TABLE IF NOT EXISTS krai_content.images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES krai_content.chunks(id),
    filename VARCHAR(255),
    original_filename VARCHAR(255),
    storage_path TEXT,
    storage_url TEXT NOT NULL,
    file_size INTEGER,
    image_format VARCHAR(10),
    width_px INTEGER,
    height_px INTEGER,
    page_number INTEGER,
    image_index INTEGER,
    image_type VARCHAR(50),
    ai_description TEXT,
    ai_confidence DECIMAL(3,2),
    contains_text BOOLEAN DEFAULT false,
    ocr_text TEXT,
    ocr_confidence DECIMAL(3,2),
    manual_description TEXT,
    tags TEXT[],
    file_hash VARCHAR(64),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Instructional Videos table
CREATE TABLE IF NOT EXISTS krai_content.instructional_videos (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    title VARCHAR(255) NOT NULL,
    description TEXT,
    video_url TEXT NOT NULL,
    thumbnail_url TEXT,
    duration_seconds INTEGER,
    file_size_mb INTEGER,
    video_format VARCHAR(20),
    resolution VARCHAR(20),
    language VARCHAR(10) DEFAULT 'en',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Print Defects table  
CREATE TABLE IF NOT EXISTS krai_content.print_defects (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    product_id UUID REFERENCES krai_core.products(id),
    original_image_id UUID REFERENCES krai_content.images(id),
    defect_name VARCHAR(100) NOT NULL,
    defect_category VARCHAR(50),
    defect_description TEXT,
    example_image_url TEXT,
    annotated_image_url TEXT,
    detection_confidence DECIMAL(3,2),
    common_causes JSONB DEFAULT '[]',
    recommended_solutions JSONB DEFAULT '[]',
    related_error_codes TEXT[],
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ======================================================================
-- KRAI_CONFIG TABLES
-- ======================================================================

-- Option Groups table
CREATE TABLE IF NOT EXISTS krai_config.option_groups (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    group_name VARCHAR(100) NOT NULL,
    group_description TEXT,
    display_order INTEGER DEFAULT 0,
    is_required BOOLEAN DEFAULT false,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(manufacturer_id, group_name)
);

-- Product Features table
CREATE TABLE IF NOT EXISTS krai_config.product_features (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    product_id UUID NOT NULL REFERENCES krai_core.products(id) ON DELETE CASCADE,
    feature_id UUID NOT NULL REFERENCES krai_config.option_groups(id),
    feature_value TEXT,
    is_standard BOOLEAN DEFAULT true,
    additional_cost_usd DECIMAL(10,2) DEFAULT 0.00,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(product_id, feature_id)
);

-- Product Compatibility table
CREATE TABLE IF NOT EXISTS krai_config.product_compatibility (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    base_product_id UUID NOT NULL REFERENCES krai_core.products(id),
    option_product_id UUID NOT NULL REFERENCES krai_core.products(id),
    compatibility_type VARCHAR(50) DEFAULT 'compatible',
    compatibility_notes TEXT,
    validated_date DATE,
    validation_status VARCHAR(20) DEFAULT 'pending',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(base_product_id, option_product_id)
);

-- Competition Analysis table
CREATE TABLE IF NOT EXISTS krai_config.competition_analysis (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    our_product_id UUID NOT NULL REFERENCES krai_core.products(id),
    competitor_manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    competitor_model_name VARCHAR(200),
    comparison_category VARCHAR(100),
    our_advantage TEXT,
    competitor_advantage TEXT,
    feature_comparison JSONB DEFAULT '{}',
    price_comparison JSONB DEFAULT '{}',
    market_position VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ======================================================================
-- KRAI_SYSTEM TABLES
-- ======================================================================

-- Audit Log table
CREATE TABLE IF NOT EXISTS krai_system.audit_log (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    table_name VARCHAR(100) NOT NULL,
    record_id UUID NOT NULL,
    operation VARCHAR(10) NOT NULL CHECK (operation IN ('INSERT', 'UPDATE', 'DELETE')),
    old_values JSONB,
    new_values JSONB,
    changed_by VARCHAR(100),
    changed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    session_id VARCHAR(100),
    ip_address INET,
    user_agent TEXT
);

-- System Metrics table
CREATE TABLE IF NOT EXISTS krai_system.system_metrics (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    metric_name VARCHAR(100) NOT NULL,
    metric_value DECIMAL(15,6),
    metric_unit VARCHAR(20),
    metric_category VARCHAR(50),
    collection_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    server_instance VARCHAR(100),
    additional_context JSONB DEFAULT '{}'
);

-- Processing Queue table
CREATE TABLE IF NOT EXISTS krai_system.processing_queue (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID REFERENCES krai_core.documents(id),
    chunk_id UUID REFERENCES krai_intelligence.chunks(id),
    image_id UUID REFERENCES krai_content.images(id),
    video_id UUID REFERENCES krai_content.instructional_videos(id),
    task_type VARCHAR(50) NOT NULL,
    priority INTEGER DEFAULT 5,
    status VARCHAR(20) DEFAULT 'pending',
    scheduled_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    started_at TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    error_message TEXT,
    retry_count INTEGER DEFAULT 0,
    max_retries INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Health Check table
CREATE TABLE IF NOT EXISTS krai_system.health_checks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    check_type VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL,
    response_time_ms INTEGER,
    error_message TEXT,
    details JSONB DEFAULT '{}',
    checked_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ======================================================================
-- FUTURE EXTENSION SCHEMAS
-- ======================================================================

-- ML Schema Tables
CREATE TABLE IF NOT EXISTS krai_ml.model_registry (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_name VARCHAR(100) NOT NULL UNIQUE,
    model_version VARCHAR(50) NOT NULL,
    model_type VARCHAR(50) NOT NULL,
    framework VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_ml.model_performance_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    model_id UUID NOT NULL REFERENCES krai_ml.model_registry(id),
    accuracy_score DECIMAL(5,4),
    precision_score DECIMAL(5,4),
    recall_score DECIMAL(5,4),
    f1_score DECIMAL(5,4),
    evaluated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Parts Schema Tables
CREATE TABLE IF NOT EXISTS krai_parts.parts_catalog (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    part_number VARCHAR(100) NOT NULL,
    part_name VARCHAR(255),
    part_description TEXT,
    part_category VARCHAR(100),
    unit_price_usd DECIMAL(10,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_parts.inventory_levels (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    part_id UUID NOT NULL REFERENCES krai_parts.parts_catalog(id),
    warehouse_location VARCHAR(100),
    current_stock INTEGER DEFAULT 0,
    minimum_stock_level INTEGER DEFAULT 0,
    maximum_stock_level INTEGER DEFAULT 1000,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Service Schema Tables
CREATE TABLE IF NOT EXISTS krai_service.service_calls (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id),
    product_id UUID REFERENCES krai_core.products(id),
    assigned_technician_id UUID REFERENCES krai_service.service_history(id),
    call_status VARCHAR(50) DEFAULT 'open',
    priority_level INTEGER DEFAULT 3,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_service.service_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_call_id UUID REFERENCES krai_service.service_calls(id),
    performed_by UUID REFERENCES krai_service.service_history(id),
    service_date TIMESTAMP WITH TIME ZONE,
    service_notes TEXT,
    parts_used JSONB DEFAULT '[]',
    labor_hours DECIMAL(4,2),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Users Schema Tables  
CREATE TABLE IF NOT EXISTS krai_users.users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    preferred_manufacturer_id UUID REFERENCES krai_core.manufacturers(id),
    username VARCHAR(100) UNIQUE NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    role VARCHAR(50) DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_users.user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES krai_users.users(id),
    session_token VARCHAR(255) NOT NULL,
    expires_at TIMESTAMP WITH TIME ZONE NOT NULL,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Integrations Schema Tables
CREATE TABLE IF NOT EXISTS krai_integrations.api_keys (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_name VARCHAR(100) NOT NULL,
    api_key_encrypted TEXT NOT NULL,
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_integrations.webhook_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    webhook_url TEXT NOT NULL,
    request_payload JSONB,
    response_status INTEGER,
    response_body TEXT,
    processed_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- ======================================================================
-- Basic Indexes for Performance  
-- ======================================================================

-- Core indexes
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer ON krai_core.documents(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_documents_product ON krai_core.documents(product_id);
CREATE INDEX IF NOT EXISTS idx_documents_type ON krai_core.documents(document_type);
CREATE INDEX IF NOT EXISTS idx_documents_status ON krai_core.documents(processing_status);

-- Intelligence indexes  
CREATE INDEX IF NOT EXISTS idx_chunks_document ON krai_intelligence.chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk ON krai_intelligence.embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_error_codes_manufacturer ON krai_intelligence.error_codes(manufacturer_id);

-- Content indexes
CREATE INDEX IF NOT EXISTS idx_images_document ON krai_content.images(document_id);
CREATE INDEX IF NOT EXISTS idx_images_hash ON krai_content.images(file_hash);

-- System indexes
CREATE INDEX IF NOT EXISTS idx_audit_log_table ON krai_system.audit_log(table_name);
CREATE INDEX IF NOT EXISTS idx_audit_log_timestamp ON krai_system.audit_log(changed_at);

-- ======================================================================
-- COMPLETION MESSAGE
-- ======================================================================

DO $$
BEGIN
    RAISE NOTICE '🎉 KRAI Complete Schema successfully created!';
    RAISE NOTICE '📊 Created 10 schemas with 31+ tables';
    RAISE NOTICE '⚡ Basic performance indexes applied';
    RAISE NOTICE '🔧 Ready for Security & RLS (Step 2)';
END $$;
