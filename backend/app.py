"""
Paper Pipeline Web Interface - Flask Backend
Serves the web application and exposes API endpoints for the paper processing pipeline.
"""

import os
import sys
import threading
import uuid
from datetime import datetime
from pathlib import Path
from queue import Queue
from typing import Any

from flask import Flask, jsonify, request
from flask_cors import CORS

# Add parent directory to path for pdf_processor import
sys.path.insert(0, str(Path(__file__).parent.parent))
from pdf_processor import LocalPDFProcessor

app = Flask(__name__, static_folder='../frontend', static_url_path='')

# Configure CORS for local network access
CORS(app, resources={
    r"/api/*": {
        "origins": "*",
        "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization"]
    }
})

# Data directory paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / 'data'
INPUT_DIR = DATA_DIR / 'input'
MARKDOWN_DIR = DATA_DIR / 'markdown'
OUTPUT_DIR = DATA_DIR / 'output'

# Ensure data directories exist
INPUT_DIR.mkdir(parents=True, exist_ok=True)
MARKDOWN_DIR.mkdir(parents=True, exist_ok=True)
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


# ============= Processing Infrastructure =============

# Job tracking
jobs: dict[str, dict[str, Any]] = {}
processing_queue: Queue[dict[str, Any]] = Queue()

# Processing state
processing_state = {
    "status": "idle",  # idle, running, paused
    "current_file": None,
    "current_phase": None,  # 1 (PDF→MD) or 2 (MD→JSON)
    "queue_length": 0,
}

# Processing lock
processing_lock = threading.Lock()

# Processor instance (lazy initialized)
_processor: LocalPDFProcessor | None = None


def get_processor() -> LocalPDFProcessor:
    """Get or create the PDF processor instance."""
    global _processor
    if _processor is None:
        _processor = LocalPDFProcessor(backend="vllm")
    return _processor


def find_file_by_id(file_id: str) -> tuple[Path, str] | None:
    """Find a PDF file by its ID. Returns (file_path, category) or None."""
    for category_dir in INPUT_DIR.iterdir():
        if category_dir.is_dir():
            for pdf_file in category_dir.glob("*.pdf"):
                if generate_file_id(category_dir.name, pdf_file.name) == file_id:
                    return (pdf_file, category_dir.name)
    return None


def process_single_file(pdf_path: Path, category: str, job_id: str) -> bool:
    """Process a single PDF file through the full pipeline."""
    global processing_state
    
    try:
        processor = get_processor()
        base_name = pdf_path.stem
        
        # Phase 1: PDF → Markdown
        with processing_lock:
            processing_state["current_file"] = pdf_path.name
            processing_state["current_phase"] = 1
        
        md_success = processor.convert_pdf_to_markdown(
            str(pdf_path), category, "001"  # sequence_id for naming
        )
        
        if not md_success:
            return False
        
        # Phase 2: Markdown → JSON
        with processing_lock:
            processing_state["current_phase"] = 2
        
        md_path = MARKDOWN_DIR / category / f"{base_name}.md"
        json_success = processor.generate_json_from_markdown(str(md_path), category)
        
        return json_success
        
    except Exception as e:
        print(f"Error processing {pdf_path.name}: {e}")
        return False


def background_processor():
    """Background thread that processes files from the queue."""
    global processing_state
    
    while True:
        # Get next file from queue
        task = processing_queue.get()
        
        if task is None:  # Shutdown signal
            break
        
        job_id = task["job_id"]
        pdf_path = task["pdf_path"]
        category = task["category"]
        file_id = task["file_id"]
        
        # Check if paused
        while True:
            with processing_lock:
                if processing_state["status"] == "idle":
                    # Job was cancelled
                    processing_queue.task_done()
                    continue
                if processing_state["status"] == "running":
                    break
            # Paused - wait a bit
            threading.Event().wait(0.5)
        
        # Update job status
        with processing_lock:
            processing_state["queue_length"] = processing_queue.qsize()
            if job_id in jobs:
                jobs[job_id]["status"] = "processing"
                jobs[job_id]["current_file"] = pdf_path.name
        
        # Process the file
        success = process_single_file(pdf_path, category, job_id)
        
        # Update job status
        with processing_lock:
            if job_id in jobs:
                if success:
                    jobs[job_id]["completed"].append(file_id)
                else:
                    jobs[job_id]["failed"].append(file_id)
            
            processing_state["queue_length"] = processing_queue.qsize()
            
            # If queue is empty, go idle
            if processing_queue.empty():
                processing_state["status"] = "idle"
                processing_state["current_file"] = None
                processing_state["current_phase"] = None
                if job_id in jobs:
                    jobs[job_id]["status"] = "completed"
        
        processing_queue.task_done()


# Start background processor thread
processor_thread = threading.Thread(target=background_processor, daemon=True)
processor_thread.start()


def get_file_status(filename: str, category: str) -> str:
    """Determine file status based on existence of output files."""
    base_name = Path(filename).stem
    json_path = OUTPUT_DIR / category / f"{base_name}.json"
    md_path = MARKDOWN_DIR / category / f"{base_name}.md"
    
    if json_path.exists():
        return "completed"
    elif md_path.exists():
        return "markdown"
    else:
        return "pending"


def get_category_stats(category_name: str) -> dict:
    """Get file counts and status summary for a category."""
    category_path = INPUT_DIR / category_name
    if not category_path.is_dir():
        return {"file_count": 0, "status_summary": {}}
    
    pdf_files = list(category_path.glob("*.pdf"))
    status_summary = {"pending": 0, "markdown": 0, "completed": 0, "failed": 0}
    
    for pdf in pdf_files:
        status = get_file_status(pdf.name, category_name)
        status_summary[status] = status_summary.get(status, 0) + 1
    
    return {
        "file_count": len(pdf_files),
        "status_summary": status_summary
    }


@app.route('/')
def index():
    """Serve the frontend index.html"""
    return app.send_static_file('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({"status": "ok"})


# ============= Processing Status API Endpoints =============

@app.route('/api/status', methods=['GET'])
def get_status():
    """Get current processing status and queue information."""
    with processing_lock:
        status_response = {
            "status": processing_state["status"],  # idle, running, or paused
            "current_file": processing_state["current_file"],
            "current_phase": processing_state["current_phase"],  # 1 (PDF→MD) or 2 (MD→JSON)
            "queue_length": processing_state["queue_length"],
        }
    
    return jsonify(status_response)


# ============= Processing Control API Endpoints =============

@app.route('/api/process/pause', methods=['POST'])
def pause_processing():
    """Pause processing after the current file completes."""
    with processing_lock:
        if processing_state["status"] == "idle":
            return jsonify({
                "error": "No processing in progress to pause"
            }), 400
        
        if processing_state["status"] == "paused":
            return jsonify({
                "message": "Processing is already paused",
                "status": "paused"
            }), 200
        
        processing_state["status"] = "paused"
        return jsonify({
            "message": "Processing will pause after current file completes",
            "status": "paused",
            "current_file": processing_state["current_file"]
        }), 200


@app.route('/api/process/resume', methods=['POST'])
def resume_processing():
    """Resume paused processing."""
    with processing_lock:
        if processing_state["status"] == "idle":
            return jsonify({
                "error": "No processing in progress to resume"
            }), 400
        
        if processing_state["status"] == "running":
            return jsonify({
                "message": "Processing is already running",
                "status": "running"
            }), 200
        
        processing_state["status"] = "running"
        return jsonify({
            "message": "Processing resumed",
            "status": "running",
            "queue_length": processing_state["queue_length"]
        }), 200


@app.route('/api/process/cancel', methods=['POST'])
def cancel_processing():
    """Cancel processing and clear the queue."""
    global processing_queue
    
    with processing_lock:
        if processing_state["status"] == "idle":
            return jsonify({
                "message": "No processing in progress",
                "status": "idle"
            }), 200
        
        # Clear the queue by creating a new empty queue
        items_cleared = processing_queue.qsize()
        
        # Drain the queue
        while not processing_queue.empty():
            try:
                processing_queue.get_nowait()
                processing_queue.task_done()
            except Exception:
                break
        
        # Reset state to idle
        processing_state["status"] = "idle"
        processing_state["current_file"] = None
        processing_state["current_phase"] = None
        processing_state["queue_length"] = 0
        
        return jsonify({
            "message": "Processing cancelled and queue cleared",
            "status": "idle",
            "items_cleared": items_cleared
        }), 200


# ============= Category API Endpoints =============

@app.route('/api/categories', methods=['GET'])
def list_categories():
    """List all categories with file counts and status summary."""
    categories = []
    
    if INPUT_DIR.exists():
        for item in sorted(INPUT_DIR.iterdir()):
            if item.is_dir():
                stats = get_category_stats(item.name)
                categories.append({
                    "name": item.name,
                    "file_count": stats["file_count"],
                    "status_summary": stats["status_summary"]
                })
    
    return jsonify({"categories": categories})


@app.route('/api/categories', methods=['POST'])
def create_category():
    """Create a new category folder in data/input/."""
    data = request.get_json()
    
    if not data or 'name' not in data:
        return jsonify({"error": "Category name is required"}), 400
    
    name = data['name'].strip()
    
    # Validate category name
    if not name:
        return jsonify({"error": "Category name cannot be empty"}), 400
    
    # Prevent special characters that could cause path issues
    if any(c in name for c in ['/', '\\', '..', '\0']):
        return jsonify({"error": "Invalid category name"}), 400
    
    category_path = INPUT_DIR / name
    
    if category_path.exists():
        return jsonify({"error": f"Category '{name}' already exists"}), 400
    
    try:
        category_path.mkdir(parents=True)
        # Also create corresponding markdown and output directories
        (MARKDOWN_DIR / name).mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / name).mkdir(parents=True, exist_ok=True)
        
        return jsonify({
            "message": f"Category '{name}' created successfully",
            "category": {
                "name": name,
                "file_count": 0,
                "status_summary": {"pending": 0, "markdown": 0, "completed": 0, "failed": 0}
            }
        }), 201
    except OSError as e:
        return jsonify({"error": f"Failed to create category: {str(e)}"}), 500


@app.route('/api/categories/<name>', methods=['DELETE'])
def delete_category(name: str):
    """Delete an empty category folder."""
    category_path = INPUT_DIR / name
    
    if not category_path.exists():
        return jsonify({"error": f"Category '{name}' not found"}), 404
    
    if not category_path.is_dir():
        return jsonify({"error": f"'{name}' is not a valid category"}), 400
    
    # Check if category is empty
    files = list(category_path.iterdir())
    if files:
        return jsonify({
            "error": f"Category '{name}' is not empty. Delete all files first.",
            "file_count": len(files)
        }), 400
    
    try:
        category_path.rmdir()
        
        # Also remove corresponding markdown and output directories if empty
        md_path = MARKDOWN_DIR / name
        out_path = OUTPUT_DIR / name
        
        if md_path.exists() and md_path.is_dir() and not any(md_path.iterdir()):
            md_path.rmdir()
        if out_path.exists() and out_path.is_dir() and not any(out_path.iterdir()):
            out_path.rmdir()
        
        return jsonify({"message": f"Category '{name}' deleted successfully"})
    except OSError as e:
        return jsonify({"error": f"Failed to delete category: {str(e)}"}), 500


# ============= File Upload API Endpoints =============

def get_unique_filename(directory: Path, filename: str) -> str:
    """Generate a unique filename by appending a number if file already exists."""
    base = Path(filename).stem
    suffix = Path(filename).suffix
    
    if not (directory / filename).exists():
        return filename
    
    counter = 1
    while True:
        new_name = f"{base}_{counter}{suffix}"
        if not (directory / new_name).exists():
            return new_name
        counter += 1


def generate_file_id(category: str, filename: str) -> str:
    """Generate a unique file ID based on category and filename."""
    import hashlib
    return hashlib.md5(f"{category}/{filename}".encode()).hexdigest()[:12]


def is_valid_pdf(file) -> bool:
    """Validate that the file is a PDF by checking extension and MIME type."""
    # Check extension
    if not file.filename or not file.filename.lower().endswith('.pdf'):
        return False
    
    # Check MIME type
    if file.content_type and file.content_type not in ['application/pdf', 'application/x-pdf']:
        # Allow empty/missing content_type as some clients don't send it
        if file.content_type != 'application/octet-stream':
            return False
    
    return True


@app.route('/api/categories/<name>/upload', methods=['POST'])
def upload_file(name: str):
    """Upload a PDF file to a specific category."""
    category_path = INPUT_DIR / name
    
    # Validate category exists
    if not category_path.exists() or not category_path.is_dir():
        return jsonify({"error": f"Category '{name}' not found"}), 404
    
    # Check for file in request
    if 'file' not in request.files:
        return jsonify({"error": "No file provided"}), 400
    
    file = request.files['file']
    
    if not file.filename:
        return jsonify({"error": "No file selected"}), 400
    
    # Validate PDF
    if not is_valid_pdf(file):
        return jsonify({"error": "Only PDF files are allowed"}), 400
    
    # Secure and handle duplicate filenames
    from werkzeug.utils import secure_filename
    safe_filename = secure_filename(file.filename)
    if not safe_filename.lower().endswith('.pdf'):
        safe_filename = safe_filename + '.pdf'
    
    final_filename = get_unique_filename(category_path, safe_filename)
    file_path = category_path / final_filename
    
    try:
        file.save(str(file_path))
        file_size = file_path.stat().st_size
        file_id = generate_file_id(name, final_filename)
        
        return jsonify({
            "message": "File uploaded successfully",
            "file": {
                "id": file_id,
                "filename": final_filename,
                "original_filename": file.filename,
                "category": name,
                "size": file_size,
                "status": "pending"
            }
        }), 201
    except OSError as e:
        return jsonify({"error": f"Failed to save file: {str(e)}"}), 500


# ============= File Listing API Endpoints =============

@app.route('/api/categories/<name>/files', methods=['GET'])
def list_files(name: str):
    """List all files in a category with their processing status."""
    category_path = INPUT_DIR / name
    
    # Validate category exists
    if not category_path.exists() or not category_path.is_dir():
        return jsonify({"error": f"Category '{name}' not found"}), 404
    
    files = []
    
    for pdf_file in sorted(category_path.glob("*.pdf")):
        stat = pdf_file.stat()
        file_id = generate_file_id(name, pdf_file.name)
        status = get_file_status(pdf_file.name, name)
        
        # Get file creation/upload time (use mtime as closest approximation)
        upload_date = datetime.fromtimestamp(stat.st_mtime).isoformat()
        
        files.append({
            "id": file_id,
            "filename": pdf_file.name,
            "category": name,
            "status": status,
            "size": stat.st_size,
            "upload_date": upload_date
        })
    
    return jsonify({
        "category": name,
        "files": files,
        "total_count": len(files)
    })


# ============= Processing Trigger API Endpoints =============

def create_job(file_count: int) -> str:
    """Create a new processing job and return its ID."""
    job_id = str(uuid.uuid4())[:8]
    jobs[job_id] = {
        "id": job_id,
        "status": "queued",
        "created_at": datetime.now().isoformat(),
        "total_files": file_count,
        "completed": [],
        "failed": [],
        "current_file": None
    }
    return job_id


def queue_files_for_processing(file_list: list[tuple[Path, str]], job_id: str) -> None:
    """Add files to the processing queue."""
    global processing_state
    
    for pdf_path, category in file_list:
        file_id = generate_file_id(category, pdf_path.name)
        processing_queue.put({
            "job_id": job_id,
            "pdf_path": pdf_path,
            "category": category,
            "file_id": file_id
        })
    
    with processing_lock:
        processing_state["status"] = "running"
        processing_state["queue_length"] = processing_queue.qsize()


@app.route('/api/process/file/<file_id>', methods=['POST'])
def process_file(file_id: str):
    """Trigger full pipeline processing for a single file."""
    result = find_file_by_id(file_id)
    
    if result is None:
        return jsonify({"error": f"File with ID '{file_id}' not found"}), 404
    
    pdf_path, category = result
    
    # Check if file is already processed
    status = get_file_status(pdf_path.name, category)
    if status == "completed":
        return jsonify({
            "error": "File is already processed",
            "suggestion": "Use /api/files/<file_id>/reprocess to reprocess"
        }), 400
    
    # Create job and queue file
    job_id = create_job(1)
    queue_files_for_processing([(pdf_path, category)], job_id)
    
    return jsonify({
        "message": "Processing started",
        "job_id": job_id,
        "file": {
            "id": file_id,
            "filename": pdf_path.name,
            "category": category
        }
    }), 202


@app.route('/api/process/category/<name>', methods=['POST'])
def process_category(name: str):
    """Trigger processing for all pending files in a category."""
    category_path = INPUT_DIR / name
    
    if not category_path.exists() or not category_path.is_dir():
        return jsonify({"error": f"Category '{name}' not found"}), 404
    
    # Find all pending files in category
    pending_files: list[tuple[Path, str]] = []
    for pdf_file in category_path.glob("*.pdf"):
        status = get_file_status(pdf_file.name, name)
        if status in ["pending", "markdown"]:  # Include markdown (phase 1 done, need phase 2)
            pending_files.append((pdf_file, name))
    
    if not pending_files:
        return jsonify({
            "message": "No pending files to process in this category"
        }), 200
    
    # Create job and queue files
    job_id = create_job(len(pending_files))
    queue_files_for_processing(pending_files, job_id)
    
    return jsonify({
        "message": f"Processing started for {len(pending_files)} files",
        "job_id": job_id,
        "category": name,
        "file_count": len(pending_files)
    }), 202


@app.route('/api/process/all', methods=['POST'])
def process_all():
    """Trigger processing for all pending files across all categories."""
    pending_files: list[tuple[Path, str]] = []
    
    for category_dir in INPUT_DIR.iterdir():
        if category_dir.is_dir():
            category_name = category_dir.name
            for pdf_file in category_dir.glob("*.pdf"):
                status = get_file_status(pdf_file.name, category_name)
                if status in ["pending", "markdown"]:
                    pending_files.append((pdf_file, category_name))
    
    if not pending_files:
        return jsonify({
            "message": "No pending files to process"
        }), 200
    
    # Create job and queue files
    job_id = create_job(len(pending_files))
    queue_files_for_processing(pending_files, job_id)
    
    # Count by category
    category_counts: dict[str, int] = {}
    for _, category in pending_files:
        category_counts[category] = category_counts.get(category, 0) + 1
    
    return jsonify({
        "message": f"Processing started for {len(pending_files)} files",
        "job_id": job_id,
        "total_files": len(pending_files),
        "by_category": category_counts
    }), 202


# ============= Results API Endpoints =============

@app.route('/api/results/<file_id>', methods=['GET'])
def get_results(file_id: str):
    """Get parsed JSON content for a processed file."""
    import json
    
    result = find_file_by_id(file_id)
    
    if result is None:
        return jsonify({"error": f"File with ID '{file_id}' not found"}), 404
    
    pdf_path, category = result
    base_name = pdf_path.stem
    json_path = OUTPUT_DIR / category / f"{base_name}.json"
    
    if not json_path.exists():
        status = get_file_status(pdf_path.name, category)
        return jsonify({
            "error": "File not yet processed",
            "file_id": file_id,
            "filename": pdf_path.name,
            "status": status,
            "suggestion": "Use /api/process/file/<file_id> to process this file"
        }), 404
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = json.load(f)
        
        return jsonify({
            "file_id": file_id,
            "filename": pdf_path.name,
            "category": category,
            "results": content
        })
    except json.JSONDecodeError as e:
        return jsonify({
            "error": "Failed to parse JSON results",
            "details": str(e)
        }), 500
    except OSError as e:
        return jsonify({
            "error": f"Failed to read results file: {str(e)}"
        }), 500


@app.route('/api/results/<file_id>/raw', methods=['GET'])
def get_results_raw(file_id: str):
    """Get raw JSON file content for a processed file."""
    from flask import Response
    
    result = find_file_by_id(file_id)
    
    if result is None:
        return jsonify({"error": f"File with ID '{file_id}' not found"}), 404
    
    pdf_path, category = result
    base_name = pdf_path.stem
    json_path = OUTPUT_DIR / category / f"{base_name}.json"
    
    if not json_path.exists():
        status = get_file_status(pdf_path.name, category)
        return jsonify({
            "error": "File not yet processed",
            "file_id": file_id,
            "filename": pdf_path.name,
            "status": status,
            "suggestion": "Use /api/process/file/<file_id> to process this file"
        }), 404
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        return Response(
            content,
            mimetype='application/json',
            headers={
                'Content-Disposition': f'attachment; filename="{base_name}.json"'
            }
        )
    except OSError as e:
        return jsonify({
            "error": f"Failed to read results file: {str(e)}"
        }), 500


# ============= File Delete and Reprocess API Endpoints =============

@app.route('/api/files/<file_id>', methods=['DELETE'])
def delete_file(file_id: str):
    """Delete a PDF file and all associated outputs (markdown and JSON)."""
    result = find_file_by_id(file_id)
    
    if result is None:
        return jsonify({"error": f"File with ID '{file_id}' not found"}), 404
    
    pdf_path, category = result
    base_name = pdf_path.stem
    
    # Paths for associated files
    md_path = MARKDOWN_DIR / category / f"{base_name}.md"
    json_path = OUTPUT_DIR / category / f"{base_name}.json"
    
    deleted_files = []
    errors = []
    
    # Delete PDF
    try:
        if pdf_path.exists():
            pdf_path.unlink()
            deleted_files.append(f"input/{category}/{pdf_path.name}")
    except OSError as e:
        errors.append(f"Failed to delete PDF: {str(e)}")
    
    # Delete markdown output
    try:
        if md_path.exists():
            md_path.unlink()
            deleted_files.append(f"markdown/{category}/{base_name}.md")
    except OSError as e:
        errors.append(f"Failed to delete markdown: {str(e)}")
    
    # Delete JSON output
    try:
        if json_path.exists():
            json_path.unlink()
            deleted_files.append(f"output/{category}/{base_name}.json")
    except OSError as e:
        errors.append(f"Failed to delete JSON: {str(e)}")
    
    if errors:
        return jsonify({
            "message": "File deletion completed with errors",
            "file_id": file_id,
            "filename": pdf_path.name,
            "category": category,
            "deleted": deleted_files,
            "errors": errors
        }), 207  # Multi-Status
    
    return jsonify({
        "message": "File and all outputs deleted successfully",
        "file_id": file_id,
        "filename": pdf_path.name,
        "category": category,
        "deleted": deleted_files
    }), 200


@app.route('/api/files/<file_id>/reprocess', methods=['POST'])
def reprocess_file(file_id: str):
    """Clear outputs and queue file for reprocessing."""
    result = find_file_by_id(file_id)
    
    if result is None:
        return jsonify({"error": f"File with ID '{file_id}' not found"}), 404
    
    pdf_path, category = result
    base_name = pdf_path.stem
    
    # Paths for associated files
    md_path = MARKDOWN_DIR / category / f"{base_name}.md"
    json_path = OUTPUT_DIR / category / f"{base_name}.json"
    
    cleared_files = []
    
    # Clear markdown output
    try:
        if md_path.exists():
            md_path.unlink()
            cleared_files.append(f"markdown/{category}/{base_name}.md")
    except OSError as e:
        return jsonify({
            "error": f"Failed to clear markdown output: {str(e)}"
        }), 500
    
    # Clear JSON output
    try:
        if json_path.exists():
            json_path.unlink()
            cleared_files.append(f"output/{category}/{base_name}.json")
    except OSError as e:
        return jsonify({
            "error": f"Failed to clear JSON output: {str(e)}"
        }), 500
    
    # Queue file for reprocessing
    job_id = create_job(1)
    queue_files_for_processing([(pdf_path, category)], job_id)
    
    return jsonify({
        "message": "File outputs cleared and queued for reprocessing",
        "job_id": job_id,
        "file_id": file_id,
        "filename": pdf_path.name,
        "category": category,
        "cleared_outputs": cleared_files
    }), 202


# ============= Search and Filter API Endpoints =============

def search_in_json_result(json_data: dict, query: str) -> dict[str, list[str]]:
    """Search for query in JSON result fields and return matching snippets.
    
    Returns dict with field names as keys and list of matching snippets as values.
    """
    query_lower = query.lower()
    matches: dict[str, list[str]] = {}
    
    # Search in title
    title = json_data.get("title", "")
    if isinstance(title, str) and query_lower in title.lower():
        matches["title"] = [title]
    
    # Search in authors
    authors = json_data.get("authors", [])
    if isinstance(authors, list):
        matching_authors = [a for a in authors if isinstance(a, str) and query_lower in a.lower()]
        if matching_authors:
            matches["authors"] = matching_authors
    elif isinstance(authors, str) and query_lower in authors.lower():
        matches["authors"] = [authors]
    
    # Search in keywords
    keywords = json_data.get("keywords", [])
    if isinstance(keywords, list):
        matching_keywords = [k for k in keywords if isinstance(k, str) and query_lower in k.lower()]
        if matching_keywords:
            matches["keywords"] = matching_keywords
    elif isinstance(keywords, str) and query_lower in keywords.lower():
        matches["keywords"] = [keywords]
    
    # Search in summary/abstract
    summary = json_data.get("summary", json_data.get("abstract", ""))
    if isinstance(summary, str) and query_lower in summary.lower():
        # Extract a snippet around the match
        idx = summary.lower().find(query_lower)
        start = max(0, idx - 50)
        end = min(len(summary), idx + len(query) + 50)
        snippet = summary[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(summary):
            snippet = snippet + "..."
        matches["summary"] = [snippet]
    
    return matches


@app.route('/api/search', methods=['GET'])
def search_files():
    """Search across processed JSON results.
    
    Query params:
        q: Search query (required)
        category: Filter by category name (optional)
    
    Returns matching files with relevance snippets.
    """
    import json
    
    query = request.args.get('q', '').strip()
    category_filter = request.args.get('category', '').strip()
    
    if not query:
        return jsonify({"error": "Search query 'q' is required"}), 400
    
    results = []
    
    # Determine which categories to search
    if category_filter:
        category_dirs = [OUTPUT_DIR / category_filter]
        if not category_dirs[0].exists():
            return jsonify({
                "error": f"Category '{category_filter}' not found",
                "query": query
            }), 404
    else:
        category_dirs = [d for d in OUTPUT_DIR.iterdir() if d.is_dir()]
    
    # Search through all JSON files
    for category_dir in category_dirs:
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        
        for json_file in category_dir.glob("*.json"):
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    json_data = json.load(f)
                
                # Search in the JSON content
                matches = search_in_json_result(json_data, query)
                
                if matches:
                    # Find the corresponding PDF to get file_id
                    pdf_name = json_file.stem + ".pdf"
                    pdf_path = INPUT_DIR / category_name / pdf_name
                    
                    if pdf_path.exists():
                        file_id = generate_file_id(category_name, pdf_name)
                    else:
                        # PDF was deleted but JSON exists - use filename as ID fallback
                        file_id = generate_file_id(category_name, pdf_name)
                    
                    results.append({
                        "file_id": file_id,
                        "filename": pdf_name,
                        "category": category_name,
                        "title": json_data.get("title", json_file.stem),
                        "matches": matches,
                        "match_count": sum(len(v) for v in matches.values())
                    })
                    
            except (json.JSONDecodeError, OSError):
                # Skip files that can't be read or parsed
                continue
    
    # Sort by match count (more matches = more relevant)
    results.sort(key=lambda x: x["match_count"], reverse=True)
    
    return jsonify({
        "query": query,
        "category": category_filter if category_filter else None,
        "results": results,
        "total_count": len(results)
    })


# ============= Batch Export API Endpoints =============


def create_export_zip(
    files_to_export: list[tuple[Path, str, str]],  # (file_path, archive_name, file_type)
    include_pdfs: bool = False
) -> bytes:
    """Create a zip file in memory with the given files.
    
    Args:
        files_to_export: List of tuples (file_path, archive_name, file_type)
            where file_type is 'json' or 'pdf'
        include_pdfs: Whether to include PDF files along with JSONs
    
    Returns:
        Bytes of the zip file
    """
    import io
    import zipfile
    
    buffer = io.BytesIO()
    
    with zipfile.ZipFile(buffer, 'w', zipfile.ZIP_DEFLATED) as zf:
        for file_path, archive_name, file_type in files_to_export:
            if file_type == 'pdf' and not include_pdfs:
                continue
            if file_path.exists():
                zf.write(file_path, archive_name)
    
    buffer.seek(0)
    return buffer.getvalue()


@app.route('/api/export/category/<name>', methods=['GET'])
def export_category(name: str):
    """Export all processed JSON results in a category as a zip file.
    
    Query params:
        include_pdf: If 'true', includes original PDF files (default: false)
    
    Returns:
        Zip file containing JSON results and optionally PDFs
    """
    from flask import Response
    
    category_output_dir = OUTPUT_DIR / name
    category_input_dir = INPUT_DIR / name
    
    # Validate category exists
    if not category_input_dir.exists() or not category_input_dir.is_dir():
        return jsonify({"error": f"Category '{name}' not found"}), 404
    
    include_pdfs = request.args.get('include_pdf', 'false').lower() == 'true'
    
    # Collect all JSON files in the category
    files_to_export: list[tuple[Path, str, str]] = []
    
    if category_output_dir.exists():
        for json_file in category_output_dir.glob("*.json"):
            # Add JSON file
            archive_name = f"{name}/{json_file.name}"
            files_to_export.append((json_file, archive_name, 'json'))
            
            # Add corresponding PDF if requested
            if include_pdfs:
                pdf_name = json_file.stem + ".pdf"
                pdf_path = category_input_dir / pdf_name
                if pdf_path.exists():
                    pdf_archive_name = f"{name}/{pdf_name}"
                    files_to_export.append((pdf_path, pdf_archive_name, 'pdf'))
    
    if not files_to_export:
        return jsonify({
            "error": "No processed files to export",
            "category": name,
            "suggestion": "Process some files first using /api/process/category/" + name
        }), 404
    
    # Create zip file
    zip_data = create_export_zip(files_to_export, include_pdfs)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_{name}_{timestamp}.zip"
    
    return Response(
        zip_data,
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(zip_data))
        }
    )


@app.route('/api/export/all', methods=['GET'])
def export_all():
    """Export all processed JSON results across all categories as a zip file.
    
    Query params:
        include_pdf: If 'true', includes original PDF files (default: false)
    
    Returns:
        Zip file containing JSON results and optionally PDFs, organized by category
    """
    from flask import Response
    
    include_pdfs = request.args.get('include_pdf', 'false').lower() == 'true'
    
    # Collect all JSON files across all categories
    files_to_export: list[tuple[Path, str, str]] = []
    
    for category_dir in OUTPUT_DIR.iterdir():
        if not category_dir.is_dir():
            continue
        
        category_name = category_dir.name
        category_input_dir = INPUT_DIR / category_name
        
        for json_file in category_dir.glob("*.json"):
            # Add JSON file
            archive_name = f"{category_name}/{json_file.name}"
            files_to_export.append((json_file, archive_name, 'json'))
            
            # Add corresponding PDF if requested
            if include_pdfs:
                pdf_name = json_file.stem + ".pdf"
                pdf_path = category_input_dir / pdf_name
                if pdf_path.exists():
                    pdf_archive_name = f"{category_name}/{pdf_name}"
                    files_to_export.append((pdf_path, pdf_archive_name, 'pdf'))
    
    if not files_to_export:
        return jsonify({
            "error": "No processed files to export",
            "suggestion": "Process some files first using /api/process/all"
        }), 404
    
    # Create zip file
    zip_data = create_export_zip(files_to_export, include_pdfs)
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"export_all_{timestamp}.zip"
    
    # Count files by category for response metadata in headers
    json_count = sum(1 for _, _, t in files_to_export if t == 'json')
    
    return Response(
        zip_data,
        mimetype='application/zip',
        headers={
            'Content-Disposition': f'attachment; filename="{filename}"',
            'Content-Length': str(len(zip_data)),
            'X-Export-File-Count': str(json_count)
        }
    )


if __name__ == '__main__':
    # Bind to 0.0.0.0 for LAN accessibility
    app.run(host='0.0.0.0', port=5000, debug=True)
