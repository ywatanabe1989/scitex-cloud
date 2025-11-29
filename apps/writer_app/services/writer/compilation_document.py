"""
Document compilation for Writer.

Handles manuscript, supplementary, and revision compilation.
"""

from pathlib import Path
from typing import Optional, Callable

from scitex import logging

logger = logging.getLogger(__name__)


def compile_manuscript(
    writer_dir: Path,
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
        writer_dir: Path to the writer directory
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
    try:
        from scitex.writer._compile import compile_manuscript as _compile

        result = _compile(
            project_dir=writer_dir,
            timeout=timeout,
            no_figs=no_figs,
            ppt2tif=ppt2tif,
            crop_tif=crop_tif,
            quiet=quiet,
            verbose=verbose,
            force=force,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        log_content = _build_log_content(result)

        return {
            "success": result.success,
            "output_pdf": str(result.output_pdf) if result.output_pdf else None,
            "log": log_content,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Compilation error: {e}", exc_info=True)
        return {
            "success": False,
            "output_pdf": None,
            "log": str(e),
            "error": str(e),
        }


def compile_supplementary(
    writer_dir: Path,
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
        writer_dir: Path to the writer directory
        timeout: Compilation timeout in seconds
        log_callback: Optional callback for real-time log streaming
        progress_callback: Optional callback for progress updates
        no_figs: Exclude figures
        ppt2tif: Convert PowerPoint to TIF on WSL
        crop_tif: Crop TIF images to remove excess whitespace
        quiet: Suppress detailed logs for LaTeX compilation
    """
    try:
        from scitex.writer._compile import compile_supplementary as _compile

        result = _compile(
            project_dir=writer_dir,
            timeout=timeout,
            no_figs=no_figs,
            ppt2tif=ppt2tif,
            crop_tif=crop_tif,
            quiet=quiet,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        log_content = _build_log_content(result)

        return {
            "success": result.success,
            "output_pdf": str(result.output_pdf) if result.output_pdf else None,
            "log": log_content,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Supplementary compilation error: {e}", exc_info=True)
        return {
            "success": False,
            "output_pdf": None,
            "log": str(e),
            "error": str(e),
        }


def compile_revision(
    writer_dir: Path,
    timeout: int = 300,
    log_callback: Optional[Callable] = None,
    progress_callback: Optional[Callable] = None,
    track_changes: bool = False,
    **kwargs,
) -> dict:
    """Compile revision response document.

    Args:
        writer_dir: Path to the writer directory
        timeout: Compilation timeout in seconds
        log_callback: Optional callback for real-time log streaming
        progress_callback: Optional callback for progress updates
        track_changes: Whether to enable change tracking
    """
    try:
        from scitex.writer._compile import compile_revision as _compile

        result = _compile(
            project_dir=writer_dir,
            timeout=timeout,
            track_changes=track_changes,
            log_callback=log_callback,
            progress_callback=progress_callback,
        )

        log_content = _build_log_content(result)

        return {
            "success": result.success,
            "output_pdf": str(result.output_pdf) if result.output_pdf else None,
            "log": log_content,
            "error": None,
        }
    except Exception as e:
        logger.error(f"Revision compilation error: {e}", exc_info=True)
        return {
            "success": False,
            "output_pdf": None,
            "log": str(e),
            "error": str(e),
        }


def _build_log_content(result) -> str:
    """Build log content from compilation result."""
    log_content = ""
    if hasattr(result, "stdout") and result.stdout:
        log_content += result.stdout
    if hasattr(result, "stderr") and result.stderr:
        if log_content:
            log_content += "\n"
        log_content += result.stderr
    return log_content
