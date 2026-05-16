from transformers import AutoConfig, AutoModelForCausalLM
import torch

def demo_automodel_parsing():
    # 1. The 'Text Model Structure' (Configuration Markup)
    # This is typically stored in a config.json file
    model_id = "Qwen/Qwen2-7B"
    
    print(f"Step 1: Fetching the 'Markup' (Config) for {model_id}...")
    config = AutoConfig.from_pretrained(model_id)
    
    # Let's look at a piece of the 'text' markup
    print(f"  -> Hidden Size: {config.hidden_size}")
    print(f"  -> Number of Layers: {config.num_hidden_layers}")

    print("\nStep 2: Feeding the Markup into the AutoModel Factory...")
    # This command parses the JSON and builds the PyTorch layers automatically
    # We use device='meta' to see the structure without needing the actual weight files
    model = AutoModelForCausalLM.from_config(
        config, 
        torch_dtype=torch.float16, 
        trust_remote_code=True
    ).to("meta")

    print("\nStep 3: Resulting PyTorch Object")
    print(f"  -> Object Type: {type(model)}")
    print(f"  -> Parameter Count: {sum(p.numel() for p in model.parameters()) / 1e9:.2f} Billion")

if __name__ == "__main__":
    try:
        demo_automodel_parsing()
    except Exception as e:
        print(f"\nNote: To run this demo, you need the 'transformers' library.")
        print(f"Error: {e}")
