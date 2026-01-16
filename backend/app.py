"""
Paper Pipeline Web Interface - Flask Backend
Serves the web application and exposes API endpoints for the paper processing pipeline.
"""

from flask import Flask, jsonify
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


@app.route('/')
def index():
    """Serve the frontend index.html"""
    return app.send_static_file('index.html')


@app.route('/api/health')
def health_check():
    """Health check endpoint to verify the server is running."""
    return jsonify({"status": "ok"})


if __name__ == '__main__':
    # Bind to 0.0.0.0 for LAN accessibility
    app.run(host='0.0.0.0', port=5000, debug=True)
