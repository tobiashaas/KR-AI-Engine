# 🚀 KRAI ENGINE - COMPLETE API DOCUMENTATION

**Database Functions & AI Agent Integration Guide**  
**Version**: 2.0 Production Ready  
**Date**: December 2024  

---

## 📋 **TABLE OF CONTENTS**

1. [Core Search Functions](#core-search-functions)
2. [Option Validation Functions](#option-validation-functions)
3. [AI Agent Integration](#ai-agent-integration)
4. [Content Management Functions](#content-management-functions)
5. [System Management Functions](#system-management-functions)
6. [Python Integration Examples](#python-integration-examples)
7. [Error Handling & Best Practices](#error-handling--best-practices)

---

## 🔍 **CORE SEARCH FUNCTIONS**

### **1. Comprehensive Search (Optimized)**

**Function**: `krai_intelligence.optimized_comprehensive_search()`

**Purpose**: Multi-table semantic search across all documentation with AI-optimized performance

**Parameters**:
- `search_query` (text): Search term (error codes, symptoms, parts, descriptions)
- `manufacturer_filter` (uuid, optional): Filter by manufacturer ID
- `product_filter` (uuid, optional): Filter by specific product ID
- `document_type_filter` (text, optional): Filter by document type
- `max_results` (integer, default: 50): Maximum number of results

**Returns**: Table with columns:
- `result_type`: 'chunk', 'error_code', 'document'
- `result_id`: UUID of the result
- `title`: Display title
- `content`: Main content text
- `similarity_score`: Relevance score (0.0-1.0)
- `metadata`: JSON with additional context

**Example Usage**:
```sql
-- Search for HP paper jam issues
SELECT * FROM krai_intelligence.optimized_comprehensive_search(
    'C1234 paper jam',
    '550e8400-e29b-41d4-a716-446655440001',  -- HP Inc. ID
    NULL,  -- No specific product filter
    'service_manual',  -- Only service manuals
    10  -- Top 10 results
);
```

**Expected Response**:
```json
{
  "result_type": "error_code",
  "result_id": "uuid-here",
  "title": "C1234",
  "content": "Paper jam in input tray. Solution: Check paper path...",
  "similarity_score": 0.95,
  "metadata": {
    "manufacturer_name": "HP Inc.",
    "document_type": "service_manual",
    "severity_level": 2,
    "affected_products": ["HP 9025", "HP 9035"]
  }
}
```

### **2. Error Code Normalization**

**Function**: `krai_intelligence.normalize_error_code(input_code)`

**Purpose**: Standardize error codes for fuzzy search across manufacturers

**Parameters**:
- `input_code` (text): Original error code

**Returns**: Normalized error code (text)

**Example Usage**:
```sql
-- Normalize various error code formats
SELECT 
    normalize_error_code('C1234') as hp_code,
    normalize_error_code('Error 1234') as generic_code,
    normalize_error_code('E-5678') as epson_code;
```

**Expected Response**:
```
hp_code: "c1234"
generic_code: "1234"  
epson_code: "e5678"
```

### **3. Product Hierarchy Navigation**

**Function**: `krai_core.get_product_hierarchy(manufacturer_id)`

**Purpose**: Get complete product hierarchy (Series → Models → Options)

**Parameters**:
- `manufacturer_id` (uuid): Manufacturer ID

**Returns**: Hierarchical product structure

**Example Usage**:
```sql
-- Get HP product hierarchy
SELECT * FROM krai_core.get_product_hierarchy(
    '550e8400-e29b-41d4-a716-446655440001'  -- HP Inc. ID
);
```

---

## ⚙️ **OPTION VALIDATION FUNCTIONS**

### **1. Option Configuration Validation (Optimized)**

**Function**: `krai_config.optimized_validate_option_configuration()`

**Purpose**: Validate complex option configurations with dependency checking

**Parameters**:
- `base_model_id` (uuid): Base product model ID
- `selected_options` (uuid[]): Array of selected option IDs

**Returns**: Validation result with:
- `is_valid`: Boolean validation result
- `validation_errors`: Array of error messages
- `suggested_additions`: Array of missing option IDs
- `suggested_removals`: Array of conflicting option IDs

**Example Usage**:
```sql
-- Validate HP 9025 with Bridge A + Finisher X
SELECT * FROM krai_config.optimized_validate_option_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY[
        '660e8400-e29b-41d4-a716-446655440003',  -- Bridge A ID
        '660e8400-e29b-41d4-a716-446655440005'   -- Finisher X ID
    ]
);
```

**Expected Response (Valid Configuration)**:
```json
{
  "is_valid": true,
  "validation_errors": [],
  "suggested_additions": [],
  "suggested_removals": []
}
```

**Expected Response (Invalid Configuration)**:
```json
{
  "is_valid": false,
  "validation_errors": [
    "Finisher Y requires Bridge B, but Bridge A is selected"
  ],
  "suggested_additions": ["660e8400-e29b-41d4-a716-446655440004"],  -- Bridge B ID
  "suggested_removals": ["660e8400-e29b-41d4-a716-446655440003"]    -- Bridge A ID
}
```

### **2. AI Agent Option Queries**

**Function**: `krai_config.ai_get_available_options(model_id)`

**Purpose**: Get all available options for a model with dependency information

**Parameters**:
- `model_id` (uuid): Product model ID

**Returns**: Available options with:
- `option_id`: UUID of the option
- `option_name`: Display name
- `option_category`: Category (bridge, finisher, tray, etc.)
- `is_compatible`: Compatibility status
- `dependencies`: Required dependencies
- `conflicts_with`: Conflicting options
- `installation_notes`: Installation information

**Example Usage**:
```sql
-- Get available options for HP 9025
SELECT * FROM krai_config.ai_get_available_options(
    '660e8400-e29b-41d4-a716-446655440002'  -- HP 9025 Model ID
);
```

**Expected Response**:
```json
[
  {
    "option_id": "uuid-bridge-a",
    "option_name": "Bridge A",
    "option_category": "bridge",
    "is_compatible": true,
    "dependencies": [],
    "conflicts_with": ["Bridge B"],
    "installation_notes": "Provides additional paper handling capabilities"
  },
  {
    "option_id": "uuid-finisher-x",
    "option_name": "Finisher X",
    "option_category": "finisher",
    "is_compatible": true,
    "dependencies": ["Requires Bridge A"],
    "conflicts_with": [],
    "installation_notes": "Requires Bridge A for proper paper path"
  }
]
```

### **3. AI Agent Configuration Validation**

**Function**: `krai_config.ai_validate_configuration(model_id, option_names)`

**Purpose**: Validate configuration using option names (AI-friendly)

**Parameters**:
- `model_id` (uuid): Product model ID
- `option_names` (text[]): Array of option names

**Returns**: Comprehensive validation with:
- `configuration_valid`: Boolean result
- `validation_summary`: Human-readable summary
- `errors`: Array of error messages
- `warnings`: Array of warning messages
- `suggestions`: Array of suggestions

**Example Usage**:
```sql
-- Validate configuration by option names
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY['Bridge A', 'Finisher X']  -- Option names
);
```

**Expected Response**:
```json
{
  "configuration_valid": true,
  "validation_summary": "Configuration is valid and ready for installation",
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

---

## 🤖 **AI AGENT INTEGRATION**

### **1. Complex Dependency Checking**

**Function**: `krai_config.check_option_dependencies(base_model_id, selected_options)`

**Purpose**: Check complex option dependencies and conflicts

**Parameters**:
- `base_model_id` (uuid): Base product model ID
- `selected_options` (uuid[]): Array of selected option IDs

**Returns**: Dependency analysis with:
- `dependency_rule`: Description of the rule
- `is_satisfied`: Whether the rule is satisfied
- `missing_options`: Missing required options
- `conflicting_options`: Conflicting options

**Example Usage**:
```sql
-- Check dependencies for Bridge A + Finisher Y
SELECT * FROM krai_config.check_option_dependencies(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY[
        '660e8400-e29b-41d4-a716-446655440003',  -- Bridge A ID
        '660e8400-e29b-41d4-a716-446655440006'   -- Finisher Y ID
    ]
);
```

**Expected Response**:
```json
{
  "dependency_rule": "Finisher Y requires Bridge B",
  "is_satisfied": false,
  "missing_options": ["660e8400-e29b-41d4-a716-446655440004"],  -- Bridge B ID
  "conflicting_options": []
}
```

### **2. Document Set Retrieval**

**Function**: `krai_core.get_hp_documentation_set(model_id, error_code_filter)`

**Purpose**: Get related documents for a specific model and error code

**Parameters**:
- `model_id` (uuid): Product model ID
- `error_code_filter` (text, optional): Filter by error code

**Returns**: Document set with:
- `cpmd_file_name`: CPMD database filename
- `service_manual_name`: Service manual filename
- `related_chunks`: Array of related text chunks
- `related_error_codes`: Array of related error codes

**Example Usage**:
```sql
-- Get HP 9025 documentation for C1234 error
SELECT * FROM krai_core.get_hp_documentation_set(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    'C1234'  -- Error code filter
);
```

---

## 🎥 **CONTENT MANAGEMENT FUNCTIONS**

### **1. Image Retrieval by Part Numbers**

**Function**: `krai_content.get_images_for_part_numbers(part_numbers)`

**Purpose**: Get images (schematics, diagrams) for specific part numbers

**Parameters**:
- `part_numbers` (text[]): Array of part numbers

**Returns**: Images with:
- `image_id`: UUID of the image
- `image_url`: URL to the image
- `image_type`: Type (schematic, diagram, photo)
- `part_numbers`: Related part numbers
- `ai_description`: AI-generated description

**Example Usage**:
```sql
-- Get images for HP toner cartridges
SELECT * FROM krai_content.get_images_for_part_numbers(
    ARRAY['CB435A', 'CE285A', 'CF400A']
);
```

### **2. Defect Pattern Analysis**

**Function**: `krai_content.get_defect_patterns_by_category(category)`

**Purpose**: Get AI training patterns for specific defect categories

**Parameters**:
- `category` (text): Defect category (banding, streaking, etc.)

**Returns**: Defect patterns with:
- `pattern_id`: UUID of the pattern
- `pattern_name`: Pattern identifier
- `training_accuracy`: AI training accuracy
- `detection_count`: How often detected
- `severity_typical`: Typical severity level

**Example Usage**:
```sql
-- Get banding defect patterns
SELECT * FROM krai_content.get_defect_patterns_by_category('banding');
```

---

## 🔧 **SYSTEM MANAGEMENT FUNCTIONS**

### **1. System Health Overview**

**Function**: `krai_system.get_system_health_overview()`

**Purpose**: Get current system health status

**Returns**: Health status with:
- `check_name`: Name of the health check
- `status`: Health status (healthy, warning, critical)
- `response_time_ms`: Response time
- `last_checked`: Last check timestamp

**Example Usage**:
```sql
-- Get system health status
SELECT * FROM krai_system.get_system_health_overview();
```

### **2. Performance Statistics**

**Function**: `krai_system.get_performance_stats(metric_name_filter, hours_back)`

**Purpose**: Get performance statistics for monitoring

**Parameters**:
- `metric_name_filter` (text, optional): Filter by metric name
- `hours_back` (integer, default: 24): Hours to look back

**Returns**: Performance stats with:
- `metric_name`: Name of the metric
- `avg_execution_time_ms`: Average execution time
- `max_execution_time_ms`: Maximum execution time
- `min_execution_time_ms`: Minimum execution time
- `total_executions`: Total number of executions
- `slow_query_count`: Number of slow queries

**Example Usage**:
```sql
-- Get comprehensive search performance stats
SELECT * FROM krai_system.get_performance_stats('comprehensive_search', 24);
```

### **3. Processing Queue Status**

**Function**: `krai_system.get_queue_status()`

**Purpose**: Get current processing queue status

**Returns**: Queue status with:
- `task_type`: Type of task
- `status`: Task status (pending, processing, completed, failed)
- `count`: Number of tasks
- `avg_processing_time_ms`: Average processing time
- `failed_count`: Number of failed tasks

**Example Usage**:
```sql
-- Get processing queue status
SELECT * FROM krai_system.get_queue_status();
```

---

## 🐍 **PYTHON INTEGRATION EXAMPLES**

### **1. FastAPI Integration**

```python
from fastapi import FastAPI, HTTPException
from supabase import create_client
import asyncio
from typing import List, Optional

app = FastAPI()

# Initialize Supabase client
supabase = create_client(
    "https://your-project.supabase.co",
    "your-service-role-key"
)

@app.get("/api/v1/search")
async def comprehensive_search(
    query: str,
    manufacturer_id: Optional[str] = None,
    product_id: Optional[str] = None,
    document_type: Optional[str] = None,
    limit: int = 50
):
    """Comprehensive search endpoint"""
    try:
        result = supabase.rpc(
            'optimized_comprehensive_search',
            {
                'search_query': query,
                'manufacturer_filter': manufacturer_id,
                'product_filter': product_id,
                'document_type_filter': document_type,
                'max_results': limit
            }
        ).execute()
        
        return {
            "status": "success",
            "query": query,
            "results": result.data,
            "count": len(result.data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/validate-configuration")
async def validate_option_configuration(
    model_id: str,
    option_ids: List[str]
):
    """Validate option configuration"""
    try:
        result = supabase.rpc(
            'optimized_validate_option_configuration',
            {
                'base_model_id': model_id,
                'selected_options': option_ids
            }
        ).execute()
        
        return {
            "status": "success",
            "validation": result.data[0] if result.data else None
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/available-options/{model_id}")
async def get_available_options(model_id: str):
    """Get available options for a model"""
    try:
        result = supabase.rpc(
            'ai_get_available_options',
            {'model_id': model_id}
        ).execute()
        
        return {
            "status": "success",
            "model_id": model_id,
            "options": result.data
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

### **2. AI Agent Integration**

```python
import asyncio
from typing import Dict, List, Optional

class KRAIAgent:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def search_documentation(self, query: str, filters: Dict = None) -> List[Dict]:
        """Search documentation using comprehensive search"""
        try:
            result = self.supabase.rpc(
                'optimized_comprehensive_search',
                {
                    'search_query': query,
                    'manufacturer_filter': filters.get('manufacturer_id'),
                    'product_filter': filters.get('product_id'),
                    'document_type_filter': filters.get('document_type'),
                    'max_results': filters.get('limit', 50)
                }
            ).execute()
            
            return result.data
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    async def validate_configuration(self, model_id: str, option_names: List[str]) -> Dict:
        """Validate option configuration by names"""
        try:
            result = self.supabase.rpc(
                'ai_validate_configuration',
                {
                    'model_id': model_id,
                    'option_names': option_names
                }
            ).execute()
            
            return result.data[0] if result.data else {}
        except Exception as e:
            print(f"Validation error: {e}")
            return {"configuration_valid": False, "errors": [str(e)]}
    
    async def get_model_options(self, model_id: str) -> List[Dict]:
        """Get available options for a model"""
        try:
            result = self.supabase.rpc(
                'ai_get_available_options',
                {'model_id': model_id}
            ).execute()
            
            return result.data
        except Exception as e:
            print(f"Options error: {e}")
            return []
    
    async def analyze_error_code(self, error_code: str, manufacturer_id: str = None) -> Dict:
        """Analyze error code and get solutions"""
        try:
            # Normalize error code
            normalized = self.supabase.rpc(
                'normalize_error_code',
                {'input_code': error_code}
            ).execute()
            
            # Search for solutions
            solutions = await self.search_documentation(
                error_code,
                {'manufacturer_id': manufacturer_id, 'limit': 10}
            )
            
            return {
                "error_code": error_code,
                "normalized_code": normalized.data,
                "solutions": solutions,
                "manufacturer": manufacturer_id
            }
        except Exception as e:
            print(f"Error analysis error: {e}")
            return {"error_code": error_code, "solutions": []}

# Usage example
async def main():
    agent = KRAIAgent(supabase_client)
    
    # Search for paper jam solutions
    results = await agent.search_documentation("C1234 paper jam")
    print(f"Found {len(results)} solutions")
    
    # Validate option configuration
    validation = await agent.validate_configuration(
        "HP-9025-MODEL-ID",
        ["Bridge A", "Finisher X"]
    )
    print(f"Configuration valid: {validation.get('configuration_valid')}")
    
    # Get available options
    options = await agent.get_model_options("HP-9025-MODEL-ID")
    print(f"Available options: {len(options)}")

if __name__ == "__main__":
    asyncio.run(main())
```

### **3. Error Handling & Retry Logic**

```python
import asyncio
from typing import Dict, List, Optional
from tenacity import retry, stop_after_attempt, wait_exponential

class RobustKRAIClient:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    async def robust_search(self, query: str, filters: Dict = None) -> Dict:
        """Robust search with retry logic"""
        try:
            result = self.supabase.rpc(
                'optimized_comprehensive_search',
                {
                    'search_query': query,
                    'manufacturer_filter': filters.get('manufacturer_id'),
                    'product_filter': filters.get('product_id'),
                    'document_type_filter': filters.get('document_type'),
                    'max_results': filters.get('limit', 50)
                }
            ).execute()
            
            return {
                "status": "success",
                "results": result.data,
                "count": len(result.data)
            }
        except Exception as e:
            print(f"Search failed: {e}")
            raise
    
    async def batch_validate_configurations(self, configurations: List[Dict]) -> List[Dict]:
        """Validate multiple configurations in batch"""
        results = []
        
        for config in configurations:
            try:
                result = self.supabase.rpc(
                    'ai_validate_configuration',
                    {
                        'model_id': config['model_id'],
                        'option_names': config['option_names']
                    }
                ).execute()
                
                results.append({
                    "config_id": config.get('id'),
                    "validation": result.data[0] if result.data else {},
                    "status": "success"
                })
            except Exception as e:
                results.append({
                    "config_id": config.get('id'),
                    "validation": {"configuration_valid": False, "errors": [str(e)]},
                    "status": "error"
                })
        
        return results
```

---

## ⚠️ **ERROR HANDLING & BEST PRACTICES**

### **1. Common Error Scenarios**

#### **Database Connection Errors**
```python
try:
    result = supabase.rpc('function_name', params).execute()
except Exception as e:
    if "connection" in str(e).lower():
        # Retry with exponential backoff
        await asyncio.sleep(2 ** retry_count)
        retry_count += 1
    else:
        # Log and handle other errors
        logger.error(f"Database error: {e}")
```

#### **Function Parameter Errors**
```python
# Validate parameters before calling functions
def validate_search_params(query: str, filters: Dict) -> bool:
    if not query or len(query.strip()) < 2:
        raise ValueError("Query must be at least 2 characters")
    
    if filters.get('limit') and filters['limit'] > 100:
        raise ValueError("Limit cannot exceed 100")
    
    return True
```

#### **Empty Result Handling**
```python
async def safe_search(self, query: str) -> List[Dict]:
    try:
        result = self.supabase.rpc('optimized_comprehensive_search', {
            'search_query': query,
            'max_results': 50
        }).execute()
        
        # Handle empty results
        if not result.data:
            return [{
                "result_type": "no_results",
                "title": "No results found",
                "content": f"No documentation found for '{query}'",
                "similarity_score": 0.0,
                "metadata": {"suggestion": "Try different search terms"}
            }]
        
        return result.data
    except Exception as e:
        logger.error(f"Search error: {e}")
        return []
```

### **2. Performance Optimization**

#### **Connection Pooling**
```python
from supabase import create_client
import asyncio

class KRAIConnectionPool:
    def __init__(self, url: str, key: str, pool_size: int = 5):
        self.url = url
        self.key = key
        self.pool_size = pool_size
        self.clients = []
        self.semaphore = asyncio.Semaphore(pool_size)
    
    async def get_client(self):
        async with self.semaphore:
            if not self.clients:
                client = create_client(self.url, self.key)
                self.clients.append(client)
            return self.clients[0]
```

#### **Caching Strategy**
```python
import asyncio
from typing import Dict, Optional
import json

class KRACache:
    def __init__(self, ttl: int = 300):  # 5 minutes TTL
        self.cache = {}
        self.ttl = ttl
    
    async def get(self, key: str) -> Optional[Dict]:
        if key in self.cache:
            data, timestamp = self.cache[key]
            if asyncio.get_event_loop().time() - timestamp < self.ttl:
                return data
            else:
                del self.cache[key]
        return None
    
    async def set(self, key: str, data: Dict):
        self.cache[key] = (data, asyncio.get_event_loop().time())
```

### **3. Monitoring & Logging**

```python
import logging
import time
from functools import wraps

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def monitor_performance(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        start_time = time.time()
        try:
            result = await func(*args, **kwargs)
            execution_time = time.time() - start_time
            
            logger.info(f"{func.__name__} completed in {execution_time:.3f}s")
            
            # Log to performance metrics
            if hasattr(wrapper, 'supabase'):
                wrapper.supabase.table('performance_metrics').insert({
                    'metric_name': func.__name__,
                    'execution_time_ms': int(execution_time * 1000),
                    'status': 'success'
                }).execute()
            
            return result
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"{func.__name__} failed after {execution_time:.3f}s: {e}")
            raise
    
    return wrapper

# Usage
@monitor_performance
async def search_documentation(self, query: str):
    # Function implementation
    pass
```

---

## 📚 **QUICK REFERENCE**

### **Function Summary**

| Function | Purpose | Input | Output |
|----------|---------|-------|--------|
| `optimized_comprehensive_search` | Multi-table search | query, filters | search results |
| `optimized_validate_option_configuration` | Validate options | model_id, option_ids | validation result |
| `ai_get_available_options` | Get model options | model_id | available options |
| `ai_validate_configuration` | AI-friendly validation | model_id, option_names | detailed validation |
| `check_option_dependencies` | Check dependencies | model_id, option_ids | dependency analysis |
| `get_images_for_part_numbers` | Get part images | part_numbers | image data |
| `get_system_health_overview` | System health | none | health status |
| `get_performance_stats` | Performance metrics | metric_name, hours | performance data |

### **Common Use Cases**

1. **Error Code Lookup**: Use `optimized_comprehensive_search` with error code
2. **Option Validation**: Use `ai_validate_configuration` with option names
3. **Document Retrieval**: Use `get_hp_documentation_set` for related docs
4. **Image Search**: Use `get_images_for_part_numbers` for schematics
5. **System Monitoring**: Use `get_system_health_overview` for status

---

**🎯 This documentation provides everything needed for Python development with the KRAI Engine database functions!**
