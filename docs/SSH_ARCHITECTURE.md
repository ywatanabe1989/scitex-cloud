# SciTeX Cloud SSH Architecture

## Overview

SciTeX Cloud requires three distinct SSH services for different purposes:

1. **Admin SSH**: System administration
2. **User SSH**: User computational workloads and file access
3. **Gitea SSH**: Git clone/push/pull operations

## Port Allocation

```
Port 22    (or custom) → Admin SSH (system administrators)
Port 2200  → User SSH (computational access for users)
Port 2222  → Gitea SSH (Git operations)
```

## 1. Admin SSH

### Purpose
- Server maintenance and debugging
- Container management
- Log inspection
- System configuration

### Access Control
- Restricted to system administrators
- Key-based authentication only
- Fail2ban protection
- Audit logging

### Implementation
```yaml
# Standard SSH on host or dedicated management container
services:
  admin-ssh:
    image: openssh-server
    ports:
      - "22:22"
    volumes:
      - ./authorized_keys:/etc/ssh/authorized_keys
```

## 2. User SSH (Computational Access) - TO BE IMPLEMENTED

### Purpose
- Users access their computational environment
- Run scripts, notebooks, and analysis
- Access their project files at `/app/data/users/{username}/`
- Install user-specific packages
- Run long-running computations

### Requirements

#### Security
- **User Isolation**: Each user gets isolated environment (container or namespace)
- **Resource Limits**: CPU, memory, GPU, disk quotas per user
- **Network Isolation**: Users cannot access other users' data
- **File System**: Read-only system, writable user home
- **No Privilege Escalation**: Users cannot become root or access other accounts

#### Resource Allocation
- CPU cores per user (e.g., 4 cores)
- Memory limit (e.g., 16GB)
- GPU allocation (if available)
- Disk quota (e.g., 100GB)
- Process limits
- Network bandwidth limits

#### Authentication
- SSH key from user's SciTeX account
- Password authentication disabled
- 2FA support (optional)
- Session timeout

### Architecture Options

#### Option A: SSH Gateway + User Containers (Recommended)
```
User → SSH Gateway (Port 2200) → Per-User Container
                                   ├─ User: ywatanabe
                                   ├─ Home: /home/ywatanabe
                                   ├─ Data: /data/users/ywatanabe
                                   ├─ Resources: CPU=4, MEM=16GB
                                   └─ Network: Isolated
```

**Pros:**
- Strong isolation
- Easy resource management
- Can provide different environments (Python, R, Julia)
- Can scale horizontally

**Implementation:**
- SSH gateway container (port 2200)
- On connection: spawn/attach to user's compute container
- User containers are persistent or on-demand
- Resource limits via Docker/Kubernetes

#### Option B: SSH + Linux Namespaces/cgroups
```
User → SSH Server (Port 2200) → chroot + namespace + cgroups
```

**Pros:**
- Lower overhead
- Simpler architecture
- Single SSH daemon

**Cons:**
- More complex security setup
- Harder to manage resources
- Less isolation than containers

### File System Layout
```
/home/ywatanabe/                    # User home directory
/data/users/ywatanabe/              # User's SciTeX projects (mounted)
  ├── project-001/
  ├── project-002/
  └── default-project/
/opt/scitex/                        # SciTeX tools (read-only)
/usr/local/                         # System packages (read-only)
```

### Proposed Implementation

```yaml
# docker-compose.yml
services:
  ssh-gateway:
    build: ./deployment/docker/ssh-gateway
    ports:
      - "${SCITEX_CLOUD_USER_SSH_PORT:-2200}:22"
    volumes:
      - /var/run/docker.sock:/var/run/docker.sock  # To spawn user containers
      - ./data/users:/data/users:ro                # User data (read-only in gateway)
    environment:
      - SCITEX_CLOUD_API_URL=http://web:8000
      - SCITEX_CLOUD_API_TOKEN=${SCITEX_CLOUD_API_TOKEN}
    depends_on:
      - web
      - db

  # User compute containers (spawned on-demand)
  # Template in ./deployment/docker/user-compute/
```

### API Integration

SSH Gateway needs to:
1. Authenticate user via SciTeX API
2. Check user's SSH public key
3. Get user's resource allocation
4. Spawn/attach to user's compute container
5. Log session activity

```python
# apps/compute_app/api.py
class ComputeAccessAPI:
    def authenticate_ssh(self, username: str, ssh_key: str) -> bool:
        """Verify SSH key matches user's registered key"""
        
    def get_user_resources(self, username: str) -> dict:
        """Get user's resource allocation"""
        return {
            'cpu_cores': 4,
            'memory_gb': 16,
            'gpu_count': 0,
            'disk_gb': 100,
        }
    
    def log_session(self, username: str, action: str):
        """Log SSH session activity"""
```

## 3. Gitea SSH (Already Implemented)

### Purpose
- Git clone, push, pull operations
- Repository access control via Gitea

### Current Implementation
```yaml
services:
  gitea:
    ports:
      - "${SCITEX_CLOUD_GITEA_SSH_PORT_DEV:-2222}:22"
```

### Usage
```bash
# Clone repository
git clone git@127.0.0.1:2222/ywatanabe/default-project.git

# Push changes
git push origin main
```

## Security Considerations

### SSH Key Management
- Users register SSH keys in SciTeX account settings
- Keys are synced to:
  1. User SSH gateway (for computational access)
  2. Gitea (for Git operations)
- Keys can be revoked from single location

### Network Security
- Admin SSH: Only accessible from trusted networks (VPN, IP whitelist)
- User SSH: Rate limited, fail2ban protected
- Gitea SSH: Protected by Gitea's authentication

### Audit Logging
- All SSH connections logged
- User activity tracked
- Resource usage monitored
- Suspicious activity alerts

## User Experience

### Setup
1. User generates SSH key in SciTeX account settings
2. Key is automatically configured for all SSH services
3. User can immediately:
   - Clone their Git repositories
   - SSH into their compute environment

### Typical Workflow
```bash
# 1. Clone project from Gitea
git clone git@scitex.cloud:2222/ywatanabe/my-analysis.git
cd my-analysis

# 2. SSH into compute environment
ssh ywatanabe@scitex.cloud -p 2200

# 3. Run analysis
python analysis.py

# 4. Commit and push results
git add results/
git commit -m "Add analysis results"
git push origin main
```

## Implementation Phases

### Phase 1: Planning (Current)
- [ ] Review architecture
- [ ] Decide on Option A (containers) vs Option B (namespaces)
- [ ] Define resource allocation policies
- [ ] Design API integration

### Phase 2: SSH Gateway
- [ ] Create SSH gateway container
- [ ] Implement authentication via SciTeX API
- [ ] Setup user container spawning
- [ ] Configure resource limits

### Phase 3: Integration
- [ ] Sync SSH keys to gateway
- [ ] Create user compute container template
- [ ] Setup file system mounts
- [ ] Add monitoring and logging

### Phase 4: Testing
- [ ] Security testing
- [ ] Resource isolation testing
- [ ] Load testing
- [ ] User acceptance testing

### Phase 5: Documentation
- [ ] User guide for SSH access
- [ ] Admin guide for resource management
- [ ] Security best practices
- [ ] Troubleshooting guide

## References

- [SSH Container Gateway Pattern](https://github.com/gravitational/teleport)
- [Kubernetes Pod Security](https://kubernetes.io/docs/concepts/security/pod-security-standards/)
- [Docker Resource Constraints](https://docs.docker.com/config/containers/resource_constraints/)
- [Linux Namespaces](https://man7.org/linux/man-pages/man7/namespaces.7.html)
