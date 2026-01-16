#!/usr/bin/env python3
"""
Rename existing numbered output files (Req_2-001.md, Req_2-001.json, etc.)
to match the original PDF filenames for proper status detection.
"""

from pathlib import Path
import shutil

# Directories
DATA_DIR = Path("data")
INPUT_DIR = DATA_DIR / "input"
MARKDOWN_DIR = DATA_DIR / "markdown"
OUTPUT_DIR = DATA_DIR / "output"


def get_pdf_files_ordered(category: str) -> list[Path]:
    """Get PDF files in a category, sorted by modification time (oldest first)."""
    category_path = INPUT_DIR / category
    if not category_path.exists():
        return []
    
    pdf_files = list(category_path.glob("*.pdf"))
    # Sort by modification time (oldest first) - this is likely the original upload order
    return sorted(pdf_files, key=lambda f: f.stat().st_mtime)


def rename_outputs_for_category(category: str, dry_run: bool = True) -> dict:
    """Rename numbered outputs to match PDF filenames."""
    md_dir = MARKDOWN_DIR / category
    json_dir = OUTPUT_DIR / category
    
    results = {
        "category": category,
        "renamed_md": [],
        "renamed_json": [],
        "skipped": [],
        "errors": []
    }
    
    # Get PDF files
    pdf_files = get_pdf_files_ordered(category)
    
    if not pdf_files:
        results["errors"].append(f"No PDF files found in {INPUT_DIR / category}")
        return results
    
    # Get numbered markdown files
    numbered_md = sorted([
        f for f in md_dir.glob("*.md") 
        if f.stem.startswith(f"{category}-") and f.stem.split("-")[-1].isdigit()
    ]) if md_dir.exists() else []
    
    # Get numbered JSON files
    numbered_json = sorted([
        f for f in json_dir.glob("*.json") 
        if f.stem.startswith(f"{category}-") and f.stem.split("-")[-1].isdigit()
    ]) if json_dir.exists() else []
    
    print(f"\n📁 Category: {category}")
    print(f"   PDFs: {len(pdf_files)}")
    print(f"   Numbered MD files: {len(numbered_md)}")
    print(f"   Numbered JSON files: {len(numbered_json)}")
    
    # Try to match by order (numbered files correspond to PDFs in order)
    for i, pdf in enumerate(pdf_files):
        base_name = pdf.stem
        seq_num = f"{i+1:03d}"  # 001, 002, 003...
        numbered_name = f"{category}-{seq_num}"
        
        # Check if already has correctly named output
        correct_md = md_dir / f"{base_name}.md"
        correct_json = json_dir / f"{base_name}.json"
        
        if correct_md.exists() and correct_json.exists():
            results["skipped"].append(f"{base_name} (already has outputs)")
            continue
        
        # Look for numbered version
        numbered_md_file = md_dir / f"{numbered_name}.md"
        numbered_json_file = json_dir / f"{numbered_name}.json"
        
        # Rename MD
        if numbered_md_file.exists() and not correct_md.exists():
            if dry_run:
                print(f"   [DRY] Would rename: {numbered_md_file.name} → {base_name}.md")
            else:
                shutil.move(str(numbered_md_file), str(correct_md))
                print(f"   ✅ Renamed: {numbered_md_file.name} → {base_name}.md")
            results["renamed_md"].append((numbered_md_file.name, f"{base_name}.md"))
        
        # Rename JSON
        if numbered_json_file.exists() and not correct_json.exists():
            if dry_run:
                print(f"   [DRY] Would rename: {numbered_json_file.name} → {base_name}.json")
            else:
                shutil.move(str(numbered_json_file), str(correct_json))
                print(f"   ✅ Renamed: {numbered_json_file.name} → {base_name}.json")
            results["renamed_json"].append((numbered_json_file.name, f"{base_name}.json"))
    
    return results


def main():
    import argparse
    parser = argparse.ArgumentParser(description="Rename numbered output files to match PDF names")
    parser.add_argument("--run", action="store_true", help="Actually perform renames (default is dry-run)")
    parser.add_argument("--category", type=str, help="Specific category to rename (default: all)")
    args = parser.parse_args()
    
    dry_run = not args.run
    
    if dry_run:
        print("🔍 DRY RUN MODE - No files will be changed. Use --run to apply changes.\n")
    else:
        print("⚠️  LIVE MODE - Files will be renamed!\n")
    
    if args.category:
        categories = [args.category]
    else:
        categories = [d.name for d in INPUT_DIR.iterdir() if d.is_dir()]
    
    all_results = []
    for cat in categories:
        results = rename_outputs_for_category(cat, dry_run=dry_run)
        all_results.append(results)
    
    # Summary
    print("\n" + "="*50)
    print("SUMMARY")
    print("="*50)
    
    total_md = sum(len(r["renamed_md"]) for r in all_results)
    total_json = sum(len(r["renamed_json"]) for r in all_results)
    total_skipped = sum(len(r["skipped"]) for r in all_results)
    
    print(f"MD files to rename: {total_md}")
    print(f"JSON files to rename: {total_json}")
    print(f"Skipped (already correct): {total_skipped}")
    
    if dry_run and (total_md > 0 or total_json > 0):
        print("\n💡 Run with --run flag to apply these changes")


if __name__ == "__main__":
    main()
