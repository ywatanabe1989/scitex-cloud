#!/usr/bin/env python3
"""
Script to create cache table in production database.
Run this on production server to fix cache errors.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Create cache table for database cache."""
    print("Creating cache table...")
    
    try:
        execute_from_command_line(['manage.py', 'createcachetable'])
        print("✅ Cache table created successfully!")
    except Exception as e:
        print(f"❌ Error creating cache table: {e}")

if __name__ == "__main__":
    main()