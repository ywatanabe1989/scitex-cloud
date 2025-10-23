from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.project_app.models import Project
from django.contrib.auth.models import User
import uuid
import os
import tempfile
from pathlib import Path
from scitex import logging

logger = logging.getLogger(__name__)


def get_or_create_guest_user(request):
    """Get or create a guest user with a session-based identity."""
    # Check if we have a guest user ID in session
    guest_user_id = request.session.get('guest_user_id')

    if guest_user_id:
        try:
            guest_user = User.objects.get(id=guest_user_id, username__startswith='guest-')
            logger.info(f"Using existing guest user: {guest_user.username}")
            return guest_user
        except User.DoesNotExist:
            pass

    # Create new guest user
    # Ensure session exists
    if not request.session.session_key:
        request.session.create()

    session_key = request.session.session_key
    guest_username = f"guest-{session_key[:12]}"

    # Create guest user (password won't be used)
    guest_user, created = User.objects.get_or_create(
        username=guest_username,
        defaults={
            'email': f'{guest_username}@guest.scitex.local',
            'is_active': False,  # Guest users are not active
        }
    )

    # Store guest user ID in session
    request.session['guest_user_id'] = guest_user.id
    request.session['is_guest'] = True

    if created:
        logger.info(f"Created new guest user: {guest_username}")

    return guest_user


def get_or_create_default_project(user, is_guest=False):
    """Get or create a default project for a user (including guests).

    Note: Writer directory is NOT created here - it's created on-demand
    when the user actually uses the writer feature.
    """
    # Check if user already has projects
    existing_project = Project.objects.filter(owner=user).first()
    if existing_project:
        logger.info(f"Using existing project: {existing_project.name}")
        return existing_project

    # Create default project (without writer directory - created on-demand)
    if is_guest:
        project_name = "Guest Demo Project"
        description = "Temporary demo project for guest user. Sign up to keep your work!"
    else:
        project_name = f"{user.username}'s Project"
        description = f"Default project for {user.username}"

    # Generate unique slug
    slug = Project.generate_unique_slug(project_name)

    # Create the project (data_location will be set when writer dir is created)
    project = Project.objects.create(
        name=project_name,
        slug=slug,
        description=description,
        owner=user,
        visibility='private'
    )

    logger.info(f"Created default project: {project.name} (slug: {slug})")
    return project


def ensure_writer_directory(project):
    """Create writer directory for project if it doesn't exist (opt-in/on-demand).

    Pattern: data/users/username/project-slug/scitex/writer/01_manuscript/...
    Uses workspace directory manager for consistent project storage.
    """
    from scitex.template import create_writer_directory
    from apps.writer_app.models import Manuscript
    from apps.workspace_app.services.directory_service import get_user_directory_manager

    # Check if writer directory already exists
    if project.data_location and Path(project.data_location).exists():
        logger.info(f"Writer directory already exists: {project.data_location}")

        # Ensure manuscript exists
        manuscript, created = Manuscript.objects.get_or_create(
            project=project,
            owner=project.owner,
            defaults={
                'title': f'{project.name} Manuscript',
                'slug': f'{project.slug}-manuscript-{uuid.uuid4().hex[:8]}',
                'is_modular': True
            }
        )
        if created:
            logger.info(f"Created manuscript: {manuscript.title}")

        return Path(project.data_location)

    # Create writer directory on-demand using workspace manager
    logger.info(f"Creating writer directory on-demand for project: {project.name}")

    # Use workspace manager to get correct base directory (local, not NAS)
    manager = get_user_directory_manager(project.owner)
    base_dir = manager.base_path / project.slug
    scitex_dir = base_dir / "scitex"
    writer_dir = scitex_dir / "writer"

    try:
        scitex_dir.mkdir(parents=True, exist_ok=True)
        create_writer_directory("writer", str(scitex_dir))
        logger.info(f"✓ Created writer directory: {writer_dir}")

        # Update project data_location
        project.data_location = str(writer_dir)
        project.save()

        # Create manuscript
        manuscript = Manuscript.objects.create(
            project=project,
            owner=project.owner,
            title=f'{project.name} Manuscript',
            slug=f'{project.slug}-manuscript-{uuid.uuid4().hex[:8]}',
            is_modular=True
        )
        logger.info(f"✓ Created manuscript: {manuscript.title}")

        return writer_dir

    except Exception as e:
        logger.error(f"Failed to create writer directory: {e}", exc_info=True)
        return None


def index(request):
    """Writer app landing page - accessible to all users.

    Simplified approach:
    - Anonymous users: Get guest user + default project
    - Logged-in users: Use their account + default/selected project
    """
    # Determine user and project
    is_guest = False
    is_anonymous = not request.user.is_authenticated

    if is_anonymous:
        # Create or get guest user
        user = get_or_create_guest_user(request)
        is_guest = True
    else:
        user = request.user

    # Get or create default project for this user
    current_project = get_or_create_default_project(user, is_guest=is_guest)

    # Get all user projects
    user_projects = Project.objects.filter(owner=user).order_by('-created_at')

    # Allow project switching for logged-in users (use same session key as scholar_app)
    if not is_guest:
        # Try to get current project from session (use current_project_slug like scholar_app)
        current_project_slug = request.session.get('current_project_slug')
        if current_project_slug:
            try:
                project_from_session = Project.objects.get(
                    slug=current_project_slug,
                    owner=user
                )
                current_project = project_from_session
            except Project.DoesNotExist:
                pass

        # Store current project in session (use slug like scholar_app for consistency)
        request.session['current_project_slug'] = current_project.slug

    # Check if writer directory exists (don't auto-create)
    writer_path = None
    writer_initialized = False

    if current_project.data_location and Path(current_project.data_location).exists():
        writer_path = Path(current_project.data_location)
        writer_initialized = True
        logger.info(f"Writer directory exists: {writer_path}")

    # Load sections from project's writer directory
    sections_data = {}
    if writer_initialized and writer_path:
        manuscript_dir = writer_path / "01_manuscript" / "contents"

        logger.info(f"Loading sections from: {manuscript_dir}")

        if manuscript_dir.exists():
            section_files = {
                'abstract': 'abstract.tex',
                'highlights': 'highlights.tex',
                'introduction': 'introduction.tex',
                'methods': 'methods.tex',
                'results': 'results.tex',
                'discussion': 'discussion.tex',
            }

            for section, filename in section_files.items():
                file_path = manuscript_dir / filename
                if file_path.exists():
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            sections_data[section] = f.read()
                        logger.debug(f"Loaded {section} from {file_path}")
                    except Exception as e:
                        logger.error(f"Failed to read {file_path}: {e}")
                        sections_data[section] = f'% Write your {section} here...\n'
                else:
                    sections_data[section] = f'% Write your {section} here...\n'
                    logger.warning(f"Section file not found: {file_path}")

            logger.info(f"Loaded {len(sections_data)} sections from project")
        else:
            logger.warning(f"Manuscript directory not found: {manuscript_dir}")
            sections_data = _get_default_sections()
    else:
        logger.warning("No project data_location set")
        sections_data = _get_default_sections()

    # Prepare sections data with default content as fallback
    if not sections_data:
        sections_data = _get_default_sections()

    # Create a manuscript object for display
    class DemoManuscript:
        def __init__(self):
            self.title = 'Untitled Manuscript'
            self.word_count = 0
            self.section_word_counts = {}
            self.is_modular = True
            self.id = None

    manuscript = DemoManuscript()

    # Calculate correct writer path for display (use workspace manager)
    from apps.workspace_app.services.directory_service import get_user_directory_manager
    manager = get_user_directory_manager(current_project.owner)
    expected_writer_path = manager.base_path / current_project.slug / "scitex" / "writer"

    context = {
        'project': current_project,
        'manuscript': manuscript,
        'sections': sections_data,
        'is_modular': True,
        'user_projects': user_projects,
        'is_demo': is_guest,  # Demo mode for guest users
        'is_anonymous': is_anonymous,
        'writer_initialized': writer_initialized,  # Whether writer workspace is set up
        'writer_path': str(expected_writer_path),  # Correct local path (not /mnt/nas)
    }

    logger.info(f"Rendering writer page - is_demo={is_guest}, writer_initialized={writer_initialized}, project={current_project.name if current_project else None}")

    return render(request, 'writer_app/project_writer.html', context)


def _get_default_sections():
    """Get default section content."""
    return {
        'abstract': '% Write your abstract here...\n',
        'highlights': '% Write key highlights here...\n',
        'introduction': '% Write your introduction here...\n',
        'methods': '% Describe your methodology...\n',
        'results': '% Present your results...\n',
        'discussion': '% Discuss your findings...\n',
    }


def simple_editor(request):
    """Writer app - direct LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def modular_editor(request):
    """Modular text-based editor with word counts (User Requested Approach)."""
    return render(request, 'writer_app/modular_editor.html')


def simple_editor(request):
    """Simple MVP LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def features(request):
    """Writer features view."""
    return render(request, 'writer_app/features.html')


def pricing(request):
    """Writer pricing view."""
    return render(request, 'writer_app/pricing.html')


@require_http_methods(["POST"])
def mock_compile(request):
    """Mock LaTeX compilation endpoint."""
    # Mock successful compilation
    return JsonResponse({
        'status': 'success',
        'pdf_url': '/static/mock/sample.pdf',
        'log': 'LaTeX compilation completed successfully.\nOutput: 2 pages, 45.7 KB',
        'pages': 2,
        'size': '45.7 KB'
    })


@require_http_methods(["POST"])
def mock_save(request):
    """Mock document save endpoint."""
    return JsonResponse({
        'status': 'success',
        'message': 'Document saved successfully',
        'timestamp': '2024-01-01 12:00:00'
    })


@require_http_methods(["POST"])
def initialize_workspace(request):
    """Initialize writer workspace for a project (opt-in/on-demand)."""
    import json

    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')

        if not project_id:
            return JsonResponse({'success': False, 'error': 'No project ID provided'}, status=400)

        # Get project
        try:
            project = Project.objects.get(id=project_id, owner=request.user)
        except Project.DoesNotExist:
            return JsonResponse({'success': False, 'error': 'Project not found'}, status=404)

        # Initialize writer directory
        writer_path = ensure_writer_directory(project)

        if writer_path:
            return JsonResponse({
                'success': True,
                'message': 'Writer workspace initialized successfully',
                'writer_path': str(writer_path)
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'Failed to create writer directory'
            }, status=500)

    except Exception as e:
        logger.error(f"Error initializing workspace: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)