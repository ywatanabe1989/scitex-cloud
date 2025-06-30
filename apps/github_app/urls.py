#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub Integration URL Configuration

URL patterns for GitHub repository integration with SciTeX Code module.
"""

from django.urls import path
from . import views

app_name = 'github_app'

urlpatterns = [
    # Main dashboard
    path('', views.github_dashboard, name='dashboard'),
    
    # Authentication
    path('connect/', views.github_connect, name='connect'),
    path('callback/', views.github_callback, name='callback'),
    path('disconnect/', views.github_disconnect, name='disconnect'),
    
    # Profile and sync
    path('sync/profile/', views.sync_profile, name='sync_profile'),
    path('sync/repositories/', views.sync_repositories, name='sync_repositories'),
    path('sync/full/', views.full_sync, name='full_sync'),
    path('settings/', views.profile_settings, name='profile_settings'),
    
    # Repositories
    path('repositories/', views.repositories_list, name='repositories'),
    path('repositories/<uuid:repository_id>/', views.repository_detail, name='repository_detail'),
    path('repositories/<uuid:repository_id>/connect/', views.connect_to_code, name='connect_to_code'),
    path('repositories/<uuid:repository_id>/sync-code/', views.sync_repository_code, name='sync_repository_code'),
    path('repositories/<uuid:repository_id>/sync-collaborators/', views.sync_repository_collaborators, name='sync_repository_collaborators'),
    
    # Logs
    path('logs/', views.sync_logs, name='sync_logs'),
    
    # API endpoints
    path('api/status/', views.api_profile_status, name='api_profile_status'),
    path('api/sync/profile/', views.api_sync_profile, name='api_sync_profile'),
    path('api/sync/repositories/', views.api_sync_repositories, name='api_sync_repositories'),
    path('api/repositories/', views.api_repositories_list, name='api_repositories_list'),
    path('api/logs/', views.api_sync_logs, name='api_sync_logs'),
    
    # Webhooks
    path('webhook/', views.github_webhook, name='webhook'),
]