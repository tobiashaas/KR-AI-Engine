#!/usr/bin/env node

/**
 * 🔍 KRAI Schema Direct Query
 * Direkte PostgreSQL Schema-Abfrage um Cache-Probleme zu umgehen
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

console.log('🔍 KRAI Direkte Schema-Abfrage');
console.log('==============================\n');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

async function directSchemaQuery() {
  try {
    console.log('📊 1. ALLE TABELLEN DIREKT ABFRAGEN\n');

    // Direkte SQL-Abfrage über RPC
    const { data: tableList, error: tableError } = await supabase
      .rpc('exec_sql', {
        sql: `
          SELECT 
            table_name,
            table_type
          FROM information_schema.tables 
          WHERE table_schema = 'public' 
          ORDER BY table_name;
        `
      });

    if (tableError) {
      console.log('❌ Direkte SQL nicht verfügbar:', tableError.message);
      console.log('🔄 Verwende alternative Methode...\n');
      
      // Alternative: Teste jede Tabelle einzeln
      const expectedTables = [
        'manufacturers', 'technicians', 'service_technician_assignments',
        'service_manuals', 'bulletins', 'schematics', 'training_modules',
        'document_chunks', 'vector_embeddings', 'search_logs',
        'quality_defect_patterns', 'defect_part_associations',
        'training_completions', 'assessments', 'certification_requirements',
        'user_activity_logs', 'performance_metrics', 'feedback'
      ];

      console.log('📋 TABELLEN-EXISTENZ-TEST:\n');
      
      for (const table of expectedTables) {
        try {
          const { data, error, count } = await supabase
            .from(table)
            .select('*', { count: 'exact', head: true });
          
          if (error) {
            if (error.message.includes('schema cache')) {
              console.log(`⚠️  ${table}: Schema Cache Problem (aber existiert wahrscheinlich)`);
            } else if (error.message.includes('does not exist')) {
              console.log(`❌ ${table}: Existiert NICHT`);
            } else {
              console.log(`🔍 ${table}: ${error.message}`);
            }
          } else {
            console.log(`✅ ${table}: Verfügbar (${count || 0} Einträge)`);
          }
        } catch (e) {
          console.log(`❌ ${table}: Exception - ${e.message}`);
        }
      }

    } else {
      console.log('✅ Gefundene Tabellen:');
      tableList.forEach(table => {
        console.log(`   📋 ${table.table_name} (${table.table_type})`);
      });
    }

    console.log('\n🧪 2. FUNKTIONS-VERFÜGBARE TABELLEN TESTEN\n');
    
    // Diese Tabellen funktionieren basierend auf vorherigem Test
    const workingTables = ['manufacturers', 'service_manuals', 'bulletins', 'quality_defect_patterns'];
    
    for (const table of workingTables) {
      console.log(`🔍 Teste ${table}:`);
      
      // Teste verschiedene Operationen
      try {
        // SELECT Test
        const { data: selectData, error: selectError } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (!selectError) {
          console.log(`   ✅ SELECT funktioniert`);
        } else {
          console.log(`   ❌ SELECT: ${selectError.message}`);
        }

        // COUNT Test
        const { count, error: countError } = await supabase
          .from(table)
          .select('*', { count: 'exact', head: true });
        
        if (!countError) {
          console.log(`   ✅ COUNT funktioniert: ${count} Einträge`);
        } else {
          console.log(`   ❌ COUNT: ${countError.message}`);
        }

      } catch (e) {
        console.log(`   ❌ Exception: ${e.message}`);
      }
      
      console.log('');
    }

    console.log('🔧 3. MANUFACTURERS SCHEMA DETAILS\n');
    
    // Teste verschiedene Felder für manufacturers
    const testFields = ['id', 'name', 'country', 'website', 'support_email', 'created_at'];
    
    for (const field of testFields) {
      try {
        const { data, error } = await supabase
          .from('manufacturers')
          .select(field)
          .limit(1);
        
        if (!error) {
          console.log(`   ✅ Feld '${field}' existiert`);
        } else {
          console.log(`   ❌ Feld '${field}': ${error.message}`);
        }
      } catch (e) {
        console.log(`   ❌ Feld '${field}': Exception`);
      }
    }

    console.log('\n📝 4. EINFACHER INSERT TEST\n');
    
    // Teste minimalen Insert
    console.log('📝 Teste minimalen Hersteller-Insert...');
    const { data: insertData, error: insertError } = await supabase
      .from('manufacturers')
      .insert({
        name: 'Test Hersteller ' + Date.now()
      })
      .select();
    
    if (insertError) {
      console.log('❌ Insert Fehler:', insertError.message);
      
      // Analysiere welche Felder fehlen
      if (insertError.message.includes('violates not-null constraint')) {
        console.log('💡 NOT NULL Constraints aktiv - Schema ist korrekt konfiguriert');
      }
    } else {
      console.log('✅ Insert erfolgreich:', insertData[0]?.name);
      
      // Teste Update
      const { data: updateData, error: updateError } = await supabase
        .from('manufacturers')
        .update({ name: insertData[0].name + ' (Updated)' })
        .eq('id', insertData[0].id)
        .select();
      
      if (!updateError) {
        console.log('✅ Update erfolgreich');
        
        // Teste Delete
        const { error: deleteError } = await supabase
          .from('manufacturers')
          .delete()
          .eq('id', insertData[0].id);
        
        if (!deleteError) {
          console.log('✅ Delete erfolgreich');
        }
      }
    }

    console.log('\n✅ DIREKTE SCHEMA-ANALYSE ABGESCHLOSSEN!\n');
    
  } catch (error) {
    console.error('❌ Kritischer Fehler:', error.message);
  }
}

directSchemaQuery();