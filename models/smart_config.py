"""
SHADA Smart Config Auto-Tuner — Automatically adjusts configuration
based on detected hardware, dataset characteristics, and training goals.

All recommendations derived from SHADA_Technical_Analysis.md
"""

import math
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class HardwareTier(Enum):
    CPU_ONLY = "cpu_only"
    ENTRY_GPU = "entry_gpu"      # < 8GB VRAM
    MID_GPU = "mid_gpu"          # 8-12GB VRAM
    HIGH_GPU = "high_gpu"        # 12-24GB VRAM
    ENTHUSIAST_GPU = "enthusiast_gpu"  # 24GB+ VRAM


class DatasetSize(Enum):
    TINY = "tiny"          # < 1K samples
    SMALL = "small"        # 1K - 10K samples
    MEDIUM = "medium"      # 10K - 100K samples
    LARGE = "large"        # 100K - 500K samples
    VERY_LARGE = "very_large"  # 500K+ samples


@dataclass
class SmartConfigRecommendation:
    """A single configuration change recommendation."""
    parameter: str
    old_value: Any
    new_value: Any
    reason: str
    md_reference: str
    priority: int  # 1 = highest priority


class SHADASmartConfig:
    """
    Intelligent configuration auto-tuner for SHADA algorithm.
    Analyzes hardware + dataset and produces optimized configuration.
    """

    def __init__(self):
        self.recommendations: list[SmartConfigRecommendation] = []

    def analyze_and_tune(
        self,
        config: dict,
        dataset_info: Optional[dict] = None,
        hardware_info: Optional[dict] = None,
        training_goal: str = "balanced"  # "balanced", "fast", "max_accuracy"
    ) -> Tuple[dict, list[SmartConfigRecommendation]]:
        """
        Analyze current config and produce optimized version.

        Args:
            config: Current SHADAConfig dict from UI
            dataset_info: Dataset metadata (num_samples, is_imbalanced, etc.)
            hardware_info: Hardware metadata (vram_gb, device, gpu_name)
            training_goal: User's priority ("balanced", "fast", "max_accuracy")

        Returns:
            Tuple of (optimized_config, list_of_recommendations)
        """
        self.recommendations = []
        optimized = config.copy()

        # Step 1: Detect hardware tier
        hw_tier = self._detect_hardware_tier(hardware_info)

        # Step 2: Detect dataset size category
        ds_size = self._detect_dataset_size(dataset_info)

        # Step 3: Apply hardware-specific optimizations
        self._apply_hardware_optimizations(optimized, hw_tier, hardware_info)

        # Step 4: Apply dataset-specific optimizations
        self._apply_dataset_optimizations(optimized, ds_size, dataset_info)

        # Step 5: Apply training goal optimizations
        self._apply_goal_optimizations(optimized, training_goal, hw_tier)

        # Step 6: Apply task-specific optimizations
        self._apply_task_optimizations(optimized, config.get("task", "classification"))

        # Step 7: Apply paradigm-specific optimizations
        self._apply_paradigm_optimizations(optimized, config.get("paradigm", "SHADA Pipeline"))

        return optimized, self.recommendations

    def _detect_hardware_tier(self, hardware_info: Optional[dict]) -> HardwareTier:
        if not hardware_info:
            return HardwareTier.MID_GPU  # Assume mid-range by default

        device = hardware_info.get("device", "cuda")
        vram_gb = hardware_info.get("vram_gb", 0)

        if device == "cpu" or vram_gb == 0:
            return HardwareTier.CPU_ONLY

        if vram_gb < 8:
            return HardwareTier.ENTRY_GPU
        elif vram_gb < 12:
            return HardwareTier.MID_GPU
        elif vram_gb < 24:
            return HardwareTier.HIGH_GPU
        else:
            return HardwareTier.ENTHUSIAST_GPU

    def _detect_dataset_size(self, dataset_info: Optional[dict]) -> DatasetSize:
        if not dataset_info:
            return DatasetSize.MEDIUM  # Assume medium by default

        num_samples = dataset_info.get("num_samples", 10000)

        if num_samples < 1000:
            return DatasetSize.TINY
        elif num_samples < 10000:
            return DatasetSize.SMALL
        elif num_samples < 100000:
            return DatasetSize.MEDIUM
        elif num_samples < 500000:
            return DatasetSize.LARGE
        else:
            return DatasetSize.VERY_LARGE

    def _add_recommendation(self, parameter: str, old_value: Any, new_value: Any,
                            reason: str, md_reference: str, priority: int = 2):
        if old_value != new_value:
            self.recommendations.append(SmartConfigRecommendation(
                parameter=parameter,
                old_value=old_value,
                new_value=new_value,
                reason=reason,
                md_reference=md_reference,
                priority=priority
            ))

    # ─────────────────────────────────────────────────────────────────────────
    # HARDWARE OPTIMIZATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_hardware_optimizations(self, config: dict, hw_tier: HardwareTier,
                                       hardware_info: Optional[dict]):
        """Apply optimizations based on hardware capabilities."""

        # Mixed precision settings
        if hw_tier == HardwareTier.CPU_ONLY:
            old = config.get("mixed_precision", "fp32")
            self._add_recommendation(
                parameter="mixed_precision",
                old_value=old,
                new_value="fp32",
                reason="CPU training requires full precision",
                md_reference="§15.1 Mixed-Precision Training",
                priority=1
            )
            config["mixed_precision"] = "fp32"

        elif hw_tier == HardwareTier.ENTRY_GPU:
            # < 8GB: aggressive memory saving
            old = config.get("mixed_precision", "fp32")
            if old != "bf16":
                self._add_recommendation(
                    parameter="mixed_precision",
                    old_value=old,
                    new_value="bf16",
                    reason="Entry GPU needs memory savings from mixed precision",
                    md_reference="§15.1 Mixed-Precision Training",
                    priority=1
                )
            config["mixed_precision"] = "bf16"

            # Gradient accumulation for larger effective batch
            old_acc = config.get("gradient_accumulation_steps", 1)
            if old_acc < 4:
                self._add_recommendation(
                    parameter="gradient_accumulation_steps",
                    old_value=old_acc,
                    new_value=4,
                    reason="Entry GPU: accumulate gradients to simulate larger batch",
                    md_reference="§15.2 Gradient Accumulation",
                    priority=2
                )
            config["gradient_accumulation_steps"] = 4

        elif hw_tier == HardwareTier.MID_GPU:
            # 8-12GB: balanced
            old = config.get("mixed_precision", "fp32")
            if old != "bf16":
                self._add_recommendation(
                    parameter="mixed_precision",
                    old_value=old,
                    new_value="bf16",
                    reason="Mid-range GPU benefits from 2-3× speedup with bf16",
                    md_reference="§15.1 Mixed-Precision Training",
                    priority=1
                )
            config["mixed_precision"] = "bf16"

            old_acc = config.get("gradient_accumulation_steps", 1)
            if old_acc < 2:
                self._add_recommendation(
                    parameter="gradient_accumulation_steps",
                    old_value=old_acc,
                    new_value=2,
                    reason="Mid GPU: moderate accumulation for stability",
                    md_reference="§15.2 Gradient Accumulation",
                    priority=2
                )
            config["gradient_accumulation_steps"] = 2

        elif hw_tier in [HardwareTier.HIGH_GPU, HardwareTier.ENTHUSIAST_GPU]:
            # 12GB+: can use larger batches
            old = config.get("mixed_precision", "fp32")
            if old != "bf16":
                self._add_recommendation(
                    parameter="mixed_precision",
                    old_value=old,
                    new_value="bf16",
                    reason="High-end GPU: bf16 for 2-3× throughput with full accuracy",
                    md_reference="§15.1 Mixed-Precision Training",
                    priority=1
                )
            config["mixed_precision"] = "bf16"

        # Batch size recommendations based on VRAM
        vram_gb = hardware_info.get("vram_gb", 0) if hardware_info else 0
        old_batch = config.get("batch_size", 16)

        if hw_tier == HardwareTier.ENTRY_GPU and old_batch > 16:
            self._add_recommendation(
                parameter="batch_size",
                old_value=old_batch,
                new_value=16,
                reason=f"Entry GPU ({vram_gb}GB VRAM): reduce batch to prevent OOM",
                md_reference="§15.2 Gradient Accumulation",
                priority=1
            )
            config["batch_size"] = 16

        elif hw_tier == HardwareTier.MID_GPU and old_batch < 32:
            self._add_recommendation(
                parameter="batch_size",
                old_value=old_batch,
                new_value=32,
                reason=f"Mid GPU ({vram_gb}GB VRAM): can handle batch=32",
                md_reference="§8.2 NT-Xent Contrastive Loss",
                priority=2
            )
            config["batch_size"] = 32

        elif hw_tier in [HardwareTier.HIGH_GPU, HardwareTier.ENTHUSIAST_GPU] and old_batch < 64:
            self._add_recommendation(
                parameter="batch_size",
                old_value=old_batch,
                new_value=64,
                reason=f"High-end GPU ({vram_gb}GB VRAM): can handle batch=64",
                md_reference="§8.2 NT-Xent Contrastive Loss",
                priority=2
            )
            config["batch_size"] = 64

        # Model tier recommendations
        model_tier = config.get("model_tier", "nano")
        if hw_tier == HardwareTier.ENTRY_GPU and model_tier in ["large", "xl"]:
            self._add_recommendation(
                parameter="model_tier",
                old_value=model_tier,
                new_value="base",
                reason=f"Entry GPU ({vram_gb}GB) cannot handle {model_tier} tier",
                md_reference="§1.1 Hierarchical Hybrid Encoder",
                priority=1
            )
            config["model_tier"] = "base"

        elif hw_tier == HardwareTier.CPU_ONLY and model_tier in ["base", "large", "xl"]:
            self._add_recommendation(
                parameter="model_tier",
                old_value=model_tier,
                new_value="nano",
                reason="CPU training: use smallest tier for reasonable speed",
                md_reference="§1.1 Hierarchical Hybrid Encoder",
                priority=1
            )
            config["model_tier"] = "nano"

    # ─────────────────────────────────────────────────────────────────────────
    # DATASET OPTIMIZATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_dataset_optimizations(self, config: dict, ds_size: DatasetSize,
                                      dataset_info: Optional[dict]):
        """Apply optimizations based on dataset characteristics."""

        # Model tier based on dataset size
        model_tier = config.get("model_tier", "nano")

        if ds_size == DatasetSize.TINY:
            if model_tier != "nano":
                self._add_recommendation(
                    parameter="model_tier",
                    old_value=model_tier,
                    new_value="nano",
                    reason="Tiny dataset (<1K): nano tier prevents overfitting",
                    md_reference="§1.1 + Data-Aware Recommendations",
                    priority=1
                )
                config["model_tier"] = "nano"

            # Strong regularization
            old_dropout = config.get("dropout", 0.1)
            if old_dropout < 0.2:
                self._add_recommendation(
                    parameter="dropout",
                    old_value=old_dropout,
                    new_value=0.2,
                    reason="Tiny dataset: increase dropout for regularization",
                    md_reference="§7.2 Dropout & Label Smoothing",
                    priority=2
                )
                config["dropout"] = 0.2

            # Freeze pretrained if available
            pretrained = config.get("pretrained_model", "None (Train from scratch)")
            if pretrained != "None (Train from scratch)":
                old_freeze = config.get("freeze_pretrained", False)
                if not old_freeze:
                    self._add_recommendation(
                        parameter="freeze_pretrained",
                        old_value=old_freeze,
                        new_value=True,
                        reason="Tiny dataset + pretrained: freeze to preserve features",
                        md_reference="§4.1 LoRA + §11.3 LLRD",
                        priority=2
                    )
                    config["freeze_pretrained"] = True

        elif ds_size == DatasetSize.SMALL:
            if model_tier in ["large", "xl"]:
                self._add_recommendation(
                    parameter="model_tier",
                    old_value=model_tier,
                    new_value="base",
                    reason="Small dataset (1K-10K): base tier sufficient, prevents overfitting",
                    md_reference="§1.1 + Data-Aware Recommendations",
                    priority=1
                )
                config["model_tier"] = "base"

            # Recommend SSL pre-training
            paradigm = config.get("paradigm", "SHADA Pipeline")
            pretrained = config.get("pretrained_model", "None (Train from scratch)")
            if pretrained == "None (Train from scratch)" and paradigm == "Standard Supervised":
                self._add_recommendation(
                    parameter="paradigm",
                    old_value=paradigm,
                    new_value="SHADA Pipeline",
                    reason="Small dataset without pretrained: SSL pre-training strongly recommended",
                    md_reference="§8 SSL + Data-Aware Recommendations",
                    priority=1
                )
                config["paradigm"] = "SHADA Pipeline"

        elif ds_size == DatasetSize.VERY_LARGE:
            if model_tier == "nano":
                self._add_recommendation(
                    parameter="model_tier",
                    old_value=model_tier,
                    new_value="large",
                    reason="Very large dataset (500K+): larger model can benefit from data",
                    md_reference="§1.1 + Data-Aware Recommendations",
                    priority=2
                )
                config["model_tier"] = "large"

            # SSL optional for very large datasets
            pretrained = config.get("pretrained_model", "None (Train from scratch)")
            if pretrained == "None (Train from scratch)":
                self._add_recommendation(
                    parameter="paradigm",
                    old_value=config.get("paradigm", "SHADA Pipeline"),
                    new_value="Standard Supervised",
                    reason="Very large labeled dataset: SSL pre-training adds time with diminishing returns",
                    md_reference="§8 SSL + Data-Aware Recommendations",
                    priority=2
                )
                config["paradigm"] = "Standard Supervised"

        # Imbalanced dataset handling
        if dataset_info and dataset_info.get("is_imbalanced", False):
            old_smoothing = config.get("label_smoothing", 0.1)
            if old_smoothing < 0.15:
                self._add_recommendation(
                    parameter="label_smoothing",
                    old_value=old_smoothing,
                    new_value=0.15,
                    reason="Imbalanced dataset: higher label smoothing improves calibration",
                    md_reference="§7.2 Dropout & Label Smoothing + Data-Aware Recommendations",
                    priority=2
                )
                config["label_smoothing"] = 0.15

            # Recommend curriculum learning
            old_curr = config.get("use_curriculum", True)
            if not old_curr:
                self._add_recommendation(
                    parameter="use_curriculum",
                    old_value=old_curr,
                    new_value=True,
                    reason="Imbalanced dataset: curriculum learning helps with hard examples",
                    md_reference="§10.1 Curriculum Learning + Data-Aware Recommendations",
                    priority=2
                )
                config["use_curriculum"] = True

        # Noisy labels handling
        if dataset_info and dataset_info.get("has_noisy_labels", False):
            old_smoothing = config.get("label_smoothing", 0.1)
            if old_smoothing < 0.2:
                self._add_recommendation(
                    parameter="label_smoothing",
                    old_value=old_smoothing,
                    new_value=0.2,
                    reason="Noisy labels: high label smoothing prevents overfitting to wrong labels",
                    md_reference="§7.2 + Data-Aware Recommendations",
                    priority=1
                )
                config["label_smoothing"] = 0.2

            # DINO-only SSL for noisy data
            ssl_alpha = config.get("ssl_alpha", 1.0)
            ssl_beta = config.get("ssl_beta", 0.5)
            if ssl_alpha > 0.5 or ssl_beta > 0.3:
                self._add_recommendation(
                    parameter="ssl_alpha",
                    old_value=ssl_alpha,
                    new_value=0.3,
                    reason="Noisy labels: reduce MAE weight, rely more on DINO (robust to noise)",
                    md_reference="§8.3 DINO + Data-Aware Recommendations",
                    priority=2
                )
                config["ssl_alpha"] = 0.3
                self._add_recommendation(
                    parameter="ssl_beta",
                    old_value=ssl_beta,
                    new_value=0.2,
                    reason="Noisy labels: reduce contrastive weight (sensitive to noise)",
                    md_reference="§8.2 NT-Xent + Data-Aware Recommendations",
                    priority=2
                )
                config["ssl_beta"] = 0.2

    # ─────────────────────────────────────────────────────────────────────────
    # GOAL OPTIMIZATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_goal_optimizations(self, config: dict, training_goal: str,
                                   hw_tier: HardwareTier):
        """Apply optimizations based on user's training priority."""

        if training_goal == "fast":
            # Minimize training time
            old_epochs = config.get("num_epochs", 100)
            if old_epochs > 20:
                self._add_recommendation(
                    parameter="num_epochs",
                    old_value=old_epochs,
                    new_value=20,
                    reason="Fast mode: reduce epochs for quick results",
                    md_reference="§15.4 Four-Phase Training Pipeline",
                    priority=2
                )
                config["num_epochs"] = 20

            # Single phase
            old_paradigm = config.get("paradigm", "SHADA Pipeline")
            if old_paradigm == "SHADA Pipeline":
                self._add_recommendation(
                    parameter="paradigm",
                    old_value=old_paradigm,
                    new_value="Standard Supervised",
                    reason="Fast mode: skip SSL pre-training phases",
                    md_reference="§15.4 Four-Phase Training Pipeline",
                    priority=1
                )
                config["paradigm"] = "Standard Supervised"

            # Disable curriculum (overhead)
            old_curr = config.get("use_curriculum", True)
            if old_curr:
                self._add_recommendation(
                    parameter="use_curriculum",
                    old_value=old_curr,
                    new_value=False,
                    reason="Fast mode: disable curriculum to reduce overhead",
                    md_reference="§10.1 Curriculum Learning",
                    priority=3
                )
                config["use_curriculum"] = False

        elif training_goal == "max_accuracy":
            # Maximize final accuracy
            old_epochs = config.get("num_epochs", 100)
            if old_epochs < 100:
                self._add_recommendation(
                    parameter="num_epochs",
                    old_value=old_epochs,
                    new_value=100,
                    reason="Max accuracy: increase epochs for full convergence",
                    md_reference="§15.4 Four-Phase Training Pipeline",
                    priority=1
                )
                config["num_epochs"] = 100

            # Enable full SHADA pipeline
            old_paradigm = config.get("paradigm", "Standard Supervised")
            if old_paradigm != "SHADA Pipeline":
                self._add_recommendation(
                    parameter="paradigm",
                    old_value=old_paradigm,
                    new_value="SHADA Pipeline",
                    reason="Max accuracy: full 4-phase pipeline for best results",
                    md_reference="§15.4 Four-Phase Training Pipeline",
                    priority=1
                )
                config["paradigm"] = "SHADA Pipeline"

            # Enable SWA (Stochastic Weight Averaging)
            # Note: SWA is automatic in finetune phase per §12.3

            # Reduce label smoothing slightly (can hurt calibration)
            old_smoothing = config.get("label_smoothing", 0.1)
            if old_smoothing > 0.1:
                self._add_recommendation(
                    parameter="label_smoothing",
                    old_value=old_smoothing,
                    new_value=0.05,
                    reason="Max accuracy: lower label smoothing for better calibration",
                    md_reference="§7.2 Dropout & Label Smoothing",
                    priority=2
                )
                config["label_smoothing"] = 0.05

            # Enable GradNorm if multi-task
            if len(config.get("tasks", ["classification"])) > 1:
                old_mtl = config.get("use_mtl", True)
                if not old_mtl:
                    self._add_recommendation(
                        parameter="use_mtl",
                        old_value=old_mtl,
                        new_value=True,
                        reason="Max accuracy + multi-task: GradNorm balances task gradients",
                        md_reference="§9.1 GradNorm",
                        priority=1
                    )
                    config["use_mtl"] = True

        # "balanced" is default - no changes needed

    # ─────────────────────────────────────────────────────────────────────────
    # TASK OPTIMIZATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_task_optimizations(self, config: dict, task: str):
        """Apply optimizations based on specific task."""

        # Language Modeling
        if task == "lm":
            # Disable adversarial (not applicable to text)
            old_adv = config.get("use_adversarial", False)
            if old_adv:
                self._add_recommendation(
                    parameter="use_adversarial",
                    old_value=old_adv,
                    new_value=False,
                    reason="LM task: PGD-AT is for continuous inputs (images) only",
                    md_reference="§14.1 PGD Adversarial Training",
                    priority=1
                )
                config["use_adversarial"] = False

            # Disable detection/segmentation heads
            tasks = config.get("tasks", ["classification"])
            if "detection" in tasks or "segmentation" in tasks:
                self._add_recommendation(
                    parameter="tasks",
                    old_value=tasks,
                    new_value=["lm"],
                    reason="LM task: disable vision-specific heads",
                    md_reference="§1.4 DETR Detection Head",
                    priority=1
                )
                config["tasks"] = ["lm"]

            # RoPE is already default for transformers

            # bf16 preferred for LLMs
            old_mp = config.get("mixed_precision", "fp32")
            if old_mp != "bf16":
                self._add_recommendation(
                    parameter="mixed_precision",
                    old_value=old_mp,
                    new_value="bf16",
                    reason="LLM training: bf16 preferred for numerical stability",
                    md_reference="§15.1 Mixed-Precision Training",
                    priority=2
                )
                config["mixed_precision"] = "bf16"

        # Object Detection
        elif task == "detection":
            # Ensure FPN is active (it's part of hierarchical encoder)
            # Recommend larger batch for detection
            old_batch = config.get("batch_size", 16)
            if old_batch < 32:
                self._add_recommendation(
                    parameter="batch_size",
                    old_value=old_batch,
                    new_value=32,
                    reason="Detection: larger batch improves box regression stability",
                    md_reference="§1.4 DETR Detection Head",
                    priority=2
                )
                config["batch_size"] = 32

        # Segmentation
        elif task == "segmentation":
            # Segmentation benefits from larger images
            old_img_size = config.get("img_size", 224)
            if old_img_size < 256:
                self._add_recommendation(
                    parameter="img_size",
                    old_value=old_img_size,
                    new_value=256,
                    reason="Segmentation: larger input preserves fine details",
                    md_reference="§1.2 FPN Neck",
                    priority=2
                )
                config["img_size"] = 256

        # Classification (default)
        elif task == "classification":
            # Standard settings work well
            pass

    # ─────────────────────────────────────────────────────────────────────────
    # PARADIGM OPTIMIZATIONS
    # ─────────────────────────────────────────────────────────────────────────
    def _apply_paradigm_optimizations(self, config: dict, paradigm: str):
        """Apply optimizations based on training paradigm."""

        if paradigm == "SHADA Pipeline":
            # Ensure all SSL weights are non-zero
            ssl_alpha = config.get("ssl_alpha", 1.0)
            ssl_beta = config.get("ssl_beta", 0.5)
            ssl_gamma = config.get("ssl_gamma", 0.3)

            if ssl_alpha == 0 and ssl_beta == 0 and ssl_gamma == 0:
                self._add_recommendation(
                    parameter="ssl_alpha",
                    old_value=0,
                    new_value=1.0,
                    reason="SHADA Pipeline: at least one SSL objective must be active",
                    md_reference="§8 SSL Coefficient Annealing",
                    priority=1
                )
                config["ssl_alpha"] = 1.0
                config["ssl_beta"] = 0.5
                config["ssl_gamma"] = 0.3

            # Ensure MTL is enabled for mtl phase
            old_mtl = config.get("use_mtl", True)
            if not old_mtl:
                self._add_recommendation(
                    parameter="use_mtl",
                    old_value=old_mtl,
                    new_value=True,
                    reason="SHADA Pipeline: GradNorm needed for mtl phase",
                    md_reference="§9.1 GradNorm + §15.4 Four-Phase Pipeline",
                    priority=2
                )
                config["use_mtl"] = True

        elif paradigm == "Contrastive SSL":
            # Focus on contrastive loss
            old_beta = config.get("ssl_beta", 0.5)
            if old_beta < 1.0:
                self._add_recommendation(
                    parameter="ssl_beta",
                    old_value=old_beta,
                    new_value=1.0,
                    reason="Contrastive SSL: maximize NT-Xent weight",
                    md_reference="§8.2 NT-Xent Contrastive Loss",
                    priority=1
                )
                config["ssl_beta"] = 1.0

            # Ensure batch size is adequate
            old_batch = config.get("batch_size", 16)
            old_acc = config.get("gradient_accumulation_steps", 1)
            effective_batch = old_batch * old_acc

            if effective_batch < 64:
                new_acc = math.ceil(64 / old_batch)
                self._add_recommendation(
                    parameter="gradient_accumulation_steps",
                    old_value=old_acc,
                    new_value=new_acc,
                    reason="Contrastive SSL: effective batch ≥64 for quality negatives",
                    md_reference="§8.2 NT-Xent Contrastive Loss",
                    priority=1
                )
                config["gradient_accumulation_steps"] = new_acc

        elif paradigm == "Standard Supervised":
            # Disable SSL weights
            old_alpha = config.get("ssl_alpha", 1.0)
            old_beta = config.get("ssl_beta", 0.5)
            old_gamma = config.get("ssl_gamma", 0.3)

            if old_alpha > 0 or old_beta > 0 or old_gamma > 0:
                self._add_recommendation(
                    parameter="ssl_alpha",
                    old_value=old_alpha,
                    new_value=0,
                    reason="Standard Supervised: SSL objectives not used",
                    md_reference="§8 SSL + §15.4 Four-Phase Pipeline",
                    priority=3
                )
                config["ssl_alpha"] = 0
                config["ssl_beta"] = 0
                config["ssl_gamma"] = 0

            # Disable curriculum (optional, reduces overhead)
            # Keep it enabled by default for better generalization


def smart_tune_config(
    config: dict,
    dataset_info: Optional[dict] = None,
    hardware_info: Optional[dict] = None,
    training_goal: str = "balanced"
) -> Tuple[dict, list[SmartConfigRecommendation]]:
    """
    Convenience function: auto-tune configuration.

    Args:
        config: Current SHADAConfig dict
        dataset_info: Dataset metadata
        hardware_info: Hardware metadata
        training_goal: "balanced", "fast", or "max_accuracy"

    Returns:
        Tuple of (optimized_config, recommendations)
    """
    tuner = SHADASmartConfig()
    return tuner.analyze_and_tune(config, dataset_info, hardware_info, training_goal)
