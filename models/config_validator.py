"""
SHADA Configuration Validator — Intelligent diagnostic checks based on
SHADA_Technical_Analysis.md documentation.

Generates structured alerts with:
- level: INFO | WARNING | CRITICAL
- parameter: exact config key name
- md_reference: section in technical documentation
- message: clear, actionable explanation
- recommendation: exact suggested value or action
- reason: why this matters for accuracy or stability
"""

import math
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum


class AlertLevel(Enum):
    INFO = "INFO"
    WARNING = "WARNING"
    CRITICAL = "CRITICAL"


@dataclass
class ConfigAlert:
    level: AlertLevel
    parameter: str
    md_reference: str
    message: str
    recommendation: str
    reason: str

    def to_dict(self) -> dict:
        return {
            "level": self.level.value,
            "parameter": self.parameter,
            "md_reference": self.md_reference,
            "message": self.message,
            "recommendation": self.recommendation,
            "reason": self.reason,
        }


class SHADAConfigValidator:
    """
    Intelligent configuration validator for SHADA algorithm.
    All rules derived from SHADA_Technical_Analysis.md
    """

    def __init__(self):
        self.alerts: List[ConfigAlert] = []

    def validate(self, config: dict, dataset_info: Optional[dict] = None,
                 hardware_info: Optional[dict] = None) -> List[dict]:
        """
        Run full diagnostic on configuration.

        Args:
            config: SHADAConfig dict from UI
            dataset_info: Optional dict with 'num_samples', 'num_classes', 'is_imbalanced', etc.
            hardware_info: Optional dict with 'vram_gb', 'device', 'gpu_name'

        Returns:
            List of alert dicts (JSON-serializable)
        """
        self.alerts = []

        # Run all validation checks
        self._check_optimizer_lr(config)
        self._check_batch_size(config, dataset_info)
        self._check_mixed_precision(config, hardware_info)
        self._check_layer_freezing(config, dataset_info)
        self._check_lora_config(config)
        self._check_regularization(config, dataset_info)
        self._check_ssl_config(config, dataset_info)
        self._check_rl_config(config)
        self._check_adversarial_config(config, dataset_info)
        self._check_mtl_config(config)
        self._check_curriculum_config(config)
        self._check_scheduler_config(config)
        self._check_epochs_config(config)
        self._check_model_tier(config, dataset_info, hardware_info)
        self._check_gradient_accumulation(config)
        self._check_warmup_config(config)
        self._check_pruning_quantization(config)

        return [alert.to_dict() for alert in self.alerts]

    def _add_alert(self, level: AlertLevel, parameter: str, md_reference: str,
                   message: str, recommendation: str, reason: str):
        self.alerts.append(ConfigAlert(
            level=level,
            parameter=parameter,
            md_reference=md_reference,
            message=message,
            recommendation=recommendation,
            reason=reason,
        ))

    # ─────────────────────────────────────────────────────────────────────────
    # §11.2 Lion Optimizer — LR must be 3–10× lower than AdamW
    # ─────────────────────────────────────────────────────────────────────────
    def _check_optimizer_lr(self, config: dict):
        optimizer = config.get("optimizer", "adamw")
        base_lr = config.get("base_lr", 1e-4)

        if optimizer == "lion" and base_lr > 1e-4:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                parameter="base_lr",
                md_reference="§11.2 Lion Optimizer",
                message=f"LR of {base_lr:.0e} is too high for Lion optimizer.",
                recommendation="Reduce base_lr to 1e-5 or 3e-5",
                reason="§11.2 documents that Lion uses only the sign of gradients, "
                       "making it 3–10× more aggressive than AdamW at the same learning rate. "
                       "Using AdamW LR directly with Lion leads to divergence."
            )
        elif optimizer == "lion":
            # Lion with appropriate LR - info about memory benefit
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="optimizer",
                md_reference="§11.2 Lion Optimizer",
                message="Lion optimizer selected with appropriate LR.",
                recommendation="Monitor training stability; Lion may be too aggressive for small datasets (<10K)",
                reason="Lion reduces memory by ~1/3 vs AdamW (no second moment) but may be too aggressive on small datasets."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §8.2 NT-Xent + §15.2 Gradient Accumulation — Effective batch size
    # ─────────────────────────────────────────────────────────────────────────
    def _check_batch_size(self, config: dict, dataset_info: Optional[dict]):
        batch_size = config.get("batch_size", 16)
        grad_acc = config.get("gradient_accumulation_steps", 1)
        effective_batch = batch_size * grad_acc
        paradigm = config.get("paradigm", "SHADA Pipeline")

        # NT-Xent requires batch ≥ 32 for quality negatives
        if effective_batch < 32 and paradigm in ["SHADA Pipeline", "Contrastive SSL"]:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="batch_size",
                md_reference="§8.2 NT-Xent Contrastive Loss + §15.2 Gradient Accumulation",
                message=f"Effective batch size ({effective_batch}) is too small for NT-Xent contrastive SSL.",
                recommendation=f"Increase batch_size to ≥32, or set gradient_accumulation_steps ≥ {math.ceil(32/batch_size)}",
                reason="§8.2 documents that NT-Xent quality degrades significantly as negatives reduce. "
                       "Minimum effective batch of 32 is required for stable contrastive pre-training."
            )

        # Very large batch may hurt generalization
        if effective_batch > 4096:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="batch_size",
                md_reference="§15.2 Gradient Accumulation",
                message=f"Effective batch size ({effective_batch}) is very large.",
                recommendation="Reduce to ≤4096 for better generalization",
                reason="§15.2 warns that very large batches may hurt generalization despite faster training."
            )

        # Dataset-aware batch size
        if dataset_info and dataset_info.get("num_samples", float("inf")) < 1000:
            if batch_size > 32:
                self._add_alert(
                    level=AlertLevel.INFO,
                    parameter="batch_size",
                    md_reference="§15.2 Gradient Accumulation",
                    message=f"Batch size {batch_size} is large relative to dataset size ({dataset_info['num_samples']} samples).",
                    recommendation="Consider reducing batch_size to 8-16 for small datasets",
                    reason="Small datasets benefit from smaller batches with more frequent updates."
                )

    # ─────────────────────────────────────────────────────────────────────────
    # §15.1 Mixed Precision — fp16 on CPU is unsupported
    # ─────────────────────────────────────────────────────────────────────────
    def _check_mixed_precision(self, config: dict, hardware_info: Optional[dict]):
        mp = config.get("mixed_precision", "fp32")
        device = hardware_info.get("device", "cuda") if hardware_info else "cuda"

        if mp == "fp16" and device == "cpu":
            self._add_alert(
                level=AlertLevel.CRITICAL,
                parameter="mixed_precision",
                md_reference="§15.1 Mixed-Precision Training",
                message="fp16 mixed precision is unsupported on CPU.",
                recommendation="Set mixed_precision = 'fp32' for CPU training",
                reason="§15.1 documents that fp16 requires Tensor Core GPUs. CPU training must use fp32."
            )

        if mp == "fp32":
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="mixed_precision",
                md_reference="§15.1 Mixed-Precision Training",
                message="Full precision (fp32) selected — 50% more memory, 2-3× slower on Tensor Core GPUs.",
                recommendation="Set mixed_precision = 'bf16' (NVIDIA Ampere+) or 'fp16' (older NVIDIA) for 2-3× speedup",
                reason="§15.1 documents that bf16/fp16 reduces GPU memory by ~50% and increases throughput by 2-3×."
            )

        if mp == "bf16" and hardware_info:
            gpu_name = hardware_info.get("gpu_name", "").lower()
            # bf16 requires Ampere (A100, RTX 30xx) or newer
            if "1660" in gpu_name or "1060" in gpu_name or "1080" in gpu_name or "2060" in gpu_name or "2080" in gpu_name:
                self._add_alert(
                    level=AlertLevel.WARNING,
                    parameter="mixed_precision",
                    md_reference="§15.1 Mixed-Precision Training",
                    message=f"bf16 may not be fully supported on {hardware_info.get('gpu_name', 'your GPU')}.",
                    recommendation="Use 'fp16' for Turing (20xx) or older GPUs",
                    reason="§15.1 notes bf16 is preferred on NVIDIA Ampere+ (A100, RTX 30xx+). Older GPUs may have limited bf16 support."
                )

    # ─────────────────────────────────────────────────────────────────────────
    # §4.1 LoRA + §11.3 LLRD — Layer Freezing Safety Rule
    # ─────────────────────────────────────────────────────────────────────────
    def _check_layer_freezing(self, config: dict, dataset_info: Optional[dict]):
        freeze = config.get("freeze_pretrained", False)
        pretrained = config.get("pretrained_model", "None (Train from scratch)")
        lora_rank = config.get("lora_rank", 16)
        llrd_decay = config.get("llrd_decay", 0.8)

        is_pretrained = pretrained != "None (Train from scratch)"

        # Freezing with no pretrained model = useless
        if freeze and not is_pretrained:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="freeze_pretrained",
                md_reference="§4.1 LoRA + §11.3 LLRD",
                message="freeze_pretrained=True but no pretrained model is loaded.",
                recommendation="Set freeze_pretrained=False when training from scratch",
                reason="Freezing layers only matters when loading pretrained weights. Training from scratch with frozen layers prevents learning."
            )

        # Freezing with large dataset = bad idea
        if freeze and dataset_info and dataset_info.get("num_samples", 0) > 10000:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                parameter="freeze_pretrained",
                md_reference="§4.1 LoRA + §11.3 LLRD",
                message=f"Layer freezing is active with dataset > 10K samples ({dataset_info['num_samples']} samples). This will severely limit fine-tuning accuracy.",
                recommendation="Set freeze_pretrained=False, llrd_decay=0.70, base_lr=1e-4",
                reason="§11.3 documents that LLRD applies a lower LR to early layers rather than stopping updates entirely. "
                       "This preserves pretrained features while allowing necessary adaptation. Freezing prevents all updates."
            )

        # LoRA + Freezing conflict
        if freeze and lora_rank > 0 and is_pretrained:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="freeze_pretrained",
                md_reference="§4.1 LoRA",
                message="LoRA adapters will train on frozen base weights. LoRA cannot adapt features—only add a delta on top of locked feature space.",
                recommendation="Either: (a) unfreeze with LLRD (freeze_pretrained=False, llrd_decay=0.70), or (b) freeze AND set lora_rank=0",
                reason="§4.1 documents that with LoRA, the base weight is frozen and only (A, B) matrices train. "
                       "On already-frozen pretrained weights, LoRA is further constrained."
            )

        # Small dataset: freezing may be acceptable
        if freeze and dataset_info and dataset_info.get("num_samples", float("inf")) < 1000:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="freeze_pretrained",
                md_reference="§4.1 LoRA",
                message=f"Freezing pretrained layers on small dataset ({dataset_info['num_samples']} samples) may be acceptable but limits adaptation.",
                recommendation="Consider unfreezing with LLRD (freeze_pretrained=False, llrd_decay=0.70) for better accuracy",
                reason="§4.1 notes freezing may be acceptable for <1K samples, but §11.3 shows LLRD achieves better results."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §4.1 LoRA — Rank and efficiency
    # ─────────────────────────────────────────────────────────────────────────
    def _check_lora_config(self, config: dict):
        lora_rank = config.get("lora_rank", 16)
        lora_alpha = config.get("lora_alpha", 32.0)
        pretrained = config.get("pretrained_model", "None (Train from scratch)")

        # High rank reduces parameter efficiency
        if lora_rank > 64:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="lora_rank",
                md_reference="§4.1 LoRA",
                message=f"LoRA rank {lora_rank} is high. This reduces parameter efficiency benefits.",
                recommendation="Use lora_rank ≤ 64 (typically 8-32 is sufficient)",
                reason="§4.1 'When NOT to use' warns that high rank approaches full fine-tuning, losing LoRA's memory efficiency."
            )

        # Rank approaching encoder dimension
        encoder_dim = config.get("encoder_dims", [128, 256, 512, 1024])[0]
        if lora_rank >= encoder_dim // 2:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="lora_rank",
                md_reference="§4.1 LoRA",
                message=f"LoRA rank ({lora_rank}) is approaching half the encoder dimension ({encoder_dim}). Consider full fine-tuning instead.",
                recommendation="If lora_rank ≥ encoder_dim/2, full fine-tuning may be more efficient",
                reason="§4.1 notes that approaching full-rank reduces LoRA's benefits; full fine-tuning becomes competitive."
            )

        # LoRA with training from scratch
        if lora_rank > 0 and pretrained == "None (Train from scratch)":
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="lora_rank",
                md_reference="§4.1 LoRA",
                message="LoRA is active but training from scratch. LoRA adds indirection without benefit when no pretrained weights exist.",
                recommendation="Set lora_rank=0 when training from scratch, or load a pretrained model",
                reason="§4.1 explicitly states: 'Training from scratch — LoRA adds indirection without benefit.'"
            )

        # Alpha should typically be 2× rank
        if lora_alpha < lora_rank:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="lora_alpha",
                md_reference="§4.1 LoRA",
                message=f"lora_alpha ({lora_alpha}) is less than lora_rank ({lora_rank}). Typical practice is alpha = 2× rank.",
                recommendation="Set lora_alpha = 2 × lora_rank (e.g., rank=16 → alpha=32)",
                reason="The scaling factor α/r controls the magnitude of LoRA updates. alpha ≥ rank is standard practice."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §7 Regularization — Dropout, DropPath, Label Smoothing
    # ─────────────────────────────────────────────────────────────────────────
    def _check_regularization(self, config: dict, dataset_info: Optional[dict]):
        dropout = config.get("dropout", 0.1)
        drop_path = config.get("drop_path_rate", 0.1)
        label_smoothing = config.get("label_smoothing", 0.1)
        model_tier = config.get("model_tier", "nano")

        num_samples = dataset_info.get("num_samples", float("inf")) if dataset_info else float("inf")

        # High dropout on small datasets
        if dropout > 0.3 and num_samples < 50000:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="dropout",
                md_reference="§7.2 Dropout & Label Smoothing",
                message=f"Dropout {dropout} is high for dataset size ({num_samples} samples). This may prevent convergence.",
                recommendation="Reduce dropout to ≤0.2 for small datasets",
                reason="§7.2 warns that high dropout on small datasets prevents the model from learning sufficient representations."
            )

        # Aggressive drop_path on tiny models
        if drop_path > 0.2 and model_tier == "nano":
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="drop_path_rate",
                md_reference="§7.1 Stochastic Depth",
                message=f"Stochastic depth rate {drop_path} is aggressive for nano-tier models.",
                recommendation="Reduce drop_path_rate to ≤0.1 for nano/base tiers",
                reason="§7.1 documents that aggressive stochastic depth on tiny models hurts performance by dropping too many critical layers."
            )

        # Excessive label smoothing
        if label_smoothing > 0.2:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="label_smoothing",
                md_reference="§7.2 Dropout & Label Smoothing",
                message=f"Label smoothing {label_smoothing} is excessive. This hurts calibration.",
                recommendation="Use label_smoothing ≤0.15 (typically 0.05-0.1)",
                reason="§7.2 warns that excessive label smoothing hurts calibration and can compound label noise."
            )

        # Imbalanced dataset recommendations
        if dataset_info and dataset_info.get("is_imbalanced", False):
            if label_smoothing < 0.1:
                self._add_alert(
                    level=AlertLevel.INFO,
                    parameter="label_smoothing",
                    md_reference="§7.2 Dropout & Label Smoothing",
                    message="Dataset is imbalanced. Current label smoothing may be insufficient.",
                    recommendation="Increase label_smoothing to 0.15 for imbalanced classes",
                    reason="§7.2 + data-aware rules recommend higher label smoothing for imbalanced datasets."
                )

    # ─────────────────────────────────────────────────────────────────────────
    # §8 SSL — Mask ratio, coefficient annealing, SSL weights
    # ─────────────────────────────────────────────────────────────────────────
    def _check_ssl_config(self, config: dict, dataset_info: Optional[dict]):
        mask_ratio = config.get("mask_ratio", 0.75)
        ssl_alpha = config.get("ssl_alpha", 1.0)
        ssl_beta = config.get("ssl_beta", 0.5)
        ssl_gamma = config.get("ssl_gamma", 0.3)
        paradigm = config.get("paradigm", "SHADA Pipeline")

        # Very high masking on small images
        if mask_ratio > 0.80:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="mask_ratio",
                md_reference="§8.1 Masked Autoencoder",
                message=f"Mask ratio {mask_ratio} is very high. This may cause unstable MAE training on small images.",
                recommendation="Use mask_ratio between 0.60-0.75 for standard 224×224 images",
                reason="§8.1 warns that very high masking (>0.80) may cause unstable training, especially on small images."
            )

        # All SSL weights zero = no learning
        if ssl_alpha + ssl_beta + ssl_gamma == 0:
            self._add_alert(
                level=AlertLevel.CRITICAL,
                parameter="ssl_alpha",
                md_reference="§8 SSL Coefficient Annealing",
                message="All SSL weights are zero (α+β+γ=0). Pre-training phase will produce no learning.",
                recommendation="Set ssl_alpha=1.0, ssl_beta=0.5, ssl_gamma=0.3 for balanced SSL",
                reason="At least one SSL objective must have non-zero weight for pre-training to work."
            )

        # SSL pre-training necessity based on dataset size
        num_samples = dataset_info.get("num_samples", float("inf")) if dataset_info else float("inf")
        has_pretrained = config.get("pretrained_model", "None") != "None (Train from scratch)"

        if num_samples > 100000 and paradigm == "SHADA Pipeline" and not has_pretrained:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="paradigm",
                md_reference="§8 SSL + §15.4 Four-Phase Pipeline",
                message=f"SSL pre-training is optional for large datasets (>100K samples). Adds training time with diminishing returns.",
                recommendation="Consider 'Standard Supervised' paradigm for faster training on large labeled datasets",
                reason="§8 documents that SSL pre-training provides diminishing returns when labeled data > 100K samples."
            )

        if num_samples < 5000 and not has_pretrained:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="paradigm",
                md_reference="§8 SSL",
                message=f"Small dataset ({num_samples} samples). Strongly recommend SSL pre-training (Phase 1) before fine-tuning.",
                recommendation="Use 'SHADA Pipeline' or 'Contrastive SSL' paradigm with ssl_alpha=1.0, ssl_beta=0.5",
                reason="§8 recommends SSL pre-training for <5K samples to learn robust representations before supervised fine-tuning."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §13 RL — PPO vs DPO, KL coefficient
    # ─────────────────────────────────────────────────────────────────────────
    def _check_rl_config(self, config: dict):
        use_rl = config.get("use_rl", False)
        rl_algo = config.get("rl_algorithm", "dpo")
        rl_kl = config.get("rl_kl_coeff", 0.1)
        task = config.get("task", "classification")

        if not use_rl:
            return

        # PPO without reward model
        if rl_algo == "ppo":
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="rl_algorithm",
                md_reference="§13.1 PPO vs §13.3 DPO",
                message="PPO requires a trained reward model for RLHF.",
                recommendation="If only preference pairs (chosen/rejected) exist, use DPO instead",
                reason="§13.1 vs §13.3: PPO needs reward model; DPO works directly with preference pairs."
            )

        # KL too low = catastrophic forgetting
        if rl_kl < 0.01:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="rl_kl_coeff",
                md_reference="§13.1 PPO",
                message=f"KL coefficient {rl_kl} is too low. Risk of catastrophic forgetting.",
                recommendation="Increase rl_kl_coeff to ≥0.1",
                reason="§13.1 documents that KL penalty keeps policy close to supervised baseline. Too low allows drift."
            )

        # KL too high = no alignment
        if rl_kl > 1.0:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="rl_kl_coeff",
                md_reference="§13.1 PPO",
                message=f"KL coefficient {rl_kl} is too high. Alignment will be prevented.",
                recommendation="Reduce rl_kl_coeff to 0.01-0.5 range",
                reason="§13.1: Excessive KL penalty prevents the policy from learning from rewards."
            )

        # RL on non-LM tasks
        if use_rl and task != "lm":
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="use_rl",
                md_reference="§13 Reinforcement Learning",
                message=f"RL is enabled for {task} task. RLHF/DPO is designed for language modeling.",
                recommendation="Disable RL for non-LM tasks unless you have specific reward signals",
                reason="§13 documents RL for language model alignment. Vision tasks rarely benefit from RL."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §14 Adversarial Training — Clean accuracy trade-off, task compatibility
    # ─────────────────────────────────────────────────────────────────────────
    def _check_adversarial_config(self, config: dict, dataset_info: Optional[dict]):
        use_adv = config.get("use_adversarial", False)
        adv_epsilon = config.get("adv_epsilon", 8/255)
        task = config.get("task", "classification")

        if not use_adv:
            return

        # Small dataset + adversarial = hurt clean accuracy
        num_samples = dataset_info.get("num_samples", float("inf")) if dataset_info else float("inf")
        if num_samples < 20000:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="use_adversarial",
                md_reference="§14.1 PGD Adversarial Training",
                message=f"Adversarial training on small dataset ({num_samples} samples) will significantly hurt clean accuracy.",
                recommendation="Disable adversarial training for <20K samples unless robustness is critical",
                reason="§14.1 documents that adversarial training typically reduces clean accuracy by 1-5%, worse on small datasets."
            )

        # Unrealistic epsilon
        if adv_epsilon > 16/255:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="adv_epsilon",
                md_reference="§14.1 PGD Adversarial Training",
                message=f"Adversarial epsilon {adv_epsilon:.3f} ({adv_epsilon*255:.1f}/255) is too high. Creates unrealistic examples.",
                recommendation="Use adv_epsilon between 8/255 and 16/255",
                reason="§14.1 warns that excessive epsilon creates adversarial examples too different from natural data."
            )

        # Adversarial on LM task = wrong tool
        if task == "lm":
            self._add_alert(
                level=AlertLevel.CRITICAL,
                parameter="use_adversarial",
                md_reference="§14.1 PGD Adversarial Training",
                message="PGD-AT is for continuous inputs (images) only. Not applicable to text (discrete tokens).",
                recommendation="Disable adversarial training for language modeling",
                reason="§14.1 'When NOT to use': Text tasks require token-swap attacks, not gradient-based PGD."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §9.1 GradNorm — Single task = useless
    # ─────────────────────────────────────────────────────────────────────────
    def _check_mtl_config(self, config: dict):
        use_mtl = config.get("use_mtl", True)
        tasks = config.get("tasks", ["classification"])

        if use_mtl and len(tasks) == 1:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="use_mtl",
                md_reference="§9.1 GradNorm",
                message="GradNorm is useless with a single task. Adds overhead with no benefit.",
                recommendation="Disable use_mtl when training single-task",
                reason="§9.1 explicitly states GradNorm dynamically weights multiple tasks. Single-task has nothing to balance."
            )

        # gradnorm_alpha too high
        gradnorm_alpha = config.get("gradnorm_alpha", 1.5)
        if gradnorm_alpha > 2.5:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="gradnorm_alpha",
                md_reference="§9.1 GradNorm",
                message=f"GradNorm alpha {gradnorm_alpha} is high. Overly sensitive to training speed differences.",
                recommendation="Use gradnorm_alpha between 1.0-2.0",
                reason="§9.1: High alpha makes GradNorm overreact to temporary gradient norm differences."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §10.1 Curriculum — Warmup vs total epochs
    # ─────────────────────────────────────────────────────────────────────────
    def _check_curriculum_config(self, config: dict):
        use_curr = config.get("use_curriculum", True)
        curriculum_warmup = config.get("curriculum_warmup", 5000)
        num_epochs = config.get("num_epochs", 10)
        batch_size = config.get("batch_size", 16)
        grad_acc = config.get("gradient_accumulation_steps", 1)

        if not use_curr:
            return

        # Estimate total steps
        # We don't know dataset size here, but can check warmup vs epochs
        steps_per_epoch = 100  # rough estimate
        total_steps = num_epochs * steps_per_epoch * grad_acc

        if curriculum_warmup > total_steps * 0.5:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="curriculum_warmup",
                md_reference="§10.1 Curriculum Learning",
                message=f"Curriculum warmup ({curriculum_warmup}) exceeds 50% of estimated training. Adjust warmup.",
                recommendation=f"Set curriculum_warmup to {max(1000, int(total_steps * 0.2))} (~20% of training)",
                reason="§10.1 warns that warmup should not dominate training; otherwise curriculum never reaches hard examples."
            )

        if num_epochs < 5 and use_curr:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="use_curriculum",
                md_reference="§10.1 Curriculum Learning",
                message=f"Curriculum learning with only {num_epochs} epochs. Warmup may exceed training length.",
                recommendation="Disable curriculum for short training runs, or increase epochs to ≥10",
                reason="§10.1 'When NOT to use': Short training runs don't benefit from curriculum scheduling."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §12 Schedulers — One-Cycle for pretrain, warmup ratio
    # ─────────────────────────────────────────────────────────────────────────
    def _check_scheduler_config(self, config: dict):
        lr_scheduler = config.get("lr_scheduler", "cosine")
        warmup_steps = config.get("warmup_steps", 2000)
        num_epochs = config.get("num_epochs", 100)
        paradigm = config.get("paradigm", "SHADA Pipeline")

        # One-Cycle for pretrain = bad
        if lr_scheduler == "onecycle" and paradigm in ["SHADA Pipeline", "Contrastive SSL"]:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="lr_scheduler",
                md_reference="§12.2 One-Cycle Policy",
                message="One-Cycle scheduler is for fine-tuning only, not pre-training.",
                recommendation="Use 'cosine' or 'plateau' for pretrain phase; 'onecycle' for finetune",
                reason="§12.2 'When NOT to use': One-Cycle can destabilise pre-training from scratch."
            )

        # Warmup consuming too much
        # Estimate total steps
        steps_per_epoch = 100
        total_steps = num_epochs * steps_per_epoch

        if warmup_steps > total_steps * 0.3:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="warmup_steps",
                md_reference="§12.1 Cosine Decay + §12 Learning Rate Schedulers",
                message=f"Warmup steps ({warmup_steps}) consume >30% of estimated training ({total_steps} steps).",
                recommendation=f"Reduce warmup_steps to {max(500, int(total_steps * 0.1))}",
                reason="§12 documents that excessive warmup wastes training budget before full LR is reached."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §15.4 Four-Phase Pipeline — Epochs per phase
    # ─────────────────────────────────────────────────────────────────────────
    def _check_epochs_config(self, config: dict):
        num_epochs = config.get("num_epochs", 10)
        paradigm = config.get("paradigm", "SHADA Pipeline")

        if paradigm == "SHADA Pipeline" and num_epochs < 20:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="num_epochs",
                md_reference="§15.4 Four-Phase Training Pipeline",
                message=f"{num_epochs} epochs with full SHADA Pipeline = ~{num_epochs//4} epochs per phase. Insufficient for convergence.",
                recommendation="Use num_epochs ≥ 50 for full pipeline, or select single phase (e.g., 'finetune')",
                reason="§15.4 documents 4 distinct phases; each needs sufficient epochs to converge."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §1.1 Model Tier — Dataset size matching
    # ─────────────────────────────────────────────────────────────────────────
    def _check_model_tier(self, config: dict, dataset_info: Optional[dict],
                          hardware_info: Optional[dict]):
        model_tier = config.get("model_tier", "nano")
        pretrained = config.get("pretrained_model", "None (Train from scratch)")

        num_samples = dataset_info.get("num_samples", float("inf")) if dataset_info else float("inf")
        vram_gb = hardware_info.get("vram_gb", 0) if hardware_info else 0

        # Small dataset + large tier = overkill
        if num_samples < 10000 and model_tier in ["large", "xl"]:
            self._add_alert(
                level=AlertLevel.WARNING,
                parameter="model_tier",
                md_reference="§1.1 Hierarchical Hybrid Encoder",
                message=f"Model tier '{model_tier}' is overkill for small dataset ({num_samples} samples).",
                recommendation="Use 'nano' or 'base' tier for <10K samples",
                reason="§1.1 + data-aware rules: Small datasets don't benefit from large models; risk overfitting."
            )

        # Large dataset + small tier = underfitting risk
        if num_samples > 500000 and model_tier == "nano":
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="model_tier",
                md_reference="§1.1 Hierarchical Hybrid Encoder",
                message=f"Model tier 'nano' may underfit large dataset ({num_samples} samples).",
                recommendation="Consider 'large' or 'xl' tier for >500K samples",
                reason="Large datasets can benefit from larger models' capacity."
            )

        # VRAM constraints
        tier_vram_requirements = {
            "nano": 2.0,
            "base": 4.0,
            "large": 12.0,
            "xl": 24.0,
        }

        if vram_gb > 0:
            required_vram = tier_vram_requirements.get(model_tier, 4.0)
            if vram_gb < required_vram:
                self._add_alert(
                    level=AlertLevel.CRITICAL,
                    parameter="model_tier",
                    md_reference="§1.1 + §15.1 Mixed-Precision",
                    message=f"Model tier '{model_tier}' requires ~{required_vram}GB VRAM. Your GPU has {vram_gb}GB.",
                    recommendation=f"Reduce to tier requiring ≤{vram_gb}GB, or enable mixed_precision='bf16'",
                    reason="Insufficient VRAM will cause OOM errors during training."
                )

        # Text-only task + Stage 1 CNN = dead weight
        task = config.get("task", "classification")
        if task == "lm" and pretrained == "None (Train from scratch)":
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="task",
                md_reference="§1.1 Hierarchical Hybrid Encoder",
                message="Text-only task: Stage 1 (ConvNeXt CNN) is unused dead weight.",
                recommendation="Consider loading a text-pretrained model (BERT, GPT) instead of training from scratch",
                reason="§1.1 'When NOT to use': Pure text-only tasks bypass the convolutional Stage 1."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §15.2 Gradient Accumulation — Minimum effective batch
    # ─────────────────────────────────────────────────────────────────────────
    def _check_gradient_accumulation(self, config: dict):
        grad_acc = config.get("gradient_accumulation_steps", 1)
        batch_size = config.get("batch_size", 16)
        effective_batch = batch_size * grad_acc

        # Already checked in _check_batch_size; add VRAM-specific advice
        if grad_acc >= 16:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="gradient_accumulation_steps",
                md_reference="§15.2 Gradient Accumulation",
                message=f"Gradient accumulation {grad_acc} is very high. Training will be slower due to multiple backward passes.",
                recommendation="Consider reducing batch_size or using mixed_precision to fit larger batches",
                reason="§15.2: High accumulation adds overhead; fitting larger physical batches is more efficient."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §12 Warmup — Absolute step count
    # ─────────────────────────────────────────────────────────────────────────
    def _check_warmup_config(self, config: dict):
        warmup_steps = config.get("warmup_steps", 2000)

        if warmup_steps == 0:
            self._add_alert(
                level=AlertLevel.INFO,
                parameter="warmup_steps",
                md_reference="§12.1 Cosine Decay with Linear Warmup",
                message="No warmup configured. Large initial updates may destabilise early training.",
                recommendation="Set warmup_steps ≥ 1000 for stable training initiation",
                reason="§12.1 documents warmup prevents gradient explosions from large updates on randomly initialised parameters."
            )

    # ─────────────────────────────────────────────────────────────────────────
    # §16 Model Compression — Pruning + Quantization interaction
    # ─────────────────────────────────────────────────────────────────────────
    def _check_pruning_quantization(self, config: dict):
        # Pruning and quantization are typically applied post-training
        # For now, just check if user has unrealistic expectations
        pass  # Future: add checks when pruning config is exposed in UI


def validate_config(config: dict, dataset_info: Optional[dict] = None,
                    hardware_info: Optional[dict] = None) -> List[dict]:
    """
    Convenience function: run validation and return alerts.

    Args:
        config: SHADAConfig dict from UI
        dataset_info: Optional dict with dataset metadata
        hardware_info: Optional dict with hardware metadata

    Returns:
        List of alert dicts
    """
    validator = SHADAConfigValidator()
    return validator.validate(config, dataset_info, hardware_info)
