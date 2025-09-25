"""
Production Configuration for KRAI Engine
Optimized for Apple M1 Pro with MPS and NVIDIA CUDA support
"""

import os
import torch
from pathlib import Path
from typing import Dict, Any, Optional
import platform

class ProductionConfig:
    """Production configuration with GPU optimization"""
    
    def __init__(self):
        self.system_info = self._get_system_info()
        self.device_config = self._configure_device()
        self.model_config = self._configure_models()
        self.performance_config = self._configure_performance()
        
    def _get_system_info(self) -> Dict[str, Any]:
        """Get system information"""
        return {
            "platform": platform.system(),
            "architecture": platform.machine(),
            "processor": platform.processor(),
            "python_version": platform.python_version(),
            "pytorch_version": torch.__version__,
            "mps_available": torch.backends.mps.is_available(),
            "mps_built": torch.backends.mps.is_built(),
            "cuda_available": torch.cuda.is_available(),
            "cuda_version": torch.version.cuda if torch.cuda.is_available() else None,
        }
    
    def _configure_device(self) -> Dict[str, Any]:
        """Configure optimal device for current system"""
        if torch.cuda.is_available():
            device = "cuda"
            device_name = f"CUDA {torch.version.cuda}"
            memory_gb = torch.cuda.get_device_properties(0).total_memory / 1e9
        elif torch.backends.mps.is_available():
            device = "mps"
            device_name = "Apple Metal Performance Shaders"
            # M1 Pro has 16-core GPU with unified memory
            memory_gb = 16  # Approximate for M1 Pro
        else:
            device = "cpu"
            device_name = "CPU"
            memory_gb = 8  # Conservative estimate
        
        return {
            "device": device,
            "device_name": device_name,
            "memory_gb": memory_gb,
            "batch_size": self._calculate_optimal_batch_size(memory_gb),
            "num_workers": self._calculate_optimal_workers(device, memory_gb)
        }
    
    def _calculate_optimal_batch_size(self, memory_gb: float) -> int:
        """Calculate optimal batch size based on available memory"""
        if memory_gb >= 16:  # M1 Pro or high-end GPU
            return 32
        elif memory_gb >= 8:  # Mid-range GPU
            return 16
        else:  # CPU or low memory
            return 8
    
    def _calculate_optimal_workers(self, device: str, memory_gb: float) -> int:
        """Calculate optimal number of workers"""
        cpu_count = os.cpu_count() or 4
        
        if device == "cuda":
            return min(cpu_count, 8)  # GPU can handle more parallelism
        elif device == "mps":
            return min(cpu_count, 6)  # MPS can handle more workers
        else:
            return min(cpu_count, 2)  # Conservative for CPU
    
    def _configure_models(self) -> Dict[str, Any]:
        """Configure model settings for production"""
        return {
            "llm": {
                "model_name": "llama3.2:3b",
                "temperature": 0.7,
                "max_tokens": 2048,
                "top_p": 0.9,
                "repeat_penalty": 1.1,
                "context_length": 8192
            },
            "embedding": {
                "model_name": "embeddinggemma",
                "dimension": 768,
                "batch_size": self.device_config["batch_size"],
                "normalize": True
            },
            "vision": {
                "model_name": "llava:7b",
                "image_size": 512,
                "batch_size": min(self.device_config["batch_size"], 4),
                "max_new_tokens": 1024
            },
            "chunking": {
                "default_chunk_size": 512,
                "chunk_overlap": 50,
                "context_chunk_size": 1024,
                "context_overlap": 100
            }
        }
    
    def _configure_performance(self) -> Dict[str, Any]:
        """Configure performance optimizations"""
        return {
            "async_processing": True,
            "concurrent_documents": 3,
            "concurrent_chunks": 10,
            "embedding_cache_size": 10000,
            "vector_cache_size": 1000,
            "image_cache_size": 500,
            "enable_quantization": True,
            "enable_compression": True,
            "enable_caching": True,
            "memory_optimization": True,
            "gpu_memory_fraction": 0.8 if self.device_config["device"] == "cuda" else 1.0
        }
    
    def get_ollama_config(self) -> Dict[str, Any]:
        """Get Ollama-specific configuration"""
        return {
            "base_url": "http://localhost:11434",
            "timeout": 300,
            "retry_attempts": 3,
            "retry_delay": 1,
            "models": {
                "llm": self.model_config["llm"]["model_name"],
                "embedding": self.model_config["embedding"]["model_name"],
                "vision": self.model_config["vision"]["model_name"]
            }
        }
    
    def get_embedding_config(self) -> Dict[str, Any]:
        """Get embedding configuration"""
        return {
            "model_name": self.model_config["embedding"]["model_name"],
            "dimension": self.model_config["embedding"]["dimension"],
            "device": self.device_config["device"],
            "batch_size": self.model_config["embedding"]["batch_size"],
            "normalize": self.model_config["embedding"]["normalize"]
        }
    
    def get_vision_config(self) -> Dict[str, Any]:
        """Get vision model configuration"""
        return {
            "model_name": self.model_config["vision"]["model_name"],
            "device": self.device_config["device"],
            "batch_size": self.model_config["vision"]["batch_size"],
            "image_size": self.model_config["vision"]["image_size"],
            "max_new_tokens": self.model_config["vision"]["max_new_tokens"]
        }
    
    def print_config_summary(self):
        """Print configuration summary"""
        print("🚀 KRAI Engine Production Configuration")
        print("=" * 50)
        print(f"System: {self.system_info['platform']} {self.system_info['architecture']}")
        print(f"Device: {self.device_config['device_name']}")
        print(f"Memory: {self.device_config['memory_gb']:.1f} GB")
        print(f"Batch Size: {self.device_config['batch_size']}")
        print(f"Workers: {self.device_config['num_workers']}")
        print("\n📦 Models:")
        print(f"  LLM: {self.model_config['llm']['model_name']}")
        print(f"  Embedding: {self.model_config['embedding']['model_name']}")
        print(f"  Vision: {self.model_config['vision']['model_name']}")
        print("\n⚡ Performance:")
        print(f"  Async Processing: {self.performance_config['async_processing']}")
        print(f"  Concurrent Documents: {self.performance_config['concurrent_documents']}")
        print(f"  Memory Optimization: {self.performance_config['memory_optimization']}")
        print("=" * 50)

# Global configuration instance
config = ProductionConfig()
