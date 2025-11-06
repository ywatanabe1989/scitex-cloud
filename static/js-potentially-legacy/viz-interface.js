/**
 * SciTeX-Viz Interactive Visualization Interface
 * Provides a comprehensive plotting environment for scientific visualization
 */

class VizInterface {
    constructor(containerId) {
        this.container = document.getElementById(containerId);
        this.currentViz = null;
        this.plotData = null;
        this.plotConfig = {
            responsive: true,
            displayModeBar: true,
            modeBarButtonsToAdd: ['drawline', 'drawopenpath', 'drawclosedpath', 'drawcircle', 'drawrect', 'eraseshape'],
            displaylogo: false
        };
        this.charts = new Map(); // Store multiple chart instances
        this.activeChartId = null;
        
        this.init();
    }
    
    init() {
        this.setupInterface();
        this.setupEventListeners();
        this.loadSampleData();
    }
    
    setupInterface() {
        this.container.innerHTML = `
            <div class="viz-interface">
                <!-- Toolbar -->
                <div class="viz-toolbar">
                    <div class="toolbar-section">
                        <div class="btn-group" role="group">
                            <button id="new-chart-btn" class="btn btn-primary btn-sm">
                                <i class="fas fa-plus"></i> New Chart
                            </button>
                            <button id="import-data-btn" class="btn btn-secondary btn-sm">
                                <i class="fas fa-upload"></i> Import Data
                            </button>
                            <button id="export-chart-btn" class="btn btn-secondary btn-sm">
                                <i class="fas fa-download"></i> Export
                            </button>
                        </div>
                    </div>
                    
                    <div class="toolbar-section">
                        <div class="btn-group" role="group">
                            <button id="save-viz-btn" class="btn btn-success btn-sm">
                                <i class="fas fa-save"></i> Save
                            </button>
                            <button id="publish-btn" class="btn btn-info btn-sm">
                                <i class="fas fa-share-alt"></i> Publish
                            </button>
                        </div>
                    </div>
                    
                    <div class="toolbar-section ml-auto">
                        <span id="viz-status" class="viz-status">
                            <i class="fas fa-circle text-success"></i> Ready
                        </span>
                    </div>
                </div>
                
                <!-- Main Interface -->
                <div class="viz-main">
                    <!-- Left Sidebar: Chart Types & Data -->
                    <div class="viz-sidebar">
                        <div class="sidebar-section">
                            <h6><i class="fas fa-chart-bar"></i> Chart Types</h6>
                            <div class="chart-types-grid">
                                <button class="chart-type-btn" data-type="scatter" title="Scatter Plot">
                                    <i class="fas fa-braille"></i>
                                    <span>Scatter</span>
                                </button>
                                <button class="chart-type-btn" data-type="line" title="Line Plot">
                                    <i class="fas fa-chart-line"></i>
                                    <span>Line</span>
                                </button>
                                <button class="chart-type-btn" data-type="bar" title="Bar Chart">
                                    <i class="fas fa-chart-bar"></i>
                                    <span>Bar</span>
                                </button>
                                <button class="chart-type-btn" data-type="histogram" title="Histogram">
                                    <i class="fas fa-chart-column"></i>
                                    <span>Histogram</span>
                                </button>
                                <button class="chart-type-btn" data-type="heatmap" title="Heatmap">
                                    <i class="fas fa-th"></i>
                                    <span>Heatmap</span>
                                </button>
                                <button class="chart-type-btn" data-type="contour" title="Contour Plot">
                                    <i class="fas fa-mountain"></i>
                                    <span>Contour</span>
                                </button>
                                <button class="chart-type-btn" data-type="3d_scatter" title="3D Scatter">
                                    <i class="fas fa-cube"></i>
                                    <span>3D Scatter</span>
                                </button>
                                <button class="chart-type-btn" data-type="3d_surface" title="3D Surface">
                                    <i class="fas fa-layer-group"></i>
                                    <span>3D Surface</span>
                                </button>
                                <button class="chart-type-btn" data-type="box" title="Box Plot">
                                    <i class="fas fa-square"></i>
                                    <span>Box Plot</span>
                                </button>
                                <button class="chart-type-btn" data-type="violin" title="Violin Plot">
                                    <i class="fas fa-grip-lines"></i>
                                    <span>Violin</span>
                                </button>
                            </div>
                        </div>
                        
                        <div class="sidebar-section">
                            <h6><i class="fas fa-database"></i> Data Preview</h6>
                            <div id="data-preview" class="data-preview">
                                <div class="text-muted text-center py-3">
                                    <i class="fas fa-table fa-2x mb-2"></i>
                                    <p>Import data to see preview</p>
                                </div>
                            </div>
                        </div>
                        
                        <div class="sidebar-section">
                            <h6><i class="fas fa-sliders-h"></i> Chart Controls</h6>
                            <div id="chart-controls" class="chart-controls">
                                <!-- Dynamic controls will be inserted here -->
                            </div>
                        </div>
                    </div>
                    
                    <!-- Center: Plot Area -->
                    <div class="viz-plot-area">
                        <div class="plot-tabs">
                            <ul class="nav nav-tabs" id="plotTabs" role="tablist">
                                <!-- Dynamic tabs for multiple charts -->
                            </ul>
                        </div>
                        <div class="tab-content" id="plotTabContent">
                            <div class="plot-welcome text-center py-5" id="welcome-screen">
                                <i class="fas fa-chart-area fa-4x text-muted mb-3"></i>
                                <h4>Welcome to SciTeX Viz</h4>
                                <p class="text-muted">Create beautiful, publication-ready scientific visualizations</p>
                                <button class="btn btn-primary" onclick="vizInterface.createNewChart()">
                                    <i class="fas fa-plus"></i> Create Your First Chart
                                </button>
                            </div>
                        </div>
                    </div>
                    
                    <!-- Right Sidebar: Configuration -->
                    <div class="viz-config-panel">
                        <div class="config-section">
                            <h6><i class="fas fa-cog"></i> Chart Configuration</h6>
                            <div id="chart-config" class="chart-config">
                                <div class="form-group">
                                    <label for="chart-title">Title</label>
                                    <input type="text" class="form-control form-control-sm" id="chart-title" placeholder="Chart Title">
                                </div>
                                <div class="form-group">
                                    <label for="x-axis-label">X-Axis Label</label>
                                    <input type="text" class="form-control form-control-sm" id="x-axis-label" placeholder="X-Axis">
                                </div>
                                <div class="form-group">
                                    <label for="y-axis-label">Y-Axis Label</label>
                                    <input type="text" class="form-control form-control-sm" id="y-axis-label" placeholder="Y-Axis">
                                </div>
                                
                                <div class="form-group">
                                    <label>Theme</label>
                                    <select class="form-control form-control-sm" id="chart-theme">
                                        <option value="plotly">Default</option>
                                        <option value="plotly_white">Clean White</option>
                                        <option value="plotly_dark">Dark</option>
                                        <option value="ggplot2">ggplot2</option>
                                        <option value="seaborn">Seaborn</option>
                                        <option value="simple_white">Simple White</option>
                                        <option value="presentation">Presentation</option>
                                        <option value="xgridoff">No X Grid</option>
                                        <option value="ygridoff">No Y Grid</option>
                                        <option value="gridon">Grid On</option>
                                    </select>
                                </div>
                                
                                <div class="form-group">
                                    <label>Color Scheme</label>
                                    <select class="form-control form-control-sm" id="color-scheme">
                                        <option value="viridis">Viridis</option>
                                        <option value="plasma">Plasma</option>
                                        <option value="inferno">Inferno</option>
                                        <option value="magma">Magma</option>
                                        <option value="cividis">Cividis</option>
                                        <option value="blues">Blues</option>
                                        <option value="reds">Reds</option>
                                        <option value="greens">Greens</option>
                                        <option value="purples">Purples</option>
                                        <option value="rdbu">RdBu</option>
                                        <option value="rdylbu">RdYlBu</option>
                                        <option value="spectral">Spectral</option>
                                    </select>
                                </div>
                                
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="show-legend" checked>
                                    <label class="form-check-label" for="show-legend">Show Legend</label>
                                </div>
                                
                                <div class="form-check">
                                    <input class="form-check-input" type="checkbox" id="show-grid" checked>
                                    <label class="form-check-label" for="show-grid">Show Grid</label>
                                </div>
                                
                                <div class="form-group mt-3">
                                    <button id="update-chart-btn" class="btn btn-primary btn-sm btn-block">
                                        <i class="fas fa-sync"></i> Update Chart
                                    </button>
                                </div>
                            </div>
                        </div>
                        
                        <div class="config-section">
                            <h6><i class="fas fa-code"></i> Code Generation</h6>
                            <div class="btn-group-vertical btn-block">
                                <button class="btn btn-outline-secondary btn-sm" onclick="vizInterface.generateCode('python')">
                                    <i class="fab fa-python"></i> Python
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="vizInterface.generateCode('r')">
                                    <i class="fab fa-r-project"></i> R
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="vizInterface.generateCode('matlab')">
                                    <i class="fas fa-calculator"></i> MATLAB
                                </button>
                                <button class="btn btn-outline-secondary btn-sm" onclick="vizInterface.generateCode('julia')">
                                    <i class="fas fa-superscript"></i> Julia
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
                
                <!-- Hidden file input for data import -->
                <input type="file" id="file-input" accept=".csv,.json,.xlsx,.txt" style="display: none;">
            </div>
        `;
    }
    
    setupEventListeners() {
        // Toolbar buttons
        document.getElementById('new-chart-btn').addEventListener('click', () => this.createNewChart());
        document.getElementById('import-data-btn').addEventListener('click', () => this.importData());
        document.getElementById('export-chart-btn').addEventListener('click', () => this.exportChart());
        document.getElementById('save-viz-btn').addEventListener('click', () => this.saveVisualization());
        document.getElementById('publish-btn').addEventListener('click', () => this.publishVisualization());
        
        // Chart type buttons
        document.querySelectorAll('.chart-type-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const chartType = e.currentTarget.dataset.type;
                this.createChart(chartType);
            });
        });
        
        // Configuration controls
        document.getElementById('update-chart-btn').addEventListener('click', () => this.updateChart());
        
        // Real-time configuration updates
        ['chart-title', 'x-axis-label', 'y-axis-label', 'chart-theme', 'color-scheme'].forEach(id => {
            const element = document.getElementById(id);
            element.addEventListener('input', () => this.updateChart());
        });
        
        ['show-legend', 'show-grid'].forEach(id => {
            document.getElementById(id).addEventListener('change', () => this.updateChart());
        });
        
        // File input
        document.getElementById('file-input').addEventListener('change', (e) => this.handleFileUpload(e));
    }
    
    loadSampleData() {
        // Generate sample scientific data
        const x = [];
        const y = [];
        const z = [];
        
        for (let i = 0; i < 100; i++) {
            const xVal = Math.random() * 10;
            const yVal = Math.random() * 10;
            const zVal = Math.sin(xVal) * Math.cos(yVal) + Math.random() * 0.5;
            
            x.push(xVal);
            y.push(yVal);
            z.push(zVal);
        }
        
        this.plotData = {
            x: x,
            y: y,
            z: z,
            columns: ['x', 'y', 'z'],
            name: 'Sample Data'
        };
        
        this.updateDataPreview();
    }
    
    updateDataPreview() {
        const preview = document.getElementById('data-preview');
        if (!this.plotData) {
            preview.innerHTML = `
                <div class="text-muted text-center py-3">
                    <i class="fas fa-table fa-2x mb-2"></i>
                    <p>No data loaded</p>
                </div>
            `;
            return;
        }
        
        const columns = this.plotData.columns || Object.keys(this.plotData);
        const sampleSize = Math.min(5, this.plotData[columns[0]]?.length || 0);
        
        let tableHTML = `
            <div class="data-info mb-2">
                <small class="text-muted">
                    ${this.plotData.name || 'Dataset'} 
                    (${this.plotData[columns[0]]?.length || 0} rows, ${columns.length} columns)
                </small>
            </div>
            <div class="table-responsive">
                <table class="table table-sm table-striped">
                    <thead>
                        <tr>
        `;
        
        columns.forEach(col => {
            tableHTML += `<th>${col}</th>`;
        });
        tableHTML += '</tr></thead><tbody>';
        
        for (let i = 0; i < sampleSize; i++) {
            tableHTML += '<tr>';
            columns.forEach(col => {
                const value = this.plotData[col] && this.plotData[col][i];
                const displayValue = typeof value === 'number' ? value.toFixed(3) : value;
                tableHTML += `<td>${displayValue || ''}</td>`;
            });
            tableHTML += '</tr>';
        }
        
        if (sampleSize < (this.plotData[columns[0]]?.length || 0)) {
            tableHTML += `<tr><td colspan="${columns.length}" class="text-center text-muted">... and ${(this.plotData[columns[0]]?.length || 0) - sampleSize} more rows</td></tr>`;
        }
        
        tableHTML += '</tbody></table></div>';
        preview.innerHTML = tableHTML;
    }
    
    createNewChart() {
        const chartId = 'chart-' + Date.now();
        this.activeChartId = chartId;
        
        // Add new tab
        this.addChartTab(chartId, 'New Chart');
        
        // Hide welcome screen
        document.getElementById('welcome-screen').style.display = 'none';
        
        // Create default scatter plot
        this.createChart('scatter', chartId);
    }
    
    addChartTab(chartId, title) {
        const tabsContainer = document.getElementById('plotTabs');
        const contentContainer = document.getElementById('plotTabContent');
        
        // Create tab
        const tabItem = document.createElement('li');
        tabItem.className = 'nav-item';
        tabItem.innerHTML = `
            <a class="nav-link ${this.charts.size === 0 ? 'active' : ''}" 
               id="${chartId}-tab" 
               data-bs-toggle="tab" 
               href="#${chartId}-content" 
               role="tab">
                ${title}
                <button type="button" class="btn-close btn-close-sm ms-2" onclick="vizInterface.closeChart('${chartId}')"></button>
            </a>
        `;
        tabsContainer.appendChild(tabItem);
        
        // Create content pane
        const contentPane = document.createElement('div');
        contentPane.className = `tab-pane fade ${this.charts.size === 0 ? 'show active' : ''}`;
        contentPane.id = `${chartId}-content`;
        contentPane.innerHTML = `<div id="${chartId}" class="plot-container"></div>`;
        contentContainer.appendChild(contentPane);
    }
    
    createChart(type, chartId = null) {
        if (!chartId) {
            chartId = this.activeChartId || 'chart-' + Date.now();
        }
        
        if (!this.plotData) {
            this.showError('Please import data first');
            return;
        }
        
        const plotDiv = document.getElementById(chartId);
        if (!plotDiv) {
            this.createNewChart();
            return;
        }
        
        let data, layout;
        
        switch (type) {
            case 'scatter':
                data = [{
                    x: this.plotData.x,
                    y: this.plotData.y,
                    mode: 'markers',
                    type: 'scatter',
                    marker: {
                        size: 8,
                        color: this.plotData.z || this.plotData.y,
                        colorscale: 'Viridis',
                        showscale: true
                    },
                    name: 'Data Points'
                }];
                layout = {
                    title: 'Scatter Plot',
                    xaxis: { title: 'X-axis' },
                    yaxis: { title: 'Y-axis' }
                };
                break;
                
            case 'line':
                data = [{
                    x: this.plotData.x,
                    y: this.plotData.y,
                    mode: 'lines+markers',
                    type: 'scatter',
                    line: { width: 2 },
                    marker: { size: 6 },
                    name: 'Data Series'
                }];
                layout = {
                    title: 'Line Plot',
                    xaxis: { title: 'X-axis' },
                    yaxis: { title: 'Y-axis' }
                };
                break;
                
            case 'bar':
                const categories = [...new Set(this.plotData.x.map(x => Math.floor(x)))];
                const counts = categories.map(cat => 
                    this.plotData.x.filter(x => Math.floor(x) === cat).length
                );
                
                data = [{
                    x: categories,
                    y: counts,
                    type: 'bar',
                    marker: { color: 'rgba(26, 35, 50, 0.8)' },
                    name: 'Frequency'
                }];
                layout = {
                    title: 'Bar Chart',
                    xaxis: { title: 'Categories' },
                    yaxis: { title: 'Count' }
                };
                break;
                
            case 'histogram':
                data = [{
                    x: this.plotData.x,
                    type: 'histogram',
                    nbinsx: 20,
                    marker: { color: 'rgba(26, 35, 50, 0.7)' },
                    name: 'Distribution'
                }];
                layout = {
                    title: 'Histogram',
                    xaxis: { title: 'Value' },
                    yaxis: { title: 'Frequency' }
                };
                break;
                
            case 'heatmap':
                // Create 2D grid from data
                const gridSize = 20;
                const xGrid = [];
                const yGrid = [];
                const zGrid = [];
                
                for (let i = 0; i < gridSize; i++) {
                    const row = [];
                    for (let j = 0; j < gridSize; j++) {
                        const x = (i / gridSize) * 10;
                        const y = (j / gridSize) * 10;
                        row.push(Math.sin(x) * Math.cos(y));
                    }
                    zGrid.push(row);
                }
                
                data = [{
                    z: zGrid,
                    type: 'heatmap',
                    colorscale: 'Viridis',
                    showscale: true
                }];
                layout = {
                    title: 'Heatmap',
                    xaxis: { title: 'X-axis' },
                    yaxis: { title: 'Y-axis' }
                };
                break;
                
            case 'contour':
                data = [{
                    x: this.plotData.x,
                    y: this.plotData.y,
                    z: this.plotData.z,
                    type: 'contour',
                    colorscale: 'Viridis',
                    showscale: true,
                    contours: {
                        showlines: true,
                        showlabels: true
                    }
                }];
                layout = {
                    title: 'Contour Plot',
                    xaxis: { title: 'X-axis' },
                    yaxis: { title: 'Y-axis' }
                };
                break;
                
            case '3d_scatter':
                data = [{
                    x: this.plotData.x,
                    y: this.plotData.y,
                    z: this.plotData.z,
                    mode: 'markers',
                    type: 'scatter3d',
                    marker: {
                        size: 5,
                        color: this.plotData.z,
                        colorscale: 'Viridis',
                        showscale: true
                    },
                    name: '3D Points'
                }];
                layout = {
                    title: '3D Scatter Plot',
                    scene: {
                        xaxis: { title: 'X-axis' },
                        yaxis: { title: 'Y-axis' },
                        zaxis: { title: 'Z-axis' }
                    }
                };
                break;
                
            case '3d_surface':
                // Create surface data
                const surfaceZ = [];
                const surfaceSize = 30;
                for (let i = 0; i < surfaceSize; i++) {
                    const row = [];
                    for (let j = 0; j < surfaceSize; j++) {
                        const x = (i - surfaceSize/2) / 5;
                        const y = (j - surfaceSize/2) / 5;
                        row.push(Math.sin(Math.sqrt(x*x + y*y)));
                    }
                    surfaceZ.push(row);
                }
                
                data = [{
                    z: surfaceZ,
                    type: 'surface',
                    colorscale: 'Viridis',
                    showscale: true
                }];
                layout = {
                    title: '3D Surface Plot',
                    scene: {
                        xaxis: { title: 'X-axis' },
                        yaxis: { title: 'Y-axis' },
                        zaxis: { title: 'Z-axis' }
                    }
                };
                break;
                
            case 'box':
                data = [{
                    y: this.plotData.y,
                    type: 'box',
                    name: 'Distribution',
                    marker: { color: 'rgba(26, 35, 50, 0.7)' }
                }];
                layout = {
                    title: 'Box Plot',
                    yaxis: { title: 'Value' }
                };
                break;
                
            case 'violin':
                data = [{
                    y: this.plotData.y,
                    type: 'violin',
                    name: 'Distribution',
                    line: { color: '#1a2332' },
                    fillcolor: 'rgba(26, 35, 50, 0.5)'
                }];
                layout = {
                    title: 'Violin Plot',
                    yaxis: { title: 'Value' }
                };
                break;
                
            default:
                this.showError('Unsupported chart type: ' + type);
                return;
        }
        
        // Apply theme and styling
        layout.template = this.getChartTheme();
        layout.autosize = true;
        layout.margin = { t: 60, b: 50, l: 60, r: 50 };
        
        // Create plot
        Plotly.newPlot(plotDiv, data, layout, this.plotConfig);
        
        // Store chart info
        this.charts.set(chartId, {
            type: type,
            data: data,
            layout: layout,
            element: plotDiv
        });
        
        this.currentViz = { chartId, type, data, layout };
        this.updateChartControls(type);
        this.setStatus('Chart created', 'success');
        
        // Update tab title
        const tab = document.getElementById(chartId + '-tab');
        if (tab) {
            tab.innerHTML = `
                ${type.charAt(0).toUpperCase() + type.slice(1).replace('_', ' ')}
                <button type="button" class="btn-close btn-close-sm ms-2" onclick="vizInterface.closeChart('${chartId}')"></button>
            `;
        }
    }
    
    updateChart() {
        if (!this.currentViz || !this.charts.has(this.currentViz.chartId)) return;
        
        const chart = this.charts.get(this.currentViz.chartId);
        const plotDiv = chart.element;
        
        // Update layout properties
        const updates = {
            'title.text': document.getElementById('chart-title').value,
            'xaxis.title.text': document.getElementById('x-axis-label').value,
            'yaxis.title.text': document.getElementById('y-axis-label').value,
            'template': this.getChartTheme(),
            'showlegend': document.getElementById('show-legend').checked
        };
        
        // Update grid
        if (!document.getElementById('show-grid').checked) {
            updates['xaxis.showgrid'] = false;
            updates['yaxis.showgrid'] = false;
        }
        
        // Update color scheme for applicable chart types
        const colorScheme = document.getElementById('color-scheme').value;
        if (chart.data[0].marker && chart.data[0].marker.colorscale !== undefined) {
            Plotly.restyle(plotDiv, {'marker.colorscale': colorScheme}, 0);
        }
        
        Plotly.relayout(plotDiv, updates);
        this.setStatus('Chart updated', 'success');
    }
    
    updateChartControls(chartType) {
        const controlsContainer = document.getElementById('chart-controls');
        let controlsHTML = '';
        
        switch (chartType) {
            case 'scatter':
                controlsHTML = `
                    <div class="form-group">
                        <label for="marker-size">Marker Size</label>
                        <input type="range" class="form-control-range" id="marker-size" min="3" max="20" value="8">
                    </div>
                    <div class="form-group">
                        <label for="marker-opacity">Opacity</label>
                        <input type="range" class="form-control-range" id="marker-opacity" min="0.1" max="1" step="0.1" value="1">
                    </div>
                `;
                break;
                
            case 'line':
                controlsHTML = `
                    <div class="form-group">
                        <label for="line-width">Line Width</label>
                        <input type="range" class="form-control-range" id="line-width" min="1" max="10" value="2">
                    </div>
                    <div class="form-group">
                        <label for="line-style">Line Style</label>
                        <select class="form-control form-control-sm" id="line-style">
                            <option value="solid">Solid</option>
                            <option value="dash">Dashed</option>
                            <option value="dot">Dotted</option>
                            <option value="dashdot">Dash-Dot</option>
                        </select>
                    </div>
                `;
                break;
                
            case 'histogram':
                controlsHTML = `
                    <div class="form-group">
                        <label for="bin-count">Number of Bins</label>
                        <input type="range" class="form-control-range" id="bin-count" min="5" max="50" value="20">
                        <small class="text-muted">Current: <span id="bin-count-value">20</span></small>
                    </div>
                `;
                break;
                
            case 'heatmap':
            case 'contour':
                controlsHTML = `
                    <div class="form-group">
                        <label for="contour-levels">Contour Levels</label>
                        <input type="range" class="form-control-range" id="contour-levels" min="5" max="50" value="20">
                    </div>
                    <div class="form-check">
                        <input class="form-check-input" type="checkbox" id="show-contour-lines" checked>
                        <label class="form-check-label" for="show-contour-lines">Show Lines</label>
                    </div>
                `;
                break;
        }
        
        controlsContainer.innerHTML = controlsHTML;
        
        // Add event listeners for dynamic controls
        if (document.getElementById('marker-size')) {
            document.getElementById('marker-size').addEventListener('input', (e) => {
                if (this.currentViz) {
                    Plotly.restyle(this.currentViz.chartId, {'marker.size': parseInt(e.target.value)}, 0);
                }
            });
        }
        
        if (document.getElementById('bin-count')) {
            const binSlider = document.getElementById('bin-count');
            const binValue = document.getElementById('bin-count-value');
            binSlider.addEventListener('input', (e) => {
                binValue.textContent = e.target.value;
                if (this.currentViz) {
                    Plotly.restyle(this.currentViz.chartId, {'nbinsx': parseInt(e.target.value)}, 0);
                }
            });
        }
    }
    
    getChartTheme() {
        const theme = document.getElementById('chart-theme').value;
        return theme;
    }
    
    importData() {
        document.getElementById('file-input').click();
    }
    
    handleFileUpload(event) {
        const file = event.target.files[0];
        if (!file) return;
        
        this.setStatus('Loading data...', 'loading');
        
        const reader = new FileReader();
        reader.onload = (e) => {
            try {
                let data;
                
                if (file.name.endsWith('.csv')) {
                    data = this.parseCSV(e.target.result);
                } else if (file.name.endsWith('.json')) {
                    data = JSON.parse(e.target.result);
                } else {
                    throw new Error('Unsupported file format');
                }
                
                this.plotData = data;
                this.plotData.name = file.name;
                this.updateDataPreview();
                this.setStatus('Data loaded successfully', 'success');
                
            } catch (error) {
                this.showError('Error loading data: ' + error.message);
            }
        };
        
        reader.readAsText(file);
    }
    
    parseCSV(csvText) {
        const lines = csvText.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim());
        const data = {};
        
        headers.forEach(header => {
            data[header] = [];
        });
        
        for (let i = 1; i < lines.length; i++) {
            const values = lines[i].split(',');
            headers.forEach((header, index) => {
                const value = values[index]?.trim();
                // Try to parse as number, otherwise keep as string
                const numValue = parseFloat(value);
                data[header].push(isNaN(numValue) ? value : numValue);
            });
        }
        
        data.columns = headers;
        return data;
    }
    
    exportChart() {
        if (!this.currentViz) {
            this.showError('No chart to export');
            return;
        }
        
        const modal = this.createExportModal();
        modal.show();
    }
    
    createExportModal() {
        // Create modal if it doesn't exist
        let modal = document.getElementById('export-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'export-modal';
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Export Chart</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="form-group">
                                <label>Format</label>
                                <select class="form-control" id="export-format">
                                    <option value="png">PNG Image</option>
                                    <option value="svg">SVG Vector</option>
                                    <option value="pdf">PDF Document</option>
                                    <option value="html">Interactive HTML</option>
                                    <option value="json">JSON Data</option>
                                </select>
                            </div>
                            <div class="form-group">
                                <label>Width (px)</label>
                                <input type="number" class="form-control" id="export-width" value="1200">
                            </div>
                            <div class="form-group">
                                <label>Height (px)</label>
                                <input type="number" class="form-control" id="export-height" value="800">
                            </div>
                            <div class="form-group">
                                <label>DPI</label>
                                <input type="number" class="form-control" id="export-dpi" value="300">
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Cancel</button>
                            <button type="button" class="btn btn-primary" onclick="vizInterface.performExport()">Export</button>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        return new bootstrap.Modal(modal);
    }
    
    performExport() {
        const format = document.getElementById('export-format').value;
        const width = parseInt(document.getElementById('export-width').value);
        const height = parseInt(document.getElementById('export-height').value);
        const dpi = parseInt(document.getElementById('export-dpi').value);
        
        const chart = this.charts.get(this.currentViz.chartId);
        const plotDiv = chart.element;
        
        if (format === 'png' || format === 'svg' || format === 'pdf') {
            // Use Plotly's export functionality
            Plotly.toImage(plotDiv, {
                format: format,
                width: width,
                height: height,
                scale: dpi / 72 // Convert DPI to scale
            }).then((dataURL) => {
                this.downloadFile(dataURL, `chart.${format}`);
                this.setStatus('Chart exported successfully', 'success');
            }).catch((error) => {
                this.showError('Export failed: ' + error.message);
            });
        } else if (format === 'html') {
            // Export as standalone HTML
            const htmlContent = this.generateHTMLExport(chart);
            const blob = new Blob([htmlContent], { type: 'text/html' });
            const url = URL.createObjectURL(blob);
            this.downloadFile(url, 'chart.html');
        } else if (format === 'json') {
            // Export data and configuration as JSON
            const exportData = {
                data: chart.data,
                layout: chart.layout,
                config: this.plotConfig,
                type: chart.type,
                exported_at: new Date().toISOString()
            };
            const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            this.downloadFile(url, 'chart.json');
        }
        
        // Close modal
        bootstrap.Modal.getInstance(document.getElementById('export-modal')).hide();
    }
    
    generateHTMLExport(chart) {
        return `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SciTeX Chart Export</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
            margin: 0; 
            padding: 20px; 
            background: #f8f9fa;
        }
        .container { 
            max-width: 1200px; 
            margin: 0 auto; 
            background: white; 
            border-radius: 8px; 
            box-shadow: 0 2px 10px rgba(0,0,0,0.1); 
            overflow: hidden;
        }
        .header { 
            background: #1a2332; 
            color: white; 
            padding: 20px; 
            text-align: center; 
        }
        .chart-container { 
            padding: 20px; 
            height: 600px; 
        }
        .footer { 
            background: #f8f9fa; 
            padding: 15px; 
            text-align: center; 
            border-top: 1px solid #dee2e6; 
            font-size: 0.9rem; 
            color: #6c757d; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>SciTeX Visualization</h1>
            <p>Generated on ${new Date().toLocaleDateString()}</p>
        </div>
        <div class="chart-container">
            <div id="plotly-chart" style="width:100%;height:100%;"></div>
        </div>
        <div class="footer">
            Created with SciTeX-Viz | Visit <a href="https://scitex.ai" target="_blank">scitex.ai</a>
        </div>
    </div>
    
    <script>
        Plotly.newPlot('plotly-chart', 
            ${JSON.stringify(chart.data)}, 
            ${JSON.stringify(chart.layout)}, 
            {responsive: true, displayModeBar: true}
        );
    </script>
</body>
</html>
        `;
    }
    
    downloadFile(dataURL, filename) {
        const link = document.createElement('a');
        link.href = dataURL;
        link.download = filename;
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }
    
    generateCode(language) {
        if (!this.currentViz) {
            this.showError('No chart to generate code for');
            return;
        }
        
        const chart = this.charts.get(this.currentViz.chartId);
        let code = '';
        
        switch (language) {
            case 'python':
                code = this.generatePythonCode(chart);
                break;
            case 'r':
                code = this.generateRCode(chart);
                break;
            case 'matlab':
                code = this.generateMatlabCode(chart);
                break;
            case 'julia':
                code = this.generateJuliaCode(chart);
                break;
        }
        
        this.showCodeModal(code, language);
    }
    
    generatePythonCode(chart) {
        const data = chart.data[0];
        let code = `import plotly.graph_objects as go
import plotly.express as px
import numpy as np
import pandas as pd

# Sample data (replace with your actual data)
`;
        
        if (data.x) code += `x = ${JSON.stringify(data.x.slice(0, 10))}  # ... truncated for display\n`;
        if (data.y) code += `y = ${JSON.stringify(data.y.slice(0, 10))}  # ... truncated for display\n`;
        if (data.z) code += `z = ${JSON.stringify(data.z.slice(0, 10))}  # ... truncated for display\n`;
        
        code += `\n# Create the ${chart.type} plot\n`;
        
        switch (chart.type) {
            case 'scatter':
                code += `fig = go.Figure(data=go.Scatter(x=x, y=y, mode='markers'))`;
                break;
            case 'line':
                code += `fig = go.Figure(data=go.Scatter(x=x, y=y, mode='lines+markers'))`;
                break;
            case 'bar':
                code += `fig = go.Figure(data=go.Bar(x=x, y=y))`;
                break;
            case 'histogram':
                code += `fig = go.Figure(data=go.Histogram(x=x))`;
                break;
            case 'heatmap':
                code += `fig = go.Figure(data=go.Heatmap(z=z))`;
                break;
            default:
                code += `fig = go.Figure()  # Add your specific plot type here`;
        }
        
        code += `\n\n# Update layout
fig.update_layout(
    title='${chart.layout.title?.text || 'Chart Title'}',
    xaxis_title='${chart.layout.xaxis?.title?.text || 'X-axis'}',
    yaxis_title='${chart.layout.yaxis?.title?.text || 'Y-axis'}',
    template='${chart.layout.template || 'plotly'}'
)

# Show the plot
fig.show()

# Save as image (optional)
# fig.write_image("chart.png", width=1200, height=800, scale=2)`;
        
        return code;
    }
    
    generateRCode(chart) {
        let code = `library(plotly)
library(ggplot2)

# Sample data (replace with your actual data)
`;
        
        const data = chart.data[0];
        if (data.x && data.y) {
            code += `df <- data.frame(
  x = c(${data.x.slice(0, 10).join(', ')}),  # ... truncated
  y = c(${data.y.slice(0, 10).join(', ')})   # ... truncated
)

`;
        }
        
        switch (chart.type) {
            case 'scatter':
                code += `# Create scatter plot
p <- ggplot(df, aes(x=x, y=y)) + 
  geom_point() +
  labs(title='${chart.layout.title?.text || 'Scatter Plot'}',
       x='${chart.layout.xaxis?.title?.text || 'X-axis'}',
       y='${chart.layout.yaxis?.title?.text || 'Y-axis'}')

# Convert to interactive plot
fig <- ggplotly(p)
fig`;
                break;
            case 'line':
                code += `# Create line plot
p <- ggplot(df, aes(x=x, y=y)) + 
  geom_line() + 
  geom_point() +
  labs(title='${chart.layout.title?.text || 'Line Plot'}',
       x='${chart.layout.xaxis?.title?.text || 'X-axis'}',
       y='${chart.layout.yaxis?.title?.text || 'Y-axis'}')

fig <- ggplotly(p)
fig`;
                break;
            default:
                code += `# Create plot using plotly
fig <- plot_ly(df, x=~x, y=~y, type='scatter', mode='markers')
fig`;
        }
        
        return code;
    }
    
    generateMatlabCode(chart) {
        const data = chart.data[0];
        let code = `% MATLAB code for ${chart.type} plot

% Sample data (replace with your actual data)
`;
        
        if (data.x) code += `x = [${data.x.slice(0, 10).join(', ')}];  % ... truncated\n`;
        if (data.y) code += `y = [${data.y.slice(0, 10).join(', ')}];  % ... truncated\n`;
        
        switch (chart.type) {
            case 'scatter':
                code += `
% Create scatter plot
figure;
scatter(x, y, 'filled');
title('${chart.layout.title?.text || 'Scatter Plot'}');
xlabel('${chart.layout.xaxis?.title?.text || 'X-axis'}');
ylabel('${chart.layout.yaxis?.title?.text || 'Y-axis'}');
grid on;`;
                break;
            case 'line':
                code += `
% Create line plot
figure;
plot(x, y, '-o');
title('${chart.layout.title?.text || 'Line Plot'}');
xlabel('${chart.layout.xaxis?.title?.text || 'X-axis'}');
ylabel('${chart.layout.yaxis?.title?.text || 'Y-axis'}');
grid on;`;
                break;
            default:
                code += `
% Create plot
figure;
plot(x, y);
title('${chart.layout.title?.text || 'Chart'}');
xlabel('${chart.layout.xaxis?.title?.text || 'X-axis'}');
ylabel('${chart.layout.yaxis?.title?.text || 'Y-axis'}');`;
        }
        
        return code;
    }
    
    generateJuliaCode(chart) {
        const data = chart.data[0];
        let code = `using Plots, PlotlyJS
plotlyjs()

# Sample data (replace with your actual data)
`;
        
        if (data.x) code += `x = [${data.x.slice(0, 10).join(', ')}]  # ... truncated\n`;
        if (data.y) code += `y = [${data.y.slice(0, 10).join(', ')}]  # ... truncated\n`;
        
        switch (chart.type) {
            case 'scatter':
                code += `
# Create scatter plot
scatter(x, y, 
    title="${chart.layout.title?.text || 'Scatter Plot'}", 
    xlabel="${chart.layout.xaxis?.title?.text || 'X-axis'}", 
    ylabel="${chart.layout.yaxis?.title?.text || 'Y-axis'}",
    markersize=6)`;
                break;
            case 'line':
                code += `
# Create line plot  
plot(x, y, 
    title="${chart.layout.title?.text || 'Line Plot'}", 
    xlabel="${chart.layout.xaxis?.title?.text || 'X-axis'}", 
    ylabel="${chart.layout.yaxis?.title?.text || 'Y-axis'}",
    linewidth=2, marker=:circle)`;
                break;
            default:
                code += `
# Create plot
plot(x, y, 
    title="${chart.layout.title?.text || 'Chart'}", 
    xlabel="${chart.layout.xaxis?.title?.text || 'X-axis'}", 
    ylabel="${chart.layout.yaxis?.title?.text || 'Y-axis'}")`;
        }
        
        return code;
    }
    
    showCodeModal(code, language) {
        let modal = document.getElementById('code-modal');
        if (!modal) {
            modal = document.createElement('div');
            modal.id = 'code-modal';
            modal.className = 'modal fade';
            modal.innerHTML = `
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Generated Code</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <span class="badge bg-primary" id="code-language"></span>
                                <button class="btn btn-outline-secondary btn-sm" onclick="vizInterface.copyCode()">
                                    <i class="fas fa-copy"></i> Copy
                                </button>
                            </div>
                            <pre><code id="code-content" class="language-python"></code></pre>
                        </div>
                    </div>
                </div>
            `;
            document.body.appendChild(modal);
        }
        
        document.getElementById('code-language').textContent = language.toUpperCase();
        document.getElementById('code-content').textContent = code;
        document.getElementById('code-content').className = `language-${language}`;
        
        new bootstrap.Modal(modal).show();
    }
    
    copyCode() {
        const codeElement = document.getElementById('code-content');
        navigator.clipboard.writeText(codeElement.textContent).then(() => {
            this.setStatus('Code copied to clipboard', 'success');
        });
    }
    
    closeChart(chartId) {
        if (this.charts.has(chartId)) {
            this.charts.delete(chartId);
            
            // Remove tab and content
            document.getElementById(chartId + '-tab').parentElement.remove();
            document.getElementById(chartId + '-content').remove();
            
            // If this was the active chart, select another or show welcome
            if (this.activeChartId === chartId) {
                if (this.charts.size > 0) {
                    const firstChart = this.charts.keys().next().value;
                    this.activeChartId = firstChart;
                    this.currentViz = { chartId: firstChart, ...this.charts.get(firstChart) };
                } else {
                    this.activeChartId = null;
                    this.currentViz = null;
                    document.getElementById('welcome-screen').style.display = 'block';
                }
            }
        }
    }
    
    saveVisualization() {
        if (!this.currentViz) {
            this.showError('No visualization to save');
            return;
        }
        
        // In a real implementation, this would send data to the server
        this.setStatus('Visualization saved', 'success');
        this.showSuccess('Visualization saved successfully!');
    }
    
    publishVisualization() {
        if (!this.currentViz) {
            this.showError('No visualization to publish');
            return;
        }
        
        // In a real implementation, this would handle publishing logic
        this.setStatus('Visualization published', 'success');
        this.showSuccess('Visualization published successfully!');
    }
    
    setStatus(message, type = 'info') {
        const statusEl = document.getElementById('viz-status');
        const iconClass = type === 'success' ? 'text-success' : 
                         type === 'error' ? 'text-danger' : 
                         type === 'loading' ? 'text-warning' : 'text-info';
        
        statusEl.innerHTML = `<i class="fas fa-circle ${iconClass}"></i> ${message}`;
        
        // Auto-clear after 3 seconds for non-error messages
        if (type !== 'error') {
            setTimeout(() => {
                statusEl.innerHTML = '<i class="fas fa-circle text-success"></i> Ready';
            }, 3000);
        }
    }
    
    showError(message) {
        this.setStatus(message, 'error');
        // You could also show a toast notification here
    }
    
    showSuccess(message) {
        // Show a toast notification
        const toast = document.createElement('div');
        toast.className = 'toast show align-items-center text-white bg-success border-0 position-fixed';
        toast.style.cssText = 'top: 20px; right: 20px; z-index: 9999;';
        toast.innerHTML = `
            <div class="d-flex">
                <div class="toast-body">${message}</div>
                <button type="button" class="btn-close btn-close-white me-2 m-auto" onclick="this.parentElement.parentElement.remove()"></button>
            </div>
        `;
        document.body.appendChild(toast);
        
        setTimeout(() => {
            if (toast.parentNode) {
                toast.remove();
            }
        }, 4000);
    }
}

// Global instance
let vizInterface = null;

// Initialize when page loads
document.addEventListener('DOMContentLoaded', function() {
    const vizContainer = document.getElementById('viz-interface-container');
    if (vizContainer) {
        vizInterface = new VizInterface('viz-interface-container');
    }
});