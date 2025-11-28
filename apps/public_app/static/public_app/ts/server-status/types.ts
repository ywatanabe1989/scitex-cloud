/**
 * Type Definitions for Server Status
 */

export interface ServerMetrics {
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

export interface HistoricalDataResponse {
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

// Declare Chart.js type
declare const Chart: any;
export { Chart };
