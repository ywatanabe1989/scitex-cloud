#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:00:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/auth_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/auth_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.urls import path

from . import views
from . import api_views

app_name = "auth_app"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("signin/", views.login_view, name="signin"),  # Primary signin endpoint
    path("login/", views.login_view, name="login"),  # Backward compatibility redirect
    path("logout/", views.logout_view, name="logout"),
    path("signout/", views.logout_view, name="signout"),  # Alternative signout endpoint
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        views.reset_password,
        name="reset-password",
    ),
    path("verify-email/", views.verify_email, name="verify-email"),
    path("delete-account/", views.delete_account, name="delete-account"),

    # API endpoints for email verification
    path("api/verify-email/", api_views.verify_email_api, name="api-verify-email"),
    path("api/resend-otp/", api_views.resend_otp_api, name="api-resend-otp"),

    # API endpoints for signup validation
    path("api/check-username/", api_views.check_username_availability, name="api-check-username"),

    # API endpoints for theme preferences
    path("api/save-theme/", views.api_save_theme_preference, name="api-save-theme"),
    path("api/get-theme/", views.api_get_theme_preference, name="api-get-theme"),
]

# EOF
