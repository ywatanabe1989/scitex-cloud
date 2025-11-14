#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-14 17:45:00 (ywatanabe)"
# File: ./apps/workspace_app/admin.py

from django.contrib import admin
from .models import UserWorkspace


@admin.register(UserWorkspace)
class UserWorkspaceAdmin(admin.ModelAdmin):
    list_display = [
        'user',
        'is_running',
        'container_name',
        'last_activity_at',
        'created_at',
    ]
    list_filter = ['is_running', 'created_at']
    search_fields = ['user__username', 'container_name']
    readonly_fields = [
        'container_id',
        'last_started_at',
        'last_stopped_at',
        'last_activity_at',
        'created_at',
        'updated_at',
    ]

# EOF
