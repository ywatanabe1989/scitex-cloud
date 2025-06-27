/**
 * Project Manager JavaScript Module
 * Handles CRUD operations for projects with API integration
 * Following clean code principles and TDD-driven design
 */

class ProjectManager {
    constructor() {
        this.apiBaseUrl = '/core/api/v1/projects/';
        this.currentProject = null;
        this.projects = [];
        
        this.initializeEventListeners();
        this.loadProjects();
    }
    
    /**
     * Initialize event listeners for project management
     */
    initializeEventListeners() {
        // Form submission
        const projectForm = document.getElementById('project-form');
        if (projectForm) {
            projectForm.addEventListener('submit', (e) => {
                e.preventDefault();
                this.handleFormSubmit();
            });
        }
        
        // Filter by status
        const statusFilter = document.getElementById('project-status-filter');
        if (statusFilter) {
            statusFilter.addEventListener('change', (e) => {
                this.handleStatusFilter(e.target.value);
            });
        }
        
        // Project list event delegation
        const projectList = document.getElementById('project-list');
        if (projectList) {
            projectList.addEventListener('click', (e) => {
                if (e.target.classList.contains('edit-btn')) {
                    this.editProject(e.target.dataset.id);
                } else if (e.target.classList.contains('delete-btn')) {
                    this.deleteProject(e.target.dataset.id);
                } else if (e.target.classList.contains('view-btn')) {
                    this.viewProject(e.target.dataset.id);
                }
            });
        }
        
        // Deadline validation
        const deadlineField = document.getElementById('deadline');
        if (deadlineField) {
            deadlineField.addEventListener('change', (e) => {
                this.validateDeadline(e.target.value);
            });
        }
    }
    
    /**
     * Load projects from API
     */
    async loadProjects(params = {}) {
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
                this.projects = data.projects;
                this.renderProjectList();
                this.renderPagination(data.pagination);
                this.updateProjectStats();
            } else {
                this.showError('Failed to load projects: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading projects: ' + error.message);
        } finally {
            this.showLoading(false);
        }
    }
    
    /**
     * Handle form submission for create/update
     */
    async handleFormSubmit() {
        try {
            const form = document.getElementById('project-form');
            const formData = new FormData(form);
            
            // Convert FormData to JSON
            const data = {};
            for (let [key, value] of formData.entries()) {
                data[key] = value;
            }
            
            // Validate required fields
            if (!data.name?.trim()) {
                this.showError('Project name is required');
                return;
            }
            
            if (!data.description?.trim()) {
                this.showError('Project description is required');
                return;
            }
            
            // Validate deadline if provided
            if (data.deadline && !this.validateDeadline(data.deadline)) {
                return;
            }
            
            const isUpdate = this.currentProject !== null;
            const url = isUpdate 
                ? `${this.apiBaseUrl}${this.currentProject.id}/`
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
                        ? 'Project updated successfully!' 
                        : 'Project created successfully!'
                );
                this.resetForm();
                this.loadProjects();
            } else {
                this.showError('Error saving project: ' + result.error);
            }
        } catch (error) {
            this.showError('Error saving project: ' + error.message);
        }
    }
    
    /**
     * Edit project - load into form
     */
    async editProject(projectId) {
        try {
            const response = await fetch(`${this.apiBaseUrl}${projectId}/`, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentProject = data.project;
                this.populateForm(data.project);
                this.scrollToForm();
            } else {
                this.showError('Error loading project: ' + data.error);
            }
        } catch (error) {
            this.showError('Error loading project: ' + error.message);
        }
    }
    
    /**
     * Delete project with confirmation
     */
    async deleteProject(projectId) {
        if (!confirm('Are you sure you want to delete this project? This action cannot be undone.')) {
            return;
        }
        
        try {
            const response = await fetch(`${this.apiBaseUrl}${projectId}/`, {
                method: 'DELETE',
                headers: {
                    'X-CSRFToken': this.getCSRFToken()
                },
                credentials: 'same-origin'
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.showSuccess('Project deleted successfully!');
                this.loadProjects();
            } else {
                this.showError('Error deleting project: ' + data.error);
            }
        } catch (error) {
            this.showError('Error deleting project: ' + error.message);
        }
    }
    
    /**
     * View project in modal or new page
     */
    viewProject(projectId) {
        const project = this.projects.find(proj => proj.id == projectId);
        if (project) {
            this.showProjectModal(project);
        }
    }
    
    /**
     * Handle status filtering
     */
    handleStatusFilter(status) {
        const params = {};
        if (status) {
            params.status = status;
        }
        this.loadProjects(params);
    }
    
    /**
     * Validate deadline
     */
    validateDeadline(deadline) {
        if (!deadline) return true;
        
        const deadlineDate = new Date(deadline);
        const now = new Date();
        
        if (deadlineDate <= now) {
            this.showError('Deadline must be in the future');
            return false;
        }
        
        return true;
    }
    
    /**
     * Render project list in DOM
     */
    renderProjectList() {
        const container = document.getElementById('project-list');
        if (!container) return;
        
        if (this.projects.length === 0) {
            container.innerHTML = `
                <div class="empty-state">
                    <p>No projects found. Create your first project!</p>
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.projects.map(project => `
            <div class="project-item card ${this.getProjectCardClass(project)}" data-id="${project.id}">
                <div class="project-header">
                    <h3 class="project-title">${this.escapeHtml(project.name)}</h3>
                    <div class="project-status-container">
                        <span class="project-status status-${project.status}">
                            ${this.formatStatus(project.status)}
                        </span>
                        ${this.getDeadlineIndicator(project)}
                    </div>
                </div>
                <div class="project-content">
                    <p class="project-description">
                        ${this.escapeHtml(project.description.substring(0, 200))}${project.description.length > 200 ? '...' : ''}
                    </p>
                    ${project.deadline ? `
                        <div class="project-deadline">
                            <strong>Deadline:</strong> ${this.formatDate(project.deadline)}
                        </div>
                    ` : ''}
                </div>
                <div class="project-meta">
                    <span class="project-date">
                        Updated: ${new Date(project.updated_at).toLocaleDateString()}
                    </span>
                    ${project.collaborators && project.collaborators.length > 0 ? `
                        <span class="collaborators-count">
                            ${project.collaborators.length} collaborator${project.collaborators.length !== 1 ? 's' : ''}
                        </span>
                    ` : ''}
                </div>
                <div class="project-actions">
                    <button class="btn btn-sm btn-primary view-btn" data-id="${project.id}">
                        View
                    </button>
                    <button class="btn btn-sm btn-secondary edit-btn" data-id="${project.id}">
                        Edit
                    </button>
                    <button class="btn btn-sm btn-danger delete-btn" data-id="${project.id}">
                        Delete
                    </button>
                </div>
            </div>
        `).join('');
    }
    
    /**
     * Get CSS class for project card based on status/deadline
     */
    getProjectCardClass(project) {
        let classes = [];
        
        if (project.deadline) {
            const deadline = new Date(project.deadline);
            const now = new Date();
            const daysDiff = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
            
            if (daysDiff < 0) {
                classes.push('overdue');
            } else if (daysDiff <= 7) {
                classes.push('deadline-soon');
            }
        }
        
        return classes.join(' ');
    }
    
    /**
     * Get deadline indicator HTML
     */
    getDeadlineIndicator(project) {
        if (!project.deadline) return '';
        
        const deadline = new Date(project.deadline);
        const now = new Date();
        const daysDiff = Math.ceil((deadline - now) / (1000 * 60 * 60 * 24));
        
        if (daysDiff < 0) {
            return '<span class="deadline-indicator overdue">Overdue</span>';
        } else if (daysDiff <= 7) {
            return '<span class="deadline-indicator warning">Due Soon</span>';
        }
        
        return '';
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
                    <button class="btn btn-outline-primary" onclick="projectManager.loadProjects({page: ${pagination.current_page - 1}})">
                        Previous
                    </button>
                ` : ''}
                
                <span class="pagination-info">
                    Page ${pagination.current_page} of ${pagination.total_pages}
                    (${pagination.total_count} total)
                </span>
                
                ${pagination.has_next ? `
                    <button class="btn btn-outline-primary" onclick="projectManager.loadProjects({page: ${pagination.current_page + 1}})">
                        Next
                    </button>
                ` : ''}
            </div>
        `;
    }
    
    /**
     * Update project statistics
     */
    updateProjectStats() {
        const statusCounts = this.projects.reduce((acc, project) => {
            acc[project.status] = (acc[project.status] || 0) + 1;
            return acc;
        }, {});
        
        // Update status count displays if they exist
        Object.keys(statusCounts).forEach(status => {
            const element = document.getElementById(`${status}-count`);
            if (element) {
                element.textContent = statusCounts[status];
            }
        });
    }
    
    /**
     * Populate form with project data
     */
    populateForm(project) {
        const form = document.getElementById('project-form');
        if (!form) return;
        
        form.name.value = project.name;
        form.description.value = project.description;
        form.status.value = project.status;
        
        if (form.deadline && project.deadline) {
            // Convert ISO datetime to datetime-local format
            const deadline = new Date(project.deadline);
            const localDeadline = new Date(deadline.getTime() - deadline.getTimezoneOffset() * 60000);
            form.deadline.value = localDeadline.toISOString().slice(0, 16);
        }
        
        // Update form title
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.textContent = 'Edit Project';
        }
        
        // Update submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Update Project';
        }
    }
    
    /**
     * Reset form to create mode
     */
    resetForm() {
        const form = document.getElementById('project-form');
        if (!form) return;
        
        form.reset();
        this.currentProject = null;
        
        // Update form title
        const formTitle = document.getElementById('form-title');
        if (formTitle) {
            formTitle.textContent = 'Create New Project';
        }
        
        // Update submit button
        const submitBtn = form.querySelector('button[type="submit"]');
        if (submitBtn) {
            submitBtn.textContent = 'Create Project';
        }
    }
    
    /**
     * Show project in modal
     */
    showProjectModal(project) {
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog modal-lg">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">${this.escapeHtml(project.name)}</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="project-meta mb-3">
                            <span class="project-status status-${project.status}">
                                ${this.formatStatus(project.status)}
                            </span>
                            <span class="text-muted">Updated: ${new Date(project.updated_at).toLocaleDateString()}</span>
                            ${project.deadline ? `
                                <span class="text-muted">Deadline: ${this.formatDate(project.deadline)}</span>
                            ` : ''}
                        </div>
                        <div class="project-description">
                            <h6>Description:</h6>
                            <p>${this.escapeHtml(project.description).replace(/\n/g, '<br>')}</p>
                        </div>
                        ${project.collaborators && project.collaborators.length > 0 ? `
                            <div class="project-collaborators">
                                <h6>Collaborators:</h6>
                                <ul>
                                    ${project.collaborators.map(collab => `
                                        <li>${this.escapeHtml(collab.username)}</li>
                                    `).join('')}
                                </ul>
                            </div>
                        ` : ''}
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Close</button>
                        <button type="button" class="btn btn-primary" onclick="projectManager.editProject(${project.id}); bootstrap.Modal.getInstance(this.closest('.modal')).hide();">
                            Edit Project
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
    formatStatus(status) {
        return status.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase());
    }
    
    formatDate(dateString) {
        return new Date(dateString).toLocaleDateString('en-US', {
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit'
        });
    }
    
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
        const form = document.getElementById('project-form');
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

// Initialize project manager when DOM is loaded
document.addEventListener('DOMContentLoaded', () => {
    window.projectManager = new ProjectManager();
});