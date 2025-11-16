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
    tools_list = [
        {
            "name": "Asta AI Citation Scraper",
            "category": "Research",
            "description": "Automatically collect all BibTeX citations from Asta AI search results. Clicks all 'Copy BibTeX' buttons, combines citations, and downloads as a .bib file.",
            "features": [
                "Fast DOM scraping mode (instant!)",
                "Live progress with counter and ETA",
                "Auto-download as .bib file",
                "Progress bar visualization",
                "Clipboard backup copy",
            ],
            "bookmarklet_url": "/tools/asta-citation-scraper/",
            "icon": "📚",
            "color": "#4a9b7e",  # SciTeX success/green
        },
        {
            "name": "Element Inspector",
            "category": "Development",
            "description": "Visual debugging tool for web developers. Inspect any element on any website with colored overlays, click to copy comprehensive debug info formatted for AI assistants.",
            "features": [
                "Alt+I keyboard shortcut to toggle",
                "Escape to close",
                "Click any element to copy debug info",
                "Works on any website",
                "AI-ready output format",
            ],
            "bookmarklet_url": "/tools/element-inspector/",
            "icon": "🔍",
            "color": "#6b8fb3",  # SciTeX info/blue
        },
        {
            "name": "Image Concatenator",
            "category": "Image Processing",
            "description": "Combine multiple images into a single tiled image. Upload images, customize layout with adjustable columns and spacing, and download the concatenated result.",
            "features": [
                "Drag & drop multiple images",
                "Customizable grid layout",
                "Adjustable spacing and background",
                "Reorder images by dragging",
                "Export as PNG, JPEG, or WebP",
                "100% private browser-based processing",
            ],
            "bookmarklet_url": "/tools/image-concatenator/",
            "icon": "🖼️",
            "color": "#9333ea",  # Purple
        },
        {
            "name": "QR Code Generator",
            "category": "Utilities",
            "description": "Generate customizable QR codes for URLs, DOIs, contact info, and more. Perfect for posters, presentations, and publications.",
            "features": [
                "Quick templates (URL, DOI, Email, Phone, WiFi, vCard)",
                "Customizable colors and size",
                "Error correction levels",
                "Download as PNG or SVG",
                "Live preview",
                "100% private browser-based",
            ],
            "bookmarklet_url": "/tools/qr-code-generator/",
            "icon": "📱",
            "color": "#ec4899",  # Pink
        },
        {
            "name": "Color Picker",
            "category": "Design",
            "description": "Advanced color picker with HEX, RGB, HSL, CMYK conversion and palette generation. Generate color harmonies for visualizations.",
            "features": [
                "Multiple format support (HEX, RGB, HSL, CMYK)",
                "Color harmonies (complementary, triadic, etc.)",
                "One-click copy to clipboard",
                "Live palette generation",
                "Perfect for data visualization",
                "100% private browser-based",
            ],
            "bookmarklet_url": "/tools/color-picker/",
            "icon": "🎨",
            "color": "#f59e0b",  # Orange
        },
        {
            "name": "Markdown Renderer",
            "category": "Text Processing",
            "description": "Real-time Markdown preview with syntax highlighting. Write and preview Markdown documents instantly.",
            "features": [
                "Real-time preview",
                "Syntax highlighting for code blocks",
                "Table support",
                "Copy as HTML or Markdown",
                "Download as .md file",
                "Split-pane editor",
            ],
            "bookmarklet_url": "/tools/markdown-renderer/",
            "icon": "📝",
            "color": "#10b981",  # Green
        },
        {
            "name": "Text Diff Checker",
            "category": "Text Processing",
            "description": "Compare two text blocks side-by-side with highlighted differences. Perfect for tracking manuscript revisions.",
            "features": [
                "Side-by-side comparison",
                "Highlighted additions and deletions",
                "Line-by-line diff view",
                "Ignore whitespace/case options",
                "Statistics (added, removed, unchanged)",
                "Swap and clear functions",
            ],
            "bookmarklet_url": "/tools/text-diff-checker/",
            "icon": "🔄",
            "color": "#3b82f6",  # Blue
        },
        {
            "name": "Images to GIF",
            "category": "Image Processing",
            "description": "Convert multiple images into animated GIF. Customize frame duration, quality, and loop settings. Perfect for creating animations.",
            "features": [
                "Drag & drop multiple images",
                "Reorder frames by dragging",
                "Adjustable frame duration",
                "Quality and loop controls",
                "Resize options",
                "Live preview before download",
            ],
            "bookmarklet_url": "/tools/images-to-gif/",
            "icon": "🎬",
            "color": "#8b5cf6",  # Violet
        },
        {
            "name": "Image Converter",
            "category": "Image Processing",
            "description": "Convert images between PNG, JPG, WEBP formats. Batch conversion with quality control for journal submissions.",
            "features": [
                "Multiple format support",
                "Batch conversion",
                "Quality settings",
                "Maintains image dimensions",
                "Fast browser-based processing",
                "Download all at once",
            ],
            "bookmarklet_url": "/tools/image-converter/",
            "icon": "🔄",
            "color": "#06b6d4",  # Cyan
        },
        {
            "name": "PDF Merger",
            "category": "PDF Tools",
            "description": "Combine multiple PDF files into a single document. Drag to reorder pages, perfect for manuscript preparation.",
            "features": [
                "Merge unlimited PDFs",
                "Drag to reorder files",
                "Page count preview",
                "Fast client-side processing",
                "No file size limits",
                "100% private",
            ],
            "bookmarklet_url": "/tools/pdf-merger/",
            "icon": "📑",
            "color": "#dc2626",  # Red
        },
        {
            "name": "Statistics Calculator",
            "category": "Analysis",
            "description": "Quick statistical analysis for research data. Calculate descriptive stats, t-tests, and correlations.",
            "features": [
                "Descriptive statistics",
                "Independent t-test",
                "Pearson correlation",
                "p-values and significance",
                "Effect sizes",
                "Copy-paste data input",
            ],
            "bookmarklet_url": "/tools/statistics-calculator/",
            "icon": "📊",
            "color": "#7c3aed",  # Purple
        },
        {
            "name": "PDF Splitter",
            "category": "PDF Tools",
            "description": "Extract specific pages from PDF files. Select page ranges or individual pages to create new PDFs.",
            "features": [
                "Page range selection (e.g., 1,3,5-8)",
                "Extract individual pages",
                "Fast client-side processing",
                "No file size limits",
                "Preview page count",
                "100% private",
            ],
            "bookmarklet_url": "/tools/pdf-splitter/",
            "icon": "✂️",
            "color": "#ef4444",  # Red
        },
        {
            "name": "Image Resizer",
            "category": "Image Processing",
            "description": "Resize and crop images for journal submissions. Preset dimensions for common formats.",
            "features": [
                "Journal presets (800×600, etc.)",
                "Custom dimensions",
                "Maintain aspect ratio",
                "Live preview",
                "High-quality output",
                "Fast browser-based",
            ],
            "bookmarklet_url": "/tools/image-resizer/",
            "icon": "📐",
            "color": "#0ea5e9",  # Sky blue
        },
        {
            "name": "Repository Concatenator",
            "category": "Development",
            "description": "Concatenate repository files into AI-ready format. Perfect for code review with Claude or GPT.",
            "features": [
                "Upload repository .zip file",
                "Filter by file extension",
                "Configurable depth and line limits",
                "Directory tree structure",
                "Token/character counting",
                "Download as Markdown",
            ],
            "bookmarklet_url": "/tools/repo-concatenator/",
            "icon": "📦",
            "color": "#06b6d4",  # Cyan
        },
        {
            "name": "JSON Formatter",
            "category": "Development",
            "description": "Format, validate, and beautify JSON data. Syntax highlighting and error detection included.",
            "features": [
                "Format with indentation",
                "Minify JSON",
                "Syntax validation",
                "Syntax highlighting",
                "Copy to clipboard",
                "Error messages",
            ],
            "bookmarklet_url": "/tools/json-formatter/",
            "icon": "{ }",
            "color": "#a855f7",  # Purple
        },
        {
            "name": "Images to PDF",
            "category": "PDF Tools",
            "description": "Convert multiple images into a single PDF document. Choose page size, orientation, and margins.",
            "features": [
                "Multiple page sizes (A4, Letter, Legal)",
                "Portrait or landscape orientation",
                "Adjustable margins",
                "Drag to reorder images",
                "Fit images to page",
                "Professional output",
            ],
            "bookmarklet_url": "/tools/images-to-pdf/",
            "icon": "📄",
            "color": "#f97316",  # Orange
        },
        {
            "name": "PDF to Images",
            "category": "PDF Tools",
            "description": "Extract all pages from PDF as PNG or JPG images. Perfect for extracting figures from papers.",
            "features": [
                "Extract all pages as images",
                "PNG or JPEG format",
                "Adjustable DPI (72-288)",
                "High-quality output",
                "Download all at once",
                "Preview before download",
            ],
            "bookmarklet_url": "/tools/pdf-to-images/",
            "icon": "🖼️",
            "color": "#14b8a6",  # Teal
        },
        {
            "name": "PDF Compressor",
            "category": "PDF Tools",
            "description": "Reduce PDF file size while maintaining quality. Perfect for email attachments and journal uploads.",
            "features": [
                "Automatic compression",
                "Before/after size comparison",
                "Compression ratio display",
                "Fast processing",
                "No quality loss",
                "100% private",
            ],
            "bookmarklet_url": "/tools/pdf-compressor/",
            "icon": "🗜️",
            "color": "#f43f5e",  # Rose
        },
        {
            "name": "Video Editor",
            "category": "Video Tools",
            "description": "Trim videos by time window. Basic video editing in your browser.",
            "features": [
                "Trim start and end time",
                "Video preview",
                "Multiple format support",
                "Browser-based processing",
                "No upload required",
                "Quick edits",
            ],
            "bookmarklet_url": "/tools/video-editor/",
            "icon": "🎬",
            "color": "#6366f1",  # Indigo
        },
    ]

    context = {
        "tools_list": tools_list,
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


# EOF
