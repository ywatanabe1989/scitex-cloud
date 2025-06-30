"""
Forms for reference manager synchronization.
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError

from .models import (
    ReferenceManagerAccount,
    SyncProfile,
    ConflictResolution
)


class SyncProfileForm(forms.ModelForm):
    """Form for creating and editing sync profiles."""
    
    class Meta:
        model = SyncProfile
        fields = [
            'name',
            'description',
            'accounts',
            'auto_sync',
            'sync_frequency',
            'sync_direction',
            'conflict_resolution',
            'sync_collections',
            'sync_tags',
            'exclude_tags',
            'sync_pdfs',
            'sync_notes',
            'sync_attachments',
            'sync_after_date',
            'sync_before_date',
        ]
        
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter profile name'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional description of this sync profile'
            }),
            'accounts': forms.CheckboxSelectMultiple(attrs={
                'class': 'form-check-input'
            }),
            'auto_sync': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sync_frequency': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sync_direction': forms.Select(attrs={
                'class': 'form-select'
            }),
            'conflict_resolution': forms.Select(attrs={
                'class': 'form-select'
            }),
            'sync_collections': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'collection1, collection2, ... (leave empty for all)'
            }),
            'sync_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'tag1, tag2, ... (leave empty for all)'
            }),
            'exclude_tags': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'exclude_tag1, exclude_tag2, ...'
            }),
            'sync_pdfs': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sync_notes': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sync_attachments': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'sync_after_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'sync_before_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
        }
        
        help_texts = {
            'auto_sync': 'Enable automatic synchronization based on the frequency setting',
            'sync_frequency': 'How often to automatically sync (only applies if auto-sync is enabled)',
            'sync_direction': 'Direction of synchronization between local and remote',
            'conflict_resolution': 'How to handle conflicts when the same reference has different data locally and remotely',
            'sync_collections': 'Comma-separated list of collection names to sync (leave empty to sync all)',
            'sync_tags': 'Only sync references with these tags (leave empty to sync all)',
            'exclude_tags': 'Exclude references with these tags from sync',
            'sync_pdfs': 'Include PDF files in synchronization',
            'sync_notes': 'Include notes and annotations in synchronization',
            'sync_attachments': 'Include other attachments in synchronization',
            'sync_after_date': 'Only sync references published after this date',
            'sync_before_date': 'Only sync references published before this date',
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if self.user:
            # Filter accounts to only show user's accounts
            self.fields['accounts'].queryset = ReferenceManagerAccount.objects.filter(
                user=self.user,
                is_active=True
            )
        
        # Convert array fields to comma-separated strings for display
        if self.instance and self.instance.pk:
            if self.instance.sync_collections:
                self.fields['sync_collections'].initial = ', '.join(self.instance.sync_collections)
            if self.instance.sync_tags:
                self.fields['sync_tags'].initial = ', '.join(self.instance.sync_tags)
            if self.instance.exclude_tags:
                self.fields['exclude_tags'].initial = ', '.join(self.instance.exclude_tags)
    
    def clean_name(self):
        """Validate profile name is unique for user."""
        name = self.cleaned_data['name']
        
        # Check for existing profile with same name
        existing = SyncProfile.objects.filter(
            user=self.user,
            name=name
        )
        
        if self.instance and self.instance.pk:
            existing = existing.exclude(pk=self.instance.pk)
        
        if existing.exists():
            raise ValidationError("A sync profile with this name already exists.")
        
        return name
    
    def clean_accounts(self):
        """Validate at least one account is selected."""
        accounts = self.cleaned_data['accounts']
        
        if not accounts:
            raise ValidationError("At least one account must be selected.")
        
        return accounts
    
    def clean_sync_after_date(self):
        """Validate sync_after_date is not in the future."""
        date = self.cleaned_data.get('sync_after_date')
        
        if date:
            from django.utils import timezone
            if date > timezone.now().date():
                raise ValidationError("Sync after date cannot be in the future.")
        
        return date
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        sync_after = cleaned_data.get('sync_after_date')
        sync_before = cleaned_data.get('sync_before_date')
        
        # Validate date range
        if sync_after and sync_before and sync_after >= sync_before:
            raise ValidationError("Sync after date must be before sync before date.")
        
        # Convert comma-separated strings back to arrays
        for field_name in ['sync_collections', 'sync_tags', 'exclude_tags']:
            field_value = cleaned_data.get(field_name, '')
            if isinstance(field_value, str) and field_value:
                # Convert to list and clean up
                items = [item.strip() for item in field_value.split(',') if item.strip()]
                cleaned_data[field_name] = items
            else:
                cleaned_data[field_name] = []
        
        return cleaned_data


class AccountConnectionForm(forms.Form):
    """Form for connecting to a reference manager account."""
    
    service = forms.ChoiceField(
        choices=[
            ('mendeley', 'Mendeley'),
            ('zotero', 'Zotero'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Select the reference manager service to connect to'
    )
    
    account_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: Custom name for this account'
        }),
        help_text='Optional custom name for this account (will be auto-detected if left empty)'
    )


class ConflictResolutionForm(forms.ModelForm):
    """Form for resolving synchronization conflicts."""
    
    RESOLUTION_CHOICES = [
        ('local_wins', 'Keep Local Version'),
        ('remote_wins', 'Keep Remote Version'),
        ('merged', 'Try to Merge'),
        ('manual', 'Manual Resolution'),
        ('skipped', 'Skip This Conflict'),
    ]
    
    resolution = forms.ChoiceField(
        choices=RESOLUTION_CHOICES,
        widget=forms.RadioSelect(attrs={
            'class': 'form-check-input'
        }),
        help_text='Choose how to resolve this conflict'
    )
    
    custom_value = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Enter custom value (only for manual resolution)'
        }),
        help_text='For manual resolution, enter the custom value as JSON'
    )
    
    resolution_notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Optional notes about this resolution'
        }),
        help_text='Optional notes about why this resolution was chosen'
    )
    
    class Meta:
        model = ConflictResolution
        fields = ['resolution', 'resolution_notes']
    
    def clean_custom_value(self):
        """Validate custom value is valid JSON if provided."""
        custom_value = self.cleaned_data.get('custom_value', '')
        resolution = self.cleaned_data.get('resolution')
        
        if resolution == 'manual' and custom_value:
            try:
                import json
                json.loads(custom_value)
            except json.JSONDecodeError:
                # If it's not valid JSON, treat it as a string value
                pass
        
        return custom_value


class BulkImportForm(forms.Form):
    """Form for bulk importing references."""
    
    FORMAT_CHOICES = [
        ('bibtex', 'BibTeX (.bib)'),
        ('json', 'JSON (.json)'),
        ('csv', 'CSV (.csv)'),
        ('ris', 'RIS (.ris)'),
    ]
    
    file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.bib,.json,.csv,.ris'
        }),
        help_text='Select a file to import references from'
    )
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='File format (will be auto-detected if not specified)'
    )
    
    profile = forms.ModelChoiceField(
        queryset=SyncProfile.objects.none(),
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False,
        help_text='Optional: Associate imported references with a sync profile'
    )
    
    create_collections = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Create collections mentioned in the import file'
    )
    
    overwrite_existing = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Overwrite existing references with matching DOI or title'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['profile'].queryset = SyncProfile.objects.filter(user=user)
    
    def clean_file(self):
        """Validate uploaded file."""
        file = self.cleaned_data['file']
        
        # Check file size (max 10MB)
        if file.size > 10 * 1024 * 1024:
            raise ValidationError("File size cannot exceed 10MB.")
        
        # Check file extension
        allowed_extensions = ['.bib', '.json', '.csv', '.ris', '.txt']
        file_extension = '.' + file.name.lower().split('.')[-1]
        
        if file_extension not in allowed_extensions:
            raise ValidationError(
                f"Unsupported file format. Allowed formats: {', '.join(allowed_extensions)}"
            )
        
        return file


class BulkExportForm(forms.Form):
    """Form for bulk exporting references."""
    
    FORMAT_CHOICES = [
        ('bibtex', 'BibTeX (.bib)'),
        ('json', 'JSON (.json)'),
        ('csv', 'CSV (.csv)'),
        ('ris', 'RIS (.ris)'),
        ('endnote', 'EndNote (.enw)'),
    ]
    
    format = forms.ChoiceField(
        choices=FORMAT_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Export format'
    )
    
    profile = forms.ModelChoiceField(
        queryset=SyncProfile.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Optional: Export only references from a specific sync profile'
    )
    
    collection = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Optional: Specific collection name'
        }),
        help_text='Optional: Export only references from a specific collection'
    )
    
    include_files = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Include attached files in export (creates a ZIP file)'
    )
    
    date_range = forms.ChoiceField(
        choices=[
            ('all', 'All references'),
            ('last_month', 'Last month'),
            ('last_year', 'Last year'),
            ('custom', 'Custom date range'),
        ],
        initial='all',
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Date range filter'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='Start date for custom range'
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        help_text='End date for custom range'
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['profile'].queryset = SyncProfile.objects.filter(user=user)
    
    def clean(self):
        """Validate form data."""
        cleaned_data = super().clean()
        
        date_range = cleaned_data.get('date_range')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        # Validate custom date range
        if date_range == 'custom':
            if not start_date:
                raise ValidationError("Start date is required for custom range.")
            if not end_date:
                raise ValidationError("End date is required for custom range.")
            if start_date >= end_date:
                raise ValidationError("Start date must be before end date.")
        
        return cleaned_data


class SyncScheduleForm(forms.Form):
    """Form for configuring sync schedule."""
    
    FREQUENCY_CHOICES = [
        ('never', 'Never (Manual only)'),
        ('hourly', 'Every hour'),
        ('daily', 'Daily'),
        ('weekly', 'Weekly'),
        ('monthly', 'Monthly'),
    ]
    
    DAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]
    
    HOUR_CHOICES = [(i, f"{i:02d}:00") for i in range(24)]
    
    frequency = forms.ChoiceField(
        choices=FREQUENCY_CHOICES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='How often to automatically sync'
    )
    
    time_of_day = forms.ChoiceField(
        choices=HOUR_CHOICES,
        initial=2,  # 2 AM
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='What time of day to sync (24-hour format)'
    )
    
    day_of_week = forms.ChoiceField(
        choices=DAY_CHOICES,
        initial=0,  # Monday
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        help_text='Day of week for weekly sync'
    )
    
    enabled = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        help_text='Enable automatic syncing'
    )


class FilterForm(forms.Form):
    """Form for filtering sync sessions and conflicts."""
    
    STATUS_CHOICES = [
        ('', 'All statuses'),
        ('pending', 'Pending'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CONFLICT_STATUS_CHOICES = [
        ('', 'All conflicts'),
        ('pending', 'Pending resolution'),
        ('resolved', 'Resolved'),
    ]
    
    status = forms.ChoiceField(
        choices=STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm'
        })
    )
    
    profile = forms.ModelChoiceField(
        queryset=SyncProfile.objects.none(),
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-select form-select-sm'
        })
    )
    
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date'
        })
    )
    
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control form-control-sm',
            'type': 'date'
        })
    )
    
    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        if user:
            self.fields['profile'].queryset = SyncProfile.objects.filter(user=user)
            # Add empty option
            self.fields['profile'].empty_label = "All profiles"