# 📊 KRAI ENGINE - COMPLETE DATABASE DOCUMENTATION

**Version**: 2.0 Final Optimized Schema  
**Date**: September 22, 2025  
**Status**: Production Ready  

---

## 🏗️ **DATABASE ARCHITECTURE OVERVIEW**

### **Core Philosophy:**
- **Performance over Complexity**: Optimized for AI agent speed and accuracy
- **Flexibility over Rigidity**: JSONB metadata for future extensibility  
- **Quality over Quantity**: Focus on essential features that work perfectly
- **Async over Sync**: Heavy operations run in background queue

### **Schema Structure:**
```
KRAI Knowledge Retrieval AI Engine
├── 🏭 Core Business (4 Tables)     → manufacturers, products, documents, chunks
├── ⚡ Performance (1 Table)        → embeddings (separate for speed)
├── 🔍 Intelligence (1 Table)       → error_codes (universal system)
├── 🎥 Content (2 Tables)           → images, instructional_videos
├── 📊 Analytics (1 Table)          → search_analytics
├── 🔧 Management (6 Tables)        → relationships, compatibility, groups, features, queue
└── 📈 Total: 16 Tables (optimized from 23 → 16)
```

---

## 📋 **COMPLETE TABLE INVENTORY**

### **🏭 1. CORE BUSINESS TABLES**

#### **`manufacturers`** → Hersteller & Wettbewerber
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique manufacturer ID |
| `name` | text | NOT NULL UNIQUE | "HP Inc.", "Canon Inc." |
| `display_name` | text | | "Hewlett Packard", "Canon" |
| `website` | text | | Official website URL |
| `support_url` | text | | Support/service URL |
| `is_competitor` | boolean | DEFAULT false | TRUE for competitive analysis |
| `metadata` | jsonb | DEFAULT '{}' | Flexible manufacturer data |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Indexes:**
- `idx_manufacturers_name` (UNIQUE)
- `idx_manufacturers_competitor` (WHERE is_competitor = true)
- `idx_manufacturers_metadata_gin` (GIN for JSONB search)

**Expected Rows**: 10-50 manufacturers  
**Growth Rate**: Slow (new manufacturers rarely added)

---

#### **`products`** → 3-Level Hierarchie (Series → Model → Option)
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique product ID |
| `manufacturer_id` | uuid | FK → manufacturers(id) | Parent manufacturer |
| `product_type` | text | CHECK (series/model/option) | Hierarchy level |
| `parent_id` | uuid | FK → products(id) | Hierarchy parent (NULL for series) |
| `name` | text | NOT NULL | "OfficeJet Pro", "9025", "Large Tray" |
| `display_name` | text | | "HP OfficeJet Pro 9025" |
| `model_number` | text | | "HP-OJP-9025" unique identifier |
| `year_introduced` | integer | | Product launch year |
| `year_discontinued` | integer | | End of life year |
| `is_active` | boolean | DEFAULT true | Currently available |
| `option_category` | text | | For options: 'tray', 'fax', 'scanner', 'finisher' |
| `compatibility_notes` | text | | Installation/compatibility notes |
| `installation_complexity` | text | CHECK (simple/standard/complex/professional) | Installation difficulty |
| `option_dependencies` | uuid[] | | Required options for this option |
| `device_category` | text[] | | ["printer", "scanner", "fax"] capabilities |
| `form_factor` | text | | "desktop", "workgroup", "production" |
| `technical_specs` | jsonb | DEFAULT '{}' | Flexible technical specifications |
| `metadata` | jsonb | DEFAULT '{}' | Additional product data |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Constraints:**
- `UNIQUE(manufacturer_id, product_type, name)` → No duplicate product names per type
- **Hierarchy Validation**: Series has no parent, Models have Series parent, Options have Model parent

**Indexes:**
- `idx_products_manufacturer_type` (manufacturer_id, product_type)
- `idx_products_3level_hierarchy` (manufacturer_id, product_type, parent_id)
- `idx_products_model_number` (model_number) WHERE model_number IS NOT NULL
- `idx_products_name_search` (GIN trigram for fuzzy search)
- `idx_products_specs_gin` (GIN for technical_specs JSONB)
- `idx_products_device_category_gin` (GIN for device_category array)
- `idx_products_option_category` (option_category) WHERE option_category IS NOT NULL
- `idx_products_active` (is_active) WHERE is_active = true
- `idx_products_option_dependencies_gin` (GIN for option_dependencies array)

**Expected Rows**: 5,000-20,000 products (Series: ~200, Models: ~2,000, Options: ~3,000)  
**Growth Rate**: Medium (new models monthly, options quarterly)

---

#### **`documents`** → Zentrale Dokumenten-Referenz
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique document ID |
| `file_name` | text | NOT NULL | "HP_9025_Service_Manual.pdf" |
| `file_hash` | text | NOT NULL UNIQUE | SHA256 hash for deduplication |
| `storage_path` | text | NOT NULL | R2/S3 storage path |
| `storage_url` | text | | Public access URL |
| `size_bytes` | bigint | | File size |
| `total_pages` | integer | | Page count (NULL for non-PDF) |
| `document_type` | text | CHECK (service_manual/parts_catalog/bulletins/cpmd_database/video_transcript) | Document category |
| `manufacturer_id` | uuid | FK → manufacturers(id) | Document owner |
| `product_ids` | uuid[] | | Array of related product IDs |
| `language` | text | DEFAULT 'en' | Document language |
| `translation_group_id` | uuid | | Group ID for same doc in different languages |
| `upload_date` | timestamptz | DEFAULT now() | When uploaded |
| `last_reviewed_date` | timestamptz | | Last manual review |
| `needs_review` | boolean | DEFAULT false | Requires manual review |
| `review_frequency_months` | integer | DEFAULT 12 | Review cycle |
| `processing_status` | text | CHECK (pending/processing/completed/failed) | Processing state |
| `processing_progress` | integer | CHECK (0-100) | Processing percentage |
| `source_system` | text | | 'cpmd_database', 'service_manual', etc. |
| `cpmd_version` | text | | HP CPMD version number |
| `related_video_id` | uuid | FK → instructional_videos(id) | Associated video |
| `metadata` | jsonb | DEFAULT '{}' | Document-specific metadata |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Indexes:**
- `idx_documents_file_hash` (UNIQUE file_hash)
- `idx_documents_manufacturer_type` (manufacturer_id, document_type)
- `idx_documents_product_ids_gin` (GIN for product_ids array)
- `idx_documents_processing_status` (processing_status)
- `idx_documents_language_type` (language, document_type)
- `idx_documents_review_needed` (needs_review) WHERE needs_review = true
- `idx_documents_filename_search` (GIN trigram for file_name)
- `idx_documents_metadata_gin` (GIN for metadata JSONB)
- `idx_documents_upload_date` (upload_date)
- `idx_documents_cpmd` (manufacturer_id, document_type) WHERE document_type = 'cpmd_database'
- `idx_documents_source_system` (source_system) WHERE source_system IS NOT NULL
- `idx_documents_video_relation` (related_video_id) WHERE related_video_id IS NOT NULL

**Expected Rows**: 10,000-100,000 documents  
**Growth Rate**: High (daily uploads during active ingestion periods)

---

#### **`chunks`** → Text-Content für AI Processing
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique chunk ID |
| `document_id` | uuid | FK → documents(id) CASCADE | Parent document |
| `chunk_index` | integer | NOT NULL | Position in document (0, 1, 2...) |
| `page_start` | integer | | Starting page number |
| `page_end` | integer | | Ending page number |
| `text_chunk` | text | NOT NULL | Extracted text content |
| `token_count` | integer | | Token count for AI limits |
| `fingerprint` | text | NOT NULL | Deduplication hash |
| `section_title` | text | | "Chapter 3: Troubleshooting" |
| `subsection_title` | text | | "3.1 Paper Jams" |
| `page_label` | text | | "Page 45", "Section 3.2.1" |
| `extracted_error_codes` | text[] | | ["C1234", "E-5678"] automatically detected |
| `normalized_error_codes` | text[] | | ["c1234", "e5678"] for fuzzy search |
| `extracted_part_numbers` | text[] | | ["CB435A", "CE285A"] automatically detected |
| `ocr_confidence` | numeric | | OCR quality (0.0-1.0) |
| `chunk_quality_score` | numeric | | AI-assessed content quality |
| `processing_status` | text | CHECK (pending/completed/failed) | Processing state |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Constraints:**
- `UNIQUE(document_id, chunk_index, fingerprint)` → Prevent duplicate chunks

**Indexes:**
- `idx_chunks_document_id` (document_id)
- `idx_chunks_document_index` (document_id, chunk_index)
- `idx_chunks_text_fts` (GIN full-text search on text_chunk - English)
- `idx_chunks_text_fts_german` (GIN full-text search on text_chunk - German)
- `idx_chunks_text_trigram` (GIN trigram for fuzzy search)
- `idx_chunks_error_codes_gin` (GIN for extracted_error_codes array)
- `idx_chunks_normalized_codes_gin` (GIN for normalized_error_codes array)
- `idx_chunks_part_numbers_gin` (GIN for extracted_part_numbers array)
- `idx_chunks_processing_status` (processing_status)
- `idx_chunks_quality` (chunk_quality_score) WHERE chunk_quality_score IS NOT NULL

**Expected Rows**: 1,000,000+ chunks (largest table)  
**Growth Rate**: Very High (100k+ chunks per large document ingestion)

---

### **⚡ 2. PERFORMANCE TABLE**

#### **`embeddings`** → Vector Embeddings (Separate for Performance)
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique embedding ID |
| `chunk_id` | uuid | FK → chunks(id) CASCADE | Source text chunk |
| `embedding` | vector(768) | | 768-dimensional vector |
| `model_name` | text | NOT NULL | "all-MiniLM-L6-v2", "multilingual-e5-base" |
| `model_version` | text | | "v1.0" for versioning |
| `embedding_quality_score` | numeric | | Quality assessment |
| `created_at` | timestamptz | DEFAULT now() | Generation timestamp |

**Constraints:**
- `UNIQUE(chunk_id, model_name)` → One embedding per chunk per model

**Indexes:**
- `idx_embeddings_chunk_id` (chunk_id)
- `idx_embeddings_model` (model_name)
- **HNSW Vector Index** (to be created after data ingestion): `CREATE INDEX embeddings_hnsw_idx ON embeddings USING hnsw (embedding vector_cosine_ops);`

**Expected Rows**: 1,000,000+ embeddings (1:1 with chunks)  
**Growth Rate**: Very High (matches chunk growth)  
**Storage Impact**: ~3KB per embedding (768 dimensions × 4 bytes)

---

### **🔍 3. INTELLIGENCE TABLE**

#### **`error_codes`** → Universal Error Code Database
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique error code ID |
| `manufacturer_id` | uuid | FK → manufacturers(id) | Error code owner |
| `document_id` | uuid | FK → documents(id) | Source document |
| `chunk_id` | uuid | FK → chunks(id) | Specific text location |
| `error_code` | text | NOT NULL | "C1234", "E-5678", original format |
| `normalized_code` | text | NOT NULL | "c1234", "e5678" for fuzzy search |
| `error_description` | text | NOT NULL | "Paper jam in input tray" |
| `solution_steps` | text | | Step-by-step solution |
| `affected_product_ids` | uuid[] | | Array of compatible product IDs |
| `device_categories` | text[] | | ["printer", "mfp"] broader applicability |
| `severity_level` | integer | CHECK (1-5) | 1=Critical, 5=Info |
| `frequency_score` | numeric | DEFAULT 0.0 | How often this error occurs (0-10) |
| `source_system` | text | CHECK (cpmd_database/service_manual/bulletin/field_report/video_content) | Error source |
| `video_timestamp_seconds` | integer | | Position in related video |
| `related_video_id` | uuid | FK → instructional_videos(id) | Associated video |
| `alternative_codes` | text[] | | ["C1234", "Error 1234", "Jam-01"] cross-reference |
| `metadata` | jsonb | DEFAULT '{}' | Additional troubleshooting data |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Constraints:**
- `UNIQUE(manufacturer_id, error_code)` → One error code per manufacturer

**Indexes:**
- `idx_error_codes_manufacturer` (manufacturer_id)
- `idx_error_codes_normalized` (normalized_code)
- `idx_error_codes_trigram` (GIN trigram for error_code fuzzy search)
- `idx_error_codes_affected_products_gin` (GIN for affected_product_ids array)
- `idx_error_codes_device_categories_gin` (GIN for device_categories array)
- `idx_error_codes_severity` (severity_level)
- `idx_error_codes_content_fts` (GIN full-text search on error_description + solution_steps)
- `idx_error_codes_alternative_gin` (GIN for alternative_codes array)
- `idx_error_codes_source_system` (manufacturer_id, source_system)
- `idx_error_codes_video_relation` (related_video_id) WHERE related_video_id IS NOT NULL

**Expected Rows**: 50,000-500,000 error codes  
**Growth Rate**: Medium (new codes with new products and updates)

---

### **🎥 4. CONTENT TABLES**

#### **`images`** → Bilder, Schematics & Diagrams
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique image ID |
| `document_id` | uuid | FK → documents(id) CASCADE | Source document |
| `chunk_id` | uuid | FK → chunks(id) | Associated text chunk (optional) |
| `storage_path` | text | NOT NULL | R2/S3 storage path |
| `storage_url` | text | | Public access URL |
| `file_hash` | text | NOT NULL | Deduplication hash |
| `original_filename` | text | | "diagram_01.png" |
| `width` | integer | | Image width in pixels |
| `height` | integer | | Image height in pixels |
| `file_size_bytes` | bigint | | File size |
| `image_format` | text | | "png", "jpg", "svg" |
| `image_type` | text | CHECK (schematic/diagram/screenshot/photo/chart) | Image classification |
| `page_number` | integer | | Source page in document |
| `page_position` | text | | "top", "bottom", "center" |
| `ai_description` | text | | "Diagram showing paper path in printer" |
| `detected_objects` | jsonb | | AI-detected objects and labels |
| `extracted_text` | text | | OCR text from image |
| `related_part_numbers` | text[] | | ["CB435A", "CE285A"] if detected |
| `metadata` | jsonb | DEFAULT '{}' | Additional image data |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Indexes:**
- `idx_images_document_id` (document_id)
- `idx_images_chunk_id` (chunk_id) WHERE chunk_id IS NOT NULL
- `idx_images_type` (image_type)
- `idx_images_file_hash` (file_hash)
- `idx_images_part_numbers_gin` (GIN for related_part_numbers array)
- `idx_images_description_fts` (GIN full-text search on ai_description)
- `idx_images_detected_objects_gin` (GIN for detected_objects JSONB)

**Expected Rows**: 100,000-1,000,000 images  
**Growth Rate**: High (many images per document)

---

#### **`instructional_videos`** → Video Anleitungen (Simplified)
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique video ID |
| `manufacturer_id` | uuid | FK → manufacturers(id) | Video creator |
| `product_ids` | uuid[] | | Related products |
| `title` | text | NOT NULL | "HP 9025 Toner Replacement" |
| `description` | text | | Detailed video description |
| `video_url` | text | NOT NULL | YouTube/Vimeo/Direct URL |
| `thumbnail_url` | text | | Video thumbnail image |
| `duration_seconds` | integer | | Video length |
| `language` | text | DEFAULT 'en' | Video language |
| `video_type` | text | CHECK (repair/maintenance/installation/troubleshooting/overview) | Content category |
| `related_part_numbers` | text[] | | Parts shown in video |
| `related_error_codes` | text[] | | Error codes addressed |
| `is_official` | boolean | DEFAULT true | Official manufacturer video |
| `metadata` | jsonb | DEFAULT '{}' | Additional video data |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Indexes:**
- `idx_videos_manufacturer_type` (manufacturer_id, video_type)
- `idx_videos_product_ids_gin` (GIN for product_ids array)
- `idx_videos_part_numbers_gin` (GIN for related_part_numbers array)
- `idx_videos_error_codes_gin` (GIN for related_error_codes array)
- `idx_videos_title_search` (GIN trigram for title search)

**Expected Rows**: 10,000-50,000 videos  
**Growth Rate**: Medium (new videos monthly)

---

### **📊 5. ANALYTICS TABLE**

#### **`search_analytics`** → Performance & Usage Tracking
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique analytics record |
| `session_id` | text | | Frontend session identifier |
| `user_id` | uuid | | Supabase user ID (optional) |
| `query_text` | text | NOT NULL | User search query |
| `query_intent` | text | | "error_lookup", "part_search", "manual_search" |
| `search_type` | text | CHECK (semantic/exact/fuzzy/comprehensive) | Search method used |
| `manufacturer_filter` | uuid | FK → manufacturers(id) | Applied manufacturer filter |
| `product_filter` | uuid | FK → products(id) | Applied product filter |
| `document_type_filter` | text | | Applied document type filter |
| `results_count` | integer | | Number of results returned |
| `top_result_similarity` | numeric | | Best match similarity score |
| `response_time_ms` | integer | | Performance metric |
| `user_clicked_result` | boolean | DEFAULT false | User engagement |
| `clicked_result_rank` | integer | | Position of clicked result |
| `user_feedback_rating` | integer | CHECK (1-5) | User satisfaction rating |
| `was_helpful` | boolean | | Overall helpfulness |
| `search_timestamp` | timestamptz | DEFAULT now() | Search execution time |

**Indexes:**
- `idx_search_analytics_timestamp` (search_timestamp)
- `idx_search_analytics_session` (session_id)
- `idx_search_analytics_performance` (search_type, response_time_ms)
- `idx_search_analytics_successful` (was_helpful) WHERE was_helpful = true

**Expected Rows**: 1,000,000+ analytics records  
**Growth Rate**: Very High (every search logged)  
**Cleanup Policy**: Delete records older than 90 days

---

### **🔧 6. MANAGEMENT TABLES**

#### **`document_relationships`** → HP CPMD + Service Manual Pairing
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique relationship ID |
| `primary_document_id` | uuid | FK → documents(id) CASCADE | Primary document |
| `secondary_document_id` | uuid | FK → documents(id) CASCADE | Related document |
| `relationship_type` | text | CHECK (cpmd_manual_pair/supersedes/supplements/translation/series_manual) | Relationship type |
| `description` | text | | Relationship description |
| `priority_order` | integer | DEFAULT 1 | Display priority |
| `created_at` | timestamptz | DEFAULT now() | Record creation |

**Constraints:**
- `CHECK(primary_document_id != secondary_document_id)` → No self-references
- `UNIQUE(primary_document_id, secondary_document_id, relationship_type)` → No duplicates

**Indexes:**
- `idx_doc_relationships_primary` (primary_document_id)
- `idx_doc_relationships_secondary` (secondary_document_id)
- `idx_doc_relationships_type` (relationship_type)

**Expected Rows**: 10,000-50,000 relationships  
**Growth Rate**: Medium (matches document growth)

---

#### **`product_compatibility`** → Model + Option Compatibility Matrix
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique compatibility ID |
| `base_product_id` | uuid | FK → products(id) | Base model |
| `option_product_id` | uuid | FK → products(id) | Compatible option |
| `is_compatible` | boolean | DEFAULT true | Compatibility status |
| `compatibility_notes` | text | | Installation notes |
| `installation_notes` | text | | Step-by-step instructions |
| `min_firmware_version` | text | | Required firmware minimum |
| `max_firmware_version` | text | | Firmware maximum (if incompatible) |
| `region_restrictions` | text[] | | ["US", "EU"] regional limitations |
| `mutually_exclusive_options` | uuid[] | | Options that cannot coexist |
| `performance_impact` | jsonb | | {"print_speed_reduction": "10%"} |
| `option_rules` | jsonb | DEFAULT '{}' | Complex dependency rules |
| `rule_priority` | integer | DEFAULT 5 | Rule evaluation priority |
| `validation_notes` | text | | Additional validation info |
| `verified_date` | timestamptz | | Last verification |
| `created_at` | timestamptz | DEFAULT now() | Record creation |

**Constraints:**
- `UNIQUE(base_product_id, option_product_id)` → One compatibility rule per pair

**Indexes:**
- `idx_compatibility_base` (base_product_id)
- `idx_compatibility_option` (option_product_id)
- `idx_compatibility_verified` (is_compatible, verified_date)

**Expected Rows**: 50,000-200,000 compatibility rules  
**Growth Rate**: Medium (grows with option combinations)

---

#### **`option_groups`** → Option Group Rules (Exclusive, Required Sets)
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique group ID |
| `manufacturer_id` | uuid | FK → manufacturers(id) | Group owner |
| `group_name` | text | NOT NULL | "Finisher Group", "Bridge Group" |
| `group_type` | text | CHECK (exclusive/required_set/max_limit) | Group behavior |
| `max_selections` | integer | | Maximum options from group |
| `min_selections` | integer | DEFAULT 0 | Minimum required selections |
| `option_product_ids` | uuid[] | | Array of option IDs in group |
| `description` | text | | Group purpose description |
| `technical_reason` | text | | "Physical space constraints" |
| `created_at` | timestamptz | DEFAULT now() | Record creation |

**Constraints:**
- `UNIQUE(manufacturer_id, group_name)` → Unique group names per manufacturer

**Indexes:**
- `idx_option_groups_manufacturer` (manufacturer_id)
- `idx_option_groups_type` (group_type)
- `idx_option_groups_options_gin` (GIN for option_product_ids array)

**Expected Rows**: 1,000-5,000 option groups  
**Growth Rate**: Low (stable group definitions)

---

#### **`processing_queue`** → Async Background Processing
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique task ID |
| `task_type` | text | CHECK (pdf_extraction/embedding_generation/video_processing/document_indexing/cpmd_parsing/relationship_mapping) | Task category |
| `document_id` | uuid | FK → documents(id) CASCADE | Target document |
| `chunk_id` | uuid | FK → chunks(id) CASCADE | Target chunk |
| `video_id` | uuid | FK → instructional_videos(id) CASCADE | Target video |
| `status` | text | CHECK (pending/processing/completed/failed/retry) | Task status |
| `priority` | integer | CHECK (1-10) | Processing priority (1=highest) |
| `attempts` | integer | DEFAULT 0 | Retry attempts |
| `max_attempts` | integer | DEFAULT 3 | Maximum retries |
| `error_message` | text | | Failure details |
| `processing_started_at` | timestamptz | | Start timestamp |
| `processing_completed_at` | timestamptz | | Completion timestamp |
| `task_metadata` | jsonb | DEFAULT '{}' | Task-specific parameters |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Indexes:**
- `idx_queue_status_priority` (status, priority DESC, created_at)
- `idx_queue_task_type` (task_type)
- `idx_queue_document` (document_id) WHERE document_id IS NOT NULL
- `idx_queue_pending` (created_at) WHERE status = 'pending'

**Expected Rows**: 100,000+ processing tasks  
**Growth Rate**: Very High (every document creates multiple tasks)  
**Cleanup Policy**: Delete completed tasks older than 30 days

---

#### **`competitive_features`** → Feature Definition für Product Comparison
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique feature ID |
| `feature_category` | text | NOT NULL | "print_speed", "connectivity", "paper_handling" |
| `feature_name` | text | NOT NULL | "pages_per_minute", "wifi_6", "duplex_scanning" |
| `feature_description` | text | | "Color pages printed per minute" |
| `data_type` | text | CHECK (numeric/boolean/text/array) | Value data type |
| `unit` | text | | "ppm", "MB", "sheets", "inches" |
| `higher_is_better` | boolean | DEFAULT true | Scoring direction |
| `weight` | numeric | DEFAULT 1.0 | Importance weight for scoring |
| `created_at` | timestamptz | DEFAULT now() | Record creation |

**Constraints:**
- `UNIQUE(feature_category, feature_name)` → No duplicate features

**Indexes:**
- `idx_competitive_features_category` (feature_category)

**Expected Rows**: 100-500 features  
**Growth Rate**: Low (stable feature definitions)

---

#### **`product_features`** → Product Feature Values für Comparison
| Column | Type | Constraint | Description |
|--------|------|------------|-------------|
| `id` | uuid | PRIMARY KEY | Unique feature value ID |
| `product_id` | uuid | FK → products(id) CASCADE | Product with feature |
| `feature_id` | uuid | FK → competitive_features(id) CASCADE | Feature definition |
| `feature_value` | jsonb | NOT NULL | {"value": 22, "verified": true} |
| `verified` | boolean | DEFAULT false | Officially verified |
| `source` | text | | "official_manual", "third_party_test" |
| `last_verified` | timestamptz | | Verification timestamp |
| `created_at` | timestamptz | DEFAULT now() | Record creation |
| `updated_at` | timestamptz | DEFAULT now() | Last modification |

**Constraints:**
- `UNIQUE(product_id, feature_id)` → One value per product per feature

**Indexes:**
- `idx_product_features_product` (product_id)
- `idx_product_features_feature` (feature_id)
- `idx_product_features_verified` (verified) WHERE verified = true

**Expected Rows**: 100,000-500,000 feature values  
**Growth Rate**: Medium (grows with products and features)

---

## 🔧 **FUNCTIONS & PROCEDURES**

### **Core Search Functions:**
1. **`normalize_error_code(TEXT)`** → Text normalization for fuzzy search
2. **`comprehensive_search(...)`** → Multi-table semantic search for AI agents
3. **`search_error_codes_fuzzy(...)`** → Fuzzy error code matching
4. **`get_documents_for_product(...)`** → Product-specific document lookup
5. **`get_images_for_part_numbers(...)`** → Schematic/diagram retrieval
6. **`validate_option_configuration(...)`** → Complex option dependency validation
7. **`get_hp_documentation_set(...)`** → HP CPMD + Service Manual pairing
8. **`compare_products(...)`** → Competitive feature comparison

### **Product Management Functions:**
9. **`get_models_for_series(UUID)`** → Hierarchy navigation
10. **`get_product_hierarchy(...)`** → Full manufacturer product tree
11. **`get_compatible_options(UUID)`** → Available options for model
12. **`get_product_configuration(UUID)`** → Complete model + options setup

### **Analytics Functions:**
13. **`log_search_analytics(...)`** → Performance tracking
14. **`check_user_permissions()`** → Security validation

### **Automation Triggers:**
- **`auto_normalize_error_code()`** → Automatic error code normalization
- **`auto_normalize_chunk_error_codes()`** → Chunk-level error code extraction

---

## 🔒 **SECURITY & PERMISSIONS**

### **Row Level Security (RLS):** ✅ Enabled on all tables

### **Access Policies:**

#### **Service Role** (Backend):
- **Full Access**: ALL operations on ALL tables
- **Use Case**: Python processing scripts, API backend

#### **Authenticated Users** (Dashboard):
- **Read Access**: ALL tables  
- **Limited Write**: search_analytics only
- **Use Case**: Admin dashboard, management interface

#### **Anonymous Users** (Public API):
- **Read Access**: manufacturers, products, documents (completed only), chunks (completed only), embeddings, error_codes, images, search_analytics (public only)
- **Write Access**: search_analytics creation only
- **Use Case**: Public search interface, AI agent queries

### **Security Functions:**
- Permission validation with `check_user_permissions()`
- Optimized policies for performance (EXISTS checks where needed)

---

## 📊 **PERFORMANCE CHARACTERISTICS**

### **Storage Estimates:**
- **manufacturers**: ~1MB (small reference table)
- **products**: ~100MB (moderate size with JSONB specs)
- **documents**: ~500MB (metadata only, files in R2/S3)
- **chunks**: ~50GB (largest table, millions of text chunks)
- **embeddings**: ~30GB (768D vectors × millions of chunks)
- **error_codes**: ~1GB (extensive error database)
- **images**: ~2GB (metadata only, files in R2/S3)
- **Total Database**: ~85GB estimated for full production load

### **Index Performance:**
- **Composite Indexes**: 20-50ms for multi-column searches
- **GIN Indexes**: 30-80ms for JSONB/array/full-text searches
- **Vector Indexes**: 10-30ms for HNSW similarity search
- **Trigram Indexes**: 40-100ms for fuzzy text matching

### **Expected Query Performance:**
- **Simple lookups**: <10ms
- **Complex searches**: 50-200ms
- **AI semantic search**: 100-500ms
- **Product configuration validation**: 200-800ms
- **Competitive analysis**: 300-1000ms

---

## 🚀 **DEPLOYMENT STRATEGY**

### **Migration Order:**
1. `01_optimized_core_schema.sql` → Core 8 tables + indexes
2. `02_optimized_functions.sql` → Search functions + helpers
3. `03_optimized_security.sql` → RLS policies + permissions
4. `04_sample_data.sql` → Basic test data
5. `05_extended_features.sql` → Videos + options + CPMD
6. `06_extended_sample_data.sql` → Extended test data
7. `07_final_optimizations.sql` → Document relationships + complex rules
8. `08_final_sample_data.sql` → Production-ready examples

### **Post-Migration Tasks:**
1. **Create HNSW Vector Index**: After embedding data ingestion
2. **Setup Cleanup Jobs**: Automated removal of old analytics/queue data
3. **Performance Monitoring**: Track query performance and optimize as needed
4. **Backup Strategy**: Regular backups with point-in-time recovery

---

## 🎯 **OPTIMIZATION NOTES**

### **Performance Optimizations:**
- **Separate Embeddings Table**: Faster text search + dedicated vector operations
- **JSONB for Flexibility**: Technical specs + metadata without schema changes
- **Async Processing Queue**: Heavy operations don't block user interface
- **Composite Indexes**: Optimized for common query patterns
- **Partial Indexes**: Only index relevant subsets (active products, pending reviews)

### **Storage Optimizations:**
- **File Storage**: Documents/images in R2/S3, only metadata in database
- **Deduplication**: SHA256 hashes prevent duplicate file storage
- **Cleanup Policies**: Automatic removal of old analytics and completed queue tasks

### **Scalability Considerations:**
- **Horizontal Scaling**: Read replicas for search-heavy workloads
- **Partition Strategy**: Large tables (chunks, embeddings) can be partitioned by manufacturer
- **Caching Layer**: Redis/Memcached for frequently accessed data
- **CDN Integration**: R2/S3 with CloudFlare for global file distribution

---

## ✅ **PRODUCTION READINESS CHECKLIST**

- [x] **All Tables Defined** with proper constraints and relationships
- [x] **Comprehensive Indexes** for all expected query patterns
- [x] **Row Level Security** implemented for multi-tenant access
- [x] **Data Validation** with CHECK constraints and triggers
- [x] **Performance Functions** optimized for AI agent usage
- [x] **Async Processing** for scalable background operations
- [x] **Competitive Analysis** for business intelligence
- [x] **Complex Dependencies** handled with validation logic
- [x] **Documentation** complete with examples and migration strategy

**🎉 Database is 100% production-ready for KRAI Engine deployment!**