-- =====================================
-- KRAI ENGINE - CONFIG SCHEMA
-- Configuration & Rules: Compatibility, Options, Features
-- =====================================

-- =====================================
-- 1. PRODUCT COMPATIBILITY TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_config.product_compatibility (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Compatibility Definition
  base_product_id uuid NOT NULL REFERENCES krai_core.products(id),
  option_product_id uuid NOT NULL REFERENCES krai_core.products(id),
  is_compatible boolean DEFAULT true,            -- Compatibility status
  
  -- Compatibility Details
  compatibility_notes text,                     -- Installation notes
  installation_notes text,                      -- Step-by-step instructions
  
  -- Firmware Requirements
  min_firmware_version text,                    -- Required firmware minimum
  max_firmware_version text,                    -- Firmware maximum (if incompatible)
  
  -- Regional Restrictions
  region_restrictions text[],                   -- ["US", "EU"] regional limitations
  
  -- Complex Dependencies
  mutually_exclusive_options uuid[],            -- Options that cannot coexist
  performance_impact jsonb,                     -- {"print_speed_reduction": "10%"}
  
  -- Rule Configuration
  option_rules jsonb DEFAULT '{}'::jsonb,       -- Complex dependency rules
  rule_priority integer DEFAULT 5,              -- Rule evaluation priority (1-10)
  validation_notes text,                        -- Additional validation info
  
  -- Verification
  verified_date timestamp with time zone,       -- Last verification
  verified_by uuid,                             -- Who verified this compatibility
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(base_product_id, option_product_id)    -- One compatibility rule per pair
);

-- Indexes for product compatibility
CREATE INDEX IF NOT EXISTS idx_compatibility_base ON krai_config.product_compatibility(base_product_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_option ON krai_config.product_compatibility(option_product_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_verified ON krai_config.product_compatibility(is_compatible, verified_date);
CREATE INDEX IF NOT EXISTS idx_compatibility_priority ON krai_config.product_compatibility(rule_priority);
CREATE INDEX IF NOT EXISTS idx_compatibility_mutually_exclusive_gin ON krai_config.product_compatibility USING GIN (mutually_exclusive_options);
CREATE INDEX IF NOT EXISTS idx_compatibility_region_gin ON krai_config.product_compatibility USING GIN (region_restrictions);

COMMENT ON TABLE krai_config.product_compatibility IS 'Product option compatibility matrix with complex dependency rules';
COMMENT ON COLUMN krai_config.product_compatibility.rule_priority IS 'Rule evaluation priority: 1=highest, 10=lowest';

-- =====================================
-- 2. OPTION GROUPS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_config.option_groups (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Group Definition
  manufacturer_id uuid NOT NULL REFERENCES krai_core.manufacturers(id),
  group_name text NOT NULL,                     -- "Finisher Group", "Bridge Group"
  group_type text CHECK (group_type IN (
    'exclusive',                               -- Only one option allowed
    'required_set',                            -- All options required
    'max_limit'                               -- Maximum number of selections
  )),
  
  -- Group Rules
  max_selections integer,                       -- Maximum options from group
  min_selections integer DEFAULT 0,            -- Minimum required selections
  option_product_ids uuid[],                   -- Array of option IDs in group
  
  -- Group Information
  description text,                             -- Group purpose description
  technical_reason text,                        -- "Physical space constraints"
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(manufacturer_id, group_name)           -- Unique group names per manufacturer
);

-- Indexes for option groups
CREATE INDEX IF NOT EXISTS idx_option_groups_manufacturer ON krai_config.option_groups(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_option_groups_type ON krai_config.option_groups(group_type);
CREATE INDEX IF NOT EXISTS idx_option_groups_options_gin ON krai_config.option_groups USING GIN (option_product_ids);

COMMENT ON TABLE krai_config.option_groups IS 'Option grouping rules for mutual exclusion and dependencies';
COMMENT ON COLUMN krai_config.option_groups.group_type IS 'Group behavior: exclusive, required_set, max_limit';

-- =====================================
-- 3. COMPETITIVE FEATURES TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_config.competitive_features (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Feature Definition
  feature_category text NOT NULL,               -- "print_speed", "connectivity", "paper_handling"
  feature_name text NOT NULL,                   -- "pages_per_minute", "wifi_6", "duplex_scanning"
  feature_description text,                     -- "Color pages printed per minute"
  
  -- Data Type & Units
  data_type text CHECK (data_type IN ('numeric', 'boolean', 'text', 'array')),
  unit text,                                    -- "ppm", "MB", "sheets", "inches"
  
  -- Scoring Configuration
  higher_is_better boolean DEFAULT true,        -- Scoring direction
  weight numeric DEFAULT 1.0,                   -- Importance weight for scoring
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(feature_category, feature_name)        -- No duplicate features
);

-- Indexes for competitive features
CREATE INDEX IF NOT EXISTS idx_competitive_features_category ON krai_config.competitive_features(feature_category);
CREATE INDEX IF NOT EXISTS idx_competitive_features_name ON krai_config.competitive_features(feature_name);
CREATE INDEX IF NOT EXISTS idx_competitive_features_weight ON krai_config.competitive_features(weight) WHERE weight > 1.0;

COMMENT ON TABLE krai_config.competitive_features IS 'Feature definitions for competitive product analysis';
COMMENT ON COLUMN krai_config.competitive_features.weight IS 'Importance weight for competitive scoring';

-- =====================================
-- 4. PRODUCT FEATURES TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_config.product_features (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Product & Feature References
  product_id uuid NOT NULL REFERENCES krai_core.products(id) ON DELETE CASCADE,
  feature_id uuid NOT NULL REFERENCES krai_config.competitive_features(id) ON DELETE CASCADE,
  
  -- Feature Value
  feature_value jsonb NOT NULL,                 -- {"value": 22, "verified": true}
  verified boolean DEFAULT false,               -- Officially verified
  source text,                                  -- "official_manual", "third_party_test"
  
  -- Verification
  last_verified timestamp with time zone,       -- Verification timestamp
  verified_by uuid,                             -- Who verified this value
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(product_id, feature_id)                -- One value per product per feature
);

-- Indexes for product features
CREATE INDEX IF NOT EXISTS idx_product_features_product ON krai_config.product_features(product_id);
CREATE INDEX IF NOT EXISTS idx_product_features_feature ON krai_config.product_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_product_features_verified ON krai_config.product_features(verified) WHERE verified = true;
CREATE INDEX IF NOT EXISTS idx_product_features_value_gin ON krai_config.product_features USING GIN (feature_value);

COMMENT ON TABLE krai_config.product_features IS 'Product feature values for competitive comparison';
COMMENT ON COLUMN krai_config.product_features.feature_value IS 'JSON value with actual feature data and metadata';

-- =====================================
-- 5. TRIGGERS FOR UPDATED_AT
-- =====================================

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_compatibility_updated_at BEFORE UPDATE ON krai_config.product_compatibility FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_option_groups_updated_at BEFORE UPDATE ON krai_config.option_groups FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_competitive_features_updated_at BEFORE UPDATE ON krai_config.competitive_features FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_product_features_updated_at BEFORE UPDATE ON krai_config.product_features FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();

-- =====================================
-- 6. VALIDATION FUNCTIONS
-- =====================================

-- Function: Validate option configuration
CREATE OR REPLACE FUNCTION krai_config.validate_option_configuration(
  base_model_id uuid,
  selected_options uuid[]
)
RETURNS TABLE (
  is_valid boolean,
  validation_errors text[],
  suggested_additions uuid[],
  suggested_removals uuid[]
) AS $$
DECLARE
  errors text[] := '{}';
  additions uuid[] := '{}';
  removals uuid[] := '{}';
  option_record record;
  group_record record;
  exclusive_violations uuid[] := '{}';
BEGIN
  -- Check each selected option for compatibility
  FOR option_record IN 
    SELECT pc.*, p.name as option_name
    FROM krai_config.product_compatibility pc
    JOIN krai_core.products p ON p.id = pc.option_product_id
    WHERE pc.base_product_id = base_model_id
      AND pc.option_product_id = ANY(selected_options)
  LOOP
    -- Check compatibility
    IF NOT option_record.is_compatible THEN
      errors := array_append(errors, 
        'Option "' || option_record.option_name || '" is not compatible with this model');
      removals := array_append(removals, option_record.option_product_id);
    END IF;
    
    -- Check mutually exclusive options
    IF option_record.mutually_exclusive_options && selected_options THEN
      exclusive_violations := option_record.mutually_exclusive_options & selected_options;
      errors := array_append(errors, 
        'Option "' || option_record.option_name || '" conflicts with mutually exclusive options');
      removals := array_cat(removals, exclusive_violations);
    END IF;
  END LOOP;
  
  -- Check option group rules
  FOR group_record IN
    SELECT og.*
    FROM krai_config.option_groups og
    WHERE og.option_product_ids && selected_options
  LOOP
    -- Count selected options in this group
    DECLARE
      selected_in_group uuid[] := og.option_product_ids & selected_options;
      group_count integer := array_length(selected_in_group, 1);
    BEGIN
      -- Check group type rules
      CASE group_record.group_type
        WHEN 'exclusive' THEN
          IF group_count > 1 THEN
            errors := array_append(errors, 
              'Group "' || group_record.group_name || '" allows only one option');
            removals := array_cat(removals, selected_in_group[2:]);
          END IF;
          
        WHEN 'required_set' THEN
          IF group_count < array_length(group_record.option_product_ids, 1) THEN
            errors := array_append(errors, 
              'Group "' || group_record.group_name || '" requires all options');
            additions := array_cat(additions, 
              group_record.option_product_ids - selected_options);
          END IF;
          
        WHEN 'max_limit' THEN
          IF group_record.max_selections IS NOT NULL AND group_count > group_record.max_selections THEN
            errors := array_append(errors, 
              'Group "' || group_record.group_name || '" allows maximum ' || 
              group_record.max_selections || ' options');
            removals := array_cat(removals, selected_in_group[(group_record.max_selections+1):]);
          END IF;
      END CASE;
    END;
  END LOOP;
  
  -- Return validation results
  is_valid := (array_length(errors, 1) IS NULL OR array_length(errors, 1) = 0);
  validation_errors := errors;
  suggested_additions := array_remove(additions, NULL);
  suggested_removals := array_remove(removals, NULL);
  
  RETURN NEXT;
END;
$$ LANGUAGE plpgsql;

-- Function: Get compatible options for a model
CREATE OR REPLACE FUNCTION krai_config.get_compatible_options(model_id uuid)
RETURNS TABLE (
  option_id uuid,
  option_name text,
  option_category text,
  is_compatible boolean,
  installation_notes text
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    pc.option_product_id,
    p.name,
    p.option_category,
    pc.is_compatible,
    pc.installation_notes
  FROM krai_config.product_compatibility pc
  JOIN krai_core.products p ON p.id = pc.option_product_id
  WHERE pc.base_product_id = model_id
    AND p.product_type = 'option'
    AND p.is_active = true
  ORDER BY pc.is_compatible DESC, p.name;
END;
$$ LANGUAGE plpgsql;

-- Function: Compare products by features
CREATE OR REPLACE FUNCTION krai_config.compare_products_by_features(
  product_ids uuid[],
  feature_category_filter text DEFAULT NULL
)
RETURNS TABLE (
  product_id uuid,
  product_name text,
  feature_name text,
  feature_value jsonb,
  feature_unit text,
  higher_is_better boolean
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    pf.product_id,
    p.display_name,
    cf.feature_name,
    pf.feature_value,
    cf.unit,
    cf.higher_is_better
  FROM krai_config.product_features pf
  JOIN krai_core.products p ON p.id = pf.product_id
  JOIN krai_config.competitive_features cf ON cf.id = pf.feature_id
  WHERE pf.product_id = ANY(product_ids)
    AND (feature_category_filter IS NULL OR cf.feature_category = feature_category_filter)
    AND pf.verified = true
  ORDER BY cf.feature_category, cf.feature_name, p.display_name;
END;
$$ LANGUAGE plpgsql;

COMMENT ON SCHEMA krai_config IS 'Configuration, business rules, and product feature definitions';
