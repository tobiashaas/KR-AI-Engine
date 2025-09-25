# KRAI Engine - API Documentation

**Complete REST API Reference**

## Base URL

```
http://localhost:8001
```

## Authentication

Currently, the API operates without authentication for development environments. Production deployments should implement appropriate authentication mechanisms.

## Core Endpoints

### System Health

#### GET /health

Returns system health status and processing statistics.

**Response:**
```json
{
  "status": "healthy",
  "service": "KRAI Engine Production",
  "version": "2.0.0",
  "gpu_device": "mps",
  "device_name": "Apple Metal Performance Shaders",
  "memory_gb": 16.0,
  "stats": {
    "documents_processed": 42,
    "chunks_created": 1337,
    "embeddings_generated": 1337,
    "images_processed": 89,
    "errors": 0,
    "uptime_seconds": 3600
  }
}
```

#### GET /

Root endpoint providing basic API information.

**Response:**
```json
{
  "message": "KRAI Engine Production API",
  "version": "2.0.0",
  "status": "running",
  "gpu_support": true
}
```

#### GET /config

Returns complete system configuration.

**Response:**
```json
{
  "system_info": {
    "platform": "Darwin",
    "architecture": "arm64",
    "processor": "arm",
    "python_version": "3.12.0",
    "pytorch_version": "2.1.0",
    "mps_available": true,
    "cuda_available": false
  },
  "device_config": {
    "device": "mps",
    "device_name": "Apple Metal Performance Shaders",
    "memory_gb": 16.0,
    "batch_size": 32,
    "num_workers": 6
  },
  "model_config": {
    "llm": {
      "model_name": "llama3.2:3b",
      "temperature": 0.7,
      "max_tokens": 2048
    },
    "embedding": {
      "model_name": "embeddinggemma",
      "dimension": 768
    },
    "vision": {
      "model_name": "llava:7b",
      "max_new_tokens": 1024
    }
  }
}
```

## Document Processing

### Upload Document

#### POST /api/production/documents/upload

Upload and process a document through the complete KRAI Engine pipeline.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): PDF file to process
- `document_type` (optional): Document type hint (service_manual, parts_catalog, cpmd_database, technical_bulletin)
- `manufacturer` (optional): Manufacturer hint (hp, konica_minolta, lexmark, utax)
- `models` (optional): Specific model information

**Example Request:**
```bash
curl -X POST http://localhost:8001/api/production/documents/upload \
  -F "file=@service_manual.pdf" \
  -F "document_type=service_manual" \
  -F "manufacturer=hp"
```

**Success Response (200):**
```json
{
  "message": "Document processed successfully",
  "document_id": "550e8400-e29b-41d4-a716-446655440000",
  "processing_time": 45.67,
  "stats": {
    "chunks_created": 89,
    "embeddings_generated": 89,
    "images_extracted": 12,
    "images_processed": 12,
    "pages_processed": 156
  },
  "gpu_used": true,
  "performance_metrics": {
    "text_processing_time": 12.34,
    "image_processing_time": 23.45,
    "embedding_generation_time": 9.88,
    "database_storage_time": 0.98
  }
}
```

**Error Responses:**
```json
// Invalid file type (400)
{
  "detail": "Only PDF files are supported"
}

// Processing failed (500)
{
  "detail": "Processing failed: Database connection error"
}

// File too large (413)
{
  "detail": "File size exceeds maximum limit of 500MB"
}
```

### Processing Statistics

#### GET /api/production/documents/stats

Get comprehensive processing statistics.

**Response:**
```json
{
  "total_documents": 150,
  "documents_by_type": {
    "service_manual": 85,
    "parts_catalog": 32,
    "cpmd_database": 18,
    "technical_bulletin": 15
  },
  "documents_by_manufacturer": {
    "hp": 67,
    "konica_minolta": 43,
    "lexmark": 25,
    "utax": 15
  },
  "processing_metrics": {
    "average_processing_time": 38.5,
    "total_chunks": 12450,
    "total_embeddings": 12450,
    "total_images": 892,
    "success_rate": 0.987
  },
  "storage_metrics": {
    "total_storage_mb": 1024.5,
    "documents_storage_mb": 856.2,
    "images_storage_mb": 168.3
  }
}
```

## AI Models

### Model Status

#### GET /api/production/models/status

Get status and availability of all AI models.

**Response:**
```json
{
  "total_models": 4,
  "required_models": {
    "llama3.2:3b": {
      "available": true,
      "status": "loaded"
    },
    "embeddinggemma": {
      "available": true,
      "status": "loaded"
    },
    "llava:7b": {
      "available": true,
      "status": "loaded"
    }
  },
  "available_models": [
    "llama3.2:3b",
    "embeddinggemma", 
    "llava:7b",
    "nomic-embed-text"
  ]
}
```

## Chat Interface

### Chat with Documents

#### POST /api/production/chat

Interactive chat interface for querying processed documents.

**Content-Type:** `application/x-www-form-urlencoded`

**Parameters:**
- `query` (required): User question or query
- `document_ids` (optional): Comma-separated list of document IDs to search

**Example Request:**
```bash
curl -X POST http://localhost:8001/api/production/chat \
  -d "query=What is error code C4-750?" \
  -d "document_ids=doc1,doc2,doc3"
```

**Response:**
```json
{
  "response": "Error code C4-750 indicates a paper jam in the fuser unit. To resolve this issue: 1) Turn off the printer and wait for it to cool down. 2) Open the rear cover and carefully remove any jammed paper. 3) Check the fuser unit for any debris or damaged components. 4) Close the cover and restart the printer.",
  "model": "llama3.2:3b",
  "processing_time": 2.34,
  "tokens_generated": 156,
  "context_documents": ["doc1", "doc3"],
  "confidence_score": 0.92
}
```

## Vision AI

### Analyze Image

#### POST /api/production/vision/analyze

Analyze technical images using Vision AI.

**Content-Type:** `multipart/form-data`

**Parameters:**
- `file` (required): Image file (JPEG, PNG, GIF)
- `prompt` (optional): Analysis prompt (default: generic technical analysis)

**Example Request:**
```bash
curl -X POST http://localhost:8001/api/production/vision/analyze \
  -F "file=@diagram.jpg" \
  -F "prompt=Analyze this printer error display and identify any error codes or indicators"
```

**Response:**
```json
{
  "analysis": "This image shows a printer control panel displaying error code E4-750. The display indicates a paper jam condition with a flashing paper icon. The LED indicators show: Power (green), Ready (off), Attention (red blinking). The error message suggests checking the paper path and removing any jammed paper from the rear access door.",
  "model": "llava:7b",
  "processing_time": 4.67,
  "image_size": 245760,
  "prompt_used": "Analyze this printer error display and identify any error codes or indicators",
  "confidence_score": 0.89,
  "detected_elements": {
    "error_codes": ["E4-750"],
    "indicators": ["power_green", "attention_red"],
    "text_elements": ["PAPER JAM", "CHECK REAR DOOR"]
  }
}
```

## Performance Monitoring

### Performance Metrics

#### GET /api/production/performance

Get detailed performance metrics and system statistics.

**Response:**
```json
{
  "performance_metrics": {
    "documents_per_hour": 156.7,
    "chunks_per_hour": 2890.3,
    "embeddings_per_hour": 2890.3,
    "error_rate": 0.013,
    "uptime_hours": 72.5,
    "average_response_time": 1.23
  },
  "system_metrics": {
    "device": "mps",
    "device_name": "Apple Metal Performance Shaders", 
    "memory_gb": 16.0,
    "batch_size": 32,
    "workers": 6,
    "cpu_usage": 45.2,
    "memory_usage": 67.8,
    "gpu_usage": 23.4
  },
  "current_stats": {
    "documents_processed": 452,
    "chunks_created": 8924,
    "embeddings_generated": 8924,
    "images_processed": 267,
    "errors": 6,
    "uptime_seconds": 261000
  },
  "database_metrics": {
    "connection_pool_size": 20,
    "active_connections": 5,
    "query_performance": {
      "average_query_time": 0.045,
      "slow_queries": 2
    }
  }
}
```

## Search and Query

### Semantic Search

#### POST /api/production/search

Perform semantic search across processed documents.

**Content-Type:** `application/json`

**Request:**
```json
{
  "query": "How to replace fuser unit",
  "limit": 10,
  "similarity_threshold": 0.7,
  "document_types": ["service_manual"],
  "manufacturers": ["hp", "konica_minolta"]
}
```

**Response:**
```json
{
  "results": [
    {
      "chunk_id": "chunk_123",
      "document_id": "doc_456", 
      "similarity_score": 0.92,
      "content": "To replace the fuser unit: 1) Turn off printer and wait 30 minutes for cooling. 2) Open rear access panel...",
      "metadata": {
        "document_type": "service_manual",
        "manufacturer": "hp",
        "model": "LaserJet Pro M404n",
        "page_number": 89,
        "section": "Maintenance Procedures"
      }
    }
  ],
  "total_results": 25,
  "query_time": 0.234,
  "embedding_time": 0.045
}
```

## Error Handling

### Standard Error Response

All API endpoints return errors in a consistent format:

```json
{
  "detail": "Error description",
  "error_code": "KRAI_001",
  "timestamp": "2024-01-25T10:30:00Z",
  "request_id": "req_12345"
}
```

### Error Codes

- `KRAI_001`: Invalid request parameters
- `KRAI_002`: File processing error
- `KRAI_003`: Database connection error
- `KRAI_004`: AI model unavailable
- `KRAI_005`: Storage service error
- `KRAI_006`: Authentication required
- `KRAI_007`: Rate limit exceeded

## Rate Limiting

### Default Limits

- **Document Upload**: 10 requests per minute
- **Chat Interface**: 100 requests per minute  
- **Search Queries**: 200 requests per minute
- **Status Checks**: 1000 requests per minute

### Rate Limit Headers

```http
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 8
X-RateLimit-Reset: 1642867800
```

## WebSocket Support

### Real-time Processing Updates

#### WS /ws/processing/{document_id}

Subscribe to real-time processing updates for a document.

**Message Types:**
```json
// Processing started
{
  "type": "processing_started",
  "document_id": "doc_123",
  "timestamp": "2024-01-25T10:30:00Z"
}

// Progress update
{
  "type": "progress_update", 
  "document_id": "doc_123",
  "progress": 0.45,
  "stage": "embedding_generation",
  "chunks_processed": 45,
  "total_chunks": 100
}

// Processing completed
{
  "type": "processing_completed",
  "document_id": "doc_123", 
  "result": {
    "status": "success",
    "processing_time": 45.67,
    "stats": {...}
  }
}

// Error occurred
{
  "type": "error",
  "document_id": "doc_123",
  "error": "Database connection timeout",
  "error_code": "KRAI_003"
}
```

## SDK Examples

### Python SDK

```python
import requests
import json

class KRAIClient:
    def __init__(self, base_url="http://localhost:8001"):
        self.base_url = base_url
    
    def upload_document(self, file_path, document_type=None, manufacturer=None):
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {}
            if document_type:
                data['document_type'] = document_type
            if manufacturer:
                data['manufacturer'] = manufacturer
            
            response = requests.post(
                f"{self.base_url}/api/production/documents/upload",
                files=files,
                data=data
            )
            return response.json()
    
    def chat(self, query, document_ids=None):
        data = {'query': query}
        if document_ids:
            data['document_ids'] = ','.join(document_ids)
        
        response = requests.post(
            f"{self.base_url}/api/production/chat",
            data=data
        )
        return response.json()

# Usage
client = KRAIClient()
result = client.upload_document("manual.pdf", "service_manual", "hp")
chat_response = client.chat("What is error code C4-750?", [result['document_id']])
```

### JavaScript SDK

```javascript
class KRAIClient {
    constructor(baseUrl = 'http://localhost:8001') {
        this.baseUrl = baseUrl;
    }
    
    async uploadDocument(file, documentType = null, manufacturer = null) {
        const formData = new FormData();
        formData.append('file', file);
        if (documentType) formData.append('document_type', documentType);
        if (manufacturer) formData.append('manufacturer', manufacturer);
        
        const response = await fetch(`${this.baseUrl}/api/production/documents/upload`, {
            method: 'POST',
            body: formData
        });
        
        return response.json();
    }
    
    async chat(query, documentIds = null) {
        const data = new URLSearchParams();
        data.append('query', query);
        if (documentIds) data.append('document_ids', documentIds.join(','));
        
        const response = await fetch(`${this.baseUrl}/api/production/chat`, {
            method: 'POST',
            headers: {'Content-Type': 'application/x-www-form-urlencoded'},
            body: data
        });
        
        return response.json();
    }
}

// Usage
const client = new KRAIClient();
const result = await client.uploadDocument(fileInput.files[0], 'service_manual', 'hp');
const chatResponse = await client.chat('What is error code C4-750?', [result.document_id]);
```

## Testing

### Health Check Script

```bash
#!/bin/bash
# Test KRAI Engine API endpoints

BASE_URL="http://localhost:8001"

echo "Testing KRAI Engine API..."

# Health check
echo "1. Health Check:"
curl -s "$BASE_URL/health" | jq '.status'

# Config check  
echo "2. Configuration:"
curl -s "$BASE_URL/config" | jq '.system_info.platform'

# Model status
echo "3. Model Status:"
curl -s "$BASE_URL/api/production/models/status" | jq '.total_models'

echo "API tests completed."
```

This documentation covers all available endpoints and provides comprehensive examples for integration with the KRAI Engine API.
