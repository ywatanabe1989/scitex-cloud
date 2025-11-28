/**
 * Chart.js Configuration Templates
 */

export const MAX_DATA_POINTS = 1800;
export const UPDATE_INTERVAL = 2000;

export const percentChartConfig: any = {
  type: 'line',
  options: {
    responsive: true,
    maintainAspectRatio: true,
    animation: { duration: 300 },
    interaction: { intersect: false, mode: 'index' },
    scales: {
      x: {
        type: 'time',
        time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } },
        title: { display: true, text: 'Time' }
      },
      y: {
        min: 0,
        max: 100,
        title: { display: true, text: 'Usage (%)' }
      }
    },
    plugins: {
      legend: { display: false },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return context.parsed.y.toFixed(1) + '%';
          }
        }
      }
    }
  }
};

export const networkChartConfig: any = {
  type: 'line',
  options: {
    responsive: true,
    maintainAspectRatio: true,
    animation: { duration: 300 },
    interaction: { intersect: false, mode: 'index' },
    scales: {
      x: {
        type: 'time',
        time: { unit: 'minute', displayFormats: { minute: 'HH:mm' } },
        title: { display: true, text: 'Time' }
      },
      y: {
        min: 0,
        title: { display: true, text: 'Total I/O (MB)' }
      }
    },
    plugins: {
      legend: { display: true },
      tooltip: {
        callbacks: {
          label: function(context: any) {
            return context.dataset.label + ': ' + context.parsed.y.toFixed(2) + ' MB';
          }
        }
      }
    }
  }
};
