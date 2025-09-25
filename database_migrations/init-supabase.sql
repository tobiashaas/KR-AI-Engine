-- KRAI Engine Supabase Local Initialization
-- This script sets up the complete KRAI Engine database schema in local Supabase

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "unaccent";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";

-- Create schemas
CREATE SCHEMA IF NOT EXISTS krai_core;
CREATE SCHEMA IF NOT EXISTS krai_intelligence;
CREATE SCHEMA IF NOT EXISTS krai_content;
CREATE SCHEMA IF NOT EXISTS krai_config;
CREATE SCHEMA IF NOT EXISTS krai_system;

-- Set search path
ALTER DATABASE postgres SET search_path TO krai_core, krai_intelligence, krai_content, krai_config, krai_system, public;

-- Create roles
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'krai_service_role') THEN
        CREATE ROLE krai_service_role;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'krai_admin_role') THEN
        CREATE ROLE krai_admin_role;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'krai_analyst_role') THEN
        CREATE ROLE krai_analyst_role;
    END IF;
    
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'krai_technician_role') THEN
        CREATE ROLE krai_technician_role;
    END IF;
END
$$;

-- Grant schema permissions
GRANT USAGE ON SCHEMA krai_core TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;
GRANT USAGE ON SCHEMA krai_intelligence TO krai_service_role, krai_admin_role, krai_analyst_role;
GRANT USAGE ON SCHEMA krai_content TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;
GRANT USAGE ON SCHEMA krai_config TO krai_service_role, krai_admin_role;
GRANT USAGE ON SCHEMA krai_system TO krai_service_role, krai_admin_role;

-- Create core tables
CREATE TABLE IF NOT EXISTS krai_core.manufacturers (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) NOT NULL UNIQUE,
    display_name VARCHAR(200),
    description TEXT,
    website_url TEXT,
    support_email VARCHAR(255),
    logo_url TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_core.product_series (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id) ON DELETE CASCADE,
    name VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(manufacturer_id, name)
);

CREATE TABLE IF NOT EXISTS krai_core.products (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID NOT NULL REFERENCES krai_core.manufacturers(id) ON DELETE CASCADE,
    series_id UUID REFERENCES krai_core.product_series(id) ON DELETE SET NULL,
    parent_id UUID REFERENCES krai_core.products(id) ON DELETE CASCADE,
    model_number VARCHAR(100) NOT NULL,
    display_name VARCHAR(200),
    description TEXT,
    category VARCHAR(50),
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    UNIQUE(manufacturer_id, model_number)
);

CREATE TABLE IF NOT EXISTS krai_core.documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    manufacturer_id UUID REFERENCES krai_core.manufacturers(id) ON DELETE SET NULL,
    product_id UUID REFERENCES krai_core.products(id) ON DELETE SET NULL,
    title VARCHAR(500) NOT NULL,
    document_type VARCHAR(50) NOT NULL,
    version VARCHAR(100),
    language VARCHAR(10) DEFAULT 'en',
    file_path TEXT,
    file_size BIGINT,
    file_hash VARCHAR(64),
    storage_url TEXT,
    metadata JSONB DEFAULT '{}',
    processing_status VARCHAR(50) DEFAULT 'pending',
    processed_at TIMESTAMP WITH TIME ZONE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_content.chunks (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    chunk_type VARCHAR(50) DEFAULT 'text',
    metadata JSONB DEFAULT '{}',
    embedding VECTOR(384),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

CREATE TABLE IF NOT EXISTS krai_content.images (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    document_id UUID NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
    chunk_id UUID REFERENCES krai_content.chunks(id) ON DELETE SET NULL,
    image_index INTEGER NOT NULL,
    file_path TEXT,
    storage_url TEXT,
    file_hash VARCHAR(64),
    width INTEGER,
    height INTEGER,
    format VARCHAR(10),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes
CREATE INDEX IF NOT EXISTS idx_products_manufacturer_id ON krai_core.products(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_products_parent_id ON krai_core.products(parent_id);
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer_id ON krai_core.documents(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_documents_product_id ON krai_core.documents(product_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON krai_content.chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_embedding ON krai_content.chunks USING hnsw (embedding vector_cosine_ops);
CREATE INDEX IF NOT EXISTS idx_images_document_id ON krai_content.images(document_id);

-- Create storage buckets
INSERT INTO storage.buckets (id, name, public) VALUES 
    ('krai-documents', 'krai-documents', false),
    ('krai-images', 'krai-images', false)
ON CONFLICT (id) DO NOTHING;

-- Create storage policies
CREATE POLICY "Enable read access for all users" ON storage.objects FOR SELECT USING (true);
CREATE POLICY "Enable insert for authenticated users only" ON storage.objects FOR INSERT WITH CHECK (true);
CREATE POLICY "Enable update for authenticated users only" ON storage.objects FOR UPDATE USING (true);
CREATE POLICY "Enable delete for authenticated users only" ON storage.objects FOR DELETE USING (true);

-- Insert sample data
INSERT INTO krai_core.manufacturers (id, name, display_name, description) VALUES 
    ('550e8400-e29b-41d4-a716-446655440001', 'hp', 'HP Inc.', 'Hewlett Packard printing and imaging solutions'),
    ('550e8400-e29b-41d4-a716-446655440002', 'konica_minolta', 'Konica Minolta', 'Konica Minolta business solutions and printing technology'),
    ('550e8400-e29b-41d4-a716-446655440003', 'lexmark', 'Lexmark International', 'Lexmark enterprise printing and imaging solutions'),
    ('550e8400-e29b-41d4-a716-446655440004', 'utax', 'UTAX Technologies', 'UTAX printing and document solutions')
ON CONFLICT (name) DO NOTHING;

-- Insert sample product series
INSERT INTO krai_core.product_series (id, manufacturer_id, name, display_name, category) VALUES 
    ('650e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'deskjet', 'DeskJet Series', 'inkjet'),
    ('650e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440002', 'bizhub_i', 'BizHub i-Series', 'laser'),
    ('650e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440003', 'cx_series', 'CX Series', 'laser')
ON CONFLICT (manufacturer_id, name) DO NOTHING;

-- Grant table permissions
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA krai_core TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA krai_content TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA krai_core TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA krai_content TO krai_service_role, krai_admin_role, krai_analyst_role, krai_technician_role;

-- Create functions
CREATE OR REPLACE FUNCTION krai_core.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Create triggers
CREATE TRIGGER update_manufacturers_updated_at BEFORE UPDATE ON krai_core.manufacturers FOR EACH ROW EXECUTE PROCEDURE krai_core.update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON krai_core.products FOR EACH ROW EXECUTE PROCEDURE krai_core.update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON krai_core.documents FOR EACH ROW EXECUTE PROCEDURE krai_core.update_updated_at_column();
CREATE TRIGGER update_chunks_updated_at BEFORE UPDATE ON krai_content.chunks FOR EACH ROW EXECUTE PROCEDURE krai_core.update_updated_at_column();

-- Success message
DO $$
BEGIN
    RAISE NOTICE 'KRAI Engine database schema initialized successfully!';
    RAISE NOTICE 'Available schemas: krai_core, krai_intelligence, krai_content, krai_config, krai_system';
    RAISE NOTICE 'Storage buckets created: krai-documents, krai-images';
    RAISE NOTICE 'Sample manufacturers and product series inserted.';
END
$$;
