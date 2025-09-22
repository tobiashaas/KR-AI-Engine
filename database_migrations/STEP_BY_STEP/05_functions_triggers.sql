-- =====================================
-- KRAI ENGINE - STEP 05: CORE FUNCTIONS & TRIGGERS
-- Search Functions + Validation Functions + Normalization Triggers
-- =====================================

-- =====================================
-- 1. UTILITY FUNCTIONS
-- =====================================

-- Function: Normalize error codes for fuzzy search
CREATE OR REPLACE FUNCTION normalize_error_code(input_code text)
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

-- Function: Check user permissions
CREATE OR REPLACE FUNCTION check_user_permissions()
RETURNS text AS $$
BEGIN
  -- Service role has full access
  IF current_setting('role') = 'service_role' THEN
    RETURN 'service_role';
  END IF;
  
  -- Authenticated users have read/write access
  IF auth.uid() IS NOT NULL THEN
    RETURN 'authenticated';
  END IF;
  
  -- Anonymous users have limited read access
  RETURN 'anonymous';
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- 2. SEARCH FUNCTIONS
-- =====================================

-- Function: Comprehensive search for AI agents
CREATE OR REPLACE FUNCTION comprehensive_search(
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
    FROM public.chunks c
    JOIN public.documents d ON d.id = c.document_id
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
        OR normalize_error_code(search_query) = ANY(c.normalized_error_codes)
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
        CASE WHEN normalize_error_code(search_query) = e.normalized_code THEN 1.0 ELSE 0.0 END
      ) as similarity_score,
      jsonb_build_object(
        'manufacturer_id', e.manufacturer_id,
        'document_id', e.document_id,
        'severity_level', e.severity_level,
        'affected_products', e.affected_product_ids,
        'device_categories', e.device_categories,
        'alternative_codes', e.alternative_codes
      ) as metadata
    FROM public.error_codes e
    WHERE 
      (manufacturer_filter IS NULL OR e.manufacturer_id = manufacturer_filter)
      AND (
        to_tsvector('english', e.error_description || ' ' || COALESCE(e.solution_steps, '')) @@ plainto_tsquery('english', search_query)
        OR e.error_code % search_query
        OR normalize_error_code(search_query) = e.normalized_code
        OR search_query = ANY(e.alternative_codes)
      )
    
    UNION ALL
    
    -- Search in documents
    SELECT 
      'document' as result_type,
      d.id as result_id,
      d.file_name as title,
      COALESCE(d.metadata->>'description', 'Document: ' || d.document_type) as content,
      similarity(d.file_name, search_query) as similarity_score,
      jsonb_build_object(
        'manufacturer_id', d.manufacturer_id,
        'document_type', d.document_type,
        'language', d.language,
        'total_pages', d.total_pages,
        'product_ids', d.product_ids,
        'upload_date', d.upload_date
      ) as metadata
    FROM public.documents d
    WHERE 
      (manufacturer_filter IS NULL OR d.manufacturer_id = manufacturer_filter)
      AND (product_filter IS NULL OR product_filter = ANY(d.product_ids))
      AND (document_type_filter IS NULL OR d.document_type = document_type_filter)
      AND d.processing_status = 'completed'
      AND d.file_name % search_query
  )
  SELECT 
    sr.result_type,
    sr.result_id,
    sr.title,
    sr.content,
    sr.similarity_score,
    sr.metadata
  FROM search_results sr
  WHERE sr.similarity_score > 0.1
  ORDER BY sr.similarity_score DESC
  LIMIT max_results;
END;
$$ LANGUAGE plpgsql;

-- Function: Search error codes with fuzzy matching
CREATE OR REPLACE FUNCTION search_error_codes_fuzzy(
  error_code_input text,
  manufacturer_filter uuid DEFAULT NULL
)
RETURNS TABLE (
  error_id uuid,
  error_code text,
  normalized_code text,
  error_description text,
  solution_steps text,
  similarity_score numeric,
  manufacturer_name text,
  affected_products jsonb
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    e.id as error_id,
    e.error_code,
    e.normalized_code,
    e.error_description,
    e.solution_steps,
    GREATEST(
      similarity(e.error_code, error_code_input),
      similarity(e.normalized_code, normalize_error_code(error_code_input)),
      CASE WHEN normalize_error_code(error_code_input) = e.normalized_code THEN 1.0 ELSE 0.0 END,
      CASE WHEN error_code_input = ANY(e.alternative_codes) THEN 0.9 ELSE 0.0 END
    ) as similarity_score,
    m.name as manufacturer_name,
    (
      SELECT jsonb_agg(jsonb_build_object('id', p.id, 'name', p.name, 'display_name', p.display_name))
      FROM public.products p 
      WHERE p.id = ANY(e.affected_product_ids)
    ) as affected_products
  FROM public.error_codes e
  JOIN public.manufacturers m ON m.id = e.manufacturer_id
  WHERE 
    (manufacturer_filter IS NULL OR e.manufacturer_id = manufacturer_filter)
    AND (
      e.error_code % error_code_input
      OR e.normalized_code % normalize_error_code(error_code_input)
      OR normalize_error_code(error_code_input) = e.normalized_code
      OR error_code_input = ANY(e.alternative_codes)
    )
  ORDER BY similarity_score DESC
  LIMIT 20;
END;
$$ LANGUAGE plpgsql;

-- Function: Get documents for a specific product
CREATE OR REPLACE FUNCTION get_documents_for_product(
  product_id uuid,
  document_type_filter text DEFAULT NULL
)
RETURNS TABLE (
  document_id uuid,
  file_name text,
  document_type text,
  storage_url text,
  total_pages integer,
  upload_date timestamp with time zone,
  related_documents jsonb
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    d.id as document_id,
    d.file_name,
    d.document_type,
    d.storage_url,
    d.total_pages,
    d.upload_date,
    (
      SELECT jsonb_agg(jsonb_build_object(
        'id', rd.id,
        'file_name', rd.file_name,
        'relationship_type', dr.relationship_type
      ))
      FROM public.document_relationships dr
      JOIN public.documents rd ON rd.id = dr.secondary_document_id
      WHERE dr.primary_document_id = d.id
    ) as related_documents
  FROM public.documents d
  WHERE 
    product_id = ANY(d.product_ids)
    AND (document_type_filter IS NULL OR d.document_type = document_type_filter)
    AND d.processing_status = 'completed'
  ORDER BY 
    CASE d.document_type 
      WHEN 'cpmd_database' THEN 1
      WHEN 'service_manual' THEN 2
      WHEN 'parts_catalog' THEN 3
      ELSE 4
    END,
    d.upload_date DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get HP CPMD + Service Manual pairs
CREATE OR REPLACE FUNCTION get_hp_documentation_set(
  model_id uuid,
  error_code_filter text DEFAULT NULL
)
RETURNS TABLE (
  cpmd_document_id uuid,
  cpmd_file_name text,
  service_manual_id uuid,
  service_manual_name text,
  related_chunks integer,
  related_error_codes text[]
) AS $$
BEGIN
  RETURN QUERY
  SELECT DISTINCT
    cpmd.id as cpmd_document_id,
    cpmd.file_name as cpmd_file_name,
    manual.id as service_manual_id, 
    manual.file_name as service_manual_name,
    (SELECT COUNT(*)::integer FROM public.chunks c WHERE c.document_id IN (cpmd.id, manual.id)) as related_chunks,
    ARRAY(SELECT DISTINCT ec.error_code FROM public.error_codes ec WHERE ec.document_id IN (cpmd.id, manual.id)) as related_error_codes
  FROM public.documents cpmd
  JOIN public.document_relationships dr ON dr.primary_document_id = cpmd.id
  JOIN public.documents manual ON manual.id = dr.secondary_document_id
  WHERE cpmd.document_type = 'cpmd_database'
    AND manual.document_type = 'service_manual'
    AND dr.relationship_type = 'cpmd_manual_pair'
    AND model_id = ANY(cpmd.product_ids)
    AND (error_code_filter IS NULL OR EXISTS (
      SELECT 1 FROM public.error_codes ec 
      WHERE ec.document_id = cpmd.id 
        AND (ec.error_code = error_code_filter OR ec.normalized_code = normalize_error_code(error_code_filter))
    ))
  ORDER BY cpmd.file_name;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 3. PRODUCT MANAGEMENT FUNCTIONS
-- =====================================

-- Function: Validate option configuration
CREATE OR REPLACE FUNCTION validate_option_configuration(
  base_model_id uuid,
  selected_options uuid[]
)
RETURNS TABLE (
  is_valid boolean,
  validation_errors text[],
  suggested_additions uuid[],
  suggested_removals uuid[],
  total_compatibility_score numeric
) AS $$
DECLARE
  error_messages text[] := '{}';
  suggestions_add uuid[] := '{}';
  suggestions_remove uuid[] := '{}';
  total_score numeric := 0.0;
  option_count integer := 0;
  valid_config boolean := true;
BEGIN
  -- Check each selected option
  FOR i IN 1..array_length(selected_options, 1) LOOP
    DECLARE
      option_id uuid := selected_options[i];
      compatibility_record record;
    BEGIN
      -- Check if option is compatible with base model
      SELECT pc.* INTO compatibility_record
      FROM public.product_compatibility pc
      WHERE pc.base_product_id = base_model_id 
        AND pc.option_product_id = option_id;
      
      IF NOT FOUND THEN
        error_messages := array_append(error_messages, 'Option not found or not compatible with base model');
        valid_config := false;
      ELSIF NOT compatibility_record.is_compatible THEN
        error_messages := array_append(error_messages, 'Option is marked as incompatible: ' || compatibility_record.compatibility_notes);
        valid_config := false;
      ELSE
        -- Check complex rules
        IF compatibility_record.option_rules ? 'requires' THEN
          DECLARE
            required_options text[];
            req_option text;
          BEGIN
            required_options := ARRAY(SELECT jsonb_array_elements_text(compatibility_record.option_rules->'requires'));
            FOREACH req_option IN ARRAY required_options LOOP
              -- Check if required option is in selected list
              IF NOT EXISTS (
                SELECT 1 FROM public.products p 
                WHERE p.name = req_option 
                  AND p.id = ANY(selected_options)
              ) THEN
                error_messages := array_append(error_messages, 'Option requires: ' || req_option);
                -- Add to suggestions (CORRECTED SYNTAX)
                DECLARE
                  req_option_id uuid;
                BEGIN
                  SELECT p.id INTO req_option_id
                  FROM public.products p 
                  WHERE p.name = req_option AND p.parent_id = base_model_id;
                  
                  IF req_option_id IS NOT NULL THEN
                    suggestions_add := array_append(suggestions_add, req_option_id);
                  END IF;
                END;
                valid_config := false;
              END IF;
            END LOOP;
          END;
        END IF;
        
        -- Check exclusions
        IF compatibility_record.option_rules ? 'excludes' THEN
          DECLARE
            excluded_options text[];
            excl_option text;
          BEGIN
            excluded_options := ARRAY(SELECT jsonb_array_elements_text(compatibility_record.option_rules->'excludes'));
            FOREACH excl_option IN ARRAY excluded_options LOOP
              IF EXISTS (
                SELECT 1 FROM public.products p 
                WHERE p.name = excl_option 
                  AND p.id = ANY(selected_options)
              ) THEN
                error_messages := array_append(error_messages, 'Options conflict: ' || option_id::text || ' excludes ' || excl_option);
                -- Add to removal suggestions (CORRECTED SYNTAX)
                DECLARE
                  excl_option_id uuid;
                BEGIN
                  SELECT p.id INTO excl_option_id
                  FROM public.products p 
                  WHERE p.name = excl_option AND p.parent_id = base_model_id;
                  
                  IF excl_option_id IS NOT NULL THEN
                    suggestions_remove := array_append(suggestions_remove, excl_option_id);
                  END IF;
                END;
                valid_config := false;
              END IF;
            END LOOP;
          END;
        END IF;
        
        total_score := total_score + 1.0;
        option_count := option_count + 1;
      END IF;
    END;
  END LOOP;
  
  -- Calculate final score
  IF option_count > 0 THEN
    total_score := total_score / option_count;
  END IF;
  
  RETURN QUERY SELECT 
    valid_config,
    error_messages,
    suggestions_add,
    suggestions_remove,
    total_score;
END;
$$ LANGUAGE plpgsql;

-- Function: Get models for a series
CREATE OR REPLACE FUNCTION get_models_for_series(series_id uuid)
RETURNS TABLE (
  model_id uuid,
  model_name text,
  display_name text,
  model_number text,
  is_active boolean,
  available_options_count integer
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    p.id as model_id,
    p.name as model_name,
    p.display_name,
    p.model_number,
    p.is_active,
    (
      SELECT COUNT(*)::integer 
      FROM public.products opt 
      WHERE opt.parent_id = p.id 
        AND opt.product_type = 'option'
        AND opt.is_active = true
    ) as available_options_count
  FROM public.products p
  WHERE p.parent_id = series_id 
    AND p.product_type = 'model'
  ORDER BY p.name;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 4. ANALYTICS FUNCTIONS
-- =====================================

-- Function: Log search analytics
CREATE OR REPLACE FUNCTION log_search_analytics(
  p_session_id text,
  p_query_text text,
  p_search_type text,
  p_results_count integer,
  p_response_time_ms integer,
  p_manufacturer_filter uuid DEFAULT NULL,
  p_product_filter uuid DEFAULT NULL
)
RETURNS uuid AS $$
DECLARE
  analytics_id uuid;
BEGIN
  INSERT INTO public.search_analytics (
    session_id,
    user_id,
    query_text,
    search_type,
    manufacturer_filter,
    product_filter,
    results_count,
    response_time_ms
  ) VALUES (
    p_session_id,
    auth.uid(),
    p_query_text,
    p_search_type,
    p_manufacturer_filter,
    p_product_filter,
    p_results_count,
    p_response_time_ms
  )
  RETURNING id INTO analytics_id;
  
  RETURN analytics_id;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- 5. TRIGGERS FOR AUTOMATION
-- =====================================

-- Trigger: Auto-normalize error codes on insert/update
CREATE OR REPLACE FUNCTION auto_normalize_error_code()
RETURNS TRIGGER AS $$
BEGIN
  NEW.normalized_code := normalize_error_code(NEW.error_code);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_normalize_error_code
  BEFORE INSERT OR UPDATE ON public.error_codes
  FOR EACH ROW
  EXECUTE FUNCTION auto_normalize_error_code();

-- Trigger: Auto-extract and normalize error codes from chunks
CREATE OR REPLACE FUNCTION auto_normalize_chunk_error_codes()
RETURNS TRIGGER AS $$
BEGIN
  -- Normalize extracted error codes
  IF NEW.extracted_error_codes IS NOT NULL THEN
    NEW.normalized_error_codes := ARRAY(
      SELECT normalize_error_code(code) 
      FROM unnest(NEW.extracted_error_codes) AS code
      WHERE normalize_error_code(code) IS NOT NULL
    );
  END IF;
  
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_auto_normalize_chunk_error_codes
  BEFORE INSERT OR UPDATE ON public.chunks
  FOR EACH ROW
  EXECUTE FUNCTION auto_normalize_chunk_error_codes();

-- Trigger: Update timestamps
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply update timestamp trigger to relevant tables
CREATE TRIGGER trigger_update_manufacturers_updated_at
  BEFORE UPDATE ON public.manufacturers
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_products_updated_at
  BEFORE UPDATE ON public.products
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_documents_updated_at
  BEFORE UPDATE ON public.documents
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_chunks_updated_at
  BEFORE UPDATE ON public.chunks
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_error_codes_updated_at
  BEFORE UPDATE ON public.error_codes
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

CREATE TRIGGER trigger_update_processing_queue_updated_at
  BEFORE UPDATE ON public.processing_queue
  FOR EACH ROW
  EXECUTE FUNCTION update_updated_at_column();

-- =====================================
-- STEP 05 COMPLETE ✅
-- Next: Run Step 06 for Security & RLS Policies
-- =====================================