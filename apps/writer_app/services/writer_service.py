"""
Django wrapper service for scitex.writer.Writer.

Provides convenient methods for Django views to interact with Writer instances.
Handles project directory management and caching.
"""

from pathlib import Path
from typing import Optional
from django.conf import settings
from scitex.writer import Writer
from scitex import logging

logger = logging.getLogger(__name__)


class WriterService:
    """Service to manage Writer instances for Django projects."""

    def __init__(self, project_id: int, user_id: int):
        """Initialize WriterService for a specific project.

        Args:
            project_id: Django Project ID
            user_id: Django User ID
        """
        self.project_id = project_id
        self.user_id = user_id
        self._writer = None
        self._project_path = None

    @property
    def project_path(self) -> Path:
        """Get or calculate the project path."""
        if self._project_path is None:
            from apps.project_app.models import Project
            from apps.project_app.services.project_filesystem import (
                get_project_filesystem_manager,
            )

            try:
                project = Project.objects.get(id=self.project_id)
                manager = get_project_filesystem_manager(project.owner)
                project_root = manager.get_project_root_path(project)
                self._project_path = project_root / "scitex" / "writer"
            except Project.DoesNotExist:
                raise RuntimeError(f"Project {self.project_id} not found")

        return self._project_path

    @property
    def writer(self) -> Writer:
        """Get or create Writer instance (lazy loading).

        Returns:
            Writer instance for this project
        """
        if self._writer is None:
            from apps.project_app.models import Project

            project = Project.objects.get(id=self.project_id)
            logger.info(f"WriterService: Creating Writer instance for project {self.project_id} at {self.project_path}")
            try:
                self._writer = Writer(
                    self.project_path,
                    name=project.name,
                    git_strategy="child",  # Isolated git per project
                )
                logger.info(f"WriterService: Writer instance created successfully")
            except Exception as e:
                logger.error(f"WriterService: Failed to create Writer instance: {e}", exc_info=True)
                raise RuntimeError(f"Failed to initialize Writer: {e}") from e

        return self._writer

    # ===== Section Operations =====

    def read_section(self, section_name: str, doc_type: str = "manuscript") -> str:
        """Read a section from manuscript/supplementary/revision.

        Args:
            section_name: Section name (e.g., 'introduction', 'abstract')
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Section content as string
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            content = section.read()

            # Convert to string if it's a list (from scitex.io.load)
            if isinstance(content, list):
                content = '\n'.join(content)
            elif content is None:
                content = ""

            return content
        except Exception as e:
            logger.error(f"Error reading section {section_name}: {e}")
            raise

    def write_section(
        self, section_name: str, content: str, doc_type: str = "manuscript"
    ) -> bool:
        """Write content to a section.

        Args:
            section_name: Section name
            content: Section content
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            return section.write(content)
        except Exception as e:
            logger.error(f"Error writing section {section_name}: {e}")
            raise

    def commit_section(
        self, section_name: str, message: str, doc_type: str = "manuscript"
    ) -> bool:
        """Commit changes to a section.

        Args:
            section_name: Section name
            message: Commit message
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            return section.commit(message)
        except Exception as e:
            logger.error(f"Error committing section {section_name}: {e}")
            raise

    # ===== Compilation Operations =====

    def compile_preview(self, latex_content: str, timeout: int = 60) -> dict:
        """Compile a quick preview of provided LaTeX content (not from workspace).

        This is used for live preview of the current section being edited.

        Args:
            latex_content: Complete LaTeX document content to compile
            timeout: Compilation timeout in seconds (default: 60 for quick preview)

        Returns:
            Compilation result dict with keys:
                - success: bool
                - output_pdf: str (path if successful)
                - log: str (compilation log)
                - error: str (error message if failed)
        """
        try:
            # Write content to a temporary file in the workspace
            temp_file = self.project_path / "preview_temp.tex"
            logger.info(f"WriterService: Creating temporary preview file at {temp_file}")
            temp_file.write_text(latex_content, encoding='utf-8')

            # Use pdflatex directly to compile the temporary file
            import subprocess
            import shutil

            # Create output directory
            output_dir = self.project_path / "preview_output"
            output_dir.mkdir(exist_ok=True)

            logger.info(f"WriterService: Compiling preview content ({len(latex_content)} chars) with timeout={timeout}s")

            # Run pdflatex
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", str(output_dir),
                    str(temp_file)
                ],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            log_content = result.stdout + result.stderr
            output_pdf = output_dir / "preview_temp.pdf"

            if result.returncode == 0 and output_pdf.exists():
                logger.info(f"WriterService: Preview compilation succeeded")
                return {
                    "success": True,
                    "output_pdf": str(output_pdf),
                    "log": log_content,
                    "error": None,
                }
            else:
                logger.error(f"WriterService: Preview compilation failed with return code {result.returncode}")
                return {
                    "success": False,
                    "output_pdf": None,
                    "log": log_content,
                    "error": f"pdflatex returned {result.returncode}",
                }

        except subprocess.TimeoutExpired:
            logger.error(f"WriterService: Preview compilation timeout after {timeout}s")
            return {
                "success": False,
                "output_pdf": None,
                "log": f"Compilation timeout after {timeout} seconds",
                "error": f"Compilation timeout",
            }
        except Exception as e:
            logger.error(f"WriterService: Preview compilation error: {e}", exc_info=True)
            return {
                "success": False,
                "output_pdf": None,
                "log": str(e),
                "error": str(e),
            }

    def compile_manuscript(self, timeout: int = 300) -> dict:
        """Compile manuscript.

        Args:
            timeout: Compilation timeout in seconds

        Returns:
            Compilation result dict with keys:
                - success: bool
                - output_pdf: str (path if successful)
                - log: str (compilation log)
                - error: str (error message if failed)
        """
        try:
            result = self.writer.compile_manuscript(timeout=timeout)
            # Build log from stdout/stderr
            log_content = ""
            if hasattr(result, 'stdout') and result.stdout:
                log_content += result.stdout
            if hasattr(result, 'stderr') and result.stderr:
                if log_content:
                    log_content += "\n"
                log_content += result.stderr

            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": log_content,
                "error": None,  # No error if compilation completed
            }
        except Exception as e:
            logger.error(f"Compilation error: {e}", exc_info=True)
            return {
                "success": False,
                "output_pdf": None,
                "log": str(e),
                "error": str(e),
            }

    def compile_supplementary(self, timeout: int = 300) -> dict:
        """Compile supplementary material."""
        try:
            result = self.writer.compile_supplementary(timeout=timeout)
            # Build log from stdout/stderr
            log_content = ""
            if hasattr(result, 'stdout') and result.stdout:
                log_content += result.stdout
            if hasattr(result, 'stderr') and result.stderr:
                if log_content:
                    log_content += "\n"
                log_content += result.stderr

            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": log_content,
                "error": None,  # No error if compilation completed
            }
        except Exception as e:
            logger.error(f"Supplementary compilation error: {e}", exc_info=True)
            return {
                "success": False,
                "output_pdf": None,
                "log": str(e),
                "error": str(e),
            }

    def compile_revision(self, timeout: int = 300, track_changes: bool = False) -> dict:
        """Compile revision response document."""
        try:
            result = self.writer.compile_revision(timeout=timeout, track_changes=track_changes)
            # Build log from stdout/stderr
            log_content = ""
            if hasattr(result, 'stdout') and result.stdout:
                log_content += result.stdout
            if hasattr(result, 'stderr') and result.stderr:
                if log_content:
                    log_content += "\n"
                log_content += result.stderr

            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": log_content,
                "error": None,  # No error if compilation completed
            }
        except Exception as e:
            logger.error(f"Revision compilation error: {e}", exc_info=True)
            return {
                "success": False,
                "output_pdf": None,
                "log": str(e),
                "error": str(e),
            }

    # ===== Git Operations =====

    def get_section_history(self, section_name: str, doc_type: str = "manuscript") -> list:
        """Get git history for a section.

        Args:
            section_name: Section name
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            List of commit messages
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            return section.history()
        except Exception as e:
            logger.error(f"Error getting history for {section_name}: {e}")
            return []

    def get_section_diff(
        self, section_name: str, ref: str = "HEAD", doc_type: str = "manuscript"
    ) -> str:
        """Get uncommitted changes for a section.

        Args:
            section_name: Section name
            ref: Git reference (default: HEAD)
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Diff string (empty if no changes)
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            return section.diff(ref=ref)
        except Exception as e:
            logger.error(f"Error getting diff for {section_name}: {e}")
            return ""

    def checkout_section(
        self, section_name: str, ref: str = "HEAD", doc_type: str = "manuscript"
    ) -> bool:
        """Restore a section from git history.

        Args:
            section_name: Section name
            ref: Git reference (commit hash, branch, tag, etc.)
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            section = getattr(doc.contents, section_name)
            return section.checkout(ref)
        except Exception as e:
            logger.error(f"Error checking out {section_name}: {e}")
            raise

    # ===== Utility Operations =====

    def get_pdf(self, doc_type: str = "manuscript") -> Optional[str]:
        """Get path to compiled PDF.

        Args:
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Path to PDF if exists, None otherwise
        """
        try:
            pdf_path = self.writer.get_pdf(doc_type=doc_type)
            return str(pdf_path) if pdf_path else None
        except Exception as e:
            logger.error(f"Error getting PDF: {e}")
            return None

    def read_tex_file(self, file_path: str) -> str:
        """Read content of a .tex file from the writer workspace.

        Args:
            file_path: Relative path to the .tex file (e.g., "main.tex" or "chapters/intro.tex")

        Returns:
            Content of the file

        Raises:
            FileNotFoundError: If file doesn't exist
        """
        full_path = self.project_path / file_path

        # Security check: ensure the path is within the project directory
        try:
            full_path.resolve().relative_to(self.project_path.resolve())
        except ValueError:
            raise PermissionError(f"Access denied: path outside project directory")

        if not full_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not full_path.is_file():
            raise ValueError(f"Not a file: {file_path}")

        try:
            return full_path.read_text(encoding='utf-8')
        except Exception as e:
            logger.error(f"Error reading file {file_path}: {e}")
            raise

    def watch(self, on_compile=None):
        """Start watching for changes and auto-compile.

        Args:
            on_compile: Optional callback function on successful compilation
        """
        try:
            self.writer.watch(on_compile=on_compile)
        except Exception as e:
            logger.error(f"Error starting watch mode: {e}")
            raise
