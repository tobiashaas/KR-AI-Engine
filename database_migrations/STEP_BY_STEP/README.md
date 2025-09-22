# 🚀 KRAI ENGINE - STEP-BY-STEP DATABASE SETUP

**Complete Database Migration in 7 Organized Steps**  
**Status**: Ready for Execution ✅

---

## 📋 **EXECUTION ORDER**

### **Step 01: Core Schema & Extensions** 
- **File**: `01_core_schema_extensions.sql`
- **Content**: PostgreSQL extensions, manufacturers, products, documents, chunks tables
- **Time**: ~2-3 minutes
- **Dependencies**: None

### **Step 02: Performance & Intelligence Tables**
- **File**: `02_performance_intelligence.sql` 
- **Content**: embeddings, error_codes, images, instructional_videos tables
- **Time**: ~2-3 minutes
- **Dependencies**: Step 01 completed

### **Step 03: Management & Relationship Tables**
- **File**: `03_management_relationships.sql`
- **Content**: document_relationships, product_compatibility, option_groups, processing_queue
- **Time**: ~2-3 minutes  
- **Dependencies**: Step 01-02 completed

### **Step 04: Analytics & Competitive Tables**
- **File**: `04_analytics_competitive.sql`
- **Content**: search_analytics, competitive_features, product_features
- **Time**: ~1-2 minutes
- **Dependencies**: Step 01-03 completed

### **Step 05: Core Functions & Triggers**
- **File**: `05_functions_triggers.sql`
- **Content**: Search functions, validation logic, automation triggers
- **Time**: ~3-5 minutes
- **Dependencies**: Step 01-04 completed

### **Step 06: Security & RLS Policies**
- **File**: `06_security_rls_policies.sql`
- **Content**: Row Level Security, access policies for all user roles
- **Time**: ~2-3 minutes
- **Dependencies**: Step 01-05 completed

### **Step 07: Sample Data & Validation**
- **File**: `07_sample_data_validation.sql`
- **Content**: Test data, complex option rules, validation tests
- **Time**: ~3-5 minutes
- **Dependencies**: Step 01-06 completed

---

## ⚡ **QUICK EXECUTION GUIDE**

### **PowerShell Commands:**
```powershell
# Navigate to migration folder
cd "C:\KRAI-Engine\database_migrations\STEP_BY_STEP"

# Execute each step in order
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 01_core_schema_extensions.sql
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 02_performance_intelligence.sql  
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 03_management_relationships.sql
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 04_analytics_competitive.sql
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 05_functions_triggers.sql
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 06_security_rls_policies.sql
psql -h your-supabase-host -p 5432 -U postgres -d postgres -f 07_sample_data_validation.sql
```

### **Supabase SQL Editor:**
1. Copy content from each file
2. Paste into Supabase SQL Editor  
3. Execute in order (01 → 02 → 03 → 04 → 05 → 06 → 07)
4. Wait for completion confirmation

---

## 🎯 **WHAT GETS CREATED**

### **📊 Final Database Structure:**
- **16 Tables** (optimized architecture)
- **50+ Indexes** (performance optimized)  
- **14 Functions** (search, validation, analytics)
- **Complete RLS Security** (3 access levels)
- **Sample Data** with complex business rules

### **🔍 Key Features:**
- ✅ **HP CPMD + Service Manual Pairing**
- ✅ **Complex Option Dependencies** (Bridge A/B + Finisher X/Y logic)
- ✅ **Fuzzy Error Code Search** with normalization
- ✅ **AI-Optimized Semantic Search** 
- ✅ **Competitive Product Analysis**
- ✅ **Async Processing Queue** for background tasks
- ✅ **Complete Security Policies** for multi-tenant access

### **📈 Expected Performance:**
- **Simple Queries**: <10ms
- **Complex Searches**: 50-200ms  
- **AI Semantic Search**: 100-500ms
- **Option Validation**: 200-800ms

---

## 🔧 **POST-MIGRATION TASKS**

### **After Step 07 Completion:**

1. **Create Vector Index** (after embedding data):
   ```sql
   CREATE INDEX embeddings_hnsw_idx ON public.embeddings 
   USING hnsw (embedding vector_cosine_ops);
   ```

2. **Verify Installation**:
   ```sql
   -- Check table counts
   SELECT 'manufacturers' as table_name, COUNT(*) as rows FROM public.manufacturers
   UNION ALL SELECT 'products', COUNT(*) FROM public.products
   UNION ALL SELECT 'documents', COUNT(*) FROM public.documents
   UNION ALL SELECT 'error_codes', COUNT(*) FROM public.error_codes;
   
   -- Test search function
   SELECT * FROM comprehensive_search('C1234', NULL, NULL, NULL, 5);
   
   -- Test option validation
   SELECT * FROM validate_option_configuration(
     (SELECT id FROM products WHERE name = '9025' AND product_type = 'model'),
     ARRAY[(SELECT id FROM products WHERE name = 'Finisher X')]
   );
   ```

3. **Performance Monitoring**:
   ```sql
   -- Enable query statistics
   SHOW shared_preload_libraries;
   
   -- Monitor slow queries
   SELECT * FROM pg_stat_statements 
   WHERE mean_exec_time > 100 
   ORDER BY mean_exec_time DESC;
   ```

---

## 🚨 **TROUBLESHOOTING**

### **Common Issues:**

#### **Extension Errors (Step 01):**
```sql
-- If vector extension fails
CREATE EXTENSION IF NOT EXISTS vector CASCADE;

-- If permissions error  
GRANT ALL ON SCHEMA public TO postgres;
```

#### **Foreign Key Errors (Step 02-03):**
- **Cause**: Previous steps not completed
- **Solution**: Re-run previous steps first

#### **Function Errors (Step 05):**
```sql
-- If plpgsql not available
CREATE EXTENSION IF NOT EXISTS plpgsql;

-- Check function creation
\df public.*
```

#### **RLS Policy Errors (Step 06):**
```sql
-- If auth schema missing  
CREATE SCHEMA IF NOT EXISTS auth;

-- Check policies
\d+ public.manufacturers
```

---

## ✅ **SUCCESS CONFIRMATION**

### **After Step 07, you should see:**
```
manufacturers: 4 rows
products: 12 rows  
documents: 3 rows
chunks: 2 rows
error_codes: 2 rows
document_relationships: 1 row
product_compatibility: 4 rows
option_groups: 2 rows
competitive_features: 9 rows
product_features: 9 rows
```

### **Validation Tests Should Show:**
- ✅ **Invalid Option Configuration** detected (Finisher X + Bridge B conflict)
- ✅ **Error Code C1234** found via comprehensive search
- ✅ **HP Documentation Set** with CPMD + Service Manual pairing

---

## 🎉 **READY FOR PYTHON DEVELOPMENT**

**Once Step 07 completes successfully:**
- Database is 100% production-ready ✅
- All business logic implemented ✅  
- Security policies active ✅
- Sample data loaded ✅
- Ready for Python script development! 🐍

**Next Phase**: Develop Python processing scripts using this optimized database structure.

---

**🚀 Execute the steps in order and let me know when you're ready for the Python development phase!**