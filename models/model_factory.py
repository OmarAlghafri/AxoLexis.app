"""
Model Factory — builds SHAHAD model from UI config dict.
Adds the project Algorithem directory to sys.path so the original
training code is imported directly (no duplication).
"""

import sys
import os
from pathlib import Path


def _ensure_algorithm_on_path():
    """Add the SHAHAD source directory to Python path."""
    # Walk up from application/ to find Algorithem/
    here = Path(__file__).resolve().parent.parent.parent  # AxoLexis/
    algo = here / "Algorithem"
    if algo.exists() and str(algo) not in sys.path:
        sys.path.insert(0, str(algo))


def build_model(cfg: dict):
    """
    Build a SHADAModel + SHADAConfig from the UI config dict.
    Returns (model, shahad_cfg).
    """
    _ensure_algorithm_on_path()

    try:
        # Import from the original SHAHAD training code
        from importlib import import_module
        import importlib.util, types

        # Load 'Trainig code.py' (note the typo in filename)
        algo_dir = Path(__file__).resolve().parent.parent.parent / "Algorithem"
        spec = importlib.util.spec_from_file_location(
            "shahad_core", algo_dir / "Trainig code.py"
        )
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)

        create_model   = mod.create_model
        SHADAConfig    = mod.SHADAConfig
        model_stats    = mod.model_stats

    except Exception as e:
        raise RuntimeError(
            f"Could not import SHAHAD training code.\n"
            f"Make sure 'Trainig code.py' exists at:\n"
            f" f:\\my projects\\AxoLexis\\Algorithem\\Trainig code.py\n\n"
            f"Error: {e}"
        ) from e

    tier = cfg.get("model_tier", "nano")
    task = cfg.get("task", "classification")

    num_classes = {"classification": 10, "detection": 80, "segmentation": 150, "lm": 50257}

    paradigm = cfg.get("paradigm", "SHADA Pipeline")

    overrides = dict(
        tasks                        = [task],
        num_classes                  = {task: num_classes.get(task, 10)},
        pretrained_model             = cfg.get("pretrained_model", "None (Train from scratch)"),
        paradigm                     = paradigm,
        optimizer                    = cfg.get("optimizer", "adamw"),
        num_epochs                   = cfg.get("num_epochs", 10),
        batch_size                   = cfg.get("batch_size", 16),
        base_lr                      = cfg.get("base_lr", 1e-4),
        weight_decay                 = cfg.get("weight_decay", 0.05),
        warmup_steps                 = cfg.get("warmup_steps", 200),
        gradient_accumulation_steps  = cfg.get("gradient_accumulation_steps", 1),
        mixed_precision              = cfg.get("mixed_precision", "fp32"),
        lora_rank                    = cfg.get("lora_rank", 16),
        lora_alpha                   = cfg.get("lora_alpha", 32.0),
        use_rl                       = cfg.get("use_rl", False),
        rl_algorithm                 = cfg.get("rl_algorithm", "dpo"),
        use_adversarial              = cfg.get("use_adversarial", False),
        use_mtl                      = cfg.get("use_mtl", True),
        output_dir                   = cfg.get("output_dir", "./shahad_output"),
        log_every                    = 5,
        eval_every                   = 50,
        save_every                   = 500,
    )

    # ── SHADA Optimized Parameters (Activated only when SHADA paradigm is chosen) ──
    if paradigm == "SHADA Pipeline":
        overrides.update(dict(
            lr_scheduler="plateau",
            eval_metric="f1_macro",
            early_stopping_patience=5,
            freeze_pretrained=False,
        ))

    model, shahad_cfg = create_model(tier=tier, **overrides)
    stats = model_stats(model)
    return model, shahad_cfg, stats, mod


def get_trainer(model, shahad_cfg, train_dl, val_dl, mod):
    """Instantiate SHADATrainer from the imported module."""
    return mod.SHADATrainer(model, shahad_cfg, train_dl, val_dl)
