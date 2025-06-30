#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Forms
Forms for subscription management and billing
"""

from django import forms
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils import timezone

from .models import (
    SubscriptionTier, UserSubscription, PaymentMethod, 
    PromoCode, InstitutionalLicense
)


class SubscriptionUpgradeForm(forms.Form):
    """Form for upgrading subscription"""
    
    tier = forms.ModelChoiceField(
        queryset=SubscriptionTier.objects.filter(is_active=True),
        widget=forms.RadioSelect,
        empty_label=None
    )
    
    billing_cycle = forms.ChoiceField(
        choices=[
            ('monthly', 'Monthly'),
            ('yearly', 'Yearly'),
        ],
        widget=forms.RadioSelect,
        initial='monthly'
    )
    
    promo_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter promo code (optional)'
        })
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        
        if user:
            # Filter tiers based on user's current subscription
            try:
                current_subscription = UserSubscription.objects.get(user=user)
                current_price = current_subscription.get_monthly_price()
                
                # Only show higher tiers
                self.fields['tier'].queryset = SubscriptionTier.objects.filter(
                    is_active=True,
                    price_monthly__gt=current_price
                ).order_by('price_monthly')
                
            except UserSubscription.DoesNotExist:
                # No current subscription, show all tiers
                self.fields['tier'].queryset = SubscriptionTier.objects.filter(
                    is_active=True
                ).order_by('price_monthly')
    
    def clean_promo_code(self):
        """Validate promo code"""
        code = self.cleaned_data.get('promo_code')
        if code:
            try:
                promo = PromoCode.objects.get(code=code.upper())
                if not promo.is_valid():
                    raise ValidationError("This promo code is expired or invalid")
                if not promo.can_be_used_by(self.user):
                    raise ValidationError("You are not eligible for this promo code")
                return code.upper()
            except PromoCode.DoesNotExist:
                raise ValidationError("Invalid promo code")
        return code


class PaymentMethodForm(forms.ModelForm):
    """Form for adding payment method"""
    
    class Meta:
        model = PaymentMethod
        fields = [
            'billing_name', 'billing_address', 'billing_city',
            'billing_state', 'billing_zip', 'billing_country'
        ]
        widgets = {
            'billing_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Full name on card'
            }),
            'billing_address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 2,
                'placeholder': 'Street address'
            }),
            'billing_city': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City'
            }),
            'billing_state': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'State/Province'
            }),
            'billing_zip': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ZIP/Postal code'
            }),
            'billing_country': forms.Select(attrs={
                'class': 'form-select'
            })
        }
    
    stripe_payment_method_id = forms.CharField(
        widget=forms.HiddenInput()
    )
    
    set_as_default = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Set as default payment method'
    )


class CancelSubscriptionForm(forms.Form):
    """Form for canceling subscription"""
    
    CANCELLATION_REASONS = [
        ('too_expensive', 'Too expensive'),
        ('not_using', 'Not using enough'),
        ('missing_features', 'Missing features I need'),
        ('technical_issues', 'Technical issues'),
        ('found_alternative', 'Found better alternative'),
        ('temporary_pause', 'Temporary pause'),
        ('other', 'Other'),
    ]
    
    reason = forms.ChoiceField(
        choices=CANCELLATION_REASONS,
        widget=forms.RadioSelect,
        required=True,
        label='Why are you canceling?'
    )
    
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please share any additional feedback (optional)'
        }),
        required=False,
        label='Additional feedback'
    )
    
    immediate = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Cancel immediately (you will lose access right away)',
        help_text='If unchecked, you will retain access until the end of your current billing period'
    )
    
    confirm = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I understand that canceling will remove access to premium features'
    )


class PromoCodeForm(forms.Form):
    """Form for applying promo codes"""
    
    code = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={
            'class': 'form-control text-uppercase',
            'placeholder': 'Enter promo code',
            'style': 'text-transform: uppercase;'
        }),
        label='Promo Code'
    )
    
    def __init__(self, user=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
    
    def clean_code(self):
        """Validate and normalize promo code"""
        code = self.cleaned_data.get('code', '').upper()
        
        if not code:
            raise ValidationError("Promo code is required")
        
        try:
            promo = PromoCode.objects.get(code=code)
            
            if not promo.is_valid():
                raise ValidationError("This promo code is expired or no longer available")
            
            if self.user and not promo.can_be_used_by(self.user):
                if promo.new_users_only:
                    raise ValidationError("This promo code is only valid for new users")
                else:
                    raise ValidationError("You are not eligible for this promo code")
            
            return code
            
        except PromoCode.DoesNotExist:
            raise ValidationError("Invalid promo code")


class InstitutionalLicenseRequestForm(forms.Form):
    """Form for requesting institutional license"""
    
    INSTITUTION_TYPES = [
        ('university', 'University'),
        ('research_institute', 'Research Institute'), 
        ('corporate', 'Corporate'),
        ('government', 'Government'),
        ('nonprofit', 'Non-Profit'),
    ]
    
    institution_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your institution name'
        })
    )
    
    institution_type = forms.ChoiceField(
        choices=INSTITUTION_TYPES,
        widget=forms.Select(attrs={
            'class': 'form-select'
        })
    )
    
    domain = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'institution.edu'
        }),
        help_text='Your institutional email domain'
    )
    
    estimated_users = forms.IntegerField(
        min_value=10,
        max_value=10000,
        widget=forms.NumberInput(attrs={
            'class': 'form-control',
            'placeholder': '50'
        }),
        help_text='Estimated number of users'
    )
    
    contact_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your full name'
        })
    )
    
    contact_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@institution.edu'
        })
    )
    
    contact_title = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Your job title'
        })
    )
    
    use_case = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 4,
            'placeholder': 'Please describe how your institution plans to use SciTeX-Cloud'
        }),
        label='Use Case Description'
    )
    
    budget_range = forms.ChoiceField(
        choices=[
            ('', 'Select budget range'),
            ('under_1k', 'Under $1,000/month'),
            ('1k_5k', '$1,000 - $5,000/month'),
            ('5k_10k', '$5,000 - $10,000/month'),
            ('10k_25k', '$10,000 - $25,000/month'),
            ('25k_plus', '$25,000+/month'),
            ('custom', 'Custom pricing needed'),
        ],
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        required=False
    )
    
    def clean_domain(self):
        """Validate institutional domain"""
        domain = self.cleaned_data.get('domain', '').lower().strip()
        
        if not domain:
            raise ValidationError("Domain is required")
        
        # Remove protocol if included
        if domain.startswith('http'):
            raise ValidationError("Please enter just the domain (e.g., university.edu)")
        
        # Remove www if included
        if domain.startswith('www.'):
            domain = domain[4:]
        
        # Basic domain validation
        if '.' not in domain:
            raise ValidationError("Please enter a valid domain")
        
        # Check if domain already has license
        existing_license = InstitutionalLicense.objects.filter(
            domain__iexact=domain,
            is_active=True
        ).first()
        
        if existing_license:
            raise ValidationError("This domain already has an institutional license")
        
        return domain
    
    def clean_contact_email(self):
        """Validate contact email matches domain"""
        email = self.cleaned_data.get('contact_email', '').lower()
        domain = self.cleaned_data.get('domain', '').lower()
        
        if email and domain:
            email_domain = email.split('@')[1] if '@' in email else ''
            if email_domain != domain:
                raise ValidationError(
                    "Contact email must be from the institutional domain"
                )
        
        return email


class UsageExportForm(forms.Form):
    """Form for exporting usage data"""
    
    EXPORT_FORMATS = [
        ('csv', 'CSV'),
        ('json', 'JSON'),
        ('pdf', 'PDF Report'),
    ]
    
    EXPORT_PERIODS = [
        ('current_month', 'Current Month'),
        ('last_month', 'Last Month'),
        ('last_3_months', 'Last 3 Months'),
        ('last_6_months', 'Last 6 Months'),
        ('last_year', 'Last Year'),
        ('custom', 'Custom Date Range'),
    ]
    
    format = forms.ChoiceField(
        choices=EXPORT_FORMATS,
        widget=forms.RadioSelect,
        initial='csv'
    )
    
    period = forms.ChoiceField(
        choices=EXPORT_PERIODS,
        widget=forms.Select(attrs={
            'class': 'form-select'
        }),
        initial='current_month'
    )
    
    start_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    end_date = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        })
    )
    
    include_metadata = forms.BooleanField(
        required=False,
        initial=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='Include metadata and details'
    )
    
    def clean(self):
        """Validate date range for custom period"""
        cleaned_data = super().clean()
        period = cleaned_data.get('period')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if period == 'custom':
            if not start_date or not end_date:
                raise ValidationError("Start date and end date are required for custom period")
            
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")
            
            if (end_date - start_date).days > 365:
                raise ValidationError("Date range cannot exceed 1 year")
        
        return cleaned_data


class BillingContactForm(forms.Form):
    """Form for updating billing contact information"""
    
    billing_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Full name for billing'
        })
    )
    
    billing_email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'billing@example.com'
        }),
        help_text='Email address for invoices and billing communications'
    )
    
    company_name = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Company name (optional)'
        })
    )
    
    tax_id = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Tax ID / VAT number (optional)'
        })
    )