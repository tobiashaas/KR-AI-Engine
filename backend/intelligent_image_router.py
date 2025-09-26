"""
Intelligent Image Router for KR-AI-Engine

Determines the correct storage bucket and image type based on:
- Document type (Service Manual, Parts Catalog)
- Image content analysis
- Upload source (Technician upload vs Document extraction)
"""

from enum import Enum
from typing import Dict, Any, Optional
import re
import logging

logger = logging.getLogger(__name__)

class ImageType(str, Enum):
    """Image type classification for storage routing"""
    ERROR_DEFECT = "error_defect"      # Techniker-uploaded defect images (AI/ML learning)
    MANUAL_INSTRUCTION = "manual_instruction"  # Service manual images (Agent context)
    PARTS_TECHNICAL = "parts_technical"    # Parts catalog technical drawings (Agent context)
    EXTRACTED_CONTENT = "extracted_content"  # Generic extracted content
    UNKNOWN = "unknown"

class ImageRouter:
    """Routes images to appropriate storage buckets based on content and context"""
    
    def __init__(self):
        # Patterns to identify different image types
        self.manual_keywords = [
            'remove', 'install', 'disassemble', 'assembly', 'screw', 'connector',
            'step', 'procedure', 'instruction', 'warning', 'caution', 'note',
            'arrow', 'diagram', 'illustration'
        ]
        
        self.parts_keywords = [
            'part', 'component', 'exploded', 'view', 'drawing', 'technical',
            'specification', 'dimension', 'measurement', 'catalog', 'number',
            'assembly', 'subassembly', 'section', 'detail'
        ]
        
        # Storage bucket mapping
        # Schema-compliant bucket mapping: All images go to krai-images
        # Schema defines: krai-documents, krai-images, krai-videos  
        self.bucket_mapping = {
            ImageType.ERROR_DEFECT: "krai-images",
            ImageType.MANUAL_INSTRUCTION: "krai-images", 
            ImageType.PARTS_TECHNICAL: "krai-images",
            ImageType.EXTRACTED_CONTENT: "krai-images",
            ImageType.UNKNOWN: "krai-images"
        }
    
    def route_image(
        self, 
        document_type: str,
        document_filename: str,
        image_description: Optional[str] = None,
        upload_source: str = "extraction",
        ai_analysis: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Route image to appropriate storage bucket
        
        Args:
            document_type: Type of source document (service_manual, parts_catalog, etc.)
            document_filename: Name of source document
            image_description: AI-generated description of image content
            upload_source: 'upload' (technician) or 'extraction' (document processing)
            ai_analysis: Optional AI analysis results
            
        Returns:
            Dict with image_type, storage_bucket, requires_anonymization
        """
        
        # 1. TECHNICIAN UPLOADS = ERROR/DEFECT IMAGES
        if upload_source == "upload":
            logger.info(f"🚨 Technician-uploaded image → ERROR_DEFECT category")
            return {
                "image_type": ImageType.ERROR_DEFECT,
                "storage_bucket": self.bucket_mapping[ImageType.ERROR_DEFECT], 
                "requires_anonymization": True,  # DSGVO compliance
                "routing_reason": "Technician upload - assumed defect image"
            }
        
        # 2. DOCUMENT EXTRACTION ROUTING
        if upload_source == "extraction":
            image_type = self._classify_extracted_image(
                document_type, document_filename, image_description, ai_analysis
            )
            
            return {
                "image_type": image_type,
                "storage_bucket": self.bucket_mapping[image_type],
                "requires_anonymization": False,  # Extracted images don't need anonymization
                "routing_reason": f"Document extraction from {document_type}"
            }
        
        # 3. DEFAULT FALLBACK
        logger.warning(f"⚠️ Unknown upload source: {upload_source}")
        return {
            "image_type": ImageType.UNKNOWN,
            "storage_bucket": self.bucket_mapping[ImageType.UNKNOWN],
            "requires_anonymization": False,
            "routing_reason": "Unknown source - default routing"
        }
    
    def _classify_extracted_image(
        self,
        document_type: str,
        document_filename: str, 
        image_description: Optional[str],
        ai_analysis: Optional[Dict[str, Any]]
    ) -> ImageType:
        """Classify extracted images based on document type and content"""
        
        # Normalize inputs
        doc_type = document_type.lower() if document_type else ""
        filename = document_filename.lower() if document_filename else ""
        description = image_description.lower() if image_description else ""
        
        # 1. PARTS CATALOG DETECTION
        if self._is_parts_catalog(doc_type, filename):
            logger.info(f"🔧 Parts catalog image → PARTS_TECHNICAL")
            return ImageType.PARTS_TECHNICAL
        
        # 2. SERVICE MANUAL DETECTION  
        if self._is_service_manual(doc_type, filename):
            # Check if it's instructional content
            if self._is_instructional_image(description, ai_analysis):
                logger.info(f"📖 Service manual instruction → MANUAL_INSTRUCTION")
                return ImageType.MANUAL_INSTRUCTION
            else:
                logger.info(f"📄 Service manual content → EXTRACTED_CONTENT")
                return ImageType.EXTRACTED_CONTENT
        
        # 3. DEFAULT FOR EXTRACTED CONTENT
        logger.info(f"📄 Generic extraction → EXTRACTED_CONTENT")
        return ImageType.EXTRACTED_CONTENT
    
    def _is_parts_catalog(self, doc_type: str, filename: str) -> bool:
        """Detect if document is a parts catalog"""
        parts_indicators = [
            'parts', 'catalog', 'parts_catalog', 'spare', 'component',
            'exploded', 'assembly', 'technical_drawing'
        ]
        
        return any(indicator in doc_type or indicator in filename 
                  for indicator in parts_indicators)
    
    def _is_service_manual(self, doc_type: str, filename: str) -> bool:
        """Detect if document is a service manual"""
        manual_indicators = [
            'service', 'manual', 'service_manual', 'repair', 'maintenance',
            'installation', 'user_manual', 'technical_manual'
        ]
        
        return any(indicator in doc_type or indicator in filename 
                  for indicator in manual_indicators)
    
    def _is_instructional_image(
        self, 
        description: str, 
        ai_analysis: Optional[Dict[str, Any]]
    ) -> bool:
        """Detect if image contains instructional content"""
        
        # Check description for instructional keywords
        instruction_score = sum(1 for keyword in self.manual_keywords 
                              if keyword in description)
        
        # Check AI analysis if available
        if ai_analysis:
            # Look for arrows, diagrams, step indicators
            if ai_analysis.get('has_arrows', False):
                instruction_score += 2
            if ai_analysis.get('has_diagrams', False):
                instruction_score += 2
            if ai_analysis.get('has_steps', False):
                instruction_score += 3
        
        # Threshold for instructional content
        return instruction_score >= 2

# Global router instance
image_router = ImageRouter()
