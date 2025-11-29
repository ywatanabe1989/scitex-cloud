"""
Writer integration for project filesystem.

Handles SciTeX Writer template initialization.
"""

import logging
from pathlib import Path
from typing import Optional, Tuple

logger = logging.getLogger(__name__)


def initialize_scitex_writer_template(project) -> Tuple[bool, Optional[Path]]:
    """
    Initialize SciTeX Writer template structure for a project.

    Args:
        project: Project instance

    Returns:
        Tuple of (success, writer_path)
    """
    try:
        from apps.writer_app.services import WriterService

        writer_service = WriterService(project.id, project.owner.id)
        writer = writer_service.writer
        writer_path = writer_service.writer_dir

        if writer_path and writer_path.exists():
            logger.info(f"✓ Writer template initialized successfully at: {writer_path}")
            return True, writer_path
        else:
            logger.warning(
                f"Writer initialization returned path but directory doesn't exist: {writer_path}"
            )
            return False, None

    except Exception as e:
        logger.error(f"Error initializing SciTeX Writer template: {e}", exc_info=True)
        return False, None
