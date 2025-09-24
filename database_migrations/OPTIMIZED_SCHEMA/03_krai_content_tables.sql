-- =====================================
-- KRAI ENGINE - CONTENT SCHEMA
-- Media Content: Images, Videos, Print Quality Analysis
-- =====================================

-- =====================================
-- 1. IMAGES TABLE (Schematics & Diagrams)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_content.images (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Source References
  document_id uuid NOT NULL REFERENCES krai_core.documents(id) ON DELETE CASCADE,
  chunk_id uuid REFERENCES krai_intelligence.chunks(id),  -- Associated text chunk (optional)
  
  -- File Information
  storage_path text NOT NULL,                   -- R2/S3 storage path
  storage_url text,                             -- Public access URL
  file_hash text NOT NULL,                      -- Deduplication hash
  original_filename text,                       -- "diagram_01.png"
  
  -- Image Properties
  width integer,                                -- Image width in pixels
  height integer,                               -- Image height in pixels
  file_size_bytes bigint,                       -- File size
  image_format text,                            -- "png", "jpg", "svg"
  image_type text CHECK (image_type IN (
    'schematic',                               -- Technical diagrams
    'diagram',                                 -- Flow charts, process diagrams
    'screenshot',                              -- Software screenshots
    'photo',                                   -- Physical device photos
    'chart',                                   -- Data charts, graphs
    'defect_image'                             -- Print quality defect photos
  )),
  
  -- Document Context
  page_number integer,                          -- Source page in document
  page_position text,                           -- "top", "bottom", "center"
  
  -- AI Analysis Results
  ai_description text,                          -- "Diagram showing paper path in printer"
  detected_objects jsonb,                       -- AI-detected objects and labels
  extracted_text text,                          -- OCR text from image
  
  -- Part Number Detection
  related_part_numbers text[],                  -- ["CB435A", "CE285A"] if detected
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional image data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for images
CREATE INDEX IF NOT EXISTS idx_images_document_id ON krai_content.images(document_id);
CREATE INDEX IF NOT EXISTS idx_images_chunk_id ON krai_content.images(chunk_id) WHERE chunk_id IS NOT NULL;
CREATE INDEX IF NOT EXISTS idx_images_type ON krai_content.images(image_type);
CREATE INDEX IF NOT EXISTS idx_images_file_hash ON krai_content.images(file_hash);
CREATE INDEX IF NOT EXISTS idx_images_part_numbers_gin ON krai_content.images USING GIN (related_part_numbers);
CREATE INDEX IF NOT EXISTS idx_images_description_fts ON krai_content.images USING GIN (to_tsvector('english', ai_description));
CREATE INDEX IF NOT EXISTS idx_images_detected_objects_gin ON krai_content.images USING GIN (detected_objects);

COMMENT ON TABLE krai_content.images IS 'Images, schematics, diagrams, and photos from documents';
COMMENT ON COLUMN krai_content.images.image_type IS 'Classification of image content: schematic, diagram, screenshot, photo, chart, defect_image';

-- =====================================
-- 2. INSTRUCTIONAL VIDEOS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_content.instructional_videos (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Video Source
  manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  product_ids uuid[],                           -- Related products
  
  -- Video Information
  title text NOT NULL,                          -- "HP 9025 Toner Replacement"
  description text,                             -- Detailed video description
  video_url text NOT NULL,                      -- YouTube/Vimeo/Direct URL
  thumbnail_url text,                           -- Video thumbnail image
  duration_seconds integer,                     -- Video length
  
  -- Content Classification
  language text DEFAULT 'en',                   -- Video language
  video_type text CHECK (video_type IN (
    'repair',                                  -- Repair procedures
    'maintenance',                             -- Maintenance tasks
    'installation',                            -- Installation guides
    'troubleshooting',                         -- Troubleshooting steps
    'overview'                                 -- Product overviews
  )),
  
  -- Related Content
  related_part_numbers text[],                  -- Parts shown in video
  related_error_codes text[],                   -- Error codes addressed
  
  -- Video Properties
  is_official boolean DEFAULT true,             -- Official manufacturer video
  view_count integer DEFAULT 0,                 -- View statistics
  rating_average numeric(3,2) DEFAULT 0.0,      -- Average rating
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional video data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for instructional videos
CREATE INDEX IF NOT EXISTS idx_videos_manufacturer_type ON krai_content.instructional_videos(manufacturer_id, video_type);
CREATE INDEX IF NOT EXISTS idx_videos_product_ids_gin ON krai_content.instructional_videos USING GIN (product_ids);
CREATE INDEX IF NOT EXISTS idx_videos_part_numbers_gin ON krai_content.instructional_videos USING GIN (related_part_numbers);
CREATE INDEX IF NOT EXISTS idx_videos_error_codes_gin ON krai_content.instructional_videos USING GIN (related_error_codes);
CREATE INDEX IF NOT EXISTS idx_videos_title_search ON krai_content.instructional_videos USING GIN (title gin_trgm_ops);
CREATE INDEX IF NOT EXISTS idx_videos_official ON krai_content.instructional_videos(is_official) WHERE is_official = true;

COMMENT ON TABLE krai_content.instructional_videos IS 'Instructional videos for repair, maintenance, and troubleshooting';
COMMENT ON COLUMN krai_content.instructional_videos.video_type IS 'Type of instructional content: repair, maintenance, installation, troubleshooting, overview';

-- =====================================
-- 3. PRINT DEFECTS TABLE
-- =====================================

CREATE TABLE IF NOT EXISTS krai_content.print_defects (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Image Information
  original_image_id uuid REFERENCES krai_content.images(id) ON DELETE CASCADE,
  processed_image_url text,                     -- AI-processed image with annotations
  thumbnail_url text,                           -- Small preview image
  
  -- Upload Context
  technician_id uuid,                           -- Who uploaded the image
  manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  product_id uuid REFERENCES krai_core.products(id),
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
  
  -- Quality Assessment
  quality_rating integer CHECK (quality_rating BETWEEN 1 AND 5), -- 1=Poor, 5=Excellent
  is_acceptable boolean,                        -- Acceptable quality level
  
  -- Resolution Tracking
  resolution_status text CHECK (resolution_status IN ('unresolved', 'in_progress', 'resolved', 'escalated')),
  resolution_notes text,                        -- How it was resolved
  resolved_by uuid,                             -- Who resolved it
  resolved_at timestamp with time zone,
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional defect data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for print defects
CREATE INDEX IF NOT EXISTS idx_print_defects_image_id ON krai_content.print_defects(original_image_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_manufacturer ON krai_content.print_defects(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_product ON krai_content.print_defects(product_id);
CREATE INDEX IF NOT EXISTS idx_print_defects_category ON krai_content.print_defects(defect_category);
CREATE INDEX IF NOT EXISTS idx_print_defects_severity ON krai_content.print_defects(severity_level);
CREATE INDEX IF NOT EXISTS idx_print_defects_confidence ON krai_content.print_defects(confidence_score) WHERE confidence_score >= 0.8;
CREATE INDEX IF NOT EXISTS idx_print_defects_resolution ON krai_content.print_defects(resolution_status);
CREATE INDEX IF NOT EXISTS idx_print_defects_quality ON krai_content.print_defects(quality_rating);

COMMENT ON TABLE krai_content.print_defects IS 'AI-powered print defect analysis and quality assessment';
COMMENT ON COLUMN krai_content.print_defects.defect_category IS 'Classification of print quality defects';
COMMENT ON COLUMN krai_content.print_defects.confidence_score IS 'AI confidence in defect detection (0.0-1.0)';

-- =====================================
-- 4. DEFECT PATTERNS TABLE (AI Training Data)
-- =====================================

CREATE TABLE IF NOT EXISTS krai_content.defect_patterns (
  id uuid PRIMARY KEY DEFAULT uuid_generate_v4(),
  
  -- Pattern Definition
  pattern_name text NOT NULL,                   -- "Banding_Pattern_001"
  defect_category text NOT NULL REFERENCES krai_content.print_defects(defect_category),
  manufacturer_id uuid REFERENCES krai_core.manufacturers(id),
  
  -- Training Data
  training_images uuid[],                       -- Array of print_defect IDs used for training
  pattern_description text,                     -- Description of the defect pattern
  visual_characteristics text[],                -- ["horizontal_lines", "regular_spacing", "light_toner"]
  
  -- AI Model Information
  model_version text,                           -- AI model version that learned this pattern
  training_accuracy numeric(4,3),               -- Training accuracy for this pattern
  validation_accuracy numeric(4,3),             -- Validation accuracy
  
  -- Pattern Metadata
  frequency_rating integer CHECK (frequency_rating BETWEEN 1 AND 10), -- How common this pattern is
  severity_typical text CHECK (severity_typical IN ('minor', 'moderate', 'severe', 'critical')),
  
  -- Usage Statistics
  detection_count integer DEFAULT 0,            -- How many times this pattern was detected
  false_positive_count integer DEFAULT 0,       -- False positive detections
  false_negative_count integer DEFAULT 0,       -- Missed detections
  
  -- Flexible Metadata
  metadata jsonb DEFAULT '{}'::jsonb,           -- Additional pattern data
  
  -- Timestamps
  created_at timestamp with time zone DEFAULT now(),
  updated_at timestamp with time zone DEFAULT now()
);

-- Indexes for defect patterns
CREATE INDEX IF NOT EXISTS idx_defect_patterns_category ON krai_content.defect_patterns(defect_category);
CREATE INDEX IF NOT EXISTS idx_defect_patterns_manufacturer ON krai_content.defect_patterns(manufacturer_id);
CREATE INDEX IF NOT EXISTS idx_defect_patterns_training_images_gin ON krai_content.defect_patterns USING GIN (training_images);
CREATE INDEX IF NOT EXISTS idx_defect_patterns_accuracy ON krai_content.defect_patterns(training_accuracy) WHERE training_accuracy >= 0.9;
CREATE INDEX IF NOT EXISTS idx_defect_patterns_frequency ON krai_content.defect_patterns(frequency_rating);

COMMENT ON TABLE krai_content.defect_patterns IS 'AI training patterns for print defect detection and classification';
COMMENT ON COLUMN krai_content.defect_patterns.pattern_name IS 'Unique identifier for the defect pattern';

-- =====================================
-- 5. TRIGGERS FOR UPDATED_AT
-- =====================================

-- Apply triggers to tables with updated_at
CREATE TRIGGER update_images_updated_at BEFORE UPDATE ON krai_content.images FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_videos_updated_at BEFORE UPDATE ON krai_content.instructional_videos FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_print_defects_updated_at BEFORE UPDATE ON krai_content.print_defects FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();
CREATE TRIGGER update_defect_patterns_updated_at BEFORE UPDATE ON krai_content.defect_patterns FOR EACH ROW EXECUTE FUNCTION krai_core.update_updated_at_column();

-- =====================================
-- 6. UTILITY FUNCTIONS
-- =====================================

-- Function: Get images for specific part numbers
CREATE OR REPLACE FUNCTION krai_content.get_images_for_part_numbers(part_numbers text[])
RETURNS TABLE (
  image_id uuid,
  image_url text,
  image_type text,
  part_numbers text[],
  ai_description text
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    i.id,
    i.storage_url,
    i.image_type,
    i.related_part_numbers,
    i.ai_description
  FROM krai_content.images i
  WHERE i.related_part_numbers && part_numbers  -- Array overlap operator
  ORDER BY i.created_at DESC;
END;
$$ LANGUAGE plpgsql;

-- Function: Get defect patterns for category
CREATE OR REPLACE FUNCTION krai_content.get_defect_patterns_by_category(category text)
RETURNS TABLE (
  pattern_id uuid,
  pattern_name text,
  training_accuracy numeric,
  detection_count integer,
  severity_typical text
) AS $$
BEGIN
  RETURN QUERY
  SELECT 
    dp.id,
    dp.pattern_name,
    dp.training_accuracy,
    dp.detection_count,
    dp.severity_typical
  FROM krai_content.defect_patterns dp
  WHERE dp.defect_category = category
  ORDER BY dp.training_accuracy DESC, dp.detection_count DESC;
END;
$$ LANGUAGE plpgsql;

COMMENT ON SCHEMA krai_content IS 'Media content, images, videos, and print quality analysis';
