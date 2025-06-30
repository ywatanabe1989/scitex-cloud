from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from django.utils import timezone
from datetime import date, timedelta
import uuid

from .models import (
    AIModel, ResearchProject, AISession, AIInteraction, ResearchSuggestion,
    LiteratureAnalysis, MethodologyRecommendation, StatisticalGuidance,
    WritingAssistance, TrendAnalysis, PersonalizedRecommendation,
    CitationSuggestion, AIUsageStatistics, AIModelConfig
)
from .services import AIResearchService


class AIAssistantModelTests(TestCase):
    """Test AI Assistant models."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.ai_model = AIModel.objects.create(
            name='Test GPT-4',
            model_type='openai_gpt4',
            max_tokens=4096,
            temperature=0.7,
            cost_per_1k_tokens=0.002,
            is_active=True,
            is_default=True
        )
        
        self.project = ResearchProject.objects.create(
            user=self.user,
            title='Test Research Project',
            description='A test research project',
            research_field='computer_science',
            keywords='AI, machine learning, testing',
            start_date=date.today()
        )
    
    def test_research_project_creation(self):
        """Test research project creation."""
        self.assertEqual(self.project.title, 'Test Research Project')
        self.assertEqual(self.project.user, self.user)
        self.assertEqual(self.project.status, 'planning')
        self.assertIsInstance(self.project.id, uuid.UUID)
    
    def test_ai_session_creation(self):
        """Test AI session creation."""
        session = AISession.objects.create(
            user=self.user,
            project=self.project,
            ai_model=self.ai_model,
            session_type='research_planning',
            title='Test Session'
        )
        
        self.assertEqual(session.user, self.user)
        self.assertEqual(session.project, self.project)
        self.assertTrue(session.is_active)
        self.assertEqual(session.total_interactions, 0)
    
    def test_ai_interaction_creation(self):
        """Test AI interaction creation."""
        session = AISession.objects.create(
            user=self.user,
            project=self.project,
            session_type='literature_analysis',
            title='Test Session'
        )
        
        interaction = AIInteraction.objects.create(
            session=session,
            interaction_type='query',
            user_prompt='What are the latest trends in AI?',
            ai_response='Recent trends include...',
            tokens_used=150,
            cost=0.0003
        )
        
        self.assertEqual(interaction.session, session)
        self.assertEqual(interaction.tokens_used, 150)
        self.assertEqual(float(interaction.cost), 0.0003)
    
    def test_research_suggestion_creation(self):
        """Test research suggestion creation."""
        suggestion = ResearchSuggestion.objects.create(
            user=self.user,
            project=self.project,
            suggestion_type='research_question',
            title='Test Suggestion',
            content='Consider exploring this research direction...',
            confidence_level='high',
            priority_score=0.8
        )
        
        self.assertEqual(suggestion.user, self.user)
        self.assertEqual(suggestion.status, 'pending')
        self.assertEqual(suggestion.priority_score, 0.8)
    
    def test_literature_analysis_creation(self):
        """Test literature analysis creation."""
        analysis = LiteratureAnalysis.objects.create(
            user=self.user,
            project=self.project,
            analysis_type='gap_analysis',
            title='Test Analysis',
            description='Analyzing literature gaps',
            search_query='AI ethics research'
        )
        
        self.assertEqual(analysis.status, 'processing')
        self.assertEqual(analysis.papers_analyzed, 0)
    
    def test_methodology_recommendation_creation(self):
        """Test methodology recommendation creation."""
        recommendation = MethodologyRecommendation.objects.create(
            user=self.user,
            project=self.project,
            title='Test Methodology',
            category='mixed_methods',
            description='Recommended methodology approach',
            research_context='Testing methodology recommendations'
        )
        
        self.assertEqual(recommendation.status, 'draft')
        self.assertEqual(recommendation.difficulty_level, 'intermediate')
    
    def test_ai_model_config_creation(self):
        """Test AI model configuration."""
        config = AIModelConfig.objects.create(
            user=self.user,
            preferred_model=self.ai_model,
            default_temperature=0.8,
            daily_token_limit=100000
        )
        
        self.assertEqual(config.user, self.user)
        self.assertEqual(config.preferred_model, self.ai_model)
        self.assertEqual(config.default_temperature, 0.8)


class AIServiceTests(TestCase):
    """Test AI research service functionality."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.ai_model = AIModel.objects.create(
            name='Test Model',
            model_type='openai_gpt35',
            max_tokens=2048,
            temperature=0.7,
            cost_per_1k_tokens=0.001,
            is_active=True,
            is_default=True
        )
        
        self.project = ResearchProject.objects.create(
            user=self.user,
            title='Test Project',
            description='Test description',
            research_field='computer_science',
            start_date=date.today()
        )
        
        self.service = AIResearchService()
    
    def test_get_user_ai_config(self):
        """Test getting user AI configuration."""
        config = self.service.get_user_ai_config(self.user)
        self.assertIsInstance(config, AIModelConfig)
        self.assertEqual(config.user, self.user)
    
    def test_get_default_ai_model(self):
        """Test getting default AI model."""
        model = self.service.get_default_ai_model(self.user)
        self.assertEqual(model, self.ai_model)
    
    def test_generate_research_suggestions(self):
        """Test research suggestion generation."""
        suggestions = self.service.generate_research_suggestions(
            user=self.user,
            project=self.project,
            context="Need help with research direction"
        )
        
        # Should create at least one suggestion
        self.assertGreaterEqual(len(suggestions), 1)
        
        if suggestions:
            suggestion = suggestions[0]
            self.assertEqual(suggestion.user, self.user)
            self.assertEqual(suggestion.project, self.project)


class AIAssistantViewTests(TestCase):
    """Test AI Assistant views."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.ai_model = AIModel.objects.create(
            name='Test Model',
            model_type='openai_gpt35',
            is_active=True,
            is_default=True
        )
        
        self.project = ResearchProject.objects.create(
            user=self.user,
            title='Test Project',
            description='Test description',
            research_field='computer_science',
            start_date=date.today()
        )
    
    def test_dashboard_view(self):
        """Test AI assistant dashboard view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_assistant:dashboard'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'AI Research Assistant')
    
    def test_project_list_view(self):
        """Test project list view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_assistant:project_list'))
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
    
    def test_project_detail_view(self):
        """Test project detail view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(
            reverse('ai_assistant:project_detail', kwargs={'pk': self.project.pk})
        )
        
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, self.project.title)
    
    def test_research_suggestions_view(self):
        """Test research suggestions view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_assistant:research_suggestions'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_literature_analysis_view(self):
        """Test literature analysis view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_assistant:literature_analysis'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_writing_assistance_view(self):
        """Test writing assistance view."""
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('ai_assistant:writing_assistance'))
        
        self.assertEqual(response.status_code, 200)
    
    def test_unauthorized_access(self):
        """Test that views require authentication."""
        response = self.client.get(reverse('ai_assistant:dashboard'))
        self.assertEqual(response.status_code, 302)  # Redirect to login


class AIUsageStatisticsTests(TestCase):
    """Test AI usage statistics tracking."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.today = timezone.now().date()
        self.month = self.today.strftime('%Y-%m')
    
    def test_usage_statistics_creation(self):
        """Test usage statistics creation."""
        stats = AIUsageStatistics.objects.create(
            user=self.user,
            date=self.today,
            month=self.month,
            total_sessions=5,
            total_interactions=25,
            total_tokens_used=5000,
            total_cost=0.50
        )
        
        self.assertEqual(stats.user, self.user)
        self.assertEqual(stats.total_sessions, 5)
        self.assertEqual(stats.total_interactions, 25)
        self.assertEqual(float(stats.total_cost), 0.50)
    
    def test_unique_user_date_constraint(self):
        """Test that only one stats record per user per date is allowed."""
        AIUsageStatistics.objects.create(
            user=self.user,
            date=self.today,
            month=self.month
        )
        
        # Creating another record for the same user and date should raise an error
        with self.assertRaises(Exception):
            AIUsageStatistics.objects.create(
                user=self.user,
                date=self.today,
                month=self.month
            )


class PersonalizedRecommendationTests(TestCase):
    """Test personalized recommendation system."""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_recommendation_creation(self):
        """Test personalized recommendation creation."""
        recommendation = PersonalizedRecommendation.objects.create(
            user=self.user,
            recommendation_type='paper_suggestion',
            title='Recommended Paper',
            description='This paper might interest you',
            reasoning='Based on your research interests',
            relevance_score=0.8,
            novelty_score=0.6,
            feasibility_score=0.9
        )
        
        self.assertEqual(recommendation.user, self.user)
        self.assertFalse(recommendation.viewed)
        self.assertFalse(recommendation.clicked)
        self.assertEqual(recommendation.priority_level, 'medium')
    
    def test_recommendation_ordering(self):
        """Test that recommendations are ordered by relevance and creation date."""
        rec1 = PersonalizedRecommendation.objects.create(
            user=self.user,
            recommendation_type='paper_suggestion',
            title='Low Relevance',
            description='Test',
            relevance_score=0.3
        )
        
        rec2 = PersonalizedRecommendation.objects.create(
            user=self.user,
            recommendation_type='paper_suggestion',
            title='High Relevance',
            description='Test',
            relevance_score=0.9
        )
        
        recommendations = PersonalizedRecommendation.objects.filter(user=self.user)
        self.assertEqual(recommendations.first(), rec2)  # Higher relevance first