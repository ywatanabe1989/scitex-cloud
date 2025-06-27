from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404

from apps.core_app.models import Document, Project, UserProfile
from .serializers import DocumentSerializer, ProjectSerializer, UserProfileSerializer


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document CRUD operations
    """
    serializer_class = DocumentSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project CRUD operations
    """
    serializer_class = ProjectSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def set_manuscript(self, request, pk=None):
        """Set the manuscript draft for a project"""
        project = self.get_object()
        document_id = request.data.get('document_id')
        
        try:
            document = Document.objects.get(id=document_id, owner=request.user)
            project.manuscript_draft = document
            project.save()
            return Response({'status': 'manuscript set'})
        except Document.DoesNotExist:
            return Response(
                {'error': 'Document not found'},
                status=status.HTTP_404_NOT_FOUND
            )


class UserProfileViewSet(viewsets.GenericViewSet):
    """
    ViewSet for UserProfile operations
    """
    serializer_class = UserProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        return get_object_or_404(UserProfile, user=self.request.user)
    
    @action(detail=False, methods=['get', 'put', 'patch'])
    def me(self, request):
        """Get or update the current user's profile"""
        profile = self.get_object()
        
        if request.method == 'GET':
            serializer = self.get_serializer(profile)
            return Response(serializer.data)
        
        elif request.method in ['PUT', 'PATCH']:
            partial = request.method == 'PATCH'
            serializer = self.get_serializer(
                profile, 
                data=request.data, 
                partial=partial
            )
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get user statistics"""
        profile = self.get_object()
        stats = {
            'total_documents': Document.objects.filter(owner=request.user).count(),
            'total_projects': Project.objects.filter(owner=request.user).count(),
            'documents_by_status': {
                'draft': Document.objects.filter(owner=request.user, document_type='draft').count(),
                'manuscript': Document.objects.filter(owner=request.user, document_type='manuscript').count(),
                'note': Document.objects.filter(owner=request.user, document_type='note').count(),
            },
            'projects_by_status': {
                'planning': Project.objects.filter(owner=request.user, status='planning').count(),
                'active': Project.objects.filter(owner=request.user, status='active').count(),
                'completed': Project.objects.filter(owner=request.user, status='completed').count(),
            }
        }
        return Response(stats)