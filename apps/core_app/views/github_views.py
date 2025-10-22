"""
GitHub Integration API Views for SciTeX Cloud
Enhanced GitHub connectivity for seamless version control integration
"""

import json
import requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from ..models import Project, GitFileStatus
import subprocess
import os
from pathlib import Path


# GitHub OAuth Configuration
GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET', '')
GITHUB_REDIRECT_URI = getattr(settings, 'GITHUB_REDIRECT_URI', '')


@login_required
@require_http_methods(["POST"])
def github_oauth_initiate(request):
    """Initiate GitHub OAuth flow"""
    project_id = request.POST.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'Project ID required'}, status=400)
    
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    # Store project ID in session for callback
    request.session['github_project_id'] = project_id
    
    # GitHub OAuth URL
    oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope=repo,user:email"
        f"&state={project_id}"
    )
    
    return JsonResponse({
        'success': True,
        'oauth_url': oauth_url
    })


@login_required
@require_http_methods(["GET"])
def github_oauth_callback(request):
    """Handle GitHub OAuth callback"""
    code = request.GET.get('code')
    state = request.GET.get('state')  # project_id
    
    if not code or not state:
        return JsonResponse({'error': 'Invalid OAuth callback'}, status=400)
    
    project = get_object_or_404(Project, id=state, owner=request.user)
    
    # Exchange code for access token
    token_response = requests.post('https://github.com/login/oauth/access_token', {
        'client_id': GITHUB_CLIENT_ID,
        'client_secret': GITHUB_CLIENT_SECRET,
        'code': code,
    }, headers={'Accept': 'application/json'})
    
    if token_response.status_code != 200:
        return JsonResponse({'error': 'Failed to get access token'}, status=400)
    
    token_data = token_response.json()
    access_token = token_data.get('access_token')
    
    if not access_token:
        return JsonResponse({'error': 'No access token received'}, status=400)
    
    # Get user info from GitHub
    user_response = requests.get('https://api.github.com/user', 
                                headers={'Authorization': f'token {access_token}'})
    
    if user_response.status_code == 200:
        user_data = user_response.json()
        
        # Update project with GitHub token
        project.github_token = access_token
        project.github_owner = user_data.get('login')
        project.github_integration_enabled = True
        project.last_sync_at = timezone.now()
        project.save()
        
        return JsonResponse({
            'success': True,
            'message': 'GitHub connected successfully',
            'github_username': user_data.get('login')
        })
    
    return JsonResponse({'error': 'Failed to get user info'}, status=400)


@login_required
@require_http_methods(["POST"])
def github_create_repository(request):
    """Create a new GitHub repository"""
    project_id = request.POST.get('project_id')
    repo_name = request.POST.get('repo_name')
    is_private = request.POST.get('is_private', 'false').lower() == 'true'
    description = request.POST.get('description', '')
    
    if not project_id or not repo_name:
        return JsonResponse({'error': 'Project ID and repository name required'}, status=400)
    
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if not project.github_token:
        return JsonResponse({'error': 'GitHub not connected'}, status=400)
    
    # Create repository via GitHub API
    repo_data = {
        'name': repo_name,
        'description': description or f"Research project: {project.name}",
        'private': is_private,
        'auto_init': True,
        'gitignore_template': 'Python'  # Research-friendly template
    }
    
    response = requests.post(
        'https://api.github.com/user/repos',
        headers={
            'Authorization': f'token {project.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        },
        json=repo_data
    )
    
    if response.status_code == 201:
        repo_info = response.json()
        
        # Update project with repository info
        project.github_repo_id = repo_info['id']
        project.github_repo_name = repo_info['name']
        project.source_code_url = repo_info['html_url']
        project.current_branch = repo_info['default_branch']
        project.last_sync_at = timezone.now()
        project.save()
        
        return JsonResponse({
            'success': True,
            'repository': {
                'id': repo_info['id'],
                'name': repo_info['name'],
                'url': repo_info['html_url'],
                'clone_url': repo_info['clone_url']
            }
        })
    
    return JsonResponse({'error': 'Failed to create repository'}, status=400)


@login_required
@require_http_methods(["POST"])
def github_link_repository(request):
    """Link existing GitHub repository to project"""
    project_id = request.POST.get('project_id')
    repo_url = request.POST.get('repo_url')
    
    if not project_id or not repo_url:
        return JsonResponse({'error': 'Project ID and repository URL required'}, status=400)
    
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if not project.github_token:
        return JsonResponse({'error': 'GitHub not connected'}, status=400)
    
    # Parse repository URL to get owner/repo
    try:
        if 'github.com/' in repo_url:
            parts = repo_url.split('github.com/')[-1].strip('/').split('/')
            if len(parts) >= 2:
                owner, repo_name = parts[0], parts[1]
            else:
                return JsonResponse({'error': 'Invalid repository URL'}, status=400)
        else:
            return JsonResponse({'error': 'Not a valid GitHub URL'}, status=400)
    except Exception:
        return JsonResponse({'error': 'Could not parse repository URL'}, status=400)
    
    # Get repository info from GitHub API
    response = requests.get(
        f'https://api.github.com/repos/{owner}/{repo_name}',
        headers={
            'Authorization': f'token {project.github_token}',
            'Accept': 'application/vnd.github.v3+json'
        }
    )
    
    if response.status_code == 200:
        repo_info = response.json()
        
        # Update project with repository info
        project.github_repo_id = repo_info['id']
        project.github_repo_name = repo_info['name']
        project.github_owner = repo_info['owner']['login']
        project.source_code_url = repo_info['html_url']
        project.current_branch = repo_info['default_branch']
        project.last_sync_at = timezone.now()
        project.save()
        
        return JsonResponse({
            'success': True,
            'repository': {
                'id': repo_info['id'],
                'name': repo_info['name'],
                'owner': repo_info['owner']['login'],
                'url': repo_info['html_url']
            }
        })
    
    return JsonResponse({'error': 'Repository not found or access denied'}, status=404)


@login_required
@require_http_methods(["GET"])
def github_get_status(request, project_id):
    """Get GitHub integration status for project"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    status_info = {
        'connected': project.is_github_connected(),
        'status': project.get_github_status(),
        'repository_url': project.get_github_repo_url(),
        'current_branch': project.current_branch,
        'last_sync': project.last_sync_at.isoformat() if project.last_sync_at else None,
    }
    
    if project.is_github_connected():
        # Get file status summary
        file_statuses = GitFileStatus.objects.filter(project=project)
        status_info['file_stats'] = {
            'total_files': file_statuses.count(),
            'modified': file_statuses.filter(git_status='modified').count(),
            'untracked': file_statuses.filter(git_status='untracked').count(),
            'staged': file_statuses.filter(git_status='staged').count(),
        }
    
    return JsonResponse(status_info)


@login_required
@require_http_methods(["POST"])
def github_sync_status(request, project_id):
    """Sync Git status for project files"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if not project.is_github_connected():
        return JsonResponse({'error': 'GitHub not connected'}, status=400)
    
    project_path = project.get_directory_path()
    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=400)
    
    try:
        # Change to project directory
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        # Run git status to get file statuses
        result = subprocess.run(['git', 'status', '--porcelain'], 
                              capture_output=True, text=True, timeout=30)
        
        if result.returncode != 0:
            return JsonResponse({'error': 'Git status command failed'}, status=400)
        
        # Clear existing file statuses
        GitFileStatus.objects.filter(project=project).delete()
        
        # Parse git status output
        updated_files = []
        for line in result.stdout.strip().split('\n'):
            if not line.strip():
                continue
                
            status_code = line[:2]
            file_path = line[3:].strip()
            
            # Map git status codes to our model
            if status_code.strip() == '??':
                git_status = 'untracked'
            elif status_code.strip() == 'M':
                git_status = 'modified'
            elif status_code.strip() == 'A':
                git_status = 'added'
            elif status_code.strip() == 'D':
                git_status = 'deleted'
            elif status_code.strip() == 'R':
                git_status = 'renamed'
            elif status_code.strip() == 'C':
                git_status = 'copied'
            else:
                git_status = 'modified'
            
            # Create GitFileStatus record
            file_status = GitFileStatus.objects.create(
                project=project,
                file_path=file_path,
                git_status=git_status
            )
            
            updated_files.append({
                'path': file_path,
                'status': git_status,
                'icon': file_status.get_status_icon(),
                'color': file_status.get_status_color()
            })
        
        # Update project sync time
        project.last_sync_at = timezone.now()
        project.save()
        
        return JsonResponse({
            'success': True,
            'files_updated': len(updated_files),
            'files': updated_files
        })
        
    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'Git command timed out'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Sync failed: {str(e)}'}, status=500)
    finally:
        os.chdir(original_cwd)


@login_required
@require_http_methods(["POST"])
def github_commit_files(request, project_id):
    """Commit staged files to Git"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if not project.is_github_connected():
        return JsonResponse({'error': 'GitHub not connected'}, status=400)
    
    commit_message = request.POST.get('commit_message', '').strip()
    if not commit_message:
        return JsonResponse({'error': 'Commit message required'}, status=400)
    
    project_path = project.get_directory_path()
    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=400)
    
    try:
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        # Configure git user if not set
        subprocess.run(['git', 'config', 'user.email', request.user.email], 
                      capture_output=True, timeout=10)
        subprocess.run(['git', 'config', 'user.name', request.user.get_full_name() or request.user.username], 
                      capture_output=True, timeout=10)
        
        # Add all modified files
        add_result = subprocess.run(['git', 'add', '.'], 
                                  capture_output=True, text=True, timeout=30)
        
        if add_result.returncode != 0:
            return JsonResponse({'error': 'Failed to stage files'}, status=400)
        
        # Commit changes
        commit_result = subprocess.run(['git', 'commit', '-m', commit_message], 
                                     capture_output=True, text=True, timeout=30)
        
        if commit_result.returncode != 0:
            if 'nothing to commit' in commit_result.stdout:
                return JsonResponse({'error': 'No changes to commit'}, status=400)
            else:
                return JsonResponse({'error': 'Commit failed'}, status=400)
        
        # Update file statuses
        GitFileStatus.objects.filter(project=project, git_status__in=['modified', 'added', 'untracked']).update(
            git_status='committed'
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Changes committed successfully',
            'commit_message': commit_message
        })
        
    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'Git command timed out'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Commit failed: {str(e)}'}, status=500)
    finally:
        os.chdir(original_cwd)


@login_required 
@require_http_methods(["POST"])
def github_push_changes(request, project_id):
    """Push committed changes to GitHub"""
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    if not project.is_github_connected():
        return JsonResponse({'error': 'GitHub not connected'}, status=400)
    
    project_path = project.get_directory_path()
    if not project_path or not project_path.exists():
        return JsonResponse({'error': 'Project directory not found'}, status=400)
    
    try:
        original_cwd = os.getcwd()
        os.chdir(project_path)
        
        # Push to current branch
        push_result = subprocess.run(['git', 'push', 'origin', project.current_branch], 
                                   capture_output=True, text=True, timeout=60)
        
        if push_result.returncode != 0:
            return JsonResponse({'error': f'Push failed: {push_result.stderr}'}, status=400)
        
        # Update sync time
        project.last_sync_at = timezone.now()
        project.save()
        
        return JsonResponse({
            'success': True,
            'message': f'Changes pushed to {project.current_branch} branch'
        })
        
    except subprocess.TimeoutExpired:
        return JsonResponse({'error': 'Push command timed out'}, status=500)
    except Exception as e:
        return JsonResponse({'error': f'Push failed: {str(e)}'}, status=500)
    finally:
        os.chdir(original_cwd)


@login_required
@require_http_methods(["GET"])
def github_list_repositories(request):
    """List user's GitHub repositories"""
    # This would require a valid GitHub token stored in user session or profile
    # For now, return empty list
    return JsonResponse({
        'repositories': [],
        'message': 'Connect to GitHub first to see your repositories'
    })