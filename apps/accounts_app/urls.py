from django.urls import path
from . import views

app_name = "accounts_app"

urlpatterns = [
    # Profile views
    path("profile/", views.profile_view, name="profile"),
    path("settings/profile/", views.profile_edit, name="profile_edit"),
    path("settings/appearance/", views.appearance_settings, name="appearance"),
    path("settings/account/", views.account_settings, name="account"),
    # Integrations
    path("settings/integrations/", views.git_integrations, name="git_integrations"),
    # SSH Keys
    path("settings/ssh-keys/", views.ssh_keys, name="ssh_keys"),
    # Remote Credentials
    path("settings/remote/", views.remote_credentials, name="remote_credentials"),
    # API Keys
    path("settings/api-keys/", views.api_keys, name="api_keys"),
    # API Endpoints
    path(
        "api/ssh-keys/generate/",
        views.api_generate_ssh_key,
        name="api_generate_ssh_key",
    ),
]
