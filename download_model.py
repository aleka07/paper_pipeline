from huggingface_hub import snapshot_download

model_id = "Qwen/Qwen3-VL-8B-Instruct"

print(f"⏳ Downloading {model_id} (approx 16GB)... This may take a while.")
snapshot_download(repo_id=model_id, resume_download=True)
print("✅ Download complete!")