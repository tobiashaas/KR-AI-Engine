#!/usr/bin/env python3
"""
🧠 Intelligent Document Classifier
Analyzes document content to automatically categorize documents

Features:
- Content-based categorization (not filename-based)
- Multi-language support
- Confidence scoring
- Manufacturer detection
- Document type classification
- Model number extraction
"""

import re
import json
from pathlib import Path
from typing import Dict, List, Tuple, Optional
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class IntelligentDocumentClassifier:
    """Intelligent document classifier based on content analysis"""
    
    def __init__(self):
        self.classification_patterns = self._load_classification_patterns()
        self.manufacturer_patterns = self._load_manufacturer_patterns()
        self.document_type_patterns = self._load_document_type_patterns()
        
    def _load_classification_patterns(self) -> Dict:
        """Load classification patterns for different document types"""
        return {
            'service_manual': {
                'keywords': [
                    'service manual', 'maintenance manual', 'repair manual',
                    'troubleshooting', 'disassembly', 'assembly',
                    'calibration', 'adjustment', 'replacement',
                    'error codes', 'diagnostic', 'preventive maintenance'
                ],
                'patterns': [
                    r'service\s+manual',
                    r'maintenance\s+manual',
                    r'repair\s+manual',
                    r'troubleshooting\s+guide',
                    r'chapter\s+\d+.*maintenance',
                    r'section\s+\d+.*repair'
                ],
                'weight': 1.0
            },
            'parts_catalog': {
                'keywords': [
                    'parts catalog', 'spare parts', 'replacement parts',
                    'part number', 'part list', 'components',
                    'accessories', 'consumables', 'order information'
                ],
                'patterns': [
                    r'parts\s+catalog',
                    r'spare\s+parts',
                    r'part\s+number.*\d+',
                    r'ordering\s+information',
                    r'price.*\$',
                    r'quantity.*\d+'
                ],
                'weight': 1.0
            },
            'cpmd_database': {
                'keywords': [
                    'cpmd', 'customer parts', 'maintenance data',
                    'error code', 'solution steps', 'field modification',
                    'technical bulletin', 'service bulletin', 'parts cross-reference'
                ],
                'patterns': [
                    r'cpmd.*database',
                    r'error\s+code.*\d+',
                    r'solution\s+steps',
                    r'field\s+modification',
                    r'technical\s+bulletin'
                ],
                'weight': 1.0
            },
            'technical_bulletin': {
                'keywords': [
                    'technical bulletin', 'service bulletin', 'field notice',
                    'urgent', 'critical', 'immediate action',
                    'bulletin number', 'issue description', 'resolution'
                ],
                'patterns': [
                    r'technical\s+bulletin',
                    r'service\s+bulletin',
                    r'field\s+notice',
                    r'bulletin\s+number',
                    r'urgent.*action'
                ],
                'weight': 1.0
            },
            'user_manual': {
                'keywords': [
                    'user manual', 'operation manual', 'user guide',
                    'getting started', 'basic operations', 'how to',
                    'installation guide', 'setup guide'
                ],
                'patterns': [
                    r'user\s+manual',
                    r'operation\s+manual',
                    r'getting\s+started',
                    r'basic\s+operations'
                ],
                'weight': 0.8
            }
        }
    
    def _load_manufacturer_patterns(self) -> Dict:
        """Load manufacturer detection patterns"""
        return {
            'hp': {
                'patterns': [
                    r'\bhp\b', r'hewlett.*packard', r'hp\s+laserjet',
                    r'hp\s+deskjet', r'hp\s+officejet', r'hp\s+photosmart'
                ],
                'model_patterns': [
                    r'HP\s+[A-Z0-9]+', r'LaserJet\s+[A-Z0-9]+',
                    r'DeskJet\s+[A-Z0-9]+', r'OfficeJet\s+[A-Z0-9]+'
                ]
            },
            'konica_minolta': {
                'patterns': [
                    r'konica\s+minolta', r'km\s+[a-z0-9]+',
                    r'minolta\s+[a-z0-9]+', r'bizhub'
                ],
                'model_patterns': [
                    r'KM\s+[A-Z0-9]+', r'BizHub\s+[A-Z0-9]+',
                    r'C\d+[a-z]?', r'P\d+[a-z]?'
                ]
            },
            'lexmark': {
                'patterns': [
                    r'lexmark', r'lexmark\s+[a-z0-9]+'
                ],
                'model_patterns': [
                    r'Lexmark\s+[A-Z0-9]+', r'MS\d+', r'MX\d+',
                    r'CX\d+', r'XC\d+'
                ]
            },
            'utax': {
                'patterns': [
                    r'utax', r'utax\s+[a-z0-9]+'
                ],
                'model_patterns': [
                    r'UTAX\s+[A-Z0-9]+', r'P-\d+[A-Z]+',
                    r'P-C\d+[A-Z]+'
                ]
            },
            'canon': {
                'patterns': [
                    r'canon', r'imageRUNNER', r'imagePRESS'
                ],
                'model_patterns': [
                    r'Canon\s+[A-Z0-9]+', r'imageRUNNER\s+[A-Z0-9]+',
                    r'imagePRESS\s+[A-Z0-9]+'
                ]
            },
            'epson': {
                'patterns': [
                    r'epson', r'workforce', r'expression'
                ],
                'model_patterns': [
                    r'Epson\s+[A-Z0-9]+', r'WorkForce\s+[A-Z0-9]+',
                    r'Expression\s+[A-Z0-9]+'
                ]
            }
        }
    
    def _load_document_type_patterns(self) -> Dict:
        """Load document type specific patterns"""
        return {
            'error_codes': [
                r'error\s+(\d+\.?\d*)', r'code\s+(\d+\.?\d*)',
                r'e(\d+)', r'error\s+code\s+(\d+)'
            ],
            'part_numbers': [
                r'part\s+number[:\s]+([A-Z0-9\-]+)',
                r'pn[:\s]+([A-Z0-9\-]+)',
                r'([A-Z]{2,4}\d{4,6}[A-Z]?)'
            ],
            'model_numbers': [
                r'model[:\s]+([A-Z0-9\-]+)',
                r'series[:\s]+([A-Z0-9\-]+)',
                r'([A-Z]{2,4}\d{3,6}[A-Z]?)'
            ],
            'versions': [
                r'version[:\s]+([0-9\.]+)',
                r'ver[:\s]+([0-9\.]+)',
                r'v([0-9\.]+)'
            ]
        }
    
    def classify_document(self, content: str, filename: str = "") -> Dict:
        """Classify document based on content analysis"""
        logger.info(f"🧠 Analyzing document content for classification...")
        
        # Normalize content for analysis
        content_lower = content.lower()
        content_length = len(content)
        
        # Initialize classification results
        classification = {
            'document_type': 'unknown',
            'document_type_confidence': 0.0,
            'manufacturer': 'unknown',
            'manufacturer_confidence': 0.0,
            'model_numbers': [],
            'error_codes': [],
            'part_numbers': [],
            'version_info': '',
            'content_analysis': {
                'total_words': len(content.split()),
                'total_characters': content_length,
                'has_technical_content': False,
                'has_parts_info': False,
                'has_error_codes': False
            },
            'classification_metadata': {
                'analysis_timestamp': datetime.utcnow().isoformat(),
                'filename_hint': filename,
                'analysis_method': 'content_based'
            }
        }
        
        # Analyze document type
        doc_type_result = self._analyze_document_type(content_lower)
        classification.update(doc_type_result)
        
        # Analyze manufacturer
        manufacturer_result = self._analyze_manufacturer(content_lower)
        classification.update(manufacturer_result)
        
        # Extract technical information
        tech_info = self._extract_technical_information(content)
        classification.update(tech_info)
        
        # Analyze content characteristics
        content_analysis = self._analyze_content_characteristics(content_lower)
        classification['content_analysis'].update(content_analysis)
        
        logger.info(f"✅ Classification completed: {classification['document_type']} ({classification['document_type_confidence']:.2f})")
        
        return classification
    
    def _analyze_document_type(self, content: str) -> Dict:
        """Analyze document type based on content patterns"""
        scores = {}
        
        for doc_type, patterns in self.classification_patterns.items():
            score = 0.0
            
            # Check keywords
            for keyword in patterns['keywords']:
                count = content.count(keyword)
                score += count * 0.1
            
            # Check regex patterns
            for pattern in patterns['patterns']:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 0.2
            
            # Apply weight
            score *= patterns['weight']
            scores[doc_type] = score
        
        # Find best match
        if scores:
            best_type = max(scores, key=scores.get)
            confidence = min(scores[best_type] / 10.0, 1.0)  # Normalize to 0-1
        else:
            best_type = 'unknown'
            confidence = 0.0
        
        return {
            'document_type': best_type,
            'document_type_confidence': confidence,
            'type_scores': scores
        }
    
    def _analyze_manufacturer(self, content: str) -> Dict:
        """Analyze manufacturer based on content patterns"""
        scores = {}
        
        for manufacturer, patterns in self.manufacturer_patterns.items():
            score = 0.0
            
            # Check manufacturer patterns
            for pattern in patterns['patterns']:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 0.3
            
            # Check model patterns
            for pattern in patterns['model_patterns']:
                matches = len(re.findall(pattern, content, re.IGNORECASE))
                score += matches * 0.5
            
            scores[manufacturer] = score
        
        # Find best match
        if scores:
            best_manufacturer = max(scores, key=scores.get)
            confidence = min(scores[best_manufacturer] / 5.0, 1.0)  # Normalize to 0-1
        else:
            best_manufacturer = 'unknown'
            confidence = 0.0
        
        return {
            'manufacturer': best_manufacturer,
            'manufacturer_confidence': confidence,
            'manufacturer_scores': scores
        }
    
    def _extract_technical_information(self, content: str) -> Dict:
        """Extract technical information from document"""
        result = {
            'model_numbers': [],
            'error_codes': [],
            'part_numbers': [],
            'version_info': ''
        }
        
        # Extract error codes
        for pattern in self.document_type_patterns['error_codes']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            result['error_codes'].extend(matches)
        
        # Extract part numbers
        for pattern in self.document_type_patterns['part_numbers']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            result['part_numbers'].extend(matches)
        
        # Extract model numbers
        for pattern in self.document_type_patterns['model_numbers']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            result['model_numbers'].extend(matches)
        
        # Extract version info
        for pattern in self.document_type_patterns['versions']:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                result['version_info'] = matches[0]
                break
        
        # Remove duplicates and clean up
        result['error_codes'] = list(set(result['error_codes']))
        result['part_numbers'] = list(set(result['part_numbers']))
        result['model_numbers'] = list(set(result['model_numbers']))
        
        return result
    
    def _analyze_content_characteristics(self, content: str) -> Dict:
        """Analyze content characteristics"""
        return {
            'has_technical_content': any(word in content for word in [
                'technical', 'specification', 'procedure', 'calibration',
                'maintenance', 'repair', 'troubleshooting'
            ]),
            'has_parts_info': any(word in content for word in [
                'part number', 'component', 'assembly', 'replacement'
            ]),
            'has_error_codes': bool(re.search(r'error\s+code|code\s+\d+', content)),
            'has_diagrams': any(word in content for word in [
                'diagram', 'figure', 'illustration', 'drawing'
            ]),
            'has_procedures': any(word in content for word in [
                'step 1', 'procedure', 'instructions', 'follow these steps'
            ])
        }

def main():
    """Test the intelligent document classifier"""
    print("🧠 Intelligent Document Classifier")
    print("=" * 50)
    
    classifier = IntelligentDocumentClassifier()
    
    # Test with sample content
    sample_content = """
    HP LaserJet Pro 4000 Series Service Manual
    Chapter 1: Introduction
    This service manual provides comprehensive maintenance and repair procedures.
    
    Error Code 13.20: Paper Jam in Duplex Unit
    Solution Steps:
    1. Open duplex unit cover
    2. Remove jammed paper
    
    Part Number: C4127-60001 - Fuser Assembly
    """
    
    result = classifier.classify_document(sample_content, "HP_4000_SM.pdf")
    
    print(f"Document Type: {result['document_type']} (confidence: {result['document_type_confidence']:.2f})")
    print(f"Manufacturer: {result['manufacturer']} (confidence: {result['manufacturer_confidence']:.2f})")
    print(f"Model Numbers: {result['model_numbers']}")
    print(f"Error Codes: {result['error_codes']}")
    print(f"Part Numbers: {result['part_numbers']}")

if __name__ == "__main__":
    main()
