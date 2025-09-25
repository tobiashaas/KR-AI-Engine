#!/usr/bin/env python3
"""
🚀 JSON Config Document Classifier
Uses JSON configuration files for error codes, part numbers, and chunk settings

Features:
- JSON-based error code patterns
- JSON-based part number patterns
- JSON-based chunk settings
- Dashboard-ready configuration
- Easy to modify and extend
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class JSONConfigClassifier:
    """Document classifier using JSON configuration files"""
    
    def __init__(self, config_path: str = None):
        if config_path:
            self.config_dir = Path(config_path)
        else:
            # Default to backend config directory
            self.config_dir = Path(__file__).parent.parent.parent / "backend" / "config"
        self.error_patterns = self._load_error_patterns()
        self.part_patterns = self._load_part_patterns()
        self.chunk_settings = self._load_chunk_settings()
        self.manufacturer_patterns = self._load_manufacturer_patterns()
        self.document_type_patterns = self._load_document_type_patterns()
        
    def _load_error_patterns(self) -> Dict:
        """Load error code patterns from JSON configuration"""
        try:
            config_file = self.config_dir / "error_code_patterns.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('error_code_patterns', {})
        except Exception as e:
            logger.error(f"Failed to load error patterns: {e}")
            return {}
    
    def _load_part_patterns(self) -> Dict:
        """Load part number patterns from JSON configuration"""
        try:
            config_file = self.config_dir / "error_code_patterns.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('part_number_patterns', {})
        except Exception as e:
            logger.error(f"Failed to load part patterns: {e}")
            return {}
    
    def _load_chunk_settings(self) -> Dict:
        """Load chunk settings from JSON configuration"""
        try:
            config_file = self.config_dir / "chunk_settings.json"
            with open(config_file, 'r', encoding='utf-8') as f:
                config = json.load(f)
            return config.get('chunk_settings', {})
        except Exception as e:
            logger.error(f"Failed to load chunk settings: {e}")
            return {}
    
    def _load_manufacturer_patterns(self) -> Dict:
        """Load manufacturer detection patterns"""
        return {
            'hp': {
                'filename_patterns': [r'^hp_', r'^hp-', r'_hp_'],
                'content_patterns': [
                    r'\bhp\b', r'hewlett.*packard', r'hp\s+laserjet',
                    r'hp\s+deskjet', r'hp\s+officejet', r'hp\s+photosmart',
                    r'hp\s+enterprise', r'hp\s+designjet', r'hp\s+color'
                ],
                'model_series': [
                    r'LaserJet\s+([A-Z0-9]+)', r'DeskJet\s+([A-Z0-9]+)',
                    r'OfficeJet\s+([A-Z0-9]+)', r'Photosmart\s+([A-Z0-9]+)',
                    r'Enterprise\s+([A-Z0-9]+)', r'DesignJet\s+([A-Z0-9]+)',
                    r'Color\s+([A-Z0-9]+)', r'E\s*(\d+)', r'X\s*(\d+)',
                    r'M\s*(\d+)', r'P\s*(\d+)'
                ],
                'confidence_boost': 1.0
            },
            'konica_minolta': {
                'filename_patterns': [r'^km_', r'^km-', r'_km_'],
                'content_patterns': [
                    r'konica\s+minolta', r'km\s+[a-z0-9]+',
                    r'minolta\s+[a-z0-9]+', r'bizhub', r'bizhub\s+[a-z0-9]+'
                ],
                'model_series': [
                    r'BizHub\s+([A-Z0-9]+)', r'KM\s+([A-Z0-9]+)',
                    r'C\s*(\d+[a-z]?)', r'P\s*(\d+[a-z]?)',
                    r'(\d+[a-z]?)\s+series', r'(\d+[a-z]?)\s+model'
                ],
                'confidence_boost': 1.0
            },
            'lexmark': {
                'filename_patterns': [r'^lexmark_', r'^lexmark-', r'_lexmark_'],
                'content_patterns': [
                    r'lexmark', r'lexmark\s+[a-z0-9]+'
                ],
                'model_series': [
                    r'Lexmark\s+([A-Z0-9]+)', r'MS\s*(\d+)', r'MX\s*(\d+)',
                    r'CX\s*(\d+)', r'XC\s*(\d+)', r'MB\s*(\d+)',
                    r'CS\s*(\d+[a-z]?)', r'C\s*(\d+[a-z]?)'
                ],
                'confidence_boost': 1.0
            },
            'utax': {
                'filename_patterns': [r'^utax_', r'^utax-', r'_utax_'],
                'content_patterns': [
                    r'utax', r'utax\s+[a-z0-9]+'
                ],
                'model_series': [
                    r'UTAX\s+([A-Z0-9]+)', r'P-\s*(\d+[A-Z]+)',
                    r'P-C\s*(\d+[A-Z]+)', r'(\d+[a-z]?)\s+ci',
                    r'(\d+[a-z]?)\s+i'
                ],
                'confidence_boost': 1.0
            }
        }
    
    def _load_document_type_patterns(self) -> Dict:
        """Load document type detection patterns"""
        return {
            'service_manual': {
                'filename_keywords': ['sm', 'service_manual', 'maintenance_manual'],
                'content_keywords': [
                    'service manual', 'maintenance manual', 'repair manual',
                    'troubleshooting', 'disassembly', 'assembly',
                    'calibration', 'adjustment', 'replacement',
                    'error codes', 'diagnostic', 'preventive maintenance'
                ],
                'content_patterns': [
                    r'service\s+manual', r'maintenance\s+manual',
                    r'repair\s+manual', r'troubleshooting\s+guide',
                    r'chapter\s+\d+.*maintenance', r'section\s+\d+.*repair'
                ],
                'confidence_weight': 1.0
            },
            'parts_catalog': {
                'filename_keywords': ['parts', 'catalog', 'spare_parts'],
                'content_keywords': [
                    'parts catalog', 'spare parts', 'replacement parts',
                    'part number', 'part list', 'components',
                    'accessories', 'consumables', 'order information'
                ],
                'content_patterns': [
                    r'parts\s+catalog', r'spare\s+parts',
                    r'part\s+number.*\d+', r'ordering\s+information',
                    r'price.*\$', r'quantity.*\d+'
                ],
                'confidence_weight': 1.0
            },
            'cpmd_database': {
                'filename_keywords': ['cpmd', 'customer_parts'],
                'content_keywords': [
                    'cpmd', 'customer parts', 'maintenance data',
                    'error code', 'solution steps', 'field modification',
                    'technical bulletin', 'service bulletin', 'parts cross-reference'
                ],
                'content_patterns': [
                    r'cpmd.*database', r'error\s+code.*\d+',
                    r'solution\s+steps', r'field\s+modification',
                    r'technical\s+bulletin'
                ],
                'confidence_weight': 1.0
            },
            'technical_bulletin': {
                'filename_keywords': ['technical', 'bulletin', 'bt', 'troubleshooting'],
                'content_keywords': [
                    'technical bulletin', 'service bulletin', 'field notice',
                    'urgent', 'critical', 'immediate action',
                    'bulletin number', 'issue description', 'resolution'
                ],
                'content_patterns': [
                    r'technical\s+bulletin', r'service\s+bulletin',
                    r'field\s+notice', r'bulletin\s+number',
                    r'urgent.*action'
                ],
                'confidence_weight': 1.0
            }
        }
    
    def classify_document(self, filename: str, content: str = "") -> Dict:
        """Classify document using JSON configuration"""
        logger.info(f"🚀 Starting JSON config classification for: {filename}")
        
        # Initialize result structure
        result = {
            'filename': filename,
            'classification': {
                'document_type': 'unknown',
                'document_type_confidence': 0.0,
                'manufacturer': 'unknown',
                'manufacturer_confidence': 0.0,
                'series': 'unknown',
                'series_confidence': 0.0,
                'models': [],
                'version': '',
                'version_confidence': 0.0
            },
            'extraction': {
                'model_numbers': [],
                'error_codes': [],
                'part_numbers': [],
                'series_info': {},
                'technical_info': {}
            },
            'chunking': {
                'recommended_strategy': 'contextual_chunking',
                'chunk_size': 1000,
                'chunk_overlap': 150,
                'settings': {}
            },
            'analysis': {
                'filename_analysis': {},
                'content_analysis': {},
                'hybrid_confidence': 0.0,
                'analysis_timestamp': datetime.utcnow().isoformat()
            }
        }
        
        # 1. Filename-based analysis
        filename_result = self._analyze_filename(filename)
        result['analysis']['filename_analysis'] = filename_result
        
        # 2. Content-based analysis (if content provided)
        content_result = {}
        if content.strip():
            content_result = self._analyze_content(content)
            result['analysis']['content_analysis'] = content_result
        
        # 3. Hybrid classification logic
        final_classification = self._hybrid_classification(filename_result, content_result)
        result['classification'].update(final_classification)
        
        # 4. Extract technical information using JSON config
        if content.strip():
            tech_info = self._extract_technical_information_json(content, final_classification['manufacturer'])
            result['extraction'].update(tech_info)
        
        # 5. Detect series information
        series_info = self._detect_series(filename, content, final_classification['manufacturer'])
        result['extraction']['series_info'] = series_info
        
        # 6. Determine chunking strategy based on JSON config
        chunking_info = self._determine_chunking_strategy(final_classification)
        result['chunking'].update(chunking_info)
        
        # 7. Calculate hybrid confidence
        result['analysis']['hybrid_confidence'] = self._calculate_hybrid_confidence(
            filename_result, content_result, final_classification
        )
        
        logger.info(f"✅ JSON config classification completed: {result['classification']['document_type']} "
                   f"({result['analysis']['hybrid_confidence']:.2f})")
        
        return result
    
    def _analyze_filename(self, filename: str) -> Dict:
        """Analyze filename for classification hints"""
        filename_lower = filename.lower()
        result = {
            'manufacturer': 'unknown',
            'manufacturer_confidence': 0.0,
            'document_type': 'unknown',
            'document_type_confidence': 0.0,
            'models': [],
            'version': '',
            'confidence': 0.0
        }
        
        # Manufacturer detection from filename
        for manufacturer, patterns in self.manufacturer_patterns.items():
            for pattern in patterns['filename_patterns']:
                if re.search(pattern, filename_lower):
                    result['manufacturer'] = manufacturer
                    result['manufacturer_confidence'] = 0.9  # High confidence for filename
                    break
            if result['manufacturer'] != 'unknown':
                break
        
        # Document type detection from filename
        for doc_type, patterns in self.document_type_patterns.items():
            for keyword in patterns['filename_keywords']:
                if keyword in filename_lower:
                    result['document_type'] = doc_type
                    result['document_type_confidence'] = 0.8  # High confidence for filename
                    break
            if result['document_type'] != 'unknown':
                break
        
        # Model extraction from filename
        models = self._extract_models_from_filename(filename)
        result['models'] = models
        
        # Version extraction from filename
        version = self._extract_version_from_filename(filename)
        result['version'] = version
        
        # Overall filename confidence
        result['confidence'] = (result['manufacturer_confidence'] + result['document_type_confidence']) / 2
        
        return result
    
    def _analyze_content(self, content: str) -> Dict:
        """Analyze document content for classification"""
        content_lower = content.lower()
        result = {
            'manufacturer': 'unknown',
            'manufacturer_confidence': 0.0,
            'document_type': 'unknown',
            'document_type_confidence': 0.0,
            'models': [],
            'version': '',
            'confidence': 0.0
        }
        
        # Manufacturer detection from content
        manufacturer_scores = {}
        for manufacturer, patterns in self.manufacturer_patterns.items():
            score = 0.0
            for pattern in patterns['content_patterns']:
                matches = len(re.findall(pattern, content_lower, re.IGNORECASE))
                score += matches * 0.3
            
            # Check model series patterns
            for pattern in patterns['model_series']:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 0.5
            
            manufacturer_scores[manufacturer] = score
        
        if manufacturer_scores:
            best_manufacturer = max(manufacturer_scores, key=manufacturer_scores.get)
            if manufacturer_scores[best_manufacturer] > 0:
                result['manufacturer'] = best_manufacturer
                result['manufacturer_confidence'] = min(manufacturer_scores[best_manufacturer] / 5.0, 1.0)
        
        # Document type detection from content
        doc_type_scores = {}
        for doc_type, patterns in self.document_type_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns['content_keywords']:
                count = content_lower.count(keyword)
                score += count * 0.1
            
            # Check regex patterns
            for pattern in patterns['content_patterns']:
                matches = len(re.findall(pattern, content_lower, re.IGNORECASE))
                score += matches * 0.2
            
            # Apply weight
            score *= patterns['confidence_weight']
            doc_type_scores[doc_type] = score
        
        if doc_type_scores:
            best_type = max(doc_type_scores, key=doc_type_scores.get)
            if doc_type_scores[best_type] > 0:
                result['document_type'] = best_type
                result['document_type_confidence'] = min(doc_type_scores[best_type] / 10.0, 1.0)
        
        # Model extraction from content
        models = self._extract_models_from_content(content, result['manufacturer'])
        result['models'] = models
        
        # Version extraction from content
        version = self._extract_version_from_content(content)
        result['version'] = version
        
        # Overall content confidence
        result['confidence'] = (result['manufacturer_confidence'] + result['document_type_confidence']) / 2
        
        return result
    
    def _extract_models_from_filename(self, filename: str) -> List[str]:
        """Extract model numbers from filename"""
        models = []
        
        # Remove file extension
        name_without_ext = Path(filename).stem
        
        # Extract potential model numbers using general patterns
        general_patterns = [
            r'([A-Z]{2,4}\d{3,6}[A-Z]?)',  # Standard model format
            r'([A-Z]+\d{3,6}[A-Z]?)',     # Alternative format
            r'(\d{3,6}[A-Z]{2,4})',       # Number-first format
            r'([A-Z]\d{3,6}[A-Z]?)',      # Single letter prefix
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, name_without_ext, re.IGNORECASE)
            models.extend(matches)
        
        # Clean and validate model numbers
        cleaned_models = []
        for model in models:
            if len(model) >= 3 and model.isalnum():  # Basic validation
                cleaned_models.append(model.upper())
        
        return list(set(cleaned_models))  # Remove duplicates
    
    def _extract_models_from_content(self, content: str, manufacturer: str) -> List[str]:
        """Extract model numbers from document content"""
        models = []
        
        # Use manufacturer-specific patterns if available
        if manufacturer in self.manufacturer_patterns:
            patterns = self.manufacturer_patterns[manufacturer]['model_series']
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                models.extend(matches)
        
        # Use general patterns as fallback
        general_patterns = [
            r'([A-Z]{2,4}\d{3,6}[A-Z]?)',  # Standard model format
            r'([A-Z]+\d{3,6}[A-Z]?)',     # Alternative format
            r'(\d{3,6}[A-Z]{2,4})',       # Number-first format
            r'([A-Z]\d{3,6}[A-Z]?)',      # Single letter prefix
        ]
        
        for pattern in general_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            models.extend(matches)
        
        # Clean and validate model numbers
        cleaned_models = []
        for model in models:
            if len(model) >= 3 and model.isalnum():
                cleaned_models.append(model.upper())
        
        return list(set(cleaned_models))  # Remove duplicates
    
    def _extract_version_from_filename(self, filename: str) -> str:
        """Extract version information from filename"""
        version_patterns = [
            r'version\s+([0-9\.]+)', r'ver\s+([0-9\.]+)',
            r'v\s*([0-9\.]+)', r'rev\s+([0-9\.]+)',
            r'revision\s+([0-9\.]+)', r'edition\s+([0-9]+(?:\\.[0-9]+)?)',
            r'fw\s+([0-9\.]+)', r'firmware\s+([0-9\.]+)',
            r'function\s+version\s+([0-9\.]+)',
            r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)',  # Standard version format
            r'([0-9]+\.[0-9]+[A-Z]?)',         # Version with letter
            r'([A-Z]\d+\.\d+)',                # Letter prefix version
            r'([0-9]{4}/[0-9]{2}/[0-9]{2})',   # Date format: 2024/12/25
            r'([0-9]{2}/[0-9]{4})',            # Date format: 5/2024
            r'([a-z]+\\s+[0-9]{4})',           # Date format: November 2024
        ]
        
        # Check for version patterns in filename
        for pattern in version_patterns:
            match = re.search(pattern, filename, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_version_from_content(self, content: str) -> str:
        """Extract version information from document content"""
        # Check document info patterns first (most reliable)
        document_info_patterns = [
            r'manual\s+([0-9\.]+)', r'service\s+manual\s+([0-9\.]+)',
            r'parts\s+catalog\s+([0-9\.]+)', r'bulletin\s+([0-9\.]+)',
            r'edition\s+([0-9]+(?:\.[0-9]+)?)\s*,?\s*([0-9]+/[0-9]{4})',  # Edition 3, 5/2024
            r'edition\s+([0-9]+(?:\.[0-9]+)?)',  # Edition 4.0
            r'([a-z]+\s+[0-9]{4})',  # November 2024
        ]
        
        for pattern in document_info_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) > 1:
                    # Return combined format for Edition + Date
                    return f"{match.group(1)}, {match.group(2)}"
                return match.group(1)
        
        # Check general version patterns
        version_patterns = [
            r'version\s+([0-9\.]+)', r'ver\s+([0-9\.]+)',
            r'v\s*([0-9\.]+)', r'rev\s+([0-9\.]+)',
            r'revision\s+([0-9\.]+)', r'edition\s+([0-9]+(?:\\.[0-9]+)?)',
            r'fw\s+([0-9\.]+)', r'firmware\s+([0-9\.]+)',
            r'function\s+version\s+([0-9\.]+)',
            r'([0-9]+\.[0-9]+(?:\.[0-9]+)?)',  # Standard version format
            r'([0-9]+\.[0-9]+[A-Z]?)',         # Version with letter
            r'([A-Z]\d+\.\d+)',                # Letter prefix version
            r'([0-9]{4}/[0-9]{2}/[0-9]{2})',   # Date format: 2024/12/25
            r'([0-9]{2}/[0-9]{4})',            # Date format: 5/2024
            r'([0-9]{4}/[0-9]{2}/[0-9]{2})',   # Date format: 2022/09/29
        ]
        
        for pattern in version_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                return match.group(1)
        
        return ''
    
    def _extract_technical_information_json(self, content: str, manufacturer: str) -> Dict:
        """Extract technical information using JSON configuration"""
        return {
            'model_numbers': self._extract_models_from_content(content, manufacturer),
            'error_codes': self._extract_error_codes_json(content, manufacturer),
            'part_numbers': self._extract_part_numbers_json(content, manufacturer),
            'technical_info': self._analyze_technical_content(content)
        }
    
    def _extract_error_codes_json(self, content: str, manufacturer: str) -> List[Dict]:
        """Extract error codes using JSON configuration"""
        error_codes = []
        
        # Get manufacturer-specific patterns from JSON config
        if manufacturer.lower() in self.error_patterns:
            manufacturer_config = self.error_patterns[manufacturer.lower()]
            patterns = manufacturer_config.get('patterns', [])
            validation_regex = manufacturer_config.get('validation_regex', '')
            examples = manufacturer_config.get('examples', [])
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Validate the error code format
                    if re.match(validation_regex, match):
                        # Find matching example for description
                        description = "Unknown error"
                        category = "unknown"
                        for example in examples:
                            if example['code'] == match:
                                description = example['description']
                                category = example['category']
                                break
                        
                        error_codes.append({
                            'code': match,
                            'description': description,
                            'category': category,
                            'manufacturer': manufacturer
                        })
        
        return error_codes
    
    def _extract_part_numbers_json(self, content: str, manufacturer: str) -> List[Dict]:
        """Extract part numbers using JSON configuration"""
        part_numbers = []
        
        # Get manufacturer-specific patterns from JSON config
        if manufacturer.lower() in self.part_patterns:
            manufacturer_config = self.part_patterns[manufacturer.lower()]
            patterns = manufacturer_config.get('patterns', [])
            validation_regex = manufacturer_config.get('validation_regex', '')
            examples = manufacturer_config.get('examples', [])
            
            for pattern in patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    # Validate the part number format
                    if re.match(validation_regex, match):
                        # Find matching example for description
                        description = "Unknown part"
                        category = "unknown"
                        models = []
                        for example in examples:
                            if example['part_number'] == match:
                                description = example['description']
                                category = example['category']
                                models = example.get('models', [])
                                break
                        
                        part_numbers.append({
                            'part_number': match,
                            'description': description,
                            'category': category,
                            'models': models,
                            'manufacturer': manufacturer
                        })
        
        return part_numbers
    
    def _detect_series(self, filename: str, content: str, manufacturer: str) -> Dict:
        """Detect printer series for better filtering"""
        series_info = {
            'detected_series': 'unknown',
            'confidence': 0.0,
            'series_models': [],
            'description': ''
        }
        
        if manufacturer == 'unknown':
            return series_info
        
        # Series detection logic (simplified for now)
        content_lower = content.lower() if content else ''
        filename_lower = filename.lower()
        
        # HP series detection
        if manufacturer.lower() == 'hp':
            if 'laserjet pro' in content_lower or 'laserjet pro' in filename_lower:
                series_info['detected_series'] = 'LaserJet Pro'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Professional laser printer series'
            elif 'deskjet' in content_lower or 'deskjet' in filename_lower:
                series_info['detected_series'] = 'DeskJet'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Consumer inkjet printer series'
            elif 'officejet' in content_lower or 'officejet' in filename_lower:
                series_info['detected_series'] = 'OfficeJet'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Office multifunction printer series'
        
        # Konica Minolta series detection
        elif manufacturer.lower() == 'konica_minolta':
            if 'bizhub' in content_lower or 'bizhub' in filename_lower:
                series_info['detected_series'] = 'BizHub'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Business multifunction printer series'
        
        # Lexmark series detection
        elif manufacturer.lower() == 'lexmark':
            if 'cx' in content_lower or 'cx' in filename_lower:
                series_info['detected_series'] = 'CX Series'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Color multifunction printer series'
        
        # UTAX series detection
        elif manufacturer.lower() == 'utax':
            if 'ci' in content_lower or 'ci' in filename_lower:
                series_info['detected_series'] = 'Ci Series'
                series_info['confidence'] = 0.9
                series_info['description'] = 'Color imaging printer series'
        
        return series_info
    
    def _determine_chunking_strategy(self, classification: Dict) -> Dict:
        """Determine chunking strategy based on JSON configuration"""
        document_type = classification.get('document_type', 'unknown')
        manufacturer = classification.get('manufacturer', 'unknown')
        
        # Get default strategy
        default_strategy = self.chunk_settings.get('default_strategy', 'contextual_chunking')
        
        # Get document type specific settings
        doc_type_settings = self.chunk_settings.get('document_type_specific', {})
        if document_type in doc_type_settings:
            settings = doc_type_settings[document_type]
            return {
                'recommended_strategy': settings.get('preferred_strategy', default_strategy),
                'chunk_size': settings.get('chunk_size', 1000),
                'chunk_overlap': settings.get('chunk_overlap', 150),
                'settings': settings
            }
        
        # Get manufacturer specific settings
        manufacturer_settings = self.chunk_settings.get('manufacturer_specific', {})
        if manufacturer in manufacturer_settings:
            settings = manufacturer_settings[manufacturer]
            multiplier = settings.get('chunk_size_multiplier', 1.0)
            return {
                'recommended_strategy': settings.get('preferred_strategy', default_strategy),
                'chunk_size': int(1000 * multiplier),
                'chunk_overlap': int(150 * multiplier),
                'settings': settings
            }
        
        # Return default settings
        return {
            'recommended_strategy': default_strategy,
            'chunk_size': 1000,
            'chunk_overlap': 150,
            'settings': {}
        }
    
    def _analyze_technical_content(self, content: str) -> Dict:
        """Analyze technical content characteristics"""
        content_lower = content.lower()
        
        return {
            'has_diagrams': any(word in content_lower for word in ['diagram', 'figure', 'illustration']),
            'has_procedures': any(word in content_lower for word in ['step 1', 'procedure', 'instructions']),
            'has_specifications': any(word in content_lower for word in ['specification', 'spec', 'technical data']),
            'has_troubleshooting': any(word in content_lower for word in ['troubleshooting', 'problem', 'solution']),
            'word_count': len(content.split()),
            'page_indicators': len(re.findall(r'page\s+\d+', content_lower))
        }
    
    def _hybrid_classification(self, filename_result: Dict, content_result: Dict) -> Dict:
        """Combine filename and content analysis for final classification"""
        result = {
            'document_type': 'unknown',
            'document_type_confidence': 0.0,
            'manufacturer': 'unknown',
            'manufacturer_confidence': 0.0,
            'series': 'unknown',
            'series_confidence': 0.0,
            'models': [],
            'version': '',
            'version_confidence': 0.0
        }
        
        # Manufacturer classification (prefer filename if high confidence)
        if filename_result['manufacturer_confidence'] >= 0.8:
            result['manufacturer'] = filename_result['manufacturer']
            result['manufacturer_confidence'] = filename_result['manufacturer_confidence']
        elif content_result and content_result['manufacturer_confidence'] > 0:
            result['manufacturer'] = content_result['manufacturer']
            result['manufacturer_confidence'] = content_result['manufacturer_confidence']
        else:
            result['manufacturer'] = filename_result['manufacturer']
            result['manufacturer_confidence'] = filename_result['manufacturer_confidence']
        
        # Document type classification (prefer filename if high confidence)
        if filename_result['document_type_confidence'] >= 0.8:
            result['document_type'] = filename_result['document_type']
            result['document_type_confidence'] = filename_result['document_type_confidence']
        elif content_result and content_result['document_type_confidence'] > 0:
            result['document_type'] = content_result['document_type']
            result['document_type_confidence'] = content_result['document_type_confidence']
        else:
            result['document_type'] = filename_result['document_type']
            result['document_type_confidence'] = filename_result['document_type_confidence']
        
        # Models (combine both sources)
        all_models = list(set(filename_result['models'] + (content_result.get('models', []) if content_result else [])))
        result['models'] = all_models
        
        # Version (prefer content if available)
        if content_result and content_result.get('version'):
            result['version'] = content_result['version']
            result['version_confidence'] = 0.8
        elif filename_result.get('version'):
            result['version'] = filename_result['version']
            result['version_confidence'] = 0.6
        else:
            result['version'] = ''
            result['version_confidence'] = 0.0
        
        return result
    
    def _calculate_hybrid_confidence(self, filename_result: Dict, content_result: Dict, final_classification: Dict) -> float:
        """Calculate overall hybrid confidence score"""
        # Base confidence from final classification
        base_confidence = (final_classification['manufacturer_confidence'] + 
                          final_classification['document_type_confidence']) / 2
        
        # Boost confidence if both filename and content agree
        if content_result:
            manufacturer_agreement = (filename_result['manufacturer'] == content_result['manufacturer'])
            type_agreement = (filename_result['document_type'] == content_result['document_type'])
            
            if manufacturer_agreement and type_agreement:
                base_confidence = min(base_confidence * 1.2, 1.0)
            elif manufacturer_agreement or type_agreement:
                base_confidence = min(base_confidence * 1.1, 1.0)
        
        # Boost confidence if we have models and version
        if final_classification['models']:
            base_confidence = min(base_confidence * 1.1, 1.0)
        
        if final_classification['version']:
            base_confidence = min(base_confidence * 1.1, 1.0)
        
        return base_confidence

def main():
    """Test the JSON config document classifier"""
    print("🚀 JSON Config Document Classifier")
    print("=" * 50)
    
    classifier = JSONConfigClassifier()
    
    # Test with sample data
    sample_filename = "HP_E786_SM_v2.1.pdf"
    sample_content = """
    HP LaserJet Pro E786 Series Service Manual
    Version 2.1 - January 2024
    
    This service manual provides comprehensive maintenance and repair procedures
    for the HP LaserJet Pro E786 series printers.
    
    Error Code 13.20.01: Paper Jam in Duplex Unit
    Solution Steps:
    1. Open duplex unit cover
    2. Remove jammed paper
    
    Part Number: C4127-60001 - Fuser Assembly
    """
    
    result = classifier.classify_document(sample_filename, sample_content)
    
    print(f"Document Type: {result['classification']['document_type']} (confidence: {result['classification']['document_type_confidence']:.2f})")
    print(f"Manufacturer: {result['classification']['manufacturer']} (confidence: {result['classification']['manufacturer_confidence']:.2f})")
    print(f"Series: {result['classification']['series']} (confidence: {result['classification']['series_confidence']:.2f})")
    print(f"Models: {result['classification']['models']}")
    print(f"Version: {result['classification']['version']}")
    print(f"Error Codes: {result['extraction']['error_codes']}")
    print(f"Part Numbers: {result['extraction']['part_numbers']}")
    print(f"Series Info: {result['extraction']['series_info']}")
    print(f"Chunking Strategy: {result['chunking']['recommended_strategy']}")
    print(f"Chunk Size: {result['chunking']['chunk_size']}")
    print(f"Hybrid Confidence: {result['analysis']['hybrid_confidence']:.2f}")

if __name__ == "__main__":
    main()
