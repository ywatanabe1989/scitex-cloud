from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from django.db import models
from .models import Project, ProjectMembership, Organization, ResearchGroup
from .decorators import project_required, project_access_required
from django.contrib.auth.models import User
import json


@login_required
def project_list(request):
    """Redirect to user's personal project page (GitHub-style)"""
    return redirect(f'/{request.user.username}/?tab=repositories')


def user_profile(request, username):
    """
    User profile page (GitHub-style /<username>/)

    Public view - no login required (like GitHub)

    Supports tabs via query parameter:
    - /<username>/ or /<username>?tab=overview - Overview
    - /<username>?tab=repositories - Projects list
    - /<username>?tab=stars - Starred projects (future)
    """
    user = get_object_or_404(User, username=username)
    tab = request.GET.get('tab', 'repositories')  # Default to repositories

    if tab == 'repositories':
        return user_project_list(request, username)
    else:
        # For now, all tabs show repositories
        # Future: overview, stars, packages, etc.
        return user_project_list(request, username)


def user_project_list(request, username):
    """List a specific user's projects (called from user_profile with tab=repositories)"""
    user = get_object_or_404(User, username=username)

    # Filter projects based on visibility and access
    user_projects = Project.objects.filter(owner=user)

    # If not the owner, only show public projects or projects where user is a collaborator
    if not (request.user.is_authenticated and request.user == user):
        if request.user.is_authenticated:
            # Show public projects + projects where user is a collaborator
            user_projects = user_projects.filter(
                models.Q(visibility='public') |
                models.Q(memberships__user=request.user)
            ).distinct()
        else:
            # Anonymous users only see public projects
            user_projects = user_projects.filter(visibility='public')

    user_projects = user_projects.order_by('-updated_at')

    # Check if this is the current user viewing their own projects
    is_own_projects = request.user.is_authenticated and request.user == user

    # Add pagination
    paginator = Paginator(user_projects, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)

    context = {
        'projects': projects,
        'profile_user': user,  # The user whose profile we're viewing
        'is_own_projects': is_own_projects,
        # Note: 'user' is automatically available as request.user in templates
        # Don't override it here - it should always be the logged-in user
    }
    return render(request, 'project_app/user_project_list.html', context)


def user_bio_page(request, username):
    """User bio/profile README page (GitHub-style /<username>/<username>/)"""
    user = get_object_or_404(User, username=username)

    # Get or create user profile
    from apps.core_app.models import UserProfile
    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user's projects
    projects = Project.objects.filter(owner=user).order_by('-updated_at')[:6]  # Show top 6

    # Check if this is the user viewing their own profile
    is_own_profile = request.user.is_authenticated and request.user == user

    context = {
        'profile_user': user,
        'profile': profile,
        'projects': projects,
        'is_own_profile': is_own_profile,
        'total_projects': Project.objects.filter(owner=user).count(),
    }

    return render(request, 'project_app/user_bio.html', context)


@project_access_required
def project_detail(request, username, slug):
    """
    Project detail page (GitHub-style /<username>/<project>/)

    Supports mode via query parameter:
    - /<username>/<project>/ or ?mode=overview - Project dashboard
    - /<username>/<project>?mode=scholar - Scholar module
    - /<username>/<project>?mode=writer - Writer module
    - /<username>/<project>?mode=code - Code module
    - /<username>/<project>?mode=viz - Viz module
    """
    # Special case: if slug matches username, this is a bio/profile README page
    if slug == username:
        return user_bio_page(request, username)

    # project available in request.project from decorator
    project = request.project
    mode = request.GET.get('mode', 'overview')
    view = request.GET.get('view', 'default')

    # Track last active repository for this user
    if request.user.is_authenticated and hasattr(request.user, 'profile'):
        if request.user.profile.last_active_repository != project:
            request.user.profile.last_active_repository = project
            request.user.profile.save(update_fields=['last_active_repository'])

    # Handle concatenated view
    if view == 'concatenated':
        return api_concatenate_directory(request, username, slug, '')

    # Route to appropriate module based on mode
    if mode == 'scholar':
        from apps.scholar_app import views as scholar_views
        return scholar_views.project_search(request, project.id)
    elif mode == 'writer':
        from apps.writer_app import views as writer_views
        return writer_views.project_writer(request, project.id)
    elif mode == 'code':
        from apps.code_app import views as code_views
        return code_views.project_code(request, project.id)
    elif mode == 'viz':
        from apps.viz_app import views as viz_views
        return viz_views.project_viz(request, project.id)

    # Default mode: overview - GitHub-style file browser with README
    # Get project directory and file list
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    # Get root directory files (like GitHub)
    files = []
    dirs = []
    readme_content = None
    readme_html = None

    if project_path and project_path.exists():
        try:
            for item in project_path.iterdir():
                # Show all files including dotfiles
                if item.is_file():
                    files.append({
                        'name': item.name,
                        'path': str(item.relative_to(project_path)),
                        'size': item.stat().st_size,
                        'modified': item.stat().st_mtime,
                    })
                elif item.is_dir():
                    dirs.append({
                        'name': item.name,
                        'path': str(item.relative_to(project_path)),
                    })

            # Read README.md if exists and convert to HTML
            readme_path = project_path / 'README.md'
            if readme_path.exists():
                readme_content = readme_path.read_text(encoding='utf-8')
                # Convert markdown to HTML
                import markdown
                readme_html = markdown.markdown(
                    readme_content,
                    extensions=['fenced_code', 'tables', 'nl2br']
                )
        except Exception as e:
            pass

    # Sort: directories first, then files
    dirs.sort(key=lambda x: x['name'].lower())
    files.sort(key=lambda x: x['name'].lower())

    context = {
        'project': project,
        'user': request.user,
        'directories': dirs,
        'files': files,
        'readme_content': readme_content,
        'readme_html': readme_html,
        'mode': mode,
    }
    return render(request, 'project_app/project_detail.html', context)


@login_required
def project_create(request):
    """Create new project"""
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()

        if not name:
            messages.error(request, 'Project name is required')
            return redirect('project_app:list')

        # Ensure unique name
        unique_name = Project.generate_unique_name(name, request.user)

        # Generate unique slug
        from django.utils.text import slugify
        base_slug = slugify(unique_name)
        unique_slug = Project.generate_unique_slug(base_slug)

        project = Project.objects.create(
            name=unique_name,
            slug=unique_slug,
            description=description,
            owner=request.user,
        )

        # Create project directory structure
        from apps.core_app.directory_manager import ensure_project_directory
        ensure_project_directory(project)

        messages.success(request, f'Project "{project.name}" created successfully')
        return redirect('user_projects:detail', username=request.user.username, slug=project.slug)
    
    return render(request, 'project_app/project_create.html')


@login_required
def project_create_from_template(request, username, slug):
    """Create template structure for an existing empty project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can create template
    if project.owner != request.user:
        messages.error(request, "Only project owner can create template structure.")
        return redirect('user_projects:detail', username=username, slug=slug)

    if request.method == 'POST':
        # Create template structure
        from apps.core_app.directory_manager import get_user_directory_manager
        manager = get_user_directory_manager(project.owner)

        success, path = manager.create_project_from_template(project)

        if success:
            messages.success(request, f'Template structure created successfully for "{project.name}"!')
        else:
            messages.error(request, 'Failed to create template structure.')

        return redirect('user_projects:detail', username=username, slug=slug)

    # GET request - show confirmation page or redirect
    return redirect('user_projects:detail', username=username, slug=slug)


@login_required
def project_edit(request, username, slug):
    """Edit project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Only project owner can edit
    if project.owner != request.user:
        messages.error(request, "You don't have permission to edit this project.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    if request.method == 'POST':
        name = request.POST.get('name', '').strip()
        description = request.POST.get('description', '').strip()
        
        if name:
            project.name = name
        if description:
            project.description = description
        
        project.save()
        messages.success(request, 'Project updated successfully')
        return redirect('project_app:detail', username=username, slug=project.slug)
    
    context = {'project': project}
    return render(request, 'project_app/project_edit.html', context)


@login_required
def project_settings(request, username, slug):
    """GitHub-style repository settings page"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can access settings
    if project.owner != request.user:
        messages.error(request, "You don't have permission to access settings.")
        return redirect('user_projects:detail', username=username, slug=slug)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'update_general':
            # Update basic project info
            project.name = request.POST.get('name', '').strip()
            project.description = request.POST.get('description', '').strip()
            project.hypotheses = request.POST.get('hypotheses', '').strip()
            project.save()
            messages.success(request, 'General settings updated successfully')

        elif action == 'update_visibility':
            # Update visibility
            new_visibility = request.POST.get('visibility')
            if new_visibility in ['public', 'private']:
                old_visibility = project.visibility
                project.visibility = new_visibility
                project.save()
                messages.success(request, f'Repository visibility changed from {old_visibility} to {new_visibility}')

        elif action == 'delete_repository':
            # Delete repository
            project_name = project.name
            project.delete()
            messages.success(request, f'Repository "{project_name}" has been deleted')
            return redirect(f'/{request.user.username}/')

        return redirect('user_projects:settings', username=username, slug=slug)

    context = {
        'project': project,
    }
    return render(request, 'project_app/project_settings.html', context)


@login_required
def project_delete(request, username, slug):
    """Delete project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can delete
    if project.owner != request.user:
        messages.error(request, "You don't have permission to delete this project.")
        return redirect('project_app:detail', username=username, slug=slug)

    if request.method == 'POST':
        project_name = project.name
        project.delete()
        messages.success(request, f'Project "{project_name}" deleted successfully')
        return redirect('project_app:list')

    context = {'project': project}
    return render(request, 'project_app/project_delete.html', context)


@login_required
def project_collaborate(request, username, slug):
    """Project collaboration management"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage collaborators
    if project.owner != request.user:
        messages.error(request, "You don't have permission to manage collaborators for this project.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    context = {
        'project': project,
        'memberships': project.memberships.all(),
    }
    return render(request, 'project_app/project_collaborate.html', context)


@login_required
def project_members(request, username, slug):
    """Project members management"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage members
    if project.owner != request.user:
        messages.error(request, "You don't have permission to manage members for this project.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    context = {
        'project': project,
        'members': project.memberships.all(),
    }
    return render(request, 'project_app/project_members.html', context)


@login_required
def github_integration(request, username, slug):
    """GitHub integration for project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Only project owner can manage GitHub integration
    if project.owner != request.user:
        messages.error(request, "You don't have permission to manage GitHub integration for this project.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    context = {
        'project': project,
    }
    return render(request, 'project_app/github_integration.html', context)


# API Views
@login_required
@require_http_methods(["GET"])
def api_file_tree(request, username, slug):
    """API endpoint to get project file tree for sidebar navigation"""
    from pathlib import Path

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists()
    )

    if not has_access:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    # Get project directory
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse({'success': False, 'error': 'Project directory not found'})

    def build_tree(path, max_depth=5, current_depth=0):
        """Build file tree recursively (deeper for full navigation)"""
        items = []
        try:
            for item in sorted(path.iterdir(), key=lambda x: (not x.is_dir(), x.name.lower())):
                if item.name.startswith('.') and item.name not in ['.gitignore']:
                    continue
                # Skip common non-essential directories
                if item.name in ['__pycache__', '.git', 'node_modules', '.venv', 'venv']:
                    continue

                rel_path = item.relative_to(project_path)
                item_data = {
                    'name': item.name,
                    'type': 'directory' if item.is_dir() else 'file',
                    'path': str(rel_path),
                }

                # Add children for directories (deeper depth for full tree)
                if item.is_dir() and current_depth < max_depth:
                    item_data['children'] = build_tree(item, max_depth, current_depth + 1)

                items.append(item_data)
        except PermissionError:
            pass

        return items

    tree = build_tree(project_path)

    return JsonResponse({'success': True, 'tree': tree})


@login_required
@require_http_methods(["GET"])
def api_project_list(request):
    """API endpoint for project list"""
    projects = Project.objects.filter(owner=request.user).values(
        'id', 'name', 'description', 'created_at', 'updated_at'
    )
    return JsonResponse({'projects': list(projects)})


@login_required
@require_http_methods(["POST"])
def api_project_create(request):
    """API endpoint for project creation"""
    try:
        data = json.loads(request.body)
        name = data.get('name', '').strip()
        description = data.get('description', '').strip()
        
        if not name:
            return JsonResponse({'success': False, 'error': 'Project name is required'})
        
        # Ensure unique name
        unique_name = Project.generate_unique_name(name, request.user)
        
        project = Project.objects.create(
            name=unique_name,
            description=description,
            owner=request.user,
        )
        
        return JsonResponse({
            'success': True, 
            'project_id': project.pk,
            'message': f'Project "{project.name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def api_concatenate_directory(request, username, slug, directory_path=''):
    """
    API endpoint to concatenate all files in a directory (like view_repo.sh).
    Returns markdown-formatted content with tree + file contents.
    """
    from pathlib import Path

    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists()
    )

    if not has_access:
        return JsonResponse({'success': False, 'error': 'Permission denied'})

    # Get directory path
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        return JsonResponse({'success': False, 'error': 'Project directory not found'})

    dir_path = project_path / directory_path

    # Security check
    try:
        dir_path = dir_path.resolve()
        if not str(dir_path).startswith(str(project_path.resolve())):
            return JsonResponse({'success': False, 'error': 'Invalid path'})
    except:
        return JsonResponse({'success': False, 'error': 'Invalid path'})

    if not dir_path.exists() or not dir_path.is_dir():
        return JsonResponse({'success': False, 'error': 'Directory not found'})

    # Whitelist extensions
    WHITELIST_EXTS = {'.txt', '.md', '.org', '.sh', '.py', '.yaml', '.yml', '.json', '.tex', '.bib'}
    MAX_FILE_SIZE = 100000  # 100KB

    output = []
    output.append(f"# Directory View: {directory_path if directory_path else 'Project Root'}")
    output.append(f"Project: {project.name}")
    output.append(f"Owner: {project.owner.username}")
    output.append(f"")
    output.append(f"## File Contents")
    output.append(f"")

    # Recursively get all files
    for file_path in sorted(dir_path.rglob('*')):
        if not file_path.is_file():
            continue
        if file_path.name.startswith('.') and file_path.name not in ['.gitignore', '.gitkeep']:
            continue
        if file_path.suffix.lower() not in WHITELIST_EXTS:
            continue
        if file_path.stat().st_size > MAX_FILE_SIZE:
            continue

        try:
            rel_path = file_path.relative_to(dir_path)
            content = file_path.read_text(encoding='utf-8', errors='ignore')

            # Get language for syntax highlighting
            lang_map = {'.py': 'python', '.sh': 'bash', '.yaml': 'yaml', '.yml': 'yaml',
                       '.json': 'json', '.md': 'markdown', '.tex': 'latex'}
            lang = lang_map.get(file_path.suffix.lower(), 'plaintext')

            output.append(f"### `{rel_path}`")
            output.append(f"")
            output.append(f"```{lang}")
            output.append(content[:5000])  # First 5000 chars
            if len(content) > 5000:
                output.append("...")
            output.append("```")
            output.append(f"")
        except Exception as e:
            continue

    concatenated_content = "\n".join(output)

    return JsonResponse({
        'success': True,
        'content': concatenated_content,
        'file_count': len([l for l in output if l.startswith('###')])
    })


@login_required
@require_http_methods(["GET"])
def api_project_detail(request, pk):
    """API endpoint for project detail"""
    try:
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        data = {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'progress': project.progress,
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
        }
        return JsonResponse({'success': True, 'project': data})
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@login_required
def project_detail_redirect(request, pk=None, slug=None):
    """Redirect old URLs to new username/project URLs for backward compatibility"""
    if pk:
        # Redirect from /projects/id/123/ to /username/project-name/
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        return redirect('project_app:detail', username=project.owner.username, slug=project.slug, permanent=True)
    elif slug:
        # Redirect from /projects/project-name/ to /username/project-name/
        project = get_object_or_404(Project, slug=slug, owner=request.user)
        return redirect('project_app:detail', username=project.owner.username, slug=project.slug, permanent=True)
    else:
        return redirect('project_app:list')


def project_directory_dynamic(request, username, slug, directory_path):
    """
    Dynamic directory browser - handles ANY directory path.

    URLs like:
    - /username/project/scripts/
    - /username/project/scripts/mnist/
    - /username/project/paper/manuscript/
    - /username/project/data/raw/images/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access permissions
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists() or
        getattr(project, 'visibility', None) == 'public'
    )

    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('user_projects:detail', username=username, slug=slug)

    # Get project path
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Construct full directory path
    from pathlib import Path
    full_directory_path = project_path / directory_path

    # Security check: ensure path is within project directory
    try:
        full_directory_path = full_directory_path.resolve()
        if not str(full_directory_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid directory path.")
            return redirect('user_projects:detail', username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Check if directory exists
    if not full_directory_path.exists():
        messages.error(request, f"Directory '{directory_path}' not found.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Get directory contents
    contents = []
    try:
        for item in full_directory_path.iterdir():
            # Show all files and directories including hidden files
            # Skip only special directories like .git
            if item.is_dir() and item.name in ['.git', '__pycache__', 'node_modules', '.venv', 'venv']:
                continue

            if item.is_file():
                contents.append({
                    'name': item.name,
                    'type': 'file',
                    'size': item.stat().st_size,
                    'modified': item.stat().st_mtime,
                    'path': str(item.relative_to(project_path))
                })
            elif item.is_dir():
                contents.append({
                    'name': item.name,
                    'type': 'directory',
                    'path': str(item.relative_to(project_path))
                })
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Sort: directories first, then files, alphabetically
    contents.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))

    # Build breadcrumb navigation
    breadcrumbs = [
        {'name': project.name, 'url': f"/{username}/{slug}/"}
    ]

    # Add each path component to breadcrumbs
    path_parts = directory_path.split('/')
    current_path = ''
    for part in path_parts:
        if part:
            current_path += part + '/'
            breadcrumbs.append({
                'name': part,
                'url': f"/{username}/{slug}/{current_path}"
            })

    context = {
        'project': project,
        'directory': path_parts[0] if path_parts else directory_path,
        'subpath': '/'.join(path_parts[1:]) if len(path_parts) > 1 else None,
        'breadcrumb_path': directory_path,
        'contents': contents,
        'breadcrumbs': breadcrumbs,
        'can_edit': project.owner == request.user or project.collaborators.filter(id=request.user.id).exists(),
    }

    return render(request, 'project_app/project_directory.html', context)


def project_file_view(request, username, slug, file_path):
    """
    View/Edit file contents (GitHub-style /blob/).

    Modes (via query parameter):
    - ?mode=view (default) - View with syntax highlighting
    - ?mode=edit - Edit file content
    - ?mode=raw - Serve raw file content

    Supports:
    - Markdown (.md) - Rendered as HTML
    - Python (.py) - Syntax highlighted
    - YAML (.yaml, .yml) - Syntax highlighted
    - JSON (.json) - Syntax highlighted
    - Text files - Plain text with line numbers
    - Images - Display inline
    """
    from pathlib import Path

    mode = request.GET.get('mode', 'view')
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)

    # Check access
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists() or
        getattr(project, 'visibility', None) == 'public'
    )

    if not has_access:
        messages.error(request, "You don't have permission to access this file.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Get file path
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)

    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect('user_projects:detail', username=username, slug=slug)

    full_file_path = project_path / file_path

    # Security check
    try:
        full_file_path = full_file_path.resolve()
        if not str(full_file_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid file path.")
            return redirect('user_projects:detail', username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid file path.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Check if file exists and is a file
    if not full_file_path.exists() or not full_file_path.is_file():
        messages.error(request, "File not found.")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Determine file type and rendering method
    file_name = full_file_path.name
    file_ext = full_file_path.suffix.lower()
    file_size = full_file_path.stat().st_size

    # Handle raw mode - serve file directly
    if mode == 'raw':
        # Determine content type based on file extension
        content_type = 'text/plain; charset=utf-8'
        if file_ext == '.pdf':
            content_type = 'application/pdf'
        elif file_ext in ['.png']:
            content_type = 'image/png'
        elif file_ext in ['.jpg', '.jpeg']:
            content_type = 'image/jpeg'
        elif file_ext in ['.gif']:
            content_type = 'image/gif'

        with open(full_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'inline; filename="{file_name}"'
            return response

    # Handle edit mode - show editor
    if mode == 'edit':
        if not (project.owner == request.user):
            messages.error(request, "Only project owner can edit files.")
            return redirect('user_projects:detail', username=username, slug=slug)

        if request.method == 'POST':
            # Save edited content
            new_content = request.POST.get('content', '')
            try:
                with open(full_file_path, 'w', encoding='utf-8') as f:
                    f.write(new_content)
                messages.success(request, f"File '{file_name}' saved successfully!")
                return redirect('user_projects:file_view', username=username, slug=slug, file_path=file_path)
            except Exception as e:
                messages.error(request, f"Error saving file: {e}")

        # Read current content for editing
        try:
            with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()
        except Exception as e:
            messages.error(request, f"Error reading file: {e}")
            return redirect('user_projects:detail', username=username, slug=slug)

        # Build breadcrumb
        breadcrumbs = [{'name': project.name, 'url': f"/{username}/{slug}/"}]
        path_parts = file_path.split('/')
        current_path = ''
        for i, part in enumerate(path_parts):
            current_path += part
            if i < len(path_parts) - 1:
                current_path += '/'
                breadcrumbs.append({'name': part, 'url': f"/{username}/{slug}/{current_path}"})
            else:
                breadcrumbs.append({'name': part, 'url': None})

        context = {
            'project': project,
            'file_name': file_name,
            'file_path': file_path,
            'file_content': file_content,
            'breadcrumbs': breadcrumbs,
            'mode': 'edit',
        }
        return render(request, 'project_app/project_file_edit.html', context)

    # Read file content
    try:
        # Check if binary file
        is_binary = file_ext in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz']

        if is_binary:
            # For images, show inline
            if file_ext in ['.png', '.jpg', '.jpeg', '.gif']:
                render_type = 'image'
                file_content = None
                file_html = None
            # For PDFs, use PDF.js viewer
            elif file_ext == '.pdf':
                render_type = 'pdf'
                file_content = None
                file_html = None
            else:
                render_type = 'binary'
                file_content = f"Binary file ({file_size} bytes)"
                file_html = None
        else:
            # Read text file
            with open(full_file_path, 'r', encoding='utf-8', errors='ignore') as f:
                file_content = f.read()

            # Render based on file type
            if file_ext == '.md':
                import markdown
                file_html = markdown.markdown(
                    file_content,
                    extensions=['fenced_code', 'tables', 'nl2br', 'codehilite']
                )
                render_type = 'markdown'
            elif file_ext in ['.py', '.yaml', '.yml', '.json', '.txt', '.sh', '.bash', '.tex', '.bib']:
                # Use Pygments for syntax highlighting
                try:
                    from pygments import highlight
                    from pygments.lexers import get_lexer_for_filename
                    from pygments.formatters import HtmlFormatter

                    lexer = get_lexer_for_filename(file_name)
                    formatter = HtmlFormatter(
                        linenos='table',
                        cssclass='highlight',
                        style='default',
                        noclasses=False
                    )
                    file_html = highlight(file_content, lexer, formatter)
                    render_type = 'code'
                except Exception as e:
                    print(f"Pygments error: {e}")
                    file_html = None
                    render_type = 'text'
            else:
                file_html = None
                render_type = 'text'

    except Exception as e:
        messages.error(request, f"Error reading file: {e}")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Build breadcrumb
    breadcrumbs = [{'name': project.name, 'url': f"/{username}/{slug}/"}]

    path_parts = file_path.split('/')
    current_path = ''
    for i, part in enumerate(path_parts):
        current_path += part
        if i < len(path_parts) - 1:  # Directory
            current_path += '/'
            breadcrumbs.append({
                'name': part,
                'url': f"/{username}/{slug}/{current_path}"
            })
        else:  # File
            breadcrumbs.append({'name': part, 'url': None})

    context = {
        'project': project,
        'file_name': file_name,
        'file_path': file_path,
        'file_size': file_size,
        'file_ext': file_ext,
        'file_content': file_content,
        'file_html': file_html,
        'render_type': render_type,
        'breadcrumbs': breadcrumbs,
        'can_edit': project.owner == request.user,
    }

    return render(request, 'project_app/project_file_view.html', context)


def project_directory(request, username, slug, directory, subpath=None):
    """
    Browse scientific workflow directories within a project.
    
    URLs like:
    - /username/project-name/scripts/
    - /username/project-name/scripts/analysis/
    - /username/project-name/data/raw/
    """
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists() or
        project.visibility == 'public'
    )
    
    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:detail', username=username, slug=slug)
    
    # Get the project directory manager
    from apps.core_app.directory_manager import get_user_directory_manager
    manager = get_user_directory_manager(project.owner)
    project_path = manager.get_project_path(project)
    
    if not project_path or not project_path.exists():
        messages.error(request, "Project directory not found.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    # Construct the full directory path
    if subpath:
        directory_path = project_path / directory / subpath
        breadcrumb_path = f"{directory}/{subpath}"
    else:
        directory_path = project_path / directory
        breadcrumb_path = directory
    
    # Security check: ensure path is within project directory
    try:
        directory_path = directory_path.resolve()
        if not str(directory_path).startswith(str(project_path.resolve())):
            messages.error(request, "Invalid directory path.")
            return redirect('project_app:detail', username=username, slug=slug)
    except Exception:
        messages.error(request, "Invalid directory path.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    # Check if directory exists
    if not directory_path.exists():
        messages.error(request, f"Directory '{breadcrumb_path}' not found.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    # Get directory contents
    contents = []
    try:
        for item in directory_path.iterdir():
            # Show all files and directories including dotfiles
            if item.is_file():
                contents.append({
                    'name': item.name,
                    'type': 'file',
                    'size': item.stat().st_size,
                    'modified': item.stat().st_mtime,
                    'path': str(item.relative_to(project_path))
                })
            elif item.is_dir():
                contents.append({
                    'name': item.name,
                    'type': 'directory',
                    'path': str(item.relative_to(project_path))
                })
    except PermissionError:
        messages.error(request, "Permission denied accessing directory.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    # Sort contents: directories first, then files, both alphabetically
    contents.sort(key=lambda x: (x['type'] == 'file', x['name'].lower()))
    
    # Build breadcrumb navigation
    breadcrumbs = [
        {'name': project.name, 'url': project.get_absolute_url()},
        {'name': directory, 'url': f"{project.get_absolute_url()}{directory}/"}
    ]
    
    if subpath:
        path_parts = subpath.split('/')
        current_path = directory
        for part in path_parts:
            current_path += f"/{part}"
            breadcrumbs.append({
                'name': part,
                'url': f"{project.get_absolute_url()}{current_path}/"
            })
    
    context = {
        'project': project,
        'directory': directory,
        'subpath': subpath,
        'breadcrumb_path': breadcrumb_path,
        'contents': contents,
        'breadcrumbs': breadcrumbs,
        'can_edit': project.owner == request.user or project.collaborators.filter(id=request.user.id).exists(),
    }
    
    return render(request, 'project_app/project_directory.html', context)