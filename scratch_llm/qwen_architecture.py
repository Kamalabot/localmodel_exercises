import torch
import torch.nn as nn
from torch.nn import functional as F

# Qwen 35B Configuration
class QwenConfig:
    n_layer = 60
    n_head = 64
    n_embd = 7168
    vocab_size = 152064
    intermediate_size = 20480 # SwiGLU expansion
    norm_eps = 1e-6

class RMSNorm(nn.Module):
    def __init__(self, dim, eps=1e-6):
        super().__init__()
        self.eps = eps
        self.weight = nn.Parameter(torch.ones(dim))

    def _norm(self, x):
        return x * torch.rsqrt(x.pow(2).mean(-1, keepdim=True) + self.eps)

    def forward(self, x):
        output = self._norm(x.float()).type_as(x)
        return output * self.weight

class QwenMLP(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.w1 = nn.Linear(config.n_embd, config.intermediate_size, bias=False)
        self.w2 = nn.Linear(config.n_embd, config.intermediate_size, bias=False)
        self.w3 = nn.Linear(config.intermediate_size, config.n_embd, bias=False)

    def forward(self, x):
        # SwiGLU activation
        return self.w3(F.silu(self.w1(x)) * self.w2(x))

class QwenAttention(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.n_head = config.n_head
        self.head_dim = config.n_embd // config.n_head
        
        self.wq = nn.Linear(config.n_embd, config.n_embd, bias=True)
        self.wk = nn.Linear(config.n_embd, config.n_embd, bias=True)
        self.wv = nn.Linear(config.n_embd, config.n_embd, bias=True)
        self.wo = nn.Linear(config.n_embd, config.n_embd, bias=False)

    def forward(self, x):
        # ... logic for Rotary Embeddings (RoPE) would go here ...
        return x

class QwenBlock(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.ln_1 = RMSNorm(config.n_embd, eps=config.norm_eps)
        self.attn = QwenAttention(config)
        self.ln_2 = RMSNorm(config.n_embd, eps=config.norm_eps)
        self.mlp = QwenMLP(config)

    def forward(self, x):
        x = x + self.attn(self.ln_1(x))
        x = x + self.mlp(self.ln_2(x))
        return x

class Qwen35B(nn.Module):
    def __init__(self, config):
        super().__init__()
        self.config = config
        self.tok_embeddings = nn.Embedding(config.vocab_size, config.n_embd)
        self.layers = nn.ModuleList([QwenBlock(config) for _ in range(config.n_layer)])
        self.norm = RMSNorm(config.n_embd, eps=config.norm_eps)
        self.output = nn.Linear(config.n_embd, config.vocab_size, bias=False)

def create_meta_qwen():
    config = QwenConfig()
    
    # Use 'meta' device to avoid OOM (Out of Memory)
    # This creates the structure without allocating RAM for weights
    with torch.device("meta"):
        model = Qwen35B(config)
    
    print("--- Qwen 35B Architecture Created on Meta Device ---")
    print(f"Total layers: {len(model.layers)}")
    
    total_params = sum(p.numel() for p in model.parameters())
    print(f"Total Parameters: {total_params / 1e9:.2f} Billion")
    
    return model

if __name__ == "__main__":
    model = create_meta_qwen()
    # Save the textual representation
    with open('qwen_35b_structure.txt', 'w') as f:
        f.write(str(model))
    print("Exported structure to qwen_35b_structure.txt")
