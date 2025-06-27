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

from .models import Document, Project, UserProfile


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
            
            if not description:
                return self.error_response("Project description is required")
            
            if not hypotheses:
                return self.error_response("Research hypotheses are required")
            
            # Create project with enhanced fields
            with transaction.atomic():
                project = Project.objects.create(
                    name=name,
                    description=description,
                    hypotheses=hypotheses,
                    source_code_url=data.get('source_code_url', '').strip(),
                    status=data.get('status', 'planning'),
                    progress=data.get('progress', 0),
                    owner=request.user
                )
                
                # Add deadline if provided
                deadline = data.get('deadline')
                if deadline:
                    from django.utils.dateparse import parse_datetime
                    project.deadline = parse_datetime(deadline)
                    project.save()
                
                # Create default directory structure if requested
                create_default_structure = data.get('create_default_structure', True)
                if create_default_structure:
                    success = project.ensure_directory()
                    if success:
                        # Create the standard research directory structure
                        self._create_default_directories(project)
            
            return self.success_response({
                'project': self._serialize_project(project),
                'message': 'Project created successfully with default directory structure'
            }, status=201)
            
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

# EOF