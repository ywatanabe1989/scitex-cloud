<!-- ---
!-- Timestamp: 2025-11-14 17:35:00
!-- Author: Claude + ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/docs/USER_SSH_IMPLEMENTATION_ROADMAP.md
!-- --- -->

# User SSH Implementation Roadmap

## Quick Answer

**Question**: Is it manageable to implement soon if we prepare a feature branch?

**Answer**: ✅ **YES - Very manageable!**

**Timeline**: 2-4 weeks for MVP, can start immediately

## Feature Branch Strategy

### Branch Structure
```bash
develop
  └── feature/user-ssh-workspace
       ├── Week 1: Container image + Manager service
       ├── Week 2: SSH gateway (basic)
       ├── Week 3: Testing + refinements
       └── Week 4: Merge to develop
```

## Implementation Plan: MVP (Minimal Viable Product)

### Week 1: Foundation (5-8 hours)
**Goal**: Get basic container spawning working

#### Day 1-2: Container Image
```bash
# Create files
touch deployment/docker/Dockerfile.user-workspace
touch scripts/build_user_workspace_image.sh

# Build image
docker build -t scitex-user-workspace:latest \
  -f deployment/docker/Dockerfile.user-workspace .
```

**Deliverable**: Working container image that you can manually run:
```bash
docker run -it \
  -v /app/data/users/testuser:/home/user \
  scitex-user-workspace:latest \
  /bin/bash
```

#### Day 3-4: Container Manager Service
```python
# Create service
apps/workspace_app/services/container_manager.py

# Test in Django shell
from apps.workspace_app.services.container_manager import UserContainerManager
from django.contrib.auth.models import User

user = User.objects.get(username='ywatanabe')
manager = UserContainerManager()
container = manager.get_or_create_container(user)
# Container created! ✅
```

**Deliverable**: Python service that can spawn/manage containers programmatically

### Week 2: SSH Gateway (8-12 hours)
**Goal**: Users can SSH in and get their container

#### Approach 1: Simple SSH Gateway (Easier, recommended for MVP)
```python
# SSH gateway using paramiko (Python SSH library)
# User connects → Authenticate → Spawn container → Forward SSH to container

Implementation:
1. Create SSH server (port 2200)
2. Authenticate against Django database
3. Spawn/attach user container
4. Forward SSH I/O to container
```

#### Approach 2: Use Existing Solution (Even easier!)
```yaml
# Use Teleport or similar SSH gateway
# Already handles SSH, just need to hook into container spawning
```

**Deliverable**: `ssh testuser@127.0.0.1 -p 2200` works locally

### Week 3: Testing & Polish (6-8 hours)
**Goal**: Stable, tested, ready for merge

Tasks:
- [ ] Test with 2-3 real users
- [ ] Add idle timeout (stop containers after 30 min)
- [ ] Add basic monitoring (container count, resource usage)
- [ ] Error handling (container creation fails, etc.)
- [ ] Documentation for users

**Deliverable**: Tested feature ready for code review

### Week 4: Review & Merge (4-6 hours)
**Goal**: Merge to develop

Tasks:
- [ ] Code review
- [ ] Address feedback
- [ ] Integration testing
- [ ] Merge to develop
- [ ] Deploy to staging

## Detailed Task Breakdown

### Phase 1: Container Image (Day 1-2)

#### File 1: Dockerfile.user-workspace
```dockerfile
# deployment/docker/Dockerfile.user-workspace
FROM python:3.11-slim

# System packages
RUN apt-get update && apt-get install -y \
    git vim nano curl wget \
    && rm -rf /var/lib/apt/lists/*

# Python packages
RUN pip install --no-cache-dir \
    numpy pandas matplotlib jupyter \
    ipython requests

# User setup
RUN useradd -m -u 1000 -s /bin/bash user
USER user
WORKDIR /home/user

CMD ["/bin/bash"]
```

#### File 2: Build script
```bash
#!/bin/bash
# scripts/build_user_workspace_image.sh

docker build \
  -t scitex-user-workspace:latest \
  -f deployment/docker/Dockerfile.user-workspace \
  .
```

**Testing**:
```bash
# Build
./scripts/build_user_workspace_image.sh

# Test run
docker run -it --rm scitex-user-workspace:latest python3 -c "import numpy; print('✅ Works!')"
```

**Time estimate**: 2-3 hours

### Phase 2: Container Manager Service (Day 3-4)

#### File: apps/workspace_app/services/container_manager.py
```python
"""User workspace container management"""
import docker
import logging
from typing import Optional
from django.contrib.auth.models import User

logger = logging.getLogger(__name__)

class UserContainerManager:
    """Manages user computational workspace containers"""

    IMAGE = "scitex-user-workspace:latest"
    NETWORK = "scitex-dev"

    def __init__(self):
        self.client = docker.from_env()

    def get_or_create_container(self, user: User):
        """Get or create container for user"""
        container_name = f"user-{user.username}"

        # Try to get existing container
        try:
            container = self.client.containers.get(container_name)

            if container.status != "running":
                logger.info(f"Starting container for {user.username}")
                container.start()

            return container

        except docker.errors.NotFound:
            # Create new container
            logger.info(f"Creating container for {user.username}")
            return self._create_container(user)

    def _create_container(self, user: User):
        """Create new container"""
        container_name = f"user-{user.username}"
        user_data = f"/app/data/users/{user.username}"

        container = self.client.containers.run(
            self.IMAGE,
            name=container_name,
            detach=True,
            stdin_open=True,
            tty=True,

            # Resources
            mem_limit="8g",
            cpu_quota=200000,

            # Volumes
            volumes={
                user_data: {'bind': '/home/user', 'mode': 'rw'}
            },

            # Network
            network=self.NETWORK,

            # Environment
            environment={
                "USER": "user",
                "HOME": "/home/user",
            }
        )

        return container

    def stop_container(self, user: User):
        """Stop user container"""
        container_name = f"user-{user.username}"
        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=10)
            logger.info(f"Stopped container for {user.username}")
        except docker.errors.NotFound:
            pass

    def exec_command(self, user: User, command: list):
        """Execute command in user container"""
        container = self.get_or_create_container(user)

        result = container.exec_run(
            command,
            stdout=True,
            stderr=True,
        )

        return result.output.decode('utf-8')
```

**Testing**:
```python
# In Django shell
from apps.workspace_app.services.container_manager import UserContainerManager
from django.contrib.auth.models import User

user = User.objects.get(username='ywatanabe')
manager = UserContainerManager()

# Create container
container = manager.get_or_create_container(user)
print(f"✅ Container created: {container.name}")

# Test command execution
output = manager.exec_command(user, ["python3", "-c", "import numpy; print('numpy works')"])
print(output)

# Stop container
manager.stop_container(user)
print("✅ Container stopped")
```

**Time estimate**: 3-4 hours

### Phase 3: SSH Gateway (Week 2)

#### Simple Approach: Django Management Command
```python
# apps/workspace_app/management/commands/run_ssh_gateway.py

"""
Simple SSH gateway that spawns containers

Usage: python manage.py run_ssh_gateway
"""

import paramiko
import threading
from django.core.management.base import BaseCommand
from django.contrib.auth import authenticate
from apps.workspace_app.services.container_manager import UserContainerManager

class SSHGateway(paramiko.ServerInterface):
    """SSH server interface"""

    def __init__(self, username, password):
        self.username = username
        self.password = password
        self.user = None

    def check_auth_password(self, username, password):
        """Authenticate against Django"""
        user = authenticate(username=username, password=password)
        if user:
            self.user = user
            return paramiko.AUTH_SUCCESSFUL
        return paramiko.AUTH_FAILED

    def check_channel_request(self, kind, chanid):
        if kind == 'session':
            return paramiko.OPEN_SUCCEEDED
        return paramiko.OPEN_FAILED_ADMINISTRATIVELY_PROHIBITED

    def check_channel_shell_request(self, channel):
        # User wants a shell, spawn their container
        manager = UserContainerManager()
        container = manager.get_or_create_container(self.user)

        # Execute bash in container and forward I/O
        exec_instance = container.exec_run(
            ["/bin/bash"],
            stdin=True,
            tty=True,
            socket=True,
        )

        # Forward SSH channel <-> Container socket
        # (Implementation details)

        return True

class Command(BaseCommand):
    help = 'Run SSH gateway for user containers'

    def handle(self, *args, **options):
        # Start SSH server on port 2200
        # Listen for connections
        # Spawn containers for authenticated users
        pass
```

**Alternative: Use existing SSH gateway like Teleport**
- Might be easier than implementing from scratch
- Configure Teleport to spawn containers on connection

**Time estimate**: 8-12 hours

### Phase 4: Web Integration (Optional for MVP)

#### Add "Open Workspace" button to project page
```python
# apps/workspace_app/views.py

def open_workspace(request, username, project_slug):
    """Open user workspace in browser"""

    # Spawn/attach container
    manager = UserContainerManager()
    container = manager.get_or_create_container(request.user)

    # Start code-server (VS Code) in container
    container.exec_run(
        ["code-server", "--bind-addr", "0.0.0.0:8080", "/home/user"],
        detach=True,
    )

    # Proxy to container:8080
    return redirect(f'/workspace/{request.user.username}/')
```

**Time estimate**: 4-6 hours (if doing web UI)

## Testing Strategy

### Manual Testing Checklist
```
[ ] Build container image successfully
[ ] Create container for test user (Django shell)
[ ] Container has correct volumes mounted
[ ] User data persists across container restart
[ ] Resource limits work (CPU, memory)
[ ] Multiple users get separate containers
[ ] SSH connection works (port 2200)
[ ] User can run Python scripts in container
[ ] User can install packages in container
[ ] Idle containers stop after timeout
[ ] Stopped containers restart quickly (<5s)
```

### Load Testing
```python
# Test with 5 concurrent users
for i in range(5):
    user = User.objects.get(username=f'testuser{i}')
    manager.get_or_create_container(user)

# Check: All 5 containers running
# Check: Host resource usage acceptable
```

## Rollout Plan

### Development → Staging → Production

#### Stage 1: Development (Week 1-3)
- Feature branch: `feature/user-ssh-workspace`
- Local testing
- 1-2 developer users

#### Stage 2: Staging (Week 4)
- Merge to `develop`
- Deploy to staging server
- Beta test with 5-10 users
- Collect feedback

#### Stage 3: Production (Week 5+)
- After successful staging
- Gradual rollout (10 users → 50 users → all)
- Monitor closely

## Risk Mitigation

### Risk 1: Implementation takes longer than expected
**Mitigation**: Start with absolute minimum
- Week 1 goal: Just get container spawning working
- SSH can wait if needed
- Web UI is optional

### Risk 2: Resource exhaustion on server
**Mitigation**: Start small
- Limit to 5 concurrent containers initially
- Add queue system if needed
- Scale server if successful

### Risk 3: SSH gateway is complex
**Mitigation**: Use simple approach first
- Management command instead of full gateway
- Or use existing solution (Teleport, Boundary)
- SSH is nice-to-have, web UI might be enough

## Success Metrics

### MVP Success Criteria
```
✅ Container image builds successfully
✅ Containers can be spawned programmatically
✅ User data mounts correctly
✅ At least one access method works (SSH or web)
✅ Tested with 2-3 users successfully
✅ No major resource issues on dev server
```

### Post-MVP Goals
```
□ 10+ users using it regularly
□ Average container startup < 5 seconds
□ No reported data loss
□ Resource usage stable
□ Positive user feedback
```

## Minimum Viable Feature Set

### Must Have (MVP)
- ✅ Container image with Python/scientific packages
- ✅ Container manager service
- ✅ At least ONE way to access (SSH OR web)
- ✅ User data persistence
- ✅ Basic resource limits

### Nice to Have (Post-MVP)
- ⏳ Both SSH AND web access
- ⏳ Idle timeout automation
- ⏳ Monitoring dashboard
- ⏳ User quota management
- ⏳ Auto-scaling

### Can Wait (Future)
- ⏱️ JupyterLab integration
- ⏱️ VS Code server (Codespace)
- ⏱️ Advanced resource scheduling
- ⏱️ Multi-server support

## Recommended Approach for Feature Branch

### Option A: Start Simple (Recommended)
```
Week 1:
✅ Dockerfile.user-workspace
✅ Container manager service
✅ Test in Django shell

Week 2:
✅ Simple management command: spawn_user_container
✅ Users manually docker exec for now
✅ Document the manual process

Week 3-4:
✅ Add SSH gateway OR web UI (pick one)
✅ Test with real users
✅ Merge to develop
```

### Option B: Go for SSH First
```
Week 1:
✅ Dockerfile + Manager (same as Option A)

Week 2:
✅ SSH gateway using paramiko
✅ Basic authentication

Week 3:
✅ Testing + polish

Week 4:
✅ Merge
```

## My Recommendation

**Start with Option A** for the feature branch:

1. **Week 1**: Get container spawning solid (this is the foundation)
2. **Week 2**: Add simplest possible access (even manual docker exec is OK for MVP)
3. **Week 3**: Add better access (SSH or web)
4. **Week 4**: Polish and merge

**Why this approach**:
- ✅ Fast iteration
- ✅ Can show progress after Week 1
- ✅ Derisks the container management (hardest part)
- ✅ Flexibility to pivot (SSH vs web)

## Next Steps to Start

```bash
# 1. Create feature branch
git checkout -b feature/user-ssh-workspace

# 2. Create basic structure
mkdir -p apps/workspace_app/services
mkdir -p apps/workspace_app/management/commands
touch deployment/docker/Dockerfile.user-workspace

# 3. Start with Dockerfile
# Copy example from USER_SSH_CONTAINER_IMAGE.md

# 4. Build and test
docker build -t scitex-user-workspace:latest -f deployment/docker/Dockerfile.user-workspace .

# 5. Commit progress
git add .
git commit -m "feat(workspace): Add user workspace container image"

# You're off to the races! 🚀
```

## Conclusion

**Is it manageable?** ✅ **ABSOLUTELY YES!**

**Timeline**: 2-4 weeks for working MVP

**Complexity**: Medium (not trivial, but very doable)

**Risk**: Low (well-proven pattern, can start small)

**Recommendation**: Create feature branch and start with container image + manager service. That alone is valuable and can be built on.

<!-- EOF -->
