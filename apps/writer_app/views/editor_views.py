from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.project_app.models import Project
from apps.project_app.services import get_or_create_default_project as centralized_get_or_create_default_project
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


# Note: get_or_create_default_project has been moved to apps.project_app.services.project_utils
# This wrapper function is kept for backward compatibility with any direct imports
def get_or_create_default_project(user, is_guest=False):
    """Wrapper for centralized get_or_create_default_project.

    Note: Writer directory is NOT created here - it's created on-demand
    when the user actually uses the writer feature.
    """
    return centralized_get_or_create_default_project(user, is_guest=is_guest)


def ensure_writer_directory(project):
    """Create writer directory for project if it doesn't exist (opt-in/on-demand).

    Pattern: data/users/username/project-slug/scitex/writer/01_manuscript/...
    Uses workspace directory manager for consistent project storage.
    Uses scitex.writer.Writer class for initialization.
    """
    from scitex.writer import Writer
    from apps.writer_app.models import Manuscript
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager

    # Get workspace manager (needed for both existing and new directories)
    manager = get_project_filesystem_manager(project.owner)

    # Calculate expected writer directory path
    base_dir = manager.base_path / project.slug
    scitex_dir = base_dir / "scitex"
    writer_dir = scitex_dir / "writer"

    # Ensure parent directories exist before Writer() tries to create the project
    scitex_dir.mkdir(parents=True, exist_ok=True)
    logger.info(f"Ensured scitex directory exists: {scitex_dir}")

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

    # Create writer directory on-demand using Writer class
    logger.info(f"Creating writer directory on-demand for project: {project.name}")

    try:
        # Determine git strategy
        project_root = base_dir
        has_git = (project_root / '.git').exists()

        if has_git:
            # Project has git repository - use parent strategy
            git_strategy = 'parent'
            logger.info(f"Using git_strategy='parent' (project has git at {project_root})")
        else:
            # No git - create isolated child repository
            git_strategy = 'child'
            logger.info(f"Using git_strategy='child' (no parent git found)")

        # Initialize Writer instance - this creates the complete structure from template
        # IMPORTANT: Writer() will create the full directory structure including scripts/
        # Do NOT create directories manually before calling Writer()
        try:
            writer = Writer(writer_dir, git_strategy=git_strategy)
            logger.info(f"✓ Writer instance initialized with git_strategy='{git_strategy}'")
            logger.info(f"✓ Writer directory created at: {writer_dir}")
            if writer.git_root:
                logger.info(f"✓ Git root: {writer.git_root}")

            # Verify the complete structure was created
            expected_dirs = ["01_manuscript", "02_supplementary", "03_revision", "scripts", "shared"]
            missing_dirs = [d for d in expected_dirs if not (writer_dir / d).exists()]
            if missing_dirs:
                logger.warning(f"Some expected directories not created: {missing_dirs}")
            else:
                logger.info(f"✓ All expected directories created: {expected_dirs}")

        except Exception as writer_error:
            logger.error(f"Writer initialization failed: {writer_error}", exc_info=True)
            raise Exception(f"Failed to initialize Writer: {writer_error}") from writer_error

        # Ensure project.data_location points to project root (not writer workspace)
        if not project.data_location:
            project.data_location = project.slug
            project.save()
            logger.info(f"Set project data_location to project root: {project.slug}")

        # Create manuscript (non-fatal if it fails - can be created later)
        try:
            manuscript = Manuscript.objects.create(
                project=project,
                owner=project.owner,
                title=f'{project.name} Manuscript',
                slug=f'{project.slug}-manuscript-{uuid.uuid4().hex[:8]}',
                is_modular=True
            )
            logger.info(f"✓ Created manuscript: {manuscript.title}")
        except Exception as manuscript_error:
            logger.warning(f"Could not create manuscript during initialization (non-fatal): {manuscript_error}")
            # Don't raise - manuscript can be created later when user visits writer page

        return writer_dir

    except Exception as e:
        logger.error(f"Failed to ensure writer directory: {e}", exc_info=True)
        # Re-raise the specific error instead of generic message
        # The caller (initialize_workspace) will catch and format it with proper error handling
        raise


def index(request):
    """Writer app landing page - accessible to all users.

    Simplified approach:
    - Anonymous users: Get guest user + default project
    - Logged-in users: Use their account + selected project from header selector
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

    # Get current project (respect header selector for logged-in users)
    current_project = None
    if not is_guest:
        # For authenticated users, use project from header selector
        if hasattr(user, 'profile') and user.profile.last_active_repository:
            current_project = user.profile.last_active_repository

        # Fallback: try session-based project selection
        if not current_project:
            current_project_slug = request.session.get('current_project_slug')
            if current_project_slug:
                try:
                    current_project = Project.objects.get(
                        slug=current_project_slug,
                        owner=user
                    )
                except Project.DoesNotExist:
                    pass

    # Final fallback: get or create default project
    if not current_project:
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

    # Check if writer directory exists and auto-initialize for guest users
    writer_path = None
    writer_initialized = False

    # Use workspace manager to get correct base directory
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager
    manager = get_project_filesystem_manager(current_project.owner)

    # Use data_location if set, otherwise use slug as fallback
    if current_project.data_location:
        # data_location is a relative path from user's base directory to project root
        project_path = manager.base_path / current_project.data_location
    else:
        # Fallback to slug if data_location not set
        project_path = manager.base_path / current_project.slug

    # Writer workspace is at: project_root/scitex/writer/
    writer_path = project_path / "scitex" / "writer"
    if writer_path.exists():
        writer_initialized = True
        logger.info(f"Writer directory exists: {writer_path}")
    elif is_guest:
        # Auto-initialize writer directory for demo/guest users to enable git functionality
        logger.info(f"Auto-initializing writer directory for demo user: {writer_path}")
        try:
            ensure_writer_directory(current_project)
            writer_initialized = True
            logger.info(f"Successfully initialized writer directory for demo user")
        except Exception as e:
            logger.error(f"Failed to initialize writer directory for demo user: {e}", exc_info=True)
            writer_initialized = False

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
    # Use data_location if set, otherwise use slug as fallback
    project_dir = current_project.data_location or current_project.slug
    expected_writer_path = manager.base_path / project_dir / "scitex" / "writer"

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
    logger.info(f"Context check - project type: {type(current_project)}, project id: {current_project.id if current_project else None}, project in context: {'project' in context}")

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
    Uses username + project_slug instead of project_id for better API design.
    """
    import json
    from apps.core.responses import success_response, error_response
    import logging
    console_logger = logging.getLogger('scitex.console')
    endpoint = '/writer/api/initialize-workspace/'

    try:
        data = json.loads(request.body)
        username = data.get('username')
        project_slug = data.get('project_slug')

        if not username or not project_slug:
            return error_response(
                message='Username and project_slug are required',
                error_type='validation_error',
                endpoint=endpoint,
                status=400
            )

        # Determine the user to use for project lookup
        user = None

        # First, check if user is authenticated
        if request.user.is_authenticated:
            user = request.user
            logger.info(f"Initializing workspace for authenticated user: {user.username}")

            # Verify the username matches (security check)
            if user.username != username:
                logger.warning(f"Username mismatch: authenticated as {user.username}, requested {username}")
                return error_response(
                    message='Username mismatch',
                    error_type='authentication_error',
                    endpoint=endpoint,
                    status=403
                )
        else:
            # Try to get guest user from session
            guest_user_id = request.session.get('guest_user_id')
            if guest_user_id:
                try:
                    user = User.objects.get(id=guest_user_id, username__startswith='guest-')
                    logger.info(f"Initializing workspace for guest user: {user.username}")

                    # Verify the username matches
                    if user.username != username:
                        logger.warning(f"Guest username mismatch: session user {user.username}, requested {username}")
                        return error_response(
                            message='Session mismatch. Please refresh the page.',
                            error_type='authentication_error',
                            endpoint=endpoint,
                            status=403
                        )
                except User.DoesNotExist:
                    logger.warning(f"Guest user not found: {guest_user_id}")
                    return error_response(
                        message='Guest session not found. Please refresh the page.',
                        error_type='authentication_error',
                        endpoint=endpoint,
                        status=401
                    )
            else:
                logger.warning("No authenticated user or guest session found")
                return error_response(
                    message='Not authenticated. Please log in or refresh the page.',
                    error_type='authentication_error',
                    endpoint=endpoint,
                    status=401
                )

        if not user:
            return error_response(
                message='Unable to determine user for workspace initialization',
                error_type='authentication_error',
                endpoint=endpoint,
                status=401
            )

        # Get project using slug and owner (more robust than project_id)
        try:
            project = Project.objects.get(slug=project_slug, owner=user)
            logger.info(f"Found project: {project.name} (slug={project_slug}, owner={user.username})")
        except Project.DoesNotExist:
            logger.error(f"Project '{project_slug}' not found for user {user.username}")
            return error_response(
                message=f"Project '{project_slug}' not found for user {user.username}",
                error_type='not_found',
                endpoint=endpoint,
                status=404
            )

        # Initialize writer directory
        logger.info(f"Creating writer directory for project: {project.name} (slug={project_slug}, owner={username})")

        try:
            writer_path = ensure_writer_directory(project)

            if writer_path:
                logger.info(f"✓ Writer workspace initialized successfully: {writer_path}")
                return success_response(
                    message='Writer workspace initialized successfully',
                    data={'writer_path': str(writer_path)},
                    endpoint=endpoint
                )
            else:
                logger.error(f"ensure_writer_directory returned None for project: {project.name}")
                return error_response(
                    message='Failed to create writer directory',
                    error_type='initialization_error',
                    error_details='ensure_writer_directory returned None',
                    endpoint=endpoint,
                    status=500
                )
        except Exception as writer_error:
            # Capture detailed error from ensure_writer_directory
            import traceback
            error_traceback = traceback.format_exc()
            logger.error(f"Failed to initialize writer directory: {writer_error}", exc_info=True)
            return error_response(
                message=f'Failed to initialize Writer: {str(writer_error)}',
                error_type='writer_initialization_error',
                error_details=str(writer_error),
                traceback=error_traceback,
                endpoint=endpoint,
                status=500
            )

    except json.JSONDecodeError:
        logger.error("Invalid JSON in initialize_workspace request")
        return error_response(
            message='Invalid JSON request',
            error_type='json_decode_error',
            endpoint=endpoint,
            status=400
        )
    except Exception as e:
        import traceback
        error_traceback = traceback.format_exc()
        logger.error(f"Error initializing workspace: {e}", exc_info=True)
        return error_response(
            message=f'Server error: {str(e)}',
            error_type='server_error',
            traceback=error_traceback,
            endpoint=endpoint,
            status=500
        )