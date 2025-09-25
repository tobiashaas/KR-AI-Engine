# KRAI Engine - Processing Status Manager
# Real-time status tracking for document processing

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime
from enum import Enum
from dataclasses import dataclass, asdict
import json
import logging

logger = logging.getLogger(__name__)

class ProcessingStage(Enum):
    """Document processing stages"""
    UPLOAD = "upload"
    EXTRACT_CONTENT = "extract_content" 
    PROCESS_IMAGES = "process_images"
    CLASSIFY_DOCUMENT = "classify_document"
    EXTRACT_METADATA = "extract_metadata"
    STORE_DOCUMENT = "store_document"
    PROCESS_CHUNKS = "process_chunks"
    GENERATE_EMBEDDINGS = "generate_embeddings"
    FINALIZE = "finalize"

class ProcessingStatus(Enum):
    """Processing status states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class StageProgress:
    """Progress information for a processing stage"""
    stage: ProcessingStage
    status: ProcessingStatus
    start_time: Optional[datetime] = None
    end_time: Optional[datetime] = None
    progress_percent: int = 0
    current_operation: str = ""
    total_operations: int = 0
    completed_operations: int = 0
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> Optional[float]:
        """Calculate stage duration in seconds"""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        elif self.start_time:
            return (datetime.now() - self.start_time).total_seconds()
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        data['stage'] = self.stage.value
        data['status'] = self.status.value
        data['start_time'] = self.start_time.isoformat() if self.start_time else None
        data['end_time'] = self.end_time.isoformat() if self.end_time else None
        data['duration'] = self.duration
        return data

@dataclass
class DocumentProcessingStatus:
    """Complete document processing status"""
    document_id: Optional[str]
    filename: str
    file_size: int
    start_time: datetime
    end_time: Optional[datetime] = None
    overall_status: ProcessingStatus = ProcessingStatus.PENDING
    current_stage: Optional[ProcessingStage] = None
    stages: Dict[ProcessingStage, StageProgress] = None
    
    def __post_init__(self):
        if self.stages is None:
            # Initialize all stages as pending
            self.stages = {
                stage: StageProgress(stage=stage, status=ProcessingStatus.PENDING)
                for stage in ProcessingStage
            }
    
    @property
    def overall_progress_percent(self) -> int:
        """Calculate overall progress percentage"""
        completed_stages = sum(1 for stage in self.stages.values() 
                             if stage.status == ProcessingStatus.COMPLETED)
        total_stages = len(self.stages)
        return int((completed_stages / total_stages) * 100)
    
    @property
    def total_duration(self) -> Optional[float]:
        """Total processing duration in seconds"""
        if self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        else:
            return (datetime.now() - self.start_time).total_seconds()
    
    @property
    def estimated_remaining(self) -> Optional[float]:
        """Estimate remaining time based on current progress"""
        if self.overall_progress_percent == 0:
            return None
        
        elapsed = self.total_duration or 0
        if self.overall_progress_percent >= 100:
            return 0
        
        # Estimate based on linear progression
        total_estimated = elapsed / (self.overall_progress_percent / 100)
        return max(0, total_estimated - elapsed)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'document_id': self.document_id,
            'filename': self.filename,
            'file_size': self.file_size,
            'start_time': self.start_time.isoformat(),
            'end_time': self.end_time.isoformat() if self.end_time else None,
            'overall_status': self.overall_status.value,
            'current_stage': self.current_stage.value if self.current_stage else None,
            'overall_progress_percent': self.overall_progress_percent,
            'total_duration': self.total_duration,
            'estimated_remaining': self.estimated_remaining,
            'stages': {
                stage.value: stage_progress.to_dict() 
                for stage, stage_progress in self.stages.items()
            }
        }

class ProcessingStatusManager:
    """Manages processing status for all documents"""
    
    def __init__(self):
        self.active_processes: Dict[str, DocumentProcessingStatus] = {}
        self.completed_processes: List[DocumentProcessingStatus] = []
        self.max_completed_history = 50
        self._lock = asyncio.Lock()
    
    async def create_process(self, filename: str, file_size: int) -> str:
        """Create a new processing status entry"""
        async with self._lock:
            process_id = f"proc_{int(time.time() * 1000)}"
            
            status = DocumentProcessingStatus(
                document_id=None,  # Will be set later
                filename=filename,
                file_size=file_size,
                start_time=datetime.now()
            )
            
            self.active_processes[process_id] = status
            
            logger.info(f"📊 Created processing status for: {filename} (ID: {process_id})")
            return process_id
    
    async def start_stage(self, process_id: str, stage: ProcessingStage, 
                         total_operations: int = 0, current_operation: str = ""):
        """Start a processing stage"""
        async with self._lock:
            if process_id not in self.active_processes:
                logger.error(f"❌ Process ID not found: {process_id}")
                return
            
            status = self.active_processes[process_id]
            status.current_stage = stage
            status.overall_status = ProcessingStatus.RUNNING
            
            stage_progress = status.stages[stage]
            stage_progress.status = ProcessingStatus.RUNNING
            stage_progress.start_time = datetime.now()
            stage_progress.total_operations = total_operations
            stage_progress.current_operation = current_operation
            stage_progress.progress_percent = 0
            
            logger.info(f"🔄 Started stage {stage.value} for {status.filename}")
    
    async def update_stage_progress(self, process_id: str, stage: ProcessingStage,
                                  completed_operations: int = 0, 
                                  current_operation: str = ""):
        """Update progress for a specific stage"""
        async with self._lock:
            if process_id not in self.active_processes:
                return
            
            status = self.active_processes[process_id]
            stage_progress = status.stages[stage]
            
            stage_progress.completed_operations = completed_operations
            if current_operation:
                stage_progress.current_operation = current_operation
            
            if stage_progress.total_operations > 0:
                stage_progress.progress_percent = int(
                    (completed_operations / stage_progress.total_operations) * 100
                )
            
            logger.debug(f"📈 Updated {stage.value}: {stage_progress.progress_percent}% - {current_operation}")
    
    async def complete_stage(self, process_id: str, stage: ProcessingStage):
        """Mark a stage as completed"""
        async with self._lock:
            if process_id not in self.active_processes:
                return
            
            status = self.active_processes[process_id]
            stage_progress = status.stages[stage]
            
            stage_progress.status = ProcessingStatus.COMPLETED
            stage_progress.end_time = datetime.now()
            stage_progress.progress_percent = 100
            
            logger.info(f"✅ Completed stage {stage.value} for {status.filename} "
                       f"(Duration: {stage_progress.duration:.2f}s)")
    
    async def fail_stage(self, process_id: str, stage: ProcessingStage, error_message: str):
        """Mark a stage as failed"""
        async with self._lock:
            if process_id not in self.active_processes:
                return
            
            status = self.active_processes[process_id]
            stage_progress = status.stages[stage]
            
            stage_progress.status = ProcessingStatus.FAILED
            stage_progress.end_time = datetime.now()
            stage_progress.error_message = error_message
            
            # Mark overall status as failed
            status.overall_status = ProcessingStatus.FAILED
            
            logger.error(f"❌ Failed stage {stage.value} for {status.filename}: {error_message}")
    
    async def complete_process(self, process_id: str, document_id: Optional[str] = None):
        """Mark entire process as completed"""
        async with self._lock:
            if process_id not in self.active_processes:
                return
            
            status = self.active_processes[process_id]
            status.document_id = document_id
            status.overall_status = ProcessingStatus.COMPLETED
            status.end_time = datetime.now()
            status.current_stage = None
            
            # Move to completed history
            self.completed_processes.append(status)
            
            # Limit completed history
            if len(self.completed_processes) > self.max_completed_history:
                self.completed_processes = self.completed_processes[-self.max_completed_history:]
            
            # Remove from active processes
            del self.active_processes[process_id]
            
            logger.info(f"🎉 Completed processing: {status.filename} "
                       f"(Total Duration: {status.total_duration:.2f}s)")
    
    async def get_process_status(self, process_id: str) -> Optional[Dict[str, Any]]:
        """Get status for a specific process"""
        async with self._lock:
            if process_id in self.active_processes:
                return self.active_processes[process_id].to_dict()
            
            # Check completed processes
            for completed in self.completed_processes:
                if completed.document_id == process_id or f"proc_{process_id}" in str(completed.document_id):
                    return completed.to_dict()
            
            return None
    
    async def get_all_active_processes(self) -> List[Dict[str, Any]]:
        """Get all active processing statuses"""
        async with self._lock:
            return [status.to_dict() for status in self.active_processes.values()]
    
    async def get_processing_summary(self) -> Dict[str, Any]:
        """Get a summary of all processing activities"""
        async with self._lock:
            active_count = len(self.active_processes)
            completed_count = len(self.completed_processes)
            
            # Calculate average processing time from completed
            avg_duration = 0
            if self.completed_processes:
                total_duration = sum(proc.total_duration or 0 for proc in self.completed_processes)
                avg_duration = total_duration / len(self.completed_processes)
            
            return {
                'active_processes': active_count,
                'completed_processes': completed_count,
                'average_processing_time': avg_duration,
                'active_details': [
                    {
                        'filename': status.filename,
                        'current_stage': status.current_stage.value if status.current_stage else None,
                        'progress_percent': status.overall_progress_percent,
                        'duration': status.total_duration
                    }
                    for status in self.active_processes.values()
                ]
            }

# Global status manager instance
status_manager = ProcessingStatusManager()

# Helper functions for easy access
async def create_processing_status(filename: str, file_size: int) -> str:
    """Create a new processing status"""
    return await status_manager.create_process(filename, file_size)

async def update_processing_status(process_id: str, stage: ProcessingStage, 
                                 operation: str = "", completed: int = 0, total: int = 0):
    """Quick update for processing status"""
    if total > 0:
        await status_manager.start_stage(process_id, stage, total, operation)
        await status_manager.update_stage_progress(process_id, stage, completed, operation)
    else:
        await status_manager.start_stage(process_id, stage, current_operation=operation)
