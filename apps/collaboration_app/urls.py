"""
URL configuration for Collaboration app.
"""
from django.urls import path, include
from . import views

app_name = 'collaboration'

# Team management URLs
team_patterns = [
    path('', views.team_list, name='team_list'),
    path('create/', views.team_create, name='team_create'),
    path('<uuid:team_id>/', views.team_detail, name='team_detail'),
    path('<uuid:team_id>/edit/', views.team_edit, name='team_edit'),
    path('<uuid:team_id>/delete/', views.team_delete, name='team_delete'),
    path('<uuid:team_id>/members/', views.team_members, name='team_members'),
    path('<uuid:team_id>/invite/', views.team_invite, name='team_invite'),
    path('<uuid:team_id>/projects/', views.team_projects, name='team_projects'),
    path('<uuid:team_id>/activity/', views.team_activity, name='team_activity'),
]

# API URLs for AJAX requests
api_patterns = [
    # Team management API
    path('teams/', views.api_teams, name='api_teams'),
    path('teams/create/', views.api_team_create, name='api_team_create'),
    path('teams/<uuid:team_id>/', views.api_team_detail, name='api_team_detail'),
    path('teams/<uuid:team_id>/members/', views.api_team_members, name='api_team_members'),
    path('teams/<uuid:team_id>/invite/', views.api_team_invite, name='api_team_invite'),
    path('teams/<uuid:team_id>/join/', views.api_team_join, name='api_team_join'),
    path('teams/<uuid:team_id>/leave/', views.api_team_leave, name='api_team_leave'),
    
    # Project sharing API
    path('projects/share/', views.api_share_project, name='api_share_project'),
    path('projects/<uuid:project_id>/shared/', views.api_project_shared_teams, name='api_project_shared_teams'),
    path('projects/<uuid:project_id>/unshare/<uuid:team_id>/', views.api_unshare_project, name='api_unshare_project'),
    
    # Comments API
    path('comments/create/', views.api_create_comment, name='api_create_comment'),
    path('comments/<int:comment_id>/', views.api_comment_detail, name='api_comment_detail'),
    path('comments/<int:comment_id>/reply/', views.api_reply_comment, name='api_reply_comment'),
    path('comments/<int:comment_id>/resolve/', views.api_resolve_comment, name='api_resolve_comment'),
    
    # Reviews API
    path('reviews/request/', views.api_request_review, name='api_request_review'),
    path('reviews/<int:review_id>/', views.api_review_detail, name='api_review_detail'),
    path('reviews/<int:review_id>/submit/', views.api_submit_review, name='api_submit_review'),
    
    # Notifications API
    path('notifications/', views.api_notifications, name='api_notifications'),
    path('notifications/<int:notification_id>/read/', views.api_mark_notification_read, name='api_mark_notification_read'),
    path('notifications/mark-all-read/', views.api_mark_all_notifications_read, name='api_mark_all_notifications_read'),
    
    # Activity feed API
    path('activity/', views.api_activity_feed, name='api_activity_feed'),
    path('activity/team/<uuid:team_id>/', views.api_team_activity, name='api_team_activity'),
]

# Invitation handling URLs
invitation_patterns = [
    path('invitations/', views.invitation_list, name='invitation_list'),
    path('invitations/<uuid:invitation_id>/accept/', views.accept_invitation, name='accept_invitation'),
    path('invitations/<uuid:invitation_id>/reject/', views.reject_invitation, name='reject_invitation'),
]

urlpatterns = [
    # Main collaboration dashboard
    path('', views.collaboration_dashboard, name='dashboard'),
    
    # Team management
    path('teams/', include(team_patterns)),
    
    # Invitations
    path('', include(invitation_patterns)),
    
    # API endpoints
    path('api/', include(api_patterns)),
    
    # Collaborative features
    path('comments/<str:content_type>/<int:object_id>/', views.object_comments, name='object_comments'),
    path('reviews/<str:content_type>/<int:object_id>/', views.object_reviews, name='object_reviews'),
]