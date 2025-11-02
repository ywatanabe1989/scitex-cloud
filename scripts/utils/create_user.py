#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('SCITEX_CLOUD_DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User

# Create user account
username = 'ywatanabe'
email = 'ywata1989@gmail.com'
password = 'scitex2025!'  # Temporary password

try:
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists")
        user = User.objects.get(username=username)
        user.email = email
        user.save()
        print(f"Updated email for user '{username}' to '{email}'")
    else:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Yusuke',
            last_name='Watanabe'
        )
        print(f"Created user '{username}' with email '{email}'")
        print(f"Temporary password: {password}")
        print("Please change password after first login")
        
    # Make user staff and superuser for admin access
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"User '{username}' now has admin privileges")
    
except Exception as e:
