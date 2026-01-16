"""
Paper Pipeline Web Interface - Flask Backend
Serves the web application and exposes API endpoints for the paper processing pipeline.
"""

import os
from pathlib import Path

from flask import Flask, jsonify, request
from flask_cors import CORS

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


if __name__ == '__main__':
    # Bind to 0.0.0.0 for LAN accessibility
    app.run(host='0.0.0.0', port=5000, debug=True)
