
# 🎯 KRAI-Engine Supabase Deployment Instructions

## Quick Deployment Steps

1. **Open Supabase Dashboard**
   - Go to https://supabase.com/dashboard
   - Select your project: nxzqpobjklqhqkqrvvvl

2. **Access SQL Editor**
   - Click on "SQL Editor" in the left sidebar
   - Click "New Query"

3. **Execute the SQL**
   - Open the file `SUPABASE_DEPLOY.sql`
   - Copy the entire content
   - Paste it into the SQL Editor
   - Click "Run" or press Ctrl+Enter

4. **Verify Deployment**
   - Check the "Table Editor" to see if tables were created
   - Look for tables like: `manufacturers`, `service_manuals`, `bulletins`, etc.
   - Check for any error messages in the SQL Editor

## Expected Results

✅ **Tables Created**: 18 main tables with proper relationships
✅ **Functions Created**: Vector search and utility functions
✅ **Policies Created**: Row Level Security policies
✅ **Indexes Created**: Performance optimization indexes
✅ **Extensions**: Vector extension enabled

## Troubleshooting

- **"already exists" errors**: Normal - means objects were already created
- **Permission errors**: Make sure you're using the service key
- **Vector extension errors**: Extension might need manual enabling
- **Index creation slow**: Large indexes take time - be patient

## After Deployment

1. Test the database connection from your application
2. Upload some test documents
3. Verify the vector search functions work
4. Check the Filament admin panel connectivity

## Manual Steps (if needed)

If some operations fail, you might need to:

```sql
-- Enable vector extension manually
CREATE EXTENSION IF NOT EXISTS vector;

-- Check if tables exist
SELECT table_name FROM information_schema.tables 
WHERE table_schema = 'public' 
ORDER BY table_name;
```

---

**Need help?** Check the deployment log file: `database_deployment.log`
