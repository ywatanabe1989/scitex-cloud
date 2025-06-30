from django.urls import path
from . import views

app_name = 'ai_assistant'

urlpatterns = [
    # Dashboard and main interface
    path('', views.dashboard, name='dashboard'),
    
    # Research Projects
    path('projects/', views.ResearchProjectListView.as_view(), name='project_list'),
    path('projects/create/', views.ResearchProjectCreateView.as_view(), name='project_create'),
    path('projects/<uuid:pk>/', views.ResearchProjectDetailView.as_view(), name='project_detail'),
    path('projects/<uuid:pk>/update/', views.ResearchProjectUpdateView.as_view(), name='project_update'),
    
    # AI Sessions
    path('sessions/start/', views.start_ai_session, name='start_session'),
    path('sessions/<uuid:pk>/', views.AISessionDetailView.as_view(), name='session_detail'),
    path('sessions/<uuid:session_id>/chat/', views.chat_interface, name='chat_interface'),
    
    # Research Suggestions
    path('suggestions/', views.research_suggestions, name='research_suggestions'),
    path('suggestions/<uuid:suggestion_id>/', views.suggestion_detail, name='suggestion_detail'),
    
    # Literature Analysis
    path('literature-analysis/', views.literature_analysis, name='literature_analysis'),
    path('literature-analysis/<uuid:analysis_id>/', views.analysis_detail, name='analysis_detail'),
    
    # Writing Assistance
    path('writing-assistance/', views.writing_assistance, name='writing_assistance'),
    
    # Methodology Recommendations
    path('methodology/', views.methodology_recommendations, name='methodology_recommendations'),
    path('methodology/<uuid:recommendation_id>/', views.methodology_detail, name='methodology_detail'),
    
    # Statistical Guidance
    path('statistical-guidance/', views.statistical_guidance, name='statistical_guidance'),
    path('statistical-guidance/<uuid:guidance_id>/', views.statistical_detail, name='statistical_detail'),
    
    # Trend Analysis
    path('trend-analysis/', views.trend_analysis, name='trend_analysis'),
    path('trend-analysis/<uuid:analysis_id>/', views.trend_detail, name='trend_detail'),
    
    # Personalized Recommendations
    path('recommendations/', views.personalized_recommendations, name='personalized_recommendations'),
    path('recommendations/<uuid:recommendation_id>/action/', views.recommendation_action, name='recommendation_action'),
    
    # Usage Statistics and Settings
    path('usage-statistics/', views.usage_statistics, name='usage_statistics'),
    path('settings/', views.ai_settings, name='ai_settings'),
    
    # Advanced AI Assistant API Endpoints
    path('api/gap-analysis/', views.api_comprehensive_gap_analysis, name='api_gap_analysis'),
    path('api/generate-hypotheses/', views.api_generate_research_hypotheses, name='api_generate_hypotheses'),
    path('api/methodology-trends/', views.api_methodology_trends, name='api_methodology_trends'),
    path('api/collaboration-suggestions/', views.api_collaboration_suggestions, name='api_collaboration_suggestions'),
    path('api/advanced-suggestions/', views.api_advanced_research_suggestions, name='api_advanced_suggestions'),
    path('api/research-insights/', views.api_research_insights_dashboard, name='api_research_insights'),
]