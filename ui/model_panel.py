"""
Model Panel — model tier and all training hyper-parameters.
Redesigned: cleaner section headers, improved form layout, accordion dividers.
Includes Smart Config auto-tuner and SHADA-aware validation.
"""
import os
from PyQt6.QtWidgets import (
    QGroupBox, QVBoxLayout, QHBoxLayout, QLabel,
    QComboBox, QSpinBox, QDoubleSpinBox, QCheckBox,
    QFormLayout, QFrame, QScrollArea, QWidget,
    QPushButton, QDialog, QTextEdit, QMessageBox,
)
from PyQt6.QtCore import Qt, pyqtSignal
from models.model_registry import MODEL_REGISTRY


class ModelPanel(QGroupBox):
    sig_task_changed = pyqtSignal(str)

    def __init__(self):
        super().__init__(" Model & Hyper-Parameters")
        self._vram_gb = 0
        self._is_over_capacity = False
        self._data_panel_ref = None
        self._config_extra = {}
        self._build()
        self._connect_internal_signals()
        self._on_task_changed() # Initial update

    def set_data_panel(self, panel):
        """Set reference to data panel for dataset analysis."""
        self._data_panel_ref = panel

    def _build(self):
        # Outer layout
        main_ly = QVBoxLayout(self)
        main_ly.setContentsMargins(0, 0, 0, 0)
        main_ly.setSpacing(0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        
        content = QWidget()
        root = QVBoxLayout(content)
        root.setSpacing(30) # High spacing between cards
        root.setContentsMargins(30, 30, 30, 30)

        # ── Resource Monitoring ──
        self._warn_frame = QFrame()
        self._warn_frame.setObjectName("glassPanel")
        self._warn_frame.setVisible(False)
        self._warn_frame.setStyleSheet("background: rgba(239, 68, 68, 0.1); border: 1px solid rgba(239, 68, 68, 0.3);")
        warn_ly = QVBoxLayout(self._warn_frame)
        warn_title = QLabel("⚠️ HARDWARE CAPACITY WARNING")
        warn_title.setStyleSheet("color: #EF4444; font-weight: 800; font-size: 10pt;")
        self._warn_txt = QLabel("")
        self._warn_txt.setWordWrap(True)
        self._warn_txt.setStyleSheet("color: #F87171; font-size: 9pt;")
        warn_ly.addWidget(warn_title)
        warn_ly.addWidget(self._warn_txt)
        root.addWidget(self._warn_frame)

        # ── Section: Architecture ──
        self._tier = QComboBox()
        self._task = QComboBox()
        self._pretrained = QComboBox()
        root.addWidget(self._create_card("Architecture & Objective", "Define the model size and learning goal.", [
            ("Model Tier", self._tier),
            ("Primary Task", self._task),
            ("Base Model", self._pretrained)
        ]))
        
        self._tier.addItems([
            "10M - 100M Params (Ultra Light)",
            "100M - 1B Params (Balanced)",
            "1B - 7B Params (High Performance)",
            "7B - 34B+ Params (State-of-the-Art)"
        ])
        
        # ── Section: Optimizer ──
        self._paradigm = QComboBox()
        self._opt = QComboBox()
        self._mp = QComboBox()
        self._lr = QDoubleSpinBox()
        self._wd = QDoubleSpinBox()
        root.addWidget(self._create_card("Training Logic", "Optimization strategy and precision.", [
            ("Algorithm", self._paradigm),
            ("Optimizer", self._opt),
            ("Precision", self._mp),
            ("Learning Rate", self._lr),
            ("Weight Decay", self._wd)
        ]))
        
        self._paradigm.addItems(["SHADA Pipeline", "Standard Supervised", "Contrastive SSL"])
        self._opt.addItems(["adamw", "lion", "sgd", "rmsprop"])
        self._mp.addItems(["fp32", "fp16", "bf16"])
        self._lr.setRange(1e-7, 1.0); self._lr.setValue(1e-4); self._lr.setDecimals(7)
        self._wd.setRange(0.0, 1.0); self._wd.setValue(0.05); self._wd.setDecimals(4)

        # ── Section: Schedule ──
        self._epochs = QSpinBox()
        self._batch = QSpinBox()
        self._warmup = QSpinBox()
        self._grad_acc = QSpinBox()
        root.addWidget(self._create_card("Schedule & Pipeline", "Epochs, batching, and performance tuning.", [
            ("Epochs", self._epochs),
            ("Batch Size", self._batch),
            ("Warmup Steps", self._warmup),
            ("Grad Accumulation", self._grad_acc)
        ]))
        
        self._epochs.setRange(1, 1000); self._epochs.setValue(10)
        self._batch.setRange(1, 4096); self._batch.setValue(16)
        self._warmup.setRange(0, 10000); self._warmup.setValue(200)
        self._grad_acc.setRange(1, 128); self._grad_acc.setValue(1)

        # ── Section: LoRA & Advanced ──
        self._lora_r = QSpinBox()
        self._lora_a = QDoubleSpinBox()
        self._lora_r.setRange(1, 256); self._lora_r.setValue(16)
        self._lora_a.setRange(1.0, 512.0); self._lora_a.setValue(32.0)
        
        root.addWidget(self._create_card("Low-Rank Adaptation (LoRA)", "Memory-efficient fine-tuning parameters.", [
            ("Rank (r)", self._lora_r),
            ("Scaling Alpha (a)", self._lora_a)
        ]))

        # ── Section: Advanced ──
        adv_card = QFrame()
        adv_card.setObjectName("glassPanel")
        adv_ly = QVBoxLayout(adv_card)
        adv_ly.setSpacing(15)
        
        hdr = QLabel("ADVANCED CAPABILITIES")
        hdr.setObjectName("fieldLabel")
        sub = QLabel("Fine-tuning and robust learning toggles.")
        sub.setStyleSheet("color: #64748B; font-size: 8pt;")
        adv_ly.addWidget(hdr); adv_ly.addWidget(sub); adv_ly.addSpacing(10)
        
        check_grid = QHBoxLayout()
        self._use_rl = QCheckBox("RL (PPO/DPO)"); self._use_rl.setToolTip("Reinforcement Learning")
        self._use_adv = QCheckBox("Adversarial"); self._use_adv.setToolTip("Robustness training")
        self._use_mtl = QCheckBox("Multi-Task"); self._use_mtl.setChecked(True)
        self._use_curriculum = QCheckBox("Curriculum"); self._use_curriculum.setChecked(True)
        
        for chk in [self._use_rl, self._use_adv, self._use_mtl, self._use_curriculum]:
            check_grid.addWidget(chk)
        adv_ly.addLayout(check_grid)
        
        # RL & Curriculum Details (Hidden or disabled by default)
        self._rl_algo = QComboBox()
        self._rl_algo.addItems(["Proximal Policy Optimization (PPO)", "Direct Preference Optimization (DPO)"])
        self._curriculum_warmup = QSpinBox()
        self._curriculum_warmup.setRange(0, 100000); self._curriculum_warmup.setValue(5000)
        
        # We can add these to the advanced card or a sub-layout
        details_ly = QFormLayout()
        details_ly.addRow("RL Algorithm", self._rl_algo)
        details_ly.addRow("Curriculum Warmup", self._curriculum_warmup)
        adv_ly.addLayout(details_ly)
        
        root.addWidget(adv_card)

        # ── Actions ──
        btn_ly = QHBoxLayout()
        self._btn_smart_config = QPushButton("AUTO-TUNE PARAMETERS")
        self._btn_smart_config.setObjectName("btnPrimary")
        self._btn_smart_config.setFixedHeight(45)
        self._btn_smart_config.clicked.connect(self._run_smart_config)
        
        self._btn_validate = QPushButton("VALIDATE CONFIG")
        self._btn_validate.setObjectName("btnSecondary")
        self._btn_validate.setFixedHeight(45)
        self._btn_validate.clicked.connect(self._run_validation)
        
        btn_ly.addWidget(self._btn_validate, 1)
        btn_ly.addWidget(self._btn_smart_config, 1)
        root.addLayout(btn_ly)

        self._use_rl.toggled.connect(self._rl_algo.setEnabled)

        scroll.setWidget(content)
        main_ly.addWidget(scroll)

    def _create_card(self, title, subtitle, rows):
        card = QFrame()
        card.setObjectName("glassPanel")
        ly = QVBoxLayout(card)
        ly.setSpacing(12)
        
        hdr = QLabel(title.upper())
        hdr.setObjectName("fieldLabel")
        sub = QLabel(subtitle)
        sub.setStyleSheet("color: #64748B; font-size: 8pt;")
        
        ly.addWidget(hdr)
        ly.addWidget(sub)
        ly.addSpacing(10)
        
        form = QFormLayout()
        form.setSpacing(15)
        form.setFormAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        
        for label_text, widget in rows:
            lbl = QLabel(label_text)
            lbl.setStyleSheet("color: #94A3B8; font-weight: 600;")
            widget.setFixedHeight(38)
            form.addRow(lbl, widget)
            
        ly.addLayout(form)
        return card

    def _connect_internal_signals(self):
        self._task.currentTextChanged.connect(self._on_task_changed)
        self._pretrained.currentTextChanged.connect(self._on_model_changed)
        
        # Capacity triggers
        self._tier.currentIndexChanged.connect(self._check_capacity)
        self._pretrained.currentIndexChanged.connect(self._check_capacity)
        self._batch.valueChanged.connect(self._check_capacity)
        self._mp.currentIndexChanged.connect(self._check_capacity)
        self._use_rl.toggled.connect(self._check_capacity)

    def set_hardware_info(self, vram_gb: float):
        self._vram_gb = vram_gb
        self._check_capacity()

    def _check_capacity(self):
        if self._vram_gb <= 0: return # CPU or unknown
        
        # 1. Base cost by tier
        tier = self._tier.currentText()
        tier_costs = {
            "10M - 100M Params (Ultra Light)": 0.4,
            "100M - 1B Params (Balanced)": 1.2,
            "1B - 7B Params (High Performance)": 3.5,
            "7B - 34B+ Params (State-of-the-Art)": 7.5
        }
        usage = tier_costs.get(tier, 1.0)
        
        # 2. Add-on costs for specific models
        model = self._pretrained.currentText()
        if "LLaMA" in model or "Mistral" in model or "Mixtral" in model:
            usage += 7.0 # Minimum for 7B models
        elif "BERT" in model or "RoBERTa" in model:
            usage += 0.8
        elif "ViT" in model or "CLIP" in model:
            usage += 1.2
            
        # 3. Batch size factor
        batch = self._batch.value()
        precision = self._mp.currentText()
        p_factor = 1.0 if precision == "fp32" else 0.5
        
        # Heuristic increase
        usage += (batch * 0.15 * p_factor)
        
        # 4. Phase factor
        if self._use_rl.isChecked(): usage *= 1.4 # RL needs more memory (critic, ref model)
        
        self._is_over_capacity = (usage > self._vram_gb)
        
        # Update UI styling
        self._warn_frame.setVisible(self._is_over_capacity)
        
        # Color specific labels/widgets red
        red_style = "color: #FF5555; font-weight: 700;"
        normal_style = ""
        
        style = red_style if self._is_over_capacity else normal_style
        
        # Applying style to form labels for critical params
        # Note: We'd need to keep references to the labels if we want to change them directly via QSS
        # For now, let's update the widgets themselves with a border
        w_style = "border: 1px solid #FF3333; background: rgba(255,50,50,0.05);" if self._is_over_capacity else ""
        
        self._batch.setStyleSheet(w_style)
        self._tier.setStyleSheet(w_style)
        self._pretrained.setStyleSheet(w_style)
        
        if self._is_over_capacity:
            self._warn_txt.setText(
                f"Estimated usage: ~{usage:.1f} GB. Your GPU has {self._vram_gb:.1f} GB.\n\n"
                "This configuration is too heavy for your GPU(s). Training will likely crash.\n"
                "Recommendation: Reduce Batch Size/Tier, or switch to CPU for absolute stability."
            )

    def set_data_format(self, fmt: str):
        """Filter available tasks based on data format."""
        fmt = fmt.lower()
        
        # Determine available tasks for this format
        available_tasks = ["Classification (Images/Text)"] # Always available
        
        if "image" in fmt or "npy" in fmt or "npz" in fmt or "medical" in fmt:
            available_tasks += ["Object Detection", "Image Segmentation"]
        elif "csv" in fmt or "json" in fmt or "text" in fmt or "parquet" in fmt:
            available_tasks += ["Language Modeling (LLM Training)"]
        else:
            # Synthetic or unknown
            available_tasks += ["Language Modeling (LLM Training)", "Object Detection", "Image Segmentation"]

        # Update the task combo box
        prev_task = self._task.currentText()
        self._task.blockSignals(True)
        self._task.clear()
        self._task.addItems(available_tasks)
        
        idx = self._task.findText(prev_task)
        if idx >= 0:
            self._task.setCurrentIndex(idx)
        else:
            self._task.setCurrentIndex(0)
            
        self._task.blockSignals(False)
        self._on_task_changed()

    def _on_task_changed(self):
        task = self._task.currentText()

        # 1. Filter models based on task

        # Mapping task to allowed categories
        task_map = {
            "Classification (Images/Text)": ["Computer Vision (CNN)", "Vision Transformers (ViT)", "Natural Language Processing (NLP)", "Medical AI"],
            "Language Modeling (LLM Training)": ["Natural Language Processing (NLP)", "Multimodal (Vision + Language)"],
            "Object Detection": ["Detection & Segmentation"],
            "Image Segmentation": ["Detection & Segmentation", "Medical AI"]
        }
        
        allowed_cats = task_map.get(task, [])
        
        # Remember current selection
        current_model = self._pretrained.currentText()
        
        self._pretrained.blockSignals(True)
        self._pretrained.clear()
        self._pretrained.addItem("None (Train from scratch)")
        
        for category, subcats in MODEL_REGISTRY.items():
            if category in allowed_cats:
                self._pretrained.addItem(f"--- {category} ---")
                self._pretrained.model().item(self._pretrained.count() - 1).setEnabled(False)
                for subcat, models in subcats.items():
                    for m in models:
                        self._pretrained.addItem(m)
        
        # Restore selection if it's still in the list
        idx = self._pretrained.findText(current_model)
        if idx >= 0:
            self._pretrained.setCurrentIndex(idx)
        else:
            self._pretrained.setCurrentIndex(0)
            
        self._pretrained.blockSignals(False)
        self._on_model_changed()
        self.sig_task_changed.emit(task)

        # 2. Logic for RL: Only for Language Modeling
        if task == "lm":
            self._use_rl.setEnabled(True)
        else:
            self._use_rl.setChecked(False)
            self._use_rl.setEnabled(False)
            self._rl_algo.setEnabled(False)

        # 3. Logic for Adversarial: Usually for CV or NLP Classification
        if task in ["classification", "detection"]:
            self._use_adv.setEnabled(True)
        else:
            self._use_adv.setChecked(False)
            self._use_adv.setEnabled(False)

    def _on_model_changed(self):
        model_name = self._pretrained.currentText()
        task = self._task.currentText()
        
        # Logic for LoRA: Only for Transformers or Language Modeling
        is_transformer = any(x in model_name for x in ["BERT", "GPT", "LLaMA", "Mistral", "ViT", "Swin", "T5", "CLIP"])
        is_lm = (task == "Language Modeling (LLM Training)")
        
        if is_transformer or is_lm:
            self._lora_r.setEnabled(True)
            self._lora_a.setEnabled(True)
        else:
            self._lora_r.setEnabled(False)
            self._lora_a.setEnabled(False)
            
        # Logic for Mixed Precision: BF16 is better for LLMs
        if "LLaMA" in model_name or "Mistral" in model_name:
            # Suggest BF16
            idx = self._mp.findText("bf16")
            if idx >= 0: self._mp.setCurrentIndex(idx)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def _section_header(self, text: str) -> QLabel:
        lbl = QLabel(text.upper())
        lbl.setObjectName("sectionLabel")
        lbl.setStyleSheet(
            "color: #5559A0; font-size: 8pt; font-weight: 700; "
            "letter-spacing: 1.8px; background: transparent; "
            "padding-top: 8px; padding-bottom: 4px;"
        )
        return lbl

    def _lbl(self, text: str) -> QLabel:
        lbl = QLabel(text)
        lbl.setObjectName("fieldLabel")
        return lbl

    def _make_form(self) -> QFormLayout:
        f = QFormLayout()
        f.setLabelAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        f.setSpacing(10)
        f.setContentsMargins(0, 6, 0, 6)
        return f

    def _divider(self) -> QFrame:
        d = QFrame()
        d.setFrameShape(QFrame.Shape.HLine)
        d.setStyleSheet("color: #1E2040; max-height: 1px; margin: 4px 0;")
        return d

    def validate_config(self, train_path: str = "", data_format: str = "") -> tuple[bool, str]:
        """
        Validate the current configuration for compatibility.
        Returns (is_valid, warning_or_error_message).
        """
        issues = []
        fmt = data_format.lower()
        is_synthetic = "synthetic" in fmt or not train_path
        is_csv = "csv" in fmt or (train_path and train_path.lower().endswith(".csv"))
        is_image_folder = "image" in fmt or (train_path and os.path.isdir(train_path))
        
        task = self._task.currentText()
        paradigm = self._paradigm.currentText()
        model = self._pretrained.currentText()
        
        # 1. Modality / Task Compatibility
        if task == "Language Modeling (LLM Training)":
            if is_image_folder:
                issues.append("Language Modeling requires a text dataset (CSV), but an Image Folder is selected.")
        
        if task in ["Object Detection", "Image Segmentation"]:
            if is_csv and not is_synthetic:
                issues.append(f"{task} requires an Image Folder, but a CSV file is selected.")

        # 2. Paradigm checks
        if paradigm == "Contrastive SSL" and task not in ["Classification (Images/Text)", "Language Modeling (LLM Training)"]:
            issues.append("Contrastive SSL works best with Classification or Language Modeling tasks.")
        
        if paradigm == "SHADA Pipeline" and "LLaMA" in model:
            issues.append("LLaMA models should use 'Standard Supervised' or load via pretrained model integration, not full SHADA pipeline.")
        
        if self._use_mtl.isChecked() and task not in ["Classification (Images/Text)", "Language Modeling (LLM Training)"]:
            # MTL in SHADA is mainly optimized for multi-task vision or hybrid, 
            # but here we check if its even applicable for non-standard tasks.
            pass

        if self._vram_gb > 0 and self._vram_gb < 4:
            if "7B" in self._tier.currentText() or "34B" in self._tier.currentText():
                issues.append(f"Large models require significant VRAM. Current: {self._vram_gb:.1f}GB. Recommended: 12GB+ for large models.")
        
        if issues:
            return False, "Configuration Issues:\n• " + "\n• ".join(issues)
        return True, ""

    def get_config(self) -> dict:
        # Mapping back to internal keys for trainer compatibility
        tier_map = {
            "10M - 100M Params (Ultra Light)": "nano",
            "100M - 1B Params (Balanced)": "base",
            "1B - 7B Params (High Performance)": "large",
            "7B - 34B+ Params (State-of-the-Art)": "xl"
        }
        task_map = {
            "Classification (Images/Text)": "classification",
            "Language Modeling (LLM Training)": "lm",
            "Object Detection": "detection",
            "Image Segmentation": "segmentation"
        }
        rl_map = {
            "Proximal Policy Optimization (PPO)": "ppo",
            "Direct Preference Optimization (DPO)": "dpo"
        }

        return {
            "model_tier":                  tier_map.get(self._tier.currentText(), "base"),
            "task":                        task_map.get(self._task.currentText(), "classification"),
            "pretrained_model":            self._pretrained.currentText(),
            "paradigm":                    self._paradigm.currentText(),
            "optimizer":                   self._opt.currentText(),
            "num_epochs":                  self._epochs.value(),
            "batch_size":                  self._batch.value(),
            "base_lr":                     self._lr.value(),
            "weight_decay":                self._wd.value(),
            "warmup_steps":                self._warmup.value(),
            "gradient_accumulation_steps": self._grad_acc.value(),
            "mixed_precision":             self._mp.currentText(),
            "lora_rank":                   self._lora_r.value(),
            "lora_alpha":                  self._lora_a.value(),
            "use_rl":                      self._use_rl.isChecked(),
            "rl_algorithm":                rl_map.get(self._rl_algo.currentText(), "ppo"),
            "use_adversarial":             self._use_adv.isChecked(),
            "use_mtl":                     self._use_mtl.isChecked(),
            "use_curriculum":              self._use_curriculum.isChecked(),
            "curriculum_warmup":           self._curriculum_warmup.value(),
        }

    # ──────────────────────────────────────────────────────────────────────────
    # Smart Config & Validation Methods
    # ──────────────────────────────────────────────────────────────────────────

    def _get_dataset_info(self, train_path: str = "", data_format: str = "") -> dict:
        """
        Extract dataset information for validation/tuning.
        Analyzes actual dataset to get: sample count, num classes, type.
        """
        info = {
            "num_samples": 10000,  # Default estimate
            "num_classes": 10,
            "is_imbalanced": False,
            "has_noisy_labels": False,
            "data_type": "unknown",  # image, text, tabular
        }

        fmt = (data_format or "").lower()
        
        # Try to get actual dataset info
        try:
            if train_path and os.path.exists(train_path):
                # CSV files - count rows and classes
                if fmt in ["csv", "parquet"] or train_path.endswith('.csv') or train_path.endswith('.parquet'):
                    info["data_type"] = "text" if "text" in fmt or "csv" in fmt else "tabular"
                    try:
                        import pandas as pd
                        if train_path.endswith('.csv'):
                            df = pd.read_csv(train_path, nrows=100000)  # Sample for speed
                        else:
                            df = pd.read_parquet(train_path)
                        
                        info["num_samples"] = len(df)
                        
                        # Try to detect label column and count classes
                        label_cols = [c for c in df.columns if 'label' in c.lower() or 'target' in c.lower() or 'class' in c.lower()]
                        if label_cols:
                            label_col = label_cols[0]
                            unique_classes = df[label_col].nunique()
                            info["num_classes"] = unique_classes
                            
                            # Check for class imbalance
                            if unique_classes > 1:
                                class_counts = df[label_col].value_counts()
                                max_ratio = class_counts.iloc[0] / class_counts.iloc[-1]
                                info["is_imbalanced"] = max_ratio > 5.0
                    except Exception:
                        pass
                
                # Image folder - count files
                elif os.path.isdir(train_path):
                    info["data_type"] = "image"
                    image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.tiff', '.webp'}
                    file_count = 0
                    class_folders = set()
                    
                    # Check if it's a class-folder structure
                    for root, dirs, files in os.walk(train_path):
                        if files:
                            class_folders.add(os.path.basename(root))
                            for f in files:
                                if os.path.splitext(f)[1].lower() in image_extensions:
                                    file_count += 1
                    
                    if file_count > 0:
                        info["num_samples"] = file_count
                        info["num_classes"] = max(1, len(class_folders) - 1)  # -1 for root
                        
                        # Check for imbalance by folder
                        if len(class_folders) > 1:
                            folder_counts = []
                            for folder in class_folders:
                                folder_path = os.path.join(train_path, folder)
                                if os.path.isdir(folder_path):
                                    count = sum(1 for f in os.listdir(folder_path) 
                                               if os.path.splitext(f)[1].lower() in image_extensions)
                                    folder_counts.append(count)
                            if folder_counts and min(folder_counts) > 0:
                                info["is_imbalanced"] = max(folder_counts) / min(folder_counts) > 5.0
        except Exception:
            pass  # Use defaults on error

        # Override based on format hints
        if "synthetic" in fmt:
            info["num_samples"] = 1000  # Synthetic is usually small
        elif "medical" in fmt:
            info["has_noisy_labels"] = True  # Medical data often has label noise

        return info

    def _run_validation(self):
        """Run configuration validation and show results dialog."""
        from models.config_validator import validate_config

        cfg = self.get_config()
        dataset_info = self._get_dataset_info()
        hardware_info = {
            "device": "cuda",
            "vram_gb": self._vram_gb,
            "gpu_name": "",
        }

        alerts = validate_config(cfg, dataset_info, hardware_info)

        if not alerts:
            QMessageBox.information(
                self,
                "Configuration Valid",
                "No issues found. Your configuration looks good."
            )
            return

        # Build alert display
        critical = [a for a in alerts if a["level"] == "CRITICAL"]
        warnings = [a for a in alerts if a["level"] == "WARNING"]
        infos = [a for a in alerts if a["level"] == "INFO"]

        dialog = ConfigValidationDialog(self)
        dialog.show_results(critical, warnings, infos)

    def _run_smart_config(self):
        """Run smart config auto-tuner and apply recommendations."""
        from models.smart_config import smart_tune_config

        # First, analyze the actual dataset
        train_path = ""
        data_format = "Synthetic (demo)"
        
        # Get dataset info from data panel if available
        if self._data_panel_ref:
            train_path = getattr(self._data_panel_ref, 'train_path', "")
            data_format = getattr(self._data_panel_ref, 'data_format', "Synthetic (demo)")
        
        dataset_info = self._get_dataset_info(train_path, data_format)
        
        # Show dataset analysis to user
        dataset_msg = (
            f"Dataset Analysis:\n\n"
            f"Samples: {dataset_info['num_samples']:,}\n"
            f"Classes: {dataset_info['num_classes']}\n"
            f"Data Type: {dataset_info['data_type']}\n"
            f"Is Imbalanced: {'Yes' if dataset_info['is_imbalanced'] else 'No'}\n"
            f"Has Noisy Labels: {'Yes' if dataset_info['has_noisy_labels'] else 'No'}"
        )
        
        QMessageBox.information(
            self,
            "Dataset Analysis",
            dataset_msg
        )

        # Ask user for training goal
        goal_dialog = TrainingGoalDialog(self)
        if goal_dialog.exec() != QDialog.DialogCode.Accepted:
            return

        training_goal = goal_dialog.get_goal()

        cfg = self.get_config()
        hardware_info = {
            "device": "cuda",
            "vram_gb": self._vram_gb,
            "gpu_name": "",
        }

        # Run auto-tuner with actual dataset info
        optimized_cfg, recommendations = smart_tune_config(
            cfg, dataset_info, hardware_info, training_goal
        )

        if not recommendations:
            QMessageBox.information(
                self,
                "Already Optimized",
                "Your configuration is already well-tuned for the selected settings."
            )
            return

        # Show recommendations and ask for confirmation
        dialog = SmartConfigDialog(self)
        if dialog.show_recommendations(recommendations, training_goal):
            # User accepted - apply changes
            self._apply_smart_config(optimized_cfg)

    def _apply_smart_config(self, optimized_cfg: dict):
        """Apply optimized configuration to UI controls."""
        # Tier mapping
        tier_reverse_map = {
            "nano": "10M - 100M Params (Ultra Light)",
            "base": "100M - 1B Params (Balanced)",
            "large": "1B - 7B Params (High Performance)",
            "xl": "7B - 34B+ Params (State-of-the-Art)"
        }
        task_reverse_map = {
            "classification": "Classification (Images/Text)",
            "lm": "Language Modeling (LLM Training)",
            "detection": "Object Detection",
            "segmentation": "Image Segmentation"
        }
        rl_reverse_map = {
            "ppo": "Proximal Policy Optimization (PPO)",
            "dpo": "Direct Preference Optimization (DPO)"
        }

        # Block signals to avoid cascading updates
        self._tier.blockSignals(True)
        self._task.blockSignals(True)
        self._pretrained.blockSignals(True)
        self._paradigm.blockSignals(True)
        self._opt.blockSignals(True)
        self._epochs.blockSignals(True)
        self._batch.blockSignals(True)
        self._lr.blockSignals(True)
        self._wd.blockSignals(True)
        self._warmup.blockSignals(True)
        self._grad_acc.blockSignals(True)
        self._mp.blockSignals(True)
        self._lora_r.blockSignals(True)
        self._lora_a.blockSignals(True)
        self._use_rl.blockSignals(True)
        self._use_adv.blockSignals(True)
        self._use_mtl.blockSignals(True)
        self._rl_algo.blockSignals(True)

        try:
            # Apply changes
            if "model_tier" in optimized_cfg and optimized_cfg["model_tier"] in tier_reverse_map:
                idx = self._tier.findText(tier_reverse_map[optimized_cfg["model_tier"]])
                if idx >= 0:
                    self._tier.setCurrentIndex(idx)

            if "task" in optimized_cfg and optimized_cfg["task"] in task_reverse_map:
                idx = self._task.findText(task_reverse_map[optimized_cfg["task"]])
                if idx >= 0:
                    self._task.setCurrentIndex(idx)

            if "paradigm" in optimized_cfg:
                idx = self._paradigm.findText(optimized_cfg["paradigm"])
                if idx >= 0:
                    self._paradigm.setCurrentIndex(idx)

            if "optimizer" in optimized_cfg:
                idx = self._opt.findText(optimized_cfg["optimizer"])
                if idx >= 0:
                    self._opt.setCurrentIndex(idx)

            if "num_epochs" in optimized_cfg:
                self._epochs.setValue(optimized_cfg["num_epochs"])

            if "batch_size" in optimized_cfg:
                self._batch.setValue(optimized_cfg["batch_size"])

            if "base_lr" in optimized_cfg:
                self._lr.setValue(optimized_cfg["base_lr"])

            if "weight_decay" in optimized_cfg:
                self._wd.setValue(optimized_cfg["weight_decay"])

            if "warmup_steps" in optimized_cfg:
                self._warmup.setValue(optimized_cfg["warmup_steps"])

            if "gradient_accumulation_steps" in optimized_cfg:
                self._grad_acc.setValue(optimized_cfg["gradient_accumulation_steps"])

            if "mixed_precision" in optimized_cfg:
                idx = self._mp.findText(optimized_cfg["mixed_precision"])
                if idx >= 0:
                    self._mp.setCurrentIndex(idx)

            if "lora_rank" in optimized_cfg:
                self._lora_r.setValue(optimized_cfg["lora_rank"])

            if "lora_alpha" in optimized_cfg:
                self._lora_a.setValue(optimized_cfg["lora_alpha"])

            if "use_rl" in optimized_cfg:
                self._use_rl.setChecked(optimized_cfg["use_rl"])

            if "use_adversarial" in optimized_cfg:
                self._use_adv.setChecked(optimized_cfg["use_adversarial"])

            if "use_mtl" in optimized_cfg:
                self._use_mtl.setChecked(optimized_cfg["use_mtl"])

            if "use_curriculum" in optimized_cfg:
                self._use_curriculum.setChecked(optimized_cfg["use_curriculum"])

            if "curriculum_warmup" in optimized_cfg:
                self._curriculum_warmup.setValue(optimized_cfg["curriculum_warmup"])

            if "rl_algorithm" in optimized_cfg and optimized_cfg["rl_algorithm"] in rl_reverse_map:
                idx = self._rl_algo.findText(rl_reverse_map[optimized_cfg["rl_algorithm"]])
                if idx >= 0:
                    self._rl_algo.setCurrentIndex(idx)

            # Additional SHADA config fields
            if "dropout" in optimized_cfg:
                self._config_extra = getattr(self, "_config_extra", {})
                self._config_extra["dropout"] = optimized_cfg["dropout"]

            if "label_smoothing" in optimized_cfg:
                self._config_extra = getattr(self, "_config_extra", {})
                self._config_extra["label_smoothing"] = optimized_cfg["label_smoothing"]

            if "ssl_alpha" in optimized_cfg:
                self._config_extra = getattr(self, "_config_extra", {})
                self._config_extra["ssl_alpha"] = optimized_cfg["ssl_alpha"]

            if "ssl_beta" in optimized_cfg:
                self._config_extra = getattr(self, "_config_extra", {})
                self._config_extra["ssl_beta"] = optimized_cfg["ssl_beta"]

        finally:
            # Restore signals
            self._tier.blockSignals(False)
            self._task.blockSignals(False)
            self._pretrained.blockSignals(False)
            self._paradigm.blockSignals(False)
            self._opt.blockSignals(False)
            self._epochs.blockSignals(False)
            self._batch.blockSignals(False)
            self._lr.blockSignals(False)
            self._wd.blockSignals(False)
            self._warmup.blockSignals(False)
            self._grad_acc.blockSignals(False)
            self._mp.blockSignals(False)
            self._lora_r.blockSignals(False)
            self._lora_a.blockSignals(False)
            self._use_rl.blockSignals(False)
            self._use_adv.blockSignals(False)
            self._use_mtl.blockSignals(False)
            self._use_curriculum.blockSignals(False)
            self._curriculum_warmup.blockSignals(False)
            self._rl_algo.blockSignals(False)

        QMessageBox.information(
            self,
            "Configuration Applied",
            "Smart configuration has been applied.\n\n"
            "You can now start training with the optimized settings."
        )


# ══════════════════════════════════════════════════════════════════════════════
# Dialog Classes
# ══════════════════════════════════════════════════════════════════════════════

class ConfigValidationDialog(QDialog):
    """Dialog showing configuration validation results with interactive controls."""

    def __init__(self, parent=None, model_panel=None):
        super().__init__(parent)
        self.setWindowTitle("Configuration Validation Results")
        self.setMinimumWidth(700)
        self.setMinimumHeight(500)
        self._model_panel = model_panel
        self._controls = {}  # Store controls for each parameter
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Configuration Validation")
        title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #5559A0;")
        layout.addWidget(title)

        # Scrollable results area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setStyleSheet("background: transparent;")

        self._content_widget = QWidget()
        self._content_layout = QVBoxLayout(self._content_widget)
        self._content_layout.setContentsMargins(0, 0, 0, 0)
        self._content_layout.setSpacing(10)

        scroll.setWidget(self._content_widget)
        layout.addWidget(scroll, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        self._apply_btn = QPushButton("Apply Changes")
        self._apply_btn.clicked.connect(self._apply_changes)
        self._apply_btn.setMinimumHeight(35)
        self._apply_btn.setMinimumWidth(120)
        self._apply_btn.setStyleSheet("""
            QPushButton {
                background-color: #5559A0;
                color: white;
                border-radius: 6px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #6a6fb8;
            }
            QPushButton:disabled {
                background-color: #555555;
                color: #888888;
            }
        """)
        btn_layout.addWidget(self._apply_btn)

        close_btn = QPushButton("Close")
        close_btn.clicked.connect(self.accept)
        close_btn.setMinimumHeight(35)
        close_btn.setMinimumWidth(100)
        btn_layout.addWidget(close_btn)

        layout.addLayout(btn_layout)

    def _create_control_for_param(self, param: str, recommendation: str, current_value=None):
        """Create an appropriate control widget for a parameter."""
        # Try to extract suggested value from recommendation
        import re
        
        # Pattern for numeric values in recommendations
        num_match = re.search(r'(\d+\.?\d*)\s*(?:to|≤|≥|=|<|>)\s*(\d+\.?\d*)?', recommendation)
        single_num_match = re.search(r'(?:to|be|set|use|reduce|increase)\s+(?:a\s+)?(\d+\.?\d*)', recommendation, re.IGNORECASE)
        
        control = None
        suggested_value = None
        
        # Common parameters and their typical ranges
        # Only include parameters that exist in the ModelPanel widgets
        param_configs = {
            "base_lr": {"type": "double", "min": 1e-6, "max": 1e-2, "decimals": 6},
            "batch_size": {"type": "int", "min": 1, "max": 512},
            "gradient_accumulation_steps": {"type": "int", "min": 1, "max": 64},
            "lora_rank": {"type": "int", "min": 1, "max": 256},
            "lora_alpha": {"type": "double", "min": 1.0, "max": 512.0, "decimals": 1},
            "mixed_precision": {"type": "choice", "choices": ["fp32", "fp16", "bf16"]},
            "optimizer": {"type": "choice", "choices": ["adamw", "lion", "sgd"]},
            "num_epochs": {"type": "int", "min": 1, "max": 1000},
            "weight_decay": {"type": "double", "min": 0.0, "max": 1.0, "decimals": 6},
            "warmup_steps": {"type": "int", "min": 0, "max": 10000},
            "use_mtl": {"type": "bool"},
            "use_curriculum": {"type": "bool"},
            "curriculum_warmup": {"type": "int", "min": 0, "max": 100000},
        }
        
        config = param_configs.get(param, None)
        
        if config:
            if config["type"] == "double":
                control = QDoubleSpinBox()
                control.setDecimals(config.get("decimals", 4))
                control.setMinimum(config.get("min", 0.0))
                control.setMaximum(config.get("max", 1000.0))
                if current_value is not None:
                    control.setValue(float(current_value))
                # Try to extract suggested value
                if num_match:
                    suggested_value = float(num_match.group(2) or num_match.group(1))
                elif single_num_match:
                    suggested_value = float(single_num_match.group(1))
                if suggested_value is not None:
                    control.setValue(suggested_value)
                    
            elif config["type"] == "int":
                control = QSpinBox()
                control.setMinimum(config.get("min", 0))
                control.setMaximum(config.get("max", 10000))
                if current_value is not None:
                    control.setValue(int(current_value))
                if num_match:
                    suggested_value = int(float(num_match.group(2) or num_match.group(1)))
                elif single_num_match:
                    suggested_value = int(float(single_num_match.group(1)))
                if suggested_value is not None:
                    control.setValue(suggested_value)
                    
            elif config["type"] == "choice":
                control = QComboBox()
                control.addItems(config["choices"])
                # Try to find suggested choice in recommendation
                for choice in config["choices"]:
                    if choice.lower() in recommendation.lower():
                        control.setCurrentText(choice)
                        suggested_value = choice
                        break
                        
            elif config["type"] == "bool":
                control = QComboBox()
                control.addItems(["True", "False"])
                if "false" in recommendation.lower():
                    control.setCurrentText("False")
                    suggested_value = False
                elif "true" in recommendation.lower():
                    control.setCurrentText("True")
                    suggested_value = True
                    
        return control, suggested_value

    def _get_current_value(self, param: str):
        """Get current value from model panel if available."""
        if not self._model_panel:
            return None
        
        try:
            # Map parameter names to model panel widget attributes
            param_map = {
                "base_lr": ("_lr", "value"),
                "batch_size": ("_batch", "value"),
                "gradient_accumulation_steps": ("_grad_acc", "value"),
                "lora_rank": ("_lora_r", "value"),
                "lora_alpha": ("_lora_a", "value"),
                "mixed_precision": ("_mp", "current_text"),
                "optimizer": ("_opt", "current_text"),
                "num_epochs": ("_epochs", "value"),
                "weight_decay": ("_wd", "value"),
                "warmup_steps": ("_warmup", "value"),
                "use_mtl": ("_use_mtl", "checked"),
                "use_curriculum": ("_use_curriculum", "checked"),
                "curriculum_warmup": ("_curriculum_warmup", "value"),
            }
            
            attr_name = param_map.get(param)
            if attr_name and hasattr(self._model_panel, attr_name[0]):
                widget = getattr(self._model_panel, attr_name[0])
                if isinstance(widget, (QSpinBox, QDoubleSpinBox)):
                    return widget.value()
                elif isinstance(widget, QComboBox):
                    return widget.currentText()
                elif isinstance(widget, QCheckBox):
                    return widget.isChecked()
        except Exception:
            pass
        return None

    def show_results(self, critical: list, warnings: list, infos: list):
        """Display validation results with interactive controls."""
        # Clear existing content
        while self._content_layout.count():
            item = self._content_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        
        self._controls.clear()
        has_editable = False

        # Process all alerts
        all_alerts = [
            (critical, "CRITICAL ISSUES", "#ff5555", "#ff5555"),
            (warnings, "WARNINGS", "#ffaa00", "#ffaa00"),
            (infos, "INFORMATION", "#55aaff", "#55aaff"),
        ]
        
        for alerts, section_title, border_color, text_color in all_alerts:
            if not alerts:
                continue
                
            # Section header
            header = QLabel(f"{section_title} ({len(alerts)})")
            header.setStyleSheet(f"color: {text_color}; font-weight: bold; font-size: 11pt; margin: 10px 0;")
            self._content_layout.addWidget(header)

            for alert in alerts:
                param = alert["parameter"]
                message = alert["message"]
                recommendation = alert["recommendation"]
                md_ref = alert["md_reference"]
                level = alert["level"]
                
                # Only add controls for warnings and critical (not info)
                can_edit = level in ["CRITICAL", "WARNING"]

                # Create alert card
                card = self._create_alert_card(
                    param, message, recommendation, md_ref,
                    border_color, can_edit
                )
                self._content_layout.addWidget(card)

                # Add control if editable
                if can_edit:
                    current_value = self._get_current_value(param)
                    control, suggested_value = self._create_control_for_param(
                        param, recommendation, current_value
                    )

                    if control:
                        has_editable = True
                        self._controls[param] = {
                            "control": control,
                            "current": current_value,
                            "suggested": suggested_value,
                        }

                        # Add control row
                        control_row = QHBoxLayout()
                        control_row.setContentsMargins(20, 5, 20, 10)

                        control_label = QLabel(f"Edit {param}:")
                        control_label.setStyleSheet("color: #aaa; font-size: 9pt;")
                        control_row.addWidget(control_label)

                        control.setMinimumWidth(150)
                        control_row.addWidget(control)

                        if suggested_value is not None:
                            suggestion_label = QLabel(f" (Suggested: {suggested_value})")
                            suggestion_label.setStyleSheet("color: #55ff55; font-size: 8pt; font-style: italic;")
                            control_row.addWidget(suggestion_label)

                        control_row.addStretch()
                        self._content_layout.addLayout(control_row)
                    else:
                        # Parameter not available in UI yet - show note
                        note_label = QLabel(f"  ⚠ {param} is not yet configurable from the UI. Please configure it in your config file.")
                        note_label.setStyleSheet("color: #ffaa00; font-size: 8.5pt; font-style: italic; padding: 5px 10px;")
                        note_label.setWordWrap(True)
                        self._content_layout.addWidget(note_label)

        if not all_alerts[0][0] and not all_alerts[1][0] and not all_alerts[2][0]:
            no_issues = QLabel('No issues found. Your configuration looks good.')
            no_issues.setStyleSheet("color: #55ff55; font-size: 11pt; text-align: center; padding: 20px;")
            self._content_layout.addWidget(no_issues)

        self._content_layout.addStretch()
        
        # Enable/disable apply button
        self._apply_btn.setEnabled(has_editable and self._model_panel is not None)
        
        self.exec()

    def _create_alert_card(self, param: str, message: str, recommendation: str, 
                           md_ref: str, border_color: str, can_edit: bool = False):
        """Create a styled card for an alert."""
        card = QFrame()
        card.setStyleSheet(f"""
            QFrame {{
                background: rgba({int(border_color[1:3], 16)}, {int(border_color[3:5], 16)}, {int(border_color[5:7], 16)}, 0.1);
                border-left: 3px solid {border_color};
                border-radius: 8px;
                padding: 8px;
                margin: 5px 0;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(5)
        
        # Parameter name and message
        header_html = f'<strong style="color: {border_color}; font-size: 10pt;">{param}</strong>: {message}'
        header = QLabel(header_html)
        header.setWordWrap(True)
        layout.addWidget(header)
        
        # Recommendation
        rec_label = QLabel(f'→ {recommendation}')
        rec_label.setStyleSheet("color: #888; font-size: 9pt;")
        rec_label.setWordWrap(True)
        layout.addWidget(rec_label)
        
        # Reference
        ref_label = QLabel(f'[{md_ref}]')
        ref_label.setStyleSheet("color: #666; font-size: 8pt;")
        layout.addWidget(ref_label)
        
        return card

    def _apply_changes(self):
        """Apply changes from controls to the model panel."""
        if not self._model_panel or not self._controls:
            return
        
        changes_applied = []
        notes = []
        
        for param, control_data in self._controls.items():
            control = control_data["control"]
            new_value = None
            
            # Get value from control
            if isinstance(control, (QSpinBox, QDoubleSpinBox)):
                new_value = control.value()
            elif isinstance(control, QComboBox):
                text = control.currentText()
                # Try to convert to appropriate type
                if text in ["True", "False"]:
                    new_value = text == "True"
                elif text in ["fp32", "fp16", "bf16", "adamw", "lion", "sgd"]:
                    new_value = text
                else:
                    try:
                        new_value = float(text)
                    except ValueError:
                        new_value = text
            
            if new_value is not None:
                # Apply to model panel
                try:
                    param_map = {
                        "base_lr": ("_lr", "value"),
                        "batch_size": ("_batch", "value"),
                        "gradient_accumulation_steps": ("_grad_acc", "value"),
                        "lora_rank": ("_lora_r", "value"),
                        "lora_alpha": ("_lora_a", "value"),
                        "mixed_precision": ("_mp", "current_text"),
                        "optimizer": ("_opt", "current_text"),
                        "num_epochs": ("_epochs", "value"),
                        "weight_decay": ("_wd", "value"),
                        "warmup_steps": ("_warmup", "value"),
                        "use_mtl": ("_use_mtl", "checked"),
                        "use_curriculum": ("_use_curriculum", "checked"),
                        "curriculum_warmup": ("_curriculum_warmup", "value"),
                    }
                    
                    if param in param_map:
                        attr_name, value_type = param_map[param]
                        if hasattr(self._model_panel, attr_name):
                            widget = getattr(self._model_panel, attr_name)
                            
                            if value_type == "value":
                                widget.setValue(new_value)
                            elif value_type == "current_text":
                                widget.setCurrentText(str(new_value))
                            elif value_type == "checked":
                                widget.setChecked(bool(new_value))
                            
                            changes_applied.append(f"{param} = {new_value}")
                except Exception as e:
                    pass  # Silently ignore errors
        
        # Build message
        message_parts = []
        if changes_applied:
            message_parts.append("The following configuration changes have been applied:\n")
            message_parts.append("\n".join(f"  • {c}" for c in changes_applied))
        
        if notes:
            message_parts.append("\n\nNote:\n")
            message_parts.append("\n".join(f"  • {n}" for n in notes))
            message_parts.append("\n\nThis parameter is not yet available in the UI.")
        
        if changes_applied or notes:
            QMessageBox.information(
                self,
                "Changes Applied",
                "\n".join(message_parts) +
                "\n\nYou can now start training with the updated settings."
            )


class SmartConfigDialog(QDialog):
    """Dialog showing smart config recommendations."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Smart Configuration Recommendations")
        self.setMinimumWidth(650)
        self.setMinimumHeight(450)
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        self._title = QLabel("Auto-Tune Recommendations")
        self._title.setStyleSheet("font-size: 16pt; font-weight: bold; color: #5559A0;")
        layout.addWidget(self._title)

        # Goal label
        self._goal_lbl = QLabel("")
        self._goal_lbl.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(self._goal_lbl)

        # Results area
        self._results = QTextEdit()
        self._results.setReadOnly(True)
        self._results.setStyleSheet("""
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
        layout.addWidget(self._results, 1)

        # Buttons
        btn_layout = QHBoxLayout()
        btn_layout.addStretch()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(35)
        cancel_btn.setMinimumWidth(100)
        btn_layout.addWidget(cancel_btn)

        apply_btn = QPushButton("Apply Changes")
        apply_btn.setObjectName("btnStart")
        apply_btn.setStyleSheet("""
            QPushButton#btnStart {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #5559A0, stop:1 #7B68EE);
                color: white;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton#btnStart:hover {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #6666bb, stop:1 #8B78EE);
            }
        """)
        apply_btn.clicked.connect(self.accept)
        apply_btn.setMinimumHeight(35)
        apply_btn.setMinimumWidth(120)
        btn_layout.addWidget(apply_btn)

        layout.addLayout(btn_layout)

    def show_recommendations(self, recommendations, training_goal: str) -> bool:
        """Show recommendations and return True if user accepted."""
        self._goal_lbl.setText(f"Training Goal: <strong>{training_goal.upper()}</strong>")

        html = []
        html.append('<div style="color: #55ff55; font-size: 10pt; margin-bottom: 10px;">')
        html.append(f'Found {len(recommendations)} optimization(s) based on SHADA best practices:')
        html.append('</div>')

        # Sort by priority
        sorted_recs = sorted(recommendations, key=lambda r: r.priority)

        for i, rec in enumerate(sorted_recs, 1):
            priority_color = "#ff5555" if rec.priority == 1 else "#ffaa00" if rec.priority == 2 else "#55aaff"
            priority_label = "HIGH" if rec.priority == 1 else "MEDIUM" if rec.priority == 2 else "LOW"

            html.append(f'<div style="background: rgba(85,85,170,0.15); border-left: 3px solid {priority_color}; padding: 10px; margin: 8px 0; border-radius: 0 6px 6px 0;">')
            html.append(f'<div style="color: {priority_color}; font-weight: bold; font-size: 9pt;">#{i} [{priority_label} PRIORITY] {rec.parameter}</div>')
            html.append(f'<div style="margin: 6px 0;">')
            html.append(f'<span style="color: #ff8888;">Current:</span> <code style="background: #333; padding: 2px 6px; border-radius: 3px;">{rec.old_value}</code>')
            html.append(f' -> <span style="color: #88ff88;">New:</span> <code style="background: #333; padding: 2px 6px; border-radius: 3px;">{rec.new_value}</code>')
            html.append(f'</div>')
            html.append(f'<div style="color: #aaa; font-size: 9pt; margin-top: 5px;">{rec.reason}</div>')
            html.append(f'<div style="color: #666; font-size: 8pt; margin-top: 3px;">[{rec.md_reference}]</div>')
            html.append('</div>')

        self._results.setHtml('\n'.join(html))
        return self.exec() == QDialog.DialogCode.Accepted


class TrainingGoalDialog(QDialog):
    """Dialog for selecting training goal."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Training Goal")
        self.setMinimumWidth(450)
        self.setModal(True)
        self._goal = "balanced"
        self._build()

    def _build(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel("Select Training Goal")
        title.setStyleSheet("font-size: 14pt; font-weight: bold; color: #5559A0;")
        layout.addWidget(title)

        # Description
        desc = QLabel("What is your primary objective for this training session?")
        desc.setStyleSheet("color: #888; font-size: 9pt;")
        layout.addWidget(desc)

        # Options
        options_layout = QVBoxLayout()
        options_layout.setSpacing(10)

        # Balanced
        self._btn_balanced = QPushButton("Balanced (Recommended)")
        self._btn_balanced.setStyleSheet("""
            QPushButton {
                background: rgba(85, 85, 170, 0.2);
                border: 2px solid #5559A0;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(85, 85, 170, 0.3);
            }
        """)
        self._btn_balanced.clicked.connect(lambda: self._select_goal("balanced"))
        options_layout.addWidget(self._btn_balanced)

        # Fast
        self._btn_fast = QPushButton("Fast Training")
        self._btn_fast.setStyleSheet("""
            QPushButton {
                background: rgba(255, 170, 0, 0.15);
                border: 2px solid #ffaa00;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(255, 170, 0, 0.25);
            }
        """)
        self._btn_fast.clicked.connect(lambda: self._select_goal("fast"))
        options_layout.addWidget(self._btn_fast)

        # Max Accuracy
        self._btn_max = QPushButton("Maximum Accuracy")
        self._btn_max.setStyleSheet("""
            QPushButton {
                background: rgba(85, 255, 85, 0.15);
                border: 2px solid #55ff55;
                border-radius: 8px;
                padding: 12px;
                text-align: left;
            }
            QPushButton:hover {
                background: rgba(85, 255, 85, 0.25);
            }
        """)
        self._btn_max.clicked.connect(lambda: self._select_goal("max_accuracy"))
        options_layout.addWidget(self._btn_max)

        layout.addLayout(options_layout)

        # Descriptions
        desc_text = QTextEdit()
        desc_text.setReadOnly(True)
        desc_text.setMaximumHeight(120)
        desc_text.setStyleSheet("""
            QTextEdit {
                background: #1a1a2e;
                color: #aaa;
                border: none;
                font-size: 8.5pt;
            }
        """)
        desc_text.setHtml("""
        <b>Balanced:</b> Good trade-off between training time and final accuracy. Recommended for most use cases.<br><br>
        <b>Fast:</b> Minimize training time. Skip SSL pre-training, reduce epochs. Good for prototyping.<br><br>
        <b>Maximum Accuracy:</b> Full SHADA pipeline with all optimizations. Longer training but best results.
        """)
        layout.addWidget(desc_text)

        # Cancel button
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setMinimumHeight(35)
        layout.addWidget(cancel_btn)

    def _select_goal(self, goal: str):
        self._goal = goal
        self.accept()

    def get_goal(self) -> str:
        return self._goal
