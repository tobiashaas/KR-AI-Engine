#!/usr/bin/env node

/**
 * 🔧 Supabase Credentials Helper
 * Hilft bei der Konfiguration der richtigen API Keys
 */

console.log(`
🔐 SUPABASE CREDENTIALS SETUP
=============================

❗ PROBLEM: Invalid API key detected!

📋 SO HOLST DU DIE RICHTIGEN KEYS:

1. 🌐 Gehe zu: https://supabase.com/dashboard
2. 📁 Wähle dein Projekt: nxzqpobjklqhqkqrvvvl
3. ⚙️  Klicke auf "Settings" (linke Sidebar)
4. 🔑 Klicke auf "API" 
5. 📋 Kopiere die Keys:

   ┌─────────────────────────────────────────┐
   │ 🔑 Project URL:                         │
   │ https://nxzqpobjklqhqkqrvvvl.supabase.co│
   │                                         │
   │ 🔑 anon / public key:                   │
   │ eyJhbGciOiJIUzI1NiIsInR5c...          │
   │                                         │
   │ 🔑 service_role / secret key:           │
   │ eyJhbGciOiJIUzI1NiIsInR5c...          │
   └─────────────────────────────────────────┘

6. ✏️  Aktualisiere deine .env Datei:

   SUPABASE_URL=https://nxzqpobjklqhqkqrvvvl.supabase.co
   SUPABASE_SERVICE_KEY=<NEUER_SERVICE_KEY>
   SUPABASE_ANON_KEY=<NEUER_ANON_KEY>

7. 🧪 Teste dann mit: npm run test:supabase

📌 WICHTIG:
- Der service_role Key ist für Backend/Server
- Der anon Key ist für Frontend/Client
- Beide Keys müssen aus dem GLEICHEN Projekt sein!

🔄 Nach dem Update kannst du testen mit:
   node test-database.js
`);

// Teste aktuelle Keys
require('dotenv').config();

if (process.env.SUPABASE_URL && process.env.SUPABASE_SERVICE_KEY) {
  console.log('\n🔍 AKTUELLE KONFIGURATION:');
  console.log('URL:', process.env.SUPABASE_URL);
  console.log('Service Key (erste 20 Zeichen):', process.env.SUPABASE_SERVICE_KEY.substring(0, 20) + '...');
  console.log('Anon Key (erste 20 Zeichen):', process.env.SUPABASE_ANON_KEY?.substring(0, 20) + '...');
  
  // JWT Token Info
  try {
    const serviceKeyPayload = JSON.parse(
      Buffer.from(process.env.SUPABASE_SERVICE_KEY.split('.')[1], 'base64').toString()
    );
    console.log('\n🔍 SERVICE KEY INFO:');
    console.log('Rolle:', serviceKeyPayload.role);
    console.log('Projekt Ref:', serviceKeyPayload.ref);
    console.log('Gültig bis:', new Date(serviceKeyPayload.exp * 1000).toLocaleDateString());
    
    if (serviceKeyPayload.ref !== 'nxzqpobjklqhqkqrvvvl') {
      console.log('❌ WARNUNG: Key ist für falsches Projekt!');
    }
    
  } catch (e) {
    console.log('❌ Service Key Format ungültig');
  }
}