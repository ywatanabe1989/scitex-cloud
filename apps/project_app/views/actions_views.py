#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CI/CD Actions Views for SciTeX Projects

GitHub Actions-style workflow management views.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.db.models import Q, Count, Avg
from django.core.paginator import Paginator
import yaml
import logging

from apps.project_app.models import Project
# TODO: Uncomment when workflow models are available
# from apps.project_app.models import (
#     Workflow,
#     WorkflowRun,
#     WorkflowJob,
#     WorkflowStep,
# )

logger = logging.getLogger(__name__)


def actions_list(request, username, slug):
    """
    List all workflows for a project

    URL: /<username>/<slug>/actions/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this project")

    # Get all workflows for this project
    workflows = Workflow.objects.filter(project=project).annotate(
        total_runs_count=Count('runs'),
        avg_duration=Avg('runs__duration_seconds')
    ).order_by('-updated_at')

    # Get recent workflow runs (last 10)
    recent_runs = WorkflowRun.objects.filter(
        workflow__project=project
    ).select_related('workflow', 'trigger_user').order_by('-created_at')[:10]

    # Calculate statistics
    total_workflows = workflows.count()
    enabled_workflows = workflows.filter(enabled=True).count()
    total_runs = WorkflowRun.objects.filter(workflow__project=project).count()
    successful_runs = WorkflowRun.objects.filter(
        workflow__project=project,
        conclusion='success'
    ).count()

    success_rate = (successful_runs / total_runs * 100) if total_runs > 0 else 0

    context = {
        'project': project,
        'workflows': workflows,
        'recent_runs': recent_runs,
        'stats': {
            'total_workflows': total_workflows,
            'enabled_workflows': enabled_workflows,
            'total_runs': total_runs,
            'success_rate': round(success_rate, 1),
        },
    }

    return render(request, 'project_app/actions/list.html', context)


def workflow_detail(request, username, slug, workflow_id):
    """
    Show workflow definition and runs history

    URL: /<username>/<slug>/actions/workflows/<workflow_id>/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    workflow = get_object_or_404(Workflow, id=workflow_id, project=project)

    # Check permissions
    if not project.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this project")

    # Get workflow runs with pagination
    runs_list = WorkflowRun.objects.filter(workflow=workflow).select_related(
        'trigger_user'
    ).order_by('-run_number')

    paginator = Paginator(runs_list, 20)
    page_number = request.GET.get('page', 1)
    runs = paginator.get_page(page_number)

    # Parse YAML for display
    yaml_data = workflow.parse_yaml()

    # Calculate statistics
    total_runs = runs_list.count()
    successful = runs_list.filter(conclusion='success').count()
    failed = runs_list.filter(conclusion='failure').count()
    cancelled = runs_list.filter(conclusion='cancelled').count()

    # Calculate average duration
    completed_runs = runs_list.filter(
        status='completed',
        duration_seconds__isnull=False
    )
    avg_duration = completed_runs.aggregate(
        avg=Avg('duration_seconds')
    )['avg'] or 0

    context = {
        'project': project,
        'workflow': workflow,
        'runs': runs,
        'yaml_data': yaml_data,
        'stats': {
            'total_runs': total_runs,
            'successful': successful,
            'failed': failed,
            'cancelled': cancelled,
            'success_rate': round(successful / total_runs * 100, 1) if total_runs > 0 else 0,
            'avg_duration': int(avg_duration),
        },
    }

    return render(request, 'project_app/workflows/detail.html', context)


def workflow_run_detail(request, username, slug, run_id):
    """
    Show specific run with job logs

    URL: /<username>/<slug>/actions/runs/<run_id>/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    run = get_object_or_404(
        WorkflowRun.objects.select_related('workflow', 'trigger_user'),
        id=run_id,
        workflow__project=project
    )

    # Check permissions
    if not project.can_view(request.user):
        return HttpResponseForbidden("You don't have permission to view this project")

    # Get all jobs with their steps
    jobs = WorkflowJob.objects.filter(run=run).prefetch_related('steps').order_by('created_at')

    # Format duration
    duration_text = None
    if run.duration_seconds:
        minutes, seconds = divmod(run.duration_seconds, 60)
        if minutes > 0:
            duration_text = f"{minutes}m {seconds}s"
        else:
            duration_text = f"{seconds}s"

    context = {
        'project': project,
        'workflow': run.workflow,
        'run': run,
        'jobs': jobs,
        'duration_text': duration_text,
    }

    return render(request, 'project_app/workflows/run_detail.html', context)


@login_required
def workflow_create(request, username, slug):
    """
    Create workflow from template or custom YAML

    URL: /<username>/<slug>/actions/new/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to edit this project")

    if request.method == 'POST':
        workflow_name = request.POST.get('name')
        yaml_content = request.POST.get('yaml_content')
        template = request.POST.get('template')

        # If template selected, load template YAML
        if template:
            yaml_content = get_workflow_template(template)

        # Validate YAML
        try:
            yaml_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            messages.error(request, f"Invalid YAML: {str(e)}")
            return render(request, 'project_app/workflows/editor.html', {
                'project': project,
                'yaml_content': yaml_content,
                'workflow_name': workflow_name,
            })

        # Extract trigger events from YAML
        trigger_events = []
        if 'on' in yaml_data:
            on_config = yaml_data['on']
            if isinstance(on_config, str):
                trigger_events.append(on_config)
            elif isinstance(on_config, list):
                trigger_events.extend(on_config)
            elif isinstance(on_config, dict):
                trigger_events.extend(on_config.keys())

        # Create workflow
        workflow = Workflow.objects.create(
            project=project,
            name=workflow_name,
            file_path=f".scitex/workflows/{workflow_name.lower().replace(' ', '_')}.yml",
            yaml_content=yaml_content,
            trigger_events=trigger_events,
            created_by=request.user,
        )

        # Save to filesystem
        save_workflow_to_filesystem(workflow)

        messages.success(request, f"Workflow '{workflow_name}' created successfully")
        return redirect('user_projects:workflow_detail',
                       username=username, slug=slug, workflow_id=workflow.id)

    # GET request - show form
    templates = get_available_templates()

    context = {
        'project': project,
        'templates': templates,
    }

    return render(request, 'project_app/workflows/editor.html', context)


@login_required
def workflow_edit(request, username, slug, workflow_id):
    """
    Edit existing workflow

    URL: /<username>/<slug>/actions/workflows/<workflow_id>/edit/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    workflow = get_object_or_404(Workflow, id=workflow_id, project=project)

    # Check permissions
    if not project.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to edit this project")

    if request.method == 'POST':
        workflow_name = request.POST.get('name')
        yaml_content = request.POST.get('yaml_content')

        # Validate YAML
        try:
            yaml_data = yaml.safe_load(yaml_content)
        except yaml.YAMLError as e:
            messages.error(request, f"Invalid YAML: {str(e)}")
            return render(request, 'project_app/workflows/editor.html', {
                'project': project,
                'workflow': workflow,
                'yaml_content': yaml_content,
                'workflow_name': workflow_name,
                'edit_mode': True,
            })

        # Extract trigger events
        trigger_events = []
        if 'on' in yaml_data:
            on_config = yaml_data['on']
            if isinstance(on_config, str):
                trigger_events.append(on_config)
            elif isinstance(on_config, list):
                trigger_events.extend(on_config)
            elif isinstance(on_config, dict):
                trigger_events.extend(on_config.keys())

        # Update workflow
        workflow.name = workflow_name
        workflow.yaml_content = yaml_content
        workflow.trigger_events = trigger_events
        workflow.save()

        # Update filesystem
        save_workflow_to_filesystem(workflow)

        messages.success(request, f"Workflow '{workflow_name}' updated successfully")
        return redirect('user_projects:workflow_detail',
                       username=username, slug=slug, workflow_id=workflow.id)

    # GET request - show form with existing data
    context = {
        'project': project,
        'workflow': workflow,
        'yaml_content': workflow.yaml_content,
        'workflow_name': workflow.name,
        'edit_mode': True,
    }

    return render(request, 'project_app/workflows/editor.html', context)


@login_required
def workflow_delete(request, username, slug, workflow_id):
    """
    Delete workflow

    URL: /<username>/<slug>/actions/workflows/<workflow_id>/delete/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    workflow = get_object_or_404(Workflow, id=workflow_id, project=project)

    # Check permissions
    if not project.can_edit(request.user):
        return HttpResponseForbidden("You don't have permission to edit this project")

    if request.method == 'POST':
        workflow_name = workflow.name
        workflow.delete()

        # Delete from filesystem
        delete_workflow_from_filesystem(project, workflow)

        messages.success(request, f"Workflow '{workflow_name}' deleted successfully")
        return redirect('user_projects:actions_list', username=username, slug=slug)

    context = {
        'project': project,
        'workflow': workflow,
    }

    return render(request, 'project_app/workflows/delete_confirm.html', context)


@login_required
def workflow_trigger(request, username, slug, workflow_id):
    """
    Manually trigger workflow

    URL: /<username>/<slug>/actions/workflows/<workflow_id>/trigger/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    workflow = get_object_or_404(Workflow, id=workflow_id, project=project)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        # Check if workflow is enabled
        if not workflow.enabled:
            return JsonResponse({'error': 'Workflow is disabled'}, status=400)

        # Get branch (default to current branch)
        branch = request.POST.get('branch', project.current_branch or 'main')

        # Create workflow run
        from apps.project_app.tasks.workflow_tasks import execute_workflow_run

        run = WorkflowRun.objects.create(
            workflow=workflow,
            trigger_event='manual',
            trigger_user=request.user,
            trigger_data={
                'branch': branch,
                'triggered_by': request.user.username,
            },
            branch=branch,
            status='queued',
        )

        # Queue workflow execution (Celery task)
        execute_workflow_run.delay(run.id)

        messages.success(request, f"Workflow '{workflow.name}' triggered successfully")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'run_id': run.id,
                'run_url': run.get_absolute_url(),
            })
        else:
            return redirect('user_projects:workflow_run_detail',
                          username=username, slug=slug, run_id=run.id)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


@login_required
def workflow_enable_disable(request, username, slug, workflow_id):
    """
    Enable or disable workflow

    URL: /<username>/<slug>/actions/workflows/<workflow_id>/toggle/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    workflow = get_object_or_404(Workflow, id=workflow_id, project=project)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    if request.method == 'POST':
        workflow.enabled = not workflow.enabled
        workflow.save()

        status = 'enabled' if workflow.enabled else 'disabled'
        messages.success(request, f"Workflow '{workflow.name}' {status}")

        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({
                'success': True,
                'enabled': workflow.enabled,
            })
        else:
            return redirect('user_projects:workflow_detail',
                          username=username, slug=slug, workflow_id=workflow.id)

    return JsonResponse({'error': 'Method not allowed'}, status=405)


# Helper functions

def get_workflow_template(template_name):
    """Get workflow template YAML content"""
    templates = {
        'python-test': '''name: Python Tests
on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: |
          pytest tests/ -v
''',
        'latex-build': '''name: LaTeX Build
on:
  push:
    branches: [ main ]
    paths:
      - '**.tex'
      - 'scitex/writer/**'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Compile LaTeX
        run: |
          cd scitex/writer/shared
          pdflatex main.tex
          bibtex main
          pdflatex main.tex
          pdflatex main.tex

      - name: Upload PDF
        uses: actions/upload-artifact@v3
        with:
          name: manuscript
          path: scitex/writer/shared/main.pdf
''',
        'code-lint': '''name: Code Linting
on:
  push:
    branches: [ main, develop ]
  pull_request:

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install linting tools
        run: |
          pip install black flake8 mypy

      - name: Run black
        run: black --check .

      - name: Run flake8
        run: flake8 .

      - name: Run mypy
        run: mypy . --ignore-missing-imports
''',
        'docker-build': '''name: Docker Build
on:
  push:
    branches: [ main ]
    tags:
      - 'v*'

jobs:
  build:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout code
        uses: actions/checkout@v3

      - name: Set up Docker Buildx
        uses: docker/setup-buildx-action@v2

      - name: Build Docker image
        run: |
          docker build -t myapp:latest .

      - name: Test Docker image
        run: |
          docker run myapp:latest pytest
''',
    }

    return templates.get(template_name, '')


def get_available_templates():
    """Get list of available workflow templates"""
    return [
        {
            'id': 'python-test',
            'name': 'Python Tests',
            'description': 'Run pytest tests on push and pull requests',
            'icon': 'python',
        },
        {
            'id': 'latex-build',
            'name': 'LaTeX Build',
            'description': 'Compile LaTeX documents and generate PDFs',
            'icon': 'document',
        },
        {
            'id': 'code-lint',
            'name': 'Code Linting',
            'description': 'Run black, flake8, and mypy for code quality',
            'icon': 'check',
        },
        {
            'id': 'docker-build',
            'name': 'Docker Build',
            'description': 'Build and test Docker images',
            'icon': 'container',
        },
    ]


def save_workflow_to_filesystem(workflow):
    """Save workflow YAML to project filesystem"""
    from pathlib import Path
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager

    try:
        manager = get_project_filesystem_manager(workflow.project.owner)
        project_path = manager.get_project_root_path(workflow.project)

        if not project_path:
            logger.error(f"Project path not found for {workflow.project.name}")
            return False

        # Create .scitex/workflows directory
        workflows_dir = project_path / '.scitex' / 'workflows'
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Save workflow YAML
        workflow_file = workflows_dir / Path(workflow.file_path).name
        workflow_file.write_text(workflow.yaml_content)

        logger.info(f"Saved workflow '{workflow.name}' to {workflow_file}")
        return True

    except Exception as e:
        logger.error(f"Failed to save workflow to filesystem: {e}")
        return False


def delete_workflow_from_filesystem(project, workflow):
    """Delete workflow YAML from project filesystem"""
    from pathlib import Path
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager

    try:
        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path:
            return False

        workflow_file = project_path / workflow.file_path
        if workflow_file.exists():
            workflow_file.unlink()
            logger.info(f"Deleted workflow file {workflow_file}")
            return True

        return False

    except Exception as e:
        logger.error(f"Failed to delete workflow from filesystem: {e}")
        return False


# EOF
