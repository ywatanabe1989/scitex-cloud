from django.urls import path
from . import views, api_views, default_workspace_views

app_name = 'viz_app'

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # Basic pages
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    
    # Main dashboard and visualization management
    path('dashboard/', views.viz_dashboard, name='viz_dashboard'),
    path('create/', views.create_visualization, name='create_visualization'),
    path('edit/<uuid:pk>/', views.edit_visualization, name='edit_visualization'),
    path('view/<uuid:pk>/', views.view_visualization, name='view_visualization'),
    path('view/<uuid:pk>/<str:share_token>/', views.view_visualization, name='view_shared_visualization'),
    path('embed/<uuid:pk>/', views.embedded_view, name='embedded_view'),
    path('embed/<uuid:pk>/<str:embed_token>/', views.embedded_view, name='embedded_view_token'),
    
    # Dashboard management
    path('dashboards/', views.dashboard_list, name='dashboard_list'),
    path('dashboards/create/', views.create_dashboard, name='create_dashboard'),
    path('dashboards/edit/<uuid:pk>/', views.edit_visualization, name='edit_dashboard'),
    
    # Data source management
    path('data-sources/', views.data_source_management, name='data_source_management'),
    
    # Export and sharing
    path('export/<uuid:pk>/', views.export_visualization, name='export_visualization'),
    path('share/<uuid:pk>/', views.share_visualization, name='share_visualization'),
    path('export-status/<uuid:job_id>/', views.export_status, name='export_status'),
    
    # AJAX endpoints
    path('api/update-data/<uuid:pk>/', views.update_visualization_data, name='update_visualization_data'),
    path('api/add-comment/<uuid:pk>/', views.add_comment, name='add_comment'),
    
    # New API endpoints for interactive viz interface
    path('api/visualizations/', api_views.VisualizationListAPI.as_view(), name='api_visualizations'),
    path('api/visualizations/<uuid:viz_id>/', api_views.VisualizationDetailAPI.as_view(), name='api_visualization_detail'),
    path('api/data-sources/', api_views.DataSourceAPI.as_view(), name='api_data_sources'),
    path('api/visualization-types/', api_views.VisualizationTypesAPI.as_view(), name='api_visualization_types'),
    path('api/color-schemes/', api_views.ColorSchemesAPI.as_view(), name='api_color_schemes'),
    path('api/export/<uuid:viz_id>/', api_views.ExportAPI.as_view(), name='api_export'),
    path('api/upload-data/', api_views.upload_data, name='api_upload_data'),
    path('api/export-status/<uuid:job_id>/', api_views.export_job_status, name='api_export_status'),
    path('api/sample-data/', api_views.generate_sample_data, name='api_sample_data'),
    
    # Code integration endpoint
    path('api/code-sources/', api_views.CodeDataSourceAPI.as_view(), name='api_code_data_sources'),
]