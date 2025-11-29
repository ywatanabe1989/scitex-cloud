#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery Task for Workflow Step Execution

Executes a single workflow step (shell command or action).
"""

from celery import shared_task
from django.utils import timezone
import subprocess
import os
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def execute_workflow_step(self, step_id):
    """
    Execute a single workflow step

    Args:
        step_id: WorkflowStep ID

    Returns:
        Dict with execution results
    """
    from apps.project_app.models import WorkflowStep
    from apps.project_app.services.project_filesystem import (
        get_project_filesystem_manager,
    )

    try:
        step = WorkflowStep.objects.select_related(
            "job", "job__run", "job__run__workflow", "job__run__workflow__project"
        ).get(id=step_id)
    except WorkflowStep.DoesNotExist:
        logger.error(f"WorkflowStep {step_id} not found")
        return {"error": "Step not found"}

    logger.info(f"Starting step {step.name} for job {step.job.id}")

    # Update step status
    step.status = "in_progress"
    step.started_at = timezone.now()
    step.save()

    try:
        project = step.job.run.workflow.project

        # Get project directory
        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            raise FileNotFoundError(f"Project directory not found: {project_path}")

        # Determine working directory
        if step.working_directory:
            working_dir = project_path / step.working_directory
        else:
            working_dir = project_path

        # Prepare environment variables
        env = os.environ.copy()
        env.update(step.environment_vars)

        # Add common environment variables
        env.update(
            {
                "GITHUB_WORKSPACE": str(project_path),
                "GITHUB_REPOSITORY": f"{project.owner.username}/{project.slug}",
                "GITHUB_RUN_ID": str(step.job.run.id),
                "GITHUB_RUN_NUMBER": str(step.job.run.run_number),
                "GITHUB_JOB": step.job.job_id,
            }
        )

        # Execute command
        if step.command.startswith("uses:"):
            # Action reference (e.g., actions/checkout@v3)
            # For now, we'll skip these and just log
            step.output = f"Action {step.command} would be executed here"
            step.exit_code = 0
            step.conclusion = "success"
        else:
            # Shell command
            logger.info(f"Executing command: {step.command}")

            process = subprocess.Popen(
                step.command,
                shell=True,
                cwd=str(working_dir),
                env=env,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
            )

            # Stream output
            stdout_lines = []
            stderr_lines = []

            # Read stdout
            for line in process.stdout:
                stdout_lines.append(line)
                logger.debug(f"STDOUT: {line.strip()}")

            # Read stderr
            for line in process.stderr:
                stderr_lines.append(line)
                logger.debug(f"STDERR: {line.strip()}")

            # Wait for process to complete
            exit_code = process.wait()

            # Save output
            step.output = "".join(stdout_lines)
            step.error_output = "".join(stderr_lines)
            step.exit_code = exit_code

            if exit_code == 0:
                step.conclusion = "success"
            else:
                step.conclusion = "failure"

        step.status = "completed"
        step.completed_at = timezone.now()
        step.calculate_duration()
        step.save()

        logger.info(f"Step {step.id} completed with exit code {step.exit_code}")

        return {
            "success": step.conclusion == "success",
            "step_id": step.id,
            "exit_code": step.exit_code,
            "conclusion": step.conclusion,
            "duration": step.duration_seconds,
        }

    except Exception as e:
        logger.error(f"Error executing step {step.id}: {e}", exc_info=True)

        step.status = "failed"
        step.conclusion = "failure"
        step.error_output = str(e)
        step.exit_code = -1
        step.completed_at = timezone.now()
        step.calculate_duration()
        step.save()

        return {
            "success": False,
            "error": str(e),
        }


# EOF
