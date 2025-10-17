from django.urls import path
from . import views

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
    path('<slug:slug>/settings/', project_edit_wrapper, name='settings'),
    path('<slug:slug>/settings/collaboration/', project_collaborate_wrapper, name='collaborate'),
    path('<slug:slug>/settings/members/', project_members_wrapper, name='members'),
    path('<slug:slug>/settings/integrations/', github_integration_wrapper, name='github'),

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

    # File viewer - GitHub-style /blob/ for viewing files
    # /<username>/<slug>/blob/<file-path> - default view
    # /<username>/<slug>/blob/<file-path>?mode=edit - edit mode
    # /<username>/<slug>/blob/<file-path>?mode=raw - raw mode
    path('<slug:slug>/blob/<path:file_path>', views.project_file_view, name='file_view'),

    # Dynamic directory browsing - catches ANY directory path (MUST BE LAST!)
    # /<username>/<slug>/<any-directory>/
    # /<username>/<slug>/<any-directory>/<any-subdirectory>/...
    path('<slug:slug>/<path:directory_path>/', views.project_directory_dynamic, name='directory_browse'),
]