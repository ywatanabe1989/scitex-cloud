#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-29 07:00:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views/status/compute_resources.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views/status/compute_resources.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Compute Resources Status

SLURM cluster and Apptainer/Singularity container runtime checks.
"""

import logging
import subprocess

logger = logging.getLogger("scitex")


def check_slurm_status(status_data):
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


def check_container_runtime_status(status_data):
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


# EOF
