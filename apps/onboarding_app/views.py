"""
Views for user onboarding system - Priority 1: User Onboarding & Growth
"""

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Count, Avg
import json

from .models import (
    OnboardingProgress, UserAchievement, OnboardingTemplate, 
    OnboardingSession, OnboardingTip, UserPreference
)
from apps.project_app.models import Project


@login_required
def onboarding_dashboard(request):
    """Main onboarding dashboard showing progress and next steps"""
    progress, created = OnboardingProgress.objects.get_or_create(
        user=request.user,
        defaults={
            'current_step': 'welcome',
            'completion_percentage': 0
        }
    )
    
    # Get recent achievements
    recent_achievements = request.user.achievements.filter(
        is_visible=True
    ).order_by('-earned_at')[:5]
    
    # Get recommended templates
    templates = OnboardingTemplate.objects.filter(
        is_active=True,
        difficulty_level='beginner'
    )[:3]
    
    # Get next step details
    next_step_key, next_step_name = progress.get_next_step()
    
    # Calculate engagement metrics
    total_projects = Project.objects.filter(created_by=request.user).count()
    
    context = {
        'progress': progress,
        'recent_achievements': recent_achievements,
        'templates': templates,
        'next_step_key': next_step_key,
        'next_step_name': next_step_name,
        'total_projects': total_projects,
        'is_completed': progress.is_completed(),
    }
    
    return render(request, 'onboarding_app/dashboard.html', context)


@login_required
def start_onboarding(request):
    """Start the interactive onboarding tutorial"""
    progress, created = OnboardingProgress.objects.get_or_create(
        user=request.user,
        defaults={
            'current_step': 'welcome',
            'completion_percentage': 0
        }
    )
    
    # Create onboarding session
    session = OnboardingSession.objects.create(
        user=request.user,
        session_type='first_visit' if created else 'returning_user'
    )
    
    # Mark session in request for tracking
    request.session['onboarding_session_id'] = str(session.id)
    
    return render(request, 'onboarding_app/tutorial_start.html', {
        'progress': progress,
        'session': session
    })


@login_required
def onboarding_step(request, step_name):
    """Display specific onboarding step"""
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Validate step exists
    step_choices = dict(OnboardingProgress.ONBOARDING_STEPS)
    if step_name not in step_choices:
        messages.error(request, 'Invalid onboarding step.')
        return redirect('onboarding:dashboard')
    
    step_display_name = step_choices[step_name]
    
    # Get contextual tips for this step
    tips = OnboardingTip.objects.filter(
        target_page=step_name,
        is_active=True
    ).order_by('-priority')
    
    # Get template for specific steps
    template_name = f'onboarding_app/steps/{step_name}.html'
    
    context = {
        'progress': progress,
        'step_name': step_name,
        'step_display_name': step_display_name,
        'tips': tips,
        'is_current_step': progress.current_step == step_name,
        'is_completed': step_name in progress.completed_steps,
    }
    
    try:
        return render(request, template_name, context)
    except:
        # Fallback to generic step template
        return render(request, 'onboarding_app/generic_step.html', context)


@login_required
@require_http_methods(["POST"])
def complete_step(request, step_name):
    """Mark an onboarding step as completed"""
    progress = get_object_or_404(OnboardingProgress, user=request.user)
    
    # Mark step as completed
    progress.mark_step_completed(step_name)
    
    # Award achievement if applicable
    award_step_achievement(request.user, step_name)
    
    # Update session if active
    session_id = request.session.get('onboarding_session_id')
    if session_id:
        try:
            session = OnboardingSession.objects.get(id=session_id)
            session.completed_steps.append(step_name)
            session.save()
        except OnboardingSession.DoesNotExist:
            pass
    
    response_data = {
        'success': True,
        'new_percentage': progress.completion_percentage,
        'next_step': progress.current_step,
        'is_completed': progress.is_completed()
    }
    
    return JsonResponse(response_data)


# @login_required
# def guided_tour(request, module_name):
#     """Guided tours removed as per user request"""
#     return redirect('onboarding:dashboard')


@login_required
def create_sample_project(request, template_id):
    """Create a sample project from template"""
    template = get_object_or_404(OnboardingTemplate, id=template_id, is_active=True)
    
    if request.method == 'POST':
        project_name = request.POST.get('project_name', f'{template.name} Sample')
        
        # Create project using template
        project = Project.objects.create(
            name=project_name,
            description=f"Sample project created from {template.name} template",
            created_by=request.user,
            project_type='research',
            is_sample=True  # Mark as sample project
        )
        
        # Create directory structure from template
        create_template_structure(project, template)
        
        # Update template usage
        template.usage_count += 1
        template.save()
        
        # Mark onboarding step as completed
        progress = OnboardingProgress.objects.get(user=request.user)
        progress.mark_step_completed('first_project')
        
        # Award achievement
        award_achievement(request.user, 'first_project', {
            'template_used': template.name,
            'project_id': str(project.id)
        })
        
        messages.success(request, f'Sample project "{project_name}" created successfully!')
        return redirect('core_app:project_detail', project_id=project.id)
    
    context = {
        'template': template,
    }
    
    return render(request, 'onboarding_app/create_sample_project.html', context)


@login_required
def achievements(request):
    """Display user achievements"""
    user_achievements = request.user.achievements.filter(
        is_visible=True
    ).order_by('-earned_at')
    
    # Group by category
    achievements_by_category = {}
    for achievement in user_achievements:
        category = achievement.get_category_display()
        if category not in achievements_by_category:
            achievements_by_category[category] = []
        achievements_by_category[category].append(achievement)
    
    # Calculate total points
    total_points = sum(a.points for a in user_achievements)
    
    context = {
        'achievements_by_category': achievements_by_category,
        'total_achievements': user_achievements.count(),
        'total_points': total_points,
    }
    
    return render(request, 'onboarding_app/achievements.html', context)


@login_required
def preferences(request):
    """User onboarding preferences"""
    preferences, created = UserPreference.objects.get_or_create(
        user=request.user
    )
    
    if request.method == 'POST':
        # Update preferences
        preferences.show_tooltips = request.POST.get('show_tooltips') == 'on'
        preferences.show_guided_tours = request.POST.get('show_guided_tours') == 'on'
        preferences.show_progress_tracker = request.POST.get('show_progress_tracker') == 'on'
        preferences.show_achievements = request.POST.get('show_achievements') == 'on'
        
        preferences.email_onboarding_tips = request.POST.get('email_onboarding_tips') == 'on'
        preferences.email_achievement_notifications = request.POST.get('email_achievement_notifications') == 'on'
        preferences.email_feature_updates = request.POST.get('email_feature_updates') == 'on'
        
        preferences.preferred_learning_style = request.POST.get('preferred_learning_style', 'visual')
        preferences.tutorial_pace = request.POST.get('tutorial_pace', 'medium')
        
        preferences.save()
        
        messages.success(request, 'Onboarding preferences updated successfully!')
        return redirect('onboarding:preferences')
    
    context = {
        'preferences': preferences,
    }
    
    return render(request, 'onboarding_app/preferences.html', context)


# API Views for AJAX interactions

@login_required
@require_http_methods(["POST"])
def api_track_action(request):
    """Track user action for analytics"""
    data = json.loads(request.body)
    action_type = data.get('action_type')
    page = data.get('page')
    metadata = data.get('metadata', {})
    
    # Update session if active
    session_id = request.session.get('onboarding_session_id')
    if session_id:
        try:
            session = OnboardingSession.objects.get(id=session_id)
            session.actions_taken.append({
                'action': action_type,
                'page': page,
                'timestamp': timezone.now().isoformat(),
                'metadata': metadata
            })
            session.save()
        except OnboardingSession.DoesNotExist:
            pass
    
    return JsonResponse({'success': True})


@login_required
def api_get_tips(request):
    """Get contextual tips for current page"""
    page = request.GET.get('page', '')
    
    tips = OnboardingTip.objects.filter(
        target_page=page,
        is_active=True
    ).order_by('-priority')
    
    tips_data = []
    for tip in tips:
        tips_data.append({
            'id': tip.id,
            'title': tip.title,
            'content': tip.content,
            'position': tip.position,
            'target_element': tip.target_element,
            'trigger_condition': tip.trigger_condition,
        })
    
    return JsonResponse({'tips': tips_data})


@login_required
@require_http_methods(["POST"])
def api_dismiss_tip(request, tip_id):
    """Dismiss a tip and update analytics"""
    try:
        tip = OnboardingTip.objects.get(id=tip_id)
        tip.dismiss_count += 1
        tip.save()
        
        return JsonResponse({'success': True})
    except OnboardingTip.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Tip not found'})


@login_required
def api_progress_status(request):
    """Get current onboarding progress"""
    try:
        progress = OnboardingProgress.objects.get(user=request.user)
        
        data = {
            'current_step': progress.current_step,
            'completion_percentage': progress.completion_percentage,
            'completed_steps': progress.completed_steps,
            'is_completed': progress.is_completed(),
            'next_step': progress.get_next_step()[0],
            'total_time_spent': str(progress.total_time_spent),
        }
        
        return JsonResponse(data)
    except OnboardingProgress.DoesNotExist:
        return JsonResponse({'error': 'Progress not found'}, status=404)


# Helper Functions

def award_step_achievement(user, step_name):
    """Award achievement for completing specific steps"""
    step_achievements = {
        'first_project': ('first_project', 'First Project Created', 'Created your first research project', 'fa-folder-plus', 50),
        'first_search': ('first_search', 'First Literature Search', 'Performed your first literature search', 'fa-search', 25),
        'first_document': ('first_document', 'First Document Created', 'Created your first document', 'fa-file-alt', 30),
        'module_tour_scholar': ('explorer', 'Module Explorer', 'Completed guided tours for modules', 'fa-compass', 40),
    }
    
    if step_name in step_achievements:
        achievement_data = step_achievements[step_name]
        award_achievement(user, achievement_data[0], {
            'step': step_name,
            'title': achievement_data[1],
            'description': achievement_data[2],
            'icon': achievement_data[3],
            'points': achievement_data[4]
        })


def award_achievement(user, achievement_type, metadata=None):
    """Award an achievement to user"""
    # Define achievement templates
    achievement_templates = {
        'first_login': ('First Login', 'Welcome to SciTeX!', 'fa-sign-in-alt', 10, 'getting_started'),
        'first_project': ('First Project', 'Created your first project', 'fa-folder-plus', 50, 'productivity'),
        'first_search': ('First Search', 'Performed first literature search', 'fa-search', 25, 'productivity'),
        'first_document': ('First Document', 'Created your first document', 'fa-file-alt', 30, 'productivity'),
        'explorer': ('Module Explorer', 'Explored multiple modules', 'fa-compass', 40, 'expertise'),
    }
    
    if achievement_type in achievement_templates:
        template = achievement_templates[achievement_type]
        
        # Create achievement if not already earned
        achievement, created = UserAchievement.objects.get_or_create(
            user=user,
            achievement_type=achievement_type,
            defaults={
                'title': metadata.get('title', template[0]) if metadata else template[0],
                'description': metadata.get('description', template[1]) if metadata else template[1],
                'icon': metadata.get('icon', template[2]) if metadata else template[2],
                'points': metadata.get('points', template[3]) if metadata else template[3],
                'category': template[4],
                'metadata': metadata or {}
            }
        )
        
        return achievement, created
    
    return None, False


def create_template_structure(project, template):
    """Create directory structure and files from template"""
    # This would integrate with the existing project file system
    # For now, just create basic structure
    structure = template.project_structure
    
    # Implementation would depend on the existing file management system
    # This is a placeholder for the actual file creation logic
    pass