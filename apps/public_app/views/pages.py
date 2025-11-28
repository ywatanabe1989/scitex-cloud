#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-11-28 21:31:00 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/public_app/views/pages.py
# ----------------------------------------
from __future__ import annotations
import os

__FILE__ = "./apps/public_app/views/pages.py"
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Information Pages Views

Handles about, publications, contributors, donate, and fundraising pages.
"""

from django.db import models
from django.shortcuts import render
from django.utils import timezone


def about(request):
    """SciTeX about page - purpose, mission, vision, and values."""
    return render(request, "public_app/pages/about.html")


def publications(request):
    """Publications page."""
    return render(request, "public_app/pages/publications.html")


def donate(request):
    """Donate page view with payment processing."""

    from django.contrib import messages

    from ..forms import DonationForm, EmailVerificationForm
    from ..models import Donation, DonationTier

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
                    from django.shortcuts import redirect
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
                    from .utils import send_donation_confirmation
                    send_donation_confirmation(donation)

                    from django.shortcuts import redirect
                    return redirect(
                        "cloud_app:donation-success", donation_id=donation.id
                    )

                elif donation.payment_method == "paypal":
                    # Redirect to PayPal
                    messages.info(request, "Redirecting to PayPal...")
                    from django.shortcuts import redirect
                    return redirect(
                        "cloud_app:donate"
                    )  # Would redirect to PayPal in production

                elif donation.payment_method == "github":
                    # Redirect to GitHub Sponsors
                    from django.shortcuts import redirect
                    return redirect("https://github.com/sponsors/SciTex-AI")

    else:
        form = DonationForm()

    # Get recent public donations
    recent_donations = (
        Donation.objects.filter(
            is_public=True, is_visitor=False, status="completed"
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


def contributors(request):
    """Contributors page - show SciTeX team and contributors."""
    from ..models import Contributor

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


# EOF
