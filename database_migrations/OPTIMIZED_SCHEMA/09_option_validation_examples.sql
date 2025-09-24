-- =====================================
-- KRAI ENGINE - OPTION VALIDATION EXAMPLES
-- Real-World Complex Option Dependencies
-- =====================================

-- =====================================
-- 1. HP 9025 COMPLEX OPTION SCENARIOS
-- =====================================

-- Example: HP 9025 with Bridge A + Finisher X (VALID)
-- This should work: Bridge A supports Finisher X
INSERT INTO krai_config.product_compatibility (
    base_product_id, 
    option_product_id, 
    is_compatible,
    installation_notes,
    mutually_exclusive_options
) VALUES 
-- Bridge A is compatible with HP 9025
('660e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440003', true, 
 'Bridge A provides additional paper handling capabilities', 
 ARRAY['660e8400-e29b-41d4-a716-446655440004']::uuid[]),  -- Conflicts with Bridge B

-- Bridge B is compatible with HP 9025  
('660e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440004', true,
 'Bridge B provides advanced finishing capabilities',
 ARRAY['660e8400-e29b-41d4-a716-446655440003']::uuid[]),  -- Conflicts with Bridge A

-- Finisher X is compatible with HP 9025 (requires Bridge A)
('660e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440005', true,
 'Finisher X requires Bridge A for proper paper path',
 ARRAY[]::uuid[]),

-- Finisher Y is compatible with HP 9025 (requires Bridge B)
('660e8400-e29b-41d4-a716-446655440002', '660e8400-e29b-41d4-a716-446655440006', true,
 'Finisher Y requires Bridge B for proper paper path',
 ARRAY[]::uuid[]);

-- Option Groups for mutual exclusion
INSERT INTO krai_config.option_groups (
    manufacturer_id,
    group_name,
    group_type,
    max_selections,
    min_selections,
    option_product_ids,
    description,
    technical_reason
) VALUES 
-- Bridge Group: Only one bridge allowed (physical space)
('550e8400-e29b-41d4-a716-446655440001', 'Bridge Group', 'exclusive', 1, 0,
 ARRAY['660e8400-e29b-41d4-a716-446655440003', '660e8400-e29b-41d4-a716-446655440004']::uuid[],
 'Bridge selection for HP 9025',
 'Physical space constraints allow only one bridge unit'),

-- Finisher Group: Multiple finishers possible but with dependencies
('550e8400-e29b-41d4-a716-446655440001', 'Finisher Group', 'max_limit', 2, 0,
 ARRAY['660e8400-e29b-41d4-a716-446655440005', '660e8400-e29b-41d4-a716-446655440006']::uuid[],
 'Finisher options for HP 9025',
 'Multiple finishers supported with proper bridge configuration');

-- =====================================
-- 2. COMPLEX DEPENDENCY RULES
-- =====================================

-- Create a function to handle complex option dependencies
CREATE OR REPLACE FUNCTION krai_config.check_option_dependencies(
    base_model_id uuid,
    selected_options uuid[]
)
RETURNS TABLE (
    dependency_rule text,
    is_satisfied boolean,
    missing_options uuid[],
    conflicting_options uuid[]
) AS $$
DECLARE
    option_record record;
    bridge_a_id uuid := '660e8400-e29b-41d4-a716-446655440003';
    bridge_b_id uuid := '660e8400-e29b-41d4-a716-446655440004';
    finisher_x_id uuid := '660e8400-e29b-41d4-a716-446655440005';
    finisher_y_id uuid := '660e8400-e29b-41d4-a716-446655440006';
BEGIN
    -- Rule 1: Finisher X requires Bridge A
    IF finisher_x_id = ANY(selected_options) AND bridge_a_id != ANY(selected_options) THEN
        dependency_rule := 'Finisher X requires Bridge A';
        is_satisfied := false;
        missing_options := ARRAY[bridge_a_id];
        conflicting_options := ARRAY[]::uuid[];
        RETURN NEXT;
    END IF;
    
    -- Rule 2: Finisher Y requires Bridge B
    IF finisher_y_id = ANY(selected_options) AND bridge_b_id != ANY(selected_options) THEN
        dependency_rule := 'Finisher Y requires Bridge B';
        is_satisfied := false;
        missing_options := ARRAY[bridge_b_id];
        conflicting_options := ARRAY[]::uuid[];
        RETURN NEXT;
    END IF;
    
    -- Rule 3: Bridge A and Bridge B are mutually exclusive
    IF bridge_a_id = ANY(selected_options) AND bridge_b_id = ANY(selected_options) THEN
        dependency_rule := 'Bridge A and Bridge B are mutually exclusive';
        is_satisfied := false;
        missing_options := ARRAY[]::uuid[];
        conflicting_options := ARRAY[bridge_a_id, bridge_b_id];
        RETURN NEXT;
    END IF;
    
    -- Rule 4: Finisher X and Finisher Y with wrong bridge combinations
    IF finisher_x_id = ANY(selected_options) AND bridge_b_id = ANY(selected_options) THEN
        dependency_rule := 'Finisher X cannot work with Bridge B';
        is_satisfied := false;
        missing_options := ARRAY[]::uuid[];
        conflicting_options := ARRAY[finisher_x_id, bridge_b_id];
        RETURN NEXT;
    END IF;
    
    IF finisher_y_id = ANY(selected_options) AND bridge_a_id = ANY(selected_options) THEN
        dependency_rule := 'Finisher Y cannot work with Bridge A';
        is_satisfied := false;
        missing_options := ARRAY[]::uuid[];
        conflicting_options := ARRAY[finisher_y_id, bridge_a_id];
        RETURN NEXT;
    END IF;
    
    -- If we get here, all dependencies are satisfied
    dependency_rule := 'All dependencies satisfied';
    is_satisfied := true;
    missing_options := ARRAY[]::uuid[];
    conflicting_options := ARRAY[]::uuid[];
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 3. AI AGENT QUERY EXAMPLES
-- =====================================

-- Example 1: AI Agent asks "What options are available for HP 9025?"
CREATE OR REPLACE FUNCTION krai_config.ai_get_available_options(model_id uuid)
RETURNS TABLE (
    option_id uuid,
    option_name text,
    option_category text,
    is_compatible boolean,
    dependencies text[],
    conflicts_with text[],
    installation_notes text
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        pc.option_product_id,
        p.display_name,
        p.option_category,
        pc.is_compatible,
        CASE 
            WHEN p.name = 'Finisher X' THEN ARRAY['Requires Bridge A']
            WHEN p.name = 'Finisher Y' THEN ARRAY['Requires Bridge B']
            ELSE ARRAY[]::text[]
        END as dependencies,
        CASE 
            WHEN p.name = 'Bridge A' THEN ARRAY['Conflicts with Bridge B']
            WHEN p.name = 'Bridge B' THEN ARRAY['Conflicts with Bridge A']
            ELSE ARRAY[]::text[]
        END as conflicts_with,
        pc.installation_notes
    FROM krai_config.product_compatibility pc
    JOIN krai_core.products p ON p.id = pc.option_product_id
    WHERE pc.base_product_id = model_id
      AND p.product_type = 'option'
      AND p.is_active = true
    ORDER BY p.option_category, p.display_name;
END;
$$ LANGUAGE plpgsql;

-- Example 2: AI Agent validates configuration "Bridge A + Finisher X"
CREATE OR REPLACE FUNCTION krai_config.ai_validate_configuration(
    model_id uuid,
    option_names text[]
)
RETURNS TABLE (
    configuration_valid boolean,
    validation_summary text,
    errors text[],
    warnings text[],
    suggestions text[]
) AS $$
DECLARE
    option_ids uuid[];
    validation_result record;
    error_messages text[] := '{}';
    warning_messages text[] := '{}';
    suggestion_messages text[] := '{}';
BEGIN
    -- Convert option names to IDs
    SELECT array_agg(p.id) INTO option_ids
    FROM krai_core.products p
    WHERE p.name = ANY(option_names)
      AND p.product_type = 'option';
    
    -- Validate the configuration
    SELECT * INTO validation_result
    FROM krai_config.optimized_validate_option_configuration(model_id, option_ids);
    
    -- Check dependencies
    FOR validation_result IN 
        SELECT * FROM krai_config.check_option_dependencies(model_id, option_ids)
    LOOP
        IF NOT validation_result.is_satisfied THEN
            error_messages := array_append(error_messages, validation_result.dependency_rule);
        END IF;
    END LOOP;
    
    -- Generate suggestions based on validation results
    IF NOT validation_result.is_valid THEN
        suggestion_messages := array_append(suggestion_messages, 
            'Try removing conflicting options or adding required dependencies');
    END IF;
    
    -- Return comprehensive validation result
    configuration_valid := validation_result.is_valid AND array_length(error_messages, 1) IS NULL;
    validation_summary := CASE 
        WHEN configuration_valid THEN 'Configuration is valid and ready for installation'
        ELSE 'Configuration has issues that need to be resolved'
    END;
    errors := array_cat(validation_result.validation_errors, error_messages);
    warnings := warning_messages;
    suggestions := suggestion_messages;
    
    RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- =====================================
-- 4. TEST SCENARIOS
-- =====================================

-- Test Scenario 1: Valid configuration - Bridge A + Finisher X
-- Expected: VALID
/*
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model
    ARRAY['Bridge A', 'Finisher X']
);
*/

-- Test Scenario 2: Invalid configuration - Bridge A + Finisher Y  
-- Expected: INVALID (Finisher Y requires Bridge B)
/*
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model
    ARRAY['Bridge A', 'Finisher Y']
);
*/

-- Test Scenario 3: Invalid configuration - Bridge A + Bridge B
-- Expected: INVALID (Mutually exclusive)
/*
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model
    ARRAY['Bridge A', 'Bridge B']
);
*/

-- Test Scenario 4: Get available options for HP 9025
-- Expected: List of all compatible options with dependencies
/*
SELECT * FROM krai_config.ai_get_available_options(
    '660e8400-e29b-41d4-a716-446655440002'  -- HP 9025 Model
);
*/

-- =====================================
-- 5. COMMENTS AND DOCUMENTATION
-- =====================================

COMMENT ON FUNCTION krai_config.check_option_dependencies IS 'Validates complex option dependencies for printer configurations';
COMMENT ON FUNCTION krai_config.ai_get_available_options IS 'AI-friendly function to get available options with dependency information';
COMMENT ON FUNCTION krai_config.ai_validate_configuration IS 'AI-friendly function to validate option configurations with detailed feedback';
