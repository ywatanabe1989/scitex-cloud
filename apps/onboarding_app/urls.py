"""
URL configuration for Onboarding app - Priority 1: User Onboarding & Growth
"""
from django.urls import path
from . import views

app_name = 'onboarding'

urlpatterns = [
    # Main onboarding views
    path('', views.onboarding_dashboard, name='dashboard'),
    path('start/', views.start_onboarding, name='start'),
    path('step/<str:step_name>/', views.onboarding_step, name='step'),
    path('complete/<str:step_name>/', views.complete_step, name='complete_step'),
    
    # Guided tours - removed as per user request
    
    # Sample projects
    path('template/<uuid:template_id>/', views.create_sample_project, name='create_sample_project'),
    
    # User achievements and preferences
    path('achievements/', views.achievements, name='achievements'),
    path('preferences/', views.preferences, name='preferences'),
    
    # API endpoints for AJAX
    path('api/track-action/', views.api_track_action, name='api_track_action'),
    path('api/tips/', views.api_get_tips, name='api_get_tips'),
    path('api/dismiss-tip/<int:tip_id>/', views.api_dismiss_tip, name='api_dismiss_tip'),
    path('api/progress/', views.api_progress_status, name='api_progress_status'),
]