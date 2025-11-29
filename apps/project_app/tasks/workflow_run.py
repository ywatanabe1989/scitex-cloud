#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Celery Task for Workflow Run Execution

Executes a complete workflow run with all its jobs.
"""

from celery import shared_task
from django.utils import timezone
import yaml
import logging

logger = logging.getLogger(__name__)


@shared_task(bind=True, max_retries=3)
def execute_workflow_run(self, run_id):
    """
    Execute a complete workflow run

    Args:
        run_id: WorkflowRun ID

    Returns:
        Dict with execution results
    """
    from apps.project_app.models import WorkflowRun, WorkflowJob
    from .workflow_job import execute_workflow_job

    try:
        run = WorkflowRun.objects.select_related("workflow", "workflow__project").get(
            id=run_id
        )
    except WorkflowRun.DoesNotExist:
        logger.error(f"WorkflowRun {run_id} not found")
        return {"error": "Run not found"}

    logger.info(f"Starting workflow run {run.workflow.name} #{run.run_number}")

    # Update run status
    run.status = "in_progress"
    run.started_at = timezone.now()
    run.save()

    try:
        # Parse workflow YAML
        workflow_config = yaml.safe_load(run.workflow.yaml_content)

        if "jobs" not in workflow_config:
            raise ValueError("Workflow must contain 'jobs' section")

        # Create jobs from YAML
        jobs_config = workflow_config["jobs"]
        jobs_order = list(jobs_config.keys())

        for job_id in jobs_order:
            job_config = jobs_config[job_id]

            # Create WorkflowJob
            job = WorkflowJob.objects.create(
                run=run,
                name=job_config.get("name", job_id),
                job_id=job_id,
                runs_on=job_config.get("runs-on", "ubuntu-latest"),
                depends_on=job_config.get("needs", []),
                status="queued",
            )

            logger.info(f"Created job {job.name} for run {run.id}")

        # Execute jobs in order (respecting dependencies)
        executed_jobs = set()
        failed_jobs = set()

        while len(executed_jobs) + len(failed_jobs) < len(jobs_order):
            # Find jobs ready to execute
            ready_jobs = []

            for job_id in jobs_order:
                if job_id in executed_jobs or job_id in failed_jobs:
                    continue

                job = WorkflowJob.objects.get(run=run, job_id=job_id)
                dependencies = job.depends_on

                # Check if all dependencies are satisfied
                if all(dep in executed_jobs for dep in dependencies):
                    ready_jobs.append(job)

            if not ready_jobs:
                # No jobs ready - check if we're deadlocked
                if len(executed_jobs) + len(failed_jobs) < len(jobs_order):
                    logger.error(f"Workflow deadlock detected in run {run.id}")
                    break
                else:
                    break

            # Execute ready jobs (can be parallelized in future)
            for job in ready_jobs:
                result = execute_workflow_job.delay(job.id)

                # Wait for job completion (blocking for now)
                job_result = result.get(timeout=3600)  # 1 hour timeout

                if job_result.get("success"):
                    executed_jobs.add(job.job_id)
                else:
                    failed_jobs.add(job.job_id)

                    # Check if workflow should continue on error
                    job_config = jobs_config.get(job.job_id, {})
                    if not job_config.get("continue-on-error", False):
                        logger.error(f"Job {job.name} failed, stopping workflow")
                        break

        # Calculate final status
        all_jobs = WorkflowJob.objects.filter(run=run)
        successful_jobs = all_jobs.filter(conclusion="success").count()
        failed_jobs_count = all_jobs.filter(conclusion="failure").count()
        total_jobs = all_jobs.count()

        if failed_jobs_count > 0:
            run.conclusion = "failure"
        elif successful_jobs == total_jobs:
            run.conclusion = "success"
        else:
            run.conclusion = "cancelled"

        run.status = "completed"
        run.completed_at = timezone.now()
        run.calculate_duration()

        # Update workflow statistics
        workflow = run.workflow
        workflow.total_runs += 1
        if run.conclusion == "success":
            workflow.successful_runs += 1
        elif run.conclusion == "failure":
            workflow.failed_runs += 1
        workflow.last_run_at = run.completed_at
        workflow.last_run_status = run.conclusion
        workflow.save()

        logger.info(f"Workflow run {run.id} completed with status {run.conclusion}")

        return {
            "success": True,
            "run_id": run.id,
            "conclusion": run.conclusion,
            "duration": run.duration_seconds,
        }

    except Exception as e:
        logger.error(f"Error executing workflow run {run.id}: {e}", exc_info=True)

        run.status = "failed"
        run.conclusion = "failure"
        run.completed_at = timezone.now()
        run.calculate_duration()
        run.save()

        return {
            "success": False,
            "error": str(e),
        }


# EOF
