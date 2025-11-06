"""API endpoints for compilation operations."""

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from ...services import CompilerService
import json
import logging

logger = logging.getLogger(__name__)


@login_required
@require_http_methods(["POST"])
def compilation_api(request):
    """Start a compilation job.

    POST body:
        {
            "project_id": <project_id>,
            "doc_type": "manuscript" | "supplementary" | "revision"
        }
    """
    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')
        doc_type = data.get('doc_type', 'manuscript')

        if not project_id:
            return JsonResponse({
                'success': False,
                'error': 'project_id required'
            }, status=400)

        compilation_service = CompilerService(project_id, request.user.id)
        result = compilation_service.compile(doc_type)

        return JsonResponse(result)

    except Exception as e:
        logger.error(f"Compilation error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


@login_required
@require_http_methods(["GET"])
def status_api(request):
    """Get compilation job status.

    Query params:
        - job_id: Compilation job ID
    """
    try:
        job_id = request.GET.get('job_id')

        if not job_id:
            return JsonResponse({
                'success': False,
                'error': 'job_id required'
            }, status=400)

        compilation_service = CompilerService(None, request.user.id)
        status = compilation_service.get_status(job_id)

        return JsonResponse({
            'success': True,
            'status': status
        })

    except Exception as e:
        logger.error(f"Status check error: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)
