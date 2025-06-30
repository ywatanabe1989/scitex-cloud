from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.http import JsonResponse
from django.contrib import messages
from django.db.models import Q, Count, Avg
from django.utils import timezone
from django.core.paginator import Paginator
from django.urls import reverse_lazy
import json
import logging

logger = logging.getLogger(__name__)

from .models import (
    AIModel, ResearchProject, AISession, AIInteraction, ResearchSuggestion,
    LiteratureAnalysis, MethodologyRecommendation, StatisticalGuidance,
    WritingAssistance, TrendAnalysis, PersonalizedRecommendation,
    CitationSuggestion, AIUsageStatistics, AIModelConfig
)
from .services import AIResearchService, AdvancedResearchAnalysisService, SmartCollaborationService
from .forms import ResearchProjectForm, AISessionForm


@login_required
def dashboard(request):
    """AI Research Assistant dashboard."""
    user = request.user
    
    # Get user's recent projects
    recent_projects = ResearchProject.objects.filter(user=user).order_by('-updated_at')[:5]
    
    # Get active AI sessions
    active_sessions = AISession.objects.filter(user=user, is_active=True).order_by('-last_activity')[:3]
    
    # Get recent suggestions
    recent_suggestions = ResearchSuggestion.objects.filter(user=user, status='pending').order_by('-priority_score', '-created_at')[:5]
    
    # Get usage statistics
    try:
        today_stats = AIUsageStatistics.objects.get(user=user, date=timezone.now().date())
    except AIUsageStatistics.DoesNotExist:
        today_stats = None
    
    # Get personalized recommendations
    recommendations = PersonalizedRecommendation.objects.filter(
        user=user, 
        viewed=False
    ).order_by('-relevance_score')[:3]
    
    context = {
        'recent_projects': recent_projects,
        'active_sessions': active_sessions,
        'recent_suggestions': recent_suggestions,
        'today_stats': today_stats,
        'recommendations': recommendations,
    }
    
    return render(request, 'ai_assistant_app/dashboard.html', context)


class ResearchProjectListView(LoginRequiredMixin, ListView):
    """List user's research projects."""
    model = ResearchProject
    template_name = 'ai_assistant_app/project_list.html'
    context_object_name = 'projects'
    paginate_by = 10
    
    def get_queryset(self):
        return ResearchProject.objects.filter(user=self.request.user).order_by('-updated_at')


class ResearchProjectDetailView(LoginRequiredMixin, DetailView):
    """Detail view for research project."""
    model = ResearchProject
    template_name = 'ai_assistant_app/project_detail.html'
    context_object_name = 'project'
    
    def get_queryset(self):
        return ResearchProject.objects.filter(
            Q(user=self.request.user) | Q(collaborators=self.request.user)
        ).distinct()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        project = self.object
        
        # Get project's AI sessions
        context['ai_sessions'] = AISession.objects.filter(project=project).order_by('-started_at')[:10]
        
        # Get project's suggestions
        context['suggestions'] = ResearchSuggestion.objects.filter(project=project).order_by('-priority_score')[:10]
        
        # Get project's analyses
        context['literature_analyses'] = LiteratureAnalysis.objects.filter(project=project).order_by('-created_at')[:5]
        context['methodology_recommendations'] = MethodologyRecommendation.objects.filter(project=project).order_by('-created_at')[:5]
        
        return context


class ResearchProjectCreateView(LoginRequiredMixin, CreateView):
    """Create new research project."""
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'ai_assistant_app/project_form.html'
    success_url = reverse_lazy('ai_assistant:project_list')
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        messages.success(self.request, 'Research project created successfully!')
        return super().form_valid(form)


class ResearchProjectUpdateView(LoginRequiredMixin, UpdateView):
    """Update existing research project."""
    model = ResearchProject
    form_class = ResearchProjectForm
    template_name = 'ai_assistant_app/project_form.html'
    
    def get_queryset(self):
        return ResearchProject.objects.filter(
            Q(user=self.request.user) | Q(collaborators=self.request.user)
        ).distinct()
    
    def get_success_url(self):
        return reverse_lazy('ai_assistant:project_detail', kwargs={'pk': self.object.pk})
    
    def form_valid(self, form):
        messages.success(self.request, 'Research project updated successfully!')
        return super().form_valid(form)


@login_required
def start_ai_session(request):
    """Start a new AI assistance session."""
    if request.method == 'POST':
        form = AISessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.user = request.user
            session.save()
            
            messages.success(request, 'AI session started successfully!')
            return redirect('ai_assistant:session_detail', pk=session.pk)
    else:
        form = AISessionForm()
    
    return render(request, 'ai_assistant_app/start_session.html', {'form': form})


class AISessionDetailView(LoginRequiredMixin, DetailView):
    """Detail view for AI session."""
    model = AISession
    template_name = 'ai_assistant_app/session_detail.html'
    context_object_name = 'session'
    
    def get_queryset(self):
        return AISession.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        session = self.object
        
        # Get session interactions
        context['interactions'] = AIInteraction.objects.filter(session=session).order_by('created_at')
        
        return context


@login_required
def chat_interface(request, session_id):
    """Interactive chat interface for AI assistance."""
    session = get_object_or_404(AISession, id=session_id, user=request.user)
    
    if request.method == 'POST':
        user_input = request.POST.get('user_input', '').strip()
        
        if user_input:
            # Process AI interaction
            ai_service = AIResearchService()
            response = ai_service.process_interaction(
                session=session,
                user_input=user_input,
                interaction_type=request.POST.get('interaction_type', 'query')
            )
            
            if response['success']:
                return JsonResponse({
                    'success': True,
                    'response': response['ai_response'],
                    'interaction_id': response['interaction_id']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': response['error']
                })
    
    # Get session interactions for display
    interactions = AIInteraction.objects.filter(session=session).order_by('created_at')
    
    context = {
        'session': session,
        'interactions': interactions,
    }
    
    return render(request, 'ai_assistant_app/chat_interface.html', context)


@login_required
def research_suggestions(request):
    """View and generate research suggestions."""
    from .forms import GenerateResearchSuggestionsForm
    from .services import AIResearchService
    
    generate_form = GenerateResearchSuggestionsForm(user=request.user)
    generation_success = False
    generated_count = 0
    
    # Handle suggestion generation
    if request.method == 'POST':
        generate_form = GenerateResearchSuggestionsForm(user=request.user, data=request.POST)
        if generate_form.is_valid():
            try:
                ai_service = AIResearchService()
                
                # Get form data
                research_field = generate_form.cleaned_data.get('research_field')
                research_context = generate_form.cleaned_data.get('research_context', '')
                project = generate_form.cleaned_data.get('project')
                
                # Add research field to context if provided
                if research_field:
                    field_context = f"Research Field: {dict(generate_form.fields['research_field'].choices).get(research_field, research_field)}\n"
                    research_context = field_context + research_context
                
                # Generate suggestions
                new_suggestions = ai_service.generate_research_suggestions(
                    user=request.user,
                    project=project,
                    context=research_context
                )
                
                generated_count = len(new_suggestions)
                if generated_count > 0:
                    generation_success = True
                    messages.success(request, f'Successfully generated {generated_count} research suggestions!')
                else:
                    messages.warning(request, 'No suggestions were generated. Please try again with more specific context.')
                    
            except Exception as e:
                logger.error(f"Error generating research suggestions: {e}")
                messages.error(request, 'Failed to generate suggestions. Please try again later.')
    
    # Get existing suggestions
    suggestions = ResearchSuggestion.objects.filter(user=request.user).order_by('-priority_score', '-created_at')
    
    # Filter by status if requested
    status_filter = request.GET.get('status')
    if status_filter:
        suggestions = suggestions.filter(status=status_filter)
    
    # Filter by type if requested
    type_filter = request.GET.get('type')
    if type_filter:
        suggestions = suggestions.filter(suggestion_type=type_filter)
    
    paginator = Paginator(suggestions, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'status_filter': status_filter,
        'type_filter': type_filter,
        'suggestion_types': ResearchSuggestion.SUGGESTION_TYPES,
        'status_choices': [
            ('pending', 'Pending'),
            ('accepted', 'Accepted'),
            ('rejected', 'Rejected'),
            ('implemented', 'Implemented'),
            ('deferred', 'Deferred'),
        ],
        'generate_form': generate_form,
        'generation_success': generation_success,
        'generated_count': generated_count,
    }
    
    return render(request, 'ai_assistant_app/research_suggestions.html', context)


@login_required
def suggestion_detail(request, suggestion_id):
    """View suggestion detail and handle user response."""
    suggestion = get_object_or_404(ResearchSuggestion, id=suggestion_id, user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action in ['accepted', 'rejected', 'implemented', 'deferred']:
            suggestion.status = action
            suggestion.user_notes = request.POST.get('user_notes', '')
            
            if action == 'implemented':
                suggestion.implementation_date = timezone.now()
            
            suggestion.save()
            messages.success(request, f'Suggestion {action} successfully!')
            
            return redirect('ai_assistant:research_suggestions')
    
    context = {'suggestion': suggestion}
    return render(request, 'ai_assistant_app/suggestion_detail.html', context)


@login_required
def literature_analysis(request):
    """Literature analysis interface."""
    if request.method == 'POST':
        # Start literature analysis
        analysis_type = request.POST.get('analysis_type')
        search_query = request.POST.get('search_query')
        project_id = request.POST.get('project_id')
        
        if analysis_type and search_query:
            ai_service = AIResearchService()
            result = ai_service.start_literature_analysis(
                user=request.user,
                analysis_type=analysis_type,
                search_query=search_query,
                project_id=project_id
            )
            
            if result['success']:
                messages.success(request, 'Literature analysis started successfully!')
                return redirect('ai_assistant:analysis_detail', analysis_id=result['analysis_id'])
            else:
                messages.error(request, f"Failed to start analysis: {result['error']}")
    
    # Get user's projects for selection
    projects = ResearchProject.objects.filter(user=request.user).order_by('-updated_at')
    
    # Get recent analyses
    recent_analyses = LiteratureAnalysis.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'projects': projects,
        'recent_analyses': recent_analyses,
        'analysis_types': LiteratureAnalysis.ANALYSIS_TYPES,
    }
    
    return render(request, 'ai_assistant_app/literature_analysis.html', context)


@login_required
def analysis_detail(request, analysis_id):
    """View literature analysis results."""
    analysis = get_object_or_404(LiteratureAnalysis, id=analysis_id, user=request.user)
    
    context = {'analysis': analysis}
    return render(request, 'ai_assistant_app/analysis_detail.html', context)


@login_required
def writing_assistance(request):
    """Writing assistance interface."""
    if request.method == 'POST':
        # Request writing assistance
        text = request.POST.get('text')
        assistance_type = request.POST.get('assistance_type')
        manuscript_id = request.POST.get('manuscript_id')
        section_id = request.POST.get('section_id')
        
        if text and assistance_type:
            ai_service = AIResearchService()
            result = ai_service.provide_writing_assistance(
                user=request.user,
                text=text,
                assistance_type=assistance_type,
                manuscript_id=manuscript_id,
                section_id=section_id
            )
            
            if result['success']:
                return JsonResponse({
                    'success': True,
                    'assistance_id': result['assistance_id'],
                    'suggestions': result['suggestions']
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': result['error']
                })
    
    # Get user's manuscripts for selection
    try:
        from apps.writer_app.models import Manuscript
        manuscripts = Manuscript.objects.filter(owner=request.user).order_by('-updated_at')
    except ImportError:
        manuscripts = []
    
    # Get recent writing assistance
    recent_assistance = WritingAssistance.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'manuscripts': manuscripts,
        'recent_assistance': recent_assistance,
        'assistance_types': WritingAssistance.ASSISTANCE_TYPES,
    }
    
    return render(request, 'ai_assistant_app/writing_assistance.html', context)


@login_required
def methodology_recommendations(request):
    """Methodology recommendations interface."""
    if request.method == 'POST':
        # Request methodology recommendation
        project_id = request.POST.get('project_id')
        research_context = request.POST.get('research_context')
        category = request.POST.get('category')
        
        if project_id and research_context:
            ai_service = AIResearchService()
            result = ai_service.generate_methodology_recommendation(
                user=request.user,
                project_id=project_id,
                research_context=research_context,
                category=category
            )
            
            if result['success']:
                messages.success(request, 'Methodology recommendation generated successfully!')
                return redirect('ai_assistant:methodology_detail', recommendation_id=result['recommendation_id'])
            else:
                messages.error(request, f"Failed to generate recommendation: {result['error']}")
    
    # Get user's projects
    projects = ResearchProject.objects.filter(user=request.user).order_by('-updated_at')
    
    # Get recent recommendations
    recent_recommendations = MethodologyRecommendation.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'projects': projects,
        'recent_recommendations': recent_recommendations,
        'methodology_categories': MethodologyRecommendation.METHODOLOGY_CATEGORIES,
    }
    
    return render(request, 'ai_assistant_app/methodology_recommendations.html', context)


@login_required
def methodology_detail(request, recommendation_id):
    """View methodology recommendation detail."""
    recommendation = get_object_or_404(MethodologyRecommendation, id=recommendation_id, user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action in ['reviewed', 'accepted', 'implemented', 'rejected']:
            recommendation.status = action
            recommendation.implementation_notes = request.POST.get('notes', '')
            recommendation.user_rating = request.POST.get('rating')
            recommendation.save()
            
            messages.success(request, f'Recommendation {action} successfully!')
    
    context = {'recommendation': recommendation}
    return render(request, 'ai_assistant_app/methodology_detail.html', context)


@login_required
def statistical_guidance(request):
    """Statistical guidance interface."""
    if request.method == 'POST':
        # Request statistical guidance
        research_question = request.POST.get('research_question')
        data_description = request.POST.get('data_description')
        analysis_type = request.POST.get('analysis_type')
        project_id = request.POST.get('project_id')
        
        if research_question and data_description:
            ai_service = AIResearchService()
            result = ai_service.provide_statistical_guidance(
                user=request.user,
                research_question=research_question,
                data_description=data_description,
                analysis_type=analysis_type,
                project_id=project_id
            )
            
            if result['success']:
                messages.success(request, 'Statistical guidance generated successfully!')
                return redirect('ai_assistant:statistical_detail', guidance_id=result['guidance_id'])
            else:
                messages.error(request, f"Failed to generate guidance: {result['error']}")
    
    # Get user's projects
    projects = ResearchProject.objects.filter(user=request.user).order_by('-updated_at')
    
    # Get recent guidance
    recent_guidance = StatisticalGuidance.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'projects': projects,
        'recent_guidance': recent_guidance,
        'analysis_types': StatisticalGuidance.ANALYSIS_TYPES,
    }
    
    return render(request, 'ai_assistant_app/statistical_guidance.html', context)


@login_required
def statistical_detail(request, guidance_id):
    """View statistical guidance detail."""
    guidance = get_object_or_404(StatisticalGuidance, id=guidance_id, user=request.user)
    
    context = {'guidance': guidance}
    return render(request, 'ai_assistant_app/statistical_detail.html', context)


@login_required
def trend_analysis(request):
    """Research trend analysis interface."""
    if request.method == 'POST':
        # Start trend analysis
        trend_type = request.POST.get('trend_type')
        research_field = request.POST.get('research_field')
        keywords = request.POST.get('keywords')
        time_period = request.POST.get('time_period')
        
        if trend_type and research_field:
            ai_service = AIResearchService()
            result = ai_service.start_trend_analysis(
                user=request.user,
                trend_type=trend_type,
                research_field=research_field,
                keywords=keywords,
                time_period=time_period
            )
            
            if result['success']:
                messages.success(request, 'Trend analysis started successfully!')
                return redirect('ai_assistant:trend_detail', analysis_id=result['analysis_id'])
            else:
                messages.error(request, f"Failed to start analysis: {result['error']}")
    
    # Get recent trend analyses
    recent_analyses = TrendAnalysis.objects.filter(user=request.user).order_by('-created_at')[:5]
    
    context = {
        'recent_analyses': recent_analyses,
        'trend_types': TrendAnalysis.TREND_TYPES,
        'research_fields': ResearchProject.RESEARCH_FIELDS,
    }
    
    return render(request, 'ai_assistant_app/trend_analysis.html', context)


@login_required
def trend_detail(request, analysis_id):
    """View trend analysis results."""
    analysis = get_object_or_404(TrendAnalysis, id=analysis_id, user=request.user)
    
    context = {'analysis': analysis}
    return render(request, 'ai_assistant_app/trend_detail.html', context)


@login_required
def personalized_recommendations(request):
    """View personalized recommendations."""
    recommendations = PersonalizedRecommendation.objects.filter(user=request.user).order_by('-relevance_score', '-created_at')
    
    # Mark as viewed
    unviewed = recommendations.filter(viewed=False)
    unviewed.update(viewed=True, viewed_at=timezone.now())
    
    paginator = Paginator(recommendations, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {'page_obj': page_obj}
    return render(request, 'ai_assistant_app/personalized_recommendations.html', context)


@login_required
def recommendation_action(request, recommendation_id):
    """Handle recommendation actions (save, dismiss, etc.)."""
    recommendation = get_object_or_404(PersonalizedRecommendation, id=recommendation_id, user=request.user)
    
    if request.method == 'POST':
        action = request.POST.get('action')
        
        if action == 'save':
            recommendation.saved = True
            recommendation.clicked = True
        elif action == 'dismiss':
            recommendation.dismissed = True
        elif action == 'rate':
            rating = request.POST.get('rating')
            if rating:
                recommendation.user_rating = int(rating)
        
        recommendation.save()
        
        return JsonResponse({'success': True})
    
    return JsonResponse({'success': False})


@login_required
def usage_statistics(request):
    """View AI usage statistics."""
    user = request.user
    
    # Get monthly statistics
    monthly_stats = AIUsageStatistics.objects.filter(user=user).order_by('-date')[:12]
    
    # Get summary statistics
    total_sessions = AISession.objects.filter(user=user).count()
    total_interactions = AIInteraction.objects.filter(session__user=user).count()
    avg_rating = AIInteraction.objects.filter(
        session__user=user, 
        user_rating__isnull=False
    ).aggregate(avg_rating=Avg('user_rating'))['avg_rating']
    
    context = {
        'monthly_stats': monthly_stats,
        'total_sessions': total_sessions,
        'total_interactions': total_interactions,
        'avg_rating': round(avg_rating, 2) if avg_rating else None,
    }
    
    return render(request, 'ai_assistant_app/usage_statistics.html', context)


@login_required
def ai_settings(request):
    """AI model configuration and settings."""
    try:
        config = AIModelConfig.objects.get(user=request.user)
    except AIModelConfig.DoesNotExist:
        config = AIModelConfig.objects.create(user=request.user)
    
    if request.method == 'POST':
        # Update configuration
        config.preferred_model_id = request.POST.get('preferred_model')
        config.default_temperature = float(request.POST.get('temperature', 0.7))
        config.default_max_tokens = int(request.POST.get('max_tokens', 2048))
        config.response_style = request.POST.get('response_style', 'academic')
        config.daily_token_limit = int(request.POST.get('daily_token_limit', 50000))
        config.monthly_cost_limit = float(request.POST.get('monthly_cost_limit', 100.00))
        
        # Notification preferences
        config.notify_on_suggestions = request.POST.get('notify_suggestions') == 'on'
        config.notify_on_analysis_completion = request.POST.get('notify_analysis') == 'on'
        config.email_summaries = request.POST.get('email_summaries') == 'on'
        
        config.save()
        messages.success(request, 'AI settings updated successfully!')
        
        return redirect('ai_assistant:ai_settings')
    
    # Get available AI models
    ai_models = AIModel.objects.filter(is_active=True).order_by('name')
    
    context = {
        'config': config,
        'ai_models': ai_models,
    }
    
    return render(request, 'ai_assistant_app/ai_settings.html', context)


# Advanced AI Assistant API Endpoints

@login_required
def api_comprehensive_gap_analysis(request):
    """API endpoint for comprehensive literature gap analysis."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            research_domain = data.get('research_domain', '').strip()
            
            if not research_domain:
                return JsonResponse({'success': False, 'error': 'Research domain is required'})
            
            # Initialize advanced analysis service
            analysis_service = AdvancedResearchAnalysisService()
            
            # Perform comprehensive gap analysis
            result = analysis_service.perform_comprehensive_literature_gap_analysis(
                user=request.user,
                research_domain=research_domain,
                existing_papers=data.get('existing_papers', [])
            )
            
            return JsonResponse(result)
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Error in gap analysis API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


@login_required 
def api_generate_research_hypotheses(request):
    """API endpoint for generating research hypotheses."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            gap_analysis_id = data.get('gap_analysis_id')
            
            if not project_id:
                return JsonResponse({'success': False, 'error': 'Project ID is required'})
            
            # Get project
            try:
                project = ResearchProject.objects.get(id=project_id, user=request.user)
            except ResearchProject.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Project not found'})
            
            # Initialize advanced analysis service
            analysis_service = AdvancedResearchAnalysisService()
            
            # Generate hypotheses
            hypotheses = analysis_service.generate_research_hypothesis_suggestions(
                user=request.user,
                project=project,
                gap_analysis_id=gap_analysis_id
            )
            
            return JsonResponse({
                'success': True,
                'hypotheses': hypotheses,
                'count': len(hypotheses)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Error in hypothesis generation API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


@login_required
def api_methodology_trends(request):
    """API endpoint for methodology trend analysis."""
    if request.method == 'GET':
        try:
            research_field = request.GET.get('research_field', '')
            time_period = request.GET.get('time_period', 'last_5_years')
            
            if not research_field:
                return JsonResponse({'success': False, 'error': 'Research field is required'})
            
            # Initialize advanced analysis service
            analysis_service = AdvancedResearchAnalysisService()
            
            # Analyze methodology trends
            result = analysis_service.analyze_methodology_trends(
                research_field=research_field,
                time_period=time_period
            )
            
            return JsonResponse(result)
            
        except Exception as e:
            logger.error(f"Error in methodology trends API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only GET method allowed'})


@login_required
def api_collaboration_suggestions(request):
    """API endpoint for AI-powered collaboration suggestions."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            
            if not project_id:
                return JsonResponse({'success': False, 'error': 'Project ID is required'})
            
            # Get project
            try:
                project = ResearchProject.objects.get(id=project_id, user=request.user)
            except ResearchProject.DoesNotExist:
                return JsonResponse({'success': False, 'error': 'Project not found'})
            
            # Initialize collaboration service
            collaboration_service = SmartCollaborationService()
            
            # Generate collaboration suggestions
            suggestions = collaboration_service.suggest_collaborators(
                user=request.user,
                project=project
            )
            
            return JsonResponse({
                'success': True,
                'collaboration_suggestions': suggestions,
                'count': len(suggestions)
            })
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Error in collaboration suggestions API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


@login_required
def api_advanced_research_suggestions(request):
    """API endpoint for advanced research suggestions with gap analysis integration."""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            project_id = data.get('project_id')
            include_gap_analysis = data.get('include_gap_analysis', True)
            research_domain = data.get('research_domain', '')
            
            # Get project if provided
            project = None
            if project_id:
                try:
                    project = ResearchProject.objects.get(id=project_id, user=request.user)
                    if not research_domain:
                        research_domain = project.get_research_field_display()
                except ResearchProject.DoesNotExist:
                    return JsonResponse({'success': False, 'error': 'Project not found'})
            
            # Initialize services
            ai_service = AIResearchService()
            analysis_service = AdvancedResearchAnalysisService()
            
            # Perform gap analysis if requested
            gap_analysis_result = None
            if include_gap_analysis and research_domain:
                gap_analysis_result = analysis_service.perform_comprehensive_literature_gap_analysis(
                    user=request.user,
                    research_domain=research_domain
                )
            
            # Generate enhanced research suggestions
            context = data.get('context', '')
            if gap_analysis_result and gap_analysis_result.get('success'):
                # Include gap analysis insights in context
                gaps = gap_analysis_result.get('gaps', [])
                if gaps:
                    gap_context = f"Based on literature gap analysis, key gaps identified: {', '.join([g.get('title', '') for g in gaps[:3]])}"
                    context = f"{context}\n\n{gap_context}"
            
            suggestions = ai_service.generate_research_suggestions(
                user=request.user,
                project=project,
                context=context
            )
            
            # Serialize suggestions for JSON response
            suggestions_data = []
            for suggestion in suggestions:
                suggestions_data.append({
                    'id': str(suggestion.id),
                    'title': suggestion.title,
                    'content': suggestion.content,
                    'reasoning': suggestion.reasoning,
                    'suggestion_type': suggestion.suggestion_type,
                    'confidence_level': suggestion.confidence_level,
                    'priority_score': float(suggestion.priority_score),
                    'status': suggestion.status,
                    'created_at': suggestion.created_at.isoformat()
                })
            
            response_data = {
                'success': True,
                'suggestions': suggestions_data,
                'suggestion_count': len(suggestions_data)
            }
            
            # Include gap analysis results if performed
            if gap_analysis_result:
                response_data['gap_analysis'] = gap_analysis_result
            
            return JsonResponse(response_data)
            
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'error': 'Invalid JSON data'})
        except Exception as e:
            logger.error(f"Error in advanced research suggestions API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only POST method allowed'})


@login_required
def api_research_insights_dashboard(request):
    """API endpoint for research insights dashboard data."""
    if request.method == 'GET':
        try:
            # Get user's AI usage statistics
            user_stats = AIUsageStatistics.objects.filter(user=request.user).order_by('-date')[:30]
            
            # Get recent research suggestions
            recent_suggestions = ResearchSuggestion.objects.filter(
                user=request.user
            ).order_by('-created_at')[:10]
            
            # Get active literature analyses
            active_analyses = LiteratureAnalysis.objects.filter(
                user=request.user,
                status__in=['processing', 'completed']
            ).order_by('-created_at')[:5]
            
            # Get methodology recommendations
            methodology_recs = MethodologyRecommendation.objects.filter(
                user=request.user
            ).order_by('-created_at')[:5]
            
            # Prepare dashboard data
            dashboard_data = {
                'usage_summary': {
                    'total_sessions': sum(stat.total_sessions for stat in user_stats),
                    'total_interactions': sum(stat.total_interactions for stat in user_stats),
                    'total_suggestions': recent_suggestions.count(),
                    'active_analyses': active_analyses.filter(status='processing').count(),
                    'completed_analyses': active_analyses.filter(status='completed').count()
                },
                'recent_suggestions': [
                    {
                        'id': str(suggestion.id),
                        'title': suggestion.title,
                        'type': suggestion.get_suggestion_type_display(),
                        'priority_score': float(suggestion.priority_score),
                        'status': suggestion.get_status_display(),
                        'created_at': suggestion.created_at.isoformat()
                    }
                    for suggestion in recent_suggestions
                ],
                'literature_analyses': [
                    {
                        'id': str(analysis.id),
                        'title': analysis.title,
                        'type': analysis.get_analysis_type_display(),
                        'status': analysis.get_status_display(),
                        'confidence_score': float(analysis.confidence_score) if analysis.confidence_score else 0,
                        'created_at': analysis.created_at.isoformat()
                    }
                    for analysis in active_analyses
                ],
                'methodology_recommendations': [
                    {
                        'id': str(rec.id),
                        'title': rec.title,
                        'category': rec.get_category_display(),
                        'difficulty_level': rec.get_difficulty_level_display(),
                        'status': rec.get_status_display(),
                        'created_at': rec.created_at.isoformat()
                    }
                    for rec in methodology_recs
                ]
            }
            
            return JsonResponse({
                'success': True,
                'dashboard_data': dashboard_data
            })
            
        except Exception as e:
            logger.error(f"Error in research insights dashboard API: {e}")
            return JsonResponse({'success': False, 'error': str(e)})
    
    return JsonResponse({'success': False, 'error': 'Only GET method allowed'})