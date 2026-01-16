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

        uploadZone.addEventListener('dragleave', () => {
            uploadZone.classList.remove('dragover');
        });

        uploadZone.addEventListener('drop', (e) => {
            e.preventDefault();
            uploadZone.classList.remove('dragover');
            // Handle file drop - implemented in US-016
        });
    }
});

// Status Polling (placeholder - implemented in US-018)
console.log('Paper Pipeline Frontend initialized');
