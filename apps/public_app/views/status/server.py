#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views/status/server.py
# Auto-restored from commit ef627adc
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views/status/server.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
import socket
import psutil
from pathlib import Path
from django.db import connection
from django.core.cache import cache
from datetime import datetime, timedelta
from ...models import ServerMetrics
# Note: Helper functions not needed - logic implemented inline in views


def server_status(request):
    """
    Server Status Page.

    Shows comprehensive server health status:
    - Docker containers status
    - SSH services (workspace gateway, Gitea)
    - Database connection
    - Redis connection
    - Disk usage
    """
    import socket
    import psutil
    from pathlib import Path
    from django.db import connection
    from django.core.cache import cache
    import os

    status_data = {
        "services": [],
        "ssh_services": [],
        "database": {"status": "unknown", "message": ""},
        "redis": {"status": "unknown", "message": ""},
        "disk": {"status": "unknown", "usage": 0, "message": ""},
    }

    # Check Docker containers
    try:
        import subprocess

        result = subprocess.run(
            ["docker", "ps", "--format", "{{.Names}}\t{{.Status}}"],
            capture_output=True,
            text=True,
            timeout=5,
        )

        if result.returncode == 0:
            for line in result.stdout.strip().split("\n"):
                if line:
                    parts = line.split("\t")
                    if len(parts) >= 2:
                        name = parts[0]
                        status = parts[1]

                        # Only show relevant containers
                        if any(
                            keyword in name.lower()
                            for keyword in [
                                "django",
                                "postgres",
                                "redis",
                                "celery",
                                "gitea",
                                "flower",
                            ]
                        ):
                            # Determine status
                            is_healthy = "up" in status.lower() and (
                                "healthy" in status.lower()
                                or "health" not in status.lower()
                            )

                            status_data["services"].append(
                                {
                                    "name": name.replace("scitex-cloud-dev-", "").replace(
                                        "-1", ""
                                    ),
                                    "status": "running" if is_healthy else "warning",
                                    "message": status,
                                }
                            )
    except Exception as e:
        status_data["services"].append(
            {"name": "Docker", "status": "error", "message": str(e)}
        )

    # Check SSH services
    ssh_services = [
        {"name": "Workspace Gateway SSH", "host": "127.0.0.1", "port": 2200},
        {"name": "Gitea SSH", "host": "127.0.0.1", "port": 2222},
    ]

    for service in ssh_services:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(2)
            result = sock.connect_ex((service["host"], service["port"]))
            sock.close()

            if result == 0:
                status_data["ssh_services"].append(
                    {
                        "name": service["name"],
                        "status": "running",
                        "message": f"Port {service['port']} accessible",
                    }
                )
            else:
                status_data["ssh_services"].append(
                    {
                        "name": service["name"],
                        "status": "error",
                        "message": f"Port {service['port']} not accessible",
                    }
                )
        except Exception as e:
            status_data["ssh_services"].append(
                {"name": service["name"], "status": "error", "message": str(e)}
            )

    # Check Database connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        status_data["database"] = {
            "status": "running",
            "message": "Database connection successful",
        }
    except Exception as e:
        status_data["database"] = {"status": "error", "message": f"Database error: {e}"}

    # Check Redis connection
    try:
        cache.set("health_check", "ok", 10)
        if cache.get("health_check") == "ok":
            status_data["redis"] = {
                "status": "running",
                "message": "Redis connection successful",
            }
        else:
            status_data["redis"] = {
                "status": "warning",
                "message": "Redis set/get mismatch",
            }
    except Exception as e:
        status_data["redis"] = {"status": "error", "message": f"Redis error: {e}"}

    # Check Disk Usage
    try:
        usage = psutil.disk_usage("/")
        percent = usage.percent

        if percent < 80:
            disk_status = "running"
        elif percent < 90:
            disk_status = "warning"
        else:
            disk_status = "error"

        status_data["disk"] = {
            "status": disk_status,
            "usage": percent,
            "message": f"{percent:.1f}% used ({usage.used / (1024**3):.1f}GB / {usage.total / (1024**3):.1f}GB)",
        }
    except Exception as e:
        status_data["disk"] = {"status": "error", "usage": 0, "message": str(e)}

    return render(request, "public_app/server_status.html", {"status": status_data})


@require_http_methods(["GET"])
def server_status_api(request):
    """API endpoint for real-time server metrics (returns JSON)"""
    import psutil

    metrics = {
        "cpu": psutil.cpu_percent(interval=0.1),
        "memory": psutil.virtual_memory().percent,
        "disk": psutil.disk_usage("/").percent,
        "timestamp": datetime.now().isoformat(),
    }

    # Get network stats if available
    try:
        net_io = psutil.net_io_counters()
        metrics["network"] = {
            "bytes_sent": net_io.bytes_sent,
            "bytes_recv": net_io.bytes_recv,
        }
    except:
        pass

    # Store in database for history
    try:
        mem = psutil.virtual_memory()
        disk = psutil.disk_usage("/")

        ServerMetrics.objects.create(
            timestamp=datetime.now(),
            cpu_percent=metrics["cpu"],
            memory_percent=metrics["memory"],
            memory_used_gb=mem.used / (1024**3),
            memory_total_gb=mem.total / (1024**3),
            memory_available_gb=mem.available / (1024**3),
            disk_percent=metrics["disk"],
            disk_used_gb=disk.used / (1024**3),
            disk_total_gb=disk.total / (1024**3),
            disk_read_mb=0,  # psutil.disk_io_counters() not always available
            disk_write_mb=0,
            net_sent_mb=metrics.get("network", {}).get("bytes_sent", 0) / (1024**2),
            net_recv_mb=metrics.get("network", {}).get("bytes_recv", 0) / (1024**2),
        )

        # Clean up old metrics (keep only last 24 hours)
        cutoff = datetime.now() - timedelta(hours=24)
        ServerMetrics.objects.filter(timestamp__lt=cutoff).delete()
    except Exception as e:
        print(f"Error storing metrics: {e}")

    return JsonResponse(metrics)


@require_http_methods(["GET"])
def server_metrics_history_api(request):
    """API endpoint for historical server metrics"""
    try:
        # Get hours parameter (default 1 hour)
        hours = int(request.GET.get("hours", 1))
        hours = min(hours, 24)  # Max 24 hours

        # Get limit parameter (default 100 points)
        limit = int(request.GET.get("limit", 100))
        limit = min(limit, 1000)  # Max 1000 points

        # Calculate time range
        cutoff = datetime.now() - timedelta(hours=hours)

        # Get metrics from database
        metrics = (
            ServerMetrics.objects.filter(timestamp__gte=cutoff)
            .order_by("-timestamp")[:limit]
            .values("timestamp", "cpu_usage", "memory_usage", "disk_usage")
        )

        # Convert to list and reverse (oldest first)
        metrics_list = list(reversed(list(metrics)))

        # Convert datetime to ISO format
        for metric in metrics_list:
            metric["timestamp"] = metric["timestamp"].isoformat()

        return JsonResponse(
            {"metrics": metrics_list, "hours": hours, "count": len(metrics_list)}
        )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_http_methods(["GET"])
@login_required
def server_metrics_export_csv(request):
    """Export server metrics as CSV"""
    import csv
    from io import StringIO

    try:
        # Get hours parameter (default 24 hours)
        hours = int(request.GET.get("hours", 24))
        hours = min(hours, 168)  # Max 1 week

        # Calculate time range
        cutoff = datetime.now() - timedelta(hours=hours)

        # Get metrics from database
        metrics = ServerMetrics.objects.filter(timestamp__gte=cutoff).order_by(
            "timestamp"
        )

        # Create CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write header
        writer.writerow(["Timestamp", "CPU Usage (%)", "Memory Usage (%)", "Disk Usage (%)"])

        # Write data
        for metric in metrics:
            writer.writerow(
                [
                    metric.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
                    f"{metric.cpu_usage:.2f}",
                    f"{metric.memory_usage:.2f}",
                    f"{metric.disk_usage:.2f}",
                ]
            )

        # Create response
        response = HttpResponse(output.getvalue(), content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="server_metrics_{datetime.now().strftime("%Y%m%d_%H%M%S")}.csv"'
        )

        return response

    except Exception as e:
        return HttpResponse(f"Error exporting metrics: {e}", status=500)
