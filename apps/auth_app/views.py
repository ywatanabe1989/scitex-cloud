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
    """User signup view with email verification required."""
    import logging
    from apps.project_app.services.email_service import EmailService

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Check if email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return render(request, "auth_app/signup.html", {"form": form})

            # Create inactive user (cannot log in until email verified)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False,  # User inactive until email verified
            )

            # Create user profile (should be auto-created by signal, but ensure it exists)
            UserProfile.objects.get_or_create(user=user)

            # Create Gitea user account (sync with Gitea)
            try:
                from apps.gitea_app.services.gitea_sync_service import (
                    sync_user_to_gitea,
                )

                sync_success = sync_user_to_gitea(user, password)
                if sync_success:
                    logger.info(f"Gitea user created for {username}")
                else:
                    logger.warning(f"Failed to create Gitea user for {username}")
            except Exception as e:
                logger.warning(f"Gitea sync failed for {username}: {e}")
                # Don't fail signup if Gitea sync fails

            # Migrate anonymous session data if exists
            if request.session.session_key:
                from apps.project_app.services.anonymous_storage import (
                    migrate_to_user_storage,
                )

                migrated = migrate_to_user_storage(request.session.session_key, user)
                if migrated:
                    logger.info(
                        f"Migrated anonymous session data for new user {username}"
                    )

            # Claim visitor project if user was using visitor pool
            # This transfers visitor-XXX's default-project to the new user's default-project
            from apps.project_app.services.visitor_pool import VisitorPool

            claimed_project = VisitorPool.claim_project_on_signup(request.session, user)
            if claimed_project:
                logger.info(
                    f"Claimed visitor project for new user {username}: {claimed_project.id}"
                )
            else:
                logger.info(f"No visitor project to claim for new user {username}")

            # Create email verification record
            from .models import EmailVerification

            verification = EmailVerification.objects.create(
                user=user,
                email=email,
            )

            # Send verification email
            try:
                success, message = EmailService.send_otp_email(
                    email=email, otp_code=verification.code, verification_type="signup"
                )

                if success:
                    logger.info(f"Verification email sent to {email}")
                    messages.success(
                        request,
                        f"Account created! Please check {email} for a verification code.",
                    )
                    # Redirect to email verification page
                    from django.urls import reverse

                    verify_url = reverse("auth_app:verify-email")
                    return redirect(f"{verify_url}?email={email}")
                else:
                    logger.error(
                        f"Failed to send verification email to {email}: {message}"
                    )
                    # Don't delete user - let them retry verification
                    messages.warning(
                        request,
                        f"Account created but verification email failed to send. "
                        f"Please contact support or try logging in later.",
                    )
                    from django.urls import reverse

                    verify_url = reverse("auth_app:verify-email")
                    return redirect(f"{verify_url}?email={email}")
            except Exception as e:
                logger.error(f"Error during signup for {email}: {str(e)}")
                # Don't delete user - keep the account
                messages.warning(
                    request,
                    f"Account created but there was an issue sending verification email. "
                    f"Please contact support or try logging in later.",
                )
                from django.urls import reverse

                verify_url = reverse("auth_app:verify-email")
                return redirect(f"{verify_url}?email={email}")
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
                # Migrate anonymous session data before login if exists
                if request.session.session_key:
                    from apps.project_app.services.anonymous_storage import (
                        migrate_to_user_storage,
                    )

                    migrated = migrate_to_user_storage(
                        request.session.session_key, user
                    )
                    if migrated:
                        import logging

                        logger = logging.getLogger(__name__)
                        logger.info(
                            f"Migrated anonymous session data for user {user.username}"
                        )
                        messages.info(
                            request,
                            "Your previous session data has been saved to your account!",
                        )

                login(request, user)

                # Handle remember me
                if not form.cleaned_data.get("remember_me"):
                    request.session.set_expiry(0)

                # Redirect to next page or user's project page
                next_page = request.GET.get("next")
                if not next_page:
                    # Default to user's project page (GitHub-style)
                    from django.urls import reverse

                    next_page = reverse(
                        "user_projects:user_profile", kwargs={"username": user.username}
                    )

                messages.success(request, f"Welcome back, @{user.username}!")

                # Create response and register account for switching
                response = redirect(next_page)
                add_authenticated_account(request, response)
                return response
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()

    context = {
        "form": form,
    }
    return render(request, "auth_app/signin.html", context)


def logout_view(request):
    """User logout view - clears all session data and redirects immediately."""
    # Clear all session data before logout
    request.session.flush()

    # Logout user
    logout(request)

    # Redirect immediately without message (cleaner UX)
    return redirect("/")


def forgot_password(request):
    """Forgot password page with email sending."""
    import logging
    from django.core.mail import send_mail
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
            protocol = "https" if request.is_secure() else "http"
            domain = request.get_host()
            reset_url = f"{protocol}://{domain}/auth/reset-password/{uid}/{token}/"

            # Send email with HTML template
            subject = "Password Reset Request - SciTeX"

            # Get site URL from settings
            site_url = getattr(settings, "SITE_URL", "http://127.0.0.1:8000")

            # Plain text message
            message = f"""Hello {user.username},

You requested a password reset for your SciTeX account.

Click the link below to reset your password:
{reset_url}

This link will expire in 24 hours.

If you didn't request this, please ignore this email.

Best regards,
The SciTeX Team
"""

            # HTML message with styled template
            html_message = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <link rel="icon" type="image/png" href="{site_url}/static/shared/images/favicon.png">
                <link rel="shortcut icon" type="image/png" href="{site_url}/static/shared/images/favicon.png">
            </head>
            <body>
            <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
                <div style="text-align: left; margin-bottom: 30px;">
                    <img src="{site_url}/static/shared/images/scitex_logos/scitex-logo-cropped.png" alt="SciTeX Logo" style="height: 60px; margin-bottom: 20px;">
                    <h2 style="margin-top: 20px;">Password Reset Request</h2>
                </div>

                <div style="background: #f8f9fa; padding: 20px; border-radius: 8px; margin-bottom: 20px;">
                    <p>Hello <strong>{user.username}</strong>,</p>
                    <p>You requested a password reset for your SciTeX account.</p>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{reset_url}" style="display: inline-block; background: #4a6baf; color: white; padding: 12px 24px; text-decoration: none; border-radius: 6px; font-weight: bold;">
                            Reset Your Password
                        </a>
                    </div>

                    <p><strong>Important:</strong></p>
                    <ul>
                        <li>This link will expire in 24 hours</li>
                        <li>If you didn't request this reset, please ignore this email</li>
                        <li>Your password will not change unless you click the link above</li>
                    </ul>
                </div>

                <div style="margin-top: 30px; padding-top: 20px; border-top: 1px solid #dee2e6; color: #666; font-size: 14px;">
                    <div style="text-align: center; margin-bottom: 15px;">
                        <img src="{site_url}/static/shared/images/scitex_logos/vectorstock/vectorstock_38853699-navy-inverted-48x48.png" alt="SciTeX" style="height: 32px; opacity: 0.6;">
                    </div>
                    <p>If you didn't request this password reset, please ignore this email or contact support if you have concerns.</p>
                    <p>Best regards,<br>The SciTeX Team</p>
                </div>
            </div>
            </body>
            </html>
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
                    html_message=html_message,
                )
                logger.info(f"Password reset email sent successfully to {email}")
                messages.success(
                    request, "Password reset instructions have been sent to your email!"
                )
            except Exception as e:
                logger.error(
                    f"Failed to send password reset email: {str(e)}", exc_info=True
                )
                if settings.DEBUG:
                    messages.error(request, f"Failed to send reset email: {str(e)}")
                else:
                    messages.error(
                        request, "Failed to send reset email. Please try again later."
                    )

        except User.DoesNotExist:
            logger.info(f"Password reset requested for non-existent email: {email}")
            # For security, don't reveal if email exists
            messages.success(
                request,
                "If an account with this email exists, you will receive password reset instructions.",
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
                    messages.error(
                        request, "Password must be at least 8 characters long."
                    )
                else:
                    # Update user password
                    user.set_password(new_password)
                    user.save()

                    messages.success(
                        request,
                        "Your password has been reset successfully! You can now log in with your new password.",
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
                request, f"Please type exactly: delete {request.user.username}"
            )
            return render(request, "auth_app/delete_account.html")

        # Delete the account
        username = request.user.username
        request.user.delete()

        # Log out and show confirmation
        logout(request)
        messages.success(request, f"Account @{username} has been permanently deleted.")
        return redirect("public_app:index")

    return render(request, "auth_app/delete_account.html")


# =============================================================================
# Theme Preference API
# =============================================================================

from django.views.decorators.http import require_POST
from django.http import JsonResponse
import json


@require_POST
def api_save_theme_preference(request):
    """
    API endpoint to save user's theme preference.

    POST /auth/api/save-theme/
    Body: {
        "theme": "light" | "dark",
        "code_theme_light": "atom-one-light",  // optional
        "code_theme_dark": "dracula"  // optional
    }
    """
    if not request.user.is_authenticated:
        return JsonResponse(
            {"success": False, "error": "Not authenticated"}, status=401
        )

    try:
        data = json.loads(request.body)
        theme = data.get("theme")
        code_theme_light = data.get("code_theme_light")
        code_theme_dark = data.get("code_theme_dark")
        editor_theme_light = data.get("editor_theme_light")
        editor_theme_dark = data.get("editor_theme_dark")

        # Validate theme
        if theme and theme not in ["light", "dark"]:
            return JsonResponse(
                {"success": False, "error": "Invalid theme"}, status=400
            )

        # Get or create user profile
        profile, created = UserProfile.objects.get_or_create(user=request.user)

        # Update theme preferences
        if theme:
            profile.theme_preference = theme
        if code_theme_light:
            profile.code_theme_light = code_theme_light
        if code_theme_dark:
            profile.code_theme_dark = code_theme_dark
        if editor_theme_light:
            profile.editor_theme_light = editor_theme_light
        if editor_theme_dark:
            profile.editor_theme_dark = editor_theme_dark

        profile.save()

        return JsonResponse(
            {
                "success": True,
                "theme": profile.theme_preference,
                "code_theme_light": profile.code_theme_light,
                "code_theme_dark": profile.code_theme_dark,
                "editor_theme_light": profile.editor_theme_light,
                "editor_theme_dark": profile.editor_theme_dark,
            }
        )

    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"success": False, "error": str(e)}, status=500)


def api_get_theme_preference(request):
    """
    API endpoint to get user's theme preference.

    GET /auth/api/get-theme/
    Returns: {
        "theme": "light" | "dark",
        "code_theme_light": "atom-one-light",
        "code_theme_dark": "dracula"
    }
    """
    if not request.user.is_authenticated:
        # Return defaults for anonymous users
        return JsonResponse(
            {
                "theme": "dark",
                "code_theme_light": "atom-one-light",
                "code_theme_dark": "nord",
                "editor_theme_light": "neat",
                "editor_theme_dark": "nord",
            }
        )

    try:
        profile = request.user.auth_profile
        return JsonResponse(
            {
                "theme": profile.theme_preference,
                "code_theme_light": profile.code_theme_light,
                "code_theme_dark": profile.code_theme_dark,
                "editor_theme_light": profile.editor_theme_light,
                "editor_theme_dark": profile.editor_theme_dark,
            }
        )
    except UserProfile.DoesNotExist:
        # Profile doesn't exist yet, return defaults
        return JsonResponse(
            {
                "theme": "dark",
                "code_theme_light": "atom-one-light",
                "code_theme_dark": "nord",
                "editor_theme_light": "neat",
                "editor_theme_dark": "nord",
            }
        )


def get_or_create_device_id(request):
    """Get or create a unique device ID for this browser."""
    import uuid

    device_id = request.COOKIES.get("device_id")
    if not device_id:
        device_id = str(uuid.uuid4())
    return device_id


def add_authenticated_account(request, response):
    """
    Register current user as authenticated on this device.
    Stores in database for persistence across sessions.
    """
    if not request.user.is_authenticated:
        return

    from .models import AuthenticatedDevice, DeviceAccount

    # Get or create device ID
    device_id = get_or_create_device_id(request)

    # Set device ID cookie (if not already set)
    response.set_cookie(
        "device_id",
        device_id,
        max_age=365 * 24 * 60 * 60,  # 1 year
        httponly=True,
        samesite="Lax",
    )

    # Get or create device record
    device, _ = AuthenticatedDevice.objects.get_or_create(device_id=device_id)

    # Add user to this device (if not already added)
    DeviceAccount.objects.get_or_create(device=device, user=request.user)


def switch_account(request, user_id):
    """
    Switch to another account that user has previously authenticated to.
    Only allows switching between accounts authenticated on THIS device.
    """
    from django.http import HttpResponseRedirect
    from django.contrib.auth import logout, login
    from .models import AuthenticatedDevice, DeviceAccount

    # Get device ID
    device_id = request.COOKIES.get("device_id")
    if not device_id:
        messages.error(request, "No device ID found")
        return redirect("/")

    try:
        device = AuthenticatedDevice.objects.get(device_id=device_id)
    except AuthenticatedDevice.DoesNotExist:
        messages.error(request, "Device not found")
        return redirect("/")

    # Check if target user is authenticated on this device
    try:
        device_account = DeviceAccount.objects.get(device=device, user_id=user_id)
    except DeviceAccount.DoesNotExist:
        messages.error(
            request,
            "You can only switch to accounts you've previously logged into on this device",
        )
        return redirect("/")

    # Store the return URL
    return_url = request.GET.get("next", request.META.get("HTTP_REFERER", "/"))

    # Logout current user
    logout(request)

    # Login as target user
    target_user = device_account.user
    login(request, target_user, backend="django.contrib.auth.backends.ModelBackend")

    # Update last_used timestamp
    device_account.save()  # Triggers auto_now on last_used

    messages.success(request, f"Switched to: {target_user.username}")

    return HttpResponseRedirect(return_url)


def get_authenticated_accounts(request):
    """
    API endpoint to get list of accounts authenticated on this device.
    Returns accounts from database based on device ID.
    """
    from django.http import JsonResponse
    from .models import AuthenticatedDevice, DeviceAccount

    if not request.user.is_authenticated:
        return JsonResponse({"accounts": []})

    # Get device ID
    device_id = request.COOKIES.get("device_id")
    if not device_id:
        return JsonResponse({"accounts": [], "current_user_id": request.user.id})

    try:
        device = AuthenticatedDevice.objects.get(device_id=device_id)
        device_accounts = DeviceAccount.objects.filter(device=device).select_related(
            "user"
        )

        accounts = [
            {
                "user_id": da.user.id,
                "username": da.user.username,
                "full_name": da.user.get_full_name() or da.user.username,
            }
            for da in device_accounts
        ]

        return JsonResponse({"accounts": accounts, "current_user_id": request.user.id})

    except AuthenticatedDevice.DoesNotExist:
        return JsonResponse({"accounts": [], "current_user_id": request.user.id})


# EOF
