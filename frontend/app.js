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
                <span class="status-badge ${file.status}">${file.status}</span>
            </div>
            <div class="file-meta">
                ${formatFileSize(file.size)} • ${formatDate(file.upload_date)}
            </div>
        `;
        card.addEventListener('click', () => viewFileResults(file));
        card.addEventListener('contextmenu', (e) => showContextMenu(e, file));
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

// File Results
async function viewFileResults(file) {
    if (file.status !== 'completed') {
        showToast('File not yet processed', 'warning');
        return;
    }

    elements.resultsPanel.classList.remove('hidden');
    // Load and display results - implemented in US-019
}

// Context Menu
function showContextMenu(event, file) {
    event.preventDefault();
    const menu = document.getElementById('context-menu');
    menu.classList.remove('hidden');
    menu.style.left = `${event.clientX}px`;
    menu.style.top = `${event.clientY}px`;
    menu.dataset.fileId = file.id;
}

// Event Listeners
document.addEventListener('DOMContentLoaded', () => {
    loadCategories();
    startStatusPolling();

    // Hide context menu on click outside
    document.addEventListener('click', () => {
        document.getElementById('context-menu').classList.add('hidden');
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
    });

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
