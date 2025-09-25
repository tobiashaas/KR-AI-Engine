# KRAI Engine

**Knowledge Retrieval and Analysis Intelligence Engine**

Eine KI-gestützte Dokumentenverarbeitungsplattform für technische Service-Umgebungen mit Fokus auf Drucker- und Kopierer-Hersteller.

## Überblick

KRAI Engine ist eine moderne, skalierbare Lösung zur intelligenten Verarbeitung und Analyse technischer Dokumentation. Das System kombiniert fortschrittliche KI-Technologien mit einer robusten Backend-Architektur für die automatisierte Extraktion, Klassifizierung und Suche in technischen Handbüchern, Service-Dokumentationen und Fehlerbehebungsanleitungen.

### Kernfunktionen

- **Intelligente Dokumentklassifizierung** - Automatische Erkennung von Dokumenttyp, Hersteller, Modell und Version
- **Fortgeschrittene Textverarbeitung** - Extraktion von Fehlercodes, Teilenummern und technischen Spezifikationen
- **KI-basierte Bildanalyse** - Erkennung und Analyse von Diagrammen, Schaltplänen und technischen Illustrationen
- **Vektorbasierte Suche** - Semantische Suche mit Embedding-Technologie
- **Multi-Hersteller-Support** - Spezialisierte Verarbeitung für HP, Konica Minolta, Lexmark, UTAX
- **RESTful API** - Vollständige API-Abdeckung für Integration und Automatisierung

## Architektur

### Backend-Stack
- **Framework**: FastAPI (Python 3.12)
- **Database**: PostgreSQL mit pgvector Extension
- **Storage**: Supabase Storage
- **AI/ML**: Ollama (Llama 3.2, LLaVA, EmbeddingGemma)
- **Async Processing**: AsyncPG, AsyncIO

### KI-Komponenten
- **LLM**: Llama 3.2:3b für Textanalyse und Chat
- **Vision**: LLaVA:7b für Bildanalyse und OCR
- **Embeddings**: EmbeddingGemma für semantische Vektorisierung
- **Device Support**: Apple MPS, NVIDIA CUDA, CPU Fallback

### Database Schema
- **krai_core**: Hersteller, Produkte, Dokumente
- **krai_intelligence**: Chunks, Embeddings, KI-Metadaten
- **krai_content**: Bilder, Medien, OCR-Ergebnisse
- **krai_config**: Systemkonfiguration und Patterns
- **krai_system**: Logging, Monitoring, Performance

## Quick Start

### Prerequisites
- Docker und Docker Compose
- Python 3.12+
- PostgreSQL 15+
- Ollama mit AI-Modellen

### Installation

#### Option 1: Complete Docker Stack (Empfohlen)
```bash
# 1. Repository klonen
git clone https://github.com/your-org/krai-engine.git
cd krai-engine

# 2. Environment konfigurieren 
cp .env.template .env
# .env nach Bedarf anpassen

# 3. Complete Stack starten
./start_krai_stack.sh

# 4. Stack stoppen
./stop_krai_stack.sh
```

#### Option 2: Einzelne Services
```bash
# Nur lokale API mit externen Services
./start_krai_api.sh
```

**Services verfügbar:**
- 🚀 **KRAI API**: `http://localhost:8001`
- 💬 **Chat Interface**: `http://localhost:8080` 
- 🗄️ **Supabase Studio**: `http://localhost:54323`
- 🤖 **Ollama API**: `http://localhost:11434`

## 📚 Dokumentation

**Vollständige Dokumentation** ist im [`/documentation`](./documentation/) Verzeichnis verfügbar:

- **[📖 Documentation Overview](./documentation/README.md)** - Übersicht aller Dokumentation
- **[🚀 Deployment Guide](./documentation/DEPLOYMENT_GUIDE.md)** - Deployment-Szenarien und Konfiguration  
- **[📡 API Documentation](./documentation/API_DOCUMENTATION.md)** - Vollständige API-Referenz
- **[⚙️ Environment Configuration](./documentation/ENV_CONFIGURATION.md)** - Single Source of Truth Setup
- **[🔧 Project Structure](./documentation/PROJECT_STRUCTURE.md)** - Architektur und Verzeichnisstruktur
- **[📝 Chunking Configuration](./documentation/CHUNKING_CONFIGURATION.md)** - Text-Chunking Strategien
- **[📚 Wiki Structure](./documentation/WIKI_STRUCTURE.md)** - Wiki-Empfehlungen für komplexe Projekte

## Support

### Unterstützte Formate
- **Dokumente**: PDF, DOCX
- **Bilder**: JPEG, PNG, GIF
- **Maximale Dateigröße**: 500MB

### Unterstützte Hersteller
- HP (LaserJet, OfficeJet, PageWide)
- Konica Minolta (bizhub Serie)
- Lexmark (CX, CS, MX Serie)  
- UTAX (alle Modelle)

## Projekt-Komplexität & Wiki-Empfehlung

Das KRAI Engine Projekt hat erhebliche Komplexität erreicht:
- **15+ Dokumentationsdateien** in `/documentation`
- **Multi-layered Architektur** (Backend, AI, Database, Storage)
- **Verschiedene Deployment-Szenarien**
- **Komplexe Konfigurationssysteme**
- **Umfangreiche API-Oberflächen**

**📖 Wiki-Empfehlung:** Für bessere Navigation und Wartung empfehlen wir die Einrichtung eines GitHub Wiki. Details siehe [Wiki Structure Guide](./documentation/WIKI_STRUCTURE.md).

## Lizenz

Proprietäre Software - Alle Rechte vorbehalten.

## Kontakt

Für Support und weitere Informationen kontaktieren Sie unser Entwicklungsteam.