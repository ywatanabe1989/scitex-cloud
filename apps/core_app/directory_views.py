"""
SciTeX Cloud - Directory Management Views

This module provides API views for managing user directory structures,
project files, and directory operations.
"""

from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.conf import settings
import json
import os
import mimetypes
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

from .models import Project, Document
from .directory_manager import get_user_directory_manager


@login_required
@require_http_methods(["GET"])
def project_structure(request, project_id):
    """Get the complete directory structure for a project."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        
        # Ensure project directory exists
        project.ensure_directory()
        
        # Get project structure
        structure = project.get_file_structure()
        
        return JsonResponse({
            'status': 'success',
            'project_id': project_id,
            'project_name': project.name,
            'structure': structure,
            'storage_used_mb': project.get_storage_usage_mb(),
            'directory_created': project.directory_created
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting project structure: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def project_files(request, project_id):
    """List files in a project directory with optional category filtering."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        category = request.GET.get('category')  # e.g., 'documents', 'data', 'code'
        
        files = project.list_files(category)
        
        return JsonResponse({
            'status': 'success',
            'project_id': project_id,
            'category': category,
            'files': files,
            'file_count': len(files)
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error listing project files: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def upload_file(request, project_id):
    """Upload one or multiple files to a project directory, preserving directory structure."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        
        # Handle multiple files
        uploaded_files = request.FILES.getlist('files')
        if not uploaded_files:
            return JsonResponse({
                'status': 'error',
                'message': 'No files provided'
            }, status=400)
        
        category = request.POST.get('category', 'data')  # Default to data category
        preserve_structure = request.POST.get('preserve_structure', 'false').lower() == 'true'
        
        # Validate category
        valid_categories = ['config', 'data', 'scripts', 'docs', 'results', 'temp']
        if category not in valid_categories:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid category. Must be one of: {", ".join(valid_categories)}'
            }, status=400)
        
        # Store files in project directory
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        uploaded_files_info = []
        directories_created = set()
        
        for uploaded_file in uploaded_files:
            # Read file content
            file_content = uploaded_file.read()
            
            # Handle directory structure preservation
            if preserve_structure and hasattr(uploaded_file, 'name'):
                # Extract relative path for directory uploads
                relative_path = uploaded_file.name
                if '/' in relative_path or '\\' in relative_path:
                    # Normalize path separators
                    relative_path = relative_path.replace('\\', '/')
                    
                    # Determine target path within category
                    dir_parts = relative_path.split('/')
                    file_name = dir_parts[-1]
                    dir_structure = '/'.join(dir_parts[:-1]) if len(dir_parts) > 1 else ''
                    
                    # Create target directory path
                    target_dir = project_path / category
                    if dir_structure:
                        target_dir = target_dir / dir_structure
                        target_dir.mkdir(parents=True, exist_ok=True)
                        directories_created.add(str(target_dir.relative_to(project_path)))
                    
                    # Store file with preserved structure
                    target_file_path = target_dir / file_name
                    with open(target_file_path, 'wb') as f:
                        f.write(file_content)
                    
                    uploaded_files_info.append({
                        'file_name': file_name,
                        'file_path': str(target_file_path.relative_to(project_path)),
                        'file_size': len(file_content),
                        'category': category,
                        'relative_path': relative_path
                    })
                else:
                    # Single file, use existing store_file method
                    success, file_path = manager.store_file(project, file_content, uploaded_file.name, category)
                    
                    if success:
                        uploaded_files_info.append({
                            'file_name': uploaded_file.name,
                            'file_path': str(file_path.relative_to(manager.base_path)),
                            'file_size': len(file_content),
                            'category': category
                        })
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Failed to upload file: {uploaded_file.name}'
                        }, status=500)
            else:
                # Regular file upload without structure preservation
                success, file_path = manager.store_file(project, file_content, uploaded_file.name, category)
                
                if success:
                    uploaded_files_info.append({
                        'file_name': uploaded_file.name,
                        'file_path': str(file_path.relative_to(manager.base_path)),
                        'file_size': len(file_content),
                        'category': category
                    })
                else:
                    return JsonResponse({
                        'status': 'error',
                        'message': f'Failed to upload file: {uploaded_file.name}'
                    }, status=500)
        
        # Update project storage usage
        project.update_storage_usage()
        
        response_data = {
            'status': 'success',
            'message': f'{len(uploaded_files_info)} file(s) uploaded successfully',
            'files': uploaded_files_info
        }
        
        if directories_created:
            response_data['directories_created'] = list(directories_created)
            
        return JsonResponse(response_data)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error uploading files: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def download_file(request, project_id):
    """Download a file or entire project as ZIP from a project directory."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        file_path = request.GET.get('file')
        download_format = request.GET.get('format')  # 'zip' for full project download
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        # Full project ZIP download
        if download_format == 'zip':
            return _create_project_zip(project, project_path)
        
        # Individual file download
        if not file_path:
            return JsonResponse({
                'status': 'error',
                'message': 'File path or format is required'
            }, status=400)
        
        full_file_path = project_path / file_path
        
        # Security check: ensure file is within project directory
        if not str(full_file_path).startswith(str(project_path)):
            return JsonResponse({
                'status': 'error',
                'message': 'Access denied'
            }, status=403)
        
        if not full_file_path.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'File not found'
            }, status=404)
        
        # Determine content type
        content_type, _ = mimetypes.guess_type(str(full_file_path))
        if content_type is None:
            content_type = 'application/octet-stream'
        
        # Read and return file
        with open(full_file_path, 'rb') as f:
            response = HttpResponse(f.read(), content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename="{full_file_path.name}"'
            return response
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error downloading file: {str(e)}'
        }, status=500)


def _create_project_zip(project, project_path):
    """Create a ZIP file containing the entire project."""
    try:
        # Create temporary file for ZIP
        with tempfile.NamedTemporaryFile(delete=False, suffix='.zip') as temp_file:
            temp_path = temp_file.name
        
        # Create ZIP file
        with zipfile.ZipFile(temp_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in project_path.rglob('*'):
                if file_path.is_file():
                    # Calculate relative path for ZIP entry
                    arc_name = file_path.relative_to(project_path)
                    zipf.write(file_path, arc_name)
        
        # Read ZIP file and return as response
        with open(temp_path, 'rb') as f:
            zip_content = f.read()
        
        # Clean up temporary file
        os.unlink(temp_path)
        
        # Create filename with timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"{project.name}_{timestamp}.zip"
        
        response = HttpResponse(zip_content, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        return response
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_path' in locals() and os.path.exists(temp_path):
            os.unlink(temp_path)
        raise e


@login_required
@require_http_methods(["POST"])
def delete_file(request, project_id):
    """Delete a file from a project directory."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        data = json.loads(request.body)
        file_path = data.get('file_path')
        
        if not file_path:
            return JsonResponse({
                'status': 'error',
                'message': 'File path is required'
            }, status=400)
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        full_file_path = project_path / file_path
        
        # Security check: ensure file is within project directory
        if not str(full_file_path).startswith(str(project_path)):
            return JsonResponse({
                'status': 'error',
                'message': 'Access denied'
            }, status=403)
        
        if not full_file_path.exists():
            return JsonResponse({
                'status': 'error',
                'message': 'File not found'
            }, status=404)
        
        # Delete file
        full_file_path.unlink()
        
        # Update project storage usage
        project.update_storage_usage()
        
        return JsonResponse({
            'status': 'success',
            'message': 'File deleted successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error deleting file: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def create_directory(request, project_id):
    """Create a new directory in a project."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        data = json.loads(request.body)
        directory_path = data.get('path')
        
        if not directory_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Directory path is required'
            }, status=400)
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        full_dir_path = project_path / directory_path
        
        # Security check: ensure directory is within project directory
        if not str(full_dir_path).startswith(str(project_path)):
            return JsonResponse({
                'status': 'error',
                'message': 'Access denied'
            }, status=403)
        
        # Create directory
        full_dir_path.mkdir(parents=True, exist_ok=True)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Directory created successfully',
            'path': directory_path
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error creating directory: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def user_storage_usage(request):
    """Get storage usage statistics for the user."""
    try:
        manager = get_user_directory_manager(request.user)
        usage_stats = manager.get_storage_usage()
        
        # Get project-specific usage
        projects_usage = []
        for project in Project.objects.filter(owner=request.user, directory_created=True):
            project_usage = project.update_storage_usage()  # Update and get latest usage
            projects_usage.append({
                'project_id': project.id,
                'project_name': project.name,
                'storage_used': project_usage,
                'storage_used_mb': project.get_storage_usage_mb(),
                'last_activity': project.last_activity.isoformat() if project.last_activity else None
            })
        
        return JsonResponse({
            'status': 'success',
            'total_usage': usage_stats,
            'projects': projects_usage
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting storage usage: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def initialize_project_directory(request, project_id):
    """Manually initialize a project directory if it doesn't exist."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        
        success = project.ensure_directory()
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Project directory initialized successfully',
                'directory_path': project.data_location
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to initialize project directory'
            }, status=500)
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error initializing project directory: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def project_readme(request, project_id):
    """Get the project README content."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        readme_path = project_path / 'README.md'
        
        if readme_path.exists():
            with open(readme_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return JsonResponse({
                'status': 'success',
                'content': content,
                'file_exists': True
            })
        else:
            return JsonResponse({
                'status': 'success',
                'content': '',
                'file_exists': False,
                'message': 'README.md not found'
            })
            
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error reading README: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def update_project_readme(request, project_id):
    """Update the project README content."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        data = json.loads(request.body)
        content = data.get('content', '')
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        readme_path = project_path / 'README.md'
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        # Update project storage usage
        project.update_storage_usage()
        
        return JsonResponse({
            'status': 'success',
            'message': 'README updated successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating README: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def sync_with_github(request, project_id):
    """Initialize or sync project with GitHub repository."""
    import subprocess
    import re
    
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        data = json.loads(request.body)
        
        github_url = data.get('github_url')
        action = data.get('action', 'status')  # 'init', 'push', 'pull', 'clone', 'status'
        commit_message = data.get('commit_message', f'Update: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}')
        
        manager = get_user_directory_manager(request.user)
        project_path = manager.get_project_path(project)
        
        if not project_path:
            return JsonResponse({
                'status': 'error',
                'message': 'Project directory not found'
            }, status=404)
        
        # Validate GitHub URL if provided
        if github_url:
            github_pattern = r'^https://github\.com/[\w\-\.]+/[\w\-\.]+(?:\.git)?/?$'
            if not re.match(github_pattern, github_url):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid GitHub URL format. Use: https://github.com/username/repository'
                }, status=400)
        
        # Helper function to run git commands safely
        def run_git_command(cmd_args, cwd=project_path):
            try:
                result = subprocess.run(
                    cmd_args,
                    cwd=cwd,
                    capture_output=True,
                    text=True,
                    timeout=30,  # 30 second timeout
                    check=False
                )
                return result.returncode == 0, result.stdout, result.stderr
            except subprocess.TimeoutExpired:
                return False, "", "Command timed out"
            except Exception as e:
                return False, "", str(e)
        
        response_data = {
            'status': 'success',
            'action': action,
            'project_path': str(project_path)
        }
        
        # Create .gitignore if it doesn't exist
        gitignore_path = project_path / '.gitignore'
        if not gitignore_path.exists():
            gitignore_content = """# SciTeX Project .gitignore

# Temporary files
temp/cache/
temp/logs/
temp/tmp/

# Large data files (consider using Git LFS)
data/raw/*.csv
data/raw/*.xlsx
data/raw/*.h5
data/raw/*.hdf5

# Python cache
__pycache__/
*.pyc
*.pyo
*.pyd

# Jupyter Notebook checkpoints
.ipynb_checkpoints/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Model files (large)
data/models/*.pkl
data/models/*.joblib
data/models/*.h5

# Log files
*.log
"""
            with open(gitignore_path, 'w') as f:
                f.write(gitignore_content)
            response_data['gitignore_created'] = True
        
        # Check if git is available
        success, _, error = run_git_command(['git', '--version'])
        if not success:
            return JsonResponse({
                'status': 'error',
                'message': 'Git is not available on the server. Please contact administrator.'
            }, status=500)
        
        # Execute action
        if action == 'status':
            # Check git status
            success, output, error = run_git_command(['git', 'status', '--porcelain'])
            if success:
                response_data['message'] = 'Git status retrieved successfully'
                response_data['git_status'] = output.strip() if output else 'Working directory clean'
                
                # Get current branch
                success_branch, branch_output, _ = run_git_command(['git', 'branch', '--show-current'])
                if success_branch:
                    response_data['current_branch'] = branch_output.strip()
                
                # Get remote URL
                success_remote, remote_output, _ = run_git_command(['git', 'remote', 'get-url', 'origin'])
                if success_remote:
                    response_data['remote_url'] = remote_output.strip()
            else:
                response_data['message'] = 'Not a git repository'
                response_data['git_status'] = 'Not initialized'
        
        elif action == 'init':
            # Initialize git repository
            success, output, error = run_git_command(['git', 'init'])
            if success:
                response_data['message'] = 'Git repository initialized successfully'
                response_data['output'] = output
                
                # Set up initial commit
                run_git_command(['git', 'add', '.'])
                success_commit, commit_output, commit_error = run_git_command([
                    'git', 'commit', '-m', f'Initial commit: {project.name}'
                ])
                
                if success_commit:
                    response_data['initial_commit'] = 'Created'
                
                # Add remote if URL provided
                if github_url:
                    success_remote, remote_output, remote_error = run_git_command([
                        'git', 'remote', 'add', 'origin', github_url
                    ])
                    if success_remote:
                        response_data['remote_added'] = github_url
                    else:
                        response_data['remote_error'] = remote_error
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to initialize git repository: {error}'
                }, status=500)
        
        elif action == 'push':
            # Add, commit, and push changes
            success_add, _, add_error = run_git_command(['git', 'add', '.'])
            if not success_add:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to stage files: {add_error}'
                }, status=500)
            
            success_commit, commit_output, commit_error = run_git_command([
                'git', 'commit', '-m', commit_message
            ])
            
            if success_commit:
                response_data['commit_created'] = commit_message
                
                # Try to push
                success_push, push_output, push_error = run_git_command(['git', 'push'])
                if success_push:
                    response_data['message'] = 'Changes pushed to GitHub successfully'
                    response_data['push_output'] = push_output
                else:
                    # Try push with upstream
                    success_push_upstream, push_upstream_output, push_upstream_error = run_git_command([
                        'git', 'push', '-u', 'origin', 'main'
                    ])
                    if success_push_upstream:
                        response_data['message'] = 'Changes pushed to GitHub successfully (upstream set)'
                        response_data['push_output'] = push_upstream_output
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': f'Failed to push: {push_error or push_upstream_error}',
                            'suggestion': 'Make sure you have push permissions and the remote repository exists'
                        }, status=400)
            elif 'nothing to commit' in commit_error:
                response_data['message'] = 'No changes to commit'
                response_data['commit_status'] = 'Nothing to commit, working tree clean'
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to commit: {commit_error}'
                }, status=500)
        
        elif action == 'pull':
            # Pull changes from remote
            success, output, error = run_git_command(['git', 'pull'])
            if success:
                response_data['message'] = 'Successfully pulled changes from GitHub'
                response_data['pull_output'] = output
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': f'Failed to pull: {error}',
                    'suggestion': 'Make sure you have a remote repository configured'
                }, status=400)
        
        elif action == 'clone' and github_url:
            # Clone repository (this will replace current contents)
            return JsonResponse({
                'status': 'error',
                'message': 'Clone operation not supported for existing projects. Use pull instead.'
            }, status=400)
        
        else:
            return JsonResponse({
                'status': 'error',
                'message': f'Invalid action: {action}'
            }, status=400)
        
        return JsonResponse(response_data)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error with GitHub sync: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["GET"])
def get_script_executions(request, project_id):
    """Get execution history for project scripts."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        script_name = request.GET.get('script')
        
        manager = get_user_directory_manager(request.user)
        executions = manager.get_script_executions(project, script_name)
        
        return JsonResponse({
            'status': 'success',
            'project_id': project_id,
            'script_name': script_name,
            'executions': executions
        })
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error getting script executions: {str(e)}'
        }, status=500)


@login_required
@require_http_methods(["POST"])
def execute_script(request, project_id):
    """Execute a script with tracking."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        data = json.loads(request.body)
        script_name = data.get('script_name')
        
        if not script_name:
            return JsonResponse({
                'status': 'error',
                'message': 'Script name is required'
            }, status=400)
        
        manager = get_user_directory_manager(request.user)
        
        # Create execution tracker
        success, execution_dir = manager.create_script_execution_tracker(project, script_name)
        
        if success:
            return JsonResponse({
                'status': 'success',
                'message': 'Script execution tracking started',
                'execution_id': execution_dir.name,
                'execution_path': str(execution_dir.relative_to(manager.base_path)),
                'instructions': f'Your script can write outputs to: {execution_dir}'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Failed to create execution tracker'
            }, status=500)
        
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Error executing script: {str(e)}'
        }, status=500)