"""
API views for reference manager synchronization.
Provides REST API endpoints for all sync operations.
"""

import logging
from datetime import datetime, timedelta

from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone
from django.http import Http404
from django.shortcuts import get_object_or_404

from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.parsers import MultiPartParser, FileUploadParser
from rest_framework.pagination import PageNumberPagination

from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    SyncSession,
    ReferenceMapping,
    ConflictResolution,
    SyncLog,
    SyncStatistics,
    WebhookEndpoint
)
from .serializers import (
    ReferenceManagerAccountSerializer,
    SyncProfileSerializer,
    SyncSessionSerializer,
    ReferenceMappingSerializer,
    ConflictResolutionSerializer,
    SyncLogSerializer,
    SyncStatisticsSerializer,
    WebhookEndpointSerializer,
    BulkImportSerializer,
    BulkExportSerializer,
    SyncStatusSerializer,
    SyncActionSerializer,
    OAuthCallbackSerializer
)
from .services import MendeleyService, ZoteroService, SyncEngine
from apps.scholar_app.models import SearchIndex


logger = logging.getLogger(__name__)


class StandardResultsSetPagination(PageNumberPagination):
    """Standard pagination for API views."""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class ReferenceManagerAccountViewSet(viewsets.ModelViewSet):
    """API for managing reference manager accounts."""
    
    serializer_class = ReferenceManagerAccountSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter accounts to current user."""
        return ReferenceManagerAccount.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating account."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def connect(self, request, pk=None):
        """Initiate OAuth connection for an account."""
        account = self.get_object()
        service_name = account.service
        
        try:
            if service_name == 'mendeley':
                service = MendeleyService(account)
            elif service_name == 'zotero':
                service = ZoteroService(account)
            else:
                return Response(
                    {'error': 'Unsupported service'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            redirect_uri = request.build_absolute_uri(
                f'/reference-sync/oauth/{service_name}/callback/'
            )
            
            oauth_url = service.get_oauth_url(
                redirect_uri=redirect_uri,
                state=str(account.id)
            )
            
            return Response({
                'oauth_url': oauth_url,
                'account_id': str(account.id)
            })
            
        except Exception as e:
            logger.error(f"OAuth connection failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['post'])
    def disconnect(self, request, pk=None):
        """Disconnect an account."""
        account = self.get_object()
        
        account.is_active = False
        account.status = 'inactive'
        account.access_token = ''
        account.refresh_token = ''
        account.save()
        
        return Response({'success': True})
    
    @action(detail=True, methods=['get'])
    def test_connection(self, request, pk=None):
        """Test connection to reference manager."""
        account = self.get_object()
        
        try:
            if account.service == 'mendeley':
                service = MendeleyService(account)
            elif account.service == 'zotero':
                service = ZoteroService(account)
            else:
                return Response(
                    {'error': 'Unsupported service'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            user_info = service.get_user_info()
            
            return Response({
                'success': True,
                'authenticated': service.is_authenticated(),
                'user_info': user_info
            })
            
        except Exception as e:
            logger.error(f"Connection test failed: {e}")
            return Response({
                'success': False,
                'error': str(e)
            })


class SyncProfileViewSet(viewsets.ModelViewSet):
    """API for managing sync profiles."""
    
    serializer_class = SyncProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter profiles to current user."""
        return SyncProfile.objects.filter(
            user=self.request.user
        ).order_by('-created_at')
    
    def perform_create(self, serializer):
        """Set user when creating profile."""
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Start synchronization for a profile."""
        profile = self.get_object()
        
        if not profile.is_active:
            return Response(
                {'error': 'Profile is not active'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if there's already a running sync
        running_sync = SyncSession.objects.filter(
            profile=profile,
            status='running'
        ).first()
        
        if running_sync:
            return Response(
                {'error': 'Sync is already running', 'session_id': str(running_sync.id)},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Start sync
            sync_engine = SyncEngine(profile)
            session = sync_engine.start_sync(trigger='manual')
            
            return Response({
                'success': True,
                'session_id': str(session.id),
                'status': session.status
            })
            
        except Exception as e:
            logger.error(f"Failed to start sync: {e}")
            return Response(
                {'error': f"Failed to start sync: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=True, methods=['get'])
    def status(self, request, pk=None):
        """Get sync status for a profile."""
        profile = self.get_object()
        
        sync_engine = SyncEngine(profile)
        sync_status = sync_engine.get_sync_status()
        
        return Response(sync_status)


class SyncSessionViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing sync sessions."""
    
    serializer_class = SyncSessionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter sessions to current user."""
        return SyncSession.objects.filter(
            profile__user=self.request.user
        ).order_by('-started_at')
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get logs for a sync session."""
        session = self.get_object()
        logs = SyncLog.objects.filter(sync_session=session).order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(logs, request)
        
        serializer = SyncLogSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def conflicts(self, request, pk=None):
        """Get conflicts for a sync session."""
        session = self.get_object()
        conflicts = ConflictResolution.objects.filter(
            sync_session=session
        ).order_by('-created_at')
        
        # Apply pagination
        paginator = StandardResultsSetPagination()
        page = paginator.paginate_queryset(conflicts, request)
        
        serializer = ConflictResolutionSerializer(page, many=True)
        return paginator.get_paginated_response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def cancel(self, request, pk=None):
        """Cancel a running sync session."""
        session = self.get_object()
        
        if session.status != 'running':
            return Response(
                {'error': 'Session is not running'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        session.status = 'cancelled'
        session.completed_at = timezone.now()
        session.save()
        
        return Response({'success': True})


class ReferenceMappingViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing reference mappings."""
    
    serializer_class = ReferenceMappingSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter mappings to current user."""
        return ReferenceMapping.objects.filter(
            account__user=self.request.user
        ).order_by('-last_synced')


class ConflictResolutionViewSet(viewsets.ModelViewSet):
    """API for managing conflict resolutions."""
    
    serializer_class = ConflictResolutionSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter conflicts to current user."""
        return ConflictResolution.objects.filter(
            sync_session__profile__user=self.request.user
        ).order_by('-created_at')
    
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Resolve a conflict."""
        conflict = self.get_object()
        
        if conflict.is_resolved():
            return Response(
                {'error': 'Conflict already resolved'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        resolution = request.data.get('resolution')
        resolution_notes = request.data.get('resolution_notes', '')
        custom_value = request.data.get('custom_value')
        
        if resolution not in ['local_wins', 'remote_wins', 'merged', 'manual', 'skipped']:
            return Response(
                {'error': 'Invalid resolution'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            with transaction.atomic():
                # Update conflict
                conflict.resolution = resolution
                conflict.resolution_notes = resolution_notes
                conflict.resolved_at = timezone.now()
                conflict.resolved_by = request.user
                
                # Apply resolution to the actual data
                if resolution == 'local_wins':
                    conflict.resolved_value = conflict.local_value
                elif resolution == 'remote_wins':
                    conflict.resolved_value = conflict.remote_value
                elif resolution == 'manual' and custom_value:
                    try:
                        import json
                        conflict.resolved_value = json.loads(custom_value)
                    except json.JSONDecodeError:
                        conflict.resolved_value = custom_value
                
                conflict.save()
                
                # Update session statistics
                session = conflict.sync_session
                session.conflicts_resolved += 1
                session.save()
                
                return Response({
                    'success': True,
                    'resolution': resolution
                })
                
        except Exception as e:
            logger.error(f"Failed to resolve conflict: {e}")
            return Response(
                {'error': f'Failed to resolve conflict: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SyncStatisticsViewSet(viewsets.ReadOnlyModelViewSet):
    """API for viewing sync statistics."""
    
    serializer_class = SyncStatisticsSerializer
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = StandardResultsSetPagination
    
    def get_queryset(self):
        """Filter statistics to current user."""
        return SyncStatistics.objects.filter(
            user=self.request.user
        ).order_by('-date')
    
    @action(detail=False, methods=['get'])
    def summary(self, request):
        """Get summary statistics."""
        user = request.user
        
        # Get statistics for different time periods
        today = timezone.now().date()
        week_ago = today - timedelta(days=7)
        month_ago = today - timedelta(days=30)
        
        def get_stats(start_date, end_date=None):
            queryset = SyncStatistics.objects.filter(
                user=user,
                date__gte=start_date
            )
            if end_date:
                queryset = queryset.filter(date__lte=end_date)
            
            stats = queryset.aggregate(
                total_sessions=models.Sum('sync_sessions'),
                successful_syncs=models.Sum('successful_syncs'),
                failed_syncs=models.Sum('failed_syncs'),
                items_synced=models.Sum('items_synced'),
                conflicts_found=models.Sum('conflicts_found'),
                conflicts_resolved=models.Sum('conflicts_resolved'),
            )
            
            # Calculate success rate
            total = stats['total_sessions'] or 0
            successful = stats['successful_syncs'] or 0
            stats['success_rate'] = (successful / total * 100) if total > 0 else 0
            
            return stats
        
        return Response({
            'today': get_stats(today),
            'last_7_days': get_stats(week_ago),
            'last_30_days': get_stats(month_ago),
        })


class BulkImportAPIView(APIView):
    """API for bulk importing references."""
    
    permission_classes = [permissions.IsAuthenticated]
    parser_classes = [MultiPartParser, FileUploadParser]
    
    def post(self, request):
        """Handle bulk import."""
        serializer = BulkImportSerializer(
            data=request.data,
            context={'request': request}
        )
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        uploaded_file = validated_data['file']
        file_format = validated_data['format']
        profile_id = validated_data.get('profile_id')
        
        try:
            # Get profile if specified
            profile = None
            if profile_id:
                profile = SyncProfile.objects.get(
                    id=profile_id,
                    user=request.user
                )
            
            # Process file based on format
            if file_format == 'bibtex':
                imported_count = self._process_bibtex_file(uploaded_file, profile)
            elif file_format == 'json':
                imported_count = self._process_json_file(uploaded_file, profile)
            elif file_format == 'csv':
                imported_count = self._process_csv_file(uploaded_file, profile)
            elif file_format == 'ris':
                imported_count = self._process_ris_file(uploaded_file, profile)
            else:
                return Response(
                    {'error': f'Unsupported format: {file_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            return Response({
                'success': True,
                'imported_count': imported_count,
                'message': f'Successfully imported {imported_count} references'
            })
            
        except Exception as e:
            logger.error(f"Bulk import failed: {e}")
            return Response(
                {'error': f'Import failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _process_bibtex_file(self, file, profile):
        """Process BibTeX file."""
        # Mock implementation - would need actual BibTeX parser
        return 0
    
    def _process_json_file(self, file, profile):
        """Process JSON file."""
        # Mock implementation
        return 0
    
    def _process_csv_file(self, file, profile):
        """Process CSV file."""
        # Mock implementation
        return 0
    
    def _process_ris_file(self, file, profile):
        """Process RIS file."""
        # Mock implementation
        return 0


class BulkExportAPIView(APIView):
    """API for bulk exporting references."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request):
        """Handle bulk export."""
        serializer = BulkExportSerializer(data=request.data)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        export_format = validated_data['format']
        
        try:
            # Generate export file
            if export_format == 'bibtex':
                file_content, filename = self._export_bibtex(validated_data)
            elif export_format == 'json':
                file_content, filename = self._export_json(validated_data)
            elif export_format == 'csv':
                file_content, filename = self._export_csv(validated_data)
            elif export_format == 'ris':
                file_content, filename = self._export_ris(validated_data)
            elif export_format == 'endnote':
                file_content, filename = self._export_endnote(validated_data)
            else:
                return Response(
                    {'error': f'Unsupported format: {export_format}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Return file response
            from django.http import HttpResponse
            response = HttpResponse(
                file_content,
                content_type='application/octet-stream'
            )
            response['Content-Disposition'] = f'attachment; filename="{filename}"'
            return response
            
        except Exception as e:
            logger.error(f"Bulk export failed: {e}")
            return Response(
                {'error': f'Export failed: {e}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    def _export_bibtex(self, data):
        """Export as BibTeX."""
        content = "% BibTeX export\n"
        filename = "references.bib"
        return content, filename
    
    def _export_json(self, data):
        """Export as JSON."""
        import json
        content = json.dumps({"references": []}, indent=2)
        filename = "references.json"
        return content, filename
    
    def _export_csv(self, data):
        """Export as CSV."""
        content = "title,authors,year,journal\n"
        filename = "references.csv"
        return content, filename
    
    def _export_ris(self, data):
        """Export as RIS."""
        content = "TY  - JOUR\nER  - \n"
        filename = "references.ris"
        return content, filename
    
    def _export_endnote(self, data):
        """Export as EndNote."""
        content = "%0 Journal Article\n"
        filename = "references.enw"
        return content, filename


class SyncStatusAPIView(APIView):
    """API for checking sync status."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request, session_id):
        """Get current sync status."""
        try:
            session = SyncSession.objects.get(
                id=session_id,
                profile__user=request.user
            )
        except SyncSession.DoesNotExist:
            raise Http404("Sync session not found")
        
        data = {
            'id': str(session.id),
            'status': session.status,
            'progress': session.progress_percentage(),
            'items_processed': session.items_processed,
            'total_items': session.total_items,
            'conflicts_found': session.conflicts_found,
            'errors_count': session.errors_count,
            'started_at': session.started_at.isoformat(),
            'completed_at': session.completed_at.isoformat() if session.completed_at else None,
            'duration_seconds': session.duration().total_seconds() if session.completed_at else None,
        }
        
        serializer = SyncStatusSerializer(data)
        return Response(serializer.data)


class WebhookAPIView(APIView):
    """API for handling webhooks from reference managers."""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, service):
        """Handle webhook from reference manager."""
        if service not in ['mendeley', 'zotero']:
            return Response(
                {'error': 'Invalid service'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify webhook signature (implementation would depend on service)
        # For now, just log the webhook
        logger.info(f"Received webhook from {service}: {request.body}")
        
        try:
            # Trigger sync for relevant profiles
            profiles = SyncProfile.objects.filter(
                user=request.user,
                auto_sync=True,
                is_active=True,
                accounts__service=service
            )
            
            triggered_count = 0
            for profile in profiles:
                sync_engine = SyncEngine(profile)
                sync_engine.start_sync(trigger='webhook')
                triggered_count += 1
            
            return Response({
                'success': True,
                'triggered_syncs': triggered_count
            })
            
        except Exception as e:
            logger.error(f"Webhook processing failed: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class OAuthCallbackAPIView(APIView):
    """API for handling OAuth callbacks."""
    
    permission_classes = [permissions.AllowAny]  # OAuth callbacks don't have auth
    
    def get(self, request, service):
        """Handle OAuth callback."""
        serializer = OAuthCallbackSerializer(data=request.query_params)
        
        if not serializer.is_valid():
            return Response(
                serializer.errors,
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        code = validated_data.get('code')
        state = validated_data.get('state')
        error = validated_data.get('error')
        
        if error:
            return Response(
                {'error': f'OAuth error: {error}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not code or not state:
            return Response(
                {'error': 'Missing code or state parameter'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get account from state
            account = ReferenceManagerAccount.objects.get(
                id=state,
                service=service
            )
            
            # Create service and exchange code for token
            if service == 'mendeley':
                service_obj = MendeleyService(account)
            elif service == 'zotero':
                service_obj = ZoteroService(account)
            else:
                return Response(
                    {'error': 'Unsupported service'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            redirect_uri = request.build_absolute_uri(
                f'/reference-sync/oauth/{service}/callback/'
            )
            
            token_data = service_obj.exchange_code_for_token(code, redirect_uri)
            
            # Get user info to update account
            user_info = service_obj.get_user_info()
            
            return Response({
                'success': True,
                'account_id': str(account.id),
                'account_name': account.account_name
            })
            
        except Exception as e:
            logger.error(f"OAuth callback error: {e}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )