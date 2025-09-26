-- =====================================
-- KRAI ENGINE - FUTURE EXTENSIONS
-- Optional Tables for Advanced Features
-- =====================================

-- =====================================
-- 1. USER MANAGEMENT SCHEMA (Optional)
-- =====================================

CREATE SCHEMA IF NOT EXISTS krai_users;
COMMENT ON SCHEMA krai_users IS 'User management and authentication';

-- Users table
CREATE TABLE IF NOT EXISTS krai_users.users (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Basic Information
  email text NOT NULL UNIQUE,
  username text NOT NULL UNIQUE,
  display_name text,
  
  -- Authentication
  password_hash text,  -- If using local auth
  auth_provider text DEFAULT 'supabase',  -- 'supabase', 'ldap', 'oauth'
  external_user_id text,  -- Supabase user ID
  
  -- Profile Information
  role text DEFAULT 'technician' CHECK (role IN ('admin', 'analyst', 'technician', 'viewer')),
  department text,
  location text,
  
  -- Preferences
  preferred_manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  preferred_language text DEFAULT 'en',
  timezone text DEFAULT 'UTC',
  
  -- Status
  is_active boolean DEFAULT true,
  last_login_at timestamp with time zone,
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- User sessions
CREATE TABLE IF NOT EXISTS krai_users.user_sessions (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  user_id uuid NOT NULL REFERENCES krai_users.users(id) ON DELETE CASCADE,
  session_token text NOT NULL UNIQUE,
  ip_address inet,
  user_agent text,
  expires_at timestamp with time zone NOT NULL,
  created_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 2. SERVICE MANAGEMENT SCHEMA (Optional)
-- =====================================

CREATE SCHEMA IF NOT EXISTS krai_service;
COMMENT ON SCHEMA krai_service IS 'Service calls, tickets, and customer interactions';

-- Service calls
CREATE TABLE IF NOT EXISTS krai_service.service_calls (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Call Information
  call_number text NOT NULL UNIQUE,  -- "SC-2024-001"
  customer_name text,
  customer_contact text,
  
  -- Equipment
  manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  product_id uuid REFERENCES krai_core.products(id),
  serial_number text,
  
  -- Issue Details
  issue_description text,
  error_codes text[],  -- Related error codes
  priority text CHECK (priority IN ('low', 'medium', 'high', 'critical')),
  
  -- Status
  status text CHECK (status IN ('open', 'in_progress', 'resolved', 'closed')) DEFAULT 'open',
  assigned_technician_id uuid REFERENCES krai_users.users(id),
  
  -- Timestamps
  reported_at timestamp with time zone DEFAULT now(),
  resolved_at timestamp with time zone,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Service call history
CREATE TABLE IF NOT EXISTS krai_service.service_history (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  service_call_id uuid NOT NULL REFERENCES krai_service.service_calls(id) ON DELETE CASCADE,
  
  -- Action Details
  action_type text CHECK (action_type IN ('created', 'updated', 'assigned', 'resolved', 'closed')),
  description text,
  performed_by uuid REFERENCES krai_users.users(id),
  
  -- Resolution Data
  resolution_notes text,
  parts_used text[],
  time_spent_minutes integer,
  
  -- Timestamps
  performed_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 3. PARTS MANAGEMENT SCHEMA (Optional)
-- =====================================

CREATE SCHEMA IF NOT EXISTS krai_parts;
COMMENT ON SCHEMA krai_parts IS 'Parts catalog, inventory, and suppliers';

-- Parts catalog
CREATE TABLE IF NOT EXISTS krai_parts.parts_catalog (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Part Information
  part_number text NOT NULL,
  manufacturer_id uuid NOT NULL REFERENCES krai_core.manufacturers(id),
  
  -- Part Details
  description text,
  category text,  -- 'toner', 'drum', 'fuser', 'paper_tray', etc.
  compatible_products uuid[],  -- Array of product IDs
  
  -- Pricing & Availability
  list_price numeric(10,2),
  cost_price numeric(10,2),
  supplier_id uuid,  -- FK to suppliers table (if created)
  
  -- Status
  is_active boolean DEFAULT true,
  is_obsolete boolean DEFAULT false,
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(part_number, manufacturer_id)
);

-- Inventory levels
CREATE TABLE IF NOT EXISTS krai_parts.inventory_levels (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  part_id uuid NOT NULL REFERENCES krai_parts.parts_catalog(id) ON DELETE CASCADE,
  
  -- Inventory Data
  current_stock integer DEFAULT 0,
  minimum_stock integer DEFAULT 0,
  maximum_stock integer,
  location text,
  
  -- Last Updated
  last_counted_at timestamp with time zone,
  last_updated_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 4. AI/ML MODEL MANAGEMENT SCHEMA (Optional)
-- =====================================

CREATE SCHEMA IF NOT EXISTS krai_ml;
COMMENT ON SCHEMA krai_ml IS 'AI/ML model management and performance tracking';

-- AI Models
CREATE TABLE IF NOT EXISTS krai_ml.ai_models (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Model Information
  model_name text NOT NULL,
  model_type text CHECK (model_type IN ('embedding', 'classification', 'detection', 'generation')),
  version text NOT NULL,
  
  -- Model Details
  description text,
  model_path text,  -- Path to model file
  model_size_mb integer,
  
  -- Performance Metrics
  accuracy numeric(5,4),  -- 0.0000 to 1.0000
  precision_score numeric(5,4),
  recall_score numeric(5,4),
  f1_score numeric(5,4),
  
  -- Training Data
  training_dataset_size integer,
  training_completed_at timestamp with time zone,
  
  -- Status
  is_active boolean DEFAULT false,
  is_production boolean DEFAULT false,
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  
  -- Constraints
  UNIQUE(model_name, version)
);

-- Model Performance History
CREATE TABLE IF NOT EXISTS krai_ml.model_performance_history (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  model_id uuid NOT NULL REFERENCES krai_ml.ai_models(id) ON DELETE CASCADE,
  
  -- Performance Data
  metric_name text NOT NULL,
  metric_value numeric,
  dataset_type text CHECK (dataset_type IN ('training', 'validation', 'test', 'production')),
  
  -- Context
  evaluation_date timestamp with time zone DEFAULT now(),
  sample_size integer,
  
  -- Additional Data
  metadata jsonb DEFAULT '{}'::jsonb
);

-- =====================================
-- 5. API & INTEGRATIONS SCHEMA (Optional)
-- =====================================

CREATE SCHEMA IF NOT EXISTS krai_integrations;
COMMENT ON SCHEMA krai_integrations IS 'External API integrations and webhook management';

-- API Endpoints
CREATE TABLE IF NOT EXISTS krai_integrations.api_endpoints (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Endpoint Information
  name text NOT NULL,
  url text NOT NULL,
  method text CHECK (method IN ('GET', 'POST', 'PUT', 'DELETE', 'PATCH')),
  
  -- Authentication
  auth_type text CHECK (auth_type IN ('none', 'api_key', 'oauth', 'basic')),
  auth_config jsonb DEFAULT '{}'::jsonb,
  
  -- Configuration
  timeout_seconds integer DEFAULT 30,
  retry_attempts integer DEFAULT 3,
  rate_limit_per_minute integer,
  
  -- Status
  is_active boolean DEFAULT true,
  last_tested_at timestamp with time zone,
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Webhook Logs
CREATE TABLE IF NOT EXISTS krai_integrations.webhook_logs (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Webhook Information
  webhook_name text NOT NULL,
  endpoint_url text NOT NULL,
  
  -- Request/Response Data
  request_headers jsonb,
  request_body text,
  response_status_code integer,
  response_body text,
  response_time_ms integer,
  
  -- Status
  success boolean,
  error_message text,
  
  -- Timestamps
  triggered_at timestamp with time zone DEFAULT now()
);

-- =====================================
-- 6. EXTENSION SCHEMA PERMISSIONS
-- =====================================

-- Grant permissions to service role
GRANT ALL ON ALL SCHEMAS IN DATABASE TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_users TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_service TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_parts TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_ml TO krai_service_role;
GRANT ALL ON ALL TABLES IN SCHEMA krai_integrations TO krai_service_role;

-- Grant limited permissions to admin role
GRANT USAGE ON SCHEMA krai_users, krai_service, krai_parts TO krai_admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA krai_users TO krai_admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA krai_service TO krai_admin_role;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA krai_parts TO krai_admin_role;

-- Grant read-only permissions to analyst role
GRANT USAGE ON SCHEMA krai_ml, krai_integrations TO krai_analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_ml TO krai_analyst_role;
GRANT SELECT ON ALL TABLES IN SCHEMA krai_integrations TO krai_analyst_role;

-- =====================================
-- 7. EXTENSION COMMENTS
-- =====================================

COMMENT ON SCHEMA krai_users IS 'User management and authentication (Optional Extension)';
COMMENT ON SCHEMA krai_service IS 'Service calls and customer interactions (Optional Extension)';
COMMENT ON SCHEMA krai_parts IS 'Parts catalog and inventory management (Optional Extension)';
COMMENT ON SCHEMA krai_ml IS 'AI/ML model management and performance tracking (Optional Extension)';
COMMENT ON SCHEMA krai_integrations IS 'External API integrations and webhooks (Optional Extension)';

-- =====================================
-- 8. EXTENSION USAGE NOTES
-- =====================================

-- These schemas are OPTIONAL and can be added later as needed
-- They extend the core functionality without breaking existing features
-- Each schema can be implemented independently based on business requirements

-- Usage Examples:
-- 1. Add user management when multi-tenant support is needed
-- 2. Add service management when customer support integration is required  
-- 3. Add parts management when inventory tracking is needed
-- 4. Add ML management when AI model versioning is required
-- 5. Add integrations when external API management is needed
