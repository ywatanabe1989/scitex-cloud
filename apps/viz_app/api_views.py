#!/usr/bin/env python3
"""
API views for SciTeX-Viz visualization platform.
"""

import json
import logging

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction, models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import (
    Visualization,
    VisualizationType,
    DataSource,
    ExportJob,
    ColorScheme,
    ChartConfiguration,
)
from .code_integration import get_viz_data_sources_for_user

logger = logging.getLogger(__name__)


@method_decorator(login_required, name="dispatch")
class VizAPIView(View):
    """Base API view for visualization operations."""

    def get_user_visualizations(self):
        return Visualization.objects.filter(owner=self.request.user)


class VisualizationListAPI(VizAPIView):
    """API for listing and creating visualizations."""

    def get(self, request):
        """List user's visualizations."""
        try:
            visualizations = (
                self.get_user_visualizations()
                .select_related("visualization_type", "data_source", "color_scheme")
                .order_by("-updated_at")
            )

            # Pagination
            page = int(request.GET.get("page", 1))
            per_page = min(int(request.GET.get("per_page", 20)), 50)
            start = (page - 1) * per_page
            end = start + per_page

            paginated_visualizations = visualizations[start:end]

            visualizations_data = []
            for viz in paginated_visualizations:
                visualizations_data.append(
                    {
                        "id": str(viz.id),
                        "title": viz.title,
                        "description": viz.description,
                        "type": viz.visualization_type.name,
                        "type_display": viz.visualization_type.display_name,
                        "status": viz.status,
                        "is_public": viz.is_public,
                        "is_interactive": viz.is_interactive,
                        "view_count": viz.view_count,
                        "created_at": viz.created_at.isoformat(),
                        "updated_at": viz.updated_at.isoformat(),
                        "published_at": viz.published_at.isoformat()
                        if viz.published_at
                        else None,
                        "data_source": viz.data_source.name
                        if viz.data_source
                        else None,
                        "color_scheme": viz.color_scheme.name
                        if viz.color_scheme
                        else None,
                        "tags": viz.tags,
                        "version": viz.version,
                    }
                )

            return JsonResponse(
                {
                    "status": "success",
                    "visualizations": visualizations_data,
                    "pagination": {
                        "page": page,
                        "per_page": per_page,
                        "total": visualizations.count(),
                        "has_next": end < visualizations.count(),
                        "has_previous": page > 1,
                    },
                }
            )

        except Exception as e:
            logger.error(f"Error listing visualizations: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def post(self, request):
        """Create a new visualization."""
        try:
            data = json.loads(request.body)
            title = data.get("title", "").strip()
            description = data.get("description", "").strip()
            viz_type_name = data.get("type", "scatter")
            template_id = data.get("template_id")

            if not title:
                return JsonResponse(
                    {"status": "error", "message": "Title is required"}, status=400
                )

            # Get or create visualization type
            viz_type, created = VisualizationType.objects.get_or_create(
                name=viz_type_name,
                defaults={
                    "display_name": viz_type_name.replace("_", " ").title(),
                    "category": "basic",
                    "description": f"{viz_type_name} visualization",
                    "default_config": {},
                },
            )

            with transaction.atomic():
                # Create visualization
                visualization = Visualization.objects.create(
                    title=title,
                    description=description,
                    owner=request.user,
                    visualization_type=viz_type,
                    template_id=template_id if template_id else None,
                    configuration=data.get("configuration", {}),
                    data=data.get("data", {}),
                    layout=data.get("layout", {}),
                    tags=data.get("tags", []),
                )

                # Create default chart configuration
                ChartConfiguration.objects.create(
                    visualization=visualization,
                    x_axis_label=data.get("x_axis_label", ""),
                    y_axis_label=data.get("y_axis_label", ""),
                    show_grid=data.get("show_grid", True),
                    show_legend=data.get("show_legend", True),
                    legend_position=data.get("legend_position", "right"),
                )

                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Visualization created successfully",
                        "visualization": {
                            "id": str(visualization.id),
                            "title": visualization.title,
                            "description": visualization.description,
                            "type": visualization.visualization_type.name,
                            "status": visualization.status,
                        },
                    }
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error creating visualization: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class VisualizationDetailAPI(VizAPIView):
    """API for individual visualization operations."""

    def get(self, request, viz_id):
        """Get visualization details."""
        try:
            visualization = (
                self.get_user_visualizations()
                .select_related(
                    "visualization_type", "data_source", "color_scheme", "chart_config"
                )
                .get(id=viz_id)
            )

            return JsonResponse(
                {
                    "status": "success",
                    "visualization": {
                        "id": str(visualization.id),
                        "title": visualization.title,
                        "description": visualization.description,
                        "type": visualization.visualization_type.name,
                        "type_display": visualization.visualization_type.display_name,
                        "status": visualization.status,
                        "is_public": visualization.is_public,
                        "is_interactive": visualization.is_interactive,
                        "allow_download": visualization.allow_download,
                        "view_count": visualization.view_count,
                        "data": visualization.data,
                        "configuration": visualization.configuration,
                        "layout": visualization.layout,
                        "tags": visualization.tags,
                        "version": visualization.version,
                        "created_at": visualization.created_at.isoformat(),
                        "updated_at": visualization.updated_at.isoformat(),
                        "published_at": visualization.published_at.isoformat()
                        if visualization.published_at
                        else None,
                        "data_source": {
                            "id": str(visualization.data_source.id),
                            "name": visualization.data_source.name,
                            "type": visualization.data_source.source_type,
                        }
                        if visualization.data_source
                        else None,
                        "color_scheme": {
                            "id": str(visualization.color_scheme.id),
                            "name": visualization.color_scheme.name,
                            "colors": visualization.color_scheme.colors,
                        }
                        if visualization.color_scheme
                        else None,
                        "chart_config": {
                            "x_axis_label": visualization.chart_config.x_axis_label,
                            "y_axis_label": visualization.chart_config.y_axis_label,
                            "z_axis_label": visualization.chart_config.z_axis_label,
                            "show_grid": visualization.chart_config.show_grid,
                            "show_legend": visualization.chart_config.show_legend,
                            "legend_position": visualization.chart_config.legend_position,
                            "annotations": visualization.chart_config.annotations,
                        }
                        if hasattr(visualization, "chart_config")
                        else None,
                    },
                }
            )

        except Visualization.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Visualization not found"}, status=404
            )
        except Exception as e:
            logger.error(f"Error getting visualization {viz_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def put(self, request, viz_id):
        """Update visualization."""
        try:
            data = json.loads(request.body)

            visualization = self.get_user_visualizations().get(id=viz_id)

            # Update fields
            if "title" in data:
                visualization.title = data["title"]
            if "description" in data:
                visualization.description = data["description"]
            if "configuration" in data:
                visualization.configuration = data["configuration"]
            if "layout" in data:
                visualization.layout = data["layout"]
            if "data" in data:
                visualization.data = data["data"]
            if "tags" in data:
                visualization.tags = data["tags"]
            if "status" in data and data["status"] in [
                "draft",
                "published",
                "archived",
            ]:
                visualization.status = data["status"]
            if "is_public" in data:
                visualization.is_public = data["is_public"]
            if "is_interactive" in data:
                visualization.is_interactive = data["is_interactive"]
            if "allow_download" in data:
                visualization.allow_download = data["allow_download"]

            visualization.save()

            # Update chart configuration if provided
            if "chart_config" in data:
                chart_config, created = ChartConfiguration.objects.get_or_create(
                    visualization=visualization
                )
                config_data = data["chart_config"]

                if "x_axis_label" in config_data:
                    chart_config.x_axis_label = config_data["x_axis_label"]
                if "y_axis_label" in config_data:
                    chart_config.y_axis_label = config_data["y_axis_label"]
                if "z_axis_label" in config_data:
                    chart_config.z_axis_label = config_data["z_axis_label"]
                if "show_grid" in config_data:
                    chart_config.show_grid = config_data["show_grid"]
                if "show_legend" in config_data:
                    chart_config.show_legend = config_data["show_legend"]
                if "legend_position" in config_data:
                    chart_config.legend_position = config_data["legend_position"]
                if "annotations" in config_data:
                    chart_config.annotations = config_data["annotations"]

                chart_config.save()

            return JsonResponse(
                {"status": "success", "message": "Visualization updated successfully"}
            )

        except Visualization.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Visualization not found"}, status=404
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error updating visualization {viz_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def delete(self, request, viz_id):
        """Delete a visualization."""
        try:
            visualization = self.get_user_visualizations().get(id=viz_id)
            visualization.delete()

            return JsonResponse(
                {"status": "success", "message": "Visualization deleted successfully"}
            )

        except Visualization.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Visualization not found"}, status=404
            )
        except Exception as e:
            logger.error(f"Error deleting visualization {viz_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class DataSourceAPI(VizAPIView):
    """API for data source management."""

    def get(self, request):
        """List user's data sources."""
        try:
            data_sources = DataSource.objects.filter(owner=request.user).order_by(
                "-updated_at"
            )

            data_sources_data = []
            for ds in data_sources:
                data_sources_data.append(
                    {
                        "id": str(ds.id),
                        "name": ds.name,
                        "type": ds.source_type,
                        "status": ds.status,
                        "last_updated": ds.last_updated.isoformat()
                        if ds.last_updated
                        else None,
                        "created_at": ds.created_at.isoformat(),
                        "error_message": ds.error_message,
                    }
                )

            return JsonResponse(
                {"status": "success", "data_sources": data_sources_data}
            )

        except Exception as e:
            logger.error(f"Error listing data sources: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def post(self, request):
        """Create a new data source."""
        try:
            data = json.loads(request.body)
            name = data.get("name", "").strip()
            source_type = data.get("type", "file")
            connection_config = data.get("connection_config", {})

            if not name:
                return JsonResponse(
                    {"status": "error", "message": "Name is required"}, status=400
                )

            # Check for duplicate names
            if DataSource.objects.filter(owner=request.user, name=name).exists():
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "A data source with this name already exists",
                    },
                    status=400,
                )

            data_source = DataSource.objects.create(
                name=name,
                owner=request.user,
                source_type=source_type,
                connection_config=connection_config,
                refresh_interval=data.get("refresh_interval"),
                status="active",
            )

            return JsonResponse(
                {
                    "status": "success",
                    "message": "Data source created successfully",
                    "data_source": {
                        "id": str(data_source.id),
                        "name": data_source.name,
                        "type": data_source.source_type,
                        "status": data_source.status,
                    },
                }
            )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error creating data source: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class VisualizationTypesAPI(View):
    """API for available visualization types."""

    def get(self, request):
        """Get available visualization types."""
        try:
            viz_types = VisualizationType.objects.filter(is_active=True).order_by(
                "category", "display_name"
            )

            types_by_category = {}
            for vt in viz_types:
                if vt.category not in types_by_category:
                    types_by_category[vt.category] = []

                types_by_category[vt.category].append(
                    {
                        "name": vt.name,
                        "display_name": vt.display_name,
                        "description": vt.description,
                        "icon": vt.icon,
                        "default_config": vt.default_config,
                    }
                )

            return JsonResponse(
                {"status": "success", "types_by_category": types_by_category}
            )

        except Exception as e:
            logger.error(f"Error getting visualization types: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class ColorSchemesAPI(VizAPIView):
    """API for color schemes."""

    def get(self, request):
        """Get available color schemes."""
        try:
            # Get user's color schemes and public ones
            color_schemes = ColorScheme.objects.filter(
                models.Q(owner=request.user) | models.Q(is_public=True)
            ).order_by("-created_at")

            schemes_data = []
            for cs in color_schemes:
                schemes_data.append(
                    {
                        "id": str(cs.id),
                        "name": cs.name,
                        "colors": cs.colors,
                        "category": cs.category,
                        "is_public": cs.is_public,
                        "owner": cs.owner.username,
                        "created_at": cs.created_at.isoformat(),
                    }
                )

            return JsonResponse({"status": "success", "color_schemes": schemes_data})

        except Exception as e:
            logger.error(f"Error getting color schemes: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


class ExportAPI(VizAPIView):
    """API for exporting visualizations."""

    def post(self, request, viz_id):
        """Export visualization in specified format."""
        try:
            data = json.loads(request.body)
            export_format = data.get("format", "png")
            options = data.get("options", {})

            visualization = self.get_user_visualizations().get(id=viz_id)

            # Create export job
            export_job = ExportJob.objects.create(
                visualization=visualization,
                user=request.user,
                format=export_format,
                options=options,
                status="pending",
            )

            # For demonstration, return immediate success for JSON/CSV formats
            if export_format in ["json", "csv"]:
                if export_format == "json":
                    export_data = {
                        "title": visualization.title,
                        "type": visualization.visualization_type.name,
                        "data": visualization.data,
                        "configuration": visualization.configuration,
                        "layout": visualization.layout,
                        "exported_at": export_job.created_at.isoformat(),
                    }
                    content = json.dumps(export_data, indent=2)
                    filename = f"{visualization.title}.json"

                elif export_format == "csv":
                    # Convert data to CSV format
                    import csv
                    import io

                    output = io.StringIO()
                    if visualization.data and isinstance(visualization.data, dict):
                        # Handle different data structures
                        if "x" in visualization.data and "y" in visualization.data:
                            writer = csv.writer(output)
                            writer.writerow(
                                ["x", "y"]
                                + (["z"] if "z" in visualization.data else [])
                            )

                            x_data = visualization.data["x"]
                            y_data = visualization.data["y"]
                            z_data = visualization.data.get("z", [])

                            for i in range(len(x_data)):
                                row = [x_data[i], y_data[i]]
                                if z_data and i < len(z_data):
                                    row.append(z_data[i])
                                writer.writerow(row)

                    content = output.getvalue()
                    filename = f"{visualization.title}.csv"

                export_job.status = "completed"
                export_job.save()

                return JsonResponse(
                    {
                        "status": "success",
                        "export_type": "direct",
                        "content": content,
                        "filename": filename,
                        "job_id": str(export_job.id),
                    }
                )

            else:
                # For image formats, return job ID for polling
                return JsonResponse(
                    {
                        "status": "success",
                        "export_type": "async",
                        "job_id": str(export_job.id),
                        "message": f"Export to {export_format.upper()} initiated. Check job status for completion.",
                    }
                )

        except Visualization.DoesNotExist:
            return JsonResponse(
                {"status": "error", "message": "Visualization not found"}, status=404
            )
        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON"}, status=400
            )
        except Exception as e:
            logger.error(f"Error exporting visualization {viz_id}: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
@csrf_exempt
def upload_data(request):
    """Handle data file uploads."""
    try:
        if "file" not in request.FILES:
            return JsonResponse(
                {"status": "error", "message": "No file provided"}, status=400
            )

        uploaded_file = request.FILES["file"]

        # Validate file type
        allowed_extensions = [".csv", ".json", ".xlsx", ".txt"]
        file_extension = "." + uploaded_file.name.split(".")[-1].lower()

        if file_extension not in allowed_extensions:
            return JsonResponse(
                {
                    "status": "error",
                    "message": f"Unsupported file type. Allowed: {', '.join(allowed_extensions)}",
                },
                status=400,
            )

        # Read and parse file content
        file_content = uploaded_file.read()

        if file_extension == ".csv":
            import csv
            import io

            text_content = file_content.decode("utf-8")
            csv_reader = csv.DictReader(io.StringIO(text_content))

            data = {}
            for row in csv_reader:
                for key, value in row.items():
                    if key not in data:
                        data[key] = []
                    # Try to convert to number
                    try:
                        numeric_value = float(value)
                        data[key].append(numeric_value)
                    except (ValueError, TypeError):
                        data[key].append(value)

            data["columns"] = list(data.keys())

        elif file_extension == ".json":
            data = json.loads(file_content.decode("utf-8"))

        else:
            return JsonResponse(
                {
                    "status": "error",
                    "message": "File parsing not implemented for this type",
                },
                status=400,
            )

        # Save file to storage (optional)
        file_path = default_storage.save(
            f"viz_data/{request.user.id}/{uploaded_file.name}",
            ContentFile(file_content),
        )

        data["name"] = uploaded_file.name
        data["file_path"] = file_path

        return JsonResponse(
            {
                "status": "success",
                "message": "Data uploaded and parsed successfully",
                "data": data,
                "file_info": {
                    "name": uploaded_file.name,
                    "size": uploaded_file.size,
                    "type": file_extension,
                },
            }
        )

    except Exception as e:
        logger.error(f"Error uploading data: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def export_job_status(request, job_id):
    """Check export job status."""
    try:
        export_job = ExportJob.objects.get(id=job_id, user=request.user)

        response_data = {
            "job_id": str(export_job.id),
            "status": export_job.status,
            "format": export_job.format,
            "created_at": export_job.created_at.isoformat(),
            "completed_at": export_job.completed_at.isoformat()
            if export_job.completed_at
            else None,
        }

        if export_job.status == "completed" and export_job.file_path:
            response_data["download_url"] = f"/viz/api/download/{export_job.id}/"
        elif export_job.status == "failed":
            response_data["error"] = export_job.error_message

        return JsonResponse({"status": "success", **response_data})

    except ExportJob.DoesNotExist:
        return JsonResponse(
            {"status": "error", "message": "Export job not found"}, status=404
        )
    except Exception as e:
        logger.error(f"Error getting export job status {job_id}: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@login_required
@require_http_methods(["GET"])
def generate_sample_data(request):
    """Generate sample scientific data for testing."""
    try:
        data_type = request.GET.get("type", "scatter")
        size = min(int(request.GET.get("size", 100)), 1000)

        import math
        import random

        if data_type == "scatter":
            x = [random.uniform(0, 10) for _ in range(size)]
            y = [random.uniform(0, 10) for _ in range(size)]
            z = [
                math.sin(x[i]) * math.cos(y[i]) + random.uniform(-0.5, 0.5)
                for i in range(size)
            ]

            data = {
                "x": x,
                "y": y,
                "z": z,
                "columns": ["x", "y", "z"],
                "name": f"Sample Scatter Data ({size} points)",
            }

        elif data_type == "timeseries":
            import datetime

            start_date = datetime.datetime.now() - datetime.timedelta(days=size)
            dates = [
                (start_date + datetime.timedelta(days=i)).isoformat()
                for i in range(size)
            ]
            values = [
                50 + 10 * math.sin(i * 0.1) + random.uniform(-5, 5) for i in range(size)
            ]

            data = {
                "date": dates,
                "value": values,
                "columns": ["date", "value"],
                "name": f"Sample Time Series ({size} points)",
            }

        elif data_type == "surface":
            grid_size = int(math.sqrt(size))
            x = []
            y = []
            z = []

            for i in range(grid_size):
                for j in range(grid_size):
                    x_val = (i - grid_size / 2) / 5
                    y_val = (j - grid_size / 2) / 5
                    z_val = math.sin(math.sqrt(x_val**2 + y_val**2))

                    x.append(x_val)
                    y.append(y_val)
                    z.append(z_val)

            data = {
                "x": x,
                "y": y,
                "z": z,
                "columns": ["x", "y", "z"],
                "name": f"Sample Surface Data ({len(x)} points)",
            }

        else:
            return JsonResponse(
                {"status": "error", "message": "Unsupported data type"}, status=400
            )

        return JsonResponse({"status": "success", "data": data})

    except Exception as e:
        logger.error(f"Error generating sample data: {e}")
        return JsonResponse({"status": "error", "message": str(e)}, status=500)


@method_decorator(login_required, name="dispatch")
class CodeDataSourceAPI(VizAPIView):
    """API for Code module data source integration."""

    def get(self, request):
        """Get available code execution results as data sources."""
        try:
            code_sources = get_viz_data_sources_for_user(request.user)

            return JsonResponse(
                {
                    "status": "success",
                    "code_sources": code_sources,
                    "count": len(code_sources),
                }
            )

        except Exception as e:
            logger.error(f"Error fetching code data sources: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)

    def post(self, request):
        """Create data source from code execution job."""
        try:
            data = json.loads(request.body)
            job_id = data.get("job_id")

            if not job_id:
                return JsonResponse(
                    {"status": "error", "message": "job_id is required"}, status=400
                )

            # Import here to avoid circular imports
            from apps.code_app.models import CodeExecutionJob
            from .code_integration import CodeVizBridge

            # Get the code job
            try:
                code_job = CodeExecutionJob.objects.get(
                    job_id=job_id, user=request.user, status="completed"
                )
            except CodeExecutionJob.DoesNotExist:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Code execution job not found or not completed",
                    },
                    status=404,
                )

            # Create data source and visualizations
            bridge = CodeVizBridge()
            result = bridge.sync_code_job_completion(code_job)

            if result.get("data_source_created"):
                return JsonResponse(
                    {
                        "status": "success",
                        "message": "Data source created successfully",
                        "data_source_id": result.get("data_source_id"),
                        "visualizations_created": result.get(
                            "visualizations_created", 0
                        ),
                        "errors": result.get("errors", []),
                    }
                )
            else:
                return JsonResponse(
                    {
                        "status": "error",
                        "message": "Failed to create data source",
                        "errors": result.get("errors", []),
                    },
                    status=500,
                )

        except json.JSONDecodeError:
            return JsonResponse(
                {"status": "error", "message": "Invalid JSON data"}, status=400
            )
        except Exception as e:
            logger.error(f"Error creating code data source: {e}")
            return JsonResponse({"status": "error", "message": str(e)}, status=500)
