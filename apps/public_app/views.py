#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-06 00:52:20 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import logging
import time

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
from django.http import JsonResponse
from django.shortcuts import redirect
from django.shortcuts import render
from django.utils import timezone

logger = logging.getLogger("scitex")


def index(request):
    """
    Cloud app index view - Landing page for all users.

    Shows the landing page to all visitors, including authenticated users.
    This allows the logo to always return to the landing page.
    """
    # Auto-allocate visitor slot if user is a visitor without an allocation
    if request.user.is_authenticated and request.user.username.startswith("visitor-"):
        from apps.project_app.services.visitor_pool import VisitorPool

        # Check if visitor has an active allocation
        allocation_token = request.session.get(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN)
        if not allocation_token:
            # No allocation - allocate one now
            project, user = VisitorPool.allocate_visitor(request.session)
            logger.info(f"[Landing] Auto-allocated visitor slot for {request.user.username}")

    # Show landing page to all users (removed auto-redirect for logged-in users)
    # Users can navigate to their profile via the header navigation

    # Features are now in HTML partials at:
    # apps/public_app/templates/public_app/landing_partials/features/

    return render(request, "public_app/landing.html")


def premium_subscription(request):
    """Premium subscription and pricing details view."""

    # Define the comprehensive pricing structure based on the premium strategy
    individual_plans = [
        {
            "name": "Free",
            "price": 0,
            "gpu_hours": "5/month",
            "literature_searches": "50/month",
            "figure_generation": "25/month",
            "storage": "500MB",
            "scientific_validation": "Basic methodology checks",
            "agent_prompts": "Basic templates",
            "collaboration": "None",
            "language_support": "English",
            "support_level": "Community",
            "key_features": [
                "Basic LaTeX compilation",
                "Git integration",
                "Methodology validation",
                "File organization & project structure",
                "Simple data visualization",
            ],
            "cta_text": "Get Started Free",
            "cta_url": "/signup/",
            "popular": False,
        },
        {
            "name": "Standard",
            "price": 29,
            "gpu_hours": "50/month",
            "literature_searches": "500/month",
            "figure_generation": "200/month",
            "storage": "5GB",
            "scientific_validation": "Statistical rigor checking",
            "agent_prompts": "Standard library",
            "collaboration": "Basic sharing",
            "language_support": "English",
            "support_level": "Email",
            "key_features": [
                "AI literature reviews",
                "Grant templates (NSF/NIH)",
                "Peer review basics",
                "Advanced bibliography management",
                "Statistical validation tools",
            ],
            "cta_text": "Start Free Trial",
            "cta_url": "/signup/?plan=standard",
            "popular": False,
        },
        {
            "name": "Professional",
            "price": 99,
            "gpu_hours": "200/month",
            "literature_searches": "Unlimited",
            "figure_generation": "1000/month",
            "storage": "25GB",
            "scientific_validation": "Advanced validation",
            "agent_prompts": "Full library",
            "collaboration": "Project workspaces",
            "language_support": "English + Japanese",
            "support_level": "Priority",
            "key_features": [
                "Full scientific writing suite",
                "SigmaPlot integration",
                "Agent orchestration",
                "JST/MEXT grant optimization",
                "Advanced statistical analysis",
            ],
            "cta_text": "Start Free Trial",
            "cta_url": "/signup/?plan=professional",
            "popular": True,
        },
        {
            "name": "Researcher Plus",
            "price": 199,
            "gpu_hours": "500/month",
            "literature_searches": "Unlimited",
            "figure_generation": "Unlimited",
            "storage": "100GB",
            "scientific_validation": "Expert validation",
            "agent_prompts": "Custom prompts",
            "collaboration": "Advanced collaboration",
            "language_support": "English + Japanese",
            "support_level": "Dedicated + Monthly consult",
            "key_features": [
                "Co-authorship validation",
                "Grant optimization",
                "Peer review assistant",
                "Expert consultation included",
                "Custom prompt development",
            ],
            "cta_text": "Contact Sales",
            "cta_url": "/contact/",
            "popular": False,
        },
    ]

    institutional_plans = [
        {
            "name": "Lab License",
            "price": 299,
            "users": "5-10 users",
            "gpu_hours": "1000 shared",
            "storage": "500GB",
            "features": [
                "Admin dashboard",
                "Quarterly training",
                "Role-based permissions",
                "Advanced validation",
                "Priority support",
            ],
        },
        {
            "name": "Department",
            "price": 999,
            "users": "25-50 users",
            "gpu_hours": "3000 shared",
            "storage": "2TB",
            "features": [
                "Custom prompts",
                "Monthly training",
                "Enterprise collaboration",
                "Expert validation",
                "Dedicated support",
            ],
        },
        {
            "name": "University Enterprise",
            "price": "Custom",
            "users": "Unlimited",
            "gpu_hours": "Unlimited",
            "storage": "Unlimited",
            "features": [
                "On-premise deployment",
                "Unlimited users",
                "Dedicated support manager",
                "Co-authorship eligible",
                "Fully customized",
            ],
        },
    ]

    japanese_specials = [
        {
            "name": "Pilot Program",
            "price": "Free (6 months)",
            "description": "Professional tier features for up to 10 researchers",
            "features": [
                "Success tracking",
                "Japanese language focus",
                "Priority support",
                "Full library access",
            ],
        },
        {
            "name": "MEXT Partnership",
            "price": "50% off all plans",
            "description": "For government-funded research institutions",
            "features": [
                "Compliance certification",
                "Custom JST/MEXT templates",
                "Enterprise collaboration",
                "Dedicated support",
            ],
        },
    ]

    add_on_services = [
        {
            "name": "Custom Prompt Development",
            "price": "$2,000/project",
            "description": "Tailored AI prompts for specific research domains",
            "available_for": "Professional+",
        },
        {
            "name": "On-Premise Setup",
            "price": "$10,000 + $2,000/month",
            "description": "Local deployment with maintenance",
            "available_for": "Enterprise only",
        },
        {
            "name": "Training Workshop",
            "price": "$5,000/session",
            "description": "Emacs + SciTeX training for teams",
            "available_for": "All institutional",
        },
        {
            "name": "Scientific Validation Consultation",
            "price": "$200/hour",
            "description": "Expert consultation on research quality",
            "available_for": "Standard+",
        },
        {
            "name": "Co-authorship Review",
            "price": "$500/paper",
            "description": "Publication-ready validation with co-author eligibility",
            "available_for": "Professional+",
        },
    ]

    context = {
        "individual_plans": individual_plans,
        "institutional_plans": institutional_plans,
        "japanese_specials": japanese_specials,
        "add_on_services": add_on_services,
    }

    return render(request, "public_app/premium_subscription.html", context)


def about(request):
    """SciTeX about page - purpose, mission, vision, and values."""
    return render(request, "public_app/pages/about.html")


# def vision(request):
#     """SciTeX vision and values page."""
#     return render(request, "public_app/pages/vision.html")


def publications(request):
    """Publications page."""
    return render(request, "public_app/pages/publications.html")


def donate(request):
    """Donate page view with payment processing."""

    from django.contrib import messages

    from .forms import DonationForm, EmailVerificationForm
    from .models import Donation, DonationTier

    # Get donation tiers
    tiers = (
        DonationTier.objects.filter(is_active=True)
        if DonationTier.objects.exists()
        else []
    )

    if request.method == "POST":
        # Check if this is email verification request
        if "verify_email" in request.POST:
            email_form = EmailVerificationForm(request.POST)
            if email_form.is_valid():
                if email_form.send_verification_email():
                    messages.success(request, "Verification code sent to your email!")
                    request.session["verification_email"] = email_form.cleaned_data[
                        "email"
                    ]
                    return redirect("cloud_app:verify-email")
                else:
                    messages.error(
                        request,
                        "Failed to send verification email. Please try again.",
                    )

        # Process donation
        elif "process_donation" in request.POST:
            form = DonationForm(request.POST)
            if form.is_valid():
                donation = form.save(commit=False)

                # If user is authenticated, link to user
                if request.user.is_authenticated:
                    donation.user = request.user

                # Save donation as pending
                donation.save()

                # Here you would integrate with payment processor
                # For now, we'll simulate successful payment
                if donation.payment_method == "credit_card":
                    # Simulate Stripe payment
                    transaction_id = f"STRIPE_{donation.id}_{timezone.now().strftime('%Y%m%d%H%M%S')}"
                    donation.complete_donation(transaction_id)
                    messages.success(
                        request,
                        f"Thank you for your ${donation.amount} donation!",
                    )

                    # Send confirmation email
                    send_donation_confirmation(donation)

                    return redirect(
                        "cloud_app:donation-success", donation_id=donation.id
                    )

                elif donation.payment_method == "paypal":
                    # Redirect to PayPal
                    messages.info(request, "Redirecting to PayPal...")
                    return redirect(
                        "cloud_app:donate"
                    )  # Would redirect to PayPal in production

                elif donation.payment_method == "github":
                    # Redirect to GitHub Sponsors
                    return redirect("https://github.com/sponsors/SciTex-AI")

    else:
        form = DonationForm()

    # Get recent public donations
    recent_donations = (
        Donation.objects.filter(
            is_public=True, is_anonymous=False, status="completed"
        ).select_related("user")[:10]
        if Donation.objects.exists()
        else []
    )

    # Calculate funding progress
    current_year = timezone.now().year
    year_donations = (
        Donation.objects.filter(
            status="completed", created_at__year=current_year
        ).aggregate(total=models.Sum("amount"))["total"]
        or 0
        if Donation.objects.exists()
        else 0
    )

    funding_goal = 75000  # $75,000 annual goal
    funding_percentage = min(100, int((year_donations / funding_goal) * 100))

    context = {
        "form": form,
        "tiers": tiers,
        "recent_donations": recent_donations,
        "year_donations": year_donations,
        "funding_goal": funding_goal,
        "funding_percentage": funding_percentage,
    }

    return render(request, "public_app/pages/donate.html", context)


def fundraising(request):
    """Fundraising and sustainability page."""
    return render(request, "public_app/pages/fundraising.html")


# ---------------------------------------
# Legal
# ---------------------------------------
def contact(request):
    """Contact page."""
    return render(request, "public_app/legal/contact.html")


def privacy_policy(request):
    """Privacy policy page."""
    return render(request, "public_app/legal/privacy_policy.html")


def terms_of_use(request):
    """Terms of use page."""
    return render(request, "public_app/legal/terms_of_use.html")


def cookie_policy(request):
    """Cookie policy page."""
    return render(request, "public_app/legal/cookie_policy.html")


# def signup(request):
#     """Signup page with user registration."""
#     from django.contrib.auth import login
#     from django.contrib.auth.models import User

#     from .forms import SignupForm

#     if request.method == "POST":
#         form = SignupForm(request.POST)
#         if form.is_valid():
#             # Create new user
#             user = User.objects.create_user(
#                 username=form.cleaned_data["username"],
#                 email=form.cleaned_data["email"],
#                 password=form.cleaned_data["password"],
#             )

#             # Create user profile
#             from apps.auth_app.models import UserProfile

#             UserProfile.objects.create(user=user)

#             # Log the user in
#             login(request, user)

#             messages.success(
#                 request,
#                 "Welcome to SciTeX! Your account has been created successfully.",
#             )
#             return redirect("project_app:list")
#     else:
#         form = SignupForm()

#     context = {
#         "form": form,
#     }
#     return render(request, "public_app/signup.html", context)


# def login_view(request):
#     """Login page with authentication."""
#     from django.contrib.auth import authenticate, login
#     from django.contrib.auth.models import User

#     from .forms import LoginForm

#     if request.method == "POST":
#         form = LoginForm(request.POST)
#         if form.is_valid():
#             username = form.cleaned_data["username"]
#             password = form.cleaned_data["password"]

#             # Check if username is actually an email
#             if "@" in username:
#                 try:
#                     user_obj = User.objects.get(email=username)
#                     username = user_obj.username
#                 except User.DoesNotExist:
#                     pass

#             # Authenticate user
#             user = authenticate(request, username=username, password=password)

#             if user is not None:
#                 login(request, user)

#                 # Handle remember me
#                 if not form.cleaned_data.get("remember_me"):
#                     request.session.set_expiry(0)

#                 # Redirect to next page or projects
#                 next_page = request.GET.get(
#                     "next", settings.LOGIN_REDIRECT_URL
#                 )
#                 messages.success(request, f"Welcome back, {user.username}!")
#                 return redirect(next_page)
#             else:
#                 messages.error(request, "Invalid username or password.")
#     else:
#         form = LoginForm()

#     context = {
#         "form": form,
#     }
#     return render(request, "public_app/signin.html", context)


# def forgot_password(request):
#     """Forgot password page."""
#     return render(request, "public_app/forgot_password.html")


# def reset_password(request, uidb64, token):
#     """Password reset confirmation page."""
#     from django.contrib.auth.models import User
#     from django.contrib.auth.tokens import default_token_generator
#     from django.utils.encoding import force_str
#     from django.utils.http import urlsafe_base64_decode

#     context = {
#         "uidb64": uidb64,
#         "token": token,
#         "valid_link": False,
#         "user": None,
#     }

#     try:
#         # Decode user ID
#         uid = force_str(urlsafe_base64_decode(uidb64))
#         user = User.objects.get(pk=uid)

#         # Validate token
#         if default_token_generator.check_token(user, token):
#             context["valid_link"] = True
#             context["user"] = user

#     except (TypeError, ValueError, OverflowError, User.DoesNotExist):
#         pass

#     return render(request, "public_app/reset_password.html", context)


# def logout_view(request):
#     """Logout page."""
#     from django.contrib.auth import logout

#     logout(request)
#     return render(request, "public_app/logout.html")


# def verify_email(request):
#     """Email verification page for account signup."""
#     # This page is for OTP email verification during account signup
#     # The actual verification is handled by the JavaScript frontend
#     # which calls the API endpoints in apps.api.v1.auth.views
#     return render(request, "public_app/email_verification.html")


def donation_success(request, donation_id):
    """Donation success page."""
    from .models import Donation

    try:
        donation = Donation.objects.get(id=donation_id)
        if (
            donation.donor_email != request.session.get("verified_email")
            and not request.user.is_authenticated
        ):
            raise PermissionDenied
    except Donation.DoesNotExist:
        messages.error(request, "Donation not found.")
        return redirect("cloud_app:donate")

    context = {
        "donation": donation,
    }

    return render(request, "public_app/donation_success.html", context)


def send_donation_confirmation(donation):
    """Send donation confirmation email."""
    from django.core.mail import send_mail

    subject = "Thank you for supporting SciTeX!"

    message = f"""
Dear {donation.donor_name},

Thank you for your generous ${donation.amount} donation to SciTeX!

Your support helps us maintain and improve our open-source scientific research platform,
making advanced tools accessible to researchers worldwide.

Transaction Details:
- Amount: ${donation.amount} USD
- Payment Method: {donation.get_payment_method_display()}
- Transaction ID: {donation.transaction_id}
- Date: {donation.completed_at.strftime("%B %d, %Y")}

This email serves as your donation receipt for tax purposes.

If you have any questions, please contact us at support@scitex.ai.

With gratitude,
The SciTeX Team
"""

    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [donation.donor_email],
            fail_silently=False,
        )
    except Exception as e:
        logger.error(f"Failed to send donation confirmation: {str(e)}")


def api_docs(request):
    """Display the API documentation page."""
    return render(request, "public_app/pages/api_docs.html")


def releases_view(request):
    """Release Notes page showing comprehensive development history."""
    return render(request, "public_app/release_note.html")


# Missing view functions - added during cleanup to fix URL import errors
def demo(request):
    """Demo page."""
    return render(request, "public_app/demo.html")


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

    status_data = {
        "services": [],
        "ssh_services": [],
        "database": {},
        "redis": {},
        "disk": {},
        "system": {},
    }

    # Check Docker containers
    try:
        import docker
        client = docker.from_env()
        containers = client.containers.list(all=True, filters={"name": "scitex-cloud-dev"})

        for container in containers:
            status_data["services"].append({
                "name": container.name.replace("scitex-cloud-dev-", "").replace("-1", ""),
                "status": container.status,
                "is_running": container.status == "running",
                "image": container.image.tags[0] if container.image.tags else "unknown",
            })
    except Exception as e:
        logger.warning(f"Could not check Docker containers: {e}")
        status_data["services"].append({
            "name": "Docker",
            "status": "unavailable",
            "is_running": False,
            "error": str(e),
        })

    # Check SSH services
    # Workspace SSH Gateway (port 2200)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 2200))
        sock.close()
        status_data["ssh_services"].append({
            "name": "Workspace SSH Gateway",
            "port": 2200,
            "is_running": result == 0,
            "status": "running" if result == 0 else "down",
        })
    except Exception as e:
        status_data["ssh_services"].append({
            "name": "Workspace SSH Gateway",
            "port": 2200,
            "is_running": False,
            "status": "error",
            "error": str(e),
        })

    # Gitea SSH (port 2222)
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(1)
        result = sock.connect_ex(('127.0.0.1', 2222))
        sock.close()
        status_data["ssh_services"].append({
            "name": "Gitea SSH (Git operations)",
            "port": 2222,
            "is_running": result == 0,
            "status": "running" if result == 0 else "down",
        })
    except Exception as e:
        status_data["ssh_services"].append({
            "name": "Gitea SSH",
            "port": 2222,
            "is_running": False,
            "status": "error",
            "error": str(e),
        })

    # Check database
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            status_data["database"] = {
                "is_running": True,
                "status": "connected",
                "backend": connection.settings_dict['ENGINE'].split('.')[-1],
                "name": connection.settings_dict['NAME'],
            }
    except Exception as e:
        status_data["database"] = {
            "is_running": False,
            "status": "error",
            "error": str(e),
        }

    # Check Redis
    try:
        cache.set('health_check', 'ok', 10)
        test_value = cache.get('health_check')
        status_data["redis"] = {
            "is_running": test_value == 'ok',
            "status": "connected" if test_value == 'ok' else "error",
        }
    except Exception as e:
        status_data["redis"] = {
            "is_running": False,
            "status": "error",
            "error": str(e),
        }

    # Check disk usage
    try:
        disk = psutil.disk_usage('/')
        status_data["disk"] = {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": disk.percent,
            "is_healthy": disk.percent < 90,
        }
    except Exception as e:
        status_data["disk"] = {
            "is_healthy": False,
            "error": str(e),
        }

    # System resources
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

        # GPU information (check for NVIDIA)
        gpu_info = "None available"
        try:
            import subprocess
            result = subprocess.run(['nvidia-smi', '--query-gpu=name', '--format=csv,noheader'],
                                  capture_output=True, text=True, timeout=2)
            if result.returncode == 0 and result.stdout.strip():
                gpu_info = result.stdout.strip()
        except:
            pass

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
            "memory_available_gb": round(psutil.virtual_memory().available / (1024**3), 2),
            "memory_total_gb": round(psutil.virtual_memory().total / (1024**3), 2),
            "gpu_info": gpu_info,
            "disk_read_mb": disk_read_mb,
            "disk_write_mb": disk_write_mb,
            "net_sent_mb": net_sent_mb,
            "net_recv_mb": net_recv_mb,
        }
    except Exception as e:
        status_data["system"] = {"error": str(e)}

    context = {
        "status_data": status_data,
    }

    return render(request, "public_app/server_status.html", context)


def server_status_api(request):
    """API endpoint for real-time server metrics (returns JSON)"""
    import psutil
    import subprocess

    try:
        data = {
            "timestamp": int(time.time() * 1000),  # milliseconds
            "cpu_percent": psutil.cpu_percent(interval=0.1),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
        }

        # GPU metrics (try nvidia-smi)
        gpu_percent = None
        try:
            result = subprocess.run(
                ['nvidia-smi', '--query-gpu=utilization.gpu', '--format=csv,noheader,nounits'],
                capture_output=True, text=True, timeout=2
            )
            if result.returncode == 0 and result.stdout.strip():
                gpu_percent = float(result.stdout.strip().split('\n')[0])
        except:
            pass
        data["gpu_percent"] = gpu_percent

        # Network I/O rates (bytes per second since last call)
        net_io = psutil.net_io_counters()
        disk_io = psutil.disk_io_counters()

        data["net_sent_mb_total"] = round(net_io.bytes_sent / (1024**2), 2)
        data["net_recv_mb_total"] = round(net_io.bytes_recv / (1024**2), 2)
        data["disk_read_mb_total"] = round(disk_io.read_bytes / (1024**2), 2) if disk_io else 0
        data["disk_write_mb_total"] = round(disk_io.write_bytes / (1024**2), 2) if disk_io else 0

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def server_metrics_history_api(request):
    """API endpoint for historical server metrics (returns JSON)"""
    from apps.public_app.models import ServerMetrics
    from datetime import timedelta

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
                }
                for m in metrics
            ]
        }

        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


def server_metrics_export_csv(request):
    """Export server metrics as CSV file"""
    from apps.public_app.models import ServerMetrics
    from datetime import timedelta
    from django.http import HttpResponse
    import csv

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
            'Memory Used (GB)',
            'Memory Total (GB)',
            'Memory Available (GB)',
            'Disk %',
            'Disk Used (GB)',
            'Disk Total (GB)',
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
                m.memory_used_gb,
                m.memory_total_gb,
                m.memory_available_gb,
                m.disk_percent,
                m.disk_used_gb,
                m.disk_total_gb,
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
    Visitor Mode Status Page.

    Shows visitor pool status without exposing privacy information.
    Displays:
    - Total slots available
    - Currently allocated slots
    - Free slots
    - User's personal countdown timer (if in visitor mode)
    - Allocation expiration times (without identifying information)
    """
    from apps.project_app.services.visitor_pool import VisitorPool
    from apps.project_app.models import VisitorAllocation
    from django.utils import timezone
    from datetime import datetime, time as dt_time

    # Check if current user has a visitor allocation, allocate if they don't
    user_allocation = None
    user_time_until_reset = None

    # Check for authenticated visitors without allocations
    if request.user.is_authenticated and request.user.username.startswith("visitor-"):
        allocation_token = request.session.get(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN)
        if allocation_token:
            try:
                user_allocation = VisitorAllocation.objects.get(
                    allocation_token=allocation_token,
                    is_active=True,
                    expires_at__gt=timezone.now()
                )
            except VisitorAllocation.DoesNotExist:
                allocation_token = None

        # If no valid allocation, allocate one now
        if not allocation_token:
            project, user = VisitorPool.allocate_visitor(request.session)
            logger.info(f"[VisitorStatus] Re-allocated visitor slot for {request.user.username}")

            # Get the new allocation
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

    elif not request.user.is_authenticated:
        # Check for existing allocation token
        allocation_token = request.session.get(VisitorPool.SESSION_KEY_ALLOCATION_TOKEN)
        if allocation_token:
            try:
                user_allocation = VisitorAllocation.objects.get(
                    allocation_token=allocation_token,
                    is_active=True,
                    expires_at__gt=timezone.now()
                )
            except VisitorAllocation.DoesNotExist:
                allocation_token = None

        # If no valid allocation, allocate one now
        if not allocation_token:
            from django.contrib.auth import login
            project, user = VisitorPool.allocate_visitor(request.session)
            if user:  # Successfully allocated
                # Log in the visitor user to make them authenticated
                if not request.user.is_authenticated:
                    login(request, user, backend='django.contrib.auth.backends.ModelBackend')
                    logger.info(f"[VisitorStatus] Logged in visitor: {user.username}")

                # Get the new allocation
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

        # Calculate time until session expires if we have an allocation
        if user_allocation:
            now = timezone.now()
            time_until_expiry = user_allocation.expires_at - now
            user_time_until_reset = {
                "hours": int(time_until_expiry.total_seconds() / 3600),
                "minutes": int((time_until_expiry.total_seconds() % 3600) / 60),
                "seconds": int(time_until_expiry.total_seconds() % 60),
                "total_seconds": int(time_until_expiry.total_seconds()),
                "reset_time": user_allocation.expires_at,
            }

    # Get pool status
    status = VisitorPool.get_pool_status()

    # Get allocation information (anonymized)
    allocations = []
    user_visitor_number = user_allocation.visitor_number if user_allocation else None

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

    context = {
        "pool_status": status,
        "allocations": allocations,
        "session_lifetime_hours": VisitorPool.SESSION_LIFETIME_HOURS,
        "user_allocation": user_allocation,
        "user_time_until_reset": user_time_until_reset,
    }

    return render(request, "public_app/visitor_status.html", context)


def contributors(request):
    """Contributors page - show SciTeX team and contributors."""
    from .models import Contributor

    # Get core team members from database
    core_team_db = Contributor.objects.filter(is_core_team=True)

    # Get community contributors from database
    contributors_db = Contributor.objects.filter(is_core_team=False)

    # Convert to template-friendly format
    core_team = []
    for member in core_team_db:
        core_team.append(
            {
                "name": member.name,
                "username": member.github_username,
                "role": member.get_role_display(),
                "avatar_url": member.avatar_url,
                "github_url": member.github_url,
                "contributions": member.contributions_description
                or f"{member.contributions} contributions",
            }
        )

    contributors = []
    for contributor in contributors_db:
        contributors.append(
            {
                "name": contributor.name,
                "username": contributor.github_username,
                "role": (
                    contributor.get_role_display()
                    if contributor.role != "contributor"
                    else None
                ),
                "avatar_url": contributor.avatar_url,
                "github_url": contributor.github_url,
                "contributions": contributor.contributions_description
                or f"{contributor.contributions} contributions",
            }
        )

    context = {
        "core_team": core_team,
        "contributors": contributors,
    }

    return render(request, "public_app/pages/contributors.html", context)


@login_required
def scitex_api_keys(request):
    """
    SciTeX API Key Management Page

    Allows users to create, view, and manage their SciTeX API keys
    for programmatic access to Scholar, Code, Viz, and Writer services.
    """
    from apps.accounts_app.models import APIKey
    from django.contrib import messages

    # Handle POST requests (create new API key)
    if request.method == "POST":
        action = request.POST.get("action")

        if action == "create":
            name = request.POST.get("name", "").strip()
            if not name:
                messages.error(request, "Please provide a name for your API key")
                return redirect("public_app:scitex_api_keys")

            # Create new API key
            api_key, full_key = APIKey.create_key(
                user=request.user,
                name=name,
                scopes=["scholar:read", "scholar:write"],  # Default scopes
            )

            # Store the full key in session to show once
            request.session["new_api_key"] = full_key
            messages.success(request, f'API key "{name}" created successfully!')
            return redirect("public_app:scitex_api_keys")

        elif action == "delete":
            key_id = request.POST.get("key_id")
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                key_name = api_key.name
                api_key.delete()
                messages.success(request, f'API key "{key_name}" deleted')
            except APIKey.DoesNotExist:
                messages.error(request, "API key not found")
            return redirect("public_app:scitex_api_keys")

        elif action == "toggle":
            key_id = request.POST.get("key_id")
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                api_key.is_active = not api_key.is_active
                api_key.save()
                status = "activated" if api_key.is_active else "deactivated"
                messages.success(request, f'API key "{api_key.name}" {status}')
            except APIKey.DoesNotExist:
                messages.error(request, "API key not found")
            return redirect("public_app:scitex_api_keys")

    # Get user's API keys
    api_keys = APIKey.objects.filter(user=request.user).order_by("-created_at")

    # Get newly created key from session (show once)
    new_api_key = request.session.pop("new_api_key", None)

    context = {
        "api_keys": api_keys,
        "new_api_key": new_api_key,
    }

    return render(request, "public_app/pages/api_keys.html", context)


def tools(request):
    """Research tools page - bookmarklets and utilities for researchers."""
    # Organized by tool type: Text → Image → PDF → Video → Rendering → Developer → Research
    domains = [
        {
            "name": "Text",
            "slug": "text",
            "icon": "📝",
            "description": "Format, compare, and process text content",
            "tools": [
                {
                    "name": "Markdown Renderer",
                    "description": "Real-time Markdown preview with syntax highlighting and table support.",
                    "use_case": "Format README files and documentation for data repositories",
                    "bookmarklet_url": "/tools/markdown-renderer/",
                    "icon": "📝",
                },
                {
                    "name": "Text Diff Checker",
                    "description": "Compare two text blocks side-by-side with highlighted differences.",
                    "use_case": "Compare dataset versions or track changes in results",
                    "bookmarklet_url": "/tools/text-diff-checker/",
                    "icon": "🔄",
                },
                {
                    "name": "JSON Formatter",
                    "description": "Format, validate, and beautify JSON data with syntax highlighting.",
                    "use_case": "Validate plot specifications and configuration files",
                    "bookmarklet_url": "/tools/json-formatter/",
                    "icon": "{ }",
                },
            ],
        },
        {
            "name": "Image",
            "slug": "image",
            "icon": "🖼️",
            "description": "Manipulate and convert images for publications",
            "tools": [
                {
                    "name": "Image & PDF Viewer",
                    "description": "View dimensions, DPI, and unit conversions (mm/inch) for publication figures.",
                    "use_case": "Verify Figure 2 meets journal dimension requirements",
                    "bookmarklet_url": "/tools/image-viewer/",
                    "icon": "📐",
                },
                {
                    "name": "Image Resizer",
                    "description": "Resize and crop images for journal submissions with preset dimensions.",
                    "use_case": "Adjust Figure 2 to exact pixel-perfect journal specs",
                    "bookmarklet_url": "/tools/image-resizer/",
                    "icon": "📏",
                },
                {
                    "name": "Image Converter",
                    "description": "Convert images between PNG, JPG, WEBP, TIFF formats with batch conversion.",
                    "use_case": "Convert PNG figures to TIFF for journal submission",
                    "bookmarklet_url": "/tools/image-converter/",
                    "icon": "🔄",
                },
                {
                    "name": "Image Concatenator",
                    "description": "Combine multiple images into a single tiled multi-panel figure.",
                    "use_case": "Create Figure 1 panel layouts (A, B, C, D)",
                    "bookmarklet_url": "/tools/image-concatenator/",
                    "icon": "🖼️",
                },
                {
                    "name": "Mermaid Diagram Renderer",
                    "description": "Create flowcharts, sequence diagrams, and concept diagrams from text syntax.",
                    "use_case": "Design experimental workflow diagrams for Methods section",
                    "bookmarklet_url": "/tools/mermaid-renderer/",
                    "icon": "🧜‍♀️",
                },
                {
                    "name": "Images to GIF",
                    "description": "Convert image sequences into animated GIF with customizable duration.",
                    "use_case": "Create supplementary animations showing temporal changes",
                    "bookmarklet_url": "/tools/images-to-gif/",
                    "icon": "🎬",
                },
                {
                    "name": "Images to PDF",
                    "description": "Convert multiple images into a single PDF with custom page orientation.",
                    "use_case": "Create supplementary figures PDF from multiple images",
                    "bookmarklet_url": "/tools/images-to-pdf/",
                    "icon": "📄",
                },
                {
                    "name": "PDF to Images",
                    "description": "Extract all pages from PDF as PNG or JPG images with adjustable DPI.",
                    "use_case": "Convert PDF figures to images for presentation slides",
                    "bookmarklet_url": "/tools/pdf-to-images/",
                    "icon": "🖼️",
                },
            ],
        },
        {
            "name": "PDF",
            "slug": "pdf",
            "icon": "📄",
            "description": "Manage and process PDF documents",
            "tools": [
                {
                    "name": "Image & PDF Viewer",
                    "description": "View dimensions, DPI, and unit conversions (mm/inch) for publication figures.",
                    "use_case": "Verify Figure 2 meets journal dimension requirements",
                    "bookmarklet_url": "/tools/image-viewer/",
                    "icon": "📐",
                },
                {
                    "name": "PDF Merger",
                    "description": "Combine multiple PDF files into a single document with drag-to-reorder.",
                    "use_case": "Merge manuscript, figures, and supplements for submission",
                    "bookmarklet_url": "/tools/pdf-merger/",
                    "icon": "📑",
                },
                {
                    "name": "PDF Compressor",
                    "description": "Reduce PDF file size while maintaining quality for email and uploads.",
                    "use_case": "Compress submission files under journal size limits",
                    "bookmarklet_url": "/tools/pdf-compressor/",
                    "icon": "🗜️",
                },
                {
                    "name": "PDF Splitter",
                    "description": "Extract specific pages from PDF files using page ranges.",
                    "use_case": "Extract figures from compiled manuscript for separate upload",
                    "bookmarklet_url": "/tools/pdf-splitter/",
                    "icon": "✂️",
                },
                {
                    "name": "Images to PDF",
                    "description": "Convert multiple images into a single PDF with custom page orientation.",
                    "use_case": "Create supplementary figures PDF from multiple images",
                    "bookmarklet_url": "/tools/images-to-pdf/",
                    "icon": "📄",
                },
                {
                    "name": "PDF to Images",
                    "description": "Extract all pages from PDF as PNG or JPG images with adjustable DPI.",
                    "use_case": "Convert PDF figures to images for presentation slides",
                    "bookmarklet_url": "/tools/pdf-to-images/",
                    "icon": "🖼️",
                },
            ],
        },
        {
            "name": "Video",
            "slug": "video",
            "icon": "🎬",
            "description": "Video and animation processing",
            "tools": [
                {
                    "name": "Video Editor",
                    "description": "Trim videos by time window with browser-based processing.",
                    "use_case": "Edit supplementary videos for journal submission",
                    "bookmarklet_url": "/tools/video-editor/",
                    "icon": "🎬",
                },
                {
                    "name": "Images to GIF",
                    "description": "Convert image sequences into animated GIF with customizable duration.",
                    "use_case": "Create supplementary animations showing temporal changes",
                    "bookmarklet_url": "/tools/images-to-gif/",
                    "icon": "🎬",
                },
            ],
        },
        {
            "name": "Rendering",
            "slug": "rendering",
            "icon": "📈",
            "description": "Create publication-quality plots and diagrams",
            "tools": [
                {
                    "name": "Plot Viewer",
                    "description": "Interactive CSV plot viewer with Nature journal standards. Supports line, scatter, and bar plots with 300 DPI rendering.",
                    "use_case": "Quick data visualization during analysis",
                    "bookmarklet_url": "/tools/plot-viewer/",
                    "icon": "📊",
                },
                {
                    "name": "Plot Backend Test",
                    "description": "Test matplotlib/scitex.plt backend with JSON specifications. Generate publication-quality SVG plots.",
                    "use_case": "Design figures with precise journal specifications",
                    "bookmarklet_url": "/tools/plot-backend-test/",
                    "icon": "🧪",
                },
                {
                    "name": "Mermaid Diagram Renderer",
                    "description": "Create flowcharts, sequence diagrams, and concept diagrams from text syntax.",
                    "use_case": "Design experimental workflow diagrams for Methods section",
                    "bookmarklet_url": "/tools/mermaid-renderer/",
                    "icon": "🧜‍♀️",
                },
                {
                    "name": "Markdown Renderer",
                    "description": "Real-time Markdown preview with syntax highlighting and table support.",
                    "use_case": "Format README files and documentation for data repositories",
                    "bookmarklet_url": "/tools/markdown-renderer/",
                    "icon": "📝",
                },
                {
                    "name": "Color Picker",
                    "description": "Advanced color picker with format conversion and palette generation.",
                    "use_case": "Design consistent color schemes for figure panels",
                    "bookmarklet_url": "/tools/color-picker/",
                    "icon": "🎨",
                },
            ],
        },
        {
            "name": "Developer",
            "slug": "development",
            "icon": "💻",
            "description": "Web development and debugging utilities",
            "tools": [
                {
                    "name": "Element Inspector",
                    "description": "Visual debugging tool with AI-ready output format.",
                    "use_case": "Debug web interface issues in research platforms",
                    "bookmarklet_url": "/tools/element-inspector/",
                    "icon": "🔍",
                },
                {
                    "name": "Repository Concatenator",
                    "description": "Concatenate repository files into AI-ready format for code review.",
                    "use_case": "Prepare analysis scripts for AI code review",
                    "bookmarklet_url": "/tools/repo-concatenator/",
                    "icon": "📦",
                },
                {
                    "name": "Color Picker",
                    "description": "Advanced color picker with format conversion and palette generation.",
                    "use_case": "Design consistent color schemes for figure panels",
                    "bookmarklet_url": "/tools/color-picker/",
                    "icon": "🎨",
                },
                {
                    "name": "QR Code Generator",
                    "description": "Generate QR codes for URLs, DOIs, posters, and presentations.",
                    "use_case": "Add QR codes to conference posters linking to papers",
                    "bookmarklet_url": "/tools/qr-code-generator/",
                    "icon": "📱",
                },
            ],
        },
        {
            "name": "Research",
            "slug": "research",
            "icon": "🔬",
            "description": "Literature management and citation tools",
            "tools": [
                {
                    "name": "Asta AI Citation Scraper",
                    "description": "Automatically collect all BibTeX citations from Asta AI search results.",
                    "use_case": "Build bibliography from AI literature searches",
                    "bookmarklet_url": "/tools/asta-citation-scraper/",
                    "icon": "📚",
                },
                {
                    "name": "Statistics Calculator",
                    "description": "Quick statistical analysis for research data with descriptive stats, t-tests, and correlations.",
                    "use_case": "Verify experimental results before plotting",
                    "bookmarklet_url": "/tools/statistics-calculator/",
                    "icon": "📈",
                },
            ],
        },
    ]

    # Calculate total tools
    total_tools = sum(len(domain["tools"]) for domain in domains)

    context = {
        "domains": domains,
        "total_tools": total_tools,
    }

    return render(request, "public_app/pages/tools.html", context)


def tool_element_inspector(request):
    """Element Inspector tool detail page."""
    return render(request, "public_app/tools/element-inspector.html")


def tool_asta_citation_scraper(request):
    """Asta AI Citation Scraper tool detail page."""
    return render(request, "public_app/tools/asta-citation-scraper.html")


def tool_image_concatenator(request):
    """Image Concatenator tool detail page."""
    return render(request, "public_app/tools/image-concatenator.html")


def tool_qr_code_generator(request):
    """QR Code Generator tool detail page."""
    return render(request, "public_app/tools/qr-code-generator.html")


def tool_color_picker(request):
    """Color Picker tool detail page."""
    return render(request, "public_app/tools/color-picker.html")


def tool_markdown_renderer(request):
    """Markdown Renderer tool detail page."""
    return render(request, "public_app/tools/markdown-renderer.html")


def tool_text_diff_checker(request):
    """Text Diff Checker tool detail page."""
    return render(request, "public_app/tools/text-diff-checker.html")


def tool_images_to_gif(request):
    """Images to GIF tool detail page."""
    return render(request, "public_app/tools/images-to-gif.html")


def tool_image_converter(request):
    """Image Converter tool detail page."""
    return render(request, "public_app/tools/image-converter.html")


def tool_pdf_merger(request):
    """PDF Merger tool detail page."""
    return render(request, "public_app/tools/pdf-merger.html")


def tool_statistics_calculator(request):
    """Statistics Calculator tool detail page."""
    return render(request, "public_app/tools/statistics-calculator.html")


def tool_pdf_splitter(request):
    """PDF Splitter tool detail page."""
    return render(request, "public_app/tools/pdf-splitter.html")


def tool_image_resizer(request):
    """Image Resizer tool detail page."""
    return render(request, "public_app/tools/image-resizer.html")


def tool_repo_concatenator(request):
    """Repository Concatenator tool detail page."""
    return render(request, "public_app/tools/repo-concatenator.html")


def tool_json_formatter(request):
    """JSON Formatter tool detail page."""
    return render(request, "public_app/tools/json-formatter.html")


def tool_images_to_pdf(request):
    """Images to PDF tool detail page."""
    return render(request, "public_app/tools/images-to-pdf.html")


def tool_pdf_to_images(request):
    """PDF to Images tool detail page."""
    return render(request, "public_app/tools/pdf-to-images.html")


def tool_pdf_compressor(request):
    """PDF Compressor tool detail page."""
    return render(request, "public_app/tools/pdf-compressor.html")


def tool_video_editor(request):
    """Video Editor tool detail page."""
    return render(request, "public_app/tools/video-editor.html")


def tool_plot_viewer(request):
    """
    Quick CSV Plot Viewer - renders simple CSV plots using Canvas.

    Accepts CSV files with column naming convention:
    ax_{axis_index}_{plot_id}_{plot_type}_{variable}

    Example: ax_00_plot_line_0_line_x, ax_00_plot_line_0_line_y

    Supports: line, scatter, bar plots only.
    For advanced plot types, use the backend plot API.
    """
    return render(request, "public_app/tools/plot-viewer.html")


def tool_plot_backend_test(request):
    """
    Backend Plot Renderer Test - test matplotlib/scitex.plt backend.

    Internal testing tool for the backend plot API.
    """
    return render(request, "public_app/tools/plot-backend-test.html")


def tool_image_viewer(request):
    """
    Image Viewer - Display image with dimension, DPI, and unit conversion info.

    Shows pixel dimensions, DPI, physical size (mm/inch), and conversions
    to help understand figure dimensions for publications.
    """
    return render(request, "public_app/tools/image-viewer.html")


def tool_mermaid_renderer(request):
    """
    Mermaid Diagram Renderer - Create diagrams from text syntax.

    Supports flowcharts, sequence diagrams, Gantt charts, class diagrams,
    pie charts, and git graphs using Mermaid.js syntax.
    """
    return render(request, "public_app/tools/mermaid-renderer.html")


# EOF
