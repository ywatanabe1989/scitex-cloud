from django.urls import path
from apps.api import code_views

urlpatterns = [
    # SciTeX-Code (MNGS) API endpoints
    path('execute/', code_views.execute_code, name='code-execute'),
    path('analyze/', code_views.analyze_data, name='code-analyze'),
    path('jobs/', code_views.list_jobs, name='code-jobs'),
    path('jobs/<str:job_id>/', code_views.job_detail, name='code-job-detail'),
    path('notebooks/', code_views.notebook_list, name='code-notebooks'),
]