import json
import uuid
import os
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum, F
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import (
    Visualization, VisualizationType, DataSource, Dashboard,
    DashboardVisualization, VisualizationShare, ExportJob,
    ColorScheme, VisualizationTemplate, ChartConfiguration,
    InteractiveElement, VisualizationComment, VisualizationAnalytics
)
from . import default_workspace_views
from . import project_views

# Expose default workspace views
guest_session_view = default_workspace_views.guest_session_view
user_default_workspace = default_workspace_views.user_default_workspace

# Expose project views
project_viz = project_views.project_viz


@login_required
def index(request):
    """Viz app - redirect to user's projects."""
    messages.info(request, 'Please select or create a project to use Viz.')
    # Force message to be stored before redirect
    request.session.modified = True
    return redirect('user_projects:user_projects', username=request.user.username)


def features(request):
    """Viz features view."""
    return render(request, 'viz_app/features.html')


def pricing(request):
    """Viz pricing view."""
    return render(request, 'viz_app/pricing.html')


@login_required
def viz_dashboard(request):
    """Main visualization dashboard showing user's visualizations and analytics."""
    # Get user's visualizations
    visualizations = Visualization.objects.filter(owner=request.user).select_related(
        'visualization_type', 'data_source'
    ).order_by('-updated_at')
    
    # Get recent analytics
    recent_analytics = VisualizationAnalytics.objects.filter(
        visualization__owner=request.user,
        date__gte=timezone.now() - timedelta(days=30)
    ).aggregate(
        total_views=Sum('views'),
        total_exports=Sum('exports'),
        total_shares=Sum('shares'),
        avg_duration=Avg('avg_view_duration')
    )
    
    # Get dashboards
    dashboards = Dashboard.objects.filter(owner=request.user).annotate(
        viz_count=Count('visualizations')
    ).order_by('-updated_at')[:5]
    
    # Get shared visualizations
    shared_with_me = VisualizationShare.objects.filter(
        shared_with=request.user,
        expires_at__gte=timezone.now()
    ).select_related('visualization', 'shared_by').order_by('-created_at')[:5]
    
    # Pagination
    paginator = Paginator(visualizations, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'dashboards': dashboards,
        'shared_with_me': shared_with_me,
        'analytics': recent_analytics,
        'total_visualizations': visualizations.count(),
        'published_count': visualizations.filter(status='published').count(),
        'draft_count': visualizations.filter(status='draft').count(),
    }
    
    return render(request, 'viz_app/dashboard.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_visualization(request):
    """Create a new visualization."""
    if request.method == "POST":
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            viz_type_id = request.POST.get('visualization_type')
            data_source_id = request.POST.get('data_source')
            template_id = request.POST.get('template')
            
            # Validate required fields
            if not title or not viz_type_id:
                raise ValueError("Title and visualization type are required")
            
            # Create visualization
            viz_type = get_object_or_404(VisualizationType, pk=viz_type_id)
            
            with transaction.atomic():
                visualization = Visualization.objects.create(
                    title=title,
                    description=description,
                    owner=request.user,
                    visualization_type=viz_type,
                    data_source_id=data_source_id if data_source_id else None,
                    template_id=template_id if template_id else None,
                    configuration=viz_type.default_config.copy() if viz_type.default_config else {}
                )
                
                # Create default chart configuration
                ChartConfiguration.objects.create(visualization=visualization)
                
                # Handle file upload if provided
                if 'data_file' in request.FILES:
                    file = request.FILES['data_file']
                    file_data = file.read()
                    
                    # Parse data based on file type
                    if file.name.endswith('.csv'):
                        # Handle CSV parsing
                        import csv
                        import io
                        data = []
                        text_data = file_data.decode('utf-8')
                        csv_reader = csv.DictReader(io.StringIO(text_data))
                        for row in csv_reader:
                            data.append(row)
                        visualization.data = data
                    elif file.name.endswith('.json'):
                        # Handle JSON parsing
                        visualization.data = json.loads(file_data)
                    else:
                        raise ValueError("Unsupported file format")
                    
                    visualization.save()
                
                messages.success(request, f"Visualization '{title}' created successfully!")
                return redirect('viz_app:edit_visualization', pk=visualization.pk)
                
        except Exception as e:
            messages.error(request, f"Error creating visualization: {str(e)}")
            return redirect('viz_app:create_visualization')
    
    # GET request - show creation form
    visualization_types = VisualizationType.objects.filter(is_active=True)
    data_sources = DataSource.objects.filter(owner=request.user, status='active')
    templates = VisualizationTemplate.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    ).select_related('visualization_type')
    color_schemes = ColorScheme.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    )
    
    context = {
        'visualization_types': visualization_types,
        'data_sources': data_sources,
        'templates': templates,
        'color_schemes': color_schemes,
    }
    
    return render(request, 'viz_app/create_visualization.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def edit_visualization(request, pk):
    """Edit an existing visualization."""
    visualization = get_object_or_404(Visualization, pk=pk)
    
    # Check permissions
    if visualization.owner != request.user:
        # Check if user has edit permissions through sharing
        share = VisualizationShare.objects.filter(
            visualization=visualization,
            shared_with=request.user,
            permission='edit',
            expires_at__gte=timezone.now()
        ).first()
        if not share:
            raise PermissionDenied("You don't have permission to edit this visualization")
    
    if request.method == "POST":
        try:
            # Update visualization
            visualization.title = request.POST.get('title', visualization.title)
            visualization.description = request.POST.get('description', visualization.description)
            
            # Update configuration
            if 'configuration' in request.POST:
                try:
                    config = json.loads(request.POST['configuration'])
                    visualization.configuration = config
                except json.JSONDecodeError:
                    messages.warning(request, "Invalid configuration format")
            
            # Update data source
            data_source_id = request.POST.get('data_source')
            if data_source_id:
                visualization.data_source_id = data_source_id
            
            # Update color scheme
            color_scheme_id = request.POST.get('color_scheme')
            if color_scheme_id:
                visualization.color_scheme_id = color_scheme_id
            
            # Update status
            new_status = request.POST.get('status')
            if new_status in ['draft', 'published', 'archived']:
                visualization.status = new_status
            
            # Update visibility
            visualization.is_public = request.POST.get('is_public') == 'true'
            visualization.is_interactive = request.POST.get('is_interactive') == 'true'
            visualization.allow_download = request.POST.get('allow_download') == 'true'
            
            # Handle tags
            tags = request.POST.get('tags', '')
            visualization.tags = [tag.strip() for tag in tags.split(',') if tag.strip()]
            
            # Save with version tracking
            if request.POST.get('create_version') == 'true':
                # Create a new version
                old_pk = visualization.pk
                visualization.pk = None
                visualization.version = F('version') + 1
                visualization.parent_version_id = old_pk
            
            visualization.save()
            
            # Update chart configuration if provided
            chart_config = visualization.chart_config
            if chart_config:
                chart_config.x_axis_label = request.POST.get('x_axis_label', '')
                chart_config.y_axis_label = request.POST.get('y_axis_label', '')
                chart_config.show_grid = request.POST.get('show_grid') == 'true'
                chart_config.show_legend = request.POST.get('show_legend') == 'true'
                chart_config.legend_position = request.POST.get('legend_position', 'right')
                chart_config.save()
            
            messages.success(request, "Visualization updated successfully!")
            
            # Handle AJAX requests
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'success',
                    'message': 'Visualization updated successfully',
                    'visualization_id': visualization.pk
                })
            
            return redirect('viz_app:edit_visualization', pk=visualization.pk)
            
        except Exception as e:
            messages.error(request, f"Error updating visualization: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                }, status=400)
    
    # GET request - show edit form
    data_sources = DataSource.objects.filter(owner=request.user, status='active')
    color_schemes = ColorScheme.objects.filter(
        Q(owner=request.user) | Q(is_public=True)
    )
    visualization_types = VisualizationType.objects.filter(is_active=True)
    interactive_elements = visualization.interactive_elements.all()
    
    context = {
        'visualization': visualization,
        'data_sources': data_sources,
        'color_schemes': color_schemes,
        'visualization_types': visualization_types,
        'interactive_elements': interactive_elements,
        'can_edit': True,
    }
    
    return render(request, 'viz_app/edit_visualization.html', context)


def view_visualization(request, pk, share_token=None):
    """View a single visualization (public or via share token)."""
    visualization = get_object_or_404(Visualization, pk=pk)
    can_view = False
    can_edit = False
    can_comment = False
    
    # Check access permissions
    if visualization.is_public and visualization.status == 'published':
        can_view = True
    elif request.user.is_authenticated:
        if visualization.owner == request.user:
            can_view = True
            can_edit = True
            can_comment = True
        else:
            # Check sharing permissions
            share = VisualizationShare.objects.filter(
                visualization=visualization,
                shared_with=request.user,
                expires_at__gte=timezone.now()
            ).first()
            if share:
                can_view = True
                can_comment = share.permission in ['comment', 'edit']
                can_edit = share.permission == 'edit'
    
    # Check share token
    if share_token:
        share = get_object_or_404(
            VisualizationShare,
            visualization=visualization,
            share_token=share_token,
            expires_at__gte=timezone.now()
        )
        can_view = True
        if not share.accessed:
            share.accessed = True
            share.accessed_at = timezone.now()
            share.save()
    
    if not can_view:
        raise PermissionDenied("You don't have permission to view this visualization")
    
    # Update view count and analytics
    visualization.view_count = F('view_count') + 1
    visualization.last_viewed = timezone.now()
    visualization.save()
    
    # Update or create analytics
    today = timezone.now().date()
    analytics, created = VisualizationAnalytics.objects.get_or_create(
        visualization=visualization,
        date=today,
        defaults={'views': 1}
    )
    if not created:
        analytics.views = F('views') + 1
        analytics.save()
    
    # Get comments if allowed
    comments = []
    if can_view:
        comments = VisualizationComment.objects.filter(
            visualization=visualization,
            is_deleted=False,
            parent__isnull=True
        ).select_related('author').prefetch_related('replies')
    
    # Get interactive elements
    interactive_elements = visualization.interactive_elements.filter(is_active=True)
    
    context = {
        'visualization': visualization,
        'can_edit': can_edit,
        'can_comment': can_comment,
        'comments': comments,
        'interactive_elements': interactive_elements,
        'share_token': share_token,
    }
    
    return render(request, 'viz_app/view_visualization.html', context)


@login_required
def dashboard_list(request):
    """List user's dashboards."""
    dashboards = Dashboard.objects.filter(owner=request.user).annotate(
        viz_count=Count('visualizations')
    ).order_by('-updated_at')
    
    # Search functionality
    search_query = request.GET.get('search')
    if search_query:
        dashboards = dashboards.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )
    
    # Pagination
    paginator = Paginator(dashboards, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_query': search_query,
    }
    
    return render(request, 'viz_app/dashboard_list.html', context)


@login_required
@require_http_methods(["GET", "POST"])
def create_dashboard(request):
    """Create a new dashboard."""
    if request.method == "POST":
        try:
            title = request.POST.get('title')
            description = request.POST.get('description', '')
            layout_type = request.POST.get('layout_type', 'grid')
            theme = request.POST.get('theme', 'light')
            
            if not title:
                raise ValueError("Dashboard title is required")
            
            # Create dashboard
            dashboard = Dashboard.objects.create(
                title=title,
                description=description,
                owner=request.user,
                layout_type=layout_type,
                theme=theme,
                is_public=request.POST.get('is_public') == 'true',
                auto_refresh=request.POST.get('auto_refresh') == 'true',
                refresh_interval=int(request.POST.get('refresh_interval', 300))
            )
            
            # Add selected visualizations
            viz_ids = request.POST.getlist('visualizations')
            for idx, viz_id in enumerate(viz_ids):
                visualization = get_object_or_404(Visualization, pk=viz_id, owner=request.user)
                DashboardVisualization.objects.create(
                    dashboard=dashboard,
                    visualization=visualization,
                    order=idx
                )
            
            messages.success(request, f"Dashboard '{title}' created successfully!")
            return redirect('viz_app:edit_dashboard', pk=dashboard.pk)
            
        except Exception as e:
            messages.error(request, f"Error creating dashboard: {str(e)}")
    
    # GET request
    visualizations = Visualization.objects.filter(
        owner=request.user,
        status='published'
    ).order_by('-updated_at')
    
    context = {
        'visualizations': visualizations,
    }
    
    return render(request, 'viz_app/create_dashboard.html', context)


@login_required
def data_source_management(request):
    """Manage data sources for visualizations."""
    data_sources = DataSource.objects.filter(owner=request.user).order_by('-updated_at')
    
    if request.method == "POST":
        action = request.POST.get('action')
        
        if action == 'create':
            try:
                name = request.POST.get('name')
                source_type = request.POST.get('source_type')
                
                if not name or not source_type:
                    raise ValueError("Name and source type are required")
                
                # Create data source
                data_source = DataSource.objects.create(
                    name=name,
                    owner=request.user,
                    source_type=source_type,
                    connection_config={}
                )
                
                # Handle different source types
                if source_type == 'file':
                    if 'file' in request.FILES:
                        file = request.FILES['file']
                        file_path = default_storage.save(
                            f'data_sources/{request.user.id}/{file.name}',
                            ContentFile(file.read())
                        )
                        data_source.connection_config = {'file_path': file_path}
                        data_source.save()
                
                elif source_type == 'database':
                    data_source.connection_config = {
                        'host': request.POST.get('db_host'),
                        'port': request.POST.get('db_port'),
                        'database': request.POST.get('db_name'),
                        'username': request.POST.get('db_user'),
                        # Password should be encrypted in production
                    }
                    data_source.save()
                
                elif source_type == 'api':
                    data_source.connection_config = {
                        'endpoint': request.POST.get('api_endpoint'),
                        'method': request.POST.get('api_method', 'GET'),
                        'headers': json.loads(request.POST.get('api_headers', '{}')),
                    }
                    data_source.refresh_interval = int(request.POST.get('refresh_interval', 3600))
                    data_source.save()
                
                elif source_type == 'code_execution':
                    # Handle code execution data source creation
                    code_job_id = request.POST.get('code_job_id')
                    if code_job_id:
                        from apps.code_app.models import CodeExecutionJob
                        from .code_integration import CodeVizBridge
                        
                        try:
                            code_job = CodeExecutionJob.objects.get(
                                job_id=code_job_id,
                                user=request.user,
                                status='completed'
                            )
                            bridge = CodeVizBridge()
                            data_source = bridge.create_data_source_from_code_job(code_job)
                            if data_source:
                                messages.success(request, f"Code execution data source '{data_source.name}' created successfully!")
                            else:
                                messages.error(request, "Failed to create data source from code execution")
                        except CodeExecutionJob.DoesNotExist:
                            messages.error(request, "Code execution job not found or not completed")
                    else:
                        messages.error(request, "Code job ID is required for code execution data source")
                else:
                    messages.success(request, f"Data source '{name}' created successfully!")
                
            except Exception as e:
                messages.error(request, f"Error creating data source: {str(e)}")
        
        elif action == 'delete':
            data_source_id = request.POST.get('data_source_id')
            try:
                data_source = get_object_or_404(DataSource, pk=data_source_id, owner=request.user)
                data_source.delete()
                messages.success(request, "Data source deleted successfully!")
            except Exception as e:
                messages.error(request, f"Error deleting data source: {str(e)}")
        
        elif action == 'refresh':
            data_source_id = request.POST.get('data_source_id')
            try:
                data_source = get_object_or_404(DataSource, pk=data_source_id, owner=request.user)
                # Trigger data refresh (implement based on source type)
                data_source.status = 'updating'
                data_source.save()
                # In production, this would trigger an async task
                messages.info(request, "Data source refresh initiated!")
            except Exception as e:
                messages.error(request, f"Error refreshing data source: {str(e)}")
        
        return redirect('viz_app:data_source_management')
    
    context = {
        'data_sources': data_sources,
    }
    
    return render(request, 'viz_app/data_source_management.html', context)


@login_required
@require_http_methods(["POST"])
def export_visualization(request, pk):
    """Export visualization in various formats."""
    visualization = get_object_or_404(Visualization, pk=pk)
    
    # Check permissions
    if visualization.owner != request.user and not visualization.is_public:
        share = VisualizationShare.objects.filter(
            visualization=visualization,
            shared_with=request.user,
            expires_at__gte=timezone.now()
        ).first()
        if not share:
            raise PermissionDenied("You don't have permission to export this visualization")
    
    if not visualization.allow_download and visualization.owner != request.user:
        raise PermissionDenied("Downloads are not allowed for this visualization")
    
    try:
        export_format = request.POST.get('format', 'png')
        options = {
            'width': int(request.POST.get('width', 1200)),
            'height': int(request.POST.get('height', 800)),
            'dpi': int(request.POST.get('dpi', 300)),
            'background': request.POST.get('background', 'white'),
        }
        
        # Create export job
        export_job = ExportJob.objects.create(
            visualization=visualization,
            user=request.user,
            format=export_format,
            options=options,
            status='pending'
        )
        
        # In production, this would trigger an async task
        # For now, we'll return a placeholder response
        if export_format == 'json':
            # Export data as JSON
            data = {
                'title': visualization.title,
                'type': visualization.visualization_type.name,
                'data': visualization.data,
                'configuration': visualization.configuration,
                'exported_at': timezone.now().isoformat()
            }
            response = JsonResponse(data)
            response['Content-Disposition'] = f'attachment; filename="{visualization.title}.json"'
            
            # Update export job
            export_job.status = 'completed'
            export_job.completed_at = timezone.now()
            export_job.save()
            
            # Update analytics
            analytics, _ = VisualizationAnalytics.objects.get_or_create(
                visualization=visualization,
                date=timezone.now().date()
            )
            analytics.exports = F('exports') + 1
            analytics.save()
            
            return response
        
        elif export_format == 'csv':
            # Export data as CSV
            import csv
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{visualization.title}.csv"'
            
            if visualization.data and isinstance(visualization.data, list):
                writer = csv.DictWriter(response, fieldnames=visualization.data[0].keys())
                writer.writeheader()
                writer.writerows(visualization.data)
            
            # Update export job
            export_job.status = 'completed'
            export_job.completed_at = timezone.now()
            export_job.save()
            
            return response
        
        else:
            # For image formats, return a status response
            # In production, this would be handled by a background task
            return JsonResponse({
                'status': 'processing',
                'job_id': export_job.pk,
                'message': f'Export to {export_format.upper()} initiated. You will be notified when ready.'
            })
    
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["GET", "POST"])
def share_visualization(request, pk):
    """Share visualization settings."""
    visualization = get_object_or_404(Visualization, pk=pk, owner=request.user)
    
    if request.method == "POST":
        try:
            action = request.POST.get('action')
            
            if action == 'create_share':
                # Create new share
                email = request.POST.get('email')
                permission = request.POST.get('permission', 'view')
                expires_days = int(request.POST.get('expires_days', 7))
                message = request.POST.get('message', '')
                
                # Check if sharing with existing user
                from django.contrib.auth.models import User
                shared_with_user = User.objects.filter(email=email).first()
                
                # Generate unique token
                share_token = str(uuid.uuid4())
                
                share = VisualizationShare.objects.create(
                    visualization=visualization,
                    shared_by=request.user,
                    shared_with=shared_with_user,
                    email=email if not shared_with_user else '',
                    permission=permission,
                    share_token=share_token,
                    expires_at=timezone.now() + timedelta(days=expires_days),
                    message=message
                )
                
                # Send email notification (implement in production)
                messages.success(request, f"Visualization shared with {email}")
                
                # Update analytics
                analytics, _ = VisualizationAnalytics.objects.get_or_create(
                    visualization=visualization,
                    date=timezone.now().date()
                )
                analytics.shares = F('shares') + 1
                analytics.save()
                
            elif action == 'update_public':
                # Update public visibility
                visualization.is_public = request.POST.get('is_public') == 'true'
                visualization.save()
                messages.success(request, "Public visibility updated")
                
            elif action == 'revoke_share':
                # Revoke share
                share_id = request.POST.get('share_id')
                share = get_object_or_404(VisualizationShare, pk=share_id, visualization=visualization)
                share.delete()
                messages.success(request, "Share access revoked")
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'success'})
            
        except Exception as e:
            messages.error(request, f"Error: {str(e)}")
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
    
    # GET request - show sharing settings
    shares = VisualizationShare.objects.filter(
        visualization=visualization
    ).select_related('shared_with').order_by('-created_at')
    
    context = {
        'visualization': visualization,
        'shares': shares,
        'share_url': request.build_absolute_uri(
            f"/viz/view/{visualization.pk}/"
        ),
    }
    
    return render(request, 'viz_app/share_visualization.html', context)


def embedded_view(request, pk, embed_token=None):
    """Embedded visualization view for external websites."""
    visualization = get_object_or_404(Visualization, pk=pk)
    
    # Check if visualization can be embedded
    if not visualization.is_public or not visualization.status == 'published':
        if not embed_token:
            raise PermissionDenied("This visualization cannot be embedded")
        
        # Verify embed token (implement token verification)
        # For now, we'll allow if token is provided
    
    # Simple embedded view without full page chrome
    context = {
        'visualization': visualization,
        'embedded': True,
        'show_branding': request.GET.get('branding', 'true') == 'true',
        'height': request.GET.get('height', '500'),
        'width': request.GET.get('width', '100%'),
    }
    
    return render(request, 'viz_app/embedded_view.html', context)


# Additional helper views for AJAX operations

@login_required
@require_http_methods(["POST"])
@csrf_exempt
def update_visualization_data(request, pk):
    """Update visualization data via AJAX."""
    visualization = get_object_or_404(Visualization, pk=pk, owner=request.user)
    
    try:
        data = json.loads(request.body)
        visualization.data = data.get('data')
        visualization.configuration = data.get('configuration', visualization.configuration)
        visualization.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Data updated successfully'
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=400)


@login_required
@require_http_methods(["POST"])
def add_comment(request, pk):
    """Add comment to visualization."""
    visualization = get_object_or_404(Visualization, pk=pk)
    
    # Check permissions
    can_comment = False
    if visualization.owner == request.user:
        can_comment = True
    elif visualization.is_public:
        can_comment = True
    else:
        share = VisualizationShare.objects.filter(
            visualization=visualization,
            shared_with=request.user,
            permission__in=['comment', 'edit'],
            expires_at__gte=timezone.now()
        ).first()
        if share:
            can_comment = True
    
    if not can_comment:
        raise PermissionDenied("You don't have permission to comment")
    
    try:
        content = request.POST.get('content')
        parent_id = request.POST.get('parent_id')
        annotation_data = request.POST.get('annotation_data')
        
        comment = VisualizationComment.objects.create(
            visualization=visualization,
            author=request.user,
            content=content,
            parent_id=parent_id if parent_id else None,
            annotation_data=json.loads(annotation_data) if annotation_data else None
        )
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'status': 'success',
                'comment': {
                    'id': comment.pk,
                    'author': comment.author.username,
                    'content': comment.content,
                    'created_at': comment.created_at.isoformat(),
                }
            })
        
        messages.success(request, "Comment added successfully!")
        return redirect('viz_app:view_visualization', pk=pk)
        
    except Exception as e:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'error', 'message': str(e)}, status=400)
        messages.error(request, f"Error adding comment: {str(e)}")
        return redirect('viz_app:view_visualization', pk=pk)


@login_required
def export_status(request, job_id):
    """Check export job status."""
    export_job = get_object_or_404(ExportJob, pk=job_id, user=request.user)
    
    return JsonResponse({
        'status': export_job.status,
        'progress': 100 if export_job.status == 'completed' else 50,
        'download_url': f'/viz/download/{export_job.pk}/' if export_job.status == 'completed' else None,
        'error': export_job.error_message if export_job.status == 'failed' else None
    })