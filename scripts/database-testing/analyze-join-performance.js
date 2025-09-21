const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

console.log('🔍 KRAI Database - JOIN Performance Analysis');
console.log('Analyzing the slow Multi-table document join (407ms)');
console.log('=====================================================\n');

async function analyzeJoinPerformance() {
  try {
    console.log('📊 1. PROBLEMATIC JOIN ANALYSIS');
    console.log('--------------------------------');
    
    console.log('Die langsame Query war:');
    console.log(`
documents.select(
  id, file_name, manufacturer_id,
  manufacturers (id, name, display_name),
  chunks (id, chunk_index)
).limit(3)
    `);
    
    console.log('\n🔍 2. SCHRITT-FÜR-SCHRITT JOIN ANALYSE');
    console.log('---------------------------------------');
    
    // Test 1: Einfache documents Query
    console.log('Testing: Simple documents query...');
    const start1 = Date.now();
    const { data: docsOnly, error: docsError } = await supabase
      .from('documents')
      .select('id, file_name, manufacturer_id')
      .limit(3);
    const time1 = Date.now() - start1;
    
    if (!docsError) {
      console.log(`✅ Simple documents: ${time1}ms (${docsOnly.length} records)`);
    } else {
      console.log(`❌ Simple documents failed: ${docsError.message}`);
    }
    
    // Test 2: documents + manufacturers JOIN (ohne chunks)
    console.log('\nTesting: Documents + manufacturers JOIN...');
    const start2 = Date.now();
    const { data: docsManuf, error: docsManuError } = await supabase
      .from('documents')
      .select(`
        id,
        file_name,
        manufacturer_id,
        manufacturers (
          id,
          name,
          display_name
        )
      `)
      .limit(3);
    const time2 = Date.now() - start2;
    
    if (!docsManuError) {
      console.log(`✅ Documents+Manufacturers: ${time2}ms (${docsManuf.length} records)`);
    } else {
      console.log(`❌ Documents+Manufacturers failed: ${docsManuError.message}`);
    }
    
    // Test 3: documents + chunks JOIN (ohne manufacturers)
    console.log('\nTesting: Documents + chunks JOIN...');
    const start3 = Date.now();
    const { data: docsChunks, error: docsChunksError } = await supabase
      .from('documents')
      .select(`
        id,
        file_name,
        chunks (
          id,
          chunk_index
        )
      `)
      .limit(3);
    const time3 = Date.now() - start3;
    
    if (!docsChunksError) {
      console.log(`✅ Documents+Chunks: ${time3}ms (${docsChunks.length} records)`);
    } else {
      console.log(`❌ Documents+Chunks failed: ${docsChunksError.message}`);
    }
    
    // Test 4: Der problematische Triple JOIN
    console.log('\nTesting: PROBLEMATIC Triple JOIN...');
    const start4 = Date.now();
    const { data: tripleJoin, error: tripleError } = await supabase
      .from('documents')
      .select(`
        id,
        file_name,
        manufacturer_id,
        manufacturers (
          id,
          name,
          display_name
        ),
        chunks (
          id,
          chunk_index
        )
      `)
      .limit(3);
    const time4 = Date.now() - start4;
    
    if (!tripleError) {
      console.log(`⚠️ Triple JOIN: ${time4}ms (${tripleJoin.length} records)`);
      console.log(`   Problem: ${time4 > 200 ? 'SLOW' : 'ACCEPTABLE'} performance`);
    } else {
      console.log(`❌ Triple JOIN failed: ${tripleError.message}`);
    }

    console.log('\n🧠 3. PERFORMANCE PROBLEM DIAGNOSE');
    console.log('-----------------------------------');
    
    console.log('ANALYSE DER ERGEBNISSE:');
    
    if (time1 && time2 && time3 && time4) {
      console.log(`Simple Query:        ${time1}ms`);
      console.log(`Two-table JOIN:      ${time2}ms`);
      console.log(`Documents+Chunks:    ${time3}ms`);
      console.log(`Triple JOIN:         ${time4}ms`);
      
      console.log('\nPROBLEM IDENTIFIKATION:');
      
      if (time4 > (time2 + time3)) {
        console.log(`🔍 PROBLEM: Triple JOIN ist deutlich langsamer als die Summe der einzelnen JOINs`);
        console.log(`   Erwartet: ~${time2 + time3}ms`);
        console.log(`   Tatsächlich: ${time4}ms`);
        console.log(`   Overhead: ${time4 - (time2 + time3)}ms`);
      }
      
      if (time4 > 200) {
        console.log(`⚠️ PROBLEM: Triple JOIN überschreitet 200ms Performance-Target`);
      }
    }

    console.log('\n🛠️ 4. MÖGLICHE URSACHEN & LÖSUNGEN');
    console.log('-----------------------------------');
    
    console.log('WAHRSCHEINLICHE URSACHEN:');
    console.log('1. 📊 Supabase PostgREST macht separate Queries für jeden JOIN');
    console.log('2. 🔄 Keine optimierten Multi-table JOINs in der API Ebene');
    console.log('3. ⚠️ Network Latency multipliziert sich bei nested JOINs');
    console.log('4. 🗃️ Leere Tabellen können paradoxerweise langsamer sein');
    
    console.log('\nEMPFOHLENE LÖSUNGEN:');
    console.log('✅ 1. SEPARATE QUERIES verwenden statt nested JOINs');
    console.log('✅ 2. VIEWS erstellen für häufige Multi-table Queries');
    console.log('✅ 3. STORED PROCEDURES für komplexe JOINs');
    console.log('✅ 4. MATERIALIZED VIEWS für read-heavy Workloads');

    console.log('\n🚀 5. ALTERNATIVE QUERY STRATEGIEN TESTEN');
    console.log('-----------------------------------------');
    
    // Test Alternative 1: Separate queries
    console.log('Testing: Alternative 1 - Separate queries...');
    const start5 = Date.now();
    
    // Query 1: Get documents
    const { data: docs } = await supabase
      .from('documents')
      .select('id, file_name, manufacturer_id')
      .limit(3);
    
    // Query 2: Get manufacturers (wenn docs exist)
    let manufacturers = [];
    if (docs && docs.length > 0) {
      const manufacturerIds = [...new Set(docs.map(d => d.manufacturer_id).filter(Boolean))];
      if (manufacturerIds.length > 0) {
        const { data: manuData } = await supabase
          .from('manufacturers')
          .select('id, name, display_name')
          .in('id', manufacturerIds);
        manufacturers = manuData || [];
      }
    }
    
    // Query 3: Get chunks (wenn docs exist)
    let chunks = [];
    if (docs && docs.length > 0) {
      const docIds = docs.map(d => d.id);
      const { data: chunkData } = await supabase
        .from('chunks')
        .select('id, chunk_index, document_id')
        .in('document_id', docIds);
      chunks = chunkData || [];
    }
    
    const time5 = Date.now() - start5;
    console.log(`✅ Separate queries strategy: ${time5}ms`);
    console.log(`   Documents: ${docs?.length || 0}`);
    console.log(`   Manufacturers: ${manufacturers.length}`);
    console.log(`   Chunks: ${chunks.length}`);
    
    // Test Alternative 2: Simpler JOIN mit LIMIT
    console.log('\nTesting: Alternative 2 - Limited scope JOIN...');
    const start6 = Date.now();
    const { data: limitedJoin, error: limitedError } = await supabase
      .from('documents')
      .select(`
        id,
        file_name,
        manufacturers (name)
      `)
      .limit(5);
    const time6 = Date.now() - start6;
    
    if (!limitedError) {
      console.log(`✅ Limited scope JOIN: ${time6}ms (${limitedJoin.length} records)`);
    }

    console.log('\n📊 6. PERFORMANCE VERGLEICH');
    console.log('----------------------------');
    
    const strategies = [
      { name: 'Triple JOIN (problematic)', time: time4 },
      { name: 'Separate Queries', time: time5 },
      { name: 'Limited JOIN', time: time6 }
    ].filter(s => s.time);
    
    strategies.sort((a, b) => a.time - b.time);
    
    console.log('PERFORMANCE RANKING:');
    strategies.forEach((strategy, index) => {
      const status = strategy.time < 100 ? '🚀' : strategy.time < 200 ? '✅' : '⚠️';
      console.log(`${index + 1}. ${status} ${strategy.name}: ${strategy.time}ms`);
    });

    console.log('\n💡 7. EMPFEHLUNGEN FÜR PRODUCTION');
    console.log('----------------------------------');
    
    console.log('IMMEDIATE ACTIONS:');
    console.log('1. 🔄 Verwenden Sie SEPARATE QUERIES für komplexe Multi-table Daten');
    console.log('2. 📊 Erstellen Sie VIEWS für häufige JOIN-Patterns');
    console.log('3. ⚡ Nutzen Sie BATCH-Queries für bessere Performance');
    console.log('4. 🎯 Limitieren Sie JOIN-Tiefe auf maximal 2 Ebenen');
    
    console.log('\nLONG-TERM OPTIMIZATIONS:');
    console.log('1. 🗃️ Materialized Views für read-heavy Multi-table Queries');
    console.log('2. 🔧 Stored Procedures für komplexe Business Logic');
    console.log('3. 📈 Caching Layer für frequent JOIN-Results');
    console.log('4. 🧠 Database denormalization für critical read paths');

    console.log('\n✅ JOIN PERFORMANCE ANALYSIS COMPLETE');
    console.log('=====================================');
    console.log('Recommendation: Use separate queries or views for better performance');

  } catch (error) {
    console.error('❌ JOIN analysis failed:', error.message);
  }
}

// Starte JOIN Performance Analyse
analyzeJoinPerformance();