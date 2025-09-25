#!/usr/bin/env python3
"""
Intelligent Model Extractor with Placeholder Handling
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Set

class IntelligentModelExtractor:
    """Extract models with intelligent placeholder handling"""
    
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_dir = Path(config_path)
        else:
            # Default to config directory relative to this file
            self.config_dir = Path(__file__).parent.parent / "config"
        self.placeholder_config = self._load_placeholder_config()
        self.known_models_db = self._load_known_models()
    
    def _load_placeholder_config(self) -> Dict:
        """Load placeholder patterns configuration"""
        try:
            config_file = self.config_dir / "model_placeholder_patterns.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Failed to load placeholder config: {e}")
            return {}
    
    def _load_known_models(self) -> Dict:
        """Load known models database"""
        # This would typically come from a database or API
        # For now, we'll use a static list
        return {
            "konica_minolta": {
                "i-series": ["C450i", "C451i", "C550i", "C551i", "C650i", "C651i", "C750i", "C751i"],
                "c-series": ["C450", "C550", "C650", "C750", "C850", "C950"],
                "bizhub": ["bizhub C450", "bizhub C550", "bizhub C650", "bizhub C750"]
            },
            "hp": {
                "laserjet_pro": ["HP LaserJet Pro 400", "HP LaserJet Pro 500", "HP LaserJet Pro 600"],
                "laserjet": ["HP 400", "HP 500", "HP 600"],
                "deskjet_2000": ["DeskJet 2130", "DeskJet 2132", "DeskJet 2134"]
            },
            "lexmark": {
                "cs_series": ["Lexmark CS725", "Lexmark CS820", "Lexmark CS925"]
            }
        }
    
    def extract_models(self, text: str, manufacturer: str = None, filename: str = None) -> Dict:
        """
        Extract models with intelligent placeholder handling
        
        Args:
            text: Text content to search
            manufacturer: Manufacturer context
            filename: Filename for additional context
            
        Returns:
            Dictionary with model extraction results
        """
        result = {
            'models': [],
            'placeholders': [],
            'series': [],
            'confidence': 0.0,
            'extraction_method': 'intelligent_placeholder_handling',
            'metadata': {
                'exact_matches': [],
                'placeholder_expansions': [],
                'series_inferences': [],
                'unknown_models': []
            }
        }
        
        # 1. Extract exact models first
        exact_models = self._extract_exact_models(text, manufacturer)
        result['models'].extend(exact_models)
        result['metadata']['exact_matches'] = exact_models
        
        # 2. Extract placeholders
        placeholders = self._extract_placeholders(text, manufacturer)
        result['placeholders'] = placeholders
        
        # 3. Expand placeholders to actual models
        expanded_models = self._expand_placeholders(placeholders, manufacturer)
        result['models'].extend(expanded_models)
        result['metadata']['placeholder_expansions'] = expanded_models
        
        # 4. Extract series information
        series = self._extract_series(text, manufacturer)
        result['series'] = series
        
        # 5. Infer models from series
        series_models = self._infer_models_from_series(series, manufacturer)
        result['models'].extend(series_models)
        result['metadata']['series_inferences'] = series_models
        
        # 6. Remove duplicates and calculate confidence
        result['models'] = list(set(result['models']))
        result['confidence'] = self._calculate_confidence(result)
        
        return result
    
    def _extract_exact_models(self, text: str, manufacturer: str = None) -> List[str]:
        """Extract exact model numbers"""
        exact_models = []
        
        # Common model patterns
        model_patterns = [
            r'\b([A-Z]\d{3,4}[A-Z]?)\b',  # C450i, C550i, etc.
            r'\b(HP\s+[A-Za-z0-9\s]+)\b',  # HP LaserJet Pro 400
            r'\b(Lexmark\s+[A-Za-z0-9\s]+)\b',  # Lexmark CS725
            r'\b(bizhub\s+[A-Za-z0-9\s]+)\b'  # bizhub C450
        ]
        
        for pattern in model_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if self._is_valid_model(match, manufacturer):
                    exact_models.append(match)
        
        return exact_models
    
    def _extract_placeholders(self, text: str, manufacturer: str = None) -> List[Dict]:
        """Extract placeholder patterns"""
        placeholders = []
        
        if not self.placeholder_config.get('model_placeholder_patterns'):
            return placeholders
        
        placeholder_types = self.placeholder_config['model_placeholder_patterns']['placeholder_types']
        
        for placeholder_type, type_data in placeholder_types.items():
            for example in type_data.get('examples', []):
                placeholder_text = example['placeholder']
                pattern = example['pattern']
                
                # Search for placeholder in text
                if re.search(placeholder_text, text, re.IGNORECASE):
                    placeholders.append({
                        'placeholder': placeholder_text,
                        'pattern': pattern,
                        'type': placeholder_type,
                        'manufacturer': example.get('manufacturer'),
                        'series': example.get('series'),
                        'actual_models': example.get('actual_models', [])
                    })
        
        return placeholders
    
    def _expand_placeholders(self, placeholders: List[Dict], manufacturer: str = None) -> List[str]:
        """Expand placeholders to actual models"""
        expanded_models = []
        
        for placeholder_info in placeholders:
            # Get actual models from placeholder info
            actual_models = placeholder_info.get('actual_models', [])
            
            # If no actual models provided, try to generate them
            if not actual_models:
                actual_models = self._generate_models_from_pattern(
                    placeholder_info['pattern'], 
                    manufacturer
                )
            
            expanded_models.extend(actual_models)
        
        return expanded_models
    
    def _generate_models_from_pattern(self, pattern: str, manufacturer: str = None) -> List[str]:
        """Generate models from regex pattern"""
        generated_models = []
        
        # This is a simplified version - in reality, you'd have more sophisticated logic
        if 'C\\d{3}0i' in pattern:
            # Generate C-series models ending with 0i
            for hundreds in range(4, 8):  # 4xx, 5xx, 6xx, 7xx
                for tens in range(0, 10):
                    model = f"C{hundreds}{tens}0i"
                    if self._is_known_model(model, manufacturer):
                        generated_models.append(model)
        
        elif 'C\\d{3}1i' in pattern:
            # Generate C-series models ending with 1i
            for hundreds in range(4, 8):
                for tens in range(0, 10):
                    model = f"C{hundreds}{tens}1i"
                    if self._is_known_model(model, manufacturer):
                        generated_models.append(model)
        
        return generated_models
    
    def _extract_series(self, text: str, manufacturer: str = None) -> List[Dict]:
        """Extract series information"""
        series = []
        
        series_patterns = [
            r'(i-series)',
            r'(bizhub\s+[A-Za-z]+)',
            r'(LaserJet\s+[A-Za-z]+)',
            r'(DeskJet\s+[A-Za-z]+)',
            r'(CS\s*[A-Za-z]*)',
            r'(C\s*[A-Za-z]*)'
        ]
        
        for pattern in series_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                series.append({
                    'series': match.strip(),
                    'manufacturer': manufacturer,
                    'confidence': 0.8
                })
        
        return series
    
    def _infer_models_from_series(self, series: List[Dict], manufacturer: str = None) -> List[str]:
        """Infer models from series information"""
        inferred_models = []
        
        for series_info in series:
            series_name = series_info['series'].lower()
            manu = series_info.get('manufacturer', manufacturer)
            
            # Look up models for this series
            if manu and manu in self.known_models_db:
                for known_series, models in self.known_models_db[manu].items():
                    if series_name in known_series.lower():
                        inferred_models.extend(models)
        
        return inferred_models
    
    def _is_valid_model(self, model: str, manufacturer: str = None) -> bool:
        """Check if a model is valid"""
        # Basic validation
        if len(model) < 3:
            return False
        
        # Check against known models
        return self._is_known_model(model, manufacturer)
    
    def _is_known_model(self, model: str, manufacturer: str = None) -> bool:
        """Check if model exists in known models database"""
        if manufacturer and manufacturer in self.known_models_db:
            for series_models in self.known_models_db[manufacturer].values():
                if model in series_models:
                    return True
        
        # Check all manufacturers
        for manu_models in self.known_models_db.values():
            for series_models in manu_models.values():
                if model in series_models:
                    return True
        
        return False
    
    def _calculate_confidence(self, result: Dict) -> float:
        """Calculate confidence score"""
        total_items = 0
        confident_items = 0
        
        # Exact matches get highest confidence
        if result['metadata']['exact_matches']:
            confident_items += len(result['metadata']['exact_matches'])
            total_items += len(result['metadata']['exact_matches'])
        
        # Placeholder expansions get medium confidence
        if result['metadata']['placeholder_expansions']:
            confident_items += len(result['metadata']['placeholder_expansions']) * 0.8
            total_items += len(result['metadata']['placeholder_expansions'])
        
        # Series inferences get lower confidence
        if result['metadata']['series_inferences']:
            confident_items += len(result['metadata']['series_inferences']) * 0.6
            total_items += len(result['metadata']['series_inferences'])
        
        if total_items == 0:
            return 0.0
        
        return confident_items / total_items
    
    def analyze_bulletin_example(self, text: str, filename: str = None) -> Dict:
        """Analyze the bulletin example specifically"""
        print("🔍 INTELLIGENT MODEL EXTRACTION - BULLETIN EXAMPLE")
        print("=" * 60)
        
        # Extract models
        result = self.extract_models(text, manufacturer="konica_minolta", filename=filename)
        
        print(f"📄 Filename: {filename}")
        print()
        
        print("🎯 EXTRACTION RESULTS:")
        print(f"   Models Found: {result['models']}")
        print(f"   Placeholders: {[p['placeholder'] for p in result['placeholders']]}")
        print(f"   Series: {[s['series'] for s in result['series']]}")
        print(f"   Confidence: {result['confidence']:.2f}")
        print()
        
        print("📊 EXTRACTION BREAKDOWN:")
        print(f"   Exact Matches: {result['metadata']['exact_matches']}")
        print(f"   Placeholder Expansions: {result['metadata']['placeholder_expansions']}")
        print(f"   Series Inferences: {result['metadata']['series_inferences']}")
        print()
        
        # Show placeholder details
        if result['placeholders']:
            print("🔍 PLACEHOLDER ANALYSIS:")
            for placeholder in result['placeholders']:
                print(f"   Placeholder: {placeholder['placeholder']}")
                print(f"   Pattern: {placeholder['pattern']}")
                print(f"   Type: {placeholder['type']}")
                print(f"   Series: {placeholder['series']}")
                print(f"   Actual Models: {placeholder['actual_models']}")
                print()
        
        return result

def main():
    """Test the intelligent model extractor with bulletin example"""
    extractor = IntelligentModelExtractor()
    
    # Test with the bulletin content
    bulletin_text = """
    © KONICA MINOLTA
    i-series (bizhub Cxx0i/Cxx1i)
    How to fix pale, light or faded image
    1 July 2025
    Office QA Div.
    Office OP Div.
    KONICA MINOLTA, INC.
    RFKM_BT2511234EN
    
    Contents
    How to fix pale, light or faded image when printing and copying
    in response to a user's request
    
    Case1: Halftone areas come out faint (such as skin tone)
    Case2: Want to deepen red color or make background color
    """
    
    filename = "i-series remedies to fix pale, light, or faint images (RFKM_BT2511234EN).pdf"
    
    result = extractor.analyze_bulletin_example(bulletin_text, filename)
    
    print("🎯 FINAL RECOMMENDATION:")
    print("=" * 40)
    
    if result['models']:
        print(f"✅ Recommended Models: {result['models']}")
    else:
        print("❌ No specific models identified")
    
    if result['placeholders']:
        print(f"📋 Placeholder Resolution: {[p['placeholder'] for p in result['placeholders']]} → {result['metadata']['placeholder_expansions']}")
    
    if result['series']:
        print(f"🏭 Series Identified: {[s['series'] for s in result['series']]}")

if __name__ == "__main__":
    main()
