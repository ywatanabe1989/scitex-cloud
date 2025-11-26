#!/usr/bin/env python3
"""
API views for Project Service Management (TensorBoard, Jupyter, etc.)
"""

import logging
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied, ValidationError
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from apps.project_app.models.repository.project import Project
from apps.code_app.models import ProjectService
from apps.code_app.services.project_service_manager import ProjectServiceManager

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class ProjectServiceAPIView(View):
    """Base API view for project service operations."""

    def get_service_manager(self):
        return ProjectServiceManager()


class ServiceStartAPI(ProjectServiceAPIView):
    """API for starting services."""

    def post(self, request, username, project_slug):
        """
        Start a service for a project.

        Request body:
            {
                "service_type": "tensorboard",  # or "jupyter", "mlflow", etc.
                "config": {}  # Optional service configuration
            }

        Returns:
            {
                "success": true,
                "service_id": "uuid",
                "service_type": "tensorboard",
                "port": 10100,
                "url": "/username/project/?port=10100",
                "status": "running"
            }
        """
        try:
            # Get project
            project = get_object_or_404(
                Project,
                owner__username=username,
                slug=project_slug
            )

            # Parse request
            import json
            data = json.loads(request.body)
            service_type = data.get("service_type")
            config = data.get("config", {})

            if not service_type:
                return JsonResponse(
                    {"success": False, "error": "service_type is required"},
                    status=400
                )

            # Start service
            manager = self.get_service_manager()
            service = manager.start_service(
                user=request.user,
                project=project,
                service_type=service_type,
                config=config
            )

            # Build URL
            service_url = f"/{username}/{project_slug}/?port={service.port}"

            return JsonResponse({
                "success": True,
                "service_id": str(service.service_id),
                "service_type": service.service_type,
                "port": service.port,
                "url": service_url,
                "status": service.status
            })

        except PermissionDenied as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=403
            )
        except ValidationError as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=400
            )
        except Exception as e:
            logger.error(f"Failed to start service: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "error": "Internal server error"},
                status=500
            )


class ServiceStopAPI(ProjectServiceAPIView):
    """API for stopping services."""

    def post(self, request, service_id):
        """
        Stop a running service.

        Returns:
            {
                "success": true,
                "message": "Service stopped"
            }
        """
        try:
            manager = self.get_service_manager()
            stopped = manager.stop_service(
                user=request.user,
                service_id=service_id
            )

            if stopped:
                return JsonResponse({
                    "success": True,
                    "message": "Service stopped"
                })
            else:
                return JsonResponse(
                    {"success": False, "error": "Service not found"},
                    status=404
                )

        except PermissionDenied as e:
            return JsonResponse(
                {"success": False, "error": str(e)},
                status=403
            )
        except Exception as e:
            logger.error(f"Failed to stop service: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "error": "Internal server error"},
                status=500
            )


class ServiceListAPI(ProjectServiceAPIView):
    """API for listing services."""

    def get(self, request, username, project_slug):
        """
        List active services for a project.

        Returns:
            {
                "success": true,
                "services": [
                    {
                        "service_id": "uuid",
                        "service_type": "tensorboard",
                        "port": 10100,
                        "url": "/username/project/?port=10100",
                        "status": "running",
                        "started_at": "2025-11-26T00:00:00Z",
                        "uptime": 3600
                    }
                ]
            }
        """
        try:
            # Get project
            project = get_object_or_404(
                Project,
                owner__username=username,
                slug=project_slug
            )

            # Check access
            manager = self.get_service_manager()
            if not manager._has_project_access(request.user, project):
                return JsonResponse(
                    {"success": False, "error": "Access denied"},
                    status=403
                )

            # Get active services
            services = ProjectService.objects.filter(
                project=project,
                status__in=["starting", "running"]
            )

            service_data = []
            for service in services:
                service_data.append({
                    "service_id": str(service.service_id),
                    "service_type": service.service_type,
                    "port": service.port,
                    "url": f"/{username}/{project_slug}/?port={service.port}",
                    "status": service.status,
                    "started_at": service.started_at.isoformat(),
                    "uptime": service.uptime
                })

            return JsonResponse({
                "success": True,
                "services": service_data
            })

        except Exception as e:
            logger.error(f"Failed to list services: {e}", exc_info=True)
            return JsonResponse(
                {"success": False, "error": "Internal server error"},
                status=500
            )


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def service_types_api(request):
    """
    Get available service types.

    Returns:
        {
            "success": true,
            "service_types": [
                {
                    "id": "tensorboard",
                    "name": "TensorBoard",
                    "description": "TensorFlow visualization tool"
                },
                ...
            ]
        }
    """
    service_types = [
        {
            "id": "tensorboard",
            "name": "TensorBoard",
            "description": "TensorFlow visualization tool for training metrics"
        },
        {
            "id": "jupyter",
            "name": "Jupyter Lab",
            "description": "Interactive Python notebook environment"
        },
        {
            "id": "mlflow",
            "name": "MLflow",
            "description": "Machine learning experiment tracking"
        },
        {
            "id": "streamlit",
            "name": "Streamlit",
            "description": "Data app framework"
        },
    ]

    return Response({
        "success": True,
        "service_types": service_types
    })
