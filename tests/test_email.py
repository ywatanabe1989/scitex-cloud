#!/usr/bin/env python3
"""
Test email configuration and send test email.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_email_config():
    """Test and display email configuration."""
    print("=" * 60)
    print("SciTeX Cloud Email Configuration Test")
    print("=" * 60)
    print()
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_PASSWORD set: {bool(settings.EMAIL_HOST_PASSWORD)}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()


def send_test_email(recipient_email='ywata1989@gmail.com'):
    """Send a test email."""
    print("=" * 60)
    print(f"Sending test email to: {recipient_email}")
    print("=" * 60)
    print()

    try:
        result = send_mail(
            subject='Test Email from SciTeX Cloud',
            message='''
This is a test email to verify SMTP configuration is working correctly.

If you receive this email, password reset and other email features will work!

Configuration tested:
- SMTP Server: mail1030.onamae.ne.jp
- Port: 587 (TLS)
- From: admin@scitex.ai

Best regards,
The SciTeX Team
''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[recipient_email],
            fail_silently=False,
        )

        print("✓ Email sent successfully!")
        print(f"  Result: {result} message(s) sent")
        return True

    except Exception as e:
        print(f"✗ Error sending email:")
        print(f"  {type(e).__name__}: {str(e)}")
        import traceback
        print()
        print("Full traceback:")
        traceback.print_exc()
        return False


if __name__ == '__main__':
    # Test configuration
    test_email_config()

    # Send test email
    import sys
    recipient = sys.argv[1] if len(sys.argv) > 1 else 'ywata1989@gmail.com'
    send_test_email(recipient)
