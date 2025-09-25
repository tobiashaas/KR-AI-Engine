# 🧪 KRAI Document Analysis Testing

**Test-Dokumente analysieren und optimale Chunking-Strategien finden**

---

## 🚀 **QUICK START**

### **1. Test-Environment Setup:**
```bash
cd backend/
python setup_test_environment.py
```

### **2. Test-Dokument hochladen:**
```bash
# Kopiere dein Test-Dokument in den test_documents Ordner
cp /path/to/your/document.pdf test_documents/
```

### **3. Dokument analysieren:**
```bash
python test_document_analyzer.py test_documents/your_document.pdf
```

---

## 📋 **WAS WIRD ANALYSIERT?**

### **📄 Dokument-Struktur:**
- **Dateigröße** und Seitenzahl
- **Text-Struktur** (Paragraphen, Sätze, Wörter)
- **Technische Begriffe** und Häufigkeiten
- **Überschriften** und Kapitel-Struktur
- **Bilder und Tabellen** (bei PDFs)

### **🧪 Chunking-Strategien getestet:**

#### **1. Simple Word Chunking**
- **Beschreibung:** Einfache Wort-basierte Aufteilung
- **Vorteil:** Gleichmäßige Chunk-Größen
- **Nachteil:** Kann Kontext unterbrechen

#### **2. Sentence-Based Chunking**
- **Beschreibung:** Satz-bewusste Aufteilung
- **Vorteil:** Behält Satz-Kontext
- **Nachteil:** Unregelmäßige Chunk-Größen

#### **3. Paragraph-Based Chunking**
- **Beschreibung:** Absatz-bewusste Aufteilung
- **Vorteil:** Behält Absatz-Kontext
- **Nachteil:** Sehr große oder kleine Chunks möglich

#### **4. Semantic Chunking**
- **Beschreibung:** Semantisch-bewusste Aufteilung
- **Vorteil:** Behält Bedeutungs-Kontext
- **Nachteil:** Komplexer zu implementieren

#### **5. Structure-Based Chunking**
- **Beschreibung:** Dokument-Struktur-bewusste Aufteilung
- **Vorteil:** Folgt Kapitel/Abschnitt-Struktur
- **Nachteil:** Funktioniert nur bei strukturierten Dokumenten

---

## 📊 **ANALYSE-ERGEBNISSE**

### **Was wird gemessen:**
- **Chunk-Anzahl** pro Strategie
- **Durchschnittliche Chunk-Größe** (in Wörtern)
- **Größen-Verteilung** (klein/medium/groß)
- **Standardabweichung** der Chunk-Größen

### **Optimale Chunk-Größe:**
- **Klein:** < 500 Wörter (zu klein für Kontext)
- **Medium:** 500-1500 Wörter (optimal)
- **Groß:** > 1500 Wörter (zu groß für Verarbeitung)

---

## 🎯 **DOKUMENT-TYP ERKENNUNG**

### **Automatische Erkennung von:**
- **Service Manual** - Reparaturhandbücher
- **Parts Catalog** - Ersatzteilkataloge
- **Technical Bulletin** - Technische Mitteilungen
- **CPMD Database** - HP-spezifische Begleithefte

### **Erkennungs-Merkmale:**
- **Keywords** im Text
- **Dateiname-Patterns**
- **Dokument-Struktur**
- **Häufigkeit technischer Begriffe**

---

## 📁 **TEST-DATEIEN STRUKTUR**

```
backend/
├── test_documents/           # Hier deine Test-Dokumente
├── analysis_reports/         # Generierte Analyse-Berichte
├── logs/                     # Log-Dateien
├── test_document_analyzer.py # Haupt-Analyse-Tool
├── setup_test_environment.py # Environment Setup
└── README_TESTING.md         # Diese Datei
```

---

## 🔧 **KONFIGURATION ANPASSEN**

### **Chunk-Größen anpassen:**
```python
# In test_document_analyzer.py
def _simple_word_chunking(self, text: str, chunk_size: int = 1000, overlap: int = 200):
    # chunk_size: Ziel-Größe in Wörtern
    # overlap: Überlappung zwischen Chunks
```

### **Neue Chunking-Strategien hinzufügen:**
```python
# Neue Strategie in self.chunking_strategies hinzufügen
'my_custom_strategy': self._my_custom_chunking
```

---

## 📊 **BEISPIEL-ERGEBNISSE**

### **Typische Ergebnisse für Service Manuals:**
```
📄 DOCUMENT ANALYSIS SUMMARY
============================================================
📁 File: HP_LaserJet_4000_Service_Manual.pdf
📏 Size: 45.2 MB
📝 Words: 125,430
📄 Pages: 234
🏷️  Type: service_manual (confidence: 0.89)

🧪 CHUNKING STRATEGIES TESTED:
  • simple_word_chunking: 126 chunks, avg 995 words
  • sentence_based: 98 chunks, avg 1280 words
  • paragraph_based: 67 chunks, avg 1872 words
  • structure_based: 45 chunks, avg 2787 words

🎯 RECOMMENDATION:
  Best strategy: sentence_based
  • Strategy 'sentence_based' provides optimal chunk distribution
  • Average chunk size: 1280 words
  • Total chunks: 98
```

---

## 🚨 **TROUBLESHOOTING**

### **Häufige Probleme:**

#### **1. "File not found" Error:**
```bash
# Stelle sicher, dass die Datei im richtigen Pfad ist
ls test_documents/
```

#### **2. "NLTK data not found" Error:**
```bash
# Setup-Script erneut ausführen
python setup_test_environment.py
```

#### **3. "PyMuPDF import error":**
```bash
# PyMuPDF installieren
pip install PyMuPDF
```

#### **4. Große PDF-Dateien (600MB+):**
- **Teste zuerst mit kleineren Dateien**
- **Erhöhe Memory-Limit falls nötig**
- **Verwende asynchrone Verarbeitung**

---

## 💡 **TIPS FÜR BESTE ERGEBNISSE**

### **Test-Dokumente auswählen:**
1. **Verschiedene Größen** testen (1MB, 10MB, 100MB+)
2. **Verschiedene Typen** testen (Service Manual, Parts Catalog, Bulletin)
3. **Verschiedene Qualitäten** testen (gescannt, digital, gemischt)

### **Chunking-Strategien optimieren:**
1. **Starte mit sentence_based** für die meisten Dokumente
2. **Verwende structure_based** für gut strukturierte Manuals
3. **Kombiniere Strategien** für komplexe Dokumente

### **Performance optimieren:**
1. **Teste mit kleinen Dokumenten** zuerst
2. **Verwende asynchrone Verarbeitung** für große Dateien
3. **Caching implementieren** für wiederholte Analysen

---

## 🎯 **NÄCHSTE SCHRITTE**

Nach der Analyse:
1. **Optimale Chunking-Strategie** identifizieren
2. **Chunk-Größen** für verschiedene Dokumenttypen festlegen
3. **Contextual Chunking** implementieren
4. **Production Document Processor** entwickeln
5. **Vision AI** für technische Zeichnungen integrieren

---

**🧪 Happy Testing! Lass uns die optimale Chunking-Strategie finden!**
