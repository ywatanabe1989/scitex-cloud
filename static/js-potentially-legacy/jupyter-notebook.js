/**
 * SciTeX-Code Jupyter Notebook Interface
 * Provides a complete notebook editing and execution environment
 */

class JupyterNotebook {
    constructor(containerId, notebookId = null) {
        this.container = document.getElementById(containerId);
        this.notebookId = notebookId;
        this.notebook = null;
        this.cells = [];
        this.activeCellIndex = 0;
        this.isExecuting = false;
        this.autoSaveInterval = null;
        
        this.init();
    }
    
    async init() {
        this.setupToolbar();
        this.setupKeyboardShortcuts();
        
        if (this.notebookId) {
            await this.loadNotebook();
        } else {
            this.createNewNotebook();
        }
        
        this.startAutoSave();
    }
    
    setupToolbar() {
        const toolbar = document.createElement('div');
        toolbar.className = 'notebook-toolbar';
        toolbar.innerHTML = `
            <div class="toolbar-section">
                <button id="save-btn" class="btn btn-primary btn-sm" title="Save (Ctrl+S)">
                    <i class="fas fa-save"></i> Save
                </button>
                <button id="add-cell-btn" class="btn btn-secondary btn-sm" title="Add Cell">
                    <i class="fas fa-plus"></i> Add Cell
                </button>
                <div class="dropdown">
                    <button class="btn btn-secondary btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                        <i class="fas fa-plus"></i> Insert
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="notebook.addCell('code')">Code Cell</a></li>
                        <li><a class="dropdown-item" href="#" onclick="notebook.addCell('markdown')">Markdown Cell</a></li>
                        <li><a class="dropdown-item" href="#" onclick="notebook.addCell('raw')">Raw Cell</a></li>
                    </ul>
                </div>
            </div>
            
            <div class="toolbar-section">
                <button id="run-cell-btn" class="btn btn-success btn-sm" title="Run Cell (Shift+Enter)">
                    <i class="fas fa-play"></i> Run
                </button>
                <button id="run-all-btn" class="btn btn-success btn-sm" title="Run All">
                    <i class="fas fa-forward"></i> Run All
                </button>
                <button id="restart-btn" class="btn btn-warning btn-sm" title="Restart Kernel">
                    <i class="fas fa-redo"></i> Restart
                </button>
            </div>
            
            <div class="toolbar-section">
                <div class="dropdown">
                    <button class="btn btn-secondary btn-sm dropdown-toggle" data-bs-toggle="dropdown">
                        <i class="fas fa-download"></i> Export
                    </button>
                    <ul class="dropdown-menu">
                        <li><a class="dropdown-item" href="#" onclick="notebook.exportNotebook('html')">HTML</a></li>
                        <li><a class="dropdown-item" href="#" onclick="notebook.exportNotebook('python')">Python (.py)</a></li>
                        <li><a class="dropdown-item" href="#" onclick="notebook.exportNotebook('markdown')">Markdown</a></li>
                    </ul>
                </div>
                <button id="share-btn" class="btn btn-info btn-sm" title="Share Notebook">
                    <i class="fas fa-share"></i> Share
                </button>
            </div>
            
            <div class="toolbar-section ml-auto">
                <span id="kernel-status" class="kernel-status">
                    <i class="fas fa-circle text-success"></i> Ready
                </span>
                <span id="save-status" class="save-status text-muted">
                    <i class="fas fa-check"></i> Saved
                </span>
            </div>
        `;
        
        this.container.appendChild(toolbar);
        this.setupToolbarEvents();
    }
    
    setupToolbarEvents() {
        document.getElementById('save-btn').addEventListener('click', () => this.saveNotebook());
        document.getElementById('add-cell-btn').addEventListener('click', () => this.addCell('code'));
        document.getElementById('run-cell-btn').addEventListener('click', () => this.runActiveCell());
        document.getElementById('run-all-btn').addEventListener('click', () => this.runAllCells());
        document.getElementById('restart-btn').addEventListener('click', () => this.restartKernel());
        document.getElementById('share-btn').addEventListener('click', () => this.showShareDialog());
    }
    
    setupKeyboardShortcuts() {
        document.addEventListener('keydown', (e) => {
            // Only handle shortcuts when notebook is focused
            if (!this.container.contains(document.activeElement)) return;
            
            if (e.ctrlKey || e.metaKey) {
                switch (e.key) {
                    case 's':
                        e.preventDefault();
                        this.saveNotebook();
                        break;
                    case 'Enter':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.runActiveCell();
                        }
                        break;
                }
            }
            
            // Cell navigation and management
            if (e.target.classList.contains('cell-editor')) {
                if (e.key === 'Escape') {
                    this.setCommandMode();
                }
            } else if (this.isInCommandMode()) {
                switch (e.key) {
                    case 'a':
                        e.preventDefault();
                        this.addCellAbove();
                        break;
                    case 'b':
                        e.preventDefault();
                        this.addCellBelow();
                        break;
                    case 'd':
                        if (e.shiftKey) {
                            e.preventDefault();
                            this.deleteActiveCell();
                        }
                        break;
                    case 'm':
                        e.preventDefault();
                        this.changeCellType('markdown');
                        break;
                    case 'y':
                        e.preventDefault();
                        this.changeCellType('code');
                        break;
                    case 'Enter':
                        e.preventDefault();
                        this.setEditMode();
                        break;
                    case 'ArrowUp':
                        e.preventDefault();
                        this.selectPreviousCell();
                        break;
                    case 'ArrowDown':
                        e.preventDefault();
                        this.selectNextCell();
                        break;
                }
            }
        });
    }
    
    async loadNotebook() {
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.notebook = data.notebook;
                this.renderNotebook();
                this.updateTitle();
            } else {
                this.showError('Failed to load notebook: ' + data.message);
            }
        } catch (error) {
            this.showError('Error loading notebook: ' + error.message);
        }
    }
    
    createNewNotebook() {
        this.notebook = {
            title: 'Untitled Notebook',
            content: {
                cells: [
                    {
                        cell_type: 'code',
                        source: ['# Welcome to SciTeX-Code Jupyter Notebook\\n', 'print("Hello, SciTeX!")'],
                        metadata: {},
                        execution_count: null,
                        outputs: []
                    }
                ],
                metadata: {
                    kernelspec: {
                        display_name: 'Python 3',
                        language: 'python',
                        name: 'python3'
                    }
                },
                nbformat: 4,
                nbformat_minor: 4
            }
        };
        this.renderNotebook();
    }
    
    renderNotebook() {
        // Clear existing content
        const existingCells = this.container.querySelector('.notebook-cells');
        if (existingCells) {
            existingCells.remove();
        }
        
        // Create cells container
        const cellsContainer = document.createElement('div');
        cellsContainer.className = 'notebook-cells';
        this.container.appendChild(cellsContainer);
        
        // Render cells
        this.cells = [];
        this.notebook.content.cells.forEach((cellData, index) => {
            const cell = this.createCell(cellData, index);
            this.cells.push(cell);
            cellsContainer.appendChild(cell.element);
        });
        
        // Select first cell
        if (this.cells.length > 0) {
            this.selectCell(0);
        }
    }
    
    createCell(cellData, index) {
        const cell = document.createElement('div');
        cell.className = `notebook-cell cell-${cellData.cell_type}`;
        cell.dataset.cellIndex = index;
        
        const cellType = cellData.cell_type;
        const source = Array.isArray(cellData.source) ? cellData.source.join('') : cellData.source;
        
        cell.innerHTML = `
            <div class="cell-toolbar">
                <select class="cell-type-selector" onchange="notebook.changeCellType('${cellType}', ${index})">
                    <option value="code" ${cellType === 'code' ? 'selected' : ''}>Code</option>
                    <option value="markdown" ${cellType === 'markdown' ? 'selected' : ''}>Markdown</option>
                    <option value="raw" ${cellType === 'raw' ? 'selected' : ''}>Raw</option>
                </select>
                <div class="cell-actions">
                    <button class="btn btn-sm btn-link" onclick="notebook.moveCell(${index}, -1)" title="Move Up">
                        <i class="fas fa-arrow-up"></i>
                    </button>
                    <button class="btn btn-sm btn-link" onclick="notebook.moveCell(${index}, 1)" title="Move Down">
                        <i class="fas fa-arrow-down"></i>
                    </button>
                    <button class="btn btn-sm btn-link" onclick="notebook.deleteCell(${index})" title="Delete">
                        <i class="fas fa-trash text-danger"></i>
                    </button>
                </div>
            </div>
            
            <div class="cell-input">
                ${cellType === 'code' ? `<div class="cell-prompt">In [${cellData.execution_count || ''}]:</div>` : ''}
                <div class="cell-editor-container">
                    <textarea class="cell-editor" data-cell-type="${cellType}" placeholder="${this.getCellPlaceholder(cellType)}">${source}</textarea>
                </div>
            </div>
            
            ${cellType === 'code' ? '<div class="cell-output"></div>' : ''}
            ${cellType === 'markdown' ? '<div class="cell-preview markdown-preview"></div>' : ''}
        `;
        
        // Setup cell editor
        const editor = cell.querySelector('.cell-editor');
        this.setupCellEditor(editor, index);
        
        // Render existing outputs for code cells
        if (cellType === 'code' && cellData.outputs && cellData.outputs.length > 0) {
            const outputContainer = cell.querySelector('.cell-output');
            this.renderCellOutputs(outputContainer, cellData.outputs);
        }
        
        // Render markdown preview
        if (cellType === 'markdown') {
            this.updateMarkdownPreview(cell, source);
        }
        
        return {
            element: cell,
            type: cellType,
            index: index,
            editor: editor
        };
    }
    
    setupCellEditor(editor, index) {
        // Auto-resize textarea
        editor.addEventListener('input', () => {
            editor.style.height = 'auto';
            editor.style.height = editor.scrollHeight + 'px';
            this.markUnsaved();
        });
        
        // Handle cell-specific shortcuts
        editor.addEventListener('keydown', (e) => {
            if (e.shiftKey && e.key === 'Enter') {
                e.preventDefault();
                this.runCell(index);
            } else if (e.ctrlKey && e.key === 'Enter') {
                e.preventDefault();
                this.runCell(index);
                this.addCellBelow();
            }
        });
        
        // Update cell content in notebook data
        editor.addEventListener('input', () => {
            this.updateCellContent(index, editor.value);
        });
        
        // Initial resize
        editor.style.height = editor.scrollHeight + 'px';
    }
    
    getCellPlaceholder(cellType) {
        switch (cellType) {
            case 'code':
                return 'Enter Python code here...';
            case 'markdown':
                return 'Enter Markdown text here...';
            case 'raw':
                return 'Enter raw text here...';
            default:
                return '';
        }
    }
    
    updateCellContent(index, content) {
        if (this.notebook.content.cells[index]) {
            this.notebook.content.cells[index].source = content.split('\\n');
        }
    }
    
    addCell(cellType = 'code', position = null) {
        const index = position !== null ? position : this.activeCellIndex + 1;
        
        const newCell = {
            cell_type: cellType,
            source: [''],
            metadata: {},
            execution_count: null,
            outputs: []
        };
        
        // Insert into notebook data
        this.notebook.content.cells.splice(index, 0, newCell);
        
        // Re-render notebook
        this.renderNotebook();
        
        // Select new cell
        this.selectCell(index);
        this.setEditMode();
        
        this.markUnsaved();
    }
    
    addCellAbove() {
        this.addCell('code', this.activeCellIndex);
    }
    
    addCellBelow() {
        this.addCell('code', this.activeCellIndex + 1);
    }
    
    deleteCell(index) {
        if (this.notebook.content.cells.length <= 1) {
            this.showWarning('Cannot delete the last cell');
            return;
        }
        
        if (confirm('Are you sure you want to delete this cell?')) {
            this.notebook.content.cells.splice(index, 1);
            this.renderNotebook();
            
            // Adjust active cell index
            if (index <= this.activeCellIndex && this.activeCellIndex > 0) {
                this.activeCellIndex--;
            }
            
            this.selectCell(Math.min(this.activeCellIndex, this.cells.length - 1));
            this.markUnsaved();
        }
    }
    
    deleteActiveCell() {
        this.deleteCell(this.activeCellIndex);
    }
    
    changeCellType(newType, index = null) {
        const cellIndex = index !== null ? index : this.activeCellIndex;
        const cell = this.notebook.content.cells[cellIndex];
        
        if (cell && cell.cell_type !== newType) {
            cell.cell_type = newType;
            
            // Clear outputs when changing from code cell
            if (newType !== 'code') {
                cell.outputs = [];
                cell.execution_count = null;
            }
            
            this.renderNotebook();
            this.selectCell(cellIndex);
            this.markUnsaved();
        }
    }
    
    selectCell(index) {
        // Remove previous selection
        this.cells.forEach(cell => cell.element.classList.remove('active'));
        
        // Select new cell
        if (index >= 0 && index < this.cells.length) {
            this.activeCellIndex = index;
            this.cells[index].element.classList.add('active');
        }
    }
    
    selectNextCell() {
        if (this.activeCellIndex < this.cells.length - 1) {
            this.selectCell(this.activeCellIndex + 1);
        }
    }
    
    selectPreviousCell() {
        if (this.activeCellIndex > 0) {
            this.selectCell(this.activeCellIndex - 1);
        }
    }
    
    setEditMode() {
        const activeCell = this.cells[this.activeCellIndex];
        if (activeCell) {
            activeCell.editor.focus();
        }
    }
    
    setCommandMode() {
        document.activeElement.blur();
    }
    
    isInCommandMode() {
        return !document.activeElement || !document.activeElement.classList.contains('cell-editor');
    }
    
    async runCell(index) {
        const cell = this.notebook.content.cells[index];
        if (!cell || cell.cell_type !== 'code') return;
        
        this.setKernelStatus('busy');
        
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/execute/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    cell_index: index,
                    timeout: 60
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.pollJobStatus(data.job_id, index);
            } else {
                this.showError('Failed to execute cell: ' + data.message);
                this.setKernelStatus('idle');
            }
        } catch (error) {
            this.showError('Error executing cell: ' + error.message);
            this.setKernelStatus('idle');
        }
    }
    
    async runActiveCell() {
        await this.runCell(this.activeCellIndex);
    }
    
    async runAllCells() {
        if (!this.notebookId) {
            this.showError('Please save the notebook before running all cells');
            return;
        }
        
        this.setKernelStatus('busy');
        
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/execute/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    timeout: 300
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.pollJobStatus(data.job_id);
            } else {
                this.showError('Failed to execute notebook: ' + data.message);
                this.setKernelStatus('idle');
            }
        } catch (error) {
            this.showError('Error executing notebook: ' + error.message);
            this.setKernelStatus('idle');
        }
    }
    
    async pollJobStatus(jobId, cellIndex = null) {
        const poll = async () => {
            try {
                const response = await fetch(`/code/api/jobs/${jobId}/status/`);
                const data = await response.json();
                
                if (data.status === 'completed') {
                    this.setKernelStatus('idle');
                    
                    if (cellIndex !== null) {
                        // Single cell execution
                        const outputs = JSON.parse(data.output || '{}');
                        this.updateCellOutput(cellIndex, outputs);
                    } else {
                        // Full notebook execution - reload notebook
                        await this.loadNotebook();
                    }
                    
                    this.showSuccess('Execution completed');
                    
                } else if (data.status === 'failed') {
                    this.setKernelStatus('idle');
                    this.showError('Execution failed: ' + (data.error_output || 'Unknown error'));
                    
                } else if (data.status === 'running') {
                    // Continue polling
                    setTimeout(poll, 1000);
                } else {
                    // Still queued or other status
                    setTimeout(poll, 2000);
                }
            } catch (error) {
                this.setKernelStatus('idle');
                this.showError('Error checking execution status: ' + error.message);
            }
        };
        
        poll();
    }
    
    updateCellOutput(cellIndex, outputs) {
        const cellElement = this.cells[cellIndex].element;
        const outputContainer = cellElement.querySelector('.cell-output');
        
        if (outputContainer && outputs.outputs) {
            this.renderCellOutputs(outputContainer, outputs.outputs);
        }
        
        // Update execution count
        if (outputs.execution_count) {
            const prompt = cellElement.querySelector('.cell-prompt');
            if (prompt) {
                prompt.textContent = `In [${outputs.execution_count}]:`;
            }
            
            // Update notebook data
            this.notebook.content.cells[cellIndex].execution_count = outputs.execution_count;
        }
    }
    
    renderCellOutputs(container, outputs) {
        container.innerHTML = '';
        
        outputs.forEach(output => {
            const outputDiv = document.createElement('div');
            outputDiv.className = 'cell-output-item';
            
            if (output.type === 'stream') {
                outputDiv.innerHTML = `<pre class="output-stream">${this.escapeHtml(output.text)}</pre>`;
            } else if (output.type === 'result' || output.type === 'display') {
                if (output.data) {
                    if (output.data['text/html']) {
                        outputDiv.innerHTML = output.data['text/html'];
                    } else if (output.data['text/plain']) {
                        outputDiv.innerHTML = `<pre class="output-text">${this.escapeHtml(output.data['text/plain'])}</pre>`;
                    } else if (output.data['image/png']) {
                        outputDiv.innerHTML = `<img src="data:image/png;base64,${output.data['image/png']}" class="output-image">`;
                    }
                }
            } else if (output.type === 'error') {
                outputDiv.innerHTML = `
                    <div class="output-error">
                        <strong>${this.escapeHtml(output.ename)}: ${this.escapeHtml(output.evalue)}</strong>
                        <pre>${output.traceback.map(line => this.escapeHtml(line)).join('\\n')}</pre>
                    </div>
                `;
            }
            
            container.appendChild(outputDiv);
        });
    }
    
    updateMarkdownPreview(cellElement, source) {
        const preview = cellElement.querySelector('.cell-preview');
        if (preview) {
            // Simple markdown rendering (you might want to use a proper markdown library)
            const html = this.simpleMarkdownToHtml(source);
            preview.innerHTML = html;
        }
    }
    
    simpleMarkdownToHtml(markdown) {
        return markdown
            .replace(/^### (.*$)/gim, '<h3>$1</h3>')
            .replace(/^## (.*$)/gim, '<h2>$1</h2>')
            .replace(/^# (.*$)/gim, '<h1>$1</h1>')
            .replace(/\\*\\*(.*?)\\*\\*/gim, '<strong>$1</strong>')
            .replace(/\\*(.*?)\\*/gim, '<em>$1</em>')
            .replace(/`(.*?)`/gim, '<code>$1</code>')
            .replace(/\\n/gim, '<br>');
    }
    
    async saveNotebook() {
        if (!this.notebookId) {
            // Create new notebook
            const title = prompt('Enter notebook title:', this.notebook.title);
            if (!title) return;
            
            try {
                const response = await fetch('/code/api/notebooks/', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': this.getCSRFToken()
                    },
                    body: JSON.stringify({
                        title: title,
                        description: ''
                    })
                });
                
                const data = await response.json();
                
                if (data.status === 'success') {
                    this.notebookId = data.notebook.id;
                    this.notebook.title = title;
                    await this.updateNotebookContent();
                } else {
                    this.showError('Failed to create notebook: ' + data.message);
                    return;
                }
            } catch (error) {
                this.showError('Error creating notebook: ' + error.message);
                return;
            }
        } else {
            await this.updateNotebookContent();
        }
        
        this.markSaved();
        this.showSuccess('Notebook saved');
    }
    
    async updateNotebookContent() {
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    content: this.notebook.content
                })
            });
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                this.showError('Failed to save notebook: ' + data.message);
            }
        } catch (error) {
            this.showError('Error saving notebook: ' + error.message);
        }
    }
    
    async exportNotebook(format) {
        if (!this.notebookId) {
            this.showError('Please save the notebook before exporting');
            return;
        }
        
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/convert/${format}/`);
            const data = await response.json();
            
            if (data.status === 'success') {
                this.downloadFile(data.content, data.filename, this.getContentType(format));
            } else {
                this.showError('Failed to export notebook: ' + data.message);
            }
        } catch (error) {
            this.showError('Error exporting notebook: ' + error.message);
        }
    }
    
    downloadFile(content, filename, contentType) {
        const blob = new Blob([content], { type: contentType });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }
    
    getContentType(format) {
        const types = {
            'html': 'text/html',
            'python': 'text/x-python',
            'markdown': 'text/markdown'
        };
        return types[format] || 'text/plain';
    }
    
    showShareDialog() {
        // Implement sharing dialog
        const modal = document.createElement('div');
        modal.className = 'modal fade';
        modal.innerHTML = `
            <div class="modal-dialog">
                <div class="modal-content">
                    <div class="modal-header">
                        <h5 class="modal-title">Share Notebook</h5>
                        <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                    </div>
                    <div class="modal-body">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="public-checkbox">
                            <label class="form-check-label" for="public-checkbox">
                                Make this notebook public
                            </label>
                        </div>
                        <div class="mt-3">
                            <label for="share-users" class="form-label">Share with specific users:</label>
                            <input type="text" class="form-control" id="share-users" placeholder="Enter usernames separated by commas">
                        </div>
                    </div>
                    <div class="modal-footer">
                        <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                        <button type="button" class="btn btn-primary" onclick="notebook.updateSharing()">Update Sharing</button>
                    </div>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        modal.addEventListener('hidden.bs.modal', () => {
            document.body.removeChild(modal);
        });
    }
    
    async updateSharing() {
        const isPublic = document.getElementById('public-checkbox').checked;
        const usersInput = document.getElementById('share-users').value;
        const usernames = usersInput.split(',').map(u => u.trim()).filter(u => u);
        
        try {
            const response = await fetch(`/code/api/notebooks/${this.notebookId}/share/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    is_public: isPublic,
                    usernames: usernames
                })
            });
            
            const data = await response.json();
            
            if (data.status === 'success') {
                this.showSuccess('Sharing settings updated');
                bootstrap.Modal.getInstance(document.querySelector('.modal')).hide();
            } else {
                this.showError('Failed to update sharing: ' + data.message);
            }
        } catch (error) {
            this.showError('Error updating sharing: ' + error.message);
        }
    }
    
    restartKernel() {
        if (confirm('Are you sure you want to restart the kernel? All variables will be lost.')) {
            this.setKernelStatus('restarting');
            // Implementation would depend on kernel management system
            setTimeout(() => {
                this.setKernelStatus('idle');
                this.showSuccess('Kernel restarted');
            }, 2000);
        }
    }
    
    setKernelStatus(status) {
        const statusEl = document.getElementById('kernel-status');
        if (statusEl) {
            switch (status) {
                case 'idle':
                    statusEl.innerHTML = '<i class="fas fa-circle text-success"></i> Ready';
                    break;
                case 'busy':
                    statusEl.innerHTML = '<i class="fas fa-circle text-warning"></i> Busy';
                    break;
                case 'restarting':
                    statusEl.innerHTML = '<i class="fas fa-circle text-info"></i> Restarting';
                    break;
                default:
                    statusEl.innerHTML = '<i class="fas fa-circle text-secondary"></i> Unknown';
            }
        }
    }
    
    markUnsaved() {
        const statusEl = document.getElementById('save-status');
        if (statusEl) {
            statusEl.innerHTML = '<i class="fas fa-circle text-warning"></i> Unsaved';
        }
    }
    
    markSaved() {
        const statusEl = document.getElementById('save-status');
        if (statusEl) {
            statusEl.innerHTML = '<i class="fas fa-check text-success"></i> Saved';
        }
    }
    
    startAutoSave() {
        this.autoSaveInterval = setInterval(() => {
            if (this.notebookId && document.getElementById('save-status').textContent.includes('Unsaved')) {
                this.updateNotebookContent();
                this.markSaved();
            }
        }, 30000); // Auto-save every 30 seconds
    }
    
    updateTitle() {
        if (this.notebook && this.notebook.title) {
            document.title = `${this.notebook.title} - SciTeX Notebook`;
        }
    }
    
    // Utility methods
    getCSRFToken() {
        return document.querySelector('[name=csrfmiddlewaretoken]')?.value || '';
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    showSuccess(message) {
        this.showToast(message, 'success');
    }
    
    showError(message) {
        this.showToast(message, 'error');
    }
    
    showWarning(message) {
        this.showToast(message, 'warning');
    }
    
    showToast(message, type) {
        const toast = document.createElement('div');
        toast.className = `toast show align-items-center text-white bg-${type === 'error' ? 'danger' : type === 'warning' ? 'warning' : 'success'} border-0`;
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        
        let container = document.getElementById('toast-container');
        if (!container) {
            container = document.createElement('div');
            container.id = 'toast-container';
            container.className = 'toast-container position-fixed top-0 end-0 p-3';
            document.body.appendChild(container);
        }
        
        container.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 5000);
    }
    
    destroy() {
        if (this.autoSaveInterval) {
            clearInterval(this.autoSaveInterval);
        }
    }
}

// Global notebook instance
let notebook = null;

// Initialize notebook when page loads
document.addEventListener('DOMContentLoaded', function() {
    const notebookContainer = document.getElementById('notebook-container');
    if (notebookContainer) {
        const notebookId = notebookContainer.dataset.notebookId || null;
        notebook = new JupyterNotebook('notebook-container', notebookId);
    }
});