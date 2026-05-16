# Scratch GPT - Model Card

This is a custom-built Large Language Model (LLM) designed for character-level text generation.

## 🏗️ Architecture (Markup Configuration)
The model structure is defined in `config.json`. Key specifications include:
- **Model Type**: GPT (Decoder-only Transformer)
- **Parameters**: ~10.7M
- **Layers**: 6 Transformer Blocks
- **Attention Heads**: 6
- **Embedding Dimension**: 384

## 📂 File Manifest
- `model.py`: The Python implementation of the layers.
- `config.json`: The architectural markup (metadata).
- `pytorch_model.bin`: (To be generated) The binary weight matrices.
- `architecture.png`: Visual diagram of the layer stack.

## 🚀 Usage
To inspect the layers programmatically:
```bash
python inspect_layers.py
```
