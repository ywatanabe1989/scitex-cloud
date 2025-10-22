"""Default workspace views for Scholar app."""
from django.shortcuts import render
from apps.core_app.anonymous_storage import get_anonymous_storage_path


def guest_session_view(request, username):
    """Guest session workspace for Scholar - supports anonymous users."""
    # Handle anonymous users
    is_anonymous = not request.user.is_authenticated

    if is_anonymous:
        # Ensure session exists for anonymous users
        if not request.session.session_key:
            request.session.create()

        # Get temporary storage path
        storage_path = get_anonymous_storage_path(request.session.session_key)
        display_username = f"guest-{request.session.session_key[:8]}"
    else:
        storage_path = f"/data/users/{request.user.username}/proj/"
        display_username = request.user.username

    context = {
        'is_guest_session': True,
        'guest_username': username,
        'is_anonymous': is_anonymous,
        'storage_path': storage_path,
        'display_username': display_username,
        'module_name': 'Scholar',
        'module_icon': 'fa-search',
        'show_save_prompt': is_anonymous,  # Show "Sign up to save" prompts
    }
    return render(request, 'scholar_app/default_workspace.html', context)


def user_default_workspace(request):
    """Default workspace for logged-in users without a specific project."""
    # Support anonymous users accessing this endpoint
    is_anonymous = not request.user.is_authenticated

    if is_anonymous:
        # Ensure session exists for anonymous users
        if not request.session.session_key:
            request.session.create()

        # Get temporary storage path
        storage_path = get_anonymous_storage_path(request.session.session_key)
        username = None
        display_username = f"guest-{request.session.session_key[:8]}"
    else:
        storage_path = f"/data/users/{request.user.username}/proj/"
        username = request.user.username
        display_username = username

    context = {
        'is_guest_session': False,
        'is_anonymous': is_anonymous,
        'username': username,
        'display_username': display_username,
        'storage_path': storage_path,
        'module_name': 'Scholar',
        'module_icon': 'fa-search',
        'show_save_prompt': is_anonymous,  # Show "Sign up to save" prompts
    }
    return render(request, 'scholar_app/default_workspace.html', context)
