# PRD: Paper Pipeline Web Interface

## Introduction

A full-featured web interface for the Paper Pipeline system, enabling coworkers and researchers to process academic PDFs over the local network. The interface provides complete control over the processing pipeline including uploading PDFs, managing categories, monitoring processing status, and viewing/exporting extracted JSON data.

**Target Environment:** Local network access (LAN) for team collaboration.

## Goals

- Allow users to upload PDFs and organize them into categories from any device on the network
- Provide real-time visibility into processing status with clear status badges
- Enable full control over the pipeline: upload, pause, resume, reprocess, delete
- Display structured JSON results with search, filter, and export capabilities
- Support batch operations for processing multiple files/categories
- Maintain the existing CLI functionality (web is an additional interface, not a replacement)

## User Stories

### US-001: Flask Backend Setup
**Description:** As a developer, I need a Flask backend that serves the web application and exposes API endpoints for the pipeline.

**Acceptance Criteria:**
- [ ] Create `backend/app.py` with Flask application setup
- [ ] Configure CORS for local network access
- [ ] Application binds to `0.0.0.0:5000` for LAN accessibility
- [ ] Health check endpoint at `/api/health` returns `{"status": "ok"}`
- [ ] Typecheck passes

---

### US-002: Category API Endpoints
**Description:** As a user, I want API endpoints to list, create, and delete categories so I can organize my papers.

**Acceptance Criteria:**
- [ ] `GET /api/categories` returns list of categories with file counts and status summary
- [ ] `POST /api/categories` creates a new category folder in `data/input/`
- [ ] `DELETE /api/categories/<name>` removes empty category folder
- [ ] Returns proper HTTP status codes (200, 201, 400, 404)
- [ ] Typecheck passes

---

### US-003: File Upload API
**Description:** As a user, I want to upload PDF files to a specific category via API.

**Acceptance Criteria:**
- [ ] `POST /api/categories/<name>/upload` accepts multipart file upload
- [ ] Validates file is PDF (checks extension and MIME type)
- [ ] Saves file to `data/input/<category>/` with original filename
- [ ] Returns uploaded file info with generated ID
- [ ] Handles duplicate filenames (appends number if exists)
- [ ] Typecheck passes

---

### US-004: File Listing API with Status
**Description:** As a user, I want to see all files in a category with their processing status.

**Acceptance Criteria:**
- [ ] `GET /api/categories/<name>/files` returns list of files
- [ ] Each file includes: filename, id, status (pending/markdown/completed/failed)
- [ ] Status derived from existence of `.md` and `.json` output files
- [ ] Includes file size and upload date
- [ ] Typecheck passes

---

### US-005: Processing Trigger API
**Description:** As a user, I want to trigger processing of files via API.

**Acceptance Criteria:**
- [ ] `POST /api/process/file/<file_id>` triggers full pipeline for single file
- [ ] `POST /api/process/category/<name>` triggers processing for all pending files in category
- [ ] `POST /api/process/all` triggers processing for all pending files
- [ ] Processing runs in background thread (non-blocking)
- [ ] Returns job ID for status tracking
- [ ] Typecheck passes

---

### US-006: Processing Status API
**Description:** As a user, I want to check the current processing status and queue.

**Acceptance Criteria:**
- [ ] `GET /api/status` returns current processing state
- [ ] Shows: currently processing file, queue length, phase (1 or 2)
- [ ] Shows if processing is idle, running, or paused
- [ ] Typecheck passes

---

### US-007: Processing Control API (Pause/Resume/Cancel)
**Description:** As a user, I want to control the processing pipeline.

**Acceptance Criteria:**
- [ ] `POST /api/process/pause` pauses processing after current file
- [ ] `POST /api/process/resume` resumes paused processing
- [ ] `POST /api/process/cancel` stops processing and clears queue
- [ ] State changes reflected in `/api/status`
- [ ] Typecheck passes

---

### US-008: Results API (JSON Output)
**Description:** As a user, I want to retrieve the extracted JSON results.

**Acceptance Criteria:**
- [ ] `GET /api/results/<file_id>` returns parsed JSON content
- [ ] `GET /api/results/<file_id>/raw` returns raw JSON file content
- [ ] Returns 404 if file not yet processed
- [ ] Typecheck passes

---

### US-009: File Delete and Reprocess API
**Description:** As a user, I want to delete files or trigger reprocessing.

**Acceptance Criteria:**
- [ ] `DELETE /api/files/<file_id>` removes PDF and all associated outputs (md, json)
- [ ] `POST /api/files/<file_id>/reprocess` clears outputs and queues for processing
- [ ] Confirms deletion with file info in response
- [ ] Typecheck passes

---

### US-010: Search and Filter API
**Description:** As a user, I want to search across processed papers.

**Acceptance Criteria:**
- [ ] `GET /api/search?q=<query>` searches across JSON results
- [ ] Searches title, authors, keywords, summary fields
- [ ] Returns matching files with relevance snippets
- [ ] Supports filter by category: `?category=<name>`
- [ ] Typecheck passes

---

### US-011: Batch Export API
**Description:** As a user, I want to export multiple results.

**Acceptance Criteria:**
- [ ] `GET /api/export/category/<name>` exports all JSONs in category as zip
- [ ] `GET /api/export/all` exports all processed JSONs as zip
- [ ] Includes original PDFs if `?include_pdf=true`
- [ ] Typecheck passes

---

### US-012: Frontend HTML Structure
**Description:** As a user, I want a clean web interface layout.

**Acceptance Criteria:**
- [ ] Create `frontend/index.html` with semantic HTML structure
- [ ] Header with app title and global actions (process all, settings)
- [ ] Sidebar for category navigation
- [ ] Main content area for file list and results
- [ ] Responsive layout works on desktop and tablet
- [ ] Verify in browser using browser tool

---

### US-013: Frontend Styling (CSS Design System)
**Description:** As a user, I want a modern, visually appealing interface.

**Acceptance Criteria:**
- [ ] Create `frontend/styles.css` with CSS custom properties for theming
- [ ] Dark mode design with vibrant accent colors
- [ ] Smooth hover effects and transitions on interactive elements
- [ ] Status badge styling: green (completed), yellow (markdown), blue (pending), red (failed)
- [ ] Glassmorphism effects on panels
- [ ] Verify in browser using browser tool

---

### US-014: Category Sidebar Component
**Description:** As a user, I want to navigate between categories in the sidebar.

**Acceptance Criteria:**
- [ ] Sidebar lists all categories from API
- [ ] Each category shows name and file count badge
- [ ] Clicking category loads its files in main area
- [ ] "Add Category" button opens modal to create new category
- [ ] Selected category visually highlighted
- [ ] Verify in browser using browser tool

---

### US-015: File List Component
**Description:** As a user, I want to see files in the selected category.

**Acceptance Criteria:**
- [ ] Main area shows grid/list of files for selected category
- [ ] Each file card shows: filename, status badge, file size
- [ ] Status badges use colors: ✅ green (done), 🔶 yellow (md only), ⏳ blue (pending)
- [ ] Click file card to view details/results
- [ ] Verify in browser using browser tool

---

### US-016: File Upload UI
**Description:** As a user, I want to upload PDFs through a drag-and-drop interface.

**Acceptance Criteria:**
- [ ] Upload zone accepts drag-and-drop of PDF files
- [ ] Click to open file picker as alternative
- [ ] Shows upload progress indicator
- [ ] Validates PDF files before upload
- [ ] New files appear in list after successful upload
- [ ] Verify in browser using browser tool

---

### US-017: Processing Controls UI
**Description:** As a user, I want buttons to control processing.

**Acceptance Criteria:**
- [ ] "Process Selected" button for selected files
- [ ] "Process Category" button in category header
- [ ] "Process All" button in global header
- [ ] Pause/Resume toggle button when processing active
- [ ] Cancel button to stop and clear queue
- [ ] Verify in browser using browser tool

---

### US-018: Processing Status Display
**Description:** As a user, I want to see current processing status.

**Acceptance Criteria:**
- [ ] Status bar shows: current file being processed, queue count
- [ ] Status updates via polling (every 2 seconds)
- [ ] Shows "Idle" when nothing is processing
- [ ] Shows "Paused" state distinctly
- [ ] Verify in browser using browser tool

---

### US-019: Results Viewer Panel
**Description:** As a user, I want to view extracted JSON data in a readable format.

**Acceptance Criteria:**
- [ ] Clicking a completed file shows results panel
- [ ] Displays metadata (title, authors, year, venue)
- [ ] Shows summary, methodology, and key findings sections
- [ ] Keywords displayed as tags
- [ ] Copy JSON button and download button
- [ ] Verify in browser using browser tool

---

### US-020: Search Interface
**Description:** As a user, I want to search across all processed papers.

**Acceptance Criteria:**
- [ ] Search input in header with instant search (debounced 300ms)
- [ ] Results show matching papers with highlighted snippets
- [ ] Click result navigates to that file's results view
- [ ] Empty state when no matches
- [ ] Verify in browser using browser tool

---

### US-021: File Context Menu (Actions)
**Description:** As a user, I want quick actions on files.

**Acceptance Criteria:**
- [ ] Right-click or menu button on file card shows context menu
- [ ] Options: View, Process, Reprocess, Download JSON, Download PDF, Delete
- [ ] Delete shows confirmation dialog
- [ ] Actions trigger appropriate API calls
- [ ] Verify in browser using browser tool

---

### US-022: Batch Selection and Actions
**Description:** As a user, I want to select multiple files for batch operations.

**Acceptance Criteria:**
- [ ] Checkbox on each file card for multi-select
- [ ] "Select All" checkbox in list header
- [ ] Batch action bar appears when files selected
- [ ] Batch options: Process Selected, Delete Selected, Export Selected
- [ ] Verify in browser using browser tool

---

### US-023: Category Export UI
**Description:** As a user, I want to export all results from a category.

**Acceptance Criteria:**
- [ ] Export button in category header
- [ ] Option to include original PDFs or JSON only
- [ ] Downloads zip file with results
- [ ] Verify in browser using browser tool

---

### US-024: Connection and Error Handling
**Description:** As a user, I want clear feedback when something goes wrong.

**Acceptance Criteria:**
- [ ] Toast notifications for success/error/warning states
- [ ] "Server Disconnected" banner when API unreachable
- [ ] Retry button on failed operations
- [ ] Loading spinners during API calls
- [ ] Verify in browser using browser tool

---

### US-025: Empty States and Onboarding
**Description:** As a new user, I want helpful guidance when starting.

**Acceptance Criteria:**
- [ ] Empty state for no categories: "Create your first category"
- [ ] Empty state for empty category: "Drop PDFs here to get started"
- [ ] Empty state for search: "No papers match your search"
- [ ] Quick start tips on first visit
- [ ] Verify in browser using browser tool

---

## Functional Requirements

- FR-1: Backend must use Flask and serve on `0.0.0.0:5000` for LAN access
- FR-2: All API endpoints return JSON with consistent error format
- FR-3: File processing runs in background threads, not blocking API
- FR-4: Frontend is vanilla HTML/CSS/JS (no build step required)
- FR-5: Frontend served as static files from `/frontend/` directory
- FR-6: Status derived from file existence (input PDF, markdown, JSON output)
- FR-7: All file operations validate paths to prevent directory traversal
- FR-8: Search indexes JSON content on-demand (no separate database)

## Non-Goals (Out of Scope)

- User authentication or access control (LAN = trusted network)
- Persistent database (file system is the source of truth)
- Real-time WebSocket updates (polling is sufficient for MVP)
- PDF preview rendering in browser
- Editing extracted JSON data
- Mobile-optimized layout (tablet minimum)
- Multiple concurrent processing queues

## Technical Considerations

- Backend: Flask with flask-cors for CORS support
- Frontend: Vanilla HTML, CSS (custom properties), JavaScript (ES6+)
- Static files: Served from `frontend/` directory
- Processing: Reuses existing `LocalPDFProcessor` class from `pdf_processor.py`
- Threading: Python `threading` module for background processing
- No additional database required - filesystem is source of truth
- Google Fonts: Inter or Outfit for modern typography

## Success Metrics

- Researchers can upload and process papers without using CLI
- Processing status visible without checking terminal
- Results searchable across all processed papers
- Full workflow (upload → process → view results) under 5 clicks
- Interface loads in under 2 seconds on LAN

## Open Questions

- Should we add a "settings" panel for configuring LLM backend (vLLM vs Ollama)?
- Should processing queue persist across server restarts?
- Should we add a markdown preview tab alongside JSON results?
