#!/usr/bin/env node

/**
 * 🔍 KRAI Vector & Functions Test
 * Teste Vector Search und SQL-Funktionen
 */

const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(process.env.SUPABASE_URL, process.env.SUPABASE_SERVICE_KEY);

async function testVectorAndFunctions() {
  console.log('🔍 KRAI Vector Search & Functions Test');
  console.log('====================================\n');

  console.log('🔤 1. SQL FUNKTIONEN TESTEN\n');
  
  const functions = [
    'get_comprehensive_dashboard_analytics',
    'contextual_search',
    'enhanced_multi_vector_search'
  ];

  for (const func of functions) {
    try {
      console.log(`🧪 Teste ${func}...`);
      const result = await supabase.rpc(func, {});
      
      if (result.error) {
        console.log(`   ❌ Fehler: ${result.error.message}`);
      } else {
        console.log(`   ✅ Funktion verfügbar`);
        console.log(`   📊 Antwort-Typ: ${typeof result.data}`);
        if (result.data) {
          const preview = JSON.stringify(result.data).substring(0, 150);
          console.log(`   📋 Vorschau: ${preview}...`);
        }
      }
    } catch (e) {
      console.log(`   ❌ Exception: ${e.message}`);
    }
    console.log('');
  }

  console.log('🧪 2. VECTOR EMBEDDINGS TESTEN\n');
  
  try {
    console.log('📝 Teste Vector Embeddings Insert...');
    
    // Erstelle Test-Embedding (384 Dimensionen für sentence-transformers)
    const testEmbedding = Array.from({length: 384}, () => Math.random() - 0.5);
    
    const { data: vectorData, error: vectorError } = await supabase
      .from('vector_embeddings')
      .insert({
        content: 'Test content für Vector Search',
        embedding: JSON.stringify(testEmbedding),
        source_table: 'test',
        source_id: '00000000-0000-0000-0000-000000000000'
      })
      .select();
    
    if (vectorError) {
      console.log('❌ Vector Insert Fehler:', vectorError.message);
      
      // Teste alternative Vector-Formate
      console.log('🔄 Teste alternatives Vector-Format...');
      
      const { data: altVectorData, error: altVectorError } = await supabase
        .from('vector_embeddings')
        .insert({
          content: 'Test content',
          embedding: testEmbedding,  // Als Array
          source_table: 'test',
          source_id: '00000000-0000-0000-0000-000000000000'
        })
        .select();
      
      if (altVectorError) {
        console.log('❌ Alternative Vector Format:', altVectorError.message);
      } else {
        console.log('✅ Vector mit Array-Format erfolgreich!');
      }
      
    } else {
      console.log('✅ Vector Embedding erfolgreich eingefügt!');
      console.log(`   🆔 ID: ${vectorData[0]?.id}`);
    }
    
  } catch (e) {
    console.log('❌ Vector Test Exception:', e.message);
  }

  console.log('\n📊 3. DASHBOARD ANALYTICS DETAILTEST\n');
  
  try {
    const { data: analytics, error: analyticsError } = await supabase
      .rpc('get_comprehensive_dashboard_analytics');
    
    if (analyticsError) {
      console.log('❌ Analytics Fehler:', analyticsError.message);
    } else {
      console.log('✅ Dashboard Analytics erfolgreich!');
      console.log('📋 Analytics Daten:');
      console.log(JSON.stringify(analytics, null, 2));
    }
  } catch (e) {
    console.log('❌ Analytics Exception:', e.message);
  }

  console.log('\n🧪 4. SAMPLE DATEN EINTRÄGE ERSTELLEN\n');
  
  try {
    // Erstelle Test-Hersteller
    console.log('📝 Erstelle Test-Hersteller...');
    const { data: mfgData, error: mfgError } = await supabase
      .from('manufacturers')
      .insert({
        name: 'KRAI Test Hersteller GmbH',
        website: 'https://test.example.com'
      })
      .select();
    
    if (mfgError) {
      console.log('❌ Hersteller Fehler:', mfgError.message);
    } else {
      console.log(`✅ Hersteller erstellt: ${mfgData[0].name}`);
      
      // Erstelle Test Service Manual
      console.log('📝 Erstelle Test Service Manual...');
      const { data: manualData, error: manualError } = await supabase
        .from('service_manuals')
        .insert({
          title: 'KRAI Test Service Manual',
          model_numbers: 'KR-2025-001',
          version: '1.0',
          language: 'de',
          file_size: 1024000,
          file_type: 'pdf',
          content_summary: 'Test-Manual für KRAI System',
          manufacturer_id: mfgData[0].id
        })
        .select();
      
      if (manualError) {
        console.log('❌ Manual Fehler:', manualError.message);
      } else {
        console.log(`✅ Service Manual erstellt: ${manualData[0].title}`);
        
        // Teste Join-Query
        console.log('🔗 Teste Join-Query...');
        const { data: joinData, error: joinError } = await supabase
          .from('service_manuals')
          .select(`
            title,
            model_numbers,
            manufacturers(name)
          `)
          .eq('id', manualData[0].id);
        
        if (joinError) {
          console.log('❌ Join Fehler:', joinError.message);
        } else {
          console.log('✅ Join Query erfolgreich!');
          console.log(`   📖 "${joinData[0].title}" von ${joinData[0].manufacturers?.name}`);
        }
      }
    }
    
  } catch (e) {
    console.log('❌ Sample Daten Exception:', e.message);
  }

  console.log('\n✅ VECTOR & FUNCTIONS TEST ABGESCHLOSSEN!\n');
}

testVectorAndFunctions();