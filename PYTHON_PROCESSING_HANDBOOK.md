# 📚 KRAI ENGINE - PYTHON PROCESSING HANDBOOK
**Interactive Terminal Processing + Filament Dashboard Integration**
*Version 1.0 - Development Implementation Guide*
*Created: 22. September 2025*

## 🎯 **DEVELOPMENT APPROACH - 2-PHASE IMPLEMENTATION**

### **Phase 1: Interactive Terminal Script** 🖥️
- **Interaktives Python Skript** für manuelle Kategorisierung
- **Terminal-basierte Eingabe** für Hersteller, Dokumenttyp, etc.
- **Sofortige Verarbeitung** und Datenbankeinträge
- **Print Quality ML Training** mit Techniker-Feedback

### **Phase 2: Filament Dashboard Integration** 🌐  
- **Web-Interface** für Upload und Kategorisierung
- **Automatische Vorschläge** basierend auf Phase 1 Daten
- **Drag & Drop** Upload mit intelligenter Kategorisierung
- **Dashboard Monitoring** aller Verarbeitungsprozesse

### **🔄 Data Flow - Interactive Processing**

```
📄 Document/Image → 🖥️ Terminal Questions → 👨‍� User Input → 🧠 AI Processing → 🗃️ Database → � Dashboard View
```

---

## 📋 **INTERACTIVE TERMINAL SCRIPT ARCHITECTURE**

### **🖥️ Script Flow: krai_processor.py**

```text
SCHRITT 1: Datei-Upload Detection
├── PDF Document detected
├── Image File detected  
└── Batch Folder detected

SCHRITT 2: Interactive Questions
├── Welcher Hersteller? [HP/Canon/Epson/Brother/Xerox/Other]
├── Dokumenttyp? [CPMD/Service Manual/Parts Catalog/Print Quality Image]
├── Produktmodell? [LaserJet Pro 4000/PIXMA TR8500/etc.]
└── Zusätzliche Metadaten? [Version/Sprache/etc.]

SCHRITT 3: AI Processing
├── OCR Text Extraction (Documents)
├── Computer Vision Analysis (Images)  
├── Error Code Pattern Recognition
└── Structured Data Extraction

SCHRITT 4: Database Storage
├── Insert into documents/images table
├── Create chunks with metadata
├── Generate vector embeddings
└── Link to manufacturer/product tables

SCHRITT 5: Learning Feedback
├── Print Quality Defect Training (für Images)
├── Error Code Pattern Validation
├── User Feedback Collection
└── ML Model Improvement
```

### **🎯 Terminal Script Features**

#### **Interactive User Input**

- **Manufacturer Selection**: Dropdown-like selection für alle Hersteller
- **Document Type Detection**: Intelligente Vorschläge basierend auf Dateiinhalt
- **Product Model Matching**: Auto-complete für bekannte Modelle
- **Quality Assessment**: Techniker-Feedback für Print Quality Images

#### **AI-Powered Suggestions**

- **Content Analysis**: Automatische Kategorisierung basierend auf Inhalt
- **Pattern Recognition**: Bekannte Error Code Patterns erkennen
- **Model Training**: Jeder Upload verbessert die AI-Genauigkeit
- **Conflict Resolution**: Hilft bei unklaren Kategorisierungen

#### **Batch Processing Support**

- **Folder Scanning**: Komplette Ordner verarbeiten
- **Progress Tracking**: Fortschrittsanzeige für große Batches
- **Error Handling**: Robuste Fehlerbehandlung mit Retry-Logic
- **Resume Capability**: Unterbrochene Prozesse fortsetzen

---

## 🗂️ **DOCUMENT TYPES & INTERACTIVE PROCESSING**

### **1. CPMD Database Files (.pdf) - Interactive Processing**

**Terminal Questions:**

```text
🏢 Hersteller: HP (detected from filename pattern)
📄 Dokumenttyp: CPMD Database (auto-detected)
🏷️ Version: [User Input] v2.1, v2.2, etc.
🌍 Sprache: [User Input] EN/DE/FR/ES
```

**Processing Strategy**: OCR + Structured Error Code Extraction  
**Target Tables**: `documents`, `chunks`, `error_codes`  
**Uniqueness**: HP-specific error database with solutions

### **2. Service Manuals (.pdf) - ALL MANUFACTURERS - Interactive Processing**

**Terminal Questions:**

```text
🏢 Hersteller: [Interactive Selection] HP/Canon/Epson/Brother/Xerox
📄 Dokumenttyp: Service Manual (detected from content)
🖨️ Produktmodell: [Auto-complete Input] LaserJet Pro 4000, PIXMA TR8500, etc.
📅 Jahr: [Optional] 2020-2025
🌍 Sprache: [User Input] EN/DE/FR/ES
```

**Processing Strategy**: OCR + Error Code Pattern Recognition  
**Target Tables**: `documents`, `chunks`, `error_codes` (extracted from content)  
**Uniqueness**: Most manufacturers embed error codes IN the service manual text

**Example Error Code Patterns:**

```text
Canon: "Error Code E001: Paper jam in rear unit"
Epson: "Error 031: Ink cartridge not recognized"  
Brother: "Error Code E-32: Fuser unit malfunction"
```

### **3. Parts Catalogs (.pdf) - ALL MANUFACTURERS - Interactive Processing**

**Terminal Questions:**

```text
🏢 Hersteller: [Interactive Selection] HP/Canon/Epson/Brother/Xerox
📄 Dokumenttyp: Parts Catalog (detected from content)
🖨️ Produktserie: [Auto-complete] LaserJet Pro Series, PIXMA Series, etc.
📅 Jahr: [Optional] 2020-2025
🌍 Sprache: [User Input] EN/DE/FR/ES
```

**Processing Strategy**: Part Number Extraction + Product Mapping  
**Target Tables**: `documents`, `chunks` (with part number metadata)

### **4. 🖼️ PRINT QUALITY IMAGES - Interactive Processing & ML Training**

**Terminal Questions:**

```text
🏢 Hersteller: [Interactive Selection] HP/Canon/Epson/Brother/Xerox
🖨️ Druckermodell: [Auto-complete] LaserJet Pro 4000, PIXMA TR8500, etc.
🖼️ Bildtyp: [Selection] Test Page/Defect Sample/Before-After Comparison
🔧 Problem: [Multi-select] Banding/Streaking/Color Issues/Paper Jam/etc.
👨‍� Techniker: [Input] Name für Feedback-Training
⭐ Qualität: [1-5 Scale] Für ML Training
```

**Processing Strategy**: Computer Vision + Defect Classification + Techniker Feedback  
**Target Tables**: `images`, `print_defects`, `quality_assessments`, `technician_feedback`  
**AI Models**: Computer Vision (YOLOv8, MobileNet) + Custom defect classifiers

#### **🔍 Interactive Print Quality Analysis Workflow:**

```python
def interactive_print_quality_analysis():
    # Step 1: Capture User Context
    manufacturer = select_manufacturer()
    printer_model = autocomplete_printer_model(manufacturer)
    defect_type = multi_select_defects()
    technician_name = input("Techniker Name: ")
    
    # Step 2: AI Vision Analysis
    defects = analyze_print_quality_with_ai(image_path)
    confidence_scores = calculate_confidence(defects)
    
    # Step 3: Techniker Feedback Collection
    user_confirms_defects = confirm_ai_analysis(defects)
    user_adds_missing_defects = add_additional_defects()
    quality_rating = input("Quality Rating (1-5): ")
    
    # Step 4: ML Training Data Generation
    store_training_data(defects, user_feedback, quality_rating)
    update_ml_model_with_feedback()
    
    # Step 5: Database Storage
    store_print_quality_analysis_results()
```
# AI Vision Pipeline for Print Quality
def analyze_print_quality_image(image_upload, technician_context):
    """
    Complete AI-powered print quality analysis pipeline
    
    Args:
        image_upload: Raw image file from technician
        technician_context: Service context (manufacturer, model, etc.)
    """
    analysis_result = {
        # 1. Image preprocessing
        "preprocessed_image": preprocess_print_sample(image_upload),
        "image_quality_check": validate_image_quality(image_upload),
        
        # 2. AI defect detection
        "detected_defects": detect_print_defects(image_upload),
        "defect_locations": get_defect_bounding_boxes(image_upload),
        "confidence_scores": calculate_detection_confidence(detected_defects),
        
        # 3. Quality assessment
        "overall_quality_score": assess_overall_quality(image_upload),
        "quality_metrics": {
            "color_accuracy": measure_color_accuracy(image_upload),
            "sharpness": measure_sharpness(image_upload),
            "uniformity": measure_uniformity(image_upload),
            "banding_severity": detect_banding_level(image_upload)
        },
        
        # 4. Root cause analysis
        "probable_causes": suggest_probable_causes(detected_defects, technician_context),
        "recommended_actions": suggest_repair_actions(detected_defects, technician_context),
        
        # 5. Quality standards compliance
        "quality_assessment": assess_against_standards(quality_metrics, manufacturer),
        "pass_fail_result": determine_pass_fail(quality_metrics, quality_standard)
    }
    
    return analysis_result

# Defect Classification Categories
DEFECT_CATEGORIES = {
    'banding': 'Horizontal/vertical bands across print',
    'streaking': 'Linear streaks or lines',
    'color_issues': 'Color deviation, mixing, registration',
    'density_variation': 'Uneven light/dark areas',
    'contamination': 'Spots, dirt, debris on print',
    'mechanical_defects': 'Physical damage patterns',
    'paper_handling': 'Wrinkles, jams, feeding issues',
    'toner_issues': 'Low toner, scatter, smearing',
    'fuser_problems': 'Heat/pressure related defects',
    'registration': 'Color misalignment issues'
}
```

#### **Multi-Manufacturer Error Code Processing:**

```python
# Universal Error Code Extraction - Works for ALL manufacturers
def extract_error_codes_from_pdf(pdf_text, manufacturer_name, document_type):
    """
    Extract error codes from PDF content (CPMD, Service Manuals, etc.)
    
    Args:
        pdf_text: OCR extracted text from PDF
        manufacturer_name: "HP", "Canon", "Epson", "Brother"
        document_type: "cpmd_database", "service_manual"
    """
    error_patterns = {
        'hp': [
            r'Error\s+Code?\s*([A-Z]?[0-9]+[-_]?[0-9]*)',  # C1234, E-5678
            r'Code\s*([A-Z][0-9]+)',                        # C123
        ],
        'canon': [
            r'Error\s+Code?\s*([E][0-9]{3,4})',            # E001, E1234
            r'Support\s+Code\s*([0-9]{4})',                # 6000
        ],
        'epson': [
            r'Error\s*([0-9]{3})',                         # 031, 079
            r'Service\s+Required\s*([0-9x]{5})',           # 0x97
        ],
        'brother': [
            r'Error\s+Code?\s*([A-Z]-?[0-9]{1,3})',        # E-32, B2
            r'([A-Z]{2}[0-9]{2})',                         # AF01
        ]
    }
    
    # CPMD specific patterns for HP
    if document_type == 'cpmd_database' and manufacturer_name.lower() == 'hp':
        # HP CPMD PDFs have structured layout with error code tables
        cpmd_patterns = [
            r'(?i)error\s+code\s*[:|\s]+([A-Z]?[0-9]+[-_]?[0-9]*)',
            r'(?i)troubleshooting\s+code\s*[:|\s]+([A-Z]?[0-9]+)',
            r'(?i)fault\s+code\s*[:|\s]+([A-Z]?[0-9]+)'
        ]
        patterns = error_patterns.get('hp', []) + cpmd_patterns
    else:
        # Standard service manual patterns
        patterns = error_patterns.get(manufacturer_name.lower(), [])
    
    # Universal fallback patterns
    if not patterns:
        patterns = [
            r'(?i)error\s+(?:code?)?\s*[:\-]?\s*([A-Z]?[0-9]+[-_]?[0-9]*)',
            r'(?i)code\s*[:\-]?\s*([A-Z]+[0-9]+)',
            r'(?i)fault\s+([0-9]+)',
        ]
    
    extracted_codes = []
    for pattern in patterns:
        matches = re.findall(pattern, pdf_text, re.IGNORECASE)
        extracted_codes.extend(matches)
    
    return list(set(extracted_codes))  # Remove duplicates

# Storage for ANY manufacturer - PDF source
for error_code in extracted_codes:
    error_record = {
        'manufacturer_id': manufacturer_id,  # HP, Canon, Epson, etc.
        'document_id': document_id,
        'error_code': error_code,
        'normalized_code': normalize_error_code(error_code, manufacturer_name),
        'error_description': extract_error_description(pdf_text, error_code),
        'solution_steps': extract_solution_steps(pdf_text, error_code),
        'source_system': document_type,  # 'cpmd_database' or 'service_manual'
        'page_references': find_page_numbers(pdf_text, error_code),
        'context_text': extract_surrounding_text(pdf_text, error_code)
    }
```

#### **Storage Flow für CPMD:**
```sql
-- Step 1: Create document record
INSERT INTO documents (
    file_name, document_type, manufacturer_id, 
    cpmd_version, metadata, processing_status
) VALUES (
    'HP_9025_CPMD_v2.1.xml', 'cpmd_database', hp_manufacturer_id,
    'v2.1.2024', json_metadata, 'processing'
);

-- Step 2: Extract and store error codes
INSERT INTO error_codes (
    manufacturer_id, document_id, error_code, normalized_code,
    error_description, solution_steps, affected_product_ids
) VALUES (
    hp_id, document_id, 'C1234', 'c1234',
    'Paper jam in input tray', solution_text, [model_id]
);

-- Step 3: Create semantic chunks
INSERT INTO chunks (
    document_id, chunk_index, text_chunk, 
    extracted_error_codes, normalized_error_codes, embedding
) VALUES (
    document_id, 0, chunk_text, 
    ['C1234'], ['c1234'], embedding_vector
);
```

### **2. HP Service Manuals (.pdf)**
**Input**: PDF Service Manuals
**Processing Strategy**: OCR + Section Detection + Manual Pairing
**Target Tables**: `documents`, `chunks`, `document_relationships`

#### **Data Extraction Process:**
```python
# 1. PDF Text Extraction
manual_data = {
    "title": "HP OfficeJet Pro 9025 Service Manual",
    "chapters": ["Troubleshooting", "Parts", "Maintenance"],
    "page_count": 234,
    "revision": "Rev A",
    "extracted_text": "Full manual content...",
    "error_references": ["C1234", "E-5678"]  # Cross-referenced
}

# 2. Storage Strategy:
documents → Manual metadata + PDF reference
chunks → Chapter-based text segments
document_relationships → Automatic CPMD pairing
```

#### **Storage Flow für Service Manuals:**
```sql
-- Step 1: Create document record
INSERT INTO documents (
    file_name, document_type, manufacturer_id,
    total_pages, metadata, processing_status
) VALUES (
    'HP_9025_Service_Manual.pdf', 'service_manual', hp_id,
    234, json_metadata, 'processing'
);

-- Step 2: Create semantic chunks by chapter
INSERT INTO chunks (
    document_id, chunk_index, page_start, page_end,
    text_chunk, section_title, extracted_error_codes, embedding
) VALUES (
    document_id, 0, 45, 45, chapter_text,
    'Chapter 5: Troubleshooting', ['C1234'], embedding_vector
);

-- Step 3: Create intelligent CPMD + Manual pairing
INSERT INTO document_relationships (
    primary_document_id, secondary_document_id, 
    relationship_type, description
) VALUES (
    cpmd_id, manual_id, 'cpmd_manual_pair',
    'Intelligent pairing for comprehensive troubleshooting'
);
```

### **3. HP Parts Catalogs (.pdf)**
**Input**: Parts Catalog PDFs
**Processing Strategy**: Part Number Extraction + Product Mapping
**Target Tables**: `documents`, `chunks` (with part number metadata)

#### **Data Extraction Process:**
```python
# 1. Parts Catalog Processing
parts_data = {
    "catalog_title": "HP OfficeJet Pro 9025 Parts Catalog",
    "part_numbers": ["CB435A", "CE285A", "CB436A"],
    "part_descriptions": ["Toner Cartridge", "Fuser Unit"],
    "compatibility": ["HP 9025", "HP 9020"],
    "illustrations": ["Figure 1-1", "Figure 2-3"]
}

# 2. Storage Strategy:
documents → Catalog metadata
chunks → Part-focused text segments with part number extraction
```

---

## 🗃️ **DETAILED TABLE STORAGE MAPPING**

### **🖼️ Print Quality Analysis Tables**

#### **� `images` Table**
**Purpose**: Store technician-uploaded photos and processed images
**Data Source**: Mobile uploads, scanner uploads, camera captures
**Python Interaction**: Image preprocessing and storage management
```python
# Store uploaded print quality image
async def store_print_quality_image(image_upload, technician_context):
    # 1. Image validation and preprocessing
    validated_image = validate_and_preprocess_image(image_upload)
    
    # 2. Store original image
    image_record = {
        'document_id': None,  # Not linked to a document
        'chunk_id': None,     # Standalone quality image
        'file_name': f"quality_sample_{timestamp}.jpg",
        'storage_url': await upload_to_storage(validated_image),
        'width': validated_image.width,
        'height': validated_image.height,
        'file_size_bytes': len(validated_image.data),
        'image_format': 'jpg',
        'image_type': 'photo',  # Print quality photo
        'alt_text': f"Print quality sample from {technician_context.manufacturer}",
        'extracted_text': None,  # No OCR needed for quality analysis
        'technician_id': technician_context.technician_id,
        'upload_context': {
            'manufacturer': technician_context.manufacturer,
            'product_model': technician_context.product_model,
            'service_call_id': technician_context.service_call_id,
            'upload_method': 'mobile_app'  # or 'web_interface'
        }
    }
    
    image_id = await insert_image_record(image_record)
    return image_id
```

#### **🔍 `print_defects` Table**
**Purpose**: AI analysis results for print quality defects
**Data Source**: Computer vision analysis of uploaded images
**Python Interaction**: Core defect detection and classification
```python
# AI-powered defect analysis
async def analyze_and_store_defects(image_id, analysis_context):
    # 1. Load AI models
    defect_detector = load_defect_detection_model()
    quality_assessor = load_quality_assessment_model()
    
    # 2. Run AI analysis
    image_data = await get_image_data(image_id)
    
    # Detect defects using computer vision
    detected_defects = defect_detector.detect(image_data)
    quality_metrics = quality_assessor.assess(image_data)
    
    # 3. Store analysis results
    for defect in detected_defects:
        defect_record = {
            'original_image_id': image_id,
            'processed_image_url': await create_annotated_image(image_data, defect),
            'thumbnail_url': await create_thumbnail(image_data, defect),
            'technician_id': analysis_context.technician_id,
            'manufacturer_id': analysis_context.manufacturer_id,
            'product_id': analysis_context.product_id,
            'service_call_id': analysis_context.service_call_id,
            
            # AI Classification Results
            'defect_category': defect.category,  # 'banding', 'streaking', etc.
            'confidence_score': defect.confidence,
            'ai_model_version': defect_detector.version,
            'detection_boxes': defect.bounding_boxes,
            'severity_level': classify_severity(defect),
            
            # AI Analysis
            'defect_description': generate_defect_description(defect),
            'affected_area_percentage': calculate_affected_area(defect, image_data),
            'probable_causes': suggest_probable_causes(defect, analysis_context),
            'recommended_actions': suggest_repair_actions(defect, analysis_context),
            
            # Quality Metrics
            'overall_quality_score': quality_metrics.overall_score,
            'color_accuracy_score': quality_metrics.color_accuracy,
            'sharpness_score': quality_metrics.sharpness,
            'uniformity_score': quality_metrics.uniformity,
            
            # Print Context
            'print_settings': analysis_context.print_settings,
            'test_pattern_used': analysis_context.test_pattern,
            'before_after': analysis_context.before_after,  # 'before', 'after', 'comparison'
            
            # Training Data
            'training_sample': True,  # Use for AI improvement
            'expert_verified': False,  # Needs technician confirmation
            'training_weight': calculate_training_weight(defect.confidence)
        }
        
        await insert_defect_record(defect_record)

# Defect severity classification
def classify_severity(defect):
    severity_thresholds = {
        'banding': {'minor': 0.05, 'moderate': 0.15, 'severe': 0.30},
        'streaking': {'minor': 0.03, 'moderate': 0.10, 'severe': 0.25},
        'color_issues': {'minor': 2.0, 'moderate': 5.0, 'severe': 10.0},
        'registration': {'minor': 0.1, 'moderate': 0.3, 'severe': 0.6}
    }
    
    thresholds = severity_thresholds.get(defect.category, {'minor': 0.1, 'moderate': 0.3, 'severe': 0.6})
    
    if defect.intensity <= thresholds['minor']:
        return 'minor'
    elif defect.intensity <= thresholds['moderate']:
        return 'moderate'
    elif defect.intensity <= thresholds['severe']:
        return 'severe'
    else:
        return 'critical'
```

#### **🏭 `products` Table** 
**Purpose**: HP Product hierarchy (Series → Model → Options)
**Data Source**: Document metadata + Manual configuration
**Python Interaction**: Product detection from document content
```python
# Auto-detect product from document
detected_products = extract_product_models(document_text)
# Example: ["HP OfficeJet Pro 9025", "HP OfficeJet Pro 9020"]

# Link to existing products or create new entries
product_ids = await link_or_create_products(detected_products, manufacturer_id)
```

#### **📄 `documents` Table**
**Purpose**: Master document registry
**Data Source**: All uploaded files
**Python Interaction**: Primary entry point for all processing
```python
# Create document record for any file type
document_record = {
    'file_name': uploaded_file.name,
    'file_hash': calculate_file_hash(file_content),
    'storage_path': storage_url,
    'document_type': detect_document_type(file_content),
    'manufacturer_id': manufacturer_id,
    'product_ids': detected_product_ids,
    'total_pages': page_count if pdf else None,
    'cpmd_version': cpmd_version if cpmd else None,
    'processing_status': 'processing',
    'metadata': extraction_metadata
}
```

#### **📝 `chunks` Table**
**Purpose**: Semantic text segments with embeddings
**Data Source**: All processed documents
**Python Interaction**: Core content storage for search
```python
# Create chunks for any document type
for i, chunk in enumerate(extracted_chunks):
    chunk_record = {
        'document_id': document_id,
        'chunk_index': i,
        'page_start': chunk.page_start,
        'page_end': chunk.page_end,
        'text_chunk': chunk.content,
        'token_count': count_tokens(chunk.content),
        'fingerprint': generate_chunk_hash(chunk.content),
        'section_title': chunk.section_title,
        'extracted_error_codes': extract_error_codes(chunk.content),
        'normalized_error_codes': normalize_error_codes(extracted_codes),
        'extracted_part_numbers': extract_part_numbers(chunk.content),
        'embedding': await generate_embedding(chunk.content),
        'ocr_confidence': chunk.ocr_confidence if ocr else None,
        'chunk_quality_score': calculate_quality_score(chunk),
        'processing_status': 'completed'
    }
```

#### **⚠️ `error_codes` Table - MULTI-MANUFACTURER**
**Purpose**: Error codes from ALL manufacturers (HP, Canon, Epson, Brother, etc.)
**Data Source**: CPMD XML files (HP only) + Service Manual extraction (All manufacturers)
**Python Interaction**: Universal error code extraction + manufacturer-specific normalization

```python
# Universal Error Code Storage - Works for ALL manufacturers
async def store_error_code(error_data, manufacturer_name):
    error_record = {
        'manufacturer_id': get_manufacturer_id(manufacturer_name),
        'document_id': error_data.document_id,
        'error_code': error_data.raw_code,  # "E001", "C1234", "B-32"
        'normalized_code': normalize_by_manufacturer(error_data.raw_code, manufacturer_name),
        'error_description': error_data.description,
        'solution_steps': error_data.solution_text,
        'affected_product_ids': error_data.compatible_products,
        'source_system': error_data.source,  # 'cpmd_database' or 'service_manual'
        'page_references': error_data.page_numbers,  # For manual sources
        'context_text': error_data.surrounding_text,  # Original context
        'extraction_confidence': error_data.confidence_score,
        'manufacturer_specific_data': {
            'hp': {'cpmd_version': '2.1'} if manufacturer_name == 'HP' else None,
            'canon': {'support_code_variant': True} if manufacturer_name == 'Canon' else None,
            'epson': {'service_mode_required': True} if manufacturer_name == 'Epson' else None,
            'brother': {'lcd_display_format': 'alphanumeric'} if manufacturer_name == 'Brother' else None
        }
    }
    
    await insert_error_code(error_record)

# Manufacturer-specific normalization
def normalize_by_manufacturer(error_code, manufacturer):
    normalizers = {
        'hp': lambda code: code.lower().replace('-', '').replace('_', ''),
        'canon': lambda code: code.upper().replace('E', 'e'),
        'epson': lambda code: code.zfill(3),  # Pad to 3 digits
        'brother': lambda code: code.upper().replace('-', ''),
        'default': lambda code: code.lower().strip()
    }
    
    normalizer = normalizers.get(manufacturer.lower(), normalizers['default'])
    return normalizer(error_code)
```

#### **🔗 `document_relationships` Table**
**Purpose**: Intelligent document pairing (CPMD + Manual)
**Data Source**: Python intelligent pairing logic
**Python Interaction**: Automatic relationship creation
```python
# Intelligent CPMD + Manual pairing
async def create_document_relationship(cpmd_doc_id, manual_doc_id):
    # Analyze content overlap and error code references
    overlap_score = calculate_content_overlap(cpmd_content, manual_content)
    common_error_codes = find_common_error_codes(cpmd_doc, manual_doc)
    
    if overlap_score > 0.7 and len(common_error_codes) > 0:
        relationship = {
            'primary_document_id': cpmd_doc_id,
            'secondary_document_id': manual_doc_id,
            'relationship_type': 'cpmd_manual_pair',
            'description': f'Intelligent pairing: {len(common_error_codes)} common error codes',
            'priority_order': 1,
            'metadata': {
                'overlap_score': overlap_score,
                'common_error_codes': common_error_codes
            }
        }
        await store_relationship(relationship)
```

### **Advanced HP Business Logic Tables**

#### **⚙️ `product_compatibility` Table**
**Purpose**: Bridge/Finisher option validation rules
**Data Source**: HP Product documentation + Configuration
**Python Interaction**: Option validation during processing
```python
# Extract option compatibility from service manuals
compatibility_rules = extract_option_rules(service_manual_content)
# Example: "Finisher X requires Bridge A"

for rule in compatibility_rules:
    compatibility_record = {
        'base_product_id': base_model_id,
        'option_product_id': option_id,
        'is_compatible': rule.is_compatible,
        'compatibility_notes': rule.description,
        'installation_notes': rule.installation_procedure,
        'option_rules': {
            'requires': rule.required_options,
            'excludes': rule.conflicting_options,
            'installation_order': rule.install_sequence
        },
        'rule_priority': rule.priority
    }
```

#### **👥 `option_groups` Table**
**Purpose**: Mutual exclusion groups (Finisher/Bridge groups)
**Data Source**: HP Product specifications
**Python Interaction**: Group validation logic
```python
# Create mutual exclusion groups for HP options
finisher_group = {
    'manufacturer_id': hp_manufacturer_id,
    'group_name': 'Finisher Group',
    'group_type': 'exclusive',  # Only one finisher allowed
    'max_selections': 1,
    'min_selections': 0,
    'option_product_ids': [finisher_x_id, finisher_y_id],
    'description': 'Only one finisher can be installed per printer',
    'technical_reason': 'Physical space constraints in rear assembly'
}
```

#### **📊 `competitive_features` & `product_features` Tables**
**Purpose**: Feature comparison framework
**Data Source**: HP Specifications + Competitive analysis
**Python Interaction**: Feature extraction from documents
```python
# Extract product features from specifications
features = extract_technical_specifications(document_content)
# Example: {"print_speed_color": 22, "max_resolution": 4800}

for feature_name, feature_value in features.items():
    feature_record = {
        'product_id': product_id,
        'feature_id': get_feature_id(feature_name),
        'feature_value': {
            'value': feature_value,
            'unit': detect_unit(feature_name),
            'verified': True
        },
        'verified': True,
        'source': 'official_manual'
    }
```

### **System Performance Tables**

#### **📈 `performance_metrics` Table**
**Purpose**: Query performance tracking
**Python Interaction**: Automatic logging during processing
```python
# Log processing performance
await log_performance_metric({
    'operation_type': 'document_processing',
    'operation_name': 'cpmd_xml_parse',
    'execution_time_ms': processing_time,
    'input_size_bytes': file_size,
    'output_records': record_count,
    'success': True,
    'metadata': {'document_type': 'cpmd_database'}
})
```

#### **🔍 `search_logs` Table**
**Purpose**: User search analytics
**Python Interaction**: API search endpoint logging
```python
# Log search queries for analytics
await log_search_query({
    'search_query': user_query,
    'search_type': 'comprehensive_search',
    'result_count': len(search_results),
    'response_time_ms': query_time,
    'user_session_id': session_id,
    'filters_applied': search_filters
})
```

#### **🔄 `processing_jobs` Table**
**Purpose**: Document processing queue
**Python Interaction**: Job queue management
```python
# Create processing job for async handling
job = {
    'job_type': 'document_processing',
    'status': 'pending',
    'input_data': {
        'file_path': storage_path,
        'document_type': detected_type,
        'manufacturer': 'HP Inc.'
    },
    'created_by': user_id,
    'priority': calculate_job_priority(file_size, document_type)
}
```

---

## 🔄 **COMPLETE PROCESSING WORKFLOW**

### **📥 Step 1: Document Upload & Classification - ENHANCED**

```python
async def process_uploaded_content(file_upload, content_type, metadata):
    """Universal content processing for documents and images"""
    
    if content_type == 'image':
        # NEW: Print quality image processing
        return await process_print_quality_image(file_upload, metadata)
    elif content_type == 'document':
        # Existing document processing
        return await process_uploaded_document(file_upload, metadata)

async def process_print_quality_image(image_upload, metadata):
    """Process technician-uploaded print quality photos"""
    
    # 1. Image validation and preprocessing
    validated_image = await validate_print_image(image_upload)
    if not validated_image.is_valid:
        raise ValueError(f"Invalid image: {validated_image.error_message}")
    
    # 2. Store original image
    image_id = await store_print_quality_image(validated_image, metadata)
    
    # 3. Create processing job for AI analysis
    job_id = await create_quality_analysis_job(image_id, metadata)
    
    # 4. Return immediate response while processing async
    return {
        "image_id": image_id,
        "job_id": job_id,
        "status": "analyzing",
        "estimated_completion": "30-60 seconds"
    }

async def process_uploaded_document(file_upload, metadata):
    # 1. File validation and storage
    file_hash = calculate_file_hash(file_upload.content)
    storage_path = await store_file(file_upload, storage_provider)
    
    # 2. Document type detection
    document_type = detect_document_type(file_upload)
    # Returns: 'cpmd_database', 'service_manual', 'parts_catalog', etc.
    
    # 3. Create processing job
    job_id = await create_processing_job(storage_path, document_type, metadata)
    
    # 4. Return immediate response while processing async
    return {"job_id": job_id, "status": "processing"}
```

### **🧠 Step 2: Content Analysis & Extraction - MULTI-MANUFACTURER**

```python
async def analyze_document_content(file_path, document_type, manufacturer_name):
    """Universal content analysis for all manufacturers"""
    
    if document_type == 'cpmd_database':
        # Only HP has CPMD files
        if manufacturer_name.lower() == 'hp':
            return await process_cpmd_xml(file_path)
        else:
            raise ValueError("CPMD files only available for HP")
    
    elif document_type == 'service_manual':
        # ALL manufacturers use service manuals with embedded error codes
        return await process_service_manual_universal(file_path, manufacturer_name)
    
    elif document_type == 'parts_catalog':
        # ALL manufacturers have parts catalogs
        return await process_parts_catalog_universal(file_path, manufacturer_name)
    
    else:
        return await process_generic_document(file_path, manufacturer_name)

async def process_service_manual_universal(file_path, manufacturer):
    """Extract error codes from ANY manufacturer's service manual"""
    
    # 1. Extract text (OCR if needed)
    manual_text = await extract_text_from_pdf(file_path)
    
    # 2. Manufacturer-specific error code extraction
    error_codes = extract_error_codes_from_manual(manual_text, manufacturer)
    
    # 3. Create semantic chunks with error code metadata
    chunks = create_semantic_chunks(manual_text, error_codes)
    
    # 4. Extract product references
    products = extract_product_references(manual_text, manufacturer)
    
    return {
        'type': 'service_manual',
        'manufacturer': manufacturer,
        'error_codes': error_codes,
        'chunks': chunks,
        'products': products,
        'text_content': manual_text
    }
```

### **💾 Step 3: Structured Data Storage**
```python
async def store_processed_data(analysis_result, document_type):
    # 1. Create master document record
    document_id = await create_document_record(analysis_result)
    
    # 2. Store document-specific data
    if document_type == 'cpmd_database':
        await store_error_codes(analysis_result.error_codes, document_id)
    
    # 3. Create semantic chunks for all document types
    await create_semantic_chunks(analysis_result.chunks, document_id)
    
    # 4. Create intelligent relationships
    await create_document_relationships(document_id, analysis_result)
    
    # 5. Update processing status
    await update_processing_status(document_id, 'completed')
```

### **🔍 Step 4: Search Index Updates**
```python
async def update_search_indexes(document_id):
    # 1. Generate vector embeddings for chunks
    chunks = await get_document_chunks(document_id)
    for chunk in chunks:
        embedding = await generate_embedding(chunk.text_content)
        await update_chunk_embedding(chunk.id, embedding)
    
    # 2. Update full-text search indexes (automatic via PostgreSQL)
    # 3. Update document relationship mappings
    # 4. Refresh materialized views if any
```

---

## ⚙️ **PYTHON CONFIGURATION MAPPING**

## Environment Variables Usage

```python
# Multi-Manufacturer Configuration
SUPPORTED_MANUFACTURERS = os.getenv('SUPPORTED_MANUFACTURERS', 'HP,Canon,Epson,Brother,Xerox').split(',')
ERROR_CODE_NORMALIZATION = os.getenv('ERROR_CODE_NORMALIZATION', 'true').lower() == 'true'
UNIVERSAL_PARTS_LOOKUP = os.getenv('UNIVERSAL_PARTS_LOOKUP', 'true').lower() == 'true'

# Print Quality Analysis Configuration  
IMAGE_ANALYSIS_ENABLED = os.getenv('IMAGE_ANALYSIS_ENABLED', 'true').lower() == 'true'
DEFECT_MODEL = os.getenv('DEFECT_MODEL', 'mobilenet_v2')
CONFIDENCE_THRESHOLD = float(os.getenv('CONFIDENCE_THRESHOLD', '0.85'))
MAX_IMAGE_SIZE = os.getenv('MAX_IMAGE_SIZE', '10MB')
SUPPORTED_IMAGE_FORMATS = os.getenv('SUPPORTED_FORMATS', 'jpg,png,jpeg').split(',')

# AI Model Configuration
EMBEDDING_PROVIDER = os.getenv('EMBEDDING_PROVIDER', 'openai')
EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-3-small')
SIMILARITY_THRESHOLD = float(os.getenv('SIMILARITY_THRESHOLD', '0.7'))

# Storage Configuration
STORAGE_PROVIDER = os.getenv('STORAGE_PROVIDER', 'supabase')
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
```

### **Database Connection Management**
```python
# Supabase Client Setup
supabase_client = create_client(
    supabase_url=SUPABASE_URL,
    supabase_key=SUPABASE_SERVICE_KEY
)

# Direct PostgreSQL for complex operations
db_connection = asyncpg.connect(
    host=DB_HOST,
    port=DB_PORT,
    user=DB_USER,
    password=DB_PASSWORD,
    database=DB_NAME
)
```

---

## 🎯 **SUCCESS METRICS & VALIDATION**

### **Processing Success Criteria**

- **CPMD Files**: Error codes extracted and normalized successfully
- **Service Manuals**: Chapters segmented and cross-references created  
- **Parts Catalogs**: Part numbers extracted with compatibility mapping
- **🖼️ Print Quality Images**: AI defect detection with confidence scores >85%
- **All Files**: Vector embeddings generated for semantic search

### **Data Quality Validation**

```python
# Enhanced validation including image analysis
async def validate_processing_quality(document_id, content_type):
    if content_type == 'image':
        return await validate_image_analysis_quality(document_id)
    else:
        return await validate_document_processing_quality(document_id)

async def validate_image_analysis_quality(image_id):
    """Validate AI analysis quality for print defect detection"""
    checks = {
        'image_stored': await check_image_storage(image_id),
        'defects_detected': await count_detected_defects(image_id) >= 0,  # 0 defects is valid
        'confidence_acceptable': await check_detection_confidence(image_id, min_confidence=0.7),
        'quality_metrics_calculated': await check_quality_metrics(image_id),
        'ai_annotations_generated': await check_annotated_image(image_id),
        'training_data_prepared': await check_training_readiness(image_id)
    }
    
    quality_score = sum(checks.values()) / len(checks)
    return quality_score >= 0.8  # 80% success threshold

async def validate_document_processing_quality(document_id):
    checks = {
        'chunks_created': await count_document_chunks(document_id) > 0,
        'embeddings_generated': await check_chunk_embeddings(document_id),
        'error_codes_extracted': await count_error_codes(document_id) if not image else True,
        'relationships_created': await check_document_relationships(document_id),
        'metadata_complete': await validate_document_metadata(document_id)
    }
    
    quality_score = sum(checks.values()) / len(checks)
    return quality_score >= 0.8  # 80% success threshold
```

---

## 📋 **IMPLEMENTATION CHECKLIST**

### **Phase 1: Interactive Terminal Script (CURRENT)** 🖥️

**Implemented Files:**
- `backend/krai_interactive_processor.py` - Main interactive script
- `backend/config.py` - Configuration management  
- `backend/requirements.txt` - Dependencies
- `backend/.env.example` - Environment template

**Features:**
- [x] Interactive file processing via terminal
- [x] Multi-manufacturer support with interactive selection
- [x] Print quality image analysis with technician feedback
- [x] AI vision integration for defect detection
- [x] Database storage with structured data
- [x] ML training data collection from user feedback

**Usage:**
```bash
cd backend
python krai_interactive_processor.py [file_path]
```

### **Phase 2: Filament Dashboard Integration (UPCOMING)** 🌐

**Planned Implementation:**
- [ ] Web-based upload interface in Filament dashboard
- [ ] Automatic categorization suggestions based on Phase 1 data
- [ ] Drag & drop file upload with progress tracking
- [ ] Batch processing management via web interface
- [ ] Real-time AI analysis status and results display
- [ ] Technician feedback interface for continuous ML improvement

**Integration Strategy:**
- Reuse Phase 1 processing logic as backend API
- Import accumulated training data from Phase 1
- Provide both manual and automatic categorization modes
- Maintain backward compatibility with terminal script

---

**🎯 Dieses Handbuch definiert exakt, wie jedes Datenelement von ALLEN Herstellern UND Print Quality Images verarbeitet und in der erweiterten Tabellen-Architektur gespeichert wird. Ready für die Multi-Manufacturer + AI Vision Python Implementation!**
 
 