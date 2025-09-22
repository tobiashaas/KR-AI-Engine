#!/usr/bin/env python3
"""
KRAI Engine - Interactive Document/Image Processing Script
==========================================================

This script provides interactive terminal-based processing for:
- Multi-manufacturer documents (PDF service manuals, parts catalogs, CPMD files)
- Print quality images with AI vision analysis and technician feedback
- Manual categorization that later integrates into Filament Dashboard

Phase 1: Interactive Terminal Processing
Phase 2: Filament Dashboard Integration (using data from Phase 1)

Usage:
    python krai_interactive_processor.py [file_path_or_folder]
"""

import os
import sys
import argparse
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import inquirer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.panel import Panel
from rich.text import Text

# Database connection
import psycopg2
from psycopg2.extras import RealDictCursor

# Document processing
import fitz  # PyMuPDF for PDF processing
import pytesseract
from PIL import Image
import cv2
import numpy as np

# AI/ML libraries
import torch
import torchvision.transforms as transforms
from transformers import AutoModel, AutoTokenizer
import openai  # For vector embeddings

# Configuration
from config import DATABASE_CONFIG, AI_CONFIG

console = Console()

class KRAIInteractiveProcessor:
    """
    Interactive processor for KRAI Engine documents and images.
    Supports multi-manufacturer processing with manual categorization.
    """
    
    def __init__(self):
        self.console = console
        self.db_connection = None
        self.supported_manufacturers = [
            "HP", "Canon", "Epson", "Brother", "Xerox", "Kyocera", "Ricoh", "Other"
        ]
        self.document_types = [
            "CPMD Database", "Service Manual", "Parts Catalog", "Print Quality Image"
        ]
        self.defect_types = [
            "Banding", "Streaking", "Color Issues", "Paper Jam", "Misalignment",
            "Smudging", "Fading", "Ghosting", "Spots/Dots", "Other"
        ]
        
    def connect_database(self) -> bool:
        """Establish database connection"""
        try:
            self.db_connection = psycopg2.connect(**DATABASE_CONFIG)
            console.print("✅ Database connected successfully", style="green")
            return True
        except Exception as e:
            console.print(f"❌ Database connection failed: {e}", style="red")
            return False
    
    def detect_file_type(self, file_path: str) -> Tuple[str, str]:
        """
        Detect file type and suggest document category
        Returns: (file_type, suggested_category)
        """
        file_ext = Path(file_path).suffix.lower()
        filename = Path(file_path).name.lower()
        
        if file_ext == '.pdf':
            if 'cpmd' in filename or 'hp' in filename:
                return "PDF", "CPMD Database"
            elif any(word in filename for word in ['service', 'manual', 'repair']):
                return "PDF", "Service Manual"
            elif any(word in filename for word in ['parts', 'catalog', 'spare']):
                return "PDF", "Parts Catalog"
            else:
                return "PDF", "Service Manual"  # Default for PDFs
        
        elif file_ext in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff']:
            return "Image", "Print Quality Image"
        
        else:
            return "Unknown", "Unknown"
    
    def interactive_manufacturer_selection(self) -> str:
        """Interactive manufacturer selection"""
        questions = [
            inquirer.List('manufacturer',
                message="🏢 Welcher Hersteller?",
                choices=self.supported_manufacturers,
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers['manufacturer']
    
    def interactive_document_type_selection(self, suggested_type: str) -> str:
        """Interactive document type selection with suggestion"""
        
        # Move suggested type to top of list
        choices = [suggested_type] + [t for t in self.document_types if t != suggested_type]
        
        questions = [
            inquirer.List('doc_type',
                message=f"📄 Dokumenttyp? (Vorschlag: {suggested_type})",
                choices=choices,
            ),
        ]
        answers = inquirer.prompt(questions)
        return answers['doc_type']
    
    def interactive_printer_model_input(self, manufacturer: str) -> str:
        """Interactive printer model input with autocomplete suggestions"""
        
        # Load common models from database or predefined list
        common_models = self.get_common_models_for_manufacturer(manufacturer)
        
        if common_models:
            questions = [
                inquirer.List('model',
                    message=f"🖨️ Drucker/Produktmodell für {manufacturer}?",
                    choices=common_models + ["Other (manual input)"],
                ),
            ]
            answer = inquirer.prompt(questions)
            
            if answer['model'] == "Other (manual input)":
                manual_input = inquirer.text(message="Bitte Modell eingeben:")
                return manual_input
            else:
                return answer['model']
        else:
            return inquirer.text(message=f"🖨️ Drucker/Produktmodell für {manufacturer}:")
    
    def get_common_models_for_manufacturer(self, manufacturer: str) -> List[str]:
        """Get common printer models for manufacturer from database"""
        try:
            with self.db_connection.cursor() as cursor:
                cursor.execute("""
                    SELECT DISTINCT model_name 
                    FROM products 
                    WHERE manufacturer = %s 
                    ORDER BY model_name LIMIT 20
                """, (manufacturer,))
                return [row[0] for row in cursor.fetchall()]
        except:
            # Fallback to predefined models
            models_by_manufacturer = {
                "HP": ["LaserJet Pro 4000", "LaserJet Pro MFP 4300", "OfficeJet Pro 9000", "DesignJet T200"],
                "Canon": ["PIXMA TR8500", "imageCLASS MF740C", "imagePROGRAF PRO-300", "MAXIFY GX7000"],
                "Epson": ["WorkForce Pro WF-4800", "EcoTank ET-4850", "SureColor P800", "Expression Photo XP-8500"],
                "Brother": ["HL-L3270CDW", "MFC-L8900CDW", "DCP-L2550DW", "QL-820NWB"],
                "Xerox": ["VersaLink C405", "WorkCentre 6515", "Phaser 6510", "AltaLink C8100"]
            }
            return models_by_manufacturer.get(manufacturer, [])
    
    def interactive_print_quality_analysis(self, image_path: str, manufacturer: str, model: str) -> Dict:
        """Interactive print quality analysis with technician feedback"""
        
        console.print("\n🖼️ PRINT QUALITY ANALYSIS", style="bold blue")
        console.print("=" * 50)
        
        # Step 1: Image type selection
        image_types = ["Test Page", "Defect Sample", "Before/After Comparison", "Calibration Print"]
        questions = [
            inquirer.List('image_type',
                message="🖼️ Bildtyp?",
                choices=image_types,
            ),
        ]
        image_type_answer = inquirer.prompt(questions)
        image_type = image_type_answer['image_type']
        
        # Step 2: Expected defects (multi-select)
        questions = [
            inquirer.Checkbox('expected_defects',
                message="🔧 Welche Probleme siehst du? (mehrere möglich)",
                choices=self.defect_types,
            ),
        ]
        defects_answer = inquirer.prompt(questions)
        expected_defects = defects_answer['expected_defects']
        
        # Step 3: Technician info
        technician_name = inquirer.text(message="👨‍💻 Dein Name (für ML Training):")
        
        # Step 4: AI Vision Analysis
        console.print("\n🤖 AI Vision Analysis läuft...", style="yellow")
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            task = progress.add_task(description="Analyzing image with AI...", total=None)
            ai_detected_defects = self.analyze_image_with_ai(image_path)
        
        # Step 5: Show AI results and get feedback
        console.print("\n🤖 AI Detection Results:", style="bold green")
        if ai_detected_defects:
            table = Table(show_header=True, header_style="bold magenta")
            table.add_column("Defect Type")
            table.add_column("Confidence")
            table.add_column("Location")
            
            for defect in ai_detected_defects:
                table.add_row(
                    defect['type'],
                    f"{defect['confidence']:.2f}",
                    f"({defect['x']}, {defect['y']})"
                )
            console.print(table)
        else:
            console.print("No defects detected by AI", style="yellow")
        
        # Step 6: Technician feedback on AI results
        if ai_detected_defects:
            questions = [
                inquirer.Confirm('ai_correct',
                    message="🎯 Stimmen die AI Ergebnisse?",
                    default=True,
                ),
            ]
            ai_feedback = inquirer.prompt(questions)
            
            if not ai_feedback['ai_correct']:
                # Collect detailed feedback
                wrong_detections = inquirer.text(message="❌ Welche Detections waren falsch? (komma-getrennt):")
                missing_defects = inquirer.text(message="➕ Welche Defekte hat die AI übersehen? (komma-getrennt):")
            else:
                wrong_detections = ""
                missing_defects = ""
        else:
            wrong_detections = ""
            missing_defects = inquirer.text(message="➕ Welche Defekte siehst du, die die AI übersehen hat? (komma-getrennt):")
        
        # Step 7: Overall quality rating
        quality_ratings = ["1 - Sehr schlecht", "2 - Schlecht", "3 - Mittel", "4 - Gut", "5 - Sehr gut"]
        questions = [
            inquirer.List('quality_rating',
                message="⭐ Gesamtqualität des Drucks?",
                choices=quality_ratings,
            ),
        ]
        quality_answer = inquirer.prompt(questions)
        quality_rating = int(quality_answer['quality_rating'][0])
        
        # Step 8: Additional notes
        additional_notes = inquirer.text(message="📝 Zusätzliche Notizen (optional):")
        
        return {
            'image_type': image_type,
            'expected_defects': expected_defects,
            'technician_name': technician_name,
            'ai_detected_defects': ai_detected_defects,
            'wrong_detections': wrong_detections,
            'missing_defects': missing_defects,
            'quality_rating': quality_rating,
            'additional_notes': additional_notes,
            'manufacturer': manufacturer,
            'model': model
        }
    
    def analyze_image_with_ai(self, image_path: str) -> List[Dict]:
        """
        AI Vision analysis for print quality defects
        Returns list of detected defects with confidence scores
        """
        # TODO: Implement actual AI vision models (YOLOv8, custom defect classifiers)
        # For now, return mock data
        
        # Simulate AI processing time
        import time
        time.sleep(2)
        
        # Mock AI results - replace with real AI vision implementation
        mock_defects = [
            {
                'type': 'Banding',
                'confidence': 0.85,
                'x': 120,
                'y': 200,
                'bbox': [100, 180, 200, 250]
            },
            {
                'type': 'Color Issues',
                'confidence': 0.72,
                'x': 300,
                'y': 150,
                'bbox': [280, 130, 350, 180]
            }
        ]
        
        return mock_defects
    
    def process_pdf_document(self, file_path: str, metadata: Dict) -> bool:
        """Process PDF document (CPMD, Service Manual, Parts Catalog)"""
        
        console.print(f"\n📄 Processing PDF: {Path(file_path).name}", style="bold blue")
        
        try:
            # Extract text using PyMuPDF
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(description="Extracting text from PDF...", total=None)
                
                doc = fitz.open(file_path)
                full_text = ""
                
                for page_num in range(len(doc)):
                    page = doc.load_page(page_num)
                    full_text += page.get_text()
                
                doc.close()
            
            # Process based on document type
            if metadata['document_type'] == 'CPMD Database':
                extracted_data = self.process_cpmd_content(full_text)
            elif metadata['document_type'] == 'Service Manual':
                extracted_data = self.process_service_manual_content(full_text)
            elif metadata['document_type'] == 'Parts Catalog':
                extracted_data = self.process_parts_catalog_content(full_text)
            
            # Store in database
            document_id = self.store_document_in_database(file_path, metadata, full_text, extracted_data)
            
            console.print(f"✅ Document processed and stored with ID: {document_id}", style="green")
            return True
            
        except Exception as e:
            console.print(f"❌ Error processing PDF: {e}", style="red")
            return False
    
    def process_cpmd_content(self, text: str) -> Dict:
        """Extract error codes and solutions from CPMD content"""
        # TODO: Implement CPMD-specific parsing logic
        return {"error_codes": [], "solutions": []}
    
    def process_service_manual_content(self, text: str) -> Dict:
        """Extract error codes and technical info from service manual"""
        # TODO: Implement service manual parsing logic
        return {"error_codes": [], "technical_procedures": []}
    
    def process_parts_catalog_content(self, text: str) -> Dict:
        """Extract part numbers and descriptions from parts catalog"""
        # TODO: Implement parts catalog parsing logic
        return {"part_numbers": [], "descriptions": []}
    
    def store_document_in_database(self, file_path: str, metadata: Dict, content: str, extracted_data: Dict) -> int:
        """Store document and metadata in database"""
        try:
            with self.db_connection.cursor() as cursor:
                # Insert into documents table
                cursor.execute("""
                    INSERT INTO documents (
                        filename, file_path, manufacturer, document_type, 
                        product_model, language, content, metadata, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    RETURNING id
                """, (
                    Path(file_path).name,
                    file_path,
                    metadata['manufacturer'],
                    metadata['document_type'],
                    metadata.get('product_model', ''),
                    metadata.get('language', 'EN'),
                    content,
                    extracted_data
                ))
                
                document_id = cursor.fetchone()[0]
                self.db_connection.commit()
                
                return document_id
                
        except Exception as e:
            self.db_connection.rollback()
            raise e
    
    def store_image_analysis_in_database(self, image_path: str, analysis_results: Dict) -> int:
        """Store image and print quality analysis in database"""
        try:
            with self.db_connection.cursor() as cursor:
                # Insert into images table
                cursor.execute("""
                    INSERT INTO images (
                        filename, file_path, manufacturer, printer_model, 
                        image_type, technician_name, quality_rating, 
                        ai_analysis_results, technician_feedback, created_at
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, NOW())
                    RETURNING id
                """, (
                    Path(image_path).name,
                    image_path,
                    analysis_results['manufacturer'],
                    analysis_results['model'],
                    analysis_results['image_type'],
                    analysis_results['technician_name'],
                    analysis_results['quality_rating'],
                    analysis_results['ai_detected_defects'],
                    {
                        'expected_defects': analysis_results['expected_defects'],
                        'wrong_detections': analysis_results['wrong_detections'],
                        'missing_defects': analysis_results['missing_defects'],
                        'additional_notes': analysis_results['additional_notes']
                    }
                ))
                
                image_id = cursor.fetchone()[0]
                
                # Insert detected defects into print_defects table
                for defect in analysis_results['ai_detected_defects']:
                    cursor.execute("""
                        INSERT INTO print_defects (
                            image_id, defect_type, confidence_score, 
                            x_coordinate, y_coordinate, bounding_box, created_at
                        ) VALUES (%s, %s, %s, %s, %s, %s, NOW())
                    """, (
                        image_id,
                        defect['type'],
                        defect['confidence'],
                        defect['x'],
                        defect['y'],
                        defect['bbox']
                    ))
                
                self.db_connection.commit()
                return image_id
                
        except Exception as e:
            self.db_connection.rollback()
            raise e
    
    def process_single_file(self, file_path: str) -> bool:
        """Process a single file (PDF or image)"""
        
        if not os.path.exists(file_path):
            console.print(f"❌ File not found: {file_path}", style="red")
            return False
        
        # Show file info
        file_info = Panel(
            f"📁 [bold]File:[/bold] {Path(file_path).name}\n"
            f"📏 [bold]Size:[/bold] {os.path.getsize(file_path) / 1024:.1f} KB\n"
            f"📅 [bold]Modified:[/bold] {os.path.getmtime(file_path)}",
            title="File Information",
            border_style="blue"
        )
        console.print(file_info)
        
        # Detect file type and suggest category
        file_type, suggested_category = self.detect_file_type(file_path)
        
        console.print(f"\n🔍 Detected: {file_type} - Suggested: {suggested_category}", style="cyan")
        
        # Interactive categorization
        manufacturer = self.interactive_manufacturer_selection()
        document_type = self.interactive_document_type_selection(suggested_category)
        
        if document_type == "Print Quality Image":
            # Image processing workflow
            model = self.interactive_printer_model_input(manufacturer)
            analysis_results = self.interactive_print_quality_analysis(file_path, manufacturer, model)
            
            # Store image analysis
            image_id = self.store_image_analysis_in_database(file_path, analysis_results)
            console.print(f"✅ Image analysis stored with ID: {image_id}", style="green")
            
        else:
            # Document processing workflow
            model = self.interactive_printer_model_input(manufacturer)
            language = inquirer.text(message="🌍 Sprache (EN/DE/FR/ES):", default="EN")
            year = inquirer.text(message="📅 Jahr (optional):", default="")
            
            metadata = {
                'manufacturer': manufacturer,
                'document_type': document_type,
                'product_model': model,
                'language': language,
                'year': year
            }
            
            # Process document
            success = self.process_pdf_document(file_path, metadata)
            
            if success:
                console.print("✅ Document processing completed!", style="green")
            else:
                console.print("❌ Document processing failed!", style="red")
                return False
        
        return True
    
    def run(self, file_path: Optional[str] = None):
        """Main entry point for interactive processing"""
        
        # Welcome message
        welcome_panel = Panel(
            Text.from_markup(
                "[bold blue]KRAI ENGINE - Interactive Processor[/bold blue]\n\n"
                "🏢 Multi-Manufacturer Support: HP, Canon, Epson, Brother, Xerox\n"
                "📄 Document Types: CPMD, Service Manuals, Parts Catalogs\n"
                "🖼️ Print Quality Analysis: AI Vision + Technician Feedback\n"
                "🗃️ Database Integration: Automatic structured storage\n\n"
                "[yellow]Phase 1: Interactive Terminal Processing[/yellow]\n"
                "[dim]Phase 2: Filament Dashboard Integration (coming soon)[/dim]"
            ),
            title="Welcome",
            border_style="green"
        )
        console.print(welcome_panel)
        
        # Connect to database
        if not self.connect_database():
            console.print("❌ Cannot proceed without database connection", style="red")
            return
        
        # File processing
        if file_path:
            # Single file mode
            self.process_single_file(file_path)
        else:
            # Interactive file selection mode
            while True:
                action_choices = [
                    "📄 Process Single File",
                    "📁 Process Folder (Batch)",
                    "📊 View Processing Statistics",
                    "🚪 Exit"
                ]
                
                questions = [
                    inquirer.List('action',
                        message="Was möchtest du tun?",
                        choices=action_choices,
                    ),
                ]
                action_answer = inquirer.prompt(questions)
                
                if not action_answer:  # User pressed Ctrl+C
                    break
                    
                action = action_answer['action']
                
                if action == "📄 Process Single File":
                    file_path = inquirer.text(message="📁 Dateipfad eingeben:")
                    if file_path:
                        self.process_single_file(file_path)
                
                elif action == "📁 Process Folder (Batch)":
                    folder_path = inquirer.text(message="📁 Ordner-Pfad eingeben:")
                    if folder_path and os.path.isdir(folder_path):
                        self.process_folder_batch(folder_path)
                    else:
                        console.print("❌ Invalid folder path", style="red")
                
                elif action == "📊 View Processing Statistics":
                    self.show_processing_statistics()
                
                elif action == "🚪 Exit":
                    break
        
        # Cleanup
        if self.db_connection:
            self.db_connection.close()
            console.print("\n👋 Database connection closed. Goodbye!", style="green")

    def process_folder_batch(self, folder_path: str):
        """Process all files in a folder"""
        # TODO: Implement batch processing
        console.print("🚧 Batch processing coming soon!", style="yellow")
    
    def show_processing_statistics(self):
        """Show processing statistics from database"""
        # TODO: Implement statistics display
        console.print("📊 Statistics feature coming soon!", style="yellow")


def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="KRAI Engine Interactive Processor")
    parser.add_argument("file", nargs="?", help="File or folder to process")
    parser.add_argument("--batch", action="store_true", help="Batch processing mode")
    
    args = parser.parse_args()
    
    processor = KRAIInteractiveProcessor()
    processor.run(args.file)


if __name__ == "__main__":
    main()