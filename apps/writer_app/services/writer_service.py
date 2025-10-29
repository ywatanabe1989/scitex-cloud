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
            self._writer = Writer(
                self.project_path,
                name=project.name,
                git_strategy="child",  # Isolated git per project
            )

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
            return section.read()
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
            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": result.log,
                "error": result.error if hasattr(result, "error") else None,
            }
        except Exception as e:
            logger.error(f"Compilation error: {e}")
            return {
                "success": False,
                "output_pdf": None,
                "log": "",
                "error": str(e),
            }

    def compile_supplementary(self, timeout: int = 300) -> dict:
        """Compile supplementary material."""
        try:
            result = self.writer.compile_supplementary(timeout=timeout)
            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": result.log,
                "error": result.error if hasattr(result, "error") else None,
            }
        except Exception as e:
            logger.error(f"Supplementary compilation error: {e}")
            return {
                "success": False,
                "output_pdf": None,
                "log": "",
                "error": str(e),
            }

    def compile_revision(self, timeout: int = 300, track_changes: bool = False) -> dict:
        """Compile revision response document."""
        try:
            result = self.writer.compile_revision(timeout=timeout, track_changes=track_changes)
            return {
                "success": result.success,
                "output_pdf": str(result.output_pdf) if result.output_pdf else None,
                "log": result.log,
                "error": result.error if hasattr(result, "error") else None,
            }
        except Exception as e:
            logger.error(f"Revision compilation error: {e}")
            return {
                "success": False,
                "output_pdf": None,
                "log": "",
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
