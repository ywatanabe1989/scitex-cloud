"""
Code Workspace API Views - File operations for the simple editor.
"""

import json
import logging
import subprocess
from pathlib import Path

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from apps.project_app.models import Project
from apps.project_app.services.git_status import get_git_status, get_file_diff
from apps.project_app.services.git_service import git_commit_and_push

logger = logging.getLogger(__name__)


@require_http_methods(["GET"])
def api_get_file_content(request, file_path):
    """Get file content for editing."""
    project_id = request.GET.get("project_id")
    
    if not project_id:
        return JsonResponse({"error": "project_id required"}, status=400)
    
    try:
        project = Project.objects.select_related("owner").get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)
    
    # Check permissions
    if not (
        request.user == project.owner
        or request.user in project.collaborators.all()
        or project.visibility == "public"
    ):
        return JsonResponse({"error": "Unauthorized"}, status=403)
    
    try:
        file_full_path = Path(project.git_clone_path) / file_path
        
        # Security check
        if not str(file_full_path.resolve()).startswith(
            str(Path(project.git_clone_path).resolve())
        ):
            return JsonResponse({"error": "Invalid file path"}, status=400)
        
        if not file_full_path.exists():
            return JsonResponse({"error": "File not found"}, status=404)
        
        if not file_full_path.is_file():
            return JsonResponse({"error": "Not a file"}, status=400)
        
        with open(file_full_path, "r", encoding="utf-8") as f:
            content = f.read()
        
        return JsonResponse({
            "success": True,
            "content": content,
            "path": file_path,
            "language": _detect_language(file_path),
        })
    
    except UnicodeDecodeError:
        return JsonResponse(
            {"error": "Binary file cannot be edited"}, status=400
        )
    except Exception as e:
        logger.error(f"Error reading file {file_path}: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_save_file(request):
    """Save file content."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        file_path = data.get("path")
        content = data.get("content")

        if not project_id or not file_path or content is None:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)
        
        file_full_path = Path(project.git_clone_path) / file_path
        
        # Security check
        if not str(file_full_path.resolve()).startswith(
            str(Path(project.git_clone_path).resolve())
        ):
            return JsonResponse({"error": "Invalid file path"}, status=400)
        
        file_full_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_full_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # Git auto-commit
        try:
            from apps.project_app.services.git_service import auto_commit_file
            
            commit_message = f"Code: Updated {Path(file_path).name}"
            success, output = auto_commit_file(
                project_dir=Path(project.git_clone_path),
                filepath=file_path,
                message=commit_message,
            )
            
            if success:
                logger.info(f"✓ Auto-committed: {file_path}")
        except Exception as e:
            logger.warning(f"Git commit failed (non-critical): {e}")
        
        return JsonResponse({
            "success": True,
            "message": "File saved successfully",
            "path": file_path
        })
    
    except Exception as e:
        logger.error(f"Error saving file: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_execute_script(request):
    """Execute a Python script."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        file_path = data.get("path")
        args = data.get("args", [])

        if not project_id or not file_path:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        file_full_path = Path(project.git_clone_path) / file_path

        # Security checks
        if not str(file_full_path.resolve()).startswith(
            str(Path(project.git_clone_path).resolve())
        ):
            return JsonResponse({"error": "Invalid file path"}, status=400)

        if not file_full_path.exists():
            return JsonResponse({"error": "File not found"}, status=404)

        if file_full_path.suffix != ".py":
            return JsonResponse(
                {"error": "Only Python files can be executed"}, status=400
            )

        result = subprocess.run(
            ["python", str(file_full_path)] + args,
            cwd=file_full_path.parent,
            capture_output=True,
            text=True,
            timeout=300,
        )

        return JsonResponse({
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "path": file_path,
        })

    except subprocess.TimeoutExpired:
        return JsonResponse(
            {"error": "Script execution timed out (5 min limit)"}, status=408
        )
    except Exception as e:
        logger.error(f"Error executing script: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_execute_command(request):
    """Execute a bash command in user's home directory context."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        command = data.get("command", "").strip()

        if not project_id or not command:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Security: Block dangerous commands
        dangerous_commands = ['rm -rf /', 'dd', 'mkfs', ':(){:|:&};:', 'chmod -R 777 /']
        if any(dangerous in command for dangerous in dangerous_commands):
            return JsonResponse(
                {"error": "Dangerous command blocked"}, status=403
            )

        # Get user info and project directory
        import os
        username = project.owner.username
        # Use /home/username as home dir (standard Linux path)
        home_dir = f"/home/{username}"
        project_dir = Path(project.git_clone_path)

        # Set up environment to feel like user's terminal
        env = os.environ.copy()
        env['HOME'] = home_dir
        env['USER'] = username
        env['LOGNAME'] = username
        env['PWD'] = str(project_dir)
        env['HOSTNAME'] = 'scitex-cloud'
        env['TERM'] = 'xterm-256color'  # Enable terminal features like clear

        # SciTeX Cloud Code-specific env vars for scitex.plt auto-detection
        env['SCITEX_CLOUD_CODE_WORKSPACE'] = 'true'  # Marker for scitex.plt
        env['SCITEX_CLOUD_CODE_BACKEND'] = 'inline'  # Use inline plotting in terminal
        env['SCITEX_CLOUD_CODE_SESSION_ID'] = str(project.id)  # Session tracking
        env['SCITEX_CLOUD_CODE_PROJECT_ROOT'] = str(project_dir)  # Project root
        env['SCITEX_CLOUD_CODE_USERNAME'] = username  # Username for debugging

        # Remove other sensitive Django env vars from user's view
        sensitive_vars = [k for k in env.keys() if (k.startswith('DJANGO_') or 'SECRET' in k or 'PASSWORD' in k or 'API_KEY' in k) and not k.startswith('SCITEX_')]
        for var in sensitive_vars:
            env.pop(var, None)

        # Execute command in project directory (like cd ~/proj/project-name)
        result = subprocess.run(
            command,
            shell=True,
            cwd=str(project_dir),
            capture_output=True,
            text=True,
            timeout=30,
            env=env,
        )

        return JsonResponse({
            "success": result.returncode == 0,
            "returncode": result.returncode,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "cwd": str(project_dir),
        })

    except subprocess.TimeoutExpired:
        return JsonResponse(
            {"error": "Command timed out (30 sec limit)"}, status=408
        )
    except Exception as e:
        logger.error(f"Error executing command: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_create_file(request):
    """Create a new file."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        file_path = data.get("path")
        content = data.get("content", "")

        if not project_id or not file_path:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        file_full_path = Path(project.git_clone_path) / file_path

        # Security check
        if not str(file_full_path.resolve()).startswith(
            str(Path(project.git_clone_path).resolve())
        ):
            return JsonResponse({"error": "Invalid file path"}, status=400)

        # Check if file already exists
        if file_full_path.exists():
            return JsonResponse({"error": "File already exists"}, status=400)

        # Create parent directories if needed
        file_full_path.parent.mkdir(parents=True, exist_ok=True)

        # Create file
        with open(file_full_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Git auto-commit
        try:
            from apps.project_app.services.git_service import auto_commit_file

            commit_message = f"Code: Created {Path(file_path).name}"
            auto_commit_file(
                project_dir=Path(project.git_clone_path),
                filepath=file_path,
                message=commit_message,
            )
        except Exception as e:
            logger.warning(f"Git commit failed (non-critical): {e}")

        return JsonResponse({
            "success": True,
            "message": "File created successfully",
            "path": file_path
        })

    except Exception as e:
        logger.error(f"Error creating file: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_delete_file(request):
    """Delete a file or folder."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        file_path = data.get("path")

        if not project_id or not file_path:
            return JsonResponse({"error": "Missing required fields"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        file_full_path = Path(project.git_clone_path) / file_path

        # Security check
        if not str(file_full_path.resolve()).startswith(
            str(Path(project.git_clone_path).resolve())
        ):
            return JsonResponse({"error": "Invalid file path"}, status=400)

        if not file_full_path.exists():
            return JsonResponse({"error": "File/folder not found"}, status=404)

        # Delete file or folder
        import shutil
        if file_full_path.is_dir():
            shutil.rmtree(file_full_path)
        else:
            file_full_path.unlink()

        # Git auto-commit
        try:
            from apps.project_app.services.git_service import auto_commit_file

            commit_message = f"Code: Deleted {Path(file_path).name}"
            auto_commit_file(
                project_dir=Path(project.git_clone_path),
                filepath=file_path,
                message=commit_message,
            )
        except Exception as e:
            logger.warning(f"Git commit failed (non-critical): {e}")

        return JsonResponse({
            "success": True,
            "message": "Deleted successfully",
            "path": file_path
        })

    except Exception as e:
        logger.error(f"Error deleting: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


def _detect_language(file_path):
    """Detect programming language from file extension."""
    ext_to_lang = {
        ".py": "python",
        ".js": "javascript",
        ".ts": "typescript",
        ".sh": "shell",
        ".bash": "shell",
        ".r": "r",
        ".R": "r",
        ".jl": "julia",
        ".yaml": "yaml",
        ".yml": "yaml",
        ".json": "json",
        ".md": "markdown",
        ".tex": "latex",
        ".bib": "bibtex",  # BibTeX files
        ".html": "html",
        ".css": "css",
        ".txt": "plaintext",
    }

    suffix = Path(file_path).suffix
    return ext_to_lang.get(suffix, "plaintext")


@require_http_methods(["GET"])
def api_get_git_status(request):
    """Get git status for all files in the project."""
    project_id = request.GET.get("project_id")

    if not project_id:
        return JsonResponse({"error": "project_id required"}, status=400)

    try:
        project = Project.objects.select_related("owner").get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)

    # Check permissions
    if not (
        request.user == project.owner
        or request.user in project.collaborators.all()
        or project.visibility == "public"
    ):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        statuses = get_git_status(Path(project.git_clone_path))

        # Convert to JSON-serializable format
        status_dict = {}
        for path, status_obj in statuses.items():
            status_dict[path] = {
                "status": status_obj.status,
                "staged": status_obj.staged
            }

        return JsonResponse({
            "success": True,
            "statuses": status_dict
        })

    except Exception as e:
        logger.error(f"Error getting git status: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
def api_get_file_diff(request, file_path):
    """Get line-level diff for a specific file."""
    project_id = request.GET.get("project_id")

    if not project_id:
        return JsonResponse({"error": "project_id required"}, status=400)

    try:
        project = Project.objects.select_related("owner").get(id=project_id)
    except Project.DoesNotExist:
        return JsonResponse({"error": "Project not found"}, status=404)

    # Check permissions
    if not (
        request.user == project.owner
        or request.user in project.collaborators.all()
        or project.visibility == "public"
    ):
        return JsonResponse({"error": "Unauthorized"}, status=403)

    try:
        diffs = get_file_diff(Path(project.git_clone_path), file_path)

        # Convert to JSON-serializable format
        diff_list = []
        for diff in diffs:
            diff_list.append({
                "line": diff.line_number,
                "status": diff.status
            })

        return JsonResponse({
            "success": True,
            "diffs": diff_list,
            "path": file_path
        })

    except Exception as e:
        logger.error(f"Error getting file diff for {file_path}: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["POST"])
def api_git_commit(request):
    """Commit changes to git."""
    try:
        data = json.loads(request.body)
        project_id = data.get("project_id")
        message = data.get("message", "")
        push = data.get("push", True)

        if not project_id or not message:
            return JsonResponse({"error": "project_id and message required"}, status=400)

        project = Project.objects.select_related("owner").get(id=project_id)

        # Check permissions (allow authenticated users and visitors with allocated project)
        if request.user.is_authenticated:
            has_access = (
                request.user == project.owner
                or request.user in project.collaborators.all()
            )
        else:
            # For anonymous users, check if this is their allocated visitor project
            visitor_project_id = request.session.get("visitor_project_id")
            has_access = (visitor_project_id and project.id == visitor_project_id)

        if not has_access:
            return JsonResponse({"error": "Unauthorized"}, status=403)

        # Commit all changes
        success, output = git_commit_and_push(
            project_dir=Path(project.git_clone_path),
            message=message,
            files=None,  # Commit all changes
            branch="develop",
            push=push,
        )

        if success:
            return JsonResponse({
                "success": True,
                "message": output,
            })
        else:
            return JsonResponse({
                "success": False,
                "error": output,
            }, status=400)

    except Exception as e:
        logger.error(f"Error committing changes: {e}", exc_info=True)
        return JsonResponse({"error": str(e)}, status=500)
