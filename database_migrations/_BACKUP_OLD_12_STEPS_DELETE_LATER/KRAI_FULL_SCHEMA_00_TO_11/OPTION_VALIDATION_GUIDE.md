# ⚙️ KRAI ENGINE - OPTION VALIDATION GUIDE

**Complex Printer Option Dependencies & AI Agent Integration**  
**Version**: 2.0 Production Ready  
**Date**: December 2024  

---

## 🎯 **OVERVIEW**

This guide covers the complex world of printer option dependencies, where certain combinations work together while others conflict. The KRAI Engine handles these intricate relationships through sophisticated validation functions.

### **The Problem We Solve**
```
❓ "Kopierer mit Option XYZ" - But what if...
   - Option A conflicts with Option B?
   - Option X requires Option Y?
   - Option Z needs Option A but conflicts with Option C?
```

**Our Solution**: Intelligent validation that understands all these relationships! 🧠

---

## 🏗️ **OPTION ARCHITECTURE**

### **Hierarchy Structure**
```
Manufacturer (HP Inc.)
├── Series (OfficeJet Pro)
    ├── Model (9025)
        ├── Option (Bridge A)
        ├── Option (Bridge B) 
        ├── Option (Finisher X)
        └── Option (Finisher Y)
```

### **Relationship Types**

#### **1. 🔗 DEPENDENCIES (Requires)**
- **Finisher X** → **requires** → **Bridge A**
- **Finisher Y** → **requires** → **Bridge B**

#### **2. ⚔️ MUTUAL EXCLUSION (Conflicts)**
- **Bridge A** → **conflicts** → **Bridge B**
- **Bridge B** → **conflicts** → **Bridge A**

#### **3. 🔄 COMPLEX COMBINATIONS**
- **Bridge A + Finisher X** ✅ (Valid - Finisher X requires Bridge A)
- **Bridge B + Finisher Y** ✅ (Valid - Finisher Y requires Bridge B)
- **Bridge A + Finisher Y** ❌ (Invalid - Finisher Y requires Bridge B)
- **Bridge B + Finisher X** ❌ (Invalid - Finisher X requires Bridge A)
- **Bridge A + Bridge B** ❌ (Invalid - Mutually exclusive)

---

## 🧪 **VALIDATION SCENARIOS**

### **Scenario 1: Valid Configuration**
**Configuration**: HP 9025 + Bridge A + Finisher X

```sql
-- AI Agent Query
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY['Bridge A', 'Finisher X']
);
```

**Expected Result**:
```json
{
  "configuration_valid": true,
  "validation_summary": "Configuration is valid and ready for installation",
  "errors": [],
  "warnings": [],
  "suggestions": []
}
```

**Why Valid**:
- ✅ Bridge A is compatible with HP 9025
- ✅ Finisher X is compatible with HP 9025
- ✅ Finisher X requires Bridge A (dependency satisfied)
- ✅ No mutual exclusions triggered

---

### **Scenario 2: Dependency Missing**
**Configuration**: HP 9025 + Bridge A + Finisher Y

```sql
-- AI Agent Query
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY['Bridge A', 'Finisher Y']
);
```

**Expected Result**:
```json
{
  "configuration_valid": false,
  "validation_summary": "Configuration has issues that need to be resolved",
  "errors": [
    "Finisher Y requires Bridge B, but Bridge A is selected"
  ],
  "warnings": [],
  "suggestions": [
    "Try removing conflicting options or adding required dependencies"
  ]
}
```

**Why Invalid**:
- ❌ Finisher Y requires Bridge B
- ❌ Bridge A is selected instead of Bridge B
- 💡 **Solution**: Replace Bridge A with Bridge B

---

### **Scenario 3: Mutual Exclusion**
**Configuration**: HP 9025 + Bridge A + Bridge B

```sql
-- AI Agent Query
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY['Bridge A', 'Bridge B']
);
```

**Expected Result**:
```json
{
  "configuration_valid": false,
  "validation_summary": "Configuration has issues that need to be resolved",
  "errors": [
    "Bridge A and Bridge B are mutually exclusive"
  ],
  "warnings": [],
  "suggestions": [
    "Try removing conflicting options or adding required dependencies"
  ]
}
```

**Why Invalid**:
- ❌ Bridge A and Bridge B cannot coexist
- ❌ Physical space constraints
- 💡 **Solution**: Choose either Bridge A OR Bridge B

---

### **Scenario 4: Complex Dependency Chain**
**Configuration**: HP 9025 + Bridge B + Finisher X

```sql
-- AI Agent Query
SELECT * FROM krai_config.ai_validate_configuration(
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model ID
    ARRAY['Bridge B', 'Finisher X']
);
```

**Expected Result**:
```json
{
  "configuration_valid": false,
  "validation_summary": "Configuration has issues that need to be resolved",
  "errors": [
    "Finisher X cannot work with Bridge B"
  ],
  "warnings": [],
  "suggestions": [
    "Try removing conflicting options or adding required dependencies"
  ]
}
```

**Why Invalid**:
- ❌ Finisher X requires Bridge A
- ❌ Bridge B is selected instead of Bridge A
- ❌ Incompatible combination
- 💡 **Solution**: Either use Bridge A + Finisher X OR Bridge B + Finisher Y

---

## 🤖 **AI AGENT INTEGRATION**

### **Python Implementation**

```python
import asyncio
from typing import Dict, List, Optional

class OptionValidator:
    def __init__(self, supabase_client):
        self.supabase = supabase_client
    
    async def validate_configuration(self, model_name: str, option_names: List[str]) -> Dict:
        """Validate option configuration with AI-friendly interface"""
        try:
            # Get model ID by name
            model_id = await self._get_model_id_by_name(model_name)
            if not model_id:
                return {
                    "configuration_valid": False,
                    "errors": [f"Model '{model_name}' not found"],
                    "suggestions": []
                }
            
            # Validate configuration
            result = self.supabase.rpc(
                'ai_validate_configuration',
                {
                    'model_id': model_id,
                    'option_names': option_names
                }
            ).execute()
            
            return result.data[0] if result.data else {}
            
        except Exception as e:
            return {
                "configuration_valid": False,
                "errors": [f"Validation error: {str(e)}"],
                "suggestions": []
            }
    
    async def get_available_options(self, model_name: str) -> List[Dict]:
        """Get available options for a model with dependency information"""
        try:
            model_id = await self._get_model_id_by_name(model_name)
            if not model_id:
                return []
            
            result = self.supabase.rpc(
                'ai_get_available_options',
                {'model_id': model_id}
            ).execute()
            
            return result.data
            
        except Exception as e:
            print(f"Error getting options: {e}")
            return []
    
    async def suggest_configuration(self, model_name: str, desired_options: List[str]) -> Dict:
        """Suggest valid configuration based on desired options"""
        try:
            available_options = await self.get_available_options(model_name)
            
            # Try to build valid configuration
            valid_config = []
            conflicts = []
            missing_deps = []
            
            for desired_option in desired_options:
                # Find option in available options
                option_info = next(
                    (opt for opt in available_options if opt['option_name'] == desired_option),
                    None
                )
                
                if not option_info:
                    conflicts.append(f"Option '{desired_option}' not available")
                    continue
                
                # Check dependencies
                if option_info['dependencies']:
                    for dep in option_info['dependencies']:
                        if not any(opt in valid_config for opt in [dep]):
                            missing_deps.append(f"{desired_option} requires {dep}")
                
                # Check conflicts
                if option_info['conflicts_with']:
                    for conflict in option_info['conflicts_with']:
                        if conflict in valid_config:
                            conflicts.append(f"{desired_option} conflicts with {conflict}")
                
                valid_config.append(desired_option)
            
            return {
                "suggested_configuration": valid_config,
                "conflicts": conflicts,
                "missing_dependencies": missing_deps,
                "is_valid": len(conflicts) == 0 and len(missing_deps) == 0
            }
            
        except Exception as e:
            return {
                "suggested_configuration": [],
                "conflicts": [f"Error: {str(e)}"],
                "missing_dependencies": [],
                "is_valid": False
            }
    
    async def _get_model_id_by_name(self, model_name: str) -> Optional[str]:
        """Get model ID by display name"""
        try:
            result = self.supabase.table('products').select('id').eq(
                'display_name', model_name
            ).eq('product_type', 'model').execute()
            
            return result.data[0]['id'] if result.data else None
            
        except Exception as e:
            print(f"Error getting model ID: {e}")
            return None

# Usage Examples
async def main():
    validator = OptionValidator(supabase_client)
    
    # Example 1: Validate valid configuration
    print("=== Valid Configuration ===")
    result = await validator.validate_configuration(
        "HP OfficeJet Pro 9025",
        ["Bridge A", "Finisher X"]
    )
    print(f"Valid: {result.get('configuration_valid')}")
    print(f"Summary: {result.get('validation_summary')}")
    
    # Example 2: Validate invalid configuration
    print("\n=== Invalid Configuration ===")
    result = await validator.validate_configuration(
        "HP OfficeJet Pro 9025",
        ["Bridge A", "Finisher Y"]
    )
    print(f"Valid: {result.get('configuration_valid')}")
    print(f"Errors: {result.get('errors')}")
    
    # Example 3: Get available options
    print("\n=== Available Options ===")
    options = await validator.get_available_options("HP OfficeJet Pro 9025")
    for option in options:
        print(f"- {option['option_name']}: {option['dependencies']}")
    
    # Example 4: Suggest configuration
    print("\n=== Suggested Configuration ===")
    suggestion = await validator.suggest_configuration(
        "HP OfficeJet Pro 9025",
        ["Finisher X", "Bridge A"]
    )
    print(f"Suggested: {suggestion['suggested_configuration']}")
    print(f"Conflicts: {suggestion['conflicts']}")

if __name__ == "__main__":
    asyncio.run(main())
```

---

## 📋 **TESTING SCENARIOS**

### **Test Suite for Option Validation**

```python
import pytest
from typing import List, Dict

class TestOptionValidation:
    def __init__(self, validator):
        self.validator = validator
        self.model_name = "HP OfficeJet Pro 9025"
    
    async def test_valid_configurations(self):
        """Test all valid configuration combinations"""
        valid_configs = [
            ["Bridge A", "Finisher X"],
            ["Bridge B", "Finisher Y"],
            ["Bridge A"],  # Single option
            ["Bridge B"],  # Single option
        ]
        
        for config in valid_configs:
            result = await self.validator.validate_configuration(
                self.model_name, config
            )
            assert result.get('configuration_valid') == True, f"Config {config} should be valid"
            print(f"✅ Valid config: {config}")
    
    async def test_invalid_configurations(self):
        """Test all invalid configuration combinations"""
        invalid_configs = [
            (["Bridge A", "Bridge B"], "Mutually exclusive bridges"),
            (["Bridge A", "Finisher Y"], "Wrong bridge for finisher"),
            (["Bridge B", "Finisher X"], "Wrong bridge for finisher"),
        ]
        
        for config, reason in invalid_configs:
            result = await self.validator.validate_configuration(
                self.model_name, config
            )
            assert result.get('configuration_valid') == False, f"Config {config} should be invalid: {reason}"
            print(f"❌ Invalid config: {config} - {reason}")
    
    async def test_dependency_validation(self):
        """Test dependency validation logic"""
        # Test missing dependency
        result = await self.validator.validate_configuration(
            self.model_name, ["Finisher X"]  # Missing Bridge A
        )
        assert "requires Bridge A" in str(result.get('errors', [])), "Should detect missing dependency"
        print("✅ Dependency validation working")
    
    async def test_mutual_exclusion(self):
        """Test mutual exclusion logic"""
        result = await self.validator.validate_configuration(
            self.model_name, ["Bridge A", "Bridge B"]
        )
        assert "mutually exclusive" in str(result.get('errors', [])), "Should detect mutual exclusion"
        print("✅ Mutual exclusion validation working")
    
    async def run_all_tests(self):
        """Run complete test suite"""
        print("🧪 Running Option Validation Tests...")
        
        await self.test_valid_configurations()
        await self.test_invalid_configurations()
        await self.test_dependency_validation()
        await self.test_mutual_exclusion()
        
        print("🎉 All tests passed!")

# Run tests
async def run_tests():
    validator = OptionValidator(supabase_client)
    test_suite = TestOptionValidation(validator)
    await test_suite.run_all_tests()

if __name__ == "__main__":
    asyncio.run(run_tests())
```

---

## 🎯 **REAL-WORLD EXAMPLES**

### **Example 1: Customer Service Scenario**
```
Customer: "I want HP 9025 with Bridge A and Finisher Y"

AI Agent Response:
❌ Configuration Invalid
📝 Issues:
   - Finisher Y requires Bridge B, but Bridge A is selected

💡 Suggestions:
   - Option 1: Use Bridge B + Finisher Y (recommended)
   - Option 2: Use Bridge A + Finisher X

🔧 Valid Configurations:
   - HP 9025 + Bridge A + Finisher X
   - HP 9025 + Bridge B + Finisher Y
```

### **Example 2: Technical Support Scenario**
```
Technician: "What options are available for HP 9025?"

AI Agent Response:
📋 Available Options:
   - Bridge A: Compatible, Conflicts with Bridge B
   - Bridge B: Compatible, Conflicts with Bridge A
   - Finisher X: Compatible, Requires Bridge A
   - Finisher Y: Compatible, Requires Bridge B

💡 Recommended Configurations:
   - For basic setup: Bridge A + Finisher X
   - For advanced setup: Bridge B + Finisher Y
```

### **Example 3: Sales Configuration Scenario**
```
Sales Rep: "Can I configure HP 9025 with both Bridge A and Bridge B?"

AI Agent Response:
❌ Not Possible
📝 Reason: Bridge A and Bridge B are mutually exclusive due to physical space constraints

✅ Alternative Options:
   - HP 9025 + Bridge A + Finisher X
   - HP 9025 + Bridge B + Finisher Y
   - HP 9025 + Bridge A (basic configuration)
   - HP 9025 + Bridge B (basic configuration)
```

---

## 🔧 **MAINTENANCE & EXTENSION**

### **Adding New Options**
```sql
-- 1. Add new option to products table
INSERT INTO krai_core.products (
    manufacturer_id, product_type, parent_id, name, display_name,
    option_category, is_active
) VALUES (
    '550e8400-e29b-41d4-a716-446655440001',  -- HP Inc.
    'option',
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025 Model
    'Extra Tray',
    'HP Extra Paper Tray',
    'tray',
    true
);

-- 2. Add compatibility rules
INSERT INTO krai_config.product_compatibility (
    base_product_id, option_product_id, is_compatible,
    installation_notes, mutually_exclusive_options
) VALUES (
    '660e8400-e29b-41d4-a716-446655440002',  -- HP 9025
    'NEW-EXTRA-TRAY-ID',                      -- New Extra Tray
    true,
    'Provides additional paper capacity',
    ARRAY[]::uuid[]  -- No conflicts
);

-- 3. Update option groups if needed
UPDATE krai_config.option_groups 
SET option_product_ids = array_append(option_product_ids, 'NEW-EXTRA-TRAY-ID')
WHERE group_name = 'Tray Group' AND manufacturer_id = '550e8400-e29b-41d4-a716-446655440001';
```

### **Adding New Dependencies**
```sql
-- Add complex dependency rule
INSERT INTO krai_config.product_compatibility (
    base_product_id, option_product_id, is_compatible,
    installation_notes, option_rules
) VALUES (
    'MODEL-ID',
    'OPTION-ID',
    true,
    'Complex installation with multiple dependencies',
    '{"requires": ["bridge_a", "finisher_x"], "conflicts": ["bridge_b"], "max_count": 1}'::jsonb
);
```

---

## 📊 **PERFORMANCE CONSIDERATIONS**

### **Optimization Tips**
1. **Use Materialized Views**: For frequently accessed option data
2. **Cache Results**: Cache validation results for common configurations
3. **Batch Validation**: Validate multiple configurations in one call
4. **Index Optimization**: Ensure proper indexes on compatibility tables

### **Monitoring**
```sql
-- Monitor validation performance
SELECT 
    metric_name,
    AVG(execution_time_ms) as avg_time,
    MAX(execution_time_ms) as max_time,
    COUNT(*) as total_calls
FROM krai_system.performance_metrics 
WHERE metric_name LIKE '%validate%'
GROUP BY metric_name;
```

---

**🎯 This guide provides everything needed to implement and maintain complex option validation in the KRAI Engine!**
