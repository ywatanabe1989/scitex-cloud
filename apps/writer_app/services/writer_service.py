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
        """Read a section from manuscript/supplementary/revision.

        Args:
            section_name: Section name (e.g., 'introduction', 'abstract', 'compiled_pdf')
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Section content as string
        """
        try:
            logger.info(f"[ReadSection] section_name={section_name}, doc_type={doc_type}")

            # Special handling for compiled sections
            if section_name == "compiled_pdf" or section_name == "compiled_tex":
                logger.info(f"[ReadSection] Reading compiled tex for {doc_type}")
                content = self._read_compiled_tex(doc_type)
                logger.info(f"[ReadSection] Compiled tex length: {len(content)}, first 100 chars: {content[:100]}")
                return content

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
            section_name: Section name (e.g., 'introduction', 'abstract')
            doc_type: 'manuscript', 'supplementary', or 'revision'

        Returns:
            Template content string, or None if template not found
        """
        try:
            # Access the document's template
            if doc_type == "manuscript":
                doc = self.writer.manuscript
            elif doc_type == "supplementary":
                doc = self.writer.supplementary
            elif doc_type == "revision":
                doc = self.writer.revision
            else:
                raise ValueError(f"Unknown document type: {doc_type}")

            # Get the section object
            section = getattr(doc.contents, section_name, None)
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

    def compile_preview(self, latex_content: str, timeout: int = 60, color_mode: str = 'light', section_name: str = 'preview') -> dict:
        """Compile a quick preview of provided LaTeX content (not from workspace).

        This is used for live preview of the current section being edited.

        Args:
            latex_content: Complete LaTeX document content to compile
            timeout: Compilation timeout in seconds (default: 60 for quick preview)
            color_mode: PDF color mode - 'light', 'dark', 'sepia', or 'paper'
            section_name: Section name for output filename (e.g., 'introduction' -> 'preview-introduction.pdf')

        Returns:
            Compilation result dict with keys:
                - success: bool
                - output_pdf: str (path if successful)
                - log: str (compilation log)
                - error: str (error message if failed)
        """
        try:
            # Apply color mode to LaTeX content
            latex_content = self._apply_color_mode_to_latex(latex_content, color_mode)

            # Sanitize section name for filename (use dash consistently)
            safe_section_name = section_name.replace('/', '-').replace(' ', '-').replace('_', '-').lower()

            # Write content to a section-specific temporary file
            temp_file = self.project_path / f"preview-{safe_section_name}-temp.tex"
            logger.info(f"[CompilePreview] Creating preview file: {temp_file.name} for section: {section_name}")
            temp_file.write_text(latex_content, encoding='utf-8')

            # Use pdflatex directly to compile the temporary file
            import subprocess
            import shutil

            # Create output directory
            output_dir = self.project_path / "preview_output"
            output_dir.mkdir(exist_ok=True)

            logger.info(f"[CompilePreview] Compiling preview ({len(latex_content)} chars) timeout={timeout}s")

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
            # Section-specific preview PDF name (use dash consistently)
            output_pdf = output_dir / f"preview-{safe_section_name}.pdf"
            temp_pdf = output_dir / f"preview-{safe_section_name}-temp.pdf"

            # pdflatex creates preview-{section}-temp.pdf, rename to preview-{section}.pdf
            logger.info(f"[CompilePreview] Looking for temp PDF: {temp_pdf.name}")
            if temp_pdf.exists():
                logger.info(f"[CompilePreview] Moving {temp_pdf.name} -> {output_pdf.name}")
                shutil.move(str(temp_pdf), str(output_pdf))

            if result.returncode == 0 and output_pdf.exists():
                logger.info(f"WriterService: Preview compilation succeeded for {section_name}: {output_pdf}")
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
