#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 16:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/apps/core_app/api_views.py
# ----------------------------------------
import os
__FILE__ = (
    "./apps/core_app/api_views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
API Views for Core App
Implements RESTful endpoints for Document and Project management
Following TDD principles and clean code guidelines
"""

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import transaction

from ..models import Project, UserProfile
# from apps.document_app.models import Document  # Removed - document_app not installed
import logging
import re
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """Base API view with common functionality"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def json_response(self, data, status=200):
        """Helper method for JSON responses"""
        return JsonResponse(data, status=status)
    
    def error_response(self, message, status=400):
        """Helper method for error responses"""
        return JsonResponse({
            'success': False,
            'error': message
        }, status=status)
    
    def success_response(self, data=None, status=200):
        """Helper method for success responses"""
        response_data = {'success': True}
        if data:
            response_data.update(data)
        return JsonResponse(response_data, status=status)


class DocumentAPIView(BaseAPIView):
    """
    API endpoints for Document CRUD operations
    
    GET /api/v1/documents/ - List user documents
    POST /api/v1/documents/ - Create new document
    GET /api/v1/documents/{id}/ - Get specific document
    PUT /api/v1/documents/{id}/ - Update document
    DELETE /api/v1/documents/{id}/ - Delete document
    """
    
    def get(self, request, document_id=None):
        """Retrieve document(s)"""
        try:
            if document_id:
                # Get specific document
                try:
                    document = Document.objects.get(
                        id=document_id, 
                        owner=request.user
                    )
                    return self.success_response({
                        'document': self._serialize_document(document)
                    })
                except Document.DoesNotExist:
                    return self.error_response("Document not found", 404)
            else:
                # List documents with pagination and filtering
                documents = Document.objects.filter(owner=request.user)
                
                # Filter by document type
                doc_type = request.GET.get('type')
                if doc_type:
                    documents = documents.filter(document_type=doc_type)
                
                # Search functionality
                search = request.GET.get('search')
                if search:
                    documents = documents.filter(
                        title__icontains=search
                    )
                
                # Pagination
                page = request.GET.get('page', 1)
                paginator = Paginator(documents.order_by('-updated_at'), 10)
                page_obj = paginator.get_page(page)
                
                return self.success_response({
                    'documents': [
                        self._serialize_document(doc) 
                        for doc in page_obj
                    ],
                    'pagination': {
                        'current_page': page_obj.number,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                    }
                })
                
        except Exception as e:
            return self.error_response(f"Error retrieving documents: {str(e)}", 500)
    
    def post(self, request):
        """Create new document"""
        try:
            # Parse request data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Validate required fields
            title = data.get('title', '').strip()
            content = data.get('content', '').strip()
            
            if not title:
                return self.error_response("Title is required")
            
            if not content:
                return self.error_response("Content is required")
            
            # Create document
            with transaction.atomic():
                document = Document.objects.create(
                    title=title,
                    content=content,
                    document_type=data.get('document_type', 'note'),
                    tags=data.get('tags', ''),
                    is_public=data.get('is_public', False),
                    owner=request.user
                )
            
            return self.success_response({
                'document': self._serialize_document(document)
            }, status=201)
            
        except Exception as e:
            return self.error_response(f"Error creating document: {str(e)}", 500)
    
    def put(self, request, document_id):
        """Update existing document"""
        try:
            # Get document
            try:
                document = Document.objects.get(
                    id=document_id,
                    owner=request.user
                )
            except Document.DoesNotExist:
                return self.error_response("Document not found", 404)
            
            # Parse request data
            data = json.loads(request.body)
            
            # Update fields
            if 'title' in data:
                title = data['title'].strip()
                if not title:
                    return self.error_response("Title cannot be empty")
                document.title = title
            
            if 'content' in data:
                content = data['content'].strip()
                if not content:
                    return self.error_response("Content cannot be empty")
                document.content = content
            
            if 'document_type' in data:
                document.document_type = data['document_type']
            
            if 'tags' in data:
                document.tags = data['tags']
            
            if 'is_public' in data:
                document.is_public = data['is_public']
            
            document.save()
            
            return self.success_response({
                'document': self._serialize_document(document)
            })
            
        except Exception as e:
            return self.error_response(f"Error updating document: {str(e)}", 500)
    
    def delete(self, request, document_id):
        """Delete document"""
        try:
            try:
                document = Document.objects.get(
                    id=document_id,
                    owner=request.user
                )
            except Document.DoesNotExist:
                return self.error_response("Document not found", 404)
            
            document.delete()
            
            return self.success_response({
                'message': 'Document deleted successfully'
            })
            
        except Exception as e:
            return self.error_response(f"Error deleting document: {str(e)}", 500)
    
    def _serialize_document(self, document):
        """Serialize document for JSON response"""
        return {
            'id': document.id,
            'title': document.title,
            'content': document.content,
            'document_type': document.document_type,
            'tags': document.tags,
            'tags_list': document.get_tags_list(),
            'is_public': document.is_public,
            'created_at': document.created_at.isoformat(),
            'updated_at': document.updated_at.isoformat(),
            'owner': {
                'id': document.owner.id,
                'username': document.owner.username
            }
        }


class ProjectAPIView(BaseAPIView):
    """
    API endpoints for Project CRUD operations
    
    GET /api/v1/projects/ - List user projects
    POST /api/v1/projects/ - Create new project
    GET /api/v1/projects/{id}/ - Get specific project  
    PUT /api/v1/projects/{id}/ - Update project
    DELETE /api/v1/projects/{id}/ - Delete project
    """
    
    def get(self, request, project_id=None):
        """Retrieve project(s)"""
        try:
            if project_id:
                # Get specific project
                try:
                    project = Project.objects.get(
                        id=project_id,
                        owner=request.user
                    )
                    return self.success_response({
                        'project': self._serialize_project(project)
                    })
                except Project.DoesNotExist:
                    return self.error_response("Project not found", 404)
            else:
                # List projects with filtering
                projects = Project.objects.filter(owner=request.user)
                
                # Filter by status
                status = request.GET.get('status')
                if status:
                    projects = projects.filter(status=status)
                
                # Pagination
                page = request.GET.get('page', 1)
                paginator = Paginator(projects.order_by('-updated_at'), 10)
                page_obj = paginator.get_page(page)
                
                return self.success_response({
                    'projects': [
                        self._serialize_project(proj) 
                        for proj in page_obj
                    ],
                    'pagination': {
                        'current_page': page_obj.number,
                        'total_pages': paginator.num_pages,
                        'total_count': paginator.count,
                        'has_next': page_obj.has_next(),
                        'has_previous': page_obj.has_previous(),
                    }
                })
                
        except Exception as e:
            return self.error_response(f"Error retrieving projects: {str(e)}", 500)
    
    def post(self, request, project_id=None):
        """Create new project with enhanced SciTeX features"""
        try:
            # Parse request data
            if request.content_type == 'application/json':
                data = json.loads(request.body)
            else:
                data = request.POST
            
            # Validate required fields
            name = data.get('name', '').strip()
            description = data.get('description', '').strip()
            hypotheses = data.get('hypotheses', '').strip()
            
            if not name:
                return self.error_response("Project name is required")
            
            # Validate and ensure unique project name
            original_name = name
            if not Project.validate_name_uniqueness(name, request.user):
                # Auto-generate unique name or return error based on preference
                auto_fix = data.get('auto_fix_name', True)
                if auto_fix:
                    name = Project.generate_unique_name(name, request.user)
                    logger.info(f"Auto-generated unique project name: {original_name} -> {name}")
                else:
                    return self.error_response(
                        f"Project name '{name}' already exists. Please choose a different name.",
                        status=409  # Conflict status code
                    )
            
            # Make description and hypotheses optional with defaults
            if not description:
                description = f"Research project: {name}"
            
            if not hypotheses:
                hypotheses = "Research hypotheses to be defined"
            
            # Check if this is a GitHub clone request
            source_code_url = data.get('source_code_url', '').strip()
            is_clone_request = bool(source_code_url)
            
            # Create project with enhanced fields
            with transaction.atomic():
                try:
                    project = Project.objects.create(
                        name=name,
                        description=description,
                        hypotheses=hypotheses,
                        source_code_url=source_code_url,
                        status=data.get('status', 'planning'),
                        progress=data.get('progress', 0),
                        owner=request.user
                    )
                except Exception as e:
                    if 'unique_together' in str(e).lower() or 'unique constraint' in str(e).lower():
                        return self.error_response(
                            f"Project name '{name}' already exists. Please choose a different name.",
                            status=409
                        )
                    raise  # Re-raise other exceptions
                
                # Add deadline if provided
                deadline = data.get('deadline')
                if deadline:
                    from django.utils.dateparse import parse_datetime
                    project.deadline = parse_datetime(deadline)
                    project.save()
                
                # Handle GitHub clone or create default structure
                if is_clone_request:
                    success = self._clone_from_github(project, source_code_url, request.user)
                    if not success:
                        # If clone fails, create default structure as fallback
                        project.ensure_directory()
                        self._create_default_directories(project)
                        return self.error_response("Failed to clone repository, created empty project instead")
                else:
                    # Create default directory structure if requested
                    create_default_structure = data.get('create_default_structure', True)
                    if create_default_structure:
                        success = project.ensure_directory()
                        if success:
                            # Create the standard research directory structure
                            self._create_default_directories(project)
            
            # Determine success message based on creation type
            if is_clone_request:
                message = f'Project cloned successfully from {source_code_url}'
            else:
                message = 'Project created successfully with default directory structure'
            
            # Add name change notification if name was auto-generated
            if name != original_name:
                message += f" (Name changed from '{original_name}' to '{name}' to ensure uniqueness)"
            
            response_data = {
                'project': self._serialize_project(project),
                'message': message
            }
            
            # Include name change information for frontend handling
            if name != original_name:
                response_data['name_changed'] = True
                response_data['original_name'] = original_name
                response_data['final_name'] = name
            
            return self.success_response(response_data, status=201)
            
        except Exception as e:
            return self.error_response(f"Error creating project: {str(e)}", 500)
    
    def _create_default_directories(self, project):
        """Create default directory structure for research project"""
        try:
            from .directory_manager import get_user_directory_manager
            manager = get_user_directory_manager(project.owner)
            
            # Standard research project directories
            directories = [
                'config',
                'data/raw',
                'data/processed', 
                'data/figures',
                'data/models',
                'scripts',
                'docs/manuscripts',
                'docs/notes',
                'docs/references',
                'results/outputs',
                'results/reports',
                'results/analysis',
                'temp/cache',
                'temp/logs',
                'temp/tmp'
            ]
            
            project_path = project.get_directory_path()
            if project_path:
                for directory in directories:
                    dir_path = project_path / directory
                    dir_path.mkdir(parents=True, exist_ok=True)
                    
                    # Create placeholder README files
                    readme_path = dir_path / 'README.md'
                    if not readme_path.exists():
                        readme_content = self._get_readme_content(directory)
                        readme_path.write_text(readme_content)
            
            return True
        except Exception as e:
            print(f"Error creating default directories: {e}")
            return False
    
    def _get_readme_content(self, directory):
        """Get README content for specific directory"""
        readme_contents = {
            'config': '# Configuration Files\n\nStore your project configuration files here:\n- Settings files\n- Environment variables\n- API keys (use .env files)\n',
            'data/raw': '# Raw Data\n\nStore original, unprocessed data files here:\n- Original datasets\n- Raw experimental data\n- Downloaded files\n',
            'data/processed': '# Processed Data\n\nStore cleaned and processed datasets here:\n- Cleaned CSV files\n- Preprocessed data\n- Feature engineered datasets\n',
            'data/figures': '# Figures and Plots\n\nStore generated visualizations here:\n- Charts and graphs\n- Statistical plots\n- Publication-ready figures\n',
            'data/models': '# Models\n\nStore trained models and model artifacts here:\n- Saved model files\n- Model weights\n- Model configurations\n',
            'scripts': '# Source Code\n\nStore your analysis and processing scripts here:\n- Python/R analysis scripts\n- Data processing pipelines\n- Utility functions\n',
            'docs/manuscripts': '# Manuscripts\n\nStore draft manuscripts and papers here:\n- LaTeX documents\n- Word documents\n- Manuscript drafts\n',
            'docs/notes': '# Research Notes\n\nStore research notes and documentation here:\n- Meeting notes\n- Literature reviews\n- Research logs\n',
            'docs/references': '# References\n\nStore reference materials here:\n- Bibliography files\n- PDF papers\n- Citation databases\n',
            'results/outputs': '# Analysis Outputs\n\nStore analysis results here:\n- Statistical results\n- Model outputs\n- Generated reports\n',
            'results/reports': '# Reports\n\nStore generated reports here:\n- HTML reports\n- PDF summaries\n- Analysis reports\n',
            'results/analysis': '# Analysis Files\n\nStore analysis notebooks and files here:\n- Jupyter notebooks\n- R Markdown files\n- Analysis scripts\n',
            'temp/cache': '# Cache Files\n\nTemporary cache files (can be deleted safely)\n',
            'temp/logs': '# Log Files\n\nApplication and processing log files\n',
            'temp/tmp': '# Temporary Files\n\nTemporary working files (can be deleted safely)\n'
        }
        
        return readme_contents.get(directory, f'# {directory.title()}\n\nDirectory for {directory} files.\n')
    
    def _clone_from_github(self, project, repo_url, user):
        """Clone repository from GitHub/Git URL using SSH or HTTPS"""
        try:
            import subprocess
            import re
            import shutil
            from pathlib import Path
            
            # Normalize URL formats
            normalized_url = self._normalize_git_url(repo_url)
            if not normalized_url:
                logger.error(f"Invalid Git URL format: {repo_url}")
                return False
            
            # Check if this is an SSH URL and user has SSH keys
            is_ssh_url = normalized_url.startswith('git@')
            ssh_manager = None
            
            if is_ssh_url:
                from apps.api.v1.auth.ssh_key_manager import SSHKeyManager
                ssh_manager = SSHKeyManager(user)
                
                if not ssh_manager.has_ssh_key():
                    logger.warning(f"SSH URL provided but user {user.username} has no SSH key")
                    return False
            
            # Ensure project directory exists
            project.ensure_directory()
            project_path = project.get_directory_path()
            
            if not project_path:
                logger.error("Failed to create project directory")
                return False
            
            # Clear directory if it exists (keep it clean for cloning)
            if project_path.exists():
                import shutil
                shutil.rmtree(project_path)
                project_path.mkdir(parents=True, exist_ok=True)
            
            # Prepare environment and command
            env = {}
            if is_ssh_url and ssh_manager:
                env = ssh_manager.get_git_env()
            
            clone_cmd = ['git', 'clone', normalized_url, str(project_path)]
            
            logger.info(f"Cloning repository: {normalized_url} to {project_path}")
            
            result = subprocess.run(
                clone_cmd,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env={**os.environ, **env}
            )
            
            if result.returncode == 0:
                logger.info(f"Successfully cloned repository to {project_path}")
                
                # Create additional SciTeX directories if they don't exist
                self._ensure_scitex_directories(project_path)
                
                return True
            else:
                logger.error(f"Git clone failed: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            logger.error("Git clone operation timed out")
            return False
        except Exception as e:
            logger.error(f"Error cloning repository: {str(e)}")
            return False
    
    def _normalize_git_url(self, url):
        """Normalize Git URL to proper format"""
        url = url.strip()
        
        # Handle SSH format: git@github.com:user/repo.git
        ssh_pattern = r'^git@([^:]+):([^/]+)/(.+?)(?:\.git)?/?$'
        ssh_match = re.match(ssh_pattern, url)
        if ssh_match:
            host, user, repo = ssh_match.groups()
            return f"git@{host}:{user}/{repo}.git"
        
        # Handle HTTPS format: https://github.com/user/repo
        https_pattern = r'^https://([^/]+)/([^/]+)/(.+?)(?:\.git)?/?$'
        https_match = re.match(https_pattern, url)
        if https_match:
            host, user, repo = https_match.groups()
            return f"https://{host}/{user}/{repo}.git"
        
        # If it already looks like a proper git URL, return as-is
        if url.endswith('.git'):
            return url
        
        return None
    
    def _ensure_scitex_directories(self, project_path):
        """Ensure SciTeX research directories exist alongside cloned content"""
        scitex_dirs = [
            'data/raw', 'data/processed', 'data/figures', 'data/models',
            'results/outputs', 'results/reports', 'results/analysis',
            'docs/manuscripts', 'docs/notes', 'docs/references',
            'temp/cache', 'temp/logs', 'temp/tmp'
        ]
        
        for directory in scitex_dirs:
            dir_path = project_path / directory
            if not dir_path.exists():
                dir_path.mkdir(parents=True, exist_ok=True)
                
                # Add README if it doesn't exist
                readme_path = dir_path / 'README.md'
                if not readme_path.exists():
                    readme_content = self._get_readme_content(directory)
                    readme_path.write_text(readme_content)
    
    def put(self, request, project_id):
        """Update existing project"""
        try:
            # Get project
            try:
                project = Project.objects.get(
                    id=project_id,
                    owner=request.user
                )
            except Project.DoesNotExist:
                return self.error_response("Project not found", 404)
            
            # Parse request data
            data = json.loads(request.body)
            
            # Update fields
            if 'name' in data:
                name = data['name'].strip()
                if not name:
                    return self.error_response("Project name cannot be empty")
                project.name = name
            
            if 'description' in data:
                description = data['description'].strip()
                if not description:
                    return self.error_response("Project description cannot be empty")
                project.description = description
            
            if 'hypotheses' in data:
                hypotheses = data['hypotheses'].strip()
                if not hypotheses:
                    return self.error_response("Research hypotheses cannot be empty")
                project.hypotheses = hypotheses
            
            if 'source_code_url' in data:
                project.source_code_url = data['source_code_url'].strip()
            
            if 'status' in data:
                project.status = data['status']
            
            if 'progress' in data:
                progress = int(data['progress'])
                if 0 <= progress <= 100:
                    project.progress = progress
                else:
                    return self.error_response("Progress must be between 0 and 100")
            
            if 'deadline' in data:
                from django.utils.dateparse import parse_datetime
                project.deadline = parse_datetime(data['deadline'])
            
            project.save()
            
            return self.success_response({
                'project': self._serialize_project(project)
            })
            
        except Exception as e:
            return self.error_response(f"Error updating project: {str(e)}", 500)
    
    def delete(self, request, project_id):
        """Delete project"""
        try:
            try:
                project = Project.objects.get(
                    id=project_id,
                    owner=request.user
                )
            except Project.DoesNotExist:
                return self.error_response("Project not found", 404)
            
            project.delete()
            
            return self.success_response({
                'message': 'Project deleted successfully'
            })
            
        except Exception as e:
            return self.error_response(f"Error deleting project: {str(e)}", 500)
    
    def _serialize_project(self, project):
        """Serialize project for JSON response"""
        return {
            'id': project.id,
            'name': project.name,
            'description': project.description,
            'hypotheses': project.hypotheses,
            'source_code_url': project.source_code_url,
            'status': project.status,
            'progress': project.progress,
            'directory_created': project.directory_created,
            'storage_used_mb': project.get_storage_usage_mb(),
            'created_at': project.created_at.isoformat(),
            'updated_at': project.updated_at.isoformat(),
            'last_activity': project.last_activity.isoformat() if project.last_activity else None,
            'deadline': project.deadline.isoformat() if project.deadline else None,
            'owner': {
                'id': project.owner.id,
                'username': project.owner.username
            },
            'collaborators': [
                {
                    'id': user.id,
                    'username': user.username
                }
                for user in project.collaborators.all()
            ]
        }


class UserStatsAPIView(BaseAPIView):
    """API endpoint for user statistics"""
    
    def get(self, request):
        """Get user statistics"""
        try:
            user = request.user
            
            # Calculate statistics
            stats = {
                'documents': {
                    'total': Document.objects.filter(owner=user).count(),
                    'public': Document.objects.filter(owner=user, is_public=True).count(),
                    'by_type': {}
                },
                'projects': {
                    'total': Project.objects.filter(owner=user).count(),
                    'by_status': {}
                }
            }
            
            # Document statistics by type
            for doc_type, _ in Document.DOCUMENT_TYPES:
                stats['documents']['by_type'][doc_type] = Document.objects.filter(
                    owner=user, document_type=doc_type
                ).count()
            
            # Project statistics by status
            for status, _ in Project.PROJECT_STATUS:
                stats['projects']['by_status'][status] = Project.objects.filter(
                    owner=user, status=status
                ).count()
            
            return self.success_response({
                'stats': stats
            })
            
        except Exception as e:
            return self.error_response(f"Error retrieving statistics: {str(e)}", 500)


class UserProfileAPIView(BaseAPIView):
    """
    API endpoint for User Profile management
    
    GET /api/v1/profile/ - Get user profile
    PUT /api/v1/profile/ - Update user profile
    """
    
    def get(self, request):
        """Get user profile"""
        try:
            user = request.user
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            return self.success_response({
                'profile': self._serialize_profile(profile)
            })
            
        except Exception as e:
            return self.error_response(f"Error retrieving profile: {str(e)}", 500)
    
    def put(self, request):
        """Update user profile"""
        try:
            user = request.user
            data = json.loads(request.body)
            
            # Get or create profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update User model fields
            user_fields = ['first_name', 'last_name', 'email']
            for field in user_fields:
                if field in data:
                    value = data[field].strip() if data[field] else ''
                    setattr(user, field, value)
            
            # Validate email format
            if 'email' in data:
                from django.core.validators import validate_email
                from django.core.exceptions import ValidationError
                try:
                    validate_email(data['email'])
                except ValidationError:
                    return self.error_response("Invalid email format")
            
            # Update UserProfile fields
            profile_fields = [
                'bio', 'institution', 'research_interests', 'website',
                'orcid', 'academic_title', 'department',
                'google_scholar', 'linkedin', 'researchgate', 'twitter',
                'profile_visibility', 'is_public', 'show_email', 
                'allow_collaboration', 'allow_messages'
            ]
            
            for field in profile_fields:
                if field in data:
                    value = data[field]
                    
                    # Special handling for boolean fields
                    if field in ['is_public', 'show_email', 'allow_collaboration', 'allow_messages']:
                        value = bool(value)
                    
                    # Special handling for ORCID validation
                    if field == 'orcid' and value:
                        if not self._validate_orcid(value):
                            return self.error_response("Invalid ORCID format. Use format: 0000-0000-0000-0000")
                    
                    # Special handling for Twitter handle
                    if field == 'twitter' and value:
                        value = value.lstrip('@')  # Remove @ if present
                    
                    setattr(profile, field, value)
            
            # Save both models
            with transaction.atomic():
                user.save()
                profile.save()
            
            return self.success_response({
                'profile': self._serialize_profile(profile),
                'message': 'Profile updated successfully'
            })
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON data")
        except Exception as e:
            return self.error_response(f"Error updating profile: {str(e)}", 500)
    
    def patch(self, request):
        """Partially update user profile (for privacy settings)"""
        try:
            user = request.user
            data = json.loads(request.body)
            
            # Get profile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Update only privacy-related fields
            privacy_fields = ['is_public', 'show_email', 'allow_messages', 'publicProfile', 'showEmail', 'allowMessages']
            
            for field in privacy_fields:
                if field in data:
                    # Handle camelCase fields from frontend
                    if field == 'publicProfile':
                        profile.is_public = bool(data[field])
                    elif field == 'showEmail':
                        profile.show_email = bool(data[field])
                    elif field == 'allowMessages':
                        profile.allow_messages = bool(data[field])
                    else:
                        setattr(profile, field, bool(data[field]))
            
            profile.save()
            
            return self.success_response({
                'message': 'Privacy settings updated'
            })
            
        except json.JSONDecodeError:
            return self.error_response("Invalid JSON data")
        except Exception as e:
            return self.error_response(f"Error updating privacy settings: {str(e)}", 500)
    
    def _validate_orcid(self, orcid):
        """Validate ORCID format"""
        import re
        pattern = r'^[0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X]$'
        return bool(re.match(pattern, orcid))
    
    def _serialize_profile(self, profile):
        """Serialize profile for JSON response"""
        return {
            'user': {
                'id': profile.user.id,
                'username': profile.user.username,
                'first_name': profile.user.first_name,
                'last_name': profile.user.last_name,
                'email': profile.user.email,
                'date_joined': profile.user.date_joined.isoformat(),
            },
            'bio': profile.bio,
            'institution': profile.institution,
            'research_interests': profile.research_interests,
            'website': profile.website,
            'orcid': profile.orcid,
            'academic_title': profile.academic_title,
            'department': profile.department,
            'google_scholar': profile.google_scholar,
            'linkedin': profile.linkedin,
            'researchgate': profile.researchgate,
            'twitter': profile.twitter,
            'profile_visibility': profile.profile_visibility,
            'show_email': profile.show_email,
            'allow_collaboration': profile.allow_collaboration,
            'created_at': profile.created_at.isoformat(),
            'updated_at': profile.updated_at.isoformat(),
            'display_name': profile.get_display_name(),
            'full_title': profile.get_full_title(),
            'is_complete': profile.is_complete(),
            'social_links': profile.get_social_links(),
        }


# Function-based view wrappers for URL routing
@csrf_exempt
@login_required
def document_api(request, document_id=None):
    """Document API endpoint wrapper"""
    view = DocumentAPIView()
    return view.dispatch(request, document_id=document_id)


@csrf_exempt
@login_required
def project_api(request, project_id=None):
    """Project API endpoint wrapper"""
    view = ProjectAPIView()
    return view.dispatch(request, project_id=project_id)


@csrf_exempt
@login_required
def user_stats_api(request):
    """User statistics API endpoint wrapper"""
    view = UserStatsAPIView()
    return view.dispatch(request)


@csrf_exempt
@login_required
def user_profile_api(request):
    """User profile API endpoint wrapper"""
    view = UserProfileAPIView()
    return view.dispatch(request)

# File System API Views for React Complex Tree Dashboard

@login_required
@require_http_methods(["GET"])
def file_tree_api(request):
    """
    API endpoint for React Complex Tree - returns real file system structure for current user.
    Scans actual project directories and returns real files and folders.
    """
    try:
        import os
        from pathlib import Path
        from django.conf import settings
        
        user = request.user
        file_tree = {}
        
        # Root node
        file_tree["root"] = {
            "id": "root",
            "name": f"{user.username}",
            "type": "folder",
            "children": ["projects"],
            "isExpanded": True,
            "canRename": False,
            "canMove": False
        }
        
        # Projects root
        file_tree["projects"] = {
            "id": "projects",
            "name": "projects", 
            "type": "folder",
            "children": [],
            "isExpanded": True,
            "canRename": False,
            "canMove": False
        }
        
        # Get user's actual projects (all active statuses)
        user_projects = Project.objects.filter(
            owner=user, 
            status__in=['active', 'planning']
        ).order_by('name')
        
        project_children = []
        
        for project in user_projects:
            project_id = f"project_{project.id}"
            project_children.append(project_id)
            
            # Get actual project directory
            project_path = project.get_directory_path()
            
            if project_path and project_path.exists():
                # Scan real directory structure
                children = []
                project_items = _scan_directory(project_path, project_id, project.id, file_tree)
                children.extend(project_items)
                
                file_tree[project_id] = {
                    "id": project_id,
                    "name": project.name,
                    "type": "folder",
                    "children": children,
                    "isExpanded": False,
                    "projectId": project.id,
                    "description": project.description or "",
                    "created": project.created_at.isoformat(),
                    "modified": project.updated_at.isoformat(),
                    "path": str(project_path)
                }
            else:
                # Project directory doesn't exist, show empty
                file_tree[project_id] = {
                    "id": project_id,
                    "name": f"{project.name} (not created)",
                    "type": "folder",
                    "children": [],
                    "isExpanded": False,
                    "projectId": project.id,
                    "description": "Project directory not created yet",
                    "created": project.created_at.isoformat(),
                    "modified": project.updated_at.isoformat()
                }
        
        # Update projects children list
        file_tree["projects"]["children"] = project_children
        
        return JsonResponse({
            "success": True,
            "fileTree": file_tree,
            "rootId": "root",
            "expandedItems": ["root", "projects"],
            "selectedItems": [],
            "focusedItem": None
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def _scan_directory(directory_path, parent_id, project_id, file_tree):
    """
    Recursively scan directory and populate file_tree with real files and folders.
    Returns list of child IDs.
    """
    try:
        from pathlib import Path
        import mimetypes
        
        children = []
        
        # Sort entries: directories first, then files
        entries = sorted(directory_path.iterdir(), key=lambda x: (x.is_file(), x.name.lower()))
        
        for entry in entries:
            # Skip hidden files and system files
            if entry.name.startswith('.'):
                continue
                
            # Generate unique ID
            entry_id = f"{parent_id}_{entry.name}".replace(' ', '_').replace('.', '_dot_')
            children.append(entry_id)
            
            if entry.is_dir():
                # Recursively scan subdirectory
                subchildren = _scan_directory(entry, entry_id, project_id, file_tree)
                
                file_tree[entry_id] = {
                    "id": entry_id,
                    "name": entry.name,
                    "type": "folder",
                    "children": subchildren,
                    "isExpanded": False,
                    "projectId": project_id,
                    "path": str(entry),
                    "modified": entry.stat().st_mtime
                }
            else:
                # File entry
                stat_info = entry.stat()
                
                # Determine file type
                file_type = _get_file_type(entry.name, entry.suffix)
                
                file_tree[entry_id] = {
                    "id": entry_id,
                    "name": entry.name,
                    "type": file_type,
                    "size": stat_info.st_size,
                    "modified": stat_info.st_mtime,
                    "projectId": project_id,
                    "path": str(entry)
                }
        
        return children
        
    except Exception as e:
        print(f"Error scanning directory {directory_path}: {e}")
        return []


def _get_file_type(filename, suffix):
    """Determine file type based on extension"""
    suffix = suffix.lower()
    
    type_map = {
        '.py': 'python',
        '.js': 'javascript', 
        '.json': 'json',
        '.md': 'markdown',
        '.txt': 'text',
        '.csv': 'text',
        '.html': 'text',
        '.css': 'text',
        '.xml': 'text',
        '.yml': 'text',
        '.yaml': 'text',
        '.png': 'image',
        '.jpg': 'image',
        '.jpeg': 'image',
        '.gif': 'image',
        '.svg': 'image',
        '.pdf': 'pdf',
        '.doc': 'word',
        '.docx': 'word',
        '.xls': 'excel',
        '.xlsx': 'excel',
        '.ppt': 'powerpoint',
        '.pptx': 'powerpoint',
        '.zip': 'archive',
        '.tar': 'archive',
        '.gz': 'archive',
        '.r': 'text',
        '.R': 'text',
        '.ipynb': 'json',
        '.tex': 'text',
        '.bib': 'text'
    }
    
    return type_map.get(suffix, 'text')


@login_required
@require_http_methods(["GET"])
def file_content_api(request, file_id):
    """
    API endpoint to get real file content for preview/editing.
    """
    try:
        from pathlib import Path
        
        # First, get the file tree to find the file path
        user = request.user
        user_projects = Project.objects.filter(
            owner=user, 
            status__in=['active', 'planning']
        )
        
        file_path = None
        file_name = ""
        
        # Search through all projects to find the file
        for project in user_projects:
            project_path = project.get_directory_path()
            if project_path and project_path.exists():
                # Recursively search for the file
                file_path, file_name = _find_file_by_id(project_path, file_id)
                if file_path:
                    break
        
        if not file_path or not Path(file_path).exists():
            return JsonResponse({
                "success": False,
                "error": "File not found"
            }, status=404)
        
        # Read file content
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
        except UnicodeDecodeError:
            # Try with different encoding or treat as binary
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
            except:
                content = f"[Binary file - {file_name}]\nUnable to display binary content."
        
        return JsonResponse({
            "success": True,
            "content": content,
            "fileId": file_id,
            "fileName": file_name,
            "filePath": str(file_path)
        })
        
    except Exception as e:
        return JsonResponse({
            "success": False,
            "error": str(e)
        }, status=500)


def _find_file_by_id(directory_path, target_file_id):
    """
    Recursively search for a file with the given ID in the directory tree.
    Returns (file_path, file_name) if found, (None, "") if not found.
    """
    try:
        for entry in directory_path.iterdir():
            if entry.name.startswith('.'):
                continue
                
            # Generate the same ID format as in _scan_directory
            entry_id = f"{target_file_id.split('_')[0]}_{target_file_id.split('_')[1]}_{entry.name}".replace(' ', '_').replace('.', '_dot_')
            
            if entry.is_file():
                # Check if this matches our target ID
                if entry_id == target_file_id:
                    return str(entry), entry.name
            elif entry.is_dir():
                # Recursively search subdirectories
                result_path, result_name = _find_file_by_id(entry, target_file_id)
                if result_path:
                    return result_path, result_name
                    
        return None, ""
        
    except Exception as e:
        print(f"Error searching for file {target_file_id} in {directory_path}: {e}")
        return None, ""


@csrf_exempt
@login_required 
def file_tree_api_wrapper(request):
    """File tree API endpoint wrapper"""
    return file_tree_api(request)


@csrf_exempt
@login_required
def file_content_api_wrapper(request, file_id):
    """File content API endpoint wrapper"""
    return file_content_api(request, file_id)


@login_required
@require_http_methods(["GET"])
def debug_user_projects(request):
    """Debug endpoint to show current user's projects"""
    try:
        from django.http import JsonResponse
        
        user = request.user
        projects = Project.objects.filter(owner=user).order_by('-created_at')
        
        project_data = []
        for project in projects:
            project_data.append({
                'id': project.id,
                'name': project.name,
                'status': project.status,
                'created_at': project.created_at.isoformat(),
                'directory_exists': project.get_directory_path().exists() if project.get_directory_path() else False
            })
        
        return JsonResponse({
            'success': True,
            'user': {
                'id': user.id,
                'username': user.username,
                'email': user.email
            },
            'projects_count': len(project_data),
            'projects': project_data
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e)
        }, status=500)

# EOF