-- =====================================
-- KRAI ENGINE - INTELLIGENCE SCHEMA
-- AI Processing: Chunks, Embeddings, Error Codes, Analytics
-- =====================================

-- =====================================
-- 1. CHUNKS TABLE (Text Content for AI Processing)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_intelligence.chunks (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Document Relationship
  document_id uuid NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
  
  -- Chunk Position & Structure
  chunk_index integer NOT NULL,                  -- Position in document (0, 1, 2...)
  page_start integer,                            -- Starting page number
  page_end integer,                              -- Ending page number
  
  -- Content
  text_chunk text NOT NULL,                      -- Extracted text content
  token_count integer,                           -- Token count for AI limits
  fingerprint text NOT NULL,                     -- Deduplication hash
  
  -- Document Structure
  section_title text,                            -- "Chapter 3: Troubleshooting"
  subsection_title text,                        -- "3.1 Paper Jams"
  page_label text,                               -- "Page 45", "Section 3.2.1"
  
  -- AI Extraction Results
  extracted_error_codes text[],                  -- ["C1234", "E-5678"] automatically detected
  normalized_error_codes text[],                 -- ["c1234", "e5678"] for fuzzy search
  extracted_part_numbers text[],                 -- ["CB435A", "CE285A"] automatically detected
  
  -- Quality Metrics
  ocr_confidence numeric,                        -- OCR quality (0.0-1.0)
  chunk_quality_score numeric,                   -- AI-assessed content quality
  
  -- Processing Status
  processing_status text CHECK (processing_status IN ('pending', 'completed', 'failed')),
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(document_id, chunk_index, fingerprint)  -- Prevent duplicate chunks
);

-- Indexes for chunks
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON krai_intelligence.chunks(document_id);
CREATE INDEX IF NOT EXISTS idx_chunks_document_index ON krai_intelligence.chunks(document_id, chunk_index);
CREATE INDEX IF NOT EXISTS idx_chunks_text_fts ON krai_intelligence.chunks USING GIN (to_tsvector('english', text_chunk));
CREATE INDEX IF NOT EXISTS idx_chunks_text_fts_german ON krai_intelligence.chunks USING GIN (to_tsvector('german', text_chunk));
CREATE INDEX IF NOT EXISTS idx_chunks_text_trigram ON krai_intelligence.chunks USING GIN (text_chunk gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_chunks_error_codes_gin ON krai_intelligence.chunks USING GIN (extracted_error_codes);
CREATE INDEX IF NOT EXISTS idx_chunks_normalized_codes_gin ON krai_intelligence.chunks USING GIN (normalized_error_codes);
CREATE INDEX IF NOT EXISTS idx_chunks_part_numbers_gin ON krai_intelligence.chunks USING GIN (extracted_part_numbers);
CREATE INDEX IF NOT EXISTS idx_chunks_processing_status ON krai_intelligence.chunks(processing_status);
CREATE INDEX IF NOT EXISTS idx_chunks_quality ON krai_intelligence.chunks(chunk_quality_score) WHERE chunk_quality_score IS NOT NULL;

COMMENT ON TABLE krai_intelligence.chunks IS 'Text chunks extracted from documents for AI processing';
COMMENT ON COLUMN krai_intelligence.chunks.fingerprint IS 'Hash for deduplication and change detection';

-- =====================================
-- 2. EMBEDDINGS TABLE (Vector Embeddings)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_intelligence.embeddings (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Chunk Relationship
  chunk_id uuid NOT NULL REFERENCES krai_intelligence.chunks(id) ON DELETE CASCADE,
  
  -- Vector Data
  embedding vector(768),                         -- 768-dimensional vector
  model_name text NOT NULL,                      -- "all-MiniLM-L6-v2", "multilingual-e5-base"
  model_version text,                            -- "v1.0" for versioning
  
  -- Quality Metrics
  embedding_quality_score numeric,               -- Quality assessment
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(chunk_id, model_name)                   -- One embedding per chunk per model
);

-- Indexes for embeddings
CREATE INDEX IF NOT EXISTS idx_embeddings_chunk_id ON krai_intelligence.embeddings(chunk_id);
CREATE INDEX IF NOT EXISTS idx_embeddings_model ON krai_intelligence.embeddings(model_name);

-- HNSW Vector Index (create after data ingestion)
-- CREATE INDEX CONCURRENTLY idx_embeddings_hnsw ON krai_intelligence.embeddings USING hnsw (embedding vector_cosine_ops);

COMMENT ON TABLE krai_intelligence.embeddings IS 'Vector embeddings for semantic search and AI processing';
COMMENT ON COLUMN krai_intelligence.embeddings.embedding IS '768-dimensional vector representation of text chunk';

-- =====================================
-- 3. ERROR CODES TABLE (Universal Intelligence)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_intelligence.error_codes (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Source References
  manufacturer_id uuid NOT NULL REFERENCES krai_core.manufacturers(id),
  document_id uuid NOT NULL REFERENCES krai_core.documents(id),
  chunk_id uuid REFERENCES krai_intelligence.chunks(id),  -- Specific text location (optional)
  
  -- Error Code Information
  error_code text NOT NULL,                      -- "C1234", "E-5678", original format
  normalized_code text NOT NULL,                 -- "c1234", "e5678" for fuzzy search
  error_description text NOT NULL,               -- "Paper jam in input tray"
  solution_steps text,                           -- Step-by-step solution
  
  -- Product Compatibility
  affected_product_ids uuid[],                   -- Array of compatible product IDs
  device_categories text[],                      -- ["printer", "mfp"] broader applicability
  
  -- Error Classification
  severity_level integer CHECK (severity_level BETWEEN 1 AND 5), -- 1=Critical, 5=Info
  frequency_score numeric DEFAULT 0.0,          -- How often this error occurs (0-10)
  
  -- Source Information
  source_system text CHECK (source_system IN (
    'cpmd_database',
    'service_manual', 
    'bulletin',
    'field_report',
    'video_content'
  )),
  
  -- Video Integration
  video_timestamp_seconds integer,               -- Position in related video
  related_video_id uuid,                         -- Associated video (FK to krai_content.instructional_videos)
  
  -- Cross-References
  alternative_codes text[],                      -- ["C1234", "Error 1234", "Jam-01"] cross-reference
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,            -- Additional troubleshooting data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(manufacturer_id, error_code)            -- One error code per manufacturer
);

-- Indexes for error codes
CREATE INDEX IF NOT EXISTS idx_error_codes_manufacturer ON krai_intelligence.error_codes(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_error_codes_normalized ON krai_intelligence.error_codes(normalized_code);
CREATE INDEX IF NOT EXISTS idx_error_codes_trigram ON krai_intelligence.error_codes USING GIN (error_code gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_error_codes_affected_products_gin ON krai_intelligence.error_codes USING GIN (affected_product_ids);
CREATE INDEX IF NOT EXISTS idx_error_codes_device_categories_gin ON krai_intelligence.error_codes USING GIN (device_categories);
CREATE INDEX IF NOT EXISTS idx_error_codes_severity ON krai_intelligence.error_codes(severity_level);
CREATE INDEX IF NOT EXISTS idx_error_codes_content_fts ON krai_intelligence.error_codes USING GIN (to_tsvector('english', error_description || ' ' || COALESCE(solution_steps, '')));
CREATE INDEX IF NOT EXISTS idx_error_codes_alternative_gin ON krai_intelligence.error_codes USING GIN (alternative_codes);
CREATE INDEX IF NOT EXISTS idx_error_codes_source_system ON krai_intelligence.error_codes(manufacturer_id, source_system);
CREATE INDEX IF NOT EXISTS idx_error_codes_video_relation ON krai_intelligence.error_codes(related_video_id) WHERE related_video_id IS NOT NULL;

COMMENT ON TABLE krai_intelligence.error_codes IS 'Universal error code database with solutions and cross-references';
COMMENT ON COLUMN krai_intelligence.error_codes.severity_level IS '1=Critical, 2=High, 3=Medium, 4=Low, 5=Info';

-- =====================================
-- 4. SEARCH ANALYTICS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_intelligence.search_analytics (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Session Information
  session_id text,                               -- Frontend session identifier
  user_id uuid,                                  -- Supabase user ID (optional)
  
  -- Search Query
  query_text text NOT NULL,                      -- User search query
  query_intent text,                             -- "error_lookup", "part_search", "manual_search"
  search_type text CHECK (search_type IN ('semantic', 'exact', 'fuzzy', 'comprehensive')),
  
  -- Applied Filters
  manufacturer_filter uuid REFERENCES krai_core.manufacturers(id),
  product_filter uuid REFERENCES krai_core.products(id),
  document_type_filter text,
  
  -- Results & Performance
  results_count integer,                         -- Number of results returned
  top_result_similarity numeric,                 -- Best match similarity score
  response_time_ms integer,                      -- Performance metric
  
  -- User Engagement
  user_clicked_result boolean DEFAULT false,     -- User engagement
  clicked_result_rank integer,                   -- Position of clicked result
  user_feedback_rating integer CHECK (user_feedback_rating BETWEEN 1 AND 5),
  was_helpful boolean,                           -- Overall helpfulness
  
  -- Timestamps
  search_timestamp timestamp with time zone DEFAULT now()
);

-- Indexes for search analytics
CREATE INDEX IF NOT EXISTS idx_search_analytics_timestamp ON krai_intelligence.search_analytics(search_timestamp);
CREATE INDEX IF NOT EXISTS idx_search_analytics_session ON krai_intelligence.search_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_search_analytics_performance ON krai_intelligence.search_analytics(search_type, response_time_ms);
CREATE INDEX IF NOT EXISTS idx_search_analytics_successful ON krai_intelligence.search_analytics(was_helpful) WHERE was_helpful = true;
CREATE INDEX IF NOT EXISTS idx_search_analytics_query_fts ON krai_intelligence.search_analytics USING GIN (to_tsvector('english', query_text));

COMMENT ON TABLE krai_intelligence.search_analytics IS 'Search performance tracking and user behavior analytics';
COMMENT ON COLUMN krai_intelligence.search_analytics.search_type IS 'Type of search performed: semantic, exact, fuzzy, comprehensive';

-- =====================================
-- 5. TRIGGERS FOR UPDATED_AT
-- =====================================

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_chunks_updated_at BEFORE UPDATE ON krai_intelligence.chunks FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_error_codes_updated_at BEFORE UPDATE ON krai_intelligence.error_codes FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();

-- =====================================
-- 6. UTILITY FUNCTIONS
-- =====================================

-- Function: Normalize error codes for fuzzy search
CREATE OR REPLACE FUNCTION krai_intelligence.normalize_error_code(input_code text)
RETURNS text AS $$
BEGIN
  IF input_code IS NULL THEN
    RETURN NULL;
  END IF;
  
  -- Convert to lowercase, remove spaces, hyphens, and common prefixes
  RETURN LOWER(
    REGEXP_REPLACE(
      REGEXP_REPLACE(input_code, '^(error|err|code|c|e)[-\s]*', '', 'i'),
      '[^a-z0-9]', '', 'g'
    )
  );
END;
$$ LANGUAGE plpgsql IMMUTABLE;

-- Function: Comprehensive search for AI agents
CREATE OR REPLACE FUNCTION krai_intelligence.comprehensive_search(
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
  RETURN QUERY
  WITH search_results AS (
    -- Search in chunks with full-text and trigram
    SELECT 
      'chunk' as result_type,
      c.id as result_id,
      d.file_name as title,
      c.text_chunk as content,
      GREATEST(
        ts_rank(to_tsvector('english', c.text_chunk), plainto_tsquery('english', search_query)),
        similarity(c.text_chunk, search_query)
      ) as similarity_score,
      jsonb_build_object(
        'document_id', c.document_id,
        'chunk_index', c.chunk_index,
        'page_start', c.page_start,
        'page_end', c.page_end,
        'section_title', c.section_title,
        'error_codes', c.extracted_error_codes,
        'part_numbers', c.extracted_part_numbers
      ) as metadata
    FROM krai_intelligence.chunks c
    JOIN krai_core.documents d ON d.id = c.document_id
    WHERE 
      (manufacturer_filter IS NULL OR d.manufacturer_id = manufacturer_filter)
      AND (product_filter IS NULL OR product_filter = ANY(d.product_ids))
      AND (document_type_filter IS NULL OR d.document_type = document_type_filter)
      AND d.processing_status = 'completed'
      AND c.processing_status = 'completed'
      AND (
        to_tsvector('english', c.text_chunk) @@ plainto_tsquery('english', search_query)
        OR c.text_chunk % search_query
        OR search_query = ANY(c.extracted_error_codes)
        OR krai_intelligence.normalize_error_code(search_query) = ANY(c.normalized_error_codes)
        OR search_query = ANY(c.extracted_part_numbers)
      )
    
    UNION ALL
    
    -- Search in error codes
    SELECT 
      'error_code' as result_type,
      e.id as result_id,
      e.error_code as title,
      e.error_description || COALESCE(' Solution: ' || e.solution_steps, '') as content,
      GREATEST(
        ts_rank(to_tsvector('english', e.error_description || ' ' || COALESCE(e.solution_steps, '')), plainto_tsquery('english', search_query)),
        similarity(e.error_code, search_query),
        CASE WHEN krai_intelligence.normalize_error_code(search_query) = e.normalized_code THEN 1.0 ELSE 0.0 END
      ) as similarity_score,
      jsonb_build_object(
        'manufacturer_id', e.manufacturer_id,
        'document_id', e.document_id,
        'severity_level', e.severity_level,
        'affected_products', e.affected_product_ids,
        'device_categories', e.device_categories,
        'alternative_codes', e.alternative_codes
      ) as metadata
    FROM krai_intelligence.error_codes e
    WHERE 
      (manufacturer_filter IS NULL OR e.manufacturer_id = manufacturer_filter)
      AND (
        to_tsvector('english', e.error_description || ' ' || COALESCE(e.solution_steps, '')) @@ plainto_tsquery('english', search_query)
        OR e.error_code % search_query
        OR krai_intelligence.normalize_error_code(search_query) = e.normalized_code
        OR search_query = ANY(e.alternative_codes)
      )
  )
  SELECT * FROM search_results
  ORDER BY similarity_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

COMMENT ON SCHEMA krai_intelligence IS 'AI processing, embeddings, error codes, and search analytics';
