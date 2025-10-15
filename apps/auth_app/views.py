#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib import messages


def signup(request):
    """User signup view - delegates to cloud_app for now."""
    return redirect('cloud_app:signup')


def login_view(request):
    """User login view - delegates to cloud_app for now."""
    return redirect('cloud_app:login')


def logout_view(request):
    """User logout view - delegates to cloud_app for now."""
    return redirect('cloud_app:logout')


def forgot_password(request):
    """Forgot password view - delegates to cloud_app for now."""
    return redirect('cloud_app:forgot-password')


def reset_password(request, uidb64, token):
    """Reset password view - delegates to cloud_app for now."""
    return redirect('cloud_app:reset-password', uidb64=uidb64, token=token)


def verify_email(request):
    """Email verification view - delegates to cloud_app for now."""
    return redirect('cloud_app:verify-email')

# EOF
