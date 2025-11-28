/**
 * Metrics Updater Module
 * Handles real-time metric updates and chart refreshes
 */

import type { ServerMetrics } from './types.js';
import type { ChartInstances } from './chart-init.js';
import type { LoaderState } from './data-loader.js';
import { MAX_DATA_POINTS } from './chart-configs.js';

let gpuAvailable: boolean | null = null;

export async function updateMetrics(
  charts: ChartInstances,
  state: LoaderState
): Promise<void> {
  try {
    const response = await fetch('/api/server-status/');
    const data: ServerMetrics = await response.json();
    const timestamp = data.timestamp;

    // Update CPU
    const cpuValue = (data.cpu_percent !== null && !isNaN(data.cpu_percent)) ? data.cpu_percent : NaN;
    charts.cpuChart.data.datasets[0].data.push({ x: timestamp, y: cpuValue });
    if (charts.cpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
      charts.cpuChart.data.datasets[0].data.shift();
    }
    charts.cpuChart.update('none');
    document.getElementById('cpuCurrentValue')!.textContent = !isNaN(cpuValue) ? cpuValue.toFixed(1) + '%' : 'N/A';

    // Update Memory
    const memoryValue = (data.memory_percent !== null && !isNaN(data.memory_percent)) ? data.memory_percent : NaN;
    charts.memoryChart.data.datasets[0].data.push({ x: timestamp, y: memoryValue });
    if (charts.memoryChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
      charts.memoryChart.data.datasets[0].data.shift();
    }
    charts.memoryChart.update('none');
    document.getElementById('memoryCurrentValue')!.textContent = !isNaN(memoryValue) ? memoryValue.toFixed(1) + '%' : 'N/A';

    // Update Disk
    const diskValue = (data.disk_percent !== null && !isNaN(data.disk_percent)) ? data.disk_percent : NaN;
    charts.diskChart.data.datasets[0].data.push({ x: timestamp, y: diskValue });
    if (charts.diskChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
      charts.diskChart.data.datasets[0].data.shift();
    }
    charts.diskChart.update('none');
    document.getElementById('diskCurrentValue')!.textContent = !isNaN(diskValue) ? diskValue.toFixed(1) + '%' : 'N/A';

    // Update GPU
    const gpuStatusEl = document.getElementById('gpuStatus')!;
    const gpuValue = (data.gpu_percent !== null && !isNaN(data.gpu_percent)) ? data.gpu_percent : NaN;

    if (!isNaN(gpuValue)) {
      if (gpuAvailable === null) {
        gpuAvailable = true;
        gpuStatusEl.innerHTML = '<i class="fas fa-check-circle" style="color: var(--status-success);"></i> GPU detected';
      }
      charts.gpuChart.data.datasets[0].data.push({ x: timestamp, y: gpuValue });
      if (charts.gpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        charts.gpuChart.data.datasets[0].data.shift();
      }
      charts.gpuChart.update('none');
      document.getElementById('gpuCurrentValue')!.textContent = gpuValue.toFixed(1) + '%';
    } else {
      if (gpuAvailable === null) {
        gpuAvailable = false;
        gpuStatusEl.innerHTML = '<i class="fas fa-times-circle" style="color: var(--text-muted);"></i> No GPU available';
      }
      charts.gpuChart.data.datasets[0].data.push({ x: timestamp, y: NaN });
      if (charts.gpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        charts.gpuChart.data.datasets[0].data.shift();
      }
      charts.gpuChart.update('none');
      document.getElementById('gpuCurrentValue')!.textContent = 'N/A';
    }

    // Calculate and update Disk I/O rates
    if (state.lastDiskRead !== null) {
      const timeDiff = state.lastTimestamp !== null ? (timestamp - state.lastTimestamp) / 1000 : 2;
      const diskReadRate = (data.disk_read_mb_total - state.lastDiskRead) / timeDiff;
      const diskWriteRate = (data.disk_write_mb_total - state.lastDiskWrite!) / timeDiff;

      charts.diskIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, diskReadRate) });
      charts.diskIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, diskWriteRate) });

      if (charts.diskIoChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        charts.diskIoChart.data.datasets[0].data.shift();
        charts.diskIoChart.data.datasets[1].data.shift();
      }
      charts.diskIoChart.update('none');

      const totalIoRate = Math.max(0, diskReadRate) + Math.max(0, diskWriteRate);
      document.getElementById('diskIoCurrentValue')!.textContent = totalIoRate.toFixed(2) + ' MB/s';
    }

    // Calculate and update Network I/O rates
    if (state.lastNetSent !== null) {
      const timeDiff = state.lastTimestamp !== null ? (timestamp - state.lastTimestamp) / 1000 : 2;
      const netSentRate = (data.net_sent_mb_total - state.lastNetSent) / timeDiff;
      const netRecvRate = (data.net_recv_mb_total - state.lastNetRecv!) / timeDiff;

      charts.netIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, netSentRate) });
      charts.netIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, netRecvRate) });

      if (charts.netIoChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        charts.netIoChart.data.datasets[0].data.shift();
        charts.netIoChart.data.datasets[1].data.shift();
      }
      charts.netIoChart.update('none');

      const totalNetRate = Math.max(0, netSentRate) + Math.max(0, netRecvRate);
      document.getElementById('netIoCurrentValue')!.textContent = totalNetRate.toFixed(2) + ' MB/s';
    }

    // Update Visitor Pool
    const visitorPoolValue = (data.visitor_pool_allocated !== null && !isNaN(data.visitor_pool_allocated)) ? data.visitor_pool_allocated : NaN;
    charts.visitorPoolChart.data.datasets[0].data.push({ x: timestamp, y: visitorPoolValue });
    if (charts.visitorPoolChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
      charts.visitorPoolChart.data.datasets[0].data.shift();
    }
    charts.visitorPoolChart.update('none');

    if (!isNaN(visitorPoolValue) && data.visitor_pool_total !== null) {
      document.getElementById('visitorPoolCurrentValue')!.textContent = `${data.visitor_pool_allocated}/${data.visitor_pool_total}`;
    } else {
      document.getElementById('visitorPoolCurrentValue')!.textContent = 'N/A';
    }

    // Update Active Users
    const activeUsersValue = (data.active_users_count !== null && !isNaN(data.active_users_count)) ? data.active_users_count : NaN;
    charts.activeUsersChart.data.datasets[0].data.push({ x: timestamp, y: activeUsersValue });
    if (charts.activeUsersChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
      charts.activeUsersChart.data.datasets[0].data.shift();
    }
    charts.activeUsersChart.update('none');

    if (!isNaN(activeUsersValue)) {
      document.getElementById('activeUsersCurrentValue')!.textContent = String(activeUsersValue);
    } else {
      document.getElementById('activeUsersCurrentValue')!.textContent = 'N/A';
    }

    // Update last values
    state.lastDiskRead = data.disk_read_mb_total;
    state.lastDiskWrite = data.disk_write_mb_total;
    state.lastNetSent = data.net_sent_mb_total;
    state.lastNetRecv = data.net_recv_mb_total;
    state.lastTimestamp = timestamp;

  } catch (error) {
    console.error('Error fetching metrics:', error);
  }
}
