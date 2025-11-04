"""
API views for research data repository management.
Provides endpoints for managing repository connections, datasets, and synchronization.
"""

import json
import logging
from typing import Dict, Any
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from ...models import (
    Repository, RepositoryConnection, Dataset, DatasetFile, 
    DatasetVersion, RepositorySync
)
from ...services.repository_services import (
    RepositoryServiceFactory, RepositoryServiceError,
    sync_dataset_with_repository, upload_dataset_to_repository
)

logger = logging.getLogger(__name__)


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing available repositories"""
    
    queryset = Repository.objects.filter(status='active')
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all available repositories"""
        repositories = self.get_queryset()
        
        data = []
        for repo in repositories:
            data.append({
                'id': str(repo.id),
                'name': repo.name,
                'type': repo.repository_type,
                'description': repo.description,
                'website_url': repo.website_url,
                'supports_doi': repo.supports_doi,
                'supports_versioning': repo.supports_versioning,
                'supports_private_datasets': repo.supports_private_datasets,
                'max_file_size_mb': repo.max_file_size_mb,
                'is_default': repo.is_default,
                'requires_authentication': repo.requires_authentication,
                'license_options': repo.license_options,
                'supported_file_formats': repo.supported_file_formats,
            })
        
        return Response(data)


class RepositoryConnectionViewSet(viewsets.ModelViewSet):
    """ViewSet for managing repository connections"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return RepositoryConnection.objects.filter(user=self.request.user)
    
    def list(self, request):
        """List user's repository connections"""
        connections = self.get_queryset()
        
        data = []
        for conn in connections:
            data.append({
                'id': str(conn.id),
                'repository': {
                    'id': str(conn.repository.id),
                    'name': conn.repository.name,
                    'type': conn.repository.repository_type,
                },
                'connection_name': conn.connection_name,
                'status': conn.status,
                'is_default': conn.is_default,
                'auto_sync_enabled': conn.auto_sync_enabled,
                'last_verified': conn.last_verified,
                'total_deposits': conn.total_deposits,
                'created_at': conn.created_at,
                'last_activity': conn.last_activity,
            })
        
        return Response(data)
    
    def create(self, request):
        """Create a new repository connection"""
        try:
            data = request.data
            repository = get_object_or_404(Repository, id=data.get('repository_id'))
            
            # Create connection
            connection = RepositoryConnection.objects.create(
                user=request.user,
                repository=repository,
                connection_name=data.get('connection_name', f"{repository.name} Connection"),
                api_token=data.get('api_token', ''),
                username=data.get('username', ''),
                is_default=data.get('is_default', False),
                auto_sync_enabled=data.get('auto_sync_enabled', True),
                notification_enabled=data.get('notification_enabled', True),
            )
            
            # Test the connection
            try:
                service = RepositoryServiceFactory.create_service(connection)
                if service.authenticate():
                    connection.status = 'active'
                    connection.last_verified = timezone.now()
                else:
                    connection.status = 'invalid'
                connection.save()
            except Exception as e:
                connection.status = 'invalid'
                connection.last_error = str(e)
                connection.save()
                logger.error(f"Failed to authenticate repository connection: {e}")
            
            return Response({
                'id': str(connection.id),
                'status': connection.status,
                'message': 'Connection created successfully' if connection.status == 'active' else 'Connection created but authentication failed'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def test_connection(self, request, pk=None):
        """Test a repository connection"""
        connection = self.get_object()
        
        try:
            service = RepositoryServiceFactory.create_service(connection)
            if service.authenticate():
                connection.status = 'active'
                connection.last_verified = timezone.now()
                connection.error_count = 0
                connection.last_error = ''
                message = 'Connection test successful'
                success = True
            else:
                connection.status = 'invalid'
                message = 'Authentication failed'
                success = False
            
            connection.save()
            
            return Response({
                'success': success,
                'status': connection.status,
                'message': message,
                'last_verified': connection.last_verified
            })
            
        except Exception as e:
            connection.status = 'invalid'
            connection.last_error = str(e)
            connection.error_count += 1
            connection.save()
            
            return Response({
                'success': False,
                'status': connection.status,
                'message': f'Connection test failed: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def list_remote_datasets(self, request, pk=None):
        """List datasets in the remote repository"""
        connection = self.get_object()
        
        try:
            service = RepositoryServiceFactory.create_service(connection)
            
            # Get filter parameters
            filters = {}
            if request.GET.get('status'):
                filters['status'] = request.GET.get('status')
            if request.GET.get('page'):
                filters['page'] = int(request.GET.get('page', 1))
            if request.GET.get('size'):
                filters['size'] = int(request.GET.get('size', 20))
            
            datasets = service.list_datasets(filters)
            
            return Response({
                'datasets': datasets,
                'count': len(datasets)
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to list remote datasets: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)


class DatasetViewSet(viewsets.ModelViewSet):
    """ViewSet for managing datasets"""
    
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Dataset.objects.filter(
            owner=self.request.user
        ).select_related(
            'repository_connection__repository', 'project', 'generated_by_job'
        ).prefetch_related('collaborators', 'files')
    
    def list(self, request):
        """List user's datasets"""
        queryset = self.get_queryset()
        
        # Apply filters
        if request.GET.get('status'):
            queryset = queryset.filter(status=request.GET.get('status'))
        if request.GET.get('dataset_type'):
            queryset = queryset.filter(dataset_type=request.GET.get('dataset_type'))
        if request.GET.get('repository_type'):
            queryset = queryset.filter(
                repository_connection__repository__repository_type=request.GET.get('repository_type')
            )
        if request.GET.get('project'):
            queryset = queryset.filter(project_id=request.GET.get('project'))
        
        # Pagination
        page_size = int(request.GET.get('page_size', 20))
        paginator = Paginator(queryset, page_size)
        page = paginator.get_page(request.GET.get('page', 1))
        
        data = []
        for dataset in page:
            data.append({
                'id': str(dataset.id),
                'title': dataset.title,
                'description': dataset.description,
                'dataset_type': dataset.dataset_type,
                'status': dataset.status,
                'visibility': dataset.visibility,
                'version': dataset.version,
                'file_count': dataset.file_count,
                'total_size_bytes': dataset.total_size_bytes,
                'size_display': dataset.get_file_size_display(),
                'repository': {
                    'name': dataset.repository_connection.repository.name,
                    'type': dataset.repository_connection.repository.repository_type,
                },
                'repository_url': dataset.repository_url,
                'repository_doi': dataset.repository_doi,
                'project': dataset.project.name if dataset.project else None,
                'created_at': dataset.created_at,
                'updated_at': dataset.updated_at,
                'published_at': dataset.published_at,
                'last_synced': dataset.last_synced,
            })
        
        return Response({
            'datasets': data,
            'pagination': {
                'count': paginator.count,
                'num_pages': paginator.num_pages,
                'current_page': page.number,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
            }
        })
    
    def create(self, request):
        """Create a new dataset"""
        try:
            data = request.data
            
            # Get repository connection
            connection = get_object_or_404(
                RepositoryConnection,
                id=data.get('repository_connection_id'),
                user=request.user
            )
            
            with transaction.atomic():
                dataset = Dataset.objects.create(
                    title=data.get('title'),
                    description=data.get('description', ''),
                    dataset_type=data.get('dataset_type', 'raw_data'),
                    keywords=data.get('keywords', ''),
                    owner=request.user,
                    repository_connection=connection,
                    version=data.get('version', '1.0'),
                    visibility=data.get('visibility', 'private'),
                    license=data.get('license', ''),
                    project_id=data.get('project_id') if data.get('project_id') else None,
                )
                
                # Add collaborators
                if 'collaborator_ids' in data:
                    dataset.collaborators.set(data['collaborator_ids'])
                
                # Link to related papers
                if 'related_paper_ids' in data:
                    dataset.related_papers.set(data['related_paper_ids'])
            
            return Response({
                'id': str(dataset.id),
                'message': 'Dataset created successfully'
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def sync_with_repository(self, request, pk=None):
        """Sync dataset with remote repository"""
        dataset = self.get_object()
        
        try:
            sync_record = sync_dataset_with_repository(dataset)
            
            return Response({
                'sync_id': str(sync_record.id),
                'status': sync_record.status,
                'message': 'Sync started successfully'
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to start sync: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def upload_to_repository(self, request, pk=None):
        """Upload dataset to repository"""
        dataset = self.get_object()
        
        try:
            file_paths = request.data.get('file_paths')  # Optional: specific files to upload
            sync_record = upload_dataset_to_repository(dataset, file_paths)
            
            return Response({
                'sync_id': str(sync_record.id),
                'status': sync_record.status,
                'message': 'Upload started successfully'
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to start upload: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def publish(self, request, pk=None):
        """Publish dataset in repository"""
        dataset = self.get_object()
        
        try:
            if not dataset.repository_id:
                return Response({
                    'error': 'Dataset must be uploaded to repository before publishing'
                }, status=status.HTTP_400_BAD_REQUEST)
            
            service = RepositoryServiceFactory.create_service(dataset.repository_connection)
            result = service.publish_dataset(dataset.repository_id)
            
            # Update local dataset
            dataset.status = 'published'
            dataset.published_at = timezone.now()
            dataset.repository_url = result.get('url', dataset.repository_url)
            dataset.repository_doi = result.get('doi', dataset.repository_doi)
            dataset.save()
            
            return Response({
                'message': 'Dataset published successfully',
                'doi': dataset.repository_doi,
                'url': dataset.repository_url
            })
            
        except Exception as e:
            return Response({
                'error': f'Failed to publish dataset: {str(e)}'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['get'])
    def files(self, request, pk=None):
        """List files in dataset"""
        dataset = self.get_object()
        
        files = dataset.files.all().order_by('file_path', 'filename')
        
        data = []
        for file_obj in files:
            data.append({
                'id': str(file_obj.id),
                'filename': file_obj.filename,
                'file_path': file_obj.file_path,
                'file_type': file_obj.file_type,
                'file_format': file_obj.file_format,
                'size_bytes': file_obj.size_bytes,
                'size_display': file_obj.get_size_display(),
                'download_url': file_obj.download_url,
                'download_count': file_obj.download_count,
                'created_at': file_obj.created_at,
            })
        
        return Response({
            'files': data,
            'total_files': len(data),
            'total_size': dataset.total_size_bytes,
            'total_size_display': dataset.get_file_size_display()
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def sync_status(request, sync_id):
    """Get sync operation status"""
    try:
        sync_record = get_object_or_404(
            RepositorySync,
            id=sync_id,
            user=request.user
        )
        
        return Response({
            'id': str(sync_record.id),
            'sync_type': sync_record.sync_type,
            'status': sync_record.status,
            'progress_percentage': sync_record.get_progress_percentage(),
            'total_items': sync_record.total_items,
            'completed_items': sync_record.completed_items,
            'failed_items': sync_record.failed_items,
            'started_at': sync_record.started_at,
            'completed_at': sync_record.completed_at,
            'estimated_completion': sync_record.estimated_completion,
            'error_message': sync_record.error_message,
            'result_data': sync_record.result_data,
        })
        
    except RepositorySync.DoesNotExist:
        return Response({
            'error': 'Sync record not found'
        }, status=status.HTTP_404_NOT_FOUND)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_repository_stats(request):
    """Get user's repository usage statistics"""
    user = request.user
    
    # Repository connections
    connections = RepositoryConnection.objects.filter(user=user)
    active_connections = connections.filter(status='active').count()
    
    # Datasets
    datasets = Dataset.objects.filter(owner=user)
    dataset_stats = {
        'total': datasets.count(),
        'by_status': {},
        'by_type': {},
        'by_repository': {},
        'total_size_bytes': 0,
    }
    
    for status_choice in Dataset.STATUS_CHOICES:
        count = datasets.filter(status=status_choice[0]).count()
        if count > 0:
            dataset_stats['by_status'][status_choice[0]] = count
    
    for type_choice in Dataset.DATASET_TYPES:
        count = datasets.filter(dataset_type=type_choice[0]).count()
        if count > 0:
            dataset_stats['by_type'][type_choice[0]] = count
    
    # Repository breakdown
    for connection in connections:
        repo_name = connection.repository.name
        count = datasets.filter(repository_connection=connection).count()
        if count > 0:
            dataset_stats['by_repository'][repo_name] = count
    
    # Total storage used
    dataset_stats['total_size_bytes'] = sum(
        dataset.total_size_bytes for dataset in datasets
    )
    
    # Recent activity
    recent_syncs = RepositorySync.objects.filter(
        user=user
    ).order_by('-created_at')[:10]
    
    sync_data = []
    for sync in recent_syncs:
        sync_data.append({
            'id': str(sync.id),
            'sync_type': sync.sync_type,
            'status': sync.status,
            'dataset_title': sync.dataset.title if sync.dataset else None,
            'repository_name': sync.repository_connection.repository.name,
            'created_at': sync.created_at,
            'completed_at': sync.completed_at,
        })
    
    return Response({
        'connections': {
            'total': connections.count(),
            'active': active_connections,
            'by_repository': {
                conn.repository.name: 1 for conn in connections
            }
        },
        'datasets': dataset_stats,
        'recent_syncs': sync_data,
    })


# Legacy view functions for backwards compatibility
@login_required
@require_http_methods(["GET"])
def list_repositories(request):
    """List available repositories"""
    repositories = Repository.objects.filter(status='active')
    
    data = []
    for repo in repositories:
        data.append({
            'id': str(repo.id),
            'name': repo.name,
            'type': repo.repository_type,
            'description': repo.description,
            'supports_doi': repo.supports_doi,
            'is_default': repo.is_default,
        })
    
    return JsonResponse({'repositories': data})


@login_required
@csrf_exempt
@require_http_methods(["POST"])
def create_repository_connection(request):
    """Create a new repository connection"""
    try:
        data = json.loads(request.body)
        repository = get_object_or_404(Repository, id=data.get('repository_id'))
        
        connection = RepositoryConnection.objects.create(
            user=request.user,
            repository=repository,
            connection_name=data.get('connection_name', f"{repository.name} Connection"),
            api_token=data.get('api_token', ''),
            username=data.get('username', ''),
        )
        
        return JsonResponse({
            'id': str(connection.id),
            'message': 'Connection created successfully'
        })
        
    except Exception as e:
        return JsonResponse({
            'error': str(e)
        }, status=400)