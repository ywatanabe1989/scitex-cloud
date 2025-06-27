from django.urls import path
from . import views, simple_views

app_name = 'writer'

urlpatterns = [
    # Project-linked Writer (Primary Interface)
    path('project/<int:project_id>/', views.project_writer, name='project-writer'),
    path('project/<int:project_id>/save-section/', views.save_section, name='save-section'),
    path('project/<int:project_id>/load-latex/', views.load_latex_section, name='load-latex'),
    path('project/<int:project_id>/save-latex/', views.save_latex_section, name='save-latex'),
    path('project/<int:project_id>/compile/', views.compile_modular_manuscript, name='compile-modular'),
    path('project/<int:project_id>/stats/', views.get_manuscript_stats, name='manuscript-stats'),
    path('project/<int:project_id>/toggle-mode/', views.toggle_editing_mode, name='toggle-mode'),
    
    # Modular Editor Interface (Standalone)
    path('', simple_views.modular_editor, name='index'),  # Modular editor at /writer/
    path('features/', simple_views.features, name='features'),
    path('pricing/', simple_views.pricing, name='pricing'),
    
    # Legacy editor interfaces
    path('simple/', simple_views.index, name='simple-editor'),  # Raw LaTeX editor
    path('advanced/', views.mvp_editor, name='advanced-editor'),  # Overleaf-style editor
    
    # API endpoints - Real compilation
    path('api/compile/', views.quick_compile, name='real-compile'),
    path('api/status/<uuid:job_id>/', views.compilation_status, name='compilation-status'),
    path('api/save/', simple_views.mock_save, name='mock-save'),
    
    # Advanced features (for future implementation)
    path('advanced/dashboard/', views.dashboard, name='dashboard'),
    path('advanced/manuscripts/', views.manuscript_list, name='manuscript-list'),
    path('advanced/compile/', views.quick_compile, name='quick-compile'),
]