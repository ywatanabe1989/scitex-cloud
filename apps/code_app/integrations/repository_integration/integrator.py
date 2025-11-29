"""
Main CodeRepositoryIntegrator class.

Service for integrating code execution results with data repositories.
"""

import logging
from typing import Optional
from django.db import transaction

from apps.scholar_app.models import Dataset, RepositoryConnection
from apps.scholar_app.repository_services import upload_dataset_to_repository

from .dataset_creators import DatasetCreatorsMixin
from .file_handlers import FileHandlersMixin

logger = logging.getLogger(__name__)


class CodeRepositoryIntegrator(DatasetCreatorsMixin, FileHandlersMixin):
    """Service for integrating code execution results with data repositories"""

    def __init__(
        self, user, repository_connection: Optional[RepositoryConnection] = None
    ):
        self.user = user
        self.repository_connection = (
            repository_connection or self._get_default_connection()
        )

    def _get_default_connection(self) -> Optional[RepositoryConnection]:
        """Get user's default repository connection"""
        return RepositoryConnection.objects.filter(
            user=self.user, is_default=True, status="active"
        ).first()

    def sync_code_execution_results(
        self, job, auto_upload: bool = True
    ) -> Optional[Dataset]:
        """Sync code execution results to repository"""

        if not self.repository_connection:
            logger.warning(
                f"No repository connection available for user {self.user.username}"
            )
            return None

        try:
            with transaction.atomic():
                # Create dataset
                dataset = self._create_dataset_from_code_job(job)

                # Add output files
                self._add_code_outputs_to_dataset(job, dataset)

                # Auto-upload if requested and job completed successfully
                if auto_upload and job.status == "completed":
                    upload_dataset_to_repository(dataset)

                logger.info(f"Created dataset {dataset.id} for code job {job.job_id}")
                return dataset

        except Exception as e:
            logger.error(f"Failed to sync code execution results: {e}")
            return None

    def sync_analysis_results(
        self, analysis_job, auto_upload: bool = True
    ) -> Optional[Dataset]:
        """Sync data analysis results to repository"""

        if not self.repository_connection:
            logger.warning(
                f"No repository connection available for user {self.user.username}"
            )
            return None

        try:
            with transaction.atomic():
                # Create dataset
                dataset = self._create_dataset_from_analysis_job(analysis_job)

                # Add analysis outputs
                self._add_analysis_outputs_to_dataset(analysis_job, dataset)

                # Auto-upload if requested
                if auto_upload:
                    upload_dataset_to_repository(dataset)

                logger.info(
                    f"Created dataset {dataset.id} for analysis job {analysis_job.analysis_id}"
                )
                return dataset

        except Exception as e:
            logger.error(f"Failed to sync analysis results: {e}")
            return None

    def sync_notebook_results(
        self, notebook, auto_upload: bool = False
    ) -> Optional[Dataset]:
        """Sync notebook execution results to repository"""

        if not self.repository_connection:
            logger.warning(
                f"No repository connection available for user {self.user.username}"
            )
            return None

        try:
            with transaction.atomic():
                # Create dataset
                dataset = self._create_dataset_from_notebook(notebook)

                # Add notebook file
                self._add_notebook_to_dataset(notebook, dataset)

                # Auto-upload if requested
                if auto_upload:
                    upload_dataset_to_repository(dataset)

                logger.info(
                    f"Created dataset {dataset.id} for notebook {notebook.notebook_id}"
                )
                return dataset

        except Exception as e:
            logger.error(f"Failed to sync notebook results: {e}")
            return None
