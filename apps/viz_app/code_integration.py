#!/usr/bin/env python3
"""
Code-Viz Integration Bridge for SciTeX-Cloud
Connects Code execution results with Viz module data sources.
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import DataSource, Visualization, VisualizationType
from apps.code_app.models import CodeExecutionJob

logger = logging.getLogger(__name__)


class CodeVizBridge:
    """Bridge between Code execution results and Viz module data sources."""

    def __init__(self):
        self.media_root = Path(settings.MEDIA_ROOT)

    def create_data_source_from_code_job(
        self, code_job: CodeExecutionJob
    ) -> Optional[DataSource]:
        """Create a Viz data source from completed code execution job."""
        try:
            if code_job.status != "completed":
                logger.warning(
                    f"Code job {code_job.job_id} not completed, cannot create data source"
                )
                return None

            # Extract data and metadata from code job
            data_source_name = f"Code Execution - {code_job.job_id}"

            # Prepare connection config with code job metadata
            connection_config = {
                "code_job_id": str(code_job.job_id),
                "execution_type": code_job.execution_type,
                "created_at": code_job.created_at.isoformat(),
                "completed_at": code_job.completed_at.isoformat()
                if code_job.completed_at
                else None,
                "output_files": code_job.output_files,
                "plot_files": code_job.plot_files,
                "source_code_preview": code_job.source_code[:500] + "..."
                if len(code_job.source_code) > 500
                else code_job.source_code,
            }

            # Extract data schema if available
            schema = self._extract_data_schema(code_job)

            # Create data source
            data_source = DataSource.objects.create(
                name=data_source_name,
                owner=code_job.user,
                source_type="code_execution",
                connection_config=connection_config,
                schema=schema,
                status="active",
                last_updated=timezone.now(),
            )

            logger.info(
                f"Created data source {data_source.id} from code job {code_job.job_id}"
            )
            return data_source

        except Exception as e:
            logger.error(
                f"Error creating data source from code job {code_job.job_id}: {e}"
            )
            return None

    def _extract_data_schema(self, code_job: CodeExecutionJob) -> Dict[str, Any]:
        """Extract data schema from code execution results."""
        schema = {"plots": [], "data_files": [], "variables": []}

        try:
            # Process plot files
            for plot_file in code_job.plot_files:
                plot_path = (
                    self.media_root
                    / "visualizations"
                    / str(code_job.user.id)
                    / plot_file
                )
                if plot_path.exists():
                    schema["plots"].append(
                        {
                            "filename": plot_file,
                            "path": str(plot_path),
                            "size": plot_path.stat().st_size,
                            "type": "image",
                        }
                    )

            # Process output files
            for output_file in code_job.output_files:
                if isinstance(output_file, dict):
                    schema["data_files"].append(output_file)
                else:
                    # Assume it's a filename
                    output_path = (
                        self.media_root
                        / "code_outputs"
                        / str(code_job.user.id)
                        / output_file
                    )
                    if output_path.exists():
                        schema["data_files"].append(
                            {
                                "filename": output_file,
                                "path": str(output_path),
                                "size": output_path.stat().st_size,
                                "type": self._get_file_type(output_file),
                            }
                        )

            # Extract variables from output if structured
            if code_job.output:
                try:
                    # Try to parse JSON output for variable information
                    output_data = json.loads(code_job.output)
                    if isinstance(output_data, dict):
                        schema["variables"] = list(output_data.keys())
                except (json.JSONDecodeError, TypeError):
                    # Output is not JSON, skip variable extraction
                    pass

        except Exception as e:
            logger.warning(
                f"Error extracting schema from code job {code_job.job_id}: {e}"
            )

        return schema

    def _get_file_type(self, filename: str) -> str:
        """Determine file type from extension."""
        extension = Path(filename).suffix.lower()
        type_mapping = {
            ".csv": "csv",
            ".json": "json",
            ".txt": "text",
            ".png": "image",
            ".jpg": "image",
            ".jpeg": "image",
            ".svg": "image",
            ".pdf": "document",
            ".xlsx": "excel",
            ".h5": "hdf5",
            ".npz": "numpy",
            ".pkl": "pickle",
        }
        return type_mapping.get(extension, "unknown")

    def create_visualization_from_code_job(
        self, code_job: CodeExecutionJob, plot_filename: str = None
    ) -> Optional[Visualization]:
        """Create a Viz visualization from code execution plot."""
        try:
            if not code_job.plot_files:
                logger.warning(f"Code job {code_job.job_id} has no plot files")
                return None

            # Use specified plot or first available
            target_plot = plot_filename or code_job.plot_files[0]
            if target_plot not in code_job.plot_files:
                logger.error(
                    f"Plot file {target_plot} not found in code job {code_job.job_id}"
                )
                return None

            # Create or get data source
            data_source = self.create_data_source_from_code_job(code_job)
            if not data_source:
                return None

            # Determine visualization type based on plot
            viz_type = self._determine_visualization_type(target_plot)
            if not viz_type:
                logger.error(
                    f"Could not determine visualization type for {target_plot}"
                )
                return None

            # Create visualization
            visualization = Visualization.objects.create(
                title=f"Code Plot - {target_plot}",
                owner=code_job.user,
                visualization_type=viz_type,
                data_source=data_source,
                description=f"Generated from code execution {code_job.job_id}",
                configuration={
                    "source_plot": target_plot,
                    "code_job_id": str(code_job.job_id),
                    "original_code_preview": code_job.source_code[:200] + "..."
                    if len(code_job.source_code) > 200
                    else code_job.source_code,
                },
                status="published",
                is_public=False,
                tags=["code-generated", "automated"],
            )

            logger.info(
                f"Created visualization {visualization.id} from code job {code_job.job_id}"
            )
            return visualization

        except Exception as e:
            logger.error(
                f"Error creating visualization from code job {code_job.job_id}: {e}"
            )
            return None

    def _determine_visualization_type(
        self, plot_filename: str
    ) -> Optional[VisualizationType]:
        """Determine visualization type from plot filename."""
        filename_lower = plot_filename.lower()

        # Map filename patterns to visualization types
        type_mapping = {
            "line": ["line", "timeseries", "time_series"],
            "scatter": ["scatter", "scatterplot"],
            "bar": ["bar", "histogram", "hist"],
            "heatmap": ["heatmap", "heat", "correlation"],
            "boxplot": ["box", "boxplot"],
            "violin": ["violin"],
            "pair": ["pair", "pairplot"],
        }

        for viz_type_name, patterns in type_mapping.items():
            if any(pattern in filename_lower for pattern in patterns):
                try:
                    return VisualizationType.objects.get(name=viz_type_name)
                except VisualizationType.DoesNotExist:
                    continue

        # Default to basic chart type
        try:
            return VisualizationType.objects.filter(category="basic").first()
        except VisualizationType.DoesNotExist:
            return None

    def get_available_code_data_sources(self, user: User) -> List[Dict[str, Any]]:
        """Get all available code execution results as potential data sources."""
        completed_jobs = CodeExecutionJob.objects.filter(
            user=user, status="completed"
        ).order_by("-completed_at")

        data_sources = []
        for job in completed_jobs:
            source_info = {
                "job_id": str(job.job_id),
                "execution_type": job.execution_type,
                "completed_at": job.completed_at,
                "plot_files": job.plot_files,
                "output_files": job.output_files,
                "has_plots": bool(job.plot_files),
                "has_data": bool(job.output_files),
                "title": f"Code Execution - {job.job_id}",
                "description": f"{job.execution_type} completed on {job.completed_at.strftime('%Y-%m-%d %H:%M')}",
            }
            data_sources.append(source_info)

        return data_sources

    def sync_code_job_completion(self, code_job: CodeExecutionJob) -> Dict[str, Any]:
        """Automatically sync completed code job to Viz module."""
        result = {
            "data_source_created": False,
            "visualizations_created": 0,
            "errors": [],
        }

        try:
            # Create data source
            data_source = self.create_data_source_from_code_job(code_job)
            if data_source:
                result["data_source_created"] = True
                result["data_source_id"] = data_source.id

                # Create visualizations for each plot file
                for plot_file in code_job.plot_files:
                    viz = self.create_visualization_from_code_job(code_job, plot_file)
                    if viz:
                        result["visualizations_created"] += 1
                    else:
                        result["errors"].append(
                            f"Failed to create visualization for {plot_file}"
                        )
            else:
                result["errors"].append("Failed to create data source")

        except Exception as e:
            result["errors"].append(f"Sync error: {str(e)}")
            logger.error(f"Error syncing code job {code_job.job_id}: {e}")

        return result


# Integration functions for use in Code module
def auto_sync_code_completion(code_job: CodeExecutionJob) -> Dict[str, Any]:
    """Auto-sync function to be called when code execution completes."""
    bridge = CodeVizBridge()
    return bridge.sync_code_job_completion(code_job)


def get_viz_data_sources_for_user(user: User) -> List[Dict[str, Any]]:
    """Get available code data sources for a user."""
    bridge = CodeVizBridge()
    return bridge.get_available_code_data_sources(user)
