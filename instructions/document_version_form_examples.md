# Dokumenten-Upload-Formular Anpassungen für Versionierung

## ProcessingLogResource mit Versionierung und Multi-Modell-Unterstützung

```php
// ProcessingLogResource mit Versionierung
class ProcessingLogResource extends Resource
{
    protected static ?string $model = ProcessingLog::class;
    
    public static function form(Form $form): Form
    {
        return $form->schema([
            FileUpload::make('document')
                ->acceptedFileTypes(['application/pdf'])
                ->disk('r2')
                ->required(),
                
            Select::make('document_type')
                ->options([
                    'service_manual' => 'Service Manual',
                    'bulletin' => 'Service Bulletin',
                    'parts_catalog' => 'Parts Catalog',
                    'cpmd_document' => 'CPMD Document',
                ])
                ->required(),
                
            TextInput::make('manufacturer')
                ->required(),
                
            // Multi-Modell-Unterstützung
            MultiSelect::make('models')
                ->relationship('productModels', 'name')
                ->preload()
                ->required()
                ->helperText('Ein Dokument kann für mehrere Modelle gelten'),
                
            TextInput::make('document_version_number')
                ->label('Version')
                ->helperText('Beliebiges Format (z.B. "1.0", "Rev A", "2025-09-Update")')
                ->required(),
                
            // Für Versionierung: nur anzeigen, wenn es vorherige Versionen gibt
            Select::make('replaces_version_id')
                ->relationship('previousVersions', 'id')
                ->label('Ersetzt Version')
                ->preload()
                ->helperText('Wählen Sie die Vorgängerversion dieses Dokuments aus')
                ->visible(fn ($record) => $this->hasPreviousVersions($record))
                ->afterStateHydrated(function ($component, $state) {
                    // Logik zum Vorschlagen einer inkrementieren Versionsnummer basierend auf der vorherigen Version
                })
        ]);
    }
    
    public static function table(Table $table): Table
    {
        return $table->columns([
            TextColumn::make('original_filename'),
            TextColumn::make('status')->badge(),
            TextColumn::make('progress_percentage')->suffix('%'),
            TextColumn::make('manufacturer'),
            TextColumn::make('document_type'),
            TextColumn::make('document_version_number')
                ->label('Version'),
            BadgeColumn::make('is_latest_version')
                ->label('Latest Version')
                ->boolean(),
            TextColumn::make('created_at')->dateTime(),
        ]);
    }
    
    protected function hasPreviousVersions($record)
    {
        if (!$record) return false;
        
        return ProcessingLog::where('manufacturer', $record->manufacturer)
            ->where('document_type', $record->document_type)
            ->whereJsonContains('models', $record->models[0] ?? null)  // Suche nach mindestens einem übereinstimmenden Modell
            ->where('id', '!=', $record->id)
            ->exists();
    }
}
```

## DocumentProcessingService mit Versionierung

```php
// Angepasster Processing Service für Versionierung
class DocumentProcessingService
{
    public function processDocument($file, $metadata)
    {
        // Create processing log entry
        $log = ProcessingLog::create([
            'original_filename' => $file->getClientOriginalName(),
            'file_hash' => hash_file('sha256', $file->path()),
            'manufacturer' => $metadata['manufacturer'],
            'models' => $metadata['models'],  // JSON-Array von Modellen
            'document_type' => $metadata['document_type'],
            'document_version_number' => $metadata['document_version_number'],
            'replaces_version_id' => $metadata['replaces_version_id'] ?? null,
            'is_latest_version' => true,  // Neue Version ist immer die neueste
            'status' => 'pending'
        ]);
        
        // Bei neuer Version: Markiere vorherige Version(en) als nicht-latest
        if ($log->replaces_version_id) {
            // Die Datenbank-Trigger übernehmen die Aktualisierung der Versionsbeziehungen
        }
        
        // Send to backend for processing
        $response = Http::attach('document', $file->getContent())
            ->post('http://backend:3000/api/process-document', [
                'log_id' => $log->id,
                'manufacturer' => $metadata['manufacturer'],
                'models' => $metadata['models'],
                'document_type' => $metadata['document_type'],
                'document_version_number' => $metadata['document_version_number'],
                'replaces_version_id' => $metadata['replaces_version_id'] ?? null
            ]);
            
        return $response->successful();
    }
}
```

## ProductModel Migration für Multi-Modell-Support

```php
// Migration für ProductModel-Beziehung
Schema::create('product_models', function (Blueprint $table) {
    $table->id();
    $table->string('name');
    $table->string('manufacturer');
    $table->string('model_series')->nullable();
    $table->timestamps();
});

// Pivot-Tabelle für Many-to-Many Beziehung zwischen Dokumenten und Modellen
Schema::create('document_model', function (Blueprint $table) {
    $table->uuid('processing_log_id');
    $table->unsignedBigInteger('product_model_id');
    $table->foreign('processing_log_id')->references('id')->on('processing_logs')->onDelete('cascade');
    $table->foreign('product_model_id')->references('id')->on('product_models')->onDelete('cascade');
    $table->primary(['processing_log_id', 'product_model_id']);
});
```

## Modell-Beziehungen in ProcessingLog

```php
// In der ProcessingLog Klasse
public function productModels()
{
    return $this->belongsToMany(ProductModel::class, 'document_model');
}

public function previousVersions()
{
    return $this::where('manufacturer', $this->manufacturer)
        ->where('document_type', $this->document_type)
        ->whereJsonOverlap('models', $this->models)
        ->where('id', '!=', $this->id)
        ->orderBy('created_at', 'desc');
}
```
