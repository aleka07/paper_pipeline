import json
import re
import os
import time
from pathlib import Path
from openai import OpenAI

# --- DOCLING IMPORTS ---
from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    AcceleratorOptions,
    AcceleratorDevice,
    PictureDescriptionVlmOptions,
    EasyOcrOptions  # GPU-accelerated OCR for better math/symbol recognition
)
from docling.datamodel.pipeline_options_vlm_model import (
    InferenceFramework,
    TransformersModelType
)

# --- CONFIG ---
MARKDOWN_DIR = Path("data/markdown")

# Backend configurations
BACKENDS = {
    "vllm": {
        "base_url": "http://localhost:8000/v1",
        "api_key": "EMPTY",
        "model": "nvidia/Qwen3-32B-FP4",
        "extra_body": {}
    },
    "ollama": {
        "base_url": "http://localhost:11434/v1",
        "api_key": "ollama",
        "model": "nemotron-large-ctx",
        "extra_body": {"num_ctx": 131072}
    }
}

class LocalPDFProcessor:
    def __init__(self, backend="vllm"):
        """
        Initialize processor with specified backend.
        
        Args:
            backend: "vllm" (default) or "ollama"
        """
        if backend not in BACKENDS:
            raise ValueError(f"Unknown backend '{backend}'. Choose from: {list(BACKENDS.keys())}")
        
        self.backend = backend
        config = BACKENDS[backend]
        
        self.client = OpenAI(base_url=config["base_url"], api_key=config["api_key"])
        self.model_name = config["model"]
        self.extra_body = config["extra_body"]
        self.system_prompt = self._load_prompt()
        
        print(f"   🔌 Using backend: {backend} ({self.model_name})")
        
        # Initialize Docling (Heavy operation, done once on startup)
        print("   ⚙️  Initializing Docling Vision Pipeline (Qwen-VL)...")
        self.converter = self._setup_docling()

    def _load_prompt(self):
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a JSON extractor."

    def _setup_docling(self):
        """Configures the Qwen-VL based document converter."""
        pipeline_options = PdfPipelineOptions()
        # OCR disabled - Scopus papers (2020+) have embedded digital text
        # Enable only if processing scanned documents
        pipeline_options.do_ocr = True
        
        # Use EasyOCR (GPU-accelerated, PyTorch-based) instead of RapidOCR
        # RapidOCR had ONNX hardware issues on this system
        pipeline_options.ocr_options = EasyOcrOptions(
            use_gpu=True,
            lang=["en"]  # English - add more languages if needed
        )
        
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True
        
        # Enable Qwen Vision for images/charts
        pipeline_options.do_picture_description = True
        
        # JSON structured output - forces complete response
        vlm_prompt = """Analyze this scientific figure and output valid JSON:

{
  "type": "chart|diagram|table|photo|other",
  "description": "what the figure shows",
  "data": ["list", "of", "all", "labels", "and", "values"],
  "insight": "what the data means or shows"
}

Output only the JSON, nothing else."""

        pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
            repo_id="Qwen/Qwen3-VL-8B-Instruct", 
            prompt=vlm_prompt,
            inference_framework=InferenceFramework.TRANSFORMERS,
            transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
            scale=3.0,
            min_coverage_area_pct=0.01,   # Process even small images (1% of page)
            batch_size=1,                  # Process one image at a time for stability
            # generation_config is the correct way to set token limits
            generation_config={
                "max_new_tokens": 2048,    # Max output length (was defaulting to 256!)
                "temperature": 0.2,
                "do_sample": True
            }
        )

        # Use the remaining GPU power (Docker used 50%, we use the rest)
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
        """Converts PDF to rich Markdown using Qwen-VL."""
        print(f"   👁️  Visual Analysis: {Path(pdf_path).name} (this takes time)...")
        try:
            start_t = time.time()
            result = self.converter.convert(pdf_path)
            
            # Export to Markdown
            # VLM descriptions are added as annotations automatically
            # image_placeholder is just for the image reference (we use empty to keep clean)
            md_content = result.document.export_to_markdown(
                image_placeholder=""  # VLM descriptions appear separately as text
            )
            
            elapsed = time.time() - start_t
            print(f"   ✅ Visual Analysis complete ({elapsed:.1f}s)")
            return md_content
        except Exception as e:
            print(f"   ❌ Docling Error: {e}")
            return None

    def clean_json_response(self, response_text):
        """Cleans <think> tags and markdown to extract raw JSON."""
        clean = re.sub(r'<think>.*?</think>', '', response_text, flags=re.DOTALL)
        json_match = re.search(r'```json\s*(.*?)\s*```', clean, re.DOTALL)
        if json_match:
            clean = json_match.group(1)
        return clean.strip()

    def convert_pdf_to_markdown(self, pdf_path, category_code, sequence_id):
        """
        Phase 1: Convert a single PDF to Markdown and save it.
        Returns True on success, False on failure.
        """
        path_obj = Path(pdf_path)
        paper_id = f"{category_code}-{sequence_id:03d}"
        
        # Extract markdown from PDF
        markdown_text = self.extract_markdown(str(path_obj))
        
        if not markdown_text:
            return False

        # Save the Markdown file
        md_output_dir = MARKDOWN_DIR / category_code
        md_output_dir.mkdir(parents=True, exist_ok=True)
        md_file = md_output_dir / f"{paper_id}.md"
        
        with open(md_file, "w", encoding="utf-8") as f:
            f.write(markdown_text)
        
        print(f"   ✅ Saved: {md_file}")
        return True

    def generate_json_from_markdown(self, md_path, category_code):
        """
        Phase 2: Read a Markdown file and generate JSON using LLM.
        Returns True on success, False on failure.
        """
        md_path = Path(md_path)
        paper_id = md_path.stem  # e.g., "category-001"
        
        # Read the markdown content
        try:
            with open(md_path, "r", encoding="utf-8") as f:
                markdown_text = f.read()
        except Exception as e:
            print(f"   ❌ Failed to read markdown: {e}")
            return False

        # Inject into Prompt
        user_message = f"PAPER ID: {paper_id}\nCATEGORY: {category_code}\n\nANALYZED DOCUMENT CONTENT (MARKDOWN):\n{markdown_text}"

        print(f"   🧠 Generating JSON with {self.model_name}...")
        try:
            # Build request kwargs
            request_kwargs = {
                "model": self.model_name,
                "messages": [
                    {"role": "system", "content": self.system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.3,
                "max_tokens": 8192
            }
            
            # Add backend-specific options (e.g., Ollama's num_ctx)
            if self.extra_body:
                request_kwargs["extra_body"] = self.extra_body
            
            completion = self.client.chat.completions.create(**request_kwargs)
            
            raw_output = completion.choices[0].message.content
            json_str = self.clean_json_response(raw_output)
            
            # Parse and Validate
            data = json.loads(json_str)
            data['paper_id'] = paper_id
            
            # Save JSON
            output_dir = Path("data/output") / category_code
            output_dir.mkdir(parents=True, exist_ok=True)
            output_file = output_dir / f"{paper_id}.json"
            
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
                
            print(f"   ✅ Saved: {output_file}")
            return True

        except Exception as e:
            print(f"   ❌ Inference Failed: {e}")
            return False

    def process_pdf(self, pdf_path, category_code, sequence_id):
        """
        Legacy method: Full pipeline (PDF → MD → JSON) for a single file.
        Kept for backwards compatibility.
        """
        # Phase 1: Convert to MD
        if not self.convert_pdf_to_markdown(pdf_path, category_code, sequence_id):
            return False
        
        # Phase 2: Generate JSON from MD
        paper_id = f"{category_code}-{sequence_id:03d}"
        md_file = MARKDOWN_DIR / category_code / f"{paper_id}.md"
        return self.generate_json_from_markdown(md_file, category_code)