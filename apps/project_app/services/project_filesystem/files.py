"""
File operations module for ProjectFilesystemManager.

Handles file storage, listing, and project structure operations.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from django.utils.text import slugify
from ..models import Project


def store_document(
    manager,
    document,
    content: str,
    doc_type: str = "manuscripts"
) -> Tuple[bool, Optional[Path]]:
    """Store a document in the appropriate project directory."""
    try:
        if not document.project:
            # Store in temp if no project
            file_path = (
                manager.base_path / "temp" / f"{document.id}_{document.title}.txt"
            )
        else:
            project_path = manager.get_project_root_path(document.project)
            if not project_path:
                return False, None

            # Determine file extension based on document type
            extension = _get_file_extension(document.document_type)
            filename = f"{slugify(document.title)}{extension}"
            file_path = project_path / "documents" / doc_type / filename

        # Ensure parent directory exists
        if not manager._ensure_directory(file_path.parent):
            return False, None

        # Write content to file
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)

        # Update document model with file path
        document.file_location = str(file_path.relative_to(manager.base_path))
        document.save()

        return True, file_path
    except Exception as e:
        print(f"Error storing document: {e}")
        return False, None


def store_file(
    manager,
    project: Project,
    file_content: bytes,
    filename: str,
    category: str = "data",
) -> Tuple[bool, Optional[Path]]:
    """Store a file in the project directory."""
    try:
        project_path = manager.get_project_root_path(project)
        if not project_path:
            return False, None

        # Determine subcategory based on file type
        subcategory = _get_subcategory(filename, category)
        file_path = project_path / category / subcategory / filename

        # Ensure parent directory exists
        if not manager._ensure_directory(file_path.parent):
            return False, None

        # Write file content
        with open(file_path, "wb") as f:
            f.write(file_content)

        return True, file_path
    except Exception as e:
        print(f"Error storing file: {e}")
        return False, None


def list_project_files(
    manager,
    project: Project,
    category: Optional[str] = None
) -> List[Dict]:
    """List files in a project directory."""
    try:
        project_path = manager.get_project_root_path(project)
        if not project_path or not project_path.exists():
            return []

        files = []
        search_path = project_path / category if category else project_path

        for file_path in search_path.rglob("*"):
            if file_path.is_file():
                stat = file_path.stat()
                files.append(
                    {
                        "name": file_path.name,
                        "path": str(file_path.relative_to(project_path)),
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "category": file_path.parent.parent.name
                        if file_path.parent.parent != project_path
                        else "root",
                        "subcategory": file_path.parent.name
                        if file_path.parent != project_path
                        else "",
                    }
                )

        return sorted(files, key=lambda x: x["modified"], reverse=True)
    except Exception as e:
        print(f"Error listing project files: {e}")
        return []


def get_project_structure(manager, project: Project) -> Dict:
    """Get the complete directory structure for a project."""
    try:
        project_path = manager.get_project_root_path(project)
        if not project_path or not project_path.exists():
            return {}

        def build_tree(path: Path) -> Dict:
            tree = {
                "name": path.name,
                "type": "directory" if path.is_dir() else "file",
                "path": str(path.relative_to(project_path)),
                "children": [],
            }

            if path.is_dir():
                for child in sorted(path.iterdir()):
                    tree["children"].append(build_tree(child))
            else:
                stat = path.stat()
                tree.update(
                    {
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(
                            stat.st_mtime
                        ).isoformat(),
                    }
                )

            return tree

        return build_tree(project_path)
    except Exception as e:
        print(f"Error getting project structure: {e}")
        return {}


def clone_from_git(
    manager,
    project: Project,
    git_url: str,
    use_ssh: bool = True
) -> Tuple[bool, Optional[str]]:
    """
    Clone a Git repository into the project directory.

    Args:
        manager: ProjectFilesystemManager instance
        project: Project instance
        git_url: Git repository URL (works with GitHub, GitLab, Bitbucket, etc.)
        use_ssh: If True and SSH key exists, use SSH for cloning

    Returns:
        Tuple of (success, error_message)
    """
    try:
        import subprocess
        import tempfile
        import shutil
        import os

        project_path = manager.get_project_root_path(project)
        if not project_path or not project_path.exists():
            return False, "Project directory not found"

        # Get SSH environment if available
        env = os.environ.copy()
        ssh_used = False

        if use_ssh:
            from .ssh_manager import SSHKeyManager

            ssh_manager = SSHKeyManager(manager.user)

            if ssh_manager.has_ssh_key():
                env = ssh_manager.get_ssh_env()
                ssh_used = True

        # Strategy: Clone to a temporary directory, then move contents
        # This avoids the "destination path already exists and is not an empty directory" error

        # Create a temporary directory for cloning
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_clone_path = Path(temp_dir) / "repo"

            # Clone the repository into the temporary directory
            result = subprocess.run(
                ["git", "clone", git_url, str(temp_clone_path)],
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout
                env=env,
            )

            if result.returncode != 0:
                error_msg = result.stderr or result.stdout or "Unknown error"
                return False, error_msg

            # Remove any existing files in the project directory (created during initialization)
            for item in project_path.iterdir():
                if item.is_file():
                    item.unlink()
                elif item.is_dir():
                    shutil.rmtree(item)

            # Move all contents from temp clone to project directory
            for item in temp_clone_path.iterdir():
                dest = project_path / item.name
                if item.is_file():
                    shutil.copy2(item, dest)
                elif item.is_dir():
                    shutil.copytree(item, dest)

        # Mark SSH key as used if it was used
        if ssh_used:
            from .ssh_manager import SSHKeyManager

            ssh_manager = SSHKeyManager(manager.user)
            ssh_manager.mark_key_used()

        return True, None

    except subprocess.TimeoutExpired:
        return False, "Git clone operation timed out (max 5 minutes)"
    except FileNotFoundError:
        return False, "Git command not found. Please ensure Git is installed."
    except Exception as e:
        return False, str(e)


def _get_file_extension(doc_type: str) -> str:
    """Get appropriate file extension for document type."""
    extensions = {
        "note": ".md",
        "manuscript": ".tex",
        "paper": ".tex",
        "report": ".md",
        "presentation": ".md",
        "dataset": ".csv",
        "code": ".py",
    }
    return extensions.get(doc_type, ".txt")


def _get_subcategory(filename: str, category: str) -> str:
    """Determine subcategory based on file type and category."""
    extension = Path(filename).suffix.lower()

    if category == "data":
        if extension in [".csv", ".xlsx", ".json", ".xml", ".gz", ".zip"]:
            return "raw"
        elif extension in [".pkl", ".parquet", ".h5", ".npy", ".npz"]:
            return "processed"
        elif extension in [".png", ".jpg", ".jpeg", ".svg", ".pdf"]:
            return "figures"
        elif extension in [".pkl", ".joblib", ".h5", ".pt", ".pth"]:
            return "models"
        else:
            return "raw"
    elif category == "scripts":
        # Scripts go directly in scripts directory, subdirs created as needed
        return ""
    elif category == "docs":
        if extension in [".tex", ".bib"]:
            return "manuscripts"
        elif extension in [".md", ".txt", ".rst"]:
            return "notes"
        else:
            return "references"
    elif category == "results":
        if extension in [".csv", ".json", ".txt"]:
            return "outputs"
        elif extension in [".pdf", ".html"]:
            return "reports"
        else:
            return "analysis"
    elif category == "temp":
        if extension in [".log"]:
            return "logs"
        elif extension in [".tmp", ".temp"]:
            return "tmp"
        else:
            return "cache"
    elif category == "config":
        return ""

    return "misc"
