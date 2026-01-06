import argparse
import logging
import time
from pathlib import Path
from datetime import datetime
from pdf_processor import LocalPDFProcessor

# --- CONFIG ---
INPUT_DIR = Path("data/input")
OUTPUT_DIR = Path("data/output")
MARKDOWN_DIR = Path("data/markdown")
LOGS_DIR = Path("logs")

# Ensure directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

# --- LOGGING SETUP ---
def setup_logging():
    """Setup logging to both console and file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = LOGS_DIR / f"pipeline_{timestamp}.log"
    
    # Create formatter
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-7s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # File handler
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    file_handler.setFormatter(formatter)
    
    # Console handler (simpler format)
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(logging.Formatter('%(message)s'))
    
    # Setup logger
    logger = logging.getLogger('pipeline')
    logger.setLevel(logging.INFO)
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    logger.info(f"📝 Logging to: {log_file}")
    return logger

# Initialize logger
log = setup_logging()


def format_time(seconds):
    """Format seconds into human-readable string."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        mins = int(seconds // 60)
        secs = int(seconds % 60)
        return f"{mins}m {secs}s"
    else:
        hours = int(seconds // 3600)
        mins = int((seconds % 3600) // 60)
        return f"{hours}h {mins}m"


def list_categories():
    """Show available PDF categories."""
    if not INPUT_DIR.exists():
        log.error("❌ 'data/input' directory not found.")
        return
    
    log.info("\n📂 Available Categories:")
    found = False
    for item in INPUT_DIR.iterdir():
        if item.is_dir():
            pdfs = list(item.glob("*.pdf"))
            mds = list((MARKDOWN_DIR / item.name).glob("*.md")) if (MARKDOWN_DIR / item.name).exists() else []
            jsons = list((OUTPUT_DIR / item.name).glob("*.json")) if (OUTPUT_DIR / item.name).exists() else []
            log.info(f"   - {item.name}: {len(pdfs)} PDFs | {len(mds)} MDs | {len(jsons)} JSONs")
            found = True
    if not found:
        log.info("   (No folders found in data/input)")


def list_files_in_category(category):
    """List all files in a category with their processing status."""
    cat_dir = INPUT_DIR / category
    if not cat_dir.exists():
        log.error(f"❌ Category '{category}' not found.")
        return
    
    files = sorted(list(cat_dir.glob("*.pdf")))
    if not files:
        log.error(f"❌ No PDF files found in '{category}'")
        return
    
    log.info(f"\n📂 Category: {category}")
    log.info(f"📁 Path: {cat_dir}")
    log.info(f"🔢 Total: {len(files)} PDFs\n")
    
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
        
        log.info(f"  {idx:3d}. {pdf_file.name}")
        log.info(f"       ID: {paper_id} | {status}")


def phase1_convert_to_markdown(processor, category=None, resume=False, start_from=1):
    """
    PHASE 1: Convert all PDFs to Markdown.
    If category is None, process all categories.
    """
    phase_start = time.time()
    
    log.info("\n" + "="*60)
    log.info("📄 PHASE 1: Converting PDFs to Markdown")
    log.info("="*60)
    
    categories = []
    if category:
        cat_dir = INPUT_DIR / category
        if not cat_dir.exists():
            log.error(f"❌ Category '{category}' not found.")
            return
        categories = [cat_dir]
    else:
        categories = [d for d in INPUT_DIR.iterdir() if d.is_dir()]
    
    total_success = 0
    total_files = 0
    timing_data = []
    
    for cat_dir in categories:
        cat_name = cat_dir.name
        files = sorted(list(cat_dir.glob("*.pdf")))
        
        if not files:
            continue
            
        log.info(f"\n🔹 Category: {cat_name} ({len(files)} PDFs)")
        
        md_output_dir = MARKDOWN_DIR / cat_name
        md_output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, pdf_file in enumerate(files, 1):
            paper_id = f"{cat_name}-{idx:03d}"
            expected_md = md_output_dir / f"{paper_id}.md"
            
            # Skip if before start_from
            if idx < start_from:
                log.info(f"   ⏩ [{idx}/{len(files)}] Skipping: {pdf_file.name} (before --start-from)")
                continue
            
            # Skip if resume and MD exists
            if resume and expected_md.exists():
                log.info(f"   ⏩ [{idx}/{len(files)}] Skipping: {pdf_file.name} (MD exists)")
                continue
            
            log.info(f"   📄 [{idx}/{len(files)}] Converting: {pdf_file.name}")
            
            file_start = time.time()
            success = processor.convert_pdf_to_markdown(pdf_file, cat_name, idx)
            file_time = time.time() - file_start
            
            timing_data.append({
                'paper_id': paper_id,
                'phase': 'Phase1_MD',
                'time_seconds': file_time,
                'success': success
            })
            
            if success:
                total_success += 1
                log.info(f"   ✅ Completed in {format_time(file_time)}")
            else:
                log.error(f"   ❌ Failed after {format_time(file_time)}")
            total_files += 1
    
    phase_time = time.time() - phase_start
    log.info(f"\n{'='*60}")
    log.info(f"✅ PHASE 1 Complete: {total_success}/{total_files} converted")
    log.info(f"⏱️  Total time: {format_time(phase_time)}")
    if total_files > 0:
        log.info(f"⏱️  Average: {format_time(phase_time/total_files)} per file")
    log.info(f"{'='*60}")
    
    return timing_data


def phase2_generate_json(processor, category=None, resume=False, start_from=1):
    """
    PHASE 2: Generate JSON from all Markdown files.
    If category is None, process all categories.
    """
    phase_start = time.time()
    
    log.info("\n" + "="*60)
    log.info("🧠 PHASE 2: Generating JSON from Markdown")
    log.info("="*60)
    
    categories = []
    if category:
        md_dir = MARKDOWN_DIR / category
        if not md_dir.exists():
            log.error(f"❌ No markdown found for '{category}'. Run Phase 1 first.")
            return
        categories = [md_dir]
    else:
        categories = [d for d in MARKDOWN_DIR.iterdir() if d.is_dir()]
    
    total_success = 0
    total_files = 0
    timing_data = []
    
    for md_dir in categories:
        cat_name = md_dir.name
        files = sorted(list(md_dir.glob("*.md")))
        
        if not files:
            continue
            
        log.info(f"\n🔹 Category: {cat_name} ({len(files)} Markdown files)")
        
        json_output_dir = OUTPUT_DIR / cat_name
        json_output_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, md_file in enumerate(files, 1):
            paper_id = md_file.stem
            expected_json = json_output_dir / f"{paper_id}.json"
            
            # Skip if before start_from
            if idx < start_from:
                log.info(f"   ⏩ [{idx}/{len(files)}] Skipping: {md_file.name} (before --start-from)")
                continue
            
            # Skip if resume and JSON exists
            if resume and expected_json.exists():
                log.info(f"   ⏩ [{idx}/{len(files)}] Skipping: {md_file.name} (JSON exists)")
                continue
            
            log.info(f"   🧠 [{idx}/{len(files)}] Processing: {md_file.name}")
            
            file_start = time.time()
            success = processor.generate_json_from_markdown(md_file, cat_name)
            file_time = time.time() - file_start
            
            timing_data.append({
                'paper_id': paper_id,
                'phase': 'Phase2_JSON',
                'time_seconds': file_time,
                'success': success
            })
            
            if success:
                total_success += 1
                log.info(f"   ✅ Completed in {format_time(file_time)}")
            else:
                log.error(f"   ❌ Failed after {format_time(file_time)}")
            total_files += 1
    
    phase_time = time.time() - phase_start
    log.info(f"\n{'='*60}")
    log.info(f"✅ PHASE 2 Complete: {total_success}/{total_files} generated")
    log.info(f"⏱️  Total time: {format_time(phase_time)}")
    if total_files > 0:
        log.info(f"⏱️  Average: {format_time(phase_time/total_files)} per file")
    log.info(f"{'='*60}")
    
    return timing_data


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

📝 LOGS:
  All runs are logged to: logs/pipeline_YYYYMMDD_HHMMSS.log
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
    
    total_start = time.time()

    if args.list:
        list_categories()
        return
    
    if args.list_files:
        list_files_in_category(args.list_files)
        return

    # Initialize Processor
    log.info("🚀 Initializing PDF Processor...")
    init_start = time.time()
    processor = LocalPDFProcessor()
    log.info(f"✅ Processor initialized in {format_time(time.time() - init_start)}")

    # Get category (None means all categories)
    def get_category(val):
        return None if val == "__ALL__" else val

    if args.file:
        # Single file processing
        pdf_path = Path(args.file)
        if not pdf_path.exists():
            log.error(f"❌ File not found: {pdf_path}")
            return
        
        # Use parent folder name as category
        category = pdf_path.parent.name if pdf_path.parent.name != "" else "single"
        
        log.info(f"\n📄 Processing single file: {pdf_path.name}")
        log.info(f"   Category: {category}")
        
        if args.json_only:
            # JSON-only mode: skip Phase 1, use existing MD
            log.info("   Mode: JSON-only (skipping Vision phase)")
            md_file = MARKDOWN_DIR / category / f"{category}-001.md"
            if not md_file.exists():
                log.error(f"❌ Markdown not found: {md_file}")
                log.info("   Run without --json-only first to generate Markdown.")
                return
            
            file_start = time.time()
            processor.generate_json_from_markdown(md_file, category)
            log.info(f"⏱️  JSON generation: {format_time(time.time() - file_start)}")
        else:
            # Full pipeline: Phase 1 + Phase 2
            phase1_start = time.time()
            success = processor.convert_pdf_to_markdown(pdf_path, category, 1)
            log.info(f"⏱️  Phase 1 (Vision): {format_time(time.time() - phase1_start)}")
            
            if success:
                md_file = MARKDOWN_DIR / category / f"{category}-001.md"
                phase2_start = time.time()
                processor.generate_json_from_markdown(md_file, category)
                log.info(f"⏱️  Phase 2 (JSON): {format_time(time.time() - phase2_start)}")

    elif args.convert:
        timing1 = phase1_convert_to_markdown(processor, get_category(args.convert), args.resume, args.start_from)
        print_timing_summary(timing1, [])
    
    elif args.generate:
        timing2 = phase2_generate_json(processor, get_category(args.generate), args.resume, args.start_from)
        print_timing_summary([], timing2)
    
    elif args.full:
        cat = get_category(args.full)
        timing1 = phase1_convert_to_markdown(processor, cat, args.resume, args.start_from)
        timing2 = phase2_generate_json(processor, cat, args.resume, args.start_from)
        print_timing_summary(timing1, timing2)
    
    # Final timing
    total_time = time.time() - total_start
    log.info(f"\n🏁 Total execution time: {format_time(total_time)}")


def print_timing_summary(phase1_data, phase2_data):
    """Print a detailed timing summary table."""
    if not phase1_data and not phase2_data:
        return
    
    log.info("\n" + "="*70)
    log.info("📊 TIMING SUMMARY")
    log.info("="*70)
    
    # Phase 1 summary
    if phase1_data:
        log.info("\n📄 PHASE 1: PDF → Markdown")
        log.info("-" * 50)
        log.info(f"{'Paper ID':<15} {'Time':>12} {'Status':>10}")
        log.info("-" * 50)
        
        total_time = 0
        for item in phase1_data:
            status = "✅" if item['success'] else "❌"
            log.info(f"{item['paper_id']:<15} {format_time(item['time_seconds']):>12} {status:>10}")
            total_time += item['time_seconds']
        
        log.info("-" * 50)
        log.info(f"{'TOTAL':<15} {format_time(total_time):>12} {len(phase1_data):>7} files")
        if phase1_data:
            log.info(f"{'AVERAGE':<15} {format_time(total_time/len(phase1_data)):>12}")
    
    # Phase 2 summary
    if phase2_data:
        log.info("\n🧠 PHASE 2: Markdown → JSON")
        log.info("-" * 50)
        log.info(f"{'Paper ID':<15} {'Time':>12} {'Status':>10}")
        log.info("-" * 50)
        
        total_time = 0
        for item in phase2_data:
            status = "✅" if item['success'] else "❌"
            log.info(f"{item['paper_id']:<15} {format_time(item['time_seconds']):>12} {status:>10}")
            total_time += item['time_seconds']
        
        log.info("-" * 50)
        log.info(f"{'TOTAL':<15} {format_time(total_time):>12} {len(phase2_data):>7} files")
        if phase2_data:
            log.info(f"{'AVERAGE':<15} {format_time(total_time/len(phase2_data)):>12}")
    
    # Combined summary if both phases ran
    if phase1_data and phase2_data:
        log.info("\n📈 COMBINED TOTALS")
        log.info("-" * 50)
        p1_total = sum(item['time_seconds'] for item in phase1_data)
        p2_total = sum(item['time_seconds'] for item in phase2_data)
        log.info(f"{'Phase 1 (Vision)':<25} {format_time(p1_total):>12}")
        log.info(f"{'Phase 2 (JSON)':<25} {format_time(p2_total):>12}")
        log.info(f"{'GRAND TOTAL':<25} {format_time(p1_total + p2_total):>12}")
    
    log.info("="*70)


if __name__ == "__main__":
    main()
