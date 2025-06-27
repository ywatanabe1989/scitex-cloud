/**
 * Document Manager JavaScript Module
 * Handles CRUD operations for documents with API integration
 * Following clean code principles and TDD-driven design
 */

class DocumentManager {
    constructor() {
        this.apiBaseUrl = '/core/api/v1/documents/';
        this.currentDocument = null;
        this.documents = [];
        
        this.initializeEventListeners();
        this.loadDocuments();
    }
    
    /**
     * Initialize event listeners for document management
     */
    initializeEventListeners() {
        // Form submission
        const documentForm = document.getElementById('document-form');
        if (documentForm) {
            documentForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }
        
        // Search functionality
        const searchInput = document.getElementById('document-search');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => {
                this.handleSearch(e.target.value);
            });
        }
        
        // Filter by type
        const typeFilter = document.getElementById('document-type-filter');
        if (typeFilter) {
            typeFilter.addEventListener('change', (e) => {
                this.handleTypeFilter(e.target.value);
            });
        }
        
        // Document list event delegation
        const documentList = document.getElementById('document-list');
        if (documentList) {
            documentList.addEventListener('click', (e) => {
                if (e.target.classList.contains('edit-btn')) {
                    this.editDocument(e.target.dataset.id);
                } else if (e.target.classList.contains('delete-btn')) {
                    this.deleteDocument(e.target.dataset.id);
                } else if (e.target.classList.contains('view-btn')) {
                    this.viewDocument(e.target.dataset.id);
                }
            });
        }
    }
    
    /**
     * Load documents from API
     */
    async loadDocuments(params = {}) {
        try {
            this.showLoading(true);
            
            const queryString = new URLSearchParams(params).toString();
            const url = queryString ? `${this.apiBaseUrl}?${queryString}` : this.apiBaseUrl;
            
            const response = await fetch(url, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.documents = data.documents;
                this.renderDocumentList();
                this.renderPagination(data.pagination);
            } else {
                this.showError('Failed to load documents: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading documents: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    /**
     * Handle form submission for create/update
     */
    async handleFormSubmit() {
        try {
            const form = document.getElementById('document-form');
            const formData = new FormData(form);
            
            // Convert FormData to JSON
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Validate required fields
            if (!data.title?.trim()) {
                this.showError('Title is required');
                return;
            }
            
            if (!data.content?.trim()) {
                this.showError('Content is required');
                return;
            }
            
            const isUpdate = this.currentDocument !== null;
            const url = isUpdate 
                ? `${this.apiBaseUrl}${this.currentDocument.id}/`
                : this.apiBaseUrl;
            const method = isUpdate ? 'PUT' : 'POST';
            
            const response = await fetch(url, {
                method: method,
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify(data),
                credentials: 'same-origin'
            });
            
            const result = await response.json();
            
            if (result.success) {
                this.showSuccess(
                    isUpdate 
                        ? 'Document updated successfully!' 
                        : 'Document created successfully!'
                );
                this.resetForm();
                this.loadDocuments();
            } else {
                this.showError('Error saving document: ' + result.error);
            }
        } catch (error) {
            this.showError('Error saving document: ' + error.message);
        }
    }
    
    /**
     * Edit document - load into form
     */
    async editDocument(documentId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${documentId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentDocument = data.document;
                this.populateForm(data.document);
                this.scrollToForm();
            } else {
                this.showError('Error loading document: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading document: ' + error.message);
        }
    }
    
    /**
     * Delete document with confirmation
     */
    async deleteDocument(documentId) {
        if (!confirm('Are you sure you want to delete this document?')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}${documentId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Document deleted successfully!');
                this.loadDocuments();
            } else {
                this.showError('Error deleting document: ' + data.error);
            }
        } catch (error) {
            this.showError('Error deleting document: ' + error.message);
        }
    }
    
    /**
     * View document in modal or new page
     */
    viewDocument(documentId) {
        const document = this.documents.find(doc => doc.id == documentId);
        if (document) {
            // Create modal or navigate to view page
            this.showDocumentModal(document);
        }
    }
    
    /**
     * Handle search functionality
     */
    handleSearch(searchTerm) {
        clearTimeout(this.searchTimeout);
        this.searchTimeout = setTimeout(() => {
            this.loadDocuments({ search: searchTerm });
        }, 300); // Debounce search
    }
    
    /**
     * Handle type filtering
     */
    handleTypeFilter(documentType) {
        const params = {};
        if (documentType) {
            params.type = documentType;
        }
        this.loadDocuments(params);
    }
    
    /**
     * Render document list in DOM
     */
    renderDocumentList() {
        const container = document.getElementById('document-list');
        if (!container) return;
        
        if (this.documents.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No documents found. Create your first document!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.documents.map(doc => `
            <div class="document-item card" data-id="${doc.id}">
                <div class="document-header">
                    <h3 class="document-title">${this.escapeHtml(doc.title)}</h3>
                    <span class="document-type badge badge-${doc.document_type}">
                        ${doc.document_type}
                    </span>
                </div>
                <div class="document-content">
                    <p class="document-excerpt">
                        ${this.escapeHtml(doc.content.substring(0, 150))}${doc.content.length > 150 ? '...' : ''}
                    </p>
                    ${doc.tags_list.length > 0 ? `
                        <div class="document-tags">
                            ${doc.tags_list.map(tag => `
                                <span class="tag">${this.escapeHtml(tag)}</span>
                            `).join('')}
                        </div>
                    ` : ''}
                </div>
                <div class="document-meta">
                    <span class="document-date">
                        Updated: ${new Date(doc.updated_at).toLocaleDateString()}
                    </span>
                    ${doc.is_public ? '<span class="public-indicator">Public</span>' : ''}
                </div>
                <div class="document-actions">
                    <button class="btn btn-sm btn-primary view-btn" data-id="${doc.id}">
                        View
                    </button>
                    <button class="btn btn-sm btn-secondary edit-btn" data-id="${doc.id}">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-danger delete-btn" data-id="${doc.id}">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Render pagination controls
     */
    renderPagination(pagination) {
        const container = document.getElementById('pagination-container');
        if (!container || !pagination) return;
        
        container.innerHTML = `
            <div class="pagination">
                ${pagination.has_previous ? `
                    <button class="btn btn-outline-primary" onclick="documentManager.loadDocuments({page: ${pagination.current_page - 1}})">
                        Previous
                    </button>
                ` : ''}
                
                <span class="pagination-info">
                    Page ${pagination.current_page} of ${pagination.total_pages}
                    (${pagination.total_count} total)
                </span>
                
                ${pagination.has_next ? `
                    <button class="btn btn-outline-primary" onclick="documentManager.loadDocuments({page: ${pagination.current_page + 1}})">
                        Next
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Populate form with document data
     */
    populateForm(document) {
        const form = document.getElementById('document-form');
        if (!form) return;
        
        form.title.value = document.title;
        form.content.value = document.content;
        form.document_type.value = document.document_type;
        form.tags.value = document.tags;
        
        if (form.is_public) {
            form.is_public.checked = document.is_public;
        }
        
        // Update form title
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.textContent = 'Edit Document';
        }
        
        // Update submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Update Document';
        }
    }
    
    /**
     * Reset form to create mode
     */
    resetForm() {
        const form = document.getElementById('document-form');
        if (!form) return;
        
        form.reset();
        this.currentDocument = null;
        
        // Update form title
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.textContent = 'Create New Document';
        }
        
        // Update submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Create Document';
        }
    }
    
    /**
     * Show document in modal
     */
    showDocumentModal(document) {
        // Create modal dynamically
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${this.escapeHtml(document.title)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="document-meta mb-3">
                            <span class="badge badge-${document.document_type}">${document.document_type}</span>
                            <span class="text-muted">Updated: ${new Date(document.updated_at).toLocaleDateString()}</span>
                        </div>
                        <div class="document-content">
                            ${this.escapeHtml(document.content).replace(/\n/g, '<br>')}
                        </div>
                        ${document.tags_list.length > 0 ? `
                            <div class="document-tags mt-3">
                                <strong>Tags:</strong>
                                ${document.tags_list.map(tag => `
                                    <span class="tag">${this.escapeHtml(tag)}</span>
                                `).join('')}
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="documentManager.editDocument(${document.id}); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                            Edit Document
                        </button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Show modal (assuming Bootstrap 5)
        if (typeof bootstrap !== 'undefined') {
            const modalInstance = new bootstrap.Modal(modal);
            modalInstance.show();
            
            modal.addEventListener('hidden.bs.modal', () => {
                modal.remove();
            });
        }
    }
    
    /**
     * Utility functions
     */
    showSuccess(message) {
        this.showMessage(message, 'success');
    }
    
    showError(message) {
        this.showMessage(message, 'error');
    }
    
    showMessage(message, type) {
        const container = document.getElementById('status-message');
        if (!container) return;
        
        container.className = `status-message ${type}`;
        container.textContent = message;
        container.style.display = 'block';
        
        // Auto hide after 5 seconds
        setTimeout(() => {
            container.style.display = 'none';
        }, 5000);
    }
    
    showLoading(show) {
        const loader = document.getElementById('loading-indicator');
        if (loader) {
            loader.style.display = show ? 'block' : 'none';
        }
    }
    
    scrollToForm() {
        const form = document.getElementById('document-form');
        if (form) {
            form.scrollIntoView({ behavior: 'smooth' });
        }
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
}

// Initialize document manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.documentManager = new DocumentManager();
});