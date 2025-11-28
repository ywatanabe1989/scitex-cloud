"""
Project Operations Module

This module handles project directory operations including:
- Project directory creation and deletion
- Template-based project initialization
- Storage usage tracking
- Project directory path resolution

Extracted from project_filesystem.py for better modularity.
"""

import shutil
from pathlib import Path
from typing import Optional, Tuple

from django.conf import settings

from .core import ProjectFilesystemManager
from ...models import Project


class ProjectOpsManager(ProjectFilesystemManager):
    """Manages project-level directory operations."""

    def create_project_directory(
        self,
        project: Project,
        use_template: bool = False,
        template_type: str = "research",
    ) -> Tuple[bool, Optional[Path]]:
        """
        Create directory structure for a new repository.

        Path: ./data/users/{username}/{project-slug}/

        Args:
            project: Project instance
            use_template: If True, create full template structure. If False, create empty directory.
            template_type: Type of template to use ('research', 'pip_project', 'singularity')
        """
        try:
            project_slug = project.slug  # Use the generated slug

            # Minimal structure: ./data/users/{username}/{project-slug}/
            project_path = self.base_path / project_slug

            # Ensure user base directory exists
            if not self._ensure_directory(self.base_path):
                return False, None

            # If template requested, try to copy from scitex template
            if use_template and self._copy_from_example_template(
                project_path, project, template_type
            ):
                # Update project with directory info
                project.data_location = str(project_path.relative_to(self.base_path))
                project.directory_created = True
                project.save()
                return True, project_path

            # Create empty project root directory
            if not self._ensure_directory(project_path):
                return False, None

            # Only create basic README for empty projects
            self._create_minimal_readme(project, project_path)

            # Note: .scitex_project.json removed - metadata already in database
            # self._create_project_metadata(project, project_path)

            # Update project model with directory path
            project.data_location = str(project_path.relative_to(self.base_path))
            project.directory_created = True
            project.save()

            return True, project_path
        except Exception as e:
            print(f"Error creating project directory: {e}")
            return False, None

    def create_project_from_template(
        self, project: Project, template_type: str = "research"
    ) -> Tuple[bool, Optional[Path]]:
        """
        Create full template structure for an existing project.
        This can be called when user clicks "Create from template" button.

        Args:
            project: Project instance
            template_type: Type of template ('research', 'pip_project', or 'singularity')
        """
        import logging

        logger = logging.getLogger(__name__)

        try:
            project_path = self.get_project_root_path(project)
            if not project_path:
                error_msg = (
                    f"Project directory not found for {project.slug}. "
                    f"Expected at: {self.base_path / project.slug}. "
                    f"This usually means the Git repository wasn't cloned successfully. "
                    f"Please check Gitea integration and try again."
                )
                logger.error(error_msg)
                raise RuntimeError(error_msg)

            # Try to use scitex template if available
            if self._copy_from_example_template(project_path, project, template_type):
                return True, project_path

            # Fallback: Create manual structure if scitex template fails
            # Create project subdirectories with scientific workflow structure
            for main_dir, sub_structure in self.PROJECT_STRUCTURE.items():
                main_path = project_path / main_dir
                if not self._ensure_directory(main_path):
                    raise RuntimeError(f"Failed to create directory: {main_path}")

                # Create additional subdirectories under scripts for scientific workflow
                if main_dir == "scripts":
                    script_subdirs = [
                        "analysis",
                        "preprocessing",
                        "modeling",
                        "visualization",
                        "utils",
                    ]
                    for subdir in script_subdirs:
                        if not self._ensure_directory(main_path / subdir):
                            raise RuntimeError(
                                f"Failed to create directory: {main_path / subdir}"
                            )

                if isinstance(sub_structure, dict):
                    # Handle nested structure (like data directory)
                    for sub_dir, sub_sub_dirs in sub_structure.items():
                        sub_path = main_path / sub_dir
                        if not self._ensure_directory(sub_path):
                            raise RuntimeError(
                                f"Failed to create directory: {sub_path}"
                            )

                        for sub_sub_dir in sub_sub_dirs:
                            if not self._ensure_directory(sub_path / sub_sub_dir):
                                raise RuntimeError(
                                    f"Failed to create directory: {sub_path / sub_sub_dir}"
                                )
                elif isinstance(sub_structure, list):
                    # Handle simple list structure
                    for sub_dir in sub_structure:
                        if not self._ensure_directory(main_path / sub_dir):
                            raise RuntimeError(
                                f"Failed to create directory: {main_path / sub_dir}"
                            )

            # Update README with full template info
            self._create_project_readme(project, project_path)

            # Create project configuration files
            self._create_project_config_files(project, project_path)

            # Create requirements.txt
            self._create_requirements_file(project, project_path)

            return True, project_path
        except Exception as e:
            logger.error(f"Error creating project from template: {e}", exc_info=True)
            raise  # Re-raise so the view can catch and display it

    def get_project_root_path(self, project: Project) -> Optional[Path]:
        """Get the root directory path for a project.

        Always uses filesystem as the source of truth (data/users/{username}/{project-slug}/).
        This ensures Django always shows the actual filesystem state in real-time.
        """
        # Always use project slug - filesystem is the single source of truth
        project_path = self.base_path / project.slug
        if project_path.exists():
            return project_path
        return None

    def delete_project_directory(self, project: Project) -> bool:
        """Delete a project directory and all its contents."""
        try:
            project_path = self.get_project_root_path(project)
            if project_path and project_path.exists():
                shutil.rmtree(project_path)
            return True
        except Exception as e:
            print(f"Error deleting project directory: {e}")
            return False

    def get_storage_usage(self) -> dict:
        """Get storage usage statistics for the user."""
        try:
            if not self.base_path.exists():
                return {"total_size": 0, "project_count": 0, "file_count": 0}

            total_size = 0
            file_count = 0

            for file_path in self.base_path.rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1

            # Count projects directly under base_path
            project_count = len(
                [
                    p
                    for p in self.base_path.iterdir()
                    if p.is_dir() and not p.name.startswith(".")
                ]
            )

            return {
                "total_size": total_size,
                "total_size_mb": round(total_size / (1024 * 1024), 2),
                "project_count": project_count,
                "file_count": file_count,
            }
        except Exception as e:
            print(f"Error getting storage usage: {e}")
            return {"total_size": 0, "project_count": 0, "file_count": 0}

    def _copy_from_example_template(
        self, project_path: Path, project, template_type: str = "research"
    ) -> bool:
        """
        Copy template structure from local master template (research)
        or clone from GitHub for other templates.

        For research template: Uses fast local copy from /app/templates/research-master
        For other templates: Falls back to git clone from GitHub

        This method copies the complete template structure including:
        - scripts/ directory for analysis and preprocessing
        - data/ directory for raw and processed data
        - docs/ directory for manuscripts and notes
        - results/ directory for analysis outputs
        - config/ directory for project configuration
        - And all other template-specific files and directories

        Args:
            project_path: Path where project will be created
            project: Project instance
            template_type: Type of template ('research', 'pip_project', or 'singularity')
        """
        try:
            # Check if project_path already exists (should not for new projects)
            if project_path.exists():
                print(f"Project path already exists: {project_path}, skipping template creation")
                return False

            # Ensure parent directory exists
            if not project_path.parent.exists():
                project_path.parent.mkdir(parents=True, exist_ok=True)

            # For research template, use local master copy (fast, offline)
            if template_type == "research":
                template_master = Path(getattr(
                    settings,
                    "VISITOR_TEMPLATE_PATH",
                    "/app/templates/research-master"
                ))

                if not template_master.exists():
                    print(f"[ProjectFS] Master template not found at {template_master}, falling back to git clone")
                    # Fall back to git clone if master template not available
                    from scitex.template import clone_research as clone_template
                    success = clone_template(
                        str(project_path),
                        git_strategy=None,
                        branch=None,
                        tag=None
                    )
                else:
                    print(f"[ProjectFS] Copying research template from {template_master} to {project_path}")
                    shutil.copytree(template_master, project_path, symlinks=True)
                    success = True

            # For other template types, use git clone
            else:
                if template_type == "pip_project":
                    from scitex.template import clone_pip_project as clone_template
                elif template_type == "singularity":
                    from scitex.template import clone_singularity as clone_template
                else:
                    print(f"Unknown template type: {template_type}, defaulting to research")
                    from scitex.template import clone_research as clone_template

                print(f"Cloning {template_type} template from GitHub to {project_path}...")
                success = clone_template(
                    str(project_path),
                    git_strategy=None,  # Don't initialize git (will be handled by Django/Gitea)
                    branch=None,
                    tag=None
                )

            if not success:
                print(f"Failed to create {template_type} template at {project_path}")
                return False

            # Customize copied template for this project
            self._customize_template_for_project(project_path, project, template_type)

            print(f"Successfully created {template_type} template at {project_path}")
            return True

        except ImportError as e:
            print(f"scitex package not available: {e}")
            print("Fallback: Project will be created with basic structure")
            return False
        except Exception as e:
            print(f"Error creating {template_type} project template: {e}")
            return False

    def _customize_template_for_project(
        self, project_path: Path, project, template_type: str = "research"
    ):
        """Customize the copied template with project-specific information."""
        try:
            # Update README.md with project info
            readme_path = project_path / "README.md"
            if readme_path.exists():
                readme_content = readme_path.read_text()
                # Replace template placeholders with actual project info
                readme_content = readme_content.replace(
                    "# SciTeX Example Research Project", f"# {project.name}"
                )
                readme_content = readme_content.replace(
                    "This is an example research project",
                    f"{project.description or 'Research project created with SciTeX Cloud'}",
                )
                readme_path.write_text(readme_content)

            # Update paper title in LaTeX files if they exist
            paper_dir = project_path / "paper"
            if paper_dir.exists():
                # Update manuscript title
                title_file = paper_dir / "manuscript" / "src" / "title.tex"
                if title_file.exists():
                    title_file.write_text(f"\\title{{{project.name}}}")

                # Update author
                author_file = paper_dir / "manuscript" / "src" / "authors.tex"
                if author_file.exists() and project.owner:
                    author_name = (
                        project.owner.get_full_name() or project.owner.username
                    )
                    author_file.write_text(f"\\author{{{author_name}}}")

            print(f"Customized template for project: {project.name}")

        except Exception as e:
            print(f"Error customizing template: {e}")


def ensure_project_directory(project: Project) -> bool:
    """Ensure a project has a directory structure."""
    from .manager import get_project_filesystem_manager

    manager = get_project_filesystem_manager(project.owner)

    # Check if project already has a directory
    if not manager.get_project_root_path(project):
        success, path = manager.create_project_directory(project)
        return success

    return True
