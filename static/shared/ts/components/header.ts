/**
 * Global Header TypeScript
 * Handles dropdown menus, search, visitor mode, and other header functionality
 */

function initializeHeader(): void {
  // Generic dropdown functionality for all header nav dropdowns
  const dropdownGroups = document.querySelectorAll(".header-dropdown-group");

  dropdownGroups.forEach((group) => {
    const toggle = group.querySelector(".header-dropdown-toggle");
    const dropdown = group.querySelector(".header-nav-dropdown") as HTMLElement;

    if (toggle && dropdown) {
      let hideTimeout: number;

      // Show dropdown on hover over toggle
      toggle.addEventListener("mouseenter", function () {
        clearTimeout(hideTimeout);

        // Close other dropdowns first
        document
          .querySelectorAll<HTMLElement>(".header-nav-dropdown")
          .forEach((otherDropdown) => {
            if (otherDropdown !== dropdown) {
              otherDropdown.style.display = "none";
            }
          });

        dropdown.style.display = "block";
      });

      // Keep dropdown open when hovering over it
      dropdown.addEventListener("mouseenter", function () {
        clearTimeout(hideTimeout);
        dropdown.style.display = "block";
      });

      // Start hide timer when leaving toggle
      toggle.addEventListener("mouseleave", function () {
        hideTimeout = window.setTimeout(() => {
          dropdown.style.display = "none";
        }, 200);
      });

      // Start hide timer when leaving dropdown
      dropdown.addEventListener("mouseleave", function () {
        hideTimeout = window.setTimeout(() => {
          dropdown.style.display = "none";
        }, 200);
      });
    }
  });

  // Close all dropdowns when clicking outside
  document.addEventListener("click", function (e) {
    if (!(e.target as Element).closest(".header-dropdown-group")) {
      document
        .querySelectorAll<HTMLElement>(".header-nav-dropdown")
        .forEach((dropdown) => {
          dropdown.style.display = "none";
        });
    }
  });

  // Close all dropdowns when pressing Escape
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") {
      document
        .querySelectorAll<HTMLElement>(".header-nav-dropdown")
        .forEach((dropdown) => {
          dropdown.style.display = "none";
        });
    }
  });

  // User menu dropdown (regular users)
  const userMenuToggle = document.getElementById("user-menu-toggle");
  const userMenuDropdown = document.getElementById("user-menu-dropdown") as HTMLElement;

  if (userMenuToggle && userMenuDropdown) {
    userMenuToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      const isVisible = userMenuDropdown.style.display !== "none";
      userMenuDropdown.style.display = isVisible ? "none" : "block";
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !userMenuToggle.contains(e.target as Node) &&
        !userMenuDropdown.contains(e.target as Node)
      ) {
        userMenuDropdown.style.display = "none";
      }
    });

    // Close dropdown when pressing Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        userMenuDropdown.style.display = "none";
      }
    });
  }

  // Visitor menu dropdown (visitors)
  const visitorMenuToggle = document.getElementById("visitor-menu-toggle");
  const visitorMenuDropdown = document.getElementById("visitor-menu-dropdown") as HTMLElement;

  if (visitorMenuToggle && visitorMenuDropdown) {
    visitorMenuToggle.addEventListener("click", function (e) {
      e.stopPropagation();
      const isVisible = visitorMenuDropdown.style.display !== "none";
      visitorMenuDropdown.style.display = isVisible ? "none" : "block";
    });

    // Close dropdown when clicking outside
    document.addEventListener("click", function (e) {
      if (
        !visitorMenuToggle.contains(e.target as Node) &&
        !visitorMenuDropdown.contains(e.target as Node)
      ) {
        visitorMenuDropdown.style.display = "none";
      }
    });

    // Close dropdown when pressing Escape
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") {
        visitorMenuDropdown.style.display = "none";
      }
    });
  }

  // Page refresh button handler
  const pageRefreshBtn = document.getElementById("page-refresh-btn");
  if (pageRefreshBtn) {
    pageRefreshBtn.addEventListener("click", function (e) {
      e.preventDefault();

      // Add spinning animation
      const icon = this.querySelector("i");
      if (icon) {
        icon.classList.add("fa-spin");
      }

      // Hard refresh (bypass cache) like Ctrl+Shift+R
      window.location.reload();
    });
  }

  // Visitor Mode Countdown Timer
  if (visitorMenuToggle && visitorMenuToggle.dataset.expiresAt) {
    const expiresAt = new Date(visitorMenuToggle.dataset.expiresAt);
    const countdownSpan = document.getElementById("visitor-countdown");

    function updateCountdown(): void {
      const now = new Date();
      const timeLeft = expiresAt.getTime() - now.getTime();

      if (timeLeft <= 0) {
        // Session expired - redirect to expiration page
        if (countdownSpan) {
          countdownSpan.textContent = "⏰ EXPIRED";
          countdownSpan.style.color = "#f44336";
        }
        setTimeout(() => {
          window.location.href = "/visitor-expired/";
        }, 2000);
        return;
      }

      const hours = Math.floor(timeLeft / (1000 * 60 * 60));
      const minutes = Math.floor((timeLeft % (1000 * 60 * 60)) / (1000 * 60));
      const seconds = Math.floor((timeLeft % (1000 * 60)) / 1000);

      // Format: MM:SS or HH:MM:SS
      let timeString: string;
      if (hours > 0) {
        timeString = `${hours}:${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
      } else {
        timeString = `${String(minutes).padStart(2, "0")}:${String(seconds).padStart(2, "0")}`;
      }

      if (countdownSpan) {
        countdownSpan.textContent = `⏰ ${timeString}`;

        // Color coding based on time remaining
        if (timeLeft < 5 * 60 * 1000) {
          // < 5 minutes: Red (urgent)
          countdownSpan.style.color = "#f44336";
        } else if (timeLeft < 15 * 60 * 1000) {
          // < 15 minutes: Orange (warning)
          countdownSpan.style.color = "#ff9800";
        } else {
          // > 15 minutes: Default color
          countdownSpan.style.color = "inherit";
        }
      }
    }

    // Update immediately and then every second
    updateCountdown();
    setInterval(updateCountdown, 1000);
  }

  // Server Status Live Indicator
  const serverStatusIndicator = document.getElementById('server-status-indicator') as HTMLElement;
  const serverStatusBtn = document.getElementById('server-status-btn');

  if (serverStatusIndicator && serverStatusBtn) {
    let lastStatus = 'healthy';

    async function updateServerStatus(): Promise<void> {
      try {
        const response = await fetch('/api/server-status/');
        const data = await response.json();

        // Determine overall health status
        let status = 'healthy';
        let statusColor = '#4caf50';
        let statusShadow = 'rgba(76, 175, 80, 0.6)';
        let statusTooltip = 'All systems operational';

        // Check critical services
        const criticalServices = [
          data.cpu_percent > 90,
          data.memory_percent > 90,
          data.disk_percent > 90
        ];

        const degradedServices = [
          data.cpu_percent > 70,
          data.memory_percent > 70,
          data.disk_percent > 70
        ];

        if (criticalServices.some(s => s)) {
          status = 'critical';
          statusColor = '#f44336';
          statusShadow = 'rgba(244, 67, 54, 0.6)';
          statusTooltip = 'System critical - High resource usage';
        } else if (degradedServices.some(s => s)) {
          status = 'degraded';
          statusColor = '#ff9800';
          statusShadow = 'rgba(255, 152, 0, 0.6)';
          statusTooltip = 'System degraded - Elevated resource usage';
        }

        // Update indicator
        serverStatusIndicator.style.background = statusColor;
        serverStatusIndicator.style.boxShadow = `0 0 4px ${statusShadow}`;
        serverStatusBtn.setAttribute('data-tooltip', statusTooltip);

        // If status changed, add pulse animation
        if (lastStatus !== status) {
          serverStatusIndicator.style.animation = 'pulse 1s ease-in-out';
          setTimeout(() => {
            serverStatusIndicator.style.animation = '';
          }, 1000);
          lastStatus = status;
        }

      } catch (error) {
        console.error('Failed to fetch server status:', error);
        // Show offline indicator
        serverStatusIndicator.style.background = '#9e9e9e';
        serverStatusIndicator.style.boxShadow = '0 0 4px rgba(158, 158, 158, 0.6)';
        serverStatusBtn.setAttribute('data-tooltip', 'Status check failed');
      }
    }

    // Update immediately and then every 30 seconds
    updateServerStatus();
    setInterval(updateServerStatus, 30000);
  }
}

// Initialize immediately if DOM is ready, otherwise wait
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initializeHeader);
} else {
  initializeHeader();
}
