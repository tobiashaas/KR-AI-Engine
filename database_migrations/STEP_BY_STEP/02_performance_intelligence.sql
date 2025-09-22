-- =====================================
-- KRAI ENGINE - STEP 02: PERFORMANCE & INTELLIGENCE TABLES
-- Embeddings + Error Codes + Images Tables
-- =====================================

-- =====================================
-- 1. EMBEDDINGS TABLE (Separated for Performance)
-- =====================================

CREATE TABLE IF NOT EXISTS public.embeddings (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Chunk Relationship
  chunk_id uuid NOT NULL REFERENCES public.chunks(id) ON DELETE CASCADE,
  
  -- Vector Data
  embedding vector(768),                        -- 768-dimensional vector
  model_name text NOT NULL,                     -- "all-MiniLM-L6-v2", "multilingual-e5-base"
  model_version text,                           -- "v1.0" for versioning
  
  -- Quality Metrics
  embedding_quality_score numeric,              -- Quality assessment
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(chunk_id, model_name)                  -- One embedding per chunk per model
);

-- =====================================
-- 2. ERROR CODES TABLE (Universal Intelligence)
-- =====================================

CREATE TABLE IF NOT EXISTS public.error_codes (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Source References
  manufacturer_id uuid NOT NULL REFERENCES public.manufacturers(id),
  document_id uuid NOT NULL REFERENCES public.documents(id),
  chunk_id uuid REFERENCES public.chunks(id),   -- Specific text location (optional)
  
  -- Error Code Information
  error_code text NOT NULL,                     -- "C1234", "E-5678", original format
  normalized_code text NOT NULL,                -- "c1234", "e5678" for fuzzy search
  error_description text NOT NULL,              -- "Paper jam in input tray"
  solution_steps text,                          -- Step-by-step solution
  
  -- Product Compatibility
  affected_product_ids uuid[],                  -- Array of compatible product IDs
  device_categories text[],                     -- ["printer", "mfp"] broader applicability
  
  -- Error Classification
  severity_level integer CHECK (severity_level BETWEEN 1 AND 5), -- 1=Critical, 5=Info
  frequency_score numeric DEFAULT 0.0,         -- How often this error occurs (0-10)
  
  -- Source Information
  source_system text CHECK (source_system IN (
    'cpmd_database',
    'service_manual', 
    'bulletin',
    'field_report',
    'video_content'
  )),
  
  -- Video Integration
  video_timestamp_seconds integer,              -- Position in related video
  related_video_id uuid,                        -- Associated video (will be added later)
  
  -- Cross-References
  alternative_codes text[],                     -- ["C1234", "Error 1234", "Jam-01"] cross-reference
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional troubleshooting data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(manufacturer_id, error_code)           -- One error code per manufacturer
);

-- =====================================
-- 3. IMAGES TABLE (Schematics & Diagrams)
-- =====================================

CREATE TABLE IF NOT EXISTS public.images (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Source References
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  chunk_id uuid REFERENCES public.chunks(id),   -- Associated text chunk (optional)
  
  -- File Information
  storage_path text NOT NULL,                   -- R2/S3 storage path
  storage_url text,                             -- Public access URL
  file_hash text NOT NULL,                      -- Deduplication hash
  original_filename text,                       -- "diagram_01.png"
  
  -- Image Properties
  width integer,                                -- Image width in pixels
  height integer,                               -- Image height in pixels
  file_size_bytes bigint,                       -- File size
  image_format text,                            -- "png", "jpg", "svg"
  
  -- Image Classification
  image_type text CHECK (image_type IN (
    'schematic',
    'diagram',
    'screenshot',
    'photo',
    'chart'
  )),
  
  -- Document Position
  page_number integer,                          -- Source page in document
  page_position text,                           -- "top", "bottom", "center"
  
  -- AI Analysis
  ai_description text,                          -- "Diagram showing paper path in printer"
  detected_objects jsonb,                       -- AI-detected objects and labels
  extracted_text text,                          -- OCR text from image
  related_part_numbers text[],                  -- ["CB435A", "CE285A"] if detected
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional image data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 4. INSTRUCTIONAL VIDEOS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS public.instructional_videos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Manufacturer & Product Relationships
  manufacturer_id uuid NOT NULL REFERENCES public.manufacturers(id),
  product_ids uuid[],                           -- Related products
  
  -- Video Information
  title text NOT NULL,                          -- "HP 9025 Toner Replacement"
  description text,                             -- Detailed video description
  video_url text NOT NULL,                      -- YouTube/Vimeo/Direct URL
  thumbnail_url text,                           -- Video thumbnail image
  duration_seconds integer,                     -- Video length
  language text DEFAULT 'en',                   -- Video language
  
  -- Video Classification
  video_type text CHECK (video_type IN (
    'repair',
    'maintenance', 
    'installation',
    'troubleshooting',
    'overview'
  )),
  
  -- Content References
  related_part_numbers text[],                  -- Parts shown in video
  related_error_codes text[],                   -- Error codes addressed
  
  -- Video Source
  is_official boolean DEFAULT true,             -- Official manufacturer video
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional video data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 5. INDEXES FOR PERFORMANCE & INTELLIGENCE TABLES
-- =====================================

-- Embeddings Indexes
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON public.embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON public.embeddings(model_name);
-- NOTE: HNSW Vector Index will be created after data ingestion:
-- CREATE INDEX embeddings_hnsw_idx ON public.embeddings USING hnsw (embedding vector_cosine_ops);

-- Error Codes Indexes
CREATE INDEX IF NOT EXISTS idx_error_codes_manufacturer ON public.error_codes(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_error_codes_normalized ON public.error_codes(normalized_code);
CREATE INDEX IF NOT EXISTS idx_error_codes_trigram ON public.error_codes USING gin(error_code gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_error_codes_affected_products_gin ON public.error_codes USING gin(affected_product_ids);
CREATE INDEX IF NOT EXISTS idx_error_codes_device_categories_gin ON public.error_codes USING gin(device_categories);
CREATE INDEX IF NOT EXISTS idx_error_codes_severity ON public.error_codes(severity_level);
CREATE INDEX IF NOT EXISTS idx_error_codes_content_fts ON public.error_codes USING gin(to_tsvector('english', error_description || ' ' || COALESCE(solution_steps, '')));
CREATE INDEX IF NOT EXISTS idx_error_codes_alternative_gin ON public.error_codes USING gin(alternative_codes);
CREATE INDEX IF NOT EXISTS idx_error_codes_source_system ON public.error_codes(manufacturer_id, source_system);

-- Images Indexes
CREATE INDEX IF NOT EXISTS idx_images_document_id ON public.images(document_id);
CREATE INDEX IF NOT EXISTS idx_images_chunk_id ON public.images(chunk_id) WHERE chunk_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_images_type ON public.images(image_type);
CREATE INDEX IF NOT EXISTS idx_images_file_hash ON public.images(file_hash);
CREATE INDEX IF NOT EXISTS idx_images_part_numbers_gin ON public.images USING gin(related_part_numbers);
CREATE INDEX IF NOT EXISTS idx_images_description_fts ON public.images USING gin(to_tsvector('english', COALESCE(ai_description, '')));
CREATE INDEX IF NOT EXISTS idx_images_detected_objects_gin ON public.images USING gin(detected_objects);

-- Instructional Videos Indexes
CREATE INDEX IF NOT EXISTS idx_videos_manufacturer_type ON public.instructional_videos(manufacturer_id, video_type);
CREATE INDEX IF NOT EXISTS idx_videos_product_ids_gin ON public.instructional_videos USING gin(product_ids);
CREATE INDEX IF NOT EXISTS idx_videos_part_numbers_gin ON public.instructional_videos USING gin(related_part_numbers);
CREATE INDEX IF NOT EXISTS idx_videos_error_codes_gin ON public.instructional_videos USING gin(related_error_codes);
CREATE INDEX IF NOT EXISTS idx_videos_title_search ON public.instructional_videos USING gin(title gin_trgm_ops);

-- =====================================
-- 6. UPDATE FOREIGN KEY REFERENCES
-- =====================================

-- Add video reference to documents (now that videos table exists)
ALTER TABLE public.documents ADD CONSTRAINT fk_documents_video 
  FOREIGN KEY (related_video_id) REFERENCES public.instructional_videos(id);

-- Add video reference to error_codes (now that videos table exists)  
ALTER TABLE public.error_codes ADD CONSTRAINT fk_error_codes_video
  FOREIGN KEY (related_video_id) REFERENCES public.instructional_videos(id);

-- =====================================
-- STEP 02 COMPLETE ✅
-- Next: Run Step 03 for Management & Relationship Tables
-- =====================================