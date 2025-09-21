-- Batch 5: fk_indexes_triggers_policies.sql
-- Additional FK indexes (non-concurrent optional), and policy templates (optional). Run after other batches.

-- FK b-tree indexes
CREATE INDEX IF NOT EXISTS idx_chunks_document_id ON public.chunks (document_id);
CREATE INDEX IF NOT EXISTS idx_documents_manufacturer ON public.documents (manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_service_manuals_document_id ON public.service_manuals (document_id);
CREATE INDEX IF NOT EXISTS idx_parts_catalog_entries_document_id ON public.parts_catalog_entries (document_id);
CREATE INDEX IF NOT EXISTS idx_parts_model_compatibility_part_id ON public.parts_model_compatibility (part_id);

-- Policy templates (ONLY if you want explicit service-role checks). These are examples and can be removed.

-- Example: allow only service_role JWT to SELECT manufacturers (redundant if no client policies exist)
CREATE POLICY "service_select_manufacturers" ON public.manufacturers
  FOR SELECT
  TO authenticated
  USING ((auth.jwt() ->> 'role') = 'service_role');

-- Example: allow service_role to INSERT/UPDATE/DELETE on documents via JWT claim check
CREATE POLICY "service_manage_documents" ON public.documents
  FOR ALL
  TO authenticated
  USING ((auth.jwt() ->> 'role') = 'service_role')
  WITH CHECK ((auth.jwt() ->> 'role') = 'service_role');

-- Note: If you truly want service-only access, you can omit creating any policies for anon/authenticated. The SERVICE_ROLE_KEY will bypass RLS and retain full access.

-- End of Batch 5