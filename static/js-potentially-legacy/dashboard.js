// SciTeX Cloud Dashboard JavaScript
// Enhanced document management functionality

class DocumentManager {
    constructor() {
        this.apiBase = '/core/api/v1';
        this.init();
    }

    init() {
        this.bindEvents();
        this.loadUserStats();
    }

    bindEvents() {
        // Bind create document button
        document.addEventListener('click', (e) => {
            if (e.target.matches('[data-action="create-document"]')) {
                this.showCreateDocumentModal();
            }
            
            if (e.target.matches('[data-action="edit-document"]')) {
                const docId = e.target.dataset.docId;
                this.editDocument(docId);
            }
            
            if (e.target.matches('[data-action="delete-document"]')) {
                const docId = e.target.dataset.docId;
                this.deleteDocument(docId);
            }
        });
    }

    async loadUserStats() {
        try {
            const response = await fetch(`${this.apiBase}/stats/`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            
            if (response.ok) {
                const data = await response.json();
                this.updateStatsDisplay(data.stats);
            }
        } catch (error) {
            console.error('Error loading user stats:', error);
        }
    }

    updateStatsDisplay(stats) {
        // Update statistics cards if they exist
        const statElements = {
            'total-documents': stats.document_count,
            'total-projects': stats.project_count
        };

        Object.entries(statElements).forEach(([id, value]) => {
            const element = document.getElementById(id);
            if (element) {
                element.textContent = value;
            }
        });
    }

    showCreateDocumentModal() {
        // Create a simple modal for document creation
        const modal = this.createModal('Create New Document', `
            <form id="create-document-form">
                <div class="mb-3">
                    <label for="doc-title" class="form-label">Title</label>
                    <input type="text" class="form-control" id="doc-title" required>
                </div>
                <div class="mb-3">
                    <label for="doc-type" class="form-label">Type</label>
                    <select class="form-select" id="doc-type">
                        <option value="note">Note</option>
                        <option value="paper">Research Paper</option>
                        <option value="project">Project</option>
                        <option value="draft">Draft</option>
                    </select>
                </div>
                <div class="mb-3">
                    <label for="doc-content" class="form-label">Content</label>
                    <textarea class="form-control" id="doc-content" rows="4" placeholder="Start writing..."></textarea>
                </div>
                <div class="mb-3">
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="doc-public">
                        <label class="form-check-label" for="doc-public">
                            Make this document public
                        </label>
                    </div>
                </div>
            </form>
        `, [
            {
                text: 'Cancel',
                class: 'btn-secondary',
                action: () => this.closeModal()
            },
            {
                text: 'Create Document',
                class: 'btn-primary',
                action: () => this.createDocument()
            }
        ]);

        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
    }

    async createDocument() {
        const form = document.getElementById('create-document-form');
        const formData = new FormData(form);
        
        const documentData = {
            title: document.getElementById('doc-title').value,
            document_type: document.getElementById('doc-type').value,
            content: document.getElementById('doc-content').value,
            is_public: document.getElementById('doc-public').checked
        };

        try {
            const response = await fetch(`${this.apiBase}/documents/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCsrfToken()
                },
                body: JSON.stringify(documentData)
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification('Document created successfully!', 'success');
                this.closeModal();
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification(result.error || 'Error creating document', 'error');
            }
        } catch (error) {
            console.error('Error creating document:', error);
            this.showNotification('Error creating document', 'error');
        }
    }

    async deleteDocument(docId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }

        try {
            const response = await fetch(`${this.apiBase}/documents/${docId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCsrfToken()
                }
            });

            const result = await response.json();

            if (response.ok && result.success) {
                this.showNotification('Document deleted successfully!', 'success');
                setTimeout(() => location.reload(), 1000);
            } else {
                this.showNotification(result.error || 'Error deleting document', 'error');
            }
        } catch (error) {
            console.error('Error deleting document:', error);
            this.showNotification('Error deleting document', 'error');
        }
    }

    createModal(title, content, buttons = []) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.tabIndex = -1;
        
        const buttonHtml = buttons.map(btn => 
            `<button type="button" class="btn ${btn.class}" data-action="${btn.action.name}">${btn.text}</button>`
        ).join('');

        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${title}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        ${content}
                    </div>
                    <div class="modal-footer">
                        ${buttonHtml}
                    </div>
                </div>
            </div>
        `;

        // Bind button actions
        buttons.forEach(btn => {
            modal.querySelector(`[data-action="${btn.action.name}"]`).onclick = btn.action;
        });

        return modal;
    }

    closeModal() {
        const modal = document.querySelector('.modal.show');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            bsModal.hide();
            setTimeout(() => modal.remove(), 300);
        }
    }

    showNotification(message, type = 'info') {
        // Create toast notification
        const toast = document.createElement('div');
        toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
        toast.setAttribute('role', 'alert');
        
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">
                    ${message}
                </div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
            </div>
        `;

        // Add to toast container or create one
        let container = document.querySelector('.toast-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }

        container.appendChild(toast);
        
        const bsToast = new bootstrap.Toast(toast);
        bsToast.show();

        // Remove after hiding
        toast.addEventListener('hidden.bs.toast', () => {
            toast.remove();
        });
    }

    getCsrfToken() {
        const cookies = document.cookie.split(';');
        for (let cookie of cookies) {
            const [name, value] = cookie.trim().split('=');
            if (name === 'csrftoken') {
                return decodeURIComponent(value);
            }
        }
        return '';
    }
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    new DocumentManager();
});

// Global functions for backward compatibility
function createNewDocument() {
    document.dispatchEvent(new CustomEvent('click', {
        target: { matches: () => true, dataset: { action: 'create-document' } }
    }));
}

function createNewProject() {
    window.location.href = '/core/projects/';
}

function copyProject(projectId, projectName) {
    if (!projectId) {
        console.error('Project ID is required for copying');
        return;
    }
    
    const newName = prompt(`Enter a name for the copy of "${projectName}":`, `${projectName} (Copy)`);
    if (!newName) {
        return; // User cancelled
    }
    
    // Show loading state
    const button = event.target;
    const originalText = button.textContent;
    button.textContent = 'Copying...';
    button.disabled = true;
    
    fetch(`/core/api/v1/projects/${projectId}/copy/`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': getCsrfToken()
        },
        body: JSON.stringify({ name: newName })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'success') {
            showNotification(data.message, 'success');
            setTimeout(() => location.reload(), 1000);
        } else {
            showNotification(data.message || 'Error copying project', 'error');
        }
    })
    .catch(error => {
        console.error('Error copying project:', error);
        showNotification('Error copying project', 'error');
    })
    .finally(() => {
        button.textContent = originalText;
        button.disabled = false;
    });
}

function getCsrfToken() {
    const cookies = document.cookie.split(';');
    for (let cookie of cookies) {
        const [name, value] = cookie.trim().split('=');
        if (name === 'csrftoken') {
            return decodeURIComponent(value);
        }
    }
    return '';
}

function showNotification(message, type = 'info') {
    // Create toast notification
    const toast = document.createElement('div');
    toast.className = `toast align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'success' ? 'success' : 'primary'} border-0`;
    toast.setAttribute('role', 'alert');
    
    toast.innerHTML = `
        <div class="d-flex">
            <div class="toast-body">
                ${message}
            </div>
            <button type="button" class="btn-close btn-close-white me-2 m-auto" data-bs-dismiss="toast"></button>
        </div>
    `;

    // Add to toast container or create one
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container position-fixed top-0 end-0 p-3';
        document.body.appendChild(container);
    }

    container.appendChild(toast);
    
    const bsToast = new bootstrap.Toast(toast);
    bsToast.show();

    // Remove after hiding
    toast.addEventListener('hidden.bs.toast', () => {
        toast.remove();
    });
}

function editDocument(docId) {
    alert('Advanced document editor coming soon!');
}

function shareDocument(docId) {
    alert('Document sharing feature coming soon!');
}

function deleteDocument(docId) {
    document.dispatchEvent(new CustomEvent('click', {
        target: { matches: () => true, dataset: { action: 'delete-document', docId: docId } }
    }));
}

function showProfile() {
    window.location.href = '/core/profile/';
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        // In a real app, this would make a logout API call
        alert('Logout functionality will be implemented with proper session management.');
    }
}