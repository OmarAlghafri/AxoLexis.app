
import torch
import sys
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

def test_image_forward():
    cfg = SHADAConfig()
    model = HierarchicalEncoder(cfg)
    
    B, C, H, W = 2, 3, 224, 224
    x = torch.randn(B, C, H, W)
    
    print(f"Input shape: {x.shape}")
    out = model.forward_image(x)
    
    # Patch embedding stride 4 -> 56x56
    # Stage 1: ConvNeXt (no downsampling) -> 56x56
    # Stage 2: d1 (downsample) -> 28x28
    # Stage 3: d2 (downsample) -> 14x14
    # Stage 4: d3 (downsample) -> 7x7
    
    for i, (sz_h, sz_w) in enumerate(out["spatial_sizes"]):
        print(f"Stage {i+1} spatial: {sz_h}x{sz_w}")
        
    final_h, final_w = out["spatial_sizes"][-1]
    if final_h == 7 and final_w == 7:
        print("Success: Image downsampling preserved.")
    else:
        print(f"Failure: Expected 7x7 at stage 4, got {final_h}x{final_w}")

if __name__ == "__main__":
    test_image_forward()
