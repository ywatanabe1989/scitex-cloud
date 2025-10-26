// =============================================================================
// PDF.js Viewer for Repository Files
// =============================================================================

// Load PDF.js from CDN
const script = document.createElement('script');
script.src = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.min.js';

let pdfDoc = null;
let currentScale = 1.5;
let currentPage = 1;
let outlineItemsMap = new Map(); // Map of page number to outline item element

// =============================================================================
// UI Controls
// =============================================================================

function toggleSidebar() {
    const sidebar = document.getElementById('pdf-sidebar');
    const overlay = document.getElementById('pdf-overlay');
    sidebar.classList.toggle('open');
    overlay.classList.toggle('open');
}

function zoomIn() {
    currentScale += 0.25;
    renderAllPages();
    document.getElementById('zoom-level').textContent = Math.round(currentScale * 100) + '%';
}

function zoomOut() {
    if (currentScale > 0.5) {
        currentScale -= 0.25;
        renderAllPages();
        document.getElementById('zoom-level').textContent = Math.round(currentScale * 100) + '%';
    }
}

function fitWidth() {
    const container = document.getElementById('pdf-viewer');
    currentScale = (container.clientWidth - 40) / 612; // Standard PDF width
    renderAllPages();
    document.getElementById('zoom-level').textContent = Math.round(currentScale * 100) + '%';
}

function prevPage() {
    if (currentPage > 1) {
        currentPage--;
        document.getElementById('page-input').value = currentPage;
        scrollToPage(currentPage);
    }
}

function nextPage() {
    if (pdfDoc && currentPage < pdfDoc.numPages) {
        currentPage++;
        document.getElementById('page-input').value = currentPage;
        scrollToPage(currentPage);
    }
}

function gotoPage() {
    const pageNum = parseInt(document.getElementById('page-input').value);
    if (pageNum >= 1 && pdfDoc && pageNum <= pdfDoc.numPages) {
        currentPage = pageNum;
        scrollToPage(pageNum);
    }
}

function scrollToPage(pageNum) {
    const pageElement = document.getElementById(`pdf-page-${pageNum}`);
    if (pageElement) {
        pageElement.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }
}

// =============================================================================
// PDF Rendering
// =============================================================================

function renderAllPages() {
    if (!pdfDoc) return;

    const container = document.getElementById('pdf-viewer');
    container.innerHTML = '';

    for (let pageNum = 1; pageNum <= pdfDoc.numPages; pageNum++) {
        const pageContainer = document.createElement('div');
        pageContainer.className = 'pdf-page-container';
        pageContainer.style.cssText = 'margin: 1rem auto; background: white; box-shadow: 0 2px 8px rgba(0,0,0,0.1); position: relative;';
        pageContainer.id = `pdf-page-${pageNum}`;
        pageContainer.dataset.pageNum = pageNum;

        // Add page number label
        const pageLabel = document.createElement('div');
        pageLabel.style.cssText = 'position: absolute; top: -1.5rem; left: 0; font-size: 0.875rem; color: var(--color-fg-muted);';
        pageLabel.textContent = `Page ${pageNum}`;
        pageContainer.appendChild(pageLabel);

        container.appendChild(pageContainer);

        pdfDoc.getPage(pageNum).then(function(page) {
            const viewport = page.getViewport({ scale: currentScale });

            const canvas = document.createElement('canvas');
            const context = canvas.getContext('2d');
            canvas.height = viewport.height;
            canvas.width = viewport.width;
            canvas.style.cssText = 'display: block;';

            pageContainer.appendChild(canvas);

            const renderContext = {
                canvasContext: context,
                viewport: viewport
            };

            page.render(renderContext);
        });
    }

    // Add scroll listener for outline sync
    setupScrollSync();
}

// =============================================================================
// Scroll Synchronization
// =============================================================================

function setupScrollSync() {
    const pdfViewer = document.getElementById('pdf-viewer');
    let scrollTimeout;

    pdfViewer.addEventListener('scroll', function() {
        clearTimeout(scrollTimeout);
        scrollTimeout = setTimeout(function() {
            updateCurrentPageFromScroll();
        }, 100);
    });
}

function updateCurrentPageFromScroll() {
    const pdfViewer = document.getElementById('pdf-viewer');
    const pages = pdfViewer.querySelectorAll('.pdf-page-container');

    let visiblePage = 1;
    const scrollTop = pdfViewer.scrollTop;
    const viewportMiddle = scrollTop + pdfViewer.clientHeight / 3;

    for (const page of pages) {
        const pageTop = page.offsetTop;
        const pageBottom = pageTop + page.offsetHeight;

        if (viewportMiddle >= pageTop && viewportMiddle < pageBottom) {
            visiblePage = parseInt(page.dataset.pageNum);
            break;
        }
    }

    if (visiblePage !== currentPage) {
        currentPage = visiblePage;
        document.getElementById('page-input').value = currentPage;
        highlightActiveOutlineItem(currentPage);
    }
}

function highlightActiveOutlineItem(pageNum, autoScroll = true) {
    // Remove all active classes
    document.querySelectorAll('.pdf-outline-item').forEach(item => {
        item.classList.remove('active');
    });

    // Find and highlight the outline item for this page
    const outlineItem = outlineItemsMap.get(pageNum);
    if (outlineItem) {
        outlineItem.classList.add('active');

        // Only auto-scroll outline if enabled (from PDF scrolling, not clicks)
        if (autoScroll) {
            const outlineContainer = document.getElementById('pdf-outline');
            if (outlineContainer) {
                const itemTop = outlineItem.offsetTop;
                const itemBottom = itemTop + outlineItem.offsetHeight;
                const containerScrollTop = outlineContainer.scrollTop;
                const containerHeight = outlineContainer.clientHeight;

                // Only scroll if item is not visible
                if (itemTop < containerScrollTop || itemBottom > containerScrollTop + containerHeight) {
                    outlineContainer.scrollTop = itemTop - containerHeight / 3;
                }
            }
        }
    }
}

// =============================================================================
// PDF Loading and Outline
// =============================================================================

script.onload = function() {
    pdfjsLib.GlobalWorkerOptions.workerSrc = 'https://cdnjs.cloudflare.com/ajax/libs/pdf.js/3.11.174/pdf.worker.min.js';

    const projectData = window.SCITEX_PROJECT_DATA;
    const filePath = window.SCITEX_FILE_PATH;

    if (!projectData || !filePath) {
        console.error('Missing project data or file path');
        return;
    }

    const pdfUrl = `/${projectData.owner}/${projectData.slug}/blob/${filePath}?mode=raw`;
    const container = document.getElementById('pdf-viewer');
    container.innerHTML = '<div style="text-align: center; padding: 2rem;"><i class="fas fa-spinner fa-spin"></i> Loading PDF...</div>';

    pdfjsLib.getDocument(pdfUrl).promise.then(function(pdf) {
        pdfDoc = pdf;
        document.getElementById('page-count').textContent = pdf.numPages;
        renderAllPages();

        // Load PDF outline/bookmarks
        pdf.getOutline().then(function(outline) {
            const outlineContainer = document.getElementById('pdf-outline');
            console.log('PDF Outline:', outline);

            if (outline && outline.length > 0) {
                outlineContainer.innerHTML = '';

                function renderOutlineItem(item, level = 1) {
                    const wrapper = document.createElement('div');

                    const itemDiv = document.createElement('div');
                    itemDiv.className = `pdf-outline-item level-${level}`;

                    // Store page mapping for scroll sync
                    if (item.dest) {
                        pdf.getDestination(item.dest).then(function(dest) {
                            if (dest) {
                                pdf.getPageIndex(dest[0]).then(function(pageIndex) {
                                    const pageNum = pageIndex + 1;
                                    outlineItemsMap.set(pageNum, itemDiv);
                                });
                            }
                        });
                    }

                    // Add toggle icon if item has children
                    const hasChildren = item.items && item.items.length > 0;

                    let toggle = null;
                    let childrenContainer = null;

                    if (hasChildren) {
                        toggle = document.createElement('span');
                        toggle.className = 'outline-toggle collapsed';
                        toggle.innerHTML = '▼';
                        itemDiv.appendChild(toggle);
                    } else {
                        // Add spacer for items without children
                        const spacer = document.createElement('span');
                        spacer.style.width = '16px';
                        spacer.style.flexShrink = '0';
                        itemDiv.appendChild(spacer);
                    }

                    // Add title
                    const titleSpan = document.createElement('span');
                    titleSpan.className = 'outline-title';
                    titleSpan.textContent = item.title;
                    titleSpan.onclick = function(e) {
                        e.preventDefault();
                        // Get destination and navigate
                        if (item.dest) {
                            pdf.getDestination(item.dest).then(function(dest) {
                                if (dest) {
                                    pdf.getPageIndex(dest[0]).then(function(pageIndex) {
                                        const targetPage = pageIndex + 1;
                                        currentPage = targetPage;
                                        document.getElementById('page-input').value = targetPage;

                                        // Scroll PDF viewer to the page
                                        const pdfViewer = document.getElementById('pdf-viewer');
                                        const pageElement = document.getElementById(`pdf-page-${targetPage}`);
                                        if (pageElement && pdfViewer) {
                                            const pageTop = pageElement.offsetTop - pdfViewer.offsetTop;
                                            pdfViewer.scrollTop = pageTop;
                                        }

                                        highlightActiveOutlineItem(targetPage, false); // Don't auto-scroll outline on click

                                        if (window.innerWidth < 768) {
                                            toggleSidebar();
                                        }
                                    });
                                }
                            });
                        }
                    };
                    itemDiv.appendChild(titleSpan);

                    wrapper.appendChild(itemDiv);

                    // Render children in a collapsible container
                    if (hasChildren) {
                        childrenContainer = document.createElement('div');
                        childrenContainer.className = 'outline-children collapsed';
                        childrenContainer.style.maxHeight = '0';

                        item.items.forEach(child => {
                            const childElement = renderOutlineItem(child, level + 1);
                            childrenContainer.appendChild(childElement);
                        });

                        wrapper.appendChild(childrenContainer);

                        // Add click handler to toggle after childrenContainer is created
                        toggle.onclick = function(e) {
                            e.stopPropagation();
                            toggle.classList.toggle('collapsed');
                            childrenContainer.classList.toggle('collapsed');
                            if (childrenContainer.classList.contains('collapsed')) {
                                childrenContainer.style.maxHeight = '0';
                            } else {
                                childrenContainer.style.maxHeight = childrenContainer.scrollHeight + 'px';
                            }
                        };
                    }

                    return wrapper;
                }

                outline.forEach(item => {
                    outlineContainer.appendChild(renderOutlineItem(item));
                });
            } else {
                outlineContainer.innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--color-fg-muted);">No outline available</div>';
            }
        }).catch(function() {
            document.getElementById('pdf-outline').innerHTML = '<div style="text-align: center; padding: 2rem; color: var(--color-fg-muted);">No outline available</div>';
        });

    }).catch(function(error) {
        const errorHtml = `
            <div style="text-align: center; padding: 2rem; color: #d73a49;">
                <i class="fas fa-exclamation-triangle"></i>
                <p>Error loading PDF: ${error.message}</p>
                <p><a href="/${projectData.owner}/${projectData.slug}/blob/${filePath}?mode=raw" class="btn btn-primary" download>Download PDF</a></p>
            </div>
        `;
        container.innerHTML = errorHtml;
    });
};

document.head.appendChild(script);
