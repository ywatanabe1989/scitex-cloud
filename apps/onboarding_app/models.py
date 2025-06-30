"""
Models for user onboarding, progress tracking, and achievements system.
Priority 1: User Onboarding & Growth implementation.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator


class OnboardingProgress(models.Model):
    """Track user progress through onboarding steps"""
    
    ONBOARDING_STEPS = [
        ('welcome', 'Welcome & Introduction'),
        ('profile_setup', 'Profile Setup'),
        ('first_project', 'Create First Project'),
        ('first_search', 'First Literature Search'),
        ('first_document', 'Create First Document'),
        ('completed', 'Onboarding Completed'),
    ]
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding_progress')
    current_step = models.CharField(max_length=30, choices=ONBOARDING_STEPS, default='welcome')
    completed_steps = models.JSONField(default=list, help_text="List of completed step names")
    
    # Progress tracking
    completion_percentage = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    started_at = models.DateTimeField(auto_now_add=True)
    last_activity_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # User preferences
    show_tips = models.BooleanField(default=True, help_text="Show contextual tips")
    
    # Engagement metrics
    session_count = models.IntegerField(default=0)
    total_time_spent = models.DurationField(default=timezone.timedelta)
    
    class Meta:
        ordering = ['-last_activity_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_current_step_display()} ({self.completion_percentage}%)"
    
    def mark_step_completed(self, step_name):
        """Mark a step as completed and update progress"""
        if step_name not in self.completed_steps:
            self.completed_steps.append(step_name)
            self.save()
            
            # Update completion percentage
            total_steps = len(self.ONBOARDING_STEPS) - 1  # Exclude 'completed' step
            self.completion_percentage = int((len(self.completed_steps) / total_steps) * 100)
            
            # Update current step to next uncompleted step
            for step_key, _ in self.ONBOARDING_STEPS:
                if step_key not in self.completed_steps:
                    self.current_step = step_key
                    break
            else:
                self.current_step = 'completed'
                self.completed_at = timezone.now()
            
            self.save()
    
    def get_next_step(self):
        """Get the next step in onboarding"""
        for step_key, step_name in self.ONBOARDING_STEPS:
            if step_key not in self.completed_steps:
                return step_key, step_name
        return None, None
    
    def is_completed(self):
        """Check if onboarding is completed"""
        return self.current_step == 'completed'


class UserAchievement(models.Model):
    """User achievements and milestones"""
    
    ACHIEVEMENT_TYPES = [
        ('first_login', 'First Login'),
        ('profile_complete', 'Profile Complete'),
        ('first_project', 'First Project Created'),
        ('first_search', 'First Literature Search'),
        ('first_document', 'First Document Created'),
        ('first_collaboration', 'First Team Collaboration'),
        ('power_user', 'Power User (10+ projects)'),
        ('researcher', 'Active Researcher (50+ searches)'),
        ('author', 'Prolific Author (10+ documents)'),
        ('collaborator', 'Team Player (5+ collaborations)'),
        ('explorer', 'Module Explorer (all modules used)'),
        ('mentor', 'Community Mentor (helped others)'),
        ('expert', 'Domain Expert (advanced features used)'),
        ('pioneer', 'Early Adopter'),
        ('contributor', 'Platform Contributor'),
        ('advocate', 'Platform Advocate'),
    ]
    
    ACHIEVEMENT_CATEGORIES = [
        ('getting_started', 'Getting Started'),
        ('productivity', 'Productivity'),
        ('collaboration', 'Collaboration'),
        ('expertise', 'Expertise'),
        ('community', 'Community'),
        ('special', 'Special Recognition'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='achievements')
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES)
    category = models.CharField(max_length=20, choices=ACHIEVEMENT_CATEGORIES, default='getting_started')
    
    # Achievement details
    title = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=50, default='fa-trophy', help_text="FontAwesome icon class")
    points = models.IntegerField(default=10, help_text="Points awarded for this achievement")
    
    # Status
    earned_at = models.DateTimeField(auto_now_add=True)
    is_visible = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    
    # Context data
    metadata = models.JSONField(default=dict, blank=True, help_text="Additional achievement data")
    
    class Meta:
        unique_together = ('user', 'achievement_type')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.title}"


class OnboardingTemplate(models.Model):
    """Sample project templates for onboarding"""
    
    TEMPLATE_TYPES = [
        ('literature_review', 'Literature Review'),
        ('research_paper', 'Research Paper'),
        ('data_analysis', 'Data Analysis Project'),
        ('collaboration', 'Team Collaboration'),
        ('thesis', 'Thesis Project'),
        ('grant_proposal', 'Grant Proposal'),
        ('conference_paper', 'Conference Paper'),
        ('journal_article', 'Journal Article'),
    ]
    
    RESEARCH_FIELDS = [
        ('computer_science', 'Computer Science'),
        ('biology', 'Biology'),
        ('chemistry', 'Chemistry'),
        ('physics', 'Physics'),
        ('medicine', 'Medicine'),
        ('psychology', 'Psychology'),
        ('economics', 'Economics'),
        ('engineering', 'Engineering'),
        ('mathematics', 'Mathematics'),
        ('social_sciences', 'Social Sciences'),
        ('humanities', 'Humanities'),
        ('interdisciplinary', 'Interdisciplinary'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=200)
    description = models.TextField()
    template_type = models.CharField(max_length=30, choices=TEMPLATE_TYPES)
    research_field = models.CharField(max_length=30, choices=RESEARCH_FIELDS, default='interdisciplinary')
    
    # Template content
    project_structure = models.JSONField(default=dict, help_text="Directory structure and files")
    sample_content = models.JSONField(default=dict, help_text="Sample file contents")
    guided_steps = models.JSONField(default=list, help_text="Step-by-step guidance")
    
    # Metadata
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
    ], default='beginner')
    estimated_time = models.DurationField(default=timezone.timedelta(hours=2))
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['template_type', 'difficulty_level']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"


class OnboardingSession(models.Model):
    """Track individual onboarding sessions"""
    
    SESSION_TYPES = [
        ('first_visit', 'First Visit'),
        ('returning_user', 'Returning User'),
        ('feature_discovery', 'Feature Discovery'),
        ('help_seeking', 'Help Seeking'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='onboarding_sessions')
    session_type = models.CharField(max_length=20, choices=SESSION_TYPES, default='first_visit')
    
    # Session tracking
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    duration = models.DurationField(null=True, blank=True)
    
    # Activities during session
    pages_visited = models.JSONField(default=list)
    actions_taken = models.JSONField(default=list)
    features_explored = models.JSONField(default=list)
    
    # Outcomes
    completed_steps = models.JSONField(default=list)
    achievements_earned = models.JSONField(default=list)
    
    # User experience
    satisfaction_rating = models.IntegerField(null=True, blank=True, validators=[MinValueValidator(1), MaxValueValidator(5)])
    feedback = models.TextField(blank=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_session_type_display()} ({self.started_at.strftime('%Y-%m-%d %H:%M')})"
    
    def end_session(self):
        """End the session and calculate duration"""
        if not self.ended_at:
            self.ended_at = timezone.now()
            self.duration = self.ended_at - self.started_at
            self.save()


class OnboardingTip(models.Model):
    """Contextual tips and help content"""
    
    TIP_TYPES = [
        ('welcome', 'Welcome Tips'),
        ('navigation', 'Navigation Help'),
        ('feature', 'Feature Introduction'),
        ('workflow', 'Workflow Guidance'),
        ('best_practice', 'Best Practices'),
        ('troubleshooting', 'Troubleshooting'),
    ]
    
    TRIGGER_CONDITIONS = [
        ('page_load', 'On Page Load'),
        ('first_visit', 'First Visit to Page'),
        ('idle_time', 'After Idle Time'),
        ('error_state', 'On Error'),
        ('feature_hover', 'On Feature Hover'),
        ('manual', 'Manual Trigger'),
    ]
    
    title = models.CharField(max_length=200)
    content = models.TextField()
    tip_type = models.CharField(max_length=20, choices=TIP_TYPES, default='feature')
    
    # Targeting
    target_page = models.CharField(max_length=100, help_text="URL pattern or page identifier")
    target_element = models.CharField(max_length=100, blank=True, help_text="CSS selector for target element")
    trigger_condition = models.CharField(max_length=20, choices=TRIGGER_CONDITIONS, default='page_load')
    
    # Display settings
    position = models.CharField(max_length=20, choices=[
        ('top', 'Top'),
        ('bottom', 'Bottom'),
        ('left', 'Left'),
        ('right', 'Right'),
        ('center', 'Center'),
        ('auto', 'Auto'),
    ], default='auto')
    
    priority = models.IntegerField(default=1, help_text="Higher numbers show first")
    
    # Status
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Analytics
    view_count = models.IntegerField(default=0)
    dismiss_count = models.IntegerField(default=0)
    action_count = models.IntegerField(default=0)
    
    class Meta:
        ordering = ['-priority', 'created_at']
    
    def __str__(self):
        return f"{self.title} ({self.target_page})"


class UserPreference(models.Model):
    """User onboarding and tutorial preferences"""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='onboarding_preferences')
    
    # Tutorial preferences
    show_tooltips = models.BooleanField(default=True)
    show_guided_tours = models.BooleanField(default=True)
    show_progress_tracker = models.BooleanField(default=True)
    show_achievements = models.BooleanField(default=True)
    
    # Notification preferences
    email_onboarding_tips = models.BooleanField(default=True)
    email_achievement_notifications = models.BooleanField(default=True)
    email_feature_updates = models.BooleanField(default=True)
    
    # Advanced settings
    preferred_learning_style = models.CharField(max_length=20, choices=[
        ('visual', 'Visual Learner'),
        ('hands_on', 'Hands-on Learner'),
        ('reading', 'Reading Learner'),
        ('minimal', 'Minimal Guidance'),
    ], default='visual')
    
    tutorial_pace = models.CharField(max_length=20, choices=[
        ('slow', 'Slow and Detailed'),
        ('medium', 'Medium Pace'),
        ('fast', 'Quick Overview'),
        ('custom', 'Let Me Control'),
    ], default='medium')
    
    # Metadata
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username} preferences"