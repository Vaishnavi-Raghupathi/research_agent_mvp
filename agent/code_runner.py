import subprocess
import tempfile
import os

# BUG FIX: Ensure both generate_code and fix_code are imported
# They are required by the functions defined here.
from agent.codegen import generate_code, fix_code
import torch
import torch.nn as nn


def execute_code_in_sandbox(code_string: str):
    """Runs Python code in a temp file and returns (success, output)."""
    with tempfile.NamedTemporaryFile(mode="w", suffix=".py", delete=False) as tmp:
        tmp.write(code_string)
        path = tmp.name

    try:
        result = subprocess.run(
            [os.sys.executable, path],
            capture_output=True,
            text=True,
            timeout=15, # Increased timeout slightly for large models
            check=False # CRITICAL: Prevents Python from raising exception on return code != 0
        )

        success = (result.returncode == 0)
        output = result.stdout if success else result.stderr

    except subprocess.TimeoutExpired:
        success = False
        output = "TimeoutExpired: Code execution exceeded the 15-second limit."
    except subprocess.SubprocessError as e:
        success = False
        output = str(e)

    finally:
        os.remove(path)

    return success, output


def run_code_agent_loop(summary, equations, max_iters=5):
    print("--- 1/3: Generating Initial Code ---")
    current = generate_code(summary, equations)

    for i in range(1, max_iters + 1):
        print(f"\n--- Iteration {i}/{max_iters}: Executing Code ---")
        
        success, output = execute_code_in_sandbox(current)

        if success:
            print("\n--- SUCCESS: Code Executed Cleanly! ---")
            return current

        # BUG FIX: Added code to show the last 5 lines of the error for visibility
        error_lines = output.strip().splitlines()
        print("\n--- ERROR FOUND (Last 5 lines) ---")
        print("\n".join(error_lines[-5:]))

        if i == max_iters:
            print("\n--- FAILED AFTER MAX ITERATIONS 💀 ---")
            return None
            
        print("\n--- FIXING CODE USING LLM ---")
        current = fix_code(current, output)

    return None # Should not be reached

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super(PositionalEncoding, self).__init__()
        self.encoding = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-torch.log(torch.tensor(10000.0)) / d_model))
        self.encoding[:, 0::2] = torch.sin(position * div_term)
        self.encoding[:, 1::2] = torch.cos(position * div_term)
        self.encoding = self.encoding.unsqueeze(0)

    def forward(self, x):
        seq_len = x.size(1)
        return x + self.encoding[:, :seq_len, :].to(x.device)

class TransformerLayer(nn.Module):
    def __init__(self, d_model, nhead):
        super(TransformerLayer, self).__init__()
        self.self_attn = nn.MultiheadAttention(embed_dim=d_model, num_heads=nhead)
        self.linear1 = nn.Linear(d_model, d_model)
        self.dropout = nn.Dropout(0.1)
        self.norm1 = nn.LayerNorm(d_model)
        self.norm2 = nn.LayerNorm(d_model)
        self.activation = nn.ReLU()

    def forward(self, input_seq):
        # Ensure query, key, and value are passed correctly
        attn_output, _ = self.self_attn(input_seq, input_seq, input_seq)
        input_seq = input_seq + self.dropout(attn_output)
        input_seq = self.norm1(input_seq)
        linear_output = self.linear1(input_seq)
        input_seq = input_seq + self.dropout(self.activation(linear_output))
        input_seq = self.norm2(input_seq)
        return input_seq

# Example usage
class ExampleModel(nn.Module):
    def __init__(self, input_dim, d_model, nhead):
        super(ExampleModel, self).__init__()
        self.positional_encoding = PositionalEncoding(d_model)
        self.encoder = nn.Linear(input_dim, d_model)
        self.transformer_layer = TransformerLayer(d_model, nhead)

    def forward(self, input_seq):
        input_seq = self.encoder(input_seq)
        input_seq = self.positional_encoding(input_seq)
        return self.transformer_layer(input_seq)

# Ensure tensors have correct dimensions
input_seq = torch.randn(10, 256, 128)  # Example input
model = ExampleModel(128, 256, 8)
output = model(input_seq)
print(output.shape)