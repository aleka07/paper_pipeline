import argparse
import sys
import time
from pathlib import Path
from pdf_processor import LocalPDFProcessor

# --- CONFIG ---
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
# Ensure these exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
Path("logs").mkdir(exist_ok=True)

def list_categories():
    if not INPUT_DIR.exists():
        print("❌ 'data/input' directory not found.")
        return
    
    print("\n📂 Available Categories:")
    found = False
    for item in INPUT_DIR.iterdir():
        if item.is_dir():
            files = list(item.glob("*.pdf"))
            if files:
                print(f"   - {item.name} ({len(files)} PDFs)")
                found = True
    if not found:
        print("   (No folders with PDFs found in data/input)")

def process_category(processor, category, resume=False, start_from=1):
    cat_dir = INPUT_DIR / category
    if not cat_dir.exists():
        print(f"❌ Category folder '{category}' not found.")
        return

    files = sorted(list(cat_dir.glob("*.pdf")))
    print(f"\n🚀 Processing Category: {category} ({len(files)} files)")
    
    success_count = 0
    
    for idx, pdf_file in enumerate(files, 1):
        if idx < start_from:
            continue
            
        # Check if already processed (Smart Resume)
        expected_json = OUTPUT_DIR / category / f"{category}-{idx:03d}.json"
        if resume and expected_json.exists():
            print(f"   ⏩ Skipping {idx}: {pdf_file.name} (Already exists)")
            continue

        print(f"\n[{idx}/{len(files)}] Processing ID: {category}-{idx:03d}")
        result = processor.process_pdf(pdf_file, category, idx)
        
        if result:
            success_count += 1
        
        # Local model cool-down (optional, keeps GPU from overheating if consumer card)
        # time.sleep(1) 

    print(f"\n✅ Completed {category}: {success_count}/{len(files)} processed.")

def main():
    parser = argparse.ArgumentParser(description="Local PDF to JSON Pipeline (vLLM)")
    
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--list", action="store_true", help="List available categories")
    group.add_argument("--category", type=str, help="Process a specific category")
    group.add_argument("--all", action="store_true", help="Process ALL categories")
    group.add_argument("--file", type=str, help="Process a single PDF file")
    
    parser.add_argument("--resume", action="store_true", help="Skip files that already have JSON output")
    parser.add_argument("--start-from", type=int, default=1, help="Start sequence ID from this number")

    args = parser.parse_args()

    # Initialize Processor
    processor = LocalPDFProcessor()

    if args.list:
        list_categories()
    
    elif args.file:
        fpath = Path(args.file)
        if not fpath.exists():
            print("❌ File not found.")
            return
        # Try to deduce category from folder name
        cat = fpath.parent.name
        print(f"Processing single file (Category: {cat})")
        processor.process_pdf(fpath, cat, args.start_from)

    elif args.category:
        process_category(processor, args.category, args.resume, args.start_from)

    elif args.all:
        for item in INPUT_DIR.iterdir():
            if item.is_dir():
                process_category(processor, item.name, args.resume)

if __name__ == "__main__":
    main()