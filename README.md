# AxoLexis — SHAHAD Model Training Desktop Application

A fully-featured PyQt6 desktop trainer for the **SHAHAD** (Self-supervised Hierarchical Adaptive Hybrid Algorithm for Deep Learning) model, featuring real-time loss/accuracy plots, multi-phase training control, and model saving.

---

##  Project Structure

```
application/
├── main.py                      ← Entry point
├── requirements.txt             ← Python dependencies
├── README.md
├── ui/
│   ├── style.qss               ← Dark theme stylesheet
│   ├── main_window.py          ← Main window shell
│   ├── data_panel.py           ← Data file selection
│   ├── model_panel.py          ← Model tier + hyper-parameters
│   ├── training_panel.py       ← Start/Stop/Save controls
│   ├── plots_panel.py          ← Real-time pyqtgraph charts
│   └── log_panel.py            ← Coloured console output
├── training/
│   └── trainer_thread.py       ← QThread training worker
├── models/
│   └── model_factory.py        ← Builds SHAHAD model from config
└── data/
    └── data_loader.py          ← CSV / Image / NumPy / Synthetic loaders
```

> **Training logic** is imported directly from `../Algorithem/Trainig code.py` — no code is duplicated.

---

##  Quick Start

### 1. Install dependencies

```powershell
cd "f:\my projects\AxoLexis\application"
pip install -r requirements.txt
```

> **PyTorch** must be installed separately. Visit https://pytorch.org/get-started for the correct command for your CUDA version, e.g.:
> ```powershell
> pip install torch torchvision --index-url https://download.pytorch.org/whl/cu121
> # or CPU-only:
> pip install torch torchvision
> ```

### 2. Run the application

```powershell
cd "f:\my projects\AxoLexis\application"
python main.py
```

---

##  Using the Application

| Panel | Description |
|-------|-------------|
| ** Data** | Browse for CSV / image folder / `.npy` file. Leave blank to use the built-in synthetic demo dataset |
| ** Model & Hyper-Parameters** | Select model tier (`nano → xl`), task, optimizer, epochs, batch size, LR, LoRA rank, etc. |
| ** Training Controls** | Choose a training phase (`pretrain`, `mtl`, `finetune`, `deploy`, `full_pipeline`), then click ** Start Training** |
| ** Training Charts** | Live updates per training step — train loss, val loss, val accuracy, LR, gradient norm |
| ** Console Log** | Colour-coded per-step log output |

### Saving a model
Click ** Save Model…** after training completes to export a `.pt` checkpoint to any location.

---

##  Build a Windows .exe (optional)

### Install PyInstaller
```powershell
pip install pyinstaller
```

### Package the app
```powershell
cd "f:\my projects\AxoLexis\application"
pyinstaller --noconfirm --onefile --windowed `
  --add-data "ui/style.qss;ui" `
  --name "AxoLexis_Trainer" `
  main.py
```

The executable will be at:
```
application/dist/AxoLexis_Trainer.exe
```

> **Note:** The `.exe` packages only the *launcher*. The SHAHAD model code (`Algorithem/Trainig code.py`) and its dependencies (PyTorch, NumPy, etc.) must still be present in the environment. For a fully standalone `.exe`, add `--add-data "../Algorithem;Algorithem"` and ensure all heavy dependencies are included with `--collect-all torch`.

---

##  Supported Data Formats

| Format | How to Select |
|--------|--------------|
| **Synthetic (demo)** | Leave "Training Data" blank, or select `Synthetic (demo)` in the format dropdown |
| **Images** | Point to a folder with class subfolders (ImageNet-style) or a flat folder of images |
| **CSV** | Columns = features; **last column** = integer class label |
| **NumPy `.npy`** | Shape `(N, F+1)` — last column = label |
| **NumPy `.npz`** | Must contain keys `X` (features) and `y` (labels) |

---

##  Dependencies

| Package | Purpose |
|---------|---------|
| `PyQt6` | Desktop UI framework |
| `pyqtgraph` | Real-time GPU-accelerated plots |
| `torch` | Model training (SHAHAD) |
| `numpy` | Numerical data loading |
| `Pillow` | Image loading |
| `pyinstaller` | `.exe` packaging (optional) |

---

##  Notes

- On **CPU**, use `Mixed Precision: fp32` (bf16/fp16 require CUDA).
- Training runs in a **background QThread** — the UI stays fully responsive.
- Model tier `nano` is recommended for testing; `base`/`large`/`xl` require more VRAM.
