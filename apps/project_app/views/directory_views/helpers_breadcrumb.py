"""
Breadcrumb Navigation Helpers

Functions for building navigation breadcrumbs.
"""

from __future__ import annotations


def build_breadcrumbs(project, username, slug, file_path):
    """
    Build breadcrumb navigation for file view.

    Args:
        project: Project instance
        username: Project owner username
        slug: Project slug
        file_path: Relative file path

    Returns:
        list: Breadcrumb items with name and url
    """
    breadcrumbs = [{"name": project.name, "url": f"/{username}/{slug}/"}]

    path_parts = file_path.split("/")
    current_path = ""
    for i, part in enumerate(path_parts):
        current_path += part
        if i < len(path_parts) - 1:
            current_path += "/"
            breadcrumbs.append(
                {"name": part, "url": f"/{username}/{slug}/{current_path}"}
            )
        else:
            breadcrumbs.append({"name": part, "url": None})

    return breadcrumbs


def build_directory_breadcrumb(username, slug, directory_path, project_name):
    """
    Build breadcrumb navigation for directory view.

    Args:
        username: Project owner username
        slug: Project slug
        directory_path: Directory path string
        project_name: Project name

    Returns:
        list: Breadcrumb items with name, url, and is_last flag
    """
    breadcrumbs = [
        {"name": project_name, "url": f"/{username}/{slug}/", "is_last": False}
    ]

    path_parts = [p for p in directory_path.split("/") if p]
    current_path = ""
    for idx, part in enumerate(path_parts):
        current_path += part + "/"
        is_last = idx == len(path_parts) - 1
        breadcrumbs.append(
            {
                "name": part,
                "url": f"/{username}/{slug}/{current_path}",
                "is_last": is_last,
            }
        )

    return breadcrumbs
