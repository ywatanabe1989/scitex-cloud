#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoints for email verification
"""
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

from .models import EmailVerification
from apps.core_app.email_service import EmailService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def verify_email_api(request):
    """API endpoint to verify email with OTP code"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        otp_code = data.get('otp_code', '').strip()

        if not email or not otp_code:
            return JsonResponse({
                'success': False,
                'error': 'Email and verification code are required.'
            }, status=400)

        # Find the most recent verification for this email
        try:
            verification = EmailVerification.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()

            if not verification:
                return JsonResponse({
                    'success': False,
                    'error': 'No pending verification found for this email.'
                }, status=404)

            # Check if verification has expired
            if verification.is_expired():
                return JsonResponse({
                    'success': False,
                    'error': 'Verification code has expired. Please request a new one.'
                }, status=400)

            # Verify the code
            if verification.code != otp_code:
                return JsonResponse({
                    'success': False,
                    'error': 'Invalid verification code. Please try again.'
                }, status=400)

            # Mark verification as complete
            verification.verify()

            # Activate the user
            user = verification.user
            user.is_active = True
            user.save()

            # Log the user in
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')

            # Send welcome email
            try:
                EmailService.send_welcome_email(user)
            except Exception as e:
                logger.warning(f"Failed to send welcome email to {user.email}: {str(e)}")

            logger.info(f"Email verified successfully for {email}")
            return JsonResponse({
                'success': True,
                'message': 'Email verified successfully!',
                'redirect_url': f'/@{user.username}/'
            })

        except EmailVerification.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Verification record not found.'
            }, status=404)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error during email verification: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred during verification. Please try again.'
        }, status=500)


@csrf_exempt
@require_http_methods(["POST"])
def resend_otp_api(request):
    """API endpoint to resend OTP verification code"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()

        if not email:
            return JsonResponse({
                'success': False,
                'error': 'Email is required.'
            }, status=400)

        # Find user with this email
        try:
            user = User.objects.get(email=email, is_active=False)
        except User.DoesNotExist:
            # Don't reveal if email exists or not for security
            return JsonResponse({
                'success': True,
                'message': 'If an account exists with this email, a new verification code has been sent.'
            })

        # Invalidate old verifications
        EmailVerification.objects.filter(
            email=email,
            is_verified=False
        ).update(is_verified=True)  # Mark old ones as used

        # Create new verification
        verification = EmailVerification.objects.create(
            user=user,
            email=email,
        )

        # Send new verification email
        try:
            success, message = EmailService.send_otp_email(
                email=email,
                otp_code=verification.code,
                verification_type='signup'
            )

            if success:
                logger.info(f"Resent verification email to {email}")
                return JsonResponse({
                    'success': True,
                    'message': 'A new verification code has been sent to your email.'
                })
            else:
                logger.error(f"Failed to resend verification email to {email}: {message}")
                return JsonResponse({
                    'success': False,
                    'error': 'Failed to send verification email. Please try again.'
                }, status=500)

        except Exception as e:
            logger.error(f"Error resending verification email to {email}: {str(e)}")
            return JsonResponse({
                'success': False,
                'error': 'An error occurred. Please try again.'
            }, status=500)

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'error': 'Invalid JSON data.'
        }, status=400)
    except Exception as e:
        logger.error(f"Error during OTP resend: {str(e)}")
        return JsonResponse({
            'success': False,
            'error': 'An error occurred. Please try again.'
        }, status=500)
