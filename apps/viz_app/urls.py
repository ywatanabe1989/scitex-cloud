from django.urls import path
from . import views

app_name = 'viz_app'

urlpatterns = [
    # Basic pages
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    
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
]