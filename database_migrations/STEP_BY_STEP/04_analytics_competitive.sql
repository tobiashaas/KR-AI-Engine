-- =====================================
-- KRAI ENGINE - STEP 04: ANALYTICS & COMPETITIVE TABLES
-- Search Analytics + Competitive Features + Product Features
-- =====================================

-- =====================================
-- 1. SEARCH ANALYTICS (Performance & Usage Tracking)
-- =====================================

CREATE TABLE IF NOT EXISTS public.search_analytics (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- User & Session Information
  session_id text,                              -- Frontend session identifier
  user_id uuid,                                 -- Supabase user ID (optional)
  
  -- Search Query Information
  query_text text NOT NULL,                     -- User search query
  query_intent text,                            -- "error_lookup", "part_search", "manual_search"
  search_type text CHECK (search_type IN ('semantic', 'exact', 'fuzzy', 'comprehensive')),
  
  -- Applied Filters
  manufacturer_filter uuid REFERENCES public.manufacturers(id),
  product_filter uuid REFERENCES public.products(id),
  document_type_filter text,                    -- Applied document type filter
  
  -- Search Results
  results_count integer,                        -- Number of results returned
  top_result_similarity numeric,                -- Best match similarity score
  response_time_ms integer,                     -- Performance metric
  
  -- User Engagement
  user_clicked_result boolean DEFAULT false,    -- User engagement
  clicked_result_rank integer,                  -- Position of clicked result
  user_feedback_rating integer CHECK (user_feedback_rating BETWEEN 1 AND 5), -- User satisfaction rating
  was_helpful boolean,                          -- Overall helpfulness
  
  -- Timestamps
  search_timestamp timestamp with time zone DEFAULT now(),
  created_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 2. COMPETITIVE FEATURES (Feature Definitions)
-- =====================================

CREATE TABLE IF NOT EXISTS public.competitive_features (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Feature Definition
  feature_category text NOT NULL,               -- "print_speed", "connectivity", "paper_handling"
  feature_name text NOT NULL,                   -- "pages_per_minute", "wifi_6", "duplex_scanning"
  feature_description text,                     -- "Color pages printed per minute"
  
  -- Data Type & Validation
  data_type text NOT NULL CHECK (data_type IN ('numeric', 'boolean', 'text', 'array')),
  unit text,                                    -- "ppm", "MB", "sheets", "inches"
  
  -- Comparison Logic
  higher_is_better boolean DEFAULT true,        -- For scoring: true for speed, false for price
  weight numeric DEFAULT 1.0,                  -- Importance weight for overall scoring
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(feature_category, feature_name)        -- No duplicate features
);

-- =====================================
-- 3. PRODUCT FEATURES (Feature Values for Comparison)
-- =====================================

CREATE TABLE IF NOT EXISTS public.product_features (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Product & Feature Reference
  product_id uuid NOT NULL REFERENCES public.products(id) ON DELETE CASCADE,
  feature_id uuid NOT NULL REFERENCES public.competitive_features(id) ON DELETE CASCADE,
  
  -- Feature Value
  feature_value jsonb NOT NULL,                 -- {"value": 22, "verified": true, "source": "official_spec"}
  
  -- Metadata
  verified boolean DEFAULT false,               -- Officially verified specification
  source text,                                  -- "official_manual", "third_party_test", "user_report"
  last_verified timestamp with time zone,
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(product_id, feature_id)                -- One value per product per feature
);

-- =====================================
-- 4. INDEXES FOR ANALYTICS & COMPETITIVE TABLES
-- =====================================

-- Search Analytics Indexes
CREATE INDEX IF NOT EXISTS idx_search_analytics_timestamp ON public.search_analytics(search_timestamp);
CREATE INDEX IF NOT EXISTS idx_search_analytics_session ON public.search_analytics(session_id);
CREATE INDEX IF NOT EXISTS idx_search_analytics_performance ON public.search_analytics(search_type, response_time_ms);
CREATE INDEX IF NOT EXISTS idx_search_analytics_successful ON public.search_analytics(was_helpful) WHERE was_helpful = true;
CREATE INDEX IF NOT EXISTS idx_search_analytics_manufacturer ON public.search_analytics(manufacturer_filter) WHERE manufacturer_filter IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_search_analytics_query_fts ON public.search_analytics USING gin(to_tsvector('english', query_text));

-- Competitive Features Indexes
CREATE INDEX IF NOT EXISTS idx_competitive_features_category ON public.competitive_features(feature_category);
CREATE INDEX IF NOT EXISTS idx_competitive_features_name ON public.competitive_features(feature_name);

-- Product Features Indexes
CREATE INDEX IF NOT EXISTS idx_product_features_product ON public.product_features(product_id);
CREATE INDEX IF NOT EXISTS idx_product_features_feature ON public.product_features(feature_id);
CREATE INDEX IF NOT EXISTS idx_product_features_verified ON public.product_features(verified) WHERE verified = true;
CREATE INDEX IF NOT EXISTS idx_product_features_value_gin ON public.product_features USING gin(feature_value);

-- =====================================
-- STEP 04 COMPLETE ✅
-- Next: Run Step 05 for Core Functions & Triggers
-- =====================================