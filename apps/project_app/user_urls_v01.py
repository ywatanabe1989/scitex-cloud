from django.urls import path
from . import views
from .api_views_module import api_views
from .views import security_views
# TODO: Uncomment when Issue models are implemented
# from .views import issues_views, api_issues_views
# TODO: Uncomment when Workflow models are implemented
# from .views import actions_views
# TODO: Uncomment when PullRequest models are implemented
# from .views import pr_views

app_name = 'user_projects'

# Wrapper view to pass username from URL kwargs to the view
def user_profile_wrapper(request, username):
    return views.user_profile(request, username)

def user_project_list_wrapper(request, username):
    return views.user_project_list(request, username)

def project_detail_wrapper(request, username, slug):
    return views.project_detail(request, username, slug)

def project_edit_wrapper(request, username, slug):
    return views.project_edit(request, username, slug)

def project_create_from_template_wrapper(request, username, slug):
    return views.project_create_from_template(request, username, slug)

def project_settings_wrapper(request, username, slug):
    return views.project_settings(request, username, slug)

def project_delete_wrapper(request, username, slug):
    return views.project_delete(request, username, slug)

def project_collaborate_wrapper(request, username, slug):
    return views.project_collaborate(request, username, slug)

def project_members_wrapper(request, username, slug):
    return views.project_members(request, username, slug)

def github_integration_wrapper(request, username, slug):
    return views.github_integration(request, username, slug)

def project_directory_wrapper(request, username, slug, directory, subpath=None):
    return views.project_directory(request, username, slug, directory, subpath)

def commit_detail_wrapper(request, username, slug, commit_hash):
    return views.commit_detail(request, username, slug, commit_hash)

urlpatterns = [
    # GitHub-style username URLs
    # /<username>/ - Profile/Overview (with ?tab= query params)
    # /<username>?tab=repositories - Projects list (GitHub pattern)
    # /<username>/<project-slug>/ - Project detail
    path('', user_profile_wrapper, name='user_profile'),  # /<username>/ with ?tab support
    path('<slug:slug>/', project_detail_wrapper, name='detail'),
    path('<slug:slug>/edit/', project_edit_wrapper, name='edit'),
    path('<slug:slug>/delete/', project_delete_wrapper, name='delete'),
    path('<slug:slug>/create-from-template/', project_create_from_template_wrapper, name='create_from_template'),

    # Settings/Management URLs (GitHub-style /settings/ pattern)
    path('<slug:slug>/settings/', project_settings_wrapper, name='settings'),
    path('<slug:slug>/settings/collaboration/', project_collaborate_wrapper, name='collaborate'),
    path('<slug:slug>/settings/members/', project_members_wrapper, name='members'),
    path('<slug:slug>/settings/integrations/', github_integration_wrapper, name='github'),

    # Security URLs (GitHub-style /security/ pattern)
    path('<slug:slug>/security/', security_views.security_overview, name='security_overview'),
    path('<slug:slug>/security/alerts/', security_views.security_alerts, name='security_alerts'),
    path('<slug:slug>/security/alerts/<int:alert_id>/', security_views.security_alert_detail, name='security_alert_detail'),
    path('<slug:slug>/security/policy/', security_views.security_policy_edit, name='security_policy'),
    path('<slug:slug>/security/advisories/', security_views.security_advisories, name='security_advisories'),
    path('<slug:slug>/security/dependabot/', security_views.dependency_graph, name='dependency_graph'),
    path('<slug:slug>/security/scans/', security_views.scan_history, name='scan_history'),

    # Note: Module views (scholar, writer, code, viz) are accessed via:
    # /<username>/<slug>/?mode=scholar
    # /<username>/<slug>/?mode=writer
    # /<username>/<slug>/?mode=code
    # /<username>/<slug>/?mode=viz
    # These are handled by project_detail view with query parameter routing

    # IMPORTANT: Specific routes MUST come before catch-all directory_browse!

    # API endpoint for file tree (sidebar navigation)
    path('<slug:slug>/api/file-tree/', views.api_file_tree, name='api_file_tree'),

    # API endpoint to concatenate all files in a directory
    path('<slug:slug>/api/concatenate/', views.api_concatenate_directory, name='api_concatenate_root'),
    path('<slug:slug>/api/concatenate/<path:directory_path>', views.api_concatenate_directory, name='api_concatenate'),

    # API endpoint to switch branch
    # TODO: Implement api_switch_branch function
    # path('<slug:slug>/api/switch-branch/', views.api_switch_branch, name='api_switch_branch'),

    # Social interaction API endpoints (Watch, Star, Fork)
    path('<slug:slug>/api/watch/', api_views.api_project_watch, name='api_watch'),
    path('<slug:slug>/api/star/', api_views.api_project_star, name='api_star'),
    path('<slug:slug>/api/fork/', api_views.api_project_fork, name='api_fork'),
    path('<slug:slug>/api/stats/', api_views.api_project_stats, name='api_stats'),

    # Security API endpoints
    path('<slug:slug>/api/security/scan/', security_views.trigger_security_scan, name='api_trigger_scan'),
    path('<slug:slug>/api/security/alerts/<int:alert_id>/dismiss/', security_views.dismiss_alert, name='api_dismiss_alert'),
    path('<slug:slug>/api/security/alerts/<int:alert_id>/reopen/', security_views.reopen_alert, name='api_reopen_alert'),
    path('<slug:slug>/api/security/alerts/<int:alert_id>/fix/', security_views.create_fix_pr, name='api_create_fix_pr'),
    path('<slug:slug>/api/security/dependencies/<int:dependency_id>/tree/', security_views.api_dependency_tree, name='api_dependency_tree'),

    # TODO: Uncomment when Issue models are implemented
    # # Issue tracking URLs
    # path('<slug:slug>/issues/', issues_views.issues_list, name='issues_list'),
    # path('<slug:slug>/issues/new/', issues_views.issue_create, name='issue_create'),
    # path('<slug:slug>/issues/<int:issue_number>/', issues_views.issue_detail, name='issue_detail'),
    # path('<slug:slug>/issues/<int:issue_number>/edit/', issues_views.issue_edit, name='issue_edit'),
    # path('<slug:slug>/issues/<int:issue_number>/comment/', issues_views.issue_comment_create, name='issue_comment_create'),
    # path('<slug:slug>/issues/labels/', issues_views.issue_label_manage, name='issue_label_manage'),
    # path('<slug:slug>/issues/milestones/', issues_views.issue_milestone_manage, name='issue_milestone_manage'),

    # # Issue API endpoints
    # path('<slug:slug>/api/issues/search/', api_issues_views.api_issue_search, name='api_issue_search'),
    # path('<slug:slug>/api/issues/<int:issue_number>/comment/', api_issues_views.api_issue_comment, name='api_issue_comment'),
    # path('<slug:slug>/api/issues/<int:issue_number>/close/', api_issues_views.api_issue_close, name='api_issue_close'),
    # path('<slug:slug>/api/issues/<int:issue_number>/reopen/', api_issues_views.api_issue_reopen, name='api_issue_reopen'),
    # path('<slug:slug>/api/issues/<int:issue_number>/assign/', api_issues_views.api_issue_assign, name='api_issue_assign'),
    # path('<slug:slug>/api/issues/<int:issue_number>/label/', api_issues_views.api_issue_label, name='api_issue_label'),
    # path('<slug:slug>/api/issues/<int:issue_number>/milestone/', api_issues_views.api_issue_milestone, name='api_issue_milestone'),

    # TODO: Uncomment when Workflow models are implemented
    # # CI/CD Actions URLs (GitHub-style /actions/ pattern)
    # path('<slug:slug>/actions/', actions_views.actions_list, name='actions_list'),
    # path('<slug:slug>/actions/new/', actions_views.workflow_create, name='workflow_create'),
    # path('<slug:slug>/actions/workflows/<int:workflow_id>/', actions_views.workflow_detail, name='workflow_detail'),
    # path('<slug:slug>/actions/workflows/<int:workflow_id>/edit/', actions_views.workflow_edit, name='workflow_edit'),
    # path('<slug:slug>/actions/workflows/<int:workflow_id>/delete/', actions_views.workflow_delete, name='workflow_delete'),
    # path('<slug:slug>/actions/workflows/<int:workflow_id>/trigger/', actions_views.workflow_trigger, name='workflow_trigger'),
    # path('<slug:slug>/actions/workflows/<int:workflow_id>/toggle/', actions_views.workflow_enable_disable, name='workflow_enable_disable'),
    # path('<slug:slug>/actions/runs/<int:run_id>/', actions_views.workflow_run_detail, name='workflow_run_detail'),

    # TODO: Uncomment when PullRequest models are implemented
    # # Pull Request URLs (GitHub-style /pull/ pattern)
    # path('<slug:slug>/pulls/', pr_views.pr_list, name='pr_list'),
    # path('<slug:slug>/pull/new/', pr_views.pr_create, name='pr_create'),
    # path('<slug:slug>/pull/<int:pr_number>/', pr_views.pr_detail, name='pr_detail'),
    # path('<slug:slug>/compare/<str:compare>/', pr_views.pr_compare, name='pr_compare'),

    # # Pull Request API endpoints
    # path('<slug:slug>/pull/<int:pr_number>/merge/', pr_views.pr_merge, name='pr_merge'),
    # path('<slug:slug>/pull/<int:pr_number>/close/', pr_views.pr_close, name='pr_close'),
    # path('<slug:slug>/pull/<int:pr_number>/reopen/', pr_views.pr_reopen, name='pr_reopen'),
    # path('<slug:slug>/pull/<int:pr_number>/review/', pr_views.pr_review_submit, name='pr_review_submit'),
    # path('<slug:slug>/pull/<int:pr_number>/comment/', pr_views.pr_comment_create, name='pr_comment_create'),

    # File viewer - GitHub-style /blob/ for viewing files
    # /<username>/<slug>/blob/<file-path> - default view
    # /<username>/<slug>/blob/<file-path>?mode=edit - edit mode
    # /<username>/<slug>/blob/<file-path>?mode=raw - raw mode
    path('<slug:slug>/blob/<path:file_path>', views.project_file_view, name='file_view'),

    # File history - GitHub-style /commits/<branch>/<file-path>
    # /<username>/<slug>/commits/<branch>/<file-path>
    path('<slug:slug>/commits/<str:branch>/<path:file_path>', views.file_history_view, name='file_history'),

    # Commit detail - GitHub-style /commit/<commit-hash>/
    # /<username>/<slug>/commit/<commit-hash>/
    path('<slug:slug>/commit/<str:commit_hash>/', commit_detail_wrapper, name='commit_detail'),

    # Dynamic directory browsing - catches ANY directory path (MUST BE LAST!)
    # /<username>/<slug>/<any-directory>/
    # /<username>/<slug>/<any-directory>/<any-subdirectory>/...
    path('<slug:slug>/<path:directory_path>/', views.project_directory_dynamic, name='directory_browse'),
]