"""
Comprehensive Logging & Transparency System for AxoLexis
Provides real-time logging, model transparency, and training visibility
"""

import os
import json
import logging
import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from PyQt6.QtCore import QObject, pyqtSignal, QTimer
from PyQt6.QtWidgets import QTextEdit, QDialog, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QTabWidget, QTableWidget, QTableWidgetItem
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

logger = logging.getLogger(__name__)

class TrainingTransparencyLogger(QObject):
    """Comprehensive logging system for training transparency"""
    
    # Signals for real-time updates
    log_entry_added = pyqtSignal(str, str)  # message, level
    training_step_completed = pyqtSignal(dict)  # step metrics
    model_configuration_changed = pyqtSignal(dict)  # config changes
    intelligent_feature_activated = pyqtSignal(str, dict)  # feature, details
    
    def __init__(self, log_dir: str = "./training_logs"):
        super().__init__()
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Training state tracking
        self.training_history = []
        self.model_configs = []
        self.intelligent_features_used = []
        self.optimization_history = []
        self.performance_metrics = []
        
        # Current training session
        self.current_session = {
            "start_time": None,
            "end_time": None,
            "model_name": None,
            "task_domain": None,
            "task_type": None,
            "data_path": None,
            "total_epochs": 0,
            "current_epoch": 0,
            "best_accuracy": 0.0,
            "final_accuracy": 0.0,
            "training_time": 0,
            "intelligent_features": [],
            "optimizations_applied": []
        }
        
        # Setup file logging
        self._setup_file_logging()
        
        # Real-time logging timer
        self.log_timer = QTimer()
        self.log_timer.timeout.connect(self._flush_logs)
        self.log_timer.start(5000)  # Flush every 5 seconds

    def _setup_file_logging(self):
        """Setup file-based logging"""
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = self.log_dir / f"training_session_{timestamp}.log"
        
        # Create file handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        file_handler.setFormatter(formatter)
        
        # Add to logger
        logger.addHandler(file_handler)
        
        # Store log file path
        self.current_log_file = log_file

    def start_training_session(self, model_name: str, task_domain: str, task_type: str, data_path: str):
        """Start a new training session"""
        self.current_session = {
            "start_time": datetime.datetime.now(),
            "end_time": None,
            "model_name": model_name,
            "task_domain": task_domain,
            "task_type": task_type,
            "data_path": data_path,
            "total_epochs": 0,
            "current_epoch": 0,
            "best_accuracy": 0.0,
            "final_accuracy": 0.0,
            "training_time": 0,
            "intelligent_features": [],
            "optimizations_applied": []
        }
        
        self.log_training_event("Training session started", "info", {
            "model": model_name,
            "task": f"{task_domain} - {task_type}",
            "data": data_path
        })

    def end_training_session(self, final_accuracy: float, total_time: float):
        """End the current training session"""
        self.current_session["end_time"] = datetime.datetime.now()
        self.current_session["final_accuracy"] = final_accuracy
        self.current_session["training_time"] = total_time
        
        self.log_training_event("Training session completed", "success", {
            "final_accuracy": final_accuracy,
            "training_time": total_time,
            "intelligent_features_used": len(self.current_session["intelligent_features"]),
            "optimizations_applied": len(self.current_session["optimizations_applied"])
        })
        
        # Save session summary
        self._save_session_summary()

    def log_training_step(self, epoch: int, step: int, metrics: Dict[str, float]):
        """Log a training step with metrics"""
        self.current_session["current_epoch"] = epoch
        
        # Update best accuracy
        if "accuracy" in metrics and metrics["accuracy"] > self.current_session["best_accuracy"]:
            self.current_session["best_accuracy"] = metrics["accuracy"]
        
        # Store step data
        step_data = {
            "timestamp": datetime.datetime.now(),
            "epoch": epoch,
            "step": step,
            "metrics": metrics.copy()
        }
        self.training_history.append(step_data)
        
        # Emit signal for UI updates
        self.training_step_completed.emit(metrics)
        
        # Log significant events
        if step == 0 and epoch == 0:
            self.log_training_event("First training step completed", "info", metrics)
        elif "accuracy" in metrics and metrics["accuracy"] > 0.9:
            self.log_training_event("High accuracy achieved", "success", {"accuracy": metrics["accuracy"]})

    def log_model_configuration(self, config: Dict[str, Any]):
        """Log model configuration changes"""
        config_entry = {
            "timestamp": datetime.datetime.now(),
            "config": config.copy()
        }
        self.model_configs.append(config_entry)
        
        self.model_configuration_changed.emit(config)
        
        self.log_training_event("Model configuration updated", "info", {
            "model_tier": config.get("model_tier", "unknown"),
            "task": config.get("task", "unknown"),
            "batch_size": config.get("batch_size", "unknown"),
            "learning_rate": config.get("base_lr", "unknown")
        })

    def log_intelligent_feature(self, feature_name: str, details: Dict[str, Any]):
        """Log intelligent feature activation"""
        feature_entry = {
            "timestamp": datetime.datetime.now(),
            "feature": feature_name,
            "details": details.copy()
        }
        self.intelligent_features_used.append(feature_entry)
        
        if feature_name not in self.current_session["intelligent_features"]:
            self.current_session["intelligent_features"].append(feature_name)
        
        self.intelligent_feature_activated.emit(feature_name, details)
        
        self.log_training_event(f"Intelligent feature activated: {feature_name}", "info", details)

    def log_optimization(self, optimization_type: str, old_value: Any, new_value: Any, reason: str):
        """Log optimization applied during training"""
        optimization_entry = {
            "timestamp": datetime.datetime.now(),
            "type": optimization_type,
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        }
        self.optimization_history.append(optimization_entry)
        
        if optimization_type not in self.current_session["optimizations_applied"]:
            self.current_session["optimizations_applied"].append(optimization_type)
        
        self.log_training_event(f"Optimization applied: {optimization_type}", "info", {
            "old_value": old_value,
            "new_value": new_value,
            "reason": reason
        })

    def log_training_event(self, message: str, level: str = "info", data: Optional[Dict] = None):
        """Log a general training event"""
        log_entry = {
            "timestamp": datetime.datetime.now(),
            "message": message,
            "level": level,
            "data": data or {}
        }
        
        # Add to training history
        self.training_history.append(log_entry)
        
        # Emit signal for UI
        self.log_entry_added.emit(message, level)
        
        # Log to file
        if level == "error":
            logger.error(f"{message} - Data: {data}")
        elif level == "warning":
            logger.warning(f"{message} - Data: {data}")
        elif level == "success":
            logger.info(f"{message} - Data: {data}")
        else:
            logger.info(f"{message} - Data: {data}")

    def log_model_selection(self, selected_model: str, reasoning: str, alternatives: List[str]):
        """Log intelligent model selection"""
        self.log_training_event("Intelligent model selection completed", "info", {
            "selected_model": selected_model,
            "reasoning": reasoning,
            "alternatives_considered": alternatives
        })

    def log_data_quality_assessment(self, quality_score: float, issues_found: int, critical_issues: int):
        """Log data quality assessment results"""
        level = "error" if critical_issues > 0 else "warning" if issues_found > 0 else "success"
        
        self.log_training_event("Data quality assessment completed", level, {
            "quality_score": quality_score,
            "total_issues": issues_found,
            "critical_issues": critical_issues
        })

    def get_training_summary(self) -> Dict[str, Any]:
        """Get comprehensive training summary"""
        return {
            "session_info": self.current_session.copy(),
            "training_steps": len(self.training_history),
            "model_configs_applied": len(self.model_configs),
            "intelligent_features_used": len(self.intelligent_features_used),
            "optimizations_applied": len(self.optimization_history),
            "log_file": str(self.current_log_file) if hasattr(self, 'current_log_file') else None
        }

    def get_performance_report(self) -> Dict[str, Any]:
        """Get detailed performance report"""
        if not self.training_history:
            return {"error": "No training data available"}
        
        # Extract metrics from training history
        accuracies = []
        losses = []
        learning_rates = []
        
        for entry in self.training_history:
            if "metrics" in entry:
                metrics = entry["metrics"]
                if "accuracy" in metrics:
                    accuracies.append(metrics["accuracy"])
                if "loss" in metrics:
                    losses.append(metrics["loss"])
                if "learning_rate" in metrics:
                    learning_rates.append(metrics["learning_rate"])
        
        report = {
            "total_steps": len(self.training_history),
            "accuracy": {
                "final": accuracies[-1] if accuracies else 0,
                "best": max(accuracies) if accuracies else 0,
                "average": sum(accuracies) / len(accuracies) if accuracies else 0,
                "trend": "improving" if len(accuracies) > 1 and accuracies[-1] > accuracies[0] else "declining"
            },
            "loss": {
                "final": losses[-1] if losses else 0,
                "best": min(losses) if losses else 0,
                "average": sum(losses) / len(losses) if losses else 0
            },
            "training_efficiency": {
                "total_time": self.current_session.get("training_time", 0),
                "time_per_step": self.current_session.get("training_time", 0) / len(self.training_history) if self.training_history else 0,
                "convergence_speed": "fast" if len(accuracies) > 10 and accuracies[-1] > 0.8 else "slow"
            }
        }
        
        return report

    def _save_session_summary(self):
        """Save comprehensive session summary"""
        summary = {
            "session": self.current_session,
            "training_history": self.training_history,
            "model_configs": self.model_configs,
            "intelligent_features": self.intelligent_features_used,
            "optimizations": self.optimization_history,
            "performance_report": self.get_performance_report()
        }
        
        # Save to JSON file
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        summary_file = self.log_dir / f"training_summary_{timestamp}.json"
        
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2, default=str)
        
        self.log_training_event("Training summary saved", "info", {
            "summary_file": str(summary_file),
            "total_entries": len(self.training_history)
        })

    def _flush_logs(self):
        """Flush logs to file periodically"""
        # This method is called by the timer to ensure logs are written
        # In a real implementation, this would handle any buffered log entries
        pass

    def generate_training_visualization(self, output_path: str = "training_visualization.png"):
        """Generate comprehensive training visualization"""
        if not self.training_history:
            return None
        
        # Create figure with subplots
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        fig.suptitle('AxoLexis Training Transparency Report', fontsize=16, fontweight='bold')
        
        # Extract data for plotting
        epochs = [entry.get("epoch", i) for i, entry in enumerate(self.training_history)]
        steps = list(range(len(self.training_history)))
        
        # Accuracy plot
        accuracies = [entry.get("metrics", {}).get("accuracy", 0) for entry in self.training_history]
        if any(accuracies):
            ax1.plot(steps, accuracies, 'b-', label='Accuracy', linewidth=2)
            ax1.set_title('Training Accuracy Over Time')
            ax1.set_xlabel('Step')
            ax1.set_ylabel('Accuracy')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
        
        # Loss plot
        losses = [entry.get("metrics", {}).get("loss", 0) for entry in self.training_history]
        if any(losses):
            ax2.plot(steps, losses, 'r-', label='Loss', linewidth=2)
            ax2.set_title('Training Loss Over Time')
            ax2.set_xlabel('Step')
            ax2.set_ylabel('Loss')
            ax2.legend()
            ax2.grid(True, alpha=0.3)
        
        # Intelligent features usage
        if self.intelligent_features_used:
            feature_names = [entry["feature"] for entry in self.intelligent_features_used]
            feature_counts = pd.Series(feature_names).value_counts()
            
            ax3.bar(range(len(feature_counts)), feature_counts.values)
            ax3.set_title('Intelligent Features Used')
            ax3.set_xlabel('Feature')
            ax3.set_ylabel('Usage Count')
            ax3.set_xticks(range(len(feature_counts)))
            ax3.set_xticklabels(feature_counts.index, rotation=45, ha='right')
        
        # Training summary
        ax4.axis('off')
        summary_text = f"""
Training Summary:

Model: {self.current_session.get('model_name', 'Unknown')}
Task: {self.current_session.get('task_domain', 'Unknown')} - {self.current_session.get('task_type', 'Unknown')}

Total Steps: {len(self.training_history)}
Best Accuracy: {self.current_session.get('best_accuracy', 0):.3f}
Final Accuracy: {self.current_session.get('final_accuracy', 0):.3f}

Intelligent Features: {len(self.current_session.get('intelligent_features', []))}
Optimizations Applied: {len(self.current_session.get('optimizations_applied', []))}

Training Time: {self.current_session.get('training_time', 0):.1f} minutes
Log File: {self.current_log_file.name if hasattr(self, 'current_log_file') else 'Not available'}
"""
        
        ax4.text(0.1, 0.9, summary_text, transform=ax4.transAxes, fontsize=12,
                verticalalignment='top', bbox=dict(boxstyle="round,pad=0.5", facecolor="lightblue", alpha=0.8))
        
        plt.tight_layout()
        plt.savefig(output_path, dpi=300, bbox_inches='tight')
        plt.close()
        
        self.log_training_event("Training visualization generated", "info", {
            "output_file": output_path,
            "total_steps": len(self.training_history)
        })
        
        return output_path

class TransparencyDashboard(QDialog):
    """Dashboard for displaying training transparency information"""
    
    def __init__(self, transparency_logger: TrainingTransparencyLogger, parent=None):
        super().__init__(parent)
        self.transparency_logger = transparency_logger
        self.setWindowTitle("Training Transparency Dashboard")
        self.setMinimumSize(1000, 700)
        self._build_ui()
        
        # Connect to logger signals
        self.transparency_logger.log_entry_added.connect(self._on_log_entry)
        self.transparency_logger.training_step_completed.connect(self._on_training_step)
        self.transparency_logger.model_configuration_changed.connect(self._on_config_change)

    def _build_ui(self):
        layout = QVBoxLayout(self)
        
        # Title
        title = QLabel("Training Transparency Dashboard")
        title.setStyleSheet("font-size: 18pt; font-weight: bold; color: #5559A0;")
        layout.addWidget(title)
        
        # Tab widget for different views
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Real-time logs tab
        self.logs_text = QTextEdit()
        self.logs_text.setReadOnly(True)
        self.logs_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                color: #e0e0e0;
                border: 1px solid #333355;
                border-radius: 8px;
                padding: 10px;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 9pt;
            }
        """)
        self.tabs.addTab(self.logs_text, "Real-time Logs")
        
        # Model configuration tab
        self.config_table = QTableWidget()
        self.config_table.setColumnCount(3)
        self.config_table.setHorizontalHeaderLabels(["Timestamp", "Parameter", "Value"])
        self.tabs.addTab(self.config_table, "Model Configuration")
        
        # Performance metrics tab
        self.metrics_table = QTableWidget()
        self.metrics_table.setColumnCount(4)
        self.metrics_table.setHorizontalHeaderLabels(["Step", "Accuracy", "Loss", "Learning Rate"])
        self.tabs.addTab(self.metrics_table, "Performance Metrics")
        
        # Intelligent features tab
        self.features_table = QTableWidget()
        self.features_table.setColumnCount(3)
        self.features_table.setHorizontalHeaderLabels(["Timestamp", "Feature", "Details"])
        self.tabs.addTab(self.features_table, "Intelligent Features")
        
        # Control buttons
        button_layout = QHBoxLayout()
        
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.refresh_dashboard)
        button_layout.addWidget(refresh_btn)
        
        export_btn = QPushButton("Export Report")
        export_btn.clicked.connect(self.export_report)
        button_layout.addWidget(export_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)

    def _on_log_entry(self, message: str, level: str):
        """Handle new log entry"""
        color_map = {
            "error": "#ff5555",
            "warning": "#ffaa00", 
            "success": "#55ff55",
            "info": "#55aaff"
        }
        
        color = color_map.get(level, "#ffffff")
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        
        self.logs_text.append(f'<span style="color: {color}">[{timestamp}] {message}</span>')

    def _on_training_step(self, metrics: dict):
        """Handle training step completion"""
        # Add to metrics table
        row_count = self.metrics_table.rowCount()
        self.metrics_table.insertRow(row_count)
        
        self.metrics_table.setItem(row_count, 0, QTableWidgetItem(str(row_count)))
        self.metrics_table.setItem(row_count, 1, QTableWidgetItem(f"{metrics.get('accuracy', 0):.4f}"))
        self.metrics_table.setItem(row_count, 2, QTableWidgetItem(f"{metrics.get('loss', 0):.4f}"))
        self.metrics_table.setItem(row_count, 3, QTableWidgetItem(f"{metrics.get('learning_rate', 0):.2e}"))

    def _on_config_change(self, config: dict):
        """Handle model configuration change"""
        row_count = self.config_table.rowCount()
        self.config_table.insertRow(row_count)
        
        timestamp = datetime.datetime.now().strftime("%H:%M:%S")
        self.config_table.setItem(row_count, 0, QTableWidgetItem(timestamp))
        self.config_table.setItem(row_count, 1, QTableWidgetItem("Full Config"))
        self.config_table.setItem(row_count, 2, QTableWidgetItem(str(config)))

    def refresh_dashboard(self):
        """Refresh dashboard with current data"""
        # Get current summary
        summary = self.transparency_logger.get_training_summary()
        performance = self.transparency_logger.get_performance_report()
        
        self._on_log_entry(f"Dashboard refreshed - {summary['training_steps']} steps logged", "info")

    def export_report(self):
        """Export comprehensive transparency report"""
        try:
            # Generate visualization
            viz_path = "training_transparency_report.png"
            self.transparency_logger.generate_training_visualization(viz_path)
            
            # Get summary data
            summary = self.transparency_logger.get_training_summary()
            performance = self.transparency_logger.get_performance_report()
            
            # Create comprehensive report
            report = {
                "transparency_report": {
                    "generated_at": datetime.datetime.now().isoformat(),
                    "summary": summary,
                    "performance": performance,
                    "intelligent_features_used": self.transparency_logger.intelligent_features_used,
                    "optimizations_applied": self.transparency_logger.optimization_history
                }
            }
            
            # Save report
            report_path = "transparency_report.json"
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2, default=str)
            
            self._on_log_entry(f"Transparency report exported to {report_path} and {viz_path}", "success")
            
        except Exception as e:
            self._on_log_entry(f"Failed to export report: {str(e)}", "error")

# Integration function
def create_transparency_logger(log_dir: str = "./training_logs") -> TrainingTransparencyLogger:
    """Create and return transparency logger"""
    return TrainingTransparencyLogger(log_dir)

def create_transparency_dashboard(transparency_logger: TrainingTransparencyLogger, parent=None) -> TransparencyDashboard:
    """Create and return transparency dashboard"""
    return TransparencyDashboard(transparency_logger, parent)

if __name__ == "__main__":
    # Test the transparency system
    print("Testing Training Transparency System")
    
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
    print(f"\nVisualization saved to: {viz_path}")
    
    print("\nTransparency system test completed!")