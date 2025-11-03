#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:05:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL Configuration for SciTeX Cloud project.
"""

import hashlib
import json
import time

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView


# API Auth functions
def api_register(request):
    """
    API endpoint for user registration.

    Expects:
        username: Desired username
        email: User's email
        password: Desired password
        first_name: (optional) User's first name
        last_name: (optional) User's last name

    Returns:
        JSON response with registration status and user information if successful
    """
    data = json.loads(request.body)

    # Required fields
    username = data.get("username", "")
    email = data.get("email", "")
    password = data.get("password", "")

    # Optional fields
    first_name = data.get("first_name", "")
    last_name = data.get("last_name", "")

    # Validate inputs
    if not username or not email or not password:
        return JsonResponse(
            {
                "success": False,
                "error": "Username, email, and password are required",
            },
            status=400,
        )

    # Check if user already exists
    if User.objects.filter(username=username).exists():
        return JsonResponse(
            {"success": False, "error": "Username already exists"}, status=400
        )

    if User.objects.filter(email=email).exists():
        return JsonResponse(
            {"success": False, "error": "Email already registered"}, status=400
        )

    # Create user
    try:
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )

        # Log user in
        login(request, user)

        return JsonResponse(
            {
                "success": True,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                },
            },
            status=201,
        )
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def api_login(request):
    """
    API endpoint for user login.

    Expects:
        username: User's username
        password: User's password

    Returns:
        JSON response with login status and user information if successful
    """
    data = json.loads(request.body)
    username = data.get("username", "")
    password = data.get("password", "")

    user = authenticate(request, username=username, password=password)

    if user is not None:
        login(request, user)

        # Generate a simple token
        token = hashlib.sha256(
            f"{user.username}{time.time()}".encode()
        ).hexdigest()

        return JsonResponse(
            {
                "success": True,
                "token": token,
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "first_name": user.first_name,
                    "last_name": user.last_name,
                },
            }
        )
    else:
        return JsonResponse(
            {"success": False, "error": "Invalid username or password"},
            status=401,
        )


def api_forgot_password(request):
    """
    API endpoint for password reset request.

    Expects:
        email: User's email address

    Returns:
        JSON response with status
    """
    data = json.loads(request.body)
    email = data.get("email", "")

    if not email:
        return JsonResponse(
            {"success": False, "error": "Email is required"},
            status=400,
        )

    # Check if user exists
    try:
        user = User.objects.get(email=email)
        # In a real implementation, you would:
        # 1. Generate a password reset token
        # 2. Send an email with reset link
        # 3. Store the token with expiry

        # For now, we'll just return success
        return JsonResponse(
            {
                "success": True,
                "message": "Password reset instructions sent to your email",
            }
        )
    except User.DoesNotExist:
        # For security, don't reveal if email exists
        return JsonResponse(
            {
                "success": True,
                "message": "If an account exists with this email, you will receive password reset instructions",
            }
        )


def api_logout(request):
    """
    API endpoint for user logout.

    Returns:
        JSON response with logout status
    """
    from django.contrib.auth import logout

    logout(request)

    return JsonResponse(
        {"success": True, "message": "Successfully logged out"}
    )


def api_search_users(request):
    """
    API endpoint to search for users by username.
    Used for collaborator autocomplete.

    Query params:
        q: Search query (username or email)

    Returns:
        JSON response with matching users
    """
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({'users': []})

    # Search by username (case-insensitive, contains)
    users = User.objects.filter(
        username__icontains=query
    )[:10]  # Limit to 10 results

    users_data = [
        {
            'id': u.id,
            'username': u.username,
            'email': u.email if u.email else None,
            'full_name': u.get_full_name() or u.username,
        }
        for u in users
    ]

    return JsonResponse({'users': users_data})


# # Create view functions to redirect to appropriate app views
# def concept_page(request):
#     return render(request, "cloud_app/pages/concept.html")


# def vision_page(request):
#     return render(request, "cloud_app/pages/vision.html")


# def roadmap_page(request):
#     return render(request, "cloud_app/pages/roadmap.html")


# def repositories_page(request):
#     return render(request, "cloud_app/pages/repositories.html")


# def windows_page(request):
#     return render(request, "cloud_app/pages/windows.html")


# def feature_request_page(request):
#     return render(request, "cloud_app/pages/feature_request.html")


# def published_papers_page(request):
#     return render(request, "cloud_app/pages/published_papers.html")


# def donate_page(request):
#     return render(request, "cloud_app/pages/donate.html")


# def contact_page(request):
#     return render(request, "cloud_app/contact.html")


# def privacy_policy_page(request):
#     return render(request, "cloud_app/privacy_policy.html")


# def terms_of_use_page(request):
#     return render(request, "cloud_app/terms_of_use.html")


# def cookie_policy_page(request):
#     return render(request, "cloud_app/cookie_policy.html")


# def signup_page(request):
#     """Redirect to cloud_app's signup view."""
#     from django.shortcuts import redirect

#     return redirect("cloud:signup")


# def product_search_page(request):
#     return render(request, "cloud_app/products/search.html")


# Automatically discover and register URL patterns for apps
def discover_app_urls():
    """Discover and register URLs for all apps in ./apps/."""
    import importlib
    from pathlib import Path

    patterns = []
    apps_dir = Path(settings.BASE_DIR) / "apps"

    # Apps to skip because they're manually configured below
    skip_apps = {'public_app'}

    if apps_dir.exists():
        for app_dir in sorted(apps_dir.iterdir()):
            if app_dir.is_dir() and not app_dir.name.startswith("_"):
                app_name = app_dir.name

                # Skip apps that are manually configured
                if app_name in skip_apps:
                    continue

                urls_file = app_dir / "urls.py"
                if urls_file.exists():
                    # Extract URL prefix from app name (remove _app suffix if present)
                    url_prefix = app_name.replace("_app", "")

                    try:
                        # Try to import the urls module and check if it has urlpatterns
                        urls_module = importlib.import_module(
                            f"apps.{app_name}.urls"
                        )
                        if (
                            hasattr(urls_module, "urlpatterns")
                            and urls_module.urlpatterns
                        ):
                            # Use app_name from urls module as namespace if available
                            namespace = getattr(urls_module, 'app_name', app_name)
                            patterns.append(
                                path(
                                    f"{url_prefix}/",
                                    include((f"apps.{app_name}.urls", namespace)),
                                )
                            )
                        else:
                            print(
                                f"Info: {app_name}/urls.py has no urlpatterns, skipping"
                            )
                    except Exception as e:
                        print(
                            f"Warning: Could not register URLs for {app_name}: {e}"
                        )

    return patterns


# Reserved paths that should NOT be treated as usernames
# Add these BEFORE the username pattern to prevent conflicts
from apps.project_app.views import project_create

def get_reserved_paths():
    """
    Dynamically generate list of reserved URL prefixes.
    Returns list of paths that cannot be used as usernames.
    """
    from pathlib import Path

    reserved = set()

    # 1. Auto-discover app URL prefixes
    apps_dir = Path(settings.BASE_DIR) / "apps"
    if apps_dir.exists():
        for app_dir in sorted(apps_dir.iterdir()):
            if app_dir.is_dir() and not app_dir.name.startswith("_"):
                urls_file = app_dir / "urls.py"
                if urls_file.exists():
                    # Extract URL prefix (remove _app suffix)
                    url_prefix = app_dir.name.replace("_app", "")
                    reserved.add(url_prefix)

    # 2. Static system paths
    reserved.update([
        'admin', 'api', 'new', 'static', 'media', 'accounts', 'auth',
        'favicon.ico', 'robots.txt', 'sitemap.xml',
    ])

    # 3. Common reserved words (user-facing pages)
    reserved.update([
        'about', 'help', 'support', 'contact', 'terms', 'privacy',
        'settings', 'dashboard', 'profile', 'account',
        'login', 'logout', 'signup', 'register', 'reset', 'verify', 'confirm',
        'explore', 'trending', 'discover',
    ])

    # 4. Development/debug paths
    if settings.DEBUG:
        reserved.update(['__reload__', '__debug__'])

    return sorted(list(reserved))

# Generate reserved paths dynamically
RESERVED_PATHS = get_reserved_paths()

# Build URL patterns with correct ordering
urlpatterns = [
    path("admin/", admin.site.urls),
] + discover_app_urls()

urlpatterns += [
    # Additional URL patterns
    # Favicon redirect to prevent 404 errors
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/images/favicon.png", permanent=True),
    ),
    # API endpoints
    path("api/users/search/", api_search_users, name="api_search_users"),
    # Public app URLs (includes landing page and auth)
    # Note: public_app is already included by discover_app_urls() at /public/
    # This additional include makes it accessible at root path /
    path("", include("apps.public_app.urls")),
]

urlpatterns += [
    # /new - Create new project (GitHub-style)
    path("new/", project_create, name="project_create"),
    # Invitation accept/decline
    path("invitations/<str:token>/accept/", lambda r, token: __import__('apps.project_app.base_views', fromlist=['accept_invitation']).accept_invitation(r, token), name="accept_invitation"),
    path("invitations/<str:token>/decline/", lambda r, token: __import__('apps.project_app.base_views', fromlist=['decline_invitation']).decline_invitation(r, token), name="decline_invitation"),
]

# GitHub-style username/project URLs (MUST be last to avoid conflicts)
# This pattern catches both regular users and guest-<sessionid>
urlpatterns += [
    path("<str:username>/", include("apps.project_app.user_urls")),
]

# Custom error handlers
def handler404(request, exception=None):
    """Custom 404 handler that renders the 404.html template."""
    from django.shortcuts import render
    from django.template.loader import render_to_string
    from django.http import HttpResponse

    try:
        return render(request, '404.html', status=404)
    except Exception:
        # Fallback if template rendering fails
        html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>Page Not Found</title>
            <style>
                body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }
                div { max-width: 600px; margin: 60px auto; padding: 0 16px; text-align: center; }
                h1 { font-size: 48px; }
                p { color: #666; }
            </style>
        </head>
        <body>
            <div>
                <h1>404</h1>
                <h2>Page Not Found</h2>
                <p>The page you're looking for doesn't exist or has been removed.</p>
                <p><a href="/">Go Home</a></p>
            </div>
        </body>
        </html>
        """
        return HttpResponse(html, status=404)

# Serve static and media files during development
if settings.DEBUG:
    urlpatterns += static(
        settings.STATIC_URL, document_root=settings.STATIC_ROOT
    )
    urlpatterns += static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT
    )

    # Add django-browser-reload URLs for hot reload
    if "django_browser_reload" in settings.INSTALLED_APPS:
        urlpatterns += [
            path("__reload__/", include("django_browser_reload.urls")),
        ]

# EOF
