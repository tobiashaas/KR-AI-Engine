# 🚨 KRITISCHE MIGRATION ANWEISUNGEN

## ⚠️ **ALLE 12 DATEIEN MÜSSEN AUSGEFÜHRT WERDEN!**

**NIEMALS nur Teile ausführen!** Dieses Schema besteht aus **12 aufeinanderfolgenden Schritten (00-11)**:

### 📋 **PFLICHTLISTE - ALLE SCHRITTE:**

```bash
# Step 1: Schema Architecture
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 00_schema_architecture.sql

# Step 2: Core Tables
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 01_krai_core_tables.sql

# Step 3: Intelligence Tables  
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 02_krai_intelligence_tables.sql

# Step 4: Content Tables
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 03_krai_content_tables.sql

# Step 5: Config Tables
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 04_krai_config_tables.sql

# Step 6: System Tables
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 05_krai_system_tables.sql

# Step 7: Security RLS Policies
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 06_security_rls_policies.sql

# Step 8: Performance Optimizations
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 07_performance_optimizations.sql

# Step 9: Future Extensions
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 08_future_extensions.sql

# Step 10: Validation Examples
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 09_option_validation_examples.sql

# Step 11: Security Fixes
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 10_security_fixes.sql

# Step 12: Final Performance
docker exec -i supabase_db_KR-AI-Engine psql -U postgres -d postgres < 11_performance_optimization.sql
```

### ✅ **ERFOLGS-VALIDIERUNG:**

Nach der kompletten Migration solltest du haben:
- **10 Schemas**: krai_core, krai_intelligence, krai_content, krai_config, krai_system, krai_ml, krai_parts, krai_service, krai_users, krai_integrations
- **31 Tabellen** total
- **403+ Spalten** total
- **3 Storage Buckets**: krai-documents, krai-images, krai-videos

### 🚨 **KRITISCHE REGEL:**

**NIEMALS EINZELNE SCHRITTE ÜBERSPRINGEN!**

Die Dateien bauen aufeinander auf. Ohne Schritte 06-11 fehlen:
- ❌ Security Policies
- ❌ Performance Indexes
- ❌ Future Schemas (ML, Parts, Service, Users, Integrations)
- ❌ Optimization Fixes

---

**🎯 Erstellt am: $(date)** 
**✅ Status: ALLE 12 SCHRITTE AUSGEFÜHRT**
