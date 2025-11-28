/**
 * Server Status TypeScript
 * Real-time metrics charts with Chart.js
 * Handles CPU, Memory, Disk, GPU, Network I/O, Visitor Pool, and Active Users metrics
 */

// TypeScript interfaces for server metrics
interface ServerMetrics {
  timestamp: number;
  cpu_percent: number | null;
  memory_percent: number | null;
  disk_percent: number | null;
  gpu_percent: number | null;
  disk_read_mb_total: number;
  disk_write_mb_total: number;
  net_sent_mb_total: number;
  net_recv_mb_total: number;
  visitor_pool_allocated: number | null;
  visitor_pool_total: number | null;
  active_users_count: number | null;
}

interface HistoricalDataResponse {
  metrics: Array<{
    timestamp: number;
    cpu_percent: number | null;
    memory_percent: number | null;
    disk_percent: number | null;
    gpu_percent: number | null;
    disk_read_mb: number | null;
    disk_write_mb: number | null;
    net_sent_mb: number | null;
    net_recv_mb: number | null;
    visitor_pool_allocated: number | null;
    active_users_count: number | null;
  }>;
}

// Declare Chart.js type (will be loaded from CDN)
declare const Chart: any;

function initializeServerStatus(): void {
  const MAX_DATA_POINTS = 1800; // Keep up to 1 hour of data (at ~2 sec intervals = 1800 points)
  const UPDATE_INTERVAL = 2000; // Update every 2 seconds

  // Chart configuration for percentage metrics (CPU, Memory, Disk, GPU)
  const percentChartConfig: any = {
    type: 'line',
    options: {
      responsive: true,
      maintainAspectRatio: true,
      animation: {
        duration: 300
      },
      interaction: {
        intersect: false,
        mode: 'index'
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'minute',
            stepSize: 5,
            displayFormats: {
              minute: 'HH:mm',
              second: 'HH:mm:ss'
            },
            tooltipFormat: 'HH:mm:ss'
          },
          title: {
            display: true,
            text: 'Time',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            maxRotation: 0,
            autoSkipPadding: 15,
            maxTicksLimit: 12
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          beginAtZero: true,
          max: 100,
          title: {
            display: true,
            text: 'Usage (%)',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            callback: function(value: number) {
              return value + '%';
            }
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.05)'
          }
        }
      },
      plugins: {
        legend: {
          display: false
        },
        tooltip: {
          enabled: true,
          callbacks: {
            label: function(context: any) {
              return context.parsed.y !== null ? context.parsed.y.toFixed(1) + '%' : 'N/A';
            }
          }
        }
      }
    }
  };

  // Chart configuration for I/O metrics (MB/s rates)
  const ioChartConfig: any = {
    type: 'line',
    options: {
      responsive: true,
      maintainAspectRatio: true,
      animation: {
        duration: 300
      },
      interaction: {
        intersect: false,
        mode: 'index'
      },
      scales: {
        x: {
          type: 'time',
          time: {
            unit: 'minute',
            stepSize: 5,
            displayFormats: {
              minute: 'HH:mm',
              second: 'HH:mm:ss'
            },
            tooltipFormat: 'HH:mm:ss'
          },
          title: {
            display: true,
            text: 'Time',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            maxRotation: 0,
            autoSkipPadding: 15,
            maxTicksLimit: 12
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.05)'
          }
        },
        y: {
          beginAtZero: true,
          title: {
            display: true,
            text: 'Rate (MB/s)',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            callback: function(value: number) {
              return value.toFixed(2) + ' MB/s';
            }
          },
          grid: {
            display: true,
            color: 'rgba(0, 0, 0, 0.05)'
          }
        }
      },
      plugins: {
        legend: {
          display: true,
          position: 'top'
        },
        tooltip: {
          enabled: true,
          callbacks: {
            label: function(context: any) {
              return context.dataset.label + ': ' + (context.parsed.y !== null ? context.parsed.y.toFixed(3) + ' MB/s' : 'N/A');
            }
          }
        }
      }
    }
  };

  // Initialize CPU chart
  const cpuCtx = (document.getElementById('cpuChart') as HTMLCanvasElement)?.getContext('2d');
  if (!cpuCtx) return;

  const cpuChart = new Chart(cpuCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'CPU Usage',
        data: [],
        borderColor: 'rgb(54, 162, 235)',
        backgroundColor: 'rgba(54, 162, 235, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(54, 162, 235)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    }
  });

  // Initialize Memory chart
  const memoryCtx = (document.getElementById('memoryChart') as HTMLCanvasElement)?.getContext('2d');
  if (!memoryCtx) return;

  const memoryChart = new Chart(memoryCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'Memory Usage',
        data: [],
        borderColor: 'rgb(255, 99, 132)',
        backgroundColor: 'rgba(255, 99, 132, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(255, 99, 132)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    }
  });

  // Initialize Disk chart
  const diskCtx = (document.getElementById('diskChart') as HTMLCanvasElement)?.getContext('2d');
  if (!diskCtx) return;

  const diskChart = new Chart(diskCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'Disk Usage',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(75, 192, 192)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    }
  });

  // Initialize GPU chart
  const gpuCtx = (document.getElementById('gpuChart') as HTMLCanvasElement)?.getContext('2d');
  if (!gpuCtx) return;

  const gpuChart = new Chart(gpuCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'GPU Usage',
        data: [],
        borderColor: 'rgb(153, 102, 255)',
        backgroundColor: 'rgba(153, 102, 255, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(153, 102, 255)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    }
  });

  // Initialize Disk I/O chart
  const diskIoCtx = (document.getElementById('diskIoChart') as HTMLCanvasElement)?.getContext('2d');
  if (!diskIoCtx) return;

  const diskIoChart = new Chart(diskIoCtx, {
    ...ioChartConfig,
    data: {
      datasets: [
        {
          label: 'Read',
          data: [],
          borderColor: 'rgb(75, 192, 192)',
          backgroundColor: 'rgba(75, 192, 192, 0.15)',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 0,
          pointHitRadius: 10,
          pointHoverRadius: 4
        },
        {
          label: 'Write',
          data: [],
          borderColor: 'rgb(255, 159, 64)',
          backgroundColor: 'rgba(255, 159, 64, 0.15)',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 0,
          pointHitRadius: 10,
          pointHoverRadius: 4
        }
      ]
    }
  });

  // Initialize Network I/O chart
  const netIoCtx = (document.getElementById('netIoChart') as HTMLCanvasElement)?.getContext('2d');
  if (!netIoCtx) return;

  const netIoChart = new Chart(netIoCtx, {
    ...ioChartConfig,
    data: {
      datasets: [
        {
          label: 'Sent',
          data: [],
          borderColor: 'rgb(255, 99, 132)',
          backgroundColor: 'rgba(255, 99, 132, 0.15)',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 0,
          pointHitRadius: 10,
          pointHoverRadius: 4
        },
        {
          label: 'Received',
          data: [],
          borderColor: 'rgb(54, 162, 235)',
          backgroundColor: 'rgba(54, 162, 235, 0.15)',
          borderWidth: 2,
          tension: 0.3,
          fill: false,
          pointRadius: 0,
          pointHitRadius: 10,
          pointHoverRadius: 4
        }
      ]
    }
  });

  // Initialize Visitor Pool chart
  const visitorPoolCtx = (document.getElementById('visitorPoolChart') as HTMLCanvasElement)?.getContext('2d');
  if (!visitorPoolCtx) return;

  const visitorPoolChart = new Chart(visitorPoolCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'Allocated Slots',
        data: [],
        borderColor: 'rgb(201, 203, 207)',
        backgroundColor: 'rgba(201, 203, 207, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(201, 203, 207)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    },
    options: {
      ...percentChartConfig.options,
      scales: {
        ...percentChartConfig.options.scales,
        y: {
          ...percentChartConfig.options.scales.y,
          max: 4,
          title: {
            display: true,
            text: 'Allocated Slots',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            stepSize: 1,
            callback: function(value: number) {
              return value;
            }
          }
        }
      }
    }
  });

  // Initialize Active Users chart
  const activeUsersCtx = (document.getElementById('activeUsersChart') as HTMLCanvasElement)?.getContext('2d');
  if (!activeUsersCtx) return;

  const activeUsersChart = new Chart(activeUsersCtx, {
    ...percentChartConfig,
    data: {
      datasets: [{
        label: 'Active Users',
        data: [],
        borderColor: 'rgb(75, 192, 192)',
        backgroundColor: 'rgba(75, 192, 192, 0.15)',
        borderWidth: 3,
        tension: 0.3,
        fill: true,
        spanGaps: false,
        pointRadius: 0,
        pointHitRadius: 10,
        pointHoverRadius: 4,
        pointHoverBackgroundColor: 'rgb(75, 192, 192)',
        pointHoverBorderColor: '#fff',
        pointHoverBorderWidth: 2
      }]
    },
    options: {
      ...percentChartConfig.options,
      scales: {
        ...percentChartConfig.options.scales,
        y: {
          ...percentChartConfig.options.scales.y,
          title: {
            display: true,
            text: 'Number of Users',
            font: {
              size: 12,
              weight: 'bold'
            }
          },
          ticks: {
            stepSize: 1,
            callback: function(value: number) {
              return Math.floor(value);
            }
          }
        }
      }
    }
  });

  let gpuAvailable: boolean | null = null;
  let lastDiskRead: number | null = null;
  let lastDiskWrite: number | null = null;
  let lastNetSent: number | null = null;
  let lastNetRecv: number | null = null;
  let lastTimestamp: number | null = null;

  // Helper function to format time range text
  function formatTimeRangeText(hours: number): string {
    if (hours === 1) return 'Last 1 Hour';
    if (hours < 24) return `Last ${hours} Hours`;
    if (hours === 24) return 'Last 24 Hours';
    if (hours === 168) return 'Last 7 Days';
    if (hours === 720) return 'Last 30 Days';
    const days = Math.floor(hours / 24);
    return `Last ${days} Days`;
  }

  // Load historical data on page load
  async function loadHistoricalData(hours: number = 1): Promise<void> {
    try {
      const limit = Math.min(hours * 720, 20000);
      const response = await fetch(`/api/server-metrics/history/?hours=${hours}&limit=${limit}`);
      const data: HistoricalDataResponse = await response.json();

      if (data.metrics && data.metrics.length > 0) {
        // Clear existing chart data
        cpuChart.data.datasets[0].data = [];
        memoryChart.data.datasets[0].data = [];
        diskChart.data.datasets[0].data = [];
        gpuChart.data.datasets[0].data = [];
        diskIoChart.data.datasets[0].data = [];
        diskIoChart.data.datasets[1].data = [];
        netIoChart.data.datasets[0].data = [];
        netIoChart.data.datasets[1].data = [];
        visitorPoolChart.data.datasets[0].data = [];
        activeUsersChart.data.datasets[0].data = [];

        let prevMetric: typeof data.metrics[0] | null = null;
        data.metrics.forEach((metric, index) => {
          const timestamp = metric.timestamp;

          // CPU, Memory, Disk, GPU data
          cpuChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.cpu_percent !== null && !isNaN(metric.cpu_percent)) ? metric.cpu_percent : NaN
          });

          memoryChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.memory_percent !== null && !isNaN(metric.memory_percent)) ? metric.memory_percent : NaN
          });

          diskChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.disk_percent !== null && !isNaN(metric.disk_percent)) ? metric.disk_percent : NaN
          });

          gpuChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.gpu_percent !== null && !isNaN(metric.gpu_percent)) ? metric.gpu_percent : NaN
          });

          visitorPoolChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.visitor_pool_allocated !== null && !isNaN(metric.visitor_pool_allocated)) ? metric.visitor_pool_allocated : NaN
          });

          activeUsersChart.data.datasets[0].data.push({
            x: timestamp,
            y: (metric.active_users_count !== null && !isNaN(metric.active_users_count)) ? metric.active_users_count : NaN
          });

          // Calculate I/O rates
          if (prevMetric && index > 0) {
            const timeDiff = (timestamp - prevMetric.timestamp) / 1000;

            if (metric.disk_read_mb !== null && prevMetric.disk_read_mb !== null) {
              const diskReadRate = (metric.disk_read_mb - prevMetric.disk_read_mb) / timeDiff;
              const diskWriteRate = (metric.disk_write_mb! - prevMetric.disk_write_mb!) / timeDiff;
              diskIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, diskReadRate) });
              diskIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, diskWriteRate) });
            }

            if (metric.net_sent_mb !== null && prevMetric.net_sent_mb !== null) {
              const netSentRate = (metric.net_sent_mb - prevMetric.net_sent_mb) / timeDiff;
              const netRecvRate = (metric.net_recv_mb! - prevMetric.net_recv_mb!) / timeDiff;
              netIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, netSentRate) });
              netIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, netRecvRate) });
            }
          }

          prevMetric = metric;
        });

        // Store last values
        if (data.metrics.length > 0) {
          const lastMetric = data.metrics[data.metrics.length - 1];
          lastDiskRead = lastMetric.disk_read_mb;
          lastDiskWrite = lastMetric.disk_write_mb;
          lastNetSent = lastMetric.net_sent_mb;
          lastNetRecv = lastMetric.net_recv_mb;
          lastTimestamp = lastMetric.timestamp;
        }

        // Adjust time scale
        const timeUnit = hours <= 1 ? 'minute' : hours <= 6 ? 'minute' : hours <= 24 ? 'hour' : hours <= 168 ? 'hour' : 'day';
        const stepSize = hours <= 1 ? 5 : hours <= 6 ? 30 : hours <= 24 ? 2 : hours <= 168 ? 6 : 1;
        const displayFormat = hours <= 6 ? 'HH:mm' : hours <= 168 ? 'MMM D HH:mm' : 'MMM D';

        [cpuChart, memoryChart, diskChart, gpuChart, diskIoChart, netIoChart, visitorPoolChart, activeUsersChart].forEach(chart => {
          chart.options.scales.x.time.unit = timeUnit;
          chart.options.scales.x.time.stepSize = stepSize;
          chart.options.scales.x.time.displayFormats[timeUnit] = displayFormat;
          chart.update();
        });

        console.log(`Loaded ${data.metrics.length} data points (${formatTimeRangeText(hours)})`);
      }
    } catch (error) {
      console.error('Error loading historical data:', error);
    }
  }

  // Fetch and update metrics
  async function updateMetrics(): Promise<void> {
    try {
      const response = await fetch('/api/server-status/');
      const data: ServerMetrics = await response.json();
      const timestamp = data.timestamp;

      // Update CPU
      const cpuValue = (data.cpu_percent !== null && !isNaN(data.cpu_percent)) ? data.cpu_percent : NaN;
      cpuChart.data.datasets[0].data.push({ x: timestamp, y: cpuValue });
      if (cpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        cpuChart.data.datasets[0].data.shift();
      }
      cpuChart.update('none');
      document.getElementById('cpuCurrentValue')!.textContent = !isNaN(cpuValue) ? cpuValue.toFixed(1) + '%' : 'N/A';

      // Update Memory
      const memoryValue = (data.memory_percent !== null && !isNaN(data.memory_percent)) ? data.memory_percent : NaN;
      memoryChart.data.datasets[0].data.push({ x: timestamp, y: memoryValue });
      if (memoryChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        memoryChart.data.datasets[0].data.shift();
      }
      memoryChart.update('none');
      document.getElementById('memoryCurrentValue')!.textContent = !isNaN(memoryValue) ? memoryValue.toFixed(1) + '%' : 'N/A';

      // Update Disk
      const diskValue = (data.disk_percent !== null && !isNaN(data.disk_percent)) ? data.disk_percent : NaN;
      diskChart.data.datasets[0].data.push({ x: timestamp, y: diskValue });
      if (diskChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        diskChart.data.datasets[0].data.shift();
      }
      diskChart.update('none');
      document.getElementById('diskCurrentValue')!.textContent = !isNaN(diskValue) ? diskValue.toFixed(1) + '%' : 'N/A';

      // Update GPU
      const gpuStatusEl = document.getElementById('gpuStatus')!;
      const gpuValue = (data.gpu_percent !== null && !isNaN(data.gpu_percent)) ? data.gpu_percent : NaN;

      if (!isNaN(gpuValue)) {
        if (gpuAvailable === null) {
          gpuAvailable = true;
          gpuStatusEl.innerHTML = '<i class="fas fa-check-circle" style="color: var(--status-success);"></i> GPU detected';
        }
        gpuChart.data.datasets[0].data.push({ x: timestamp, y: gpuValue });
        if (gpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
          gpuChart.data.datasets[0].data.shift();
        }
        gpuChart.update('none');
        document.getElementById('gpuCurrentValue')!.textContent = gpuValue.toFixed(1) + '%';
      } else {
        if (gpuAvailable === null) {
          gpuAvailable = false;
          gpuStatusEl.innerHTML = '<i class="fas fa-times-circle" style="color: var(--text-muted);"></i> No GPU available';
        }
        gpuChart.data.datasets[0].data.push({ x: timestamp, y: NaN });
        if (gpuChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
          gpuChart.data.datasets[0].data.shift();
        }
        gpuChart.update('none');
        document.getElementById('gpuCurrentValue')!.textContent = 'N/A';
      }

      // Calculate and update Disk I/O rates
      if (lastDiskRead !== null) {
        const timeDiff = lastTimestamp !== null ? (timestamp - lastTimestamp) / 1000 : 2;
        const diskReadRate = (data.disk_read_mb_total - lastDiskRead) / timeDiff;
        const diskWriteRate = (data.disk_write_mb_total - lastDiskWrite!) / timeDiff;

        diskIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, diskReadRate) });
        diskIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, diskWriteRate) });

        if (diskIoChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
          diskIoChart.data.datasets[0].data.shift();
          diskIoChart.data.datasets[1].data.shift();
        }
        diskIoChart.update('none');

        const totalIoRate = Math.max(0, diskReadRate) + Math.max(0, diskWriteRate);
        document.getElementById('diskIoCurrentValue')!.textContent = totalIoRate.toFixed(2) + ' MB/s';
      }

      // Calculate and update Network I/O rates
      if (lastNetSent !== null) {
        const timeDiff = lastTimestamp !== null ? (timestamp - lastTimestamp) / 1000 : 2;
        const netSentRate = (data.net_sent_mb_total - lastNetSent) / timeDiff;
        const netRecvRate = (data.net_recv_mb_total - lastNetRecv!) / timeDiff;

        netIoChart.data.datasets[0].data.push({ x: timestamp, y: Math.max(0, netSentRate) });
        netIoChart.data.datasets[1].data.push({ x: timestamp, y: Math.max(0, netRecvRate) });

        if (netIoChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
          netIoChart.data.datasets[0].data.shift();
          netIoChart.data.datasets[1].data.shift();
        }
        netIoChart.update('none');

        const totalNetRate = Math.max(0, netSentRate) + Math.max(0, netRecvRate);
        document.getElementById('netIoCurrentValue')!.textContent = totalNetRate.toFixed(2) + ' MB/s';
      }

      // Update Visitor Pool
      const visitorPoolValue = (data.visitor_pool_allocated !== null && !isNaN(data.visitor_pool_allocated)) ? data.visitor_pool_allocated : NaN;
      visitorPoolChart.data.datasets[0].data.push({ x: timestamp, y: visitorPoolValue });
      if (visitorPoolChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        visitorPoolChart.data.datasets[0].data.shift();
      }
      visitorPoolChart.update('none');

      if (!isNaN(visitorPoolValue) && data.visitor_pool_total !== null) {
        document.getElementById('visitorPoolCurrentValue')!.textContent = `${data.visitor_pool_allocated}/${data.visitor_pool_total}`;
      } else {
        document.getElementById('visitorPoolCurrentValue')!.textContent = 'N/A';
      }

      // Update Active Users
      const activeUsersValue = (data.active_users_count !== null && !isNaN(data.active_users_count)) ? data.active_users_count : NaN;
      activeUsersChart.data.datasets[0].data.push({ x: timestamp, y: activeUsersValue });
      if (activeUsersChart.data.datasets[0].data.length > MAX_DATA_POINTS) {
        activeUsersChart.data.datasets[0].data.shift();
      }
      activeUsersChart.update('none');

      if (!isNaN(activeUsersValue)) {
        document.getElementById('activeUsersCurrentValue')!.textContent = String(activeUsersValue);
      } else {
        document.getElementById('activeUsersCurrentValue')!.textContent = 'N/A';
      }

      // Update last values
      lastDiskRead = data.disk_read_mb_total;
      lastDiskWrite = data.disk_write_mb_total;
      lastNetSent = data.net_sent_mb_total;
      lastNetRecv = data.net_recv_mb_total;
      lastTimestamp = timestamp;

    } catch (error) {
      console.error('Error fetching metrics:', error);
    }
  }

  // Initialize
  async function initialize(): Promise<void> {
    await loadHistoricalData();
    updateMetrics();
    setInterval(updateMetrics, UPDATE_INTERVAL);
  }

  initialize();
}

// Live countdown timer for visitor pool slots
function updateVisitorCountdowns(): void {
  document.querySelectorAll('.slot-time-remaining').forEach((element: Element) => {
    const expiresAt = (element as HTMLElement).dataset.expires;
    if (!expiresAt) return;

    const span = element.querySelector('span');
    if (!span) return;

    const now = new Date();
    const expires = new Date(expiresAt);
    const remainingMs = expires.getTime() - now.getTime();
    const remainingSeconds = Math.max(0, Math.floor(remainingMs / 1000));
    const remainingMinutes = Math.floor(remainingSeconds / 60);

    if (remainingSeconds > 0) {
      span.textContent = `Expires in ${remainingMinutes} min`;
    } else {
      span.textContent = 'Expired';
      setTimeout(() => location.reload(), 1000);
    }
  });
}

// Wait for Chart.js to load
window.addEventListener('load', function() {
  initializeServerStatus();

  // Update countdowns every second
  setInterval(updateVisitorCountdowns, 1000);
  updateVisitorCountdowns();
});
