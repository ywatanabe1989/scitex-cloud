#!/usr/bin/env python
"""
Create a test user for SciTeX authentication testing.
Usage: python manage.py shell < tmp/create_test_user.py
"""
from django.contrib.auth.models import User
from apps.auth_app.models import UserProfile

# Test user credentials
username = "testuser"
email = "test@example.com"
password = "TestPass123!"

# Check if user already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"✓ User '{username}' already exists")
    print(f"  Email: {user.email}")
    print(f"  Resetting password to: {password}")
    user.set_password(password)
    user.save()
    print(f"  Password updated!")
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    # Create profile
    UserProfile.objects.get_or_create(user=user)
    print(f"✓ Created new user '{username}'")
    print(f"  Email: {email}")
    print(f"  Password: {password}")

print(f"\nYou can now log in with:")
print(f"  Username: {username}")
print(f"  Email: {email}")
print(f"  Password: {password}")
