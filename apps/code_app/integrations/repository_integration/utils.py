"""
Utility functions for automatic repository integration.

Provides auto-sync functionality for code execution results.
"""

import logging
from typing import Dict, Any, Optional

from apps.code_app.models import CodeExecutionJob, DataAnalysisJob
from apps.scholar_app.models import Dataset, RepositoryConnection

from .integrator import CodeRepositoryIntegrator

logger = logging.getLogger(__name__)


def auto_sync_code_completion(job: CodeExecutionJob) -> Dict[str, Any]:
    """Automatically sync code execution results on job completion"""

    # Check if user has auto-sync enabled
    default_connection = RepositoryConnection.objects.filter(
        user=job.user, is_default=True, auto_sync_enabled=True, status="active"
    ).first()

    if not default_connection:
        logger.info(f"No auto-sync repository connection for user {job.user.username}")
        return {"auto_sync": False, "reason": "no_auto_sync_connection"}

    try:
        integrator = CodeRepositoryIntegrator(job.user, default_connection)
        dataset = integrator.sync_code_execution_results(job, auto_upload=True)

        if dataset:
            return {
                "auto_sync": True,
                "dataset_id": str(dataset.id),
                "dataset_title": dataset.title,
                "repository_name": default_connection.repository.name,
                "files_synced": dataset.file_count,
                "total_size": dataset.total_size_bytes,
            }
        else:
            return {"auto_sync": False, "reason": "sync_failed"}

    except Exception as e:
        logger.error(f"Auto-sync failed for job {job.job_id}: {e}")
        return {"auto_sync": False, "reason": "sync_error", "error": str(e)}


def sync_project_data_to_repository(
    project, repository_connection: RepositoryConnection
) -> Optional[Dataset]:
    """Sync all project data to a repository"""

    try:
        # Create a project-wide dataset
        dataset = Dataset.objects.create(
            title=f"Project Data - {project.name}",
            description=f"Complete data and outputs from project: {project.name}\n\n{project.description}",
            dataset_type="supplementary",
            owner=project.owner,
            repository_connection=repository_connection,
            project=project,
            keywords=f"project data, {project.name}, computational results",
            status="draft",
        )

        integrator = CodeRepositoryIntegrator(project.owner, repository_connection)

        # Add all code execution results from this project
        code_jobs = CodeExecutionJob.objects.filter(
            user=project.owner
        )  # Filter by project if available
        for job in code_jobs:
            if job.status == "completed":
                integrator._add_code_outputs_to_dataset(job, dataset)

        # Add all analysis results from this project
        analysis_jobs = DataAnalysisJob.objects.filter(
            user=project.owner
        )  # Filter by project if available
        for analysis_job in analysis_jobs:
            integrator._add_analysis_outputs_to_dataset(analysis_job, dataset)

        # Update dataset stats
        integrator._update_dataset_stats(dataset)

        logger.info(f"Created project dataset {dataset.id} for project {project.name}")
        return dataset

    except Exception as e:
        logger.error(f"Failed to sync project data: {e}")
        return None
