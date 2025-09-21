-- KRAI Database Data Export
-- Generated: 2025-09-21T14:55:50.166Z
-- Contains all current data from production database

-- =====================================
-- DATA INSERTION SCRIPTS
-- =====================================

-- Data for table: manufacturers
-- Records: 1

INSERT INTO public.manufacturers (id, name, display_name, website, metadata, created_at, updated_at) VALUES ('7a1f6449-3c71-45bd-b40a-fb5fc30ac87f', 'KRAI Test Hersteller GmbH', NULL, 'https://test.example.com', '{}', '2025-09-21T14:18:00.640941+00:00', '2025-09-21T14:18:00.640941+00:00');

-- documents: No data to export (empty table)

-- chunks: No data to export (empty table)

-- Data for table: service_manuals
-- Records: 1

INSERT INTO public.service_manuals (id, document_id, manufacturer_id, model, model_series, file_hash, processing_status, embedding, metadata, created_at, updated_at) VALUES ('57c9f24d-3590-469c-ba47-54c6476e2cda', NULL, NULL, NULL, NULL, NULL, 'pending', NULL, '{}', '2025-09-21T14:15:16.868641+00:00', '2025-09-21T14:15:16.868641+00:00');

-- parts_catalog_entries: No data to export (empty table)

-- bulletins: No data to export (empty table)

-- images: No data to export (empty table)

-- vision_analysis_results: No data to export (empty table)

-- chat_sessions: No data to export (empty table)

-- chat_messages: No data to export (empty table)

-- processing_logs: No data to export (empty table)

-- product_models: No data to export (empty table)

-- quality_defect_patterns: No data to export (empty table)

-- parts_model_compatibility: No data to export (empty table)

-- company_internal_docs: No data to export (empty table)

