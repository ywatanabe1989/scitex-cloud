from django import forms
from django.contrib.auth.models import User
from .models import ResearchProject, AISession, AIModelConfig


class ResearchProjectForm(forms.ModelForm):
    """Form for creating and editing research projects."""
    
    class Meta:
        model = ResearchProject
        fields = [
            'title', 'description', 'research_field', 'keywords',
            'research_questions', 'hypotheses', 'methodology_notes',
            'start_date', 'target_completion', 'collaborators'
        ]
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter project title'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your research project'
            }),
            'research_field': forms.Select(attrs={
                'class': 'form-select'
            }),
            'keywords': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter keywords separated by commas'
            }),
            'research_questions': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'What are your main research questions?'
            }),
            'hypotheses': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'State your research hypotheses'
            }),
            'methodology_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Notes about your methodology'
            }),
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'target_completion': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'collaborators': forms.SelectMultiple(attrs={
                'class': 'form-select',
                'size': '4'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter collaborators to exclude the current user
            self.fields['collaborators'].queryset = User.objects.exclude(id=user.id)


class AISessionForm(forms.ModelForm):
    """Form for starting AI assistance sessions."""
    
    class Meta:
        model = AISession
        fields = ['title', 'session_type', 'project', 'context']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Session title (e.g., "Literature Review Help")'
            }),
            'session_type': forms.Select(attrs={
                'class': 'form-select'
            }),
            'project': forms.Select(attrs={
                'class': 'form-select'
            }),
            'context': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provide context for the AI assistant (optional)'
            })
        }
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            # Filter projects to user's projects
            self.fields['project'].queryset = ResearchProject.objects.filter(user=user)
            self.fields['project'].empty_label = "Select a project (optional)"


class LiteratureAnalysisForm(forms.Form):
    """Form for starting literature analysis."""
    
    analysis_type = forms.ChoiceField(
        choices=[
            ('gap_analysis', 'Literature Gap Analysis'),
            ('trend_analysis', 'Research Trend Analysis'),
            ('citation_network', 'Citation Network Analysis'),
            ('methodology_comparison', 'Methodology Comparison'),
            ('thematic_analysis', 'Thematic Analysis'),
            ('quality_assessment', 'Quality Assessment'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    search_query = forms.CharField(
        max_length=500,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter search terms for literature analysis'
        })
    )
    
    project = forms.ModelChoiceField(
        queryset=ResearchProject.objects.none(),
        required=False,
        empty_label="Select a project (optional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    time_period = forms.CharField(
        max_length=50,
        initial="Last 5 years",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "Last 5 years", "2020-2024"'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['project'].queryset = ResearchProject.objects.filter(user=user)


class WritingAssistanceForm(forms.Form):
    """Form for requesting writing assistance."""
    
    assistance_type = forms.ChoiceField(
        choices=[
            ('structure', 'Structure Improvement'),
            ('clarity', 'Clarity Enhancement'),
            ('flow', 'Flow and Transitions'),
            ('tone', 'Tone Adjustment'),
            ('conciseness', 'Conciseness'),
            ('argument', 'Argument Strengthening'),
            ('evidence', 'Evidence Integration'),
            ('formatting', 'Formatting and Style'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    text = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 10,
            'placeholder': 'Paste the text you want to improve'
        })
    )
    
    target_audience = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "Academic peers", "General public"'
        })
    )
    
    target_journal = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Target journal (if applicable)'
        })
    )


class MethodologyRecommendationForm(forms.Form):
    """Form for requesting methodology recommendations."""
    
    project = forms.ModelChoiceField(
        queryset=ResearchProject.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    research_context = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 5,
            'placeholder': 'Describe your research context, objectives, and constraints'
        })
    )
    
    category = forms.ChoiceField(
        choices=[
            ('quantitative', 'Quantitative Research'),
            ('qualitative', 'Qualitative Research'),
            ('mixed_methods', 'Mixed Methods'),
            ('experimental', 'Experimental Design'),
            ('observational', 'Observational Study'),
            ('computational', 'Computational Methods'),
            ('theoretical', 'Theoretical Framework'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['project'].queryset = ResearchProject.objects.filter(user=user)


class StatisticalGuidanceForm(forms.Form):
    """Form for requesting statistical guidance."""
    
    research_question = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'What is your research question?'
        })
    )
    
    data_description = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your data: type, size, variables, etc.'
        })
    )
    
    analysis_type = forms.ChoiceField(
        choices=[
            ('descriptive', 'Descriptive Statistics'),
            ('inferential', 'Inferential Statistics'),
            ('regression', 'Regression Analysis'),
            ('anova', 'ANOVA'),
            ('time_series', 'Time Series Analysis'),
            ('machine_learning', 'Machine Learning'),
            ('bayesian', 'Bayesian Analysis'),
            ('non_parametric', 'Non-parametric Tests'),
            ('multivariate', 'Multivariate Analysis'),
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    project = forms.ModelChoiceField(
        queryset=ResearchProject.objects.none(),
        required=False,
        empty_label="Select a project (optional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['project'].queryset = ResearchProject.objects.filter(user=user)


class TrendAnalysisForm(forms.Form):
    """Form for starting trend analysis."""
    
    trend_type = forms.ChoiceField(
        choices=[
            ('emerging_topics', 'Emerging Research Topics'),
            ('methodology_trends', 'Methodology Trends'),
            ('citation_patterns', 'Citation Patterns'),
            ('collaboration_networks', 'Collaboration Networks'),
            ('funding_trends', 'Funding Trends'),
            ('publication_patterns', 'Publication Patterns'),
            ('interdisciplinary_growth', 'Interdisciplinary Growth'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    research_field = forms.ChoiceField(
        choices=ResearchProject.RESEARCH_FIELDS,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    keywords = forms.CharField(
        max_length=500,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Keywords to focus the analysis (optional)'
        })
    )
    
    time_period = forms.CharField(
        max_length=50,
        initial="Last 5 years",
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'e.g., "Last 5 years", "2020-2024"'
        })
    )


class AIModelConfigForm(forms.ModelForm):
    """Form for AI model configuration."""
    
    class Meta:
        model = AIModelConfig
        fields = [
            'preferred_model', 'backup_model', 'default_temperature',
            'default_max_tokens', 'response_style', 'daily_token_limit',
            'monthly_cost_limit', 'notify_on_suggestions',
            'notify_on_analysis_completion', 'email_summaries'
        ]
        widgets = {
            'preferred_model': forms.Select(attrs={'class': 'form-select'}),
            'backup_model': forms.Select(attrs={'class': 'form-select'}),
            'default_temperature': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.1',
                'min': '0.0',
                'max': '2.0'
            }),
            'default_max_tokens': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '100',
                'max': '8192'
            }),
            'response_style': forms.Select(attrs={'class': 'form-select'}),
            'daily_token_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1000'
            }),
            'monthly_cost_limit': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '1.00'
            }),
            'notify_on_suggestions': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'notify_on_analysis_completion': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'email_summaries': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class InteractionFeedbackForm(forms.Form):
    """Form for providing feedback on AI interactions."""
    
    rating = forms.ChoiceField(
        choices=[(i, i) for i in range(1, 6)],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    feedback = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Additional feedback (optional)'
        })
    )
    
    is_helpful = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    
    implemented = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )


class GenerateResearchSuggestionsForm(forms.Form):
    """Form for generating new research suggestions."""
    
    research_field = forms.ChoiceField(
        choices=[
            ('', 'Select field (optional)'),
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
        ],
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    research_context = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Describe your research interests, current work, or specific areas you want suggestions for...'
        }),
        help_text="Provide context about your research to get more relevant suggestions",
        required=False
    )
    
    project = forms.ModelChoiceField(
        queryset=ResearchProject.objects.none(),
        required=False,
        empty_label="Select a project (optional)",
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if user:
            self.fields['project'].queryset = ResearchProject.objects.filter(user=user)


class SuggestionResponseForm(forms.Form):
    """Form for responding to research suggestions."""
    
    STATUS_CHOICES = [
        ('accepted', 'Accept'),
        ('rejected', 'Reject'),
        ('implemented', 'Mark as Implemented'),
        ('deferred', 'Defer for Later'),
    ]
    
    action = forms.ChoiceField(
        choices=STATUS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    user_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Your notes about this suggestion (optional)'
        })
    )