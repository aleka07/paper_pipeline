# GEMINI.md - Project-Specific Agent Instructions

## Environment Setup

**Always activate the conda environment before running any commands:**

```bash
conda activate paper-pipeline
```

This applies to:
- Running Python scripts (`main.py`, `pdf_processor.py`, etc.)
- Installing dependencies
- Running tests
- Starting the backend/frontend servers

## Codebase Patterns

### Architecture
- Backend uses Flask with a REST API, serves on `0.0.0.0:5000` for LAN access
- Frontend is vanilla HTML/CSS/JS in `frontend/` directory
- PDF processing uses Docling (vision) and vLLM/Ollama (logic) via `LocalPDFProcessor`
- Flask serves static files from `../frontend` relative to `backend/app.py`
- **LLM Model**: Use `nemotron-large-ctx:latest` via Ollama for Phase 2 processing

### Directory Structure
- Input PDFs: `data/input/<category>/`
- Markdown output: `data/markdown/<category>/`
- JSON output: `data/output/<category>/`
- Category operations must create/delete folders in all three directories

### File Status Logic
File status derived from existence checks (in this order):
1. `.json` in `data/output/` → `completed`
2. `.md` in `data/markdown/` → `markdown` (phase 1 done, needs phase 2)
3. PDF exists only → `pending`

### File Handling
- File IDs: 12-char MD5 hash of `category/filename`
- Use `secure_filename()` from werkzeug to prevent path traversal
- Duplicate filenames handled by appending `_1`, `_2`, etc.
- MIME type checking should allow `application/octet-stream` as fallback

### Background Processing
- Use `threading.Thread(daemon=True)` for background processor
- Use `Queue` from stdlib for thread-safe task queue
- Use `processing_lock` when reading/writing shared `processing_state`
- Lazy-initialize processor with global `_processor` variable
- **Processing time**: One file can take up to 10 minutes to process (Phase 1: PDF to Markdown via Docling, Phase 2: Markdown to JSON via LLM)
