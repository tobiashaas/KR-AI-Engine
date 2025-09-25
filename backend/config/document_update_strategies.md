# 📄 Document Update Strategies

## 🎯 **UPDATE-STRATEGIEN FÜR DOKUMENTE**

---

## **1. VOLLSTÄNDIGER ERSATZ (Complete Replacement)**

### ✅ **Vorteile:**
- **Einfach zu implementieren** ✅
- **Konsistente Daten** ✅
- **Keine Konflikte** ✅
- **Schnelle Ausführung** ✅

### ⚠️ **Nachteile:**
- **Verlust der Historie** ⚠️
- **Downtime während Update** ⚠️
- **Verlust von Metadaten** ⚠️

### 🔧 **Implementierung:**
```sql
-- 1. Altes Dokument löschen (CASCADE löscht automatisch alle Chunks, Embeddings, etc.)
DELETE FROM krai_core.documents WHERE file_hash = 'old_hash';

-- 2. Neues Dokument einfügen
INSERT INTO krai_core.documents (file_name, file_hash, storage_path, ...)
VALUES ('new_file.pdf', 'new_hash', 'path/to/new/file', ...);

-- 3. Alle Chunks und Embeddings werden automatisch neu erstellt
```

---

## **2. VERSIONIERTE UPDATES (Versioned Updates)**

### ✅ **Vorteile:**
- **Historie bleibt erhalten** ✅
- **Rollback möglich** ✅
- **Vergleich zwischen Versionen** ✅
- **Audit Trail** ✅

### ⚠️ **Nachteile:**
- **Mehr Speicherplatz** ⚠️
- **Komplexere Logik** ⚠️
- **Performance-Impact** ⚠️

### 🔧 **Implementierung:**
```sql
-- 1. Alte Version als "superseded" markieren
UPDATE krai_core.documents 
SET processing_status = 'superseded'
WHERE file_hash = 'old_hash';

-- 2. Relationship erstellen
INSERT INTO krai_core.document_relationships 
(primary_document_id, secondary_document_id, relationship_type)
VALUES (new_doc_id, old_doc_id, 'supersedes');

-- 3. Neue Version als "active" einfügen
INSERT INTO krai_core.documents (file_name, file_hash, ...)
VALUES ('new_file.pdf', 'new_hash', ...);
```

---

## **3. INTELLIGENTE UPDATES (Intelligent Updates)**

### ✅ **Vorteile:**
- **Nur geänderte Teile werden aktualisiert** ✅
- **Minimaler Speicherverbrauch** ✅
- **Schnelle Updates** ✅
- **Inkrementelle Verarbeitung** ✅

### ⚠️ **Nachteile:**
- **Sehr komplexe Implementierung** ⚠️
- **Diff-Algorithmus erforderlich** ⚠️
- **Fehleranfällig** ⚠️

### 🔧 **Implementierung:**
```sql
-- 1. Chunk-Fingerprints vergleichen
SELECT chunk_index, fingerprint 
FROM krai_intelligence.chunks 
WHERE document_id = 'old_doc_id';

-- 2. Nur geänderte Chunks aktualisieren
UPDATE krai_intelligence.chunks 
SET text_chunk = 'new_content', updated_at = now()
WHERE document_id = 'old_doc_id' AND fingerprint != 'new_fingerprint';

-- 3. Neue Chunks hinzufügen
INSERT INTO krai_intelligence.chunks (document_id, chunk_index, ...)
VALUES ('doc_id', chunk_index, ...);
```

---

## **📊 DATENBANK-SCHEMA FÜR VERSIONEN**

### **Aktuelle Struktur:**
```sql
krai_core.documents:
├── file_hash (UNIQUE) - Identifiziert Dokument eindeutig
├── cpmd_version - HP CPMD Version
├── metadata (jsonb) - Flexible Version-Info
└── document_relationships - Version-Beziehungen

krai_core.document_relationships:
├── relationship_type = 'supersedes' - Neue Version ersetzt alte
├── relationship_type = 'supplements' - Zusätzliche Information
└── relationship_type = 'translation' - Übersetzung
```

---

## **🔍 VERSION-ERKENNUNG IN TEST-DOKUMENTEN**

### **Erkannte Versionen:**
```
📄 HP_E786_SM.pdf
   Version: (leer)
   Manufacturer: hp
   Document Type: service_manual

📄 Lexmark_CX825_CX860_XC8155_XC8160.pdf
   Version: (leer)
   Manufacturer: lexmark
   Document Type: service_manual

📄 HP_E786_CPMD.pdf
   Version: (leer)
   Manufacturer: hp
   Document Type: cpmd_database

📄 KM_4750i_4050i_4751i_4051i_SM.pdf
   Version: (sehr lange Zeichenkette - möglicherweise Datum)
   Manufacturer: konica_minolta
   Document Type: service_manual

📄 KM_C658_C558_C458_C368_C308_C258_SM_EN.pdf
   Version: 4.2
   Manufacturer: konica_minolta
   Document Type: service_manual
```

---

## **💡 EMPFOHLENE STRATEGIE**

### **Für eure Anwendung: VOLLSTÄNDIGER ERSATZ + VERSION-TRACKING**

```python
def update_document(new_file_path, old_file_hash):
    """Update document with complete replacement + version tracking"""
    
    # 1. Altes Dokument finden
    old_doc = get_document_by_hash(old_file_hash)
    
    # 2. Version-Info extrahieren
    new_version = extract_version_from_document(new_file_path)
    
    # 3. Prüfen ob wirklich Update nötig
    if old_doc['cpmd_version'] == new_version:
        return {"status": "no_update_needed", "reason": "same_version"}
    
    # 4. Altes Dokument als "superseded" markieren
    mark_document_superseded(old_doc['id'])
    
    # 5. Neues Dokument einfügen
    new_doc = insert_new_document(new_file_path)
    
    # 6. Relationship erstellen
    create_document_relationship(
        primary_doc_id=new_doc['id'],
        secondary_doc_id=old_doc['id'],
        relationship_type='supersedes'
    )
    
    # 7. Alle Chunks und Embeddings werden automatisch neu erstellt
    return {"status": "updated", "new_doc_id": new_doc['id']}
```

---

## **🎯 VERSION-ERKENNUNG VERBESSERN**

### **Aktuelle Patterns:**
```python
version_patterns = [
    r'version\s+([0-9\.]+)',
    r'ver\s+([0-9\.]+)',
    r'v\s*([0-9\.]+)',
    r'rev\s+([0-9\.]+)',
    r'revision\s+([0-9\.]+)',
    r'edition\s+([0-9\.]+)',
    r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)',  # Standard version
    r'([0-9]+\.[0-9]+[A-Z]?)',         # Version with letter
    r'([A-Z]\d+\.\d+)',                # Letter prefix version
    r'(\d{4}-\d{2}-\d{2})',            # Date format
    r'(\d{2}\.\d{2}\.\d{4})',          # German date format
]
```

### **Erweiterte Version-Erkennung:**
```python
def extract_version_enhanced(text_content):
    """Enhanced version extraction with date support"""
    
    # Standard version patterns
    version_patterns = [...]
    
    # Date patterns (oft als Version verwendet)
    date_patterns = [
        r'(\d{4}-\d{2}-\d{2})',        # 2024-01-15
        r'(\d{2}\.\d{2}\.\d{4})',      # 15.01.2024
        r'(\d{2}/\d{2}/\d{4})',        # 15/01/2024
        r'(\d{4}\.\d{2}\.\d{2})',      # 2024.01.15
    ]
    
    # Check for version patterns first
    for pattern in version_patterns:
        match = re.search(pattern, text_content, re.IGNORECASE)
        if match:
            return match.group(1)
    
    # Check for date patterns
    for pattern in date_patterns:
        match = re.search(pattern, text_content)
        if match:
            return match.group(1)
    
    return None
```

---

## **🚀 FAZIT**

### **Empfohlene Strategie:**
1. **VOLLSTÄNDIGER ERSATZ** für einfache Updates ✅
2. **VERSION-TRACKING** über `document_relationships` ✅
3. **ERWEITERTE VERSION-ERKENNUNG** für Datum-Formate ✅
4. **CASCADE DELETE** für automatische Chunk/Embedding-Updates ✅

### **Vorteile:**
- ✅ **Einfach zu implementieren**
- ✅ **Datenbank bleibt konsistent**
- ✅ **Historie wird erhalten**
- ✅ **Performance bleibt gut**

**Das System ist bereit für Document Updates!** 🎯
