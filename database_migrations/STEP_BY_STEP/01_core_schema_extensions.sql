-- =====================================
-- KRAI ENGINE - STEP 01: CORE SCHEMA & EXTENSIONS
-- Fresh Database Setup - Extensions + Core Tables
-- =====================================

-- =====================================
-- 1. ENABLE REQUIRED EXTENSIONS
-- =====================================

-- Vector similarity search (pgvector)
CREATE EXTENSION IF NOT EXISTS vector;

-- UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Full text search improvements
CREATE EXTENSION IF NOT EXISTS pg_trgm;

-- Additional text search functions
CREATE EXTENSION IF NOT EXISTS unaccent;

-- =====================================
-- 2. CORE TABLE: MANUFACTURERS
-- =====================================

CREATE TABLE IF NOT EXISTS public.manufacturers (
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

-- =====================================
-- 3. CORE TABLE: PRODUCTS (3-Level Hierarchy)
-- =====================================

CREATE TABLE IF NOT EXISTS public.products (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Hierarchy & Relationships
  manufacturer_id uuid NOT NULL REFERENCES public.manufacturers(id),
  product_type text NOT NULL CHECK (product_type IN ('series', 'model', 'option')),
  parent_id uuid REFERENCES public.products(id),  -- NULL for series, points to parent for models/options
  
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

-- =====================================
-- 4. CORE TABLE: DOCUMENTS
-- =====================================

CREATE TABLE IF NOT EXISTS public.documents (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- File Information
  file_name text NOT NULL,                      -- "HP_9025_Service_Manual.pdf"
  file_hash text NOT NULL UNIQUE,               -- SHA256 hash for deduplication
  storage_path text NOT NULL,                   -- R2/S3 storage path
  storage_url text,                             -- Public access URL
  size_bytes bigint,                            -- File size
  total_pages integer,                          -- Page count (NULL for non-PDF)
  
  -- Document Classification
  document_type text NOT NULL CHECK (document_type IN (
    'service_manual',
    'parts_catalog', 
    'bulletins',
    'cpmd_database',
    'video_transcript'
  )),
  
  -- Relationships
  manufacturer_id uuid NOT NULL REFERENCES public.manufacturers(id),
  product_ids uuid[],                           -- Array of related product IDs
  
  -- Localization
  language text DEFAULT 'en',                   -- Document language
  translation_group_id uuid,                    -- Group ID for same doc in different languages
  
  -- Review & Maintenance
  upload_date timestamp with time zone DEFAULT now(),
  last_reviewed_date timestamp with time zone,
  needs_review boolean DEFAULT false,
  review_frequency_months integer DEFAULT 12,
  
  -- Processing Status
  processing_status text DEFAULT 'pending' CHECK (processing_status IN ('pending', 'processing', 'completed', 'failed')),
  processing_progress integer CHECK (processing_progress >= 0 AND processing_progress <= 100),
  
  -- Source Information
  source_system text,                           -- 'cpmd_database', 'service_manual', etc.
  cpmd_version text,                            -- HP CPMD version number
  related_video_id uuid,                        -- Associated video (will be added later)
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Document-specific metadata
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 5. CORE TABLE: CHUNKS (Text Content for AI)
-- =====================================

CREATE TABLE IF NOT EXISTS public.chunks (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Document Relationship
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  
  -- Chunk Position & Structure
  chunk_index integer NOT NULL,                 -- Position in document (0, 1, 2...)
  page_start integer,                           -- Starting page number
  page_end integer,                             -- Ending page number
  
  -- Content
  text_chunk text NOT NULL,                     -- Extracted text content
  token_count integer,                          -- Token count for AI limits
  fingerprint text NOT NULL,                    -- Deduplication hash
  
  -- Structure Information
  section_title text,                           -- "Chapter 3: Troubleshooting"
  subsection_title text,                        -- "3.1 Paper Jams"
  page_label text,                              -- "Page 45", "Section 3.2.1"
  
  -- Extracted Information
  extracted_error_codes text[],                 -- ["C1234", "E-5678"] automatically detected
  normalized_error_codes text[],                -- ["c1234", "e5678"] for fuzzy search
  extracted_part_numbers text[],                -- ["CB435A", "CE285A"] automatically detected
  
  -- Quality Metrics
  ocr_confidence numeric,                       -- OCR quality (0.0-1.0)
  chunk_quality_score numeric,                  -- AI-assessed content quality
  
  -- Processing Status
  processing_status text DEFAULT 'pending' CHECK (processing_status IN ('pending', 'completed', 'failed')),
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(document_id, chunk_index, fingerprint) -- Prevent duplicate chunks
);

-- =====================================
-- 6. BASIC INDEXES FOR CORE TABLES
-- =====================================

-- Manufacturers Indexes
CREATE INDEX IF NOT EXISTS idx_manufacturers_name ON public.manufacturers(name);
CREATE INDEX IF NOT EXISTS idx_manufacturers_competitor ON public.manufacturers(is_competitor) WHERE is_competitor = true;
CREATE INDEX IF NOT EXISTS idx_manufacturers_metadata_gin ON public.manufacturers USING gin(metadata);

-- Products Indexes  
CREATE INDEX IF NOT EXISTS idx_products_manufacturer_type ON public.products(manufacturer_id, product_type);
CREATE INDEX IF NOT EXISTS idx_products_3level_hierarchy ON public.products(manufacturer_id, product_type, parent_id);
CREATE INDEX IF NOT EXISTS idx_products_model_number ON public.products(model_number) WHERE model_number IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_name_search ON public.products USING gin(name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_products_specs_gin ON public.products USING gin(technical_specs);
CREATE INDEX IF NOT EXISTS idx_products_device_category_gin ON public.products USING gin(device_category);
CREATE INDEX IF NOT EXISTS idx_products_option_category ON public.products(option_category) WHERE option_category IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_products_active ON public.products(is_active) WHERE is_active = true;
CREATE INDEX IF NOT EXISTS idx_products_option_dependencies_gin ON public.products USING gin(option_dependencies);

-- Documents Indexes
CREATE INDEX IF NOT EXISTS idx_documents_file_hash ON public.documents(file_hash);
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer_type ON public.documents(manufacturer_id, document_type);
CREATE INDEX IF NOT EXISTS idx_documents_product_ids_gin ON public.documents USING gin(product_ids);
CREATE INDEX IF NOT EXISTS idx_documents_processing_status ON public.documents(processing_status);
CREATE INDEX IF NOT EXISTS idx_documents_language_type ON public.documents(language, document_type);
CREATE INDEX IF NOT EXISTS idx_documents_review_needed ON public.documents(needs_review) WHERE needs_review = true;
CREATE INDEX IF NOT EXISTS idx_documents_filename_search ON public.documents USING gin(file_name gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_documents_metadata_gin ON public.documents USING gin(metadata);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON public.documents(upload_date);
CREATE INDEX IF NOT EXISTS idx_documents_cpmd ON public.documents(manufacturer_id, document_type) WHERE document_type = 'cpmd_database';
CREATE INDEX IF NOT EXISTS idx_documents_source_system ON public.documents(source_system) WHERE source_system IS NOT NULL;

-- Chunks Indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON public.chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_index ON public.chunks(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_chunks_text_fts ON public.chunks USING gin(to_tsvector('english', text_chunk));
CREATE INDEX IF NOT EXISTS idx_chunks_text_fts_german ON public.chunks USING gin(to_tsvector('german', text_chunk));
CREATE INDEX IF NOT EXISTS idx_chunks_text_trigram ON public.chunks USING gin(text_chunk gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_chunks_error_codes_gin ON public.chunks USING gin(extracted_error_codes);
CREATE INDEX IF NOT EXISTS idx_chunks_normalized_codes_gin ON public.chunks USING gin(normalized_error_codes);
CREATE INDEX IF NOT EXISTS idx_chunks_part_numbers_gin ON public.chunks USING gin(extracted_part_numbers);
CREATE INDEX IF NOT EXISTS idx_chunks_processing_status ON public.chunks(processing_status);
CREATE INDEX IF NOT EXISTS idx_chunks_quality ON public.chunks(chunk_quality_score) WHERE chunk_quality_score IS NOT NULL;

-- =====================================
-- STEP 01 COMPLETE ✅
-- Next: Run Step 02 for Performance & Intelligence Tables
-- =====================================