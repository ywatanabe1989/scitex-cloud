# Monitoring Guide

## Quick Reference

| Service | URL | Purpose |
|---------|-----|---------|
| Django | http://localhost:8000 | Web application |
| Flower | http://localhost:5555 | Celery task monitoring |
| Gitea | http://localhost:3001 | Git server |

## Flower Dashboard (Celery Tasks)

Access: http://localhost:5555 (development)

### What You Can Monitor:
- Active tasks per queue (ai_queue, search_queue, etc.)
- Task success/failure rates
- Worker status and health
- Per-user task distribution
- Rate limit status
- Queue lengths

### Key Metrics:
- **Task throughput**: Tasks/minute per queue
- **Success rate**: % of successful tasks
- **Worker utilization**: Active vs idle workers
- **Queue depth**: Pending tasks

## SLURM Monitoring

### Check Queue Status
```bash
squeue              # All jobs
squeue -u username  # User's jobs
sinfo               # Node status
```

### Check Job History
```bash
sacct -u username --format=JobID,JobName,State,Elapsed,MaxRSS
```

### Resource Usage
```bash
sstat -j JOBID --format=AveCPU,AveRSS,MaxRSS
```

## Server Status Dashboard

Access: https://scitex.ai/server-status/

Real-time metrics:
- CPU usage
- Memory usage
- Disk usage
- Active users
- Running jobs (SLURM)
- Active tasks (Celery)

## Docker Service Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 web
```

## Detailed Operations

See [Operations Guide](../../deployment/docs/07_OPERATIONS_GUIDE.md) for complete commands.
