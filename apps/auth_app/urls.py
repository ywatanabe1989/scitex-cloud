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

app_name = "auth_app"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        views.reset_password,
        name="reset-password",
    ),
    path("verify-email/", views.verify_email, name="verify-email"),
]

# EOF
