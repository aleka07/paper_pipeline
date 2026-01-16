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


if __name__ == '__main__':
    # Bind to 0.0.0.0 for LAN accessibility
    app.run(host='0.0.0.0', port=5000, debug=True)
