from django.urls import path
from . import views

app_name = 'code'

urlpatterns = [
    # Landing pages
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    
    # Core functionality
    path('editor/', views.editor, name='editor'),
    path('execute/', views.execute_code, name='execute_code'),
    path('analysis/', views.analysis, name='analysis'),
    path('analysis/run/', views.run_analysis, name='run_analysis'),
    
    # Job management
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<uuid:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<uuid:job_id>/status/', views.job_status, name='job_status'),
    
    # Notebook management
    path('notebooks/', views.notebooks, name='notebooks'),
    path('notebooks/<uuid:notebook_id>/', views.notebook_detail, name='notebook_detail'),
]