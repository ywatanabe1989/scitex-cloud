#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-04 20:30:42 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/code_app/api_views.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/code_app/api_views.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
API views for SciTeX-Code Jupyter notebook integration.
"""

import json
import logging
import threading
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view
from rest_framework.decorators import permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notebook
from .models import CodeExecutionJob
from .jupyter import NotebookManager
from .jupyter import NotebookExecutor
from .jupyter import NotebookConverter
from .jupyter import NotebookTemplates
from .jupyter import NotebookValidator

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class NotebookAPIView(View):
    """Base API view for notebook operations."""

    def get_notebook_manager(self):
        return NotebookManager(self.request.user)


class NotebookListAPI(NotebookAPIView):
    """API for listing and creating notebooks."""

    def get(self, request):
        """List user's notebooks."""
        try:
            notebooks = Notebook.objects.filter(user=request.user).order_by(
                "-updated_at"
            )

            # Pagination
            page = int(request.GET.get("page", 1))
            per_page = min(int(request.GET.get("per_page", 20)), 50)
            start = (page - 1) * per_page
            end = start + per_page

            paginated_notebooks = notebooks[start:end]

            notebooks_data = []
            for notebook in paginated_notebooks:
                notebooks_data.append(
                    {
                        "id": str(notebook.notebook_id),
                        "title": notebook.title,
                        "description": notebook.description,
                        "status": notebook.status,
                        "is_public": notebook.is_public,
                        "execution_count": notebook.execution_count,
                        "last_executed": (
                            notebook.last_executed.isoformat()
                            if notebook.last_executed
                            else None
                        ),
                        "created_at": notebook.created_at.isoformat(),
                        "updated_at": notebook.updated_at.isoformat(),
                        "cell_count": len(notebook.content.get("cells", [])),
                        "shared_with_count": notebook.shared_with.count(),
                    }
                )

            return JsonResponse(
                {
                    "status": "success",
                    "notebooks": notebooks_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": notebooks.count(),
                        "has_next": end < notebooks.count(),
                        "has_previous": page > 1,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error listing notebooks: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def post(self, request):
        """Create a new notebook."""
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            description = data.get("description", "").strip()
            template = data.get("template", "blank")

            if not title:
                return JsonResponse(
                    {"status": "error", "message": "Title is required"},
                    status=400,
                )

            # Check for duplicate titles
            if Notebook.objects.filter(user=request.user, title=title).exists():
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "A notebook with this title already exists",
                    },
                    status=400,
                )

            manager = self.get_notebook_manager()

            # Create notebook with template
            if template == "data_analysis":
                notebook_content = NotebookTemplates.get_data_analysis_template()
            elif template == "machine_learning":
                notebook_content = NotebookTemplates.get_machine_learning_template()
            elif template == "visualization":
                notebook_content = NotebookTemplates.get_visualization_template()
            else:
                # Create blank notebook
                notebook = manager.create_notebook(title, description)
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Notebook created successfully",
                        "notebook": {
                            "id": str(notebook.notebook_id),
                            "title": notebook.title,
                            "description": notebook.description,
                            "status": notebook.status,
                        },
                    }
                )

            # Create notebook with template content
            notebook = Notebook.objects.create(
                user=request.user,
                title=title,
                description=description,
                content=notebook_content,
                status="draft",
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Notebook created successfully",
                    "notebook": {
                        "id": str(notebook.notebook_id),
                        "title": notebook.title,
                        "description": notebook.description,
                        "status": notebook.status,
                        "template": template,
                    },
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error creating notebook: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class NotebookDetailAPI(NotebookAPIView):
    """API for individual notebook operations."""

    def get(self, request, notebook_id):
        """Get notebook details and content."""
        try:
            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            return JsonResponse(
                {
                    "status": "success",
                    "notebook": {
                        "id": str(notebook.notebook_id),
                        "title": notebook.title,
                        "description": notebook.description,
                        "status": notebook.status,
                        "content": notebook.content,
                        "is_public": notebook.is_public,
                        "execution_count": notebook.execution_count,
                        "last_executed": (
                            notebook.last_executed.isoformat()
                            if notebook.last_executed
                            else None
                        ),
                        "created_at": notebook.created_at.isoformat(),
                        "updated_at": notebook.updated_at.isoformat(),
                        "shared_with": [
                            user.username for user in notebook.shared_with.all()
                        ],
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error getting notebook {notebook_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def put(self, request, notebook_id):
        """Update notebook content."""
        try:
            data = json.loads(request.body)
            content = data.get("content")
            title = data.get("title")
            description = data.get("description")

            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            # Update metadata if provided
            updated = False
            if title and title != notebook.title:
                # Check for duplicate titles
                if (
                    Notebook.objects.filter(user=request.user, title=title)
                    .exclude(notebook_id=notebook_id)
                    .exists()
                ):
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "A notebook with this title already exists",
                        },
                        status=400,
                    )
                notebook.title = title
                updated = True

            if description is not None and description != notebook.description:
                notebook.description = description
                updated = True

            # Update content if provided
            if content:
                # Validate notebook content
                is_valid, errors = NotebookValidator.validate_notebook(content)
                if not is_valid:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "Invalid notebook content",
                            "errors": errors,
                        },
                        status=400,
                    )

                success = manager.save_notebook(notebook_id, content)
                if not success:
                    return JsonResponse(
                        {
                            "status": "error",
                            "message": "Failed to save notebook content",
                        },
                        status=500,
                    )
                updated = True

            if updated:
                notebook.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Notebook updated successfully",
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error updating notebook {notebook_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def delete(self, request, notebook_id):
        """Delete a notebook."""
        try:
            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            # Delete file if exists
            if notebook.file_path and notebook.file_path.startswith(
                str(manager.base_path)
            ):
                try:
                    import os

                    if os.path.exists(notebook.file_path):
                        os.remove(notebook.file_path)
                except Exception as e:
                    logger.warning(
                        f"Could not delete notebook file {notebook.file_path}: {e}"
                    )

            # Delete from database
            notebook.delete()

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Notebook deleted successfully",
                }
            )

        except Exception as e:
            logger.error(f"Error deleting notebook {notebook_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class NotebookExecutionAPI(NotebookAPIView):
    """API for notebook execution."""

    def post(self, request, notebook_id):
        """Execute a notebook or specific cell."""
        try:
            data = json.loads(request.body)
            cell_index = data.get("cell_index")  # If specified, execute only this cell
            timeout = min(int(data.get("timeout", 300)), 600)
            memory_limit = min(int(data.get("memory_limit", 512)), 2048)

            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            # Create execution job
            job = CodeExecutionJob.objects.create(
                user=request.user,
                execution_type="notebook",
                source_code=f"Notebook: {notebook.title}",
                timeout_seconds=timeout,
                max_memory_mb=memory_limit,
            )

            executor = NotebookExecutor(timeout=timeout, memory_limit=memory_limit)

            if cell_index is not None:
                # Execute single cell
                def execute_cell():
                    success, result = executor.execute_cell(notebook, cell_index)

                    job.status = "completed" if success else "failed"
                    from datetime import timezone

                    job.completed_at = timezone.now()
                    if success:
                        job.output = json.dumps(result, indent=2)
                    else:
                        job.error_output = result.get("error", "Unknown error")
                    job.save()

                execution_thread = threading.Thread(target=execute_cell)
                execution_thread.daemon = True
                execution_thread.start()

                return JsonResponse(
                    {
                        "status": "success",
                        "message": f"Cell {cell_index} execution started",
                        "job_id": str(job.job_id),
                        "execution_type": "cell",
                    }
                )

            else:
                # Execute entire notebook
                def execute_notebook():
                    executor.execute_notebook(notebook, job)

                execution_thread = threading.Thread(target=execute_notebook)
                execution_thread.daemon = True
                execution_thread.start()

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Notebook execution started",
                        "job_id": str(job.job_id),
                        "execution_type": "notebook",
                    }
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error executing notebook {notebook_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class NotebookConversionAPI(NotebookAPIView):
    """API for notebook format conversion."""

    def get(self, request, notebook_id, format_type):
        """Convert notebook to different formats."""
        try:
            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            if format_type == "html":
                content = NotebookConverter.to_html(notebook)
                return JsonResponse(
                    {
                        "status": "success",
                        "format": "html",
                        "content": content,
                        "filename": f"{notebook.title}.html",
                    }
                )

            elif format_type == "python":
                content = NotebookConverter.to_python(notebook)
                return JsonResponse(
                    {
                        "status": "success",
                        "format": "python",
                        "content": content,
                        "filename": f"{notebook.title}.py",
                    }
                )

            elif format_type == "markdown":
                content = NotebookConverter.to_markdown(notebook)
                return JsonResponse(
                    {
                        "status": "success",
                        "format": "markdown",
                        "content": content,
                        "filename": f"{notebook.title}.md",
                    }
                )

            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Unsupported format. Supported formats: html, python, markdown",
                    },
                    status=400,
                )

        except Exception as e:
            logger.error(
                f"Error converting notebook {notebook_id} to {format_type}: {e}"
            )
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class NotebookSharingAPI(NotebookAPIView):
    """API for notebook sharing."""

    def post(self, request, notebook_id):
        """Share notebook with other users."""
        try:
            data = json.loads(request.body)
            usernames = data.get("usernames", [])
            is_public = data.get("is_public", False)

            manager = self.get_notebook_manager()
            notebook = manager.load_notebook(notebook_id)

            if not notebook:
                return JsonResponse(
                    {"status": "error", "message": "Notebook not found"},
                    status=404,
                )

            # Update public status
            notebook.is_public = is_public

            # Share with specific users
            if usernames:
                from django.contrib.auth.models import User

                users = User.objects.filter(username__in=usernames)
                notebook.shared_with.set(users)

            notebook.save()

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Notebook sharing updated",
                    "shared_with": [
                        user.username for user in notebook.shared_with.all()
                    ],
                    "is_public": notebook.is_public,
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error sharing notebook {notebook_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class NotebookTemplatesAPI(NotebookAPIView):
    """API for notebook templates."""

    def get(self, request):
        """Get available notebook templates."""
        try:
            templates = [
                {
                    "id": "blank",
                    "name": "Blank Notebook",
                    "description": "Start with an empty notebook",
                    "category": "general",
                },
                {
                    "id": "data_analysis",
                    "name": "Data Analysis",
                    "description": "Structured template for data analysis projects",
                    "category": "analysis",
                },
                {
                    "id": "machine_learning",
                    "name": "Machine Learning",
                    "description": "Template for ML model development and evaluation",
                    "category": "ml",
                },
                {
                    "id": "visualization",
                    "name": "Data Visualization",
                    "description": "Create publication-ready visualizations",
                    "category": "visualization",
                },
            ]

            return JsonResponse({"status": "success", "templates": templates})

        except Exception as e:
            logger.error(f"Error getting templates: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


# REST Framework API Views


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def notebook_status_api(request, job_id):
    """Get notebook execution status via REST API."""
    try:
        job = CodeExecutionJob.objects.get(job_id=job_id, user=request.user)

        return Response(
            {
                "job_id": str(job.job_id),
                "status": job.status,
                "execution_type": job.execution_type,
                "created_at": job.created_at,
                "started_at": job.started_at,
                "completed_at": job.completed_at,
                "execution_time": job.execution_time,
                "cpu_time": job.cpu_time,
                "memory_peak": job.memory_peak,
                "output": json.loads(job.output) if job.output else None,
                "error_output": job.error_output,
            }
        )

    except CodeExecutionJob.DoesNotExist:
        return Response({"error": "Job not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        logger.error(f"Error getting job status {job_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(["POST"])
@permission_classes([IsAuthenticated])
def duplicate_notebook_api(request, notebook_id):
    """Duplicate a notebook via REST API."""
    try:
        data = request.data
        new_title = data.get("title", "").strip()

        if not new_title:
            return Response(
                {"error": "New title is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        manager = NotebookManager(request.user)
        new_notebook = manager.duplicate_notebook(notebook_id, new_title)

        if not new_notebook:
            return Response(
                {"error": "Notebook not found or duplication failed"},
                status=status.HTTP_404_NOT_FOUND,
            )

        return Response(
            {
                "status": "success",
                "message": "Notebook duplicated successfully",
                "notebook": {
                    "id": str(new_notebook.notebook_id),
                    "title": new_notebook.title,
                    "description": new_notebook.description,
                    "status": new_notebook.status,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error duplicating notebook {notebook_id}: {e}")
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# EOF
