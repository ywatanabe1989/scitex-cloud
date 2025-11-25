# 07 - Operations Guide

## Quick Reference

### Start Everything

```bash
cd deployment/docker/docker_dev
docker-compose up -d
```

### Check Status

```bash
# Docker services
docker-compose ps

# SLURM queue
squeue

# SLURM nodes
sinfo
```

### URLs

| Service | URL |
|---------|-----|
| Django | http://localhost:8000 |
| Flower (Celery) | http://localhost:5555 |
| Gitea | http://localhost:3001 |

---

## Docker Operations

### Start/Stop

```bash
# Start all
docker-compose up -d

# Stop all
docker-compose down

# Restart specific service
docker-compose restart web
docker-compose restart celery_worker
```

### Logs

```bash
# All logs
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f celery_worker

# Last 100 lines
docker-compose logs --tail=100 web
```

### Rebuild

```bash
# Rebuild after requirements change
docker-compose build web
docker-compose up -d

# Force rebuild (no cache)
docker-compose build --no-cache web
```

### Shell Access

```bash
# Django shell
docker-compose exec web python manage.py shell

# Bash in container
docker-compose exec web bash

# Database shell
docker-compose exec db psql -U scitex_dev scitex_cloud_dev
```

---

## SLURM Operations

### Queue Management

```bash
# View queue
squeue

# View queue (detailed)
squeue -l

# View specific job
scontrol show job <job_id>

# View node status
sinfo

# View partitions
sinfo -s
```

### Job Control

```bash
# Cancel job
scancel <job_id>

# Cancel all user's jobs
scancel -u <username>

# Hold job
scontrol hold <job_id>

# Release job
scontrol release <job_id>
```

### Job History

```bash
# Recent jobs
sacct -u $USER

# Specific job details
sacct -j <job_id> --format=JobID,JobName,State,ExitCode,Elapsed,MaxRSS

# Jobs from last 24 hours
sacct --starttime=now-1day
```

### Service Control

```bash
# Restart SLURM controller
sudo systemctl restart slurmctld

# Restart SLURM daemon
sudo systemctl restart slurmd

# Check status
sudo systemctl status slurmctld slurmd munge
```

---

## Celery Operations

### Via Docker

```bash
# Restart worker
docker-compose restart celery_worker

# View worker status
docker-compose exec celery_worker celery -A config status

# Purge all tasks (careful!)
docker-compose exec celery_worker celery -A config purge

# Inspect active tasks
docker-compose exec celery_worker celery -A config inspect active
```

### Flower Dashboard

Open http://localhost:5555

- **Dashboard**: Overview of workers and queues
- **Tasks**: Task history and details
- **Broker**: Redis queue status
- **Monitor**: Real-time task monitoring

---

## Monitoring

### System Resources

```bash
# CPU/Memory
htop

# Disk usage
df -h

# Docker disk usage
docker system df
```

### Application Logs

```bash
# Django logs
tail -f logs/django.log

# All logs in container
docker-compose exec web tail -f /app/logs/django.log
```

### SLURM Job Output

```bash
# View job output
cat /tmp/user_workspace/slurm_outputs/slurm-<job_id>.out

# View job errors
cat /tmp/user_workspace/slurm_outputs/slurm-<job_id>.err
```

---

## Troubleshooting

### Docker Issues

| Problem | Solution |
|---------|----------|
| Container won't start | `docker-compose logs <service>` |
| Port already in use | `lsof -i :<port>` then kill process |
| Out of disk space | `docker system prune -a` |
| Permission denied | Check volume mounts |

### SLURM Issues

| Problem | Solution |
|---------|----------|
| Job pending (Resources) | Check `sinfo`, reduce resource request |
| Job pending (Priority) | Wait or use express partition |
| Node down | `sudo scontrol update nodename=X state=idle` |
| Plugin error (WSL) | Use `proctrack/linuxproc` |

### Celery Issues

| Problem | Solution |
|---------|----------|
| Tasks not running | Check `docker-compose ps celery_worker` |
| Rate limit exceeded | Wait for `retry_after` seconds |
| Worker crashed | `docker-compose restart celery_worker` |
| Redis connection failed | Check Redis is running |

---

## Maintenance

### Database Backup

```bash
# Backup
docker-compose exec db pg_dump -U scitex_dev scitex_cloud_dev > backup.sql

# Restore
docker-compose exec -T db psql -U scitex_dev scitex_cloud_dev < backup.sql
```

### Clean Up

```bash
# Remove old Docker images
docker image prune -a

# Remove old job outputs (older than 7 days)
find /tmp/*/slurm_outputs -mtime +7 -delete

# Clear Celery results (older than 30 days)
docker-compose exec web python manage.py cleartasks --days=30
```

### Update Container

```bash
# Rebuild Apptainer container
cd deployment/singularity
sudo apptainer build scitex-user-workspace.sif scitex-user-workspace.def
```

---

## Cheat Sheet

```
┌─────────────────────────────────────────────────────────────┐
│                    Operations Cheat Sheet                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  DOCKER:                                                    │
│  ────────                                                   │
│  docker-compose up -d          # Start all                  │
│  docker-compose ps             # Status                     │
│  docker-compose logs -f web    # View logs                  │
│  docker-compose restart web    # Restart                    │
│                                                             │
│  SLURM:                                                     │
│  ───────                                                    │
│  squeue                        # View queue                 │
│  sinfo                         # Node status                │
│  scancel <id>                  # Cancel job                 │
│  sacct -j <id>                 # Job history                │
│                                                             │
│  CELERY:                                                    │
│  ────────                                                   │
│  http://localhost:5555         # Flower dashboard           │
│  docker-compose restart celery_worker  # Restart            │
│                                                             │
│  LOGS:                                                      │
│  ──────                                                     │
│  logs/django.log               # Django                     │
│  slurm_outputs/slurm-*.out     # SLURM jobs                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```
