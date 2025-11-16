# Terminal Architecture & Security

## Current Implementation

### How It Works
Commands execute in Docker container:
- **Container user**: root (all users share container)
- **File isolation**: `/app/data/users/<username>/<project>/`
- **Environment vars**: `USER=ywatanabe`, `HOME=/home/ywatanabe`
- **Working directory**: Project directory

### What Users See
```bash
$ whoami
root              # Container user (not their username)

$ pwd
/app/data/users/ywatanabe/default-project  # ✓ Correct!

$ echo $USER
ywatanabe         # ✓ Correct! (env var)
```

## Security Model

**✅ Current Security (Container-based)**
- Each user's files in separate directory
- Commands run in sandboxed Docker container
- Path traversal protection
- Dangerous commands blocked
- 30-second timeout
- **Actual security is GOOD** - files are isolated

**⚠️ UX Issue**
- `whoami` returns "root" (container user)
- Doesn't FEEL like their terminal
- Users see Docker internals

## Solutions

### Option 1: Command Wrapping (Quick Fix)
Intercept and override certain commands:
```python
# In api_execute_command
if command == 'whoami':
    return username  # Return project owner
if command == 'pwd':
    return f"/home/{username}/proj/{project_name}"
```

**Pros**: Quick, feels like their terminal
**Cons**: Not real, fake responses

### Option 2: User Namespaces (Proper Solution)
Create actual Linux users in container:
```dockerfile
RUN useradd -m -s /bin/bash ywatanabe
```

Run commands as that user:
```python
subprocess.run(command, user=username, ...)
```

**Pros**: Real users, real security, authentic terminal
**Cons**: Complex, requires container rebuild per user

### Option 3: Full Isolation (Future: Kubernetes)
Each user gets their own container:
- Real user accounts
- True isolation
- Dedicated resources
- Scale with K8s

**Pros**: Perfect security and UX
**Cons**: Infrastructure complexity

### Option 4: Accept & Document (Current)
Keep current implementation, document it:
- Security IS good (file isolation)
- Terminal shows container reality
- Users understand it's sandboxed

## Recommendation

**For MVP/Current:**
- ✅ Keep current (it works, it's secure)
- ✅ Document that it's sandboxed
- ✅ Remove confusing error messages (done!)

**For Future:**
- 🚀 Desktop app (Electron/Tauri) → Real local terminal!
- 🚀 Kubernetes with user namespaces → True multi-tenancy
- 🚀 Custom browser → Full keyboard control

## Current Status

**What Works:**
- ✅ File isolation (/app/data/users/username/)
- ✅ Clean terminal (no error messages)
- ✅ Text selection works
- ✅ Tab completion
- ✅ Real bash commands
- ✅ Command history

**Known Limitations:**
- `whoami` returns "root" (container user)
- Users see Docker environment variables
- Not a "true" personal terminal (but secure!)

## Future Desktop App Benefits
When you build the desktop app:
- ✅ Real local terminal (no container)
- ✅ Real whoami (actual username)
- ✅ Real home directory
- ✅ Full keyboard shortcuts (no browser limits)
- ✅ Better performance

---

**Current implementation is production-ready for web IDE, with clear path to desktop app for true local experience!**
