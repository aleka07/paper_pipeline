# 📘 Paper Pipeline - Project Overview

## What is this?

A **100% local AI pipeline** for extracting structured data from academic research papers. It converts PDF papers into rich Markdown (with visual analysis) and then into structured JSON using large language models.

**Key Features:**
- 🔒 **Fully local** - No data leaves your machine
- 👁️ **Vision-enabled** - AI describes charts, diagrams, and figures
- 📊 **Structured output** - Clean JSON for databases, analysis, or RAG systems
- ⚡ **Two-phase architecture** - Batch convert all PDFs first, then generate JSON

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                     DUAL-ENGINE ARCHITECTURE                        │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │    PDFs     │────▶│  PHASE 1    │────▶│  Markdown   │           │
│  │  (input)    │     │  Docling +  │     │  (with VLM  │           │
│  └─────────────┘     │  Qwen3-VL   │     │  analysis)  │           │
│                      └─────────────┘     └──────┬──────┘           │
│                                                 │                   │
│                                                 ▼                   │
│  ┌─────────────┐     ┌─────────────┐     ┌─────────────┐           │
│  │    JSON     │◀────│  PHASE 2    │◀────│  Markdown   │           │
│  │  (output)   │     │  Qwen3-32B  │     │  files      │           │
│  └─────────────┘     │  via vLLM   │     └─────────────┘           │
│                      └─────────────┘                                │
└─────────────────────────────────────────────────────────────────────┘
```

| Engine | Model | Role | Runs On |
|--------|-------|------|---------|
| **Vision (Phase 1)** | `Qwen/Qwen3-VL-8B-Instruct` | Reads PDFs, describes charts/diagrams | Python (Docling) |
| **Logic (Phase 2)** | `nvidia/Qwen3-32B-FP4` | Analyzes markdown, generates JSON | Docker (vLLM) |

---

## Directory Structure

```
paper-pipeline/
├── main.py              # CLI entry point
├── pdf_processor.py     # Core processing logic
├── prompt.md            # LLM system prompt for JSON extraction
├── data/
│   ├── input/           # Place PDF folders here
│   │   └── CategoryName/
│   │       ├── paper1.pdf
│   │       └── paper2.pdf
│   ├── markdown/        # Phase 1 output (intermediate)
│   │   └── CategoryName/
│   │       ├── CategoryName-001.md
│   │       └── CategoryName-002.md
│   └── output/          # Phase 2 output (final JSON)
│       └── CategoryName/
│           ├── CategoryName-001.json
│           └── CategoryName-002.json
└── logs/
```

---

## CLI Commands

| Command | Description |
|---------|-------------|
| `python main.py --list` | Show all categories with file counts |
| `python main.py --convert` | Phase 1: Convert ALL PDFs → Markdown |
| `python main.py --convert CategoryName` | Phase 1: Only specific category |
| `python main.py --generate` | Phase 2: Generate ALL JSON from Markdown |
| `python main.py --generate CategoryName` | Phase 2: Only specific category |
| `python main.py --full` | Run both phases |
| `python main.py --full CategoryName --resume` | Both phases, skip existing |

**The `--resume` flag** skips files that already have output (smart resume for long batches).

---

## How It Works

### Phase 1: PDF → Markdown (Vision)

**File:** `pdf_processor.py` → `convert_pdf_to_markdown()`

1. **Docling** parses the PDF structure (text, tables, images)
2. **TableFormer** extracts table structures accurately
3. **Qwen3-VL-8B** analyzes each image/chart and writes descriptions
4. Results are exported as rich Markdown

**VLM Prompt** (for image analysis):
```
Analyze this image from a scientific/academic paper...
- For CHARTS: extract all numeric values, axis labels, trends
- For DIAGRAMS: describe components and connections
- For TABLES: list headers and key values
```

### Phase 2: Markdown → JSON (Logic)

**File:** `pdf_processor.py` → `generate_json_from_markdown()`

1. Reads the Markdown file
2. Sends to **Qwen3-32B** via vLLM (OpenAI-compatible API)
3. LLM extracts structured data following the schema in `prompt.md`
4. Response is cleaned (removes `<think>` tags, extracts JSON)
5. Saved as validated JSON

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
  "visual_insights": {
    "has_visuals": true,
    "description": "..."
  },
  "keywords": ["..."]
}
```

---

## Configuration

### VLM Settings (in `pdf_processor.py`)

```python
PictureDescriptionVlmOptions(
    repo_id="Qwen/Qwen3-VL-8B-Instruct",
    temperature=0.2,
    scale=2.0,                    # Image upscaling factor
    max_new_tokens=1024,          # Prevents mid-sentence cutoff
    min_coverage_area_pct=0.01,   # Process images ≥1% of page
    batch_size=1                  # One image at a time
)
```

### Processing Options

| Option | Current Setting | Notes |
|--------|-----------------|-------|
| `do_ocr` | `False` | Disabled for digital PDFs (Scopus 2020+) |
| `do_table_structure` | `True` | TableFormer for accurate table extraction |
| `do_formula_enrichment` | `True` | LaTeX formula detection |
| `do_picture_description` | `True` | VLM describes charts/diagrams |

---

## Prerequisites

### 1. Docker (vLLM for Logic Engine)

```bash
docker run -d --gpus all \
    -p 8000:8000 \
    --name vllm_server \
    --ipc=host \
    -v ~/.cache/huggingface:/root/.cache/huggingface \
    nvcr.io/nvidia/vllm:v0.6.3 \
    vllm serve "nvidia/Qwen3-32B-FP4" \
    --max_model_len 32768 \
    --gpu-memory-utilization 0.5 \
    --trust-remote-code
```

### 2. Python Environment

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install openai docling docling-core torch transformers
```

---

## Typical Workflow

```bash
# 1. Check what's available
python main.py --list

# 2. Convert all PDFs to Markdown (takes time - VLM analysis)
python main.py --convert --resume

# 3. Generate JSON from Markdown (faster - just LLM inference)
python main.py --generate --resume

# 4. Check results
ls data/output/*/
```

---

## Performance Notes

- **Phase 1** is slow (~1-3 min per PDF) due to VLM image analysis
- **Phase 2** is fast (~10-30 sec per file) - just LLM inference
- Use `--resume` to skip already-processed files
- GPU memory is split 50/50 between Docker (vLLM) and Python (Docling)

---

## Files Reference

| File | Purpose |
|------|---------|
| `main.py` | CLI interface, orchestrates phases |
| `pdf_processor.py` | Core `LocalPDFProcessor` class |
| `prompt.md` | System prompt for JSON extraction |
| `DOC.md` | Original project documentation |
| `README_DEPLOY.md` | Deployment instructions |
