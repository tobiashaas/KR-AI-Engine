-- Batch 3 (adjusted): All CREATE INDEX CONCURRENTLY statements extracted and ready-to-run individually.
-- Run these statements one by one in the SQL editor or psql (they must not be wrapped in a transaction).

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_manufacturers_name 
  ON public.manufacturers (name);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_manufacturer_model_series 
  ON public.service_manuals (manufacturer_id, model, model_series);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_ service_manuals_file_hash 
  ON public.service_manuals (file_hash);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_processing_status 
  ON public.service_manuals (processing_status, quality_score DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_procedures 
  ON public.service_manuals USING gin(procedures);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_error_codes 
  ON public.service_manuals USING gin(error_codes);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_part_numbers 
  ON public.service_manuals USING gin(part_numbers_mentioned);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_embedding 
  ON public.service_manuals USING hnsw (embedding extensions.vector_cosine_ops) 
  WITH (m = 32, ef_construction = 128);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_service_manuals_semantic_tags 
  ON public.service_manuals USING gin(semantic_tags);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulletins_manufacturer_priority 
  ON public.bulletins (manufacturer_id, priority_level, effective_date DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulletins_models_affected 
  ON public.bulletins USING gin(models_affected);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulletins_severity_status 
  ON public.bulletins (severity_level, resolution_status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulletins_embedding 
  ON public.bulletins USING hnsw (embedding extensions.vector_cosine_ops)
  WITH (m = 24, ef_construction = 96);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_bulletins_symptoms 
  ON public.bulletins USING gin(symptoms);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalogs_manufacturer_model_family 
  ON public.parts_catalogs (manufacturer_id, model, model_family);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalogs_part_numbers 
  ON public.parts_catalogs USING gin(part_numbers_mentioned);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalogs_compatibility 
  ON public.parts_catalogs USING gin(compatibility_info);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalogs_embedding 
  ON public.parts_catalogs USING hnsw (embedding extensions.vector_cosine_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cpmd_model_message_code_type 
  ON public.cpmd_documents (model, message_code, message_type);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cpmd_error_codes 
  ON public.cpmd_documents USING gin(related_error_codes);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cpmd_firmware_compatibility 
  ON public.cpmd_documents USING gin(firmware_version);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_cpmd_embedding 
  ON public.cpmd_documents USING hnsw (embedding extensions.vector_cosine_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_images_file_hash 
  ON public.images (file_hash);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_images_r2_key_status 
  ON public.images (r2_key, r2_upload_status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_images_defect_training 
  ON public.images (defect_type, defect_severity, human_verified);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_images_manufacturer_model_series 
  ON public.images (manufacturer_id, model, model_series);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_images_vision_analysis 
  ON public.images (vision_processed, vision_confidence DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalog_partnumber_manufacturer 
  ON public.parts_catalog (manufacturer_id, part_number);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalog_availability 
  ON public.parts_catalog (availability_status, stock_level);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalog_compatibility 
  ON public.parts_catalog USING gin(models_compatible);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_parts_catalog_category 
  ON public.parts_catalog (category, sub_category);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_quality_defect_patterns_category 
  ON public.quality_defect_patterns (defect_category, defect_subcategory);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_quality_defect_patterns_embedding 
  ON public.quality_defect_patterns USING hnsw (embedding extensions.vector_cosine_ops)
  WITH (m = 40, ef_construction = 160);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_quality_defect_patterns_accuracy 
  ON public.quality_defect_patterns (training_accuracy DESC, detection_accuracy DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_internal_docs_category_dept 
  ON public.company_internal_docs (document_category, department);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_internal_docs_embedding 
  ON public.company_internal_docs USING hnsw (embedding extensions.vector_cosine_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_internal_docs_tags 
  ON public.company_internal_docs USING gin(tags);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_company_internal_docs_keywords 
  ON public.company_internal_docs USING gin(keywords);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technician_case_history_technician 
  ON public.technician_case_history (technician_id, case_priority);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technician_case_history_embedding 
  ON public.technician_case_history USING hnsw (embedding extensions.vector_cosine_ops);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technician_case_history_manufacturer_model 
  ON public.technician_case_history (manufacturer_id, customer_model);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_technician_case_history_problem_category 
  ON public.technician_case_history (problem_category, problem_severity);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processing_logs_status_created 
  ON public.processing_logs (status, created_at DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processing_logs_file_hash 
  ON public.processing_logs (file_hash);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processing_logs_performance 
  ON public.processing_logs (processing_time_seconds, chunks_created);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_processing_logs_document_type 
  ON public.processing_logs (document_type, manufacturer_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_n8n_chat_session_sequence 
  ON public.n8n_chat_memory (session_id, message_sequence DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_n8n_chat_manufacturer_model_context 
  ON public.n8n_chat_memory (manufacturer_context_id, model_context);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_n8n_chat_intent_confidence 
  ON public.n8n_chat_memory (intent_detected, confidence_score DESC);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vision_analysis_image_id 
  ON public.vision_analysis_results (source_image_id);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_vision_analysis_verification_status 
  ON public.vision_analysis_results (human_verification_status);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_models_manufacturer_series 
  ON public.product_models (manufacturer_id, model_series);

CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_product_models_lifecycle 
  ON public.product_models (launch_date, discontinuation_date);