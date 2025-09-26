-- =====================================
-- KRAI ENGINE - CORE BUSINESS SCHEMA
-- Manufacturers, Products, Documents, Relationships
-- =====================================

-- =====================================
-- 1. MANUFACTURERS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_core.manufacturers (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Basic Information
  name text NOT NULL UNIQUE,                    -- "HP Inc.", "Canon Inc."
  display_name text,                            -- "Hewlett Packard", "Canon"
  website text,                                 -- Official website URL
  support_url text,                             -- Support/service URL
  
  -- Business Classification
  is_competitor boolean DEFAULT false,          -- TRUE for competitive analysis
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional manufacturer data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for manufacturers
CREATE INDEX IF NOT EXISTS idx_manufacturers_name ON krai_core.manufacturers(name);
CREATE INDEX IF NOT EXISTS idx_manufacturers_competitor ON krai_core.manufacturers(is_competitor) WHERE is_competitor = true;
CREATE INDEX IF NOT EXISTS idx_manufacturers_metadata_gin ON krai_core.manufacturers USING GIN (metadata);

COMMENT ON TABLE krai_core.manufacturers IS 'Manufacturer information and competitive analysis data';
COMMENT ON COLUMN krai_core.manufacturers.is_competitor IS 'Mark competitors for competitive analysis features';

-- =====================================
-- 2. PRODUCTS TABLE (3-Level Hierarchy)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_core.products (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Hierarchy & Relationships
  manufacturer_id uuid NOT NULL REFERENCES krai_core.manufacturers(id),
  product_type text NOT NULL CHECK (product_type IN ('series', 'model', 'option')),
  parent_id uuid REFERENCES krai_core.products(id),  -- NULL for series, points to parent for models/options
  
  -- Product Identity
  name text NOT NULL,                           -- "OfficeJet Pro", "9025", "Large Tray"
  display_name text,                            -- "HP OfficeJet Pro 9025"
  model_number text,                            -- "HP-OJP-9025" unique identifier
  
  -- Product Lifecycle
  year_introduced integer,                      -- Product launch year
  year_discontinued integer,                    -- End of life year
  is_active boolean DEFAULT true,               -- Currently available
  
  -- Option-Specific Fields
  option_category text,                         -- For options: 'tray', 'fax', 'scanner', 'finisher'
  compatibility_notes text,                     -- Installation/compatibility notes
  installation_complexity text CHECK (installation_complexity IN ('simple', 'standard', 'complex', 'professional')),
  option_dependencies uuid[],                   -- Required options for this option
  
  -- Product Classification
  device_category text[],                       -- ["printer", "scanner", "fax"] capabilities
  form_factor text,                             -- "desktop", "workgroup", "production"
  
  -- Flexible Data
  technical_specs jsonb DEFAULT '{}'::jsonb,    -- Technical specifications
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional product data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(manufacturer_id, product_type, name)   -- No duplicate product names per type
);

-- Indexes for products
CREATE INDEX IF NOT EXISTS idx_products_manufacturer_type ON krai_core.products(manufacturer_id, product_type);
CREATE INDEX IF NOT EXISTS idx_products_3level_hierarchy ON krai_core.products(manufacturer_id, product_type, parent_id);
CREATE INDEX IF NOT EXISTS idx_products_model_number ON krai_core.products(model_number) WHERE model_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_name_search ON krai_core.products USING GIN (name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_specs_gin ON krai_core.products USING GIN (technical_specs);
CREATE INDEX IF NOT EXISTS idx_products_device_category_gin ON krai_core.products USING GIN (device_category);
CREATE INDEX IF NOT EXISTS idx_products_option_category ON krai_core.products(option_category) WHERE option_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_active ON krai_core.products(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_option_dependencies_gin ON krai_core.products USING GIN (option_dependencies);

COMMENT ON TABLE krai_core.products IS '3-level product hierarchy: Series → Model → Options';
COMMENT ON COLUMN krai_core.products.product_type IS 'series, model, or option';
COMMENT ON COLUMN krai_core.products.parent_id IS 'Hierarchy parent: NULL for series, series for models, model for options';

-- =====================================
-- 3. DOCUMENTS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_core.documents (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- File Information
  file_name text NOT NULL,                      -- "HP_9025_Service_Manual.pdf"
  file_hash text NOT NULL UNIQUE,               -- SHA256 hash for deduplication
  storage_path text NOT NULL,                   -- R2/S3 storage path
  storage_url text,                             -- Public access URL
  size_bytes bigint,                            -- File size
  total_pages integer,                          -- Page count (NULL for non-PDF)
  
  -- Document Classification
  document_type text CHECK (document_type IN (
    'service_manual',
    'parts_catalog', 
    'bulletins',
    'cpmd_database',
    'video_transcript'
  )),
  
  -- Ownership & Relationships
  manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  product_ids uuid[],                           -- Array of related product IDs
  
  -- Language & Translation
  language text DEFAULT 'en',                   -- Document language
  translation_group_id uuid,                    -- Group ID for same doc in different languages
  
  -- Processing & Review
  upload_date timestamp with time zone DEFAULT now(),
  last_reviewed_date timestamp with time zone,
  needs_review boolean DEFAULT false,           -- Requires manual review
  review_frequency_months integer DEFAULT 12,   -- Review cycle
  processing_status text CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_progress integer CHECK (processing_progress BETWEEN 0 AND 100),
  
  -- Source Information
  source_system text,                           -- 'cpmd_database', 'service_manual', etc.
  cpmd_version text,                            -- HP CPMD version number
  related_video_id uuid,                        -- Associated video (FK to krai_content.instructional_videos)
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Document-specific metadata
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for documents
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON krai_core.documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer_type ON krai_core.documents(manufacturer_id, document_type);
CREATE INDEX IF NOT EXISTS idx_documents_product_ids_gin ON krai_core.documents USING GIN (product_ids);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON krai_core.documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_language_type ON krai_core.documents(language, document_type);
CREATE INDEX IF NOT EXISTS idx_documents_review_needed ON krai_core.documents(needs_review) WHERE needs_review = true;
CREATE INDEX IF NOT EXISTS idx_documents_filename_search ON krai_core.documents USING GIN (file_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin ON krai_core.documents USING GIN (metadata);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON krai_core.documents(upload_date);
CREATE INDEX IF NOT EXISTS idx_documents_cpmd ON krai_core.documents(manufacturer_id, document_type) WHERE document_type = 'cpmd_database';
CREATE INDEX IF NOT EXISTS idx_documents_source_system ON krai_core.documents(source_system) WHERE source_system IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_documents_video_relation ON krai_core.documents(related_video_id) WHERE related_video_id IS NOT NULL;

COMMENT ON TABLE krai_core.documents IS 'Document metadata and processing information';
COMMENT ON COLUMN krai_core.documents.document_type IS 'Type of document: service_manual, parts_catalog, bulletins, cpmd_database, video_transcript';

-- =====================================
-- 4. DOCUMENT RELATIONSHIPS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_core.document_relationships (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Relationship Definition
  primary_document_id uuid NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
  secondary_document_id uuid NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
  
  -- Relationship Type
  relationship_type text CHECK (relationship_type IN (
    'cpmd_manual_pair',     -- CPMD database + Service manual pairing
    'supersedes',           -- New version supersedes old
    'supplements',          -- Additional information
    'translation',          -- Same document in different language
    'series_manual'         -- Manual applies to entire series
  )),
  
  -- Relationship Details
  description text,                             -- Relationship description
  priority_order integer DEFAULT 1,            -- Display priority
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  CHECK(primary_document_id != secondary_document_id),  -- No self-references
  UNIQUE(primary_document_id, secondary_document_id, relationship_type)  -- No duplicates
);

-- Indexes for document relationships
CREATE INDEX IF NOT EXISTS idx_doc_relationships_primary ON krai_core.document_relationships(primary_document_id);
CREATE INDEX IF NOT EXISTS idx_doc_relationships_secondary ON krai_core.document_relationships(secondary_document_id);
CREATE INDEX IF NOT EXISTS idx_doc_relationships_type ON krai_core.document_relationships(relationship_type);

COMMENT ON TABLE krai_core.document_relationships IS 'Intelligent document pairing and cross-references';
COMMENT ON COLUMN krai_core.document_relationships.relationship_type IS 'Type of relationship between documents';

-- =====================================
-- 5. TRIGGERS FOR UPDATED_AT
-- =====================================

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION krai_core.update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = now();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply triggers to all tables with updated_at
CREATE TRIGGER update_manufacturers_updated_at BEFORE UPDATE ON krai_core.manufacturers FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_products_updated_at BEFORE UPDATE ON krai_core.products FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_documents_updated_at BEFORE UPDATE ON krai_core.documents FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();

-- =====================================
-- 6. SAMPLE DATA FOR TESTING
-- =====================================

-- Insert sample manufacturers
INSERT INTO krai_core.manufacturers (id, name, display_name, website, support_url, is_competitor) VALUES
('550e8400-e29b-41d4-a716-446655440001', 'HP Inc.', 'Hewlett Packard', 'https://www.hp.com', 'https://support.hp.com', false),
('550e8400-e29b-41d4-a716-446655440002', 'Canon Inc.', 'Canon', 'https://www.canon.com', 'https://support.canon.com', true),
('550e8400-e29b-41d4-a716-446655440003', 'Epson', 'Epson', 'https://www.epson.com', 'https://support.epson.com', true),
('550e8400-e29b-41d4-a716-446655440004', 'Brother', 'Brother', 'https://www.brother.com', 'https://support.brother.com', true)
ON CONFLICT (name) DO NOTHING;

-- Insert sample products (HP 9025 series hierarchy)
INSERT INTO krai_core.products (id, manufacturer_id, product_type, parent_id, name, display_name, model_number, year_introduced, is_active, device_category, form_factor) VALUES
-- Series
('660e8400-e29b-41d4-a716-446655440001', '550e8400-e29b-41d4-a716-446655440001', 'series', NULL, 'OfficeJet Pro', 'HP OfficeJet Pro Series', NULL, 2020, true, ARRAY['printer', 'scanner'], 'workgroup'),
-- Model
('660e8400-e29b-41d4-a716-446655440002', '550e8400-e29b-41d4-a716-446655440001', 'model', '660e8400-e29b-41d4-a716-446655440001', '9025', 'HP OfficeJet Pro 9025', 'HP-OJP-9025', 2020, true, ARRAY['printer', 'scanner', 'fax'], 'workgroup'),
-- Options
('660e8400-e29b-41d4-a716-446655440003', '550e8400-e29b-41d4-a716-446655440001', 'option', '660e8400-e29b-41d4-a716-446655440002', 'Bridge A', 'HP Bridge A', 'HP-BA-9025', 2020, true, ARRAY['bridge'], 'accessory'),
('660e8400-e29b-41d4-a716-446655440004', '550e8400-e29b-41d4-a716-446655440001', 'option', '660e8400-e29b-41d4-a716-446655440002', 'Bridge B', 'HP Bridge B', 'HP-BB-9025', 2020, true, ARRAY['bridge'], 'accessory'),
('660e8400-e29b-41d4-a716-446655440005', '550e8400-e29b-41d4-a716-446655440001', 'option', '660e8400-e29b-41d4-a716-446655440002', 'Finisher X', 'HP Finisher X', 'HP-FX-9025', 2020, true, ARRAY['finisher'], 'accessory'),
('660e8400-e29b-41d4-a716-446655440006', '550e8400-e29b-41d4-a716-446655440001', 'option', '660e8400-e29b-41d4-a716-446655440002', 'Finisher Y', 'HP Finisher Y', 'HP-FY-9025', 2020, true, ARRAY['finisher'], 'accessory')
ON CONFLICT (manufacturer_id, product_type, name) DO NOTHING;

COMMENT ON SCHEMA krai_core IS 'Core business entities and relationships';
