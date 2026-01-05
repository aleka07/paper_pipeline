import logging
import time
from pathlib import Path

from docling.document_converter import DocumentConverter, PdfFormatOption
from docling.datamodel.base_models import InputFormat
from docling.datamodel.pipeline_options import (
    PdfPipelineOptions,
    TableFormerMode,
    AcceleratorOptions,
    AcceleratorDevice,
    PictureDescriptionVlmOptions  # Use the standard class
)
# Necessary imports for custom models
from docling.datamodel.pipeline_options_vlm_model import (
    InferenceFramework,
    TransformersModelType
)

# 1. Configure Logging
logging.basicConfig(level=logging.INFO)

# 2. Define Pipeline Options
pipeline_options = PdfPipelineOptions()
pipeline_options.do_ocr = True
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE
pipeline_options.do_formula_enrichment = True
pipeline_options.do_code_enrichment = True

# --- CONFIGURE QWEN3-VL-8B ---
pipeline_options.do_picture_description = True

# We manually configure the VLM options to point to the Qwen repo
pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="Qwen/Qwen3-VL-8B-Instruct",  # The specific model ID
    prompt=(
        "Describe this image in detail. "
        "If it is a chart, extract the data trends and axis labels. "
        "If it is a diagram, explain the flow and connections."
    ),
    # Critical settings for custom HF models:
    inference_framework=InferenceFramework.TRANSFORMERS,
    transformers_model_type=TransformersModelType.AUTOMODEL_IMAGETEXTTOTEXT,
    # Qwen benefits from a slightly lower temperature for factual descriptions
    temperature=0.1, 
    # Qwen can handle higher resolutions; scale=2.0 is usually a good balance
    scale=2.0 
)

# --- HARDWARE ACCELERATION ---
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=8,
    device=AcceleratorDevice.CUDA
)

# 3. Initialize Converter
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

def process_paper(pdf_path: str):
    start_time = time.time()
    print(f"🚀 Processing: {pdf_path} using Qwen3-VL-8B...")
    
    result = doc_converter.convert(pdf_path)
    
    # Custom placeholder makes it easy to find Qwen's output in the markdown
    md_output = result.document.export_to_markdown(image_placeholder="\n\n> **[Qwen Description]**\n")
    
    output_filename = Path(pdf_path).stem + "_qwen.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(md_output)
    
    print(f"✅ Done in {time.time() - start_time:.2f}s.")
    print(f"📄 Saved to: {output_filename}")

if __name__ == "__main__":
    process_paper("test.pdf")