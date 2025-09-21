# Dokumenten-Versionierung im KRAI-System

Das KRAI-System implementiert ein flexibles System zur Dokumenten-Versionierung, das es ermöglicht, verschiedene Versionen derselben Dokumente zu verwalten, zu vergleichen und zu verfolgen.

## Kernkonzepte

- **Flexible Versions-Formate**: Das System unterstützt beliebige Versionsformate (z.B. "1.0", "Rev A", "2025-09-Update"), um der Vielfalt der Hersteller-spezifischen Formatierungen gerecht zu werden.
- **Hierarchische Versionsbeziehungen**: Jedes Dokument kann auf eine Vorgängerversion verweisen, wodurch eine Versionshistorie entsteht.
- **Automatische "Neueste Version"-Markierung**: Das System verwaltet automatisch, welche Version eines Dokuments die aktuellste ist.
- **Multi-Modell-Unterstützung**: Ein Dokument kann für mehrere Gerätemodelle gleichzeitig gültig sein.

## Datenbank-Schema

Die Versionierung wird durch folgende Felder in allen dokumentbezogenen Tabellen umgesetzt:

```sql
-- Hinzugefügt zu service_manuals, bulletins, parts_catalogs, cpmd_documents
document_version_number TEXT           -- Beliebiges Versionsformat
replaces_version_id UUID               -- Verweis auf Vorgänger-Dokument
is_latest_version BOOLEAN DEFAULT TRUE -- Automatisch verwaltet
```

### Automatische Versionslogik über Datenbank-Trigger

Das System verwendet PostgreSQL-Trigger, um automatisch zu erkennen, wenn ein neueres Dokument hochgeladen wird, und aktualisiert die Versionsbeziehungen entsprechend:

```sql
CREATE OR REPLACE FUNCTION update_document_version_status()
RETURNS TRIGGER AS $$
DECLARE
    table_name text;
    id_column text := 'id';
    previous_version_id uuid;
BEGIN
    table_name := TG_TABLE_NAME;
    
    -- Nur aktualisieren, wenn explizit als neueste Version markiert
    IF NEW.is_latest_version = TRUE AND NEW.replaces_version_id IS NOT NULL THEN
        -- Vorherige Version als nicht aktuell markieren
        EXECUTE format('UPDATE %I SET is_latest_version = FALSE WHERE id = $1', table_name)
        USING NEW.replaces_version_id;
        
        -- Auch alle anderen Versionen in der Kette aktualisieren
        previous_version_id := NEW.replaces_version_id;
        
        WHILE previous_version_id IS NOT NULL LOOP
            -- Hole die vorherige Version der vorherigen Version
            EXECUTE format('SELECT replaces_version_id FROM %I WHERE id = $1', table_name)
            INTO previous_version_id
            USING previous_version_id;
            
            -- Wenn es eine weitere Version in der Kette gibt, aktualisiere sie
            IF previous_version_id IS NOT NULL THEN
                EXECUTE format('UPDATE %I SET is_latest_version = FALSE WHERE id = $1', table_name)
                USING previous_version_id;
            END IF;
        END LOOP;
    END IF;
    
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
```

Diese Trigger-Funktion wird auf allen Dokumententabellen angewendet.

## Versionierungsprozess

1. **Hochladen eines neuen Dokuments**:
   - Der Admin gibt eine Versionsnummer im freien Format an
   - Das Dokument wird als neueste Version markiert (`is_latest_version = TRUE`)

2. **Hochladen einer aktualisierten Version**:
   - Der Admin gibt eine neue Versionsnummer an
   - Der Admin wählt die Vorgängerversion aus einer Liste aus
   - Das neue Dokument wird als `is_latest_version = TRUE` markiert
   - Die Trigger-Funktion setzt automatisch alle Vorgängerversionen auf `is_latest_version = FALSE`

3. **Suchen nach Dokumenten**:
   - Standardmäßig werden nur die neuesten Versionen (`is_latest_version = TRUE`) angezeigt
   - Optionale Filter ermöglichen die Anzeige älterer Versionen

## Implementation im UI

Im Filament-Formular wird die Versionierung durch folgende Felder implementiert:

```php
TextInput::make('document_version_number')
    ->label('Version')
    ->helperText('Beliebiges Format (z.B. "1.0", "Rev A", "2025-09-Update")')
    ->required(),
    
Select::make('replaces_version_id')
    ->relationship('previousVersions', 'id')
    ->label('Ersetzt Version')
    ->preload()
    ->helperText('Wählen Sie die Vorgängerversion dieses Dokuments aus')
    ->visible(fn ($record) => $this->hasPreviousVersions($record))
```

## Datenmodell-Beziehungen

Das Datenmodell unterstützt die Versionierung durch folgende Beziehungen:

```php
// In DocumentModel.php
public function previousVersion()
{
    return $this->belongsTo(static::class, 'replaces_version_id');
}

public function newerVersions()
{
    return $this->hasMany(static::class, 'replaces_version_id');
}
```

## Versionsabfragen für Vector Search

Die Vector-Search-Funktionen werden angepasst, um standardmäßig nur die neuesten Versionen einzubeziehen:

```sql
CREATE OR REPLACE FUNCTION search_all_documents(
  query_text TEXT,
  search_manufacturer TEXT DEFAULT NULL,
  search_model TEXT DEFAULT NULL,
  max_results INTEGER DEFAULT 20,
  similarity_threshold FLOAT DEFAULT 0.5,
  include_older_versions BOOLEAN DEFAULT FALSE
)
```

Der Parameter `include_older_versions` ermöglicht die optionale Einbeziehung älterer Dokumentversionen in die Suchergebnisse.

## Vorteile dieses Ansatzes

1. **Flexibilität**: Unterstützt beliebige Versionierungsformate der Hersteller
2. **Automatisierung**: Verwaltet automatisch die "neueste Version"-Beziehungen
3. **Benutzbarkeit**: Vereinfacht die Auswahl der relevanten Version für Admins
4. **Suchoptimierung**: Vector-Suche standardmäßig auf aktuelle Dokumente fokussiert
5. **Multi-Modell**: Ein Dokument kann für mehrere Modelle gelten, mit konsistenter Versionierung
