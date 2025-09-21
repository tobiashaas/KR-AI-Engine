-- KRAI Database Complete Schema Export
-- Generated: 2025-09-21T14:55:50.160Z
-- Source: https://nxzqpobjklqhqkqrvvvl.supabase.co
-- Status: Production-optimized with indexes

-- =====================================
-- EXTENSIONS & SCHEMA SETUP
-- =====================================

CREATE SCHEMA IF NOT EXISTS extensions;

-- Install required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;

-- Enable Row Level Security (will be configured separately)
-- Enable realtime if needed
-- SELECT cron.schedule('cleanup-old-logs', '0 2 * * *', 'DELETE FROM processing_logs WHERE created_at < NOW() - INTERVAL ''30 days'';');

-- =====================================
-- TABLE CREATION (from working schema)
-- =====================================

-- Batch 1: create_extensions_and_tables.sql
-- Extensions, schemas and core tables. Do NOT run index CONCURRENTLY here.

CREATE SCHEMA IF NOT EXISTS extensions;

-- Extensions installed into extensions schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp" SCHEMA extensions;
CREATE EXTENSION IF NOT EXISTS vector SCHEMA extensions;

-- Manufacturers / OEMs
CREATE TABLE IF NOT EXISTS public.manufacturers (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  name text NOT NULL UNIQUE,
  display_name text,
  website text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Documents (one row per uploaded file/pdf)
CREATE TABLE IF NOT EXISTS public.documents (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  file_name text NOT NULL,
  file_hash text NOT NULL UNIQUE,
  storage_path text NOT NULL,
  size_bytes bigint NOT NULL,
  total_pages integer NOT NULL,
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  model text,
  model_series text,
  processing_status text NOT NULL DEFAULT 'pending',
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Chunks (one row per semantic/text chunk)
CREATE TABLE IF NOT EXISTS public.chunks (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid NOT NULL REFERENCES public.documents(id) ON DELETE CASCADE,
  chunk_index integer NOT NULL,
  page_start integer,
  page_end integer,
  text_chunk text NOT NULL,
  token_count integer,
  fingerprint text NOT NULL,
  embedding vector(768),
  ocr_confidence numeric,
  chunk_quality_score numeric DEFAULT 0.0,
  processing_status text NOT NULL DEFAULT 'pending',
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE (document_id, chunk_index, fingerprint)
);

-- Service manuals (denormalized quick-access view table for manuals metadata)
CREATE TABLE IF NOT EXISTS public.service_manuals (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  model text,
  model_series text,
  file_hash text,
  processing_status text NOT NULL DEFAULT 'pending',
  embedding vector(768),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Parts catalog entries (catalog per document, but searchable)
CREATE TABLE IF NOT EXISTS public.parts_catalog_entries (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  part_number text NOT NULL,
  part_name text,
  description text,
  attributes jsonb DEFAULT '{}'::jsonb,
  embedding vector(768),
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now(),
  UNIQUE (document_id, part_number)
);

-- Bulletins (safety/service bulletins)
CREATE TABLE IF NOT EXISTS public.bulletins (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  title text NOT NULL,
  summary text,
  content text,
  embedding vector(768),
  priority_level integer DEFAULT 0,
  effective_date timestamp with time zone,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Images (stored in object storage; we keep metadata and optional embeddings)
CREATE TABLE IF NOT EXISTS public.images (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  storage_path text NOT NULL,
  file_hash text NOT NULL,
  width integer,
  height integer,
  embedding vector(768),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Vision analysis results (detections, labels, scores)
CREATE TABLE IF NOT EXISTS public.vision_analysis_results (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  image_id uuid REFERENCES public.images(id) ON DELETE CASCADE,
  detector_name text,
  labels jsonb,
  embedding vector(768),
  confidence numeric,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Technician chat memory / session context (short-lived conversation storage)
CREATE TABLE IF NOT EXISTS public.chat_sessions (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  session_id text NOT NULL,
  user_id uuid,
  created_at timestamp with time zone DEFAULT now(),
  last_interaction_at timestamp with time zone DEFAULT now()
);

CREATE TABLE IF NOT EXISTS public.chat_messages (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  session_id uuid REFERENCES public.chat_sessions(id) ON DELETE CASCADE,
  role text NOT NULL,
  content text NOT NULL,
  tokens integer,
  embedding vector(768),
  created_at timestamp with time zone DEFAULT now()
);

-- Processing logs (ingest/worker logs)
CREATE TABLE IF NOT EXISTS public.processing_logs (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  document_id uuid REFERENCES public.documents(id) ON DELETE CASCADE,
  component text,
  message text,
  status text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Product models table
CREATE TABLE IF NOT EXISTS public.product_models (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  manufacturer_id uuid REFERENCES public.manufacturers(id),
  model text,
  model_series text,
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Quality defect patterns (text and image embeddings)
CREATE TABLE IF NOT EXISTS public.quality_defect_patterns (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  name text NOT NULL,
  description text,
  embedding vector(768),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now()
);

-- Parts model compatibility mapping
CREATE TABLE IF NOT EXISTS public.parts_model_compatibility (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  part_id uuid REFERENCES public.parts_catalog_entries(id) ON DELETE CASCADE,
  model_id uuid REFERENCES public.product_models(id) ON DELETE CASCADE,
  notes text,
  created_at timestamp with time zone DEFAULT now()
);

-- Company internal docs (sensitive, service-only)
CREATE TABLE IF NOT EXISTS public.company_internal_docs (
  id uuid PRIMARY KEY DEFAULT extensions.uuid_generate_v4(),
  title text,
  content text,
  embedding vector(768),
  metadata jsonb DEFAULT '{}'::jsonb,
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Ensure RLS will be enabled later for these tables (Batch 2)

-- End of Batch 1

