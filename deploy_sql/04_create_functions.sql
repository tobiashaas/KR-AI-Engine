-- Batch 4: create_functions.sql
-- Utility functions and vector search helpers. Using vector(768) in signatures.

-- updated_at trigger helper
CREATE OR REPLACE FUNCTION public.set_updated_at_column()
RETURNS trigger AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function: enhanced_multi_vector_search
CREATE OR REPLACE FUNCTION public.enhanced_multi_vector_search(
  query_embedding vector(768),
  search_manufacturer_id uuid DEFAULT NULL,
  search_model text DEFAULT NULL,
  max_results integer DEFAULT 20,
  min_similarity numeric DEFAULT 0.0,
  fetch_chunks boolean DEFAULT true
)
RETURNS TABLE (
  source_table text,
  record_id uuid,
  snippet text,
  similarity numeric,
  metadata jsonb,
  manufacturer_id uuid,
  model text
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT 'chunks'::text, c.id, LEFT(c.text_chunk, 1024), 1 - (c.embedding <-> query_embedding), c.metadata, d.manufacturer_id, d.model
  FROM public.chunks c
  JOIN public.documents d ON d.id = c.document_id
  WHERE c.embedding IS NOT NULL
    AND (search_manufacturer_id IS NULL OR d.manufacturer_id = search_manufacturer_id)
    AND (search_model IS NULL OR d.model = search_model)
  ORDER BY c.embedding <-> query_embedding
  LIMIT max_results;

  RETURN;
END;
$$;

-- Function: get_dashboard_stats
CREATE OR REPLACE FUNCTION public.get_dashboard_stats()
RETURNS jsonb
LANGUAGE plpgsql
AS $$
DECLARE
  result jsonb;
BEGIN
  SELECT jsonb_build_object(
    'totals', jsonb_build_object(
      'manufacturers', (SELECT COUNT(*) FROM public.manufacturers),
      'documents', (SELECT COUNT(*) FROM public.documents),
      'chunks', (SELECT COUNT(*) FROM public.chunks),
      'images', (SELECT COUNT(*) FROM public.images)
    ),
    'processing', jsonb_build_object(
      'pending', (SELECT COUNT(*) FROM public.processing_logs WHERE status = 'pending'),
      'failed', (SELECT COUNT(*) FROM public.processing_logs WHERE status = 'failed')
    )
  ) INTO result;

  RETURN result;
END;
$$;

-- Attach update triggers to keep updated_at current
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_documents_set_updated_at') THEN
    CREATE TRIGGER trg_documents_set_updated_at
    BEFORE UPDATE ON public.documents
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at_column();
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_chunks_set_updated_at') THEN
    CREATE TRIGGER trg_chunks_set_updated_at
    BEFORE UPDATE ON public.chunks
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at_column();
  END IF;

  IF NOT EXISTS (SELECT 1 FROM pg_trigger WHERE tgname = 'trg_service_manuals_set_updated_at') THEN
    CREATE TRIGGER trg_service_manuals_set_updated_at
    BEFORE UPDATE ON public.service_manuals
    FOR EACH ROW
    EXECUTE FUNCTION public.set_updated_at_column();
  END IF;
END;
$$;

-- End of Batch 4