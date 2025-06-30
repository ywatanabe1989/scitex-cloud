from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Project, ProjectMembership, Organization, ResearchGroup
from django.contrib.auth.models import User
import json


@login_required
def project_list(request):
    """List current user's projects with file manager interface"""
    user_projects = Project.objects.filter(owner=request.user).order_by('-updated_at')
    
    # Add pagination
    paginator = Paginator(user_projects, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'projects': projects,
        'user': request.user,
        'is_own_projects': True,
    }
    return render(request, 'project_app/project_list.html', context)


def user_project_list(request, username):
    """List a specific user's projects (GitHub-style /username/)"""
    user = get_object_or_404(User, username=username)
    
    # For now, show all projects. Later we can add privacy settings
    user_projects = Project.objects.filter(owner=user).order_by('-updated_at')
    
    # If this is the current user viewing their own projects, redirect to /projects/
    if request.user.is_authenticated and request.user == user:
        return redirect('project_app:list')
    
    # Add pagination
    paginator = Paginator(user_projects, 12)
    page_number = request.GET.get('page')
    projects = paginator.get_page(page_number)
    
    context = {
        'projects': projects,
        'user': user,
        'is_own_projects': False,
        'profile_user': user,
    }
    return render(request, 'project_app/user_project_list.html', context)


def project_detail(request, username, slug):
    """Project detail with file manager - GitHub-style URL"""
    # Get user by username
    user = get_object_or_404(User, username=username)
    # Get project by slug and owner
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check if current user has access to this project
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )
    else:
        # For now, only authenticated users can view projects
        # Later we can add public project visibility settings
        has_access = False
    
    if not has_access and not request.user.is_authenticated:
        from django.contrib.auth.views import redirect_to_login
        return redirect_to_login(request.get_full_path())
    elif not has_access:
        messages.error(request, "You don't have permission to access this project.")
        return redirect('project_app:list')
    
    # Get project manuscripts from Writer app
    project_manuscripts = []
    try:
        from apps.writer_app.models import Manuscript
        project_manuscripts = Manuscript.objects.filter(
            project=project, 
            owner=request.user
        ).order_by('-updated_at')[:5]
    except:
        pass
    
    # Get project documents from Document app
    project_documents = []
    try:
        from apps.document_app.models import Document
        project_documents = Document.objects.filter(
            project=project,
            owner=request.user
        ).order_by('-updated_at')[:5]
    except:
        pass
    
    # Get saved papers from Scholar app
    saved_papers = []
    try:
        from apps.scholar_app.models import UserLibrary
        saved_papers = UserLibrary.objects.filter(
            user=request.user,
            project=project
        ).select_related('paper').order_by('-saved_at')[:5]
    except:
        pass
    
    context = {
        'project': project,
        'user': request.user,
        'project_manuscripts': project_manuscripts,
        'project_documents': project_documents,
        'saved_papers': saved_papers,
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
        
        project = Project.objects.create(
            name=unique_name,
            description=description,
            owner=request.user,
            hypotheses=''  # Required field
        )
        
        messages.success(request, f'Project "{project.name}" created successfully')
        return redirect('project_app:detail', slug=project.slug)
    
    return render(request, 'project_app/project_create.html')


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
def project_files(request, username, slug):
    """Project file manager"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists() or
        request.user.is_staff
    )
    
    if not has_access:
        messages.error(request, "You don't have permission to access this project's files.")
        return redirect('project_app:detail', username=username, slug=slug)
    
    context = {
        'project': project,
        'user': request.user,
    }
    return render(request, 'project_app/project_files.html', context)


@login_required
def file_upload(request, username, slug):
    """File upload for project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check write permissions
    has_write_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists()
    )
    
    if not has_write_access:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    if request.method == 'POST':
        # Handle file upload logic here
        messages.success(request, 'Files uploaded successfully')
        return redirect('project_app:files', username=username, slug=slug)
    
    return JsonResponse({'success': False, 'error': 'Invalid request'})


@login_required
def file_download(request, username, slug):
    """File download from project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check read permissions
    has_access = (
        project.owner == request.user or
        project.collaborators.filter(id=request.user.id).exists() or
        request.user.is_staff
    )
    
    if not has_access:
        return JsonResponse({'success': False, 'error': 'Permission denied'})
    
    # Handle file download logic here
    return HttpResponse('File download not implemented yet')


@login_required
def project_collaborate(request, slug):
    """Project collaboration management"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    context = {
        'project': project,
        'memberships': project.memberships.all(),
    }
    return render(request, 'project_app/project_collaborate.html', context)


@login_required
def project_members(request, slug):
    """Project members management"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    context = {
        'project': project,
        'members': project.memberships.all(),
    }
    return render(request, 'project_app/project_members.html', context)


@login_required
def github_integration(request, slug):
    """GitHub integration for project"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    context = {
        'project': project,
    }
    return render(request, 'project_app/github_integration.html', context)


@login_required
def project_sync(request, slug):
    """Sync project with external services"""
    project = get_object_or_404(Project, slug=slug, owner=request.user)
    
    # Handle sync logic here
    return JsonResponse({'success': True, 'message': 'Project synced successfully'})


# API Views
@login_required
@require_http_methods(["GET"])
def api_project_list(request):
    """API endpoint for project list"""
    projects = Project.objects.filter(owner=request.user).values(
        'id', 'name', 'description', 'status', 'created_at', 'updated_at'
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
            hypotheses=''  # Required field
        )
        
        return JsonResponse({
            'success': True, 
            'project_id': project.pk,
            'message': f'Project "{project.name}" created successfully'
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


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
            'status': project.status,
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


# Module Integration Views
def project_scholar(request, username, slug):
    """Redirect to Scholar search for this project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )
    else:
        has_access = False
    
    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:detail', username=username, slug=slug)
    
    # Redirect to Scholar with project context
    from django.urls import reverse
    scholar_url = reverse('scholar_app:project_search', kwargs={'project_id': project.id})
    return redirect(scholar_url)


def project_writer(request, username, slug):
    """Redirect to Writer for this project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )
    else:
        has_access = False
    
    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:detail', username=username, slug=slug)
    
    # Redirect to Writer with project context
    from django.urls import reverse
    writer_url = reverse('writer_app:project_dashboard', kwargs={'project_id': project.id})
    return redirect(writer_url)


def project_code(request, username, slug):
    """Code module integration for this project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )
    else:
        has_access = False
    
    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:detail', username=username, slug=slug)
    
    # For now, redirect to code app with project context
    return redirect('code_app:index')


def project_viz(request, username, slug):
    """Viz module integration for this project"""
    user = get_object_or_404(User, username=username)
    project = get_object_or_404(Project, slug=slug, owner=user)
    
    # Check access permissions
    if request.user.is_authenticated:
        has_access = (
            project.owner == request.user or
            project.collaborators.filter(id=request.user.id).exists() or
            request.user.is_staff
        )
    else:
        has_access = False
    
    if not has_access:
        if not request.user.is_authenticated:
            from django.contrib.auth.views import redirect_to_login
            return redirect_to_login(request.get_full_path())
        else:
            messages.error(request, "You don't have permission to access this project.")
            return redirect('project_app:detail', username=username, slug=slug)
    
    # For now, redirect to viz app with project context
    return redirect('viz_app:index')


@login_required
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
            if item.is_file() and not item.name.startswith('.'):
                contents.append({
                    'name': item.name,
                    'type': 'file',
                    'size': item.stat().st_size,
                    'modified': item.stat().st_mtime,
                    'path': str(item.relative_to(project_path))
                })
            elif item.is_dir() and not item.name.startswith('.'):
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