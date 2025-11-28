"""
Middleware for SciTeX Cloud.
"""

import logging
from django.contrib.auth import login

logger = logging.getLogger(__name__)


class VisitorAutoLoginMiddleware:
    """
    Middleware that auto-logs in anonymous users as visitors.

    Works on any page - landing, /code/, /writer/, /scholar/, /vis/, etc.
    Skips health checks and internal requests.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Skip if already authenticated
        if request.user.is_authenticated:
            return self.get_response(request)

        # Skip health checks and internal requests
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        remote_ip = request.META.get('REMOTE_ADDR', '')

        is_health_check = (
            'curl' in user_agent.lower() or
            'wget' in user_agent.lower() or
            remote_ip.startswith('127.') or
            remote_ip.startswith('172.') or
            remote_ip.startswith('10.') or
            not user_agent
        )

        if is_health_check:
            return self.get_response(request)

        # Skip static files, media, and paths that don't need visitor
        path = request.path
        skip_paths = (
            '/static/',
            '/media/',
            '/favicon.ico',
            '/robots.txt',
            '/sitemap.xml',
            '/api/server-status/',
            '/admin/',
            '/health/',
            '/__debug__/',
        )

        if any(path.startswith(p) for p in skip_paths):
            return self.get_response(request)

        # Auto-login as visitor
        try:
            from apps.project_app.services.visitor_pool import VisitorPool

            visitor_project, visitor_user = VisitorPool.allocate_visitor(request.session)
            if visitor_user:
                login(request, visitor_user, backend='django.contrib.auth.backends.ModelBackend')
                logger.info(f"[Middleware] Auto-logged in visitor: {visitor_user.username} for {path}")
        except Exception as e:
            logger.error(f"[Middleware] Visitor auto-login failed: {e}")

        return self.get_response(request)


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

            pattern = r"^/([^/]+)/([^/?]+)/"
            match = re.match(pattern, request.path)

            if match:
                username = match.group(1)
                project_slug = match.group(2)

                # If this is a project page (not 'projects' or other reserved words)
                if (
                    project_slug not in ["projects"]
                    and username == request.user.username
                ):
                    # Update session with current project
                    request.session["current_project_slug"] = project_slug
                    request.session.modified = True

        response = self.get_response(request)
        return response
