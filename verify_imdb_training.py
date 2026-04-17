
import os
import sys
import torch
from pathlib import Path

# Add application to sys.path
app_path = Path(r"f:\my projects\AxoLexis\application")
if str(app_path) not in sys.path:
    sys.path.append(str(app_path))

from models.model_factory import build_model, get_trainer
from data.data_loader import build_dataloaders

def verify_pipeline():
    print("========== AxoLexis Headless Verification (IMDB BERT-Base) ==========")
    
    # 1. Setup Config
    csv_path = r"f:\my projects\AxoLexis\IMDB Dataset.csv"
    if not os.path.exists(csv_path):
        print(f"[ERROR] CSV not found at {csv_path}")
        return

    config = {
        "model_tier": "nano",
        "task": "classification",
        "pretrained_model": "BERT-Base (NLP)",
        "paradigm": "SHADA",
        "batch_size": 2, # Smaller for verification
        "learning_rate": 5e-5,
        "num_epochs": 1,
        "device": "cuda" if torch.cuda.is_available() else "cpu",
        "mixed_precision": "fp16",
        "use_wandb": False,
        "output_dir": "./test_output"
    }
    
    print(f"[INFO] Using device: {config['device']}")

    # 2. Build Dataloaders (with CORRECT tokenizer)
    try:
        # Crucial: tokenizer MUST match the model's vocabulary
        train_dl, val_dl = build_dataloaders(
            train_path=csv_path,
            val_path="",
            data_format="csv",
            batch_size=config["batch_size"],
            val_split=0.2,
            nrows=100,
            tokenizer_name="bert-base-uncased"
        )
        print(f"[INFO] Dataloaders built. Train batches: {len(train_dl)}")
    except Exception as e:
        print(f"[ERROR] Failed to build dataloaders: {e}")
        return

    # 3. Build Model
    print(f"[INFO] Building model: {config['pretrained_model']}...")
    try:
        model, shahad_cfg, stats, mod = build_model(config)
        trainer = get_trainer(model, shahad_cfg, train_dl, val_dl, mod)
        print(f"[INFO] Model and Trainer initialized.")
    except Exception as e:
        print(f"[ERROR] Failed to build model: {e}")
        import traceback
        traceback.print_exc()
        return

    # 4. Run verification step
    print(f"[INFO] Running verification step...")
    try:
        batch = next(iter(train_dl))
        
        # Test forward pass
        trainer.model.train()
        print(f"[DEBUG] input_ids sum: {batch['input_ids'].sum()}")
        print(f"[DEBUG] max index: {batch['input_ids'].max()}")
        
        # Use CPU if it's easier to debug asserts, but keep CUDA for now
        ids = batch["input_ids"].to(trainer.device)
        attn = batch["attention_mask"].to(trainer.device)
        labels = batch["labels"].to(trainer.device)
        
        # We need to pass attention mask too! 
        # But our patched forward currently only takes input_ids as x.
        # Let's see if it works without passing mask explicitly first.
        outputs = trainer.model.forward_task(ids, "text", "classification")
        print(f"[SUCCESS] Forward pass successful.")
        
        if "logits" in outputs:
            print(f"[DEBUG]   Logits shape: {outputs['logits'].shape}")
            print(f"[DEBUG]   Labels shape: {batch['labels'].shape}")
        
        # Run trainer step
        print("[INFO] Executing trainer _train_step...")
        info = trainer._train_step(batch, "finetune", 0)
        print(f"[SUCCESS] Step info: {info}")
        
    except Exception as e:
        print(f"[ERROR] Training step failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n[COMPLETE] Pipeline verification successful!")

if __name__ == "__main__":
    verify_pipeline()
