# SciTeX Package Installation Strategy

## Overview

The `scitex` Python package is installed differently depending on the environment:

- **Development:** Editable install from local `/scitex-code` (for active development)
- **Production:** PyPI install (stable releases)
- **NAS:** PyPI install (stable releases)

## Installation Methods

### Development (Editable Mode)

**Where:** `docker_dev/`

**Method:** Volume mount + pip editable install

**docker-compose.dev.yml:**
```yaml
volumes:
  - /home/ywatanabe/proj/scitex-code:/scitex-code  # Mount local dev repo
```

**entrypoint.sh:**
```bash
if [ -d "/scitex-code" ]; then
    pip install --user -e /scitex-code  # Editable install
fi
```

**Benefits:**
- Live code changes (no rebuild needed)
- Local development workflow
- Can modify scitex package simultaneously

**Requirements:**
- Local scitex-code repository at `/home/ywatanabe/proj/scitex-code`
- Git repository for development

---

### Production (PyPI)

**Where:** `docker_prod/`

**Method:** PyPI install in Dockerfile

**Dockerfile.prod:**
```dockerfile
# Stage 1: python-builder
RUN uv pip install --system scitex[web,scholar,writer]
```

**docker-compose.prod.yml:**
```yaml
volumes:
  - static_volume:/app/staticfiles
  - media_volume:/app/media
  # No scitex-code mount
```

**entrypoint.sh:**
```bash
if [ -d "/scitex-code" ]; then
    # Editable install (dev only)
else
    python -c "import scitex; print(f'✅ Scitex {scitex.__version__} available')"
fi
```

**Benefits:**
- Stable, tested releases
- No dependency on local filesystem
- Faster container startup
- Smaller attack surface

**Requirements:**
- scitex published to PyPI
- Pinned version in requirements (optional but recommended)

---

### NAS (PyPI)

**Where:** `docker_nas/`

**Method:** Same as Production (PyPI install)

**Dockerfile:** Uses `docker_prod/Dockerfile.prod`

**Benefits:**
- Same as production
- No need to sync local scitex-code to NAS

---

## Package Extras

### For SciTeX-Cloud (Minimal)
```dockerfile
RUN uv pip install --system scitex[web,scholar,writer]
```

**Includes:**
- `web` - FastAPI, Flask, Streamlit
- `scholar` - Playwright, Selenium, bibtexparser
- `writer` - yq (YAML parser)

**Size:** ~500 MB

### Complete Toolkit (Optional)
```dockerfile
RUN uv pip install --system scitex[all,dev]
```

**Includes:** dl, ml, jupyter, neuro, web, scholar, writer, dev

**Size:** ~2-5 GB

---

## Development Workflow

### Scenario 1: Developing SciTeX Cloud Only

```bash
# Start dev environment (scitex from PyPI)
cd containers/docker_dev
# Comment out /scitex-code volume mount
docker compose up
```

### Scenario 2: Developing Both Cloud + Package

```bash
# Start dev environment (scitex editable)
cd containers/docker_dev
# Ensure /scitex-code volume mount is present
make -f Makefile.dev start

# Edit scitex package
cd /home/ywatanabe/proj/scitex-code/src/scitex
# Make changes - reflected immediately in container
```

### Scenario 3: Testing PyPI Version in Dev

```bash
# Temporarily remove mount
cd containers/docker_dev
# Comment out: - /home/ywatanabe/proj/scitex-code:/scitex-code
docker compose down && docker compose up --build
```

---

## Publishing to PyPI

### 1. Build Package
```bash
cd /home/ywatanabe/proj/scitex-code
python -m build
```

### 2. Upload to PyPI
```bash
python -m twine upload dist/*
```

### 3. Verify
```bash
pip install scitex[web,scholar,writer]
python -c "import scitex; print(scitex.__version__)"
```

### 4. Update Production
```bash
# Rebuild prod image (will pull new version from PyPI)
cd /home/ywatanabe/proj/scitex-cloud
make ENV=prod rebuild
```

---

## Version Management

### Development
- Always uses latest code from `/scitex-code`
- No version pinning needed
- `scitex.__version__` from local source

### Production
- Uses specific version from PyPI
- Pin version in `requirements.txt` (optional):
  ```
  scitex[web,scholar,writer]==2.1.0
  ```
- Or use latest: `scitex[web,scholar,writer]` (not recommended)

---

## Troubleshooting

### Dev: "ModuleNotFoundError: scitex"

**Check volume mount:**
```bash
docker exec docker-web-1 ls -la /scitex-code
# Should show scitex package files
```

**Check installation:**
```bash
docker exec docker-web-1 pip show scitex
# Should show: Location: /scitex-code/src
```

**Fix:**
```bash
# Ensure mount in docker-compose.dev.yml
volumes:
  - /home/ywatanabe/proj/scitex-code:/scitex-code
```

### Prod: "ModuleNotFoundError: scitex"

**Check PyPI installation:**
```bash
docker exec <prod-container> pip show scitex
# Should show: Location: /usr/local/lib/python3.11/site-packages
```

**Fix:**
```bash
# Rebuild Dockerfile (installs from PyPI)
cd containers/docker_prod
docker compose build
```

### Version Mismatch

**Check version:**
```bash
# Dev (from local)
docker exec docker-web-1 python -c "import scitex; print(scitex.__version__)"

# Prod (from PyPI)
docker exec <prod-container> python -c "import scitex; print(scitex.__version__)"
```

---

## Summary

| Environment | Install Method | Source | Update Method |
|-------------|---------------|---------|---------------|
| **Dev** | Editable (`-e`) | `/scitex-code` mount | Edit local files |
| **Prod** | PyPI | PyPI registry | Rebuild Dockerfile |
| **NAS** | PyPI | PyPI registry | Rebuild Dockerfile |

**Key Points:**
- Dev = Editable (for active development)
- Prod/NAS = PyPI (for stability)
- Entrypoint detects mode automatically
- No manual intervention needed

---

**Related Files:**
- `pyproject.toml` - Package definition
- `Dockerfile.dev` - Dev install (no scitex in Dockerfile)
- `Dockerfile.prod` - Prod install (scitex from PyPI)
- `entrypoint.sh` - Auto-detection logic
- `docker-compose.*.yml` - Volume mounts
