"""
Pull Request Views

GitHub-style pull request views for code review and collaboration.
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.db.models import Q, Count, Prefetch
from django.utils import timezone
from django.views.decorators.http import require_http_methods, require_POST
from django.core.paginator import Paginator
import subprocess
import logging

from apps.project_app.models import (
    Project,
    PullRequest,
    PullRequestReview,
    PullRequestComment,
    PullRequestCommit,
    PullRequestLabel,
    PullRequestEvent,
)

logger = logging.getLogger(__name__)


def pr_list(request, username, slug):
    """
    List all PRs with filtering (open/closed/merged, author, reviewer).

    URL: /<username>/<slug>/pulls/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Project not found")

    # Get filter parameters
    state_filter = request.GET.get('state', 'open')  # open, closed, merged, all
    author_filter = request.GET.get('author', '')
    reviewer_filter = request.GET.get('reviewer', '')
    label_filter = request.GET.get('label', '')
    sort_by = request.GET.get('sort', 'created')  # created, updated, comments
    direction = request.GET.get('direction', 'desc')  # asc, desc

    # Build query
    queryset = PullRequest.objects.filter(project=project)

    # State filter
    if state_filter == 'open':
        queryset = queryset.filter(state='open')
    elif state_filter == 'closed':
        queryset = queryset.filter(state='closed')
    elif state_filter == 'merged':
        queryset = queryset.filter(state='merged')
    # 'all' shows everything

    # Author filter
    if author_filter:
        queryset = queryset.filter(author__username=author_filter)

    # Reviewer filter
    if reviewer_filter:
        queryset = queryset.filter(reviewers__username=reviewer_filter)

    # Label filter
    if label_filter:
        queryset = queryset.filter(labels__contains=[label_filter])

    # Sorting
    sort_field = {
        'created': 'created_at',
        'updated': 'updated_at',
        'comments': 'comment_count',
    }.get(sort_by, 'created_at')

    if direction == 'asc':
        queryset = queryset.order_by(sort_field)
    else:
        queryset = queryset.order_by(f'-{sort_field}')

    # Annotate with counts
    queryset = queryset.annotate(
        comment_count=Count('comments'),
        review_count=Count('reviews'),
    ).select_related('author').prefetch_related('reviewers', 'assignees')

    # Pagination
    paginator = Paginator(queryset, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)

    # Get PR labels for filter
    labels = PullRequestLabel.objects.filter(project=project)

    # Count PRs by state
    open_count = PullRequest.objects.filter(project=project, state='open').count()
    closed_count = PullRequest.objects.filter(project=project, state='closed').count()
    merged_count = PullRequest.objects.filter(project=project, state='merged').count()

    # Get branches for branch selector
    from apps.project_app.services.project_filesystem import get_project_filesystem_manager
    import subprocess
    import logging

    logger = logging.getLogger(__name__)
    manager = get_project_filesystem_manager(project.owner)
    project_path = manager.get_project_root_path(project)

    branches = []
    current_branch = project.current_branch or 'develop'
    if project_path and project_path.exists():
        try:
            result = subprocess.run(
                ['git', 'branch', '-a'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if line.strip():
                        # Remove * prefix and remotes/origin/ prefix
                        branch = line.replace('*', '').strip()
                        branch = branch.replace('remotes/origin/', '')
                        if branch and branch not in branches:
                            branches.append(branch)
                        # Check if this is the current branch
                        if line.startswith('*'):
                            current_branch = branch
        except Exception as e:
            logger.debug(f"Error getting branches: {e}")

    if not branches:
        branches = [current_branch]

    context = {
        'project': project,
        'page_obj': page_obj,
        'prs': page_obj.object_list,
        'state_filter': state_filter,
        'author_filter': author_filter,
        'reviewer_filter': reviewer_filter,
        'label_filter': label_filter,
        'sort_by': sort_by,
        'direction': direction,
        'labels': labels,
        'open_count': open_count,
        'closed_count': closed_count,
        'merged_count': merged_count,
        'can_create': project.can_edit(request.user),
        'branches': branches,
        'current_branch': current_branch,
    }

    return render(request, 'project_app/pull_requests/pr_list.html', context)


def pr_detail(request, username, slug, pr_number):
    """
    Show PR detail with diff, commits, conversation.

    URL: /<username>/<slug>/pull/<pr_number>/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Project not found")

    # Get tab (conversation, commits, files, checks)
    active_tab = request.GET.get('tab', 'conversation')

    # Get PR data with related objects
    pr = PullRequest.objects.filter(
        project=project, number=pr_number
    ).select_related(
        'author', 'merged_by'
    ).prefetch_related(
        'reviewers',
        'assignees',
        Prefetch('comments', queryset=PullRequestComment.objects.select_related('author')),
        Prefetch('reviews', queryset=PullRequestReview.objects.select_related('reviewer')),
        Prefetch('commits', queryset=PullRequestCommit.objects.all()),
        Prefetch('events', queryset=PullRequestEvent.objects.select_related('actor')),
    ).first()

    if not pr:
        raise Http404("Pull request not found")

    # Get approval status
    approval_status = pr.get_approval_status()

    # Check if user can merge
    can_merge, merge_reason = pr.can_merge(request.user) if request.user.is_authenticated else (False, "Not authenticated")

    # Get diff if on files tab
    diff_data = None
    changed_files = []
    if active_tab == 'files':
        diff_data, changed_files = get_pr_diff(project, pr)

    # Get checks status (if checks are configured)
    checks = []
    if active_tab == 'checks':
        checks = get_pr_checks(project, pr)

    # Get timeline (comments + events merged chronologically)
    timeline = get_pr_timeline(pr)

    context = {
        'project': project,
        'pr': pr,
        'active_tab': active_tab,
        'approval_status': approval_status,
        'can_merge': can_merge,
        'merge_reason': merge_reason,
        'can_edit': project.can_edit(request.user),
        'is_author': request.user == pr.author if request.user.is_authenticated else False,
        'diff_data': diff_data,
        'changed_files': changed_files,
        'checks': checks,
        'timeline': timeline,
    }

    return render(request, 'project_app/pull_requests/pr_detail.html', context)


@login_required
def pr_create(request, username, slug):
    """
    Form to create new PR from branch comparison.

    URL: /<username>/<slug>/pull/new/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_edit(request.user):
        messages.error(request, "You don't have permission to create pull requests")
        return redirect('user_projects:detail', username=username, slug=slug)

    # Get compare parameters (base and head branches)
    base_branch = request.GET.get('base', project.current_branch or 'main')
    head_branch = request.GET.get('head', '')

    # Get list of branches
    branches = get_project_branches(project)

    if request.method == 'POST':
        # Create PR
        title = request.POST.get('title', '').strip()
        description = request.POST.get('description', '').strip()
        base = request.POST.get('base', base_branch)
        head = request.POST.get('head', head_branch)
        is_draft = request.POST.get('is_draft') == 'on'
        reviewers = request.POST.getlist('reviewers')

        # Validation
        if not title:
            messages.error(request, "PR title is required")
        elif not head:
            messages.error(request, "Source branch is required")
        elif base == head:
            messages.error(request, "Source and target branches must be different")
        else:
            try:
                # Create PR
                pr = PullRequest.objects.create(
                    project=project,
                    title=title,
                    description=description,
                    author=request.user,
                    source_branch=head,
                    target_branch=base,
                    state='draft' if is_draft else 'open',
                    is_draft=is_draft,
                )

                # Add reviewers
                if reviewers:
                    from django.contrib.auth.models import User
                    reviewer_users = User.objects.filter(username__in=reviewers)
                    pr.reviewers.set(reviewer_users)

                # Sync commits from git
                sync_pr_commits(pr)

                # Check for conflicts
                check_pr_conflicts(pr)

                # Create event
                PullRequestEvent.objects.create(
                    pull_request=pr,
                    event_type='opened',
                    actor=request.user,
                )

                messages.success(request, f"Pull request #{pr.number} created successfully")
                return redirect('user_projects:pr_detail', username=username, slug=slug, pr_number=pr.number)

            except Exception as e:
                logger.error(f"Failed to create PR: {e}")
                messages.error(request, f"Failed to create pull request: {str(e)}")

    # Get comparison data if both branches are selected
    comparison = None
    if head_branch and base_branch:
        comparison = compare_branches(project, base_branch, head_branch)

    # Get potential reviewers (collaborators)
    potential_reviewers = project.collaborators.exclude(id=request.user.id)

    context = {
        'project': project,
        'base_branch': base_branch,
        'head_branch': head_branch,
        'branches': branches,
        'comparison': comparison,
        'potential_reviewers': potential_reviewers,
    }

    return render(request, 'project_app/pull_requests/pr_form.html', context)


@login_required
@require_POST
def pr_merge(request, username, slug, pr_number):
    """
    Merge PR (with merge strategies: merge commit, squash, rebase).

    URL: /<username>/<slug>/pull/<pr_number>/merge/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Check permissions
    if not project.can_edit(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get merge strategy
    strategy = request.POST.get('strategy', 'merge')  # merge, squash, rebase
    commit_message = request.POST.get('commit_message', '')

    # Validate strategy
    if strategy not in ['merge', 'squash', 'rebase']:
        return JsonResponse({'error': 'Invalid merge strategy'}, status=400)

    # Attempt merge
    success, message = pr.merge(request.user, strategy=strategy, commit_message=commit_message)

    if success:
        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type='merged',
            actor=request.user,
            metadata={'strategy': strategy},
        )

        return JsonResponse({
            'success': True,
            'message': message,
            'redirect_url': pr.get_absolute_url(),
        })
    else:
        return JsonResponse({
            'success': False,
            'error': message,
        }, status=400)


@login_required
@require_POST
def pr_review_submit(request, username, slug, pr_number):
    """
    Submit review (approve, request changes, comment).

    URL: /<username>/<slug>/pull/<pr_number>/review/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Check permissions
    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get review data
    review_state = request.POST.get('state', 'commented')  # approved, changes_requested, commented
    content = request.POST.get('content', '').strip()

    # Validation
    if review_state not in ['approved', 'changes_requested', 'commented']:
        return JsonResponse({'error': 'Invalid review state'}, status=400)

    if not content and review_state != 'approved':
        return JsonResponse({'error': 'Review content is required'}, status=400)

    try:
        # Create review
        review = PullRequestReview.objects.create(
            pull_request=pr,
            reviewer=request.user,
            state=review_state,
            content=content,
        )

        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type='reviewed',
            actor=request.user,
            metadata={'state': review_state},
        )

        return JsonResponse({
            'success': True,
            'message': 'Review submitted successfully',
            'review_id': review.id,
        })

    except Exception as e:
        logger.error(f"Failed to submit review: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_POST
def pr_comment_create(request, username, slug, pr_number):
    """
    Add comment (general or inline).

    URL: /<username>/<slug>/pull/<pr_number>/comment/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Check permissions
    if not project.can_view(request.user):
        return JsonResponse({'error': 'Permission denied'}, status=403)

    # Get comment data
    content = request.POST.get('content', '').strip()
    file_path = request.POST.get('file_path', '')
    line_number = request.POST.get('line_number', '')
    commit_sha = request.POST.get('commit_sha', '')
    parent_id = request.POST.get('parent_id', '')

    # Validation
    if not content:
        return JsonResponse({'error': 'Comment content is required'}, status=400)

    try:
        # Create comment
        comment_data = {
            'pull_request': pr,
            'author': request.user,
            'content': content,
        }

        # Add inline comment fields if provided
        if file_path and line_number:
            comment_data['file_path'] = file_path
            comment_data['line_number'] = int(line_number)
            comment_data['commit_sha'] = commit_sha

        # Add parent for threaded comments
        if parent_id:
            parent_comment = PullRequestComment.objects.get(id=parent_id, pull_request=pr)
            comment_data['parent_comment'] = parent_comment

        comment = PullRequestComment.objects.create(**comment_data)

        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type='comment',
            actor=request.user,
        )

        return JsonResponse({
            'success': True,
            'message': 'Comment added successfully',
            'comment_id': comment.id,
        })

    except Exception as e:
        logger.error(f"Failed to create comment: {e}")
        return JsonResponse({
            'success': False,
            'error': str(e),
        }, status=500)


@login_required
@require_POST
def pr_close(request, username, slug, pr_number):
    """
    Close PR without merging.

    URL: /<username>/<slug>/pull/<pr_number>/close/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Attempt to close
    success, message = pr.close(request.user)

    if success:
        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type='closed',
            actor=request.user,
        )

        return JsonResponse({
            'success': True,
            'message': message,
        })
    else:
        return JsonResponse({
            'success': False,
            'error': message,
        }, status=400)


@login_required
@require_POST
def pr_reopen(request, username, slug, pr_number):
    """
    Reopen a closed PR.

    URL: /<username>/<slug>/pull/<pr_number>/reopen/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)
    pr = get_object_or_404(PullRequest, project=project, number=pr_number)

    # Attempt to reopen
    success, message = pr.reopen(request.user)

    if success:
        # Create event
        PullRequestEvent.objects.create(
            pull_request=pr,
            event_type='reopened',
            actor=request.user,
        )

        return JsonResponse({
            'success': True,
            'message': message,
        })
    else:
        return JsonResponse({
            'success': False,
            'error': message,
        }, status=400)


def pr_compare(request, username, slug):
    """
    Branch comparison for creating PR.

    URL: /<username>/<slug>/compare/<base>...<head>/
    """
    project = get_object_or_404(Project, owner__username=username, slug=slug)

    # Check permissions
    if not project.can_view(request.user):
        raise Http404("Project not found")

    # Get compare parameters
    compare_str = request.GET.get('compare', '')
    if '...' in compare_str:
        base, head = compare_str.split('...')
    else:
        base = project.current_branch or 'main'
        head = ''

    # Get list of branches
    branches = get_project_branches(project)

    # Get comparison data
    comparison = None
    if head and base:
        comparison = compare_branches(project, base, head)

    context = {
        'project': project,
        'base_branch': base,
        'head_branch': head,
        'branches': branches,
        'comparison': comparison,
        'can_create': project.can_edit(request.user),
    }

    return render(request, 'project_app/pull_requests/pr_compare.html', context)


# ============================================================================
# Helper Functions
# ============================================================================

def get_project_branches(project):
    """
    Get list of branches for a project.

    Returns:
        list: Branch names
    """
    try:
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return []

        # Get branches from git
        result = subprocess.run(
            ['git', 'branch', '-a'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        if result.returncode != 0:
            return []

        # Parse branch names
        branches = []
        for line in result.stdout.split('\n'):
            line = line.strip()
            if line and not line.startswith('*'):
                # Remove remote prefix
                branch = line.replace('remotes/origin/', '')
                if branch not in branches:
                    branches.append(branch)

        return sorted(branches)

    except Exception as e:
        logger.error(f"Failed to get branches: {e}")
        return []


def compare_branches(project, base, head):
    """
    Compare two branches.

    Returns:
        dict: Comparison data (commits, files changed, diff)
    """
    try:
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return None

        # Get diff between branches
        result = subprocess.run(
            ['git', 'diff', f'{base}...{head}', '--stat'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None

        # Get commit count
        commit_result = subprocess.run(
            ['git', 'rev-list', '--count', f'{base}..{head}'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        commit_count = int(commit_result.stdout.strip()) if commit_result.returncode == 0 else 0

        return {
            'base': base,
            'head': head,
            'commit_count': commit_count,
            'diff_stat': result.stdout,
        }

    except Exception as e:
        logger.error(f"Failed to compare branches: {e}")
        return None


def get_pr_diff(project, pr):
    """
    Get diff for a PR.

    Returns:
        tuple: (diff_data: str, changed_files: list)
    """
    try:
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(project.owner)
        project_path = manager.get_project_root_path(project)

        if not project_path or not project_path.exists():
            return None, []

        # Get full diff
        result = subprocess.run(
            ['git', 'diff', f'{pr.target_branch}...{pr.source_branch}'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return None, []

        diff_data = result.stdout

        # Get changed files
        files_result = subprocess.run(
            ['git', 'diff', '--name-status', f'{pr.target_branch}...{pr.source_branch}'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=10
        )

        changed_files = []
        if files_result.returncode == 0:
            for line in files_result.stdout.split('\n'):
                if line.strip():
                    parts = line.split('\t')
                    if len(parts) >= 2:
                        changed_files.append({
                            'status': parts[0],
                            'path': parts[1],
                        })

        return diff_data, changed_files

    except Exception as e:
        logger.error(f"Failed to get PR diff: {e}")
        return None, []


def get_pr_checks(project, pr):
    """
    Get CI/CD checks status for a PR.

    Returns:
        list: Check results
    """
    # TODO: Implement integration with CI/CD system (GitHub Actions equivalent)
    # For now, return empty list
    return []


def get_pr_timeline(pr):
    """
    Get merged timeline of comments and events.

    Returns:
        list: Timeline items sorted chronologically
    """
    from itertools import chain
    from operator import attrgetter

    # Get comments and events
    comments = list(pr.comments.filter(parent_comment__isnull=True).select_related('author'))
    events = list(pr.events.select_related('actor'))

    # Merge and sort by created_at
    timeline = sorted(
        chain(comments, events),
        key=attrgetter('created_at')
    )

    return timeline


def sync_pr_commits(pr):
    """
    Sync commits from git to PR.

    Args:
        pr: PullRequest instance
    """
    try:
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(pr.project.owner)
        project_path = manager.get_project_root_path(pr.project)

        if not project_path or not project_path.exists():
            return

        # Get commits between base and head
        result = subprocess.run(
            ['git', 'log', f'{pr.target_branch}..{pr.source_branch}', '--format=%H|%an|%ae|%at|%s'],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        if result.returncode != 0:
            return

        # Parse and create commit records
        for line in result.stdout.split('\n'):
            if not line.strip():
                continue

            parts = line.split('|')
            if len(parts) >= 5:
                commit_hash, author_name, author_email, timestamp, message = parts[:5]

                # Create or update commit
                PullRequestCommit.objects.get_or_create(
                    pull_request=pr,
                    commit_hash=commit_hash,
                    defaults={
                        'commit_message': message,
                        'author_name': author_name,
                        'author_email': author_email,
                        'committed_at': timezone.datetime.fromtimestamp(int(timestamp)),
                    }
                )

    except Exception as e:
        logger.error(f"Failed to sync PR commits: {e}")


def check_pr_conflicts(pr):
    """
    Check if PR has merge conflicts.

    Args:
        pr: PullRequest instance
    """
    try:
        from apps.project_app.services.project_filesystem import get_project_filesystem_manager
        manager = get_project_filesystem_manager(pr.project.owner)
        project_path = manager.get_project_root_path(pr.project)

        if not project_path or not project_path.exists():
            return

        # Try to merge (dry run)
        result = subprocess.run(
            ['git', 'merge-tree', pr.target_branch, pr.source_branch],
            cwd=project_path,
            capture_output=True,
            text=True,
            timeout=30
        )

        # Check for conflicts in output
        has_conflicts = 'CONFLICT' in result.stdout

        # Update PR
        pr.has_conflicts = has_conflicts
        if has_conflicts:
            # Parse conflict files
            conflict_files = []
            for line in result.stdout.split('\n'):
                if 'CONFLICT' in line:
                    # Extract filename from conflict message
                    parts = line.split()
                    if len(parts) > 2:
                        conflict_files.append(parts[-1])
            pr.conflict_files = conflict_files

        pr.save(update_fields=['has_conflicts', 'conflict_files'])

    except Exception as e:
        logger.error(f"Failed to check PR conflicts: {e}")
