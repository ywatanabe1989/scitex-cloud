from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
from django.contrib.auth.models import User
from django.db import transaction
import datetime
import json
import uuid


class DocViewSet(viewsets.ViewSet):
    """
    API for SciTeX-Doc (LaTeX management)
    """
    permission_classes = [IsAuthenticated]
    
    @action(detail=False, methods=['get'])
    def manuscripts(self, request):
        """List user's manuscripts"""
        # Mock data - in production would query database
        manuscripts = [
            {
                'id': 'manuscript_1',
                'title': 'Machine Learning in Neuroscience',
                'status': 'draft',
                'created_at': '2025-01-15T10:00:00Z',
                'modified_at': '2025-01-23T14:30:00Z',
                'collaborators': 2,
                'version': 'v2.3'
            },
            {
                'id': 'manuscript_2',
                'title': 'Statistical Methods for fMRI Analysis',
                'status': 'review',
                'created_at': '2025-01-10T09:00:00Z',
                'modified_at': '2025-01-22T16:45:00Z',
                'collaborators': 3,
                'version': 'v1.5'
            }
        ]
        
        return Response({
            'manuscripts': manuscripts,
            'count': len(manuscripts)
        })
    
    @action(detail=False, methods=['post'])
    def create_manuscript(self, request):
        """Create new manuscript"""
        title = request.data.get('title', 'Untitled')
        template = request.data.get('template', 'default')
        
        manuscript = {
            'id': f"manuscript_{datetime.datetime.now().timestamp()}",
            'title': title,
            'template': template,
            'status': 'draft',
            'created_at': datetime.datetime.now().isoformat(),
            'version': 'v1.0'
        }
        
        return Response({
            'manuscript': manuscript,
            'message': 'Manuscript created successfully'
        }, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def templates(self, request):
        """Get available LaTeX templates"""
        templates = [
            {
                'id': 'ieee',
                'name': 'IEEE Transaction',
                'description': 'Standard IEEE journal template',
                'category': 'journal'
            },
            {
                'id': 'nature',
                'name': 'Nature',
                'description': 'Nature journal submission template',
                'category': 'journal'
            },
            {
                'id': 'thesis',
                'name': 'PhD Thesis',
                'description': 'Complete thesis template',
                'category': 'thesis'
            }
        ]
        
        return Response({
            'templates': templates,
            'count': len(templates)
        })
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get manuscript version history"""
        versions = [
            {
                'version': 'v2.3',
                'timestamp': '2025-01-23T14:30:00Z',
                'author': 'John Doe',
                'changes': 'Updated methodology section'
            },
            {
                'version': 'v2.2',
                'timestamp': '2025-01-22T10:15:00Z',
                'author': 'Jane Smith',
                'changes': 'Fixed citations'
            }
        ]
        
        return Response({
            'manuscript_id': pk,
            'versions': versions
        })
    
    @action(detail=True, methods=['post'])
    def start_collaboration(self, request, pk=None):
        """Start collaborative editing session"""
        user = request.user
        
        # Create or get collaboration session
        session_key = f"collaboration_session_{pk}"
        session_data = cache.get(session_key, {
            'document_id': pk,
            'active_users': {},
            'operations': [],
            'created_at': datetime.datetime.now().isoformat(),
            'version': 1
        })
        
        # Add user to session
        session_data['active_users'][str(user.id)] = {
            'username': user.username,
            'joined_at': datetime.datetime.now().isoformat(),
            'cursor_position': 0
        }
        
        # Store session in cache
        cache.set(session_key, session_data, timeout=3600 * 24)  # 24 hours
        
        return Response({
            'session_id': pk,
            'collaboration_url': f'/ws/writer/document/{pk}/',
            'active_users': list(session_data['active_users'].values()),
            'message': 'Collaboration session started'
        })
    
    @action(detail=True, methods=['post'])
    def save_content(self, request, pk=None):
        """Save document content with version control"""
        content = request.data.get('content', '')
        comment = request.data.get('comment', 'Auto-save')
        
        # Create new version
        version_key = f"document_version_{pk}_{datetime.datetime.now().timestamp()}"
        version_data = {
            'document_id': pk,
            'content': content,
            'author': request.user.username,
            'comment': comment,
            'timestamp': datetime.datetime.now().isoformat(),
            'version_number': self.get_next_version_number(pk)
        }
        
        # Store version
        cache.set(version_key, version_data, timeout=3600 * 24 * 30)  # 30 days
        
        # Update current document
        document_key = f"document_content_{pk}"
        cache.set(document_key, {
            'content': content,
            'last_modified': datetime.datetime.now().isoformat(),
            'last_author': request.user.username,
            'version': version_data['version_number']
        }, timeout=3600 * 24)
        
        return Response({
            'message': 'Document saved successfully',
            'version': version_data['version_number'],
            'timestamp': version_data['timestamp']
        })
    
    @action(detail=True, methods=['get'])
    def get_content(self, request, pk=None):
        """Get current document content"""
        document_key = f"document_content_{pk}"
        content = cache.get(document_key, {
            'content': '',
            'last_modified': None,
            'last_author': None,
            'version': 1
        })
        
        return Response({
            'document_id': pk,
            'content': content['content'],
            'last_modified': content['last_modified'],
            'last_author': content['last_author'],
            'version': content['version']
        })
    
    @action(detail=True, methods=['get'])
    def get_collaboration_status(self, request, pk=None):
        """Get collaboration status for document"""
        session_key = f"collaboration_session_{pk}"
        session_data = cache.get(session_key, None)
        
        if not session_data:
            return Response({
                'is_collaborative': False,
                'active_users': [],
                'message': 'No active collaboration session'
            })
        
        return Response({
            'is_collaborative': True,
            'active_users': list(session_data['active_users'].values()),
            'session_created': session_data.get('created_at'),
            'version': session_data.get('version', 1)
        })
    
    @action(detail=True, methods=['post'])
    def share_document(self, request, pk=None):
        """Generate sharing link for document"""
        permissions = request.data.get('permissions', 'read')  # read, write, admin
        expires_in = request.data.get('expires_in', 24)  # hours
        
        share_token = str(uuid.uuid4())
        share_key = f"document_share_{share_token}"
        
        share_data = {
            'document_id': pk,
            'created_by': request.user.username,
            'permissions': permissions,
            'created_at': datetime.datetime.now().isoformat(),
            'expires_at': (datetime.datetime.now() + datetime.timedelta(hours=expires_in)).isoformat()
        }
        
        cache.set(share_key, share_data, timeout=expires_in * 3600)
        
        share_url = f"{request.build_absolute_uri('/').rstrip('/')}/writer/shared/{share_token}"
        
        return Response({
            'share_url': share_url,
            'share_token': share_token,
            'permissions': permissions,
            'expires_at': share_data['expires_at'],
            'message': 'Share link created successfully'
        })
    
    @action(detail=True, methods=['get'])
    def export_document(self, request, pk=None):
        """Export document in various formats"""
        export_format = request.query_params.get('format', 'latex')
        
        # Get document content
        document_key = f"document_content_{pk}"
        content_data = cache.get(document_key, {'content': ''})
        content = content_data['content']
        
        if export_format == 'latex':
            return Response({
                'format': 'latex',
                'content': content,
                'filename': f'manuscript_{pk}.tex'
            })
        elif export_format == 'pdf':
            # In production, this would generate PDF
            return Response({
                'format': 'pdf',
                'download_url': f'/api/v1/writer/documents/{pk}/download/pdf/',
                'filename': f'manuscript_{pk}.pdf'
            })
        elif export_format == 'docx':
            # In production, this would convert to DOCX
            return Response({
                'format': 'docx',
                'download_url': f'/api/v1/writer/documents/{pk}/download/docx/',
                'filename': f'manuscript_{pk}.docx'
            })
        else:
            return Response({
                'error': 'Unsupported export format'
            }, status=status.HTTP_400_BAD_REQUEST)
    
    def get_next_version_number(self, document_id):
        """Get next version number for document"""
        # In production, this would query database
        # For now, use cache-based versioning
        version_key = f"document_version_counter_{document_id}"
        current_version = cache.get(version_key, 0)
        next_version = current_version + 1
        cache.set(version_key, next_version, timeout=3600 * 24 * 365)  # 1 year
        return next_version