"""
Middleware for SciTeX Cloud.
"""

import secrets


class GuestSessionMiddleware:
    """
    Track user state including current/last accessed project.

    For logged-in users:
    - Tracks current project in session
    - Used for smart module navigation

    For anonymous users (no longer used):
    - Previously generated guest session IDs
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track current project from URL for logged-in users
        if request.user.is_authenticated:
            # Check if URL matches /<username>/<project>/...
            import re
            pattern = r'^/([^/]+)/([^/?]+)/'
            match = re.match(pattern, request.path)

            if match:
                username = match.group(1)
                project_slug = match.group(2)

                # If this is a project page (not 'projects' or other reserved words)
                if project_slug not in ['projects'] and username == request.user.username:
                    # Update session with current project
                    request.session['current_project_slug'] = project_slug
                    request.session.modified = True

        response = self.get_response(request)
        return response
