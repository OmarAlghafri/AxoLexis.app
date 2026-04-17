"""
Runtime Validation System for AxoLexis
Validates task, model, and dataset compatibility before training starts
"""

import os
import torch
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QMessageBox
import logging

logger = logging.getLogger(__name__)

class RuntimeValidator(QObject):
    """Comprehensive runtime validation system"""
    
    validation_started = pyqtSignal()
    validation_completed = pyqtSignal(bool, str)  # success, message
    validation_warning = pyqtSignal(str, str)  # warning_type, message
    
    def __init__(self):
        super().__init__()
        self.validation_results = []
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []

    def validate_training_setup(self, config: Dict[str, Any], 
                              dataset_info: Dict[str, Any], 
                              hardware_info: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Comprehensive validation of training setup
        Returns: (is_valid, validation_report)
        """
        self.validation_started.emit()
        self.validation_results = []
        self.critical_issues = []
        self.warnings = []
        self.recommendations = []
        
        try:
            logger.info("Starting comprehensive runtime validation...")
            
            # 1. Task Definition Validation
            self._validate_task_definition(config)
            
            # 2. Model Configuration Validation
            self._validate_model_configuration(config, hardware_info)
            
            # 3. Dataset Compatibility Validation
            self._validate_dataset_compatibility(config, dataset_info)
            
            # 4. Hardware Resource Validation
            self._validate_hardware_resources(config, hardware_info)
            
            # 5. Training Configuration Validation
            self._validate_training_configuration(config)
            
            # 6. Intelligent Features Validation
            self._validate_intelligent_features(config)
            
            # Generate final report
            is_valid = len(self.critical_issues) == 0
            report = self._generate_validation_report()
            
            self.validation_completed.emit(is_valid, report)
            
            logger.info(f"Runtime validation completed. Status: {'PASSED' if is_valid else 'FAILED'}")
            
            return is_valid, report
            
        except Exception as e:
            error_msg = f"Validation system error: {str(e)}"
            logger.error(error_msg)
            self.validation_completed.emit(False, error_msg)
            return False, error_msg

    def _validate_task_definition(self, config: Dict[str, Any]):
        """Validate task domain and type definition"""
        task_domain = config.get("task_domain", "")
        task_type = config.get("task_type", "")
        
        # Check if task domain is specified
        if not task_domain:
            self.critical_issues.append({
                "type": "task_definition",
                "severity": "CRITICAL",
                "message": "Task domain is not specified",
                "recommendation": "Select a task domain from the available options"
            })
            return
        
        # Check if task type is specified
        if not task_type:
            self.critical_issues.append({
                "type": "task_definition",
                "severity": "CRITICAL", 
                "message": "Task type is not specified",
                "recommendation": "Select a task type for the chosen domain"
            })
            return
        
        # Validate task domain/type compatibility
        valid_domains = [
            "Computer Vision", "Natural Language Processing (NLP)", 
            "Speech & Audio", "Time Series & Forecasting",
            "Reinforcement Learning", "Graph AI", "Multimodal AI"
        ]
        
        if task_domain not in valid_domains:
            self.critical_issues.append({
                "type": "task_definition",
                "severity": "CRITICAL",
                "message": f"Invalid task domain: {task_domain}",
                "recommendation": f"Choose from: {', '.join(valid_domains)}"
            })
        
        # Log successful validation
        self.validation_results.append({
            "type": "task_definition",
            "status": "PASSED",
            "message": f"Task definition validated: {task_domain} - {task_type}"
        })

    def _validate_model_configuration(self, config: Dict[str, Any], hardware_info: Dict[str, Any]):
        """Validate model configuration and compatibility"""
        model_name = config.get("pretrained_model", "")
        model_tier = config.get("model_tier", "base")
        
        # Check if model is specified
        if not model_name or model_name == "None (Train from scratch)":
            self.warnings.append({
                "type": "model_configuration",
                "severity": "WARNING",
                "message": "Training from scratch without pretrained model",
                "recommendation": "Consider using a pretrained model for better performance"
            })
            return
        
        # Validate model tier
        valid_tiers = ["nano", "base", "large", "xl"]
        if model_tier not in valid_tiers:
            self.critical_issues.append({
                "type": "model_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid model tier: {model_tier}",
                "recommendation": f"Choose from: {', '.join(valid_tiers)}"
            })
        
        # Check model size vs hardware
        vram_gb = hardware_info.get("vram_gb", 0)
        model_size_mb = self._estimate_model_size(model_name, model_tier)
        
        if vram_gb > 0 and model_size_mb > vram_gb * 1024:  # Convert GB to MB
            self.critical_issues.append({
                "type": "model_configuration",
                "severity": "CRITICAL",
                "message": f"Model too large for available VRAM: {model_size_mb}MB > {vram_gb*1024}MB",
                "recommendation": "Choose a smaller model tier or upgrade hardware"
            })
        
        # Validate model compatibility with task
        task_domain = config.get("task_domain", "")
        task_type = config.get("task_type", "")
        
        if not self._is_model_compatible_with_task(model_name, task_domain, task_type):
            self.warnings.append({
                "type": "model_configuration",
                "severity": "WARNING",
                "message": f"Model {model_name} may not be optimal for {task_domain} - {task_type}",
                "recommendation": "Consider using a model specifically designed for your task"
            })
        
        # Log successful validation
        self.validation_results.append({
            "type": "model_configuration",
            "status": "PASSED",
            "message": f"Model configuration validated: {model_name} ({model_tier})"
        })

    def _validate_dataset_compatibility(self, config: Dict[str, Any], dataset_info: Dict[str, Any]):
        """Validate dataset compatibility with task and model"""
        task_domain = config.get("task_domain", "")
        data_type = dataset_info.get("data_type", "unknown")
        num_samples = dataset_info.get("num_samples", 0)
        num_classes = dataset_info.get("num_classes", 0)
        
        # Check dataset size
        if num_samples < 100:
            self.critical_issues.append({
                "type": "dataset_compatibility",
                "severity": "CRITICAL",
                "message": f"Dataset too small: {num_samples} samples",
                "recommendation": "Minimum 100 samples required for meaningful training"
            })
        elif num_samples < 1000:
            self.warnings.append({
                "type": "dataset_compatibility",
                "severity": "WARNING",
                "message": f"Small dataset: {num_samples} samples",
                "recommendation": "Consider data augmentation or transfer learning"
            })
        
        # Check data type compatibility with task
        compatibility_matrix = {
            "Computer Vision": ["image", "medical", "synthetic"],
            "Natural Language Processing (NLP)": ["text", "csv", "json"],
            "Speech & Audio": ["audio", "speech"],
            "Time Series & Forecasting": ["csv", "json", "tabular"],
            "Graph AI": ["json", "graph"],
            "Multimodal AI": ["image", "text", "audio"]
        }
        
        if task_domain in compatibility_matrix:
            valid_types = compatibility_matrix[task_domain]
            if data_type not in valid_types and data_type != "synthetic":
                self.critical_issues.append({
                    "type": "dataset_compatibility",
                    "severity": "CRITICAL",
                    "message": f"Data type {data_type} incompatible with {task_domain}",
                    "recommendation": f"Expected data types: {', '.join(valid_types)}"
                })
        
        # Check class balance for classification tasks
        if dataset_info.get("is_imbalanced", False):
            self.warnings.append({
                "type": "dataset_compatibility",
                "severity": "WARNING",
                "message": "Dataset has class imbalance",
                "recommendation": "Consider using class weights or resampling techniques"
            })
        
        # Check for noisy labels
        if dataset_info.get("has_noisy_labels", False):
            self.warnings.append({
                "type": "dataset_compatibility",
                "severity": "WARNING",
                "message": "Dataset may contain noisy labels",
                "recommendation": "Consider label smoothing or robust loss functions"
            })
        
        # Log successful validation
        self.validation_results.append({
            "type": "dataset_compatibility",
            "status": "PASSED",
            "message": f"Dataset compatibility validated: {num_samples} samples, {num_classes} classes"
        })

    def _validate_hardware_resources(self, config: Dict[str, Any], hardware_info: Dict[str, Any]):
        """Validate hardware resources against requirements"""
        device = hardware_info.get("device", "cpu")
        vram_gb = hardware_info.get("vram_gb", 0)
        cpu_count = hardware_info.get("cpu_count", 1)
        
        # Check device availability
        if device == "cpu":
            self.warnings.append({
                "type": "hardware_resources",
                "severity": "WARNING",
                "message": "Training on CPU may be slow",
                "recommendation": "Consider using GPU for faster training"
            })
        
        # Check VRAM for large models
        model_tier = config.get("model_tier", "base")
        batch_size = config.get("batch_size", 16)
        
        estimated_vram = self._estimate_vram_usage(model_tier, batch_size)
        
        if vram_gb > 0 and estimated_vram > vram_gb:
            self.critical_issues.append({
                "type": "hardware_resources",
                "severity": "CRITICAL",
                "message": f"Insufficient VRAM: need {estimated_vram}GB, have {vram_gb}GB",
                "recommendation": "Reduce batch size or model tier"
            })
        
        # Check CPU cores for data loading
        if cpu_count < 4:
            self.warnings.append({
                "type": "hardware_resources",
                "severity": "WARNING",
                "message": f"Limited CPU cores: {cpu_count}",
                "recommendation": "Consider reducing data loading workers"
            })
        
        # Log successful validation
        self.validation_results.append({
            "type": "hardware_resources",
            "status": "PASSED",
            "message": f"Hardware resources validated: {device} with {vram_gb}GB VRAM"
        })

    def _validate_training_configuration(self, config: Dict[str, Any]):
        """Validate training hyperparameters and configuration"""
        # Learning rate validation
        lr = config.get("base_lr", 1e-4)
        if lr <= 0 or lr > 1.0:
            self.critical_issues.append({
                "type": "training_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid learning rate: {lr}",
                "recommendation": "Learning rate should be between 0 and 1.0"
            })
        
        # Batch size validation
        batch_size = config.get("batch_size", 16)
        if batch_size < 1 or batch_size > 4096:
            self.critical_issues.append({
                "type": "training_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid batch size: {batch_size}",
                "recommendation": "Batch size should be between 1 and 4096"
            })
        
        # Epochs validation
        epochs = config.get("num_epochs", 10)
        if epochs < 1 or epochs > 1000:
            self.critical_issues.append({
                "type": "training_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid number of epochs: {epochs}",
                "recommendation": "Epochs should be between 1 and 1000"
            })
        
        # Optimizer validation
        optimizer = config.get("optimizer", "adamw")
        valid_optimizers = ["adamw", "adam", "sgd", "rmsprop", "lion"]
        if optimizer not in valid_optimizers:
            self.critical_issues.append({
                "type": "training_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid optimizer: {optimizer}",
                "recommendation": f"Choose from: {', '.join(valid_optimizers)}"
            })
        
        # Mixed precision validation
        mixed_precision = config.get("mixed_precision", "fp32")
        valid_precisions = ["fp32", "fp16", "bf16"]
        if mixed_precision not in valid_precisions:
            self.critical_issues.append({
                "type": "training_configuration",
                "severity": "CRITICAL",
                "message": f"Invalid mixed precision: {mixed_precision}",
                "recommendation": f"Choose from: {', '.join(valid_precisions)}"
            })
        
        # LoRA validation
        if config.get("use_lora", False):
            lora_rank = config.get("lora_rank", 16)
            if lora_rank < 1 or lora_rank > 512:
                self.critical_issues.append({
                    "type": "training_configuration",
                    "severity": "CRITICAL",
                    "message": f"Invalid LoRA rank: {lora_rank}",
                    "recommendation": "LoRA rank should be between 1 and 512"
                })
        
        # Log successful validation
        self.validation_results.append({
            "type": "training_configuration",
            "status": "PASSED",
            "message": f"Training configuration validated: LR={lr}, Batch={batch_size}, Epochs={epochs}"
        })

    def _validate_intelligent_features(self, config: Dict[str, Any]):
        """Validate intelligent training features configuration"""
        # Check AutoML features
        if config.get("use_automl", False):
            self.validation_results.append({
                "type": "intelligent_features",
                "status": "INFO",
                "message": "AutoML features enabled"
            })
        
        # Check quality checking
        if config.get("use_quality_check", False):
            self.validation_results.append({
                "type": "intelligent_features",
                "status": "INFO",
                "message": "Data quality checking enabled"
            })
        
        # Check intelligent model selection
        if config.get("use_intelligent_selection", False):
            self.validation_results.append({
                "type": "intelligent_features",
                "status": "INFO",
                "message": "Intelligent model selection enabled"
            })
        
        # Check adaptive learning
        if config.get("use_adaptive_learning", False):
            self.validation_results.append({
                "type": "intelligent_features",
                "status": "INFO",
                "message": "Adaptive learning enabled"
            })
        
        # Check hyperparameter optimization
        if config.get("use_hyperopt", False):
            self.validation_results.append({
                "type": "intelligent_features",
                "status": "INFO",
                "message": "Hyperparameter optimization enabled"
            })

    def _estimate_model_size(self, model_name: str, model_tier: str) -> int:
        """Estimate model size in MB"""
        # Rough estimates based on model tier
        tier_sizes = {
            "nano": 50,      # ~50MB
            "base": 500,     # ~500MB  
            "large": 2000,   # ~2GB
            "xl": 8000       # ~8GB
        }
        
        return tier_sizes.get(model_tier, 500)

    def _estimate_vram_usage(self, model_tier: str, batch_size: int) -> float:
        """Estimate VRAM usage in GB"""
        # Rough estimates based on model tier and batch size
        base_usage = {
            "nano": 1.0,
            "base": 3.0,
            "large": 8.0,
            "xl": 16.0
        }
        
        base = base_usage.get(model_tier, 3.0)
        batch_factor = batch_size / 16  # Normalize to batch size 16
        
        return base * batch_factor

    def _is_model_compatible_with_task(self, model_name: str, task_domain: str, task_type: str) -> bool:
        """Check if model is compatible with task"""
        # Domain-specific model compatibility
        compatibility = {
            "Computer Vision": ["resnet", "vgg", "efficientnet", "mobilenet", "vit", "swin", "yolo", "detr"],
            "Natural Language Processing (NLP)": ["bert", "gpt", "t5", "roberta", "llama", "mistral", "falcon"],
            "Speech & Audio": ["whisper", "wav2vec", "speech"],
            "Multimodal AI": ["clip", "blip", "llava"]
        }
        
        if task_domain in compatibility:
            valid_models = compatibility[task_domain]
            return any(model_keyword in model_name.lower() for model_keyword in valid_models)
        
        return True  # Default to compatible if domain not found

    def _generate_validation_report(self) -> str:
        """Generate comprehensive validation report"""
        report = []
        report.append("=" * 60)
        report.append("AXOLEXIS RUNTIME VALIDATION REPORT")
        report.append("=" * 60)
        report.append(f"Validation Time: {pd.Timestamp.now()}")
        report.append("")
        
        # Critical Issues
        if self.critical_issues:
            report.append("CRITICAL ISSUES (Must Fix):")
            for issue in self.critical_issues:
                report.append(f"   • [{issue['type']}] {issue['message']}")
                report.append(f"     → {issue['recommendation']}")
            report.append("")
        
        # Warnings
        if self.warnings:
            report.append("WARNINGS (Recommended to Address):")
            for warning in self.warnings:
                report.append(f"   • [{warning['type']}] {warning['message']}")
                report.append(f"     → {warning['recommendation']}")
            report.append("")
        
        # Passed Validations
        if self.validation_results:
            report.append("PASSED VALIDATIONS:")
            for result in self.validation_results:
                report.append(f"   • [{result['type']}] {result['message']}")
            report.append("")
        
        # Final Status
        is_valid = len(self.critical_issues) == 0
        report.append("=" * 60)
        report.append(f"OVERALL STATUS: {'PASSED' if is_valid else 'FAILED'}")
        report.append("=" * 60)
        
        return "\n".join(report)

# Integration function
def create_runtime_validator() -> RuntimeValidator:
    """Create and return runtime validator"""
    return RuntimeValidator()

if __name__ == "__main__":
    # Test the runtime validation system
    print("Starting Runtime Validation System")
    
    # Create validator
    validator = create_runtime_validator()
    
    # Test configuration
    test_config = {
        "task_domain": "Computer Vision",
        "task_type": "Image Classification",
        "pretrained_model": "resnet50",
        "model_tier": "base",
        "base_lr": 1e-4,
        "batch_size": 32,
        "num_epochs": 50,
        "optimizer": "adamw",
        "mixed_precision": "fp16",
        "use_automl": True,
        "use_quality_check": True
    }
    
    # Test dataset info
    test_dataset = {
        "data_type": "image",
        "num_samples": 5000,
        "num_classes": 10,
        "is_imbalanced": False,
        "has_noisy_labels": False
    }
    
    # Test hardware info
    test_hardware = {
        "device": "cuda",
        "vram_gb": 8.0,
        "cpu_count": 8
    }
    
    # Run validation
    is_valid, report = validator.validate_training_setup(test_config, test_dataset, test_hardware)
    
    print(f"\n{report}")
    print(f"\nValidation Result: {'PASSED' if is_valid else 'FAILED'}")
    
    print("\nRuntime validation system test completed!")