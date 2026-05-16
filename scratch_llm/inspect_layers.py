import torch
from model import GPTLanguageModel

def inspect_model():
    # Initialize a fresh model (the "empty matrix" state)
    # Using a typical vocab size for char-level models
    vocab_size = 65 
    model = GPTLanguageModel(vocab_size)
    
    print("="*60)
    print(f"{'LAYER NAME':<40} | {'PARAMETER SHAPE'}")
    print("="*60)
    
    # Iterate through all modules (layers)
    for name, module in model.named_modules():
        # We only want to print leaf modules (the actual layers like Linear, Embedding, etc.)
        if len(list(module.children())) == 0:
            print(f"{name:<40}")
            # Each layer has one or more parameters (weight, bias)
            for p_name, param in module.named_parameters():
                shape_str = str(list(param.shape))
                print(f"  -> {p_name:<35} | {shape_str}")
            print("-" * 60)

    total_params = sum(p.numel() for p in model.parameters())
    print(f"\nTotal Programmatic Parameters (The 'Empty Matrix'): {total_params:,}")

if __name__ == "__main__":
    inspect_model()
