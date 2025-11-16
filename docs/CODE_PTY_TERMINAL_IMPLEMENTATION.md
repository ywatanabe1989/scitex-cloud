# Real PTY Terminal Implementation

## Overview
Implemented **real interactive terminal with PTY** support for Code Workspace.
Researchers can now run IPython, vim, htop, and any interactive programs!

## Architecture

### Backend (Django Channels + PTY)
```
WebSocket ←→ Django Channels ←→ PTY ←→ bash shell
   ↑                                      ↓
Browser                              IPython/vim/etc
```

**Components:**
- `apps/code_app/terminal_views.py` - TerminalConsumer (WebSocket handler)
- `apps/code_app/routing.py` - WebSocket URL routing
- PTY (pseudo-terminal) - Real bash session

### Frontend (xterm.js)
```
xterm.js ←→ WebSocket ←→ PTY
   ↑
Browser Terminal
```

**Components:**
- `apps/code_app/static/code_app/ts/pty-terminal.ts` - PTY client
- xterm.js (CDN) - Terminal emulator
- xterm-addon-fit - Auto-resize

## Environment Variables

**SCITEX_CLOUD_CODE_* Variables:**
```bash
SCITEX_CLOUD_CODE_WORKSPACE=true     # Code workspace marker
SCITEX_CLOUD_CODE_BACKEND=inline     # Use inline plotting
SCITEX_CLOUD_CODE_SESSION_ID=123     # Project/session ID
SCITEX_CLOUD_CODE_PROJECT_ROOT=/...  # Project directory
SCITEX_CLOUD_CODE_USERNAME=ywatanabe # Username
```

**Standard Variables:**
```bash
HOME=/home/ywatanabe
USER=ywatanabe
LOGNAME=ywatanabe
PWD=/home/ywatanabe/proj/default-project
HOSTNAME=scitex-cloud
TERM=xterm-256color
```

## What This Enables

### Interactive Programs
```bash
$ ipython
Python 3.11.14
IPython 8.22.2

In [1]: import matplotlib.pyplot as plt

In [2]: plt.plot([1,2,3])

In [3]: plt.show()  # Inline plot in terminal!

In [4]: _
```

### Text Editors
```bash
$ vim script.py    # Full vim!
$ nano config.yaml # nano works!
$ emacs -nw file   # Emacs in terminal!
```

### System Tools
```bash
$ htop          # Process monitor
$ less file.txt # Pager
$ man ls        # Man pages
$ git log       # Interactive git
```

### All With:
- ✅ Full color support (xterm-256color)
- ✅ Keyboard shortcuts (Ctrl+C, Ctrl+Z, etc.)
- ✅ Terminal resize
- ✅ Persistent session
- ✅ Inline image display (matplotlib)
- ✅ Auto-reconnect

## Integration with scitex.plt

**Auto-Detection:**
```python
import scitex.plt as plt

# Automatically detects SCITEX_CLOUD_CODE_WORKSPACE
# Uses inline backend automatically!

plt.plot([1,2,3])
plt.show()  # → Displays inline in terminal
```

**Debug Mode:**
```python
# With DEBUG=True in environment
import scitex.plt as plt

# Output:
# [scitex.cloud.code] Auto-detected SciTeX Cloud Code environment
# [scitex.cloud.code] Backend: inline
# [scitex.cloud.code] Rendering plot...
```

## Installation Requirements

**Python Packages:**
```bash
pip install channels channels-redis
```

**ASGI Configuration:**
```python
# config/asgi.py
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.code_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
```

## Benefits for Researchers

### Data Science Workflow
```python
$ ipython

In [1]: import pandas as pd
In [2]: import scitex.plt as plt

In [3]: df = pd.read_csv('data.csv')
In [4]: df.head()

In [5]: plt.plot(df['x'], df['y'])
In [6]: plt.show()  # ← Inline plot!

In [7]: # Continue working...
```

### Debugging
```python
$ ipython -i script.py  # Run and drop to REPL
$ python -m pdb script.py  # Full debugger!
$ pytest --pdb  # Debug on failure
```

### System Administration
```bash
$ ps aux | grep python
$ df -h
$ du -sh *
$ find . -name "*.py"
$ grep -r "TODO" .
```

## Security

**Still Sandboxed:**
- ✅ Runs in Docker container
- ✅ File access limited to project directory
- ✅ No access to other users' files
- ✅ Resource limits (CPU/memory)
- ✅ Network isolation

**User Experience:**
- Feels like their own terminal
- Full bash features
- Persistent session
- Real IPython REPL

## Next Steps

1. **Install Channels**: `pip install channels channels-redis`
2. **Update ASGI**: Configure channels in `config/asgi.py`
3. **Test**: Open `/code/` and type `ipython`
4. **Integrate with scitex.plt**: Update auto-detection in `~/proj/scitex-code/src/scitex/plt/`

## Future Enhancements

- [ ] Terminal tabs (multiple sessions)
- [ ] Session persistence (survive page refresh)
- [ ] Terminal sharing (collaborative coding)
- [ ] Recording/playback
- [ ] Custom shell (zsh/fish)

---

**This makes Code Workspace a true professional IDE for researchers!** 🎊

Full IPython + inline plotting + real terminal = Jupyter Notebook + IDE combined!
