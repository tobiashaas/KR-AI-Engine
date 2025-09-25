# KRAI Engine - Chunking Configuration

**Comprehensive Guide to Text Chunking Strategies**

## Overview

The KRAI Engine implements sophisticated chunking strategies to optimize text processing for technical documentation. The system automatically selects the most appropriate chunking strategy based on document type, manufacturer, and content structure.

## Configuration File

Chunking settings are managed through `backend/config/chunk_settings.json`

## Available Strategies

### 1. Simple Word Chunking

Basic word-based chunking with fixed parameters.

**Configuration:**
```json
{
  "chunk_size": 1000,
  "chunk_overlap": 100,
  "min_chunk_size": 100,
  "max_chunk_size": 2000,
  "priority": 1
}
```

**Use Case:** General-purpose text processing where content structure is less important.

### 2. Sentence-Based Chunking

Chunks text at natural sentence boundaries for better semantic coherence.

**Configuration:**
```json
{
  "chunk_size": 800,
  "chunk_overlap": 80,
  "min_chunk_size": 50,
  "max_chunk_size": 1500,
  "priority": 2
}
```

**Use Case:** Documents where sentence-level context is crucial for understanding.

### 3. Paragraph-Based Chunking

Respects paragraph boundaries to maintain logical text groupings.

**Configuration:**
```json
{
  "chunk_size": 1200,
  "chunk_overlap": 120,
  "min_chunk_size": 200,
  "max_chunk_size": 2500,
  "priority": 3
}
```

**Use Case:** Technical bulletins and documentation with clear paragraph structures.

### 4. Contextual Chunking (Default)

Intelligent chunking that preserves important technical contexts.

**Configuration:**
```json
{
  "chunk_size": 1000,
  "chunk_overlap": 150,
  "min_chunk_size": 200,
  "max_chunk_size": 2000,
  "priority": 4,
  "context_rules": {
    "preserve_sections": true,
    "preserve_chapters": true,
    "preserve_procedures": true,
    "preserve_error_codes": true,
    "preserve_part_numbers": true
  }
}
```

**Use Case:** Service manuals and technical documentation requiring context preservation.

### 5. Structure-Based Chunking

Chunking based on document hierarchical structure.

**Configuration:**
```json
{
  "chunk_size": 1500,
  "chunk_overlap": 200,
  "min_chunk_size": 300,
  "max_chunk_size": 3000,
  "priority": 5,
  "structure_rules": {
    "chapter_boundaries": true,
    "section_boundaries": true,
    "procedure_boundaries": true,
    "error_code_boundaries": true,
    "part_number_boundaries": true
  }
}
```

**Use Case:** Highly structured documents with clear hierarchical organization.

## Document Type Specifications

### Service Manual
```json
{
  "preferred_strategy": "contextual_chunking",
  "chunk_size": 1200,
  "chunk_overlap": 150,
  "preserve_structure": true,
  "preserve_procedures": true,
  "preserve_error_codes": true,
  "preserve_part_numbers": true
}
```

### Parts Catalog
```json
{
  "preferred_strategy": "structure_based_chunking",
  "chunk_size": 800,
  "chunk_overlap": 100,
  "preserve_structure": true,
  "preserve_part_numbers": true,
  "preserve_descriptions": true
}
```

### CPMD Database
```json
{
  "preferred_strategy": "contextual_chunking",
  "chunk_size": 600,
  "chunk_overlap": 80,
  "preserve_error_codes": true,
  "preserve_solutions": true,
  "preserve_procedures": true
}
```

### Technical Bulletin
```json
{
  "preferred_strategy": "paragraph_based_chunking",
  "chunk_size": 1000,
  "chunk_overlap": 120,
  "preserve_structure": true,
  "preserve_procedures": true,
  "preserve_error_codes": true
}
```

## Manufacturer-Specific Settings

### HP
```json
{
  "chunk_size_multiplier": 1.0,
  "preferred_strategy": "contextual_chunking",
  "special_rules": {
    "preserve_cpmd_structure": true,
    "preserve_error_code_context": true,
    "preserve_part_number_context": true
  }
}
```

### Konica Minolta
```json
{
  "chunk_size_multiplier": 1.1,
  "preferred_strategy": "contextual_chunking",
  "special_rules": {
    "preserve_bizhub_structure": true,
    "preserve_error_code_context": true,
    "preserve_part_number_context": true
  }
}
```

### Lexmark
```json
{
  "chunk_size_multiplier": 1.0,
  "preferred_strategy": "contextual_chunking",
  "special_rules": {
    "preserve_cx_structure": true,
    "preserve_error_code_context": true,
    "preserve_part_number_context": true
  }
}
```

### UTAX
```json
{
  "chunk_size_multiplier": 1.0,
  "preferred_strategy": "contextual_chunking",
  "special_rules": {
    "preserve_utax_structure": true,
    "preserve_error_code_context": true,
    "preserve_part_number_context": true
  }
}
```

## Advanced Settings

### Global Configuration
```json
{
  "preserve_context": true,
  "preserve_metadata": true,
  "preserve_relationships": true,
  "smart_boundaries": true,
  "adaptive_sizing": true,
  "quality_threshold": 0.8
}
```

### Parameter Descriptions

**preserve_context**: Maintains semantic context across chunk boundaries
**preserve_metadata**: Preserves document metadata in chunks
**preserve_relationships**: Maintains relationships between related content
**smart_boundaries**: Uses intelligent boundary detection
**adaptive_sizing**: Adjusts chunk sizes based on content complexity
**quality_threshold**: Minimum quality score for chunk acceptance

## Chunk Quality Metrics

### Evaluation Criteria
1. **Semantic Completeness**: Chunk contains complete ideas
2. **Context Preservation**: Important context is not lost at boundaries
3. **Technical Accuracy**: Technical terms and codes remain intact
4. **Size Optimization**: Chunks fit within embedding model constraints
5. **Overlap Quality**: Overlapping content provides continuity

### Quality Scoring
- **0.9-1.0**: Excellent chunk quality
- **0.8-0.9**: Good chunk quality
- **0.7-0.8**: Acceptable chunk quality
- **< 0.7**: Poor chunk quality (requires reprocessing)

## Customization

### Adding New Document Types

1. Add document type configuration to `chunk_settings.json`
2. Define specific chunking parameters
3. Set preservation rules for technical content
4. Test with sample documents

Example:
```json
"new_document_type": {
  "preferred_strategy": "contextual_chunking",
  "chunk_size": 1000,
  "chunk_overlap": 150,
  "preserve_custom_elements": true
}
```

### Creating Manufacturer-Specific Rules

1. Add manufacturer configuration to `manufacturer_specific` section
2. Define chunk size multipliers
3. Set special preservation rules
4. Configure strategy preferences

### Environment-Based Overrides

Chunking parameters can be overridden via environment variables:

```env
DEFAULT_CHUNKING_STRATEGY=contextual_chunking
CHUNK_SIZE=1000
CHUNK_OVERLAP=150
```

## Performance Considerations

### Memory Usage
- Larger chunks require more memory for processing
- Smaller chunks increase processing overhead
- Optimal chunk size balances memory and performance

### Processing Speed
- Simple strategies are faster but less accurate
- Contextual strategies provide better results but require more processing
- Structure-based strategies need document parsing overhead

### Embedding Quality
- Chunk size affects embedding quality
- Too small: Loss of context
- Too large: Diluted semantic meaning
- Optimal size: 500-1500 characters for technical content

## Troubleshooting

### Common Issues

**Chunks too small**: Increase `min_chunk_size` parameter
**Chunks too large**: Decrease `max_chunk_size` parameter
**Context loss**: Enable context preservation rules
**Poor overlap**: Adjust `chunk_overlap` percentage
**Wrong strategy**: Check document type classification

### Debug Mode

Enable chunking debug mode via environment:
```env
DEBUG_CHUNKING=true
LOG_LEVEL=DEBUG
```

This provides detailed logging of chunking decisions and quality metrics.

## Best Practices

1. **Test with representative documents** before production deployment
2. **Monitor chunk quality metrics** to ensure optimal performance
3. **Adjust parameters gradually** to find optimal settings
4. **Consider document variability** within manufacturer categories
5. **Regular evaluation** of chunking effectiveness with new document types
6. **Balance performance and accuracy** based on use case requirements

## API Integration

The chunking system integrates with the main KRAI API:

```python
# Get chunking configuration
GET /api/production/config/chunking

# Override chunking strategy for specific document
POST /api/production/documents/upload
{
  "chunking_strategy": "contextual_chunking",
  "chunk_size": 1200
}
```
