#!/usr/bin/env node

/**
 * 🔍 KRAI Schema Analysis
 * Detaillierte Analyse der Datenbankstruktur
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

console.log('🔍 KRAI Schema-Analyse');
console.log('=====================\n');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

async function analyzeSchema() {
  try {
    console.log('📊 DETAILLIERTE TABELLEN-ANALYSE\n');

    const tables = [
      'manufacturers', 'technicians', 'service_technician_assignments',
      'service_manuals', 'bulletins', 'schematics', 'training_modules',
      'document_chunks', 'vector_embeddings', 'search_logs',
      'quality_defect_patterns', 'defect_part_associations',
      'training_completions', 'assessments', 'certification_requirements',
      'user_activity_logs', 'performance_metrics', 'feedback'
    ];

    for (const table of tables) {
      console.log(`🔍 Analysiere: ${table}`);
      
      try {
        // Test Insert (leeres Objekt, um Schema zu sehen)
        const { data, error } = await supabase
          .from(table)
          .insert({})
          .select();
        
        if (error) {
          console.log(`   ❌ Insert-Test: ${error.message}`);
          
          // Analysiere Fehlermeldung für Schema-Info
          if (error.message.includes('violates not-null constraint')) {
            const match = error.message.match(/column "([^"]+)"/);
            if (match) {
              console.log(`   📋 Required Field: ${match[1]}`);
            }
          }
          
          if (error.message.includes('null value in column')) {
            const match = error.message.match(/column "([^"]+)"/);
            if (match) {
              console.log(`   📋 NOT NULL: ${match[1]}`);
            }
          }
        } else {
          console.log(`   ✅ Insert erfolgreich`);
        }

        // Test Select für Schema-Info
        const { data: selectData, error: selectError } = await supabase
          .from(table)
          .select('*')
          .limit(1);
        
        if (!selectError) {
          console.log(`   ✅ Select funktioniert`);
        }

      } catch (e) {
        console.log(`   ❌ Fehler: ${e.message}`);
      }
      
      console.log('');
    }

    console.log('🧪 SAMPLE DATEN EINFÜGEN\n');
    
    // Test: Hersteller einfügen
    console.log('📝 Füge Test-Hersteller hinzu...');
    const { data: mfgData, error: mfgError } = await supabase
      .from('manufacturers')
      .insert({
        name: 'Test Hersteller GmbH',
        country: 'Deutschland',
        website: 'https://test-hersteller.de',
        support_email: 'support@test-hersteller.de',
        support_phone: '+49 123 456789'
      })
      .select();
    
    if (mfgError) {
      console.log('❌ Hersteller Insert Fehler:', mfgError.message);
    } else {
      console.log('✅ Hersteller erfolgreich eingefügt:', mfgData[0]?.name);
      
      // Test: Techniker mit Hersteller-Referenz
      console.log('📝 Füge Test-Techniker hinzu...');
      const { data: techData, error: techError } = await supabase
        .from('technicians')
        .insert({
          first_name: 'Max',
          last_name: 'Mustermann',
          email: 'max.mustermann@test.de',
          phone: '+49 987 654321',
          specialization: 'Hydraulik',
          certification_level: 'senior',
          manufacturer_id: mfgData[0].id
        })
        .select();
      
      if (techError) {
        console.log('❌ Techniker Insert Fehler:', techError.message);
      } else {
        console.log('✅ Techniker erfolgreich eingefügt:', `${techData[0]?.first_name} ${techData[0]?.last_name}`);
        
        // Test: Service Manual
        console.log('📝 Füge Test-Service Manual hinzu...');
        const { data: manualData, error: manualError } = await supabase
          .from('service_manuals')
          .insert({
            title: 'Test Service Manual',
            model_numbers: 'TM-2025-001',
            version: '1.0',
            language: 'de',
            file_size: 1024000,
            file_type: 'pdf',
            content_summary: 'Test-Handbuch für Funktionstest',
            manufacturer_id: mfgData[0].id
          })
          .select();
        
        if (manualError) {
          console.log('❌ Manual Insert Fehler:', manualError.message);
        } else {
          console.log('✅ Service Manual erfolgreich eingefügt:', manualData[0]?.title);
        }
      }
    }

    console.log('\n🔗 BEZIEHUNGEN TESTEN\n');
    
    // Test Join-Query
    const { data: joinData, error: joinError } = await supabase
      .from('service_manuals')
      .select(`
        *,
        manufacturers(name, country)
      `)
      .limit(5);
    
    if (joinError) {
      console.log('❌ Join-Query Fehler:', joinError.message);
    } else {
      console.log('✅ Join-Query erfolgreich');
      if (joinData && joinData.length > 0) {
        joinData.forEach(manual => {
          console.log(`   📖 "${manual.title}" von ${manual.manufacturers?.name || 'Unbekannt'}`);
        });
      }
    }

    console.log('\n✅ SCHEMA-ANALYSE ABGESCHLOSSEN!\n');
    
  } catch (error) {
    console.error('❌ Kritischer Fehler:', error.message);
  }
}

analyzeSchema();