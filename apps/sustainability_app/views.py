#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django.shortcuts import render, redirect


def pricing(request):
    """Display pricing plans."""
    return render(request, 'sustainability_app/pricing.html')


def premium_subscription(request):
    """Premium subscription page."""
    return render(request, 'sustainability_app/premium_subscription.html')


def donation_success(request, donation_id=None):
    """Donation success page."""
    return render(request, 'sustainability_app/donation_success.html')


def fundraising(request):
    """Fundraising page - delegates to cloud_app for now."""
    return redirect('cloud_app:fundraising')

# EOF
