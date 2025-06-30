from django.contrib import admin
from .models import (
    AIModel, ResearchProject, AISession, AIInteraction, ResearchSuggestion,
    LiteratureAnalysis, MethodologyRecommendation, StatisticalGuidance,
    WritingAssistance, TrendAnalysis, PersonalizedRecommendation,
    CitationSuggestion, AIUsageStatistics, AIModelConfig
)


@admin.register(AIModel)
class AIModelAdmin(admin.ModelAdmin):
    list_display = ['name', 'model_type', 'is_active', 'is_default', 'max_tokens', 'cost_per_1k_tokens']
    list_filter = ['model_type', 'is_active', 'is_default']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(ResearchProject)
class ResearchProjectAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'research_field', 'status', 'start_date', 'ai_sessions_count']
    list_filter = ['research_field', 'status', 'is_public']
    search_fields = ['title', 'description', 'keywords']
    filter_horizontal = ['collaborators', 'scholar_papers', 'writer_manuscripts']
    readonly_fields = ['created_at', 'updated_at', 'ai_sessions_count', 'total_ai_interactions', 'ai_cost_accumulated']
    date_hierarchy = 'created_at'


@admin.register(AISession)
class AISessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'session_type', 'total_interactions', 'total_cost', 'is_active', 'started_at']
    list_filter = ['session_type', 'is_active', 'ai_model']
    search_fields = ['title', 'user__username']
    filter_horizontal = ['scholar_papers_referenced', 'writer_sections_assisted']
    readonly_fields = ['started_at', 'ended_at', 'last_activity', 'session_duration']
    date_hierarchy = 'started_at'


@admin.register(AIInteraction)
class AIInteractionAdmin(admin.ModelAdmin):
    list_display = ['session', 'interaction_type', 'tokens_used', 'cost', 'user_rating', 'is_helpful', 'created_at']
    list_filter = ['interaction_type', 'user_rating', 'is_helpful', 'implemented']
    search_fields = ['user_prompt', 'ai_response', 'session__title']
    readonly_fields = ['created_at', 'response_time_seconds']
    date_hierarchy = 'created_at'


@admin.register(ResearchSuggestion)
class ResearchSuggestionAdmin(admin.ModelAdmin):
    list_display = ['title', 'suggestion_type', 'user', 'confidence_level', 'priority_score', 'status', 'created_at']
    list_filter = ['suggestion_type', 'confidence_level', 'status']
    search_fields = ['title', 'content', 'user__username']
    filter_horizontal = ['related_papers']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(LiteratureAnalysis)
class LiteratureAnalysisAdmin(admin.ModelAdmin):
    list_display = ['title', 'analysis_type', 'user', 'papers_analyzed', 'confidence_score', 'status', 'created_at']
    list_filter = ['analysis_type', 'status']
    search_fields = ['title', 'description', 'user__username']
    filter_horizontal = ['analyzed_papers']
    readonly_fields = ['created_at', 'completed_at', 'processing_time_seconds']
    date_hierarchy = 'created_at'


@admin.register(MethodologyRecommendation)
class MethodologyRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'category', 'project', 'difficulty_level', 'status', 'user_rating', 'created_at']
    list_filter = ['category', 'difficulty_level', 'status', 'user_rating']
    search_fields = ['title', 'description', 'project__title']
    filter_horizontal = ['supporting_literature']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(StatisticalGuidance)
class StatisticalGuidanceAdmin(admin.ModelAdmin):
    list_display = ['analysis_type', 'project', 'status', 'user_rating', 'created_at']
    list_filter = ['analysis_type', 'status', 'user_rating']
    search_fields = ['research_question', 'data_description', 'project__title']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(WritingAssistance)
class WritingAssistanceAdmin(admin.ModelAdmin):
    list_display = ['assistance_type', 'manuscript', 'section', 'status', 'created_at']
    list_filter = ['assistance_type', 'status']
    search_fields = ['manuscript__title', 'section__title', 'overall_feedback']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'


@admin.register(TrendAnalysis)
class TrendAnalysisAdmin(admin.ModelAdmin):
    list_display = ['trend_type', 'research_field', 'user', 'papers_analyzed', 'confidence_level', 'user_rating', 'created_at']
    list_filter = ['trend_type', 'research_field', 'user_rating']
    search_fields = ['keywords_analyzed', 'potential_impact']
    readonly_fields = ['created_at', 'completed_at', 'processing_time_minutes']
    date_hierarchy = 'created_at'


@admin.register(PersonalizedRecommendation)
class PersonalizedRecommendationAdmin(admin.ModelAdmin):
    list_display = ['title', 'recommendation_type', 'user', 'relevance_score', 'priority_level', 'viewed', 'saved', 'created_at']
    list_filter = ['recommendation_type', 'priority_level', 'viewed', 'clicked', 'dismissed', 'saved']
    search_fields = ['title', 'description', 'user__username']
    readonly_fields = ['created_at', 'viewed_at']
    date_hierarchy = 'created_at'


@admin.register(CitationSuggestion)
class CitationSuggestionAdmin(admin.ModelAdmin):
    list_display = ['suggestion_type', 'manuscript', 'suggested_paper', 'confidence_score', 'status', 'created_at']
    list_filter = ['suggestion_type', 'status']
    search_fields = ['text_context', 'relevance_explanation', 'manuscript__title']
    readonly_fields = ['created_at', 'reviewed_at']
    date_hierarchy = 'created_at'


@admin.register(AIUsageStatistics)
class AIUsageStatisticsAdmin(admin.ModelAdmin):
    list_display = ['user', 'date', 'total_sessions', 'total_interactions', 'total_cost', 'average_user_rating']
    list_filter = ['date', 'month']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'


@admin.register(AIModelConfig)
class AIModelConfigAdmin(admin.ModelAdmin):
    list_display = ['user', 'preferred_model', 'default_temperature', 'daily_token_limit', 'monthly_cost_limit']
    search_fields = ['user__username']
    readonly_fields = ['created_at', 'updated_at']