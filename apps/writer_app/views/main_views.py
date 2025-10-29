"""
Minimal Writer views - delegates to scitex.writer.Writer via REST API.

This replaces the old 3000+ line views/main_views.py
All manuscript operations go through WriterService and REST API endpoints.
"""

from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.conf import settings
from ..models import Manuscript
from apps.project_app.models import Project
from apps.project_app.services import get_current_project
import json
import logging

logger = logging.getLogger(__name__)


def index(request):
    """SciTeX Writer home page."""
    context = {
        'is_anonymous': not request.user.is_authenticated,
        'writer_initialized': False,
    }

    if request.user.is_authenticated:
        # Get user's projects for project selector
        user_projects = Project.objects.filter(owner=request.user).order_by('name')
        context['user_projects'] = user_projects

        # Get current project (from session/header selector)
        current_project = get_current_project(request, user=request.user)
        if current_project:
            context['current_project'] = current_project
            context['project'] = current_project

            # Get or create manuscript record
            manuscript, created = Manuscript.objects.get_or_create(
                project=current_project,
                owner=request.user,
                defaults={
                    'title': f'{current_project.name} Manuscript',
                    'description': f'Manuscript for {current_project.name}',
                }
            )
            context['manuscript'] = manuscript
            context['manuscript_id'] = manuscript.id
            context['writer_initialized'] = manuscript.writer_initialized
        else:
            # User authenticated but no project selected
            context['needs_project_creation'] = True
    else:
        # Anonymous user - show demo banner and init prompt
        context['is_demo'] = True
        context['sections'] = {}  # Empty sections for anonymous users

    return render(request, 'writer_app/index.html', context)


@login_required
def initialize_workspace(request):
    """Initialize Writer workspace for a project.

    POST body:
        {
            "project_id": <project_id>
        }
    """
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=405)

    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')

        if not project_id:
            return JsonResponse({'success': False, 'error': 'project_id required'}, status=400)

        # Verify project access
        project = Project.objects.get(id=project_id, owner=request.user)

        # Get or create manuscript
        manuscript, created = Manuscript.objects.get_or_create(
            project=project,
            owner=request.user,
            defaults={'title': f'{project.name} Manuscript'}
        )

        # Check if Writer already initialized
        if manuscript.writer_initialized:
            return JsonResponse({
                'success': True,
                'message': 'Writer workspace already initialized',
                'manuscript_id': manuscript.id,
            })

        # Initialize Writer (creates directory structure)
        from ..services.writer_service import WriterService
        service = WriterService(project_id, request.user.id)

        # Trigger initialization by accessing writer property
        # This creates the directory structure
        writer = service.writer

        return JsonResponse({
            'success': True,
            'message': 'Writer workspace initialized',
            'manuscript_id': manuscript.id,
        })

    except Project.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


# Stub functions for compatibility - these are handled by REST API now
def user_default_workspace(request):
    """Redirect to index."""
    return index(request)


def project_writer(request, project_id):
    """Project writer interface."""
    return index(request)


def save_section(request, project_id):
    """Use POST /api/project/<id>/section/<name>/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def load_latex_section(request, project_id):
    """Use GET /api/project/<id>/section/<name>/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def save_latex_section(request, project_id):
    """Use POST /api/project/<id>/section/<name>/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def list_tex_files(request, project_id):
    """Use GET /api/project/<id>/sections/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def compile_modular_manuscript(request, project_id):
    """Use POST /api/project/<id>/compile/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def get_manuscript_stats(request, project_id):
    """Not implemented."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def toggle_editing_mode(request, project_id):
    """Not implemented."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def cloud_compile_sections(request, project_id):
    """Use POST /api/project/<id>/compile/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def download_paper_zip(request, project_id):
    """Not implemented yet."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def download_compiled_pdf(request, project_id):
    """Use GET /api/project/<id>/pdf/ instead."""
    return JsonResponse({'success': False, 'error': 'Use API endpoint'}, status=410)


def collaborative_editor(request, manuscript_id):
    """Collaborative editor using WebSocket."""
    context = {'manuscript_id': manuscript_id}
    return render(request, 'writer_app/collaborative.html', context)


def features(request):
    """Writer features page."""
    return render(request, 'writer_app/features.html')


def pricing(request):
    """Writer pricing page."""
    return render(request, 'writer_app/pricing.html')


def modular_editor(request):
    """Modular editor interface."""
    return index(request)


def simple_editor(request):
    """Simple editor interface."""
    return index(request)


def latex_editor_view(request):
    """LaTeX editor interface."""
    return index(request)


def quick_compile(request):
    """Quick compilation endpoint."""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'}, status=400)

    try:
        data = json.loads(request.body)
        content = data.get('content', '')
        project_slug = data.get('projectSlug')
        doc_type = data.get('docType', 'manuscript')

        if not project_slug:
            return JsonResponse({
                'success': False,
                'error': 'Project slug required'
            }, status=400)

        # Get or create project directory
        from pathlib import Path
        project_dir = Path(settings.SCITEX_PROJECTS_DIR) / project_slug
        project_dir.mkdir(parents=True, exist_ok=True)

        # Get compiler and compile
        from ..services.compiler import get_compiler
        compiler = get_compiler(project_dir)
        result = compiler.compile_manuscript(content=content)

        return JsonResponse(result)

    except Exception as e:
        import traceback
        logger.error(f"Compilation error: {e}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)


def compilation_status(request, job_id):
    """Get compilation job status."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def mock_save(request):
    """Mock save endpoint (deprecated)."""
    return JsonResponse({'success': True, 'message': 'Use REST API instead'})


def collaborative_sessions(request, manuscript_id):
    """Get active collaboration sessions."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def join_collaboration(request, manuscript_id):
    """Join collaboration (use WebSocket instead)."""
    return JsonResponse({'success': False, 'error': 'Use WebSocket'}, status=410)


def leave_collaboration(request, manuscript_id):
    """Leave collaboration (use WebSocket instead)."""
    return JsonResponse({'success': False, 'error': 'Use WebSocket'}, status=410)


def lock_section(request, section_id):
    """Lock section for editing."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def unlock_section(request, section_id):
    """Unlock section."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def version_history(request, manuscript_id):
    """Get manuscript version history."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def create_version(request, manuscript_id):
    """Create manuscript version."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def view_diff(request, manuscript_id, from_version_id, to_version_id):
    """View diff between versions."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def rollback_version(request, manuscript_id, version_id):
    """Rollback to version."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def branch_list(request, manuscript_id):
    """List manuscript branches."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def create_branch(request, manuscript_id):
    """Create manuscript branch."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def create_merge_request(request, manuscript_id):
    """Create merge request."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def version_control_dashboard(request, manuscript_id):
    """Version control dashboard."""
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def writer_dashboard_view(request):
    """Writer dashboard."""
    return index(request)


def manuscript_list(request):
    """List user's manuscripts."""
    return index(request)


# arXiv stubs - to be removed later
class ArxivDashboardView:
    @staticmethod
    def as_view():
        return lambda r: JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def arxiv_account_setup(request):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


class SubmissionListView:
    @staticmethod
    def as_view():
        return lambda r: JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def manuscript_submission_form(request, manuscript_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def submission_detail(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def validate_submission(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def prepare_submission_files(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def submit_to_arxiv(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def check_submission_status(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def withdraw_submission(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def create_replacement(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def submission_history_api(request, submission_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def categories_api(request):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def suggest_categories_api(request, manuscript_id):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def arxiv_status_check(request):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)


def initialize_categories(request):
    return JsonResponse({'success': False, 'error': 'Not implemented'}, status=501)
