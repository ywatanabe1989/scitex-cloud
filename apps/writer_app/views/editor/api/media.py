#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/writer_app/views/editor/api/media.py
"""Media management - figures and tables operations."""

from __future__ import annotations
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from ..auth_utils import api_login_optional, get_user_for_request

logger = logging.getLogger(__name__)


@api_login_optional
@require_http_methods(["GET"])
def figures_api(request, project_id):
    """
    Get all figures from project SQLite DB (fast!).

    Query params:
        - source: 'paper', 'pool', 'data', 'scripts', 'all' (default: 'all')
        - is_referenced: 'true', 'false', 'all' (default: 'all')
        - file_type: 'png', 'pdf', 'jpg', etc. or 'all' (default: 'all')
        - q: search query (full-text search)

    Returns:
        JSON with:
            - success: bool
            - figures: list of figure dictionaries
            - stats: {total, referenced, sources, total_size}
    """
    try:
        from apps.project_app.models import Project
        from ....utils.project_db import get_project_db

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        db = get_project_db(project)

        # Parse filters
        filters = {}
        if request.GET.get('source') and request.GET.get('source') != 'all':
            filters['source'] = request.GET.get('source')

        if request.GET.get('is_referenced') and request.GET.get('is_referenced') != 'all':
            filters['is_referenced'] = request.GET.get('is_referenced') == 'true'

        if request.GET.get('file_type') and request.GET.get('file_type') != 'all':
            filters['file_type'] = request.GET.get('file_type')

        # Search or filter
        search_query = request.GET.get('q')
        if search_query:
            figures = db.search_figures(search_query)
        else:
            figures = db.get_all_figures(filters)

        # Get stats
        stats = db.get_stats()

        # Convert thumbnail paths to URLs
        for fig in figures:
            if fig.get('thumbnail_path'):
                # Serve from project's scitex/thumbnails/
                from pathlib import Path
                thumb_name = Path(fig['thumbnail_path']).name
                fig['thumbnail_url'] = f"/writer/api/project/{project_id}/thumbnail/{thumb_name}"
            else:
                fig['thumbnail_url'] = '/static/images/thumbnail_placeholder.png'

        logger.info(f"[Figures API] Returned {len(figures)} figures for project {project_id}")

        return JsonResponse({
            'success': True,
            'figures': figures,
            'stats': stats,
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Figures API] Error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["GET"])
def tables_api(request, project_id):
    """
    Get all tables from project SQLite DB.

    Query params:
        - source: 'paper', 'pool', 'data', 'scripts', 'all' (default: 'all')
        - is_referenced: 'true', 'false', 'all' (default: 'all')
        - q: search query (full-text search)

    Returns:
        JSON with:
            - success: bool
            - tables: list of table dictionaries
            - stats: {total, referenced}
    """
    try:
        from apps.project_app.models import Project
        from ....utils.project_db import get_project_db

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        db = get_project_db(project)

        # Parse filters from query params
        filters = {}
        source = request.GET.get('source', 'all')
        if source != 'all':
            filters['source'] = source

        is_referenced = request.GET.get('is_referenced', 'all')
        if is_referenced in ['true', 'false']:
            filters['is_referenced'] = is_referenced == 'true'

        # Get all tables with filters
        tables = db.get_all_tables(filters=filters if filters else None)

        # Add thumbnail URLs
        from pathlib import Path
        for table in tables:
            if table.get('thumbnail_path'):
                thumb_name = Path(table['thumbnail_path']).name
                table['thumbnail_url'] = f"/writer/api/project/{project_id}/thumbnail/{thumb_name}"
            else:
                table['thumbnail_url'] = '/static/images/thumbnail_placeholder.png'

        # Calculate stats
        all_tables = db.get_all_tables()
        stats = {
            'total': len(all_tables),
            'referenced': sum(1 for t in all_tables if t.get('is_referenced')),
        }

        logger.info(f"[Tables API] Returned {len(tables)} tables for project {project_id}")

        return JsonResponse({
            'success': True,
            'tables': tables,
            'stats': stats,
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Tables API] Error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["POST"])
def refresh_figures_index(request, project_id):
    """
    Trigger background re-indexing of figures.

    This starts an asynchronous task to scan the project and update
    the metadata database.

    Returns:
        JSON with success status
    """
    try:
        from apps.project_app.models import Project
        from ....tasks.indexer import index_project_figures, CELERY_AVAILABLE

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Trigger background indexing
        if CELERY_AVAILABLE:
            index_project_figures.delay(project_id)
        else:
            # Call directly if Celery not available (dev mode)
            index_project_figures(project_id)

        logger.info(f"[Figures API] Triggered re-indexing for project {project_id}")

        return JsonResponse({
            'success': True,
            'message': 'Indexing started in background'
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Figures API] Error triggering refresh: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["POST"])
def refresh_tables_index(request, project_id):
    """
    Trigger background re-indexing of tables.

    This starts an asynchronous task to scan the project and update
    the metadata database, including thumbnail generation.

    Returns:
        JSON with success status
    """
    try:
        from apps.project_app.models import Project
        from ....tasks.indexer import index_project_tables, CELERY_AVAILABLE

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Trigger background indexing
        if CELERY_AVAILABLE:
            index_project_tables.delay(project_id)
        else:
            # Call directly if Celery not available (dev mode)
            index_project_tables(project_id)

        logger.info(f"[Tables API] Triggered re-indexing for project {project_id}")

        return JsonResponse({
            'success': True,
            'message': 'Table indexing started in background'
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Tables API] Error triggering refresh: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["POST"])
def upload_figures(request, project_id):
    """
    Upload figure files to scitex/writer/uploads/figures/.

    Accepts multipart/form-data with files array.
    After upload, triggers indexing task.

    Returns:
        JSON with success status and list of uploaded files
    """
    try:
        from apps.project_app.models import Project
        from pathlib import Path
        from ....tasks.indexer import index_project_figures, CELERY_AVAILABLE

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Get uploaded files
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse(
                {"success": False, "error": "No files provided"}, status=400
            )

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                raise ValueError("Cannot determine project owner")
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                raise ValueError(f"Project path not found for project {project.id}")

        # Create upload directory: scitex/writer/uploads/figures/
        upload_dir = project_path / 'scitex' / 'writer' / 'uploads' / 'figures'
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        uploaded_files = []
        for uploaded_file in files:
            file_path = upload_dir / uploaded_file.name

            # Write file in chunks
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            uploaded_files.append({
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'path': str(file_path.relative_to(project_path))
            })

            logger.info(f"[Upload] Saved figure: {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Trigger indexing
        if CELERY_AVAILABLE:
            index_project_figures.delay(project_id)
        else:
            index_project_figures(project_id)

        logger.info(f"[Upload] Uploaded {len(uploaded_files)} figures for project {project_id}")

        return JsonResponse({
            'success': True,
            'files': uploaded_files,
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)'
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Upload] Error uploading figures: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["POST"])
def upload_tables(request, project_id):
    """
    Upload table files to scitex/writer/uploads/tables/.

    Accepts multipart/form-data with files array.
    After upload, triggers indexing task.

    Returns:
        JSON with success status and list of uploaded files
    """
    try:
        from apps.project_app.models import Project
        from pathlib import Path
        from ....tasks.indexer import index_project_tables, CELERY_AVAILABLE

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Get uploaded files
        files = request.FILES.getlist('files')
        if not files:
            return JsonResponse(
                {"success": False, "error": "No files provided"}, status=400
            )

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.project_filesystem import get_project_filesystem_manager
            if not hasattr(project, 'owner') or not project.owner:
                raise ValueError("Cannot determine project owner")
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                raise ValueError(f"Project path not found for project {project.id}")

        # Create upload directory: scitex/writer/uploads/tables/
        upload_dir = project_path / 'scitex' / 'writer' / 'uploads' / 'tables'
        upload_dir.mkdir(parents=True, exist_ok=True)

        # Save files
        uploaded_files = []
        for uploaded_file in files:
            file_path = upload_dir / uploaded_file.name

            # Write file in chunks
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)

            uploaded_files.append({
                'name': uploaded_file.name,
                'size': uploaded_file.size,
                'path': str(file_path.relative_to(project_path))
            })

            logger.info(f"[Upload] Saved table: {uploaded_file.name} ({uploaded_file.size} bytes)")

        # Trigger indexing
        if CELERY_AVAILABLE:
            index_project_tables.delay(project_id)
        else:
            index_project_tables(project_id)

        logger.info(f"[Upload] Uploaded {len(uploaded_files)} tables for project {project_id}")

        return JsonResponse({
            'success': True,
            'files': uploaded_files,
            'message': f'Successfully uploaded {len(uploaded_files)} file(s)'
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Upload] Error uploading tables: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["GET"])
def table_data_api(request, project_id, file_hash):
    """
    Get full table data for preview/editing.

    Args:
        project_id: Project ID
        file_hash: SHA256 hash of the table file (first 16 chars)

    Returns:
        JSON with:
            - success: bool
            - data: list of dictionaries (rows)
            - columns: list of column names
            - metadata: {file_name, file_path, file_type, rows, cols}
    """
    try:
        import pandas as pd
        from pathlib import Path
        from apps.project_app.models import Project
        from ....utils.project_db import get_project_db

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        db = get_project_db(project)

        # Find table by hash
        tables = db.get_all_tables()
        table = None
        for t in tables:
            if t.get('file_hash', '').startswith(file_hash):
                table = t
                break

        if not table:
            return JsonResponse(
                {"success": False, "error": "Table not found"}, status=404
            )

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.filesystem_manager import get_project_filesystem_manager
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                raise ValueError(f"Project path not found")

        # Read table file
        file_path = project_path / table['file_path']
        if not file_path.exists():
            return JsonResponse(
                {"success": False, "error": "Table file not found"}, status=404
            )

        file_type = file_path.suffix.lower()

        # Read data based on file type
        if file_type == '.csv':
            df = pd.read_csv(file_path)
        elif file_type in ['.xlsx', '.xls']:
            df = pd.read_excel(file_path)
        elif file_type == '.tsv':
            df = pd.read_csv(file_path, sep='\t')
        elif file_type == '.ods':
            df = pd.read_excel(file_path, engine='odf')
        else:
            return JsonResponse(
                {"success": False, "error": f"Unsupported file type: {file_type}"},
                status=400
            )

        # Convert to JSON-friendly format
        # Replace NaN with None for JSON serialization
        df = df.where(pd.notna(df), None)

        data = df.to_dict('records')
        columns = df.columns.tolist()

        logger.info(f"[Table Data API] Loaded {len(data)} rows × {len(columns)} cols from {table['file_name']}")

        return JsonResponse({
            'success': True,
            'data': data,
            'columns': columns,
            'metadata': {
                'file_name': table['file_name'],
                'file_path': table['file_path'],
                'file_type': file_type,
                'file_hash': table['file_hash'],
                'rows': len(data),
                'cols': len(columns),
            }
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Table Data API] Error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@api_login_optional
@require_http_methods(["POST"])
def table_update_api(request, project_id, file_hash):
    """
    Update table data (save modifications).

    Expects JSON body with:
        - data: list of dictionaries (updated rows)
        - columns: list of column names

    Returns:
        JSON with success status and updated metadata
    """
    try:
        import json
        import pandas as pd
        from pathlib import Path
        from apps.project_app.models import Project
        from ....utils.project_db import get_project_db
        from ....tasks.indexer import index_project_tables, CELERY_AVAILABLE

        project = Project.objects.get(id=project_id)
        user, is_visitor = get_user_for_request(request, project_id)

        if not user:
            return JsonResponse(
                {"success": False, "error": "Invalid session"}, status=403
            )

        # Parse request body
        body = json.loads(request.body)
        data = body.get('data', [])
        columns = body.get('columns', [])

        if not data or not columns:
            return JsonResponse(
                {"success": False, "error": "Missing data or columns"}, status=400
            )

        db = get_project_db(project)

        # Find table by hash
        tables = db.get_all_tables()
        table = None
        for t in tables:
            if t.get('file_hash', '').startswith(file_hash):
                table = t
                break

        if not table:
            return JsonResponse(
                {"success": False, "error": "Table not found"}, status=404
            )

        # Get project path
        if hasattr(project, 'git_clone_path') and project.git_clone_path:
            project_path = Path(project.git_clone_path)
        else:
            from apps.project_app.services.filesystem_manager import get_project_filesystem_manager
            manager = get_project_filesystem_manager(project.owner)
            project_path = manager.get_project_root_path(project)
            if not project_path:
                raise ValueError(f"Project path not found")

        # Write data to file
        file_path = project_path / table['file_path']
        file_type = file_path.suffix.lower()

        # Create DataFrame from data
        df = pd.DataFrame(data, columns=columns)

        # Save based on file type
        if file_type == '.csv':
            df.to_csv(file_path, index=False)
        elif file_type in ['.xlsx', '.xls']:
            df.to_excel(file_path, index=False, engine='openpyxl')
        elif file_type == '.tsv':
            df.to_csv(file_path, sep='\t', index=False)
        elif file_type == '.ods':
            df.to_excel(file_path, index=False, engine='odf')
        else:
            return JsonResponse(
                {"success": False, "error": f"Unsupported file type: {file_type}"},
                status=400
            )

        logger.info(f"[Table Update API] Saved {len(data)} rows to {table['file_name']}")

        # Re-index to update thumbnail and metadata
        if CELERY_AVAILABLE:
            index_project_tables.delay(project_id)
        else:
            index_project_tables(project_id)

        return JsonResponse({
            'success': True,
            'message': 'Table updated successfully',
            'metadata': {
                'rows': len(data),
                'cols': len(columns),
            }
        })

    except Project.DoesNotExist:
        return JsonResponse(
            {"success": False, "error": "Project not found"}, status=404
        )
    except Exception as e:
        logger.error(f"[Table Update API] Error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# EOF
