"""
Preview compilation for Writer.

Handles quick preview compilation of LaTeX content.
"""

import subprocess
import shutil
from pathlib import Path

from scitex import logging

from .compilation_color import apply_color_mode_to_latex

logger = logging.getLogger(__name__)

# Auxiliary file extensions to clean up after compilation
AUX_EXTENSIONS = [
    ".aux", ".log", ".fls", ".fdb_latexmk", ".bbl",
    ".blg", ".out", ".toc", ".nav", ".snm",
]


def compile_preview(
    writer_dir: Path,
    latex_content: str,
    timeout: int = 60,
    color_mode: str = "light",
    section_name: str = "preview",
    doc_type: str = "manuscript",
) -> dict:
    """Compile a quick preview of provided LaTeX content.

    Args:
        writer_dir: Path to the writer directory
        latex_content: Complete LaTeX document content to compile
        timeout: Compilation timeout in seconds
        color_mode: PDF color mode - 'light', 'dark', 'sepia', or 'paper'
        section_name: Section name for output filename
        doc_type: Document type - 'manuscript', 'supplementary', or 'revision'

    Returns:
        Compilation result dict with keys:
            - success: bool
            - output_pdf: str (path if successful)
            - log: str (compilation log)
            - error: str (error message if failed)
    """
    try:
        # Apply color mode to LaTeX content
        latex_content = apply_color_mode_to_latex(latex_content, color_mode)

        # Create preview directory
        preview_dir = writer_dir / ".preview"
        preview_dir.mkdir(parents=True, exist_ok=True)

        # Setup bibliography symlink
        _setup_bibliography_symlink(writer_dir, preview_dir)

        # Write content to temporary file
        temp_tex = preview_dir / f"preview-{section_name}-{color_mode}-temp.tex"
        logger.info(
            f"[CompilePreview] Creating preview file: {temp_tex} for section: {section_name}, theme: {color_mode}"
        )
        temp_tex.write_text(latex_content, encoding="utf-8")

        # Compile with latexmk
        logger.info(
            f"[CompilePreview] Compiling {color_mode} preview with latexmk ({len(latex_content)} chars) timeout={timeout}s"
        )

        result = subprocess.run(
            [
                "latexmk",
                "-pdf",
                "-interaction=nonstopmode",
                f"-output-directory={preview_dir}",
                "-silent",
                str(temp_tex),
            ],
            capture_output=True,
            text=True,
            timeout=timeout,
            cwd=str(preview_dir),
        )

        log_content = result.stdout + result.stderr

        # Check for output PDF
        temp_pdf = preview_dir / f"preview-{section_name}-{color_mode}-temp.pdf"
        output_pdf = preview_dir / f"preview-{section_name}-{color_mode}.pdf"

        logger.info(f"[CompilePreview] Looking for compiled PDF: {temp_pdf}")

        if temp_pdf.exists():
            logger.info(
                f"[CompilePreview] {color_mode} PDF compiled successfully at {temp_pdf}"
            )

            # Clean up auxiliary files
            _cleanup_aux_files(preview_dir, temp_tex.stem)

            # Rename to final filename
            if temp_pdf != output_pdf:
                shutil.move(str(temp_pdf), str(output_pdf))

            logger.info(
                f"WriterService: Preview compilation succeeded for {section_name} ({color_mode}): {output_pdf}"
            )

            return {
                "success": True,
                "output_pdf": str(output_pdf),
                "log": log_content,
                "error": None,
            }
        else:
            logger.error(
                f"WriterService: Preview compilation failed - PDF not found at {temp_pdf}"
            )
            logger.error(f"latexmk return code: {result.returncode}")
            logger.error(f"latexmk output:\n{log_content}")
            return {
                "success": False,
                "output_pdf": None,
                "log": log_content,
                "error": "PDF compilation failed - no output PDF generated",
            }

    except subprocess.TimeoutExpired:
        logger.error(f"WriterService: Preview compilation timeout after {timeout}s")
        return {
            "success": False,
            "output_pdf": None,
            "log": f"Compilation timeout after {timeout} seconds",
            "error": "Compilation timeout",
        }
    except Exception as e:
        logger.error(f"WriterService: Preview compilation error: {e}", exc_info=True)
        return {
            "success": False,
            "output_pdf": None,
            "log": str(e),
            "error": str(e),
        }


def _setup_bibliography_symlink(writer_dir: Path, preview_dir: Path) -> None:
    """Setup bibliography symlink for citations."""
    bib_source = writer_dir / "00_shared" / "bib_files" / "bibliography.bib"
    bib_link = preview_dir / "bibliography.bib"
    if bib_source.exists() and not bib_link.exists():
        try:
            bib_link.symlink_to(bib_source)
            logger.info("[CompilePreview] Created bibliography symlink for citations")
        except Exception as e:
            logger.warning(f"[CompilePreview] Could not create bibliography symlink: {e}")


def _cleanup_aux_files(preview_dir: Path, base_name: str) -> None:
    """Clean up auxiliary files after compilation."""
    for ext in AUX_EXTENSIONS:
        aux_file = preview_dir / f"{base_name}{ext}"
        if aux_file.exists():
            try:
                aux_file.unlink()
            except Exception as e:
                logger.debug(
                    f"[CompilePreview] Could not remove auxiliary file {aux_file.name}: {e}"
                )
