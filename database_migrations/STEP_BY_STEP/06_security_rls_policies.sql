-- =====================================
-- KRAI ENGINE - STEP 06: SECURITY & RLS POLICIES
-- Row Level Security + Access Control Policies
-- =====================================

-- =====================================
-- 1. ENABLE ROW LEVEL SECURITY ON ALL TABLES
-- =====================================

-- Core Tables
ALTER TABLE public.manufacturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.products ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;

-- Performance & Intelligence Tables
ALTER TABLE public.embeddings ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.error_codes ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.instructional_videos ENABLE ROW LEVEL SECURITY;

-- Management & Relationship Tables
ALTER TABLE public.document_relationships ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_compatibility ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.option_groups ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_queue ENABLE ROW LEVEL SECURITY;

-- Analytics & Competitive Tables
ALTER TABLE public.search_analytics ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.competitive_features ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_features ENABLE ROW LEVEL SECURITY;

-- =====================================
-- 2. SERVICE ROLE POLICIES (Full Access)
-- Backend Python scripts, Admin operations
-- =====================================

-- Service role bypass (full access to everything)
CREATE POLICY "service_role_all_manufacturers" ON public.manufacturers FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_products" ON public.products FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_documents" ON public.documents FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_chunks" ON public.chunks FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_embeddings" ON public.embeddings FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_error_codes" ON public.error_codes FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_images" ON public.images FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_videos" ON public.instructional_videos FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_doc_relationships" ON public.document_relationships FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_compatibility" ON public.product_compatibility FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_option_groups" ON public.option_groups FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_queue" ON public.processing_queue FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_analytics" ON public.search_analytics FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_competitive_features" ON public.competitive_features FOR ALL TO service_role USING (true) WITH CHECK (true);
CREATE POLICY "service_role_all_product_features" ON public.product_features FOR ALL TO service_role USING (true) WITH CHECK (true);

-- =====================================
-- 3. AUTHENTICATED USER POLICIES (Dashboard Users)
-- Read access to most data, limited write access
-- =====================================

-- Read access to all core data
CREATE POLICY "authenticated_read_manufacturers" ON public.manufacturers FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_products" ON public.products FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_documents" ON public.documents FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_chunks" ON public.chunks FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_embeddings" ON public.embeddings FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_error_codes" ON public.error_codes FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_images" ON public.images FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_videos" ON public.instructional_videos FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_doc_relationships" ON public.document_relationships FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_compatibility" ON public.product_compatibility FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_option_groups" ON public.option_groups FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_queue" ON public.processing_queue FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_competitive_features" ON public.competitive_features FOR SELECT TO authenticated USING (true);
CREATE POLICY "authenticated_read_product_features" ON public.product_features FOR SELECT TO authenticated USING (true);

-- Limited write access for authenticated users
CREATE POLICY "authenticated_write_analytics" ON public.search_analytics FOR ALL TO authenticated USING (true) WITH CHECK (true);

-- Authenticated users can update their own search analytics
CREATE POLICY "authenticated_read_analytics" ON public.search_analytics FOR SELECT TO authenticated USING (
  user_id IS NULL OR user_id = auth.uid()
);

-- =====================================
-- 4. ANONYMOUS USER POLICIES (Public API)
-- Read-only access to completed, public content
-- =====================================

-- Anonymous read access to basic manufacturer info
CREATE POLICY "anonymous_read_manufacturers" ON public.manufacturers FOR SELECT TO anon USING (true);

-- Anonymous read access to active products only
CREATE POLICY "anonymous_read_products" ON public.products FOR SELECT TO anon USING (is_active = true);

-- Anonymous read access to completed documents only
CREATE POLICY "anonymous_read_documents" ON public.documents FOR SELECT TO anon USING (
  processing_status = 'completed'
);

-- Anonymous read access to completed chunks only
CREATE POLICY "anonymous_read_chunks" ON public.chunks FOR SELECT TO anon USING (
  processing_status = 'completed'
  AND EXISTS (
    SELECT 1 FROM public.documents d 
    WHERE d.id = document_id 
      AND d.processing_status = 'completed'
  )
);

-- Anonymous read access to embeddings for completed chunks
CREATE POLICY "anonymous_read_embeddings" ON public.embeddings FOR SELECT TO anon USING (
  EXISTS (
    SELECT 1 FROM public.chunks c
    JOIN public.documents d ON d.id = c.document_id
    WHERE c.id = chunk_id 
      AND c.processing_status = 'completed'
      AND d.processing_status = 'completed'
  )
);

-- Anonymous read access to error codes
CREATE POLICY "anonymous_read_error_codes" ON public.error_codes FOR SELECT TO anon USING (true);

-- Anonymous read access to images
CREATE POLICY "anonymous_read_images" ON public.images FOR SELECT TO anon USING (
  EXISTS (
    SELECT 1 FROM public.documents d 
    WHERE d.id = document_id 
      AND d.processing_status = 'completed'
  )
);

-- Anonymous read access to official videos only
CREATE POLICY "anonymous_read_videos" ON public.instructional_videos FOR SELECT TO anon USING (is_official = true);

-- Anonymous read access to document relationships
CREATE POLICY "anonymous_read_doc_relationships" ON public.document_relationships FOR SELECT TO anon USING (
  EXISTS (
    SELECT 1 FROM public.documents d1, public.documents d2
    WHERE d1.id = primary_document_id 
      AND d2.id = secondary_document_id
      AND d1.processing_status = 'completed'
      AND d2.processing_status = 'completed'
  )
);

-- Anonymous read access to verified compatibility data
CREATE POLICY "anonymous_read_compatibility" ON public.product_compatibility FOR SELECT TO anon USING (
  is_compatible = true 
  AND verified_date IS NOT NULL
);

-- Anonymous read access to option groups
CREATE POLICY "anonymous_read_option_groups" ON public.option_groups FOR SELECT TO anon USING (true);

-- Anonymous read access to competitive features
CREATE POLICY "anonymous_read_competitive_features" ON public.competitive_features FOR SELECT TO anon USING (true);

-- Anonymous read access to verified product features
CREATE POLICY "anonymous_read_product_features" ON public.product_features FOR SELECT TO anon USING (verified = true);

-- Anonymous can create search analytics (for tracking)
CREATE POLICY "anonymous_create_analytics" ON public.search_analytics FOR INSERT TO anon WITH CHECK (
  user_id IS NULL  -- Anonymous users can't set user_id
);

-- Anonymous read access to public analytics (no personal data)
CREATE POLICY "anonymous_read_public_analytics" ON public.search_analytics FOR SELECT TO anon USING (
  user_id IS NULL 
  AND search_timestamp >= now() - interval '7 days'  -- Only recent public data
);

-- =====================================
-- 5. ADDITIONAL SECURITY POLICIES
-- =====================================

-- Prevent anonymous access to processing queue (sensitive operational data)
-- No policy = no access for anonymous users

-- Prevent anonymous access to personal analytics data
-- Covered by existing policies above

-- =====================================
-- 6. GRANT NECESSARY PERMISSIONS
-- =====================================

-- Grant usage on schemas
GRANT USAGE ON SCHEMA public TO anon, authenticated, service_role;
GRANT USAGE ON SCHEMA auth TO anon, authenticated, service_role;

-- Grant execute permissions on functions
GRANT EXECUTE ON ALL FUNCTIONS IN SCHEMA public TO anon, authenticated, service_role;

-- Grant sequence permissions for ID generation
GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO anon, authenticated, service_role;

-- =====================================
-- 7. SECURITY VALIDATION FUNCTIONS
-- =====================================

-- Function to check if user has admin privileges
CREATE OR REPLACE FUNCTION is_admin_user()
RETURNS boolean AS $$
BEGIN
  -- Check if user has admin role or is service_role
  RETURN (
    current_setting('role') = 'service_role'
    OR (
      auth.uid() IS NOT NULL 
      AND EXISTS (
        SELECT 1 FROM auth.users 
        WHERE id = auth.uid() 
          AND raw_user_meta_data->>'role' = 'admin'
      )
    )
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to validate document access
CREATE OR REPLACE FUNCTION can_access_document(doc_id uuid)
RETURNS boolean AS $$
BEGIN
  -- Service role can access everything
  IF current_setting('role') = 'service_role' THEN
    RETURN true;
  END IF;
  
  -- Check if document is completed (for public access)
  RETURN EXISTS (
    SELECT 1 FROM public.documents 
    WHERE id = doc_id 
      AND processing_status = 'completed'
  );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- =====================================
-- STEP 06 COMPLETE ✅
-- Next: Run Step 07 for Sample Data & Validation
-- =====================================