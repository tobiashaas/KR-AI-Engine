-- =====================================
-- KRAI ENGINE - STEP 07: SAMPLE DATA & VALIDATION
-- Test Data + Complex Option Rules + Relationship Validation
-- =====================================

-- =====================================
-- 1. SAMPLE MANUFACTURERS
-- =====================================

INSERT INTO public.manufacturers (name, display_name, website, support_url, is_competitor, metadata) VALUES
('HP Inc.', 'Hewlett Packard', 'https://www.hp.com', 'https://support.hp.com', false, '{"founded": 1939, "headquarters": "Palo Alto, CA"}'::jsonb),
('Canon Inc.', 'Canon', 'https://www.canon.com', 'https://support.canon.com', true, '{"founded": 1937, "headquarters": "Tokyo, Japan"}'::jsonb),
('Xerox Corporation', 'Xerox', 'https://www.xerox.com', 'https://support.xerox.com', true, '{"founded": 1906, "headquarters": "Norwalk, CT"}'::jsonb),
('Brother Industries', 'Brother', 'https://www.brother.com', 'https://support.brother.com', true, '{"founded": 1908, "headquarters": "Nagoya, Japan"}'::jsonb);

-- =====================================
-- 2. SAMPLE PRODUCT HIERARCHY (HP OfficeJet Pro Series)
-- =====================================

-- Insert HP OfficeJet Pro Series
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name, 
  year_introduced, is_active, device_category, form_factor, technical_specs
)
SELECT 
  m.id,
  'series',
  NULL,
  'OfficeJet Pro',
  'HP OfficeJet Pro Series',
  2015,
  true,
  ARRAY['printer', 'scanner', 'fax'],
  'desktop',
  '{"target_market": "small_business", "technology": "inkjet"}'::jsonb
FROM public.manufacturers m WHERE m.name = 'HP Inc.';

-- Insert HP OfficeJet Pro 9025 Model
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name, model_number,
  year_introduced, is_active, device_category, form_factor, technical_specs
)
SELECT 
  m.id,
  'model',
  series.id,
  '9025',
  'HP OfficeJet Pro 9025',
  'HP-OJP-9025',
  2020,
  true,
  ARRAY['printer', 'scanner', 'fax'],
  'desktop',
  '{
    "print_speed_color": 22,
    "print_speed_mono": 24,
    "max_resolution": 4800,
    "connectivity": ["wifi", "ethernet", "usb"],
    "monthly_volume": 500,
    "paper_capacity_standard": 250
  }'::jsonb
FROM public.manufacturers m, public.products series
WHERE m.name = 'HP Inc.' 
  AND series.name = 'OfficeJet Pro' AND series.product_type = 'series';

-- Insert HP OfficeJet Pro 9020 Model (for comparison)
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name, model_number,
  year_introduced, is_active, device_category, form_factor, technical_specs
)
SELECT 
  m.id,
  'model',
  series.id,
  '9020',
  'HP OfficeJet Pro 9020',
  'HP-OJP-9020',
  2019,
  true,
  ARRAY['printer', 'scanner'],
  'desktop',
  '{
    "print_speed_color": 20,
    "print_speed_mono": 22,
    "max_resolution": 4800,
    "connectivity": ["wifi", "usb"],
    "monthly_volume": 400,
    "paper_capacity_standard": 250
  }'::jsonb
FROM public.manufacturers m, public.products series
WHERE m.name = 'HP Inc.' 
  AND series.name = 'OfficeJet Pro' AND series.product_type = 'series';

-- =====================================
-- 3. COMPLEX OPTIONS WITH DEPENDENCIES
-- =====================================

-- Insert Bridge Options (Required for Finishers)
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name,
  option_category, installation_complexity, technical_specs, is_active
)
SELECT 
  m.id,
  'option',
  model.id,
  'Bridge A',
  'HP Bridge Unit A (for Standard Finishers)',
  'bridge',
  'standard',
  '{"weight_kg": 2.5, "enables": ["finisher_x"], "conflicts_with": ["bridge_b"]}'::jsonb,
  true
FROM public.manufacturers m, public.products model
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name,
  option_category, installation_complexity, technical_specs, is_active
)
SELECT 
  m.id,
  'option',
  model.id,
  'Bridge B',
  'HP Bridge Unit B (for Advanced Finishers)',
  'bridge',
  'standard',
  '{"weight_kg": 3.2, "enables": ["finisher_y"], "conflicts_with": ["bridge_a"]}'::jsonb,
  true
FROM public.manufacturers m, public.products model
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

-- Insert Finisher Options
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name,
  option_category, installation_complexity, option_dependencies, technical_specs, is_active
)
SELECT 
  m.id,
  'option',
  model.id,
  'Finisher X',
  'HP Professional Finisher X (Staple + Sort)',
  'finisher',
  'complex',
  ARRAY[bridge.id],  -- Requires Bridge A
  '{"staple_capacity": 50, "sort_bins": 5, "requires_bridge": "bridge_a"}'::jsonb,
  true
FROM public.manufacturers m, public.products model, public.products bridge
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model'
  AND bridge.name = 'Bridge A' AND bridge.parent_id = model.id;

INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name,
  option_category, installation_complexity, option_dependencies, technical_specs, is_active
)
SELECT 
  m.id,
  'option',
  model.id,
  'Finisher Y',
  'HP Advanced Finisher Y (Booklet + Hole Punch)',
  'finisher',
  'complex',
  ARRAY[bridge.id],  -- Requires Bridge B
  '{"booklet_capacity": 20, "hole_punch": true, "requires_bridge": "bridge_b"}'::jsonb,
  true
FROM public.manufacturers m, public.products model, public.products bridge
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model'
  AND bridge.name = 'Bridge B' AND bridge.parent_id = model.id;

-- Insert Additional Options
INSERT INTO public.products (
  manufacturer_id, product_type, parent_id, name, display_name,
  option_category, installation_complexity, technical_specs, is_active
) 
SELECT 
  m.id,
  'option',
  model.id,
  option_data.name,
  option_data.display_name,
  option_data.category,
  option_data.complexity,
  option_data.specs::jsonb,
  true
FROM public.manufacturers m, public.products model,
(VALUES 
  ('Large Paper Tray', 'HP 550-Sheet Paper Tray', 'tray', 'simple', '{"capacity": 550, "paper_sizes": ["A4", "Letter", "Legal"]}'),
  ('Wireless Module', 'HP Wireless 802.11ac Module', 'connectivity', 'standard', '{"wifi_standard": "802.11ac", "frequency": "2.4/5GHz"}'),
  ('Fax Module', 'HP Digital Fax Module', 'fax', 'standard', '{"transmission_speed": "33.6k", "memory": "8MB"}'),
  ('Security Module', 'HP JetAdvantage Security Module', 'security', 'professional', '{"encryption": "AES-256", "authentication": "LDAP"}')
) AS option_data(name, display_name, category, complexity, specs)
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

-- =====================================
-- 4. SAMPLE DOCUMENTS
-- =====================================

-- Insert CPMD Database
INSERT INTO public.documents (
  file_name, file_hash, storage_path, document_type, manufacturer_id, 
  product_ids, language, processing_status, source_system, cpmd_version, metadata
)
SELECT 
  'HP_9025_CPMD_Database_v2.1.pdf',
  'a1b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef123456',
  '/cpmd/hp/hp_9025_cpmd_v2.1.xml',
  'cpmd_database',
  m.id,
  ARRAY[model.id],
  'en',
  'completed',
  'cpmd_database',
  'v2.1.2024',
  '{"error_count": 287, "last_update": "2024-03-15", "format": "xml"}'::jsonb
FROM public.manufacturers m, public.products model
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

-- Insert Service Manual
INSERT INTO public.documents (
  file_name, file_hash, storage_path, document_type, manufacturer_id,
  product_ids, total_pages, language, processing_status, metadata
)
SELECT 
  'HP_OfficeJet_Pro_9025_Service_Manual.pdf',
  'b2c3d4e5f6789012345678901234567890abcdef1234567890abcdef1234567',
  '/manuals/hp/hp_9025_service_manual.pdf',
  'service_manual',
  m.id,
  ARRAY[model.id],
  234,
  'en',
  'completed',
  '{"revision": "Rev A", "publication_date": "2024-02-10", "chapters": 12}'::jsonb
FROM public.manufacturers m, public.products model
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

-- Insert Parts Catalog
INSERT INTO public.documents (
  file_name, file_hash, storage_path, document_type, manufacturer_id,
  product_ids, total_pages, language, processing_status, metadata
)
SELECT 
  'HP_OfficeJet_Pro_9025_Parts_Catalog.pdf',
  'c3d4e5f6789012345678901234567890abcdef1234567890abcdef12345678',
  '/parts/hp/hp_9025_parts_catalog.pdf',
  'parts_catalog',
  m.id,
  ARRAY[model.id],
  89,
  'en',
  'completed',
  '{"part_count": 156, "illustrations": 45, "revision": "Rev B"}'::jsonb
FROM public.manufacturers m, public.products model
WHERE m.name = 'HP Inc.' 
  AND model.name = '9025' AND model.product_type = 'model';

-- =====================================
-- 5. DOCUMENT RELATIONSHIPS (CPMD + Manual Pairing)
-- =====================================

INSERT INTO public.document_relationships (
  primary_document_id, secondary_document_id, relationship_type, description, priority_order
)
SELECT 
  cpmd.id,
  manual.id,
  'cpmd_manual_pair',
  'HP 9025 CPMD Database paired with Service Manual for comprehensive troubleshooting',
  1
FROM public.documents cpmd, public.documents manual
WHERE cpmd.file_name LIKE '%CPMD_Database%' 
  AND cpmd.document_type = 'cpmd_database'
  AND manual.file_name LIKE '%Service_Manual%'
  AND manual.document_type = 'service_manual'
  AND cpmd.manufacturer_id = manual.manufacturer_id;

-- =====================================
-- 6. COMPLEX COMPATIBILITY RULES
-- =====================================

-- Finisher X requires Bridge A
INSERT INTO public.product_compatibility (
  base_product_id, option_product_id, is_compatible,
  compatibility_notes, installation_notes, option_rules, rule_priority
)
SELECT 
  base.id,
  finisher.id,
  true,
  'Finisher X requires Bridge A to be installed first',
  'Install Bridge A, then Finisher X. Professional installation recommended.',
  '{
    "requires": ["bridge_a"],
    "excludes": ["finisher_y", "bridge_b"],
    "installation_order": ["bridge_a", "finisher_x"]
  }'::jsonb,
  1
FROM public.products base, public.products finisher
WHERE base.name = '9025' AND base.product_type = 'model'
  AND finisher.name = 'Finisher X' AND finisher.parent_id = base.id;

-- Finisher Y requires Bridge B  
INSERT INTO public.product_compatibility (
  base_product_id, option_product_id, is_compatible,
  compatibility_notes, installation_notes, option_rules, rule_priority
)
SELECT 
  base.id,
  finisher.id,
  true,
  'Finisher Y requires Bridge B to be installed first',
  'Install Bridge B, then Finisher Y. Requires firmware v2.5+.',
  '{
    "requires": ["bridge_b"],
    "excludes": ["finisher_x", "bridge_a"],
    "min_firmware": "v2.5.0",
    "installation_order": ["bridge_b", "finisher_y"]
  }'::jsonb,
  1
FROM public.products base, public.products finisher
WHERE base.name = '9025' AND base.product_type = 'model'
  AND finisher.name = 'Finisher Y' AND finisher.parent_id = base.id;

-- Bridge compatibility rules
INSERT INTO public.product_compatibility (
  base_product_id, option_product_id, is_compatible,
  compatibility_notes, option_rules
)
SELECT 
  base.id,
  bridge.id,
  true,
  'Bridge A is required for Finisher X installation',
  '{"enables": ["finisher_x"], "conflicts_with": ["bridge_b"]}'::jsonb
FROM public.products base, public.products bridge
WHERE base.name = '9025' AND base.product_type = 'model'
  AND bridge.name = 'Bridge A' AND bridge.parent_id = base.id;

INSERT INTO public.product_compatibility (
  base_product_id, option_product_id, is_compatible,
  compatibility_notes, option_rules
)
SELECT 
  base.id,
  bridge.id,
  true,
  'Bridge B is required for Finisher Y installation',
  '{"enables": ["finisher_y"], "conflicts_with": ["bridge_a"]}'::jsonb
FROM public.products base, public.products bridge
WHERE base.name = '9025' AND base.product_type = 'model'
  AND bridge.name = 'Bridge B' AND bridge.parent_id = base.id;

-- =====================================
-- 7. OPTION GROUPS (Mutual Exclusions)
-- =====================================

-- HP Finisher Group (mutually exclusive)
INSERT INTO public.option_groups (
  manufacturer_id, group_name, group_type, max_selections, min_selections,
  option_product_ids, description, technical_reason
)
SELECT 
  m.id,
  'Finisher Group',
  'exclusive',
  1,
  0,
  ARRAY[
    (SELECT id FROM public.products WHERE name = 'Finisher X' AND parent_id IN (SELECT id FROM public.products WHERE name = '9025')),
    (SELECT id FROM public.products WHERE name = 'Finisher Y' AND parent_id IN (SELECT id FROM public.products WHERE name = '9025'))
  ],
  'Only one finisher can be installed per printer',
  'Physical space constraints in rear assembly area'
FROM public.manufacturers m
WHERE m.name = 'HP Inc.';

-- HP Bridge Group (mutually exclusive)
INSERT INTO public.option_groups (
  manufacturer_id, group_name, group_type, max_selections, min_selections,
  option_product_ids, description, technical_reason
)
SELECT 
  m.id,
  'Bridge Group',
  'exclusive',
  1,
  0,
  ARRAY[
    (SELECT id FROM public.products WHERE name = 'Bridge A' AND parent_id IN (SELECT id FROM public.products WHERE name = '9025')),
    (SELECT id FROM public.products WHERE name = 'Bridge B' AND parent_id IN (SELECT id FROM public.products WHERE name = '9025'))
  ],
  'Only one bridge unit can be installed',
  'Single bridge interface point available'
FROM public.manufacturers m
WHERE m.name = 'HP Inc.';

-- =====================================
-- 8. SAMPLE ERROR CODES
-- =====================================

INSERT INTO public.error_codes (
  manufacturer_id, document_id, error_code, normalized_code, error_description,
  solution_steps, affected_product_ids, device_categories, severity_level,
  frequency_score, source_system, alternative_codes, metadata
)
SELECT 
  m.id,
  d.id,
  'C1234',
  normalize_error_code('C1234'),
  'Paper jam in input tray assembly',
  E'1. Turn off printer and unplug power\n2. Remove all paper from input tray\n3. Check for torn paper pieces\n4. Reinstall tray and power on\n5. Test with single sheet',
  ARRAY[model.id],
  ARRAY['printer', 'mfp'],
  3,
  7.5,
  'cpmd_database',
  ARRAY['Error C1234', 'Jam-Input-01', 'Paper Jam 1234'],
  '{"frequency_monthly": 45, "resolution_time_minutes": 5, "field_replaceable": false}'::jsonb
FROM public.manufacturers m, public.documents d, public.products model
WHERE m.name = 'HP Inc.'
  AND d.document_type = 'cpmd_database'
  AND d.file_name LIKE '%9025%'
  AND model.name = '9025' AND model.product_type = 'model';

INSERT INTO public.error_codes (
  manufacturer_id, document_id, error_code, normalized_code, error_description,
  solution_steps, affected_product_ids, device_categories, severity_level,
  frequency_score, source_system, alternative_codes, metadata
)
SELECT 
  m.id,
  d.id,
  'E-5678',
  normalize_error_code('E-5678'),
  'Scanner calibration failure',
  E'1. Clean scanner glass with lint-free cloth\n2. Access Service Menu > Calibration\n3. Run auto-calibration sequence\n4. If failure persists, replace scanner assembly',
  ARRAY[model.id],
  ARRAY['scanner', 'mfp'],
  2,
  3.2,
  'cpmd_database',
  ARRAY['Error E5678', 'Scanner Error 5678', 'Cal-Fail-5678'],
  '{"frequency_monthly": 12, "resolution_time_minutes": 15, "field_replaceable": true}'::jsonb
FROM public.manufacturers m, public.documents d, public.products model
WHERE m.name = 'HP Inc.'
  AND d.document_type = 'cpmd_database'
  AND d.file_name LIKE '%9025%'
  AND model.name = '9025' AND model.product_type = 'model';

-- =====================================
-- 9. SAMPLE CHUNKS (Text Content)
-- =====================================

INSERT INTO public.chunks (
  document_id, chunk_index, page_start, page_end, text_chunk, token_count,
  fingerprint, section_title, extracted_error_codes, normalized_error_codes,
  extracted_part_numbers, ocr_confidence, chunk_quality_score, processing_status
)
SELECT 
  d.id,
  0,
  45,
  45,
  'Paper Jam Troubleshooting - Error Code C1234. When the printer displays error C1234, this indicates a paper jam in the input tray assembly. The paper path sensors have detected an obstruction that prevents normal paper feeding. This error commonly occurs when: 1) Paper is loaded incorrectly, 2) Foreign objects are in the paper path, 3) Torn paper remains from previous jams. Resolution requires careful inspection of the entire paper path from input tray to output area.',
  156,
  'chunk_hash_001_troubleshooting_c1234',
  'Chapter 5: Troubleshooting Common Issues',
  ARRAY['C1234'],
  ARRAY[normalize_error_code('C1234')],
  ARRAY['CB435A', 'CE285A'],
  0.95,
  0.88,
  'completed'
FROM public.documents d
WHERE d.document_type = 'service_manual' AND d.file_name LIKE '%9025%';

INSERT INTO public.chunks (
  document_id, chunk_index, page_start, page_end, text_chunk, token_count,
  fingerprint, section_title, extracted_error_codes, normalized_error_codes,
  ocr_confidence, chunk_quality_score, processing_status
)
SELECT 
  d.id,
  1,
  67,
  67,
  'Scanner Assembly Maintenance - Error E-5678. The scanner calibration process ensures accurate color reproduction and proper image quality. Error E-5678 indicates that the automatic calibration sequence has failed. This typically occurs due to: dirty scanner glass, misaligned scanning head, or sensor malfunction. Regular cleaning of the scanner glass every 1000 scans prevents most calibration issues.',
  143,
  'chunk_hash_002_scanner_e5678',
  'Chapter 7: Scanner Maintenance and Calibration',
  ARRAY['E-5678'],
  ARRAY[normalize_error_code('E-5678')],
  0.92,
  0.91,
  'completed'
FROM public.documents d
WHERE d.document_type = 'service_manual' AND d.file_name LIKE '%9025%';

-- =====================================
-- 10. COMPETITIVE FEATURES SETUP
-- =====================================

-- Define competitive feature categories
INSERT INTO public.competitive_features (
  feature_category, feature_name, feature_description, data_type, unit, higher_is_better, weight
) VALUES
('print_performance', 'pages_per_minute_color', 'Color pages printed per minute', 'numeric', 'ppm', true, 1.0),
('print_performance', 'pages_per_minute_mono', 'Monochrome pages printed per minute', 'numeric', 'ppm', true, 1.0),
('print_quality', 'max_resolution', 'Maximum print resolution', 'numeric', 'dpi', true, 0.8),
('connectivity', 'wifi_standard', 'WiFi standard supported', 'text', '', true, 0.9),
('connectivity', 'ethernet_port', 'Ethernet connectivity available', 'boolean', '', true, 0.7),
('paper_handling', 'input_capacity', 'Standard input tray capacity', 'numeric', 'sheets', true, 0.8),
('paper_handling', 'duplex_printing', 'Automatic duplex printing support', 'boolean', '', true, 0.9),
('physical', 'weight', 'Device weight', 'numeric', 'kg', false, 0.5),
('physical', 'dimensions', 'Device dimensions (WxDxH)', 'text', 'mm', false, 0.3);

-- Add features for HP OfficeJet Pro 9025
INSERT INTO public.product_features (
  product_id, feature_id, feature_value, verified, source
)
SELECT 
  p.id,
  cf.id,
  CASE cf.feature_name
    WHEN 'pages_per_minute_color' THEN '{"value": 22, "verified": true}'::jsonb
    WHEN 'pages_per_minute_mono' THEN '{"value": 24, "verified": true}'::jsonb
    WHEN 'max_resolution' THEN '{"value": 4800, "unit": "dpi", "verified": true}'::jsonb
    WHEN 'wifi_standard' THEN '{"value": "802.11ac", "verified": true}'::jsonb
    WHEN 'ethernet_port' THEN '{"value": true, "verified": true}'::jsonb
    WHEN 'input_capacity' THEN '{"value": 250, "verified": true}'::jsonb
    WHEN 'duplex_printing' THEN '{"value": true, "verified": true}'::jsonb
    WHEN 'weight' THEN '{"value": 22.2, "verified": true}'::jsonb
    WHEN 'dimensions' THEN '{"value": "521x386x306", "verified": true}'::jsonb
  END,
  true,
  'official_manual'
FROM public.products p, public.competitive_features cf
WHERE p.name = '9025' AND p.product_type = 'model'
  AND cf.feature_name IN (
    'pages_per_minute_color', 'pages_per_minute_mono', 'max_resolution',
    'wifi_standard', 'ethernet_port', 'input_capacity', 'duplex_printing',
    'weight', 'dimensions'
  );

-- =====================================
-- 11. VALIDATION TESTS
-- =====================================

-- Test 1: Validate option configuration (should fail due to conflicting bridges)
DO $$
DECLARE
    validation_result record;
    base_model_id uuid;
    finisher_x_id uuid;
    bridge_b_id uuid;
    test_options uuid[];
BEGIN
    -- Get IDs
    SELECT id INTO base_model_id FROM public.products WHERE name = '9025' AND product_type = 'model';
    SELECT id INTO finisher_x_id FROM public.products WHERE name = 'Finisher X' AND parent_id = base_model_id;
    SELECT id INTO bridge_b_id FROM public.products WHERE name = 'Bridge B' AND parent_id = base_model_id;
    
    -- Test invalid configuration (Finisher X + Bridge B should fail)
    test_options := ARRAY[finisher_x_id, bridge_b_id];
    
    SELECT * INTO validation_result FROM validate_option_configuration(base_model_id, test_options);
    
    RAISE NOTICE 'Validation Test 1 - Invalid Configuration:';
    RAISE NOTICE 'Is Valid: %', validation_result.is_valid;
    RAISE NOTICE 'Errors: %', validation_result.validation_errors;
    RAISE NOTICE 'Suggested Additions: %', validation_result.suggested_additions;
    RAISE NOTICE 'Suggested Removals: %', validation_result.suggested_removals;
END $$;

-- Test 2: Search function test
DO $$
DECLARE
    search_result record;
BEGIN
    RAISE NOTICE 'Search Test - Looking for error code C1234:';
    
    FOR search_result IN 
        SELECT * FROM comprehensive_search('C1234', NULL, NULL, NULL, 5)
    LOOP
        RAISE NOTICE 'Result Type: %, Title: %, Similarity: %', 
            search_result.result_type, 
            search_result.title, 
            search_result.similarity_score;
    END LOOP;
END $$;

-- Test 3: HP Documentation Set retrieval
DO $$
DECLARE
    doc_result record;
    model_id uuid;
BEGIN
    SELECT id INTO model_id FROM public.products WHERE name = '9025' AND product_type = 'model';
    
    RAISE NOTICE 'HP Documentation Set Test:';
    
    FOR doc_result IN 
        SELECT * FROM get_hp_documentation_set(model_id, 'C1234')
    LOOP
        RAISE NOTICE 'CPMD: %, Manual: %, Chunks: %, Error Codes: %',
            doc_result.cpmd_file_name,
            doc_result.service_manual_name,
            doc_result.related_chunks,
            doc_result.related_error_codes;
    END LOOP;
END $$;

-- =====================================
-- STEP 07 COMPLETE ✅
-- Database is fully populated and validated!
-- =====================================

-- Final validation query to show database structure
SELECT 
    'manufacturers' as table_name, COUNT(*) as row_count FROM public.manufacturers
UNION ALL SELECT 'products', COUNT(*) FROM public.products
UNION ALL SELECT 'documents', COUNT(*) FROM public.documents  
UNION ALL SELECT 'chunks', COUNT(*) FROM public.chunks
UNION ALL SELECT 'error_codes', COUNT(*) FROM public.error_codes
UNION ALL SELECT 'document_relationships', COUNT(*) FROM public.document_relationships
UNION ALL SELECT 'product_compatibility', COUNT(*) FROM public.product_compatibility
UNION ALL SELECT 'option_groups', COUNT(*) FROM public.option_groups
UNION ALL SELECT 'competitive_features', COUNT(*) FROM public.competitive_features
UNION ALL SELECT 'product_features', COUNT(*) FROM public.product_features
ORDER BY table_name;