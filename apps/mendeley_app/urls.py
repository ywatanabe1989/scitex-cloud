#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mendeley Integration URL Configuration
"""

from django.urls import path
from . import views

app_name = 'mendeley_app'

urlpatterns = [
    # Dashboard
    path('', views.mendeley_dashboard, name='dashboard'),
    
    # Authentication
    path('connect/', views.mendeley_connect, name='connect'),
    path('callback/', views.mendeley_callback, name='callback'),
    path('disconnect/', views.mendeley_disconnect, name='disconnect'),
    
    # Zotero-specific setup
    path('zotero/setup/', views.zotero_api_key_setup, name='zotero_api_key_setup'),
    
    # Synchronization
    path('sync/profile/', views.sync_profile, name='sync_profile'),
    path('sync/documents/', views.sync_documents, name='sync_documents'),
    path('sync/full/', views.full_sync, name='full_sync'),
    path('sync/logs/', views.sync_logs, name='sync_logs'),
    
    # Documents
    path('documents/', views.documents_list, name='documents'),
    path('documents/<uuid:document_id>/', views.document_detail, name='document_detail'),
    path('documents/<uuid:document_id>/import/', views.import_to_scholar, name='import_to_scholar'),
    path('documents/bulk-import/', views.bulk_import_to_scholar, name='bulk_import_to_scholar'),
    
    # Settings
    path('settings/', views.profile_settings, name='profile_settings'),
    
    # API Endpoints
    path('api/profile/status/', views.api_profile_status, name='api_profile_status'),
    path('api/sync/profile/', views.api_sync_profile, name='api_sync_profile'),
    path('api/sync/documents/', views.api_sync_documents, name='api_sync_documents'),
    path('api/documents/', views.api_documents_list, name='api_documents_list'),
    path('api/sync/logs/', views.api_sync_logs, name='api_sync_logs'),
]