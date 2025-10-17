"""Default workspace views for Code app."""
from django.shortcuts import render


def guest_session_view(request, username):
    """Guest session workspace for Code."""
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'module_name': 'Code',
        'module_icon': 'fa-code',
    }
    return render(request, 'code_app/default_workspace.html', context)


def user_default_workspace(request, username):
    """Default workspace for logged-in users."""
    context = {
        'is_guest_session': False,
        'username': username,
        'module_name': 'Code',
        'module_icon': 'fa-code',
    }
    return render(request, 'code_app/default_workspace.html', context)
