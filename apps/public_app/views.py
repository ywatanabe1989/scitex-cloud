#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-02 12:13:11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/public_app/views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import logging

from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db import models
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
    # Show landing page to all users (removed auto-redirect for logged-in users)
    # Users can navigate to their profile via the header navigation

    # Module features for landing page demos
    scholar_features = [
        {
            "title": "Multi-Source Search",
            "description": "Concurrent search across CrossRef, PubMed, OpenAlex, Semantic Scholar, and arXiv",
        },
        {
            "title": "Metadata Enrichment",
            "description": "Automatic retrieval of abstract, citation counts, and journal impact factor",
        },
        {
            "title": "PDF Downloads",
            "description": "PDF download with institutional authentication support. Extraction of text, tables, and figures",
        },
        {
            "title": "Local Library",
            "description": "Manage and search your local PDF collection. Compatible with Zotero.",
        },
        {
            "title": "Exporting Formats",
            "description": "Export to BibTeX, RIS, JSON, and Markdown formats",
        },
    ]

    writer_features = [
        {
            "title": "LaTeX Integration",
            "description": "LaTeX compilation with reference management, style changes, and words counts",
        },
        {
            "title": "Manuscript Types",
            "description": "Templates ready for manuscripts, supplementary materials, and revision letters",
        },
        {
            "title": "AI Applicability",
            "description": "Optimized structure for LLM assistants. Automatic differences with visual markup",
        },
        {
            "title": "Bibliography Management",
            "description": "Fact-based reference insertion with Scholar module",
        },
        {
            "title": "Version Control",
            "description": "Git-based workflow with manuscript versioning",
        },
    ]

    code_features = [
        {
            "title": "Session Management",
            "description": "Auto-organized outputs with RUNNING/FINISHED_SUCCESS/ERROR structure",
        },
        {
            "title": "Universal I/O",
            "description": "30+ formats supported: CSV, JSON, HDF5, Zarr, pickle, Excel with auto-detection",
        },
        {
            "title": "Statistical Testing",
            "description": "23 parametric/non-parametric tests, effect sizes, power analysis, 9 export formats",
        },
        {
            "title": "ML & AI Unified",
            "description": "PyTorch training utilities, GenAI (7 providers), cost tracking, classification tools",
        },
        {
            "title": "40+ Research Modules",
            "description": "DSP, plots, scholar, browser, decorators, logging, and more",
        },
    ]

    viz_features = [
        {
            "title": "Publication Quality",
            "description": "Python Wrapper for SigmaPlot to produce publication-ready figures",
        },
        {
            "title": "Style Consistency",
            "description": "Unified/customizable color schemes and typography across all figures",
        },
        {
            "title": "Multi-Format Export",
            "description": "Export to PDF, SVG, PNG, and interactive HTML formats",
        },
    ]

    cloud_features = [
        {
            "title": "Web Interface",
            "description": "Access all SciTeX modules through this website (scitex.ai)",
        },
        {
            "title": "Project Management",
            "description": "Organize research projects with integrated tools and collaboration features",
        },
        {
            "title": "Cloud Storage",
            "description": "Store and sync your research data, papers, and figures across devices",
        },
        {
            "title": "Team Collaboration",
            "description": "Share projects, papers, and resources with research team members",
        },
        {
            "title": "API Access",
            "description": "Programmatic access to all SciTeX modules via REST API",
        },
    ]

    context = {
        "scholar_features": scholar_features,
        "writer_features": writer_features,
        "code_features": code_features,
        "viz_features": viz_features,
        "cloud_features": cloud_features,
    }

    # Otherwise show landing page for anonymous users
    return render(request, "public_app/landing.html", context)


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
    import json

    from django.contrib import messages

    from .forms import DonationForm, EmailVerificationForm, VerifyCodeForm
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
                    messages.success(
                        request, "Verification code sent to your email!"
                    )
                    request.session["verification_email"] = (
                        email_form.cleaned_data["email"]
                    )
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
    from django.template.loader import render_to_string

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
- Date: {donation.completed_at.strftime('%B %d, %Y')}

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


# Missing view functions - added during cleanup to fix URL import errors
def demo(request):
    """Demo page."""
    return render(request, "public_app/demo.html")


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
                "role": contributor.get_role_display() if contributor.role != "contributor" else None,
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
                messages.error(
                    request, "Please provide a name for your API key"
                )
                return redirect("public_app:scitex_api_keys")

            # Create new API key
            api_key, full_key = APIKey.create_key(
                user=request.user,
                name=name,
                scopes=["scholar:read", "scholar:write"],  # Default scopes
            )

            # Store the full key in session to show once
            request.session["new_api_key"] = full_key
            messages.success(
                request, f'API key "{name}" created successfully!'
            )
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

# EOF
