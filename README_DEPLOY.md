Here is your complete **Master Deployment Guide**. You can save this file as `README_DEPLOY.md` or simply keep it as your reference.

Follow these steps exactly on your new DGX machine, and the entire system will work immediately.

---

# 🚀 Local PDF-to-JSON Pipeline Deployment Guide

**Objective:** Deploy a local, privacy-first pipeline to process academic PDFs using **vLLM (Qwen-32B)** on NVIDIA DGX hardware.
**System Requirements:** NVIDIA GPU(s) with drivers installed, Docker with NVIDIA Runtime, Python 3.8+.

---

## 🛠️ Part 1: Start the AI Inference Server (vLLM)

We use the NVIDIA container to serve the `nvidia/Qwen3-32B-FP4` model.

**1. Set the Version Variable**
(Or simply use the specific tag provided in your registry)

```bash
export LATEST_VLLM_VERSION=v0.6.3

```

**2. Run the Optimized Server Command**
This command is tuned for **Maximum Quality** (32k context) and **Maximum Performance** (95% GPU usage).

```bash
docker run -d --gpus all \
    -p 8000:8000 \
    --name vllm_server \
    --ipc=host \
    nvcr.io/nvidia/vllm:${LATEST_VLLM_VERSION} \
    vllm serve "nvidia/Qwen3-32B-FP4" \
    --max_model_len 32768 \
    --gpu-memory-utilization 0.95 \
    --trust-remote-code

```

**3. Verification**
Wait 1-2 minutes for the model to load. Run this command to check if it's ready:

```bash
docker logs -f vllm_server

```

*You are ready when you see: `Application Startup Complete`.*
*(Press `Ctrl+C` to exit logs)*

---

## 📂 Part 2: Project Setup & Installation

**1. Create Project Directory**

```bash
mkdir -p ~/paper-pipeline/data/input
mkdir -p ~/paper-pipeline/data/output
mkdir -p ~/paper-pipeline/logs
cd ~/paper-pipeline

```

**2. Setup Python Environment**

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai pypdf

```

---

## 📝 Part 3: The Codebase

Create the following 3 files in your `~/paper-pipeline` folder.

### File 1: `prompt.md`

*Contains the instructions for the AI.*

```markdown
# Role
You are a highly specialized AI Research Assistant. Your function is to analyze scientific papers and convert them into structured JSON.

# Instructions
1. Analyze the provided text.
2. Extract details according to the JSON schema below.
3. Your output must be **strictly valid JSON**.
4. Do NOT output markdown code blocks (like ```json). Just the raw JSON string.
5. Do NOT output any introductory text or explanations.

# JSON Schema
{
  "paper_id": "PLACEHOLDER_ID",
  "metadata": {
    "title": "String (Exact Title)",
    "authors": ["String", "String"],
    "year": Integer,
    "publication_venue": "String (or null)",
    "doi": "String (or null)"
  },
  "summary": {
    "problem_statement": "String (1 sentence)",
    "objective": "String (1 sentence)",
    "key_contribution": "String (1 sentence)"
  },
  "methodology": {
    "approach_type": "String (e.g., 'System Architecture', 'Novel Algorithm')",
    "technologies_and_protocols": ["String", "String"],
    "method_summary": "String (2-3 sentences)"
  },
  "results_and_evaluation": {
    "key_findings": ["String", "String"],
    "evaluation_metrics": ["String", "String"]
  },
  "keywords": ["String", "String", "String"]
}

```

### File 2: `pdf_processor.py`

*Handles text extraction (with smart cleaning) and API communication.*

```python
import json
import re
import os
from pathlib import Path
from openai import OpenAI
from pypdf import PdfReader

class LocalPDFProcessor:
    def __init__(self, base_url="http://localhost:8000/v1", model_name="nvidia/Qwen3-32B-FP4"):
        self.client = OpenAI(base_url=base_url, api_key="EMPTY")
        self.model_name = model_name
        self.system_prompt = self._load_prompt()

    def _load_prompt(self):
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a JSON extractor."

    def extract_text(self, pdf_path, max_chars=120000):
        """Extracts text, removes References section, and handles truncation."""
        print(f"   📖 Reading: {Path(pdf_path).name}")
        try:
            reader = PdfReader(pdf_path)
            full_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
            
            # --- SMART CLEANING: Remove References ---
            # Finds 'References' or 'Bibliography' on a generic line and cuts everything after
            match = re.search(r'\n\s*(References|Bibliography|REFERENCES)\s*\n', full_text)
            if match:
                print(f"   ✂️  Smart Clean: Removed References/Bibliography section.")
                full_text = full_text[:match.start()]
                
            # --- TRUNCATION ---
            if len(full_text) > max_chars:
                print(f"   ⚠️  Truncating text ({len(full_text)} -> {max_chars} chars)")
                return full_text[:max_chars]
                
            return full_text
        except Exception as e:
            print(f"   ❌ Error reading PDF: {e}")
            return None

    def clean_json_response(self, response_text):
        """Cleans <think> tags and markdown to extract raw JSON."""
        # 1. Remove Chain of Thought (<think>...</think>)
        clean = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        
        # 2. Extract from Markdown blocks if present
        json_match = re.search(r'```json\s*(.*?)\s*```', clean, re.DOTALL)
        if json_match:
            clean = json_match.group(1)
        
        return clean.strip()

    def process_pdf(self, pdf_path, category_code, sequence_id):
        path_obj = Path(pdf_path)
        paper_id = f"{category_code}-{sequence_id:03d}"
        
        text = self.extract_text(path_obj)
        if not text: return False

        # Inject dynamic ID into the user prompt
        user_message = f"PAPER ID: {paper_id}\nCATEGORY: {category_code}\n\nPAPER TEXT:\n{text}"

        print(f"   🧠 Analyzing with {self.model_name}...")
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1, 
                max_tokens=4096
            )
            
            raw_output = completion.choices[0].message.content
            json_str = self.clean_json_response(raw_output)
            
            # Parse and Validate
            data = json.loads(json_str)
            data['paper_id'] = paper_id # Ensure ID is correct
            
            # Save
            output_dir = Path("data/output") / category_code
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{paper_id}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            print(f"   ✅ Saved: {output_file}")
            return True

        except Exception as e:
            print(f"   ❌ Failed: {e}")
            # Optional: save failed output for debug
            # with open(f"logs/fail_{paper_id}.txt", "w") as f: f.write(raw_output)
            return False

```

### File 3: `main.py`

*The User Interface CLI.*

```python
import argparse
from pathlib import Path
from pdf_processor import LocalPDFProcessor

INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")

def list_categories():
    if not INPUT_DIR.exists():
        print("❌ 'data/input' not found.")
        return
    print("\n📂 Available Categories:")
    for item in INPUT_DIR.iterdir():
        if item.is_dir():
            files = list(item.glob("*.pdf"))
            if files: print(f"   - {item.name} ({len(files)} PDFs)")

def process_category(processor, category, resume=False, start_from=1):
    cat_dir = INPUT_DIR / category
    if not cat_dir.exists():
        print(f"❌ Category '{category}' not found.")
        return

    files = sorted(list(cat_dir.glob("*.pdf")))
    print(f"\n🚀 Processing Category: {category} ({len(files)} files)")
    
    for idx, pdf_file in enumerate(files, 1):
        if idx < start_from: continue
            
        if resume and (OUTPUT_DIR / category / f"{category}-{idx:03d}.json").exists():
            print(f"   ⏩ Skipping {idx}: {pdf_file.name}")
            continue

        print(f"\n[{idx}/{len(files)}] Processing ID: {category}-{idx:03d}")
        processor.process_pdf(pdf_file, category, idx)

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true")
    group.add_argument("--category", type=str)
    group.add_argument("--all", action="store_true")
    group.add_argument("--file", type=str)
    
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--start-from", type=int, default=1)

    args = parser.parse_args()
    processor = LocalPDFProcessor()

    if args.list: list_categories()
    elif args.category: process_category(processor, args.category, args.resume, args.start_from)
    elif args.file: processor.process_pdf(args.file, Path(args.file).parent.name, 1)
    elif args.all:
        for item in INPUT_DIR.iterdir():
            if item.is_dir(): process_category(processor, item.name, args.resume)

if __name__ == "__main__":
    main()

```

---

## ⚡ Part 4: How to Run It

### 1. Organize Input

Create folders inside `data/input` and drop your PDFs there.

```bash
mkdir data/input/ML
cp my_paper.pdf data/input/ML/

```

### 2. Run Processing

**List what you have:**

```bash
python main.py --list

```

**Process a specific category:**

```bash
python main.py --category ML

```

**Process everything:**

```bash
python main.py --all

```

**Resume if interrupted:**

```bash
python main.py --category ML --resume

```

---

## 🔧 Troubleshooting

* **Error: `connection refused**`
* **Fix:** The Docker container isn't running. Run `docker ps` to check. If missing, restart Part 1.


* **Error: `CUDA out of memory**`
* **Fix:** Stop the container (`docker stop vllm_server; docker rm vllm_server`). Restart it but change `--max_model_len 32768` to `--max_model_len 16384`.


* **Quality is poor?**
* **Fix:** Check `pdf_processor.py`. Ensure `max_chars` is set to `120000` (Step 3).