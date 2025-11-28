#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Project Detail View

Display project details with GitHub-style file browser and README.
"""

from __future__ import annotations
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from ...models import Project, ProjectWatch, ProjectStar, ProjectFork
from ...decorators import project_access_required

logger = logging.getLogger(__name__)


@project_access_required
def project_detail(request, username, slug):
    """
    Project detail page (GitHub-style /<username>/<project>/)

    Supports mode via query parameter:
    - /<username>/<project>/ or ?mode=overview - Project dashboard
    - /<username>/<project>?mode=writer - Writer module (legacy, use /writer/)
    - /<username>/<project>?mode=code - Code module (legacy, use /code/)
    - /<username>/<project>?mode=viz - Viz module (legacy, use /viz/)
    - /<username>/<project>?port=6006 - Proxy to localhost:6006 (services)

    Note: Scholar module now only accessible via /scholar/
    """
    # Special case: if slug matches username, this is a bio/profile README page
    if slug == username:
        from ..users.profile import user_bio_page

        return user_bio_page(request, username)

    # project available in request.project from decorator
    project = request.project

    # Check for port proxy request (e.g., ?port=6006)
    port_param = request.GET.get("port")
    if port_param:
        try:
            port = int(port_param)
            from ...utils.port_proxy import get_port_proxy_manager

            proxy_manager = get_port_proxy_manager()
            return proxy_manager.proxy_request(request, port)
        except ValueError:
            from django.http import HttpResponse
            return HttpResponse(
                f"Invalid port parameter: {port_param}",
                status=400,
                content_type='text/plain'
            )
        except Exception as e:
            from django.http import HttpResponse
            logger.error(f"Port proxy error: {e}", exc_info=True)
            return HttpResponse(
                f"Proxy error: {str(e)}",
                status=500,
                content_type='text/plain'
            )

    mode = request.GET.get("mode", "overview")
    view = request.GET.get("view", "default")

    # Track last active repository for this user
    if request.user.is_authenticated and hasattr(request.user, "profile"):
        if request.user.profile.last_active_repository != project:
            request.user.profile.last_active_repository = project
            request.user.profile.save(update_fields=["last_active_repository"])

    # Handle concatenated view
    if view == "concatenated":
        from ..api_views import api_concatenate_directory

        return api_concatenate_directory(request, username, slug, "")

    # Route to appropriate module based on mode
    if mode == "writer":
        from apps.writer_app import views as writer_views

        return writer_views.project_writer(request, project.id)
    elif mode == "code":
        from apps.code_app import views as code_views

        return code_views.project_code(request, project.id)
    elif mode == "viz":
        from apps.viz_app import views as viz_views

        return viz_views.project_viz(request, project.id)

    # Default mode: overview - GitHub-style file browser with README
    # Get project directory and file list
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    # Get root directory files (like GitHub)
    files = []
    dirs = []
    readme_content = None
    readme_html = None

    if project_path and project_path.exists():
        try:
            # Helper function to get git commit info for a file/folder
            def get_git_info(path):
                """Get last commit message, author, hash, and time for a file/folder"""
                try:
                    import subprocess

                    # Get last commit for this file (including hash)
                    result = subprocess.run(
                        [
                            "git",
                            "log",
                            "-1",
                            "--format=%an|%ar|%s|%h",
                            "--",
                            str(path.name),
                        ],
                        cwd=project_path,
                        capture_output=True,
                        text=True,
                        timeout=5,
                    )

                    if result.returncode == 0 and result.stdout.strip():
                        author, time_ago, message, commit_hash = (
                            result.stdout.strip().split("|", 3)
                        )
                        return {
                            "author": author,
                            "time_ago": time_ago,
                            "message": message[:80],  # Truncate to 80 chars
                            "hash": commit_hash,
                        }
                except Exception as e:
                    logger.debug(f"Error getting git info for {path}: {e}")

                return {"author": "", "time_ago": "", "message": "", "hash": ""}

            for item in project_path.iterdir():
                # Show all files including dotfiles
                git_info = get_git_info(item)

                if item.is_file():
                    files.append(
                        {
                            "name": item.name,
                            "path": str(item.relative_to(project_path)),
                            "size": item.stat().st_size,
                            "modified": item.stat().st_mtime,
                            "author": git_info.get("author", ""),
                            "time_ago": git_info.get("time_ago", ""),
                            "message": git_info.get("message", ""),
                            "hash": git_info.get("hash", ""),
                        }
                    )
                elif item.is_dir():
                    dirs.append(
                        {
                            "name": item.name,
                            "path": str(item.relative_to(project_path)),
                            "author": git_info.get("author", ""),
                            "time_ago": git_info.get("time_ago", ""),
                            "message": git_info.get("message", ""),
                            "hash": git_info.get("hash", ""),
                        }
                    )

            # Read README.md if exists and convert to HTML
            readme_path = project_path / "README.md"
            if readme_path.exists():
                readme_content = readme_path.read_text(encoding="utf-8")
                # Convert markdown to HTML
                import markdown

                readme_html = markdown.markdown(
                    readme_content,
                    extensions=["fenced_code", "tables", "nl2br"],
                )
        except Exception:
            pass

    # Sort: directories first, then files
    dirs.sort(key=lambda x: x["name"].lower())
    files.sort(key=lambda x: x["name"].lower())

    # Get branches for branch selector
    branches = []
    current_branch = project.current_branch or "develop"
    if project_path and project_path.exists():
        try:
            import subprocess

            result = subprocess.run(
                ["git", "branch", "-a"],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5,
            )
            if result.returncode == 0:
                for line in result.stdout.split("\n"):
                    line = line.strip()
                    if line:
                        # Remove * prefix and remotes/origin/ prefix
                        branch = line.replace("*", "").strip()
                        branch = branch.replace("remotes/origin/", "")
                        if branch and branch not in branches:
                            branches.append(branch)
                        # Check if this is the current branch
                        if line.startswith("*"):
                            current_branch = branch
        except Exception as e:
            logger.debug(f"Error getting branches: {e}")

    if not branches:
        branches = [current_branch]

    # Get social interaction counts
    watch_count = ProjectWatch.objects.filter(project=project).count()
    star_count = ProjectStar.objects.filter(project=project).count()
    fork_count = ProjectFork.objects.filter(original_project=project).count()

    # Check if current user has watched/starred the project
    is_watching = False
    is_starred = False
    if request.user.is_authenticated:
        is_watching = ProjectWatch.objects.filter(
            user=request.user, project=project
        ).exists()
        is_starred = ProjectStar.objects.filter(
            user=request.user, project=project
        ).exists()

    # Get Gitea URLs for clone button
    from django.conf import settings
    gitea_url = getattr(settings, 'SCITEX_CLOUD_GITEA_URL', 'http://127.0.0.1:3000')
    gitea_ssh_domain = getattr(settings, 'SCITEX_CLOUD_GIT_DOMAIN', '127.0.0.1')
    gitea_ssh_port = getattr(settings, 'SCITEX_CLOUD_GITEA_SSH_PORT', '2222')

    gitea_https_url = f"{gitea_url}/{project.owner.username}/{project.slug}.git"
    # Use SSH URI format with explicit port: ssh://user@host:port/path
    gitea_ssh_url = f"ssh://git@{gitea_ssh_domain}:{gitea_ssh_port}/{project.owner.username}/{project.slug}.git"
    download_zip_url = f"{gitea_url}/{project.owner.username}/{project.slug}/archive/{current_branch}.zip"

    context = {
        "project": project,
        "user": request.user,
        "directories": dirs,
        "files": files,
        "readme_content": readme_content,
        "readme_html": readme_html,
        "mode": mode,
        "branches": branches,
        "current_branch": current_branch,
        "watch_count": watch_count,
        "star_count": star_count,
        "fork_count": fork_count,
        "is_watching": is_watching,
        "is_starred": is_starred,
        "gitea_https_url": gitea_https_url,
        "gitea_ssh_url": gitea_ssh_url,
        "download_zip_url": download_zip_url,
    }
    return render(request, "project_app/repository/browse.html", context)


@login_required
def project_detail_redirect(request, pk=None, slug=None):
    """Redirect old URLs to new username/project URLs for backward compatibility"""
    if pk:
        # Redirect from /projects/id/123/ to /username/project-name/
        project = get_object_or_404(Project, pk=pk, owner=request.user)
        return redirect(
            "project_app:detail",
            username=project.owner.username,
            slug=project.slug,
            permanent=True,
        )
    elif slug:
        # Redirect from /projects/project-name/ to /username/project-name/
        project = get_object_or_404(Project, slug=slug, owner=request.user)
        return redirect(
            "project_app:detail",
            username=project.owner.username,
            slug=project.slug,
            permanent=True,
        )
    else:
        return redirect("project_app:list")


# EOF
