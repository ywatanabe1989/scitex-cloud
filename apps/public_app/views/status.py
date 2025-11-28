#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-28 21:31:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views/status.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views/status.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Server Status and Monitoring Views

Handles server status, visitor status, and metrics endpoints.
"""

import csv
import logging
import socket
import subprocess
import time
from datetime import timedelta
from pathlib import Path

import psutil
from django.conf import settings
from django.core.cache import cache
from django.db import connection
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone

logger = logging.getLogger("scitex")


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
    status_data = {
        "services": [],
        "ssh_services": [],
        "database": {},
        "redis": {},
        "disk": {},
        "system": {},
    }

    # Determine environment for container name filter
    scitex_env = os.environ.get("SCITEX_CLOUD_ENV", "dev")
    container_name_prefix = f"scitex-cloud-{scitex_env}"

    # Check Docker containers
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list(all=True, filters={"name": container_name_prefix})

        for container in containers:
            # Get health status if available
            health_status = None
            try:
                health = container.attrs.get('State', {}).get('Health', {})
                health_status = health.get('Status') if health else None
            except Exception:
                pass

            # Determine display status and health class
            is_running = container.status == "running"
            if health_status:
                display_status = f"{container.status} ({health_status})"
                health_class = health_status  # healthy, unhealthy, starting
            else:
                display_status = container.status
                health_class = "healthy" if is_running else "down"

            status_data["services"].append({
                "name": container.name.replace("scitex-cloud-dev-", "").replace("-1", ""),
                "status": container.status,
                "display_status": display_status,
                "health_status": health_status,
                "health_class": health_class,
                "is_running": is_running,
                "is_healthy": is_running and health_status in (None, "healthy"),
                "image": container.image.tags[0] if container.image.tags else "unknown",
            })
    except Exception as e:
        logger.warning(f"Could not check Docker containers: {e}")
        status_data["services"].append({
            "name": "Docker",
            "status": "unavailable",
            "display_status": "unavailable",
            "health_status": None,
            "health_class": "down",
            "is_running": False,
            "is_healthy": False,
            "error": str(e),
        })

    # Check SSH services
    # Determine host to check - use host.docker.internal if in Docker, otherwise localhost
    ssh_check_host = '127.0.0.1'
    if Path('/.dockerenv').exists():
        # We're running inside Docker, check host services
        ssh_check_host = 'host.docker.internal'

    # Workspace SSH Gateway (port 2200)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ssh_check_host, 2200))
        sock.close()
        is_running = result == 0
        status_data["ssh_services"].append({
            "name": "Workspace SSH Gateway",
            "port": 2200,
            "is_running": is_running,
            "status": "running" if is_running else "down",
            "health_class": "healthy" if is_running else "down",
        })
    except Exception as e:
        status_data["ssh_services"].append({
            "name": "Workspace SSH Gateway",
            "port": 2200,
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        })

    # Gitea SSH (port from settings - dev: 2222, nas: 222, prod: 22)
    gitea_ssh_port = int(getattr(settings, 'SCITEX_CLOUD_GITEA_SSH_PORT', 2222))
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex((ssh_check_host, gitea_ssh_port))
        sock.close()
        is_running = result == 0
        status_data["ssh_services"].append({
            "name": "Gitea SSH (Git operations)",
            "port": gitea_ssh_port,
            "is_running": is_running,
            "status": "running" if is_running else "down",
            "health_class": "healthy" if is_running else "down",
        })
    except Exception as e:
        status_data["ssh_services"].append({
            "name": "Gitea SSH",
            "port": gitea_ssh_port,
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        })

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status_data["database"] = {
                "is_running": True,
                "status": "connected",
                "health_class": "healthy",
                "backend": connection.settings_dict['ENGINE'].split('.')[-1],
                "name": connection.settings_dict['NAME'],
            }
    except Exception as e:
        status_data["database"] = {
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        }

    # Check Redis
    try:
        cache.set('health_check', 'ok', 10)
        test_value = cache.get('health_check')
        is_connected = test_value == 'ok'
        status_data["redis"] = {
            "is_running": is_connected,
            "status": "connected" if is_connected else "error",
            "health_class": "healthy" if is_connected else "unhealthy",
        }
    except Exception as e:
        status_data["redis"] = {
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        }

    # Check disk usage
    try:
        disk = psutil.disk_usage('/')
        status_data["disk"] = {
            "total_tb": round(disk.total / (1024**4), 2),
            "used_tb": round(disk.used / (1024**4), 2),
            "free_tb": round(disk.free / (1024**4), 2),
            "percent_used": disk.percent,
            "is_healthy": disk.percent < 90,
        }
    except Exception as e:
        status_data["disk"] = {
            "is_healthy": False,
            "error": str(e),
        }

    # Check SLURM status
    _check_slurm_status(status_data)

    # Check Apptainer/Singularity status
    _check_container_runtime_status(status_data)

    # System resources
    _check_system_resources(status_data)

    # Get visitor pool status
    _check_visitor_pool_status(request, status_data)

    context = {
        "status_data": status_data,
    }

    return render(request, "public_app/server_status.html", context)


def _check_slurm_status(status_data):
    """Check SLURM cluster status."""
    try:
        # Use sinfo to check if SLURM is responding - this is more reliable
        result = subprocess.run(
            ['sinfo', '--noheader', '-o', '%P %a %D %t'],
            capture_output=True, text=True, timeout=5
        )
        is_up = result.returncode == 0 and result.stdout.strip()
        status_data["slurm"] = {
            "is_running": is_up,
            "status": "running" if is_up else "down",
            "health_class": "healthy" if is_up else "unhealthy",
            "message": "SLURM cluster is operational" if is_up else result.stderr.strip() or "SLURM not responding",
            "partitions": result.stdout.strip() if is_up else None,
        }
        # Get job queue info if SLURM is up
        if is_up:
            try:
                squeue_result = subprocess.run(
                    ['squeue', '--noheader', '-o', '%i %P %j %u %t %M'],
                    capture_output=True, text=True, timeout=5
                )
                status_data["slurm"]["jobs"] = squeue_result.stdout.strip() or "No jobs running"
            except Exception:
                pass
    except FileNotFoundError:
        status_data["slurm"] = {
            "is_running": False,
            "status": "not installed",
            "health_class": "down",
            "error": "SLURM not installed",
        }
    except Exception as e:
        status_data["slurm"] = {
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        }


def _check_container_runtime_status(status_data):
    """Check Apptainer/Singularity container runtime status."""
    try:
        # Try apptainer first, then singularity
        container_cmd = None
        for cmd in ['apptainer', 'singularity']:
            try:
                result = subprocess.run(
                    [cmd, '--version'],
                    capture_output=True, text=True, timeout=5
                )
                if result.returncode == 0:
                    container_cmd = cmd
                    version = result.stdout.strip()
                    break
            except FileNotFoundError:
                continue

        if container_cmd:
            status_data["apptainer"] = {
                "is_running": True,
                "status": "available",
                "health_class": "healthy",
                "command": container_cmd,
                "version": version,
            }
        else:
            status_data["apptainer"] = {
                "is_running": False,
                "status": "not installed",
                "health_class": "down",
                "error": "Apptainer/Singularity not installed",
            }
    except Exception as e:
        status_data["apptainer"] = {
            "is_running": False,
            "status": "error",
            "health_class": "unhealthy",
            "error": str(e),
        }


def _check_system_resources(status_data):
    """Check system resource usage."""
    try:
        # CPU information
        cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)

        # Try to get CPU name from /proc/cpuinfo (Linux)
        cpu_name = "Unknown"
        try:
            with open('/proc/cpuinfo', 'r') as f:
                for line in f:
                    if 'model name' in line:
                        cpu_name = line.split(':')[1].strip()
                        break
        except:
            pass

        # GPU information
        gpu_info = _get_gpu_info(cpu_name)

        # Disk I/O stats
        disk_io = psutil.disk_io_counters()
        disk_read_mb = round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0
        disk_write_mb = round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0

        # Network I/O stats
        net_io = psutil.net_io_counters()
        net_sent_mb = round(net_io.bytes_sent / (1024**2), 2) if net_io else 0
        net_recv_mb = round(net_io.bytes_recv / (1024**2), 2) if net_io else 0

        status_data["system"] = {
            "cpu_percent": psutil.cpu_percent(interval=1),
            "cpu_cores": cpu_count,
            "cpu_cores_logical": cpu_count_logical,
            "cpu_name": cpu_name,
            "memory_percent": psutil.virtual_memory().percent,
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 1),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 1),
            "gpu_info": gpu_info,
            "disk_read_mb": disk_read_mb,
            "disk_write_mb": disk_write_mb,
            "net_sent_mb": net_sent_mb,
            "net_recv_mb": net_recv_mb,
        }
    except Exception as e:
        status_data["system"] = {"error": str(e)}


def _get_gpu_info(cpu_name):
    """Get GPU information from various sources."""
    gpu_info = "None available"
    try:
        # Try NVIDIA first
        try:
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except:
            pass

        # If no NVIDIA GPU, check CPU info for integrated graphics
        if cpu_name and ('Radeon Graphics' in cpu_name or 'Intel' in cpu_name):
            if 'Radeon Graphics' in cpu_name:
                return "AMD Radeon Graphics (Integrated)"
            elif 'Intel' in cpu_name and 'Graphics' in cpu_name:
                return "Intel Integrated Graphics"

        # Try AMD/other GPUs via lspci
        try:
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=2)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'VGA compatible controller' in line or 'Display controller' in line:
                        parts = line.split(': ', 1)
                        if len(parts) > 1:
                            return parts[1].strip()
        except:
            pass
    except:
        pass

    return gpu_info


def _check_visitor_pool_status(request, status_data):
    """Check visitor pool status and allocations."""
    try:
        from apps.project_app.services.visitor_pool import VisitorPool
        from apps.project_app.models import VisitorAllocation

        pool_status = VisitorPool.get_pool_status()

        # Get current user's allocation if they have one
        user_allocation = None
        allocation_token = request.session.get(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN)
        if allocation_token:
            try:
                user_allocation = VisitorAllocation.objects.get(
                    allocation_token=allocation_token,
                    is_active=True,
                    expires_at__gt=timezone.now()
                )
            except VisitorAllocation.DoesNotExist:
                pass

        user_visitor_number = user_allocation.visitor_number if user_allocation else None

        # Get all allocations
        allocations = []
        for i in range(1, VisitorPool.POOL_SIZE + 1):
            allocation = VisitorAllocation.objects.filter(visitor_number=i).first()
            is_current_user = (user_visitor_number == i)

            if allocation and allocation.is_active and allocation.expires_at > timezone.now():
                # Active allocation
                time_remaining = allocation.expires_at - timezone.now()
                total_minutes = int(time_remaining.total_seconds() / 60)

                allocations.append({
                    "slot_number": i,
                    "status": "allocated",
                    "expires_at": allocation.expires_at,
                    "minutes_remaining": total_minutes,
                    "visitor_username": f"visitor-{allocation.visitor_number:03d}",
                    "is_current_user": is_current_user,
                })
            else:
                # Free slot
                allocations.append({
                    "slot_number": i,
                    "status": "free",
                    "expires_at": None,
                    "minutes_remaining": None,
                    "visitor_username": None,
                    "is_current_user": False,
                })

        status_data["visitor_pool"] = {
            "pool_status": pool_status,
            "allocations": allocations,
            "session_lifetime_hours": VisitorPool.SESSION_LIFETIME_HOURS,
        }
    except Exception as e:
        logger.warning(f"Could not get visitor pool status: {e}")
        status_data["visitor_pool"] = {"error": str(e)}


def server_status_api(request):
    """API endpoint for real-time server metrics (returns JSON)"""
    try:
        data = {
            "timestamp": int(time.time() * 1000),  # milliseconds
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }

        # GPU metrics
        data["gpu_percent"] = _get_gpu_utilization()

        # Network I/O rates
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        data["net_sent_mb_total"] = round(net_io.bytes_sent / (1024**2), 2)
        data["net_recv_mb_total"] = round(net_io.bytes_recv / (1024**2), 2)
        data["disk_read_mb_total"] = round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0
        data["disk_write_mb_total"] = round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0

        # Visitor pool status
        try:
            from apps.project_app.services.visitor_pool import VisitorPool
            pool_status = VisitorPool.get_pool_status()
            data["visitor_pool_allocated"] = pool_status['allocated']
            data["visitor_pool_total"] = pool_status['total']
        except Exception as e:
            logger.debug(f"Could not get visitor pool status: {e}")
            data["visitor_pool_allocated"] = None
            data["visitor_pool_total"] = None

        # Active users count
        try:
            from django.contrib.sessions.models import Session
            active_sessions = Session.objects.filter(expire_date__gte=timezone.now())
            user_ids = set()
            for session in active_sessions:
                session_data = session.get_decoded()
                user_id = session_data.get('_auth_user_id')
                if user_id:
                    user_ids.add(user_id)
            data["active_users_count"] = len(user_ids)
        except Exception as e:
            logger.debug(f"Could not get active users count: {e}")
            data["active_users_count"] = None

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def _get_gpu_utilization():
    """Get GPU utilization percentage."""
    gpu_percent = None
    try:
        # Try NVIDIA nvidia-smi
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_percent = float(result.stdout.strip().split('\n')[0])
        except:
            pass

        # Try AMD rocm-smi
        if gpu_percent is None:
            try:
                result = subprocess.run(
                    ['rocm-smi', '--showuse'],
                    capture_output=True, text=True, timeout=2
                )
                if result.returncode == 0 and result.stdout:
                    import re
                    for line in result.stdout.split('\n'):
                        if 'GPU use' in line or '%' in line:
                            match = re.search(r'(\d+(?:\.\d+)?)\s*%', line)
                            if match:
                                gpu_percent = float(match.group(1))
                                break
            except:
                pass
    except:
        pass

    return gpu_percent


def server_metrics_history_api(request):
    """API endpoint for historical server metrics (returns JSON)"""
    from ..models import ServerMetrics

    try:
        # Get query parameters
        hours = int(request.GET.get('hours', 24))  # Default: last 24 hours
        limit = int(request.GET.get('limit', 1000))  # Max records to return

        # Query metrics
        start_time = timezone.now() - timedelta(hours=hours)
        metrics = ServerMetrics.objects.filter(
            timestamp__gte=start_time
        ).order_by('timestamp')[:limit]

        # Format data
        data = {
            "count": metrics.count(),
            "start_time": start_time.isoformat(),
            "end_time": timezone.now().isoformat(),
            "metrics": [
                {
                    "timestamp": int(m.timestamp.timestamp() * 1000),
                    "cpu_percent": m.cpu_percent,
                    "memory_percent": m.memory_percent,
                    "disk_percent": m.disk_percent,
                    "memory_used_gb": m.memory_used_gb,
                    "disk_used_gb": m.disk_used_gb,
                    "net_sent_mb": m.net_sent_mb,
                    "net_recv_mb": m.net_recv_mb,
                    "disk_read_mb": m.disk_read_mb,
                    "disk_write_mb": m.disk_write_mb,
                    "visitor_pool_allocated": m.visitor_pool_allocated,
                    "visitor_pool_total": m.visitor_pool_total,
                    "active_users_count": m.active_users_count,
                    "gpu_percent": m.gpu_percent if hasattr(m, 'gpu_percent') else None,
                }
                for m in metrics
            ]
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def server_metrics_export_csv(request):
    """Export server metrics as CSV file"""
    from ..models import ServerMetrics

    try:
        # Get query parameters
        hours = int(request.GET.get('hours', 24))
        start_time = timezone.now() - timedelta(hours=hours)

        # Query metrics
        metrics = ServerMetrics.objects.filter(
            timestamp__gte=start_time
        ).order_by('timestamp')

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = f'attachment; filename="server_metrics_{timezone.now().strftime("%Y%m%d_%H%M%S")}.csv"'

        writer = csv.writer(response)

        # Write header
        writer.writerow([
            'Timestamp',
            'CPU %',
            'CPU Cores',
            'CPU Cores Logical',
            'Memory %',
            'Memory Used (TB)',
            'Memory Total (TB)',
            'Memory Available (TB)',
            'Disk %',
            'Disk Used (TB)',
            'Disk Total (TB)',
            'Disk Read (MB)',
            'Disk Write (MB)',
            'Network Sent (MB)',
            'Network Received (MB)',
            'Docker Services',
            'SSH Gateway',
            'Gitea SSH',
            'Database',
            'Redis',
        ])

        # Write data
        for m in metrics:
            writer.writerow([
                m.timestamp.isoformat(),
                m.cpu_percent,
                m.cpu_cores,
                m.cpu_cores_logical,
                m.memory_percent,
                round(m.memory_used_gb / 1024, 3) if m.memory_used_gb else None,
                round(m.memory_total_gb / 1024, 3) if m.memory_total_gb else None,
                round(m.memory_available_gb / 1024, 3) if m.memory_available_gb else None,
                m.disk_percent,
                round(m.disk_used_gb / 1024, 2) if m.disk_used_gb else None,
                round(m.disk_total_gb / 1024, 2) if m.disk_total_gb else None,
                m.disk_read_mb,
                m.disk_write_mb,
                m.net_sent_mb,
                m.net_recv_mb,
                m.docker_services_running,
                m.ssh_gateway_status,
                m.gitea_ssh_status,
                m.database_status,
                m.redis_status,
            ])

        return response
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def visitor_status(request):
    """
    Redirect to server_status page.

    This view is deprecated. All visitor status information is now
    integrated into the server status page at /server-status/
    """
    return redirect('public_app:server_status', permanent=True)


def visitor_restart_session(request):
    """
    Restart visitor session - logs out current expired visitor and redirects to landing.

    This allows expired visitors to get a new 60-minute session.
    VisitorAutoLoginMiddleware will allocate them a new visitor slot on the landing page.
    """
    from django.contrib.auth import logout
    from apps.project_app.services.visitor_pool import VisitorPool

    # Clear visitor allocation from session
    request.session.pop(VisitorPool.SESSION_KEY_PROJECT_ID, None)
    request.session.pop(VisitorPool.SESSION_KEY_VISITOR_ID, None)
    request.session.pop(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN, None)

    # Log out the current visitor user
    logout(request)

    # Redirect to landing page where VisitorAutoLoginMiddleware will allocate a new slot
    return redirect('public_app:index')


def visitor_expired(request):
    """
    Visitor session expiration page.

    Shown when a visitor's 60-minute session expires.
    Provides clear explanation and options to sign up or start a new session.
    """
    from apps.project_app.services.visitor_pool import VisitorPool
    from apps.project_app.models import VisitorAllocation

    # Try to get visitor allocation info from session or database
    visitor_number = None
    expired_at = None
    expired_minutes_ago = None

    # Check session for visitor allocation token
    allocation_token = request.session.get(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN)
    if allocation_token:
        try:
            allocation = VisitorAllocation.objects.get(
                allocation_token=allocation_token
            )
            visitor_number = allocation.visitor_number
            expired_at = allocation.expires_at

            # Calculate how long ago it expired
            if expired_at:
                time_diff = timezone.now() - expired_at
                expired_minutes_ago = max(1, int(time_diff.total_seconds() / 60))
        except VisitorAllocation.DoesNotExist:
            pass

    # If no allocation found in session, check if user is logged in as visitor
    if not visitor_number and request.user.is_authenticated:
        username = request.user.username
        if username.startswith('visitor-'):
            try:
                # Extract visitor number from username (visitor-001 -> 1)
                visitor_number = int(username.replace('visitor-', ''))
            except (ValueError, AttributeError):
                pass

    context = {
        'visitor_number': visitor_number,
        'expired_at': expired_at,
        'expired_minutes_ago': expired_minutes_ago or 1,  # Default to 1 if unknown
    }

    return render(request, 'public_app/visitor_expired.html', context)


# EOF
