# Requirements Management

## 📦 Single Source of Truth

**Location:**
```
./requirements.txt (project root)
```

This is the ONLY requirements file. All Dockerfiles use this file.

---

## 🏗️ How Docker Uses It

All Docker environments (dev, prod, nas) use the same requirements.txt:

```dockerfile
# deployment/docker/docker_dev/Dockerfile
# deployment/docker/docker_prod/Dockerfile
# deployment/docker/docker_nas/Dockerfile

# Build context is set to project root:
build:
  context: ../../..              # = project root

# Dockerfile copies from context root:
COPY requirements.txt .          # Copies ./requirements.txt
RUN uv pip install --system -r requirements.txt
```

---

## ✏️ How to Update Dependencies

### Add a New Package

1. Edit `./requirements.txt`:
   ```bash
   # Add new package with version
   newpackage==1.2.3  # Description of why we need it
   ```

2. Rebuild Docker image:
   ```bash
   make ENV=dev rebuild
   ```

3. Verify installation:
   ```bash
   docker exec scitex-cloud-dev-web-1 pip show newpackage
   ```

### Update Package Version

```diff
- oldpackage==1.0.0
+ oldpackage==2.0.0
```

Then rebuild: `make ENV=dev rebuild`

---

## ⚠️ Common Mistakes to Avoid

### ❌ Wrong: pip install flags in requirements.txt

```python
# DON'T DO THIS:
django --break-system-packages
requests --upgrade
```

**Why it breaks:**
- These are CLI flags for `pip install`, not package specifications
- Will cause build to fail silently
- Docker falls back to old cached image

**Correct:**
```python
# DO THIS:
django==5.2.7
requests==2.32.5
```

### ❌ Wrong: Creating multiple requirements files

```
./requirements.txt           # Main
./deployment/requirements.txt  # ❌ DON'T CREATE THIS
./requirements-dev.txt         # ❌ DON'T CREATE THIS
./requirements-prod.txt        # ❌ DON'T CREATE THIS
```

**Why it's bad:**
- Causes confusion about which file is used
- Files get out of sync
- Missing critical dependencies (like daphne incident)

**Correct:**
```
./requirements.txt           # ONLY THIS FILE
```

---

## 🔍 Verification

### Check what's actually installed in container:

```bash
# List all packages
docker exec scitex-cloud-dev-web-1 pip list

# Check specific package
docker exec scitex-cloud-dev-web-1 pip show daphne

# Compare with requirements.txt
diff <(docker exec scitex-cloud-dev-web-1 cat /app/requirements.txt) ./requirements.txt
# Should show: no differences
```

### Check which file Docker is using:

```bash
# Show requirements.txt inside container
docker exec scitex-cloud-dev-web-1 cat /app/requirements.txt | head -20

# Should match project root
cat ./requirements.txt | head -20
```

---

## 📋 Current Package List

**Total packages:** 90+

**Critical packages:**
- `django==5.2.7` - Web framework
- `daphne==4.1.2` - ASGI server (WebSocket support)
- `channels==4.3.1` - WebSocket channels
- `playwright==1.48.0` - Browser automation
- `docker==7.1.0` - Container management
- `paramiko==3.4.0` - SSH gateway
- `psycopg2-binary==2.9.9` - PostgreSQL driver

**Full list:** See `./requirements.txt`

---

## 🛠️ Troubleshooting

### Build fails silently, old packages used

**Symptom:** After updating requirements.txt, `make rebuild` completes but new packages aren't installed.

**Cause:** Syntax error in requirements.txt (like `--break-system-packages`)

**Solution:**
1. Check build logs: `docker build -f deployment/docker/docker_dev/Dockerfile . 2>&1 | grep -E "error|ERROR"`
2. Fix syntax errors
3. Rebuild: `make ENV=dev rebuild`

### Package version conflicts

**Symptom:** Build fails with dependency resolution errors

**Solution:**
```bash
# Check which package has conflicts
uv pip compile requirements.txt

# Update conflicting versions
```

### Missing package at runtime

**Symptom:** Import error when running Django

**Solution:**
1. Add to `./requirements.txt`
2. Rebuild: `make ENV=dev rebuild`
3. Don't use `docker exec ... pip install` (won't persist)

---

## 📝 Best Practices

1. **Always specify versions:**
   ```python
   ✅ django==5.2.7
   ❌ django
   ```

2. **Add comments for non-obvious packages:**
   ```python
   daphne==4.1.2  # ASGI server for WebSocket support
   ```

3. **Group related packages:**
   ```python
   # Database
   psycopg2-binary==2.9.9

   # WebSocket support
   channels==4.3.1
   channels-redis==4.3.0
   daphne==4.1.2
   ```

4. **Test after changes:**
   ```bash
   make ENV=dev rebuild
   make ENV=dev test
   ```

5. **Never bypass the requirements file:**
   ```bash
   # ❌ DON'T: Manual install (lost on rebuild)
   docker exec ... pip install newpackage

   # ✅ DO: Add to requirements.txt and rebuild
   echo "newpackage==1.0.0" >> requirements.txt
   make ENV=dev rebuild
   ```

---

## 🎯 Summary

- **One file:** `./requirements.txt` (project root)
- **All environments:** Use same file (dev, prod, nas)
- **Update process:** Edit file → `make ENV=dev rebuild`
- **Verification:** Check container has matching file

**Remember:** If you update requirements.txt, you MUST rebuild the Docker image!

---

**Last Updated:** 2025-11-17
**Related:** See Dockerfile at `deployment/docker/docker_dev/Dockerfile:134`
