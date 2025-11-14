#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-14 20:15:00 (ywatanabe)"
# File: ./apps/workspace_app/urls.py

from django.urls import path
from . import views

app_name = 'workspace_app'

urlpatterns = [
    path('', views.workspace_dashboard, name='dashboard'),
    path('start/', views.start_workspace, name='start'),
    path('stop/', views.stop_workspace, name='stop'),
    path('api/status/', views.workspace_status_api, name='status_api'),
    path('api/exec/', views.exec_command, name='exec'),
]

# EOF
