#!/usr/bin/env python
"""
Update user information for SciTeX Cloud platform
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.workspace_app.models import UserProfile

def update_user_info():
    """Update the user with the requested information"""
    username = 'ywatanabe'
    new_email = 'ywatanabe@unimelb.edu.au'
    new_password = 'ywatanabe123'
    first_name = 'Yusuke'
    last_name = 'Watanabe'
    
    try:
        # Get the existing user
        user = User.objects.get(username=username)
        print(f"Found existing user: {user.username}")
        print(f"Current email: {user.email}")
        
        # Update user information
        user.email = new_email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(new_password)  # This will hash the password properly
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"✅ Updated user information:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        
        # Update or create UserProfile
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
        
        if not created:
            # Update existing profile
            profile.academic_title = 'Researcher'
            profile.affiliation = 'University of Melbourne'
            profile.is_academic = True
            profile.is_academic_ja = False
            profile.allow_messages = True
            profile.is_public = True
            profile.save()
            print(f"✅ Updated UserProfile")
        else:
            print(f"✅ Created new UserProfile")
            
        return user
        
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return None

if __name__ == '__main__':
    try:
        user = update_user_info()
        if user:
            print("\n🎉 User information updated successfully!")
            print("You can now login with:")
            print(f"  Username: {user.username}")
            print(f"  Email: {user.email}")
            print(f"  Password: ywatanabe123")
    except Exception as e:
        print(f"❌ Error updating user: {e}")
