/**
 * Paper Pipeline - Frontend Application
 * Placeholder JavaScript - Will be fully implemented in subsequent user stories
 */

// API Base URL
const API_BASE = '/api';

// DOM Elements
const elements = {
    // Header
    searchInput: document.getElementById('search-input'),
    processAllBtn: document.getElementById('process-all-btn'),
    settingsBtn: document.getElementById('settings-btn'),

    // Status Bar
    statusDot: document.getElementById('status-dot'),
    statusText: document.getElementById('status-text'),
    queueCount: document.getElementById('queue-count'),
    pauseBtn: document.getElementById('pause-btn'),
    cancelBtn: document.getElementById('cancel-btn'),

    // Sidebar
    categoryList: document.getElementById('category-list'),
    addCategoryBtn: document.getElementById('add-category-btn'),
    totalFilesCount: document.getElementById('total-files-count'),

    // Main Content
    currentCategoryName: document.getElementById('current-category-name'),
    fileCountBadge: document.getElementById('file-count-badge'),
    processCategoryBtn: document.getElementById('process-category-btn'),
    exportCategoryBtn: document.getElementById('export-category-btn'),
    uploadZone: document.getElementById('upload-zone'),
    fileInput: document.getElementById('file-input'),
    browseFilesBtn: document.getElementById('browse-files-btn'),
    fileGrid: document.getElementById('file-grid'),
    emptyStateFiles: document.getElementById('empty-state-files'),

    // Results Panel
    resultsPanel: document.getElementById('results-panel'),
    closePanelBtn: document.getElementById('close-panel-btn'),

    // Modals
    addCategoryModal: document.getElementById('add-category-modal'),
    categoryNameInput: document.getElementById('category-name-input'),
    createCategoryBtn: document.getElementById('create-category-btn'),
    cancelCategoryBtn: document.getElementById('cancel-category-btn'),

    // Toast Container
    toastContainer: document.getElementById('toast-container'),
};

// Application State
let state = {
    currentCategory: null,
    categories: [],
    files: [],
    selectedFiles: new Set(),
    isConnected: true,
    processingStatus: { status: 'idle', queue_length: 0 }
};

// Utility Functions
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `<span>${message}</span>`;
    elements.toastContainer.appendChild(toast);

    setTimeout(() => toast.remove(), 3000);
}

async function fetchAPI(endpoint, options = {}) {
    try {
        const response = await fetch(`${API_BASE}${endpoint}`, {
            headers: { 'Content-Type': 'application/json', ...options.headers },
            ...options
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        return response.json();
    } catch (error) {
        showToast(`API Error: ${error.message}`, 'error');
        throw error;
    }
}

// Categories
async function loadCategories() {
    try {
        const data = await fetchAPI('/categories');
        state.categories = data.categories || [];
        renderCategories();
        updateTotalFilesCount();
    } catch (error) {
        console.error('Failed to load categories:', error);
    }
}

// Search functionality
let searchDebounceTimer = null;
let currentSearchQuery = '';

function debounce(func, wait) {
    return function executedFunction(...args) {
        clearTimeout(searchDebounceTimer);
        searchDebounceTimer = setTimeout(() => func.apply(this, args), wait);
    };
}

async function performSearch(query) {
    if (!query || query.trim().length < 2) {
        hideSearchResults();
        return;
    }

    currentSearchQuery = query.trim();

    try {
        const data = await fetchAPI(`/search?q=${encodeURIComponent(currentSearchQuery)}`);
        const results = data.results || [];
        showSearchResults(results, currentSearchQuery);
    } catch (error) {
        console.error('Search failed:', error);
        showToast('Search failed', 'error');
    }
}

const debouncedSearch = debounce(performSearch, 300);

function showSearchResults(results, query) {
    const searchResultsSection = document.getElementById('search-results');
    const searchResultsList = document.getElementById('search-results-list');
    const queryDisplay = document.getElementById('search-query-display');
    const emptyStateSearch = document.getElementById('empty-state-search');
    const fileGridContainer = document.getElementById('file-grid-container');

    // Show search results section, hide file grid
    searchResultsSection.classList.remove('hidden');
    fileGridContainer.classList.add('hidden');

    // Update query display
    queryDisplay.textContent = `"${query}"`;

    if (results.length === 0) {
        searchResultsList.innerHTML = '';
        emptyStateSearch.classList.remove('hidden');
        return;
    }

    emptyStateSearch.classList.add('hidden');
    searchResultsList.innerHTML = '';

    results.forEach(result => {
        const card = document.createElement('div');
        card.className = 'search-result-card';
        card.dataset.fileId = result.file_id;

        // Highlight the query in snippets
        const highlightedSnippets = result.snippets
            .map(snippet => highlightText(snippet, query))
            .join(' ... ');

        card.innerHTML = `
            <div class="search-result-header">
                <span class="search-result-filename">${result.filename}</span>
                <span class="search-result-category">${result.category}</span>
            </div>
            <div class="search-result-snippets">${highlightedSnippets}</div>
            <div class="search-result-meta">
                <span class="search-result-matches">${result.match_count} match${result.match_count !== 1 ? 'es' : ''}</span>
            </div>
        `;

        // Click to navigate to results
        card.addEventListener('click', () => {
            // Create file object for viewFileResults
            const file = {
                id: result.file_id,
                filename: result.filename,
                category: result.category,
                status: 'completed' // Search only returns completed files
            };
            viewFileResults(file);
        });

        searchResultsList.appendChild(card);
    });
}

function highlightText(text, query) {
    if (!query) return escapeHtml(text);

    const escapedQuery = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const regex = new RegExp(`(${escapedQuery})`, 'gi');

    return escapeHtml(text).replace(regex, '<mark class="highlight">$1</mark>');
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function hideSearchResults() {
    const searchResultsSection = document.getElementById('search-results');
    const fileGridContainer = document.getElementById('file-grid-container');

    searchResultsSection.classList.add('hidden');
    fileGridContainer.classList.remove('hidden');
    currentSearchQuery = '';
}

function clearSearch() {
    if (elements.searchInput) {
        elements.searchInput.value = '';
    }
    hideSearchResults();
}

function renderCategories() {
    const list = elements.categoryList;
    list.innerHTML = '';

    if (state.categories.length === 0) {
        list.innerHTML = '<li class="empty-message" style="padding: 1rem; color: var(--color-text-secondary); text-align: center;">No categories yet</li>';
        return;
    }

    state.categories.forEach(cat => {
        const li = document.createElement('li');
        li.className = `category-item${state.currentCategory === cat.name ? ' active' : ''}`;
        li.innerHTML = `
            <span class="category-name">${cat.name}</span>
            <span class="category-badge">${cat.total_files || 0}</span>
        `;
        li.addEventListener('click', () => selectCategory(cat.name));
        list.appendChild(li);
    });
}

function updateTotalFilesCount() {
    const total = state.categories.reduce((sum, cat) => sum + (cat.total_files || 0), 0);
    elements.totalFilesCount.textContent = total;
}

async function selectCategory(name) {
    state.currentCategory = name;
    elements.currentCategoryName.textContent = name;
    elements.processCategoryBtn.disabled = false;
    elements.exportCategoryBtn.disabled = false;

    // Update file count badge from category data
    const category = state.categories.find(c => c.name === name);
    if (category) {
        elements.fileCountBadge.textContent = `${category.total_files || 0} files`;
    }

    renderCategories();
    await loadFiles(name);
}

// Files
async function loadFiles(category) {
    try {
        const data = await fetchAPI(`/categories/${category}/files`);
        state.files = data.files || [];
        renderFiles();
    } catch (error) {
        console.error('Failed to load files:', error);
    }
}

function renderFiles() {
    const grid = elements.fileGrid;
    grid.innerHTML = '';

    if (state.files.length === 0) {
        elements.emptyStateFiles.classList.remove('hidden');
        return;
    }

    elements.emptyStateFiles.classList.add('hidden');

    state.files.forEach(file => {
        const card = document.createElement('div');
        card.className = 'file-card';
        card.dataset.fileId = file.id;
        card.innerHTML = `
            <div class="file-card-header">
                <span class="file-name">${file.filename}</span>
                <div class="file-card-actions">
                    <span class="status-badge ${file.status}">${file.status}</span>
                    <button class="btn btn-icon btn-small file-menu-btn" aria-label="File menu">
                        <span class="icon">⋮</span>
                    </button>
                </div>
            </div>
            <div class="file-meta">
                ${formatFileSize(file.size)} • ${formatDate(file.upload_date)}
            </div>
        `;

        // Click on card to view results
        card.addEventListener('click', (e) => {
            // Don't trigger if clicking the menu button
            if (!e.target.closest('.file-menu-btn')) {
                viewFileResults(file);
            }
        });

        // Right-click for context menu
        card.addEventListener('contextmenu', (e) => showContextMenu(e, file));

        // Menu button click (for touch devices)
        const menuBtn = card.querySelector('.file-menu-btn');
        menuBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            showContextMenu(e, file);
        });

        grid.appendChild(card);
    });
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + ' B';
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB';
    return (bytes / (1024 * 1024)).toFixed(1) + ' MB';
}

function formatDate(isoString) {
    return new Date(isoString).toLocaleDateString();
}

// File Results - Current file data for panel actions
let currentPanelFile = null;
let currentPanelData = null;

async function viewFileResults(file) {
    if (file.status !== 'completed') {
        showToast('File not yet processed', 'warning');
        return;
    }

    // Show loading state
    elements.resultsPanel.classList.remove('hidden');
    document.getElementById('results-title').textContent = 'Loading...';

    try {
        // Fetch the JSON results
        const response = await fetchAPI(`/results/${file.id}`);

        // The API returns { file_id, filename, category, results: {...} }
        // The actual JSON content is in the 'results' field
        const data = response.results || response;

        // Store for panel actions (copy/download)
        currentPanelFile = file;
        currentPanelData = data;

        // Populate the panel
        renderResultsPanel(data, file);
    } catch (error) {
        console.error('Failed to load results:', error);
        showToast('Failed to load results', 'error');
        elements.resultsPanel.classList.add('hidden');
    }
}

function renderResultsPanel(data, file) {
    // Set panel title
    document.getElementById('results-title').textContent = file.filename;

    // Handle nested structure: data.metadata.title OR flat data.title
    const metadata = data.metadata || {};

    // Title - check nested metadata first, then flat
    const title = metadata.title || data.title || '-';
    document.getElementById('result-title').textContent = title;

    // Authors - handle nested metadata, array or string
    const authors = metadata.authors || data.authors;
    if (Array.isArray(authors)) {
        document.getElementById('result-authors').textContent = authors.join(', ') || '-';
    } else {
        document.getElementById('result-authors').textContent = authors || '-';
    }

    // Year - handle various formats and nested structure
    const year = metadata.year || metadata.publication_year || data.year || data.publication_year || data.date;
    document.getElementById('result-year').textContent = year || '-';

    // Venue - handle nested structure and various field names
    const venue = metadata.publication_venue || metadata.venue || metadata.journal || metadata.conference ||
        data.venue || data.journal || data.conference || data.publication;
    document.getElementById('result-venue').textContent = venue || '-';

    // Keywords as tags - can be at top level
    const keywordsContainer = document.getElementById('result-keywords');
    keywordsContainer.innerHTML = '';
    const keywords = data.keywords || metadata.keywords || [];
    if (Array.isArray(keywords) && keywords.length > 0) {
        keywords.forEach(keyword => {
            const tag = document.createElement('span');
            tag.className = 'tag';
            tag.textContent = keyword;
            keywordsContainer.appendChild(tag);
        });
    } else {
        keywordsContainer.innerHTML = '<span class="no-data">No keywords</span>';
    }

    // Summary - handle nested structure: data.summary can be an object with fields
    const summaryObj = data.summary || {};
    let summary;
    if (typeof summaryObj === 'object' && summaryObj !== null) {
        // Combine relevant summary fields
        const parts = [];
        if (summaryObj.problem_statement) parts.push(summaryObj.problem_statement);
        if (summaryObj.objective) parts.push('Objective: ' + summaryObj.objective);
        if (summaryObj.key_contribution) parts.push('Key Contribution: ' + summaryObj.key_contribution);
        summary = parts.length > 0 ? parts.join('\n\n') : null;
    } else {
        summary = summaryObj;
    }
    document.getElementById('result-summary').textContent = summary || data.abstract || '-';

    // Methodology - handle nested structure
    const methodologyObj = data.methodology || {};
    let methodology;
    if (typeof methodologyObj === 'object' && methodologyObj !== null) {
        methodology = methodologyObj.method_summary || methodologyObj.approach_type || null;
    } else {
        methodology = methodologyObj;
    }
    document.getElementById('result-methodology').textContent = methodology || data.methods || '-';

    // Key Findings - handle nested structure: data.results_and_evaluation.key_findings
    const findingsContainer = document.getElementById('result-findings');
    findingsContainer.innerHTML = '';
    const resultsEval = data.results_and_evaluation || {};
    const findings = resultsEval.key_findings || data.key_findings || data.findings || data.conclusions || [];
    if (Array.isArray(findings) && findings.length > 0) {
        findings.forEach(finding => {
            const li = document.createElement('li');
            li.textContent = finding;
            findingsContainer.appendChild(li);
        });
    } else if (typeof findings === 'string' && findings) {
        const li = document.createElement('li');
        li.textContent = findings;
        findingsContainer.appendChild(li);
    } else {
        findingsContainer.innerHTML = '<li class="no-data">No findings available</li>';
    }
}

function copyJsonToClipboard() {
    if (!currentPanelData) {
        showToast('No data to copy', 'warning');
        return;
    }

    const jsonStr = JSON.stringify(currentPanelData, null, 2);
    navigator.clipboard.writeText(jsonStr).then(() => {
        showToast('JSON copied to clipboard', 'success');
    }).catch(err => {
        console.error('Failed to copy:', err);
        showToast('Failed to copy to clipboard', 'error');
    });
}

function downloadJson() {
    if (!currentPanelData || !currentPanelFile) {
        showToast('No data to download', 'warning');
        return;
    }

    const jsonStr = JSON.stringify(currentPanelData, null, 2);
    const blob = new Blob([jsonStr], { type: 'application/json' });
    const url = URL.createObjectURL(blob);

    const a = document.createElement('a');
    a.href = url;
    // Use filename without extension + .json
    const baseName = currentPanelFile.filename.replace(/\.pdf$/i, '');
    a.download = `${baseName}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    showToast('JSON downloaded', 'success');
}

// Context Menu
let currentContextFile = null;

function showContextMenu(event, file) {
    event.preventDefault();
    event.stopPropagation();

    currentContextFile = file;

    const menu = document.getElementById('context-menu');
    menu.classList.remove('hidden');

    // Position menu, ensuring it doesn't go off-screen
    let x = event.clientX;
    let y = event.clientY;

    // Adjust if menu would go off right edge
    const menuWidth = 200;
    if (x + menuWidth > window.innerWidth) {
        x = window.innerWidth - menuWidth - 10;
    }

    // Adjust if menu would go off bottom edge
    const menuHeight = 280;
    if (y + menuHeight > window.innerHeight) {
        y = window.innerHeight - menuHeight - 10;
    }

    menu.style.left = `${x}px`;
    menu.style.top = `${y}px`;
    menu.dataset.fileId = file.id;

    // Update menu items based on file status
    updateContextMenuItems(file);
}

function updateContextMenuItems(file) {
    const viewBtn = document.querySelector('[data-action="view"]');
    const downloadJsonBtn = document.querySelector('[data-action="download-json"]');

    // Disable view and download JSON for non-completed files
    if (file.status !== 'completed') {
        viewBtn?.classList.add('disabled');
        downloadJsonBtn?.classList.add('disabled');
    } else {
        viewBtn?.classList.remove('disabled');
        downloadJsonBtn?.classList.remove('disabled');
    }
}

function hideContextMenu() {
    document.getElementById('context-menu').classList.add('hidden');
    currentContextFile = null;
}

// Context Menu Action Handlers
async function handleContextMenuAction(action) {
    if (!currentContextFile) {
        showToast('No file selected', 'warning');
        return;
    }

    const file = currentContextFile;
    hideContextMenu();

    switch (action) {
        case 'view':
            viewFileResults(file);
            break;
        case 'process':
            await processFile(file.id);
            break;
        case 'reprocess':
            await reprocessFile(file.id);
            break;
        case 'download-json':
            await downloadFileJson(file.id, file.filename);
            break;
        case 'download-pdf':
            downloadFilePdf(file.id, file.filename);
            break;
        case 'delete':
            showDeleteConfirmModal(file);
            break;
        default:
            console.warn('Unknown context menu action:', action);
    }
}

async function reprocessFile(fileId) {
    try {
        const result = await fetchAPI(`/files/${fileId}/reprocess`, { method: 'POST' });
        showToast('File queued for reprocessing', 'success');
        // Refresh the file list
        if (state.currentCategory) {
            await loadFiles(state.currentCategory);
        }
        return result;
    } catch (error) {
        showToast('Failed to reprocess file', 'error');
        throw error;
    }
}

async function downloadFileJson(fileId, filename) {
    try {
        const response = await fetch(`${API_BASE}/results/${fileId}/raw`);

        if (!response.ok) {
            if (response.status === 404) {
                showToast('File not yet processed', 'warning');
            } else {
                showToast('Failed to download JSON', 'error');
            }
            return;
        }

        const blob = await response.blob();
        const url = URL.createObjectURL(blob);

        const a = document.createElement('a');
        a.href = url;
        a.download = filename.replace(/\.pdf$/i, '.json');
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);

        showToast('JSON downloaded', 'success');
    } catch (error) {
        console.error('Download JSON error:', error);
        showToast('Failed to download JSON', 'error');
    }
}

function downloadFilePdf(fileId, filename) {
    // Trigger direct download via browser
    const a = document.createElement('a');
    a.href = `${API_BASE}/files/${fileId}/pdf`;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);

    showToast('PDF download started', 'info');
}

// Delete Confirmation Modal
let pendingDeleteFile = null;

function showDeleteConfirmModal(file) {
    pendingDeleteFile = file;

    const modal = document.getElementById('delete-confirm-modal');
    const confirmText = document.getElementById('delete-confirm-text');

    confirmText.textContent = `Are you sure you want to delete "${file.filename}"? This will remove the PDF and all associated output files. This action cannot be undone.`;

    modal.classList.remove('hidden');
}

function hideDeleteConfirmModal() {
    document.getElementById('delete-confirm-modal').classList.add('hidden');
    pendingDeleteFile = null;
}

async function confirmDelete() {
    if (!pendingDeleteFile) {
        hideDeleteConfirmModal();
        return;
    }

    const file = pendingDeleteFile;
    hideDeleteConfirmModal();

    try {
        await fetchAPI(`/files/${file.id}`, { method: 'DELETE' });
        showToast(`"${file.filename}" deleted successfully`, 'success');

        // Refresh the file list and categories
        if (state.currentCategory) {
            await loadFiles(state.currentCategory);
            await loadCategories();
        }
    } catch (error) {
        showToast('Failed to delete file', 'error');
    }
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    startStatusPolling();

    // Hide context menu on click outside
    document.addEventListener('click', () => {
        document.getElementById('context-menu').classList.add('hidden');
    });

    // Search input with instant debounced search
    elements.searchInput?.addEventListener('input', (e) => {
        debouncedSearch(e.target.value);
    });

    // Clear search on Escape key
    elements.searchInput?.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') {
            clearSearch();
        }
    });

    // Search button click (for explicit search)
    document.getElementById('search-btn')?.addEventListener('click', () => {
        performSearch(elements.searchInput?.value || '');
    });

    // Add Category Modal
    elements.addCategoryBtn?.addEventListener('click', () => {
        elements.addCategoryModal.classList.remove('hidden');
    });

    elements.cancelCategoryBtn?.addEventListener('click', () => {
        elements.addCategoryModal.classList.add('hidden');
    });

    elements.createCategoryBtn?.addEventListener('click', async () => {
        const name = elements.categoryNameInput.value.trim();
        if (!name) return;

        try {
            await fetchAPI('/categories', {
                method: 'POST',
                body: JSON.stringify({ name })
            });
            showToast(`Category "${name}" created`, 'success');
            elements.addCategoryModal.classList.add('hidden');
            elements.categoryNameInput.value = '';
            await loadCategories();
        } catch (error) {
            showToast('Failed to create category', 'error');
        }
    });

    // Close modals on overlay click
    document.querySelectorAll('.modal-overlay').forEach(overlay => {
        overlay.addEventListener('click', (e) => {
            if (e.target === overlay) {
                overlay.classList.add('hidden');
            }
        });
    });

    // Close modals on X button
    document.querySelectorAll('.modal-close').forEach(btn => {
        btn.addEventListener('click', () => {
            btn.closest('.modal-overlay').classList.add('hidden');
        });
    });

    // Browse files button
    elements.browseFilesBtn?.addEventListener('click', () => {
        elements.fileInput.click();
    });

    // File input change handler
    elements.fileInput?.addEventListener('change', (e) => {
        if (e.target.files.length > 0) {
            handleFileUpload(Array.from(e.target.files));
            e.target.value = ''; // Reset input for future uploads
        }
    });

    // Close results panel
    elements.closePanelBtn?.addEventListener('click', () => {
        elements.resultsPanel.classList.add('hidden');
        currentPanelFile = null;
        currentPanelData = null;
    });

    // Copy JSON button
    document.getElementById('copy-json-btn')?.addEventListener('click', copyJsonToClipboard);

    // Download JSON button
    document.getElementById('download-json-btn')?.addEventListener('click', downloadJson);

    // Upload zone drag and drop
    const uploadZone = elements.uploadZone;
    if (uploadZone) {
        uploadZone.addEventListener('dragover', (e) => {
            e.preventDefault();
            uploadZone.classList.add('dragover');
        });

        uploadZone.addEventListener('dragleave', (e) => {
            // Only remove dragover if leaving the upload zone entirely
            if (!uploadZone.contains(e.relatedTarget)) {
                uploadZone.classList.remove('dragover');
            }
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            const files = Array.from(e.dataTransfer.files);
            handleFileUpload(files);
        });
    }

    // Processing Controls
    // Process All button in header
    elements.processAllBtn?.addEventListener('click', () => {
        processAll();
    });

    // Process Category button
    elements.processCategoryBtn?.addEventListener('click', () => {
        if (state.currentCategory) {
            processCategory(state.currentCategory);
        }
    });

    // Pause/Resume button (toggle based on current state)
    elements.pauseBtn?.addEventListener('click', () => {
        if (state.processingStatus.status === 'paused') {
            resumeProcessing();
        } else {
            pauseProcessing();
        }
    });

    // Cancel button
    elements.cancelBtn?.addEventListener('click', () => {
        cancelProcessing();
    });

    // Batch Process Selected button
    document.getElementById('batch-process-btn')?.addEventListener('click', () => {
        processSelectedFiles();
    });

    // Context Menu Items
    document.querySelectorAll('.context-menu-item').forEach(item => {
        item.addEventListener('click', (e) => {
            e.stopPropagation();
            const action = item.dataset.action;
            if (action && !item.classList.contains('disabled')) {
                handleContextMenuAction(action);
            }
        });
    });

    // Also add a menu button to each file card (for mobile/touch devices)
    // This is handled dynamically in renderFiles()

    // Delete Confirmation Modal
    document.getElementById('cancel-delete-btn')?.addEventListener('click', () => {
        hideDeleteConfirmModal();
    });

    document.getElementById('confirm-delete-btn')?.addEventListener('click', () => {
        confirmDelete();
    });
});

// File Upload Functions
function validatePdfFile(file) {
    // Check extension
    const ext = file.name.toLowerCase().split('.').pop();
    if (ext !== 'pdf') {
        return { valid: false, error: `"${file.name}" is not a PDF file` };
    }

    // Check MIME type (allow octet-stream as fallback)
    const validMimeTypes = ['application/pdf', 'application/octet-stream'];
    if (!validMimeTypes.includes(file.type) && file.type !== '') {
        return { valid: false, error: `"${file.name}" has invalid MIME type: ${file.type}` };
    }

    // Check size (100MB limit)
    const maxSize = 100 * 1024 * 1024;
    if (file.size > maxSize) {
        return { valid: false, error: `"${file.name}" exceeds 100MB limit` };
    }

    return { valid: true };
}

async function handleFileUpload(files) {
    if (!state.currentCategory) {
        showToast('Please select a category first', 'warning');
        return;
    }

    // Filter and validate PDF files
    const pdfFiles = [];
    const errors = [];

    for (const file of files) {
        const validation = validatePdfFile(file);
        if (validation.valid) {
            pdfFiles.push(file);
        } else {
            errors.push(validation.error);
        }
    }

    // Show validation errors
    if (errors.length > 0) {
        errors.forEach(err => showToast(err, 'error'));
    }

    if (pdfFiles.length === 0) {
        return;
    }

    // Upload each file with progress tracking
    let successCount = 0;
    let failCount = 0;

    for (const file of pdfFiles) {
        try {
            await uploadFile(file, state.currentCategory);
            successCount++;
        } catch (error) {
            failCount++;
            showToast(`Failed to upload "${file.name}": ${error.message}`, 'error');
        }
    }

    // Show summary toast
    if (successCount > 0) {
        showToast(`Uploaded ${successCount} file${successCount > 1 ? 's' : ''} successfully`, 'success');
    }

    // Refresh file list and categories
    await loadFiles(state.currentCategory);
    await loadCategories();
}

function uploadFile(file, category) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();
        formData.append('file', file);

        const xhr = new XMLHttpRequest();

        // Show upload progress in upload zone
        const uploadZone = elements.uploadZone;
        const originalContent = uploadZone.innerHTML;

        xhr.upload.addEventListener('progress', (e) => {
            if (e.lengthComputable) {
                const percent = Math.round((e.loaded / e.total) * 100);
                uploadZone.innerHTML = `
                    <div class="upload-progress">
                        <span class="upload-icon">📤</span>
                        <p class="upload-text">Uploading ${file.name}</p>
                        <div class="progress-bar">
                            <div class="progress-fill" style="width: ${percent}%"></div>
                        </div>
                        <p class="upload-hint">${percent}%</p>
                    </div>
                `;
            }
        });

        xhr.addEventListener('load', () => {
            uploadZone.innerHTML = originalContent;
            // Re-attach browse button event
            const browseBtn = uploadZone.querySelector('#browse-files-btn');
            if (browseBtn) {
                browseBtn.addEventListener('click', () => elements.fileInput.click());
            }

            if (xhr.status >= 200 && xhr.status < 300) {
                resolve(JSON.parse(xhr.responseText));
            } else {
                let errorMsg = 'Upload failed';
                try {
                    const response = JSON.parse(xhr.responseText);
                    errorMsg = response.error || errorMsg;
                } catch (e) { }
                reject(new Error(errorMsg));
            }
        });

        xhr.addEventListener('error', () => {
            uploadZone.innerHTML = originalContent;
            const browseBtn = uploadZone.querySelector('#browse-files-btn');
            if (browseBtn) {
                browseBtn.addEventListener('click', () => elements.fileInput.click());
            }
            reject(new Error('Network error'));
        });

        xhr.open('POST', `${API_BASE}/categories/${category}/upload`);
        xhr.send(formData);
    });
}

// Processing Controls
async function processAll() {
    try {
        const result = await fetchAPI('/process/all', { method: 'POST' });
        showToast('Processing started for all pending files', 'success');
        return result;
    } catch (error) {
        showToast('Failed to start processing', 'error');
        throw error;
    }
}

async function processCategory(categoryName) {
    if (!categoryName) {
        showToast('No category selected', 'warning');
        return;
    }

    try {
        const result = await fetchAPI(`/process/category/${categoryName}`, { method: 'POST' });
        showToast(`Processing started for category "${categoryName}"`, 'success');
        return result;
    } catch (error) {
        showToast('Failed to start category processing', 'error');
        throw error;
    }
}

async function processFile(fileId) {
    try {
        const result = await fetchAPI(`/process/file/${fileId}`, { method: 'POST' });
        showToast('Processing started', 'success');
        return result;
    } catch (error) {
        showToast('Failed to start file processing', 'error');
        throw error;
    }
}

async function pauseProcessing() {
    try {
        await fetchAPI('/process/pause', { method: 'POST' });
        showToast('Processing paused', 'info');
        updateProcessingUI({ status: 'paused' });
    } catch (error) {
        showToast('Failed to pause processing', 'error');
    }
}

async function resumeProcessing() {
    try {
        await fetchAPI('/process/resume', { method: 'POST' });
        showToast('Processing resumed', 'success');
        updateProcessingUI({ status: 'running' });
    } catch (error) {
        showToast('Failed to resume processing', 'error');
    }
}

async function cancelProcessing() {
    try {
        await fetchAPI('/process/cancel', { method: 'POST' });
        showToast('Processing cancelled', 'warning');
        updateProcessingUI({ status: 'idle', queue_length: 0 });
    } catch (error) {
        showToast('Failed to cancel processing', 'error');
    }
}

function updateProcessingUI(status) {
    state.processingStatus = { ...state.processingStatus, ...status };
    const { status: procStatus, queue_length } = state.processingStatus;

    // Update status indicator
    const statusDot = elements.statusDot;
    const statusText = elements.statusText;

    // Remove all status classes
    statusDot.className = 'status-dot';

    if (procStatus === 'running') {
        statusDot.classList.add('running');
        let statusMessage = 'Processing...';
        if (state.processingStatus.current_file) {
            const phase = state.processingStatus.current_phase;
            const phaseText = phase ? ` (Phase ${phase})` : '';
            statusMessage = `Processing: ${state.processingStatus.current_file}${phaseText}`;
        }
        statusText.textContent = statusMessage;
        elements.pauseBtn.disabled = false;
        elements.pauseBtn.innerHTML = '<span class="icon">⏸️</span> Pause';
        elements.cancelBtn.disabled = false;
    } else if (procStatus === 'paused') {
        statusDot.classList.add('paused');
        statusText.textContent = 'Paused';
        elements.pauseBtn.disabled = false;
        elements.pauseBtn.innerHTML = '<span class="icon">▶️</span> Resume';
        elements.cancelBtn.disabled = false;
    } else {
        statusDot.classList.add('idle');
        statusText.textContent = 'Idle';
        elements.pauseBtn.disabled = true;
        elements.pauseBtn.innerHTML = '<span class="icon">⏸️</span> Pause';
        elements.cancelBtn.disabled = true;
    }

    // Update queue count
    elements.queueCount.textContent = queue_length || 0;
}

// Process Selected Files (batch)
async function processSelectedFiles() {
    if (state.selectedFiles.size === 0) {
        showToast('No files selected', 'warning');
        return;
    }

    let successCount = 0;
    let failCount = 0;

    for (const fileId of state.selectedFiles) {
        try {
            await fetchAPI(`/process/file/${fileId}`, { method: 'POST' });
            successCount++;
        } catch (error) {
            failCount++;
        }
    }

    if (successCount > 0) {
        showToast(`Queued ${successCount} file${successCount > 1 ? 's' : ''} for processing`, 'success');
    }
    if (failCount > 0) {
        showToast(`Failed to queue ${failCount} file${failCount > 1 ? 's' : ''}`, 'error');
    }

    state.selectedFiles.clear();
    updateBatchActionBar();
}

// Batch Action Bar
function updateBatchActionBar() {
    const bar = document.getElementById('batch-action-bar');
    const selectedCount = document.getElementById('selected-count');
    const selectAllCheckbox = document.getElementById('select-all-checkbox');

    if (state.selectedFiles.size > 0) {
        bar.classList.remove('hidden');
        selectedCount.textContent = state.selectedFiles.size;
    } else {
        bar.classList.add('hidden');
    }

    // Update select all checkbox state
    if (selectAllCheckbox && state.files.length > 0) {
        selectAllCheckbox.checked = state.selectedFiles.size === state.files.length;
        selectAllCheckbox.indeterminate = state.selectedFiles.size > 0 && state.selectedFiles.size < state.files.length;
    }
}

// Status Polling
let statusPollInterval = null;

async function fetchStatus() {
    try {
        const response = await fetch(`${API_BASE}/status`);
        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }
        const status = await response.json();
        updateProcessingUI(status);

        // Refresh file list if status changed to idle (processing completed)
        if (state.processingStatus.status === 'running' && status.status === 'idle') {
            if (state.currentCategory) {
                await loadFiles(state.currentCategory);
                await loadCategories();
            }
        }

        state.isConnected = true;
        hideConnectionBanner();
    } catch (error) {
        state.isConnected = false;
        showConnectionBanner();
    }
}

function startStatusPolling() {
    // Clear any existing interval
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
    }

    // Fetch immediately
    fetchStatus();

    // Poll every 2 seconds
    statusPollInterval = setInterval(fetchStatus, 2000);
}

function stopStatusPolling() {
    if (statusPollInterval) {
        clearInterval(statusPollInterval);
        statusPollInterval = null;
    }
}

function showConnectionBanner() {
    const banner = document.getElementById('connection-banner');
    if (banner) {
        banner.classList.remove('hidden');
    }
}

function hideConnectionBanner() {
    const banner = document.getElementById('connection-banner');
    if (banner) {
        banner.classList.add('hidden');
    }
}

console.log('Paper Pipeline Frontend initialized');
