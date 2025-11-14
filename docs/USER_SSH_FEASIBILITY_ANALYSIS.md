<!-- ---
!-- Timestamp: 2025-11-14 17:10:00
!-- Author: Claude + ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/docs/USER_SSH_FEASIBILITY_ANALYSIS.md
!-- --- -->

# User SSH Dynamic Container Feasibility Analysis

## Executive Summary

**Question**: Is dynamic container spawning for User SSH manageable for our infrastructure?

**Answer**: ✅ **YES** - Highly feasible with proper implementation

**Confidence Level**: High - This is a well-established pattern used by major platforms (GitHub Codespaces, GitPod, JupyterHub, etc.)

## Current Infrastructure Assessment

### Existing Setup (from `docker-compose.yml`)
```
Current Containers:
- web (Django app)
- db (PostgreSQL)
- redis (Cache)
- gitea (Git server)

Network: Bridge network (172.20.0.0/16)
Resource: Shared host resources with Docker
```

### Infrastructure Strengths
1. ✅ **Already Docker-based**: Infrastructure is container-native
2. ✅ **Network isolation**: Existing bridge network for inter-container communication
3. ✅ **Volume management**: Proven pattern with user data at `/app/data/users/{username}/`
4. ✅ **Service orchestration**: docker-compose for service management

## Dynamic Container Architecture

### How It Works
```
User SSH Connection Flow:
1. User: ssh user@scitex.ai -p 2200
2. SSH Gateway Container: Authenticates via Django API
3. Gateway: Checks if user container exists
   - If exists: Attach to running container
   - If not: Spawn new container
4. User gets shell in their personal container
5. On disconnect: Container kept alive (configurable timeout)
6. On timeout: Container stops (data persists in volumes)
```

### Resource Model

#### Per-User Container Specs (Configurable)
```yaml
CPU: 2-4 cores (limit)
Memory: 4-16 GB (limit)
Disk: 10-100 GB (via volume quota)
Network: Isolated (bridge network)
Timeout: 30-60 minutes idle (configurable)
```

#### Infrastructure Capacity Planning
```
Example: 16-core server, 64GB RAM

Conservative allocation (4 cores, 16GB per user):
- Max concurrent users: 4 users (at peak resource usage)
- Typical concurrent users: 8-12 users (50% avg utilization)

Moderate allocation (2 cores, 8GB per user):
- Max concurrent users: 8 users
- Typical concurrent users: 16-24 users

With idle timeout (30 min):
- Active containers: Only users actively working
- Stopped containers: Zero resource consumption
- Restart time: <5 seconds (cached image)
```

## Implementation Approaches

### Option A: Docker API (Recommended)
**Pros**:
- Direct Docker control via Python SDK
- No additional infrastructure needed
- Full container lifecycle management
- Works on existing setup

**Implementation**:
```python
import docker

client = docker.from_env()

# Spawn user container
container = client.containers.run(
    image="scitex-user-env",
    name=f"user-{username}",
    detach=True,
    mem_limit="8g",
    cpu_quota=200000,  # 2 cores
    volumes={
        f'/app/data/users/{username}': {'bind': '/home/user', 'mode': 'rw'}
    },
    network="scitex-dev"
)
```

### Option B: Kubernetes (Overkill for now)
**When to consider**:
- Multi-server deployment
- 100+ concurrent users
- Auto-scaling requirements

## Resource Management Strategy

### 1. Container Lifecycle
```python
# Pseudo-code
class UserContainerManager:
    def get_or_create(user):
        container = find_existing_container(user)
        if container and container.status == "running":
            return container
        elif container and container.status == "exited":
            container.start()
            return container
        else:
            return create_new_container(user)

    def cleanup_idle():
        # Run every 5 minutes
        for container in get_idle_containers(timeout=30*60):
            container.stop()
            # Keep container, just stop it (fast restart)
```

### 2. Resource Limits
```python
# Docker resource constraints
CONTAINER_LIMITS = {
    "mem_limit": "8g",
    "memswap_limit": "8g",  # Disable swap
    "cpu_quota": 200000,     # 2 CPU cores
    "cpu_period": 100000,
    "pids_limit": 512,       # Max processes
    "ulimits": [
        docker.types.Ulimit(name='nofile', soft=1024, hard=2048)
    ],
}
```

### 3. Disk Quotas
```bash
# Use XFS project quotas or bind mounts with size limits
# Per-user disk quota: 50GB default, 100GB max

# Example with loop device
truncate -s 50G /data/user-disks/user-123.img
mkfs.ext4 /data/user-disks/user-123.img
mount -o loop,rw /data/user-disks/user-123.img /app/data/users/username
```

## Security Considerations

### Isolation
1. ✅ **Process isolation**: Docker namespaces
2. ✅ **Network isolation**: User containers in separate network
3. ✅ **Filesystem isolation**: Each user has own volume
4. ✅ **No privileged access**: Containers run as non-root

### Security Measures
```dockerfile
# User container Dockerfile
FROM python:3.11-slim

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash user

# No sudo/root access
USER user
WORKDIR /home/user

# Resource limits enforced at runtime
# Network access controlled by firewall rules
```

## Cost Analysis

### Compute Costs
```
Example: AWS/GCP pricing

Single Server (16 cores, 64GB RAM):
- Cost: $200-300/month
- Capacity: 8-12 concurrent users (moderate allocation)
- Cost per user: $20-30/month

With auto-scaling (managed Kubernetes):
- Cost: $50/user/month base + usage
- Better for 50+ users
```

### Storage Costs
```
User Data Storage:
- 50GB per user × 100 users = 5TB
- Block storage: $100-150/month (AWS EBS)
- Object storage backup: $25/month (S3)
```

## Monitoring & Observability

### Key Metrics to Track
```yaml
Container Metrics:
  - Active containers count
  - CPU usage per container
  - Memory usage per container
  - Network I/O
  - Disk I/O

User Metrics:
  - Session duration
  - Idle time
  - Resource usage patterns
  - Login frequency

Infrastructure Metrics:
  - Host CPU/Memory availability
  - Disk space
  - Network bandwidth
  - Container start/stop latency
```

### Implementation with Prometheus
```python
from prometheus_client import Counter, Gauge, Histogram

container_spawns = Counter('user_containers_spawned_total', 'Total containers spawned')
active_containers = Gauge('user_containers_active', 'Currently active containers')
container_start_time = Histogram('user_container_start_seconds', 'Time to start container')
```

## Implementation Phases

### Phase 1: MVP (2-4 weeks)
- [ ] Create user container base image
- [ ] Implement SSH gateway with Docker API
- [ ] Basic resource limits (CPU, memory)
- [ ] User data volume mounting
- [ ] Simple idle timeout (30 min)
- [ ] Manual testing with 2-3 users

### Phase 2: Production Ready (4-6 weeks)
- [ ] Automated container cleanup
- [ ] Monitoring and alerting
- [ ] Resource usage dashboard
- [ ] Disk quotas
- [ ] Security hardening
- [ ] Load testing (10-20 concurrent users)

### Phase 3: Scale (8-12 weeks)
- [ ] Auto-scaling logic
- [ ] Multi-server support
- [ ] Container image caching
- [ ] Advanced resource scheduling
- [ ] User resource quota management UI

## Risks & Mitigations

### Risk 1: Resource Exhaustion
**Problem**: Too many containers, server runs out of resources
**Mitigation**:
- Hard limit on concurrent containers (e.g., 12 max)
- Queue system for excess users
- Aggressive idle timeout
- User quotas

### Risk 2: Container Start Latency
**Problem**: Slow container startup frustrates users
**Mitigation**:
- Pre-warmed container pool (3-5 ready containers)
- Cached container images
- Fast storage (SSD)
- Target: <5 second startup

### Risk 3: Data Loss
**Problem**: Container crashes, user loses work
**Mitigation**:
- All user data on persistent volumes (not in container)
- Automated backups (daily)
- Git integration (users push to Gitea)
- Data is never in container ephemeral storage

### Risk 4: Security Breach
**Problem**: User escapes container, accesses host
**Mitigation**:
- AppArmor/SELinux profiles
- No privileged containers
- Regular security updates
- Network segmentation
- Audit logging

## Comparison with Alternatives

### Option 1: Static Containers (One per user, always running)
❌ **Not recommended**
- Wastes resources (users not always active)
- Expensive at scale
- Same complexity as dynamic

### Option 2: Shared Shell Server (All users in one container)
❌ **Not recommended**
- Poor isolation
- Resource conflicts
- Security risks
- Hard to limit per-user resources

### Option 3: VM per User
❌ **Not recommended**
- Much heavier than containers (GB RAM overhead per user)
- Slower startup (30+ seconds)
- More expensive
- Overkill for our use case

## Conclusion

### Recommendation: **PROCEED with Dynamic Containers**

**Justification**:
1. ✅ **Technically Feasible**: Well-proven pattern, existing Docker infrastructure
2. ✅ **Cost Effective**: Only pay for active resources
3. ✅ **Scalable**: Can start small (4-8 users), grow to 100+
4. ✅ **Secure**: Strong isolation via Docker
5. ✅ **Good UX**: Fast startup (<5s), seamless experience

**Starting Point**:
- Single server with 16 cores, 64GB RAM
- Support 8-12 concurrent users
- Total capacity: 50-100 registered users (with idle timeout)
- Cost: ~$250-300/month infrastructure

**Growth Path**:
- Add servers as needed (linear scaling)
- Consider Kubernetes at 50+ concurrent users
- Monitor and adjust resource limits based on actual usage

## Next Steps

1. **Immediate** (Week 1-2):
   - [ ] Build user container base image
   - [ ] Set up development test environment
   - [ ] Implement basic Docker API integration

2. **Short-term** (Week 3-4):
   - [ ] Implement SSH gateway
   - [ ] Test with 2-3 users
   - [ ] Implement idle timeout

3. **Medium-term** (Week 5-8):
   - [ ] Production deployment
   - [ ] Monitoring setup
   - [ ] Resource limit tuning
   - [ ] Beta testing with 10 users

## References

- Docker Python SDK: https://docker-py.readthedocs.io/
- JupyterHub (similar architecture): https://github.com/jupyterhub/jupyterhub
- Gitpod (commercial example): https://www.gitpod.io/
- GitHub Codespaces: Similar container-per-user model

<!-- EOF -->
