import uuid
import json
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
# Use JSONField for SQLite compatibility instead of ArrayField


class AIModel(models.Model):
    """Configuration for different AI models used in research assistance."""
    
    MODEL_TYPES = [
        ('openai_gpt4', 'OpenAI GPT-4'),
        ('openai_gpt35', 'OpenAI GPT-3.5'),
        ('claude', 'Anthropic Claude'),
        ('local_llm', 'Local LLM'),
        ('custom', 'Custom Model'),
    ]
    
    MODEL_CAPABILITIES = [
        ('text_generation', 'Text Generation'),
        ('research_analysis', 'Research Analysis'),
        ('citation_analysis', 'Citation Analysis'),
        ('literature_review', 'Literature Review'),
        ('methodology_design', 'Methodology Design'),
        ('statistical_guidance', 'Statistical Guidance'),
        ('writing_assistance', 'Writing Assistance'),
        ('trend_analysis', 'Trend Analysis'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    model_type = models.CharField(max_length=20, choices=MODEL_TYPES)
    api_endpoint = models.URLField(blank=True)
    api_key_required = models.BooleanField(default=True)
    
    # Model configuration
    max_tokens = models.IntegerField(default=4096)
    temperature = models.FloatField(default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(2.0)])
    cost_per_1k_tokens = models.DecimalField(max_digits=6, decimal_places=4, default=0.002)
    
    # Capabilities
    capabilities = models.JSONField(default=list)  # List of MODEL_CAPABILITIES
    
    # Status
    is_active = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    
    # Metadata
    description = models.TextField(blank=True)
    version = models.CharField(max_length=50, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.get_model_type_display()})"


class ResearchProject(models.Model):
    """Research projects for organizing AI assistance context."""
    
    PROJECT_STATUS = [
        ('planning', 'Planning'),
        ('literature_review', 'Literature Review'),
        ('methodology', 'Methodology Design'),
        ('data_collection', 'Data Collection'),
        ('analysis', 'Analysis'),
        ('writing', 'Writing'),
        ('revision', 'Revision'),
        ('submitted', 'Submitted'),
        ('published', 'Published'),
        ('completed', 'Completed'),
        ('paused', 'Paused'),
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
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_projects')
    
    # Basic information
    title = models.CharField(max_length=500)
    description = models.TextField()
    research_field = models.CharField(max_length=30, choices=RESEARCH_FIELDS)
    keywords = models.TextField(blank=True, help_text="Comma-separated keywords")
    
    # Status and timeline
    status = models.CharField(max_length=20, choices=PROJECT_STATUS, default='planning')
    start_date = models.DateField()
    target_completion = models.DateField(null=True, blank=True)
    actual_completion = models.DateField(null=True, blank=True)
    
    # Research context
    research_questions = models.TextField(blank=True, help_text="Primary research questions")
    hypotheses = models.TextField(blank=True, help_text="Research hypotheses")
    methodology_notes = models.TextField(blank=True)
    
    # Integration with other modules
    scholar_papers = models.ManyToManyField('scholar_app.SearchIndex', blank=True, related_name='ai_projects')
    writer_manuscripts = models.ManyToManyField('writer_app.Manuscript', blank=True, related_name='ai_projects')
    
    # AI assistance tracking
    ai_sessions_count = models.IntegerField(default=0)
    total_ai_interactions = models.IntegerField(default=0)
    ai_cost_accumulated = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    
    # Collaboration
    collaborators = models.ManyToManyField(User, related_name='shared_research_projects', blank=True)
    is_public = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return self.title
    
    def get_keywords_list(self):
        """Return keywords as a list."""
        if self.keywords:
            return [kw.strip() for kw in self.keywords.split(',') if kw.strip()]
        return []


class AISession(models.Model):
    """Track AI assistance sessions for research projects."""
    
    SESSION_TYPES = [
        ('research_planning', 'Research Planning'),
        ('literature_analysis', 'Literature Analysis'),
        ('methodology_design', 'Methodology Design'),
        ('data_analysis_guidance', 'Data Analysis Guidance'),
        ('writing_assistance', 'Writing Assistance'),
        ('citation_suggestion', 'Citation Suggestion'),
        ('trend_analysis', 'Trend Analysis'),
        ('general_consultation', 'General Consultation'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_sessions')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='ai_sessions', null=True, blank=True)
    ai_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True)
    
    # Session details
    session_type = models.CharField(max_length=30, choices=SESSION_TYPES)
    title = models.CharField(max_length=200)
    context = models.TextField(blank=True, help_text="Research context provided to AI")
    
    # Session metrics
    total_interactions = models.IntegerField(default=0)
    total_tokens_used = models.IntegerField(default=0)
    total_cost = models.DecimalField(max_digits=8, decimal_places=4, default=0.0000)
    session_duration = models.DurationField(null=True, blank=True)
    
    # Session status
    is_active = models.BooleanField(default=True)
    
    # Integration tracking
    scholar_papers_referenced = models.ManyToManyField('scholar_app.SearchIndex', blank=True)
    writer_sections_assisted = models.ManyToManyField('writer_app.ManuscriptSection', blank=True)
    
    started_at = models.DateTimeField(auto_now_add=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    last_activity = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-started_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def end_session(self):
        """End the AI session."""
        self.is_active = False
        self.ended_at = timezone.now()
        if self.started_at:
            self.session_duration = self.ended_at - self.started_at
        self.save()


class AIInteraction(models.Model):
    """Individual AI interactions within sessions."""
    
    INTERACTION_TYPES = [
        ('query', 'Research Query'),
        ('suggestion_request', 'Suggestion Request'),
        ('analysis_request', 'Analysis Request'),
        ('writing_help', 'Writing Help'),
        ('citation_search', 'Citation Search'),
        ('methodology_advice', 'Methodology Advice'),
        ('statistical_guidance', 'Statistical Guidance'),
        ('trend_prediction', 'Trend Prediction'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(AISession, on_delete=models.CASCADE, related_name='interactions')
    
    # Interaction details
    interaction_type = models.CharField(max_length=30, choices=INTERACTION_TYPES)
    user_prompt = models.TextField(help_text="User's input/question")
    ai_response = models.TextField(help_text="AI's response")
    
    # Context and metadata
    context_data = models.JSONField(default=dict, blank=True)  # Additional context provided
    response_metadata = models.JSONField(default=dict, blank=True)  # AI model metadata
    
    # Metrics
    tokens_used = models.IntegerField(default=0)
    response_time_seconds = models.FloatField(null=True, blank=True)
    cost = models.DecimalField(max_digits=6, decimal_places=4, default=0.0000)
    
    # Quality and feedback
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="User rating 1-5"
    )
    user_feedback = models.TextField(blank=True)
    is_helpful = models.BooleanField(null=True, blank=True)
    
    # Actions taken
    implemented = models.BooleanField(default=False, help_text="Whether user implemented the suggestion")
    follow_up_needed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_interaction_type_display()} - {self.session.title}"


class ResearchSuggestion(models.Model):
    """AI-generated research suggestions and recommendations."""
    
    SUGGESTION_TYPES = [
        ('research_question', 'Research Question'),
        ('methodology', 'Methodology'),
        ('literature_gap', 'Literature Gap'),
        ('analysis_approach', 'Analysis Approach'),
        ('writing_improvement', 'Writing Improvement'),
        ('citation_recommendation', 'Citation Recommendation'),
        ('trend_insight', 'Trend Insight'),
        ('collaboration_opportunity', 'Collaboration Opportunity'),
    ]
    
    CONFIDENCE_LEVELS = [
        ('low', 'Low Confidence'),
        ('medium', 'Medium Confidence'),
        ('high', 'High Confidence'),
        ('very_high', 'Very High Confidence'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='research_suggestions')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='suggestions', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Suggestion content
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPES)
    title = models.CharField(max_length=200)
    content = models.TextField()
    reasoning = models.TextField(blank=True, help_text="AI's reasoning for this suggestion")
    
    # Confidence and priority
    confidence_level = models.CharField(max_length=10, choices=CONFIDENCE_LEVELS)
    priority_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Evidence and sources
    supporting_evidence = models.JSONField(default=list, blank=True)  # References, data points, etc.
    related_papers = models.ManyToManyField('scholar_app.SearchIndex', blank=True)
    
    # User response
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('implemented', 'Implemented'),
        ('deferred', 'Deferred'),
    ], default='pending')
    
    user_notes = models.TextField(blank=True)
    implementation_date = models.DateTimeField(null=True, blank=True)
    
    # Metadata
    tags = models.CharField(max_length=500, blank=True, help_text="Comma-separated tags")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_suggestion_type_display()})"


class LiteratureAnalysis(models.Model):
    """AI-powered literature analysis results."""
    
    ANALYSIS_TYPES = [
        ('gap_analysis', 'Literature Gap Analysis'),
        ('trend_analysis', 'Research Trend Analysis'),
        ('citation_network', 'Citation Network Analysis'),
        ('methodology_comparison', 'Methodology Comparison'),
        ('thematic_analysis', 'Thematic Analysis'),
        ('quality_assessment', 'Quality Assessment'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='literature_analyses')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='literature_analyses', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analysis details
    analysis_type = models.CharField(max_length=30, choices=ANALYSIS_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    
    # Input data
    analyzed_papers = models.ManyToManyField('scholar_app.SearchIndex', related_name='ai_analyses')
    search_query = models.TextField(blank=True, help_text="Original search query")
    analysis_parameters = models.JSONField(default=dict, blank=True)
    
    # Results
    key_findings = models.JSONField(default=list, blank=True)
    identified_gaps = models.JSONField(default=list, blank=True)
    research_trends = models.JSONField(default=list, blank=True)
    methodology_insights = models.JSONField(default=dict, blank=True)
    
    # Visualizations and reports
    summary_report = models.TextField(blank=True)
    visualization_data = models.JSONField(default=dict, blank=True)
    
    # Metrics
    papers_analyzed = models.IntegerField(default=0)
    confidence_score = models.FloatField(default=0.0, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    processing_time_seconds = models.FloatField(null=True, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=[
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ], default='processing')
    
    # User interaction
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user_feedback = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_analysis_type_display()})"


class MethodologyRecommendation(models.Model):
    """AI-generated methodology recommendations."""
    
    METHODOLOGY_CATEGORIES = [
        ('quantitative', 'Quantitative Research'),
        ('qualitative', 'Qualitative Research'),
        ('mixed_methods', 'Mixed Methods'),
        ('experimental', 'Experimental Design'),
        ('observational', 'Observational Study'),
        ('computational', 'Computational Methods'),
        ('theoretical', 'Theoretical Framework'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='methodology_recommendations')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='methodology_recommendations')
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Recommendation details
    title = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=METHODOLOGY_CATEGORIES)
    description = models.TextField()
    detailed_steps = models.JSONField(default=list, blank=True)
    
    # Context and rationale
    research_context = models.TextField(help_text="Research context considered")
    rationale = models.TextField(help_text="Why this methodology is recommended")
    assumptions = models.JSONField(default=list, blank=True)
    
    # Implementation guidance
    required_resources = models.JSONField(default=list, blank=True)
    estimated_timeline = models.CharField(max_length=100, blank=True)
    difficulty_level = models.CharField(max_length=20, choices=[
        ('beginner', 'Beginner'),
        ('intermediate', 'Intermediate'),
        ('advanced', 'Advanced'),
        ('expert', 'Expert'),
    ], default='intermediate')
    
    # Quality and validation
    statistical_considerations = models.TextField(blank=True)
    potential_limitations = models.JSONField(default=list, blank=True)
    validation_approaches = models.JSONField(default=list, blank=True)
    
    # References and examples
    supporting_literature = models.ManyToManyField('scholar_app.SearchIndex', blank=True)
    example_studies = models.JSONField(default=list, blank=True)
    
    # User feedback
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('accepted', 'Accepted'),
        ('implemented', 'Implemented'),
        ('rejected', 'Rejected'),
    ], default='draft')
    
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    implementation_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.project.title}"


class StatisticalGuidance(models.Model):
    """AI-powered statistical analysis guidance."""
    
    ANALYSIS_TYPES = [
        ('descriptive', 'Descriptive Statistics'),
        ('inferential', 'Inferential Statistics'),
        ('regression', 'Regression Analysis'),
        ('anova', 'ANOVA'),
        ('time_series', 'Time Series Analysis'),
        ('machine_learning', 'Machine Learning'),
        ('bayesian', 'Bayesian Analysis'),
        ('non_parametric', 'Non-parametric Tests'),
        ('multivariate', 'Multivariate Analysis'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='statistical_guidance')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='statistical_guidance', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analysis context
    analysis_type = models.CharField(max_length=20, choices=ANALYSIS_TYPES)
    research_question = models.TextField()
    data_description = models.TextField()
    
    # Recommendations
    recommended_tests = models.JSONField(default=list, blank=True)
    assumptions_to_check = models.JSONField(default=list, blank=True)
    sample_size_guidance = models.TextField(blank=True)
    effect_size_considerations = models.TextField(blank=True)
    
    # Implementation details
    software_recommendations = models.JSONField(default=list, blank=True)
    code_examples = models.JSONField(default=dict, blank=True)  # Language -> code
    interpretation_guidance = models.TextField(blank=True)
    
    # Reporting guidance
    reporting_checklist = models.JSONField(default=list, blank=True)
    visualization_suggestions = models.JSONField(default=list, blank=True)
    
    # Quality considerations
    power_analysis_notes = models.TextField(blank=True)
    potential_confounders = models.JSONField(default=list, blank=True)
    limitation_notes = models.TextField(blank=True)
    
    # User feedback
    status = models.CharField(max_length=20, choices=[
        ('draft', 'Draft'),
        ('reviewed', 'Reviewed'),
        ('implemented', 'Implemented'),
        ('needs_revision', 'Needs Revision'),
    ], default='draft')
    
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    implementation_results = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Statistical Guidance: {self.get_analysis_type_display()}"


class WritingAssistance(models.Model):
    """AI-powered writing improvement suggestions."""
    
    ASSISTANCE_TYPES = [
        ('structure', 'Structure Improvement'),
        ('clarity', 'Clarity Enhancement'),
        ('flow', 'Flow and Transitions'),
        ('tone', 'Tone Adjustment'),
        ('conciseness', 'Conciseness'),
        ('argument', 'Argument Strengthening'),
        ('evidence', 'Evidence Integration'),
        ('formatting', 'Formatting and Style'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='writing_assistance')
    manuscript = models.ForeignKey('writer_app.Manuscript', on_delete=models.CASCADE, related_name='ai_assistance', null=True, blank=True)
    section = models.ForeignKey('writer_app.ManuscriptSection', on_delete=models.CASCADE, related_name='ai_assistance', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Content context
    assistance_type = models.CharField(max_length=20, choices=ASSISTANCE_TYPES)
    original_text = models.TextField()
    target_audience = models.CharField(max_length=100, blank=True)
    target_journal = models.CharField(max_length=200, blank=True)
    
    # Suggestions
    suggested_revisions = models.JSONField(default=list, blank=True)
    overall_feedback = models.TextField()
    specific_improvements = models.JSONField(default=list, blank=True)
    
    # Style and tone guidance
    tone_suggestions = models.TextField(blank=True)
    style_recommendations = models.TextField(blank=True)
    word_choice_improvements = models.JSONField(default=list, blank=True)
    
    # Structure recommendations
    organization_feedback = models.TextField(blank=True)
    paragraph_suggestions = models.JSONField(default=list, blank=True)
    transition_improvements = models.JSONField(default=list, blank=True)
    
    # Citation and evidence
    citation_suggestions = models.JSONField(default=list, blank=True)
    evidence_strengthening = models.TextField(blank=True)
    
    # Revised version
    suggested_rewrite = models.TextField(blank=True)
    
    # User response
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('partially_accepted', 'Partially Accepted'),
        ('fully_accepted', 'Fully Accepted'),
        ('rejected', 'Rejected'),
        ('needs_clarification', 'Needs Clarification'),
    ], default='pending')
    
    user_feedback = models.TextField(blank=True)
    accepted_suggestions = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Writing Assistance: {self.get_assistance_type_display()}"


class TrendAnalysis(models.Model):
    """AI-powered research trend analysis and predictions."""
    
    TREND_TYPES = [
        ('emerging_topics', 'Emerging Research Topics'),
        ('methodology_trends', 'Methodology Trends'),
        ('citation_patterns', 'Citation Patterns'),
        ('collaboration_networks', 'Collaboration Networks'),
        ('funding_trends', 'Funding Trends'),
        ('publication_patterns', 'Publication Patterns'),
        ('interdisciplinary_growth', 'Interdisciplinary Growth'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='trend_analyses')
    project = models.ForeignKey(ResearchProject, on_delete=models.CASCADE, related_name='trend_analyses', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Analysis scope
    trend_type = models.CharField(max_length=30, choices=TREND_TYPES)
    research_field = models.CharField(max_length=30, choices=ResearchProject.RESEARCH_FIELDS)
    time_period = models.CharField(max_length=50, help_text="e.g., '2020-2024', 'Last 5 years'")
    
    # Input data
    data_sources = models.JSONField(default=list, blank=True)
    analysis_parameters = models.JSONField(default=dict, blank=True)
    keywords_analyzed = models.TextField(blank=True)
    
    # Results
    identified_trends = models.JSONField(default=list, blank=True)
    trend_predictions = models.JSONField(default=list, blank=True)
    statistical_insights = models.JSONField(default=dict, blank=True)
    
    # Visualizations
    trend_charts = models.JSONField(default=dict, blank=True)
    network_analysis = models.JSONField(default=dict, blank=True)
    
    # Impact assessment
    potential_impact = models.TextField(blank=True)
    research_opportunities = models.JSONField(default=list, blank=True)
    collaboration_suggestions = models.JSONField(default=list, blank=True)
    
    # Quality metrics
    confidence_level = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    data_quality_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # Analysis metadata
    papers_analyzed = models.IntegerField(default=0)
    processing_time_minutes = models.FloatField(null=True, blank=True)
    
    # User feedback
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    actionability_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user_notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Trend Analysis: {self.get_trend_type_display()} in {self.research_field}"


class PersonalizedRecommendation(models.Model):
    """Personalized research recommendations based on user behavior and preferences."""
    
    RECOMMENDATION_TYPES = [
        ('paper_suggestion', 'Paper Suggestion'),
        ('collaboration_opportunity', 'Collaboration Opportunity'),
        ('methodology_suggestion', 'Methodology Suggestion'),
        ('tool_recommendation', 'Tool Recommendation'),
        ('conference_suggestion', 'Conference Suggestion'),
        ('journal_recommendation', 'Journal Recommendation'),
        ('skill_development', 'Skill Development'),
        ('research_direction', 'Research Direction'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='personalized_recommendations')
    
    # Recommendation details
    recommendation_type = models.CharField(max_length=30, choices=RECOMMENDATION_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField()
    reasoning = models.TextField(help_text="Why this is recommended for the user")
    
    # Personalization factors
    user_interests = models.JSONField(default=list, blank=True)
    behavioral_patterns = models.JSONField(default=dict, blank=True)
    research_history = models.JSONField(default=dict, blank=True)
    
    # Recommendation content
    recommended_items = models.JSONField(default=list, blank=True)  # Papers, tools, etc.
    action_items = models.JSONField(default=list, blank=True)
    resources = models.JSONField(default=list, blank=True)
    
    # Scoring and ranking
    relevance_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    novelty_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    feasibility_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # User interaction
    viewed = models.BooleanField(default=False)
    clicked = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)
    saved = models.BooleanField(default=False)
    
    user_rating = models.IntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    user_feedback = models.TextField(blank=True)
    
    # Timing and expiry
    priority_level = models.CharField(max_length=10, choices=[
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ], default='medium')
    
    expires_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    viewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-relevance_score', '-created_at']
    
    def __str__(self):
        return f"{self.title} ({self.get_recommendation_type_display()})"


class CitationSuggestion(models.Model):
    """AI-powered citation suggestions for manuscripts."""
    
    SUGGESTION_TYPES = [
        ('missing_reference', 'Missing Reference'),
        ('supporting_evidence', 'Supporting Evidence'),
        ('contrasting_view', 'Contrasting View'),
        ('methodology_reference', 'Methodology Reference'),
        ('recent_development', 'Recent Development'),
        ('foundational_work', 'Foundational Work'),
        ('similar_study', 'Similar Study'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='citation_suggestions')
    manuscript = models.ForeignKey('writer_app.Manuscript', on_delete=models.CASCADE, related_name='citation_suggestions', null=True, blank=True)
    section = models.ForeignKey('writer_app.ManuscriptSection', on_delete=models.CASCADE, related_name='citation_suggestions', null=True, blank=True)
    ai_interaction = models.ForeignKey(AIInteraction, on_delete=models.SET_NULL, null=True, blank=True)
    
    # Suggestion context
    suggestion_type = models.CharField(max_length=30, choices=SUGGESTION_TYPES)
    text_context = models.TextField(help_text="Text where citation should be added")
    position_in_text = models.IntegerField(null=True, blank=True)
    
    # Suggested paper
    suggested_paper = models.ForeignKey('scholar_app.SearchIndex', on_delete=models.CASCADE, related_name='citation_suggestions')
    relevance_explanation = models.TextField()
    
    # Citation details
    suggested_citation_text = models.TextField(blank=True)
    citation_style = models.CharField(max_length=20, default='apa')
    
    # Confidence and ranking
    confidence_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    relevance_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    novelty_score = models.FloatField(default=0.5, validators=[MinValueValidator(0.0), MaxValueValidator(1.0)])
    
    # User response
    status = models.CharField(max_length=20, choices=[
        ('pending', 'Pending Review'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
        ('modified', 'Modified'),
        ('already_cited', 'Already Cited'),
    ], default='pending')
    
    user_notes = models.TextField(blank=True)
    implemented_citation = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-relevance_score', '-created_at']
    
    def __str__(self):
        return f"Citation suggestion: {self.suggested_paper.title[:50]}..."


class AIUsageStatistics(models.Model):
    """Track AI usage statistics for billing and analytics."""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='ai_usage_stats')
    
    # Usage metrics
    total_sessions = models.IntegerField(default=0)
    total_interactions = models.IntegerField(default=0)
    total_tokens_used = models.BigIntegerField(default=0)
    total_cost = models.DecimalField(max_digits=10, decimal_places=4, default=0.0000)
    
    # Feature usage
    research_suggestions_generated = models.IntegerField(default=0)
    literature_analyses_performed = models.IntegerField(default=0)
    methodology_recommendations_given = models.IntegerField(default=0)
    writing_assistance_sessions = models.IntegerField(default=0)
    citation_suggestions_made = models.IntegerField(default=0)
    trend_analyses_performed = models.IntegerField(default=0)
    
    # Quality metrics
    average_user_rating = models.FloatField(null=True, blank=True)
    total_positive_feedback = models.IntegerField(default=0)
    total_negative_feedback = models.IntegerField(default=0)
    suggestions_implemented = models.IntegerField(default=0)
    
    # Time period
    date = models.DateField()
    month = models.CharField(max_length=7)  # YYYY-MM format
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"AI Usage: {self.user.username} - {self.date}"


class AIModelConfig(models.Model):
    """User-specific AI model configurations and preferences."""
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='ai_config')
    
    # Default model preferences
    preferred_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, related_name='preferred_by_users')
    backup_model = models.ForeignKey(AIModel, on_delete=models.SET_NULL, null=True, related_name='backup_for_users')
    
    # Generation parameters
    default_temperature = models.FloatField(default=0.7, validators=[MinValueValidator(0.0), MaxValueValidator(2.0)])
    default_max_tokens = models.IntegerField(default=2048)
    
    # User preferences
    response_style = models.CharField(max_length=20, choices=[
        ('concise', 'Concise'),
        ('detailed', 'Detailed'),
        ('academic', 'Academic'),
        ('conversational', 'Conversational'),
    ], default='academic')
    
    # API keys (encrypted)
    openai_api_key = models.CharField(max_length=500, blank=True, help_text="Encrypted OpenAI API key")
    claude_api_key = models.CharField(max_length=500, blank=True, help_text="Encrypted Claude API key")
    
    # Usage limits
    daily_token_limit = models.IntegerField(default=50000)
    monthly_cost_limit = models.DecimalField(max_digits=8, decimal_places=2, default=100.00)
    
    # Notification preferences
    notify_on_suggestions = models.BooleanField(default=True)
    notify_on_analysis_completion = models.BooleanField(default=True)
    email_summaries = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"AI Config: {self.user.username}"