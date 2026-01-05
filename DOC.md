This is your **Project Bible**. It contains everything you need to recreate, understand, and run your High-Performance Local Research Pipeline.

Save this content as `README.md` or `PROJECT_DOCS.md` in your project root.

---

# 📘 Project: Dual-Engine Local Paper Analysis Pipeline

## 1. System Architecture

This project uses a **Dual-Engine Architecture** to process scientific papers locally with high accuracy. It separates "Vision" (reading the PDF) from "Reasoning" (analyzing the content).

| Component | Model | Function | Hosted Where? |
| --- | --- | --- | --- |
| **Engine A (Vision)** | **`Qwen/Qwen3-VL-8B-Instruct`** | Reads PDF, charts, diagrams, and converts them to Markdown. | Python Script (`docling`) |
| **Engine B (Logic)** | **`nvidia/Qwen3-32B-FP4`** | Reads the Markdown, extracts insights, and creates JSON. | Docker (`vLLM`) |

### Why this architecture?

* **Accuracy:** Standard PDF tools lose data in charts. `Qwen3-VL` "sees" the charts and describes them.
* **Privacy:** Everything runs 100% locally on your DGX.
* **Efficiency:** We split the GPU 50/50 so both models run simultaneously without crashing.

---

## 2. Installation & Setup

### Step 1: The Folder Structure

Run these commands to set up the project skeleton on a new machine.

```bash
mkdir -p ~/paper-pipeline/data/input
mkdir -p ~/paper-pipeline/data/output
mkdir -p ~/paper-pipeline/data/debug_markdown
mkdir -p ~/paper-pipeline/logs
mkdir -p ~/.cache/huggingface  # Critical for model caching
cd ~/paper-pipeline

```

### Step 2: The Docker Engine (Logic)

This starts the Logic Brain (Qwen 32B). We map the cache volume so it **doesn't download the model every time**.

```bash
# Set the version
export LATEST_VLLM_VERSION=v0.6.3

# Run the container
docker run -d --gpus all \
    -p 8000:8000 \
    --name vllm_server \
    --ipc=host \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    nvcr.io/nvidia/vllm:${LATEST_VLLM_VERSION} \
    vllm serve "nvidia/Qwen3-32B-FP4" \
    --max_model_len 32768 \
    --gpu-memory-utilization 0.5 \
    --trust-remote-code

```

* **`--gpu-memory-utilization 0.5`**: Reserves 50% GPU for Docker, leaving 50% for the Vision script.
* **`-v ...`**: Saves models to your local disk so restarts are instant.

### Step 3: Python Environment (Vision)

This sets up the Vision Eye (Qwen-VL).

```bash
python3 -m venv .venv
source .venv/bin/activate

# Install critical dependencies
pip install openai pypdf docling docling-core

```

---

## 3. The Codebase

Create these three files in `~/paper-pipeline/`.

### File 1: `prompt.md`

*The instructions for the Logic Engine.*

```markdown
# Role
You are a highly specialized AI Research Assistant. Your function is to analyze scientific papers and convert them into structured JSON.

# Instructions
1. Analyze the provided text.
2. Extract details according to the JSON schema below.
3. Your output must be **strictly valid JSON**.
4. Do NOT output markdown code blocks (like ```json). Just the raw JSON string.

# JSON Schema
{
  "paper_id": "PLACEHOLDER_ID",
  "metadata": {
    "title": "String",
    "authors": ["String"],
    "year": Integer,
    "publication_venue": "String",
    "doi": "String"
  },
  "summary": {
    "problem_statement": "String (1 sentence)",
    "objective": "String (1 sentence)",
    "key_contribution": "String (1 sentence)"
  },
  "methodology": {
    "approach_type": "String",
    "technologies_and_protocols": ["String"],
    "method_summary": "String (2-3 sentences)"
  },
  "results_and_evaluation": {
    "key_findings": ["String"],
    "evaluation_metrics": ["String"]
  },
  "keywords": ["String"]
}

```

### File 2: `pdf_processor.py`

*The Engine Driver. Connects Vision (Docling) to Logic (vLLM).*

```python
import json
import re
import os
import time
from pathlib import Path
from openai import OpenAI

# Docling & Qwen-VL Imports
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    AcceleratorOptions,
    AcceleratorDevice,
    PictureDescriptionVlmOptions
)
from docling.datamodel.pipeline_options_vlm_model import (
    InferenceFramework,
    TransformersModelType
)

class LocalPDFProcessor:
    def __init__(self, base_url="http://localhost:8000/v1", model_name="nvidia/Qwen3-32B-FP4"):
        self.client = OpenAI(base_url=base_url, api_key="EMPTY")
        self.model_name = model_name
        self.system_prompt = self._load_prompt()
        
        print("   ⚙️  Initializing Docling Vision Pipeline (Qwen3-VL-8B-Instruct)...")
        self.converter = self._setup_docling()

    def _load_prompt(self):
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a JSON extractor."

    def _setup_docling(self):
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        
        # --- VISION CONFIGURATION ---
        pipeline_options.do_picture_description = True
        pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
            repo_id="Qwen/Qwen3-VL-8B-Instruct",  # STRICTLY ENFORCED MODEL
            prompt="Describe this image in detail. Extract data trends from charts and connection flows from diagrams.",
            inference_framework=InferenceFramework.TRANSFORMERS,
            transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
            temperature=0.1,
            scale=2.0
        )

        pipeline_options.accelerator_options = AcceleratorOptions(
            num_threads=8,
            device=AcceleratorDevice.CUDA
        )

        return DocumentConverter(
            format_options={
                InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
            }
        )

    def extract_markdown(self, pdf_path):
        print(f"   👁️  Visual Analysis: {Path(pdf_path).name}...")
        try:
            start_t = time.time()
            result = self.converter.convert(pdf_path)
            md_content = result.document.export_to_markdown(image_placeholder="\n\n> **[Visual Content Description]**\n")
            print(f"   ✅ Visual Analysis complete ({time.time() - start_t:.1f}s)")
            return md_content
        except Exception as e:
            print(f"   ❌ Docling Error: {e}")
            return None

    def clean_json_response(self, response_text):
        clean = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        json_match = re.search(r'```json\s*(.*?)\s*```', clean, re.DOTALL)
        if json_match: return json_match.group(1)
        return clean.strip()

    def process_pdf(self, pdf_path, category_code, sequence_id):
        path_obj = Path(pdf_path)
        paper_id = f"{category_code}-{sequence_id:03d}"
        
        # 1. Vision Phase
        markdown_text = self.extract_markdown(str(path_obj))
        if not markdown_text: return False

        # Save Debug Markdown
        (Path("data/debug_markdown") / category_code).mkdir(parents=True, exist_ok=True)
        with open(f"data/debug_markdown/{category_code}/{paper_id}.md", "w") as f:
            f.write(markdown_text)

        # 2. Logic Phase
        user_message = f"PAPER ID: {paper_id}\nCATEGORY: {category_code}\n\nCONTENT:\n{markdown_text}"
        
        print(f"   🧠 Logic Analysis with {self.model_name}...")
        try:
            completion = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                temperature=0.1, max_tokens=4096
            )
            
            data = json.loads(self.clean_json_response(completion.choices[0].message.content))
            data['paper_id'] = paper_id
            
            output_dir = Path("data/output") / category_code
            output_dir.mkdir(parents=True, exist_ok=True)
            with open(output_dir / f"{paper_id}.json", "w") as f:
                json.dump(data, f, indent=2)
                
            print(f"   ✅ Saved: data/output/{category_code}/{paper_id}.json")
            return True
        except Exception as e:
            print(f"   ❌ Logic Failed: {e}")
            return False

```

### File 3: `main.py`

*The Command Line Interface.*

```python
import argparse
from pathlib import Path
from pdf_processor import LocalPDFProcessor

INPUT_DIR = Path("data/input")

def main():
    parser = argparse.ArgumentParser()
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List categories")
    group.add_argument("--category", type=str, help="Process category folder")
    group.add_argument("--all", action="store_true", help="Process ALL")
    group.add_argument("--file", type=str, help="Process single file")
    
    args = parser.parse_args()
    processor = LocalPDFProcessor()

    if args.list:
        if INPUT_DIR.exists():
            for d in INPUT_DIR.iterdir():
                if d.is_dir(): print(f" - {d.name}")
    
    elif args.file:
        processor.process_pdf(args.file, Path(args.file).parent.name, 1)

    elif args.category:
        cat_dir = INPUT_DIR / args.category
        files = sorted(list(cat_dir.glob("*.pdf")))
        print(f"🚀 Category: {args.category} ({len(files)} files)")
        for i, f in enumerate(files, 1):
            print(f"\nProcessing {i}/{len(files)}: {f.name}")
            processor.process_pdf(f, args.category, i)

    elif args.all:
        for d in INPUT_DIR.iterdir():
            if d.is_dir():
                files = sorted(list(d.glob("*.pdf")))
                print(f"🚀 Category: {d.name}")
                for i, f in enumerate(files, 1):
                    processor.process_pdf(f, d.name, i)

if __name__ == "__main__":
    main()

```

---

## 4. Operational Workflow

### Daily Start-up

1. **Check Docker:**
```bash
docker ps

```


*If not running, run the command in Step 2.*
2. **Activate Python:**
```bash
source .venv/bin/activate

```



### Adding New Data

1. Create a folder: `mkdir data/input/NewTopic`
2. Copy PDFs there.

### Running Analysis

* **One Category:** `python main.py --category NewTopic`
* **Everything:** `python main.py --all`
* **One File:** `python main.py --file data/input/NewTopic/paper.pdf`

### Checking Results

* **JSON Output:** `data/output/NewTopic/NewTopic-001.json`
* **Visual Debug:** `data/debug_markdown/NewTopic/NewTopic-001.md` (Open this to see how Qwen-VL described the charts).