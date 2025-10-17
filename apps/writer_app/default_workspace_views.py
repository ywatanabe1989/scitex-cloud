"""
Views for default workspace (guest sessions and user default workspace).

Handles:
- /guest-<sessionid>/default/writer/
- /<username>/default/writer/
"""

from django.shortcuts import render
from django.http import JsonResponse


def guest_session_view(request, username):
    """
    Guest session workspace for Writer.

    URL: /guest-<sessionid>/default/writer/

    Provides session-isolated workspace for anonymous users.
    """
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'workspace_type': 'guest',
        'session_id': username.replace('guest-', ''),
    }
    return render(request, 'writer_app/default_workspace.html', context)


def user_default_workspace(request, username):
    """
    Default workspace for logged-in users without a specific project.

    URL: /<username>/default/writer/

    Temporary workspace until user creates a project.
    """
    context = {
        'is_guest_session': False,
        'workspace_type': 'default',
        'username': username,
    }
    return render(request, 'writer_app/default_workspace.html', context)
