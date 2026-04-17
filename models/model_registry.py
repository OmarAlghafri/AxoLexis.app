"""
Model Registry — single source of truth for all supported architectures.
Categorized hierarchical structure for the UI to digest.
"""

MODEL_REGISTRY = {
    "Computer Vision (CNN)": {
        "ResNet": ["ResNet-18", "ResNet-34", "ResNet-50", "ResNet-101", "ResNet-152"],
        "VGG": ["VGG-16", "VGG-19"],
        "DenseNet": ["DenseNet-121", "DenseNet-169", "DenseNet-201"],
        "EfficientNet": [f"EfficientNet-B{i}" for i in range(8)],
        "MobileNet": ["MobileNet-V1", "MobileNet-V2", "MobileNet-V3-Small", "MobileNet-V3-Large"],
        "Inception": ["Inception-V3", "Inception-V4"],
        "Xception": ["Xception"],
        "NASNet": ["NASNet-Mobile", "NASNet-Large"],
    },
    "Vision Transformers (ViT)": {
        "ViT": ["ViT-Base", "ViT-Large", "ViT-Huge"],
        "DeiT": ["DeiT-Base", "DeiT-Small", "DeiT-Tiny"],
        "Swin": ["Swin-Base", "Swin-Small", "Swin-Tiny"],
        "ConvNeXt": ["ConvNeXt-Base", "ConvNeXt-Small", "ConvNeXt-Tiny"],
        "BEiT": ["BEiT-Base", "BEiT-Large"],
    },
    "Detection & Segmentation": {
        "YOLO": ["YOLOv5", "YOLOv7", "YOLOv8"],
        "Faster R-CNN": ["Faster R-CNN"],
        "Mask R-CNN": ["Mask R-CNN"],
        "RetinaNet": ["RetinaNet"],
        "U-Net": ["U-Net"],
        "DeepLabV3": ["DeepLabV3"],
    },
    "Natural Language Processing (NLP)": {
        "Transformers": ["BERT-Base", "BERT-Large", "RoBERTa-Base", "RoBERTa-Large", "DistilBERT", "ALBERT", "ELECTRA"],
        "Generative": ["GPT-2", "GPT-Neo", "GPT-J", "GPT-NeoX"],
        "Modern LLMs": ["LLaMA-1", "LLaMA-2", "LLaMA-3", "Mistral-7B", "Mixtral-8x7B", "Falcon", "BLOOM"],
        "Specialized": ["T5", "FLAN-T5", "BART", "Pegasus (Summarization)"],
    },
    "Multimodal (Vision + Language)": {
        "General": ["CLIP", "BLIP", "BLIP-2", "Flamingo", "LLaVA", "MiniGPT-4", "Kosmos-2"],
    },
    "Medical AI": {
        "Vision": ["CheXNet (DenseNet-121)", "MedCLIP", "BioViL"],
        "MONAI Models": ["MONAI-UNet", "MONAI-ResNet-18", "MONAI-VNet"],
    }
}

def get_all_model_names():
    names = ["None (Train from scratch)"]
    for cat, subcats in MODEL_REGISTRY.items():
        for subcat, models in subcats.items():
            names.extend(models)
    return names
