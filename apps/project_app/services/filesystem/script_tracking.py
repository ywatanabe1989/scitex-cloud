"""
Script execution tracking for projects.

Handles creation and tracking of script execution directories.
"""

import os
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from .paths import ensure_directory


def create_script_execution_tracker(
    project_path: Path, script_name: str
) -> Tuple[bool, Optional[Path]]:
    """
    Create execution tracking for a script.

    Args:
        project_path: Root path of the project
        script_name: Name of the script being executed

    Returns:
        Tuple of (success, execution_dir)
    """
    try:
        if not project_path:
            return False, None

        script_base = Path(script_name).stem
        script_dir = project_path / "scripts" / script_base

        if not ensure_directory(script_dir):
            return False, None

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        execution_dir = script_dir / f"execution_{timestamp}"

        if not ensure_directory(execution_dir):
            return False, None

        # Create running marker
        running_marker = execution_dir / "RUNNING"
        with open(running_marker, "w") as f:
            f.write(f"""Script: {script_name}
Started: {datetime.now().isoformat()}
Status: Running
PID: {os.getpid()}
""")

        # Create output directories
        for output_dir in ["logs", "outputs", "figures", "data"]:
            if not ensure_directory(execution_dir / output_dir):
                return False, None

        return True, execution_dir

    except Exception as e:
        print(f"Error creating script execution tracker: {e}")
        return False, None


def mark_script_finished(
    execution_dir: Path, success: bool = True, error_msg: str = None
) -> bool:
    """
    Mark script execution as finished.

    Args:
        execution_dir: Path to the execution directory
        success: Whether execution was successful
        error_msg: Optional error message if failed

    Returns:
        True if successfully marked
    """
    try:
        if not execution_dir.exists():
            return False

        # Remove running marker
        running_marker = execution_dir / "RUNNING"
        if running_marker.exists():
            running_marker.unlink()

        # Create finish marker
        marker = execution_dir / ("FINISHED_SUCCESS" if success else "FINISHED_ERROR")
        status = "Completed Successfully" if success else "Failed"

        with open(marker, "w") as f:
            f.write(f"""Status: {status}
Finished: {datetime.now().isoformat()}
Error: {error_msg or "None"}
""")

        # Write execution summary
        summary_file = execution_dir / "execution_summary.json"
        summary = {
            "script_name": execution_dir.parent.name,
            "execution_id": execution_dir.name,
            "finished_at": datetime.now().isoformat(),
            "success": success,
            "error_message": error_msg,
            "output_files": [
                f.name
                for f in execution_dir.rglob("*")
                if f.is_file() and f.name not in ["RUNNING", "FINISHED_SUCCESS", "FINISHED_ERROR"]
            ],
            "logs_available": (execution_dir / "logs").exists(),
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return True

    except Exception as e:
        print(f"Error marking script as finished: {e}")
        return False
