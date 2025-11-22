#!/usr/bin/env python3
"""
Services package for SciTeX-Code application.
Contains business logic and service classes.
"""

# Services are imported on-demand to avoid circular dependencies
# Import specific services as needed using:
# from apps.code_app.services.jupyter_service import NotebookManager
# from apps.code_app.services.environment_manager import EnvironmentManager
# from apps.code_app.services.visualization_pipeline import VisualizationPipeline

__all__ = [
    "jupyter_service",
    "environment_manager",
    "visualization_pipeline",
]
