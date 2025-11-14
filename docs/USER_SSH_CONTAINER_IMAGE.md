<!-- ---
!-- Timestamp: 2025-11-14 17:25:00
!-- Author: Claude + ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/docs/USER_SSH_CONTAINER_IMAGE.md
!-- --- -->

# User SSH Workspace Container Image

## Overview

**Question**: Do we need to prepare an image for user SSH workspace?

**Answer**: ✅ **YES** - We need a pre-built container image that serves as the user's computational environment

## Container Image Purpose

This image is the **user's workspace** - their computational environment with:
- Python, R, Julia, and other scientific computing tools
- Common data science libraries
- Text editors (vim, nano, emacs)
- Git client
- User's project files (mounted at runtime)

## Workflow

### One-Time Setup (Before Launch)
```bash
# 1. Build the user workspace image
docker build -t scitex-user-workspace:latest -f Dockerfile.user-workspace .

# 2. Push to registry (optional, for multi-server deployment)
docker push scitex-user-workspace:latest
```

### Runtime (When User Connects)
```python
# When user connects via SSH or clicks "Open Workspace"
1. User: ssh user@scitex.ai -p 2200
   OR clicks "Open Codespace" button

2. SciTeX checks:
   - Does container exist for this user?
   - Is it running?

3. Three scenarios:

   A. Container doesn't exist → CREATE NEW
      container = docker.run(
          image="scitex-user-workspace:latest",  # Use pre-built image
          name=f"user-{username}",
          volumes={
              f"/app/data/users/{username}": "/home/user"  # Mount user data
          },
          ...
      )
      Time: ~10 seconds (first time)

   B. Container exists but stopped → START
      container.start()
      Time: ~2-5 seconds (cached, fast)

   C. Container running → ATTACH
      Time: Instant

4. User gets their shell or Codespace UI
```

## Container Image Design

### Dockerfile.user-workspace (Example)
```dockerfile
FROM ubuntu:22.04

# Metadata
LABEL maintainer="SciTeX Cloud <support@scitex.ai>"
LABEL description="User computational workspace for SciTeX Cloud"

# Set timezone
ENV TZ=UTC
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Install system dependencies
RUN apt-get update && apt-get install -y \
    # Development tools
    build-essential \
    git \
    wget \
    curl \
    vim \
    nano \
    tmux \
    htop \
    tree \
    # SSH client (for git operations)
    openssh-client \
    # Python
    python3.11 \
    python3.11-dev \
    python3-pip \
    # R
    r-base \
    r-base-dev \
    # Julia (optional)
    # julia \
    # Other utilities
    zip \
    unzip \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN useradd -m -u 1000 -s /bin/bash user && \
    echo "user:user" | chpasswd

# Install Python scientific stack
RUN pip3 install --no-cache-dir \
    numpy \
    scipy \
    pandas \
    matplotlib \
    seaborn \
    scikit-learn \
    jupyter \
    jupyterlab \
    ipython \
    # Deep learning
    torch \
    tensorflow \
    # SciTeX package (editable mode will be mounted at runtime)
    # Other common packages
    requests \
    beautifulsoup4 \
    plotly

# Install R packages (optional)
RUN R -e "install.packages(c('ggplot2', 'dplyr', 'tidyr'), repos='http://cran.rstudio.com/')"

# Set up user environment
USER user
WORKDIR /home/user

# Configure shell
RUN echo 'export PATH=$HOME/.local/bin:$PATH' >> ~/.bashrc && \
    echo 'alias ll="ls -lah"' >> ~/.bashrc && \
    echo 'alias python=python3' >> ~/.bashrc

# Default command (will be overridden by SSH or exec)
CMD ["/bin/bash"]
```

### Build Script
```bash
#!/bin/bash
# File: scripts/build_user_workspace_image.sh

set -e

IMAGE_NAME="scitex-user-workspace"
VERSION="2.1.0"

echo "Building user workspace image: $IMAGE_NAME:$VERSION"

docker build \
    -t $IMAGE_NAME:$VERSION \
    -t $IMAGE_NAME:latest \
    -f deployment/docker/Dockerfile.user-workspace \
    .

echo "✓ Image built successfully"
echo "  - $IMAGE_NAME:$VERSION"
echo "  - $IMAGE_NAME:latest"

# Optional: Push to registry
read -p "Push to registry? (y/n) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    docker push $IMAGE_NAME:$VERSION
    docker push $IMAGE_NAME:latest
    echo "✓ Image pushed to registry"
fi
```

## Container Lifecycle Management

### Python Service: UserContainerManager
```python
# File: apps/workspace_app/services/container_manager.py

import docker
from typing import Optional
from django.contrib.auth.models import User

class UserContainerManager:
    """Manages user workspace containers"""

    def __init__(self):
        self.client = docker.from_env()
        self.image = "scitex-user-workspace:latest"

    def get_or_create_container(self, user: User) -> docker.models.containers.Container:
        """
        Get existing container or create new one

        Returns:
            Running container for the user
        """
        container_name = f"user-{user.username}"

        # Try to find existing container
        try:
            container = self.client.containers.get(container_name)

            # If stopped, start it
            if container.status != "running":
                container.start()
                logger.info(f"Started existing container for {user.username}")

            return container

        except docker.errors.NotFound:
            # Create new container
            return self._create_container(user)

    def _create_container(self, user: User) -> docker.models.containers.Container:
        """Create new user container"""
        container_name = f"user-{user.username}"
        user_data_path = f"/app/data/users/{user.username}"

        container = self.client.containers.run(
            image=self.image,
            name=container_name,
            detach=True,

            # Resource limits
            mem_limit="8g",
            cpu_quota=200000,  # 2 CPU cores

            # Volumes - Mount user's data
            volumes={
                user_data_path: {
                    'bind': '/home/user',
                    'mode': 'rw'
                },
                # Optional: Mount scitex package (editable mode)
                '/scitex-code': {
                    'bind': '/scitex-code',
                    'mode': 'ro'
                }
            },

            # Network
            network="scitex-dev",

            # Environment
            environment={
                "USERNAME": user.username,
                "USER_ID": user.id,
            },

            # Keep container alive
            stdin_open=True,
            tty=True,
        )

        logger.info(f"Created new container for {user.username}")
        return container

    def stop_idle_containers(self, idle_timeout_minutes: int = 30):
        """Stop containers idle for more than timeout"""
        # Implementation: Track last activity, stop if idle
        pass

    def cleanup_container(self, user: User):
        """Stop and optionally remove user container"""
        container_name = f"user-{user.username}"

        try:
            container = self.client.containers.get(container_name)
            container.stop(timeout=10)
            # Optional: container.remove() - usually we keep stopped containers
            logger.info(f"Stopped container for {user.username}")
        except docker.errors.NotFound:
            pass
```

## Image Update Strategy

### Versioning
```
scitex-user-workspace:2.0.0  # Stable release
scitex-user-workspace:2.1.0  # New packages added
scitex-user-workspace:latest # Always points to latest stable
```

### Rolling Updates
```python
# When new image is available
def update_user_containers():
    """
    Update user containers to new image version

    Strategy:
    1. Build new image
    2. For each user:
       - Next time they connect, use new image
       - Or: Stop old container, create new one with new image
    """
    new_image = "scitex-user-workspace:2.1.0"

    # Update will happen on next user connection
    # Old containers continue to work until stopped
```

## Storage Considerations

### Image Size
```
Typical size:
- Base Ubuntu: ~80 MB
- + Python 3.11: ~150 MB
- + Scientific packages: ~2-3 GB
- Total: ~3-4 GB

Storage per server:
- 1 image × 4 GB = 4 GB (shared by all users)
- User data: 50 GB × 100 users = 5 TB
```

### Layer Caching
```dockerfile
# Optimize Dockerfile for caching
# Put frequently changing layers at bottom

# These change rarely → cache well
FROM ubuntu:22.04
RUN apt-get update && apt-get install -y python3.11 ...

# These change more often → lower in Dockerfile
RUN pip3 install numpy scipy pandas
RUN pip3 install scitex  # Your package
```

## Integration Points

### 1. SSH Gateway
```python
# When user SSH connects
from apps.workspace_app.services.container_manager import UserContainerManager

def handle_ssh_connection(user):
    manager = UserContainerManager()
    container = manager.get_or_create_container(user)

    # Execute SSH shell in container
    exec_instance = container.exec_run(
        cmd=["/bin/bash"],
        stdin=True,
        tty=True,
        stream=True,
    )

    # Forward SSH I/O to container exec
    # ...
```

### 2. Web Codespace (VS Code in Browser)
```python
# When user clicks "Open Codespace"
def open_codespace(user):
    manager = UserContainerManager()
    container = manager.get_or_create_container(user)

    # Start code-server (VS Code) in container
    container.exec_run(
        cmd=["code-server", "--bind-addr", "0.0.0.0:8080", "/home/user"],
        detach=True,
    )

    # Proxy user's browser to container:8080
    return redirect(f"/codespace/{user.username}/")
```

### 3. JupyterLab
```python
# When user opens Jupyter
def open_jupyter(user):
    manager = UserContainerManager()
    container = manager.get_or_create_container(user)

    # Start Jupyter in container
    container.exec_run(
        cmd=["jupyter", "lab", "--ip=0.0.0.0", "--port=8888"],
        detach=True,
    )

    return redirect(f"/jupyter/{user.username}/")
```

## Summary

### What You Need to Prepare

1. **Image Definition** ✅ Required
   - Create `Dockerfile.user-workspace`
   - Include Python, R, scientific packages
   - Configure for non-root user
   - Build once, use for all users

2. **Build Script** ✅ Required
   - Automate image building
   - Version tagging
   - Push to registry (optional)

3. **Container Manager Service** ✅ Required
   - Python service to spawn/manage containers
   - Uses Docker Python SDK
   - Handles container lifecycle

4. **Integration** ✅ Required
   - SSH gateway uses container manager
   - Codespace UI uses container manager
   - JupyterLab uses container manager

### Workflow Summary
```
One time:
1. Build image: docker build -t scitex-user-workspace .
2. Image available on server (4GB, shared by all users)

Every user connection:
1. User connects (SSH or web UI)
2. System checks: Container for user X?
   - Not exist → Create from image (~10s first time)
   - Exists stopped → Start (~2-5s)
   - Exists running → Use immediately (instant)
3. User gets their workspace
4. User disconnects → Container keeps running
5. After 30 min idle → Container stops (saves resources)
6. User's data always persists in volume

Result: Fast, efficient, isolated workspaces
```

## Next Steps

1. Create `Dockerfile.user-workspace` with your required tools
2. Implement `UserContainerManager` service
3. Test with 1-2 users
4. Iterate on image (add/remove packages)
5. Implement SSH gateway integration
6. Add monitoring for container resources

<!-- EOF -->
