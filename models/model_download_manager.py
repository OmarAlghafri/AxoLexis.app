"""
Model Availability & Auto-Download System for AxoLexis
Handles automatic model downloads from multiple sources (Hugging Face, Torch Hub, etc.)
"""

import os
import json
import requests
import torch
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QThread
from PyQt6.QtWidgets import QMessageBox, QProgressDialog
import hashlib
import urllib.request
from tqdm import tqdm

logger = logging.getLogger(__name__)

class ModelDownloadManager(QObject):
    """Manages model downloads from multiple sources"""
    
    download_progress = pyqtSignal(int, int)  # current, total
    download_completed = pyqtSignal(str, bool)  # model_name, success
    download_error = pyqtSignal(str, str)  # model_name, error
    
    def __init__(self, cache_dir: str = "./models_cache"):
        super().__init__()
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        
        # Model sources configuration
        self.model_sources = {
            "huggingface": {
                "base_url": "https://huggingface.co",
                "api_url": "https://huggingface.co/api/models",
                "models": {
                    "bert-base-uncased": "bert-base-uncased",
                    "roberta-base": "roberta-base",
                    "distilbert-base-uncased": "distilbert-base-uncased",
                    "gpt2": "gpt2",
                    "t5-small": "t5-small",
                    "llama-2-7b": "meta-llama/Llama-2-7b-hf",
                    "mistral-7b": "mistralai/Mistral-7B-v0.1",
                    "falcon-7b": "tiiuae/falcon-7b",
                    "clip-vit-base": "openai/clip-vit-base-patch32",
                    "whisper-base": "openai/whisper-base"
                }
            },
            "torch_hub": {
                "base_url": "https://download.pytorch.org/models",
                "models": {
                    "resnet18": "resnet18-f37072fd.pth",
                    "resnet50": "resnet50-0676ba61.pth",
                    "vgg16": "vgg16-397923af.pth",
                    "efficientnet_b0": "efficientnet_b0_rwightman-3dd342df.pth",
                    "mobilenet_v2": "mobilenet_v2-b0353104.pth"
                }
            },
            "onnx_model_zoo": {
                "base_url": "https://github.com/onnx/models/raw/main",
                "models": {
                    "yolov5s": "vision/object_detection_segmentation/yolov5/model/yolov5s.onnx",
                    "efficientnet_lite0": "vision/classification/efficientnet-lite4/model/efficientnet-lite4-11.onnx"
                }
            }
        }
        
        # Model size estimates (in MB)
        self.model_sizes = {
            "bert-base-uncased": 440,
            "roberta-base": 502,
            "distilbert-base-uncased": 268,
            "gpt2": 548,
            "t5-small": 242,
            "llama-2-7b": 13000,
            "mistral-7b": 13000,
            "falcon-7b": 13000,
            "clip-vit-base": 605,
            "whisper-base": 151,
            "resnet18": 44,
            "resnet50": 98,
            "vgg16": 528,
            "efficientnet_b0": 20,
            "mobilenet_v2": 14
        }

    def check_model_availability(self, model_name: str) -> Tuple[bool, str, Optional[str]]:
        """
        Check if model is available and return download info
        Returns: (is_available, source, model_path)
        """
        # Check if already cached
        cached_path = self._get_cached_model_path(model_name)
        if cached_path and cached_path.exists():
            return True, "cached", str(cached_path)
        
        # Check available sources
        for source, config in self.model_sources.items():
            if model_name in config["models"]:
                return False, source, config["models"][model_name]
        
        return False, "not_found", None

    def download_model(self, model_name: str, source: str, model_path: str, 
                      parent=None) -> bool:
        """Download model from specified source"""
        try:
            if source == "huggingface":
                return self._download_huggingface_model(model_name, model_path, parent)
            elif source == "torch_hub":
                return self._download_torch_hub_model(model_name, model_path, parent)
            elif source == "onnx_model_zoo":
                return self._download_onnx_model(model_name, model_path, parent)
            else:
                logger.error(f"Unknown source: {source}")
                return False
        except Exception as e:
            logger.error(f"Download failed for {model_name}: {e}")
            self.download_error.emit(model_name, str(e))
            return False

    def _download_huggingface_model(self, model_name: str, model_id: str, parent=None) -> bool:
        """Download model from Hugging Face"""
        try:
            from transformers import AutoModel, AutoTokenizer
            
            # Show progress dialog
            progress = QProgressDialog(f"Downloading {model_name} from Hugging Face...", 
                                     "Cancel", 0, 100, parent)
            progress.setWindowTitle("Model Download")
            progress.setModal(True)
            progress.show()
            
            # Get model size estimate
            estimated_size = self.model_sizes.get(model_name, 500)  # Default 500MB
            
            def progress_callback(current, total):
                progress_value = int((current / total) * 100) if total > 0 else 0
                progress.setValue(progress_value)
                self.download_progress.emit(current, total)
                return not progress.wasCanceled()
            
            # Download model and tokenizer
            logger.info(f"Downloading {model_name} from Hugging Face...")
            
            model = AutoModel.from_pretrained(model_id)
            tokenizer = AutoTokenizer.from_pretrained(model_id)
            
            # Save to cache
            cache_path = self.cache_dir / "huggingface" / model_name
            cache_path.mkdir(parents=True, exist_ok=True)
            
            model.save_pretrained(cache_path)
            tokenizer.save_pretrained(cache_path)
            
            progress.setValue(100)
            logger.info(f"Successfully downloaded {model_name}")
            
            self.download_completed.emit(model_name, True)
            return True
            
        except Exception as e:
            logger.error(f"Hugging Face download failed: {e}")
            self.download_error.emit(model_name, str(e))
            return False

    def _download_torch_hub_model(self, model_name: str, model_file: str, parent=None) -> bool:
        """Download model from Torch Hub"""
        try:
            # Show progress dialog
            progress = QProgressDialog(f"Downloading {model_name} from Torch Hub...", 
                                     "Cancel", 0, 100, parent)
            progress.setWindowTitle("Model Download")
            progress.setModal(True)
            progress.show()
            
            # Download using torch.hub
            logger.info(f"Downloading {model_name} from Torch Hub...")
            
            model = torch.hub.load('pytorch/vision:v0.10.0', model_name, pretrained=True)
            
            # Save to cache
            cache_path = self.cache_dir / "torch_hub" / f"{model_name}.pth"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            torch.save(model.state_dict(), cache_path)
            
            progress.setValue(100)
            logger.info(f"Successfully downloaded {model_name}")
            
            self.download_completed.emit(model_name, True)
            return True
            
        except Exception as e:
            logger.error(f"Torch Hub download failed: {e}")
            self.download_error.emit(model_name, str(e))
            return False

    def _download_onnx_model(self, model_name: str, model_path: str, parent=None) -> bool:
        """Download ONNX model from ONNX Model Zoo"""
        try:
            # Construct full URL
            base_url = self.model_sources["onnx_model_zoo"]["base_url"]
            full_url = f"{base_url}/{model_path}"
            
            # Show progress dialog
            progress = QProgressDialog(f"Downloading {model_name} from ONNX Model Zoo...", 
                                     "Cancel", 0, 100, parent)
            progress.setWindowTitle("Model Download")
            progress.setModal(True)
            progress.show()
            
            # Download file
            cache_path = self.cache_dir / "onnx" / f"{model_name}.onnx"
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            
            def download_with_progress(url: str, filepath: Path):
                """Download file with progress reporting"""
                response = requests.get(url, stream=True)
                response.raise_for_status()
                
                total_size = int(response.headers.get('content-length', 0))
                downloaded = 0
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        if chunk:
                            f.write(chunk)
                            downloaded += len(chunk)
                            if total_size > 0:
                                progress_value = int((downloaded / total_size) * 100)
                                progress.setValue(progress_value)
                                self.download_progress.emit(downloaded, total_size)
                                
                                if progress.wasCanceled():
                                    raise InterruptedError("Download cancelled by user")
            
            download_with_progress(full_url, cache_path)
            
            progress.setValue(100)
            logger.info(f"Successfully downloaded {model_name}")
            
            self.download_completed.emit(model_name, True)
            return True
            
        except Exception as e:
            logger.error(f"ONNX Model Zoo download failed: {e}")
            self.download_error.emit(model_name, str(e))
            return False

    def _get_cached_model_path(self, model_name: str) -> Optional[Path]:
        """Get path to cached model if it exists"""
        # Check Hugging Face cache
        hf_path = self.cache_dir / "huggingface" / model_name
        if hf_path.exists():
            return hf_path
        
        # Check Torch Hub cache
        th_path = self.cache_dir / "torch_hub" / f"{model_name}.pth"
        if th_path.exists():
            return th_path
        
        # Check ONNX cache
        onnx_path = self.cache_dir / "onnx" / f"{model_name}.onnx"
        if onnx_path.exists():
            return onnx_path
        
        return None

    def get_available_models(self) -> Dict[str, List[str]]:
        """Get list of available models grouped by source"""
        available = {
            "cached": [],
            "huggingface": [],
            "torch_hub": [],
            "onnx_model_zoo": []
        }
        
        # Check cached models
        for source_dir in ["huggingface", "torch_hub", "onnx"]:
            source_path = self.cache_dir / source_dir
            if source_path.exists():
                if source_dir == "huggingface":
                    for model_dir in source_path.iterdir():
                        if model_dir.is_dir():
                            available["cached"].append(model_dir.name)
                else:
                    for model_file in source_path.iterdir():
                        if model_file.is_file():
                            model_name = model_file.stem
                            available["cached"].append(model_name)
        
        # Add downloadable models
        for source, config in self.model_sources.items():
            available[source].extend(list(config["models"].keys()))
        
        return available

    def get_model_info(self, model_name: str) -> Dict[str, any]:
        """Get information about a model"""
        is_available, source, path = self.check_model_availability(model_name)
        
        info = {
            "name": model_name,
            "available": is_available,
            "source": source,
            "path": path,
            "size_mb": self.model_sizes.get(model_name, "Unknown"),
            "download_required": not is_available
        }
        
        return info

    def cleanup_cache(self, max_size_gb: float = 10.0):
        """Clean up old models to stay within cache size limit"""
        try:
            total_size = 0
            model_files = []
            
            # Calculate total cache size
            for source_dir in ["huggingface", "torch_hub", "onnx"]:
                source_path = self.cache_dir / source_dir
                if source_path.exists():
                    for item in source_path.rglob("*"):
                        if item.is_file():
                            size = item.stat().st_size
                            total_size += size
                            model_files.append((item, item.stat().st_mtime, size))
            
            total_size_gb = total_size / (1024**3)
            
            if total_size_gb > max_size_gb:
                logger.info(f"Cache size {total_size_gb:.1f}GB exceeds limit {max_size_gb}GB, cleaning up...")
                
                # Sort by last modified time (oldest first)
                model_files.sort(key=lambda x: x[1])
                
                # Remove oldest models until under limit
                removed_size = 0
                target_size = max_size_gb * 1024**3
                
                for file_path, mtime, size in model_files:
                    if total_size - removed_size <= target_size:
                        break
                    
                    try:
                        file_path.unlink()
                        removed_size += size
                        logger.info(f"Removed cached model: {file_path}")
                    except Exception as e:
                        logger.warning(f"Failed to remove {file_path}: {e}")
                
                logger.info(f"Cleaned up {removed_size / (1024**3):.1f}GB of cached models")
                
        except Exception as e:
            logger.error(f"Cache cleanup failed: {e}")

class ModelAvailabilityChecker:
    """Checks model availability and manages downloads"""
    
    def __init__(self, download_manager: ModelDownloadManager):
        self.download_manager = download_manager

    def check_and_prompt_download(self, model_name: str, parent=None) -> bool:
        """
        Check if model is available and prompt user to download if needed
        Returns: True if model is available (cached or downloaded), False otherwise
        """
        info = self.download_manager.get_model_info(model_name)
        
        if info["available"]:
            return True
        
        # Model needs to be downloaded
        if info["download_required"]:
            reply = QMessageBox.question(
                parent,
                "Model Download Required",
                f"Model '{model_name}' is not available locally.\n\n"
                f"Source: {info['source']}\n"
                f"Estimated size: {info['size_mb']} MB\n\n"
                "Would you like to download it now?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
                QMessageBox.StandardButton.Yes
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                return self.download_manager.download_model(
                    model_name, info["source"], info["path"], parent
                )
            else:
                return False
        
        return False

    def get_recommended_models(self, task_domain: str, task_type: str) -> List[str]:
        """Get recommended models for specific task"""
        # Task-specific model recommendations
        recommendations = {
            ("Computer Vision", "Image Classification"): [
                "resnet18", "resnet50", "efficientnet_b0", "mobilenet_v2"
            ],
            ("Computer Vision", "Object Detection"): [
                "yolov5s", "faster-rcnn", "retinanet"
            ],
            ("Natural Language Processing (NLP)", "Text Classification"): [
                "bert-base-uncased", "roberta-base", "distilbert-base-uncased"
            ],
            ("Natural Language Processing (NLP)", "Text Generation"): [
                "gpt2", "t5-small", "llama-2-7b", "mistral-7b"
            ],
            ("Speech & Audio", "Speech Recognition"): [
                "whisper-base"
            ],
            ("Multimodal AI", "Vision + Language"): [
                "clip-vit-base"
            ]
        }
        
        key = (task_domain, task_type)
        if key in recommendations:
            return recommendations[key]
        
        # Default recommendations
        return ["resnet18", "bert-base-uncased"]

    def check_multiple_models(self, model_names: List[str]) -> Dict[str, bool]:
        """Check availability of multiple models"""
        results = {}
        for model_name in model_names:
            info = self.download_manager.get_model_info(model_name)
            results[model_name] = info["available"]
        return results

# Integration function
def create_model_download_manager(cache_dir: str = "./models_cache") -> ModelDownloadManager:
    """Create and return model download manager"""
    return ModelDownloadManager(cache_dir)

def create_model_availability_checker(download_manager: ModelDownloadManager) -> ModelAvailabilityChecker:
    """Create and return model availability checker"""
    return ModelAvailabilityChecker(download_manager)

if __name__ == "__main__":
    # Test the model download system
    print("🚀 Testing Model Download System")
    
    # Create manager
    manager = create_model_download_manager()
    checker = create_model_availability_checker(manager)
    
    # Test model availability
    test_models = ["bert-base-uncased", "resnet18", "gpt2"]
    
    for model in test_models:
        info = manager.get_model_info(model)
        print(f"\n📊 Model: {model}")
        print(f"   Available: {info['available']}")
        print(f"   Source: {info['source']}")
        print(f"   Size: {info['size_mb']} MB")
        print(f"   Download required: {info['download_required']}")
    
    # Get available models
    available = manager.get_available_models()
    print(f"\n📦 Available models by source:")
    for source, models in available.items():
        print(f"   {source}: {len(models)} models")
    
    print("\n✅ Model download system test completed!")