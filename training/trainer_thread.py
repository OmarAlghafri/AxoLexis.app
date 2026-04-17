"""
TrainerThread — runs SHAHAD training in a QThread so the UI stays responsive.

Key responsibilities:
  • Build model + dataloaders from UI config
  • Run phase(s) via SHAHADTrainer
  • Emit per-step signals for live plots / log
  • Support stop requests and checkpoint saving
  • Validate configuration before training starts
"""

import time
import traceback
import json
import types
from pathlib import Path

import torch
from PyQt6.QtCore import QThread, pyqtSignal


class TrainerThread(QThread):
    # Signals
    sig_step          = pyqtSignal(dict)   # metrics dict per step
    sig_log           = pyqtSignal(str, str)  # (message, level)
    sig_finished      = pyqtSignal(str)
    sig_device        = pyqtSignal(str)
    sig_progress      = pyqtSignal(int)    # 0–100
    sig_config_alerts = pyqtSignal(list)   # List of config alert dicts

    def __init__(self, cfg: dict):
        super().__init__()
        self.cfg = cfg
        self._stop_flag = False
        self._trainer   = None
        self._model     = None

    def request_stop(self):
        self._stop_flag = True

    # ──────────────────────────────────────────────────────────────
    def run(self):
        try:
            self._run_training()
        except Exception:
            tb = traceback.format_exc()
            self.sig_log.emit(f"[ERROR] Training failed:\n{tb}", "error")
            self.sig_finished.emit("Error")

    # ──────────────────────────────────────────────────────────────
    def _get_hardware_info(self, device: str) -> dict:
        """Extract hardware information for config validation."""
        hw_info = {
            "device": device,
            "vram_gb": 0,
            "gpu_name": "",
        }
        
        if device == "cuda" and torch.cuda.is_available():
            try:
                hw_info["vram_gb"] = torch.cuda.get_device_properties(0).total_memory / (1024**3)
                hw_info["gpu_name"] = torch.cuda.get_device_name(0)
            except Exception:
                pass
        
        return hw_info

    def _validate_configuration(self, cfg: dict, dataset_info: dict, hardware_info: dict) -> bool:
        """
        Run SHADA config validator before training.
        Returns True if training can proceed, False if critical issues found.
        """
        try:
            from models.config_validator import validate_config
            
            alerts = validate_config(cfg, dataset_info, hardware_info)
            
            # Emit alerts to UI
            self.sig_config_alerts.emit(alerts)
            
            # Log alerts
            critical_count = sum(1 for a in alerts if a["level"] == "CRITICAL")
            warning_count = sum(1 for a in alerts if a["level"] == "WARNING")
            info_count = sum(1 for a in alerts if a["level"] == "INFO")
            
            if alerts:
                self.sig_log.emit(
                    f"[CONFIG] Validation complete: {critical_count} critical, "
                    f"{warning_count} warnings, {info_count} info",
                    "warn" if critical_count > 0 else "info"
                )
                
                # Log critical alerts
                for alert in alerts:
                    if alert["level"] == "CRITICAL":
                        self.sig_log.emit(
                            f"[CRITICAL] {alert['parameter']}: {alert['message']}",
                            "error"
                        )
                    elif alert["level"] == "WARNING":
                        self.sig_log.emit(
                            f"[WARNING] {alert['parameter']}: {alert['message']}",
                            "warn"
                        )
            
            # Block training on critical issues
            if critical_count > 0:
                self.sig_log.emit(
                    "[CONFIG] Training blocked due to critical configuration issues. "
                    "Please fix the issues and restart.",
                    "error"
                )
                return False
            
            return True
            
        except Exception as e:
            self.sig_log.emit(f"[CONFIG] Validation error: {e}", "warn")
            return True  # Allow training to proceed if validation fails

    # ──────────────────────────────────────────────────────────────
    def _run_training(self):
        cfg = self.cfg

        # 1) Device
        device = "cuda" if torch.cuda.is_available() else "cpu"
        self.sig_device.emit(device.upper())
        self.sig_log.emit(f"[INFO] Device: {device.upper()}", "info")

        # 2) Build dataloaders
        self.sig_log.emit("[INFO] Building dataset…", "info")
        from data.data_loader import build_dataloaders
        train_dl, val_dl = build_dataloaders(
            train_path  = cfg.get("train_path", ""),
            val_path    = cfg.get("val_path", ""),
            data_format = cfg.get("data_format", "Synthetic (demo)"),
            batch_size  = cfg.get("batch_size", 16),
        )
        n_tr = len(train_dl.dataset)
        n_va = len(val_dl.dataset) if val_dl else 0
        self.sig_log.emit(
            f"[INFO] Dataset — train: {n_tr} samples, val: {n_va} samples", "info"
        )

        # 2.5) Validate configuration
        self.sig_log.emit("[CONFIG] Running configuration validation…", "info")
        
        # Build dataset info with actual counts
        dataset_info = {
            "num_samples": n_tr,
            "num_classes": cfg.get("num_classes", {}).get(cfg.get("task", "classification"), 10),
            "is_imbalanced": False,
            "has_noisy_labels": False,
        }
        
        # Try to detect class imbalance from dataloader
        try:
            if hasattr(train_dl.dataset, 'targets') and train_dl.dataset.targets is not None:
                targets = train_dl.dataset.targets
                if isinstance(targets, torch.Tensor):
                    targets = targets.tolist()
                unique_classes = len(set(targets))
                dataset_info["num_classes"] = unique_classes

                # Check imbalance
                from collections import Counter
                counts = Counter(targets)
                if len(counts) > 1:
                    max_count = max(counts.values())
                    min_count = min(counts.values())
                    dataset_info["is_imbalanced"] = (max_count / min_count) > 5.0
        except Exception:
            pass  # Use defaults if detection fails
        
        hardware_info = self._get_hardware_info(device)

        if not self._validate_configuration(cfg, dataset_info, hardware_info):
            self.sig_finished.emit("Configuration Error")
            return

        # 3) Build model
        self.sig_log.emit("[INFO] Building SHAHAD model…", "info")
        from models.model_factory import build_model, get_trainer
        model, shahad_cfg, stats, mod = build_model(cfg)
        self._model = model

        self.sig_log.emit(
            f"[INFO] Model tier: {cfg.get('model_tier','nano')} | "
            f"Total params: {stats['total_params']:,} | "
            f"Trainable (LoRA): {stats['trainable_params']:,} ({stats['trainable_pct']:.1f}%)",
            "info"
        )

        # 4) Trainer
        trainer = get_trainer(model, shahad_cfg, train_dl, val_dl, mod)
        self._trainer = trainer

        # Patch the trainer to emit signals every N steps
        phase_arg = cfg.get("phase", "full_pipeline")
        self.sig_log.emit(f"[INFO] Starting phase: {phase_arg}", "info")

        total_steps = shahad_cfg.num_epochs * len(train_dl)
        done_steps  = 0

        # ── Phase dispatch ────────────────────────────────────────
        if phase_arg == "full_pipeline":
            paradigm = getattr(shahad_cfg, "paradigm", "SHADA Pipeline")
            if paradigm == "SHADA Pipeline":
                phases = [
                    ("pretrain", max(1, total_steps // 4)),
                    ("mtl",      max(1, total_steps // 4)),
                    ("finetune", max(1, total_steps // 4)),
                    ("deploy",   max(1, total_steps // 4)),
                ]
            elif paradigm == "Contrastive SSL":
                phases = [
                    ("pretrain", max(1, total_steps // 2)),
                    ("finetune", max(1, total_steps // 2)),
                ]
            else: # Standard Supervised
                phases = [
                    ("finetune", max(1, int(total_steps * 0.8))),
                    ("deploy",   max(1, int(total_steps * 0.2))),
                ]
        else:
            phases = [(phase_arg, total_steps)]

        grand_total = sum(s for _, s in phases)

        for phase_name, num_steps in phases:
            if self._stop_flag:
                break
            self.sig_log.emit(
                f"[INFO] ── Phase: {phase_name.upper()} ({num_steps} steps) ──", "info"
            )

            # Monkey-patch the trainer's _train_step to intercept signals
            original_train_step = trainer._train_step

            def patched_step(batch, phase, accum_i,
                             _orig=original_train_step,
                             _done=done_steps):
                info = _orig(batch, phase, accum_i)
                info["step"] = trainer.global_step

                # Emit signal
                self.sig_step.emit(dict(info))

                # Log every log_every steps
                if trainer.global_step % shahad_cfg.log_every == 0:
                    loss = info.get("loss/total", info.get("ssl/total_ssl", 0))
                    lr   = info.get("lr", 0)
                    gn   = info.get("grad_norm", 0)
                    self.sig_log.emit(
                        f"[STEP {trainer.global_step:6d}] "
                        f"loss={loss:.4f}  lr={lr:.2e}  gnorm={gn:.3f}",
                        "debug"
                    )

                # Progress
                nonlocal done_steps
                done_steps += 1
                pct = int(min(100, done_steps / max(grand_total, 1) * 100))
                self.sig_progress.emit(pct)

                return info

            trainer._train_step = patched_step

            def patched_run_phase(self_t, phase, num_steps, use_rl=False,
                                  _st=self._stop_flag):
                """Delegates to original but checks stop flag between batches."""
                self_t.model.train()
                accum_i = 0
                done    = 0
                for _epoch in range(self_t.cfg.num_epochs):
                    for batch in self_t.train_dl:
                        if done >= num_steps or self._stop_flag:
                            break
                        info = (self_t._rl_step(batch) if use_rl and self_t.cfg.use_rl
                                else self_t._train_step(batch, phase, accum_i))
                        for k, v in info.items():
                            if isinstance(v, (int, float)):
                                self_t.history[k].append(v)
                        if self_t.cfg.use_curriculum and hasattr(self_t, "curriculum"):
                            self_t.curriculum.tick()
                        accum_i = (accum_i + 1) % self_t.cfg.gradient_accumulation_steps
                        done += 1
                        # Periodic val
                        if (self_t.global_step % self_t.cfg.eval_every == 0
                                and self_t.val_dl):
                            vm = self_t.evaluate(self_t.val_dl, phase)
                            self.sig_step.emit({**vm, "step": self_t.global_step})
                            self.sig_log.emit(
                                f"[VAL  {self_t.global_step:6d}] {vm}", "success"
                            )
                    if done >= num_steps or self._stop_flag:
                        break
                return {}

            trainer.run_phase = types.MethodType(patched_run_phase, trainer)

            trainer.run_phase(phase_name, num_steps)

        # 5) Save final checkpoint
        if not self._stop_flag:
            out_dir = Path(shahad_cfg.output_dir)
            out_dir.mkdir(parents=True, exist_ok=True)
            final_path = str(out_dir / "final.pt")
            trainer._save(final_path)
            self.sig_log.emit(f"[INFO]  Final checkpoint saved → {final_path}", "success")
            
            # 6) Automated Evaluation
            if "eval_config" in cfg:
                self._run_evaluation(trainer, val_dl)
                
            self.sig_finished.emit("Complete")
        else:
            self.sig_finished.emit("Stopped by user")

    def _run_evaluation(self, trainer, val_dl):
        """Run post-training evaluation suite."""
        ec = self.cfg.get("eval_config", {})
        self.sig_log.emit("[EVAL] Running automated evaluation suite...", "info")
        
        results = {}
        
        # 1. Performance Benchmark
        if ec.get("eval_latency"):
            self.sig_log.emit("[EVAL] Benchmarking inference latency...", "info")
            start = time.time()
            with torch.no_grad():
                for i, batch in enumerate(val_dl):
                    if i > 10: break # Benchmark first few batches
                    trainer.model_task_forward(batch, "test")
            elapsed = (time.time() - start) / 11.0 # avg per batch
            results["latency_ms_per_batch"] = elapsed * 1000
            self.sig_log.emit(f"[EVAL] Avg Latency: {elapsed*1000:.2f} ms/batch", "success")

        # 2. Metrics based on model evaluation logic
        if val_dl:
            metrics = trainer.evaluate(val_dl, "test")
            results.update(metrics)
            for k, v in metrics.items():
                self.sig_log.emit(f"[EVAL] Metric {k}: {v}", "success")

        # 3. Report Saving
        if ec.get("save_json"):
            out_dir = Path(self.cfg.get("output_dir", "./shahad_output"))
            report_path = out_dir / "evaluation_report.json"
            with open(report_path, "w") as f:
                json.dump(results, f, indent=4)
            self.sig_log.emit(f"[INFO] Evaluation report saved to {report_path}", "info")

    # ──────────────────────────────────────────────────────────────
    def save_checkpoint(self, path: str):
        """Save checkpoint to user-chosen path."""
        if self._trainer:
            try:
                self._trainer._save(path)
            except Exception as e:
                self.sig_log.emit(f"[ERROR] Save failed: {e}", "error")
        elif self._model:
            torch.save({"model": self._model.state_dict()}, path)
