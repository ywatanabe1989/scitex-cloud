#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 20:10:04 (ywatanabe)"
# File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/config/urls.py
# ----------------------------------------
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
from django.views.generic import RedirectView, TemplateView


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
    from pathlib import Path
    import importlib

    patterns = []
    apps_dir = Path(settings.BASE_DIR) / 'apps'

    if apps_dir.exists():
        for app_dir in sorted(apps_dir.iterdir()):
            if app_dir.is_dir() and not app_dir.name.startswith('_'):
                urls_file = app_dir / 'urls.py'
                if urls_file.exists():
                    app_name = app_dir.name
                    # Extract URL prefix from app name (remove _app suffix if present)
                    url_prefix = app_name.replace('_app', '')

                    try:
                        # Try to import the urls module and check if it has urlpatterns
                        urls_module = importlib.import_module(f'apps.{app_name}.urls')
                        if hasattr(urls_module, 'urlpatterns') and urls_module.urlpatterns:
                            patterns.append(
                                path(f"{url_prefix}/", include(f"apps.{app_name}.urls"))
                            )
                        else:
                            print(f"Info: {app_name}/urls.py has no urlpatterns, skipping")
                    except Exception as e:
                        print(f"Warning: Could not register URLs for {app_name}: {e}")

    return patterns

urlpatterns = [
    path("admin/", admin.site.urls),
] + discover_app_urls()

urlpatterns += [
    # Additional URL patterns
    # Direct dashboard access redirects to core
    path(
        "dashboard/",
        RedirectView.as_view(url="/core/", permanent=False),
    ),
    # Design system documentation
    path(
        "design/",
        TemplateView.as_view(template_name="design_system.html"),
        name="design_system",
    ),
    # Favicon redirect to prevent 404 errors
    path(
        "favicon.ico",
        RedirectView.as_view(url="/static/images/favicon.svg", permanent=True),
    ),
    # SciTeX API v1
    # path("api/", include("apps.api.urls")),  # API app removed
    # Commented out - reference_sync_app not in INSTALLED_APPS
    # path(
    #     "api/reference-sync/",
    #     include(
    #         "apps.reference_sync_app.api_urls", namespace="reference_sync_api"
    #     ),
    # ),
    # Cloud app URLs (includes landing page and auth)
    path("", include("apps.cloud_app.urls", namespace="cloud_app")),
    
    # GitHub-style username/project URLs (MUST be last to avoid conflicts)
    path("<str:username>/", include("apps.project_app.user_urls")),
]

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
