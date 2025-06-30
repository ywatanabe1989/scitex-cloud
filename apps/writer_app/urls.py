from django.urls import path
from . import views, simple_views, arxiv_views

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
    path('project/<int:project_id>/cloud-compile/', views.cloud_compile_sections, name='cloud-compile-sections'),
    path('project/<int:project_id>/download-paper/', views.download_paper_zip, name='download-paper-zip'),
    
    # Modular Editor Interface (Standalone)
    path('', simple_views.index, name='index'),  # Main writer page with hero section at /writer/
    path('collaborative/<int:manuscript_id>/', views.collaborative_editor, name='collaborative-editor'),  # Collaborative editor
    path('features/', simple_views.features, name='features'),
    path('pricing/', simple_views.pricing, name='pricing'),
    
    # Editor interfaces
    path('modular/', simple_views.modular_editor, name='modular-editor'),  # Modular editor
    path('simple/', simple_views.simple_editor, name='simple-editor'),  # Raw LaTeX editor
    path('advanced/', views.mvp_editor, name='advanced-editor'),  # Overleaf-style editor
    
    # API endpoints - Real compilation
    path('api/compile/', views.quick_compile, name='real-compile'),
    path('api/status/<uuid:job_id>/', views.compilation_status, name='compilation-status'),
    # path('api/test-compilation/', views.test_compilation, name='test-compilation'),  # Temporarily disabled
    path('api/save/', simple_views.mock_save, name='mock-save'),
    
    # Collaborative editing API endpoints
    path('api/collaborate/manuscript/<int:manuscript_id>/sessions/', views.collaborative_sessions, name='collaborative-sessions'),
    path('api/collaborate/manuscript/<int:manuscript_id>/join/', views.join_collaboration, name='join-collaboration'),
    path('api/collaborate/manuscript/<int:manuscript_id>/leave/', views.leave_collaboration, name='leave-collaboration'),
    path('api/collaborate/section/<int:section_id>/lock/', views.lock_section, name='lock-section'),
    path('api/collaborate/section/<int:section_id>/unlock/', views.unlock_section, name='unlock-section'),
    
    # Version control API endpoints
    path('api/version/<int:manuscript_id>/history/', views.version_history, name='version-history'),
    path('api/version/<int:manuscript_id>/create/', views.create_version, name='create-version'),
    path('api/version/<int:manuscript_id>/diff/<uuid:from_version_id>/<uuid:to_version_id>/', views.view_diff, name='view-diff'),
    path('api/version/<int:manuscript_id>/rollback/<uuid:version_id>/', views.rollback_version, name='rollback-version'),
    path('api/branch/<int:manuscript_id>/list/', views.branch_list, name='branch-list'),
    path('api/branch/<int:manuscript_id>/create/', views.create_branch, name='create-branch'),
    path('api/merge/<int:manuscript_id>/create/', views.create_merge_request, name='create-merge-request'),
    path('version-control/<int:manuscript_id>/', views.version_control_dashboard, name='version-control-dashboard'),
    
    # Advanced features (for future implementation)
    path('advanced/dashboard/', views.dashboard, name='dashboard'),
    path('advanced/manuscripts/', views.manuscript_list, name='manuscript-list'),
    path('advanced/compile/', views.quick_compile, name='quick-compile'),
    
    # arXiv Integration URLs
    path('arxiv/', arxiv_views.ArxivDashboardView.as_view(), name='arxiv-dashboard'),
    path('arxiv/account/setup/', arxiv_views.arxiv_account_setup, name='arxiv-account-setup'),
    path('arxiv/submissions/', arxiv_views.SubmissionListView.as_view(), name='arxiv-submission-list'),
    path('arxiv/submit/<int:manuscript_id>/', arxiv_views.manuscript_submission_form, name='arxiv-submit-manuscript'),
    path('arxiv/submission/<str:submission_id>/', arxiv_views.submission_detail, name='arxiv-submission-detail'),
    path('arxiv/submission/<str:submission_id>/validate/', arxiv_views.validate_submission, name='arxiv-validate-submission'),
    path('arxiv/submission/<str:submission_id>/prepare-files/', arxiv_views.prepare_submission_files, name='arxiv-prepare-files'),
    path('arxiv/submission/<str:submission_id>/submit/', arxiv_views.submit_to_arxiv, name='arxiv-submit-to-arxiv'),
    path('arxiv/submission/<str:submission_id>/check-status/', arxiv_views.check_submission_status, name='arxiv-check-status'),
    path('arxiv/submission/<str:submission_id>/withdraw/', arxiv_views.withdraw_submission, name='arxiv-withdraw-submission'),
    path('arxiv/submission/<str:submission_id>/replace/', arxiv_views.create_replacement, name='arxiv-create-replacement'),
    path('arxiv/submission/<str:submission_id>/history/', arxiv_views.submission_history_api, name='arxiv-submission-history'),
    
    # arXiv API endpoints
    path('arxiv/api/categories/', arxiv_views.categories_api, name='arxiv-categories-api'),
    path('arxiv/api/suggest-categories/<int:manuscript_id>/', arxiv_views.suggest_categories_api, name='arxiv-suggest-categories'),
    path('arxiv/api/status/', arxiv_views.arxiv_status_check, name='arxiv-status-check'),
    path('arxiv/api/initialize-categories/', arxiv_views.initialize_categories, name='arxiv-initialize-categories'),
]