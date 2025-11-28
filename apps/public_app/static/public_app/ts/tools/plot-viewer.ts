// Nature Journal Standards - Precise Canvas-based Rendering
// All measurements at 300 DPI for publication quality

const csvFileInput = document.getElementById('csvFileInput');
const plotCanvas = document.getElementById('plotCanvas');
const plotInfo = document.getElementById('plotInfo');
const plotContainer = document.getElementById('plotContainer');

let currentPlotData = null;  // Store for download
let currentCSVData = null;   // Store current CSV data for re-rendering
let currentPlots = null;     // Store current plots for re-rendering

// Dynamic settings with Nature defaults
let plotSettings = {
    figureWidth: 35,
    figureHeight: 24.5,   // 0.7 * width
    lineWidth: 0.12,
    tickLength: 0.8,
    tickWidth: 0.2,
    axisWidth: 0.2,
    titleFontSize: 8,
    axisFontSize: 8,
    tickFontSize: 7,
    markerSize: 0.8,
    numTicks: 4,
    xLabel: 'X axis',
    yLabel: 'Y axis'
};

// Interactive controls functions
function toggleSettingsPanel() {
    const panel = document.getElementById('settingsPanel');
    const button = document.getElementById('toggleSettings');
    if (panel.style.display === 'none' || panel.style.display === '') {
        panel.style.display = 'block';
        button.textContent = '⚙️ Hide Settings';
    } else {
        panel.style.display = 'none';
        button.textContent = '⚙️ Adjust Figure Settings';
    }
}

function updateSetting(param, value) {
    // Don't parse float for string values (labels)
    if (param !== 'xLabel' && param !== 'yLabel') {
        value = parseFloat(value);
    }

    // Update the setting
    switch(param) {
        case 'width':
            plotSettings.figureWidth = value;
            plotSettings.figureHeight = value * 0.7;  // Auto-calculate height
            document.getElementById('widthValue').textContent = value.toFixed(1) + ' mm';
            document.getElementById('heightValue').textContent = (value * 0.7).toFixed(1) + ' mm';
            document.getElementById('figureHeight').value = value * 0.7;
            break;
        case 'lineWidth':
            plotSettings.lineWidth = value;
            document.getElementById('lineWidthValue').textContent = value.toFixed(2) + ' mm';
            break;
        case 'tickLength':
            plotSettings.tickLength = value;
            document.getElementById('tickLengthValue').textContent = value.toFixed(1) + ' mm';
            break;
        case 'tickWidth':
            plotSettings.tickWidth = value;
            document.getElementById('tickWidthValue').textContent = value.toFixed(2) + ' mm';
            break;
        case 'axisWidth':
            plotSettings.axisWidth = value;
            document.getElementById('axisWidthValue').textContent = value.toFixed(2) + ' mm';
            break;
        case 'titleFont':
            plotSettings.titleFontSize = value;
            document.getElementById('titleFontValue').textContent = value.toFixed(0) + ' pt';
            break;
        case 'axisFont':
            plotSettings.axisFontSize = value;
            document.getElementById('axisFontValue').textContent = value.toFixed(0) + ' pt';
            break;
        case 'tickFont':
            plotSettings.tickFontSize = value;
            document.getElementById('tickFontValue').textContent = value.toFixed(0) + ' pt';
            break;
        case 'markerSize':
            plotSettings.markerSize = value;
            document.getElementById('markerSizeValue').textContent = value.toFixed(1) + ' mm';
            break;
        case 'numTicks':
            plotSettings.numTicks = Math.round(value);
            document.getElementById('numTicksValue').textContent = Math.round(value);
            break;
        case 'xLabel':
            plotSettings.xLabel = value;
            document.getElementById('xLabelValue').textContent = value;
            break;
        case 'yLabel':
            plotSettings.yLabel = value;
            document.getElementById('yLabelValue').textContent = value;
            break;
    }

    // Re-render if data is loaded
    if (currentCSVData && currentPlots) {
        renderPlots(currentCSVData, currentPlots);
    }
}

function resetToNatureDefaults() {
    // Reset all settings to Nature defaults
    document.getElementById('figureWidth').value = 35;
    updateSetting('width', 35);

    document.getElementById('lineWidth').value = 0.12;
    updateSetting('lineWidth', 0.12);

    document.getElementById('tickLength').value = 0.8;
    updateSetting('tickLength', 0.8);

    document.getElementById('tickWidth').value = 0.2;
    updateSetting('tickWidth', 0.2);

    document.getElementById('axisWidth').value = 0.2;
    updateSetting('axisWidth', 0.2);

    document.getElementById('titleFont').value = 8;
    updateSetting('titleFont', 8);

    document.getElementById('axisFont').value = 8;
    updateSetting('axisFont', 8);

    document.getElementById('tickFont').value = 7;
    updateSetting('tickFont', 7);

    document.getElementById('markerSize').value = 0.8;
    updateSetting('markerSize', 0.8);

    document.getElementById('numTicks').value = 4;
    updateSetting('numTicks', 4);

    document.getElementById('xLabel').value = 'X axis';
    updateSetting('xLabel', 'X axis');

    document.getElementById('yLabel').value = 'Y axis';
    updateSetting('yLabel', 'Y axis');
}

csvFileInput.addEventListener('change', function(e) {
    const file = e.target.files[0];
    if (file) {
        readCSVFile(file);
    }
});

function readCSVFile(file) {
    const reader = new FileReader();
    reader.onload = function(e) {
        const csvText = e.target.result;
        parseAndPlot(csvText, file.name);
    };
    reader.readAsText(file);
}

function downloadPlot() {
    if (!currentPlotData) return;
    const link = document.createElement('a');
    link.download = 'scitex_plot_300dpi.png';
    link.href = plotCanvas.toDataURL('image/png');
    link.click();
}

function parseAndPlot(csvText, filename) {
    // Parse CSV
    const lines = csvText.trim().split('\n');
    const headers = lines[0].split(',');
    const data = {};

    // Initialize arrays for each column
    headers.forEach(header => {
        data[header.trim()] = [];
    });

    // Parse data rows
    for (let i = 1; i < lines.length; i++) {
        const values = lines[i].split(',');
        headers.forEach((header, idx) => {
            const value = parseFloat(values[idx]);
            data[header.trim()].push(isNaN(value) ? null : value);
        });
    }

    // Detect plots from column names
    const plots = detectPlots(headers);

    // Store data for re-rendering
    currentCSVData = data;
    currentPlots = plots;

    // Update info panel
    updateInfoPanel(filename, lines.length - 1, headers.length, plots.length, headers);

    // Show settings button
    document.getElementById('toggleSettings').style.display = 'inline-block';

    // Render plots
    renderPlots(data, plots);
}

function detectPlots(headers) {
    const plots = [];
    const processed = new Set();

    for (const header of headers) {
        if (processed.has(header)) continue;

        // Three patterns to match:
        // 1. Line: ax_00_plot_line_test_line_x, ax_00_plot_line_test_line_y
        // 2. Scatter: ax_00_scatter_test_scatter_x, ax_00_scatter_test_scatter_y
        // 3. Bar: ax_00_bar_test_x, ax_00_bar_test_y

        let match;
        let plotType, plotId, xCol, yCol;

        // Try line pattern: {prefix}_line_x
        match = header.match(/^(ax_\d+_)?(.+?)_line_(x|y)$/);
        if (match && match[3] === 'x') {
            const [, axisPrefix, id] = match;
            plotType = 'line';
            plotId = id;
            xCol = header;
            yCol = headers.find(h => h === (axisPrefix || '') + id + '_line_y');
        }

        // Try scatter pattern: {prefix}_scatter_x
        if (!match || !yCol) {
            match = header.match(/^(ax_\d+_)?(.+?)_scatter_(x|y)$/);
            if (match && match[3] === 'x') {
                const [, axisPrefix, id] = match;
                plotType = 'scatter';
                plotId = id;
                xCol = header;
                yCol = headers.find(h => h === (axisPrefix || '') + id + '_scatter_y');
            }
        }

        // Try bar pattern: {prefix}_x (no type keyword)
        if (!match || !yCol) {
            match = header.match(/^(ax_\d+_)?(.+?)_(x|y)$/);
            if (match && match[3] === 'x') {
                const [, axisPrefix, id] = match;
                // Only treat as bar if it doesn't match line or scatter patterns
                if (!id.endsWith('_line') && !id.endsWith('_scatter')) {
                    plotType = 'bar';
                    plotId = id;
                    xCol = header;
                    yCol = headers.find(h => h === (axisPrefix || '') + id + '_y');
                }
            }
        }

        // Add plot if we found a valid x/y pair
        if (xCol && yCol) {
            plots.push({
                type: plotType,
                id: plotId,
                xColumn: xCol,
                yColumn: yCol,
                axis: header.match(/^ax_\d+/)?.[0] || 'ax_00'
            });
            processed.add(xCol);
            processed.add(yCol);
        }
    }

    return plots;
}

function renderPlots(data, plots) {
    // Nature journal specifications (precise measurements)
    const DPI = 300;
    const MM_TO_PX = DPI / 25.4;  // 1mm = 11.811px at 300 DPI

    // Use dynamic plotSettings instead of hardcoded values
    const SPECS = plotSettings;

    // Nature color palette (RGB)
    const NATURE_COLORS = [
        [0, 128, 192],      // Blue
        [255, 70, 50],      // Red
        [20, 180, 20],      // Green
        [230, 160, 20],     // Yellow
        [200, 50, 255],     // Purple
        [255, 150, 200],    // Pink
        [20, 200, 200],     // Cyan
        [128, 0, 0],        // Brown
        [0, 0, 100],        // Navy
        [228, 94, 50]       // Vermilion
    ];

    // Convert mm to pixels
    const mm = (val) => val * MM_TO_PX;

    // Set canvas size (at 300 DPI)
    const canvasWidth = mm(SPECS.figureWidth);
    const canvasHeight = mm(SPECS.figureHeight);
    plotCanvas.width = canvasWidth;
    plotCanvas.height = canvasHeight;

    const ctx = plotCanvas.getContext('2d');

    // Enable high-quality rendering
    ctx.imageSmoothingEnabled = true;
    ctx.imageSmoothingQuality = 'high';

    // Clear canvas with white background
    ctx.fillStyle = '#ffffff';
    ctx.fillRect(0, 0, canvasWidth, canvasHeight);

    // Define plot area with margins
    const margin = {
        left: mm(8),    // 8mm for y-axis labels
        right: mm(2),   // 2mm
        top: mm(3),     // 3mm for title
        bottom: mm(6)   // 6mm for x-axis labels
    };

    const plotArea = {
        x: margin.left,
        y: margin.top,
        width: canvasWidth - margin.left - margin.right,
        height: canvasHeight - margin.top - margin.bottom
    };

    // Collect all data points for scaling
    let allX = [], allY = [];
    plots.forEach(plot => {
        const xData = data[plot.xColumn].filter(v => v !== null);
        const yData = data[plot.yColumn].filter(v => v !== null);
        allX = allX.concat(xData);
        allY = allY.concat(yData);
    });

    const xMin = Math.min(...allX);
    const xMax = Math.max(...allX);
    const yMin = Math.min(...allY);
    const yMax = Math.max(...allY);

    // Add 5% padding to data range
    const xRange = xMax - xMin;
    const yRange = yMax - yMin;
    const xScale = {
        min: xMin - xRange * 0.05,
        max: xMax + xRange * 0.05
    };
    const yScale = {
        min: yMin - yRange * 0.05,
        max: yMax + yRange * 0.05
    };

    // Coordinate transformation functions
    const toCanvasX = (x) => {
        return plotArea.x + ((x - xScale.min) / (xScale.max - xScale.min)) * plotArea.width;
    };
    const toCanvasY = (y) => {
        return plotArea.y + plotArea.height - ((y - yScale.min) / (yScale.max - yScale.min)) * plotArea.height;
    };

    // Draw axes (0.2mm width per Nature specs)
    ctx.strokeStyle = '#000000';
    ctx.lineWidth = mm(SPECS.axisWidth);
    ctx.beginPath();
    // X-axis
    ctx.moveTo(plotArea.x, plotArea.y + plotArea.height);
    ctx.lineTo(plotArea.x + plotArea.width, plotArea.y + plotArea.height);
    // Y-axis
    ctx.moveTo(plotArea.x, plotArea.y);
    ctx.lineTo(plotArea.x, plotArea.y + plotArea.height);
    ctx.stroke();

    // Draw ticks and labels
    ctx.font = `${SPECS.tickFontSize}pt Arial`;
    ctx.fillStyle = '#000000';
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';

    // X-axis ticks (use dynamic numTicks)
    const xTicks = generateNiceTicks(xScale.min, xScale.max, SPECS.numTicks);
    xTicks.forEach(tick => {
        const x = toCanvasX(tick);
        // Draw tick
        ctx.lineWidth = mm(SPECS.tickWidth);
        ctx.beginPath();
        ctx.moveTo(x, plotArea.y + plotArea.height);
        ctx.lineTo(x, plotArea.y + plotArea.height + mm(SPECS.tickLength));
        ctx.stroke();
        // Draw label
        ctx.fillText(formatNumber(tick), x, plotArea.y + plotArea.height + mm(SPECS.tickLength) + mm(1));
    });

    // Y-axis ticks (use dynamic numTicks)
    ctx.textAlign = 'right';
    ctx.textBaseline = 'middle';
    const yTicks = generateNiceTicks(yScale.min, yScale.max, SPECS.numTicks);
    yTicks.forEach(tick => {
        const y = toCanvasY(tick);
        // Draw tick
        ctx.lineWidth = mm(SPECS.tickWidth);
        ctx.beginPath();
        ctx.moveTo(plotArea.x, y);
        ctx.lineTo(plotArea.x - mm(SPECS.tickLength), y);
        ctx.stroke();
        // Draw label
        ctx.fillText(formatNumber(tick), plotArea.x - mm(SPECS.tickLength) - mm(0.5), y);
    });

    // Draw data plots
    plots.forEach((plot, idx) => {
        const xData = data[plot.xColumn];
        const yData = data[plot.yColumn];
        const color = NATURE_COLORS[idx % NATURE_COLORS.length];
        const colorStr = `rgb(${color[0]}, ${color[1]}, ${color[2]})`;

        if (plot.type === 'line') {
            // Draw line (use dynamic lineWidth)
            ctx.strokeStyle = colorStr;
            ctx.lineWidth = mm(SPECS.lineWidth);
            ctx.beginPath();
            let firstPoint = true;
            for (let i = 0; i < xData.length; i++) {
                if (xData[i] !== null && yData[i] !== null) {
                    const x = toCanvasX(xData[i]);
                    const y = toCanvasY(yData[i]);
                    if (firstPoint) {
                        ctx.moveTo(x, y);
                        firstPoint = false;
                    } else {
                        ctx.lineTo(x, y);
                    }
                }
            }
            ctx.stroke();
        } else if (plot.type === 'scatter') {
            // Draw markers (use dynamic markerSize)
            ctx.fillStyle = colorStr;
            const radius = mm(SPECS.markerSize) / 2;
            for (let i = 0; i < xData.length; i++) {
                if (xData[i] !== null && yData[i] !== null) {
                    const x = toCanvasX(xData[i]);
                    const y = toCanvasY(yData[i]);
                    ctx.beginPath();
                    ctx.arc(x, y, radius, 0, 2 * Math.PI);
                    ctx.fill();
                }
            }
        } else if (plot.type === 'bar') {
            // Draw bars
            ctx.fillStyle = colorStr;
            ctx.strokeStyle = '#000000';
            ctx.lineWidth = mm(SPECS.axisWidth);

            // Calculate bar width
            const barWidth = plotArea.width / xData.length * 0.8; // 80% of available space

            for (let i = 0; i < xData.length; i++) {
                if (xData[i] !== null && yData[i] !== null) {
                    // For categorical x-axis, use index-based positioning
                    const x = plotArea.x + (i + 0.5) * (plotArea.width / xData.length) - barWidth / 2;
                    const y = toCanvasY(yData[i]);
                    const height = plotArea.y + plotArea.height - y;

                    // Draw filled bar
                    ctx.fillRect(x, y, barWidth, height);
                    // Draw bar outline
                    ctx.strokeRect(x, y, barWidth, height);
                }
            }
        }
    });

    // Draw title (centered on figure)
    ctx.font = `${SPECS.titleFontSize}pt Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillStyle = '#000000';
    ctx.fillText('SciTeX Plot', canvasWidth / 2, mm(0.5));

    // Draw X-axis label (centered below x-axis)
    ctx.font = `${SPECS.axisFontSize}pt Arial`;
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(plotSettings.xLabel, plotArea.x + plotArea.width / 2, canvasHeight - mm(1.5));

    // Draw Y-axis label (centered along y-axis, rotated)
    ctx.save();
    ctx.translate(mm(1.5), plotArea.y + plotArea.height / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.textAlign = 'center';
    ctx.textBaseline = 'top';
    ctx.fillText(plotSettings.yLabel, 0, 0);
    ctx.restore();

    // Update size indicator with dynamic values
    document.querySelector('.size-indicator').textContent =
        `Figure size: ${SPECS.figureWidth.toFixed(1)}mm × ${SPECS.figureHeight.toFixed(1)}mm | 300 DPI`;

    // Store data for download
    currentPlotData = { data, plots };

    // Show plot container
    plotContainer.style.display = 'block';
    plotInfo.style.display = 'block';
}

// Helper function to generate nice tick values
function generateNiceTicks(min, max, count) {
    const range = max - min;
    const step = range / (count - 1);
    const magnitude = Math.pow(10, Math.floor(Math.log10(step)));
    const niceStep = Math.ceil(step / magnitude) * magnitude;

    const ticks = [];
    const start = Math.floor(min / niceStep) * niceStep;
    for (let i = 0; i <= count; i++) {
        const tick = start + i * niceStep;
        if (tick >= min && tick <= max) {
            ticks.push(tick);
        }
    }
    return ticks;
}

// Helper function to format numbers for tick labels
function formatNumber(num) {
    if (Math.abs(num) < 0.01 || Math.abs(num) > 10000) {
        return num.toExponential(1);
    }
    return num.toFixed(2).replace(/\.?0+$/, '');
}

function updateInfoPanel(filename, dataPoints, columnCount, plotCount, headers) {
    document.getElementById('filename').textContent = filename;
    document.getElementById('dataPoints').textContent = dataPoints.toLocaleString();
    document.getElementById('columnCount').textContent = columnCount;
    document.getElementById('plotCount').textContent = plotCount;

    const columnList = document.getElementById('columnList');
    columnList.innerHTML = '';

    headers.forEach(header => {
        const div = document.createElement('div');
        div.className = 'column-item';

        // Extract axis info if present
        const axisMatch = header.match(/^ax_(\d+)_/);
        if (axisMatch) {
            const badge = document.createElement('span');
            badge.className = 'axis-badge';
            badge.textContent = `ax_${axisMatch[1]}`;
            div.appendChild(badge);
        }

        div.appendChild(document.createTextNode(header));
        columnList.appendChild(div);
    });
}

function loadDemoData() {
    const demoCSV = `ax_00_plot_line_test_line_x,ax_00_plot_line_test_line_y
0,0.0
1,0.1008384202581046
2,0.2006488565226854
3,0.2984138044476411
4,0.3931366121483298
5,0.48385164043793466
6,0.5696341069089657
7,0.6496095135057065
8,0.7229625614794605
9,0.7889454628442574
10,0.8468855636029834
11,0.8961922010299563
12,0.9363627251042848
13,0.9669876227092996
14,0.9877546923600838
15,0.9984522269003895
16,0.9989711717233568
17,0.9893062365143401
18,0.9695559491823237
19,0.9398954546557377
20,0.900576516328075`;

    parseAndPlot(demoCSV, 'demo_plot_line.csv');
}
