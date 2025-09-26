# 🚀 KRAI ENGINE - OPTIMIZED SCHEMA ARCHITECTURE

**Professional Schema Separation & Security Implementation**

---

## 🎯 **WARUM SCHEMA-TRENNUNG?**

### ❌ **Probleme des aktuellen Designs:**
- Alle 16 Tabellen im `public` Schema
- Keine logische Trennung der Verantwortlichkeiten
- Schwierige granulare Berechtigungen
- Unübersichtlich bei wachsender Komplexität
- Security-Risiken durch zu breite Zugriffe

### ✅ **Vorteile der neuen Architektur:**
- **Logische Trennung**: Jedes Schema hat klare Verantwortlichkeit
- **Granulare Security**: Rollen-basierte Zugriffskontrolle
- **Bessere Performance**: Optimierte Index-Strategien pro Schema
- **Skalierbarkeit**: Einfache Erweiterung um neue Schemas
- **Wartbarkeit**: Klare Struktur für Entwickler

---

## 🏗️ **SCHEMA-ARCHITEKTUR**

### **📊 KRAI_CORE** - Core Business Data
```sql
krai_core.manufacturers          -- Hersteller-Daten
krai_core.products               -- Produkt-Hierarchie (Series → Model → Options)
krai_core.documents              -- Dokumenten-Metadaten (Service Manuals, Parts Catalogs, CPMD, Bulletins)
krai_core.document_relationships -- Dokument-Beziehungen
```

### **🧠 KRAI_INTELLIGENCE** - AI & Intelligence
```sql
krai_intelligence.chunks              -- Text-Chunks für AI Processing
krai_intelligence.embeddings          -- Vector Embeddings (768D)
krai_intelligence.error_codes         -- Universal Error Code Database
krai_intelligence.search_analytics    -- Search Performance Tracking
```

### **🎥 KRAI_CONTENT** - Content & Media
```sql
krai_content.images                   -- Bilder, Schematics, Diagrams
krai_content.instructional_videos     -- Video-Anleitungen
krai_content.print_defects            -- Print Quality Analysis
krai_content.defect_patterns          -- AI Training Data
```

### **⚙️ KRAI_CONFIG** - Configuration & Rules
```sql
krai_config.product_compatibility     -- Option Compatibility Matrix
krai_config.option_groups            -- Option Group Rules (Exclusive/Required)
krai_config.competitive_features -- Feature Definitions
krai_config.product_features    -- Product Feature Values
```

### **🔧 KRAI_SYSTEM** - System Operations
```sql
krai_system.processing_queue    -- Background Processing Jobs
krai_system.performance_metrics -- System Performance Monitoring
krai_system.audit_log          -- Audit Trail
krai_system.system_health      -- Health Monitoring
```

---

## 🔒 **SECURITY & ROLES**

### **Rollen-Definition:**

#### **🔧 KRAI_SERVICE_ROLE** (Backend API)
- **Zugriff**: ALL schemas, ALL operations
- **Verwendung**: Python FastAPI Backend
- **Berechtigung**: Vollzugriff für Dokumentenverarbeitung

#### **👨‍💼 KRAI_ADMIN_ROLE** (Dashboard Admin)
- **Zugriff**: krai_core, krai_config (Read/Write), andere (Read-Only)
- **Verwendung**: Laravel Filament Admin Dashboard
- **Berechtigung**: Verwaltung von Produkten, Dokumenten, Konfiguration

#### **📊 KRAI_ANALYST_ROLE** (Analytics)
- **Zugriff**: krai_intelligence, krai_content (Read-Only)
- **Verwendung**: Business Intelligence, Analytics Dashboard
- **Berechtigung**: Nur Lesezugriff auf Analytics und Content

#### **🔧 KRAI_TECHNICIAN_ROLE** (Service Techniker)
- **Zugriff**: krai_core, krai_content (Read-Only)
- **Verwendung**: Service Interface für Techniker
- **Berechtigung**: Dokumente lesen, Bilder/Videos ansehen

---

## 📋 **MIGRATION-STRATEGIE**

### **Phase 1: Schema Setup** ✅
```bash
# 1. Schema-Architektur erstellen
psql -f 00_schema_architecture.sql

# 2. Core Tables erstellen
psql -f 01_krai_core_tables.sql

# 3. Intelligence Tables erstellen
psql -f 02_krai_intelligence_tables.sql

# 4. Content Tables erstellen
psql -f 03_krai_content_tables.sql

# 5. Config Tables erstellen
psql -f 04_krai_config_tables.sql

# 6. System Tables erstellen
psql -f 05_krai_system_tables.sql

# 7. Security & RLS Policies
psql -f 06_security_rls_policies.sql

# 8. Performance Optimizations
psql -f 07_performance_optimizations.sql

# 9. AI Agent Functions
psql -f 09_option_validation_examples.sql
```

### **Phase 2: Post-Migration Optimization** ✅
```bash
# 10. Security Fixes (Function Search Paths, Extensions)
psql -f 10_security_fixes.sql

# 11. Performance Optimization (Index Cleanup)
psql -f 11_performance_optimization.sql
```

### **Phase 2: Data Migration** (Falls vorhanden)
```sql
-- Daten von public Schema migrieren (falls bereits vorhanden)
INSERT INTO krai_core.manufacturers SELECT * FROM public.manufacturers;
INSERT INTO krai_core.products SELECT * FROM public.products;
-- ... weitere Migrations
```

### **Phase 3: Security Setup**
```sql
-- RLS Policies pro Schema
-- User-Rollen zuweisen
-- Test-Zugriffe validieren
```

### **Phase 4: Performance Optimization**
```sql
-- HNSW Vector Index erstellen (nach Datenimport)
CREATE INDEX CONCURRENTLY idx_embeddings_hnsw 
ON krai_intelligence.embeddings USING hnsw (embedding vector_cosine_ops);
```

---

## 🚀 **PERFORMANCE-VERBESSERUNGEN**

### **1. Spezialisierte Indexes pro Schema:**

#### **KRAI_CORE:**
```sql
-- Optimierte Composite Indexes
CREATE INDEX CONCURRENTLY idx_products_hierarchy_optimized 
ON krai_core.products(manufacturer_id, product_type, is_active) 
WHERE is_active = true;

-- Partial Index für aktive Dokumente
CREATE INDEX CONCURRENTLY idx_documents_active 
ON krai_core.documents(manufacturer_id, document_type) 
WHERE processing_status = 'completed';
```

#### **KRAI_INTELLIGENCE:**
```sql
-- Vector Index für Embeddings
CREATE INDEX CONCURRENTLY idx_embeddings_hnsw 
ON krai_intelligence.embeddings USING hnsw (embedding vector_cosine_ops);

-- Spezialisierte Error Code Suche
CREATE INDEX CONCURRENTLY idx_error_codes_fuzzy 
ON krai_intelligence.error_codes USING GIN (error_code gin_trgm_ops);
```

#### **KRAI_CONFIG:**
```sql
-- Compatibility Matrix Index
CREATE INDEX CONCURRENTLY idx_compatibility_optimized 
ON krai_config.product_compatibility(base_product_id, is_compatible) 
WHERE is_compatible = true;
```

### **2. Query Performance:**

#### **Cross-Schema Queries optimieren:**
```sql
-- Beispiel: Comprehensive Search über mehrere Schemas
SELECT 
  c.text_chunk,
  d.file_name,
  e.error_code,
  p.display_name
FROM krai_intelligence.chunks c
JOIN krai_core.documents d ON d.id = c.document_id
LEFT JOIN krai_intelligence.error_codes e ON e.chunk_id = c.id
LEFT JOIN krai_core.products p ON p.id = ANY(d.product_ids)
WHERE c.text_chunk @@ plainto_tsquery('english', 'paper jam');
```

---

## 🔍 **MONITORING & ANALYTICS**

### **Schema-Performance Monitoring:**
```sql
-- Schema-übergreifende Performance View
CREATE VIEW krai_system.schema_performance AS
SELECT 
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch,
    n_tup_ins,
    n_tup_upd,
    n_tup_del
FROM pg_stat_user_tables 
WHERE schemaname LIKE 'krai_%'
ORDER BY schemaname, tablename;
```

### **Storage Monitoring:**
```sql
-- Schema Storage Usage
SELECT 
    schemaname,
    pg_size_pretty(SUM(pg_total_relation_size(schemaname||'.'||tablename))) as total_size
FROM pg_tables 
WHERE schemaname LIKE 'krai_%'
GROUP BY schemaname
ORDER BY SUM(pg_total_relation_size(schemaname||'.'||tablename)) DESC;
```

---

## ✅ **VOR- UND NACHTEILE**

### **✅ Vorteile:**
- **Bessere Organisation**: Klare logische Trennung
- **Granulare Security**: Rollen-basierte Zugriffe
- **Performance**: Optimierte Index-Strategien
- **Skalierbarkeit**: Einfache Erweiterung
- **Wartbarkeit**: Klare Struktur für Entwickler
- **Security**: Minimale Berechtigungen pro Rolle

### **⚠️ Nachteile:**
- **Komplexität**: Mehr Schemas zu verwalten
- **Cross-Schema Queries**: Können komplexer werden
- **Migration**: Bestehende Daten müssen migriert werden
- **Lernkurve**: Entwickler müssen neue Struktur verstehen

---

## 🎯 **EMPFEHLUNG**

**JA, definitiv implementieren!** Die Schema-Trennung bringt erhebliche Vorteile:

1. **Professionelle Architektur** für Enterprise-Umgebung
2. **Bessere Security** durch granulare Berechtigungen  
3. **Performance-Optimierung** durch spezialisierte Indexes
4. **Skalierbarkeit** für zukünftige Erweiterungen
5. **Wartbarkeit** durch klare Struktur

**Nächster Schritt**: Migration in Supabase ausführen und testen!
