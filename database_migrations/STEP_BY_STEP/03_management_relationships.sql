-- =====================================
-- KRAI ENGINE - STEP 03: MANAGEMENT & RELATIONSHIP TABLES
-- Document Relationships + Product Compatibility + Option Groups + Processing Queue
-- =====================================

-- =====================================
-- 1. DOCUMENT RELATIONSHIPS (HP CPMD + Manual Pairing)
-- =====================================

CREATE TABLE IF NOT EXISTS public.document_relationships (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Document Pairing
  primary_document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  secondary_document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  
  -- Relationship Type
  relationship_type text NOT NULL CHECK (relationship_type IN (
    'cpmd_manual_pair',    -- HP: CPMD Database + Service Manual
    'supersedes',          -- New version replaces old
    'supplements',         -- Additional information
    'translation',         -- Same document, different language
    'series_manual'        -- Manual covers multiple models in series
  )),
  
  -- Relationship Details
  description text,
  priority_order integer DEFAULT 1, -- 1 = primary, 2 = secondary for display order
  
  -- Metadata
  created_at timestamp with time zone DEFAULT now(),
  
  -- Prevent self-references and duplicates
  CHECK (primary_document_id != secondary_document_id),
  UNIQUE(primary_document_id, secondary_document_id, relationship_type)
);

-- =====================================
-- 2. PRODUCT COMPATIBILITY (Model + Option Matrix)
-- =====================================

CREATE TABLE IF NOT EXISTS public.product_compatibility (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Product Relationship
  base_product_id uuid NOT NULL REFERENCES public.products(id),
  option_product_id uuid NOT NULL REFERENCES public.products(id),
  
  -- Compatibility Status
  is_compatible boolean DEFAULT true,           -- Compatibility status
  compatibility_notes text,                     -- Installation notes
  installation_notes text,                      -- Step-by-step instructions
  
  -- Technical Requirements
  min_firmware_version text,                    -- Required firmware minimum
  max_firmware_version text,                    -- Firmware maximum (if incompatible)
  region_restrictions text[],                   -- ["US", "EU"] regional limitations
  mutually_exclusive_options uuid[],            -- Options that cannot coexist
  performance_impact jsonb,                     -- {"print_speed_reduction": "10%"}
  
  -- Complex Rules (NEW)
  option_rules jsonb DEFAULT '{}'::jsonb,       -- Complex dependency rules
  rule_priority integer DEFAULT 5,              -- Rule evaluation priority
  validation_notes text,                        -- Additional validation info
  verified_date timestamp with time zone,       -- Last verification
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(base_product_id, option_product_id)    -- One compatibility rule per pair
);

-- =====================================
-- 3. OPTION GROUPS (Mutual Exclusions, Required Sets)
-- =====================================

CREATE TABLE IF NOT EXISTS public.option_groups (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Group Ownership
  manufacturer_id uuid NOT NULL REFERENCES public.manufacturers(id),
  
  -- Group Definition
  group_name text NOT NULL,                     -- "Finisher Group", "Bridge Group"
  group_type text NOT NULL CHECK (group_type IN ('exclusive', 'required_set', 'max_limit')),
  
  -- Group Rules
  max_selections integer,                       -- Max options from this group (NULL = unlimited)
  min_selections integer DEFAULT 0,             -- Min required selections
  
  -- Members of this group
  option_product_ids uuid[],                    -- Array of option IDs in this group
  
  -- Rule Description
  description text,                             -- "Only one finisher can be installed"
  technical_reason text,                        -- "Physical space constraints in rear assembly"
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(manufacturer_id, group_name)           -- Unique group names per manufacturer
);

-- =====================================
-- 4. PROCESSING QUEUE (Async Background Tasks)
-- =====================================

CREATE TABLE IF NOT EXISTS public.processing_queue (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Task Definition
  task_type text NOT NULL CHECK (task_type IN (
    'pdf_extraction',
    'embedding_generation',
    'video_processing',
    'document_indexing',
    'cpmd_parsing',
    'relationship_mapping'
  )),
  
  -- Task Targets (Optional - depends on task type)
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  chunk_id uuid REFERENCES public.chunks(id) ON DELETE CASCADE,
  video_id uuid REFERENCES public.instructional_videos(id) ON DELETE CASCADE,
  
  -- Task Status
  status text NOT NULL DEFAULT 'pending' CHECK (status IN ('pending', 'processing', 'completed', 'failed', 'retry')),
  priority integer NOT NULL CHECK (priority BETWEEN 1 AND 10), -- 1=highest, 10=lowest
  
  -- Retry Logic
  attempts integer DEFAULT 0,                   -- Retry attempts
  max_attempts integer DEFAULT 3,               -- Maximum retries
  error_message text,                           -- Failure details
  
  -- Timing
  processing_started_at timestamp with time zone,
  processing_completed_at timestamp with time zone,
  
  -- Task Configuration
  task_metadata jsonb DEFAULT '{}'::jsonb,      -- Task-specific parameters
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 5. INDEXES FOR MANAGEMENT & RELATIONSHIP TABLES
-- =====================================

-- Document Relationships Indexes
CREATE INDEX IF NOT EXISTS idx_doc_relationships_primary ON public.document_relationships(primary_document_id);
CREATE INDEX IF NOT EXISTS idx_doc_relationships_secondary ON public.document_relationships(secondary_document_id);
CREATE INDEX IF NOT EXISTS idx_doc_relationships_type ON public.document_relationships(relationship_type);

-- Product Compatibility Indexes
CREATE INDEX IF NOT EXISTS idx_compatibility_base ON public.product_compatibility(base_product_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_option ON public.product_compatibility(option_product_id);
CREATE INDEX IF NOT EXISTS idx_compatibility_verified ON public.product_compatibility(is_compatible, verified_date);
CREATE INDEX IF NOT EXISTS idx_compatibility_rules_gin ON public.product_compatibility USING gin(option_rules);

-- Option Groups Indexes
CREATE INDEX IF NOT EXISTS idx_option_groups_manufacturer ON public.option_groups(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_option_groups_type ON public.option_groups(group_type);
CREATE INDEX IF NOT EXISTS idx_option_groups_options_gin ON public.option_groups USING gin(option_product_ids);

-- Processing Queue Indexes
CREATE INDEX IF NOT EXISTS idx_queue_status_priority ON public.processing_queue(status, priority DESC, created_at);
CREATE INDEX IF NOT EXISTS idx_queue_task_type ON public.processing_queue(task_type);
CREATE INDEX IF NOT EXISTS idx_queue_document ON public.processing_queue(document_id) WHERE document_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_queue_pending ON public.processing_queue(created_at) WHERE status = 'pending';

-- =====================================
-- STEP 03 COMPLETE ✅
-- Next: Run Step 04 for Analytics & Competitive Tables
-- =====================================