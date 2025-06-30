"""
AI Research Assistant Services
"""

import json
import logging
import openai
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from .models import (
    AIModel, ResearchProject, AISession, AIInteraction, ResearchSuggestion,
    LiteratureAnalysis, MethodologyRecommendation, StatisticalGuidance,
    WritingAssistance, TrendAnalysis, PersonalizedRecommendation,
    CitationSuggestion, AIUsageStatistics, AIModelConfig
)

logger = logging.getLogger(__name__)


class AIResearchService:
    """Main service class for AI research assistance."""
    
    def __init__(self):
        self.openai_client = None
        self._initialize_ai_clients()
    
    def _initialize_ai_clients(self):
        """Initialize AI service clients."""
        try:
            # Initialize OpenAI client if API key is available
            openai_key = getattr(settings, 'OPENAI_API_KEY', None)
            if openai_key:
                openai.api_key = openai_key
                self.openai_client = openai
        except Exception as e:
            logger.warning(f"Failed to initialize AI clients: {e}")
    
    def get_user_ai_config(self, user: User) -> AIModelConfig:
        """Get or create user's AI configuration."""
        config, created = AIModelConfig.objects.get_or_create(user=user)
        return config
    
    def get_default_ai_model(self, user: User) -> AIModel:
        """Get the default AI model for a user."""
        config = self.get_user_ai_config(user)
        
        if config.preferred_model and config.preferred_model.is_active:
            return config.preferred_model
        
        # Fallback to system default
        return AIModel.objects.filter(is_active=True, is_default=True).first()
    
    def process_interaction(self, session: AISession, user_input: str, 
                          interaction_type: str = 'query') -> Dict[str, Any]:
        """Process an AI interaction within a session."""
        try:
            # Get AI model
            ai_model = session.ai_model or self.get_default_ai_model(session.user)
            if not ai_model:
                return {'success': False, 'error': 'No AI model available'}
            
            # Generate AI response
            ai_response, tokens_used, response_time = self._generate_ai_response(
                ai_model, user_input, session
            )
            
            if not ai_response:
                return {'success': False, 'error': 'Failed to generate AI response'}
            
            # Calculate cost
            cost = self._calculate_cost(ai_model, tokens_used)
            
            # Create interaction record
            interaction = AIInteraction.objects.create(
                session=session,
                interaction_type=interaction_type,
                user_prompt=user_input,
                ai_response=ai_response,
                tokens_used=tokens_used,
                response_time_seconds=response_time,
                cost=cost
            )
            
            # Update session metrics
            session.total_interactions += 1
            session.total_tokens_used += tokens_used
            session.total_cost += float(session.total_cost) + cost  # Convert to float for arithmetic
            session.last_activity = timezone.now()
            session.save()
            
            # Update user statistics
            self._update_user_statistics(session.user, tokens_used, cost)
            
            return {
                'success': True,
                'ai_response': ai_response,
                'interaction_id': str(interaction.id),
                'tokens_used': tokens_used,
                'cost': float(cost)
            }
            
        except Exception as e:
            logger.error(f"Error processing AI interaction: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_ai_response(self, ai_model: AIModel, prompt: str, 
                             session: AISession) -> tuple:
        """Generate AI response using the specified model."""
        start_time = timezone.now()
        
        try:
            if ai_model.model_type == 'openai_gpt4' and self.openai_client:
                return self._generate_openai_response(ai_model, prompt, session)
            elif ai_model.model_type == 'openai_gpt35' and self.openai_client:
                return self._generate_openai_response(ai_model, prompt, session)
            else:
                # Fallback to mock response for development
                return self._generate_mock_response(prompt, session)
                
        except Exception as e:
            logger.error(f"Error generating AI response: {e}")
            return None, 0, 0
    
    def _generate_openai_response(self, ai_model: AIModel, prompt: str, 
                                 session: AISession) -> tuple:
        """Generate response using OpenAI API."""
        try:
            # Build context from session
            context = self._build_session_context(session)
            
            messages = [
                {"role": "system", "content": context},
                {"role": "user", "content": prompt}
            ]
            
            # Get model configuration
            config = self.get_user_ai_config(session.user)
            
            model_name = "gpt-4" if ai_model.model_type == 'openai_gpt4' else "gpt-3.5-turbo"
            
            response = self.openai_client.ChatCompletion.create(
                model=model_name,
                messages=messages,
                max_tokens=min(ai_model.max_tokens, config.default_max_tokens),
                temperature=config.default_temperature
            )
            
            ai_response = response.choices[0].message.content
            tokens_used = response.usage.total_tokens
            
            response_time = (timezone.now() - start_time).total_seconds()
            
            return ai_response, tokens_used, response_time
            
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            raise e
    
    def _generate_mock_response(self, prompt: str, session: AISession) -> tuple:
        """Generate mock response for development/testing."""
        # Check if this is a research suggestions request
        if 'research suggestions' in prompt.lower() or 'suggestions' in prompt.lower():
            # Generate mock research suggestions in JSON format
            mock_suggestions = {
                "suggestions": [
                    {
                        "title": "Investigate Novel Machine Learning Approaches",
                        "description": "Explore the application of recent deep learning techniques to your research domain. This could involve investigating transformer architectures, attention mechanisms, or graph neural networks depending on your data structure.",
                        "rationale": "Machine learning is rapidly evolving, and new architectures often provide significant improvements over traditional methods. Early adoption can lead to innovative research contributions.",
                        "confidence_level": "high",
                        "priority_score": 0.9,
                        "suggestion_type": "research_question"
                    },
                    {
                        "title": "Cross-Disciplinary Collaboration Analysis",
                        "description": "Consider examining how your research area intersects with other disciplines. This could reveal new research questions and methodological approaches that haven't been explored.",
                        "rationale": "Interdisciplinary research often leads to breakthrough discoveries and is increasingly valued by funding agencies and journals.",
                        "confidence_level": "high",
                        "priority_score": 0.8,
                        "suggestion_type": "methodology_innovation"
                    },
                    {
                        "title": "Longitudinal Impact Assessment",
                        "description": "Develop a framework for assessing the long-term implications of your research findings. This could involve follow-up studies or impact measurement methodologies.",
                        "rationale": "Understanding long-term impacts is crucial for demonstrating research value and informing future policy decisions.",
                        "confidence_level": "medium",
                        "priority_score": 0.7,
                        "suggestion_type": "study_design"
                    },
                    {
                        "title": "Open Science and Reproducibility Focus",
                        "description": "Incorporate open science practices into your research methodology, including data sharing protocols, reproducible analysis pipelines, and transparent reporting.",
                        "rationale": "Open science practices are becoming standard requirements and improve research credibility and impact.",
                        "confidence_level": "very_high",
                        "priority_score": 0.85,
                        "suggestion_type": "methodology_innovation"
                    },
                    {
                        "title": "Ethical Implications Framework",
                        "description": "Develop a comprehensive framework for addressing ethical considerations specific to your research area, including data privacy, algorithmic bias, and societal impact.",
                        "rationale": "Ethical considerations are increasingly important in research evaluation and can prevent future complications while strengthening research proposals.",
                        "confidence_level": "high",
                        "priority_score": 0.75,
                        "suggestion_type": "research_question"
                    }
                ]
            }
            response = json.dumps(mock_suggestions, indent=2)
        else:
            # Regular response templates for other session types
            response_templates = {
                'literature_analysis': f"For your literature analysis query '{prompt[:50]}...', I've identified several key patterns: 1) Emerging trends in your field, 2) Methodological gaps, 3) Citation networks. Based on recent publications, there's growing interest in interdisciplinary approaches.",
                'methodology_design': f"Regarding methodology for '{prompt[:50]}...', I recommend considering: 1) Mixed methods approach combining quantitative and qualitative data, 2) Longitudinal study design for temporal insights, 3) Control groups for validation. The methodology should align with your research questions.",
                'writing_assistance': f"For the text you provided '{prompt[:50]}...', I suggest: 1) Improving clarity by simplifying complex sentences, 2) Strengthening arguments with additional evidence, 3) Better transitions between paragraphs. Consider your target audience and journal requirements."
            }
            
            session_type = session.session_type if session else 'general_consultation'
            response = response_templates.get(session_type, f"Thank you for your question: '{prompt[:50]}...'. Based on the context, I recommend exploring the following approaches and considering recent developments in your field.")
        
        # Simulate processing time and token usage
        import time
        time.sleep(0.5)  # Simulate API delay
        
        tokens_used = len(prompt.split()) + len(response.split())
        response_time = 0.5
        
        return response, tokens_used, response_time
    
    def _build_session_context(self, session: AISession) -> str:
        """Build context string for AI model."""
        context_parts = [
            "You are an AI research assistant helping with academic research.",
            f"Session type: {session.get_session_type_display()}"
        ]
        
        if session.project:
            context_parts.extend([
                f"Research project: {session.project.title}",
                f"Research field: {session.project.get_research_field_display()}",
                f"Project description: {session.project.description[:200]}..."
            ])
            
            if session.project.research_questions:
                context_parts.append(f"Research questions: {session.project.research_questions[:200]}...")
        
        if session.context:
            context_parts.append(f"Additional context: {session.context}")
        
        return "\n".join(context_parts)
    
    def _calculate_cost(self, ai_model: AIModel, tokens_used: int) -> float:
        """Calculate cost for AI interaction."""
        cost_per_1k = float(ai_model.cost_per_1k_tokens)
        return (tokens_used / 1000) * cost_per_1k
    
    def _update_user_statistics(self, user: User, tokens_used: int, cost: float):
        """Update user's daily AI usage statistics."""
        today = timezone.now().date()
        month = today.strftime('%Y-%m')
        
        stats, created = AIUsageStatistics.objects.get_or_create(
            user=user,
            date=today,
            defaults={'month': month}
        )
        
        stats.total_interactions += 1
        stats.total_tokens_used += tokens_used
        stats.total_cost += cost
        stats.save()
    
    def generate_research_suggestions(self, user: User, project: ResearchProject = None,
                                    context: str = "") -> List[ResearchSuggestion]:
        """Generate personalized research suggestions."""
        try:
            # Create AI session for suggestion generation
            session = AISession.objects.create(
                user=user,
                project=project,
                session_type='research_planning',
                title='Research Suggestions Generation',
                context=context
            )
            
            # Generate suggestions using AI
            suggestions_prompt = self._build_suggestions_prompt(user, project, context)
            
            result = self.process_interaction(
                session=session,
                user_input=suggestions_prompt,
                interaction_type='suggestion_request'
            )
            
            if result['success']:
                # Parse AI response and create suggestion objects
                suggestions = self._parse_suggestions_response(
                    result['ai_response'], user, project
                )
                
                # End the session
                session.end_session()
                
                return suggestions
            else:
                logger.error(f"Failed to generate suggestions: {result['error']}")
                return []
                
        except Exception as e:
            logger.error(f"Error generating research suggestions: {e}")
            return []
    
    def _build_suggestions_prompt(self, user: User, project: ResearchProject = None,
                                 context: str = "") -> str:
        """Build prompt for research suggestions."""
        prompt_parts = [
            "Please provide 5 specific research suggestions based on the following information:",
        ]
        
        if project:
            prompt_parts.extend([
                f"Research Project: {project.title}",
                f"Field: {project.get_research_field_display()}",
                f"Description: {project.description}",
                f"Current Status: {project.get_status_display()}"
            ])
            
            if project.research_questions:
                prompt_parts.append(f"Research Questions: {project.research_questions}")
            
            if project.keywords:
                prompt_parts.append(f"Keywords: {project.keywords}")
        
        if context:
            prompt_parts.append(f"Additional Context: {context}")
        
        prompt_parts.extend([
            "",
            "For each suggestion, provide:",
            "1. A clear title",
            "2. Detailed description (2-3 sentences)",
            "3. Rationale for why this is important",
            "4. Confidence level (low/medium/high/very_high)",
            "5. Priority score (0.0-1.0)",
            "",
            "Format your response as JSON with the following structure:",
            """
            {
                "suggestions": [
                    {
                        "title": "Suggestion Title",
                        "description": "Detailed description...",
                        "rationale": "Why this is important...",
                        "confidence_level": "high",
                        "priority_score": 0.8,
                        "suggestion_type": "research_question"
                    }
                ]
            }
            """
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_suggestions_response(self, ai_response: str, user: User,
                                  project: ResearchProject = None) -> List[ResearchSuggestion]:
        """Parse AI response and create suggestion objects."""
        suggestions = []
        
        try:
            # Try to parse JSON response
            response_data = json.loads(ai_response)
            
            for suggestion_data in response_data.get('suggestions', []):
                suggestion = ResearchSuggestion.objects.create(
                    user=user,
                    project=project,
                    suggestion_type=suggestion_data.get('suggestion_type', 'research_question'),
                    title=suggestion_data.get('title', 'Untitled Suggestion'),
                    content=suggestion_data.get('description', ''),
                    reasoning=suggestion_data.get('rationale', ''),
                    confidence_level=suggestion_data.get('confidence_level', 'medium'),
                    priority_score=suggestion_data.get('priority_score', 0.5)
                )
                suggestions.append(suggestion)
                
        except json.JSONDecodeError:
            # Fallback: create a single suggestion from the response text
            suggestion = ResearchSuggestion.objects.create(
                user=user,
                project=project,
                suggestion_type='general_consultation',
                title='AI Research Suggestion',
                content=ai_response[:500],
                reasoning='Generated based on research context',
                confidence_level='medium',
                priority_score=0.5
            )
            suggestions.append(suggestion)
        
        return suggestions
    
    def start_literature_analysis(self, user: User, analysis_type: str,
                                 search_query: str, project_id: str = None) -> Dict[str, Any]:
        """Start literature analysis process."""
        try:
            project = None
            if project_id:
                project = ResearchProject.objects.get(id=project_id, user=user)
            
            # Create analysis record
            analysis = LiteratureAnalysis.objects.create(
                user=user,
                project=project,
                analysis_type=analysis_type,
                title=f"{analysis_type.replace('_', ' ').title()} Analysis",
                description=f"Analysis based on query: {search_query}",
                search_query=search_query
            )
            
            # Start async analysis (in production, this would be a background task)
            self._perform_literature_analysis(analysis)
            
            return {
                'success': True,
                'analysis_id': str(analysis.id)
            }
            
        except Exception as e:
            logger.error(f"Error starting literature analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def _perform_literature_analysis(self, analysis: LiteratureAnalysis):
        """Perform the actual literature analysis."""
        try:
            # Mock implementation - in production, this would integrate with real databases
            analysis.status = 'processing'
            analysis.save()
            
            # Simulate analysis
            import time
            time.sleep(1)
            
            # Generate mock results
            analysis.key_findings = [
                "Increasing trend in interdisciplinary research",
                "Gap identified in longitudinal studies",
                "Strong citation network around key methodologies"
            ]
            
            analysis.identified_gaps = [
                "Limited research on long-term impacts",
                "Insufficient diversity in study populations",
                "Need for standardized measurement tools"
            ]
            
            analysis.research_trends = [
                {"trend": "Machine learning applications", "growth": "45%"},
                {"trend": "Open science practices", "growth": "30%"},
                {"trend": "Collaborative research", "growth": "25%"}
            ]
            
            analysis.papers_analyzed = 150
            analysis.confidence_score = 0.8
            analysis.processing_time_seconds = 1.0
            analysis.status = 'completed'
            analysis.completed_at = timezone.now()
            analysis.save()
            
        except Exception as e:
            logger.error(f"Error performing literature analysis: {e}")
            analysis.status = 'failed'
            analysis.save()
    
    def provide_writing_assistance(self, user: User, text: str, assistance_type: str,
                                 manuscript_id: str = None, section_id: str = None) -> Dict[str, Any]:
        """Provide AI-powered writing assistance."""
        try:
            manuscript = None
            section = None
            
            if manuscript_id:
                from apps.writer_app.models import Manuscript
                manuscript = Manuscript.objects.get(id=manuscript_id, owner=user)
            
            if section_id:
                from apps.writer_app.models import ManuscriptSection
                section = ManuscriptSection.objects.get(id=section_id, manuscript__owner=user)
            
            # Create assistance record
            assistance = WritingAssistance.objects.create(
                user=user,
                manuscript=manuscript,
                section=section,
                assistance_type=assistance_type,
                original_text=text
            )
            
            # Generate assistance using AI
            suggestions = self._generate_writing_suggestions(assistance, text, assistance_type)
            
            return {
                'success': True,
                'assistance_id': str(assistance.id),
                'suggestions': suggestions
            }
            
        except Exception as e:
            logger.error(f"Error providing writing assistance: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_writing_suggestions(self, assistance: WritingAssistance, 
                                    text: str, assistance_type: str) -> Dict[str, Any]:
        """Generate writing improvement suggestions."""
        # Mock implementation
        suggestions = {
            'structure': {
                'feedback': 'Consider reorganizing paragraphs for better flow',
                'improvements': ['Move thesis statement to the beginning', 'Add transition sentences']
            },
            'clarity': {
                'feedback': 'Some sentences could be simplified for clarity',
                'improvements': ['Break down complex sentences', 'Use active voice']
            },
            'style': {
                'feedback': 'Writing style is appropriate for academic audience',
                'improvements': ['Maintain consistent terminology', 'Vary sentence length']
            }
        }
        
        # Update assistance record
        assistance.overall_feedback = f"Provided {assistance_type} assistance for {len(text)} characters of text"
        assistance.specific_improvements = suggestions.get(assistance_type, {}).get('improvements', [])
        assistance.save()
        
        return suggestions
    
    def generate_methodology_recommendation(self, user: User, project_id: str,
                                          research_context: str, category: str = None) -> Dict[str, Any]:
        """Generate methodology recommendations."""
        try:
            project = ResearchProject.objects.get(id=project_id, user=user)
            
            recommendation = MethodologyRecommendation.objects.create(
                user=user,
                project=project,
                title=f"Methodology Recommendation for {project.title}",
                category=category or 'mixed_methods',
                description="AI-generated methodology recommendation",
                research_context=research_context
            )
            
            # Generate recommendation details
            self._generate_methodology_details(recommendation)
            
            return {
                'success': True,
                'recommendation_id': str(recommendation.id)
            }
            
        except Exception as e:
            logger.error(f"Error generating methodology recommendation: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_methodology_details(self, recommendation: MethodologyRecommendation):
        """Generate detailed methodology recommendation."""
        # Mock implementation
        recommendation.rationale = "Based on your research questions and context, a mixed methods approach would provide comprehensive insights."
        recommendation.detailed_steps = [
            "Conduct preliminary qualitative interviews",
            "Design quantitative survey based on qualitative findings",
            "Implement survey with stratified sampling",
            "Analyze results using both descriptive and inferential statistics",
            "Integrate findings in discussion"
        ]
        recommendation.required_resources = [
            "Survey platform subscription",
            "Statistical analysis software",
            "Interview recording equipment",
            "Data collection time: 3-6 months"
        ]
        recommendation.estimated_timeline = "6-12 months"
        recommendation.statistical_considerations = "Ensure adequate sample size for statistical power. Consider multiple testing corrections."
        recommendation.potential_limitations = [
            "Response rate variability",
            "Self-selection bias",
            "Temporal constraints"
        ]
        recommendation.save()
    
    def provide_statistical_guidance(self, user: User, research_question: str,
                                   data_description: str, analysis_type: str = None,
                                   project_id: str = None) -> Dict[str, Any]:
        """Provide statistical analysis guidance."""
        try:
            project = None
            if project_id:
                project = ResearchProject.objects.get(id=project_id, user=user)
            
            guidance = StatisticalGuidance.objects.create(
                user=user,
                project=project,
                analysis_type=analysis_type or 'descriptive',
                research_question=research_question,
                data_description=data_description
            )
            
            # Generate guidance details
            self._generate_statistical_details(guidance)
            
            return {
                'success': True,
                'guidance_id': str(guidance.id)
            }
            
        except Exception as e:
            logger.error(f"Error providing statistical guidance: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_statistical_details(self, guidance: StatisticalGuidance):
        """Generate detailed statistical guidance."""
        # Mock implementation based on analysis type
        type_guidance = {
            'descriptive': {
                'tests': ['Mean, median, mode', 'Standard deviation', 'Frequency distributions'],
                'assumptions': ['Data normality', 'Outlier identification'],
                'software': ['R', 'Python (pandas)', 'SPSS']
            },
            'regression': {
                'tests': ['Linear regression', 'Multiple regression', 'Logistic regression'],
                'assumptions': ['Linearity', 'Independence', 'Homoscedasticity', 'Normality'],
                'software': ['R (lm function)', 'Python (scikit-learn)', 'Stata']
            },
            'anova': {
                'tests': ['One-way ANOVA', 'Two-way ANOVA', 'Repeated measures ANOVA'],
                'assumptions': ['Normality', 'Equal variances', 'Independence'],
                'software': ['R (aov function)', 'Python (scipy.stats)', 'SPSS']
            }
        }
        
        details = type_guidance.get(guidance.analysis_type, type_guidance['descriptive'])
        
        guidance.recommended_tests = details['tests']
        guidance.assumptions_to_check = details['assumptions']
        guidance.software_recommendations = details['software']
        guidance.interpretation_guidance = f"Interpret results in context of your research question: {guidance.research_question[:100]}..."
        guidance.save()
    
    def start_trend_analysis(self, user: User, trend_type: str, research_field: str,
                           keywords: str = "", time_period: str = "") -> Dict[str, Any]:
        """Start research trend analysis."""
        try:
            analysis = TrendAnalysis.objects.create(
                user=user,
                trend_type=trend_type,
                research_field=research_field,
                time_period=time_period or "Last 5 years",
                keywords_analyzed=keywords
            )
            
            # Perform trend analysis
            self._perform_trend_analysis(analysis)
            
            return {
                'success': True,
                'analysis_id': str(analysis.id)
            }
            
        except Exception as e:
            logger.error(f"Error starting trend analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def _perform_trend_analysis(self, analysis: TrendAnalysis):
        """Perform trend analysis."""
        try:
            # Mock implementation
            analysis.identified_trends = [
                {
                    "trend": "AI/ML Integration",
                    "growth_rate": "120%",
                    "confidence": 0.9,
                    "impact": "High"
                },
                {
                    "trend": "Open Science Practices",
                    "growth_rate": "85%",
                    "confidence": 0.8,
                    "impact": "Medium"
                }
            ]
            
            analysis.trend_predictions = [
                "Continued growth in AI applications",
                "Increased focus on reproducibility",
                "More interdisciplinary collaboration"
            ]
            
            analysis.research_opportunities = [
                "Novel AI applications in domain",
                "Standardization initiatives",
                "Cross-sector partnerships"
            ]
            
            analysis.papers_analyzed = 500
            analysis.confidence_level = 0.85
            analysis.processing_time_minutes = 2.0
            analysis.completed_at = timezone.now()
            analysis.save()
            
        except Exception as e:
            logger.error(f"Error performing trend analysis: {e}")
    
    def generate_personalized_recommendations(self, user: User) -> List[PersonalizedRecommendation]:
        """Generate personalized recommendations for user."""
        try:
            recommendations = []
            
            # Analyze user's research patterns
            user_projects = ResearchProject.objects.filter(user=user)
            user_sessions = AISession.objects.filter(user=user)
            
            # Generate different types of recommendations
            if user_projects.exists():
                recommendations.extend(self._generate_project_recommendations(user, user_projects))
            
            if user_sessions.exists():
                recommendations.extend(self._generate_behavior_recommendations(user, user_sessions))
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating personalized recommendations: {e}")
            return []
    
    def _generate_project_recommendations(self, user: User, projects) -> List[PersonalizedRecommendation]:
        """Generate recommendations based on user's projects."""
        recommendations = []
        
        for project in projects[:3]:  # Analyze recent projects
            rec = PersonalizedRecommendation.objects.create(
                user=user,
                recommendation_type='research_direction',
                title=f"Expand research in {project.research_field}",
                description=f"Based on your work on '{project.title}', consider exploring related methodologies or interdisciplinary approaches.",
                reasoning=f"Your active research in {project.get_research_field_display()} shows potential for expansion.",
                relevance_score=0.8,
                novelty_score=0.6,
                feasibility_score=0.9
            )
            recommendations.append(rec)
        
        return recommendations
    
    def _generate_behavior_recommendations(self, user: User, sessions) -> List[PersonalizedRecommendation]:
        """Generate recommendations based on user behavior."""
        recommendations = []
        
        # Analyze session types
        session_types = sessions.values_list('session_type', flat=True)
        most_common_type = max(set(session_types), key=session_types.count) if session_types else None
        
        if most_common_type:
            rec = PersonalizedRecommendation.objects.create(
                user=user,
                recommendation_type='tool_recommendation',
                title=f"Advanced {most_common_type.replace('_', ' ').title()} Tools",
                description=f"Since you frequently use {most_common_type.replace('_', ' ')}, consider these advanced tools and techniques.",
                reasoning=f"Your usage pattern shows strong interest in {most_common_type}.",
                relevance_score=0.9,
                novelty_score=0.7,
                feasibility_score=0.8
            )
            recommendations.append(rec)
        
        return recommendations


class CitationAnalysisService:
    """Service for citation analysis and suggestions."""
    
    def suggest_citations(self, manuscript, section, text_context: str) -> List[CitationSuggestion]:
        """Suggest citations for given text context."""
        suggestions = []
        
        try:
            # Mock implementation - in production, this would analyze the text
            # and search for relevant papers from the Scholar module
            
            # For now, create mock suggestions
            from apps.scholar_app.models import SearchIndex
            
            # Get some papers from the database
            papers = SearchIndex.objects.filter(status='active')[:3]
            
            for i, paper in enumerate(papers):
                suggestion = CitationSuggestion.objects.create(
                    user=manuscript.owner,
                    manuscript=manuscript,
                    section=section,
                    suggestion_type='supporting_evidence',
                    text_context=text_context,
                    suggested_paper=paper,
                    relevance_explanation=f"This paper provides relevant background for your discussion on {text_context[:50]}...",
                    confidence_score=0.8 - (i * 0.1),
                    relevance_score=0.9 - (i * 0.1),
                    novelty_score=0.7
                )
                suggestions.append(suggestion)
        
        except Exception as e:
            logger.error(f"Error suggesting citations: {e}")
        
        return suggestions


class ResearchTrendService:
    """Service for research trend analysis and prediction."""
    
    def analyze_field_trends(self, research_field: str, time_period: str = "5 years") -> Dict[str, Any]:
        """Analyze trends in a research field."""
        # Mock implementation
        return {
            'emerging_topics': [
                {'topic': 'AI Ethics', 'growth_rate': '150%'},
                {'topic': 'Quantum Computing', 'growth_rate': '120%'},
                {'topic': 'Sustainable Technology', 'growth_rate': '95%'}
            ],
            'declining_topics': [
                {'topic': 'Traditional Methods', 'decline_rate': '-20%'}
            ],
            'stable_topics': [
                {'topic': 'Statistical Analysis', 'stability': 'High'}
            ],
            'predictions': [
                'Increased interdisciplinary research',
                'Greater focus on reproducibility',
                'More open science practices'
            ]
        }
    
    def predict_research_opportunities(self, user_interests: List[str]) -> List[Dict[str, Any]]:
        """Predict research opportunities based on user interests."""
        opportunities = []
        
        for interest in user_interests[:5]:
            opportunities.append({
                'opportunity': f"Novel applications of {interest}",
                'potential_impact': 'High',
                'feasibility': 'Medium',
                'time_to_market': '2-3 years',
                'confidence': 0.8
            })
        
        return opportunities


class AdvancedResearchAnalysisService:
    """Advanced AI service for deep research analysis and gap identification."""
    
    def __init__(self):
        self.ai_service = AIResearchService()
    
    def perform_comprehensive_literature_gap_analysis(self, user: User, research_domain: str, 
                                                    existing_papers: List = None) -> Dict[str, Any]:
        """Perform comprehensive literature gap analysis using AI."""
        try:
            # Create analysis session
            session = AISession.objects.create(
                user=user,
                session_type='literature_analysis',
                title=f'Literature Gap Analysis: {research_domain}',
                context=f'Comprehensive gap analysis for domain: {research_domain}'
            )
            
            # Build comprehensive prompt for gap analysis
            gap_analysis_prompt = self._build_gap_analysis_prompt(research_domain, existing_papers)
            
            # Process with AI
            result = self.ai_service.process_interaction(
                session=session,
                user_input=gap_analysis_prompt,
                interaction_type='analysis_request'
            )
            
            if result['success']:
                # Parse and structure the gap analysis results
                gap_analysis = self._parse_gap_analysis_response(
                    result['ai_response'], user, research_domain
                )
                
                session.end_session()
                return gap_analysis
            else:
                return {'success': False, 'error': result['error']}
                
        except Exception as e:
            logger.error(f"Error in comprehensive literature gap analysis: {e}")
            return {'success': False, 'error': str(e)}
    
    def _build_gap_analysis_prompt(self, research_domain: str, existing_papers: List = None) -> str:
        """Build comprehensive prompt for literature gap analysis."""
        prompt_parts = [
            f"Perform a comprehensive literature gap analysis for the research domain: {research_domain}",
            "",
            "Please analyze and identify:",
            "1. METHODOLOGICAL GAPS - Missing or underexplored research methods",
            "2. THEORETICAL GAPS - Unexplored theoretical frameworks or concepts", 
            "3. EMPIRICAL GAPS - Lack of empirical evidence in specific areas",
            "4. POPULATION GAPS - Underrepresented populations or demographics",
            "5. GEOGRAPHICAL GAPS - Underexplored regions or contexts",
            "6. TEMPORAL GAPS - Historical periods or timeframes needing study",
            "7. INTERDISCIPLINARY GAPS - Opportunities for cross-field collaboration",
            "",
            "For each gap identified, provide:",
            "- Clear description of the gap",
            "- Why this gap is significant",
            "- Potential research questions to address the gap",
            "- Suggested methodological approaches",
            "- Expected impact if addressed",
            "- Feasibility assessment (High/Medium/Low)",
            "",
        ]
        
        if existing_papers:
            prompt_parts.extend([
                "Consider the following existing research:",
                f"Papers analyzed: {len(existing_papers)} studies",
                ""
            ])
        
        prompt_parts.extend([
            "Format your response as structured JSON:",
            """
            {
                "domain_analysis": {
                    "domain": "research domain",
                    "current_state": "overview of current research state",
                    "maturity_level": "emerging/developing/mature"
                },
                "identified_gaps": [
                    {
                        "gap_type": "methodological/theoretical/empirical/population/geographical/temporal/interdisciplinary",
                        "title": "Gap Title",
                        "description": "Detailed description",
                        "significance": "Why this matters",
                        "research_questions": ["Question 1", "Question 2"],
                        "suggested_methods": ["Method 1", "Method 2"],
                        "expected_impact": "High/Medium/Low",
                        "feasibility": "High/Medium/Low",
                        "priority_score": 0.8,
                        "timeframe": "Short-term/Medium-term/Long-term"
                    }
                ],
                "emerging_opportunities": [
                    {
                        "opportunity": "Description",
                        "rationale": "Why this is emerging",
                        "potential_impact": "Expected impact",
                        "collaboration_potential": "High/Medium/Low"
                    }
                ],
                "recommendations": [
                    "Specific recommendation 1",
                    "Specific recommendation 2"
                ]
            }
            """
        ])
        
        return "\n".join(prompt_parts)
    
    def _parse_gap_analysis_response(self, ai_response: str, user: User, 
                                   research_domain: str) -> Dict[str, Any]:
        """Parse and structure gap analysis response."""
        try:
            # Try to parse JSON response
            analysis_data = json.loads(ai_response)
            
            # Create LiteratureAnalysis record for persistence
            literature_analysis = LiteratureAnalysis.objects.create(
                user=user,
                analysis_type='gap_analysis',
                title=f'Literature Gap Analysis: {research_domain}',
                description=f'Comprehensive gap analysis for {research_domain}',
                search_query=research_domain,
                status='completed',
                completed_at=timezone.now()
            )
            
            # Extract and structure the results
            domain_info = analysis_data.get('domain_analysis', {})
            gaps = analysis_data.get('identified_gaps', [])
            opportunities = analysis_data.get('emerging_opportunities', [])
            recommendations = analysis_data.get('recommendations', [])
            
            # Store structured results
            literature_analysis.key_findings = [
                f"Domain maturity: {domain_info.get('maturity_level', 'Unknown')}",
                f"Total gaps identified: {len(gaps)}",
                f"Emerging opportunities: {len(opportunities)}"
            ]
            
            literature_analysis.identified_gaps = [
                {
                    'type': gap.get('gap_type'),
                    'title': gap.get('title'),
                    'description': gap.get('description'),
                    'priority': gap.get('priority_score', 0.5),
                    'feasibility': gap.get('feasibility'),
                    'impact': gap.get('expected_impact')
                }
                for gap in gaps
            ]
            
            literature_analysis.methodology_insights = {
                'domain_state': domain_info.get('current_state'),
                'opportunities': opportunities,
                'recommendations': recommendations
            }
            
            literature_analysis.confidence_score = 0.85  # High confidence for structured analysis
            literature_analysis.save()
            
            # Generate specific research suggestions based on gaps
            self._generate_gap_based_suggestions(user, gaps, research_domain)
            
            return {
                'success': True,
                'analysis_id': str(literature_analysis.id),
                'domain_analysis': domain_info,
                'gaps_identified': len(gaps),
                'high_priority_gaps': len([g for g in gaps if g.get('priority_score', 0) > 0.7]),
                'gaps': gaps,
                'opportunities': opportunities,
                'recommendations': recommendations
            }
            
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return {
                'success': True,
                'analysis_text': ai_response,
                'structured': False
            }
        except Exception as e:
            logger.error(f"Error parsing gap analysis response: {e}")
            return {'success': False, 'error': str(e)}
    
    def _generate_gap_based_suggestions(self, user: User, gaps: List[Dict], 
                                      research_domain: str):
        """Generate specific research suggestions based on identified gaps."""
        try:
            for gap in gaps[:3]:  # Focus on top 3 gaps
                priority_score = gap.get('priority_score', 0.5)
                feasibility = gap.get('feasibility', 'Medium')
                
                # Convert feasibility to numeric score
                feasibility_scores = {'High': 0.9, 'Medium': 0.6, 'Low': 0.3}
                feasibility_score = feasibility_scores.get(feasibility, 0.6)
                
                # Create research suggestion
                ResearchSuggestion.objects.create(
                    user=user,
                    suggestion_type='literature_gap',
                    title=f"Address {gap.get('gap_type', 'Research')} Gap: {gap.get('title', 'Untitled')}",
                    content=gap.get('description', '') + "\n\nSuggested approach: " + 
                           ", ".join(gap.get('suggested_methods', [])),
                    reasoning=gap.get('significance', 'Important research gap identified through literature analysis'),
                    confidence_level='high',
                    priority_score=min(priority_score, 1.0),
                    supporting_evidence=[{
                        'source': 'AI Literature Gap Analysis',
                        'domain': research_domain,
                        'feasibility': feasibility,
                        'expected_impact': gap.get('expected_impact'),
                        'timeframe': gap.get('timeframe')
                    }]
                )
                
        except Exception as e:
            logger.error(f"Error generating gap-based suggestions: {e}")
    
    def generate_research_hypothesis_suggestions(self, user: User, project: ResearchProject,
                                               gap_analysis_id: str = None) -> List[Dict[str, Any]]:
        """Generate specific research hypotheses based on gap analysis and project context."""
        try:
            # Build context from project and gap analysis
            context_parts = [
                f"Project: {project.title}",
                f"Field: {project.get_research_field_display()}",
                f"Description: {project.description}",
            ]
            
            if project.research_questions:
                context_parts.append(f"Current research questions: {project.research_questions}")
            
            if gap_analysis_id:
                try:
                    gap_analysis = LiteratureAnalysis.objects.get(id=gap_analysis_id, user=user)
                    context_parts.append(f"Based on literature gap analysis findings:")
                    for gap in gap_analysis.identified_gaps[:3]:
                        context_parts.append(f"- {gap.get('title')}: {gap.get('description')}")
                except LiteratureAnalysis.DoesNotExist:
                    pass
            
            # Create AI session for hypothesis generation
            session = AISession.objects.create(
                user=user,
                project=project,
                session_type='research_planning',
                title='Research Hypothesis Generation',
                context="\n".join(context_parts)
            )
            
            # Build hypothesis generation prompt
            hypothesis_prompt = self._build_hypothesis_prompt(project, context_parts)
            
            # Process with AI
            result = self.ai_service.process_interaction(
                session=session,
                user_input=hypothesis_prompt,
                interaction_type='suggestion_request'
            )
            
            if result['success']:
                hypotheses = self._parse_hypothesis_response(result['ai_response'], user, project)
                session.end_session()
                return hypotheses
            else:
                return []
                
        except Exception as e:
            logger.error(f"Error generating research hypotheses: {e}")
            return []
    
    def _build_hypothesis_prompt(self, project: ResearchProject, context_parts: List[str]) -> str:
        """Build prompt for research hypothesis generation."""
        prompt_parts = [
            "Generate 5 specific, testable research hypotheses based on the following project context:",
            "",
            *context_parts,
            "",
            "For each hypothesis, provide:",
            "1. Clear, testable hypothesis statement",
            "2. Independent and dependent variables",
            "3. Expected relationship/direction",
            "4. Rationale based on existing theory/evidence",
            "5. Suggested measurement approach",
            "6. Potential confounding variables to consider",
            "7. Testability assessment (High/Medium/Low)",
            "",
            "Format as JSON:",
            """
            {
                "hypotheses": [
                    {
                        "hypothesis": "Clear hypothesis statement",
                        "independent_variable": "IV description",
                        "dependent_variable": "DV description", 
                        "expected_relationship": "positive/negative/curvilinear/no effect",
                        "rationale": "Theoretical/empirical justification",
                        "measurement_approach": "How to measure variables",
                        "confounders": ["Potential confounding variable 1", "Variable 2"],
                        "testability": "High/Medium/Low",
                        "novelty_score": 0.8,
                        "feasibility_score": 0.7
                    }
                ]
            }
            """
        ]
        
        return "\n".join(prompt_parts)
    
    def _parse_hypothesis_response(self, ai_response: str, user: User, 
                                 project: ResearchProject) -> List[Dict[str, Any]]:
        """Parse hypothesis generation response."""
        try:
            response_data = json.loads(ai_response)
            hypotheses = []
            
            for hyp_data in response_data.get('hypotheses', []):
                # Create research suggestion for each hypothesis
                suggestion = ResearchSuggestion.objects.create(
                    user=user,
                    project=project,
                    suggestion_type='research_question',
                    title=f"Hypothesis: {hyp_data.get('hypothesis', 'Untitled')[:100]}",
                    content=hyp_data.get('hypothesis', ''),
                    reasoning=hyp_data.get('rationale', ''),
                    confidence_level='high',
                    priority_score=hyp_data.get('novelty_score', 0.5),
                    supporting_evidence=[{
                        'methodology': hyp_data.get('measurement_approach'),
                        'variables': {
                            'independent': hyp_data.get('independent_variable'),
                            'dependent': hyp_data.get('dependent_variable'),
                            'confounders': hyp_data.get('confounders', [])
                        },
                        'expected_relationship': hyp_data.get('expected_relationship'),
                        'testability': hyp_data.get('testability'),
                        'feasibility': hyp_data.get('feasibility_score', 0.5)
                    }]
                )
                
                hypotheses.append({
                    'suggestion_id': str(suggestion.id),
                    **hyp_data
                })
                
            return hypotheses
            
        except json.JSONDecodeError:
            # Fallback for non-JSON responses
            return [{'text_response': ai_response}]
        except Exception as e:
            logger.error(f"Error parsing hypothesis response: {e}")
            return []
    
    def analyze_methodology_trends(self, research_field: str, 
                                 time_period: str = "last_5_years") -> Dict[str, Any]:
        """Analyze methodology trends in a specific research field."""
        try:
            # Create trend analysis
            trend_analysis = TrendAnalysis.objects.create(
                user=None,  # System-generated analysis
                trend_type='methodology_trends',
                research_field=research_field,
                time_period=time_period,
                keywords_analyzed=f"methodology trends {research_field}"
            )
            
            # Mock advanced methodology trend analysis
            methodology_trends = {
                'emerging_methods': [
                    {
                        'method': 'Mixed Reality Data Collection',
                        'adoption_rate': '45% increase',
                        'advantages': ['Immersive data', 'Ecological validity'],
                        'challenges': ['Technical complexity', 'Cost'],
                        'recommended_for': ['Behavioral studies', 'Training research']
                    },
                    {
                        'method': 'AI-Assisted Data Analysis',
                        'adoption_rate': '67% increase', 
                        'advantages': ['Speed', 'Pattern detection', 'Scalability'],
                        'challenges': ['Interpretability', 'Bias'],
                        'recommended_for': ['Large datasets', 'Complex patterns']
                    }
                ],
                'declining_methods': [
                    {
                        'method': 'Traditional Survey Methods',
                        'decline_rate': '23% decrease',
                        'reasons': ['Low response rates', 'Limited engagement'],
                        'alternatives': ['Mobile apps', 'Gamified surveys']
                    }
                ],
                'stable_methods': [
                    {
                        'method': 'Randomized Controlled Trials',
                        'stability': 'High - gold standard maintained',
                        'innovations': ['Digital randomization', 'Remote monitoring']
                    }
                ],
                'predicted_future_trends': [
                    'Increased automation in data collection',
                    'Real-time analysis and feedback',
                    'Integration of multiple data sources',
                    'Emphasis on reproducible workflows'
                ]
            }
            
            # Update trend analysis with results
            trend_analysis.identified_trends = methodology_trends['emerging_methods']
            trend_analysis.trend_predictions = methodology_trends['predicted_future_trends']
            trend_analysis.statistical_insights = {
                'methodology_adoption_trends': methodology_trends,
                'confidence_level': 0.8
            }
            trend_analysis.completed_at = timezone.now()
            trend_analysis.save()
            
            return {
                'success': True,
                'analysis_id': str(trend_analysis.id),
                'methodology_trends': methodology_trends
            }
            
        except Exception as e:
            logger.error(f"Error analyzing methodology trends: {e}")
            return {'success': False, 'error': str(e)}


class SmartCollaborationService:
    """Service for AI-powered collaboration recommendations."""
    
    def __init__(self):
        self.ai_service = AIResearchService()
    
    def suggest_collaborators(self, user: User, project: ResearchProject) -> List[Dict[str, Any]]:
        """Suggest potential collaborators based on research interests and expertise."""
        try:
            # Analyze project requirements
            collaboration_needs = self._analyze_collaboration_needs(project)
            
            # Find potential collaborators from platform users
            potential_collaborators = self._find_potential_collaborators(
                user, project, collaboration_needs
            )
            
            # Generate collaboration recommendations
            recommendations = []
            for collaborator_data in potential_collaborators[:5]:
                rec = PersonalizedRecommendation.objects.create(
                    user=user,
                    recommendation_type='collaboration_opportunity',
                    title=f"Collaboration with {collaborator_data['name']}",
                    description=collaborator_data['rationale'],
                    reasoning=collaborator_data['match_reasons'],
                    relevance_score=collaborator_data['match_score'],
                    novelty_score=0.7,
                    feasibility_score=0.8,
                    recommended_items=[collaborator_data],
                    priority_level='medium'
                )
                recommendations.append({
                    'recommendation_id': str(rec.id),
                    **collaborator_data
                })
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error suggesting collaborators: {e}")
            return []
    
    def _analyze_collaboration_needs(self, project: ResearchProject) -> Dict[str, Any]:
        """Analyze what kind of collaboration the project needs."""
        # Mock analysis - in production, this would use AI to analyze project text
        needs = {
            'required_expertise': [],
            'methodology_gaps': [],
            'resource_needs': [],
            'collaboration_type': 'complementary'  # or 'supplementary', 'validation'
        }
        
        # Basic keyword analysis
        description_lower = project.description.lower()
        
        if 'machine learning' in description_lower or 'ai' in description_lower:
            needs['required_expertise'].append('Machine Learning')
        if 'statistics' in description_lower or 'analysis' in description_lower:
            needs['required_expertise'].append('Statistical Analysis')
        if 'qualitative' in description_lower:
            needs['required_expertise'].append('Qualitative Methods')
            
        return needs
    
    def _find_potential_collaborators(self, user: User, project: ResearchProject, 
                                    needs: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Find potential collaborators from the platform."""
        # Mock implementation - in production, this would analyze user profiles and research history
        potential_collaborators = [
            {
                'user_id': 'mock_user_1',
                'name': 'Dr. Sarah Chen',
                'expertise': ['Machine Learning', 'Data Analysis'],
                'institution': 'MIT',
                'match_score': 0.85,
                'match_reasons': 'Strong expertise in ML and complementary research interests',
                'rationale': 'Dr. Chen\'s work in ML applications aligns perfectly with your project needs.',
                'recent_publications': 3,
                'collaboration_history': 'Active collaborator'
            },
            {
                'user_id': 'mock_user_2', 
                'name': 'Prof. Michael Rodriguez',
                'expertise': ['Statistical Methods', 'Experimental Design'],
                'institution': 'Stanford University',
                'match_score': 0.78,
                'match_reasons': 'Methodological expertise and similar research domain',
                'rationale': 'Prof. Rodriguez can provide statistical methodology guidance.',
                'recent_publications': 5,
                'collaboration_history': 'Open to collaboration'
            }
        ]
        
        return potential_collaborators