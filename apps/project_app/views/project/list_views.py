#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-29"
# File: /home/ywatanabe/proj/scitex-cloud/apps/project_app/views/project/list_views.py
# ----------------------------------------
"""
Project List Views Module

This module contains view functions for project listing and user profiles:
- User profile pages (GitHub-style /<username>/)
- Project listing views
- User overview and project boards
- Starred repositories
"""

from __future__ import annotations
import logging

# Django imports
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import Http404
from django.core.paginator import Paginator
from django.db import models

# Local imports
from ...models import Project

logger = logging.getLogger(__name__)


@login_required
def project_list(request):
    """Redirect to user's personal project page (GitHub-style)"""
    return redirect(f"/{request.user.username}/?tab=repositories")


def user_profile(request, username):
    """
    User profile page (GitHub-style /<username>/)

    Public view - no login required (like GitHub)

    Supports tabs via query parameter:
    - /<username>/ or /<username>?tab=overview - Overview
    - /<username>?tab=repositories - Projects list
    - /<username>?tab=projects - Project boards (future)
    - /<username>?tab=stars - Starred projects
    """
    # Check if username is a reserved path
    from config.urls import RESERVED_PATHS

    if username.lower() in [path.lower() for path in RESERVED_PATHS]:
        raise Http404("This path is reserved and not a valid username")

    user = get_object_or_404(User, username=username)
    tab = request.GET.get("tab", "repositories")  # Default to repositories

    if tab == "repositories":
        return user_project_list(request, username)
    elif tab == "overview":
        return user_overview(request, username)
    elif tab == "projects":
        return user_projects_board(request, username)
    elif tab == "stars":
        return user_stars(request, username)
    else:
        # Invalid tab - redirect to repositories
        return user_project_list(request, username)


def user_project_list(request, username):
    """List a specific user's projects (called from user_profile with tab=repositories)"""
    user = get_object_or_404(User, username=username)

    # Filter projects based on visibility and access
    user_projects = Project.objects.filter(owner=user)

    # If not the owner, only show public projects or projects where user is a collaborator
    if not (request.user.is_authenticated and request.user == user):
        if request.user.is_authenticated:
            # Show public projects + projects where user is a collaborator
            user_projects = user_projects.filter(
                models.Q(visibility="public") | models.Q(memberships__user=request.user)
            ).distinct()
        else:
            # Visitor users only see public projects
            user_projects = user_projects.filter(visibility="public")

    user_projects = user_projects.order_by("-updated_at")

    # Check if this is the current user viewing their own projects
    is_own_projects = request.user.is_authenticated and request.user == user

    # Add pagination
    paginator = Paginator(user_projects, 12)
    page_number = request.GET.get("page")
    projects = paginator.get_page(page_number)

    # Get social stats
    from apps.social_app.models import UserFollow

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "projects": projects,
        "profile_user": user,  # The user whose profile we're viewing
        "is_own_projects": is_own_projects,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "repositories",
        # Note: 'user' is automatically available as request.user in templates
        # Don't override it here - it should always be the logged-in user
    }
    return render(request, "project_app/users/projects.html", context)


def user_bio_page(request, username):
    """User bio/profile README page (GitHub-style /<username>/<username>/)"""
    user = get_object_or_404(User, username=username)

    # Get or create user profile
    from apps.accounts_app.models import UserProfile

    profile, created = UserProfile.objects.get_or_create(user=user)

    # Get user's projects
    projects = Project.objects.filter(owner=user).order_by("-updated_at")[
        :6
    ]  # Show top 6

    # Check if this is the user viewing their own profile
    is_own_profile = request.user.is_authenticated and request.user == user

    context = {
        "profile_user": user,
        "profile": profile,
        "projects": projects,
        "is_own_profile": is_own_profile,
        "total_projects": Project.objects.filter(owner=user).count(),
    }

    return render(request, "project_app/users/bio.html", context)


def user_overview(request, username):
    """User profile overview tab"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get recent activity
    recent_projects = Project.objects.filter(owner=user)
    if not is_own_profile:
        recent_projects = recent_projects.filter(visibility="public")
    recent_projects = recent_projects.order_by("-updated_at")[:6]

    # Get social stats
    from apps.social_app.models import UserFollow

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "recent_projects": recent_projects,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "overview",
    }
    return render(request, "project_app/users/overview.html", context)


def user_projects_board(request, username):
    """User project boards tab (placeholder for future implementation)"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get social stats
    from apps.social_app.models import UserFollow

    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "projects",
    }
    return render(request, "project_app/users/board.html", context)


def user_stars(request, username):
    """User starred repositories tab"""
    user = get_object_or_404(User, username=username)
    is_own_profile = request.user.is_authenticated and request.user == user

    # Get starred repositories
    from apps.social_app.models import RepositoryStar, UserFollow

    starred_repos = (
        RepositoryStar.objects.filter(user=user)
        .select_related("repository")
        .order_by("-created_at")
    )

    # Pagination
    paginator = Paginator(starred_repos, 12)
    page_number = request.GET.get("page")
    stars = paginator.get_page(page_number)

    # Get social stats
    followers_count = UserFollow.get_followers_count(user)
    following_count = UserFollow.get_following_count(user)
    is_following = (
        UserFollow.is_following(request.user, user)
        if request.user.is_authenticated
        else False
    )

    context = {
        "profile_user": user,
        "is_own_profile": is_own_profile,
        "stars": stars,
        "followers_count": followers_count,
        "following_count": following_count,
        "is_following": is_following,
        "active_tab": "stars",
    }
    return render(request, "project_app/users/stars.html", context)


# EOF
