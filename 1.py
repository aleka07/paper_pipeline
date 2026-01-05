import torch
from transformers import AutoTokenizer, AutoModelForCausalLM

# Load tokenizer and model (use FP8 variant if preferred: nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8)
tokenizer = AutoTokenizer.from_pretrained("nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8")
model = AutoModelForCausalLM.from_pretrained(
    "nvidia/NVIDIA-Nemotron-3-Nano-30B-A3B-FP8",
    torch_dtype=torch.float8_e5m2fnuz,
    trust_remote_code=True,
    device_map="auto"  # Auto-distributes across your GPU
)

# Example: Generate with reasoning (model "thinks" step-by-step)
messages = [{"role": "user", "content": "Explain quantum computing in simple terms."}]
inputs = tokenizer.apply_chat_template(messages, tokenize=True, add_generation_prompt=True, return_tensors="pt").to(model.device)
outputs = model.generate(inputs, max_new_tokens=512, temperature=1.0, top_p=1.0)
print(tokenizer.decode(outputs[0]))