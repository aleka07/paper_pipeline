import argparse
from pathlib import Path
from pdf_processor import LocalPDFProcessor

# --- CONFIG ---
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
MARKDOWN_DIR = Path("data/markdown")

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)


def list_categories():
    """Show available PDF categories."""
    if not INPUT_DIR.exists():
        print("❌ 'data/input' directory not found.")
        return
    
    print("\n📂 Available Categories:")
    found = False
    for item in INPUT_DIR.iterdir():
        if item.is_dir():
            pdfs = list(item.glob("*.pdf"))
            mds = list((MARKDOWN_DIR / item.name).glob("*.md")) if (MARKDOWN_DIR / item.name).exists() else []
            jsons = list((OUTPUT_DIR / item.name).glob("*.json")) if (OUTPUT_DIR / item.name).exists() else []
            print(f"   - {item.name}: {len(pdfs)} PDFs | {len(mds)} MDs | {len(jsons)} JSONs")
            found = True
    if not found:
        print("   (No folders found in data/input)")


def list_files_in_category(category):
    """List all files in a category with their processing status."""
    cat_dir = INPUT_DIR / category
    if not cat_dir.exists():
        print(f"❌ Category '{category}' not found.")
        return
    
    files = sorted(list(cat_dir.glob("*.pdf")))
    if not files:
        print(f"❌ No PDF files found in '{category}'")
        return
    
    print(f"\n📂 Category: {category}")
    print(f"📁 Path: {cat_dir}")
    print(f"🔢 Total: {len(files)} PDFs\n")
    
    for idx, pdf_file in enumerate(files, 1):
        paper_id = f"{category}-{idx:03d}"
        md_exists = (MARKDOWN_DIR / category / f"{paper_id}.md").exists()
        json_exists = (OUTPUT_DIR / category / f"{paper_id}.json").exists()
        
        # Status indicators
        if json_exists:
            status = "✅ Complete"
        elif md_exists:
            status = "🔶 MD only (needs JSON)"
        else:
            status = "⏳ Pending"
        
        print(f"  {idx:3d}. {pdf_file.name}")
        print(f"       ID: {paper_id} | {status}")


def phase1_convert_to_markdown(processor, category=None, resume=False, start_from=1):
    """
    PHASE 1: Convert all PDFs to Markdown.
    If category is None, process all categories.
    """
    print("\n" + "="*60)
    print("📄 PHASE 1: Converting PDFs to Markdown")
    print("="*60)
    
    categories = []
    if category:
        cat_dir = INPUT_DIR / category
        if not cat_dir.exists():
            print(f"❌ Category '{category}' not found.")
            return
        categories = [cat_dir]
    else:
        categories = [d for d in INPUT_DIR.iterdir() if d.is_dir()]
    
    total_success = 0
    total_files = 0
    
    for cat_dir in categories:
        cat_name = cat_dir.name
        files = sorted(list(cat_dir.glob("*.pdf")))
        
        if not files:
            continue
            
        print(f"\n🔹 Category: {cat_name} ({len(files)} PDFs)")
        
        md_output_dir = MARKDOWN_DIR / cat_name
        md_output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, pdf_file in enumerate(files, 1):
            paper_id = f"{cat_name}-{idx:03d}"
            expected_md = md_output_dir / f"{paper_id}.md"
            
            # Skip if before start_from
            if idx < start_from:
                print(f"   ⏩ [{idx}/{len(files)}] Skipping: {pdf_file.name} (before --start-from)")
                continue
            
            # Skip if resume and MD exists
            if resume and expected_md.exists():
                print(f"   ⏩ [{idx}/{len(files)}] Skipping: {pdf_file.name} (MD exists)")
                continue
            
            print(f"   📄 [{idx}/{len(files)}] Converting: {pdf_file.name}")
            success = processor.convert_pdf_to_markdown(pdf_file, cat_name, idx)
            
            if success:
                total_success += 1
            total_files += 1
    
    print(f"\n✅ PHASE 1 Complete: {total_success}/{total_files} converted to Markdown")


def phase2_generate_json(processor, category=None, resume=False, start_from=1):
    """
    PHASE 2: Generate JSON from all Markdown files.
    If category is None, process all categories.
    """
    print("\n" + "="*60)
    print("🧠 PHASE 2: Generating JSON from Markdown")
    print("="*60)
    
    categories = []
    if category:
        md_dir = MARKDOWN_DIR / category
        if not md_dir.exists():
            print(f"❌ No markdown found for '{category}'. Run Phase 1 first.")
            return
        categories = [md_dir]
    else:
        categories = [d for d in MARKDOWN_DIR.iterdir() if d.is_dir()]
    
    total_success = 0
    total_files = 0
    
    for md_dir in categories:
        cat_name = md_dir.name
        files = sorted(list(md_dir.glob("*.md")))
        
        if not files:
            continue
            
        print(f"\n🔹 Category: {cat_name} ({len(files)} Markdown files)")
        
        json_output_dir = OUTPUT_DIR / cat_name
        json_output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, md_file in enumerate(files, 1):
            paper_id = md_file.stem
            expected_json = json_output_dir / f"{paper_id}.json"
            
            # Skip if before start_from
            if idx < start_from:
                print(f"   ⏩ [{idx}/{len(files)}] Skipping: {md_file.name} (before --start-from)")
                continue
            
            # Skip if resume and JSON exists
            if resume and expected_json.exists():
                print(f"   ⏩ [{idx}/{len(files)}] Skipping: {md_file.name} (JSON exists)")
                continue
            
            print(f"   🧠 [{idx}/{len(files)}] Processing: {md_file.name}")
            success = processor.generate_json_from_markdown(md_file, cat_name)
            
            if success:
                total_success += 1
            total_files += 1
    
    print(f"\n✅ PHASE 2 Complete: {total_success}/{total_files} JSON generated")


def main():
    parser = argparse.ArgumentParser(
        description="Two-Phase PDF Pipeline: PDF → Markdown → JSON",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
═══════════════════════════════════════════════════════════════════
                           EXAMPLES
═══════════════════════════════════════════════════════════════════

📋 LIST & STATUS:
  python main.py --list                    # Show all categories with counts
  python main.py --list-files Req_2        # List files in Req_2 with status

📄 PHASE 1 (PDF → Markdown):
  python main.py --convert                 # Convert ALL PDFs to Markdown
  python main.py --convert Req_2           # Convert only 'Req_2' category
  python main.py --convert Req_2 --resume  # Skip PDFs that already have .md

🧠 PHASE 2 (Markdown → JSON):
  python main.py --generate                # Generate JSON for ALL Markdown
  python main.py --generate Req_2          # Generate JSON only for 'Req_2'
  python main.py --generate --resume       # Skip if .json already exists

🔄 FULL PIPELINE (Both Phases):
  python main.py --full                    # Process ALL: PDF → MD → JSON
  python main.py --full Req_2              # Full pipeline for 'Req_2' only
  python main.py --full Req_2 --resume     # Skip already processed files

📄 SINGLE FILE:
  python main.py --file path/to/paper.pdf           # Full pipeline for one PDF
  python main.py --file path/to/paper.pdf --json-only  # Only regenerate JSON

🔢 START FROM SPECIFIC FILE:
  python main.py --convert Req_2 --start-from 5     # Start Phase 1 from file #5
  python main.py --generate Req_2 --start-from 10   # Start Phase 2 from file #10
  python main.py --full Req_2 --start-from 15       # Start both from #15

💡 COMMON WORKFLOWS:
  # First run (process everything)
  python main.py --full Req_2
  
  # Resume after interruption
  python main.py --full Req_2 --resume
  
  # Re-generate JSON with new prompt (keep existing markdown)
  python main.py --generate Req_2
  
  # Fix single file's JSON only
  python main.py --file data/input/Req_2/paper.pdf --json-only
═══════════════════════════════════════════════════════════════════
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", 
                       help="List available categories with file counts")
    group.add_argument("--list-files", type=str, metavar="CATEGORY", 
                       help="List all files in a category with processing status")
    group.add_argument("--convert", nargs="?", const="__ALL__", metavar="CATEGORY", 
                       help="Phase 1: Convert PDFs to Markdown (all or specific category)")
    group.add_argument("--generate", nargs="?", const="__ALL__", metavar="CATEGORY", 
                       help="Phase 2: Generate JSON from Markdown (all or specific category)")
    group.add_argument("--full", nargs="?", const="__ALL__", metavar="CATEGORY", 
                       help="Run both phases: PDF → MD → JSON")
    group.add_argument("--file", type=str, metavar="PDF_PATH", 
                       help="Process a single PDF file (both phases)")
    
    parser.add_argument("--resume", action="store_true", 
                        help="Skip files that already have output")
    parser.add_argument("--start-from", type=int, default=1, metavar="N",
                        help="Start processing from sequence number N (skip 1 to N-1)")
    parser.add_argument("--json-only", action="store_true",
                        help="For --file: skip Phase 1, only regenerate JSON from existing MD")

    args = parser.parse_args()

    if args.list:
        list_categories()
        return
    
    if args.list_files:
        list_files_in_category(args.list_files)
        return

    # Initialize Processor
    processor = LocalPDFProcessor()

    # Get category (None means all categories)
    def get_category(val):
        return None if val == "__ALL__" else val

    if args.file:
        # Single file processing
        pdf_path = Path(args.file)
        if not pdf_path.exists():
            print(f"❌ File not found: {pdf_path}")
            return
        
        # Use parent folder name as category
        category = pdf_path.parent.name if pdf_path.parent.name != "" else "single"
        
        print(f"\n📄 Processing single file: {pdf_path.name}")
        print(f"   Category: {category}")
        
        if args.json_only:
            # JSON-only mode: skip Phase 1, use existing MD
            print("   Mode: JSON-only (skipping Vision phase)")
            md_file = MARKDOWN_DIR / category / f"{category}-001.md"
            if not md_file.exists():
                print(f"❌ Markdown not found: {md_file}")
                print("   Run without --json-only first to generate Markdown.")
                return
            processor.generate_json_from_markdown(md_file, category)
        else:
            # Full pipeline: Phase 1 + Phase 2
            success = processor.convert_pdf_to_markdown(pdf_path, category, 1)
            if success:
                md_file = MARKDOWN_DIR / category / f"{category}-001.md"
                processor.generate_json_from_markdown(md_file, category)

    elif args.convert:
        phase1_convert_to_markdown(processor, get_category(args.convert), args.resume, args.start_from)
    
    elif args.generate:
        phase2_generate_json(processor, get_category(args.generate), args.resume, args.start_from)
    
    elif args.full:
        cat = get_category(args.full)
        phase1_convert_to_markdown(processor, cat, args.resume, args.start_from)
        phase2_generate_json(processor, cat, args.resume, args.start_from)


if __name__ == "__main__":
    main()
