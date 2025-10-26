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
    Creates directory structure directly without git cloning for reliability.
    """
    from apps.writer_app.models import Manuscript
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager

    # Get workspace manager (needed for both existing and new directories)
    manager = get_project_filesystem_manager(project.owner)

    # Calculate expected writer directory path
    base_dir = manager.base_path / project.slug
    scitex_dir = base_dir / "scitex"
    writer_dir = scitex_dir / "writer"

    # Check if writer directory already exists (must check the actual writer dir, not just data_location)
    if writer_dir.exists() and (writer_dir / "01_manuscript").exists():
        logger.info(f"Writer directory already exists: {writer_dir}")

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

        # Ensure project.data_location points to project root (not writer workspace)
        expected_project_path = project.slug
        if not project.data_location or project.data_location != expected_project_path:
            project.data_location = expected_project_path
            project.save()
            logger.info(f"Corrected project data_location to project root: {expected_project_path}")

        return writer_dir  # Return absolute path to writer directory

    # Create writer directory on-demand with minimal structure
    logger.info(f"Creating writer directory on-demand for project: {project.name}")

    try:
        # Create main writer directory structure
        scitex_dir.mkdir(parents=True, exist_ok=True)
        writer_dir.mkdir(parents=True, exist_ok=True)

        # Create required subdirectories
        directories = [
            writer_dir / "01_manuscript" / "contents",
            writer_dir / "02_supplementary" / "contents",
            writer_dir / "03_revision" / "contents",
            writer_dir / "shared",
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)
            logger.debug(f"Created directory: {directory}")

        # Create minimal .gitkeep files to ensure directories are committed
        for directory in [writer_dir / "01_manuscript", writer_dir / "02_supplementary",
                         writer_dir / "03_revision", writer_dir / "shared"]:
            gitkeep_file = directory / ".gitkeep"
            gitkeep_file.touch()
            logger.debug(f"Created .gitkeep in {directory}")

        logger.info(f"✓ Created writer directory structure: {writer_dir}")

        # Ensure project.data_location points to project root (not writer workspace)
        if not project.data_location:
            project.data_location = project.slug
            project.save()
            logger.info(f"Set project data_location to project root: {project.slug}")

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

    # Use workspace manager to get correct base directory
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager
    manager = get_project_filesystem_manager(current_project.owner)

    if current_project.data_location:
        # data_location is a relative path from user's base directory
        full_writer_path = manager.base_path / current_project.data_location
        if full_writer_path.exists():
            writer_path = full_writer_path
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
            self.word_count_abstract = 0
            self.word_count_introduction = 0
            self.word_count_methods = 0
            self.word_count_results = 0
            self.word_count_discussion = 0
            self.section_word_counts = {}
            self.is_modular = True
            self.id = None

    manuscript = DemoManuscript()

    # Calculate correct writer path for display (manager already created above)
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

    return render(request, 'writer_app/index.html', context)


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
    """Simple LaTeX editor interface."""
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
    """Initialize writer workspace for a project (opt-in/on-demand).

    Handles both authenticated users and guest users via session.
    """
    import json

    try:
        data = json.loads(request.body)
        project_id = data.get('project_id')

        if not project_id:
            return JsonResponse({'success': False, 'error': 'No project ID provided'}, status=400)

        # Determine the user to use for project lookup
        user = None

        # First, check if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            logger.info(f"Initializing workspace for authenticated user: {user.username}")
        else:
            # Try to get guest user from session
            guest_user_id = request.session.get('guest_user_id')
            if guest_user_id:
                try:
                    user = User.objects.get(id=guest_user_id, username__startswith='guest-')
                    logger.info(f"Initializing workspace for guest user: {user.username}")
                except User.DoesNotExist:
                    logger.warning(f"Guest user not found: {guest_user_id}")
                    return JsonResponse({
                        'success': False,
                        'error': 'Guest session not found. Please refresh the page.'
                    }, status=401)
            else:
                logger.warning("No authenticated user or guest session found")
                return JsonResponse({
                    'success': False,
                    'error': 'Not authenticated. Please log in or refresh the page.'
                }, status=401)

        if not user:
            return JsonResponse({
                'success': False,
                'error': 'Unable to determine user for workspace initialization'
            }, status=401)

        # Get project
        try:
            project = Project.objects.get(id=project_id, owner=user)
        except Project.DoesNotExist:
            logger.error(f"Project {project_id} not found for user {user.username}")
            return JsonResponse({
                'success': False,
                'error': f'Project not found for user {user.username}'
            }, status=404)

        # Initialize writer directory
        logger.info(f"Creating writer directory for project: {project.name} (id={project_id})")
        writer_path = ensure_writer_directory(project)

        if writer_path:
            logger.info(f"✓ Writer workspace initialized successfully: {writer_path}")
            return JsonResponse({
                'success': True,
                'message': 'Writer workspace initialized successfully',
                'writer_path': str(writer_path)
            })
        else:
            logger.error(f"Failed to create writer directory for project: {project.name}")
            return JsonResponse({
                'success': False,
                'error': 'Failed to create writer directory'
            }, status=500)

    except json.JSONDecodeError:
        logger.error("Invalid JSON in initialize_workspace request")
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON request'
        }, status=400)
    except Exception as e:
        logger.error(f"Error initializing workspace: {e}", exc_info=True)
        return JsonResponse({
            'success': False,
            'error': f'Server error: {str(e)}'
        }, status=500)