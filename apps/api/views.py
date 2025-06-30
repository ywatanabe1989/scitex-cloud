from rest_framework import viewsets, permissions, status
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from apps.document_app.models import Document
from apps.project_app.models import Project
from apps.auth_app.models import UserProfile
from apps.cloud_app.models import Subscription, CloudResource, APIKey
from apps.api.serializers import (
    ProjectSerializer, DocumentSerializer, 
    UserProfileSerializer, SubscriptionSerializer,
    APIKeySerializer, ResourceUsageSerializer
)

@api_view(['GET'])
def api_root(request):
    """API root endpoint with available resources."""
    return Response({
        'modules': {
            'engine': request.build_absolute_uri('/api/v1/engine/'),
            'search': request.build_absolute_uri('/api/v1/search/'),
            'code': request.build_absolute_uri('/api/v1/code/'),
            'viz': request.build_absolute_uri('/api/v1/viz/'),
            'doc': request.build_absolute_uri('/api/v1/doc/'),
        },
        'resources': {
            'projects': request.build_absolute_uri('/api/v1/projects/'),
            'documents': request.build_absolute_uri('/api/v1/documents/'),
            'user': request.build_absolute_uri('/api/v1/user/profile/'),
            'subscription': request.build_absolute_uri('/api/v1/user/subscription/'),
            'usage': request.build_absolute_uri('/api/v1/user/usage/'),
            'api_keys': request.build_absolute_uri('/api/v1/keys/'),
        }
    })


class ProjectViewSet(viewsets.ModelViewSet):
    """ViewSet for managing research projects."""
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Project.objects.filter(owner=self.request.user)
    
    def perform_create(self, serializer):
        # Check subscription limits
        subscription = self.request.user.cloud_subscriptions.filter(
            status__in=['trial', 'active']
        ).first()
        
        if subscription:
            current_projects = self.get_queryset().count()
            if current_projects >= subscription.plan.max_projects:
                return Response(
                    {'error': f'Project limit reached. Your plan allows {subscription.plan.max_projects} projects.'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        serializer.save(owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def archive(self, request, pk=None):
        """Archive a project and generate DOI."""
        project = self.get_object()
        # TODO: Implement archive logic with DOI generation
        project.is_archived = True
        project.archived_at = timezone.now()
        project.save()
        return Response({'status': 'archived', 'doi': 'pending'})


class DocumentViewSet(viewsets.ModelViewSet):
    """ViewSet for managing documents."""
    serializer_class = DocumentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Document.objects.filter(project__owner=self.request.user)
    
    @action(detail=True, methods=['post'])
    def compile(self, request, pk=None):
        """Compile document using SciTeX-Doc."""
        document = self.get_object()
        # TODO: Implement compilation logic
        return Response({'status': 'compiling', 'job_id': 'pending'})


class UserProfileView(APIView):
    """View for user profile information."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)


class UserSubscriptionView(APIView):
    """View for user subscription information."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        subscription = request.user.cloud_subscriptions.filter(
            status__in=['trial', 'active']
        ).first()
        
        if subscription:
            serializer = SubscriptionSerializer(subscription)
            return Response(serializer.data)
        
        return Response({'message': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)


class UserUsageView(APIView):
    """View for user resource usage."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        # Get current billing period
        subscription = request.user.cloud_subscriptions.filter(
            status__in=['trial', 'active']
        ).first()
        
        if not subscription:
            return Response({'message': 'No active subscription'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get usage for current period
        usage = CloudResource.objects.filter(
            user=request.user,
            period_start__gte=subscription.current_period_start,
            period_end__lte=subscription.current_period_end
        )
        
        serializer = ResourceUsageSerializer(usage, many=True)
        
        # Calculate summary
        summary = {
            'cpu_hours': sum(u.amount_used for u in usage if u.resource_type == 'cpu'),
            'gpu_hours': sum(u.amount_used for u in usage if u.resource_type == 'gpu'),
            'storage_gb': sum(u.amount_used for u in usage if u.resource_type == 'storage'),
            'api_calls': sum(u.amount_used for u in usage if u.resource_type == 'api_calls'),
        }
        
        return Response({
            'period': {
                'start': subscription.current_period_start,
                'end': subscription.current_period_end,
            },
            'summary': summary,
            'details': serializer.data
        })


class APIKeyListCreateView(APIView):
    """View for listing and creating API keys."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        keys = APIKey.objects.filter(user=request.user, is_active=True)
        serializer = APIKeySerializer(keys, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = APIKeySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class APIKeyDetailView(APIView):
    """View for API key details."""
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, prefix):
        key = get_object_or_404(APIKey, prefix=prefix, user=request.user)
        serializer = APIKeySerializer(key)
        return Response(serializer.data)
    
    def delete(self, request, prefix):
        key = get_object_or_404(APIKey, prefix=prefix, user=request.user)
        key.is_active = False
        key.save()
        return Response(status=status.HTTP_204_NO_CONTENT)