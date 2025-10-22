"""
SciTeX Cloud - Native File Views

API views for native filesystem operations.
These views work directly with the filesystem without database overhead.
"""

from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from pathlib import Path
import json

from apps.project_app.models import Project
from ..services.directory_service import get_user_directory_manager
from ..services.filesystem_utils import NativeFileHandler, ProjectFileScanner


@login_required
@require_http_methods(["GET"])
def native_list_directory(request, username, slug, directory_path=''):
    """
    List directory contents using native filesystem operations.

    Query parameters:
        - recursive: Include subdirectories (true/false)
        - hidden: Include hidden files (true/false)

    Example: GET /api/native/ywatanabe/my-project/scripts/
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    # Permission check
    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get project directory
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    # Construct target directory path
    target_path = project_path / directory_path if directory_path else project_path

    # Security check
    try:
        target_path = target_path.resolve()
        if not str(target_path).startswith(str(project_path.resolve())):
            return JsonResponse({'error': 'Invalid path'}, status=400)
    except:
        return JsonResponse({'error': 'Invalid path'}, status=400)

    # Parse query parameters
    recursive = request.GET.get('recursive', 'false').lower() == 'true'
    hidden = request.GET.get('hidden', 'false').lower() == 'true'

    try:
        # Use native file handler - NO database queries!
        items = NativeFileHandler.list_directory(
            target_path,
            recursive=recursive,
            include_hidden=hidden
        )

        # Convert paths to relative
        for item in items:
            full_path = Path(item['path'])
            item['path'] = str(full_path.relative_to(project_path))

        return JsonResponse({
            'success': True,
            'project': {
                'name': project.name,
                'slug': project.slug,
                'owner': project.owner.username
            },
            'directory': directory_path or '.',
            'items': items,
            'count': len(items)
        })

    except NotADirectoryError:
        return JsonResponse({'error': 'Not a directory'}, status=400)
    except PermissionError:
        return JsonResponse({'error': 'Permission denied'}, status=403)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def native_read_file(request, username, slug, file_path):
    """
    Read file content directly from filesystem.

    Query parameters:
        - max_size: Maximum file size in bytes (default 1MB)

    Example: GET /api/native/ywatanabe/my-project/file/scripts/analysis.py
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    # Permission check
    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get file path
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path:
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            return JsonResponse({'error': 'Invalid path'}, status=400)
    except:
        return JsonResponse({'error': 'Invalid path'}, status=400)

    try:
        # Get file info
        file_info = NativeFileHandler.get_file_info(full_file_path)

        # Read content
        max_size = int(request.GET.get('max_size', 1024 * 1024))
        success, content = NativeFileHandler.read_file_content(full_file_path, max_size)

        if not success:
            return JsonResponse({
                'success': False,
                'error': content,  # Error message
                'file_info': file_info
            }, status=400)

        return JsonResponse({
            'success': True,
            'file_info': {
                **file_info,
                'path': str(full_file_path.relative_to(project_path)),
                'modified': file_info['modified'].isoformat()
            },
            'content': content,
            'lines': len(content.split('\n'))
        })

    except FileNotFoundError:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def native_write_file(request, username, slug, file_path):
    """
    Write file content directly to filesystem.

    Body: JSON with 'content' field

    Example: POST /api/native/ywatanabe/my-project/file/scripts/analysis.py
             {"content": "import numpy as np\n..."}
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    # Permission check - must be able to edit
    if not project.can_edit(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get file path
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path:
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            return JsonResponse({'error': 'Invalid path'}, status=400)
    except:
        return JsonResponse({'error': 'Invalid path'}, status=400)

    try:
        # Parse request body
        data = json.loads(request.body)
        content = data.get('content', '')

        # Write file
        success, message = NativeFileHandler.write_file_content(
            full_file_path,
            content,
            create_dirs=True
        )

        if not success:
            return JsonResponse({'success': False, 'error': message}, status=500)

        # Get updated file info
        file_info = NativeFileHandler.get_file_info(full_file_path)

        # Update project last_activity (minimal DB touch)
        project.save(update_fields=['last_activity'])

        return JsonResponse({
            'success': True,
            'message': message,
            'file_info': {
                **file_info,
                'path': str(full_file_path.relative_to(project_path)),
                'modified': file_info['modified'].isoformat()
            }
        })

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def native_project_stats(request, username, slug):
    """
    Get project statistics from filesystem.

    Returns:
        - Total size
        - File count
        - Recent files
        - Directory structure
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    try:
        # Get directory stats
        stats = NativeFileHandler.get_directory_stats(project_path)

        # Get recent files
        scanner = ProjectFileScanner(project_path)
        recent_files = scanner.get_recent_files(limit=10)

        # Format recent files
        for f in recent_files:
            f['modified'] = f['modified'].isoformat()
            f['path'] = str(Path(f['path']).relative_to(project_path))

        return JsonResponse({
            'success': True,
            'project': {
                'name': project.name,
                'slug': project.slug,
                'owner': project.owner.username
            },
            'stats': stats,
            'recent_files': recent_files
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def native_search_files(request, username, slug):
    """
    Search files in project.

    Query parameters:
        - q: Search query (searches filenames and content)
        - pattern: File pattern (e.g., "*.py")
        - content: Search in content (true/false)

    Example: GET /api/native/ywatanabe/my-project/search?q=analysis&pattern=*.py&content=true
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    query = request.GET.get('q', '')
    pattern = request.GET.get('pattern', '*')
    search_content = request.GET.get('content', 'false').lower() == 'true'

    if not query:
        return JsonResponse({'error': 'Query parameter "q" is required'}, status=400)

    try:
        results = {
            'filename_matches': [],
            'content_matches': []
        }

        # Find files matching pattern
        files = NativeFileHandler.find_files(project_path, pattern)

        # Search filenames
        for file_path in files:
            if query.lower() in file_path.name.lower():
                results['filename_matches'].append({
                    'path': str(file_path.relative_to(project_path)),
                    'name': file_path.name,
                    'size': file_path.stat().st_size
                })

        # Search content if requested
        if search_content:
            scanner = ProjectFileScanner(project_path)
            content_results = scanner.search_content(query, [pattern])
            results['content_matches'] = content_results

        return JsonResponse({
            'success': True,
            'query': query,
            'pattern': pattern,
            'results': results,
            'total_matches': len(results['filename_matches']) + len(results['content_matches'])
        })

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def native_file_info(request, username, slug, file_path):
    """
    Get detailed file information.

    Returns metadata without reading full content (fast).
    """
    project = get_object_or_404(Project, slug=slug, owner__username=username)

    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path:
        return JsonResponse({'error': 'Project directory not found'}, status=404)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            return JsonResponse({'error': 'Invalid path'}, status=400)
    except:
        return JsonResponse({'error': 'Invalid path'}, status=400)

    try:
        file_info = NativeFileHandler.get_file_info(full_file_path)
        file_info['path'] = str(full_file_path.relative_to(project_path))
        file_info['modified'] = file_info['modified'].isoformat()
        file_info['created'] = file_info['created'].isoformat()

        return JsonResponse({
            'success': True,
            'file_info': file_info
        })

    except FileNotFoundError:
        return JsonResponse({'error': 'File not found'}, status=404)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
