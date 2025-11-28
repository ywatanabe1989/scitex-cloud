/**
 * Server Status - Main Entry Point (Orchestrator)
 * Real-time metrics charts with Chart.js
 *
 * Refactored from 788 lines to modular architecture.
 * Original: server-status_backup.ts
 */

import { initializeCharts } from './server-status/chart-init.js';
import { loadHistoricalData } from './server-status/data-loader.js';
import { updateMetrics } from './server-status/metrics-updater.js';
import { updateVisitorCountdowns } from './server-status/visitor-countdown.js';
import { UPDATE_INTERVAL } from './server-status/chart-configs.js';
import type { LoaderState } from './server-status/data-loader.js';

console.log('[DEBUG] server-status.ts loaded (orchestrator pattern)');

function initializeServerStatus(): void {
  // Initialize all charts
  const charts = initializeCharts();
  if (!charts) {
    console.error('[server-status] Failed to initialize charts');
    return;
  }

  // Initialize state
  const state: LoaderState = {
    lastDiskRead: null,
    lastDiskWrite: null,
    lastNetSent: null,
    lastNetRecv: null,
    lastTimestamp: null
  };

  // Load historical data and start real-time updates
  async function initialize(): Promise<void> {
    await loadHistoricalData(charts, state);
    updateMetrics(charts, state);
    setInterval(() => updateMetrics(charts, state), UPDATE_INTERVAL);
  }

  initialize();
}

// Wait for Chart.js to load
window.addEventListener('load', function() {
  initializeServerStatus();

  // Update visitor pool countdowns every second
  setInterval(updateVisitorCountdowns, 1000);
  updateVisitorCountdowns();
});
