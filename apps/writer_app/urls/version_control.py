from django.urls import path
from ..views.version_control import dashboard

urlpatterns = [
    path('', dashboard.version_control_dashboard, name='dashboard'),
]
