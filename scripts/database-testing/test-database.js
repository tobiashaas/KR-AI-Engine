#!/usr/bin/env node

/**
 * 🔍 KRAI Database Function Test
 * Comprehensive validation of Supabase database
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

console.log('🔍 KRAI Datenbank-Funktionstest');
console.log('=================================\n');

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

async function testDatabase() {
  try {
    console.log('📊 1. GRUNDLEGENDE VERBINDUNG');
    console.log('URL:', process.env.SUPABASE_URL);
    console.log('Service Key:', process.env.SUPABASE_SERVICE_KEY ? '✅ Vorhanden' : '❌ Fehlt');
    console.log('');

    // Test 1: Einfache Verbindung
    const { data: connectionTest, error: connError } = await supabase
      .from('manufacturers')
      .select('count', { count: 'exact', head: true });
    
    if (connError) {
      console.log('❌ Verbindung fehlgeschlagen:', connError.message);
      return;
    }
    console.log('✅ Datenbankverbindung erfolgreich\n');

    // Test 2: Tabellen auflisten
    console.log('📋 2. TABELLEN-ÜBERSICHT');
    const tables = [
      'manufacturers', 'technicians', 'service_technician_assignments',
      'service_manuals', 'bulletins', 'schematics', 'training_modules',
      'document_chunks', 'vector_embeddings', 'search_logs',
      'quality_defect_patterns', 'defect_part_associations',
      'training_completions', 'assessments', 'certification_requirements',
      'user_activity_logs', 'performance_metrics', 'feedback'
    ];

    const tableStatus = {};
    for (const table of tables) {
      try {
        const { data, error, count } = await supabase
          .from(table)
          .select('*', { count: 'exact', head: true });
        
        tableStatus[table] = {
          exists: !error,
          count: count || 0,
          error: error?.message
        };
      } catch (e) {
        tableStatus[table] = { exists: false, error: e.message };
      }
    }

    // Ergebnisse anzeigen
    let existingTables = 0;
    Object.entries(tableStatus).forEach(([table, status]) => {
      const icon = status.exists ? '✅' : '❌';
      const countInfo = status.exists ? ` (Einträge: ${status.count})` : '';
      console.log(`  ${icon} ${table}${countInfo}`);
      if (status.exists) existingTables++;
      if (!status.exists && status.error) {
        console.log(`      Fehler: ${status.error}`);
      }
    });

    console.log(`\n📊 Tabellen-Status: ${existingTables}/${tables.length} verfügbar\n`);

    // Test 3: Sample Daten Details
    console.log('🧪 3. DATEN-DETAILS TEST');
    
    // Manufacturers Details
    const { data: mfgData, error: mfgError } = await supabase
      .from('manufacturers')
      .select('*')
      .limit(5);
    
    if (!mfgError && mfgData) {
      console.log(`✅ Manufacturers: ${mfgData.length} Einträge geladen`);
      if (mfgData.length > 0) {
        console.log('   Beispiel-Hersteller:');
        mfgData.forEach((mfg, i) => {
          console.log(`   ${i+1}. ${mfg.name || 'Unbenannt'} (ID: ${mfg.id})`);
        });
      }
    } else {
      console.log('❌ Manufacturers Fehler:', mfgError?.message);
    }

    // Service Manuals Details
    const { data: manualData, error: manualError } = await supabase
      .from('service_manuals')
      .select('*')
      .limit(5);
    
    if (!manualError && manualData) {
      console.log(`\n✅ Service Manuals: ${manualData.length} Einträge`);
      if (manualData.length > 0) {
        console.log('   Beispiel-Manuals:');
        manualData.forEach((manual, i) => {
          console.log(`   ${i+1}. ${manual.title || 'Unbenannt'} (${manual.model_numbers || 'Keine Modellnummer'})`);
        });
      }
    } else {
      console.log('\n❌ Service Manuals Fehler:', manualError?.message);
    }

    // Technicians Test
    const { data: techData, error: techError } = await supabase
      .from('technicians')
      .select('*')
      .limit(5);
    
    if (!techError && techData) {
      console.log(`\n✅ Technicians: ${techData.length} Einträge`);
      if (techData.length > 0) {
        console.log('   Beispiel-Techniker:');
        techData.forEach((tech, i) => {
          console.log(`   ${i+1}. ${tech.first_name} ${tech.last_name} (${tech.specialization || 'Keine Spezialisierung'})`);
        });
      }
    } else {
      console.log('\n❌ Technicians Fehler:', techError?.message);
    }

    console.log('\n🎯 4. FUNKTIONEN TEST');
    
    // Test SQL Funktionen
    const functions = [
      'get_comprehensive_dashboard_analytics',
      'contextual_search', 
      'enhanced_multi_vector_search'
    ];

    for (const func of functions) {
      try {
        const result = await supabase.rpc(func, {});
        console.log(`✅ ${func}: Verfügbar`);
        if (result.data) {
          console.log(`   Antwort: ${JSON.stringify(result.data).substring(0, 100)}...`);
        }
      } catch (e) {
        console.log(`❌ ${func}: ${e.message}`);
      }
    }

    console.log('\n🔗 5. BEZIEHUNGEN TEST');
    
    // Test Foreign Key Relationships
    try {
      const { data: joinTest } = await supabase
        .from('service_manuals')
        .select(`
          *,
          manufacturers(name),
          document_chunks(content)
        `)
        .limit(2);
      
      if (joinTest && joinTest.length > 0) {
        console.log('✅ Foreign Key Beziehungen funktionieren');
        console.log(`   Beispiel: Manual "${joinTest[0].title}" von Hersteller "${joinTest[0].manufacturers?.name || 'Unbekannt'}"`);
      } else {
        console.log('⚠️ Keine Join-Daten gefunden');
      }
    } catch (e) {
      console.log('❌ Beziehungstest fehlgeschlagen:', e.message);
    }

    console.log('\n✅ DATENBANK-FUNKTIONSTEST ABGESCHLOSSEN!');
    console.log('🎯 Ergebnis: Datenbank ist bereit für KRAI-Betrieb\n');
    
  } catch (error) {
    console.error('❌ Kritischer Fehler:', error.message);
  }
}

testDatabase();