"""
Views for the Collaboration app - Team workspace and collaboration features.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
import json

from .models import (
    Team, TeamMembership, TeamInvitation, SharedProject, Comment, 
    Review, ActivityFeed, Notification, CollaborativeEdit
)
from apps.core_app.models import Project


@login_required
def collaboration_dashboard(request):
    """Main collaboration dashboard showing teams, notifications, and activity"""
    # Get user's teams
    user_teams = Team.objects.filter(
        Q(owner=request.user) | 
        Q(admins=request.user) | 
        Q(memberships__user=request.user, memberships__is_active=True)
    ).distinct()[:5]
    
    # Get recent notifications
    notifications = request.user.notifications.filter(is_read=False)[:10]
    
    # Get recent activity from user's teams
    activity = ActivityFeed.objects.filter(
        Q(team__in=user_teams) | Q(actor=request.user)
    ).select_related('actor', 'team').order_by('-created_at')[:20]
    
    # Get pending invitations
    pending_invitations = TeamInvitation.objects.filter(
        email=request.user.email, 
        status='pending'
    ).select_related('team', 'invited_by')
    
    context = {
        'user_teams': user_teams,
        'notifications': notifications,
        'activity': activity,
        'pending_invitations': pending_invitations,
        'unread_count': notifications.count(),
    }
    
    return render(request, 'collaboration_app/dashboard.html', context)


@login_required
def team_list(request):
    """List all teams user has access to"""
    # Get teams where user is owner, admin, or member
    teams = Team.objects.filter(
        Q(owner=request.user) | 
        Q(admins=request.user) | 
        Q(memberships__user=request.user, memberships__is_active=True)
    ).distinct().annotate(
        member_count=Count('memberships', filter=Q(memberships__is_active=True))
    ).order_by('-updated_at')
    
    # Pagination
    paginator = Paginator(teams, 12)  # Show 12 teams per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'teams': page_obj,
        'total_teams': teams.count(),
    }
    
    return render(request, 'collaboration_app/team_list.html', context)


@login_required
def team_detail(request, team_id):
    """Team detail page with projects, members, and activity"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check if user has access to this team
    if not team.is_member(request.user):
        raise Http404("Team not found")
    
    # Get team members
    members = team.get_all_members()
    
    # Get shared projects
    shared_projects = team.shared_projects.filter(
        is_active=True
    ).select_related('project', 'shared_by')
    
    # Get recent activity
    activity = team.activities.all()[:20]
    
    # Get user's role in team
    user_role = team.get_user_role(request.user)
    
    context = {
        'team': team,
        'members': members,
        'shared_projects': shared_projects,
        'activity': activity,
        'user_role': user_role,
        'can_manage': team.is_admin(request.user),
    }
    
    return render(request, 'collaboration_app/team_detail.html', context)


@login_required
def team_create(request):
    """Create a new team"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description', '')
        team_type = request.POST.get('team_type', 'research')
        visibility = request.POST.get('visibility', 'private')
        
        if name:
            team = Team.objects.create(
                name=name,
                description=description,
                team_type=team_type,
                visibility=visibility,
                owner=request.user
            )
            
            # Create activity log
            ActivityFeed.objects.create(
                team=team,
                actor=request.user,
                activity_type='team_created',
                description=f"Created team '{team.name}'"
            )
            
            messages.success(request, f"Team '{name}' created successfully!")
            return redirect('collaboration:team_detail', team_id=team.id)
        else:
            messages.error(request, "Team name is required.")
    
    return render(request, 'collaboration_app/team_create.html')


@login_required 
def team_edit(request, team_id):
    """Edit team settings"""
    team = get_object_or_404(Team, id=team_id)
    
    # Only owners and admins can edit
    if not team.is_admin(request.user):
        messages.error(request, "You don't have permission to edit this team.")
        return redirect('collaboration:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        team.name = request.POST.get('name', team.name)
        team.description = request.POST.get('description', team.description)
        team.visibility = request.POST.get('visibility', team.visibility)
        team.allow_member_invites = 'allow_member_invites' in request.POST
        team.require_approval = 'require_approval' in request.POST
        team.max_members = int(request.POST.get('max_members', team.max_members))
        team.save()
        
        messages.success(request, "Team settings updated successfully!")
        return redirect('collaboration:team_detail', team_id=team.id)
    
    context = {'team': team}
    return render(request, 'collaboration_app/team_edit.html', context)


@login_required
def team_delete(request, team_id):
    """Delete a team (owner only)"""
    team = get_object_or_404(Team, id=team_id)
    
    if team.owner != request.user:
        messages.error(request, "Only the team owner can delete the team.")
        return redirect('collaboration:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        team_name = team.name
        team.delete()
        messages.success(request, f"Team '{team_name}' has been deleted.")
        return redirect('collaboration:team_list')
    
    context = {'team': team}
    return render(request, 'collaboration_app/team_delete.html', context)


@login_required
def team_members(request, team_id):
    """Manage team members"""
    team = get_object_or_404(Team, id=team_id)
    
    if not team.is_member(request.user):
        raise Http404("Team not found")
    
    members = team.get_all_members()
    memberships = team.memberships.filter(is_active=True).select_related('user')
    pending_invitations = team.invitations.filter(status='pending')
    
    context = {
        'team': team,
        'members': members,
        'memberships': memberships,
        'pending_invitations': pending_invitations,
        'can_manage': team.is_admin(request.user),
    }
    
    return render(request, 'collaboration_app/team_members.html', context)


@login_required
def team_invite(request, team_id):
    """Invite users to team"""
    team = get_object_or_404(Team, id=team_id)
    
    # Check permissions
    can_invite = (team.is_admin(request.user) or 
                 (team.allow_member_invites and team.is_member(request.user)))
    
    if not can_invite:
        messages.error(request, "You don't have permission to invite members.")
        return redirect('collaboration:team_detail', team_id=team.id)
    
    if request.method == 'POST':
        email = request.POST.get('email')
        role = request.POST.get('role', 'member')
        message = request.POST.get('message', '')
        
        if email:
            # Check if invitation already exists
            existing = TeamInvitation.objects.filter(
                team=team, email=email, status='pending'
            ).exists()
            
            if existing:
                messages.warning(request, f"An invitation to {email} is already pending.")
            else:
                invitation = TeamInvitation.objects.create(
                    team=team,
                    email=email,
                    role=role,
                    message=message,
                    invited_by=request.user
                )
                
                # TODO: Send email notification
                messages.success(request, f"Invitation sent to {email}!")
        
        return redirect('collaboration:team_members', team_id=team.id)
    
    context = {'team': team}
    return render(request, 'collaboration_app/team_invite.html', context)


@login_required
def team_projects(request, team_id):
    """View projects shared with team"""
    team = get_object_or_404(Team, id=team_id)
    
    if not team.is_member(request.user):
        raise Http404("Team not found")
    
    shared_projects = team.shared_projects.filter(
        is_active=True
    ).select_related('project', 'shared_by').order_by('-shared_at')
    
    context = {
        'team': team,
        'shared_projects': shared_projects,
    }
    
    return render(request, 'collaboration_app/team_projects.html', context)


@login_required
def team_activity(request, team_id):
    """View team activity feed"""
    team = get_object_or_404(Team, id=team_id)
    
    if not team.is_member(request.user):
        raise Http404("Team not found")
    
    activity = team.activities.select_related('actor').order_by('-created_at')
    
    # Pagination
    paginator = Paginator(activity, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'team': team,
        'activity': page_obj,
    }
    
    return render(request, 'collaboration_app/team_activity.html', context)


@login_required
def invitation_list(request):
    """List pending invitations for user"""
    invitations = TeamInvitation.objects.filter(
        email=request.user.email, 
        status='pending'
    ).select_related('team', 'invited_by').order_by('-created_at')
    
    context = {'invitations': invitations}
    return render(request, 'collaboration_app/invitations.html', context)


@login_required
def accept_invitation(request, invitation_id):
    """Accept team invitation"""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id)
    
    if invitation.email != request.user.email:
        raise Http404("Invitation not found")
    
    success, message = invitation.accept(request.user)
    if success:
        messages.success(request, "Invitation accepted! Welcome to the team.")
        return redirect('collaboration:team_detail', team_id=invitation.team.id)
    else:
        messages.error(request, f"Could not accept invitation: {message}")
        return redirect('collaboration:invitation_list')


@login_required
def reject_invitation(request, invitation_id):
    """Reject team invitation"""
    invitation = get_object_or_404(TeamInvitation, id=invitation_id)
    
    if invitation.email != request.user.email:
        raise Http404("Invitation not found")
    
    invitation.reject()
    messages.info(request, "Invitation rejected.")
    return redirect('collaboration:invitation_list')


@login_required
def object_comments(request, content_type, object_id):
    """View comments for a specific object"""
    try:
        ct = ContentType.objects.get(model=content_type.lower())
        comments = Comment.objects.filter(
            content_type=ct, 
            object_id=object_id,
            is_public=True
        ).select_related('author').order_by('created_at')
    except ContentType.DoesNotExist:
        raise Http404("Invalid content type")
    
    context = {
        'comments': comments,
        'content_type': content_type,
        'object_id': object_id,
    }
    
    return render(request, 'collaboration_app/comments.html', context)


@login_required 
def object_reviews(request, content_type, object_id):
    """View reviews for a specific object"""
    try:
        ct = ContentType.objects.get(model=content_type.lower())
        reviews = Review.objects.filter(
            content_type=ct,
            object_id=object_id
        ).select_related('reviewer', 'requested_by').order_by('-requested_at')
    except ContentType.DoesNotExist:
        raise Http404("Invalid content type")
    
    context = {
        'reviews': reviews,
        'content_type': content_type,
        'object_id': object_id,
    }
    
    return render(request, 'collaboration_app/reviews.html', context)


# API Views for AJAX requests

@login_required
@require_http_methods(["GET"])
def api_teams(request):
    """API endpoint to get user's teams"""
    teams = Team.objects.filter(
        Q(owner=request.user) | 
        Q(admins=request.user) | 
        Q(memberships__user=request.user, memberships__is_active=True)
    ).distinct().values('id', 'name', 'description', 'team_type', 'visibility')
    
    return JsonResponse({'teams': list(teams)})


@login_required
@require_http_methods(["POST"])
def api_team_create(request):
    """API endpoint to create a team"""
    try:
        data = json.loads(request.body)
        team = Team.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            team_type=data.get('team_type', 'research'),
            visibility=data.get('visibility', 'private'),
            owner=request.user
        )
        
        return JsonResponse({
            'success': True,
            'team_id': str(team.id),
            'message': 'Team created successfully'
        })
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_http_methods(["GET"])
def api_team_detail(request, team_id):
    """API endpoint to get team details"""
    try:
        team = Team.objects.get(id=team_id)
        if not team.is_member(request.user):
            return JsonResponse({'error': 'Access denied'}, status=403)
        
        data = {
            'id': str(team.id),
            'name': team.name,
            'description': team.description,
            'team_type': team.team_type,
            'visibility': team.visibility,
            'member_count': team.get_member_count(),
            'user_role': team.get_user_role(request.user),
        }
        
        return JsonResponse(data)
    except Team.DoesNotExist:
        return JsonResponse({'error': 'Team not found'}, status=404)


@login_required
@require_http_methods(["GET"])
def api_notifications(request):
    """API endpoint to get user notifications"""
    notifications = request.user.notifications.filter(
        is_read=False
    ).order_by('-created_at')[:20]
    
    data = [{
        'id': n.id,
        'title': n.title,
        'message': n.message,
        'type': n.notification_type,
        'priority': n.priority,
        'created_at': n.created_at.isoformat(),
        'action_url': n.action_url,
    } for n in notifications]
    
    return JsonResponse({'notifications': data})


@login_required
@require_http_methods(["POST"])
def api_mark_notification_read(request, notification_id):
    """API endpoint to mark notification as read"""
    try:
        notification = request.user.notifications.get(id=notification_id)
        notification.mark_as_read()
        return JsonResponse({'success': True})
    except Notification.DoesNotExist:
        return JsonResponse({'error': 'Notification not found'}, status=404)


@login_required
@require_http_methods(["POST"])
def api_mark_all_notifications_read(request):
    """API endpoint to mark all notifications as read"""
    count = request.user.notifications.filter(is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    return JsonResponse({'success': True, 'count': count})


# Placeholder views for other API endpoints
def api_team_members(request, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_team_invite(request, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_team_join(request, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_team_leave(request, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_share_project(request):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_project_shared_teams(request, project_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_unshare_project(request, project_id, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_create_comment(request):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_comment_detail(request, comment_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_reply_comment(request, comment_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_resolve_comment(request, comment_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_request_review(request):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_review_detail(request, review_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_submit_review(request, review_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_activity_feed(request):
    return JsonResponse({'error': 'Not implemented'}, status=501)

def api_team_activity(request, team_id):
    return JsonResponse({'error': 'Not implemented'}, status=501)