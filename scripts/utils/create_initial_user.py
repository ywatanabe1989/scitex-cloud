#!/usr/bin/env python
"""
Create initial user for SciTeX Cloud platform
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.workspace_app.models import UserProfile

def create_initial_user():
    """Create the initial user and profile"""
    username = 'ywatanabe'
    email = 'ywatanabe@unimelb.edu.au'
    password = 'ywatanabe123'
    first_name = 'Yusuke'
    last_name = 'Watanabe'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
        print(f"Existing user: {user.username} ({user.email})")
        return user
    
    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,  # Give admin access
        is_superuser=True  # Give superuser access
    )
    
    # Create or update UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'academic_title': 'Researcher',
            'affiliation': 'University of Melbourne',
            'is_academic': True,
            'is_academic_ja': False,  # Australian university
            'allow_messages': True,
            'is_public': True
        }
    )
    
    if created:
        print(f"Created UserProfile for {username}")
    else:
        print(f"UserProfile already exists for {username}")
    
    print(f"Successfully created user: {username}")
    print(f"Email: {email}")
    print(f"Name: {first_name} {last_name}")
    print(f"Admin access: {user.is_staff}")
    print(f"Superuser: {user.is_superuser}")
    print(f"Profile created: {created}")
    
    return user

if __name__ == '__main__':
    try:
        user = create_initial_user()
        print("\n✅ Database initialization completed successfully!")
    except Exception as e:
        print(f"❌ Error creating user: {e}")
