-- =====================================
-- KRAI ENGINE - STEP 08: PRINT QUALITY ANALYSIS
-- AI-Powered Print Defect Detection & Training System
-- =====================================

-- =====================================
-- 1. PRINT DEFECTS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS public.print_defects (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Image Information
  original_image_id uuid REFERENCES public.images(id) ON DELETE CASCADE,
  processed_image_url text,                     -- AI-processed image with annotations
  thumbnail_url text,                           -- Small preview image
  
  -- Upload Context
  technician_id uuid,                           -- Who uploaded the image
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  product_id uuid REFERENCES public.products(id),
  service_call_id uuid,                         -- External service call reference
  
  -- Defect Classification
  defect_category text NOT NULL CHECK (defect_category IN (
    'banding',                                  -- Horizontal/vertical bands
    'streaking',                               -- Streaks or lines
    'color_issues',                            -- Color deviation/mixing
    'registration',                            -- Misalignment issues
    'density_variation',                       -- Light/dark areas
    'contamination',                           -- Spots, dirt, debris
    'mechanical_defects',                      -- Physical damage patterns
    'paper_handling',                          -- Wrinkles, jams, feeding issues
    'toner_issues',                           -- Low toner, toner scatter
    'fuser_problems',                         -- Heat/pressure related
    'multiple_defects',                       -- Complex issues
    'quality_check'                           -- Overall quality assessment
  )),
  
  -- AI Analysis Results
  confidence_score numeric(4,3) CHECK (confidence_score >= 0.0 AND confidence_score <= 1.0),
  ai_model_version text,                        -- Model used for detection
  detection_boxes jsonb,                        -- Bounding boxes for defects
  severity_level text CHECK (severity_level IN ('minor', 'moderate', 'severe', 'critical')),
  
  -- Defect Details
  defect_description text,                      -- AI-generated description
  affected_area_percentage numeric(5,2),        -- % of page affected
  probable_causes text[],                       -- AI-suggested causes
  recommended_actions text[],                   -- AI-suggested solutions
  
  -- Human Validation
  technician_confirmed boolean DEFAULT NULL,    -- Human validation of AI results
  technician_notes text,                        -- Additional technician input
  actual_cause text,                            -- Confirmed root cause
  resolution_applied text,                      -- What fix was applied
  resolution_successful boolean,                -- Did the fix work?
  
  -- Print Sample Information
  print_settings jsonb,                         -- DPI, color mode, paper type, etc.
  page_number integer,                          -- Which page in the document
  test_pattern_used text,                       -- Standard test pattern name
  before_after text CHECK (before_after IN ('before', 'after', 'comparison')),
  
  -- Quality Metrics
  overall_quality_score numeric(3,2),          -- 0.0 to 5.0 scale
  color_accuracy_score numeric(3,2),           -- Color deviation metrics
  sharpness_score numeric(3,2),                -- Edge definition quality
  uniformity_score numeric(3,2),               -- Consistency across page
  
  -- Learning & Training
  training_sample boolean DEFAULT false,        -- Use for AI training
  expert_verified boolean DEFAULT false,        -- Quality control check
  training_weight numeric(3,2) DEFAULT 1.0,    -- Importance for training
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  resolved_at timestamp with time zone,         -- When issue was fixed
  
  -- Metadata
  metadata jsonb DEFAULT '{}'::jsonb            -- Additional defect data
);

-- =====================================
-- 2. DEFECT PATTERNS TABLE (AI Training Data)
-- =====================================

CREATE TABLE IF NOT EXISTS public.defect_patterns (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Pattern Identity
  pattern_name text NOT NULL,                   -- "horizontal_banding_laser", "color_shift_inkjet"
  pattern_category text NOT NULL,               -- Same categories as print_defects
  
  -- Visual Characteristics
  visual_signature jsonb NOT NULL,              -- Feature vectors, histograms, etc.
  typical_causes text[] NOT NULL,               -- Known root causes
  fix_procedures text[] NOT NULL,               -- Standard repair procedures
  
  -- Pattern Classification
  manufacturer_specific uuid REFERENCES public.manufacturers(id),  -- NULL = universal
  product_line_specific text,                   -- "laser", "inkjet", "solid_ink"
  complexity_level text CHECK (complexity_level IN ('simple', 'moderate', 'complex', 'expert')),
  
  -- AI Training Data
  training_samples_count integer DEFAULT 0,     -- How many samples used to learn this
  accuracy_rate numeric(4,3),                  -- How accurately we detect this
  false_positive_rate numeric(4,3),            -- How often we're wrong
  last_training_update timestamp with time zone,
  
  -- Pattern Metadata
  description text,                             -- Human-readable description
  example_images uuid[],                        -- Reference image IDs
  related_error_codes text[],                   -- Associated error codes
  severity_indicators jsonb,                    -- What makes it minor vs severe
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 3. QUALITY STANDARDS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS public.quality_standards (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Standard Identity
  standard_name text NOT NULL,                  -- "ISO_13660", "HP_Quality_Level_A"
  standard_version text,                        -- Version number
  manufacturer_id uuid REFERENCES public.manufacturers(id),  -- NULL = industry standard
  
  -- Quality Thresholds
  acceptable_quality_threshold numeric(3,2),    -- Minimum acceptable score
  excellent_quality_threshold numeric(3,2),     -- Score for excellent quality
  
  -- Defect Tolerances
  defect_tolerances jsonb NOT NULL,             -- Per-defect-type thresholds
  -- Example: {"banding": {"minor": 0.05, "severe": 0.20}, "color_shift": {"minor": 2.0, "severe": 5.0}}
  
  -- Test Conditions
  required_test_patterns text[],                -- Which test patterns to use
  print_settings_requirements jsonb,            -- Required print settings
  measurement_procedures text,                  -- How to measure quality
  
  -- Applicability
  applicable_product_types text[],              -- "laser", "inkjet", etc.
  applicable_paper_types text[],                -- "plain", "photo", "cardstock"
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(standard_name, manufacturer_id)
);

-- =====================================
-- 4. QUALITY ASSESSMENTS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS public.quality_assessments (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Assessment Context
  print_defect_id uuid REFERENCES public.print_defects(id) ON DELETE CASCADE,
  quality_standard_id uuid REFERENCES public.quality_standards(id),
  technician_id uuid,                           -- Who performed the assessment
  
  -- Assessment Results
  overall_grade text CHECK (overall_grade IN ('A', 'B', 'C', 'D', 'F')),
  numeric_score numeric(3,2),                   -- Numeric quality score
  pass_fail boolean,                            -- Meet minimum standards?
  
  -- Detailed Measurements
  measured_values jsonb,                        -- Actual measurements taken
  threshold_violations jsonb,                   -- Which thresholds were exceeded
  
  -- Assessment Notes
  assessment_notes text,                        -- Additional observations
  recommended_improvements text[],              -- Suggestions for improvement
  
  -- Timestamps
  assessed_at timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 5. TECHNICIAN FEEDBACK TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS public.technician_feedback (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Feedback Context
  print_defect_id uuid REFERENCES public.print_defects(id) ON DELETE CASCADE,
  technician_id uuid NOT NULL,
  
  -- AI Accuracy Feedback
  ai_classification_correct boolean,            -- Was the AI right?
  ai_severity_correct boolean,                  -- Was severity assessment right?
  ai_causes_helpful boolean,                    -- Were suggested causes useful?
  ai_solutions_helpful boolean,                 -- Were suggested fixes useful?
  
  -- Improvement Suggestions
  correct_classification text,                  -- What it should have been
  correct_severity text,                        -- What severity it should have been
  actual_root_cause text,                       -- Real cause of the problem
  successful_solution text,                     -- What actually fixed it
  
  -- Training Value
  should_use_for_training boolean DEFAULT true, -- Include in training data?
  training_priority text CHECK (training_priority IN ('low', 'medium', 'high', 'critical')),
  
  -- Feedback Quality
  feedback_quality text CHECK (feedback_quality IN ('poor', 'adequate', 'good', 'excellent')),
  feedback_notes text,                          -- Additional context
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 6. INDEXES FOR PERFORMANCE
-- =====================================

-- Print Defects Indexes
CREATE INDEX IF NOT EXISTS idx_print_defects_technician ON public.print_defects(technician_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_manufacturer ON public.print_defects(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_product ON public.print_defects(product_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_category ON public.print_defects(defect_category);
CREATE INDEX IF NOT EXISTS idx_print_defects_severity ON public.print_defects(severity_level);
CREATE INDEX IF NOT EXISTS idx_print_defects_confirmed ON public.print_defects(technician_confirmed) WHERE technician_confirmed IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_print_defects_training ON public.print_defects(training_sample) WHERE training_sample = true;
CREATE INDEX IF NOT EXISTS idx_print_defects_resolved ON public.print_defects(resolved_at) WHERE resolved_at IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_print_defects_quality_score ON public.print_defects(overall_quality_score) WHERE overall_quality_score IS NOT NULL;

-- Defect Patterns Indexes
CREATE INDEX IF NOT EXISTS idx_defect_patterns_category ON public.defect_patterns(pattern_category);
CREATE INDEX IF NOT EXISTS idx_defect_patterns_manufacturer ON public.defect_patterns(manufacturer_specific) WHERE manufacturer_specific IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_defect_patterns_accuracy ON public.defect_patterns(accuracy_rate) WHERE accuracy_rate IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_defect_patterns_name ON public.defect_patterns(pattern_name);

-- Quality Standards Indexes
CREATE INDEX IF NOT EXISTS idx_quality_standards_manufacturer ON public.quality_standards(manufacturer_id) WHERE manufacturer_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_quality_standards_name ON public.quality_standards(standard_name);

-- Quality Assessments Indexes
CREATE INDEX IF NOT EXISTS idx_quality_assessments_defect ON public.quality_assessments(print_defect_id);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_standard ON public.quality_assessments(quality_standard_id);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_grade ON public.quality_assessments(overall_grade);
CREATE INDEX IF NOT EXISTS idx_quality_assessments_pass_fail ON public.quality_assessments(pass_fail);

-- Technician Feedback Indexes
CREATE INDEX IF NOT EXISTS idx_technician_feedback_defect ON public.technician_feedback(print_defect_id);
CREATE INDEX IF NOT EXISTS idx_technician_feedback_technician ON public.technician_feedback(technician_id);
CREATE INDEX IF NOT EXISTS idx_technician_feedback_training ON public.technician_feedback(should_use_for_training) WHERE should_use_for_training = true;
CREATE INDEX IF NOT EXISTS idx_technician_feedback_priority ON public.technician_feedback(training_priority);

-- =====================================
-- 7. SAMPLE QUALITY STANDARDS
-- =====================================

-- Insert Industry Standard Quality Levels
INSERT INTO public.quality_standards (
  standard_name, 
  standard_version,
  manufacturer_id,
  acceptable_quality_threshold,
  excellent_quality_threshold,
  defect_tolerances,
  required_test_patterns,
  print_settings_requirements,
  measurement_procedures,
  applicable_product_types,
  applicable_paper_types
) VALUES 
(
  'ISO_13660_Commercial',
  '2020',
  NULL,  -- Industry standard
  3.0,   -- Acceptable quality score
  4.5,   -- Excellent quality score
  '{
    "banding": {"minor": 0.05, "moderate": 0.10, "severe": 0.20},
    "streaking": {"minor": 0.03, "moderate": 0.08, "severe": 0.15},
    "color_issues": {"minor": 2.0, "moderate": 4.0, "severe": 8.0},
    "registration": {"minor": 0.1, "moderate": 0.2, "severe": 0.4},
    "density_variation": {"minor": 0.05, "moderate": 0.10, "severe": 0.20}
  }'::jsonb,
  ARRAY['iso_test_chart', 'color_bar', 'resolution_test'],
  '{
    "resolution": "600x600",
    "color_mode": "cmyk",
    "paper_weight": "80gsm"
  }'::jsonb,
  'Visual inspection using calibrated monitor and measurement tools',
  ARRAY['laser', 'inkjet', 'solid_ink'],
  ARRAY['plain', 'coated', 'photo']
),
(
  'Basic_Office_Quality',
  '1.0',
  NULL,
  2.5,   -- Lower standards for basic office printing
  4.0,
  '{
    "banding": {"minor": 0.08, "moderate": 0.15, "severe": 0.25},
    "streaking": {"minor": 0.05, "moderate": 0.12, "severe": 0.20},
    "color_issues": {"minor": 3.0, "moderate": 6.0, "severe": 10.0},
    "registration": {"minor": 0.15, "moderate": 0.25, "severe": 0.5},
    "density_variation": {"minor": 0.08, "moderate": 0.15, "severe": 0.25}
  }'::jsonb,
  ARRAY['basic_test_page', 'text_quality'],
  '{
    "resolution": "300x300",
    "color_mode": "rgb",
    "paper_weight": "75gsm"
  }'::jsonb,
  'Basic visual inspection for office document quality',
  ARRAY['laser', 'inkjet'],
  ARRAY['plain', 'recycled']
);

-- =====================================
-- STEP 08 COMPLETE ✅
-- Next: Integrate with Python AI processing pipeline
-- =====================================