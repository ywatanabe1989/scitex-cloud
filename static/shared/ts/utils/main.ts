/**
 * SciTeX Cloud - Main Application Initialization
 * Handles mobile menu, global UI initialization
 */

/**
 * Initialize the main application
 */

console.log(
  "[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/main.ts loaded",
);
function initApp(): void {
  // Initialize mobile menu toggle
  initMobileMenu();

  // Add event listeners for primary CTAs
  const getStartedBtn =
    document.querySelector<HTMLButtonElement>(".btn-primary");
  if (getStartedBtn) {
    getStartedBtn.addEventListener("click", () => {
      // Add navigation or modal display logic here
      console.log("[Main] Get Started button clicked");
    });
  }
}

/**
 * Initialize mobile menu functionality
 * Handles responsive menu toggle and cloning header actions for mobile
 */
function initMobileMenu(): void {
  const mobileToggle = document.querySelector<HTMLElement>(
    ".mobile-menu-toggle",
  );
  const siteNavigation =
    document.querySelector<HTMLElement>(".site-navigation");
  const headerActions = document.querySelector<HTMLElement>(".header-actions");

  if (mobileToggle && siteNavigation) {
    // Toggle menu on button click
    mobileToggle.addEventListener("click", () => {
      const isOpen = siteNavigation.classList.contains("open");

      if (isOpen) {
        // Close menu
        siteNavigation.classList.remove("open");

        // Remove header actions from mobile menu if they were added
        const mobileActions =
          siteNavigation.querySelector<HTMLElement>(".header-actions");
        if (mobileActions) {
          mobileActions.remove();
        }
      } else {
        // Open menu
        siteNavigation.classList.add("open");

        // Clone header actions into mobile menu on small screens
        if (window.innerWidth <= 576 && headerActions) {
          const mobileActions = headerActions.cloneNode(true) as HTMLElement;
          mobileActions.style.display = "flex";
          siteNavigation.appendChild(mobileActions);
        }
      }
    });

    // Handle window resize - close mobile menu on desktop
    window.addEventListener("resize", () => {
      if (window.innerWidth > 768) {
        siteNavigation.classList.remove("open");

        // Remove cloned actions if they exist
        const mobileActions =
          siteNavigation.querySelector<HTMLElement>(".header-actions");
        if (mobileActions) {
          mobileActions.remove();
        }
      }
    });
  }
}

// Initialize when DOM is ready
document.addEventListener("DOMContentLoaded", () => {
  initApp();
});
