import json
import torch
from model import GPTLanguageModel
import os

def export_model_hf_style():
    # 1. Define the "Markup" (Configuration)
    config = {
        "architectures": ["GPTLanguageModel"],
        "vocab_size": 65,
        "n_embd": 384,
        "n_head": 6,
        "n_layer": 6,
        "block_size": 256,
        "dropout": 0.2,
        "model_type": "gpt_scratch"
    }

    # Write the markup file
    with open('config.json', 'w') as f:
        json.dump(config, f, indent=4)
    print("Created config.json (The Model Markup)")

    # 2. Initialize the model and save the raw weights
    model = GPTLanguageModel(config['vocab_size'])
    
    # Save the matrices (weights)
    torch.save(model.state_dict(), 'pytorch_model.bin')
    print("Created pytorch_model.bin (The Raw Matrices)")

    # 3. Export Model Structure as Text
    with open('model_structure.txt', 'w') as f:
        f.write("=== GPT Model Textual Representation ===\n\n")
        f.write(str(model))
        f.write("\n\n=== Parameter Breakdown ===\n")
        for name, param in model.named_parameters():
            f.write(f"{name:<40} | {list(param.shape)}\n")
    print("Created model_structure.txt (The Textual Export)")

    # 4. Create a simple Model Card (Markup Documentation)
    model_card = f"""
# Scratch GPT Model

This model is a custom Transformer implemented in PyTorch.

## Architecture Configuration:
- Layers: {config['n_layer']}
- Heads: {config['n_head']}
- Embedding Dimension: {config['n_embd']}
- Context Length: {config['block_size']}

## File Structure:
- `config.json`: The architectural markup.
- `pytorch_model.bin`: The trained (or empty) weight matrices.
"""
    with open('README.md', 'w') as f:
        f.write(model_card)
    print("Created README.md (The Model Card)")

if __name__ == "__main__":
    export_model_hf_style()
