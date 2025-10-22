"""
Views package for workspace_app.
Exports all view functions for use in urls.py
"""

from .core_views import (
    landing,
    index,
    dashboard_react_tree,
    about,
    contact,
    privacy_policy,
    terms_of_use,
    cookie_policy,
    document_list,
    project_list,
    monitoring,
    monitoring_data,
    create_example_project,
    copy_project,
)

__all__ = [
    'landing',
    'index',
    'dashboard_react_tree',
    'about',
    'contact',
    'privacy_policy',
    'terms_of_use',
    'cookie_policy',
    'document_list',
    'project_list',
    'monitoring',
    'monitoring_data',
    'create_example_project',
    'copy_project',
]
