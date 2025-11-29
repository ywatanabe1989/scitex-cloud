#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery Task for Workflow Job Execution

Executes a single workflow job with all its steps.
"""

from celery import shared_task
from django.utils import timezone
import yaml
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def execute_workflow_job(self, job_id):
    """
    Execute a single workflow job

    Args:
        job_id: WorkflowJob ID

    Returns:
        Dict with execution results
    """
    from apps.project_app.models import WorkflowJob, WorkflowStep
    from .workflow_step import execute_workflow_step

    try:
        job = WorkflowJob.objects.select_related(
            "run", "run__workflow", "run__workflow__project"
        ).get(id=job_id)
    except WorkflowJob.DoesNotExist:
        logger.error(f"WorkflowJob {job_id} not found")
        return {"error": "Job not found"}

    logger.info(f"Starting job {job.name} for run {job.run.id}")

    # Update job status
    job.status = "in_progress"
    job.started_at = timezone.now()
    job.save()

    try:
        # Parse workflow YAML to get job configuration
        workflow_config = yaml.safe_load(job.run.workflow.yaml_content)
        job_config = workflow_config["jobs"][job.job_id]

        # Get steps
        steps_config = job_config.get("steps", [])

        # Create WorkflowStep objects
        for step_number, step_config in enumerate(steps_config, start=1):
            step_name = step_config.get("name", f"Step {step_number}")
            step_command = step_config.get("run", step_config.get("uses", ""))

            step = WorkflowStep.objects.create(
                job=job,
                name=step_name,
                step_number=step_number,
                command=step_command,
                working_directory=step_config.get("working-directory", ""),
                environment_vars=step_config.get("env", {}),
                condition=step_config.get("if", ""),
                continue_on_error=step_config.get("continue-on-error", False),
                status="queued",
            )

            logger.info(f"Created step {step.name} for job {job.id}")

        # Execute steps sequentially
        steps = WorkflowStep.objects.filter(job=job).order_by("step_number")

        for step in steps:
            # Check condition (simplified - just check for 'always()')
            if step.condition and step.condition != "always()":
                # Skip conditional steps for now
                step.status = "skipped"
                step.save()
                continue

            # Execute step
            result = execute_workflow_step.delay(step.id)
            step_result = result.get(timeout=3600)  # 1 hour timeout

            if not step_result.get("success"):
                if not step.continue_on_error:
                    logger.error(f"Step {step.name} failed, stopping job")
                    break

        # Calculate job conclusion
        all_steps = steps.count()
        successful_steps = steps.filter(conclusion="success").count()
        failed_steps = steps.filter(conclusion="failure").count()

        if failed_steps > 0:
            job.conclusion = "failure"
        elif successful_steps == all_steps:
            job.conclusion = "success"
        else:
            job.conclusion = "skipped"

        job.status = "completed"
        job.completed_at = timezone.now()
        job.calculate_duration()
        job.save()

        logger.info(f"Job {job.id} completed with conclusion {job.conclusion}")

        return {
            "success": job.conclusion == "success",
            "job_id": job.id,
            "conclusion": job.conclusion,
            "duration": job.duration_seconds,
        }

    except Exception as e:
        logger.error(f"Error executing job {job.id}: {e}", exc_info=True)

        job.status = "failed"
        job.conclusion = "failure"
        job.completed_at = timezone.now()
        job.calculate_duration()
        job.save()

        return {
            "success": False,
            "error": str(e),
        }


# EOF
