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

- Backend uses Flask with a REST API
- Frontend is vanilla HTML/CSS/JS
- PDF processing uses Docling for vision and vLLM/Ollama for logic
