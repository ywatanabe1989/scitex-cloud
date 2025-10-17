#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 01:47:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/dev_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/dev_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.urls import path

from . import views
from .views import DesignSystemView

app_name = "dev_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("design/", DesignSystemView.as_view(), name="design"),
]

# EOF
