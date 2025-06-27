from django.urls import path
from . import views

app_name = 'monitoring_app'

urlpatterns = [
    path('', views.monitoring_dashboard, name='dashboard'),
    path('api/performance/', views.api_performance_data, name='api_performance_data'),
    path('api/user-activity/', views.user_activity_data, name='user_activity_data'),
    path('api/health/', views.system_health, name='system_health'),
    path('errors/', views.error_logs, name='error_logs'),
    
    # Enhanced real-time monitoring endpoints
    path('api/realtime/', views.real_time_metrics, name='real_time_metrics'),
    path('api/features/', views.feature_analytics, name='feature_analytics'),
    path('api/trends/', views.performance_trends, name='performance_trends'),
]