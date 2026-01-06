# 📘 Paper Pipeline

A **100% local AI pipeline** for extracting structured data from academic research papers. It converts PDF papers into rich Markdown (with visual analysis) and then into structured JSON using large language models.

**Key Features:**
- 🔒 **Fully local** - No data leaves your machine
- 👁️ **Vision-enabled** - AI describes charts, diagrams, and figures using Qwen3-VL
- 📊 **Structured output** - Clean JSON for databases, analysis, or RAG systems
- ⚡ **Two-phase architecture** - Vision (Docling) → Logic (vLLM)

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DUAL-ENGINE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │    PDFs     │────▶│  PHASE 1    │────▶│  Markdown   │           │
│  │  (input)    │     │  Docling +  │     │  (with VLM  │           │
│  └─────────────┘     │  Qwen3-VL   │     │  analysis)  │           │
│                      └─────────────┘     └──────┬──────┘           │
│                                                 │                   │
│                                                 ▼                   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │    JSON     │◀────│  PHASE 2    │◀────│  Markdown   │           │
│  │  (output)   │     │ Qwen3-14B   │     │  files      │           │
│  └─────────────┘     │  via vLLM   │     └─────────────┘           │
│                      └─────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

| Engine | Model | Role | Runs On |
|--------|-------|------|---------|
| **Vision (Phase 1)** | `Qwen/Qwen3-VL-8B-Instruct` | Reads PDFs, describes charts/diagrams | Python (Docling) |
| **Logic (Phase 2)** | `nvidia/Qwen3-14B-FP8` | Analyzes markdown, generates JSON | Docker (vLLM) |

---

## Quick Start

### 1. Start the LLM Server (Docker)

```bash
docker run -d --gpus all -p 8000:8000 \
  nvcr.io/nvidia/vllm:v0.6.3 \
  vllm serve "nvidia/Qwen3-14B-FP8" \
  --max_model_len 40960 \
  --gpu-memory-utilization 0.45
```

```bash
docker run -d --gpus all -p 8000:8000 \
  -v ~/.cache/huggingface:/root/.cache/huggingface \
  nvcr.io/nvidia/vllm:${LATEST_VLLM_VERSION} \
  vllm serve "nvidia/Qwen3-32B-FP4" \
  --max_model_len 40960 \
  --gpu-memory-utilization 0.45
```

> **Note:** The FP8 model has a max context of 40960 tokens. Don't set `--max_model_len` higher.

Wait for `Application Startup Complete` in logs:
```bash
docker logs -f <container_id>
```

### 2. Setup Python Environment

```bash
# Using conda (recommended)
conda create -n paper-pipeline python=3.12
conda activate paper-pipeline

# Install dependencies
pip install openai docling docling-core torch transformers easyocr pymupdf
```

### 3. Run the Pipeline

```bash
# Place PDFs in data/input/CategoryName/
mkdir -p data/input/MyPapers
cp paper.pdf data/input/MyPapers/

# Process a single file
python main.py --file data/input/MyPapers/paper.pdf

# Process entire category
python main.py --category MyPapers

# Process ALL categories
python main.py --all
```

---

## Directory Structure

```
paper-pipeline/
├── main.py              # CLI entry point
├── pdf_processor.py     # Core processing logic
├── prompt.md            # LLM system prompt for JSON extraction
├── test_nougat.py       # Alternative math extraction (Nougat)
├── data/
│   ├── input/           # Place PDF folders here
│   │   └── CategoryName/
│   │       └── paper.pdf
│   ├── markdown/        # Phase 1 output (intermediate)
│   │   └── CategoryName/
│   │       └── CategoryName-001.md
│   └── output/          # Phase 2 output (final JSON)
│       └── CategoryName/
│           └── CategoryName-001.json
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py --list` | Show all categories with file counts |
| `python main.py --file path/to/paper.pdf` | Process single PDF |
| `python main.py --category CategoryName` | Process all PDFs in category |
| `python main.py --all` | Process ALL categories |

---

## Configuration

### OCR Settings

The pipeline uses **EasyOCR** (GPU-accelerated) for optical character recognition. Configured in `pdf_processor.py`:

```python
pipeline_options.do_ocr = True
pipeline_options.ocr_options = EasyOcrOptions(
    use_gpu=True,
    lang=["en"]  # Add more languages if needed
)
```

### VLM Settings (Image Analysis)

```python
PictureDescriptionVlmOptions(
    repo_id="Qwen/Qwen3-VL-8B-Instruct",
    scale=3.0,                    # Image upscaling (higher = better quality)
    min_coverage_area_pct=0.01,   # Process images ≥1% of page
    batch_size=1,
    generation_config={
        "max_new_tokens": 2048,   # Prevents truncation
        "temperature": 0.2
    }
)
```

### LLM Settings (JSON Generation)

In `pdf_processor.py`:
```python
max_tokens=8192  # Output token limit (needs 40K+ context)
temperature=0.3  # Lower = more deterministic
```

---

## Output JSON Schema

```json
{
  "paper_id": "CategoryName-001",
  "metadata": {
    "title": "...",
    "authors": ["..."],
    "year": 2024,
    "publication_venue": "...",
    "doi": "..."
  },
  "summary": {
    "problem_statement": "...",
    "objective": "...",
    "key_contribution": "..."
  },
  "methodology": {
    "approach_type": "...",
    "technologies_and_protocols": ["..."],
    "method_summary": "..."
  },
  "results_and_evaluation": {
    "key_findings": ["..."],
    "evaluation_metrics": ["..."]
  },
  "keywords": ["..."]
}
```

---

## Troubleshooting

### Error: `connection refused`
Docker container not running. Check with `docker ps`.

### Error: `max_tokens is too large`
Input is too long. Either:
- Increase `--max_model_len` in Docker (up to 40960 for FP8)
- Reduce `max_tokens` in `pdf_processor.py`

### Error: `CUDA out of memory`
Reduce docker GPU usage:
```bash
--gpu-memory-utilization 0.35
```

### OCR: `RapidOCR returned empty result`
This was a known issue with RapidOCR on some hardware. We now use EasyOCR.

### Math equations look broken in Markdown?
Try the **Nougat** alternative for math-heavy papers:
```bash
python test_nougat.py
```

---

## Performance Notes

- **Phase 1** (Vision): ~5-15 min per PDF (VLM analyzes each image)
- **Phase 2** (Logic): ~10-30 sec per file (LLM inference)
- GPU memory split: ~45% Docker (vLLM), ~50% Python (Docling + Qwen-VL)
- Processing 12-page paper with EasyOCR: ~13 minutes

---

## Alternative: Nougat for Math

For papers with heavy mathematical equations, Nougat (Meta AI) provides better LaTeX extraction:

```bash
python test_nougat.py
```

Output: `data/nougat_output/*.mmd`

Nougat uses `\bmatrix` and `\begin{array}` for matrices instead of hallucinating integrals.
