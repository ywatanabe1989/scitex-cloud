#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/urls.py

from django.urls import path
from . import views

app_name = "docs"

urlpatterns = [
    # Documentation landing page
    path("", views.docs_index, name="index"),

    # Module-specific documentation
    path("scholar/", views.docs_scholar, name="scholar"),
    path("code/", views.docs_code, name="code"),
    path("viz/", views.docs_viz, name="viz"),
    path("writer/", views.docs_writer, name="writer"),

    # Serve specific documentation pages
    path("<str:module>/<path:page>", views.docs_page, name="page"),
]
