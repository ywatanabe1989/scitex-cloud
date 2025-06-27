from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
import datetime


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