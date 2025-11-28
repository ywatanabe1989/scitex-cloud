#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-28 21:31:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views/status/helpers.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views/status/helpers.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Status View Helper Functions

Utility functions for checking system resources and services.
"""

import logging
import subprocess

import psutil
from django.utils import timezone

logger = logging.getLogger("scitex")


def check_slurm_status(status_data):
    """Check SLURM cluster status."""
    try:
        # Use sinfo to check if SLURM is responding
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


def check_container_runtime_status(status_data):
    """Check Apptainer/Singularity container runtime status."""
    try:
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


def check_system_resources(status_data):
    """Check system resource usage."""
    try:
        cpu_count = psutil.cpu_count(logical=False) or psutil.cpu_count()
        cpu_count_logical = psutil.cpu_count(logical=True)

        cpu_name = get_cpu_name()
        gpu_info = get_gpu_info(cpu_name)

        disk_io = psutil.disk_io_counters()
        disk_read_mb = round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0
        disk_write_mb = round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0

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


def get_cpu_name():
    """Get CPU name from /proc/cpuinfo (Linux)."""
    cpu_name = "Unknown"
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'model name' in line:
                    cpu_name = line.split(':')[1].strip()
                    break
    except:
        pass
    return cpu_name


def get_gpu_info(cpu_name):
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


def get_gpu_utilization():
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


def check_visitor_pool_status(request, status_data):
    """Check visitor pool status and allocations."""
    try:
        from apps.project_app.services.visitor_pool import VisitorPool
        from apps.project_app.models import VisitorAllocation

        pool_status = VisitorPool.get_pool_status()

        # Get current user's allocation
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


# EOF
