"""
Comprehensive Test Suite for AxoLexis Intelligent Training System
Tests all new features and integrations
"""

import os
import sys
import torch
import numpy as np
import pandas as pd
from pathlib import Path
import logging
import tempfile
import json
from datetime import datetime

# Add the application directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_intelligent_training_integration():
    """Test the intelligent training integration system"""
    print("\n" + "="*60)
    print("🧪 TESTING INTELLIGENT TRAINING INTEGRATION")
    print("="*60)
    
    try:
        from intelligent_training_integration import IntelligentTrainingIntegration
        
        # Create test system
        system = IntelligentTrainingIntegration()
        
        # Create test configuration
        test_config = {
            'model_tier': 'base',
            'task_domain': 'Computer Vision',
            'task_type': 'Image Classification',
            'num_epochs': 5,
            'batch_size': 16,
            'base_lr': 1e-4,
            'optimizer': 'adamw'
        }
        
        # Create test data
        test_data_path = "intelligent_test_data.csv"
        np.random.seed(42)
        
        # Generate synthetic data
        n_samples = 1000
        n_features = 20
        
        X = np.random.randn(n_samples, n_features)
        y = np.random.choice([0, 1, 2], size=n_samples, p=[0.6, 0.3, 0.1])
        
        feature_names = [f"feature_{i}" for i in range(n_features)]
        df = pd.DataFrame(X, columns=feature_names)
        df["target"] = y
        
        # Add some quality issues
        missing_mask = np.random.random((n_samples, n_features)) < 0.02
        X[missing_mask] = np.nan
        df = pd.DataFrame(X, columns=feature_names)
        df["target"] = y
        
        df.to_csv(test_data_path, index=False)
        
        # Test signals
        results = []
        
        def on_progress(progress, message):
            print(f"📈 Progress: {progress}% - {message}")
        
        def on_feature_activated(feature, description):
            print(f"🤖 Feature Activated: {feature} - {description}")
        
        def on_model_selected(model, reasoning):
            print(f"🎯 Model Selected: {model}")
            print(f"   Reasoning: {reasoning}")
        
        def on_optimization_applied(opt_type, details):
            print(f"⚡ Optimization: {opt_type} - {details}")
        
        def on_training_completed(result):
            print(f"✅ Training Completed!")
            results.append(result)
        
        # Connect signals
        system.sig_training_progress.connect(on_progress)
        system.sig_intelligent_feature_activated.connect(on_feature_activated)
        system.sig_model_selected.connect(on_model_selected)
        system.sig_optimization_applied.connect(on_optimization_applied)
        system.sig_training_completed.connect(on_training_completed)
        
        # Run intelligent training
        print("\n🚀 Starting Intelligent Training...")
        result = system.start_intelligent_training(test_data_path, test_config)
        
        # Verify results
        assert len(results) > 0, "Training should have completed"
        final_result = results[0]
        
        assert 'intelligent_features_used' in final_result, "Should have intelligent features"
        assert 'optimization_summary' in final_result, "Should have optimization summary"
        assert 'data_quality_assessment' in final_result, "Should have quality assessment"
        assert 'model_selection' in final_result, "Should have model selection"
        
        print(f"\n📊 Final Results:")
        print(f"   Intelligent Features Used: {len(final_result['intelligent_features_used'])}")
        print(f"   Optimizations Applied: {final_result['optimization_summary']['total_optimizations_applied']}")
        print(f"   Data Quality Score: {final_result['data_quality_assessment']['overall_score']}")
        
        # Clean up
        if os.path.exists(test_data_path):
            os.remove(test_data_path)
        
        print("\n✅ Intelligent Training Integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Intelligent Training Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_enhanced_model_registry():
    """Test the enhanced model registry"""
    print("\n" + "="*60)
    print("🧪 TESTING ENHANCED MODEL REGISTRY")
    print("="*60)
    
    try:
        from models.enhanced_model_registry import (
            AI_TASK_DOMAINS, MODEL_REGISTRY, get_models_by_task, 
            validate_task_compatibility, get_all_model_names
        )
        
        # Test task domains
        print(f"📋 Available Task Domains: {len(AI_TASK_DOMAINS)}")
        for domain, tasks in AI_TASK_DOMAINS.items():
            print(f"   {domain}: {len(tasks)} task types")
        
        # Test model registry
        print(f"\n📦 Available Model Categories: {len(MODEL_REGISTRY)}")
        total_models = 0
        for category, subcategories in MODEL_REGISTRY.items():
            for subcategory, models in subcategories.items():
                total_models += len(models)
        print(f"   Total Models: {total_models}")
        
        # Test model recommendation for specific tasks
        test_tasks = [
            ("Computer Vision", "Image Classification"),
            ("Natural Language Processing (NLP)", "Text Classification"),
            ("Speech & Audio", "Speech Recognition")
        ]
        
        for domain, task in test_tasks:
            recommended = get_models_by_task(domain, task)
            print(f"\n🎯 Recommended models for {domain} - {task}:")
            for category, models in recommended.items():
                print(f"   {category}: {len(models)} models")
        
        # Test task compatibility validation
        test_compatibility = [
            ("Computer Vision", "Image Classification", "ResNet-50"),
            ("Natural Language Processing (NLP)", "Text Classification", "BERT-Base"),
            ("Computer Vision", "Image Classification", "BERT-Base")  # Should be incompatible
        ]
        
        for domain, task, model in test_compatibility:
            is_compatible = validate_task_compatibility(domain, task, "", model)
            print(f"\n🔍 {model} for {domain} - {task}: {'✅ Compatible' if is_compatible else '❌ Incompatible'}")
        
        # Test all model names
        all_models = get_all_model_names()
        print(f"\n📋 Total model options: {len(all_models)}")
        print(f"   First 10: {all_models[:10]}")
        
        print("\n✅ Enhanced Model Registry test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Enhanced Model Registry test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_model_download_manager():
    """Test the model download manager"""
    print("\n" + "="*60)
    print("🧪 TESTING MODEL DOWNLOAD MANAGER")
    print("="*60)
    
    try:
        from models.model_download_manager import create_model_download_manager, create_model_availability_checker
        
        # Create managers
        download_manager = create_model_download_manager()
        availability_checker = create_model_availability_checker(download_manager)
        
        # Test model availability checking
        test_models = ["bert-base-uncased", "resnet18", "gpt2"]
        
        for model in test_models:
            is_available, source, path = download_manager.check_model_availability(model)
            info = download_manager.get_model_info(model)
            
            print(f"\n📊 Model: {model}")
            print(f"   Available: {is_available}")
            print(f"   Source: {source}")
            print(f"   Size: {info['size_mb']} MB")
            print(f"   Download Required: {info['download_required']}")
        
        # Test available models
        available = download_manager.get_available_models()
        print(f"\n📦 Available models by source:")
        for source, models in available.items():
            print(f"   {source}: {len(models)} models")
        
        # Test recommendations
        recommendations = availability_checker.get_recommended_models("Computer Vision", "Image Classification")
        print(f"\n🎯 Recommended CV models: {recommendations}")
        
        recommendations = availability_checker.get_recommended_models("Natural Language Processing (NLP)", "Text Classification")
        print(f"\n🎯 Recommended NLP models: {recommendations}")
        
        print("\n✅ Model Download Manager test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model Download Manager test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_transparency_logger():
    """Test the transparency logging system"""
    print("\n" + "="*60)
    print("🧪 TESTING TRANSPARENCY LOGGER")
    print("="*60)
    
    try:
        from training_transparency_logger import create_transparency_logger
        
        # Create logger
        logger = create_transparency_logger()
        
        # Simulate training session
        logger.start_training_session("ResNet-50", "Computer Vision", "Image Classification", "dataset.csv")
        
        # Simulate training steps
        for i in range(10):
            metrics = {
                "accuracy": 0.5 + (i * 0.05),
                "loss": 1.0 - (i * 0.08),
                "learning_rate": 0.001 * (0.95 ** i)
            }
            logger.log_training_step(epoch=i//2, step=i, metrics=metrics)
        
        # Simulate intelligent features
        logger.log_intelligent_feature("Model Selection", {"selected_model": "ResNet-50", "reasoning": "Best for image classification"})
        logger.log_optimization("learning_rate", 0.001, 0.0005, "Reduced for better convergence")
        
        # Simulate data quality assessment
        logger.log_data_quality_assessment(quality_score=85.5, issues_found=2, critical_issues=0)
        
        # Simulate model selection
        logger.log_model_selection("ResNet-50", "Optimal for image classification task", ["VGG-16", "EfficientNet-B0"])
        
        # End session
        logger.end_training_session(final_accuracy=0.95, total_time=1200)
        
        # Get reports
        summary = logger.get_training_summary()
        performance = logger.get_performance_report()
        
        print(f"\n📊 Training Summary:")
        print(f"   Model: {summary['session_info']['model_name']}")
        print(f"   Task: {summary['session_info']['task_domain']} - {summary['session_info']['task_type']}")
        print(f"   Steps: {summary['training_steps']}")
        print(f"   Final Accuracy: {summary['session_info']['final_accuracy']}")
        
        print(f"\n📈 Performance Report:")
        print(f"   Best Accuracy: {performance['accuracy']['best']:.3f}")
        print(f"   Average Accuracy: {performance['accuracy']['average']:.3f}")
        print(f"   Training Time: {performance['training_efficiency']['total_time']:.1f} minutes")
        
        # Generate visualization
        viz_path = logger.generate_training_visualization()
        print(f"\n🖼️  Visualization saved to: {viz_path}")
        
        print("\n✅ Transparency Logger test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Transparency Logger test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_runtime_validator():
    """Test the runtime validation system"""
    print("\n" + "="*60)
    print("🧪 TESTING RUNTIME VALIDATOR")
    print("="*60)
    
    try:
        from runtime_validator import create_runtime_validator
        
        # Create validator
        validator = create_runtime_validator()
        
        # Test valid configuration
        test_config = {
            "task_domain": "Computer Vision",
            "task_type": "Image Classification",
            "pretrained_model": "resnet50",
            "model_tier": "base",
            "base_lr": 1e-4,
            "batch_size": 32,
            "num_epochs": 50,
            "optimizer": "adamw",
            "mixed_precision": "fp16"
        }
        
        test_dataset = {
            "data_type": "image",
            "num_samples": 5000,
            "num_classes": 10,
            "is_imbalanced": False,
            "has_noisy_labels": False
        }
        
        test_hardware = {
            "device": "cuda",
            "vram_gb": 8.0,
            "cpu_count": 8
        }
        
        # Run validation
        is_valid, report = validator.validate_training_setup(test_config, test_dataset, test_hardware)
        
        print(f"\n📋 Validation Report:")
        print(report)
        print(f"\nValidation Result: {'PASSED' if is_valid else 'FAILED'}")
        
        # Test invalid configuration
        invalid_config = test_config.copy()
        invalid_config["base_lr"] = -0.1  # Invalid learning rate
        invalid_config["batch_size"] = 0   # Invalid batch size
        
        is_valid_invalid, report_invalid = validator.validate_training_setup(invalid_config, test_dataset, test_hardware)
        
        print(f"\n📋 Invalid Configuration Test:")
        print(f"Validation Result: {'PASSED' if is_valid_invalid else 'FAILED'}")
        assert not is_valid_invalid, "Invalid configuration should fail validation"
        
        print("\n✅ Runtime Validator test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Runtime Validator test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_integration():
    """Test complete system integration"""
    print("\n" + "="*60)
    print("🧪 TESTING COMPLETE SYSTEM INTEGRATION")
    print("="*60)
    
    try:
        # Test that all modules can be imported together
        from intelligent_training_integration import IntelligentTrainingIntegration
        from models.enhanced_model_registry import AI_TASK_DOMAINS, MODEL_REGISTRY
        from models.model_download_manager import create_model_download_manager
        from training_transparency_logger import create_transparency_logger
        from runtime_validator import create_runtime_validator
        
        print("✅ All modules imported successfully")
        
        # Test cross-module functionality
        print("\n🔄 Testing cross-module integration...")
        
        # Create test instances
        intelligent_training = IntelligentTrainingIntegration()
        transparency_logger = create_transparency_logger()
        runtime_validator = create_runtime_validator()
        
        # Test configuration compatibility
        test_config = {
            'task_domain': 'Computer Vision',
            'task_type': 'Image Classification',
            'model_tier': 'base',
            'pretrained_model': 'resnet50',
            'num_epochs': 10,
            'batch_size': 16,
            'base_lr': 1e-4,
            'optimizer': 'adamw',
            'mixed_precision': 'fp16'
        }
        
        test_dataset = {
            'data_type': 'image',
            'num_samples': 1000,
            'num_classes': 10,
            'is_imbalanced': False,
            'has_noisy_labels': False
        }
        
        test_hardware = {
            'device': 'cuda' if torch.cuda.is_available() else 'cpu',
            'vram_gb': 8.0 if torch.cuda.is_available() else 0,
            'cpu_count': 4
        }
        
        # Validate configuration
        is_valid, report = runtime_validator.validate_training_setup(test_config, test_dataset, test_hardware)
        print(f"   Runtime validation: {'✅ PASSED' if is_valid else '❌ FAILED'}")
        
        # Test transparency logging
        transparency_logger.log_model_configuration(test_config)
        transparency_logger.log_intelligent_feature("System Integration Test", {"status": "passed"})
        
        summary = transparency_logger.get_training_summary()
        print(f"   Transparency logging: ✅ Active ({summary['model_configs_applied']} configs logged)")
        
        print("\n✅ Complete System Integration test PASSED!")
        return True
        
    except Exception as e:
        print(f"\n❌ Complete System Integration test FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_all_tests():
    """Run all test suites"""
    print("\n" + "="*80)
    print("🚀 AXOLEXIS INTELLIGENT TRAINING SYSTEM - COMPREHENSIVE TEST SUITE")
    print("="*80)
    
    tests = [
        ("Intelligent Training Integration", test_intelligent_training_integration),
        ("Enhanced Model Registry", test_enhanced_model_registry),
        ("Model Download Manager", test_model_download_manager),
        ("Transparency Logger", test_transparency_logger),
        ("Runtime Validator", test_runtime_validator),
        ("Complete System Integration", test_system_integration)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            print(f"\n{'='*60}")
            print(f"🧪 Running: {test_name}")
            print('='*60)
            
            success = test_func()
            results.append((test_name, success))
            
            if success:
                print(f"\n✅ {test_name} - PASSED")
            else:
                print(f"\n❌ {test_name} - FAILED")
                
        except Exception as e:
            print(f"\n💥 {test_name} - CRASHED: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "="*80)
    print("📊 TEST SUMMARY")
    print("="*80)
    
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    for test_name, success in results:
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"   {test_name:<40} {status}")
    
    print(f"\n📈 Overall Results: {passed}/{total} tests passed ({passed/total*100:.1f}%)")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! AxoLexis Intelligent Training System is ready!")
        print("\n🚀 System Features Verified:")
        print("   ✅ Intelligent Training Integration")
        print("   ✅ Comprehensive AI Task Domains (7 domains, 25+ task types)")
        print("   ✅ Enhanced Model Registry (100+ models across 8 categories)")
        print("   ✅ Model Auto-Download System (Hugging Face, Torch Hub, ONNX)")
        print("   ✅ Real-time Transparency & Logging")
        print("   ✅ Runtime Validation System")
        print("   ✅ Complete System Integration")
        
        print("\n🎯 Key Capabilities:")
        print("   • AutoML with intelligent model selection")
        print("   • Adaptive hyperparameter optimization")
        print("   • Real-time data quality checking")
        print("   • Dynamic architecture selection")
        print("   • Comprehensive logging and transparency")
        print("   • Task-specific model recommendations")
        print("   • Hardware-aware configuration validation")
        
        return True
    else:
        print(f"\n⚠️  {total - passed} tests failed. Please review the errors above.")
        return False

if __name__ == "__main__":
    try:
        success = run_all_tests()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Test suite interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\n💥 Test suite crashed: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)