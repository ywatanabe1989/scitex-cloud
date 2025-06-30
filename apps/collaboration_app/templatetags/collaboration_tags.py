from django import template
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q
from ..models import SharedProject, Comment, Team, Notification

register = template.Library()


@register.inclusion_tag('collaboration_app/widgets/project_collaboration.html', takes_context=True)
def project_collaboration_widget(context, project):
    """
    Render collaboration widget for a project
    Usage: {% project_collaboration_widget project %}
    """
    request = context['request']
    user = request.user
    
    # Get shared teams for this project
    shared_teams = SharedProject.objects.filter(
        project=project, 
        is_active=True
    ).select_related('team', 'shared_by')[:5]
    
    # Get recent collaborators (users who have commented or worked on the project)
    project_content_type = ContentType.objects.get_for_model(project)
    recent_collaborators = set()
    
    # Add users from shared teams
    for shared_project in shared_teams:
        team_members = shared_project.team.get_all_members()[:3]  # Limit to avoid too many
        recent_collaborators.update(team_members)
    
    # Remove the current user and project owner
    recent_collaborators.discard(user)
    recent_collaborators.discard(project.owner)
    recent_collaborators = list(recent_collaborators)[:5]
    
    # Get recent comments
    recent_comments = Comment.objects.filter(
        content_type=project_content_type,
        object_id=project.id,
        is_public=True
    ).select_related('author').order_by('-created_at')[:3]
    
    return {
        'project': project,
        'shared_teams': shared_teams,
        'recent_collaborators': recent_collaborators,
        'recent_comments': recent_comments,
        'content_type_id': project_content_type.id,
        'user': user,
        'request': request,
    }


@register.simple_tag
def get_unread_notifications_count(user):
    """
    Get count of unread notifications for user
    Usage: {% get_unread_notifications_count user %}
    """
    if not user.is_authenticated:
        return 0
    return Notification.objects.filter(recipient=user, is_read=False).count()


@register.simple_tag
def get_user_teams_count(user):
    """
    Get count of teams user belongs to
    Usage: {% get_user_teams_count user %}
    """
    if not user.is_authenticated:
        return 0
    return Team.objects.filter(
        Q(owner=user) | 
        Q(admins=user) | 
        Q(memberships__user=user, memberships__is_active=True)
    ).distinct().count()


@register.filter
def can_manage_collaborators(project, user):
    """
    Check if user can manage collaborators for a project
    Usage: {{ project|can_manage_collaborators:user }}
    """
    if not user.is_authenticated:
        return False
    return project.owner == user or project.has_permission(user, 'can_manage_collaborators')


@register.inclusion_tag('collaboration_app/widgets/notification_bell.html', takes_context=True)
def notification_bell(context):
    """
    Render notification bell with count
    Usage: {% notification_bell %}
    """
    request = context['request']
    user = request.user
    
    if not user.is_authenticated:
        return {'count': 0}
    
    count = Notification.objects.filter(recipient=user, is_read=False).count()
    
    return {
        'count': count,
        'user': user,
        'request': request,
    }


@register.simple_tag
def get_team_role(team, user):
    """
    Get user's role in a team
    Usage: {% get_team_role team user %}
    """
    if not user.is_authenticated:
        return None
    return team.get_user_role(user)


@register.filter
def is_team_member(team, user):
    """
    Check if user is a member of a team
    Usage: {{ team|is_team_member:user }}
    """
    if not user.is_authenticated:
        return False
    return team.is_member(user)


@register.filter
def is_team_admin(team, user):
    """
    Check if user is an admin of a team
    Usage: {{ team|is_team_admin:user }}
    """
    if not user.is_authenticated:
        return False
    return team.is_admin(user)


@register.inclusion_tag('collaboration_app/widgets/team_card.html')
def team_card(team, user=None):
    """
    Render a team card
    Usage: {% team_card team user %}
    """
    return {
        'team': team,
        'user': user,
        'member_count': team.get_member_count(),
        'user_role': team.get_user_role(user) if user else None,
    }


@register.simple_tag
def get_shared_projects_for_team(team):
    """
    Get projects shared with a team
    Usage: {% get_shared_projects_for_team team %}
    """
    return SharedProject.objects.filter(
        team=team, 
        is_active=True
    ).select_related('project', 'shared_by').order_by('-shared_at')


@register.filter
def truncate_content(content, length=100):
    """
    Truncate content to specified length
    Usage: {{ content|truncate_content:80 }}
    """
    if len(content) <= length:
        return content
    return content[:length] + "..."


@register.simple_tag
def get_comment_count(object_instance):
    """
    Get comment count for an object
    Usage: {% get_comment_count project %}
    """
    content_type = ContentType.objects.get_for_model(object_instance)
    return Comment.objects.filter(
        content_type=content_type,
        object_id=object_instance.id,
        is_public=True
    ).count()