"""
Script execution tracking module for ProjectFilesystemManager.

Handles creation and management of script execution tracking with
RUNNING/FINISHED_SUCCESS markers and execution logs.
"""

import os
import json
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
from ..models import Project


def create_script_execution_tracker(
    manager,
    project: Project,
    script_name: str
) -> Tuple[bool, Optional[Path]]:
    """Create execution tracking for a script with RUNNING/FINISHED_SUCCESS markers."""
    try:
        project_path = manager.get_project_root_path(project)
        if not project_path:
            return False, None

        # Create script-specific directory
        script_base = Path(script_name).stem  # Remove extension
        script_dir = project_path / "scripts" / script_base

        if not manager._ensure_directory(script_dir):
            return False, None

        # Create execution tracking structure
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        execution_dir = script_dir / f"execution_{timestamp}"

        if not manager._ensure_directory(execution_dir):
            return False, None

        # Create RUNNING marker
        running_marker = execution_dir / "RUNNING"
        with open(running_marker, "w") as f:
            f.write(f"""Script: {script_name}
Started: {datetime.now().isoformat()}
Status: Running
PID: {os.getpid()}
""")

        # Create logs directory
        logs_dir = execution_dir / "logs"
        if not manager._ensure_directory(logs_dir):
            return False, None

        # Create output directories
        for output_dir in ["outputs", "figures", "data"]:
            if not manager._ensure_directory(execution_dir / output_dir):
                return False, None

        return True, execution_dir
    except Exception as e:
        print(f"Error creating script execution tracker: {e}")
        return False, None


def mark_script_finished(
    execution_dir: Path,
    success: bool = True,
    error_msg: str = None
) -> bool:
    """Mark script execution as finished with success/failure status."""
    try:
        if not execution_dir.exists():
            return False

        # Remove RUNNING marker
        running_marker = execution_dir / "RUNNING"
        if running_marker.exists():
            running_marker.unlink()

        # Create appropriate finish marker
        if success:
            marker = execution_dir / "FINISHED_SUCCESS"
            status = "Completed Successfully"
        else:
            marker = execution_dir / "FINISHED_ERROR"
            status = "Failed"

        with open(marker, "w") as f:
            f.write(f"""Status: {status}
Finished: {datetime.now().isoformat()}
Duration: {datetime.now().isoformat()}
Error: {error_msg or "None"}
""")

        # Create execution summary
        summary_file = execution_dir / "execution_summary.json"
        summary = {
            "script_name": execution_dir.parent.name,
            "execution_id": execution_dir.name,
            "started_at": None,  # Would need to read from RUNNING marker
            "finished_at": datetime.now().isoformat(),
            "success": success,
            "error_message": error_msg,
            "output_files": [
                f.name
                for f in execution_dir.rglob("*")
                if f.is_file()
                and f.name not in ["RUNNING", "FINISHED_SUCCESS", "FINISHED_ERROR"]
            ],
            "logs_available": (execution_dir / "logs").exists(),
        }

        with open(summary_file, "w") as f:
            json.dump(summary, f, indent=2)

        return True
    except Exception as e:
        print(f"Error marking script as finished: {e}")
        return False


def get_script_executions(
    manager,
    project: Project,
    script_name: str = None
) -> List[Dict]:
    """Get execution history for scripts in the project."""
    try:
        project_path = manager.get_project_root_path(project)
        if not project_path:
            return []

        scripts_path = project_path / "scripts"
        if not scripts_path.exists():
            return []

        executions = []

        # If specific script requested, only check that one
        if script_name:
            script_base = Path(script_name).stem
            script_dirs = (
                [scripts_path / script_base]
                if (scripts_path / script_base).exists()
                else []
            )
        else:
            script_dirs = [d for d in scripts_path.iterdir() if d.is_dir()]

        for script_dir in script_dirs:
            for execution_dir in script_dir.iterdir():
                if execution_dir.is_dir() and execution_dir.name.startswith(
                    "execution_"
                ):
                    # Check for status markers
                    if (execution_dir / "RUNNING").exists():
                        status = "running"
                    elif (execution_dir / "FINISHED_SUCCESS").exists():
                        status = "success"
                    elif (execution_dir / "FINISHED_ERROR").exists():
                        status = "error"
                    else:
                        status = "unknown"

                    # Try to load execution summary
                    summary_file = execution_dir / "execution_summary.json"
                    if summary_file.exists():
                        with open(summary_file, "r") as f:
                            summary = json.load(f)
                    else:
                        summary = {}

                    executions.append(
                        {
                            "script_name": script_dir.name,
                            "execution_id": execution_dir.name,
                            "status": status,
                            "path": str(execution_dir.relative_to(project_path)),
                            "timestamp": execution_dir.name.split("_", 1)[1]
                            if "_" in execution_dir.name
                            else "",
                            "summary": summary,
                        }
                    )

        # Sort by timestamp (newest first)
        executions.sort(key=lambda x: x["timestamp"], reverse=True)
        return executions
    except Exception as e:
        print(f"Error getting script executions: {e}")
        return []
