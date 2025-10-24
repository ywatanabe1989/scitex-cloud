"""
Issue tracking views for SciTeX projects
GitHub-style issue management system
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Q, Count, Max
from django.utils import timezone
from django.core.paginator import Paginator

from apps.project_app.models import Project
# TODO: Uncomment when Issue models are available
# from apps.project_app.models import (
#     Issue,
#     IssueComment,
#     IssueLabel,
#     IssueMilestone,
#     IssueAssignment,
#     IssueEvent,
# )


# =============================================================================
# Issue List View
# =============================================================================

def issues_list(request, username, slug):
    """
    List all issues for a project with filtering
    Similar to GitHub issues list
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Project not found")

    # Base queryset
    issues = project.issues.select_related(
        'author', 'milestone', 'closed_by'
    ).prefetch_related('labels', 'assignees')

    # Filtering
    state_filter = request.GET.get('state', 'open')  # open, closed, all
    if state_filter == 'open':
        issues = issues.filter(state='open')
    elif state_filter == 'closed':
        issues = issues.filter(state='closed')

    # Label filter
    label_filter = request.GET.getlist('label')
    if label_filter:
        for label in label_filter:
            issues = issues.filter(labels__name=label)

    # Assignee filter
    assignee_filter = request.GET.get('assignee')
    if assignee_filter:
        if assignee_filter == 'none':
            issues = issues.filter(assignees__isnull=True)
        else:
            issues = issues.filter(assignees__username=assignee_filter)

    # Milestone filter
    milestone_filter = request.GET.get('milestone')
    if milestone_filter:
        if milestone_filter == 'none':
            issues = issues.filter(milestone__isnull=True)
        else:
            issues = issues.filter(milestone__title=milestone_filter)

    # Author filter
    author_filter = request.GET.get('author')
    if author_filter:
        issues = issues.filter(author__username=author_filter)

    # Search
    search_query = request.GET.get('q', '').strip()
    if search_query:
        issues = issues.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query)
        )

    # Sorting
    sort = request.GET.get('sort', 'newest')
    if sort == 'newest':
        issues = issues.order_by('-created_at')
    elif sort == 'oldest':
        issues = issues.order_by('created_at')
    elif sort == 'most_commented':
        issues = issues.annotate(
            comment_count=Count('comments')
        ).order_by('-comment_count')
    elif sort == 'recently_updated':
        issues = issues.order_by('-updated_at')

    # Pagination
    paginator = Paginator(issues, 25)  # 25 issues per page
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get labels and milestones for filtering UI
    labels = project.issue_labels.all()
    milestones = project.issue_milestones.filter(state='open')

    # Count statistics
    open_count = project.issues.filter(state='open').count()
    closed_count = project.issues.filter(state='closed').count()

    context = {
        'project': project,
        'issues': page_obj,
        'labels': labels,
        'milestones': milestones,
        'open_count': open_count,
        'closed_count': closed_count,
        'state_filter': state_filter,
        'search_query': search_query,
        'sort': sort,
        'current_filters': {
            'label': label_filter,
            'assignee': assignee_filter,
            'milestone': milestone_filter,
            'author': author_filter,
        }
    }

    return render(request, 'project_app/issues/issues_list.html', context)


# =============================================================================
# Issue Detail View
# =============================================================================

def issue_detail(request, username, slug, issue_number):
    """
    Display a single issue with all comments and events
    Similar to GitHub issue detail page
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(
        Issue.objects.select_related('author', 'milestone', 'closed_by'),
        project=project,
        number=issue_number
    )

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Issue not found")

    # Get comments
    comments = issue.comments.select_related('author').order_by('created_at')

    # Get events (optional - for timeline)
    events = issue.events.select_related('actor').order_by('created_at')

    # Get labels and milestones for editing
    labels = project.issue_labels.all()
    milestones = project.issue_milestones.filter(state='open')

    # Get potential assignees (project collaborators)
    potential_assignees = project.memberships.select_related('user').values_list('user', flat=True)
    from django.contrib.auth.models import User
    assignable_users = User.objects.filter(
        Q(id__in=potential_assignees) | Q(id=project.owner.id)
    ).distinct()

    context = {
        'project': project,
        'issue': issue,
        'comments': comments,
        'events': events,
        'labels': labels,
        'milestones': milestones,
        'assignable_users': assignable_users,
        'can_edit': issue.can_edit(request.user),
        'can_comment': issue.can_comment(request.user),
    }

    return render(request, 'project_app/issues/issue_detail.html', context)


# =============================================================================
# Issue Create View
# =============================================================================

@login_required
def issue_create(request, username, slug):
    """
    Create a new issue
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions (can view = can create issues)
    if not project.can_view(request.user):
        raise Http404("Project not found")

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        label_ids = request.POST.getlist('labels')
        milestone_id = request.POST.get('milestone')
        assignee_ids = request.POST.getlist('assignees')

        # Validation
        if not title:
            messages.error(request, 'Issue title is required')
            return redirect('user_projects:issue_create', username=username, slug=slug)

        # Create issue
        issue = Issue.objects.create(
            project=project,
            title=title,
            description=description,
            author=request.user,
        )

        # Add labels
        if label_ids:
            labels = IssueLabel.objects.filter(id__in=label_ids, project=project)
            issue.labels.set(labels)

        # Add milestone
        if milestone_id:
            try:
                milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
                issue.milestone = milestone
                issue.save()
            except IssueMilestone.DoesNotExist:
                pass

        # Add assignees
        if assignee_ids and project.can_edit(request.user):
            for user_id in assignee_ids:
                try:
                    from django.contrib.auth.models import User
                    user = User.objects.get(id=user_id)
                    IssueAssignment.objects.create(
                        issue=issue,
                        user=user,
                        assigned_by=request.user
                    )
                except User.DoesNotExist:
                    pass

        # Create event
        IssueEvent.objects.create(
            issue=issue,
            event_type='created',
            actor=request.user
        )

        messages.success(request, f'Issue #{issue.number} created successfully')
        return redirect(issue.get_absolute_url())

    # GET request - show form
    labels = project.issue_labels.all()
    milestones = project.issue_milestones.filter(state='open')

    # Get potential assignees
    potential_assignees = project.memberships.select_related('user').values_list('user', flat=True)
    from django.contrib.auth.models import User
    assignable_users = User.objects.filter(
        Q(id__in=potential_assignees) | Q(id=project.owner.id)
    ).distinct()

    context = {
        'project': project,
        'labels': labels,
        'milestones': milestones,
        'assignable_users': assignable_users,
    }

    return render(request, 'project_app/issues/issue_form.html', context)


# =============================================================================
# Issue Edit View
# =============================================================================

@login_required
def issue_edit(request, username, slug, issue_number):
    """
    Edit an existing issue
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not issue.can_edit(request.user):
        messages.error(request, 'You do not have permission to edit this issue')
        return redirect(issue.get_absolute_url())

    if request.method == 'POST':
        old_title = issue.title
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()

        # Validation
        if not title:
            messages.error(request, 'Issue title is required')
            return redirect('user_projects:issue_edit', username=username, slug=slug, issue_number=issue_number)

        # Update issue
        issue.title = title
        issue.description = description
        issue.save()

        # Track rename event
        if old_title != title:
            IssueEvent.objects.create(
                issue=issue,
                event_type='renamed',
                actor=request.user,
                metadata={'old_title': old_title, 'new_title': title}
            )

        messages.success(request, f'Issue #{issue.number} updated successfully')
        return redirect(issue.get_absolute_url())

    # GET request - show form
    context = {
        'project': project,
        'issue': issue,
        'edit_mode': True,
    }

    return render(request, 'project_app/issues/issue_form.html', context)


# =============================================================================
# Issue Comment Create
# =============================================================================

@login_required
def issue_comment_create(request, username, slug, issue_number):
    """
    Add a comment to an issue
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    issue = get_object_or_404(Issue, project=project, number=issue_number)

    # Check permissions
    if not issue.can_comment(request.user):
        messages.error(request, 'You do not have permission to comment on this issue')
        return redirect(issue.get_absolute_url())

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()

        if not content:
            messages.error(request, 'Comment content is required')
            return redirect(issue.get_absolute_url())

        # Create comment
        comment = IssueComment.objects.create(
            issue=issue,
            author=request.user,
            content=content
        )

        messages.success(request, 'Comment added successfully')
        return redirect(issue.get_absolute_url() + f'#comment-{comment.id}')

    return redirect(issue.get_absolute_url())


# =============================================================================
# Label Management
# =============================================================================

@login_required
def issue_label_manage(request, username, slug):
    """
    Manage issue labels for a project
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_edit(request.user):
        raise Http404("Project not found")

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            color = request.POST.get('color', '#0366d6')
            description = request.POST.get('description', '').strip()

            if not name:
                messages.error(request, 'Label name is required')
            else:
                # Check if label already exists
                if IssueLabel.objects.filter(project=project, name=name).exists():
                    messages.error(request, f'Label "{name}" already exists')
                else:
                    IssueLabel.objects.create(
                        project=project,
                        name=name,
                        color=color,
                        description=description
                    )
                    messages.success(request, f'Label "{name}" created successfully')

        elif action == 'edit':
            label_id = request.POST.get('label_id')
            name = request.POST.get('name', '').strip()
            color = request.POST.get('color', '#0366d6')
            description = request.POST.get('description', '').strip()

            try:
                label = IssueLabel.objects.get(id=label_id, project=project)
                label.name = name
                label.color = color
                label.description = description
                label.save()
                messages.success(request, f'Label "{name}" updated successfully')
            except IssueLabel.DoesNotExist:
                messages.error(request, 'Label not found')

        elif action == 'delete':
            label_id = request.POST.get('label_id')
            try:
                label = IssueLabel.objects.get(id=label_id, project=project)
                label.delete()
                messages.success(request, 'Label deleted successfully')
            except IssueLabel.DoesNotExist:
                messages.error(request, 'Label not found')

        return redirect('user_projects:issue_label_manage', username=username, slug=slug)

    # GET request
    labels = project.issue_labels.annotate(
        issue_count=Count('issues')
    ).order_by('name')

    context = {
        'project': project,
        'labels': labels,
    }

    return render(request, 'project_app/issues/label_manage.html', context)


# =============================================================================
# Milestone Management
# =============================================================================

@login_required
def issue_milestone_manage(request, username, slug):
    """
    Manage issue milestones for a project
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_edit(request.user):
        raise Http404("Project not found")

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            due_date = request.POST.get('due_date')

            if not title:
                messages.error(request, 'Milestone title is required')
            else:
                # Check if milestone already exists
                if IssueMilestone.objects.filter(project=project, title=title).exists():
                    messages.error(request, f'Milestone "{title}" already exists')
                else:
                    milestone = IssueMilestone.objects.create(
                        project=project,
                        title=title,
                        description=description
                    )
                    if due_date:
                        from django.utils.dateparse import parse_datetime
                        milestone.due_date = parse_datetime(due_date)
                        milestone.save()
                    messages.success(request, f'Milestone "{title}" created successfully')

        elif action == 'edit':
            milestone_id = request.POST.get('milestone_id')
            title = request.POST.get('title', '').strip()
            description = request.POST.get('description', '').strip()
            due_date = request.POST.get('due_date')

            try:
                milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
                milestone.title = title
                milestone.description = description
                if due_date:
                    from django.utils.dateparse import parse_datetime
                    milestone.due_date = parse_datetime(due_date)
                else:
                    milestone.due_date = None
                milestone.save()
                messages.success(request, f'Milestone "{title}" updated successfully')
            except IssueMilestone.DoesNotExist:
                messages.error(request, 'Milestone not found')

        elif action == 'close':
            milestone_id = request.POST.get('milestone_id')
            try:
                milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
                milestone.close()
                messages.success(request, f'Milestone "{milestone.title}" closed')
            except IssueMilestone.DoesNotExist:
                messages.error(request, 'Milestone not found')

        elif action == 'reopen':
            milestone_id = request.POST.get('milestone_id')
            try:
                milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
                milestone.reopen()
                messages.success(request, f'Milestone "{milestone.title}" reopened')
            except IssueMilestone.DoesNotExist:
                messages.error(request, 'Milestone not found')

        elif action == 'delete':
            milestone_id = request.POST.get('milestone_id')
            try:
                milestone = IssueMilestone.objects.get(id=milestone_id, project=project)
                milestone.delete()
                messages.success(request, 'Milestone deleted successfully')
            except IssueMilestone.DoesNotExist:
                messages.error(request, 'Milestone not found')

        return redirect('user_projects:issue_milestone_manage', username=username, slug=slug)

    # GET request
    milestones = project.issue_milestones.annotate(
        issue_count=Count('issues')
    ).order_by('-created_at')

    # Add progress to each milestone
    for milestone in milestones:
        closed, total, percentage = milestone.get_progress()
        milestone.progress_closed = closed
        milestone.progress_total = total
        milestone.progress_percentage = percentage

    context = {
        'project': project,
        'milestones': milestones,
    }

    return render(request, 'project_app/issues/milestone_manage.html', context)
