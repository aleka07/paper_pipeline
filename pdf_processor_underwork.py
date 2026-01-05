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

class LocalPDFProcessor:
    def __init__(self, base_url="http://localhost:8000/v1", model_name="openai/gpt-oss-20b"):
        self.client = OpenAI(base_url=base_url, api_key="EMPTY")
        self.model_name = model_name
        self.system_prompt = self._load_prompt()
        
        # Initialize Docling (Heavy operation, done once on startup)
        print("   ⚙️  Initializing Docling Vision Pipeline (Granite 2B)...")
        self.converter = self._setup_docling()

    def _load_prompt(self):
        try:
            with open("prompt.md", "r", encoding="utf-8") as f:
                return f.read()
        except FileNotFoundError:
            return "You are a JSON extractor."

    def _setup_docling(self):
        """Configures the Granite Vision based document converter."""
        pipeline_options = PdfPipelineOptions()
        pipeline_options.do_ocr = True
        pipeline_options.do_table_structure = True
        pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
        pipeline_options.do_formula_enrichment = True
        pipeline_options.do_code_enrichment = True
        
        # --- CONFIGURE GRANITE VISION (2B) ---
        pipeline_options.do_picture_description = True
        pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
            repo_id="ibm-granite/granite-vision-3.1-2b-preview",
            # Hardened prompt to prevent hallucinations
            prompt=(
                "Describe this image for a scientific paper analysis. "
                "If it is a chart, read the labels and trends. "
                "If it is a diagram, explain the components. "
                "Do not invent text that is not visible."
            ),
            scale=2.0
        )

        # Hardware Acceleration
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
        """Converts PDF to rich Markdown using Granite Vision."""
        print(f"   👁️  Visual Analysis: {Path(pdf_path).name}...")
        try:
            start_t = time.time()
            result = self.converter.convert(pdf_path)
            
            # Export to Markdown with placeholders for images
            # This marker helps the Logic Model find the visual descriptions
            md_content = result.document.export_to_markdown(image_placeholder="\n\n> **[Visual Content Description]**\n")
            
            elapsed = time.time() - start_t
            print(f"   ✅ Visual Analysis complete ({elapsed:.1f}s)")
            return md_content
        except Exception as e:
            print(f"   ❌ Docling/Granite Error: {e}")
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
        
        # 1. Use Docling (Granite) to get Markdown
        markdown_text = self.extract_markdown(str(path_obj))
        
        if not markdown_text:
            return False

        # Save the intermediate Markdown for debugging/verification
        debug_dir = Path("data/debug_markdown") / category_code
        debug_dir.mkdir(parents=True, exist_ok=True)
        with open(debug_dir / f"{paper_id}.md", "w", encoding="utf-8") as f:
            f.write(markdown_text)

        # 2. Inject into Prompt for the Logic Model
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