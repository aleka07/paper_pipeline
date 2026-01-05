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
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True
        
        # Enable Qwen Vision for images/charts
        pipeline_options.do_picture_description = True
        pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
            # NOTE: Verify this ID exists on HF. Standard is often "Qwen/Qwen2.5-VL-7B-Instruct"
            repo_id="Qwen/Qwen2.5-VL-7B-Instruct", 
            prompt="Describe this image in detail. Extract data trends from charts and connection flows from diagrams.",
            inference_framework=InferenceFramework.TRANSFORMERS,
            transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
            temperature=0.1,
            scale=2.0
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
            
            # Export to Markdown with placeholders for images
            md_content = result.document.export_to_markdown(image_placeholder="\n\n> **[Visual Content Description]**\n")
            
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

    def process_pdf(self, pdf_path, category_code, sequence_id):
        path_obj = Path(pdf_path)
        paper_id = f"{category_code}-{sequence_id:03d}"
        
        # 1. Use Docling to get Markdown instead of simple Text
        markdown_text = self.extract_markdown(str(path_obj))
        
        if not markdown_text:
            return False

        # Save the intermediate Markdown for debugging/verification
        debug_dir = Path("data/debug_markdown") / category_code
        debug_dir.mkdir(parents=True, exist_ok=True)
        with open(debug_dir / f"{paper_id}.md", "w", encoding="utf-8") as f:
            f.write(markdown_text)

        # 2. Inject into Prompt
        user_message = f"PAPER ID: {paper_id}\nCATEGORY: {category_code}\n\nANALYZED DOCUMENT CONTENT (MARKDOWN):\n{markdown_text}"

        print(f"   🧠 Generating JSON with {self.model_name}...")
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