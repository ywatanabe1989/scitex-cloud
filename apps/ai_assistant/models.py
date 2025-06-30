#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
AI Research Assistant Models
Database models for AI-powered research assistance features
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ResearchQuery(models.Model):
    """Model to store research queries and AI responses"""
    
    QUERY_TYPES = [
        ('question_suggestion', 'Research Question Suggestion'),
        ('literature_gap', 'Literature Gap Analysis'),
        ('methodology', 'Methodology Recommendation'),
        ('statistical_guidance', 'Statistical Analysis Guidance'),
        ('writing_improvement', 'Writing Improvement'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    query_type = models.CharField(max_length=50, choices=QUERY_TYPES)
    input_text = models.TextField(help_text="User's input text or research content")
    context_data = models.JSONField(
        default=dict, 
        help_text="Additional context like research field, methodology, etc."
    )
    ai_response = models.TextField(help_text="AI-generated response")
    feedback_rating = models.IntegerField(
        null=True, blank=True,
        help_text="User feedback rating (1-5)"
    )
    feedback_text = models.TextField(blank=True, help_text="User feedback comments")
    is_helpful = models.BooleanField(null=True, blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Research Query'
        verbose_name_plural = 'Research Queries'
    
    def __str__(self):
        return f"{self.get_query_type_display()} - {self.user.username}"


class ResearchSuggestion(models.Model):
    """Model to store AI-generated research suggestions"""
    
    SUGGESTION_TYPES = [
        ('research_question', 'Research Question'),
        ('hypothesis', 'Hypothesis'),
        ('methodology', 'Methodology'),
        ('analysis_approach', 'Analysis Approach'),
        ('literature_source', 'Literature Source'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    suggestion_type = models.CharField(max_length=50, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    confidence_score = models.FloatField(
        help_text="AI confidence score (0.0-1.0)"
    )
    relevance_tags = models.JSONField(
        default=list,
        help_text="Tags for categorizing suggestion relevance"
    )
    
    # Relationships
    related_query = models.ForeignKey(
        ResearchQuery, 
        on_delete=models.CASCADE, 
        null=True, 
        blank=True,
        related_name='suggestions'
    )
    
    # User interaction
    is_bookmarked = models.BooleanField(default=False)
    is_implemented = models.BooleanField(default=False)
    user_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-confidence_score', '-created_at']
        verbose_name = 'Research Suggestion'
        verbose_name_plural = 'Research Suggestions'
    
    def __str__(self):
        return f"{self.title} ({self.get_suggestion_type_display()})"


class ResearchGap(models.Model):
    """Model to store identified literature gaps"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    research_area = models.CharField(max_length=200)
    gap_description = models.TextField()
    potential_impact = models.TextField(help_text="Potential impact of addressing this gap")
    suggested_approaches = models.JSONField(
        default=list,
        help_text="AI-suggested approaches to address the gap"
    )
    related_papers = models.JSONField(
        default=list,
        help_text="Related papers that highlight this gap"
    )
    
    # AI analysis metadata
    confidence_level = models.CharField(
        max_length=20,
        choices=[
            ('high', 'High Confidence'),
            ('medium', 'Medium Confidence'),
            ('low', 'Low Confidence'),
        ],
        default='medium'
    )
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Research Gap'
        verbose_name_plural = 'Research Gaps'
    
    def __str__(self):
        return f"Gap in {self.research_area}"


class AIAssistantSession(models.Model):
    """Model to track AI assistant conversation sessions"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    session_name = models.CharField(max_length=200, default="Research Session")
    conversation_history = models.JSONField(
        default=list,
        help_text="Full conversation history with AI assistant"
    )
    research_context = models.JSONField(
        default=dict,
        help_text="Research context and metadata"
    )
    
    # Session metadata
    total_queries = models.IntegerField(default=0)
    avg_satisfaction = models.FloatField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    last_activity = models.DateTimeField(default=timezone.now)
    
    class Meta:
        ordering = ['-last_activity']
        verbose_name = 'AI Assistant Session'
        verbose_name_plural = 'AI Assistant Sessions'
    
    def __str__(self):
        return f"{self.session_name} - {self.user.username}"
    
    def add_conversation_turn(self, user_message, ai_response, query_type=None):
        """Add a new conversation turn to the session"""
        turn = {
            'timestamp': timezone.now().isoformat(),
            'user_message': user_message,
            'ai_response': ai_response,
            'query_type': query_type,
        }
        self.conversation_history.append(turn)
        self.total_queries += 1
        self.last_activity = timezone.now()
        self.save()