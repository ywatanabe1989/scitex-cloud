#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:00:47 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/public_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import redirect
from django.urls import path

from . import views

app_name = "public_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("cloud/", lambda request: redirect("public_app:index"), name="cloud"),
    # Concept and vision pages
    path("vision/", views.vision, name="vision"),
    path("publications/", views.publications, name="publications"),
    path("contributors/", views.contributors, name="contributors"),
    # Support pages
    path("donate/", views.donate, name="donate"),
    # Legal and contact pages
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("terms/", views.terms_of_use, name="terms"),
    path("cookies/", views.cookie_policy, name="cookies"),
    # Demo page
    path("demo/", views.demo, name="demo"),
    # API Documentation
    path("api-docs/", views.api_docs, name="api-docs"),
    # SciTeX API Key Management
    path("api-keys/", views.scitex_api_keys, name="scitex_api_keys"),
]

# EOF
