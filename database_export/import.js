const { createClient } = require('@supabase/supabase-js');
const fs = require('fs');
require('dotenv').config();

console.log('🚀 KRAI Database Node.js Import');
console.log('===============================\n');

async function importDatabase() {
  const supabase = createClient(
    process.env.SUPABASE_URL,
    process.env.SUPABASE_SERVICE_KEY
  );

  try {
    console.log('📊 Reading schema file...');
    const schema = fs.readFileSync('./database_export/01_schema.sql', 'utf8');
    
    console.log('🔧 Reading indexes file...');
    const indexes = fs.readFileSync('./database_export/03_indexes.sql', 'utf8');
    
    console.log('📊 Reading data file...');
    const data = fs.readFileSync('./database_export/02_data.sql', 'utf8');
    
    console.log('⚠️ NOTE: For full import, use the bash script or run SQL files directly.');
    console.log('This Node.js script is for verification and simple operations only.');
    
    // Test connection
    const { data: testData, error } = await supabase
      .from('manufacturers')
      .select('count')
      .limit(1);
      
    if (error) {
      console.log('❌ Database connection failed:', error.message);
      console.log('💡 Make sure your .env file has correct Supabase credentials');
    } else {
      console.log('✅ Database connection successful!');
    }
    
  } catch (error) {
    console.error('❌ Import failed:', error.message);
  }
}

importDatabase();
