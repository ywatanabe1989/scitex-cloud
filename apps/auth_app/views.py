#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.conf import settings

from .forms import SignupForm, LoginForm
from .models import UserProfile


def signup(request):
    """User signup view with registration."""
    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            # Create new user
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )

            # Create user profile (should be auto-created by signal, but ensure it exists)
            UserProfile.objects.get_or_create(user=user)

            # Log the user in
            login(request, user)

            messages.success(
                request,
                f"Welcome to SciTeX, @{user.username}! Your account has been created successfully.",
            )
            # Redirect to user's project page (GitHub-style)
            return redirect('user_projects:user_profile', username=user.username)
    else:
        form = SignupForm()

    context = {
        "form": form,
    }
    return render(request, "auth_app/signup.html", context)


def login_view(request):
    """User login view with authentication."""
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Check if username is actually an email
            if "@" in username:
                try:
                    user_obj = User.objects.get(email=username)
                    username = user_obj.username
                except User.DoesNotExist:
                    pass

            # Authenticate user
            user = authenticate(request, username=username, password=password)

            if user is not None:
                login(request, user)

                # Handle remember me
                if not form.cleaned_data.get("remember_me"):
                    request.session.set_expiry(0)

                # Redirect to next page or user's project page
                next_page = request.GET.get("next")
                if not next_page:
                    # Default to user's project page (GitHub-style)
                    from django.urls import reverse
                    next_page = reverse('user_projects:user_profile', kwargs={'username': user.username})

                messages.success(request, f"Welcome back, @{user.username}!")
                return redirect(next_page)
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {
        "form": form,
    }
    return render(request, "auth_app/login.html", context)


def logout_view(request):
    """User logout view."""
    logout(request)
    messages.success(request, "You have been logged out successfully.")
    return render(request, "auth_app/logout.html")


def forgot_password(request):
    """Forgot password page with email sending."""
    import logging
    from django.core.mail import send_mail
    from django.template.loader import render_to_string
    from django.utils.http import urlsafe_base64_encode
    from django.utils.encoding import force_bytes

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        email = request.POST.get("email", "").strip()

        if not email:
            messages.error(request, "Please provide an email address.")
            return render(request, "auth_app/forgot_password.html")

        try:
            user = User.objects.get(email=email)

            # Generate password reset token
            token = default_token_generator.make_token(user)
            uid = urlsafe_base64_encode(force_bytes(user.pk))

            # Build reset URL with correct domain
            protocol = 'https' if request.is_secure() else 'http'
            domain = request.get_host()
            reset_url = f"{protocol}://{domain}/auth/reset-password/{uid}/{token}/"

            # Send email
            subject = "Password Reset Request - SciTeX"
            message = f"""Hello {user.username},

You requested a password reset for your SciTeX account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
The SciTeX Team
"""

            try:
                logger.info(f"Attempting to send password reset email to {email}")
                logger.info(f"From: {settings.DEFAULT_FROM_EMAIL}")
                logger.info(f"Reset URL: {reset_url}")

                send_mail(
                    subject,
                    message,
                    settings.DEFAULT_FROM_EMAIL,
                    [email],
                    fail_silently=False,
                )
                logger.info(f"Password reset email sent successfully to {email}")
                messages.success(
                    request,
                    "Password reset instructions have been sent to your email!"
                )
            except Exception as e:
                logger.error(f"Failed to send password reset email: {str(e)}", exc_info=True)
                if settings.DEBUG:
                    messages.error(
                        request,
                        f"Failed to send reset email: {str(e)}"
                    )
                else:
                    messages.error(
                        request,
                        "Failed to send reset email. Please try again later."
                    )

        except User.DoesNotExist:
            logger.info(f"Password reset requested for non-existent email: {email}")
            # For security, don't reveal if email exists
            messages.success(
                request,
                "If an account with this email exists, you will receive password reset instructions."
            )

    return render(request, "auth_app/forgot_password.html")


def reset_password(request, uidb64, token):
    """Password reset confirmation page with password update."""
    context = {
        "uidb64": uidb64,
        "token": token,
        "valid_link": False,
        "user": None,
    }

    try:
        # Decode user ID
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)

        # Validate token
        if default_token_generator.check_token(user, token):
            context["valid_link"] = True
            context["user"] = user

            # Handle POST request to update password
            if request.method == "POST":
                new_password = request.POST.get("new_password")
                confirm_password = request.POST.get("confirm_password")

                if not new_password or not confirm_password:
                    messages.error(request, "Please provide both password fields.")
                elif new_password != confirm_password:
                    messages.error(request, "Passwords do not match.")
                elif len(new_password) < 8:
                    messages.error(request, "Password must be at least 8 characters long.")
                else:
                    # Update user password
                    user.set_password(new_password)
                    user.save()

                    messages.success(
                        request,
                        "Your password has been reset successfully! You can now log in with your new password."
                    )
                    return redirect("auth_app:login")

    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        pass

    return render(request, "auth_app/reset_password.html", context)


def verify_email(request):
    """Email verification page for account signup."""
    return render(request, "auth_app/email_verification.html")


from django.contrib.auth.decorators import login_required


@login_required
def delete_account(request):
    """Delete user account with confirmation."""
    if request.method == "POST":
        password = request.POST.get("password", "")
        confirm_text = request.POST.get("confirm_text", "")

        # Verify password
        user = authenticate(request, username=request.user.username, password=password)
        if user is None:
            messages.error(request, "Invalid password. Please try again.")
            return render(request, "auth_app/delete_account.html")

        # Verify confirmation text
        expected_text = f"delete {request.user.username}"
        if confirm_text.strip() != expected_text:
            messages.error(
                request,
                f'Please type exactly: delete {request.user.username}'
            )
            return render(request, "auth_app/delete_account.html")

        # Delete the account
        username = request.user.username
        request.user.delete()

        # Log out and show confirmation
        logout(request)
        messages.success(
            request,
            f"Account @{username} has been permanently deleted."
        )
        return redirect("cloud_app:index")

    return render(request, "auth_app/delete_account.html")

# EOF
