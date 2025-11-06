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

                # Check if project_root is None (directory doesn't exist)
                if project_root is None:
                    raise RuntimeError(
                        f"Project directory not found for project {self.project_id} (slug: {project.slug}). "
                        f"Please ensure the project directory exists."
                    )

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

            # Ensure parent directories exist before creating Writer
            # This is necessary because clone_project needs the parent directory to exist
            parent_dir = self.project_path.parent
            parent_dir.mkdir(parents=True, exist_ok=True)
            logger.info(f"WriterService: Ensured parent directory exists at {parent_dir}")

            try:
                # IMPORTANT: Do NOT pass 'name' parameter to Writer
                #
                # The scitex.writer.Writer class expects to create a NEW project with its own directory.
                # When you pass a 'name' parameter, Writer creates a subdirectory: project_path/name/
                #
                # However, Django SciTeX Cloud uses an organized ecosystem structure:
                #   data/users/{username}/{project-slug}/scitex/writer/
                #
                # The 'writer' directory is already the final target where Writer should operate.
                # We pass the exact path where Writer should work, not a parent directory.
                # This prevents Writer from creating: scitex/writer/{project-name}/
                #
                # Example structure:
                #   ✓ Correct: data/users/test-user/test-002/scitex/writer/01_manuscript/
                #   ✗ Wrong:   data/users/test-user/test-002/scitex/writer/test-002/01_manuscript/
                #
                # Git Strategy: Use "parent" to share the main project's git repository
                # The writer directory is part of the main project, not a separate repo.
                self._writer = Writer(
                    self.project_path,  # Already points to: {project-root}/scitex/writer/
                    # name=project.name,  # REMOVED - causes extra subdirectory creation
                    git_strategy="parent",  # Use parent project's git repository
                )
                logger.info(f"WriterService: Writer instance created successfully")
            except Exception as e:
                logger.error(f"WriterService: Failed to create Writer instance: {e}", exc_info=True)
                raise RuntimeError(f"Failed to initialize Writer: {e}") from e

        return self._writer

    # ===== Section Operations =====

    def read_section(self, section_name: str, doc_type: str = "manuscript") -> str:
        """Read a section from shared/manuscript/supplementary/revision.

        Args:
            section_name: Section name (e.g., 'introduction', 'abstract', 'title', 'authors')
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            Section content as string
        """
        try:
            logger.info(f"[ReadSection] section_name={section_name}, doc_type={doc_type}")

            # Special handling for compiled sections (not applicable to shared)
            if section_name == "compiled_pdf" or section_name == "compiled_tex":
                if doc_type == "shared":
                    logger.warning("[ReadSection] Compiled sections not available for 'shared' doc_type")
                    return ""
                logger.info(f"[ReadSection] Reading compiled tex for {doc_type}")
                content = self._read_compiled_tex(doc_type)
                logger.info(f"[ReadSection] Compiled tex length: {len(content)}, first 100 chars: {content[:100]}")
                return content

            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                # For shared, sections are at the root level (no .contents)
                # shared has: title, authors, keywords, journal_name
                if not hasattr(doc, section_name):
                    logger.info(f"Section {section_name} not found in shared tree")
                    return ""
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.info(f"Section {section_name} not found for {doc_type}: ManuscriptContents does not have attribute '{section_name}'")
                    return ""
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.info(f"Section {section_name} not found for {doc_type}")
                    return ""
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.info(f"Section {section_name} not found for {doc_type}")
                    return ""
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

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

    def _read_compiled_tex(self, doc_type: str = "manuscript") -> str:
        """Read the compiled TeX file (merged document).

        Args:
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Compiled TeX content or helpful message if not compiled yet
        """
        # Map document type to directory
        dir_map = {
            "manuscript": "01_manuscript",
            "supplementary": "02_supplementary",
            "revision": "03_revision",
        }

        if doc_type not in dir_map:
            raise ValueError(f"Unknown document type: {doc_type}")

        # Path to compiled tex file (e.g., manuscript.tex, supplementary.tex, revision.tex)
        compiled_tex_path = self.project_path / dir_map[doc_type] / f"{doc_type}.tex"

        # Check if file exists
        if not compiled_tex_path.exists():
            # Return helpful message
            doc_type_label = doc_type.capitalize()
            return f"""% Compiled {doc_type_label} TeX not yet generated
%
% This file will be created after compilation.
% Click the "Compile {doc_type_label} PDF" button to generate it.
%
% The compiled TeX file merges all sections into a single document
% that can be compiled to PDF.
"""

        # Read and return the compiled TeX
        try:
            with open(compiled_tex_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            logger.error(f"Error reading compiled TeX: {e}")
            return f"% Error reading compiled TeX file: {str(e)}"

    def get_template_content(
        self, section_name: str, doc_type: str = "manuscript"
    ) -> str | None:
        """Get original template content for a section.

        This retrieves the clean template content from scitex.writer.Writer,
        which can be used to reset a section to its original state.

        Args:
            section_name: Section name (e.g., 'introduction', 'abstract', 'title', 'authors')
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            Template content string, or None if template not found
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                section = getattr(doc, section_name, None)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                section = getattr(doc.contents, section_name, None)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                section = getattr(doc.contents, section_name, None)
            elif doc_type == "revision":
                doc = self.writer.revision
                section = getattr(doc.contents, section_name, None)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            if section is None:
                logger.warning(f"Section '{section_name}' not found in {doc_type}")
                return None

            # Get template content from the section's template
            # The Writer class should have a method or property to access template content
            if hasattr(section, 'template'):
                return section.template
            elif hasattr(section, 'get_template'):
                return section.get_template()
            else:
                # Fallback: return empty string with comment
                logger.warning(f"No template method found for section '{section_name}'")
                return f"% Template for {section_name}\n\n"

        except Exception as e:
            logger.error(f"Error getting template content for {section_name}: {e}", exc_info=True)
            return None

    def write_section(
        self, section_name: str, content: str, doc_type: str = "manuscript"
    ) -> bool:
        """Write content to a section.

        Args:
            section_name: Section name
            content: Section content
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                # For shared, sections are at the root level (no .contents)
                if not hasattr(doc, section_name):
                    logger.warning(f"Cannot write to non-existent section {section_name} in shared tree")
                    return False
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot write to non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot write to non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot write to non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

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
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                if not hasattr(doc, section_name):
                    logger.warning(f"Cannot commit non-existent section {section_name} in shared tree")
                    return False
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot commit non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot commit non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot commit non-existent section {section_name} for {doc_type}")
                    return False
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            logger.info(f"Committing section {section_name} with message: {message}")

            # Check if section has commit method
            if not hasattr(section, 'commit'):
                logger.error(f"Section {section_name} does not have commit method")
                raise AttributeError(f"Section {section_name} does not support git commits")

            result = section.commit(message)
            logger.info(f"Commit result for {section_name}: {result}")
            return result
        except Exception as e:
            logger.error(f"Error committing section {section_name}: {e}", exc_info=True)
            raise

    # ===== Compilation Operations =====

    def _apply_color_mode_to_latex(self, latex_content: str, color_mode: str) -> str:
        """Apply color mode to LaTeX content by injecting color commands.

        Args:
            latex_content: Original LaTeX content
            color_mode: 'light', 'dark', 'sepia', or 'paper'

        Returns:
            Modified LaTeX content with color commands
        """
        # Skip color injection for light mode (default LaTeX colors)
        if color_mode == 'light':
            return latex_content

        # Define dark mode colors
        # Must be after \documentclass but before \begin{document}
        color_commands = """\\usepackage{xcolor}
\\pagecolor[rgb]{0.1,0.1,0.1}
\\color[rgb]{0.9,0.9,0.9}
"""

        # Find the position to inject
        if '\\begin{document}' in latex_content:
            # Insert right before \begin{document}
            latex_content = latex_content.replace('\\begin{document}', f'{color_commands}\\begin{{document}}', 1)
        else:
            # Just prepend if no \begin{document} found
            latex_content = color_commands + latex_content

        return latex_content

    def compile_preview(self, latex_content: str, timeout: int = 60, color_mode: str = 'light', section_name: str = 'preview', doc_type: str = 'manuscript') -> dict:
        """Compile a quick preview of provided LaTeX content (not from workspace).

        This is used for live preview of the current section being edited.

        Args:
            latex_content: Complete LaTeX document content to compile
            timeout: Compilation timeout in seconds (default: 60 for quick preview)
            color_mode: PDF color mode - 'light', 'dark', 'sepia', or 'paper'
            section_name: Section name for output filename (e.g., 'introduction')
            doc_type: Document type - 'manuscript', 'supplementary', or 'revision'

        Returns:
            Compilation result dict with keys:
                - success: bool
                - output_pdf: str (path if successful)
                - log: str (compilation log)
                - error: str (error message if failed)
        """
        # Import at method start to avoid UnboundLocalError in except clauses
        import subprocess
        import shutil

        try:
            # Apply color mode to LaTeX content
            latex_content = self._apply_color_mode_to_latex(latex_content, color_mode)

            # Create .preview directory in scitex/writer for compiled previews
            # This directory stores temporary compiled PDFs for quick preview
            # Structure: scitex/writer/.preview/
            preview_dir = self.project_path / "scitex" / "writer" / ".preview"
            preview_dir.mkdir(parents=True, exist_ok=True)

            # Write content to temporary .tex file in .preview directory
            temp_tex = preview_dir / f"preview-{section_name}-temp.tex"
            logger.info(f"[CompilePreview] Creating preview file: {temp_tex} for section: {section_name}")
            temp_tex.write_text(latex_content, encoding='utf-8')

            logger.info(f"[CompilePreview] Compiling preview ({len(latex_content)} chars) timeout={timeout}s")

            # Run pdflatex with output to .preview directory
            result = subprocess.run(
                [
                    "pdflatex",
                    "-interaction=nonstopmode",
                    "-output-directory", str(preview_dir),
                    str(temp_tex)
                ],
                capture_output=True,
                text=True,
                timeout=timeout
            )

            log_content = result.stdout + result.stderr

            # Expected PDF output: .preview/preview-{section_name}-temp.pdf
            temp_pdf = preview_dir / f"preview-{section_name}-temp.pdf"
            # Final PDF name: .preview/preview-{section_name}.pdf
            output_pdf = preview_dir / f"preview-{section_name}.pdf"

            # pdflatex creates preview-{section_name}-temp.pdf from preview-{section_name}-temp.tex
            logger.info(f"[CompilePreview] Looking for compiled PDF: {temp_pdf}")

            # Check if compilation succeeded by looking for the PDF file
            # Note: pdflatex return code may be non-zero even on successful compilation
            # with -interaction=nonstopmode, so we check for the PDF file instead
            if temp_pdf.exists():
                logger.info(f"[CompilePreview] PDF compiled successfully at {temp_pdf}")
                # Rename from temp filename to final filename
                if temp_pdf != output_pdf:
                    shutil.move(str(temp_pdf), str(output_pdf))

                logger.info(f"WriterService: Preview compilation succeeded for {section_name}: {output_pdf}")
                return {
                    "success": True,
                    "output_pdf": str(output_pdf),
                    "log": log_content,
                    "error": None,
                }
            else:
                logger.error(f"WriterService: Preview compilation failed - PDF not found at {temp_pdf}")
                logger.error(f"pdflatex return code: {result.returncode}")
                logger.error(f"pdflatex output:\n{log_content}")
                return {
                    "success": False,
                    "output_pdf": None,
                    "log": log_content,
                    "error": f"PDF compilation failed - no output PDF generated",
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
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            List of commit messages
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                if not hasattr(doc, section_name):
                    logger.warning(f"Cannot get history for non-existent section {section_name} in shared tree")
                    return []
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get history for non-existent section {section_name}")
                    return []
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get history for non-existent section {section_name}")
                    return []
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get history for non-existent section {section_name}")
                    return []
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

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
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            Diff string (empty if no changes)
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                if not hasattr(doc, section_name):
                    logger.warning(f"Cannot get diff for non-existent section {section_name} in shared tree")
                    return ""
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get diff for non-existent section {section_name}")
                    return ""
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get diff for non-existent section {section_name}")
                    return ""
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot get diff for non-existent section {section_name}")
                    return ""
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

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
            doc_type: 'shared', 'manuscript', 'supplementary', or 'revision'

        Returns:
            True if successful
        """
        try:
            # Get the appropriate document tree
            if doc_type == "shared":
                doc = self.writer.shared
                if not hasattr(doc, section_name):
                    logger.warning(f"Cannot checkout non-existent section {section_name} in shared tree")
                    return False
                section = getattr(doc, section_name)
            elif doc_type == "manuscript":
                doc = self.writer.manuscript
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot checkout non-existent section {section_name}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot checkout non-existent section {section_name}")
                    return False
                section = getattr(doc.contents, section_name)
            elif doc_type == "revision":
                doc = self.writer.revision
                if not hasattr(doc.contents, section_name):
                    logger.warning(f"Cannot checkout non-existent section {section_name}")
                    return False
                section = getattr(doc.contents, section_name)
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

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
