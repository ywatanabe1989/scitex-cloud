"""
LaTeX compilation operations for Writer.

Handles preview compilation, manuscript/supplementary/revision compilation.

Modular structure:
- compilation_color.py: Color mode handling for LaTeX
- compilation_preview.py: Quick preview compilation
- compilation_document.py: Full document compilation
"""

from typing import Optional, Callable

from scitex import logging

from .compilation_color import apply_color_mode_to_latex
from .compilation_preview import compile_preview as _compile_preview
from .compilation_document import (
    compile_manuscript as _compile_manuscript,
    compile_supplementary as _compile_supplementary,
    compile_revision as _compile_revision,
)

logger = logging.getLogger(__name__)


class CompilationMixin:
    """Mixin for compilation-related operations.

    Requires self.writer_dir to be set by the parent class.
    """

    def _apply_color_mode_to_latex(self, latex_content: str, color_mode: str) -> str:
        """Apply color mode to LaTeX content by injecting color commands.

        Args:
            latex_content: Original LaTeX content
            color_mode: 'light', 'dark', 'sepia', or 'paper'

        Returns:
            Modified LaTeX content with color commands
        """
        return apply_color_mode_to_latex(latex_content, color_mode)

    def compile_preview(
        self,
        latex_content: str,
        timeout: int = 60,
        color_mode: str = "light",
        section_name: str = "preview",
        doc_type: str = "manuscript",
    ) -> dict:
        """Compile a quick preview of provided LaTeX content.

        Args:
            latex_content: Complete LaTeX document content to compile
            timeout: Compilation timeout in seconds
            color_mode: PDF color mode - 'light', 'dark', 'sepia', or 'paper'
            section_name: Section name for output filename
            doc_type: Document type - 'manuscript', 'supplementary', or 'revision'

        Returns:
            Compilation result dict
        """
        return _compile_preview(
            writer_dir=self.writer_dir,
            latex_content=latex_content,
            timeout=timeout,
            color_mode=color_mode,
            section_name=section_name,
            doc_type=doc_type,
        )

    def compile_manuscript(
        self,
        timeout: int = 300,
        log_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        no_figs: bool = False,
        ppt2tif: bool = False,
        crop_tif: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        force: bool = False,
        **kwargs,
    ) -> dict:
        """Compile manuscript with optional callbacks for live updates.

        Args:
            timeout: Compilation timeout in seconds
            log_callback: Optional callback for real-time log streaming
            progress_callback: Optional callback for progress updates
            no_figs: Exclude figures for quick compilation
            ppt2tif: Convert PowerPoint to TIF on WSL
            crop_tif: Crop TIF images to remove excess whitespace
            quiet: Suppress detailed logs for LaTeX compilation
            verbose: Show detailed logs for LaTeX compilation
            force: Force full recompilation, ignore cache

        Returns:
            Compilation result dict
        """
        return _compile_manuscript(
            writer_dir=self.writer_dir,
            timeout=timeout,
            log_callback=log_callback,
            progress_callback=progress_callback,
            no_figs=no_figs,
            ppt2tif=ppt2tif,
            crop_tif=crop_tif,
            quiet=quiet,
            verbose=verbose,
            force=force,
            **kwargs,
        )

    def compile_supplementary(
        self,
        timeout: int = 300,
        log_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        no_figs: bool = False,
        ppt2tif: bool = False,
        crop_tif: bool = False,
        quiet: bool = False,
        **kwargs,
    ) -> dict:
        """Compile supplementary material.

        Args:
            timeout: Compilation timeout in seconds
            log_callback: Optional callback for real-time log streaming
            progress_callback: Optional callback for progress updates
            no_figs: Exclude figures
            ppt2tif: Convert PowerPoint to TIF on WSL
            crop_tif: Crop TIF images to remove excess whitespace
            quiet: Suppress detailed logs for LaTeX compilation

        Returns:
            Compilation result dict
        """
        return _compile_supplementary(
            writer_dir=self.writer_dir,
            timeout=timeout,
            log_callback=log_callback,
            progress_callback=progress_callback,
            no_figs=no_figs,
            ppt2tif=ppt2tif,
            crop_tif=crop_tif,
            quiet=quiet,
            **kwargs,
        )

    def compile_revision(
        self,
        timeout: int = 300,
        log_callback: Optional[Callable] = None,
        progress_callback: Optional[Callable] = None,
        track_changes: bool = False,
        **kwargs,
    ) -> dict:
        """Compile revision response document.

        Args:
            timeout: Compilation timeout in seconds
            log_callback: Optional callback for real-time log streaming
            progress_callback: Optional callback for progress updates
            track_changes: Whether to enable change tracking

        Returns:
            Compilation result dict
        """
        return _compile_revision(
            writer_dir=self.writer_dir,
            timeout=timeout,
            log_callback=log_callback,
            progress_callback=progress_callback,
            track_changes=track_changes,
            **kwargs,
        )
