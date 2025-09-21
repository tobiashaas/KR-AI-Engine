-- Batch 2: enable_rls_service_only.sql
-- Enable Row Level Security for sensitive tables (service-only strategy)

ALTER TABLE public.manufacturers ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.documents ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chunks ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.service_manuals ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parts_catalog_entries ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.bulletins ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.images ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.vision_analysis_results ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_sessions ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.chat_messages ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.processing_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.product_models ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.quality_defect_patterns ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.parts_model_compatibility ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.company_internal_docs ENABLE ROW LEVEL SECURITY;

-- Note: No policies for anonymous/authenticated clients are created. Only service-role (SERVICE_ROLE_KEY) or DB owners can access these tables.
-- End of Batch 2