#!/usr/bin/env python3
"""
JSON-based Version Extractor using configuration files
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple

class JSONVersionExtractor:
    """Version extractor using JSON configuration"""
    
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_dir = Path(config_path)
        else:
            # Default to backend config directory
            self.config_dir = Path(__file__).parent.parent.parent / "backend" / "config"
        self.version_config = self._load_version_config()
        self.patterns = self._compile_patterns()
    
    def _load_version_config(self) -> Dict:
        """Load version patterns configuration"""
        try:
            config_file = self.config_dir / "version_patterns.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load version config: {e}")
            return {}
    
    def _compile_patterns(self) -> Dict:
        """Compile regex patterns from configuration"""
        compiled_patterns = {}
        
        if not self.version_config.get('version_patterns'):
            return compiled_patterns
        
        patterns_config = self.version_config['version_patterns']['patterns']
        
        for category, category_data in patterns_config.items():
            compiled_patterns[category] = []
            
            for pattern_info in category_data['patterns']:
                try:
                    compiled_pattern = re.compile(pattern_info['pattern'], re.IGNORECASE)
                    compiled_patterns[category].append({
                        'pattern': compiled_pattern,
                        'info': pattern_info
                    })
                except re.error as e:
                    print(f"Failed to compile pattern {pattern_info['pattern']}: {e}")
        
        return compiled_patterns
    
    def extract_version(self, text: str, manufacturer: str = None, document_type: str = None) -> Dict:
        """
        Extract version information from text using JSON configuration
        
        Args:
            text: Text content to search
            manufacturer: Optional manufacturer for specific patterns
            document_type: Optional document type for specific patterns
            
        Returns:
            Dictionary with version information
        """
        result = {
            'version': '',
            'confidence': 0.0,
            'pattern_category': '',
            'pattern_info': {},
            'matches': [],
            'extraction_method': 'json_config'
        }
        
        if not self.patterns:
            return result
        
        # Get search order from config
        search_order = self.version_config.get('version_patterns', {}).get('extraction_settings', {}).get('search_order', [])
        
        # If manufacturer specified, prioritize manufacturer-specific patterns
        if manufacturer and manufacturer.lower() in self.version_config.get('version_patterns', {}).get('manufacturer_specific', {}):
            manu_config = self.version_config['version_patterns']['manufacturer_specific'][manufacturer.lower()]
            preferred_patterns = manu_config.get('preferred_patterns', [])
            # Reorder search order to prioritize manufacturer patterns
            search_order = preferred_patterns + [p for p in search_order if p not in preferred_patterns]
        
        # Search through patterns in order
        for category in search_order:
            if category not in self.patterns:
                continue
                
            for pattern_data in self.patterns[category]:
                pattern = pattern_data['pattern']
                info = pattern_data['info']
                
                # Search for matches
                matches = pattern.findall(text)
                
                if matches:
                    # Take first match (or combine if configured)
                    match = matches[0] if isinstance(matches[0], str) else matches[0]
                    
                    # Format output according to pattern configuration
                    version = self._format_version(match, info, pattern)
                    
                    # Validate version
                    if self._validate_version(version):
                        result['version'] = version
                        result['confidence'] = 1.0 - (search_order.index(category) * 0.1)
                        result['pattern_category'] = category
                        result['pattern_info'] = info
                        result['matches'] = matches
                        
                        return result
        
        return result
    
    def _format_version(self, match, pattern_info: Dict, pattern) -> str:
        """Format version according to pattern configuration"""
        output_format = pattern_info.get('output_format', '{version}')
        
        if isinstance(match, tuple):
            # Multiple capture groups
            if len(match) == 2:
                return output_format.format(edition=match[0], date=match[1], version=match[0], month_year=match[0])
            else:
                return output_format.format(version=match[0], month_year=match[0])
        else:
            # Single capture group - handle all possible format keys
            format_dict = {
                'version': match,
                'edition': match,
                'date': match,
                'month_year': match
            }
            return output_format.format(**format_dict)
    
    def _validate_version(self, version: str) -> bool:
        """Validate extracted version"""
        if not version:
            return False
        
        validation_config = self.version_config.get('version_patterns', {}).get('validation', {})
        
        # Check length
        min_length = validation_config.get('min_version_length', 1)
        max_length = validation_config.get('max_version_length', 50)
        
        if not (min_length <= len(version) <= max_length):
            return False
        
        # Check allowed characters
        allowed_chars = validation_config.get('allowed_characters', '0-9a-zA-Z.,/-\\s')
        allowed_pattern = f'^[{allowed_chars}]+$'
        
        if not re.match(allowed_pattern, version):
            return False
        
        # Check forbidden patterns
        forbidden_patterns = validation_config.get('forbidden_patterns', [])
        for forbidden in forbidden_patterns:
            if re.search(forbidden, version, re.IGNORECASE):
                return False
        
        return True
    
    def get_manufacturer_examples(self, manufacturer: str) -> List[Dict]:
        """Get version examples for a specific manufacturer"""
        manu_config = self.version_config.get('version_patterns', {}).get('manufacturer_specific', {}).get(manufacturer.lower(), {})
        return manu_config.get('examples', [])
    
    def get_pattern_categories(self) -> List[str]:
        """Get available pattern categories"""
        return list(self.patterns.keys())
    
    def test_patterns(self, test_cases: List[Dict]) -> Dict:
        """Test version patterns with provided test cases"""
        results = {
            'total_tests': len(test_cases),
            'successful_extractions': 0,
            'failed_extractions': 0,
            'results': []
        }
        
        for test_case in test_cases:
            text = test_case.get('text', '')
            expected = test_case.get('expected', '')
            manufacturer = test_case.get('manufacturer')
            
            extracted = self.extract_version(text, manufacturer)
            
            test_result = {
                'test_case': test_case,
                'extracted_version': extracted['version'],
                'expected_version': expected,
                'confidence': extracted['confidence'],
                'pattern_category': extracted['pattern_category'],
                'success': expected.lower() in extracted['version'].lower() or extracted['version'].lower() in expected.lower()
            }
            
            results['results'].append(test_result)
            
            if test_result['success']:
                results['successful_extractions'] += 1
            else:
                results['failed_extractions'] += 1
        
        results['success_rate'] = results['successful_extractions'] / results['total_tests'] if results['total_tests'] > 0 else 0
        
        return results

def main():
    """Test the JSON version extractor"""
    extractor = JSONVersionExtractor()
    
    print("🔍 JSON VERSION EXTRACTOR TEST")
    print("=" * 50)
    
    # Test cases based on real document versions
    test_cases = [
        {
            'text': 'Service Manual Edition 3, 5/2024',
            'expected': 'Edition 3, 5/2024',
            'manufacturer': 'hp'
        },
        {
            'text': 'November 2024 Service Manual',
            'expected': 'November 2024',
            'manufacturer': 'lexmark'
        },
        {
            'text': 'CPMD Database Edition 4.0, 04/2025',
            'expected': 'Edition 4.0, 04/2025',
            'manufacturer': 'hp'
        },
        {
            'text': 'Service Manual 2024/12/25',
            'expected': '2024/12/25',
            'manufacturer': 'konica_minolta'
        },
        {
            'text': 'Service Manual 2022/09/29',
            'expected': '2022/09/29',
            'manufacturer': 'konica_minolta'
        },
        {
            'text': 'Firmware Version 4.2',
            'expected': 'FW 4.2',
            'manufacturer': 'konica_minolta'
        }
    ]
    
    # Run tests
    results = extractor.test_patterns(test_cases)
    
    print(f"📊 TEST RESULTS:")
    print(f"   Total Tests: {results['total_tests']}")
    print(f"   Successful: {results['successful_extractions']}")
    print(f"   Failed: {results['failed_extractions']}")
    print(f"   Success Rate: {results['success_rate']:.1%}")
    print()
    
    # Show detailed results
    for result in results['results']:
        status = "✅" if result['success'] else "❌"
        print(f"{status} {result['test_case']['text']}")
        print(f"   Expected: {result['expected_version']}")
        print(f"   Extracted: {result['extracted_version']}")
        print(f"   Pattern: {result['pattern_category']}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print()
    
    # Show manufacturer examples
    print("📋 MANUFACTURER EXAMPLES:")
    for manufacturer in ['hp', 'lexmark', 'konica_minolta']:
        examples = extractor.get_manufacturer_examples(manufacturer)
        if examples:
            print(f"   {manufacturer.upper()}:")
            for example in examples:
                print(f"     {example['document_type']}: {example['version_format']}")
            print()

if __name__ == "__main__":
    main()
