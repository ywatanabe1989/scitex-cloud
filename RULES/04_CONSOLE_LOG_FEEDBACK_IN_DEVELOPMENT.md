# Console Log Feedback in Development

## Overview

Browser console logs are automatically captured and written to `./logs/console.log` during development, providing **tee-like functionality** where logs appear in both the browser DevTools and the server log file.

This feature dramatically improves debugging by:
- Centralizing all console output in one accessible file on the host
- Preserving logs even after browser sessions end
- Enabling analysis of console output across multiple pages/sessions
- Capturing source file locations and timestamps

## Architecture

### Component 1: TypeScript Console Interceptor
**File:** `static/ts/utils/console-interceptor.ts`
**Compiled to:** `static/js/utils/console-interceptor.js`

**Key Features:**
- Intercepts: `console.log`, `console.info`, `console.warn`, `console.error`, `console.debug`
- **Tee behavior:** Original console methods preserved (shows in DevTools) + sends to server
- **Batching:** Collects logs and sends every 1 second OR when buffer reaches 50 entries
- **Source tracking:** Parses stack traces to capture file path, line number, column
- **Smart activation:** Only active on localhost/127.0.0.1 (detected automatically)

**How it works:**
```typescript
// Intercept console.log
console.log = function(...args: any[]) {
    self.originalConsole.log.apply(console, args);  // Show in browser (tee)
    self.capture('log', args);                       // Send to server (tee)
};
```

### Component 2: Django API Endpoint
**File:** `apps/core_app/views/console_logger.py`
**Endpoint:** `POST /dev/api/console/`
**URL Config:** `apps/dev_app/urls.py`

**Functionality:**
- Receives batched console logs from browser
- Only active when `settings.DEBUG = True`
- Maps console levels to Python logging levels:
  - `log`, `info` → `logging.INFO`
  - `warn`, `warning` → `logging.WARNING`
  - `error` → `logging.ERROR`
  - `debug` → `logging.DEBUG`
- Writes to `./logs/console.log` with formatting

**Expected Payload:**
```json
{
  "logs": [
    {
      "level": "log|info|warn|error|debug",
      "message": "Console message text",
      "source": "file.js:123:45",
      "timestamp": 1234567890123,
      "url": "http://127.0.0.1:8000/page/"
    }
  ]
}
```

### Component 3: Global Integration
**File:** `templates/global_base_partials/global_head_meta.html`

The console interceptor is loaded globally in the `<head>` section:
```html
<!-- Console Logger (Development Only) -->
<script src="{% static 'js/utils/console-interceptor.js' %}"></script>
```

This ensures it's active on **all pages** across the entire application.

## Log Output Format

**File location:** `./logs/console.log` (on host)

**Format:**
```
[YYYY-MM-DD HH:MM:SS] LEVEL: message (source:line:col) | url
```

**Example:**
```
[2025-11-05 11:00:23] INFO: ✅ Test message (utils/console-interceptor.js:44:18) | http://127.0.0.1:8000/
[2025-11-05 11:00:23] WARN: ⚠️  Warning occurred (file_view.js:102:12) | http://127.0.0.1:8000/writer/
[2025-11-05 11:00:23] ERRO: ❌ API call failed (api.js:55:8) | http://127.0.0.1:8000/search/
```

## Usage

### For Developers

**1. Console output automatically captured:**
```javascript
// In any JavaScript/TypeScript file
console.log("User clicked button");        // → Appears in DevTools + logs/console.log
console.warn("API rate limit approaching"); // → Appears in DevTools + logs/console.log
console.error("Failed to load data");       // → Appears in DevTools + logs/console.log
```

**2. View logs on host:**
```bash
# Watch logs in real-time
tail -f ./logs/console.log

# Search for specific errors
grep "ERROR" ./logs/console.log

# Filter by source file
grep "file_view.js" ./logs/console.log

# Show last 50 entries
tail -50 ./logs/console.log
```

**3. Debug TypeScript compilation issues:**
Since TypeScript compiles to JavaScript and this system tracks source locations, you can see exactly where issues occur in your compiled code.

### Important Notes

1. **No code changes needed:** Just write normal `console.log()` statements
2. **Zero impact on production:** Only active on localhost/127.0.0.1
3. **CSRF exempt:** The `/dev/api/console/` endpoint is CSRF-exempt for convenience
4. **Volume mounted:** `./logs/` directory is Docker-volume-mounted, so logs persist on host
5. **Batching reduces overhead:** Network requests are minimized through batching

## System Flow

```
Browser JavaScript/TypeScript
         ↓
    console.log("message")
         ↓
   Console Interceptor
         ↓
    ┌────┴────┐
    ↓         ↓
DevTools   Buffer (1s or 50 entries)
(tee)          ↓
          POST /dev/api/console/
               ↓
        Django View Handler
               ↓
         Python logging
               ↓
      ./logs/console.log (host)
```

## Files Modified/Created

### Created:
- `static/ts/utils/console-interceptor.ts` (TypeScript source)
- `static/js/utils/console-interceptor.js` (compiled, auto-generated)
- `apps/core_app/views/console_logger.py` (Django endpoint)
- `RULES/04_CONSOLE_LOG_FEEDBACK_IN_DEVELOPMENT.md` (this file)

### Modified:
- `templates/global_base_partials/global_head_meta.html` (added script tag)
- `apps/dev_app/urls.py` (added URL route)
- `.gitignore` (already ignores `*.log`)

## Troubleshooting

### Logs not appearing in file?

1. **Check if script is loaded:**
   - Open DevTools → Console
   - Look for: `[Console Interceptor] Active - logs will be saved to ./logs/console.log`

2. **Check endpoint accessibility:**
   ```bash
   curl -X POST http://127.0.0.1:8000/dev/api/console/ \
     -H "Content-Type: application/json" \
     -d '{"logs":[{"level":"log","message":"test","source":"","timestamp":0,"url":""}]}'
   ```

3. **Check Django DEBUG setting:**
   - Endpoint only works when `DEBUG = True`

4. **Check log file permissions:**
   ```bash
   ls -la ./logs/console.log
   ```

### Network errors in DevTools?

- The interceptor gracefully handles network failures
- Failed batches are logged to original console with warning
- Does not interrupt normal application operation

## Performance Considerations

- **Batching:** Logs sent every 1 second (not per log)
- **Max batch size:** 50 entries per request
- **Network overhead:** Minimal due to batching
- **Production impact:** Zero (only active on localhost)

## Future Enhancements

Possible improvements:
- [ ] WebSocket connection for real-time streaming
- [ ] Log level filtering (capture only errors/warnings)
- [ ] Searchable web UI for log viewing
- [ ] Integration with structured logging format (JSON)
- [ ] Automatic log rotation/cleanup

## Related Documentation

- `RULES/02_TYPESCRIPT_HOT_BUILDING_IN_DEVELOPMENT.md` - TypeScript compilation
- `RULES/03_TYPESCRIPT_WATCH_MECHANISM.md` - How TypeScript detects changes
- `apps/dev_app/README.md` - Development app documentation

---

**Last Updated:** 2025-11-05
**Status:** ✅ Fully Implemented and Tested

<!-- EOF -->