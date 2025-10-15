#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/apps.py

from django.apps import AppConfig


class DocsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.docs_app"
    verbose_name = "SciTeX Documentation"
