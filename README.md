# AxoLexis — SHADA Model Training Desktop Application

A fully-featured PyQt6 desktop trainer for the **SHADA** (Self-supervised · Hierarchical · Adaptive · Deep · Algorithm) model, featuring real-time loss/accuracy plots, multi-phase training control, intelligent model selection, and comprehensive quality validation.

---

## Project Structure

```
application/
├── main_enhanced.py              ← Core Application (v1.0.0-beta)
├── AxoLexis.py                   ← Application Launcher
├── requirements.txt               ← Python dependencies
├── README.md
├── app_icon.ico                  ← Application icon
├── version.txt                   ← Version information
├── ui/
│   ├── enhanced_main_window.py  ← Main window with intelligent features
│   ├── enhanced_model_panel.py  ← Enhanced model configuration
│   ├── theme_manager.py          ← Theme system (light/dark/premium)
│   ├── training_goal_dialog.py   ← Training goals configuration
│   ├── style.qss                  ← Dark theme stylesheet
│   ├── style_light.py             ← Light theme
│   ├── style_dark.py              ← Dark theme
│   ├── style_premium.py           ← Premium theme
│   ├── main_window.py             ← Legacy main window
│   ├── data_panel.py             ← Data file selection
│   ├── model_panel.py            ← Model tier + hyper-parameters
│   ├── training_panel.py         ← Start/Stop/Save controls
│   ├── plots_panel.py             ← Real-time pyqtgraph charts
│   ├── evaluation_panel.py       ← Model evaluation & metrics
│   └── log_panel.py              ← Coloured console output
├── training/
│   └── trainer_thread.py         ← QThread training worker
├── models/
│   ├── model_factory.py          ← Builds SHADA model from config
│   ├── enhanced_model_registry.py ← Enhanced model registry
│   ├── model_download_manager.py  ← Model download & caching
│   └── smart_config.py            ← Smart configuration
├── intelligent_training_integration.py  ← Intelligent training system
├── intelligent_model_selector.py         ← AI model selector
├── intelligent_quality_checker.py        ← Data quality validation
├── auto_pipeline.py                      ← AutoML pipeline logic
├── training_transparency_logger.py      ← Training transparency
├── runtime_validator.py                  ← Runtime validation
├── setup_updater.py                     ← GUI setup tool
└── data/
    └── data_loader.py          ← Data loading utilities
```

---

## Quick Start

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
python AxoLexis.py
```

> **Note:** The application includes a self-bootstrapping launcher (`AxoLexis.py`) that will automatically create a virtual environment (`venv/`) and install all required dependencies on the first run.

---

## New Features (v1.0.0-beta)

### Intelligent Training System
- **AI Model Selection**: Automatically selects optimal model based on data characteristics
- **Quality Validation**: Comprehensive data quality checking before training
- **AutoML Integration**: Automated hyperparameter optimization
- **Training Transparency**: Full logging and tracking of training progress

### Enhanced UI
- **Theme System**: Light, Dark, and Premium themes
- **Training Goals**: Set and track training objectives
- **Model Evaluation**: Comprehensive evaluation metrics and visualization
- **Enhanced Controls**: Improved training phase management

### Validation & Quality
- **Runtime Validator**: Validates system requirements before training
- **Smart Configuration**: Intelligent parameter suggestions
- **Model Download Manager**: Automatic model downloading and caching

---

## Using the Application

| Panel | Description |
|-------|-------------|
| **Data** | Browse for CSV / image folder / `.npy` file. Leave blank to use the built-in synthetic demo dataset |
| **Model & Hyper-Parameters** | Select model tier (`nano → xl`), task, optimizer, epochs, batch size, LR, LoRA rank, etc. |
| **Training Controls** | Choose a training phase (`pretrain`, `mtl`, `finetune`, `deploy`, `full_pipeline`), then click **Start Training** |
| **Training Charts** | Live updates per training step — train loss, val loss, val accuracy, LR, gradient norm |
| **Evaluation** | Comprehensive model evaluation with multiple metrics |
| **Console Log** | Colour-coded per-step log output |

### Saving a model
Click **Save Model…** after training completes to export a `.pt` checkpoint to any location.

---

## Build a Windows .exe (optional)

### Install PyInstaller
```powershell
pip install pyinstaller
```

### Package the app
```powershell
cd "f:\my projects\AxoLexis\application"
pyinstaller --noconfirm --onefile --windowed `
  --add-data "ui/style.qss;ui" `
  --add-data "ui/style_light.py;ui" `
  --add-data "ui/style_dark.py;ui" `
  --add-data "ui/style_premium.py;ui" `
  --name "AxoLexis_Trainer" `
  main_enhanced.py
```

The executable will be at:
```
application/dist/AxoLexis_Trainer.exe
```

> **Note:** The `.exe` packages only the *launcher*. The SHADA model code and its dependencies (PyTorch, NumPy, etc.) must still be present in the environment.

---

## Supported Data Formats

| Format | How to Select |
|--------|--------------|
| **Synthetic (demo)** | Leave "Training Data" blank, or select `Synthetic (demo)` in the format dropdown |
| **Images** | Point to a folder with class subfolders (ImageNet-style) or a flat folder of images |
| **CSV** | Columns = features; **last column** = integer class label |
| **NumPy `.npy`** | Shape `(N, F+1)` — last column = label |
| **NumPy `.npz`** | Must contain keys `X` (features) and `y` (labels) |

---

## Dependencies

| Package | Purpose |
|---------|---------|
| `PyQt6` | Desktop UI framework |
| `pyqtgraph` | Real-time GPU-accelerated plots |
| `torch` | Model training (SHADA) |
| `numpy` | Numerical data loading |
| `Pillow` | Image loading |
| `pyinstaller` | `.exe` packaging (optional) |

---

## Notes

- On **CPU**, use `Mixed Precision: fp32` (bf16/fp16 require CUDA).
- Training runs in a **background QThread** — the UI stays fully responsive.
- Model tier `nano` is recommended for testing; `base`/`large`/`xl` require more VRAM.
- The intelligent training system will automatically validate your data before training.