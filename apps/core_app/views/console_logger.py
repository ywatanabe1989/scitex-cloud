"""
Console Logger View - Captures browser console logs to server file
"""
import json
import logging
from pathlib import Path

from django.conf import settings
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods

# Setup dedicated console logger
console_log_file = Path(settings.BASE_DIR) / "logs" / "console.log"
console_log_file.parent.mkdir(parents=True, exist_ok=True)

console_logger = logging.getLogger('browser_console')
console_logger.setLevel(logging.DEBUG)

# File handler
file_handler = logging.FileHandler(console_log_file)
file_handler.setLevel(logging.DEBUG)

# Format: [timestamp] LEVEL: message (file:line:col)
formatter = logging.Formatter(
    '[%(asctime)s] %(levelname)s: %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
file_handler.setFormatter(formatter)
console_logger.addHandler(file_handler)

# Prevent propagation to root logger
console_logger.propagate = False


@csrf_exempt  # Allow from dev frontend without CSRF
@require_http_methods(["POST"])
def log_console(request):
    """
    Receive browser console logs and write to ./logs/console.log

    Expected payload:
    {
        "logs": [
            {
                "level": "log|info|warn|error",
                "message": "Console message",
                "source": "file.js:123:45",
                "timestamp": 1234567890.123,
                "url": "http://localhost:8000/writer/"
            },
            ...
        ]
    }
    """
    try:
        data = json.loads(request.body)
        logs = data.get('logs', [])

        # Map console levels to logging levels
        level_map = {
            'log': logging.INFO,
            'info': logging.INFO,
            'warn': logging.WARNING,
            'warning': logging.WARNING,
            'error': logging.ERROR,
            'debug': logging.DEBUG,
        }

        for log_entry in logs:
            level = log_entry.get('level', 'log').lower()
            message = log_entry.get('message', '')
            source = log_entry.get('source', '')
            url = log_entry.get('url', '')

            # Format log message
            log_msg = f"{message}"
            if source:
                log_msg += f" ({source})"
            if url:
                log_msg += f" | {url}"

            log_level = level_map.get(level, logging.INFO)
            console_logger.log(log_level, log_msg)

        return JsonResponse({'status': 'ok', 'logged': len(logs)})

    except Exception as e:
        console_logger.error(f"Failed to process console logs: {e}")
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
