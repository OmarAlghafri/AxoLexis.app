"""
Intelligent Model Selection and Architecture Optimization
Integrates with SHAHAD model factory to automatically select optimal architectures
"""

import torch
import torch.nn as nn
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
import numpy as np
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

@dataclass
class ModelRecommendation:
    """Model architecture recommendation"""
    architecture: str
    model_size: str
    num_parameters: int
    estimated_memory_mb: int
    training_time_estimate: str
    performance_estimate: float
    reasoning: str
    hyperparameters: Dict[str, Any]

class IntelligentModelSelector:
    """Automatically selects optimal model architecture based on data characteristics"""
    
    def __init__(self):
        self.architectures = {
            'shada_nano': {
                'params': 5e6,
                'memory_mb': 512,
                'training_time': 'fast',
                'best_for': 'small_datasets',
                'description': 'Lightweight SHADA for quick prototyping'
            },
            'shada_base': {
                'params': 50e6,
                'memory_mb': 2048,
                'training_time': 'medium',
                'best_for': 'medium_datasets',
                'description': 'Balanced SHADA for general use'
            },
            'shada_large': {
                'params': 200e6,
                'memory_mb': 8192,
                'training_time': 'slow',
                'best_for': 'large_datasets',
                'description': 'Large SHADA for complex tasks'
            },
            'shada_xl': {
                'params': 1e9,
                'memory_mb': 16384,
                'training_time': 'very_slow',
                'best_for': 'massive_datasets',
                'description': 'Extra-large SHADA for state-of-the-art'
            },
            'efficientnet_b0': {
                'params': 5.3e6,
                'memory_mb': 512,
                'training_time': 'fast',
                'best_for': 'image_classification',
                'description': 'EfficientNet-B0 for image tasks'
            },
            'efficientnet_b3': {
                'params': 12e6,
                'memory_mb': 1024,
                'training_time': 'medium',
                'best_for': 'image_classification',
                'description': 'EfficientNet-B3 for better accuracy'
            },
            'efficientnet_b5': {
                'params': 30e6,
                'memory_mb': 2048,
                'training_time': 'medium',
                'best_for': 'image_classification',
                'description': 'EfficientNet-B5 for high accuracy'
            },
            'gpt2_small': {
                'params': 117e6,
                'memory_mb': 4096,
                'training_time': 'medium',
                'best_for': 'text_tasks',
                'description': 'GPT-2 small for text processing'
            }
        }
    
    def recommend_model(self, data_analysis: Dict[str, Any], hardware_info: Optional[Dict[str, Any]] = None) -> ModelRecommendation:
        """Recommend optimal model based on data analysis and hardware constraints"""
        
        data_type = data_analysis['data_type']
        num_samples = data_analysis['num_samples']
        num_classes = data_analysis['num_classes']
        num_features = data_analysis['num_features']
        data_quality = data_analysis['data_quality_score']
        
        # Get hardware constraints
        if hardware_info is None:
            hardware_info = self._get_hardware_info()
        
        available_memory = hardware_info.get('gpu_memory_mb', 4096)  # Default 4GB
        
        logger.info(f"Recommending model for: {data_type} data, {num_samples} samples, {num_classes} classes")
        logger.info(f"Hardware constraints: {available_memory}MB GPU memory")
        
        # Filter architectures based on data type and constraints
        suitable_architectures = self._filter_architectures(data_type, num_samples, available_memory)
        
        # Rank architectures
        ranked_architectures = self._rank_architectures(suitable_architectures, data_analysis)
        
        # Select best architecture
        best_architecture = ranked_architectures[0]
        
        # Generate hyperparameters
        hyperparameters = self._generate_hyperparameters(best_architecture, data_analysis)
        
        # Create recommendation
        recommendation = ModelRecommendation(
            architecture=best_architecture,
            model_size=self.architectures[best_architecture]['description'],
            num_parameters=int(self.architectures[best_architecture]['params']),
            estimated_memory_mb=self.architectures[best_architecture]['memory_mb'],
            training_time_estimate=self.architectures[best_architecture]['training_time'],
            performance_estimate=self._estimate_performance(best_architecture, data_analysis),
            reasoning=self._generate_reasoning(best_architecture, data_analysis, hardware_info),
            hyperparameters=hyperparameters
        )
        
        return recommendation
    
    def _get_hardware_info(self) -> Dict[str, Any]:
        """Get current hardware information"""
        info = {}
        
        if torch.cuda.is_available():
            info['gpu_name'] = torch.cuda.get_device_name(0)
            info['gpu_memory_mb'] = torch.cuda.get_device_properties(0).total_memory // (1024 * 1024)
            info['cuda_version'] = torch.version.cuda
        else:
            info['gpu_name'] = 'CPU'
            info['gpu_memory_mb'] = 0
            info['cuda_version'] = None
        
        info['cpu_count'] = torch.get_num_threads()
        
        return info
    
    def _filter_architectures(self, data_type: str, num_samples: int, available_memory: int) -> List[str]:
        """Filter architectures based on data type and memory constraints"""
        suitable = []
        
        for arch_name, arch_info in self.architectures.items():
            # Memory constraint
            if arch_info['memory_mb'] > available_memory * 0.8:  # Use 80% as safety margin
                continue
            
            # Data type filtering
            if data_type == 'image' and 'efficientnet' in arch_name:
                suitable.append(arch_name)
            elif data_type == 'text' and 'gpt2' in arch_name:
                suitable.append(arch_name)
            elif 'shada' in arch_name:  # SHADA is multi-modal
                suitable.append(arch_name)
        
        # If no specific architecture found, default to SHADA
        if not suitable:
            suitable = ['shada_nano', 'shada_base']
        
        return suitable
    
    def _rank_architectures(self, architectures: List[str], data_analysis: Dict[str, Any]) -> List[str]:
        """Rank architectures based on suitability"""
        scores = {}
        
        for arch in architectures:
            score = self._calculate_architecture_score(arch, data_analysis)
            scores[arch] = score
        
        # Sort by score (descending)
        ranked = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)
        
        return ranked
    
    def _calculate_architecture_score(self, architecture: str, data_analysis: Dict[str, Any]) -> float:
        """Calculate suitability score for an architecture"""
        score = 0.0
        arch_info = self.architectures[architecture]
        
        num_samples = data_analysis['num_samples']
        data_quality = data_analysis['data_quality_score']
        num_classes = data_analysis['num_classes']
        
        # Dataset size scoring
        if arch_info['best_for'] == 'small_datasets' and num_samples < 1000:
            score += 0.3
        elif arch_info['best_for'] == 'medium_datasets' and 1000 <= num_samples < 10000:
            score += 0.3
        elif arch_info['best_for'] == 'large_datasets' and 10000 <= num_samples < 50000:
            score += 0.3
        elif arch_info['best_for'] == 'massive_datasets' and num_samples >= 50000:
            score += 0.3
        
        # Data quality scoring
        score += data_quality * 0.2
        
        # Complexity scoring (more classes = more complex model needed)
        if num_classes > 10 and 'large' in architecture:
            score += 0.2
        elif num_classes > 5 and 'base' in architecture:
            score += 0.2
        elif num_classes <= 5 and 'nano' in architecture:
            score += 0.2
        
        # Training time preference (faster models get slight bonus)
        if arch_info['training_time'] == 'fast':
            score += 0.1
        elif arch_info['training_time'] == 'very_slow':
            score -= 0.1
        
        return score
    
    def _generate_hyperparameters(self, architecture: str, data_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate optimal hyperparameters for the selected architecture"""
        hyperparams = {}
        
        num_samples = data_analysis['num_samples']
        num_classes = data_analysis['num_classes']
        data_quality = data_analysis['data_quality_score']
        
        # Learning rate (inverse relationship with dataset size)
        if num_samples < 1000:
            hyperparams['learning_rate'] = 1e-3
        elif num_samples < 10000:
            hyperparams['learning_rate'] = 5e-4
        else:
            hyperparams['learning_rate'] = 1e-4
        
        # Batch size (proportional to dataset size, but capped)
        if num_samples < 500:
            hyperparams['batch_size'] = 8
        elif num_samples < 2000:
            hyperparams['batch_size'] = 16
        elif num_samples < 10000:
            hyperparams['batch_size'] = 32
        else:
            hyperparams['batch_size'] = 64
        
        # Number of epochs (inverse relationship with data quality)
        if data_quality > 0.9:
            hyperparams['epochs'] = 50
        elif data_quality > 0.7:
            hyperparams['epochs'] = 75
        else:
            hyperparams['epochs'] = 100
        
        # Architecture-specific hyperparameters
        if 'shada' in architecture:
            hyperparams['model_tier'] = architecture.replace('shada_', '')
            hyperparams['use_ssl'] = True
            hyperparams['ssl_weight'] = 0.3 if data_quality < 0.8 else 0.1
            
            # Multi-task learning for complex datasets
            if num_classes > 10:
                hyperparams['multi_task'] = True
                hyperparams['auxiliary_heads'] = min(num_classes // 5, 5)
            else:
                hyperparams['multi_task'] = False
        
        elif 'efficientnet' in architecture:
            hyperparams['dropout_rate'] = 0.2 if num_samples > 10000 else 0.1
            hyperparams['label_smoothing'] = 0.1 if num_classes > 5 else 0.0
        
        elif 'gpt2' in architecture:
            hyperparams['max_seq_length'] = 512
            hyperparams['warmup_steps'] = min(1000, num_samples // 10)
        
        # Optimization hyperparameters
        hyperparams['optimizer'] = 'adamw'
        hyperparams['weight_decay'] = 0.01 if num_samples > 5000 else 0.001
        hyperparams['scheduler'] = 'cosine'
        
        return hyperparams
    
    def _estimate_performance(self, architecture: str, data_analysis: Dict[str, Any]) -> float:
        """Estimate expected performance based on architecture and data characteristics"""
        base_performance = 0.85  # Base performance assumption
        
        # Architecture modifier
        if 'nano' in architecture:
            arch_modifier = -0.1
        elif 'base' in architecture:
            arch_modifier = 0.0
        elif 'large' in architecture:
            arch_modifier = 0.05
        elif 'xl' in architecture:
            arch_modifier = 0.1
        else:
            arch_modifier = 0.0
        
        # Data quality modifier
        quality_modifier = (data_analysis['data_quality_score'] - 0.8) * 0.2
        
        # Dataset size modifier (diminishing returns)
        num_samples = data_analysis['num_samples']
        if num_samples < 1000:
            size_modifier = -0.15
        elif num_samples < 5000:
            size_modifier = -0.05
        elif num_samples < 20000:
            size_modifier = 0.0
        else:
            size_modifier = 0.05
        
        estimated_performance = base_performance + arch_modifier + quality_modifier + size_modifier
        
        return max(0.5, min(0.99, estimated_performance))  # Clamp between 50% and 99%
    
    def _generate_reasoning(self, architecture: str, data_analysis: Dict[str, Any], hardware_info: Dict[str, Any]) -> str:
        """Generate reasoning for the recommendation"""
        reasons = []
        
        # Data-based reasoning
        num_samples = data_analysis['num_samples']
        if num_samples < 1000:
            reasons.append(f"Small dataset ({num_samples} samples) favors lighter architectures")
        elif num_samples > 50000:
            reasons.append(f"Large dataset ({num_samples} samples) can support complex architectures")
        
        # Quality-based reasoning
        quality = data_analysis['data_quality_score']
        if quality < 0.7:
            reasons.append(f"Lower data quality (score: {quality:.2f}) suggests starting with simpler models")
        
        # Hardware-based reasoning
        if hardware_info['gpu_memory_mb'] < 4096:
            reasons.append(f"Limited GPU memory ({hardware_info['gpu_memory_mb']}MB) restricts model size")
        
        # Architecture-specific reasoning
        if 'shada' in architecture:
            reasons.append("SHADA architecture provides good balance of performance and efficiency")
        elif 'efficientnet' in architecture:
            reasons.append("EfficientNet optimized for image classification with good accuracy/efficiency trade-off")
        elif 'gpt2' in architecture:
            reasons.append("GPT-2 architecture well-suited for text processing tasks")
        
        return "; ".join(reasons)

class AdaptiveHyperparameterOptimizer:
    """Automatically optimizes hyperparameters during training"""
    
    def __init__(self):
        self.optimization_history = []
        self.best_params = None
        self.best_score = 0.0
    
    def adaptive_learning_rate_schedule(self, epoch: int, initial_lr: float, validation_scores: List[float]) -> float:
        """Dynamically adjust learning rate based on validation performance"""
        if len(validation_scores) < 3:
            return initial_lr
        
        # Check for plateau
        recent_scores = validation_scores[-3:]
        if max(recent_scores) - min(recent_scores) < 0.01:  # Plateau detected
            return initial_lr * 0.5
        
        # Check for degradation
        if validation_scores[-1] < validation_scores[-2] - 0.02:  # Performance dropped
            return initial_lr * 0.8
        
        # Gradual decay
        decay_factor = 0.95 ** (epoch // 10)
        return initial_lr * decay_factor
    
    def adaptive_batch_size(self, current_batch_size: int, gpu_utilization: float, training_speed: float) -> int:
        """Adjust batch size based on GPU utilization and training speed"""
        if gpu_utilization < 0.7 and training_speed < 100:  # Underutilized
            return min(current_batch_size * 2, 256)  # Double batch size, cap at 256
        elif gpu_utilization > 0.95:  # Overutilized
            return max(current_batch_size // 2, 8)  # Halve batch size, min 8
        
        return current_batch_size
    
    def early_stopping_criterion(self, validation_scores: List[float], patience: int = 10) -> bool:
        """Determine if training should stop early"""
        if len(validation_scores) < patience:
            return False
        
        recent_best = max(validation_scores[-patience:])
        overall_best = max(validation_scores)
        
        # Stop if no improvement in patience epochs
        if recent_best < overall_best - 0.01:  # Allow small tolerance
            return True
        
        return False

# Integration with AxoLexis
def integrate_with_axolexis(data_path: str, model_selector: IntelligentModelSelector) -> Dict[str, Any]:
    """Integrate intelligent model selection with AxoLexis application"""
    
    # Import the data analyzer from our auto_pipeline
    from auto_pipeline import IntelligentDataAnalyzer
    
    # Analyze data
    analyzer = IntelligentDataAnalyzer()
    data_analysis = analyzer.analyze_data_path(data_path)
    
    # Convert to dict for model selector
    analysis_dict = {
        'data_type': data_analysis.data_type,
        'num_samples': data_analysis.num_samples,
        'num_features': data_analysis.num_features,
        'num_classes': data_analysis.num_classes,
        'data_quality_score': data_analysis.data_quality_score,
        'class_distribution': data_analysis.class_distribution
    }
    
    # Get model recommendation
    recommendation = model_selector.recommend_model(analysis_dict)
    
    # Create integration result
    integration_result = {
        'data_analysis': analysis_dict,
        'model_recommendation': {
            'architecture': recommendation.architecture,
            'model_size': recommendation.model_size,
            'num_parameters': recommendation.num_parameters,
            'estimated_memory_mb': recommendation.estimated_memory_mb,
            'performance_estimate': recommendation.performance_estimate,
            'reasoning': recommendation.reasoning,
            'hyperparameters': recommendation.hyperparameters
        },
        'integration_notes': [
            f"Recommended model: {recommendation.architecture}",
            f"Expected performance: {recommendation.performance_estimate:.1%}",
            f"Estimated memory usage: {recommendation.estimated_memory_mb}MB",
            f"Training time: {recommendation.training_time_estimate}",
            "Configure AxoLexis with these parameters for optimal results"
        ]
    }
    
    return integration_result

if __name__ == "__main__":
    # Test the intelligent model selector
    print("Intelligent Model Selector for AxoLexis")
    print("="*50)
    
    # Create test data analysis
    test_analysis = {
        'data_type': 'image',
        'num_samples': 5000,
        'num_features': 224*224*3,
        'num_classes': 10,
        'data_quality_score': 0.85,
        'class_distribution': {'class_0': 500, 'class_1': 450, 'class_2': 520}
    }
    
    # Create model selector
    selector = IntelligentModelSelector()
    
    # Get recommendation
    recommendation = selector.recommend_model(test_analysis)
    
    # Print results
    print(f"📊 Data: {test_analysis['num_samples']} samples, {test_analysis['num_classes']} classes")
    print(f"⭐ Quality: {test_analysis['data_quality_score']:.2f}")
    print(f"\nRecommended Architecture: {recommendation.architecture}")
    print(f"📏 Model Size: {recommendation.model_size}")
    print(f"🔢 Parameters: {recommendation.num_parameters:,}")
    print(f"💾 Memory: {recommendation.estimated_memory_mb}MB")
    print(f"Training Time: {recommendation.training_time_estimate}")
    print(f"📈 Expected Performance: {recommendation.performance_estimate:.1%}")
    print(f"\n🤔 Reasoning: {recommendation.reasoning}")
    
    print(f"\n⚙️  Recommended Hyperparameters:")
    for key, value in recommendation.hyperparameters.items():
        print(f"  • {key}: {value}")
    
    print("\n" + "="*50)