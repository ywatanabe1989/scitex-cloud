from django.urls import path
from apps.api import engine_views

urlpatterns = [
    # SciTeX-Engine API endpoints
    path('orchestrate/', engine_views.orchestrate_workflow, name='engine-orchestrate'),
    path('status/<str:job_id>/', engine_views.job_status, name='engine-job-status'),
    path('templates/', engine_views.list_templates, name='engine-templates'),
    path('emacs/config/', engine_views.emacs_config, name='engine-emacs-config'),
    path('emacs/request/', engine_views.emacs_request, name='engine-emacs-request'),
    path('emacs/end-session/', engine_views.end_session, name='engine-end-session'),
]