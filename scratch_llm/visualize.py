import torch
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from model import GPTLanguageModel
import os

def visualize_weights(checkpoint_path):
    if not os.path.exists(checkpoint_path):
        print(f"Checkpoint {checkpoint_path} not found.")
        return

    checkpoint = torch.load(checkpoint_path, map_location='cpu')
    state_dict = checkpoint['model']
    vocab_size = checkpoint['vocab_size']
    
    # Initialize model to get structure
    model = GPTLanguageModel(vocab_size)
    model.load_state_dict(state_dict)
    
    # 1. Visualize Embedding Matrix
    plt.figure(figsize=(15, 10))
    emb_weights = state_dict['token_embedding_table.weight'].numpy()
    sns.heatmap(emb_weights[:100, :100], cmap='viridis')
    plt.title("Token Embedding Matrix (First 100x100 segment)")
    plt.xlabel("Embedding Dimension")
    plt.ylabel("Token Index")
    plt.savefig('visual_embedding_matrix.png')
    plt.close()
    print("Saved visual_embedding_matrix.png")

    # 2. Visualize Weight Distribution in a Block
    plt.figure(figsize=(12, 6))
    weights = state_dict['blocks.0.sa.heads.0.key.weight'].flatten().numpy()
    plt.hist(weights, bins=100, color='skyblue', edgecolor='black')
    plt.title("Distribution of Weights in Block 0 Attention Key Matrix")
    plt.xlabel("Weight Value")
    plt.ylabel("Frequency")
    plt.savefig('visual_weight_distribution.png')
    plt.close()
    print("Saved visual_weight_distribution.png")

    # 3. Visualize Multi-Head Attention Head (First Block)
    plt.figure(figsize=(10, 8))
    q_weight = state_dict['blocks.0.sa.heads.0.query.weight'].numpy()
    sns.heatmap(q_weight[:50, :50], cmap='magma')
    plt.title("Query Matrix Weights (Block 0, Head 0, 50x50 segment)")
    plt.savefig('visual_query_matrix.png')
    plt.close()
    print("Saved visual_query_matrix.png")

    print("\nVisual Exploration Complete. Check the generated .png files.")

if __name__ == "__main__":
    # Look for the latest checkpoint
    checkpoints = [f for f in os.listdir('.') if f.startswith('gpt_checkpoint_iter_') and f.endswith('.pth')]
    if checkpoints:
        latest = sorted(checkpoints, key=lambda x: int(x.split('_')[-1].split('.')[0]))[-1]
        print(f"Visualizing weights from {latest}...")
        visualize_weights(latest)
    else:
        print("No checkpoints found. Training might not have started yet.")
        # We can still visualize the "empty" matrix by initializing a fresh model
        print("Visualizing a fresh 'empty' matrix...")
        model = GPTLanguageModel(65) # Dummy vocab size
        torch.save({'model': model.state_dict(), 'vocab_size': 65}, 'empty_model.pth')
        visualize_weights('empty_model.pth')
