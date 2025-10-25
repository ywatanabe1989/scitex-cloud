<!-- ---
!-- Timestamp: 2025-10-26 01:47:13
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/containers/docker/DOCKER_SETUP.md
!-- --- -->

# Docker Setup Guide

How to install and configure Docker on Ubuntu.

---

## Install Docker

```bash
# Update package index
sudo apt update

# Install Docker
sudo apt install -y docker.io

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Verify installation
sudo docker --version
docker-compose --version
```

**Expected output:**
```
Docker version 28.x.x
docker-compose version 1.29.2
```

---

## Configure Permissions

```bash
# Add your user to docker group
sudo usermod -aG docker $USER

# Activate group membership
newgrp docker

# Verify (should work without sudo)
docker ps
```

**If `docker ps` works without sudo, you're ready!**

---

## Troubleshooting

**Permission denied when running docker commands?**

```bash
# Option 1: Use sudo
sudo docker-compose ...

# Option 2: Fix permissions
sudo usermod -aG docker $USER
newgrp docker
```

**Docker service not running?**

```bash
sudo systemctl start docker
sudo systemctl status docker
```

**Check Docker is working:**

```bash
docker run hello-world
```

---

**Next:** See `README_PROD.md` for deployment instructions.

<!-- EOF -->
