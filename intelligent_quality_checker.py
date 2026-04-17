"""
Intelligent Error Detection and Data Quality System
Automatically detects and fixes common data quality issues
"""

import os
import numpy as np
import pandas as pd
import torch
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass
from pathlib import Path
import logging
from PIL import Image
import hashlib
import warnings
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

@dataclass
class DataQualityIssue:
    """Represents a detected data quality issue"""
    issue_type: str
    severity: str  # 'critical', 'major', 'minor'
    description: str
    affected_samples: int
    affected_features: Optional[List[str]] = None
    suggested_fix: str = ""
    auto_fixable: bool = False

@dataclass
class DataQualityReport:
    """Complete data quality assessment report"""
    total_issues: int
    critical_issues: int
    major_issues: int
    minor_issues: int
    overall_score: float
    issues: List[DataQualityIssue]
    recommendations: List[str]
    auto_fix_summary: Dict[str, Any]

class IntelligentDataQualityChecker:
    """Intelligent system for detecting and fixing data quality issues"""
    
    def __init__(self):
        self.issues = []
        self.supported_formats = {
            'image': ['.png', '.jpg', '.jpeg', '.bmp', '.webp', '.tiff'],
            'csv': ['.csv', '.tsv'],
            'numpy': ['.npy', '.npz'],
            'json': ['.json']
        }
    
    def comprehensive_quality_check(self, data_path: str, auto_fix: bool = True) -> DataQualityReport:
        """Perform comprehensive data quality assessment"""
        logger.info(f"Starting comprehensive quality check for: {data_path}")
        
        self.issues = []
        path = Path(data_path)
        
        if not path.exists():
            raise FileNotFoundError(f"Data path not found: {data_path}")
        
        # Detect data type
        data_type = self._detect_data_type(path)
        logger.info(f"Detected data type: {data_type}")
        
        # Run appropriate quality checks
        if data_type == 'image':
            self._check_image_quality(path)
        elif data_type == 'csv':
            self._check_csv_quality(path)
        elif data_type == 'numpy':
            self._check_numpy_quality(path)
        elif data_type == 'json':
            self._check_json_quality(path)
        else:
            self._check_generic_quality(path)
        
        # Generate report
        report = self._generate_quality_report()
        
        # Auto-fix if requested
        auto_fix_results = {}
        if auto_fix:
            auto_fix_results = self._auto_fix_issues(data_path, data_type)
            report.auto_fix_summary = auto_fix_results
        
        return report
    
    def _detect_data_type(self, path: Path) -> str:
        """Automatically detect data type"""
        if path.is_dir():
            # Check for image files
            for ext in self.supported_formats['image']:
                if any(path.rglob(f"*{ext}")):
                    return 'image'
            return 'directory'
        
        # Single file
        suffix = path.suffix.lower()
        for data_type, extensions in self.supported_formats.items():
            if suffix in extensions:
                return data_type
        
        return 'unknown'
    
    def _check_image_quality(self, path: Path):
        """Check image dataset quality"""
        image_files = []
        for ext in self.supported_formats['image']:
            if path.is_dir():
                image_files.extend(path.rglob(f"*{ext}"))
            else:
                if path.suffix.lower() == ext:
                    image_files.append(path)
        
        logger.info(f"Found {len(image_files)} image files")
        
        # Check 1: Corrupted images
        self._check_corrupted_images(image_files)
        
        # Check 2: Inconsistent image sizes
        self._check_image_dimensions(image_files)
        
        # Check 3: Class imbalance
        if path.is_dir():
            self._check_class_distribution(path, image_files)
        
        # Check 4: Duplicate images (using hash)
        self._check_duplicate_images(image_files)
        
        # Check 5: Image format consistency
        self._check_image_formats(image_files)
        
        # Check 6: File naming issues
        self._check_file_naming(image_files)
    
    def _check_csv_quality(self, path: Path):
        """Check CSV dataset quality"""
        try:
            df = pd.read_csv(path)
        except Exception as e:
            self.issues.append(DataQualityIssue(
                issue_type="file_read_error",
                severity="critical",
                description=f"Cannot read CSV file: {str(e)}",
                affected_samples=0,
                auto_fixable=False,
                suggested_fix="Check file format and encoding"
            ))
            return
        
        logger.info(f"Loaded CSV with shape: {df.shape}")
        
        # Check 1: Missing values
        self._check_missing_values(df)
        
        # Check 2: Duplicate rows
        self._check_duplicate_rows(df)
        
        # Check 3: Data type consistency
        self._check_data_types(df)
        
        # Check 4: Outliers
        self._check_outliers(df)
        
        # Check 5: Class imbalance (if classification)
        self._check_target_distribution(df)
        
        # Check 6: Feature correlation
        self._check_feature_correlation(df)
        
        # Check 7: Constant features
        self._check_constant_features(df)
        
        # Check 8: Data range issues
        self._check_data_ranges(df)
    
    def _check_numpy_quality(self, path: Path):
        """Check NumPy array quality"""
        try:
            data = np.load(path)
        except Exception as e:
            self.issues.append(DataQualityIssue(
                issue_type="file_read_error",
                severity="critical",
                description=f"Cannot load NumPy file: {str(e)}",
                affected_samples=0,
                auto_fixable=False,
                suggested_fix="Check file format and corruption"
            ))
            return
        
        logger.info(f"Loaded NumPy array with shape: {data.shape}")
        
        # Check for NaN or infinite values
        nan_count = np.isnan(data).sum()
        inf_count = np.isinf(data).sum()
        
        if nan_count > 0:
            self.issues.append(DataQualityIssue(
                issue_type="missing_values",
                severity="major",
                description=f"Found {nan_count} NaN values in array",
                affected_samples=nan_count,
                auto_fixable=True,
                suggested_fix="Replace NaN values with mean/median or remove affected samples"
            ))
        
        if inf_count > 0:
            self.issues.append(DataQualityIssue(
                issue_type="infinite_values",
                severity="major",
                description=f"Found {inf_count} infinite values in array",
                affected_samples=inf_count,
                auto_fixable=True,
                suggested_fix="Replace infinite values with finite bounds or remove affected samples"
            ))
        
        # Check for extreme values
        if data.size > 0:
            q1, q3 = np.percentile(data.flatten(), [25, 75])
            iqr = q3 - q1
            lower_bound = q1 - 3 * iqr
            upper_bound = q3 + 3 * iqr
            
            extreme_count = np.sum((data < lower_bound) | (data > upper_bound))
            if extreme_count > 0:
                self.issues.append(DataQualityIssue(
                    issue_type="extreme_values",
                    severity="minor",
                    description=f"Found {extreme_count} extreme values (outliers)",
                    affected_samples=extreme_count,
                    auto_fixable=True,
                    suggested_fix="Consider outlier removal or transformation"
                ))
    
    def _check_json_quality(self, path: Path):
        """Check JSON data quality"""
        try:
            with open(path, 'r') as f:
                data = json.load(f)
        except Exception as e:
            self.issues.append(DataQualityIssue(
                issue_type="file_read_error",
                severity="critical",
                description=f"Cannot load JSON file: {str(e)}",
                affected_samples=0,
                auto_fixable=False,
                suggested_fix="Check JSON syntax and file encoding"
            ))
            return
        
        # Check structure consistency
        if isinstance(data, list) and len(data) > 0:
            # Check for consistent keys in list of dicts
            if isinstance(data[0], dict):
                keys = set(data[0].keys())
                inconsistent_records = 0
                
                for record in data[1:min(100, len(data))]:  # Sample first 100
                    if isinstance(record, dict) and set(record.keys()) != keys:
                        inconsistent_records += 1
                
                if inconsistent_records > 0:
                    self.issues.append(DataQualityIssue(
                        issue_type="inconsistent_structure",
                        severity="major",
                        description=f"Found {inconsistent_records} records with inconsistent structure",
                        affected_samples=inconsistent_records,
                        auto_fixable=True,
                        suggested_fix="Standardize record structure or filter inconsistent records"
                    ))
    
    def _check_corrupted_images(self, image_files: List[Path]):
        """Check for corrupted image files"""
        corrupted_count = 0
        total_checked = min(100, len(image_files))  # Sample first 100
        
        for img_file in image_files[:total_checked]:
            try:
                with Image.open(img_file) as img:
                    img.verify()
            except Exception:
                corrupted_count += 1
        
        if corrupted_count > 0:
            estimated_total = int(corrupted_count * len(image_files) / total_checked)
            self.issues.append(DataQualityIssue(
                issue_type="corrupted_files",
                severity="critical",
                description=f"Found {corrupted_count} corrupted images in sample (estimated {estimated_total} total)",
                affected_samples=estimated_total,
                auto_fixable=True,
                suggested_fix="Remove corrupted images and re-download if possible"
            ))
    
    def _check_image_dimensions(self, image_files: List[Path]):
        """Check for inconsistent image dimensions"""
        dimensions = {}
        sample_size = min(50, len(image_files))
        
        for img_file in image_files[:sample_size]:
            try:
                with Image.open(img_file) as img:
                    size = img.size
                    dimensions[size] = dimensions.get(size, 0) + 1
            except Exception:
                continue
        
        if len(dimensions) > 3:  # Too many different sizes
            self.issues.append(DataQualityIssue(
                issue_type="inconsistent_dimensions",
                severity="minor",
                description=f"Found {len(dimensions)} different image dimensions",
                affected_samples=len(image_files),
                auto_fixable=True,
                suggested_fix="Resize images to consistent dimensions during preprocessing"
            ))
    
    def _check_class_distribution(self, data_path: Path, image_files: List[Path]):
        """Check for class imbalance in image dataset"""
        class_counts = {}
        
        for img_file in image_files:
            try:
                relative_path = img_file.relative_to(data_path)
                if len(relative_path.parts) > 1:
                    class_name = relative_path.parts[0]
                    class_counts[class_name] = class_counts.get(class_name, 0) + 1
            except Exception:
                continue
        
        if len(class_counts) > 1:
            counts = list(class_counts.values())
            min_count = min(counts)
            max_count = max(counts)
            imbalance_ratio = min_count / max_count
            
            if imbalance_ratio < 0.1:  # Severe imbalance
                severity = "major"
                description = f"Severe class imbalance detected (ratio: {imbalance_ratio:.2f})"
            elif imbalance_ratio < 0.3:  # Moderate imbalance
                severity = "minor"
                description = f"Moderate class imbalance detected (ratio: {imbalance_ratio:.2f})"
            else:
                return
            
            self.issues.append(DataQualityIssue(
                issue_type="class_imbalance",
                severity=severity,
                description=description,
                affected_samples=len(image_files),
                auto_fixable=True,
                suggested_fix="Apply data augmentation, resampling, or weighted loss functions"
            ))
    
    def _check_duplicate_images(self, image_files: List[Path]):
        """Check for duplicate images using hash"""
        hashes = {}
        duplicates = 0
        sample_size = min(100, len(image_files))
        
        for img_file in image_files[:sample_size]:
            try:
                with Image.open(img_file) as img:
                    # Create hash of image content
                    img_hash = hashlib.md5(img.tobytes()).hexdigest()
                    if img_hash in hashes:
                        duplicates += 1
                    else:
                        hashes[img_hash] = img_file
            except Exception:
                continue
        
        if duplicates > 0:
            estimated_total = int(duplicates * len(image_files) / sample_size)
            self.issues.append(DataQualityIssue(
                issue_type="duplicate_images",
                severity="minor",
                description=f"Found {duplicates} duplicate images in sample (estimated {estimated_total} total)",
                affected_samples=estimated_total,
                auto_fixable=True,
                suggested_fix="Remove duplicate images to prevent overfitting"
            ))
    
    def _check_image_formats(self, image_files: List[Path]):
        """Check for inconsistent image formats"""
        formats = {}
        
        for img_file in image_files[:min(100, len(image_files))]:
            ext = img_file.suffix.lower()
            formats[ext] = formats.get(ext, 0) + 1
        
        if len(formats) > 2:  # More than 2 formats
            self.issues.append(DataQualityIssue(
                issue_type="inconsistent_formats",
                severity="minor",
                description=f"Found {len(formats)} different image formats",
                affected_samples=len(image_files),
                auto_fixable=True,
                suggested_fix="Convert images to consistent format during preprocessing"
            ))
    
    def _check_file_naming(self, image_files: List[Path]):
        """Check for file naming issues"""
        issues_found = 0
        
        for img_file in image_files[:min(50, len(image_files))]:
            filename = img_file.name
            
            # Check for spaces
            if ' ' in filename:
                issues_found += 1
            
            # Check for special characters
            special_chars = set('!@#$%^&*()+=[]{}|;:,.<>?')
            if any(char in filename for char in special_chars):
                issues_found += 1
        
        if issues_found > 0:
            self.issues.append(DataQualityIssue(
                issue_type="naming_issues",
                severity="minor",
                description=f"Found {issues_found} files with naming issues (spaces, special characters)",
                affected_samples=len(image_files),
                auto_fixable=True,
                suggested_fix="Rename files to use only alphanumeric characters and underscores"
            ))
    
    def _check_missing_values(self, df: pd.DataFrame):
        """Check for missing values in DataFrame"""
        missing_counts = df.isnull().sum()
        total_missing = missing_counts.sum()
        
        if total_missing > 0:
            missing_percentage = (total_missing / (df.shape[0] * df.shape[1])) * 100
            
            if missing_percentage > 20:
                severity = "major"
            elif missing_percentage > 5:
                severity = "minor"
            else:
                severity = "minor"
            
            # Find columns with most missing values
            worst_columns = missing_counts.nlargest(3)
            worst_cols_str = ", ".join([f"{col} ({count})" for col, count in worst_columns.items()])
            
            self.issues.append(DataQualityIssue(
                issue_type="missing_values",
                severity=severity,
                description=f"Found {total_missing} missing values ({missing_percentage:.1f}% of dataset). Worst columns: {worst_cols_str}",
                affected_samples=total_missing,
                affected_features=list(missing_counts[missing_counts > 0].index),
                auto_fixable=True,
                suggested_fix="Use imputation (mean/median for numeric, mode for categorical) or remove affected rows/columns"
            ))
    
    def _check_duplicate_rows(self, df: pd.DataFrame):
        """Check for duplicate rows"""
        duplicate_count = df.duplicated().sum()
        
        if duplicate_count > 0:
            duplicate_percentage = (duplicate_count / len(df)) * 100
            
            if duplicate_percentage > 10:
                severity = "major"
            elif duplicate_percentage > 1:
                severity = "minor"
            else:
                severity = "minor"
            
            self.issues.append(DataQualityIssue(
                issue_type="duplicate_rows",
                severity=severity,
                description=f"Found {duplicate_count} duplicate rows ({duplicate_percentage:.1f}% of dataset)",
                affected_samples=duplicate_count,
                auto_fixable=True,
                suggested_fix="Remove duplicate rows to prevent overfitting"
            ))
    
    def _check_data_types(self, df: pd.DataFrame):
        """Check for data type inconsistencies"""
        mixed_type_columns = []
        
        for col in df.columns:
            # Check if column contains mixed types
            col_data = df[col].dropna()
            if len(col_data) > 0:
                types = set(type(x).__name__ for x in col_data)
                if len(types) > 2:  # More than 2 different types
                    mixed_type_columns.append(col)
        
        if mixed_type_columns:
            self.issues.append(DataQualityIssue(
                issue_type="mixed_data_types",
                severity="major",
                description=f"Found {len(mixed_type_columns)} columns with mixed data types",
                affected_samples=len(df),
                affected_features=mixed_type_columns,
                auto_fixable=True,
                suggested_fix="Convert columns to consistent data types"
            ))
    
    def _check_outliers(self, df: pd.DataFrame):
        """Check for outliers in numeric columns"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        outlier_info = []
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                Q1 = col_data.quantile(0.25)
                Q3 = col_data.quantile(0.75)
                IQR = Q3 - Q1
                
                lower_bound = Q1 - 1.5 * IQR
                upper_bound = Q3 + 1.5 * IQR
                
                outliers = col_data[(col_data < lower_bound) | (col_data > upper_bound)]
                outlier_count = len(outliers)
                
                if outlier_count > 0:
                    outlier_percentage = (outlier_count / len(col_data)) * 100
                    outlier_info.append(f"{col}: {outlier_count} ({outlier_percentage:.1f}%)")
        
        if outlier_info:
            self.issues.append(DataQualityIssue(
                issue_type="outliers",
                severity="minor",
                description=f"Found outliers in columns: {', '.join(outlier_info)}",
                affected_samples=len(df),
                affected_features=[info.split(':')[0] for info in outlier_info],
                auto_fixable=True,
                suggested_fix="Consider outlier removal, transformation, or robust modeling techniques"
            ))
    
    def _check_target_distribution(self, df: pd.DataFrame):
        """Check target variable distribution for classification tasks"""
        target_col = df.columns[-1]  # Assume last column is target
        target_data = df[target_col].dropna()
        
        if target_data.dtype == 'object' or target_data.nunique() < 20:
            # Classification task
            value_counts = target_data.value_counts()
            min_count = value_counts.min()
            max_count = value_counts.max()
            imbalance_ratio = min_count / max_count
            
            if imbalance_ratio < 0.1:
                severity = "major"
                description = f"Severe class imbalance in target '{target_col}' (ratio: {imbalance_ratio:.2f})"
            elif imbalance_ratio < 0.3:
                severity = "minor"
                description = f"Moderate class imbalance in target '{target_col}' (ratio: {imbalance_ratio:.2f})"
            else:
                return
            
            self.issues.append(DataQualityIssue(
                issue_type="class_imbalance",
                severity=severity,
                description=description,
                affected_samples=len(df),
                affected_features=[target_col],
                auto_fixable=True,
                suggested_fix="Apply class weighting, resampling, or stratified sampling"
            ))
    
    def _check_feature_correlation(self, df: pd.DataFrame):
        """Check for highly correlated features"""
        numeric_df = df.select_dtypes(include=[np.number])
        
        if len(numeric_df.columns) < 2:
            return
        
        corr_matrix = numeric_df.corr()
        high_corr_pairs = []
        
        for i in range(len(corr_matrix.columns)):
            for j in range(i+1, len(corr_matrix.columns)):
                corr_value = abs(corr_matrix.iloc[i, j])
                if corr_value > 0.95:  # Very high correlation
                    high_corr_pairs.append((corr_matrix.columns[i], corr_matrix.columns[j], corr_value))
        
        if high_corr_pairs:
            corr_desc = ", ".join([f"{col1}-{col2} ({corr:.2f})" for col1, col2, corr in high_corr_pairs[:3]])
            self.issues.append(DataQualityIssue(
                issue_type="high_correlation",
                severity="minor",
                description=f"Found {len(high_corr_pairs)} highly correlated feature pairs (|r| > 0.95): {corr_desc}",
                affected_samples=len(df),
                affected_features=list(set([col for pair in high_corr_pairs for col in pair[:2]])),
                auto_fixable=True,
                suggested_fix="Consider feature selection or dimensionality reduction"
            ))
    
    def _check_constant_features(self, df: pd.DataFrame):
        """Check for constant features"""
        constant_cols = []
        for col in df.columns:
            if df[col].nunique() == 1:
                constant_cols.append(col)
        
        if constant_cols:
            self.issues.append(DataQualityIssue(
                issue_type="constant_features",
                severity="minor",
                description=f"Found {len(constant_cols)} constant features: {', '.join(constant_cols)}",
                affected_samples=len(df),
                affected_features=constant_cols,
                auto_fixable=True,
                suggested_fix="Remove constant features as they provide no information"
            ))
    
    def _check_data_ranges(self, df: pd.DataFrame):
        """Check for data range issues"""
        numeric_cols = df.select_dtypes(include=[np.number]).columns
        
        for col in numeric_cols:
            col_data = df[col].dropna()
            if len(col_data) > 0:
                min_val = col_data.min()
                max_val = col_data.max()
                
                # Check for extreme ranges
                data_range = max_val - min_val
                if data_range > 1e6:
                    self.issues.append(DataQualityIssue(
                        issue_type="extreme_range",
                        severity="minor",
                        description=f"Column '{col}' has extreme range: [{min_val:.2e}, {max_val:.2e}]",
                        affected_samples=len(df),
                        affected_features=[col],
                        auto_fixable=True,
                        suggested_fix="Consider standardization or log transformation"
                    ))
                
                # Check for negative values in what should be positive features
                if min_val < 0 and col.lower() in ['age', 'count', 'size', 'length', 'width', 'height']:
                    negative_count = (col_data < 0).sum()
                    if negative_count > 0:
                        self.issues.append(DataQualityIssue(
                            issue_type="invalid_negative_values",
                            severity="major",
                            description=f"Column '{col}' contains {negative_count} negative values",
                            affected_samples=negative_count,
                            affected_features=[col],
                            auto_fixable=True,
                            suggested_fix="Investigate and correct invalid negative values"
                        ))
    
    def _check_generic_quality(self, path: Path):
        """Generic quality checks for unknown data types"""
        # Check file size
        if path.is_file():
            file_size = path.stat().st_size
            if file_size == 0:
                self.issues.append(DataQualityIssue(
                    issue_type="empty_file",
                    severity="critical",
                    description="File is empty (0 bytes)",
                    affected_samples=1,
                    auto_fixable=False,
                    suggested_fix="Check file integrity and re-upload"
                ))
            elif file_size > 1e9:  # > 1GB
                self.issues.append(DataQualityIssue(
                    issue_type="large_file",
                    severity="minor",
                    description=f"Large file detected ({file_size / 1e9:.1f} GB)",
                    affected_samples=1,
                    auto_fixable=False,
                    suggested_fix="Consider data sampling or chunking for large files"
                ))
    
    def _generate_quality_report(self) -> DataQualityReport:
        """Generate comprehensive quality report"""
        # Categorize issues by severity
        critical_issues = [issue for issue in self.issues if issue.severity == 'critical']
        major_issues = [issue for issue in self.issues if issue.severity == 'major']
        minor_issues = [issue for issue in self.issues if issue.severity == 'minor']
        
        # Calculate overall score (0-100)
        base_score = 100.0
        
        # Deduct points for issues
        score_penalties = {
            'critical': 20.0,
            'major': 10.0,
            'minor': 2.0
        }
        
        for issue in self.issues:
            base_score -= score_penalties.get(issue.severity, 0.0)
        
        overall_score = max(0.0, base_score)
        
        # Generate recommendations
        recommendations = self._generate_recommendations()
        
        return DataQualityReport(
            total_issues=len(self.issues),
            critical_issues=len(critical_issues),
            major_issues=len(major_issues),
            minor_issues=len(minor_issues),
            overall_score=overall_score,
            issues=self.issues,
            recommendations=recommendations,
            auto_fix_summary={}
        )
    
    def _generate_recommendations(self) -> List[str]:
        """Generate actionable recommendations based on detected issues"""
        recommendations = []
        
        # Critical issues
        critical_issues = [issue for issue in self.issues if issue.severity == 'critical']
        if critical_issues:
            recommendations.append("🚨 CRITICAL: Address critical issues before training to prevent failures")
            for issue in critical_issues:
                recommendations.append(f"   • {issue.description}")
        
        # Major issues
        major_issues = [issue for issue in self.issues if issue.severity == 'major']
        if major_issues:
            recommendations.append("⚠️  MAJOR: Fix major issues to significantly improve model performance")
            for issue in major_issues[:3]:  # Show top 3
                recommendations.append(f"   • {issue.description}")
        
        # Minor issues
        minor_issues = [issue for issue in self.issues if issue.severity == 'minor']
        if minor_issues:
            recommendations.append("💡 MINOR: Consider fixing minor issues for optimal results")
            for issue in minor_issues[:2]:  # Show top 2
                recommendations.append(f"   • {issue.description}")
        
        # General recommendations
        if not recommendations:
            recommendations.append("✅ No significant quality issues detected. Dataset is ready for training!")
        
        recommendations.append("📊 Always validate model performance on a held-out test set")
        recommendations.append("🔍 Monitor training metrics to detect potential data quality issues")
        
        return recommendations
    
    def _auto_fix_issues(self, data_path: str, data_type: str) -> Dict[str, Any]:
        """Automatically fix issues where possible"""
        logger.info("Attempting automatic fixes...")
        
        fix_results = {
            'issues_fixed': 0,
            'issues_remaining': len(self.issues),
            'fixes_applied': [],
            'warnings': []
        }
        
        # Only attempt fixes for auto-fixable issues
        fixable_issues = [issue for issue in self.issues if issue.auto_fixable]
        
        if data_type == 'csv':
            try:
                df = pd.read_csv(data_path)
                original_shape = df.shape
                
                # Apply fixes
                df_fixed = self._apply_csv_fixes(df, fixable_issues)
                
                # Save fixed data
                if df_fixed.shape != original_shape or not df_fixed.equals(df):
                    fixed_path = str(data_path).replace('.csv', '_fixed.csv')
                    df_fixed.to_csv(fixed_path, index=False)
                    fix_results['fixes_applied'].append(f"Saved fixed data to: {fixed_path}")
                    fix_results['issues_fixed'] = len([issue for issue in fixable_issues if issue.severity != 'critical'])
                
            except Exception as e:
                fix_results['warnings'].append(f"Could not apply CSV fixes: {str(e)}")
        
        fix_results['issues_remaining'] = len(self.issues) - fix_results['issues_fixed']
        
        logger.info(f"Fixed {fix_results['issues_fixed']} issues, {fix_results['issues_remaining']} remaining")
        return fix_results
    
    def _apply_csv_fixes(self, df: pd.DataFrame, issues: List[DataQualityIssue]) -> pd.DataFrame:
        """Apply automatic fixes to CSV data"""
        df_fixed = df.copy()
        
        for issue in issues:
            if issue.severity == 'critical':
                continue  # Don't auto-fix critical issues
            
            if issue.issue_type == "missing_values":
                # Simple imputation for numeric columns
                numeric_cols = df_fixed.select_dtypes(include=[np.number]).columns
                for col in numeric_cols:
                    if df_fixed[col].isnull().sum() > 0:
                        df_fixed[col].fillna(df_fixed[col].median(), inplace=True)
            
            elif issue.issue_type == "duplicate_rows":
                df_fixed = df_fixed.drop_duplicates()
            
            elif issue.issue_type == "constant_features":
                # Remove constant features
                for col in issue.affected_features:
                    if col in df_fixed.columns:
                        df_fixed = df_fixed.drop(columns=[col])
            
            elif issue.issue_type == "mixed_data_types":
                # Try to convert to numeric where possible
                for col in issue.affected_features:
                    if col in df_fixed.columns:
                        try:
                            df_fixed[col] = pd.to_numeric(df_fixed[col], errors='coerce')
                        except Exception:
                            pass
        
        return df_fixed

def create_quality_visualization(report: DataQualityReport, output_path: str = "data_quality_report.png"):
    """Create visualization of data quality issues"""
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(15, 12))
    
    # Issue severity distribution
    severities = ['Critical', 'Major', 'Minor']
    counts = [report.critical_issues, report.major_issues, report.minor_issues]
    colors = ['red', 'orange', 'yellow']
    
    ax1.pie(counts, labels=severities, colors=colors, autopct='%1.1f%%', startangle=90)
    ax1.set_title('Issue Severity Distribution')
    
    # Overall quality score
    ax2.bar(['Overall Score'], [report.overall_score], color='green' if report.overall_score > 80 else 'orange' if report.overall_score > 60 else 'red')
    ax2.set_ylim(0, 100)
    ax2.set_ylabel('Quality Score')
    ax2.set_title(f'Overall Quality Score: {report.overall_score:.1f}/100')
    
    # Issue types (top 5)
    issue_types = {}
    for issue in report.issues:
        issue_types[issue.issue_type] = issue_types.get(issue.issue_type, 0) + 1
    
    top_issues = dict(sorted(issue_types.items(), key=lambda x: x[1], reverse=True)[:5])
    
    ax3.barh(list(top_issues.keys()), list(top_issues.values()))
    ax3.set_xlabel('Number of Issues')
    ax3.set_title('Top Issue Types')
    
    # Recommendations (text)
    ax4.axis('off')
    recommendations_text = "\n".join(report.recommendations[:8])  # Top 8 recommendations
    ax4.text(0.05, 0.95, "Key Recommendations:\n\n" + recommendations_text, 
             transform=ax4.transAxes, fontsize=10, verticalalignment='top',
             bbox=dict(boxstyle="round,pad=0.3", facecolor="lightblue", alpha=0.5))
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    logger.info(f"Quality visualization saved to: {output_path}")

# Integration function for AxoLexis
def run_intelligent_quality_check(data_path: str, auto_fix: bool = True, create_visualization: bool = True) -> Dict[str, Any]:
    """Run intelligent data quality check for AxoLexis"""
    
    print("🔍 Running Intelligent Data Quality Assessment...")
    print("="*60)
    
    # Create quality checker
    checker = IntelligentDataQualityChecker()
    
    # Run comprehensive check
    try:
        report = checker.comprehensive_quality_check(data_path, auto_fix=auto_fix)
        
        # Print summary
        print(f"📊 Quality Assessment Complete!")
        print(f"   Overall Score: {report.overall_score:.1f}/100")
        print(f"   Total Issues: {report.total_issues}")
        print(f"   Critical: {report.critical_issues} | Major: {report.major_issues} | Minor: {report.minor_issues}")
        
        if report.issues:
            print(f"\n🚨 Top Issues:")
            for i, issue in enumerate(report.issues[:5], 1):
                print(f"   {i}. [{issue.severity.upper()}] {issue.description}")
        
        print(f"\n💡 Key Recommendations:")
        for i, rec in enumerate(report.recommendations[:3], 1):
            print(f"   {i}. {rec}")
        
        # Create visualization if requested
        if create_visualization:
            viz_path = "data_quality_report.png"
            create_quality_visualization(report, viz_path)
            print(f"\n📈 Quality visualization saved to: {viz_path}")
        
        # Return comprehensive results
        return {
            'quality_score': report.overall_score,
            'issues_found': report.total_issues,
            'critical_issues': report.critical_issues,
            'major_issues': report.major_issues,
            'minor_issues': report.minor_issues,
            'data_ready_for_training': report.overall_score > 70 and report.critical_issues == 0,
            'recommendations': report.recommendations,
            'detailed_report': report,
            'auto_fix_results': report.auto_fix_summary if auto_fix else None
        }
        
    except Exception as e:
        logger.error(f"Quality check failed: {e}")
        return {
            'error': str(e),
            'quality_score': 0,
            'data_ready_for_training': False,
            'recommendations': [f"Error during quality check: {str(e)}"]
        }

if __name__ == "__main__":
    # Test the quality checker
    print("🧪 Testing Intelligent Data Quality Checker")
    print("="*50)
    
    # Create test CSV with various issues
    test_data_path = "test_quality_data.csv"
    np.random.seed(42)
    
    # Create data with intentional issues
    n_samples = 1000
    n_features = 10
    
    # Generate features
    X = np.random.randn(n_samples, n_features)
    
    # Add some missing values
    missing_mask = np.random.random((n_samples, n_features)) < 0.05  # 5% missing
    X[missing_mask] = np.nan
    
    # Add some outliers
    outlier_indices = np.random.choice(n_samples, size=50, replace=False)
    X[outlier_indices, 0] = X[outlier_indices, 0] * 10  # Make outliers
    
    # Create target with class imbalance
    y = np.random.choice([0, 1, 2], size=n_samples, p=[0.7, 0.2, 0.1])  # Imbalanced
    
    # Create DataFrame
    feature_names = [f"feature_{i}" for i in range(n_features)]
    df = pd.DataFrame(X, columns=feature_names)
    df["target"] = y
    
    # Add duplicate rows
    duplicate_indices = np.random.choice(df.index, size=50, replace=False)
    df = pd.concat([df, df.loc[duplicate_indices]], ignore_index=True)
    
    # Add constant feature
    df["constant_feature"] = 42
    
    # Save to CSV
    df.to_csv(test_data_path, index=False)
    print(f"✅ Created test data with intentional quality issues: {test_data_path}")
    
    # Run quality check
    results = run_intelligent_quality_check(test_data_path, auto_fix=True)
    
    # Clean up
    if os.path.exists(test_data_path):
        os.remove(test_data_path)
        print(f"🧹 Cleaned up test file: {test_data_path}")
    
    print("\n" + "="*50)
    print("Quality check completed successfully!")