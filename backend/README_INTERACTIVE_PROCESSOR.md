# 🖥️ KRAI Interactive Processor
**Terminal-Based Document & Image Processing for Multi-Manufacturer Support**

## 🎯 Überblick

Der KRAI Interactive Processor ist ein Terminal-basiertes Skript für die Verarbeitung von:
- **Multi-manufacturer documents** (HP, Canon, Epson, Brother, Xerox)
- **Print quality images** mit AI Vision Analysis
- **Technician feedback** für ML Training
- **Strukturierte Datenspeicherung** für spätere Filament Dashboard Integration

## 🚀 Quick Start

### 1. Setup

```bash
# Clone repository
cd KRAI-Engine/backend

# Install dependencies
pip install -r requirements.txt

# Copy environment template
cp .env.example .env

# Edit .env with your database credentials
```

### 2. Database Setup

```bash
# Ensure PostgreSQL is running with KRAI Engine database
# Run database migrations first (siehe deploy_sql/)
```

### 3. Run Interactive Processor

```bash
# Single file processing
python krai_interactive_processor.py /path/to/document.pdf

# Interactive mode (file selection)
python krai_interactive_processor.py
```

## 🖼️ Print Quality Analysis Workflow

### Schritt 1: Image Upload Detection
```text
🖼️ Image detected: printer_output.jpg
🏢 Hersteller: [Interactive Selection]
🖨️ Druckermodell: [Auto-complete Input]
```

### Schritt 2: AI Vision Analysis
```text
🤖 AI Vision Analysis läuft...
✅ Detected: Banding (Confidence: 85%)
✅ Detected: Color Issues (Confidence: 72%)
```

### Schritt 3: Technician Feedback
```text
🎯 Stimmen die AI Ergebnisse? [y/N]
➕ Welche Defekte hat die AI übersehen?
⭐ Gesamtqualität des Drucks? [1-5]
```

### Schritt 4: ML Training Data Collection
```text
✅ Training data stored for model improvement
✅ Image analysis completed and stored in database
```

## 📄 Document Processing

### Supported Document Types

1. **CPMD Database Files (.pdf)**
   - HP-specific error code databases
   - Automatic error code extraction
   - Solution mapping

2. **Service Manuals (.pdf)**
   - All manufacturers supported
   - Error code pattern recognition
   - Technical procedure extraction

3. **Parts Catalogs (.pdf)**
   - Part number extraction
   - Product mapping
   - Cross-reference creation

### Interactive Questions

```text
🏢 Hersteller: HP/Canon/Epson/Brother/Xerox/Other
📄 Dokumenttyp: [Auto-detected with confirmation]
🖨️ Produktmodell: [Auto-complete from database]
📅 Jahr: [Optional]
🌍 Sprache: EN/DE/FR/ES
```

## 🗃️ Database Integration

### Automatic Storage
- **documents** table: Document metadata and content
- **chunks** table: Processed text chunks with embeddings  
- **error_codes** table: Extracted error codes and solutions
- **images** table: Print quality images with metadata
- **print_defects** table: AI-detected defects
- **quality_assessments** table: Technician feedback
- **technician_feedback** table: ML training data

### Data Flow
```text
Input File → Interactive Questions → AI Processing → Database Storage → Future Dashboard Integration
```

## 🤖 AI Vision Features

### Computer Vision Models
- **YOLOv8**: Object detection for print defects
- **MobileNet**: Quality assessment scoring
- **Custom Models**: Manufacturer-specific defect patterns

### Defect Categories
- Banding (horizontal lines)
- Streaking (vertical lines/smears)
- Color Issues (wrong colors, color shift)
- Paper Jam damage
- Misalignment
- Smudging
- Fading
- Ghosting
- Spots/Dots
- Registration issues

### ML Training Loop
1. AI detects defects automatically
2. Technician confirms/corrects results
3. Feedback stored as training data
4. Models improve over time
5. Better detection accuracy

## 🔧 Configuration

### Environment Variables (.env)
```bash
# Database
DB_HOST=localhost
DB_NAME=krai_engine
DB_USER=postgres
DB_PASSWORD=your_password

# AI Models
OPENAI_API_KEY=your_key_here
VISION_MODEL_PATH=./models

# Processing
MAX_FILE_SIZE_MB=100
ENABLE_GPU_ACCELERATION=false
```

### Supported File Types
- **PDFs**: Service manuals, parts catalogs, CPMD files
- **Images**: JPG, PNG, BMP, TIFF (print quality samples)

## 📊 Features

### Phase 1 (Current) - Interactive Terminal
- [x] Multi-manufacturer document processing
- [x] Interactive categorization with auto-suggestions
- [x] Print quality image analysis with AI vision
- [x] Technician feedback collection for ML training
- [x] Structured database storage
- [x] Progress tracking and error handling

### Phase 2 (Upcoming) - Filament Dashboard Integration
- [ ] Web-based upload interface
- [ ] Automatic categorization suggestions
- [ ] Batch processing management
- [ ] Real-time AI analysis status
- [ ] Dashboard statistics and monitoring

## 🛠️ Development

### Testing
```bash
# Run with sample files
python krai_interactive_processor.py samples/hp_service_manual.pdf

# Test batch processing (upcoming)
python krai_interactive_processor.py --batch samples/
```

### Debugging
```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python krai_interactive_processor.py
```

## 🎓 Usage Examples

### Example 1: HP Service Manual
```text
📁 File: HP_LaserJet_Pro_4000_Service_Manual.pdf
🏢 Hersteller: HP (auto-detected)
📄 Dokumenttyp: Service Manual (auto-detected)
🖨️ Produktmodell: LaserJet Pro 4000 Series (auto-complete)
🌍 Sprache: EN
✅ Processing complete - 47 error codes extracted
```

### Example 2: Print Quality Image
```text
📁 File: canon_print_defect_sample.jpg  
🏢 Hersteller: Canon
🖨️ Druckermodell: PIXMA TR8500 Series
🖼️ Bildtyp: Defect Sample
🔧 Probleme: [Banding, Color Issues]
👨‍💻 Techniker: Max Mustermann
🤖 AI detected: Banding (85%), Color Issues (72%)
🎯 AI Ergebnisse korrekt? Ja
⭐ Qualität: 2 - Schlecht
✅ ML training data collected
```

## 🔗 Integration mit Filament Dashboard

### Data Export für Dashboard
Alle verarbeiteten Daten werden strukturiert in der Datenbank gespeichert und können später vom Filament Dashboard genutzt werden:

- **Auto-Kategorisierung**: Basierend auf Phase 1 Trainingsdaten
- **Model Suggestions**: Intelligente Produktmodell-Vorschläge  
- **Quality Standards**: Aus Techniker-Feedback abgeleitete Qualitätsstandards
- **Error Pattern Recognition**: Verbesserte Error Code Erkennung

---

**🎯 Ready für Multi-Manufacturer Processing mit AI Vision Integration!**