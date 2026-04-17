
import torch
import sys
import os
from pathlib import Path

# Add Algorithem to path
algo_dir = Path(r"f:\my projects\AxoLexis\Algorithem")
sys.path.insert(0, str(algo_dir))

try:
    from shada_core import HierarchicalEncoder, SHADAConfig
except ImportError:
    import importlib.util
    spec = importlib.util.spec_from_file_location("shada_core", algo_dir / "Trainig code.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    HierarchicalEncoder = mod.HierarchicalEncoder
    SHADAConfig = mod.SHADAConfig

def test_text_forward():
    cfg = SHADAConfig()
    model = HierarchicalEncoder(cfg)
    
    B, N, D = 2, 16, cfg.encoder_dims[1]
    x = torch.randn(B, N, D)
    
    print(f"Input shape: {x.shape}")
    out = model.forward_text(x)
    
    seq_out = out["sequence_output"]
    print(f"Output shape: {seq_out.shape}")
    
    # N + 1 because of CLS token
    expected_len = N + 1
    if seq_out.shape[1] == expected_len:
        print("Success: Sequence length preserved.")
    else:
        print(f"Failure: Sequence length changed to {seq_out.shape[1]}")
        
    for i, feat in enumerate(out["stage_features"]):
        print(f"Stage {i+2} shape: {feat.shape}")

if __name__ == "__main__":
    test_text_forward()
