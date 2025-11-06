"use strict";
/**
 * SciTeX Cloud - Dropdown Menu Functionality
 * Handles generic dropdown menus with click-outside-to-close behavior
 */
/**
 * Initialize dropdown menu functionality
 */
console.log("[DEBUG] /home/ywatanabe/proj/scitex-cloud/static/ts/utils/dropdown.ts loaded");
function initDropdowns() {
    // Get all dropdown toggles
    const dropdownToggles = document.querySelectorAll('.dropdown-toggle');
    // Handle click events for all devices
    dropdownToggles.forEach(toggle => {
        toggle.addEventListener('click', function (e) {
            e.preventDefault();
            const parent = this.parentNode;
            const menu = parent?.querySelector('.dropdown-menu');
            if (!menu)
                return;
            // Close other open dropdowns
            document.querySelectorAll('.dropdown-menu.show').forEach(otherMenu => {
                if (otherMenu !== menu) {
                    otherMenu.classList.remove('show');
                }
            });
            // Toggle the 'show' class
            menu.classList.toggle('show');
        });
    });
    // Close dropdowns when clicking outside
    document.addEventListener('click', function (e) {
        const target = e.target;
        if (!target.closest('.dropdown')) {
            document.querySelectorAll('.dropdown-menu.show').forEach(menu => {
                menu.classList.remove('show');
            });
        }
    });
    // Ensure logout/signout navigates in same tab (not new tab)
    const logoutLink = document.querySelector('a[href*="/logout/"]');
    if (logoutLink) {
        logoutLink.removeAttribute('target');
        logoutLink.addEventListener('click', function (e) {
            e.preventDefault();
            // Ensure default behavior (navigate in same tab)
            window.location.href = this.href;
        });
    }
}
// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    initDropdowns();
});
//# sourceMappingURL=dropdown.js.map