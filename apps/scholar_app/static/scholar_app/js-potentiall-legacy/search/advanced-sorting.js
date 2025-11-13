/**
 * Advanced Multi-Level Sorting Controls
 * Allows users to sort by multiple criteria in order (like pandas multi-column sorting)
 */

(function () {
  "use strict";

  // Multi-level sorting state
  let sortCriteria = [];

  // Initialize on DOM ready
  document.addEventListener("DOMContentLoaded", function () {
    initializeAdvancedSorting();
    initializeResultSelection();
    initializeRangeFilters();
  });

  function initializeAdvancedSorting() {
    const advancedSortBtn = document.getElementById("toggleAdvancedSort");
    if (!advancedSortBtn) return;

    advancedSortBtn.addEventListener("click", function (e) {
      e.preventDefault();
      const container = document.getElementById("advancedSortContainer");
      if (container) {
        container.style.display =
          container.style.display === "none" ? "block" : "none";
      }
    });

    // Add event listeners to sort criterion buttons
    document.querySelectorAll(".sort-criterion-btn").forEach((btn) => {
      btn.addEventListener("click", function (e) {
        e.preventDefault();
        const field = this.dataset.field;
        const order = this.dataset.order;
        addSortCriterionByButton(field, order, this);
      });
    });

    // Clear all button
    const clearBtn = document.getElementById("clearSortCriteria");
    if (clearBtn) {
      clearBtn.addEventListener("click", function (e) {
        e.preventDefault();
        sortCriteria = [];
        renderSortCriteria();
        updateHiddenSortInput();
        // Reset button states
        document.querySelectorAll(".sort-criterion-btn").forEach((btn) => {
          btn.classList.remove("active");
          btn.classList.add("btn-outline-primary");
          btn.classList.remove("btn-primary");
          const badge = btn.querySelector(".badge");
          if (badge) badge.remove();
        });
      });
    }

    // Initialize with existing sort parameters if present
    const urlParams = new URLSearchParams(window.location.search);
    const sortBy = urlParams.get("sort_by");
    if (sortBy && sortBy.includes(",")) {
      // Multi-level sort detected
      parseSortCriteria(sortBy);
      renderSortCriteria();
    }
  }

  function parseSortCriteria(sortByString) {
    sortCriteria = [];
    const criteria = sortByString.split(",");
    criteria.forEach((criterion) => {
      const parts = criterion.split(":");
      if (parts.length === 2) {
        sortCriteria.push({
          field: parts[0].trim(),
          order: parts[1].trim(),
        });
      }
    });
  }

  function addSortCriterionByButton(field, order, buttonElement) {
    // Check if already exists
    const existingIndex = sortCriteria.findIndex((c) => c.field === field);

    if (existingIndex >= 0) {
      // Remove if clicking again
      sortCriteria.splice(existingIndex, 1);
      buttonElement.classList.remove("active", "btn-primary");
      buttonElement.classList.add("btn-outline-primary");
      const badge = buttonElement.querySelector(".badge");
      if (badge) badge.remove();
    } else {
      // Add new criterion
      sortCriteria.push({ field, order });
      buttonElement.classList.add("active", "btn-primary");
      buttonElement.classList.remove("btn-outline-primary");

      // Add priority badge
      const priorityBadge = document.createElement("span");
      priorityBadge.className = "badge bg-warning text-dark ms-1";
      priorityBadge.textContent = sortCriteria.length;
      buttonElement.appendChild(priorityBadge);
    }

    // Update all badges to reflect current order
    updateButtonPriorities();
    renderSortCriteria();
    updateHiddenSortInput();
  }

  function updateButtonPriorities() {
    // Clear all badges first
    document
      .querySelectorAll(".sort-criterion-btn .badge")
      .forEach((badge) => badge.remove());

    // Add badges in priority order
    sortCriteria.forEach((criterion, index) => {
      const button = document.querySelector(
        `.sort-criterion-btn[data-field="${criterion.field}"]`,
      );
      if (button) {
        const badge = document.createElement("span");
        badge.className = "badge bg-warning text-dark ms-1";
        badge.textContent = index + 1;
        button.appendChild(badge);
      }
    });
  }

  function addSortCriterion() {
    const field = document.getElementById("sortFieldSelect")?.value;
    const order = document.getElementById("sortOrderSelect")?.value;

    if (!field || field === "relevance") return;

    // Check if already exists
    const exists = sortCriteria.some((c) => c.field === field);
    if (exists) {
      alert(`Already sorting by ${field}`);
      return;
    }

    sortCriteria.push({ field, order });
    renderSortCriteria();
    updateHiddenSortInput();
  }

  function removeSortCriterion(index) {
    sortCriteria.splice(index, 1);
    renderSortCriteria();
    updateHiddenSortInput();
  }

  function moveSortCriterion(index, direction) {
    if (direction === "up" && index > 0) {
      [sortCriteria[index], sortCriteria[index - 1]] = [
        sortCriteria[index - 1],
        sortCriteria[index],
      ];
    } else if (direction === "down" && index < sortCriteria.length - 1) {
      [sortCriteria[index], sortCriteria[index + 1]] = [
        sortCriteria[index + 1],
        sortCriteria[index],
      ];
    }
    renderSortCriteria();
    updateHiddenSortInput();
  }

  function renderSortCriteria() {
    const container = document.getElementById("sortCriteriaList");
    if (!container) return;

    if (sortCriteria.length === 0) {
      container.innerHTML =
        '<p class="text-muted small">No multi-level sorting configured. Add criteria above.</p>';
      return;
    }

    let html = '<div class="list-group list-group-flush">';
    sortCriteria.forEach((criterion, index) => {
      const fieldLabel = getFieldLabel(criterion.field);
      const orderLabel =
        criterion.order === "desc" ? "↓ High to Low" : "↑ Low to High";

      html += `
                <div class="list-group-item d-flex justify-content-between align-items-center p-2">
                    <div>
                        <strong>${index + 1}.</strong>
                        <span class="badge bg-primary">${fieldLabel}</span>
                        <span class="badge bg-secondary">${orderLabel}</span>
                    </div>
                    <div class="btn-group btn-group-sm" role="group">
                        ${index > 0 ? `<button type="button" class="btn btn-outline-secondary" onclick="window.scholarSorting.moveCriterion(${index}, 'up')" title="Move up"><i class="fas fa-arrow-up"></i></button>` : ""}
                        ${index < sortCriteria.length - 1 ? `<button type="button" class="btn btn-outline-secondary" onclick="window.scholarSorting.moveCriterion(${index}, 'down')" title="Move down"><i class="fas fa-arrow-down"></i></button>` : ""}
                        <button type="button" class="btn btn-outline-danger" onclick="window.scholarSorting.removeCriterion(${index})" title="Remove"><i class="fas fa-times"></i></button>
                    </div>
                </div>
            `;
    });
    html += "</div>";

    container.innerHTML = html;
  }

  function getFieldLabel(field) {
    const labels = {
      citations: "Citations",
      year: "Year",
      title: "Title",
      impact_factor: "Impact Factor",
    };
    return labels[field] || field;
  }

  function updateHiddenSortInput() {
    // Update the hidden input or main sort_by field with comma-separated criteria
    const sortByInput = document.querySelector('select[name="sort_by"]');
    if (!sortByInput) return;

    if (sortCriteria.length === 0) {
      sortByInput.value = "relevance";
    } else if (sortCriteria.length === 1) {
      sortByInput.value = sortCriteria[0].field;
      const orderSelect = document.querySelector('select[name="sort_order"]');
      if (orderSelect) {
        orderSelect.value = sortCriteria[0].order;
      }
    } else {
      // Multi-level: create comma-separated string
      const sortString = sortCriteria
        .map((c) => `${c.field}:${c.order}`)
        .join(",");
      sortByInput.value = sortString;
    }
  }

  // Paper selection functionality
  function initializeResultSelection() {
    const selectAllBtn = document.getElementById("selectAllResults");
    const deselectAllBtn = document.getElementById("deselectAllResults");
    const exportSelectedBtn = document.getElementById("exportSelectedBibtex");

    if (selectAllBtn) {
      selectAllBtn.addEventListener("click", function () {
        document.querySelectorAll(".paper-select-checkbox").forEach((cb) => {
          cb.checked = true;
        });
        updateSelectionCount();
      });
    }

    if (deselectAllBtn) {
      deselectAllBtn.addEventListener("click", function () {
        document.querySelectorAll(".paper-select-checkbox").forEach((cb) => {
          cb.checked = false;
        });
        updateSelectionCount();
      });
    }

    if (exportSelectedBtn) {
      exportSelectedBtn.addEventListener("click", exportSelectedPapers);
    }

    // Add event listeners to checkboxes
    document.querySelectorAll(".paper-select-checkbox").forEach((cb) => {
      cb.addEventListener("change", updateSelectionCount);
    });

    updateSelectionCount();
  }

  function updateSelectionCount() {
    const selectedCount = document.querySelectorAll(
      ".paper-select-checkbox:checked",
    ).length;
    const totalCount = document.querySelectorAll(
      ".paper-select-checkbox",
    ).length;

    const countDisplay = document.getElementById("selectedCount");
    if (countDisplay) {
      countDisplay.textContent = `${selectedCount} of ${totalCount} selected`;
    }

    const exportBtn = document.getElementById("exportSelectedBibtex");
    if (exportBtn) {
      exportBtn.disabled = selectedCount === 0;
    }
  }

  function exportSelectedPapers() {
    const selectedPaperIds = Array.from(
      document.querySelectorAll(".paper-select-checkbox:checked"),
    )
      .map((cb) => cb.dataset.paperId)
      .filter((id) => id);

    if (selectedPaperIds.length === 0) {
      alert("Please select at least one paper to export.");
      return;
    }

    // Get CSRF token
    const csrfToken =
      document.querySelector("[name=csrfmiddlewaretoken]")?.value ||
      getCookie("csrftoken");

    if (!csrfToken) {
      alert("CSRF token not found. Please refresh the page and try again.");
      return;
    }

    // Send to export endpoint via fetch
    fetch("/scholar/api/export/bibtex/", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        "X-CSRFToken": csrfToken,
      },
      body: JSON.stringify({
        paper_ids: selectedPaperIds,
        collection_name: "search_results",
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          // Create a blob and download
          const blob = new Blob([data.content], { type: "text/plain" });
          const url = window.URL.createObjectURL(blob);
          const a = document.createElement("a");
          a.href = url;
          a.download = data.filename;
          document.body.appendChild(a);
          a.click();
          window.URL.revokeObjectURL(url);
          document.body.removeChild(a);

          alert(`Successfully exported ${data.count} papers as BibTeX!`);
        } else {
          alert("Export failed: " + (data.error || "Unknown error"));
        }
      })
      .catch((error) => {
        console.error("Export error:", error);
        alert("Failed to export papers. Please try again.");
      });
  }

  // Helper function to get cookie
  function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== "") {
      const cookies = document.cookie.split(";");
      for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.substring(0, name.length + 1) === name + "=") {
          cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
          break;
        }
      }
    }
    return cookieValue;
  }

  // Dual-range filter synchronization with swarm plot integration
  function initializeRangeFilters() {
    // Initialize Year dual-range slider
    initializeDualRangeSlider({
      minSlider: document.getElementById("yearRangeSliderMin"),
      maxSlider: document.getElementById("yearRangeSliderMax"),
      minInput: document.getElementById("yearFromInput"),
      maxInput: document.getElementById("yearToInput"),
      highlight: document.getElementById("yearRangeHighlight"),
      min: 1900,
      max: 2025,
      swarmPlotId: "yearSwarmPlot",
      field: "year",
    });

    // Initialize Citations dual-range slider
    initializeDualRangeSlider({
      minSlider: document.getElementById("citationsRangeSliderMin"),
      maxSlider: document.getElementById("citationsRangeSliderMax"),
      minInput: document.getElementById("citationsMinInput"),
      maxInput: document.getElementById("citationsMaxInput"),
      highlight: document.getElementById("citationsRangeHighlight"),
      min: 0,
      max: 12000,
      swarmPlotId: "citationsSwarmPlot",
      field: "citations",
    });

    // Initialize Impact Factor dual-range slider
    initializeDualRangeSlider({
      minSlider: document.getElementById("impactFactorRangeSliderMin"),
      maxSlider: document.getElementById("impactFactorRangeSliderMax"),
      minInput: document.getElementById("impactFactorMinInput"),
      maxInput: document.getElementById("impactFactorMaxInput"),
      highlight: document.getElementById("impactFactorRangeHighlight"),
      min: 0,
      max: 50,
      swarmPlotId: "impactFactorSwarmPlot",
      field: "impact_factor",
    });
  }

  function initializeDualRangeSlider(config) {
    const {
      minSlider,
      maxSlider,
      minInput,
      maxInput,
      highlight,
      min,
      max,
      swarmPlotId,
      field,
    } = config;

    if (!minSlider || !maxSlider || !minInput || !maxInput || !highlight)
      return;

    // Enable both sliders for dual-range
    minSlider.style.pointerEvents = "auto";
    minSlider.style.opacity = "1";
    maxSlider.style.pointerEvents = "auto";

    // Style the sliders - proper z-index management
    const styleSliders = () => {
      const minVal = parseInt(minSlider.value);
      const maxVal = parseInt(maxSlider.value);
      const midpoint = (max + min) / 2;

      // Put the slider with higher value on top so thumbs don't overlap
      if (Math.abs(minVal - maxVal) < (max - min) * 0.05) {
        // Values very close - use midpoint logic
        minSlider.style.zIndex = minVal > midpoint ? "5" : "3";
        maxSlider.style.zIndex = maxVal > midpoint ? "3" : "5";
      } else {
        // Standard case - max slider always on top
        minSlider.style.zIndex = "3";
        maxSlider.style.zIndex = "5";
      }
    };

    // Update highlight bar position
    const updateHighlight = () => {
      const minVal = parseInt(minSlider.value);
      const maxVal = parseInt(maxSlider.value);

      // Ensure min <= max
      if (minVal > maxVal) {
        if (minSlider === document.activeElement) {
          minSlider.value = maxVal;
          minInput.value = maxVal;
        } else {
          maxSlider.value = minVal;
          maxInput.value = minVal;
        }
        return;
      }

      const percent1 = ((minVal - min) / (max - min)) * 100;
      const percent2 = ((maxVal - min) / (max - min)) * 100;

      highlight.style.left = percent1 + "%";
      highlight.style.width = percent2 - percent1 + "%";

      styleSliders();

      // Update swarm plot selection if it exists
      updateSwarmPlotSelection(swarmPlotId, field, minVal, maxVal);
    };

    // Event listeners for both sliders
    minSlider.addEventListener("input", function () {
      minInput.value = this.value;
      updateHighlight();
    });

    maxSlider.addEventListener("input", function () {
      maxInput.value = this.value;
      updateHighlight();
    });

    // Event listeners for both input boxes
    minInput.addEventListener("input", function () {
      const val = Math.max(min, Math.min(max, parseInt(this.value) || min));
      minSlider.value = val;
      this.value = val;
      updateHighlight();
    });

    maxInput.addEventListener("input", function () {
      const val = Math.max(min, Math.min(max, parseInt(this.value) || max));
      maxSlider.value = val;
      this.value = val;
      updateHighlight();
    });

    // Initialize highlight position
    updateHighlight();
  }

  // Update swarm plot selection based on range slider values
  function updateSwarmPlotSelection(swarmPlotId, field, minVal, maxVal) {
    const swarmPlot = document.getElementById(swarmPlotId);
    if (!swarmPlot) return;

    const svg = swarmPlot.querySelector("svg");
    if (!svg) return;

    // Update visual selection on swarm plot
    const circles = svg.querySelectorAll("circle[data-paper-id]");
    circles.forEach((circle) => {
      const paperId = circle.dataset.paperId;
      const card = document.querySelector(
        `.result-card[data-paper-id="${paperId}"]`,
      );
      if (!card) return;

      let value;
      if (field === "year") {
        value = parseInt(card.dataset.year);
      } else if (field === "citations") {
        const citationText = card.textContent.match(/(\d+)\s+citations/);
        value = citationText ? parseInt(citationText[1]) : null;
      } else if (field === "impact_factor") {
        // Would need impact factor data in card
        return;
      }

      if (value !== null && value >= minVal && value <= maxVal) {
        circle.setAttribute("fill", "var(--scitex-color-03)");
        circle.setAttribute("opacity", "0.9");
      } else {
        circle.setAttribute("fill", "var(--scitex-color-05)");
        circle.setAttribute("opacity", "0.3");
      }
    });
  }

  // Generate histograms and swarm plots from search results
  function generateHistograms() {
    // Collect paper data from result cards
    const paperCards = document.querySelectorAll(".result-card");
    if (paperCards.length === 0) return;

    const papers = [];

    paperCards.forEach((card) => {
      const paperId = card.dataset.paperId;
      const year = parseInt(card.dataset.year);

      // Extract citations from the text content
      const citationText = card.textContent.match(/(\d+)\s+citations/);
      const citations = citationText ? parseInt(citationText[1]) : null;

      papers.push({
        id: paperId,
        year: year,
        citations: citations,
        card: card,
      });
    });

    // Generate visualizations
    if (papers.length > 0) {
      const years = papers.filter((p) => p.year).map((p) => p.year);
      const citations = papers
        .filter((p) => p.citations !== null)
        .map((p) => p.citations);

      // Histograms
      if (years.length > 0) {
        renderHistogram("yearHistogram", years, 10, 1900, 2025);
      }

      if (citations.length > 0) {
        const citationBins = [0, 10, 50, 100, 500, 1000, 5000, 10000];
        renderHistogramBinned("citationsHistogram", citations, citationBins);
      }

      // Swarm plots
      renderSwarmPlot(
        "yearSwarmPlot",
        papers.filter((p) => p.year),
        "year",
        1900,
        2025,
      );
      renderSwarmPlot(
        "citationsSwarmPlot",
        papers.filter((p) => p.citations !== null),
        "citations",
        0,
        12000,
      );
    }
  }

  function renderHistogram(containerId, data, numBins, minVal, maxVal) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Create bins
    const binSize = (maxVal - minVal) / numBins;
    const bins = new Array(numBins).fill(0);

    data.forEach((value) => {
      const binIndex = Math.floor((value - minVal) / binSize);
      if (binIndex >= 0 && binIndex < numBins) {
        bins[binIndex]++;
      }
    });

    // Find max for scaling
    const maxCount = Math.max(...bins, 1);

    // Render bars
    container.innerHTML = "";
    bins.forEach((count, index) => {
      const bar = document.createElement("div");
      const height = (count / maxCount) * 100;
      bar.style.flex = "1";
      bar.style.height = `${height}%`;
      bar.style.background =
        count > 0 ? "var(--scitex-color-05)" : "var(--color-border-default)";
      bar.style.borderRadius = "2px";
      bar.style.opacity = count > 0 ? "0.7" : "0.2";
      bar.style.transition = "all 0.2s";
      bar.title = `${Math.round(minVal + index * binSize)}-${Math.round(minVal + (index + 1) * binSize)}: ${count} papers`;

      // Hover effect
      bar.addEventListener("mouseenter", function () {
        this.style.opacity = "1";
        this.style.background = "var(--scitex-color-03)";
      });
      bar.addEventListener("mouseleave", function () {
        this.style.opacity = count > 0 ? "0.7" : "0.2";
        this.style.background =
          count > 0 ? "var(--scitex-color-05)" : "var(--color-border-default)";
      });

      container.appendChild(bar);
    });
  }

  function renderHistogramBinned(containerId, data, bins) {
    const container = document.getElementById(containerId);
    if (!container) return;

    // Count items in each bin
    const counts = new Array(bins.length - 1).fill(0);

    data.forEach((value) => {
      for (let i = 0; i < bins.length - 1; i++) {
        if (value >= bins[i] && value < bins[i + 1]) {
          counts[i]++;
          break;
        }
      }
    });

    // Find max for scaling
    const maxCount = Math.max(...counts, 1);

    // Render bars
    container.innerHTML = "";
    counts.forEach((count, index) => {
      const bar = document.createElement("div");
      const height = (count / maxCount) * 100;
      bar.style.flex = "1";
      bar.style.height = `${height}%`;
      bar.style.background =
        count > 0 ? "var(--scitex-color-05)" : "var(--color-border-default)";
      bar.style.borderRadius = "2px";
      bar.style.opacity = count > 0 ? "0.7" : "0.2";
      bar.style.transition = "all 0.2s";
      bar.title = `${bins[index]}-${bins[index + 1]}: ${count} papers`;

      // Hover effect
      bar.addEventListener("mouseenter", function () {
        this.style.opacity = "1";
        this.style.background = "var(--scitex-color-03)";
      });
      bar.addEventListener("mouseleave", function () {
        this.style.opacity = count > 0 ? "0.7" : "0.2";
        this.style.background =
          count > 0 ? "var(--scitex-color-05)" : "var(--color-border-default)";
      });

      container.appendChild(bar);
    });
  }

  // Generate histograms when Advanced Filters are shown
  const advancedFiltersBtn = document.getElementById("toggleAdvancedFilters");
  if (advancedFiltersBtn) {
    advancedFiltersBtn.addEventListener("click", function () {
      setTimeout(generateHistograms, 100); // Small delay to ensure filters are visible
    });
  }

  // Swarm plot rendering with cross-filtering and range selection
  function renderSwarmPlot(containerId, papers, field, minVal, maxVal) {
    const container = document.getElementById(containerId);
    if (!container || papers.length === 0) return;

    container.innerHTML = "";
    container.style.position = "relative";
    container.style.height = "60px";
    container.style.background = "var(--color-canvas-subtle)";
    container.style.borderRadius = "4px";
    container.style.padding = "4px";
    container.style.marginBottom = "8px";

    const width = container.offsetWidth;
    const height = 52; // Container height minus padding
    const dotRadius = 3;

    // Range selection state
    let rangeSelection = {
      active: false,
      startX: null,
      endX: null,
    };

    // Position dots with jitter to prevent overlap
    const positions = [];
    papers.forEach((paper, index) => {
      const value = paper[field];
      if (value === null || value === undefined) return;

      // Calculate x position based on value
      const x = ((value - minVal) / (maxVal - minVal)) * width;

      // Calculate y position with jitter to prevent overlap
      let y = height / 2;
      let attempts = 0;
      const maxAttempts = 50;

      while (attempts < maxAttempts) {
        const tooClose = positions.some((pos) => {
          const dist = Math.sqrt(
            Math.pow(pos.x - x, 2) + Math.pow(pos.y - y, 2),
          );
          return dist < dotRadius * 2.5;
        });

        if (!tooClose) break;

        // Add jitter
        const jitter = (Math.random() - 0.5) * height * 0.7;
        y = height / 2 + jitter;
        attempts++;
      }

      positions.push({ x, y, paper });
    });

    // Create SVG for better rendering
    const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg");
    svg.setAttribute("width", width);
    svg.setAttribute("height", height);
    svg.style.overflow = "visible";

    // Render dots
    positions.forEach(({ x, y, paper }) => {
      const circle = document.createElementNS(
        "http://www.w3.org/2000/svg",
        "circle",
      );
      circle.setAttribute("cx", x);
      circle.setAttribute("cy", y);
      circle.setAttribute("r", dotRadius);
      circle.setAttribute("fill", "var(--scitex-color-05)");
      circle.setAttribute("opacity", "0.7");
      circle.setAttribute("stroke", "var(--color-border-default)");
      circle.setAttribute("stroke-width", "0.5");
      circle.style.cursor = "pointer";
      circle.style.transition = "all 0.2s";

      // Store paper reference
      circle.dataset.paperId = paper.id;

      // Tooltip
      const titleText = paper.card
        ? paper.card.querySelector(".result-title")?.textContent.trim()
        : "";
      circle.innerHTML = `<title>${titleText}\n${field}: ${paper[field]}</title>`;

      // Click to select/filter
      circle.addEventListener("click", function () {
        const checkbox = document.getElementById(`select_${paper.id}`);
        if (checkbox) {
          checkbox.checked = !checkbox.checked;
          updateSelectionCount();
        }

        // Visual feedback
        if (checkbox && checkbox.checked) {
          this.setAttribute("fill", "var(--scitex-color-03)");
          this.setAttribute("r", dotRadius * 1.3);
          this.setAttribute("stroke-width", "1.5");
        } else {
          this.setAttribute("fill", "var(--scitex-color-05)");
          this.setAttribute("r", dotRadius);
          this.setAttribute("stroke-width", "0.5");
        }
      });

      // Hover effect
      circle.addEventListener("mouseenter", function () {
        this.setAttribute("opacity", "1");
        this.setAttribute("r", dotRadius * 1.2);
        this.setAttribute("stroke", "var(--scitex-color-03)");
        this.setAttribute("stroke-width", "1.5");

        // Highlight corresponding card
        if (paper.card) {
          paper.card.style.outline = "2px solid var(--scitex-color-03)";
          paper.card.scrollIntoView({ behavior: "smooth", block: "nearest" });
        }
      });

      circle.addEventListener("mouseleave", function () {
        const checkbox = document.getElementById(`select_${paper.id}`);
        const isSelected = checkbox && checkbox.checked;

        this.setAttribute("opacity", "0.7");
        this.setAttribute("r", isSelected ? dotRadius * 1.3 : dotRadius);
        this.setAttribute("stroke", "var(--color-border-default)");
        this.setAttribute("stroke-width", isSelected ? "1.5" : "0.5");

        // Remove card highlight
        if (paper.card) {
          paper.card.style.outline = "";
        }
      });

      svg.appendChild(circle);
    });

    // Create range selection overlay (rectangle)
    const rangeRect = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "rect",
    );
    rangeRect.setAttribute("x", 0);
    rangeRect.setAttribute("y", 0);
    rangeRect.setAttribute("width", 0);
    rangeRect.setAttribute("height", height);
    rangeRect.setAttribute("fill", "var(--scitex-color-03)");
    rangeRect.setAttribute("opacity", "0.2");
    rangeRect.setAttribute("stroke", "var(--scitex-color-03)");
    rangeRect.setAttribute("stroke-width", "1");
    rangeRect.style.pointerEvents = "none";
    rangeRect.style.display = "none";
    svg.appendChild(rangeRect);

    // Add drag selection handlers to SVG
    svg.addEventListener("mousedown", function (e) {
      const rect = svg.getBoundingClientRect();
      rangeSelection.active = true;
      rangeSelection.startX = e.clientX - rect.left;
      rangeSelection.endX = rangeSelection.startX;
      rangeRect.style.display = "block";
      updateRangeRect();
    });

    svg.addEventListener("mousemove", function (e) {
      if (!rangeSelection.active) return;
      const rect = svg.getBoundingClientRect();
      rangeSelection.endX = e.clientX - rect.left;
      updateRangeRect();
    });

    svg.addEventListener("mouseup", function (e) {
      if (!rangeSelection.active) return;
      rangeSelection.active = false;

      // Select all papers within range
      const minX = Math.min(rangeSelection.startX, rangeSelection.endX);
      const maxX = Math.max(rangeSelection.startX, rangeSelection.endX);

      positions.forEach(({ x, paper }) => {
        if (x >= minX && x <= maxX) {
          const checkbox = document.getElementById(`select_${paper.id}`);
          if (checkbox) {
            checkbox.checked = true;
            // Update visual state of corresponding dot
            const circle = svg.querySelector(
              `circle[data-paper-id="${paper.id}"]`,
            );
            if (circle) {
              circle.setAttribute("fill", "var(--scitex-color-03)");
              circle.setAttribute("r", dotRadius * 1.3);
              circle.setAttribute("stroke-width", "1.5");
            }
          }
        }
      });

      updateSelectionCount();

      // Hide range rect after a brief moment
      setTimeout(() => {
        rangeRect.style.display = "none";
      }, 300);
    });

    svg.addEventListener("mouseleave", function () {
      if (rangeSelection.active) {
        rangeSelection.active = false;
        rangeRect.style.display = "none";
      }
    });

    function updateRangeRect() {
      const minX = Math.min(rangeSelection.startX, rangeSelection.endX);
      const maxX = Math.max(rangeSelection.startX, rangeSelection.endX);
      rangeRect.setAttribute("x", minX);
      rangeRect.setAttribute("width", maxX - minX);
    }

    container.appendChild(svg);

    // Add axis labels
    const axisLabel = document.createElement("div");
    axisLabel.style.display = "flex";
    axisLabel.style.justifyContent = "space-between";
    axisLabel.style.fontSize = "10px";
    axisLabel.style.color = "var(--color-fg-muted)";
    axisLabel.style.marginTop = "2px";
    axisLabel.innerHTML = `<span>${minVal}</span><span>${field.charAt(0).toUpperCase() + field.slice(1)} (drag to select range)</span><span>${maxVal}${field === "citations" ? "+" : ""}</span>`;
    container.appendChild(axisLabel);
  }

  // Generate on page load if results exist
  if (document.querySelectorAll(".result-card").length > 0) {
    setTimeout(generateHistograms, 500);
  }

  // Expose functions to global scope for onclick handlers
  window.scholarSorting = {
    removeCriterion: removeSortCriterion,
    moveCriterion: moveSortCriterion,
    addCriterion: addSortCriterion,
  };
})();
