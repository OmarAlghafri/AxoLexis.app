"""
Data Loader — handles CSV, Image folder, NumPy, and synthetic datasets.
Returns (train_DataLoader, val_DataLoader | None) tuples.
"""

import os
import numpy as np
import torch
from torch.utils.data import Dataset, DataLoader, random_split
from pathlib import Path


# ── Synthetic (demo) dataset ─────────────────────────────────────────────────

class SyntheticDataset(Dataset):
    """Fast synthetic dataset for testing the full pipeline without real data."""
    def __init__(self, n: int = 256, img_sz: int = 32, seq_len: int = 16, vocab: int = 1000):
        self.n, self.img_sz, self.seq_len, self.vocab = n, img_sz, seq_len, vocab

    def __len__(self):
        return self.n

    def __getitem__(self, _):
        return {
            "images":       torch.randn(3, self.img_sz, self.img_sz),
            "images_aug1":  torch.randn(3, self.img_sz, self.img_sz),
            "images_aug2":  torch.randn(3, self.img_sz, self.img_sz),
            "labels":       torch.randint(0, 10, ()).long(),
            "input_ids":    torch.randint(0, self.vocab, (self.seq_len,)).long(),
            "chosen_ids":   torch.randint(0, self.vocab, (self.seq_len,)).long(),
            "rejected_ids": torch.randint(0, self.vocab, (self.seq_len,)).long(),
            "task":         "classification",
            "modality":     "image",
        }


# ── Image folder dataset ─────────────────────────────────────────────────────

class ImageFolderDataset(Dataset):
    """
    Loads images from a flat folder or class-subfolders.
    Subfolders → class labels;  flat folder → label 0.
    """
    IMG_EXT = {".png", ".jpg", ".jpeg", ".bmp", ".webp"}

    def __init__(self, root: str, img_sz: int = 224):
        from PIL import Image
        import torchvision.transforms as T

        self.root  = Path(root)
        self.img_sz = img_sz
        self.Image = Image

        self.transform = T.Compose([
            T.Resize((img_sz, img_sz)),
            T.ToTensor(),
            T.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])

        self.samples: list[tuple[Path, int]] = []
        self.classes: list[str] = []

        # Class-subfolder layout (ImageNet-style)
        subdirs = [d for d in self.root.iterdir() if d.is_dir()]
        if subdirs:
            self.classes = sorted(d.name for d in subdirs)
            for idx, cls in enumerate(self.classes):
                for f in (self.root / cls).iterdir():
                    if f.suffix.lower() in self.IMG_EXT:
                        self.samples.append((f, idx))
        else:
            # Flat folder
            self.classes = ["unknown"]
            for f in self.root.iterdir():
                if f.suffix.lower() in self.IMG_EXT:
                    self.samples.append((f, 0))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        path, label = self.samples[idx]
        img = self.Image.open(path).convert("RGB")
        img = self.transform(img)
        aug1 = img + 0.05 * torch.randn_like(img)
        aug2 = img + 0.05 * torch.randn_like(img)
        return {
            "images": img, "images_aug1": aug1, "images_aug2": aug2,
            "labels": torch.tensor(label).long(),
            "task": "classification", "modality": "image",
        }


# ── CSV dataset ──────────────────────────────────────────────────────────────

class CSVDataset(Dataset):
    """
    Loads a CSV file.
    Last column = label; remaining columns = features as a flat float tensor.
    """
    def __init__(self, path: str):
        import csv
        rows = []
        if not os.path.exists(path):
            raise FileNotFoundError(f"CSV file not found: {path}")

        with open(path, newline="", encoding="utf-8") as f:
            # 1) Try to sniff delimiter (comma, semicolon, tab, etc.)
            sample = f.read(8192)
            f.seek(0)
            dialect = None
            if sample.strip():
                try:
                    dialect = csv.Sniffer().sniff(sample)
                except Exception:
                    pass

            f.seek(0)
            reader = csv.reader(f, dialect=dialect) if dialect else csv.reader(f)

            # 2) Smart header detection
            first_row = next(reader, None)
            if first_row:
                try:
                    # If every element in the first row is a number, treat as data
                    [float(x) for x in first_row if x.strip()]
                    rows.append([float(x) for x in first_row if x.strip()])
                except ValueError:
                    # Likely a header row, so we skip it (already consumed)
                    pass

            # 3) Load remaining rows
            for row in reader:
                if not any(row): continue   # skip empty lines
                try:
                    rows.append([float(x) for x in row if x.strip()])
                except ValueError:
                    continue   # skip non-numeric rows

        if not rows:
            raise ValueError(
                f"The CSV file at {path} contains no valid numeric data rows.\n"
                "Please ensure the file has at least one row of numeric values."
            )

        data = np.array(rows, dtype=np.float32)

        # Handle case where data might be 1D (shouldn't happen with rows as list-of-lists, but for safety)
        if data.ndim == 1:
            data = data.reshape(1, -1)

        if data.shape[1] < 2:
            # Only one column: use it as Labels, features become empty
            self.X = torch.zeros((data.shape[0], 0), dtype=torch.float32)
            raw_y = data[:, 0].astype(int)
        else:
            # Standard: last column is label, rest are features
            self.X = torch.tensor(data[:, :-1])
            raw_y = data[:, -1].astype(int)
        # Re-index labels to 0-based
        unique = sorted(set(raw_y.tolist()))
        mapping = {v: i for i, v in enumerate(unique)}
        self.y  = torch.tensor([mapping[v] for v in raw_y.tolist()]).long()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        feat  = self.X[idx]
        label = self.y[idx]
        # Wrap features as a 1D "image" (C=1, H=1, W=features)
        img = feat.unsqueeze(0).unsqueeze(0)   # (1, 1, F)
        return {
            "images": img, "images_aug1": img, "images_aug2": img,
            "labels": label,
            "task": "classification", "modality": "image",
        }


# ── NumPy dataset ─────────────────────────────────────────────────────────────

class NumpyDataset(Dataset):
    """
    Loads a .npy or .npz file.
    .npy  → expects shape (N, ...) — last dim used as label if available.
    .npz  → expects keys 'X' and 'y'.
    """
    def __init__(self, path: str):
        ext = Path(path).suffix.lower()
        if ext == ".npz":
            d = np.load(path)
            self.X = torch.tensor(d["X"], dtype=torch.float32)
            self.y = torch.tensor(d["y"], dtype=torch.long)
        else:
            arr = np.load(path).astype(np.float32)
            if arr.ndim == 1:
                arr = arr.reshape(-1, 1)
            self.X = torch.tensor(arr[:, :-1])
            self.y = torch.tensor(arr[:, -1].astype(int)).long()

    def __len__(self):
        return len(self.X)

    def __getitem__(self, idx):
        feat  = self.X[idx]
        label = self.y[idx]
        img = feat.view(1, 1, -1)
        return {
            "images": img, "images_aug1": img, "images_aug2": img,
            "labels": label,
            "task": "classification", "modality": "image",
        }


# ── Text / NLP Dataset ────────────────────────────────────────────────────────

class TextCSVDataset(Dataset):
    """
    Loads a CSV containing text (e.g., IMDB).
    Finds the text column (longest average string) and captures labels.
    Tokenizes text into 'input_ids'.
    """
    def __init__(self, path: str, max_length: int = 512, tokenizer_name: str = "gpt2", nrows: int = None):
        import csv
        from transformers import AutoTokenizer
        
        self.tokenizer = AutoTokenizer.from_pretrained(tokenizer_name)
        if self.tokenizer.pad_token is None:
            self.tokenizer.pad_token = self.tokenizer.eos_token

        print(f"[INFO] Loading CSV: {path} (nrows={nrows})")
        
        rows = []
        with open(path, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            header = next(reader, None)
            for i, row in enumerate(reader):
                if nrows and i >= nrows:
                    break
                if row:
                    rows.append(row)
        
        if not rows:
            raise ValueError(f"CSV file at {path} is empty.")
        
        col_count = len(rows[0])
        headers = header if header else [f"col_{i}" for i in range(col_count)]
        
        col_avg_len = [0] * col_count
        for row in rows:
            for i, val in enumerate(row):
                col_avg_len[i] += len(val)
        for i in range(col_count):
            col_avg_len[i] /= len(rows)
        
        text_col_idx = max(range(col_count), key=lambda i: col_avg_len[i])
        label_col_idx = 0 if 0 != text_col_idx else (1 if col_count > 1 else 0)
        if label_col_idx == text_col_idx:
            for i in range(col_count):
                if i != text_col_idx:
                    label_col_idx = i
                    break
        
        texts = [row[text_col_idx] for row in rows]
        raw_labels = [row[label_col_idx] for row in rows]

        print(f"[INFO] Tokenizing {len(texts)} samples...")
        encodings = self.tokenizer(
            texts, truncation=True, padding="max_length", 
            max_length=max_length, return_tensors="pt"
        )
        self.input_ids = encodings["input_ids"]
        self.attn_mask = encodings["attention_mask"]

        unique_labels = sorted(set(raw_labels))
        mapping = {v: i for i, v in enumerate(unique_labels)}
        self.labels = torch.tensor([mapping[v] for v in raw_labels]).long()

    def __len__(self):
        return len(self.labels)

    def __getitem__(self, idx):
        return {
            "input_ids":    self.input_ids[idx],
            "attention_mask": self.attn_mask[idx],
            "labels":       self.labels[idx],
            "task":         "classification",
            "modality":     "text",
        }


# ── Factory ───────────────────────────────────────────────────────────────────

def build_dataloaders(
    train_path: str,
    val_path: str,
    data_format: str,
    batch_size: int,
    val_split: float = 0.15,
    **kwargs
) -> tuple[DataLoader, DataLoader | None]:
    """
    Returns (train_dl, val_dl).
    val_dl is None if no val data and no split possible.
    """
    fmt = data_format.lower()

    # ── Pick dataset class ────────────────────────────────────────
    if "synthetic" in fmt or not train_path:
        train_ds = SyntheticDataset(n=512)
        val_ds   = SyntheticDataset(n=128) if not val_path else None

    elif "csv" in fmt or (train_path and train_path.lower().endswith(".csv")):
        try:
            # Attempt numeric CSV first
            full_ds = CSVDataset(train_path)
        except ValueError:
            # Fallback to Text CSV format
            full_ds = TextCSVDataset(train_path, **kwargs)
            
        train_ds, val_ds = _split(full_ds, val_split, val_path)

    elif "npy" in fmt or "numpy" in fmt or (train_path and train_path.lower().endswith((".npy", ".npz"))):
        full_ds = NumpyDataset(train_path)
        train_ds, val_ds = _split(full_ds, val_split, val_path)

    elif "image" in fmt or (train_path and os.path.isdir(train_path)):
        train_ds = ImageFolderDataset(train_path)
        val_ds   = ImageFolderDataset(val_path) if val_path and os.path.isdir(val_path) else None
        if val_ds is None and len(train_ds) > 10:
            train_ds, val_ds = _split(train_ds, val_split, val_path)

    else:
        # Auto-detect
        if train_path.endswith(".csv"):
            try:
                full_ds = CSVDataset(train_path)
            except ValueError:
                full_ds = TextCSVDataset(train_path, **kwargs)
        elif train_path.endswith((".npy", ".npz")):
            full_ds = NumpyDataset(train_path)
        elif os.path.isdir(train_path):
            full_ds = ImageFolderDataset(train_path)
        else:
            full_ds = SyntheticDataset()
        train_ds, val_ds = _split(full_ds, val_split, val_path)

    num_workers = 0

    train_dl = DataLoader(
        train_ds, batch_size=batch_size,
        shuffle=True, num_workers=num_workers, pin_memory=False,
    )
    val_dl = DataLoader(
        val_ds, batch_size=batch_size,
        shuffle=False, num_workers=num_workers, pin_memory=False,
    ) if val_ds else None

    return train_dl, val_dl


def _split(dataset, val_split: float, existing_val_path: str):
    """Split dataset into train/val, loading existing val path if provided."""
    if existing_val_path:
        return dataset, None
    n_total = len(dataset)
    n_val   = max(1, int(n_total * val_split))
    n_train = n_total - n_val
    if n_train < 1:
        return dataset, None
    return random_split(dataset, [n_train, n_val])
