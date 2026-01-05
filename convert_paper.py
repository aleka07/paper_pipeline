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
    PictureDescriptionVlmOptions  # Import the generic VLM options class
)

# 1. Configure Logging
logging.basicConfig(level=logging.INFO)

# 2. Define Advanced Pipeline Options
pipeline_options = PdfPipelineOptions()

# --- OPTICAL CHARACTER RECOGNITION (OCR) ---
pipeline_options.do_ocr = True

# --- TABLE STRUCTURE ---
# Essential for scientific papers
pipeline_options.do_table_structure = True
pipeline_options.table_structure_options.mode = TableFormerMode.ACCURATE

# --- SCIENTIFIC ENRICHMENT ---
pipeline_options.do_formula_enrichment = True
pipeline_options.do_code_enrichment = True

# --- HIGH QUALITY VLM (Granite Vision) ---
pipeline_options.do_picture_description = True

# We use the generic VlmOptions class to specify the EXACT model we want.
# "ibm-granite/granite-vision-3.1-2b-preview" is the 2B parameter model.
# It is much smarter than SmolVLM but still fast on a DGX.
pipeline_options.picture_description_options = PictureDescriptionVlmOptions(
    repo_id="ibm-granite/granite-vision-3.1-2b-preview",
    prompt=(
        "Describe this scientific figure in detail. "
        "If it is a chart, read the axis labels, legend, and data trends. "
        "If it is a diagram, explain the components and their relationships. "
        "Do not hallucinate content not present in the image."
    )
)

# --- HARDWARE ACCELERATION ---
# Forced to CUDA since we know it works now.
pipeline_options.accelerator_options = AcceleratorOptions(
    num_threads=8,
    device=AcceleratorDevice.CUDA
)

# 3. Initialize the Converter
doc_converter = DocumentConverter(
    format_options={
        InputFormat.PDF: PdfFormatOption(pipeline_options=pipeline_options)
    }
)

def process_paper(pdf_path: str):
    start_time = time.time()
    print(f"🚀 Processing: {pdf_path} using Granite Vision...")
    
    # Run conversion
    result = doc_converter.convert(pdf_path)
    
    # Export to Markdown
    # We use a distinct placeholder so you can grep for it easily
    md_output = result.document.export_to_markdown(image_placeholder="\n\n### [FIGURE DESCRIPTION]\n")
    
    output_filename = Path(pdf_path).stem + "_granite.md"
    with open(output_filename, "w", encoding="utf-8") as f:
        f.write(md_output)
    
    print(f"✅ Done in {time.time() - start_time:.2f}s.")
    print(f"📄 Saved to: {output_filename}")

# 4. Run it
if __name__ == "__main__":
    process_paper("test.pdf")