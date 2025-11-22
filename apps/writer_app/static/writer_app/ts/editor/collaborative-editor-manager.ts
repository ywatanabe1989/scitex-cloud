/**
 * Collaborative Editor Manager
 * Handles manuscript editing, collaboration, auto-save, word counts, and version control
 *
 * @version 2.0.0 (TypeScript)
 * @author SciTeX Development Team
 */

import { getCsrfToken } from "@/utils/csrf.js";

// ============================================================================
// Type Definitions
// ============================================================================

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/apps/writer_app/static/writer_app/ts/editor/collaborative-editor-manager.ts loaded",
);
interface ManuscriptConfig {
  id: number;
  sections: string[];
}

interface ManuscriptData {
  [sectionName: string]: string;
}

interface VersionData {
  commit_message: string;
  version_tag: string;
  branch_name: string;
  is_major: boolean;
}

interface VersionResponse {
  success: boolean;
  version?: {
    version_number: string;
  };
  error?: string;
}

interface ExportData {
  manuscript_id: number;
  sections: ManuscriptData;
  exported_at: string;
}

// ============================================================================
// Collaborative Editor Manager Class
// ============================================================================

export class CollaborativeEditorManager {
  private manuscriptConfig: ManuscriptConfig;
  private isCollaborationEnabled: boolean = false;
  private autoSaveInterval: ReturnType<typeof setInterval> | null = null;

  constructor(manuscriptConfig: ManuscriptConfig) {
    this.manuscriptConfig = manuscriptConfig;
  }

  /**
   * Initialize the editor
   */
  initialize(): void {
    console.log("[CollabEditor] Initializing collaborative editor");

    this.setupEditorListeners();
    this.setupAutoSave();
    this.loadSavedContent();
    this.updateWordCounts();

    console.log("[CollabEditor] Initialization complete");
  }

  /**
   * Setup event listeners for all section textareas
   */
  private setupEditorListeners(): void {
    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        textarea.addEventListener("input", () => {
          this.updateWordCount(section);
          this.updateProgress();
          this.markAsModified();
        });
      }
    });
  }

  /**
   * Setup collaboration toggle button
   */
  setupCollaborationToggle(): void {
    const toggle = document.getElementById("collaboration-toggle");
    if (!toggle) {
      console.warn("[CollabEditor] Collaboration toggle not found");
      return;
    }

    toggle.addEventListener("click", () => {
      if (!this.isCollaborationEnabled) {
        this.enableCollaboration();
      } else {
        this.disableCollaboration();
      }
    });
  }

  /**
   * Enable collaboration mode
   */
  private enableCollaboration(): void {
    this.isCollaborationEnabled = true;
    const toggle = document.getElementById("collaboration-toggle");
    const status = document.getElementById("collab-status");
    const info = document.getElementById("collaboration-info");

    if (toggle) {
      toggle.classList.add("active");
      toggle.innerHTML = '<i class="fas fa-users"></i> Collaboration Active';
    }

    if (status) status.classList.remove("hidden");
    if (info) info.classList.remove("hidden");

    // Show collaborative help sections
    document.querySelectorAll(".collaborative-help").forEach((help) => {
      help.classList.remove("hidden");
    });

    // Add collaborative styling to editors
    document.querySelectorAll(".text-editor").forEach((editor) => {
      editor.classList.add("collaborative-editing");
    });

    // Initialize WebSocket collaboration if available
    if ((window as any).collaborativeEditor) {
      console.log("[CollabEditor] Collaborative editing enabled");
    }

    // Update all section badges to show collaboration status
    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        const wordCount = this.countWords(textarea.value);
        this.updateSectionBadge(section, wordCount);
      }
    });
  }

  /**
   * Disable collaboration mode
   */
  private disableCollaboration(): void {
    this.isCollaborationEnabled = false;
    const toggle = document.getElementById("collaboration-toggle");
    const status = document.getElementById("collab-status");
    const info = document.getElementById("collaboration-info");

    if (toggle) {
      toggle.classList.remove("active");
      toggle.innerHTML = '<i class="fas fa-users"></i> Enable Collaboration';
    }

    if (status) status.classList.add("hidden");
    if (info) info.classList.add("hidden");

    // Hide collaborative help sections
    document.querySelectorAll(".collaborative-help").forEach((help) => {
      help.classList.add("hidden");
    });

    // Remove collaborative styling from editors
    document.querySelectorAll(".text-editor").forEach((editor) => {
      editor.classList.remove("collaborative-editing");
    });

    // Disconnect WebSocket collaboration if available
    if ((window as any).collaborativeEditor) {
      (window as any).collaborativeEditor.destroy();
      console.log("[CollabEditor] Collaborative editing disabled");
    }

    // Update badges to remove collaboration indicators
    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        const wordCount = this.countWords(textarea.value);
        this.updateSectionBadge(section, wordCount);
      }
    });
  }

  /**
   * Count words in a text string
   */
  private countWords(text: string): number {
    return text
      .trim()
      .split(/\s+/)
      .filter((word) => word.length > 0).length;
  }

  /**
   * Update word count for a specific section
   */
  private updateWordCount(section: string): void {
    const textarea = document.getElementById(
      `section-${section}`,
    ) as HTMLTextAreaElement;
    const countElement = document.getElementById(`${section}-count`);

    if (textarea && countElement) {
      const wordCount = this.countWords(textarea.value);
      countElement.textContent = `${wordCount} words`;

      // Update section badge
      this.updateSectionBadge(section, wordCount);
    }
  }

  /**
   * Update section badge with word count and collaboration status
   */
  private updateSectionBadge(section: string, wordCount: number): void {
    const badgesContainer = document.getElementById(`${section}-badges`);
    if (!badgesContainer) return;

    // Clear existing badges
    badgesContainer.innerHTML = "";

    // Add word count badge
    if (wordCount > 0) {
      const badge = document.createElement("span");
      badge.className = "collaboration-badge active";
      badge.innerHTML = `<i class="fas fa-edit"></i> ${wordCount} words`;
      badgesContainer.appendChild(badge);
    }

    // Add collaboration badges if enabled
    if (this.isCollaborationEnabled) {
      const collabBadge = document.createElement("span");
      collabBadge.className = "collaboration-badge editing";
      collabBadge.innerHTML = `<i class="fas fa-users"></i> Live`;
      badgesContainer.appendChild(collabBadge);
    }
  }

  /**
   * Update word counts for all sections
   */
  private updateWordCounts(): void {
    this.manuscriptConfig.sections.forEach((section) => {
      this.updateWordCount(section);
    });
    this.updateProgress();
  }

  /**
   * Update overall progress indicators
   */
  private updateProgress(): void {
    let totalWords = 0;
    let sectionsCompleted = 0;

    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        const wordCount = this.countWords(textarea.value);
        totalWords += wordCount;
        if (wordCount > 0) sectionsCompleted++;
      }
    });

    const completionPercentage = Math.round(
      (sectionsCompleted / this.manuscriptConfig.sections.length) * 100,
    );

    // Update progress display
    const totalWordsEl = document.getElementById("total-words");
    const sectionsCompletedEl = document.getElementById("sections-completed");
    const completionPercentageEl = document.getElementById(
      "completion-percentage",
    );

    if (totalWordsEl) totalWordsEl.textContent = String(totalWords);
    if (sectionsCompletedEl) {
      sectionsCompletedEl.textContent = `${sectionsCompleted}/${this.manuscriptConfig.sections.length}`;
    }
    if (completionPercentageEl) {
      completionPercentageEl.textContent = `${completionPercentage}%`;
    }
  }

  /**
   * Auto-save manuscript to localStorage
   */
  private autoSave(): void {
    const data: ManuscriptData = {};

    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        data[section] = textarea.value;
      }
    });

    // Save to localStorage
    const storageKey = `manuscript_${this.manuscriptConfig.id}`;
    localStorage.setItem(storageKey, JSON.stringify(data));

    // Update save time
    this.updateLastSaveTime("Auto-saved just now");

    console.log("[CollabEditor] Manuscript auto-saved");
  }

  /**
   * Setup auto-save interval
   */
  private setupAutoSave(): void {
    // Auto-save every 30 seconds
    this.autoSaveInterval = setInterval(() => this.autoSave(), 30000);

    // Save on page unload
    window.addEventListener("beforeunload", () => this.autoSave());
  }

  /**
   * Export manuscript as JSON
   */
  exportJSON(): void {
    const data: ExportData = {
      manuscript_id: this.manuscriptConfig.id,
      sections: {},
      exported_at: new Date().toISOString(),
    };

    this.manuscriptConfig.sections.forEach((section) => {
      const textarea = document.getElementById(
        `section-${section}`,
      ) as HTMLTextAreaElement;
      if (textarea) {
        data.sections[section] = textarea.value;
      }
    });

    const blob = new Blob([JSON.stringify(data, null, 2)], {
      type: "application/json",
    });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = `manuscript_${this.manuscriptConfig.id}.json`;
    a.click();
    URL.revokeObjectURL(url);

    console.log("[CollabEditor] Manuscript exported as JSON");
  }

  /**
   * Show LaTeX view (placeholder)
   */
  showLatexView(): void {
    alert(
      "LaTeX view coming soon! This will show the generated LaTeX code for your manuscript.",
    );
  }

  /**
   * Compile manuscript to PDF (placeholder)
   */
  compileManuscript(): void {
    alert(
      "PDF compilation coming soon! This will generate a PDF from your manuscript.",
    );
  }

  /**
   * Open version control dashboard
   */
  openVersionControl(): void {
    window.location.href = `/writer/version-control/${this.manuscriptConfig.id}/`;
  }

  /**
   * Create a new version with git commit
   */
  async createVersion(): Promise<void> {
    const commitMessage = prompt("Enter a commit message for this version:");
    if (!commitMessage) return;

    const versionTag =
      prompt(
        'Enter an optional version tag (e.g., "Draft 1", "Final Version"):',
      ) || "";

    // First auto-save current content
    this.autoSave();

    const formData: VersionData = {
      commit_message: commitMessage,
      version_tag: versionTag,
      branch_name: "main",
      is_major: false,
    };

    try {
      const response = await fetch(
        `/writer/api/version/${this.manuscriptConfig.id}/create/`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify(formData),
        },
      );

      const data: VersionResponse = await response.json();

      if (data.success && data.version) {
        alert(`Version created successfully: v${data.version.version_number}`);
        this.updateLastSaveTime("Version saved");
      } else {
        alert("Error creating version: " + (data.error || "Unknown error"));
      }
    } catch (error) {
      console.error("[CollabEditor] Error creating version:", error);
      alert("Error creating version");
    }
  }

  /**
   * Update last save time message
   */
  private updateLastSaveTime(message: string): void {
    const saveTime = document.getElementById("last-save-time");
    if (saveTime) {
      saveTime.textContent = message;
    }
  }

  /**
   * Mark document as modified (visual indicator)
   */
  private markAsModified(): void {
    // Visual indication that document has unsaved changes
    if (!document.title.startsWith("● ")) {
      document.title = "● " + document.title;
    }
  }

  /**
   * Load saved content from localStorage
   */
  private loadSavedContent(): void {
    const storageKey = `manuscript_${this.manuscriptConfig.id}`;
    const saved = localStorage.getItem(storageKey);

    if (saved) {
      try {
        const data: ManuscriptData = JSON.parse(saved);

        this.manuscriptConfig.sections.forEach((section) => {
          const textarea = document.getElementById(
            `section-${section}`,
          ) as HTMLTextAreaElement;
          if (textarea && data[section]) {
            textarea.value = data[section];
          }
        });

        this.updateWordCounts();
        console.log("[CollabEditor] Loaded saved content from localStorage");
      } catch (error) {
        console.error("[CollabEditor] Error loading saved content:", error);
      }
    }
  }

  /**
   * Destroy the editor manager and cleanup
   */
  destroy(): void {
    // Clear auto-save interval
    if (this.autoSaveInterval) {
      clearInterval(this.autoSaveInterval);
      this.autoSaveInterval = null;
    }

    // Final auto-save
    this.autoSave();

    console.log("[CollabEditor] Editor manager destroyed");
  }
}

// ============================================================================
// Global Export
// ============================================================================

declare global {
  interface Window {
    CollaborativeEditorManager: typeof CollaborativeEditorManager;
    collaborativeEditorManager?: CollaborativeEditorManager;
  }
}

// Export to window for access from templates
window.CollaborativeEditorManager = CollaborativeEditorManager;
