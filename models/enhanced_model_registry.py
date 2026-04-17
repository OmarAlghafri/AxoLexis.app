"""
Enhanced Model Registry with comprehensive AI task domains and model categories
Updated with all required models from the specification
"""

from typing import Dict, List, Optional, Any, Tuple

# Comprehensive AI Task Domains
AI_TASK_DOMAINS = {
    "Computer Vision": {
        "Image Classification": ["Image Classification", "Multi-label Classification", "Hierarchical Classification"],
        "Object Detection": ["Object Detection", "Instance Segmentation", "Panoptic Segmentation"],
        "Image Segmentation": ["Semantic Segmentation", "Instance Segmentation", "Medical Segmentation"],
        "Image Generation": ["Image Synthesis", "Style Transfer", "Super Resolution"],
        "Video Analysis": ["Video Classification", "Action Recognition", "Video Object Detection"]
    },
    "Natural Language Processing (NLP)": {
        "Text Classification": ["Sentiment Analysis", "Topic Classification", "Intent Detection"],
        "Text Generation": ["Creative Writing", "Code Generation", "Dialogue Generation"],
        "Machine Translation": ["Language Translation", "Cross-lingual Transfer", "Multilingual Models"],
        "Question Answering": ["Reading Comprehension", "Open-domain QA", "Conversational QA"],
        "Summarization": ["Extractive Summarization", "Abstractive Summarization", "Multi-document Summarization"],
        "Sentiment Analysis": ["Aspect-based Sentiment", "Emotion Detection", "Opinion Mining"]
    },
    "Speech & Audio": {
        "Speech Recognition": ["Automatic Speech Recognition", "Speaker Diarization", "Speech-to-Text"],
        "Text-to-Speech (TTS)": ["Neural TTS", "Voice Cloning", "Multilingual TTS"],
        "Audio Classification": ["Music Genre Classification", "Environmental Sound Classification", "Audio Event Detection"]
    },
    "Time Series & Forecasting": {
        "Prediction": ["Time Series Forecasting", "Demand Prediction", "Stock Market Prediction"],
        "Anomaly Detection": ["Time Series Anomaly", "Fraud Detection", "System Monitoring"]
    },
    "Reinforcement Learning": {
        "Decision Making": ["Game Playing", "Resource Allocation", "Strategy Optimization"],
        "Control Systems": ["Robotics Control", "Process Control", "Autonomous Systems"],
        "Robotics": ["Robot Navigation", "Manipulation Tasks", "Multi-agent Systems"]
    },
    "Graph AI": {
        "Node Classification": ["Social Network Analysis", "Fraud Detection", "Recommendation Systems"],
        "Link Prediction": ["Social Link Prediction", "Knowledge Graph Completion", "Network Analysis"],
        "Graph Analysis": ["Graph Classification", "Community Detection", "Graph Generation"]
    },
    "Multimodal AI": {
        "Vision + Language": ["Image Captioning", "Visual Question Answering", "Image-Text Retrieval"],
        "Audio + Text": ["Speech Translation", "Audio Captioning", "Multimodal Dialogue"],
        "Cross-modal Retrieval": ["Text-to-Image Search", "Audio-to-Text Retrieval", "Cross-modal Alignment"]
    }
}

# Enhanced Model Registry with comprehensive model categories
MODEL_REGISTRY = {
    # CNN (Convolutional) Models
    "CNN (Convolutional)": {
        "Classic CNNs": [
            "LeNet", "AlexNet", "VGG-16", "VGG-19"
        ],
        "Modern CNNs": [
            "ResNet-18", "ResNet-34", "ResNet-50", "ResNet-101", "ResNet-152",
            "Inception-V1", "Inception-V2", "Inception-V3", "Inception-V4",
            "DenseNet-121", "DenseNet-169", "DenseNet-201", "DenseNet-264"
        ],
        "Efficient CNNs": [
            "MobileNet-V1", "MobileNet-V2", "MobileNet-V3-Small", "MobileNet-V3-Large",
            "EfficientNet-B0", "EfficientNet-B1", "EfficientNet-B2", "EfficientNet-B3",
            "EfficientNet-B4", "EfficientNet-B5", "EfficientNet-B6", "EfficientNet-B7",
            "SENet", "RegNet-X", "RegNet-Y", "Xception", "ConvNeXt"
        ],
        "Segmentation Models": [
            "U-Net", "U-Net++", "Attention U-Net",
            "FCN-8s", "FCN-16s", "FCN-32s"
        ],
        "Detection Models": [
            "YOLOv1", "YOLOv2", "YOLOv3", "YOLOv4", "YOLOv5", "YOLOv6", "YOLOv7", "YOLOv8", "YOLOv9",
            "SSD", "RetinaNet", "FPN (Feature Pyramid Network)", "Mask R-CNN"
        ]
    },
    
    # Transformers
    "Transformers": {
        "BERT Family": [
            "BERT-Base", "BERT-Large", "RoBERTa-Base", "RoBERTa-Large",
            "ALBERT-Base", "ALBERT-Large", "ALBERT-XLarge", "ALBERT-XXLarge",
            "DistilBERT", "ELECTRA-Base", "ELECTRA-Large", "DeBERTa-Base", "DeBERTa-Large"
        ],
        "Vision Transformers": [
            "ViT-Base", "ViT-Large", "ViT-Huge", "ViT-Giant",
            "Swin-Base", "Swin-Large", "Swin-Huge",
            "DETR (Detection Transformer)", "DeiT-Base", "DeiT-Small", "DeiT-Tiny"
        ],
        "Speech Transformers": [
            "Whisper-Base", "Whisper-Small", "Whisper-Medium", "Whisper-Large", "Whisper-Large-v2"
        ],
        "Modern LLMs": [
            "GPT-2", "GPT-2-Medium", "GPT-2-Large", "GPT-2-XL",
            "LLaMA-1-7B", "LLaMA-1-13B", "LLaMA-1-30B", "LLaMA-1-65B",
            "LLaMA-2-7B", "LLaMA-2-13B", "LLaMA-2-70B",
            "LLaMA-3-8B", "LLaMA-3-70B",
            "Mistral-7B", "Mixtral-8x7B", "Mixtral-8x22B",
            "Gemma-2B", "Gemma-7B", "Falcon-7B", "Falcon-40B", "Falcon-180B",
            "Qwen-7B", "Qwen-14B", "Qwen-72B",
            "Phi-1", "Phi-1.5", "Phi-2", "Phi-3",
            "BLOOM-560M", "BLOOM-1.1B", "BLOOM-1.7B", "BLOOM-3B", "BLOOM-7.1B", "BLOOM-176B"
        ],
        "Specialized Transformers": [
            "T5-Small", "T5-Base", "T5-Large", "T5-3B", "T5-11B",
            "BART-Base", "BART-Large", "Pegasus-Large"
        ]
    },
    
    # RNN Family
    "RNN Family": {
        "Basic RNNs": [
            "Simple RNN", "Vanilla RNN"
        ],
        "LSTM Models": [
            "LSTM", "BiLSTM", "Peephole LSTM", "Stacked LSTM"
        ],
        "GRU Models": [
            "GRU", "BiGRU"
        ],
        "Advanced RNNs": [
            "ESN (Echo State Network)", "IndRNN (Independently RNN)"
        ]
    },
    
    # GNN (Graph Neural Networks)
    "GNN (Graph Neural Networks)": {
        "Graph Convolutional Networks": [
            "GCN (Graph Convolutional Network)", "GAT (Graph Attention Network)",
            "GraphSAGE", "GIN (Graph Isomorphism Network)", "MPNN (Message Passing NN)"
        ],
        "Specialized GNNs": [
            "R-GCN (Relational GCN)", "ChebNet (Chebyshev GCN)", "CayleyNet",
            "AGNN (Attention-based GNN)", "Graph Transformer", "STGNN (Spatio-Temporal GNN)"
        ]
    },
    
    # Generative Models
    "Generative Models": {
        "GANs": [
            "GAN", "DCGAN", "StyleGAN", "StyleGAN2", "StyleGAN3",
            "CycleGAN", "pix2pix", "BigGAN", "ProGAN"
        ],
        "VAEs": [
            "VAE", "β-VAE", "VQ-VAE", "VQ-VAE-2"
        ],
        "Diffusion Models": [
            "DDPM", "DDIM", "Stable Diffusion v1", "Stable Diffusion v2", "Stable Diffusion XL",
            "DALL·E", "DALL·E 2", "Imagen"
        ]
    },
    
    # Advanced & Hybrid Models
    "Advanced & Hybrid": {
        "State Space Models": [
            "Mamba", "S4 (Structured State Space)", "Jamba"
        ],
        "Alternative Architectures": [
            "RWKV", "ConvNeXt", "MLP-Mixer", "ResMLP", "gMLP"
        ],
        "Mixture of Experts": [
            "Mixtral-8x7B", "Mixtral-8x22B", "Qwen2MoE"
        ],
        "Multimodal Models": [
            "CLIP", "FLAVA", "BLIP", "BLIP-2", "Perceiver", "Perceiver IO", "FNet"
        ]
    },
    
    # Reinforcement Learning
    "Reinforcement Learning": {
        "Value-based Methods": [
            "DQN (Deep Q-Network)", "Double DQN", "Dueling DQN", "Rainbow DQN"
        ],
        "Policy Gradient Methods": [
            "A2C", "A3C", "PPO (Proximal Policy Optimization)", "TRPO (Trust Region Policy Optimization)"
        ],
        "Actor-Critic Methods": [
            "DDPG", "TD3 (Twin Delayed DDPG)", "SAC (Soft Actor-Critic)"
        ],
        "Advanced RL": [
            "IMPALA", "R2D2", "AlphaGo", "AlphaZero", "MuZero"
        ]
    }
}

def get_all_model_names():
    """Get all available model names for dropdown"""
    names = ["None (Train from scratch)"]
    for category, subcategories in MODEL_REGISTRY.items():
        for subcategory, models in subcategories.items():
            names.extend(models)
    return names

def get_models_by_task(task_domain: str, task_type: str) -> Dict[str, List[str]]:
    """Get recommended models for specific task domain and type"""
    
    # Task to model mapping
    task_model_mapping = {
        # Computer Vision
        ("Computer Vision", "Image Classification"): {
            "CNN (Convolutional)": ["ResNet-18", "ResNet-50", "EfficientNet-B0", "EfficientNet-B3", "MobileNet-V2"],
            "Vision Transformers": ["ViT-Base", "DeiT-Base", "Swin-Base"]
        },
        ("Computer Vision", "Object Detection"): {
            "Detection Models": ["YOLOv5", "YOLOv8", "Faster R-CNN", "RetinaNet"]
        },
        ("Computer Vision", "Image Segmentation"): {
            "Segmentation Models": ["U-Net", "DeepLabV3", "Mask R-CNN"]
        },
        ("Computer Vision", "Image Generation"): {
            "GANs": ["StyleGAN2", "StyleGAN3", "BigGAN"],
            "Diffusion Models": ["Stable Diffusion v2", "Stable Diffusion XL"]
        },
        
        # NLP
        ("Natural Language Processing (NLP)", "Text Classification"): {
            "BERT Family": ["BERT-Base", "RoBERTa-Base", "DistilBERT", "ALBERT-Base"]
        },
        ("Natural Language Processing (NLP)", "Text Generation"): {
            "Modern LLMs": ["GPT-2", "LLaMA-2-7B", "Mistral-7B", "Falcon-7B"]
        },
        ("Natural Language Processing (NLP)", "Machine Translation"): {
            "Specialized Transformers": ["T5-Base", "T5-Large", "BART-Large"]
        },
        ("Natural Language Processing (NLP)", "Question Answering"): {
            "BERT Family": ["BERT-Large", "RoBERTa-Large", "DeBERTa-Large"]
        },
        
        # Speech & Audio
        ("Speech & Audio", "Speech Recognition"): {
            "Speech Transformers": ["Whisper-Base", "Whisper-Small", "Whisper-Large"]
        },
        ("Speech & Audio", "Text-to-Speech (TTS)") : {
            "Modern LLMs": ["LLaMA-2-7B", "Mistral-7B"]  # For neural TTS
        },
        
        # Time Series
        ("Time Series & Forecasting", "Prediction"): {
            "RNN Family": ["LSTM", "GRU", "BiLSTM"],
            "Advanced & Hybrid": ["RWKV", "S4"]
        },
        
        # Reinforcement Learning
        ("Reinforcement Learning", "Decision Making"): {
            "Actor-Critic Methods": ["PPO", "A2C", "SAC"]
        },
        
        # Graph AI
        ("Graph AI", "Node Classification"): {
            "GNN (Graph Neural Networks)": ["GCN", "GAT", "GraphSAGE"]
        },
        
        # Multimodal
        ("Multimodal AI", "Vision + Language"): {
            "Multimodal Models": ["CLIP", "BLIP", "BLIP-2", "LLaVA"]
        }
    }
    
    # Return mapped models or default models
    key = (task_domain, task_type)
    if key in task_model_mapping:
        return task_model_mapping[key]
    
    # Default recommendation based on task domain
    if task_domain == "Computer Vision":
        return {"CNN (Convolutional)": ["ResNet-50", "EfficientNet-B0"]}
    elif task_domain == "Natural Language Processing (NLP)":
        return {"BERT Family": ["BERT-Base", "RoBERTa-Base"]}
    else:
        return {"Modern LLMs": ["LLaMA-2-7B", "Mistral-7B"]}

def get_task_domains() -> Dict[str, List[str]]:
    """Get all available task domains and their task types"""
    return AI_TASK_DOMAINS

def validate_task_compatibility(task_domain: str, task_type: str, model_category: str, model_name: str) -> bool:
    """Validate if a model is compatible with the selected task"""
    
    # Get recommended models for the task
    recommended_models = get_models_by_task(task_domain, task_type)
    
    # Check if the selected model is in recommended models
    for category, models in recommended_models.items():
        if model_name in models:
            return True
    
    # Additional compatibility checks
    if task_domain == "Computer Vision":
        vision_models = ["CNN", "ViT", "Swin", "ConvNeXt", "EfficientNet", "ResNet", "VGG", "DenseNet", "MobileNet", "Inception"]
        return any(vision_keyword in model_name for vision_keyword in vision_models)
    
    elif task_domain == "Natural Language Processing (NLP)":
        nlp_models = ["BERT", "GPT", "T5", "BART", "RoBERTa", "LLaMA", "Mistral", "Falcon", "Qwen", "Phi", "BLOOM", "Transformer"]
        return any(nlp_keyword in model_name for nlp_keyword in nlp_models)
    
    elif task_domain == "Speech & Audio":
        audio_models = ["Whisper", "Speech", "Audio"]
        return any(audio_keyword in model_name for audio_keyword in audio_models)
    
    elif task_domain == "Multimodal AI":
        multimodal_models = ["CLIP", "BLIP", "LLaVA", "Flamingo", "Kosmos", "Multimodal"]
        return any(multimodal_keyword in model_name for multimodal_keyword in multimodal_models)
    
    return False  # Default to incompatible if no match found