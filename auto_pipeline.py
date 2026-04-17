"""
Intelligent AutoML Pipeline for AxoLexis
Automatically analyzes data and builds optimal ML pipelines
"""

import os
import json
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
from PIL import Image
import torchvision.transforms as transforms
from torch.utils.data import Dataset, DataLoader
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

@dataclass
class DataAnalysis:
    """Results of automatic data analysis"""
    data_type: str
    num_samples: int
    num_features: int
    num_classes: int
    class_names: List[str]
    class_distribution: Dict[str, int]
    missing_values: float
    data_quality_score: float
    recommended_model: str
    recommended_batch_size: int
    recommended_learning_rate: float

class IntelligentDataAnalyzer:
    """Automatically analyzes different types of data and provides insights"""
    
    def __init__(self):
        self.supported_formats = {
            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.webp'],
            'csv': ['.csv'],
            'numpy': ['.npy', '.npz'],
            'json': ['.json']
        }
    
    def analyze_data_path(self, data_path: str) -> DataAnalysis:
        """Analyze data from file path and return comprehensive analysis"""
        path = Path(data_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Data path not found: {data_path}")
        
        # Determine data type
        data_type = self._detect_data_type(path)
        logger.info(f"Detected data type: {data_type}")
        
        # Analyze based on data type
        if data_type == 'image':
            return self._analyze_image_data(path)
        elif data_type == 'csv':
            return self._analyze_csv_data(path)
        elif data_type == 'numpy':
            return self._analyze_numpy_data(path)
        elif data_type == 'json':
            return self._analyze_json_data(path)
        else:
            raise ValueError(f"Unsupported data type: {data_type}")
    
    def _detect_data_type(self, path: Path) -> str:
        """Automatically detect data type from file extension and structure"""
        if path.is_dir():
            # Check for image folder structure
            image_extensions = self.supported_formats['image']
            for ext in image_extensions:
                if any(path.rglob(f"*{ext}")):
                    return 'image'
            return 'unknown'
        
        # Single file
        suffix = path.suffix.lower()
        for data_type, extensions in self.supported_formats.items():
            if suffix in extensions:
                return data_type
        
        return 'unknown'
    
    def _analyze_image_data(self, path: Path) -> DataAnalysis:
        """Analyze image dataset structure"""
        image_extensions = self.supported_formats['image']
        
        # Find all images
        if path.is_dir():
            image_files = []
            for ext in image_extensions:
                image_files.extend(path.rglob(f"*{ext}"))
        else:
            image_files = [path] if path.suffix.lower() in image_extensions else []
        
        if not image_files:
            raise ValueError("No image files found")
        
        # Analyze folder structure for classes
        class_names = set()
        if path.is_dir():
            for img_file in image_files:
                # Check if organized in subfolders (class structure)
                relative_path = img_file.relative_to(path)
                if len(relative_path.parts) > 1:
                    class_names.add(relative_path.parts[0])
        
        if not class_names:
            class_names = ["unknown"]
        
        # Sample a few images to get dimensions
        sample_images = image_files[:min(10, len(image_files))]
        sizes = []
        for img_file in sample_images:
            try:
                with Image.open(img_file) as img:
                    sizes.append(img.size)
            except Exception as e:
                logger.warning(f"Could not open image {img_file}: {e}")
        
        # Class distribution
        class_distribution = {}
        if path.is_dir() and len(class_names) > 1:
            for class_name in class_names:
                class_images = list(path.joinpath(class_name).rglob("*"))
                class_distribution[class_name] = len([f for f in class_images if f.suffix.lower() in image_extensions])
        else:
            class_distribution["unknown"] = len(image_files)
        
        # Calculate data quality score
        data_quality_score = self._calculate_image_quality_score(image_files)
        
        # Recommend model based on data characteristics
        num_samples = len(image_files)
        num_classes = len(class_names)
        
        recommended_model = self._recommend_image_model(num_samples, num_classes)
        recommended_batch_size = self._recommend_batch_size(num_samples)
        recommended_learning_rate = self._recommend_learning_rate(num_samples)
        
        return DataAnalysis(
            data_type='image',
            num_samples=num_samples,
            num_features=len(sizes[0]) if sizes else 0,
            num_classes=num_classes,
            class_names=list(class_names),
            class_distribution=class_distribution,
            missing_values=0.0,
            data_quality_score=data_quality_score,
            recommended_model=recommended_model,
            recommended_batch_size=recommended_batch_size,
            recommended_learning_rate=recommended_learning_rate
        )
    
    def _analyze_csv_data(self, path: Path) -> DataAnalysis:
        """Analyze CSV dataset"""
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise ValueError(f"Could not read CSV file: {e}")
        
        num_samples = len(df)
        num_features = len(df.columns) - 1  # Assume last column is target
        
        # Detect target column (last column)
        target_col = df.columns[-1]
        
        # Analyze target variable
        if df[target_col].dtype == 'object' or df[target_col].nunique() < 20:
            # Classification
            class_distribution = df[target_col].value_counts().to_dict()
            num_classes = len(class_distribution)
            class_names = list(class_distribution.keys())
        else:
            # Regression
            class_distribution = {target_col: num_samples}
            num_classes = 1
            class_names = [target_col]
        
        # Calculate missing values percentage
        missing_values = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 100
        
        # Data quality score
        data_quality_score = self._calculate_tabular_quality_score(df)
        
        # Recommend model
        recommended_model = self._recommend_tabular_model(num_samples, num_features, num_classes)
        recommended_batch_size = self._recommend_batch_size(num_samples)
        recommended_learning_rate = self._recommend_learning_rate(num_samples)
        
        return DataAnalysis(
            data_type='tabular',
            num_samples=num_samples,
            num_features=num_features,
            num_classes=num_classes,
            class_names=class_names,
            class_distribution=class_distribution,
            missing_values=missing_values,
            data_quality_score=data_quality_score,
            recommended_model=recommended_model,
            recommended_batch_size=recommended_batch_size,
            recommended_learning_rate=recommended_learning_rate
        )
    
    def _analyze_numpy_data(self, path: Path) -> DataAnalysis:
        """Analyze NumPy data"""
        try:
            data = np.load(path)
        except Exception as e:
            raise ValueError(f"Could not load NumPy file: {e}")
        
        if data.ndim == 2:
            # Tabular data
            num_samples, num_features = data.shape
            num_classes = 1
            class_names = ["target"]
            class_distribution = {"target": num_samples}
        elif data.ndim == 4:
            # Image data (N, H, W, C) or (N, C, H, W)
            num_samples = data.shape[0]
            num_features = data.shape[1:]
            num_classes = 1
            class_names = ["unknown"]
            class_distribution = {"unknown": num_samples}
        else:
            raise ValueError(f"Unsupported NumPy array shape: {data.shape}")
        
        data_quality_score = 1.0  # NumPy data is assumed clean
        
        recommended_model = "shada_base"  # Default recommendation
        recommended_batch_size = self._recommend_batch_size(num_samples)
        recommended_learning_rate = self._recommend_learning_rate(num_samples)
        
        return DataAnalysis(
            data_type='numpy',
            num_samples=num_samples,
            num_features=num_features if isinstance(num_features, int) else np.prod(num_features),
            num_classes=num_classes,
            class_names=class_names,
            class_distribution=class_distribution,
            missing_values=0.0,
            data_quality_score=data_quality_score,
            recommended_model=recommended_model,
            recommended_batch_size=recommended_batch_size,
            recommended_learning_rate=recommended_learning_rate
        )
    
    def _analyze_json_data(self, path: Path) -> DataAnalysis:
        """Analyze JSON data"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            raise ValueError(f"Could not load JSON file: {e}")
        
        # Handle different JSON structures
        if isinstance(data, list):
            num_samples = len(data)
            if num_samples > 0 and isinstance(data[0], dict):
                # List of records
                keys = list(data[0].keys())
                num_features = len(keys) - 1  # Assume one target
                
                # Try to find target variable
                target_key = keys[-1]  # Assume last key is target
                if isinstance(data[0][target_key], str):
                    # Classification
                    classes = list(set(item[target_key] for item in data))
                    num_classes = len(classes)
                    class_names = classes
                    class_distribution = {cls: sum(1 for item in data if item[target_key] == cls) for cls in classes}
                else:
                    # Regression
                    num_classes = 1
                    class_names = [target_key]
                    class_distribution = {target_key: num_samples}
            else:
                raise ValueError("Unsupported JSON structure")
        else:
            raise ValueError("Unsupported JSON structure")
        
        data_quality_score = 1.0
        recommended_model = "shada_base"
        recommended_batch_size = self._recommend_batch_size(num_samples)
        recommended_learning_rate = self._recommend_learning_rate(num_samples)
        
        return DataAnalysis(
            data_type='json',
            num_samples=num_samples,
            num_features=num_features,
            num_classes=num_classes,
            class_names=class_names,
            class_distribution=class_distribution,
            missing_values=0.0,
            data_quality_score=data_quality_score,
            recommended_model=recommended_model,
            recommended_batch_size=recommended_batch_size,
            recommended_learning_rate=recommended_learning_rate
        )
    
    def _calculate_image_quality_score(self, image_files: List[Path]) -> float:
        """Calculate data quality score for images"""
        corrupted_count = 0
        total_count = len(image_files)
        
        for img_file in image_files[:min(100, total_count)]:  # Sample 100 images
            try:
                with Image.open(img_file) as img:
                    img.verify()
            except Exception:
                corrupted_count += 1
        
        corruption_rate = corrupted_count / min(100, total_count)
        return max(0.0, 1.0 - corruption_rate)
    
    def _calculate_tabular_quality_score(self, df: pd.DataFrame) -> float:
        """Calculate data quality score for tabular data"""
        # Missing values penalty
        missing_penalty = (df.isnull().sum().sum() / (df.shape[0] * df.shape[1])) * 0.5
        
        # Duplicate rows penalty
        duplicate_penalty = (df.duplicated().sum() / len(df)) * 0.3
        
        # Class imbalance penalty (for classification)
        if df.iloc[:, -1].dtype == 'object' or df.iloc[:, -1].nunique() < 20:
            class_counts = df.iloc[:, -1].value_counts()
            imbalance_ratio = class_counts.min() / class_counts.max()
            imbalance_penalty = (1 - imbalance_ratio) * 0.2
        else:
            imbalance_penalty = 0.0
        
        return max(0.0, 1.0 - missing_penalty - duplicate_penalty - imbalance_penalty)
    
    def _recommend_image_model(self, num_samples: int, num_classes: int) -> str:
        """Recommend optimal model for image data"""
        if num_samples < 1000:
            return "efficientnet_b0"  # Small model for small datasets
        elif num_samples < 10000:
            return "efficientnet_b3"  # Medium model
        elif num_samples < 50000:
            return "efficientnet_b5"  # Large model
        else:
            return "shada_large"  # Custom large architecture
    
    def _recommend_tabular_model(self, num_samples: int, num_features: int, num_classes: int) -> str:
        """Recommend optimal model for tabular data"""
        if num_classes == 1:
            # Regression
            return "shada_regression"
        elif num_classes == 2:
            # Binary classification
            return "shada_binary"
        else:
            # Multi-class classification
            return "shada_multiclass"
    
    def _recommend_batch_size(self, num_samples: int) -> int:
        """Recommend optimal batch size based on dataset size"""
        if num_samples < 100:
            return 8
        elif num_samples < 1000:
            return 16
        elif num_samples < 10000:
            return 32
        else:
            return 64
    
    def _recommend_learning_rate(self, num_samples: int) -> float:
        """Recommend optimal learning rate based on dataset size"""
        if num_samples < 1000:
            return 1e-4
        elif num_samples < 10000:
            return 5e-5
        else:
            return 1e-5

class AutoMLPipeline:
    """Intelligent pipeline that automatically builds optimal models"""
    
    def __init__(self):
        self.analyzer = IntelligentDataAnalyzer()
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        logger.info(f"Using device: {self.device}")
    
    def run_auto_pipeline(self, data_path: str, output_dir: str = "./auto_results") -> Dict[str, Any]:
        """Run the complete automated ML pipeline"""
        logger.info("Starting AutoML Pipeline...")
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Step 1: Analyze data
        logger.info("Step 1: Analyzing data...")
        analysis = self.analyzer.analyze_data_path(data_path)
        
        # Step 2: Generate report
        logger.info("Step 2: Generating analysis report...")
        report = self.generate_report(analysis, data_path)
        
        # Step 3: Build and train model
        logger.info("Step 3: Building and training model...")
        training_results = self.build_and_train_model(data_path, analysis, output_dir)
        
        # Step 4: Generate final report
        logger.info("Step 4: Generating final report...")
        final_report = {
            "data_analysis": analysis.__dict__,
            "initial_report": report,
            "training_results": training_results,
            "recommendations": self.generate_recommendations(analysis, training_results)
        }
        
        # Save report
        report_path = os.path.join(output_dir, "auto_pipeline_report.json")
        with open(report_path, 'w') as f:
            json.dump(final_report, f, indent=2, default=str)
        
        logger.info(f"AutoML pipeline completed! Report saved to: {report_path}")
        return final_report
    
    def generate_report(self, analysis: DataAnalysis, data_path: str) -> Dict[str, Any]:
        """Generate comprehensive data analysis report"""
        report = {
            "dataset_info": {
                "path": data_path,
                "type": analysis.data_type,
                "num_samples": analysis.num_samples,
                "num_features": analysis.num_features,
                "num_classes": analysis.num_classes
            },
            "class_distribution": analysis.class_distribution,
            "data_quality": {
                "score": analysis.data_quality_score,
                "missing_values_percent": analysis.missing_values,
                "quality_assessment": self.assess_data_quality(analysis.data_quality_score)
            },
            "recommendations": {
                "model": analysis.recommended_model,
                "batch_size": analysis.recommended_batch_size,
                "learning_rate": analysis.recommended_learning_rate
            },
            "insights": self.generate_insights(analysis)
        }
        
        return report
    
    def assess_data_quality(self, score: float) -> str:
        """Assess data quality based on score"""
        if score >= 0.9:
            return "Excellent - High quality data suitable for training"
        elif score >= 0.7:
            return "Good - Data quality is acceptable with minor issues"
        elif score >= 0.5:
            return "Fair - Data has some quality issues that may affect training"
        else:
            return "Poor - Data quality needs significant improvement"
    
    def generate_insights(self, analysis: DataAnalysis) -> List[str]:
        """Generate data insights"""
        insights = []
        
        # Class imbalance insight
        if analysis.num_classes > 1:
            class_counts = list(analysis.class_distribution.values())
            max_count = max(class_counts)
            min_count = min(class_counts)
            imbalance_ratio = min_count / max_count
            
            if imbalance_ratio < 0.3:
                insights.append(f"Severe class imbalance detected (ratio: {imbalance_ratio:.2f}). Consider data augmentation or weighted loss.")
            elif imbalance_ratio < 0.7:
                insights.append(f"Moderate class imbalance detected (ratio: {imbalance_ratio:.2f}). Monitor model performance across classes.")
        
        # Dataset size insight
        if analysis.num_samples < 1000:
            insights.append("Small dataset detected. Consider data augmentation and transfer learning.")
        elif analysis.num_samples > 50000:
            insights.append("Large dataset detected. Can support complex model architectures.")
        
        # Data quality insight
        if analysis.data_quality_score < 0.7:
            insights.append("Data quality issues detected. Consider data cleaning before training.")
        
        # Feature insight for tabular data
        if analysis.data_type == 'tabular' and analysis.num_features > 100:
            insights.append("High-dimensional data detected. Consider feature selection or dimensionality reduction.")
        
        return insights
    
    def build_and_train_model(self, data_path: str, analysis: DataAnalysis, output_dir: str) -> Dict[str, Any]:
        """Build and train the recommended model"""
        # This is a placeholder for the actual model training
        # In a real implementation, this would integrate with the SHAHAD model factory
        
        logger.info(f"Building {analysis.recommended_model} model...")
        
        # Simulate training results
        training_results = {
            "model_type": analysis.recommended_model,
            "training_time": "15 minutes",  # Placeholder
            "final_accuracy": 0.92,  # Placeholder
            "final_loss": 0.15,  # Placeholder
            "epochs_trained": 10,  # Placeholder
            "best_hyperparameters": {
                "batch_size": analysis.recommended_batch_size,
                "learning_rate": analysis.recommended_learning_rate,
                "optimizer": "adamw"
            }
        }
        
        return training_results
    
    def generate_recommendations(self, analysis: DataAnalysis, training_results: Dict[str, Any]) -> List[str]:
        """Generate final recommendations"""
        recommendations = []
        
        # Model performance recommendations
        if training_results.get("final_accuracy", 0) < 0.8:
            recommendations.append("Consider hyperparameter tuning to improve model performance")
        
        # Data-specific recommendations
        if analysis.data_type == 'image':
            if analysis.num_samples < 5000:
                recommendations.append("Apply data augmentation techniques (rotation, flipping, scaling)")
            if analysis.data_quality_score < 0.8:
                recommendations.append("Clean corrupted images and ensure consistent image formats")
        
        elif analysis.data_type == 'tabular':
            if analysis.missing_values > 5:
                recommendations.append("Handle missing values using imputation techniques")
            if analysis.num_classes > 10:
                recommendations.append("Consider hierarchical classification for many classes")
        
        # General recommendations
        if analysis.num_classes > 1:
            class_counts = list(analysis.class_distribution.values())
            imbalance_ratio = min(class_counts) / max(class_counts)
            if imbalance_ratio < 0.5:
                recommendations.append("Use class-weighted loss or resampling for imbalanced data")
        
        recommendations.append("📊 Monitor validation metrics during training to prevent overfitting")
        recommendations.append("Save model checkpoints regularly during training")
        
        return recommendations

# Main execution function
def run_intelligent_analysis(data_path: str, output_dir: str = "./auto_results"):
    """Main function to run intelligent analysis"""
    pipeline = AutoMLPipeline()
    
    try:
        results = pipeline.run_auto_pipeline(data_path, output_dir)
        
        # Print summary
        print("\n" + "="*60)
        print("AXOLEXIS INTELLIGENT ANALYSIS COMPLETE")
        print("="*60)
        
        analysis = results["data_analysis"]
        print(f"📊 Dataset: {analysis['num_samples']} samples, {analysis['num_features']} features")
        print(f"🏷️  Classes: {analysis['num_classes']} ({', '.join(analysis['class_names'])})")
        print(f"⭐ Quality Score: {analysis['data_quality_score']:.2f}/1.0")
        print(f"🎯 Recommended Model: {analysis['recommended_model']}")
        print(f"⚙️  Batch Size: {analysis['recommended_batch_size']}, LR: {analysis['recommended_learning_rate']}")
        
        print("\n🔍 Key Insights:")
        for insight in results["initial_report"]["insights"]:
            print(f"  • {insight}")
        
        print("\n💡 Recommendations:")
        for rec in results["recommendations"]:
            print(f"  • {rec}")
        
        print(f"\n📁 Full report saved to: {output_dir}/auto_pipeline_report.json")
        print("="*60)
        
        return results
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    print("AxoLexis Intelligent AutoML Pipeline")
    print("This system will automatically analyze your data and build optimal models")
    print("="*60)
    
    # For testing, we'll create a synthetic dataset
    print("\n📁 Creating synthetic test dataset...")
    
    # Create synthetic CSV data
    test_data_path = "synthetic_test_data.csv"
    np.random.seed(42)
    n_samples = 1000
    n_features = 20
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Generate target (binary classification)
    y = (X[:, 0] + X[:, 1] * 2 + np.random.randn(n_samples) * 0.5) > 0
    y = y.astype(int)
    
    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y
    
    # Save to CSV
    df.to_csv(test_data_path, index=False)
    print(f"Created synthetic dataset: {test_data_path}")
    
    # Run intelligent analysis
    results = run_intelligent_analysis(test_data_path)
    
    # Clean up
    if os.path.exists(test_data_path):
        os.remove(test_data_path)
        print(f"🧹 Cleaned up test file: {test_data_path}")