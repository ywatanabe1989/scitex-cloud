#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-23 08:15:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/apps/workspace_app/management/commands/create_sample_data.py
# ----------------------------------------
import os
__FILE__ = (
    "./apps/workspace_app/management/commands/create_sample_data.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Django management command to create sample data for testing
"""

from django.core.management.base import BaseCommand
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta
import random

# from apps.document_app  # Removed - document_app not installed.models import Document
from apps.auth_app.models import UserProfile
from apps.project_app.models import Project, ProjectPermission
from apps.organizations_app.models import Organization, OrganizationMembership
from apps.writer_app.models import Manuscript


class Command(BaseCommand):
    help = 'Create sample data for testing SciTeX Cloud'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create groups
        research_group, _ = Group.objects.get_or_create(name='Researchers')
        admin_group, _ = Group.objects.get_or_create(name='Administrators')
        
        # Create organizations
        org1, _ = Organization.objects.get_or_create(
            name='SciTeX Research Institute',
            defaults={'description': 'Leading research institute for scientific computing'}
        )
        
        org2, _ = Organization.objects.get_or_create(
            name='Data Science Lab',
            defaults={'description': 'Advanced data science and machine learning research'}
        )
        
        # Create test users
        users = []
        for i in range(5):
            username = f'researcher{i+1}'
            user, created = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': f'{username}@scitex.ai',
                    'first_name': f'Researcher',
                    'last_name': f'{i+1}',
                }
            )
            if created:
                user.set_password('testpass123')
                user.save()
                users.append(user)
                
                # Add to groups
                if i < 3:
                    user.groups.add(research_group)
                if i == 0:
                    user.groups.add(admin_group)
                
                # Create user profile
                profile, _ = UserProfile.objects.get_or_create(
                    user=user,
                    defaults={
                        'bio': f'Research scientist specializing in {random.choice(["AI", "ML", "Data Science", "Bioinformatics", "Physics"])}',
                        'institution': random.choice(['MIT', 'Stanford', 'Harvard', 'Oxford', 'Cambridge']),
                        'research_interests': 'Machine learning, data analysis, scientific computing',
                        'academic_title': random.choice(['PhD', 'MSc', 'Professor', 'Dr.']),
                        'orcid': f'0000-0002-{random.randint(1000,9999)}-{random.randint(1000,9999)}',
                    }
                )
                
                # Add to organizations
                if i < 3:
                    OrganizationMembership.objects.get_or_create(
                        user=user,
                        organization=org1,
                        defaults={'role': 'admin' if i == 0 else 'member'}
                    )
                if i >= 2:
                    OrganizationMembership.objects.get_or_create(
                        user=user,
                        organization=org2,
                        defaults={'role': 'member'}
                    )
                
                self.stdout.write(f'Created user: {username}')
        
        # Create documents for each user
        document_types = ['paper', 'note', 'project', 'draft']
        document_titles = [
            'Deep Learning for Scientific Discovery',
            'Quantum Computing Applications in Chemistry',
            'Statistical Methods for Genomic Analysis',
            'Climate Modeling with Neural Networks',
            'Protein Folding Prediction Algorithms',
            'Data Visualization Best Practices',
            'Research Methodology Guidelines',
            'Machine Learning in Healthcare',
        ]
        
        for user in User.objects.filter(username__startswith='researcher'):
            # Create 3-5 documents per user
            for j in range(random.randint(3, 5)):
                doc_type = random.choice(document_types)
                title = random.choice(document_titles) + f' - {user.username}'
                
                Document.objects.get_or_create(
                    title=title,
                    owner=user,
                    defaults={
                        'content': f'# {title}\n\nThis is a sample document for testing purposes.\n\n## Introduction\n\nLorem ipsum dolor sit amet...',
                        'document_type': doc_type,
                        'is_public': random.choice([True, False]),
                        'tags': 'research, science, ' + doc_type,
                        'created_at': timezone.now() - timedelta(days=random.randint(0, 30)),
                    }
                )
        
        # Create projects
        project_names = [
            'AI-Powered Drug Discovery',
            'Climate Change Prediction Model',
            'Genome Sequencing Pipeline',
            'Quantum Algorithm Development',
            'Neural Interface Research',
        ]
        
        for i, proj_name in enumerate(project_names):
            user = User.objects.filter(username__startswith='researcher')[i % 3]
            
            project, created = Project.objects.get_or_create(
                name=proj_name,
                owner=user,
                defaults={
                    'description': f'Advanced research project focusing on {proj_name.lower()}',
                    'status': random.choice(['planning', 'active', 'active', 'completed']),
                    'progress': random.randint(10, 90),
                    'hypotheses': f'Hypothesis: {proj_name} can significantly improve current methodologies',
                    'data_location': f'/data/projects/{proj_name.lower().replace(" ", "_")}',
                    'organization': org1 if i < 3 else org2,
                    'deadline': timezone.now() + timedelta(days=random.randint(30, 365)),
                }
            )
            
            if created:
                # Add collaborators
                collaborators = User.objects.filter(username__startswith='researcher').exclude(id=user.id)[:2]
                for collab in collaborators:
                    project.collaborators.add(collab)
                    ProjectPermission.objects.get_or_create(
                        user=collab,
                        project=project,
                        defaults={'permission': random.choice(['viewer', 'editor'])}
                    )
                
                # Create manuscripts
                for version in range(1, random.randint(2, 4)):
                    Manuscript.objects.create(
                        project=project,
                        version=version,
                        title=f'{proj_name} - Research Paper',
                        content=f'# {proj_name}\n\n## Abstract\n\nSample manuscript content for version {version}...',
                        created_by=user,
                        is_active=(version == 1),
                    )
                
                self.stdout.write(f'Created project: {proj_name}')
        
        # Create special test user
        test_user, created = User.objects.get_or_create(
            username='testuser',
            defaults={
                'email': 'test@example.com',
                'first_name': 'Test',
                'last_name': 'User',
            }
        )
        if created:
            test_user.set_password('testpass123')
            test_user.save()
            test_user.groups.add(research_group)
            
            # Create profile
            UserProfile.objects.get_or_create(
                user=test_user,
                defaults={
                    'bio': 'Test user for development and testing',
                    'institution': 'SciTeX Institute',
                    'research_interests': 'Testing, Development, QA',
                }
            )
            
            # Add to organization
            OrganizationMembership.objects.get_or_create(
                user=test_user,
                organization=org1,
                defaults={'role': 'member'}
            )
        
        self.stdout.write(self.style.SUCCESS('Successfully created sample data!'))
        self.stdout.write('Login credentials:')
        self.stdout.write('  Username: testuser')
        self.stdout.write('  Password: testpass123')
        self.stdout.write('  Other users: researcher1-5 with same password')

