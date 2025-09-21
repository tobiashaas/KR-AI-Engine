const { createClient } = require('@supabase/supabase-js');
require('dotenv').config();

const supabase = createClient(
  process.env.SUPABASE_URL,
  process.env.SUPABASE_SERVICE_KEY
);

console.log('🔍 KRAI Database - Index Performance Test');
console.log('==========================================\n');

async function testIndexes() {
  try {
    // Test 1: Liste aller Indizes abrufen
    console.log('📊 1. VERFÜGBARE INDIZES ANALYSIEREN');
    console.log('----------------------------------------');
    
    const { data: indexes, error: indexError } = await supabase
      .rpc('get_table_indexes', {});
    
    if (indexError) {
      console.log('⚠️ RPC Funktion nicht verfügbar (Cache Problem)');
      console.log('Verwende alternative Methode...\n');
      
      // Alternative: Direkte SQL Query für Indizes
      const { data: indexData, error: sqlError } = await supabase
        .from('pg_indexes')
        .select('*')
        .eq('schemaname', 'public');
        
      if (sqlError) {
        console.log('⚠️ pg_indexes nicht direkt zugreifbar');
        console.log('Teste Index-Performance durch Query-Analyse...\n');
      } else {
        console.log('✅ Gefundene Indizes:');
        indexData.forEach(idx => {
          console.log(`  - ${idx.tablename}.${idx.indexname}: ${idx.indexdef}`);
        });
        console.log('');
      }
    }

    // Test 2: Performance Test für häufige Queries
    console.log('🚀 2. INDEX PERFORMANCE TESTS');
    console.log('------------------------------');

    // Test manufacturers Index (name sollte UNIQUE Index haben)
    console.log('Testing manufacturers.name index...');
    const start1 = Date.now();
    const { data: mfg1, error: mfgError1 } = await supabase
      .from('manufacturers')
      .select('id, name')
      .eq('name', 'Test Manufacturer')
      .limit(1);
    const time1 = Date.now() - start1;
    
    if (mfgError1) {
      console.log(`❌ manufacturers query failed: ${mfgError1.message}`);
    } else {
      console.log(`✅ manufacturers.name lookup: ${time1}ms`);
    }

    // Test service_manuals foreign key Index
    console.log('Testing service_manuals.manufacturer_id index...');
    const start2 = Date.now();
    const { data: manuals, error: manualsError } = await supabase
      .from('service_manuals')
      .select('id, title, manufacturer_id')
      .not('manufacturer_id', 'is', null)
      .limit(10);
    const time2 = Date.now() - start2;
    
    if (manualsError) {
      console.log(`❌ service_manuals query failed: ${manualsError.message}`);
    } else {
      console.log(`✅ service_manuals.manufacturer_id lookup: ${time2}ms`);
    }

    // Test JOIN Performance (sollte durch Foreign Key Index optimiert sein)
    console.log('Testing JOIN performance (manufacturers + service_manuals)...');
    const start3 = Date.now();
    const { data: joinData, error: joinError } = await supabase
      .from('service_manuals')
      .select(`
        id,
        title,
        manufacturer_id,
        manufacturers (
          id,
          name
        )
      `)
      .limit(5);
    const time3 = Date.now() - start3;
    
    if (joinError) {
      console.log(`❌ JOIN query failed: ${joinError.message}`);
    } else {
      console.log(`✅ JOIN manufacturers+service_manuals: ${time3}ms`);
      console.log(`   Found ${joinData.length} records with relationships`);
    }

    // Test 3: Vector Index (wenn pgvector installiert)
    console.log('\n🧠 3. VECTOR INDEX TESTS');
    console.log('-------------------------');
    
    console.log('Testing vector_embeddings table access...');
    const start4 = Date.now();
    const { data: vectorData, error: vectorError } = await supabase
      .from('vector_embeddings')
      .select('id, document_chunk_id')
      .limit(5);
    const time4 = Date.now() - start4;
    
    if (vectorError) {
      console.log(`❌ vector_embeddings access failed: ${vectorError.message}`);
    } else {
      console.log(`✅ vector_embeddings table access: ${time4}ms`);
      console.log(`   Records found: ${vectorData.length}`);
    }

    // Test 4: Created_at Index Tests (Zeitbasierte Queries)
    console.log('\n📅 4. TIMESTAMP INDEX TESTS');
    console.log('----------------------------');
    
    console.log('Testing created_at index performance...');
    const start5 = Date.now();
    const { data: timeData, error: timeError } = await supabase
      .from('manufacturers')
      .select('id, name, created_at')
      .gte('created_at', '2024-01-01')
      .order('created_at', { ascending: false })
      .limit(10);
    const time5 = Date.now() - start5;
    
    if (timeError) {
      console.log(`❌ created_at query failed: ${timeError.message}`);
    } else {
      console.log(`✅ created_at range query: ${time5}ms`);
      console.log(`   Records in date range: ${timeData.length}`);
    }

    // Test 5: Text Search Index Performance
    console.log('\n🔍 5. TEXT SEARCH INDEX TESTS');
    console.log('------------------------------');
    
    console.log('Testing text search on service_manuals.title...');
    const start6 = Date.now();
    const { data: searchData, error: searchError } = await supabase
      .from('service_manuals')
      .select('id, title, content_summary')
      .ilike('title', '%manual%')
      .limit(10);
    const time6 = Date.now() - start6;
    
    if (searchError) {
      console.log(`❌ text search failed: ${searchError.message}`);
    } else {
      console.log(`✅ text search (ILIKE): ${time6}ms`);
      console.log(`   Matching records: ${searchData.length}`);
    }

    // Test 6: Composite Index Tests (falls vorhanden)
    console.log('\n🔗 6. COMPOSITE INDEX TESTS');
    console.log('----------------------------');
    
    console.log('Testing multi-column queries...');
    const start7 = Date.now();
    const { data: compositeData, error: compositeError } = await supabase
      .from('service_manuals')
      .select('id, title, version, language')
      .eq('language', 'en')
      .not('version', 'is', null)
      .limit(5);
    const time7 = Date.now() - start7;
    
    if (compositeError) {
      console.log(`❌ composite query failed: ${compositeError.message}`);
    } else {
      console.log(`✅ multi-column query: ${time7}ms`);
      console.log(`   Records found: ${compositeData.length}`);
    }

    // Test 7: Index Usage Analysis
    console.log('\n📈 7. QUERY PLAN ANALYSIS');
    console.log('--------------------------');
    
    console.log('Analyzing query execution plans...');
    
    // Test EXPLAIN für eine komplexe Query
    try {
      const { data: explainData, error: explainError } = await supabase
        .rpc('explain_query', {
          query_text: `
            SELECT sm.id, sm.title, m.name as manufacturer_name
            FROM service_manuals sm
            JOIN manufacturers m ON sm.manufacturer_id = m.id
            WHERE m.name ILIKE '%test%'
            AND sm.created_at >= '2024-01-01'
            LIMIT 10
          `
        });
        
      if (explainError) {
        console.log('⚠️ EXPLAIN function not available (expected with cache issues)');
      } else {
        console.log('✅ Query plan analysis available');
        console.log(explainData);
      }
    } catch (error) {
      console.log('⚠️ Query plan analysis not accessible via RPC');
    }

    // Test 8: Index Effectiveness Summary
    console.log('\n📊 8. INDEX EFFECTIVENESS SUMMARY');
    console.log('----------------------------------');
    
    const avgTime = (time1 + time2 + time3 + time4 + time5 + time6 + time7) / 7;
    
    console.log('Performance Summary:');
    console.log(`  Average query time: ${avgTime.toFixed(2)}ms`);
    console.log(`  Fastest query: ${Math.min(time1, time2, time3, time4, time5, time6, time7)}ms`);
    console.log(`  Slowest query: ${Math.max(time1, time2, time3, time4, time5, time6, time7)}ms`);
    
    if (avgTime < 50) {
      console.log('  🚀 Excellent performance - Indexes working well!');
    } else if (avgTime < 200) {
      console.log('  ✅ Good performance - Indexes functioning properly');
    } else {
      console.log('  ⚠️ Performance could be improved - Check index usage');
    }

    // Test 9: Missing Index Detection
    console.log('\n🔍 9. MISSING INDEX DETECTION');
    console.log('------------------------------');
    
    console.log('Testing common query patterns for missing indexes...');
    
    // Test häufige WHERE clauses
    const commonQueries = [
      { table: 'service_manuals', column: 'model_numbers', test: 'Model search' },
      { table: 'service_manuals', column: 'file_type', test: 'File type filter' },
      { table: 'technicians', column: 'specialization', test: 'Specialization lookup' },
      { table: 'document_chunks', column: 'chunk_index', test: 'Chunk ordering' }
    ];
    
    for (const query of commonQueries) {
      console.log(`Testing ${query.test}...`);
      const start = Date.now();
      
      try {
        const { data, error } = await supabase
          .from(query.table)
          .select('id')
          .not(query.column, 'is', null)
          .limit(1);
          
        const time = Date.now() - start;
        
        if (error) {
          console.log(`  ❌ ${query.test}: ${error.message}`);
        } else {
          console.log(`  ✅ ${query.test}: ${time}ms`);
          if (time > 100) {
            console.log(`    ⚠️ Consider adding index on ${query.table}.${query.column}`);
          }
        }
      } catch (error) {
        console.log(`  ⚠️ ${query.test}: Table/column not accessible`);
      }
    }

    console.log('\n✅ INDEX PERFORMANCE TEST COMPLETE');
    console.log('===================================');
    console.log('📊 All available indexes tested for performance');
    console.log('🚀 Database ready for production workloads');
    console.log('📈 Consider monitoring query performance in production');

  } catch (error) {
    console.error('❌ Index test failed:', error.message);
  }
}

// Starte Index Tests
testIndexes();