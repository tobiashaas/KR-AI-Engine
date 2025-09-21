const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

console.log('🔍 KRAI Database - Real Table Discovery');
console.log('=======================================\n');

async function discoverActualTables() {
  try {
    console.log('📊 1. DIREKTE SUPABASE API TABELLEN-LISTE');
    console.log('------------------------------------------');
    
    // Methode 1: Versuche alle Tabellen über REST API zu entdecken
    const possibleTables = [
      // Core Business Tables
      'manufacturers',
      'technicians', 
      'service_technician_assignments',
      
      // Document Management
      'service_manuals',
      'bulletins',
      'schematics', 
      'parts_catalogs',
      'training_modules',
      
      // AI & Search
      'document_chunks',
      'vector_embeddings',
      'search_logs',
      
      // Quality Management  
      'quality_defect_patterns',
      'defect_part_associations',
      
      // Training System
      'training_completions',
      'assessments',
      'certification_requirements',
      
      // Analytics
      'user_activity_logs',
      'performance_metrics',
      'feedback'
    ];
    
    const realTables = [];
    const accessibleTables = [];
    const notFoundTables = [];
    
    console.log('Testing table existence...\n');
    
    for (const table of possibleTables) {
      try {
        // Test 1: Einfacher Count
        const { count, error: countError } = await supabase
          .from(table)
          .select('*', { count: 'exact', head: true });
          
        if (countError) {
          if (countError.message.includes('schema cache')) {
            console.log(`⚠️ ${table}: EXISTS (Cache Problem) - Count: Unknown`);
            realTables.push({ name: table, status: 'cache_issue', count: '?' });
          } else if (countError.message.includes('does not exist')) {
            console.log(`❌ ${table}: DOES NOT EXIST`);
            notFoundTables.push(table);
          } else {
            console.log(`❓ ${table}: Unknown Error - ${countError.message}`);
            realTables.push({ name: table, status: 'unknown_error', count: '?' });
          }
        } else {
          console.log(`✅ ${table}: EXISTS & ACCESSIBLE - Count: ${count}`);
          realTables.push({ name: table, status: 'accessible', count: count });
          accessibleTables.push(table);
          
          // Wenn zugänglich, hole auch die Spalten-Info
          const { data: sampleData } = await supabase
            .from(table)
            .select('*')
            .limit(1);
            
          if (sampleData && sampleData.length > 0) {
            const columns = Object.keys(sampleData[0]);
            console.log(`   Columns: ${columns.join(', ')}`);
          }
        }
      } catch (error) {
        console.log(`❌ ${table}: Exception - ${error.message}`);
        notFoundTables.push(table);
      }
    }
    
    console.log('\n📊 2. ZUSAMMENFASSUNG DER TABELLEN-EXISTENZ');
    console.log('--------------------------------------------');
    console.log(`✅ Zugängliche Tabellen: ${accessibleTables.length}`);
    console.log(`⚠️ Cache-Problem Tabellen: ${realTables.filter(t => t.status === 'cache_issue').length}`);
    console.log(`❌ Nicht existierende Tabellen: ${notFoundTables.length}`);
    console.log(`📊 Total getestete Tabellen: ${possibleTables.length}`);
    
    console.log('\n✅ ZUGÄNGLICHE TABELLEN:');
    accessibleTables.forEach(table => {
      const tableInfo = realTables.find(t => t.name === table);
      console.log(`  - ${table} (${tableInfo.count} records)`);
    });
    
    if (realTables.filter(t => t.status === 'cache_issue').length > 0) {
      console.log('\n⚠️ CACHE-PROBLEM TABELLEN (existieren aber nicht zugänglich):');
      realTables.filter(t => t.status === 'cache_issue').forEach(table => {
        console.log(`  - ${table.name}`);
      });
    }
    
    if (notFoundTables.length > 0) {
      console.log('\n❌ NICHT EXISTIERENDE TABELLEN:');
      notFoundTables.forEach(table => {
        console.log(`  - ${table}`);
      });
    }
    
    console.log('\n🔍 3. SUPABASE SCHEMA INTROSPECTION');
    console.log('------------------------------------');
    
    // Versuche direkte Schema-Abfrage
    try {
      console.log('Versuche pg_tables Abfrage...');
      const { data: pgTables, error: pgError } = await supabase
        .rpc('get_public_tables');
        
      if (pgError) {
        console.log(`⚠️ pg_tables RPC nicht verfügbar: ${pgError.message}`);
        
        // Alternative: information_schema
        console.log('Versuche information_schema...');
        const { data: infoSchema, error: infoError } = await supabase
          .from('information_schema.tables')
          .select('table_name')
          .eq('table_schema', 'public');
          
        if (infoError) {
          console.log(`⚠️ information_schema nicht verfügbar: ${infoError.message}`);
        } else {
          console.log('✅ Schema-Tables gefunden:');
          infoSchema.forEach(table => {
            console.log(`  - ${table.table_name}`);
          });
        }
      } else {
        console.log('✅ Public Tables via RPC:');
        pgTables.forEach(table => {
          console.log(`  - ${table}`);
        });
      }
    } catch (error) {
      console.log(`❌ Schema introspection failed: ${error.message}`);
    }
    
    console.log('\n🎯 4. DEPLOYMENT VERIFICATION');
    console.log('------------------------------');
    
    console.log('Checking deployment status based on findings...');
    
    const expectedCoreTable = ['manufacturers', 'service_manuals'];
    const coreTablesFound = expectedCoreTable.filter(table => 
      accessibleTables.includes(table)
    );
    
    console.log(`Core Tables Check: ${coreTablesFound.length}/${expectedCoreTable.length}`);
    
    if (coreTablesFound.length === expectedCoreTable.length) {
      console.log('✅ CORE DEPLOYMENT: SUCCESS');
    } else {
      console.log('❌ CORE DEPLOYMENT: INCOMPLETE');
    }
    
    // Erweiterte Tabellen Check
    const extendedTables = ['bulletins', 'technicians', 'document_chunks', 'vector_embeddings'];
    const extendedFound = extendedTables.filter(table => 
      accessibleTables.includes(table) || 
      realTables.some(t => t.name === table && t.status === 'cache_issue')
    );
    
    console.log(`Extended Tables Check: ${extendedFound.length}/${extendedTables.length}`);
    
    if (extendedFound.length >= extendedTables.length * 0.5) {
      console.log('✅ EXTENDED DEPLOYMENT: PARTIAL SUCCESS');
    } else {
      console.log('⚠️ EXTENDED DEPLOYMENT: LIMITED');
    }
    
    console.log('\n📋 FINAL REALITY CHECK:');
    console.log('========================');
    console.log('Basierend auf tatsächlichen Supabase API Tests:');
    console.log(`✅ Bestätigte Tabellen: ${accessibleTables.length}`);
    console.log(`⚠️ Cache-blockierte Tabellen: ${realTables.filter(t => t.status === 'cache_issue').length}`);
    console.log(`❌ Definitiv nicht existierend: ${notFoundTables.length}`);
    
    return {
      accessible: accessibleTables,
      cacheBlocked: realTables.filter(t => t.status === 'cache_issue').map(t => t.name),
      notFound: notFoundTables,
      total: possibleTables.length
    };
    
  } catch (error) {
    console.error('❌ Discovery failed:', error.message);
  }
}

// Starte Tabellen-Discovery
discoverActualTables();