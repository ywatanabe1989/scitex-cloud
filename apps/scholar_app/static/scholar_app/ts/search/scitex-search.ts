/**

 * SciTeX Unified Search Implementation
 *
 * This file implements the unified search system for SciTeX Scholar that aggregates
 * results from multiple academic sources (PubMed, Google Scholar, arXiv, Semantic Scholar)
 * and the SciTeX Index. Results are deduplicated, merged, and ranked intelligently.
 *
 * @version 1.0.0
 */

// Window interface for global configuration

console.log(
  "[DEBUG] apps/scholar_app/static/scholar_app/ts/search/scitex-search.ts loaded",
);
declare global {
  interface Window {
    SCHOLAR_CONFIG?: {
      urls?: {
        search?: string;
      };
    };
    saveSourcePreferences?: () => void;
  }
}

// Export to make this an ES module
export {};

/**
 * Search result interface
 */
interface SearchResult {
  id?: string;
  title?: string;
  authors?: string;
  year?: string | number;
  journal?: string;
  abstract?: string;
  citations?: number;
  pmid?: string;
  doi?: string;
  arxivId?: string;
  externalUrl?: string;
  source?: string;
  pdf_url?: string;
  is_open_access?: boolean;
  impact_factor?: number | string;
}

/**
 * Source configuration
 */
interface SourceConfig {
  name: string;
  endpoint: string;
  maxResults: number;
}

// Initialize on DOM ready
document.addEventListener("DOMContentLoaded", function () {
  console.log("[SciTeX Search] Initializing unified search system...");

  const searchForm = document.getElementById(
    "literatureSearchForm",
  ) as HTMLFormElement | null;
  const searchInput = document.querySelector(
    'input[name="q"]',
  ) as HTMLInputElement | null;
  const searchButton = document.getElementById(
    "searchButton",
  ) as HTMLButtonElement | null;
  const progressiveResults = document.getElementById(
    "progressiveResults",
  ) as HTMLElement | null;

  if (!searchForm || !searchInput) {
    console.log(
      "[SciTeX Search] Search form not found, skipping initialization",
    );
    return;
  }

  // Intercept form submission
  searchForm.addEventListener("submit", function (e: Event) {
    e.preventDefault();
    const query = searchInput.value.trim();

    // Save current source preferences (defined in scholar-index-main.ts)
    if (typeof (window as any).saveSourcePreferences === "function") {
      (window as any).saveSourcePreferences();
    }

    // Hide regular results
    document.querySelectorAll(".result-card").forEach((card) => {
      (card as HTMLElement).style.display = "none";
    });

    // Show progressive interface
    const progressiveLoadingStatus = document.getElementById(
      "progressiveLoadingStatus",
    ) as HTMLElement | null;
    if (progressiveLoadingStatus)
      progressiveLoadingStatus.style.display = "block";

    if (progressiveResults) {
      progressiveResults.style.display = "block";
      progressiveResults.innerHTML = "";
    }

    // Reset progress indicators
    document.querySelectorAll(".progress-source").forEach((source) => {
      const badge = source.querySelector(".badge") as HTMLElement | null;
      const spinner = source.querySelector(
        ".spinner-border",
      ) as HTMLElement | null;
      const count = source.querySelector(".count") as HTMLElement | null;

      if (badge) badge.className = "badge bg-secondary";
      if (spinner) spinner.style.display = "inline-block";
      if (count) count.textContent = "0";
    });

    // Start unified search
    startUnifiedSearch(query);
  });

  console.log("[SciTeX Search] Initialization complete");
});

/**
 * Start unified search across all sources
 */
function startUnifiedSearch(query: string): void {
  console.log("[SciTeX Search] Starting unified search for:", query);

  // Get selected sources
  const selectedCheckboxes = document.querySelectorAll(
    ".source-toggle:checked",
  ) as NodeListOf<HTMLInputElement>;
  const selectedSourceValues = Array.from(selectedCheckboxes).map(
    (cb) => cb.value,
  );

  // All source configurations
  const allSources: SourceConfig[] = [
    { name: "pubmed", endpoint: "/scholar/api/search/pubmed/", maxResults: 50 },
    {
      name: "google_scholar",
      endpoint: "/scholar/api/search/google-scholar/",
      maxResults: 50,
    },
    { name: "arxiv", endpoint: "/scholar/api/search/arxiv/", maxResults: 50 },
    {
      name: "semantic",
      endpoint: "/scholar/api/search/semantic/",
      maxResults: 25,
    },
  ];

  // Filter to selected sources
  const sourcesToSearch = allSources.filter((source) =>
    selectedSourceValues.includes(source.name),
  );

  if (sourcesToSearch.length === 0) {
    alert("Please select at least one search source.");
    resetProgressIndicators();
    return;
  }

  // Search each source in parallel
  sourcesToSearch.forEach((source) => {
    searchSource(source, query);
  });

  // Reset unselected sources
  allSources.forEach((source) => {
    if (!selectedSourceValues.includes(source.name)) {
      const progressSource = document.querySelector(
        `[data-source="${source.name}"]`,
      ) as HTMLElement | null;
      if (progressSource) {
        const badge = progressSource.querySelector(
          ".badge",
        ) as HTMLElement | null;
        const spinner = progressSource.querySelector(
          ".spinner-border",
        ) as HTMLElement | null;
        const count = progressSource.querySelector(
          ".count",
        ) as HTMLElement | null;

        if (badge) badge.className = "badge bg-light";
        if (spinner) spinner.style.display = "none";
        if (count) count.textContent = "-";
      }
    }
  });
}

/**
 * Search a single source
 */
function searchSource(source: SourceConfig, query: string): void {
  const url = `${source.endpoint}?q=${encodeURIComponent(query)}&max_results=${source.maxResults}`;
  const progressSource = document.querySelector(
    `[data-source="${source.name}"]`,
  ) as HTMLElement | null;

  fetch(url)
    .then((response) => response.json())
    .then((data: any) => {
      if (data.status === "success") {
        // Update progress indicator
        if (progressSource) {
          const badge = progressSource.querySelector(
            ".badge",
          ) as HTMLElement | null;
          const spinner = progressSource.querySelector(
            ".spinner-border",
          ) as HTMLElement | null;
          const count = progressSource.querySelector(
            ".count",
          ) as HTMLElement | null;

          if (badge) badge.className = "badge bg-success";
          if (spinner) spinner.style.display = "none";
          if (count) count.textContent = data.count || "0";
        }

        // Add results
        if (data.results && Array.isArray(data.results)) {
          data.results.forEach((result: SearchResult) => {
            addResultToProgressive(result);
          });
        }
      } else {
        handleSearchError(source.name, data.error || "Unknown error");
      }
    })
    .catch((error: Error) => {
      handleSearchError(source.name, error.message);
    });
}

/**
 * Add a result to the progressive results container
 */
function addResultToProgressive(result: SearchResult): void {
  const progressiveResults = document.getElementById(
    "progressiveResults",
  ) as HTMLElement | null;
  if (!progressiveResults) {
    console.warn("[SciTeX Search] Progressive results container not found");
    return;
  }

  const resultCard = createResultCard(result);
  progressiveResults.appendChild(resultCard);

  // Animate
  resultCard.style.opacity = "0";
  resultCard.style.transform = "translateY(20px)";
  setTimeout(() => {
    resultCard.style.transition = "all 0.3s ease";
    resultCard.style.opacity = "1";
    resultCard.style.transform = "translateY(0)";
  }, 50);
}

/**
 * Create a result card element
 */
function createResultCard(result: SearchResult): HTMLElement {
  const cardDiv = document.createElement("div");
  cardDiv.className = "result-card";
  cardDiv.setAttribute("data-paper-id", result.id || "");
  cardDiv.setAttribute("data-title", result.title || "");
  cardDiv.setAttribute("data-authors", result.authors || "");
  cardDiv.setAttribute("data-year", (result.year || "").toString());
  cardDiv.setAttribute("data-journal", result.journal || "Unknown Journal");

  cardDiv.innerHTML = `
        <h6 class="result-title">
            <a href="#" class="text-decoration-none">${result.title || "Unknown Title"}</a>
        </h6>
        <div class="result-authors">${result.authors || "Unknown Authors"}</div>
        <div class="d-flex align-items-center mt-2 flex-wrap">
            <span class="year-badge me-2">${result.year || "2024"}</span>
            ${result.is_open_access ? '<span class="open-access me-2">Open Access</span>' : ""}
            ${result.impact_factor ? `<span class="badge bg-warning text-dark me-2" style="font-size: 0.7rem;">IF: ${result.impact_factor}</span>` : ""}
            <small class="text-muted">
                ${result.journal || "Unknown Journal"}
                ${result.citations && result.citations > 0 ? ` • <strong>${result.citations} citations</strong>` : ""}
                ${result.pmid ? ` • PMID: ${result.pmid}` : ""}
            </small>
            ${result.source ? `<span class="badge bg-info ms-2" style="font-size: 0.7rem;">${result.source.toUpperCase()}</span>` : ""}
        </div>
        <div class="result-snippet mt-2">${result.abstract || "No abstract available."}</div>
    `;

  return cardDiv;
}

/**
 * Handle search error
 */
function handleSearchError(sourceName: string, errorMessage: string): void {
  const progressSource = document.querySelector(
    `[data-source="${sourceName}"]`,
  ) as HTMLElement | null;
  if (progressSource) {
    const badge = progressSource.querySelector(".badge") as HTMLElement | null;
    const spinner = progressSource.querySelector(
      ".spinner-border",
    ) as HTMLElement | null;
    const count = progressSource.querySelector(".count") as HTMLElement | null;

    if (badge) badge.className = "badge bg-danger";
    if (spinner) spinner.style.display = "none";
    if (count) count.textContent = "Error";
  }

  console.error(`[SciTeX Search] ${sourceName} search failed:`, errorMessage);
}

/**
 * Reset progress indicators
 */
function resetProgressIndicators(): void {
  document.querySelectorAll(".progress-source").forEach((source) => {
    const badge = source.querySelector(".badge") as HTMLElement | null;
    const spinner = source.querySelector(
      ".spinner-border",
    ) as HTMLElement | null;
    const count = source.querySelector(".count") as HTMLElement | null;

    if (badge) badge.className = "badge bg-light";
    if (spinner) spinner.style.display = "none";
    if (count) count.textContent = "-";
  });
}

// Note: saveSourcePreferences function is defined in scholar-index-main.ts
// This file assumes it's available in the global scope
