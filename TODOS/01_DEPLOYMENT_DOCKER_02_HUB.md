<!-- ---
!-- Timestamp: 2025-10-26 16:50:11
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/01_DEPLOYMENT_DOCKER_HUB.md
!-- --- -->

# SciTeX Cloud - DockerHub Deployment Guide

## Prerequisites

- [ ] Create DockerHub account: https://hub.docker.com/
- [ ] Generate DockerHub access token (Settings > Security > Access Tokens)
- [ ] Understand image naming: `username/repository:tag`

---

## Manual Deployment

### 1. Login to DockerHub

```bash
docker login
# Enter username and password/token when prompted
```

### 2. Build and Tag

```bash
# Build for development
docker build -t ywatanabe1989/scitex-cloud:latest \
  -f containers/docker/Dockerfile .

# Or tag existing local image
docker tag docker_web:latest ywatanabe1989/scitex-cloud:latest

# Build with version tags
docker build -t ywatanabe1989/scitex-cloud:v1.0.0 \
  -f containers/docker/Dockerfile .
```

### 3. Push to DockerHub

```bash
# Push latest
docker push ywatanabe1989/scitex-cloud:latest

# Push versioned
docker push ywatanabe1989/scitex-cloud:v1.0.0
```

### 4. Verify

Visit: https://hub.docker.com/r/ywatanabe1989/scitex-cloud

---

## Automated CI/CD with GitHub Actions

Create `.github/workflows/docker-publish.yml`:

```yaml
name: Build and Publish to DockerHub

on:
  push:
    branches:
      - main
      - develop
    tags:
      - 'v*'
  workflow_dispatch:  # Allow manual trigger

env:
  REGISTRY: docker.io
  IMAGE_NAME: ywatanabe1989/scitex-cloud

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    permissions:
      contents: read
      packages: write

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v3

      - name: Login to DockerHub
        uses: docker/login-action@v3
        with:
          username: ${{ secrets.DOCKER_USERNAME }}
          password: ${{ secrets.DOCKER_PASSWORD }}

      - name: Extract metadata
        id: meta
        uses: docker/metadata-action@v5
        with:
          images: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}
          tags: |
            type=ref,event=branch
            type=semver,pattern={{version}}
            type=semver,pattern={{major}}.{{minor}}
            type=sha
            type=raw,value=latest,enable={{is_default_branch}}

      - name: Build and push
        uses: docker/build-push-action@v5
        with:
          context: .
          file: containers/docker/Dockerfile
          push: true
          tags: ${{ steps.meta.outputs.tags }}
          labels: ${{ steps.meta.outputs.labels }}
          cache-from: type=gha
          cache-to: type=gha,mode=max
```

### Setup GitHub Secrets

1. Go to repository Settings > Secrets and Variables > Actions
2. Add these secrets:
   - `DOCKER_USERNAME`: Your DockerHub username
   - `DOCKER_PASSWORD`: Your DockerHub access token

---

## Multi-Image Strategy

For production, consider separate images optimized for different use cases:

### Image Variants

| Image | Use Case | Dependencies |
|-------|----------|--------------|
| `scitex-cloud:core` | Minimal web app | Django, PostgreSQL client |
| `scitex-cloud:scholar` | Paper management | + scholar module (bs4, feedparser) |
| `scitex-cloud:full` | All features | All extras (scholar, web, jupyter, ml) |
| `scitex-cloud:latest` | Latest dev build | Equivalent to `full` |

### Example Matrix Build in GitHub Actions

```yaml
build-matrix:
  runs-on: ubuntu-latest
  strategy:
    matrix:
      variant: [core, scholar, full]
  steps:
    - name: Build variant
      uses: docker/build-push-action@v5
      with:
        build-args: |
          SCITEX_EXTRAS=${{ matrix.variant }}
        tags: ${{ env.REGISTRY }}/${{ env.IMAGE_NAME }}:${{ matrix.variant }}
```

---

## Important Considerations

### Security & Secrets

- ✅ Mount `.env` files as volumes, don't bake into image
- ✅ Use Docker secrets for sensitive data in swarm/k8s
- ❌ Never commit `.env` files to git
- ❌ Never include API keys or passwords in Dockerfile

### Image Size

Current estimated sizes:
- Core: ~500MB
- Scholar: ~1.5GB
- Full (all extras): ~3-5GB

**Optimization options:**
- Use multi-stage builds to exclude build dependencies
- Separate production/development Dockerfiles
- Consider distroless base images for minimal size

### License & Attribution

Document included licenses in image:
- Create `LICENSE.md` in Docker image
- Include in README
- All dependencies must comply with project license

---

## Quick Reference

### Deploy Latest Dev Build

```bash
docker pull ywatanabe1989/scitex-cloud:latest
docker-compose -f docker-compose.prod.yml up -d
```

### Run Specific Version

```bash
docker run -d \
  -p 8000:8000 \
  --env-file .env.prod \
  ywatanabe1989/scitex-cloud:v1.0.0
```

### Check Image History

```bash
docker history ywatanabe1989/scitex-cloud:latest
```

### View DockerHub Stats

```bash
# From CLI (requires authentication)
docker inspect ywatanabe1989/scitex-cloud:latest
```

---

## Status Checklist

- [x] DockerHub account created
- [ ] Initial image pushed manually
- [ ] GitHub Actions workflow configured
- [ ] Secrets added to repository
- [ ] First automated build triggered
- [ ] Multi-image strategy documented
- [ ] Production docker-compose.yml updated
- [ ] LICENSE.md added to documentation

<!-- EOF -->