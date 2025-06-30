"""
Admin interface for onboarding system
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import (
    OnboardingProgress, UserAchievement, OnboardingTemplate,
    OnboardingSession, OnboardingTip, UserPreference
)


@admin.register(OnboardingProgress)
class OnboardingProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'current_step', 'completion_percentage', 'session_count', 'last_activity_at', 'is_completed')
    list_filter = ('current_step', 'completion_percentage', 'show_tips')
    search_fields = ('user__username', 'user__email')
    readonly_fields = ('started_at', 'last_activity_at', 'completed_at')
    
    fieldsets = (
        ('User Info', {
            'fields': ('user', 'current_step', 'completion_percentage')
        }),
        ('Progress Tracking', {
            'fields': ('completed_steps', 'started_at', 'last_activity_at', 'completed_at')
        }),
        ('Preferences', {
            'fields': ('show_tips',)
        }),
        ('Engagement', {
            'fields': ('session_count', 'total_time_spent')
        }),
    )
    
    def is_completed(self, obj):
        return obj.is_completed()
    is_completed.boolean = True
    is_completed.short_description = 'Completed'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'title', 'achievement_type', 'category', 'points', 'earned_at', 'is_featured')
    list_filter = ('achievement_type', 'category', 'is_visible', 'is_featured', 'earned_at')
    search_fields = ('user__username', 'title', 'description')
    readonly_fields = ('earned_at',)
    
    fieldsets = (
        ('Achievement Info', {
            'fields': ('user', 'achievement_type', 'category', 'title', 'description')
        }),
        ('Display', {
            'fields': ('icon', 'points', 'is_visible', 'is_featured')
        }),
        ('Metadata', {
            'fields': ('metadata', 'earned_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OnboardingTemplate)
class OnboardingTemplateAdmin(admin.ModelAdmin):
    list_display = ('name', 'template_type', 'research_field', 'difficulty_level', 'usage_count', 'is_active')
    list_filter = ('template_type', 'research_field', 'difficulty_level', 'is_active')
    search_fields = ('name', 'description')
    readonly_fields = ('usage_count', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Template Info', {
            'fields': ('name', 'description', 'template_type', 'research_field')
        }),
        ('Content', {
            'fields': ('project_structure', 'sample_content', 'guided_steps'),
            'classes': ('collapse',)
        }),
        ('Settings', {
            'fields': ('difficulty_level', 'estimated_time', 'is_active')
        }),
        ('Usage Stats', {
            'fields': ('usage_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(OnboardingSession)
class OnboardingSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'session_type', 'started_at', 'duration_display', 'pages_count', 'satisfaction_rating')
    list_filter = ('session_type', 'satisfaction_rating', 'started_at')
    search_fields = ('user__username', 'feedback')
    readonly_fields = ('started_at', 'ended_at', 'duration')
    
    fieldsets = (
        ('Session Info', {
            'fields': ('user', 'session_type', 'started_at', 'ended_at', 'duration')
        }),
        ('Activity', {
            'fields': ('pages_visited', 'actions_taken', 'features_explored'),
            'classes': ('collapse',)
        }),
        ('Outcomes', {
            'fields': ('completed_steps', 'achievements_earned')
        }),
        ('Feedback', {
            'fields': ('satisfaction_rating', 'feedback')
        }),
    )
    
    def duration_display(self, obj):
        if obj.duration:
            return str(obj.duration)
        return "Ongoing"
    duration_display.short_description = 'Duration'
    
    def pages_count(self, obj):
        return len(obj.pages_visited)
    pages_count.short_description = 'Pages Visited'


@admin.register(OnboardingTip)
class OnboardingTipAdmin(admin.ModelAdmin):
    list_display = ('title', 'tip_type', 'target_page', 'trigger_condition', 'priority', 'view_count', 'is_active')
    list_filter = ('tip_type', 'trigger_condition', 'position', 'is_active')
    search_fields = ('title', 'content', 'target_page')
    readonly_fields = ('view_count', 'dismiss_count', 'action_count', 'created_at')
    
    fieldsets = (
        ('Tip Info', {
            'fields': ('title', 'content', 'tip_type')
        }),
        ('Targeting', {
            'fields': ('target_page', 'target_element', 'trigger_condition')
        }),
        ('Display', {
            'fields': ('position', 'priority', 'is_active')
        }),
        ('Analytics', {
            'fields': ('view_count', 'dismiss_count', 'action_count', 'created_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(UserPreference)
class UserPreferenceAdmin(admin.ModelAdmin):
    list_display = ('user', 'show_tooltips', 'show_guided_tours', 'preferred_learning_style', 'tutorial_pace', 'updated_at')
    list_filter = ('show_tooltips', 'show_guided_tours', 'preferred_learning_style', 'tutorial_pace')
    search_fields = ('user__username',)
    readonly_fields = ('updated_at',)
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Tutorial Preferences', {
            'fields': ('show_tooltips', 'show_guided_tours', 'show_progress_tracker', 'show_achievements')
        }),
        ('Notification Preferences', {
            'fields': ('email_onboarding_tips', 'email_achievement_notifications', 'email_feature_updates')
        }),
        ('Learning Style', {
            'fields': ('preferred_learning_style', 'tutorial_pace')
        }),
        ('Metadata', {
            'fields': ('updated_at',)
        }),
    )