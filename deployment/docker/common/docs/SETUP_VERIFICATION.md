# SciTeX Package Installation - Setup Verification

## ✅ Current Configuration (Correct!)

### Development Environment

**1. Volume Mount** (`docker_dev/docker-compose.dev.yml`):
```yaml
volumes:
  - /home/ywatanabe/proj/scitex-code:/scitex-code  # ✅ Mounts local repo
```

**2. Entrypoint Detection** (`common/scripts/entrypoint.sh`):
```bash
if [ -d "/scitex-code" ]; then
    echo "📦 Development mode: Installing scitex from /scitex-code (editable)..."
    pip install --user -e /scitex-code  # ✅ Editable install
    echo "✅ Scitex package installed in editable mode!"
fi
```

**3. Dockerfile** (`docker_dev/Dockerfile.dev`):
- ✅ Does NOT install scitex (correct - installed by entrypoint)
- ✅ Only installs requirements.txt
- ✅ Mounts handle the scitex package

**Result:**
- ✅ Editable install: `/scitex-code` → `pip install -e`
- ✅ Live changes: Edit local files, no rebuild needed
- ✅ Development workflow: Simultaneous cloud + package development

---

### Production Environment

**1. No Volume Mount** (`docker_prod/docker-compose.prod.yml`):
```yaml
volumes:
  - static_volume:/app/staticfiles
  - media_volume:/app/media
  # ✅ No /scitex-code mount (correct)
```

**2. Dockerfile Install** (`docker_prod/Dockerfile.prod`):
```dockerfile
# Install scitex from PyPI (production uses stable releases)
RUN --mount=type=cache,target=/root/.cache/uv \
    uv pip install --system scitex[web,scholar,writer]  # ✅ From PyPI
```

**3. Entrypoint Detection** (`common/scripts/entrypoint.sh`):
```bash
if [ -d "/scitex-code" ]; then
    # Skipped in prod (no mount)
else
    echo "📦 Production mode: Using scitex from PyPI (installed in Dockerfile)"
    python -c "import scitex; print(f'✅ Scitex {scitex.__version__} available')"
fi
```

**Result:**
- ✅ PyPI install: Stable release from package registry
- ✅ No local dependency: Works anywhere
- ✅ Production workflow: Predictable, versioned releases

---

### NAS Environment

**Same as Production:**
- ✅ No volume mount
- ✅ Installs from PyPI in Dockerfile
- ✅ Uses stable releases

---

## Installation Flow

### Development Startup

```
1. Docker Compose starts container
   └─> Mounts: /home/ywatanabe/proj/scitex-code → /scitex-code

2. Entrypoint runs
   └─> Detects: /scitex-code exists
   └─> Executes: pip install --user -e /scitex-code
   └─> Result: Editable install, live changes

3. Django starts
   └─> import scitex → from /scitex-code/src/
```

### Production Startup

```
1. Docker Build
   └─> Runs: uv pip install scitex[web,scholar,writer]
   └─> Result: Installed from PyPI to /usr/local/lib/python3.11/site-packages

2. Docker Compose starts container
   └─> No /scitex-code mount

3. Entrypoint runs
   └─> Detects: /scitex-code does NOT exist
   └─> Verifies: import scitex (already installed)

4. Django starts
   └─> import scitex → from site-packages
```

---

## Testing the Setup

### Verify Dev (Editable)

```bash
# Start dev
make start

# Check installation
docker exec docker-web-1 pip show scitex
# Expected: Location: /scitex-code/src (editable)

# Verify editable mode
docker exec docker-web-1 python -c "
import scitex
import os
print(f'Version: {scitex.__version__}')
print(f'Path: {scitex.__file__}')
print(f'Editable: {'/scitex-code' in scitex.__file__}')
"
# Expected: Editable: True
```

### Verify Prod (PyPI)

```bash
# Build prod
make ENV=prod build

# Check installation
docker exec <prod-container> pip show scitex
# Expected: Location: /usr/local/lib/python3.11/site-packages

# Verify NOT editable
docker exec <prod-container> python -c "
import scitex
print(f'Version: {scitex.__version__}')
print(f'Path: {scitex.__file__}')
print(f'From PyPI: {'site-packages' in scitex.__file__}')
"
# Expected: From PyPI: True
```

---

## Common Scenarios

### Scenario: Update scitex in Dev

```bash
# Edit local scitex-code
cd /home/ywatanabe/proj/scitex-code/src/scitex
vim scholar/search.py

# Changes reflected immediately (no restart needed)
# If Python changes require restart:
make restart
```

### Scenario: Update scitex in Prod

```bash
# 1. Publish new version to PyPI
cd /home/ywatanabe/proj/scitex-code
python -m build
python -m twine upload dist/*

# 2. Update requirements.txt (optional - pin version)
echo "scitex[web,scholar,writer]==2.1.1" >> requirements.txt

# 3. Rebuild prod
make ENV=prod rebuild
```

### Scenario: Switch Dev to PyPI (testing)

```bash
# 1. Edit docker-compose.dev.yml
# Comment out: - /home/ywatanabe/proj/scitex-code:/scitex-code

# 2. Update Dockerfile.dev to install from PyPI
# Add: RUN uv pip install --system scitex[web,scholar,writer]

# 3. Rebuild
make rebuild
```

---

## Summary

**✅ Development:**
- Mounts: `/home/ywatanabe/proj/scitex-code` → `/scitex-code`
- Install: `pip install -e /scitex-code` (entrypoint)
- Mode: Editable (live changes)

**✅ Production:**
- Mounts: None
- Install: `uv pip install scitex[web,scholar,writer]` (Dockerfile)
- Mode: PyPI (stable releases)

**✅ NAS:**
- Same as Production

**The setup is correct and follows best practices!** 🎯
