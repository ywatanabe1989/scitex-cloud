"""
Concatenate repository files API endpoint.
"""

from __future__ import annotations

import json
import logging
import shutil

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .state import _temp_repos

logger = logging.getLogger(__name__)


@require_http_methods(["POST"])
def api_concatenate_repo(request):
    """
    Concatenate repository files and cleanup.

    POST data:
    - temp_path: Path to cloned repository
    - max_lines: Maximum lines per file
    - max_depth: Maximum directory depth
    - extensions: List of file extensions to include

    Returns:
    - content: Concatenated markdown content
    - stats: File count, line count, character count
    """
    try:
        data = json.loads(request.body)
        temp_path_key = data.get('temp_path', '')
        max_lines = data.get('max_lines', 100)
        max_depth = data.get('max_depth', 5)
        extensions = set(data.get('extensions', []))

        # Get temp path and metadata
        repo_data = _temp_repos.get(temp_path_key)
        if not repo_data:
            return JsonResponse({'error': 'Repository not found or expired'}, status=404)

        temp_path = repo_data['temp_path']
        subdirectory = repo_data.get('subdirectory')
        branch = repo_data.get('branch', 'main')

        if not temp_path.exists():
            return JsonResponse({'error': 'Repository path not found'}, status=404)

        # Determine the base path for concatenation
        base_path = temp_path
        if subdirectory:
            base_path = temp_path / subdirectory
            if not base_path.exists():
                return JsonResponse({'error': f'Subdirectory "{subdirectory}" not found'}, status=404)

        # Generate concatenated content
        output = f'# Repository Contents: {subdirectory or "Root"}\n\n'
        if subdirectory:
            output += f'Branch: {branch}\nSubdirectory: {subdirectory}\n\n'

        file_count = 0
        line_count = 0
        char_count = 0

        ignore_patterns = {'.git', 'node_modules', '__pycache__', 'dist', 'build', '.egg-info', 'htmlcov', 'venv', '.venv'}

        # Generate tree structure
        output += '## Directory Structure\n```\n'
        tree_lines = []
        for file_path in sorted(base_path.rglob('*')):
            if any(pattern in str(file_path) for pattern in ignore_patterns):
                continue

            relative_path = file_path.relative_to(base_path)
            depth = len(relative_path.parts) - 1

            if depth <= max_depth:
                indent = '  ' * depth
                name = relative_path.name
                tree_lines.append(f'{indent}{name}')

        output += '\n'.join(tree_lines[:500])  # Limit tree size
        output += '\n```\n\n'

        # Concatenate file contents
        output += '## File Contents\n\n'

        for file_path in sorted(base_path.rglob('*')):
            if not file_path.is_file():
                continue

            # Check ignore patterns
            if any(pattern in str(file_path) for pattern in ignore_patterns):
                continue

            # Check extension
            ext = file_path.suffix.lower()
            if ext not in extensions:
                continue

            # Check depth
            relative_path = file_path.relative_to(base_path)
            depth = len(relative_path.parts) - 1
            if depth > max_depth:
                continue

            try:
                content = file_path.read_text(encoding='utf-8', errors='ignore')
                lines = content.splitlines()

                output += f'### {relative_path}\n```{ext[1:]}\n'

                if len(lines) <= max_lines:
                    output += content
                else:
                    output += '\n'.join(lines[:max_lines])
                    output += f'\n... [{len(lines) - max_lines} lines truncated]'

                output += '\n```\n\n'

                file_count += 1
                line_count += min(len(lines), max_lines)
                char_count += len(content)

            except Exception as e:
                logger.warning(f'Error reading {file_path}: {e}')
                continue

        # Cleanup temporary directory
        try:
            shutil.rmtree(temp_path, ignore_errors=True)
            del _temp_repos[temp_path_key]
        except Exception as e:
            logger.warning(f'Error cleaning up temp directory: {e}')

        return JsonResponse({
            'success': True,
            'content': output,
            'stats': {
                'file_count': file_count,
                'line_count': line_count,
                'char_count': char_count,
            },
        })

    except Exception as e:
        logger.error(f'Error in concatenate_repo: {e}')
        return JsonResponse({'error': str(e)}, status=500)
