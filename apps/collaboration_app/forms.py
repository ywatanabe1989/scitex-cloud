from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from .models import (
    Team, TeamMembership, TeamInvitation, SharedProject,
    Comment, Review
)


class TeamCreateForm(forms.ModelForm):
    """Form for creating a new team"""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'team_type', 'visibility', 'allow_member_invites', 
                 'require_approval', 'max_members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter team name',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Describe your team\'s purpose and objectives'
            }),
            'team_type': forms.Select(attrs={'class': 'form-select'}),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'max_members': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 500,
                'value': 50
            }),
            'allow_member_invites': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'require_approval': forms.CheckboxInput(attrs={'class': 'form-check-input', 'checked': True})
        }
    
    def clean_name(self):
        name = self.cleaned_data.get('name')
        if len(name) < 3:
            raise ValidationError("Team name must be at least 3 characters long.")
        return name
    
    def clean_max_members(self):
        max_members = self.cleaned_data.get('max_members')
        if max_members < 1:
            raise ValidationError("Team must allow at least 1 member.")
        if max_members > 500:
            raise ValidationError("Maximum team size is 500 members.")
        return max_members


class TeamUpdateForm(forms.ModelForm):
    """Form for updating team settings"""
    
    class Meta:
        model = Team
        fields = ['name', 'description', 'visibility', 'allow_member_invites', 
                 'require_approval', 'max_members']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'required': True
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4
            }),
            'visibility': forms.Select(attrs={'class': 'form-select'}),
            'max_members': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 500
            }),
            'allow_member_invites': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'require_approval': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class TeamInviteForm(forms.ModelForm):
    """Form for inviting users to a team"""
    
    class Meta:
        model = TeamInvitation
        fields = ['email', 'role', 'message']
        widgets = {
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter email address',
                'required': True
            }),
            'role': forms.Select(attrs={'class': 'form-select'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Add a personal message to the invitation (optional)'
            })
        }
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise ValidationError("Email address is required.")
        return email.lower()


class CommentForm(forms.ModelForm):
    """Form for adding comments"""
    
    class Meta:
        model = Comment
        fields = ['content', 'comment_type']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Enter your comment...',
                'required': True
            }),
            'comment_type': forms.Select(attrs={'class': 'form-select'})
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 5:
            raise ValidationError("Comment must be at least 5 characters long.")
        return content


class ReviewForm(forms.ModelForm):
    """Form for submitting reviews"""
    
    class Meta:
        model = Review
        fields = ['summary', 'detailed_feedback', 'methodology_score', 'clarity_score', 
                 'significance_score', 'overall_score', 'decision']
        widgets = {
            'summary': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Provide a brief summary of your review'
            }),
            'detailed_feedback': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 6,
                'placeholder': 'Provide detailed feedback and suggestions'
            }),
            'methodology_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'clarity_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'significance_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'overall_score': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1,
                'max': 5,
                'step': 1
            }),
            'decision': forms.Select(attrs={'class': 'form-select'})
        }
    
    def clean(self):
        cleaned_data = super().clean()
        
        # Validate score ranges
        score_fields = ['methodology_score', 'clarity_score', 'significance_score', 'overall_score']
        for field in score_fields:
            score = cleaned_data.get(field)
            if score is not None and (score < 1 or score > 5):
                raise ValidationError(f"{field.replace('_', ' ').title()} must be between 1 and 5.")
        
        return cleaned_data


class ProjectShareForm(forms.ModelForm):
    """Form for sharing projects with teams"""
    
    team = forms.ModelChoiceField(
        queryset=Team.objects.none(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select a team..."
    )
    
    class Meta:
        model = SharedProject
        fields = ['team', 'sharing_type', 'expires_at']
        widgets = {
            'sharing_type': forms.Select(attrs={'class': 'form-select'}),
            'expires_at': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def __init__(self, *args, user_teams=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user_teams is not None:
            self.fields['team'].queryset = user_teams
        
        # Make expires_at optional
        self.fields['expires_at'].required = False


class TeamMembershipUpdateForm(forms.ModelForm):
    """Form for updating team membership permissions"""
    
    class Meta:
        model = TeamMembership
        fields = ['role', 'can_invite_members', 'can_create_projects', 
                 'can_manage_projects', 'can_review_work', 'can_export_data']
        widgets = {
            'role': forms.Select(attrs={'class': 'form-select'}),
            'can_invite_members': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_create_projects': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_manage_projects': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_review_work': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'can_export_data': forms.CheckboxInput(attrs={'class': 'form-check-input'})
        }


class ReviewRequestForm(forms.ModelForm):
    """Form for requesting a review"""
    
    reviewer = forms.ModelChoiceField(
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        empty_label="Select a reviewer..."
    )
    
    class Meta:
        model = Review
        fields = ['reviewer', 'review_type', 'deadline']
        widgets = {
            'review_type': forms.Select(attrs={'class': 'form-select'}),
            'deadline': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'type': 'datetime-local'
            })
        }
    
    def __init__(self, *args, available_reviewers=None, **kwargs):
        super().__init__(*args, **kwargs)
        if available_reviewers is not None:
            self.fields['reviewer'].queryset = available_reviewers
        
        # Make deadline optional
        self.fields['deadline'].required = False


class BulkInviteForm(forms.Form):
    """Form for bulk inviting users to a team"""
    
    emails = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 6,
            'placeholder': 'Enter email addresses, one per line or separated by commas'
        }),
        help_text="Enter multiple email addresses separated by commas or new lines"
    )
    
    role = forms.ChoiceField(
        choices=TeamMembership.ROLES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        initial='member'
    )
    
    message = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Add a personal message to all invitations (optional)'
        }),
        required=False
    )
    
    def clean_emails(self):
        emails_text = self.cleaned_data.get('emails', '')
        
        # Split by comma or newline
        emails = []
        for line in emails_text.split('\n'):
            for email in line.split(','):
                email = email.strip()
                if email:
                    emails.append(email)
        
        # Validate each email
        from django.core.validators import validate_email
        validated_emails = []
        for email in emails:
            try:
                validate_email(email)
                validated_emails.append(email.lower())
            except ValidationError:
                raise ValidationError(f"Invalid email address: {email}")
        
        if not validated_emails:
            raise ValidationError("At least one valid email address is required.")
        
        if len(validated_emails) > 50:
            raise ValidationError("Cannot invite more than 50 users at once.")
        
        # Remove duplicates
        validated_emails = list(set(validated_emails))
        
        return validated_emails


class CommentReplyForm(forms.ModelForm):
    """Form for replying to comments"""
    
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Write your reply...',
                'required': True
            })
        }
    
    def clean_content(self):
        content = self.cleaned_data.get('content')
        if len(content.strip()) < 3:
            raise ValidationError("Reply must be at least 3 characters long.")
        return content