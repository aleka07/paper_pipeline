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


def phase1_convert_to_markdown(processor, category=None, resume=False):
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


def phase2_generate_json(processor, category=None, resume=False):
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
Examples:
  python main.py --list                 # Show categories
  python main.py --convert              # Phase 1: All PDFs → MD
  python main.py --convert Req_2        # Phase 1: Only 'Req_2' category
  python main.py --generate             # Phase 2: All MD → JSON  
  python main.py --generate Req_2       # Phase 2: Only 'Req_2' category
  python main.py --full                 # Both phases for all
  python main.py --full Req_2 --resume  # Both phases, skip existing
        """
    )
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available categories")
    group.add_argument("--convert", nargs="?", const="__ALL__", metavar="CATEGORY", help="Phase 1: Convert PDFs to Markdown")
    group.add_argument("--generate", nargs="?", const="__ALL__", metavar="CATEGORY", help="Phase 2: Generate JSON from Markdown")
    group.add_argument("--full", nargs="?", const="__ALL__", metavar="CATEGORY", help="Run both phases (PDF → MD → JSON)")
    
    parser.add_argument("--resume", action="store_true", help="Skip files that already have output")

    args = parser.parse_args()

    if args.list:
        list_categories()
        return

    # Initialize Processor
    processor = LocalPDFProcessor()

    # Get category (None means all categories)
    def get_category(val):
        return None if val == "__ALL__" else val

    if args.convert:
        phase1_convert_to_markdown(processor, get_category(args.convert), args.resume)
    
    elif args.generate:
        phase2_generate_json(processor, get_category(args.generate), args.resume)
    
    elif args.full:
        cat = get_category(args.full)
        phase1_convert_to_markdown(processor, cat, args.resume)
        phase2_generate_json(processor, cat, args.resume)


if __name__ == "__main__":
    main()
