16,769 lines & 52,865 words

# Repository View
#### Repository: `/home/ywatanabe/proj/scitex-cloud`
#### Output: `/home/ywatanabe/proj/scitex-cloud/viewed.md`

## Configurations
##### Tree:
- Maximum depth: 3
- .gitignore respected
- Blacklist expresssions:
```plaintext
node_modules,.*,*.py[cod],__pycache__,*.elc,env,env-[0-9]*.[0-9]*,[1-2][0-9][0-9
][0-9]Y-*,htmlcov,*.sif,*.img,*.image,*.sandbox,*.log,logs,build,dist,*_back,*_b
ackup,*old*,.old,RUNNING,FINISHED
```

#### File content:
- Number of head: 50
- Whitelist extensions:
```plaintext
.txt,.md,.org,.el,.sh,.py,.yaml,.yml,.json,.def
```
- Blacklist expressions:
```plaintext
*.mat,*.npy,*.npz,*.csv,*.pkl,*.jpg,*.jpeg,*.mp4,*.pth,*.db*,*.out,*.err,*.cbm,*
.pt,*.egg-info,*.aux,*.pdf,*.png,*.tiff,*.wav
```


## Tree contents
.
├── apps
│   ├── auth_app
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── validators.py
│   │   └── views.py
│   ├── billing_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── cloud_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── forms.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── code_app
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── default_workspace_views.py
│   │   ├── environment_manager.py
│   │   ├── __init__.py
│   │   ├── jupyter_utils.py
│   │   ├── models.py
│   │   ├── project_views.py
│   │   ├── repository_integration.py
│   │   ├── urls.py
│   │   ├── views.py
│   │   └── visualization_pipeline.py
│   ├── core_app
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── context_processors.py
│   │   ├── dashboard_views.py
│   │   ├── directory_manager.py
│   │   ├── directory_urls.py
│   │   ├── directory_views.py
│   │   ├── github_views.py
│   │   ├── __init__.py
│   │   ├── middleware.py
│   │   ├── model_imports.py
│   │   ├── models.py
│   │   ├── permissions.py
│   │   ├── services.py
│   │   ├── signals.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── dev_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── docs_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── __init__.py
│   ├── integrations_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── permissions_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── decorators.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── README.md
│   │   ├── services.py
│   │   ├── tests.py
│   │   └── views.py
│   ├── profile_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   └── signals.py
│   ├── project_app
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── decorators.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── user_urls.py
│   │   └── views.py
│   ├── scholar_app
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── bibtex_models.py
│   │   ├── bibtex_views.py
│   │   ├── default_workspace_views.py
│   │   ├── doi_services.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── project_views.py
│   │   ├── repository_services.py
│   │   ├── repository_views.py
│   │   ├── simple_views.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   ├── utils.py
│   │   └── views.py
│   ├── viz_app
│   │   ├── admin.py
│   │   ├── api_views.py
│   │   ├── apps.py
│   │   ├── code_integration.py
│   │   ├── default_workspace_views.py
│   │   ├── __init__.py
│   │   ├── models.py
│   │   ├── project_views.py
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   └── writer_app
│       ├── admin.py
│       ├── ai_assistant.py
│       ├── apps.py
│       ├── arxiv_formatters.py
│       ├── arxiv_services.py
│       ├── arxiv_views.py
│       ├── consumers.py
│       ├── default_workspace_views.py
│       ├── __init__.py
│       ├── models.py
│       ├── operational_transform.py
│       ├── operational_transforms.py
│       ├── repository_integration.py
│       ├── routing.py
│       ├── simple_views.py
│       ├── tests.py
│       ├── TODO.md
│       ├── urls.py
│       ├── utils.py
│       ├── version_control.py
│       └── views.py
├── CLAUDE.md
├── config
│   ├── asgi.py
│   ├── __init__.py
│   ├── logger.py
│   ├── README.md
│   ├── routing.py
│   ├── settings
│   │   ├── __init__.py
│   │   ├── settings_dev.py
│   │   ├── settings_prod.py
│   │   └── settings_shared.py
│   ├── urls.py
│   └── wsgi.py
├── docs
│   ├── APP_REORGANIZATION_SUMMARY.md
│   ├── BROWSER_REFRESH_NEEDED.md
│   ├── DARK_MODE_IMPLEMENTATION.md
│   ├── DATABASE_REFRESH_SUMMARY.md
│   ├── DOCUMENTATION_HOSTING_GUIDE.md
│   ├── examples
│   │   └── 000_ENV_SCITEX.src.example
│   ├── GITHUB_LAYOUT_COMPLETE.md
│   ├── GITHUB_STYLE_COMPLETE.md
│   ├── GITHUB_STYLE_IMPROVEMENTS.md
│   ├── GUEST_PROJECT_NAVIGATION.md
│   ├── IMPLEMENTATION_SUMMARY_WRITER_INTEGRATION.md
│   ├── installation.md
│   ├── INTEGRATIONS_ACTIVATION_CHECKLIST.md
│   ├── INTEGRATIONS_DEPLOYED.md
│   ├── INTEGRATIONS_IMPLEMENTATION_SUMMARY.md
│   ├── INTEGRATIONS_SETUP.md
│   ├── monetization_plans.md
│   ├── NAVIGATION_SUMMARY.md
│   ├── PASSWORD_RESET_IMPLEMENTATION.md
│   ├── REFACTORING_PLAN_FROM_USER.md
│   ├── REFACTORING_PLAN.md
│   ├── REORGANIZATION_COMPLETE.md
│   ├── SCHOLAR_AUTHENTICATION_ANALYSIS.md
│   ├── SCHOLAR_INTEGRATION_STRATEGY.md
│   ├── SCITEX_STANDALONE_PLAN.md
│   ├── SCITEX_WRITER_TEMPLATE_USAGE.md
│   ├── SINGLE_SOURCE_OF_TRUTH.md
│   ├── TEMPLATE_CLEANUP_PLAN.md
│   ├── TERMINOLOGY_GITHUB_ALIGNMENT.md
│   ├── tex_templates
│   │   ├── abstract_minimal.tex
│   │   ├── discussion_minimal.tex
│   │   ├── highlights_minimal.tex
│   │   ├── introduction_minimal.tex
│   │   ├── methods_minimal.tex
│   │   └── results_minimal.tex
│   ├── to_claude
│   │   └── section_writing_guidelines.json
│   ├── URL_STRUCTURE.md
│   ├── V1_QUICK_START.md
│   ├── values_mission_vision_how-to-write.md
│   └── values_mission_vision.md
├── externals
│   ├── impact_factor
│   │   ├── build.sh
│   │   ├── MANIFEST.in
│   │   ├── README.md
│   │   └── setup.py
│   ├── install_externals.sh
│   ├── INTEGRATION_COMPLETE.md
│   ├── integration_status.json
│   └── README.md
├── manage.py
├── package.json
├── project_management
│   ├── accessibility-improvements-20250521.md
│   ├── advancement-priorities-20250628.md
│   ├── AGENT_BULLETIN_BOARD.md
│   ├── airight-comparison-20250522.md
│   ├── autonomous-development-final-summary-20250522.md
│   ├── autonomous-development-session-summary-20250522.md
│   ├── bug-reports
│   │   ├── bug-report-dashboard-directory-structure-not-shown.md
│   │   ├── bug-report-github-sync-authentication.md
│   │   └── bug-report-github-sync-not-working.md
│   ├── bug-report-signup-2025-0521.md
│   ├── BULLETIN-BOARD.md
│   ├── CLAUDE_PLAN.md
│   ├── cleanup-plan-2025-0521-030635.md
│   ├── cleanup-plan-2025-0521-051500.md
│   ├── cleanup-summary-2025-0521-030635.md
│   ├── cleanup-summary-2025-0521-032740.md
│   ├── cleanup-summary-2025-0521-051500.md
│   ├── cloud-integration-roadmap.md
│   ├── color-update-scitex-800-20250523.md
│   ├── create_cache_table.py
│   ├── css-refactoring-plan.md
│   ├── daily-development-summary-20250523.md
│   ├── deployment-progress-20250106.md
│   ├── deployment-readiness-final-20250523.md
│   ├── deployment-success-20250106.md
│   ├── design-system-enhancement-20250522.md
│   ├── development-session-20250523-final.md
│   ├── development-summary-20250523.md
│   ├── django-dev-session-20250523.md
│   ├── django-structure-implementation-plan.md
│   ├── feature_requests
│   │   ├── feature-request-cloud-computing-integration.md
│   │   ├── feature-request-code-enhanced-page.md
│   │   ├── feature-request-common-css.md
│   │   ├── feature-request-concept-pages.md
│   │   ├── feature-request-default-project-structure-enhancements.md
│   │   ├── feature-request-fundraising-page.md
│   │   ├── feature-request-github-integration-enhancement.md
│   │   ├── feature-request-landing-page.md
│   │   ├── feature-request-legal-and-contact-pages.md
│   │   ├── feature-request-local-html-server.md
│   │   ├── feature-request-modularity-messaging.md
│   │   ├── feature-request-module-card-formatting.md
│   │   ├── feature-request-module-ordering-and-coming-soon-status.md
│   │   ├── feature-request-naming-branding-strategy.md
│   │   ├── feature-request-reflect-products.md
│   │   ├── feature-request-remove-redundant-scitex-branding.md
│   │   ├── feature-request-remove-unnecessary-pages.md
│   │   ├── feature-request-system-requirements-clarification.md
│   │   ├── feature-request-viz-enhanced-page.md
│   │   └── feature-request-windows-chrome-access.md
│   ├── fixes-summary-20250522.md
│   ├── github-buttons-landing-page-summary.md
│   ├── git-setup-summary-2025-0522.md
│   ├── header-footer-implementation-summary.md
│   ├── implementation-summary-local-dev-server.md
│   ├── modularity-implementation-summary.md
│   ├── monitoring-system-implementation-20250627.md
│   ├── naming-quick-reference.md
│   ├── navigation-improvements-20250522.md
│   ├── next_steps-20250521-030455.md
│   ├── optimization-implementation-20250523.md
│   ├── optimization-opportunities-20250523.md
│   ├── platform-health-check-20250523.md
│   ├── platform-readiness-assessment-20250523.md
│   ├── pre-deployment-security-checklist.md
│   ├── progress-development-server-complete.md
│   ├── progress-module-ordering-ux-improvements-20250628.md
│   ├── progress-SciTeX-Design-System-20250522.md
│   ├── progress-SciTeX-Web-20250521-030455.md
│   ├── progress-SciTeX-Web-20250521-030455.mmd
│   ├── progress-TDD-20250521-031917.md
│   ├── progress-TDD-20250521-031917.mmd
│   ├── project-advancement-priorities.md
│   ├── revised-english-content.md
│   ├── scitex-color-implementation-summary.md
│   ├── scitex.service
│   ├── seo-enhancements-20250523.md
│   ├── server
│   ├── settings-fixes-20250522.md
│   ├── stop.sh
│   ├── structure-improvement-plan.md
│   ├── system-requirements-implementation-summary.md
│   ├── timeline-20250627.mmd
│   ├── url-namespace-fix-20250522.md
│   └── USER_PLAN.md
├── README.md
├── run
│   └── scitex.pid
├── scripts
│   ├── build_all_docs.sh
│   ├── build_module_docs.sh
│   ├── create_viz_demo.sh
│   ├── create_viz_demo_video.sh
│   ├── demo.py
│   ├── dev
│   │   ├── monitor.sh
│   │   ├── start_dev_background.sh
│   │   ├── start_dev.sh
│   │   └── start_dev_windows.sh
│   ├── format_django_templates.sh
│   ├── format_templates.py
│   ├── prod
│   │   ├── deploy_prod.sh
│   │   ├── monitor_prod.sh
│   │   └── start_prod.sh
│   ├── scitex_server.sh
│   ├── start
│   ├── stop
│   └── utils
│       ├── check_logs.sh
│       ├── create_initial_user.py
│       ├── create_user.py
│       ├── reset_accounts.py
│       ├── reset_database_with_permissions.py
│       ├── setup_externals.sh
│       ├── system_validation.py
│       └── update_user_info.py
├── server.sh -> scripts/scitex_server.sh
├── static
│   ├── brain-icon-preview.html
│   ├── css
│   │   ├── github_header.css
│   │   └── README.md
│   ├── _favicon.ico
│   ├── images
│   │   ├── favicon.ico -> favicon-white.svg
│   │   └── README.md
│   ├── js
│   │   ├── collaborative-editor.js
│   │   ├── darkmode.js
│   │   ├── dashboard.js
│   │   ├── document-manager.js
│   │   ├── dropdown.js
│   │   ├── jupyter-notebook.js
│   │   ├── landing.js
│   │   ├── main.js
│   │   ├── module-cards.js
│   │   ├── onboarding.js
│   │   ├── profile-manager.js
│   │   ├── project-manager.js
│   │   ├── test-dropdown.js
│   │   ├── theme-switcher.js
│   │   ├── viz-interface.js
│   │   └── writer_collaboration.js
│   └── videos
│       └── README.md
├── stop.sh
├── templates
│   ├── base.html -> global_base.html
│   ├── github_base.html
│   ├── global_base.html
│   └── partials
│       ├── global_body_scripts.html
│       ├── global_footer.html
│       ├── global_header.html
│       ├── global_head_meta.html
│       ├── global_head_styles.html
│       └── README.md
├── __tests__
│   ├── dashboard.test.js
│   ├── document-management.test.js
│   ├── profile-management.test.js
│   └── project-management.test.js
├── tests
│   ├── custom
│   │   ├── test_citation_export.py
│   │   ├── test_otp_email.py
│   │   └── test_simple_citation.py
│   ├── js
│   │   ├── jest.config.js
│   │   └── jest.setup.js
│   ├── run_tests.sh
│   ├── _test_api_integration.py
│   ├── _test_api.py
│   ├── _test_app.py
│   ├── _test_config.py
│   ├── _test_django_models.py
│   ├── test_email.py
│   ├── test_forgot_password.py
│   ├── _test_production_login.py
│   ├── _test_project_redirects.py
│   ├── _test_views.py
│   └── _test_web_login.py
├── tmp
│   └── create_test_user.py
├── TODOS
│   ├── COLLABORATOR_UI.md
│   ├── FUTURE.md
│   ├── GITHUB_LAYOUT.md
│   ├── GUEST_COLLABORATORS.md
│   ├── INTEGRATIONS.md
│   ├── OUR_CODE_REFERENCES.md
│   ├── PERMISSIONS_SYSTEM.md
│   ├── REPOSITORY.md
│   ├── SCHOLAR.md
│   ├── SOCIAL.md
│   ├── TEMPLATES.md
│   ├── URL_NAVIGATION.md
│   └── WRITER.md
└── viewed.md


## File contents

### `./apps/auth_app/admin.py`

```python
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, EmailVerification


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Profile Information', {
            'fields': ('profession', 'research_field', 'institution', 'bio')
        }),
        ('Verification', {
            'fields': ('is_academic_verified',),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'weekly_digest'),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': ('last_login_at', 'total_login_count', 'profile_completed', 'profile_completion_date'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('is_academic_verified', 'profile_completed', 'profile_completion_date', 'last_login_at')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'user__username')
    readonly_fields = ('created_at', 'verified_at')
    
    def has_change_permission(self, request, obj=None):
        # Make email verifications read-only after creation
        return False


...
```


### `./apps/auth_app/api_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
API endpoints for email verification
"""
from django.http import JsonResponse
from django.contrib.auth.models import User
from django.contrib.auth import login
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
import json
import logging

from .models import EmailVerification
from apps.core_app.services import EmailService

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["POST"])
def verify_email_api(request):
    """API endpoint to verify email with OTP code"""
    try:
        data = json.loads(request.body)
        email = data.get('email', '').strip()
        otp_code = data.get('otp_code', '').strip()

        if not email or not otp_code:
            return JsonResponse({
                'success': False,
                'error': 'Email and verification code are required.'
            }, status=400)

        # Find the most recent verification for this email
        try:
            verification = EmailVerification.objects.filter(
                email=email,
                is_verified=False
            ).order_by('-created_at').first()

            if not verification:
                return JsonResponse({
                    'success': False,
                    'error': 'No pending verification found for this email.'
                }, status=404)

            # Check if verification has expired
            if verification.is_expired():

...
```


### `./apps/auth_app/apps.py`

```python
from django.apps import AppConfig


class AuthAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.auth_app'
    verbose_name = 'Authentication & User Management'
    
    def ready(self):
        """Initialize the app when Django starts."""
        pass
...
```


### `./apps/auth_app/forms.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django import forms
from django.contrib.auth.models import User
import re


class SignupForm(forms.Form):
    """Form for user registration."""
    username = forms.CharField(
        max_length=39,  # GitHub's maximum username length
        min_length=1,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Choose a username (e.g., john-doe-42)'
        }),
        help_text='Username may only contain alphanumeric characters, hyphens, and underscores. Cannot begin or end with a hyphen.'
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'your.email@example.com'
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
    )
    password2 = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        }),
        label='Confirm Password'
    )
    agree_terms = forms.BooleanField(
        required=True,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input'
        }),
        label='I agree to the Terms of Service and Privacy Policy'
    )

    def clean_username(self):
        """Validate username follows GitHub-style rules and is unique."""
        username = self.cleaned_data['username']


...
```


### `./apps/auth_app/__init__.py`

```python

...
```


### `./apps/auth_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


# Japanese Academic domains to recognize
JAPANESE_ACADEMIC_DOMAINS = [
    # Japanese Academic (.ac.jp) - All academic institutions
    '.ac.jp',
    '.u-tokyo.ac.jp', '.kyoto-u.ac.jp', '.osaka-u.ac.jp',
    '.tohoku.ac.jp', '.nagoya-u.ac.jp', '.kyushu-u.ac.jp',
    '.hokudai.ac.jp', '.tsukuba.ac.jp', '.hiroshima-u.ac.jp',
    '.kobe-u.ac.jp', '.waseda.jp', '.keio.ac.jp',
    
    # Government Research Institutions (.go.jp)
    '.go.jp',  # Broader government research support
    '.riken.jp', '.aist.go.jp', '.nict.go.jp', '.jaxa.jp',
    '.jst.go.jp', '.nims.go.jp', '.nies.go.jp'
]


def is_japanese_academic_email(email):
    """Check if email belongs to Japanese academic institution"""
    if not email:
        return False
    try:
        domain = email.lower().split('@')[1]
        # Check if domain matches exactly or ends with the academic domain
        for academic_domain in JAPANESE_ACADEMIC_DOMAINS:
            # Remove leading dot for exact matching
            clean_domain = academic_domain.lstrip('.')
            if domain == clean_domain or domain.endswith(academic_domain):
                return True
        return False
    except (IndexError, AttributeError):
        return False


class UserProfile(models.Model):
    """Extended user profile for SciTeX users"""
    
    PROFESSION_CHOICES = [
        ('student', 'Student (Undergraduate/Graduate)'),
        ('researcher', 'Researcher/Postdoc'),
        ('professor', 'Professor/Faculty'),
        ('industry', 'Industry Professional'),
        ('independent', 'Independent Researcher'),

...
```


### `./apps/auth_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/auth_app/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:00:52 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/auth_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/auth_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.urls import path

from . import views
from . import api_views

app_name = "auth_app"

urlpatterns = [
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    path(
        "reset-password/<str:uidb64>/<str:token>/",
        views.reset_password,
        name="reset-password",
    ),
    path("verify-email/", views.verify_email, name="verify-email"),
    path("delete-account/", views.delete_account, name="delete-account"),

    # API endpoints for email verification
    path("api/verify-email/", api_views.verify_email_api, name="api-verify-email"),
    path("api/resend-otp/", api_views.resend_otp_api, name="api-resend-otp"),
]

# EOF

...
```


### `./apps/auth_app/validators.py`

```python
"""Username validation for SciTeX Cloud"""


def get_reserved_usernames():
    """
    Get dynamically generated list of reserved usernames.
    Syncs with RESERVED_PATHS from config.urls
    """
    try:
        from config.urls import RESERVED_PATHS
        # Remove file extensions and convert to set
        reserved = set()
        for path in RESERVED_PATHS:
            # Remove extensions like .ico, .txt, .xml
            path_clean = path.split('.')[0]
            reserved.add(path_clean)

        # Add guest prefix (for guest sessions)
        reserved.add('guest')

        return reserved
    except ImportError:
        # Fallback if import fails
        return {
            'admin', 'api', 'auth', 'billing', 'cloud', 'code', 'core',
            'dev', 'docs', 'integrations', 'project', 'scholar', 'viz', 'writer',
            'new', 'static', 'media', 'guest',
            'about', 'help', 'support', 'contact', 'terms', 'privacy',
            'settings', 'dashboard', 'profile', 'account', 'login', 'logout',
            'signup', 'register', 'reset', 'verify', 'confirm',
        }


def is_username_reserved(username):
    """
    Check if username is reserved and cannot be used.

    Args:
        username: Username to check

    Returns:
        bool: True if reserved, False if available
    """
    if not username:
        return True

    username_lower = username.lower()
    reserved_usernames = get_reserved_usernames()

    # Check exact match

...
```


### `./apps/auth_app/views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.conf import settings

from .forms import SignupForm, LoginForm
from .models import UserProfile


def signup(request):
    """User signup view with email verification required."""
    import logging
    from apps.core_app.services import EmailService

    logger = logging.getLogger(__name__)

    if request.method == "POST":
        form = SignupForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data["email"]
            username = form.cleaned_data["username"]
            password = form.cleaned_data["password"]

            # Check if email is already registered
            if User.objects.filter(email=email).exists():
                messages.error(request, "An account with this email already exists.")
                return render(request, "auth_app/signup.html", {"form": form})

            # Create inactive user (cannot log in until email verified)
            user = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                is_active=False,  # User inactive until email verified
            )

            # Create user profile (should be auto-created by signal, but ensure it exists)
            UserProfile.objects.get_or_create(user=user)

            # Create email verification record
            from .models import EmailVerification
            verification = EmailVerification.objects.create(
                user=user,

...
```


### `./apps/billing_app/admin.py`

```python
from django.contrib import admin

# Register your models here.

...
```


### `./apps/billing_app/apps.py`

```python
from django.apps import AppConfig


class BillingAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing_app'
    verbose_name = 'Billing and Subscriptions'

...
```


### `./apps/billing_app/__init__.py`

```python

...
```


### `./apps/billing_app/models.py`

```python
from django.db import models

# Create your models here.

...
```


### `./apps/billing_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/billing_app/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:01:04 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/billing_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/billing_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
from django.urls import path

from . import views

app_name = "billing"

urlpatterns = [
    # Pricing and subscription pages
    path("pricing/", views.pricing, name="pricing"),
    path("subscribe/", views.premium_subscription, name="subscribe"),
    path("donation/success/", views.donation_success, name="donation_success"),
    path("premium/", views.premium_subscription, name="premium"),
    path("fundraising/", views.fundraising, name="fundraising"),
    path(
        "donation-success/<int:donation_id>/",
        views.donation_success,
        name="donation-success",
    ),
]

# EOF

...
```


### `./apps/billing_app/views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations
from django.shortcuts import render, redirect


def pricing(request):
    """Display pricing plans."""
    return render(request, 'billing_app/pricing.html')


def premium_subscription(request):
    """Premium subscription page."""
    return render(request, 'billing_app/premium_subscription.html')


def donation_success(request, donation_id=None):
    """Donation success page."""
    return render(request, 'billing_app/donation_success.html')


def fundraising(request):
    """Fundraising page - delegates to cloud_app for now."""
    return redirect('cloud_app:fundraising')

# EOF

...
```


### `./apps/cloud_app/admin.py`

```python
from django.contrib import admin
from .models import (
    EmailVerification, Donation, DonationTier,
    SubscriptionPlan, Subscription, CloudResource,
    APIKey, ServiceIntegration
)

@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ['email', 'code', 'is_verified', 'created_at']
    list_filter = ['is_verified', 'created_at']
    search_fields = ['email']
    readonly_fields = ['created_at']

@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = ['donor_name', 'donor_email', 'amount', 'status', 'created_at']
    list_filter = ['status', 'payment_method', 'created_at']
    search_fields = ['donor_name', 'donor_email', 'transaction_id']
    readonly_fields = ['created_at', 'completed_at']

@admin.register(DonationTier)
class DonationTierAdmin(admin.ModelAdmin):
    list_display = ['name', 'minimum_amount', 'is_active']
    list_filter = ['is_active']
    ordering = ['minimum_amount']

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'max_projects', 'storage_gb', 'is_featured', 'is_active']
    list_filter = ['plan_type', 'is_featured', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'price_monthly', 'price_yearly', 'is_featured', 'is_active', 'display_order')
        }),
        ('Resource Limits', {
            'fields': ('max_projects', 'storage_gb', 'cpu_cores', 'gpu_vram_gb')
        }),
        ('Feature Flags', {
            'fields': ('has_watermark', 'requires_citation', 'requires_archive', 
                      'has_priority_support', 'has_custom_integrations', 'has_team_collaboration')
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_start', 'current_period_end']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']

...
```


### `./apps/cloud_app/apps.py`

```python
from django.apps import AppConfig


class CloudAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cloud_app'
    verbose_name = 'Cloud'
...
```


### `./apps/cloud_app/forms.py`

```python
from django import forms
from django.core.mail import send_mail
from django.conf import settings
from .models import Donation, EmailVerification
import logging

logger = logging.getLogger('scitex')


class DonationForm(forms.ModelForm):
    """Form for processing donations."""
    
    class Meta:
        model = Donation
        fields = ['donor_name', 'donor_email', 'amount', 'payment_method', 
                  'is_public', 'message']
        widgets = {
            'donor_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'donor_email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'your.email@example.com'
            }),
            'amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'step': '0.01'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Optional: Leave a message (will be public if you choose)'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['is_public'].label = "List me as a public supporter"
        self.fields['message'].required = False


class EmailVerificationForm(forms.Form):
    """Form for email verification."""
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={

...
```


### `./apps/cloud_app/__init__.py`

```python

...
```


### `./apps/cloud_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import random
import string
import uuid

class EmailVerification(models.Model):
    """Model for storing email verification codes."""
    email = models.EmailField()
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-created_at']
    
    def save(self, *args, **kwargs):
        if not self.code:
            self.code = self.generate_code()
        super().save(*args, **kwargs)
    
    def is_expired(self):
        """Check if code is expired (15 minutes validity)."""
        return timezone.now() > self.created_at + timezone.timedelta(minutes=15)
    
    @classmethod
    def generate_code(cls):
        """Generate a 6-digit verification code."""
        return ''.join(random.choices(string.digits, k=6))
    
    def __str__(self):
        return f"{self.email} - {self.code}"


class Donation(models.Model):
    """Model for tracking donations."""
    PAYMENT_METHODS = [
        ('credit_card', 'Credit Card'),
        ('paypal', 'PayPal'),
        ('github', 'GitHub Sponsors'),
        ('bank_transfer', 'Bank Transfer'),
    ]
    
    DONATION_STATUS = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('refunded', 'Refunded'),
    ]

...
```


### `./apps/cloud_app/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SubscriptionPlan, Subscription, EmailVerification, Donation


class SubscriptionPlanTestCase(TestCase):
    def setUp(self):
        self.plan = SubscriptionPlan.objects.create(
            name="Test Plan",
            plan_type="test",
            price_monthly=50,
            price_yearly=500,
            max_projects=10,
            storage_gb=100,
            cpu_cores=4,
            gpu_vram_gb=8
        )
    
    def test_plan_creation(self):
        self.assertEqual(self.plan.name, "Test Plan")
        self.assertEqual(self.plan.price_monthly, 50)
        self.assertTrue(self.plan.is_active)
    
    def test_plan_string_representation(self):
        self.assertEqual(str(self.plan), "Test Plan - $50/month")


class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_index_page(self):
        response = self.client.get(reverse('cloud_app:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'SciTeX')
    
    def test_features_page(self):
        response = self.client.get(reverse('cloud_app:features'))
        self.assertEqual(response.status_code, 200)
    
    def test_pricing_page(self):
        # Create some test plans
        SubscriptionPlan.objects.create(
            name="Free",

...
```


### `./apps/cloud_app/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:00:47 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/cloud_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/cloud_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import redirect
from django.urls import path

from . import views

app_name = "cloud_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("cloud/", lambda request: redirect("cloud_app:index"), name="cloud"),
    # Concept and vision pages
    path("vision/", views.vision, name="vision"),
    path("publications/", views.publications, name="publications"),
    path("contributors/", views.contributors, name="contributors"),
    # Support pages
    path("donate/", views.donate, name="donate"),
    # Legal and contact pages
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("terms/", views.terms_of_use, name="terms"),
    path("cookies/", views.cookie_policy, name="cookies"),
    # Demo page
    path("demo/", views.demo, name="demo"),
    # API Documentation
    path("api-docs/", views.api_docs, name="api-docs"),
]

# EOF

...
```


### `./apps/cloud_app/views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 05:41:11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/cloud_app/views.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/cloud_app/views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

import logging

from django.conf import settings
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db import models
from django.shortcuts import redirect, render
from django.utils import timezone

logger = logging.getLogger("scitex")


def index(request):
    """Cloud app index view - redirect logged-in users to their profile (GitHub-style)."""
    # If user is authenticated, redirect to their profile page (GitHub-style: /username/)
    if request.user.is_authenticated:
        return redirect(f'/{request.user.username}/')

    # Module features for landing page demos
    scholar_features = [
        {
            "title": "Multi-Source Search",
            "description": "Concurrent search across CrossRef, PubMed, OpenAlex, Semantic Scholar, and arXiv",
        },
        {
            "title": "Metadata Enrichment",
            "description": "Automatic retrieval of abstract, citation counts, and journal impact factor",
        },
        {
            "title": "PDF Downloads",
            "description": "PDF download with institutional authentication support. Extraction of text, tables, and figures",
        },
        {
            "title": "Local Library",
            "description": "Manage and search your local PDF collection. Compatible with Zotero.",
        },
        {

...
```


### `./apps/code_app/admin.py`

```python

...
```


### `./apps/code_app/api_views.py`

```python
#!/usr/bin/env python3
"""
API views for SciTeX-Code Jupyter notebook integration.
"""

import json
import logging
import threading
from typing import Dict, Any

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status

from .models import Notebook, CodeExecutionJob
from .jupyter_utils import (
    NotebookManager, NotebookExecutor, NotebookConverter, 
    NotebookTemplates, NotebookValidator
)

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class NotebookAPIView(View):
    """Base API view for notebook operations."""
    
    def get_notebook_manager(self):
        return NotebookManager(self.request.user)


class NotebookListAPI(NotebookAPIView):
    """API for listing and creating notebooks."""
    
    def get(self, request):
        """List user's notebooks."""
        try:
            notebooks = Notebook.objects.filter(user=request.user).order_by('-updated_at')
            
            # Pagination
            page = int(request.GET.get('page', 1))
            per_page = min(int(request.GET.get('per_page', 20)), 50)
            start = (page - 1) * per_page

...
```


### `./apps/code_app/apps.py`

```python
from django.apps import AppConfig


class CodeAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.code_app'
    verbose_name = 'Code'
...
```


### `./apps/code_app/default_workspace_views.py`

```python
"""Default workspace views for Code app."""
from django.shortcuts import render


def guest_session_view(request, username):
    """Guest session workspace for Code."""
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'module_name': 'Code',
        'module_icon': 'fa-code',
    }
    return render(request, 'code_app/default_workspace.html', context)


def user_default_workspace(request):
    """Default workspace for logged-in users without a specific project."""
    context = {
        'is_guest_session': False,
        'username': request.user.username if request.user.is_authenticated else None,
        'module_name': 'Code',
        'module_icon': 'fa-code',
    }
    return render(request, 'code_app/default_workspace.html', context)

...
```


### `./apps/code_app/environment_manager.py`

```python
#!/usr/bin/env python3
"""
Environment Management for SciTeX-Code
Provides reproducible Python environments with package management.
"""

import os
import json
import subprocess
import tempfile
import venv
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging
from datetime import datetime, timedelta

from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from .models import CodeExecutionJob

logger = logging.getLogger(__name__)


class EnvironmentError(Exception):
    """Raised when environment operations fail."""
    pass


class PackageRequirement:
    """Represents a Python package requirement."""
    
    def __init__(self, name: str, version: Optional[str] = None, 
                 source: str = 'pypi', extras: Optional[List[str]] = None):
        self.name = name
        self.version = version
        self.source = source
        self.extras = extras or []
    
    def __str__(self):
        """Return pip-compatible requirement string."""
        req = self.name
        if self.extras:
            req += f"[{','.join(self.extras)}]"
        if self.version:
            req += f"=={self.version}"
        return req
    

...
```


### `./apps/code_app/__init__.py`

```python

...
```


### `./apps/code_app/jupyter_utils.py`

```python
#!/usr/bin/env python3
"""
Jupyter notebook integration utilities for SciTeX-Code.
Provides secure notebook execution, conversion, and management.
"""

import os
import json
import subprocess
import tempfile
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

import nbformat
from nbconvert import HTMLExporter, PythonExporter, MarkdownExporter
from nbconvert.preprocessors import ExecutePreprocessor, ClearOutputPreprocessor
from jupyter_client import KernelManager
from django.conf import settings
from django.core.files.storage import default_storage
from django.utils import timezone

from .models import Notebook, CodeExecutionJob

logger = logging.getLogger(__name__)


class NotebookExecutionError(Exception):
    """Raised when notebook execution fails."""
    pass


class NotebookValidator:
    """Validates and sanitizes Jupyter notebooks."""
    
    @staticmethod
    def validate_notebook(notebook_content: dict) -> Tuple[bool, List[str]]:
        """
        Validate notebook structure and content.
        
        Returns:
            (is_valid, errors)
        """
        errors = []
        
        # Basic structure validation
        required_fields = ['cells', 'metadata', 'nbformat', 'nbformat_minor']
        for field in required_fields:
            if field not in notebook_content:

...
```


### `./apps/code_app/models.py`

```python
#!/usr/bin/env python3
"""
Models for SciTeX-Code application - secure Python code execution.
"""

import uuid
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class CodeExecutionJob(models.Model):
    """Track code execution jobs with security and resource monitoring."""
    
    JOB_STATUS = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('timeout', 'Timeout'),
        ('cancelled', 'Cancelled'),
    ]
    
    EXECUTION_TYPES = [
        ('script', 'Python Script'),
        ('notebook', 'Jupyter Notebook'),
        ('analysis', 'Data Analysis'),
        ('mngs', 'MNGS Function Call'),
    ]
    
    # Job identification
    job_id = models.UUIDField(default=uuid.uuid4, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='code_jobs')
    
    # Code and execution
    execution_type = models.CharField(max_length=20, choices=EXECUTION_TYPES, default='script')
    source_code = models.TextField()
    requirements = models.TextField(blank=True)  # pip requirements
    
    # Job status and results
    status = models.CharField(max_length=20, choices=JOB_STATUS, default='queued')
    output = models.TextField(blank=True)
    error_output = models.TextField(blank=True)
    return_code = models.IntegerField(null=True, blank=True)
    
    # Resource usage tracking
    cpu_time = models.FloatField(null=True, blank=True)  # CPU seconds
    memory_peak = models.BigIntegerField(null=True, blank=True)  # Peak memory in bytes
    execution_time = models.FloatField(null=True, blank=True)  # Wall clock time in seconds
    

...
```


### `./apps/code_app/project_views.py`

```python
"""
Project-specific views for Code app.
"""

from django.shortcuts import render, get_object_or_404
from apps.project_app.models import Project


def project_code(request, project_id):
    """Code interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    context = {
        'project': project,
    }
    return render(request, 'code_app/project_code.html', context)

...
```


### `./apps/code_app/repository_integration.py`

```python
"""
Repository integration for Code execution results.
Automatically sync code outputs, datasets, and analysis results to research data repositories.
"""

import os
import json
import logging
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Any
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction

from .models import CodeExecutionJob, DataAnalysisJob, Notebook, ResourceUsage
from apps.scholar_app.models import (
    Dataset, DatasetFile, RepositoryConnection, Repository
)
from apps.scholar_app.repository_services import (
    RepositoryServiceFactory, upload_dataset_to_repository
)

logger = logging.getLogger(__name__)


class CodeRepositoryIntegrator:
    """Service for integrating code execution results with data repositories"""
    
    def __init__(self, user, repository_connection: Optional[RepositoryConnection] = None):
        self.user = user
        self.repository_connection = repository_connection or self._get_default_connection()
        
    def _get_default_connection(self) -> Optional[RepositoryConnection]:
        """Get user's default repository connection"""
        return RepositoryConnection.objects.filter(
            user=self.user,
            is_default=True,
            status='active'
        ).first()
    
    def sync_code_execution_results(self, job: CodeExecutionJob, 
                                  auto_upload: bool = True) -> Optional[Dataset]:
        """Sync code execution results to repository"""
        
        if not self.repository_connection:
            logger.warning(f"No repository connection available for user {self.user.username}")
            return None
        

...
```


### `./apps/code_app/urls.py`

```python
from django.urls import path
from . import views, api_views, default_workspace_views

app_name = 'code'

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # Landing pages
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    
    # Core functionality
    path('editor/', views.editor, name='editor'),
    path('execute/', views.execute_code, name='execute_code'),
    path('analysis/', views.analysis, name='analysis'),
    path('analysis/run/', views.run_analysis, name='run_analysis'),
    path('templates/', views.templates, name='templates'),
    
    # Job management
    path('jobs/', views.jobs, name='jobs'),
    path('jobs/<uuid:job_id>/', views.job_detail, name='job_detail'),
    path('jobs/<uuid:job_id>/status/', views.job_status, name='job_status'),
    
    # Notebook management (views)
    path('notebooks/', views.notebooks, name='notebooks'),
    path('notebooks/<uuid:notebook_id>/', views.notebook_detail, name='notebook_detail'),
    path('notebooks/create/', views.create_notebook, name='create_notebook'),
    path('notebooks/<uuid:notebook_id>/execute/', views.execute_notebook, name='execute_notebook'),
    
    # Environment management
    path('environments/', views.environments, name='environments'),
    path('environments/create/', views.create_environment, name='create_environment'),
    path('environments/<str:env_id>/', views.environment_detail, name='environment_detail'),
    path('environments/<str:env_id>/setup/', views.setup_environment, name='setup_environment'),
    path('environments/<str:env_id>/execute/', views.execute_in_environment, name='execute_in_environment'),
    
    # Workflow management
    path('workflows/', views.workflows, name='workflows'),
    path('workflows/create/', views.create_workflow, name='create_workflow'),
    path('workflows/<str:workflow_id>/', views.workflow_detail, name='workflow_detail'),
    path('workflows/<str:workflow_id>/execute/', views.execute_workflow, name='execute_workflow'),
    
    # Data visualization pipeline
    path('visualizations/', views.visualizations, name='visualizations'),
    path('visualizations/generate/', views.generate_visualization, name='generate_visualization'),
    path('visualizations/process/', views.process_data_visualization, name='process_data_visualization'),
    path('reports/create/', views.create_research_report, name='create_research_report'),

...
```


### `./apps/code_app/views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from django.core.paginator import Paginator
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from .models import CodeExecutionJob, DataAnalysisJob, Notebook, ResourceUsage
# from apps.api  # Removed - api app not installed.utils import execute_code_safely, generate_analysis_code
import json
import threading
from . import default_workspace_views
from . import project_views

# Expose default workspace views
guest_session_view = default_workspace_views.guest_session_view
user_default_workspace = default_workspace_views.user_default_workspace

# Expose project views
project_code = project_views.project_code


@login_required
def index(request):
    """Code app - redirect to user's projects."""
    messages.info(request, 'Please select or create a project to use Code.')
    return redirect('user_projects:user_projects', username=request.user.username)


def features(request):
    """Code features view."""
    return render(request, 'code_app/features.html')


def pricing(request):
    """Code pricing view."""
    return render(request, 'code_app/pricing.html')


@login_required
def editor(request):
    """SciTeX Code editor interface."""
    # Get user's recent jobs for sidebar
    recent_jobs = CodeExecutionJob.objects.filter(user=request.user)[:5]
    
    context = {
        'recent_jobs': recent_jobs,
        'user_notebooks': Notebook.objects.filter(user=request.user)[:5]
    }
    return render(request, 'code_app/editor.html', context)

...
```


### `./apps/code_app/visualization_pipeline.py`

```python
#!/usr/bin/env python3
"""
Data Visualization Pipeline for SciTeX-Code
Integrates with Viz Module for publication-ready figure generation.
"""

import json
import uuid
import tempfile
import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Any
import logging

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User

from .models import CodeExecutionJob

logger = logging.getLogger(__name__)


class VisualizationGenerator:
    """Generates publication-ready visualizations from data."""
    
    def __init__(self, user: User):
        self.user = user
        self.output_dir = Path(settings.MEDIA_ROOT) / 'visualizations' / str(user.id)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set publication-ready defaults
        self._setup_matplotlib_style()
    
    def _setup_matplotlib_style(self):
        """Configure matplotlib for publication-ready plots."""
        plt.rcParams.update({
            'figure.figsize': (10, 6),
            'figure.dpi': 300,
            'savefig.dpi': 300,
            'savefig.bbox': 'tight',
            'savefig.pad_inches': 0.1,
            'font.family': 'serif',
            'font.serif': ['Times', 'Times New Roman', 'DejaVu Serif'],
            'font.size': 12,
            'axes.titlesize': 14,

...
```


### `./apps/core_app/admin.py`

```python
"""
SciTeX Cloud - Admin Interface

Administrative interface for managing users, projects, research groups,
and collaboration permissions.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import (
    Organization, OrganizationMembership,
    ResearchGroup, ResearchGroupMembership,
    Project, ProjectMembership, GitFileStatus
)
# UserProfile now managed in profile_app
from apps.profile_app.models import UserProfile


# Inline admin classes
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = (
        'bio', 'institution', 'academic_title', 'department', 'research_interests',
        'orcid', 'website', 'google_scholar', 'linkedin', 'researchgate', 'twitter',
        'profile_visibility', 'is_public', 'show_email', 'allow_collaboration', 'allow_messages',
        'is_academic_ja', 'deletion_scheduled_at'
    )
    readonly_fields = ('is_academic_ja',)


class OrganizationMembershipInline(admin.TabularInline):
    model = OrganizationMembership
    extra = 0
    fields = ('organization', 'role', 'joined_at')
    readonly_fields = ('joined_at',)


class ResearchGroupMembershipInline(admin.TabularInline):
    model = ResearchGroupMembership
    extra = 0
    fields = ('group', 'role', 'can_create_projects', 'can_invite_collaborators', 'joined_at', 'is_active')
    readonly_fields = ('joined_at',)


...
```


### `./apps/core_app/api_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 16:20:00 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/apps/core_app/api_views.py
# ----------------------------------------
import os
__FILE__ = (
    "./apps/core_app/api_views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
API Views for Core App
Implements RESTful endpoints for Document and Project management
Following TDD principles and clean code guidelines
"""

import json
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator
from django.db import transaction

from .models import Project, UserProfile
# from apps.document_app  # Removed - document_app not installed.models import Document
import logging
import re
import subprocess
import shutil
from pathlib import Path

logger = logging.getLogger(__name__)


class BaseAPIView(View):
    """Base API view with common functionality"""
    
    @method_decorator(csrf_exempt)
    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)
    
    def json_response(self, data, status=200):
        """Helper method for JSON responses"""
        return JsonResponse(data, status=status)

...
```


### `./apps/core_app/apps.py`

```python
from django.apps import AppConfig
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_app'
    verbose_name = 'SciTeX Core Application'

    def ready(self):
        # Import signals to ensure they are connected
        import apps.core_app.signals
        
        # Auto-create cache table if using database cache
        self.ensure_cache_table()

    def ensure_cache_table(self):
        """Ensure cache table exists for database cache."""
        try:
            # Check if we're using database cache
            cache_config = getattr(settings, 'CACHES', {}).get('default', {})
            if cache_config.get('BACKEND') == 'django.core.cache.backends.db.DatabaseCache':
                from django.core.management import call_command
                from django.db import connection
                
                table_name = cache_config.get('LOCATION', 'cache_table')
                
                with connection.cursor() as cursor:
                    # Check if cache table exists (SQLite specific query)
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", 
                        [table_name]
                    )
                    if not cursor.fetchone():
                        logger.info(f"Cache table '{table_name}' not found, creating...")
                        call_command('createcachetable', table_name)
                        logger.info(f"✅ Cache table '{table_name}' created successfully")
                    else:
                        logger.debug(f"Cache table '{table_name}' already exists")
                        
        except Exception as e:
            logger.warning(f"Could not ensure cache table: {e}")
...
```


### `./apps/core_app/context_processors.py`

```python
"""
Context processors for making common variables available in all templates.
"""
import re
from apps.project_app.models import Project


def project_context(request):
    """
    Add current project to context if URL matches /<username>/<project-slug>/ pattern.

    This makes 'project' available in all templates for context-aware navigation.

    For anonymous users, provides guest-<session-id>/default as workspace URL.
    """
    # Pattern: /<username>/<project-slug>/...
    pattern = r'^/([^/]+)/([^/]+)/'
    match = re.match(pattern, request.path)

    # Get guest project URL from middleware
    guest_project_url = getattr(request, 'guest_project_url', '/guest/default')

    if match:
        username = match.group(1)
        project_slug = match.group(2)

        # Handle guest sessions (guest-<16chars>/default)
        if username.startswith('guest-') and project_slug == 'default':
            # Guest session workspace
            return {
                'project': None,
                'guest_project_url': guest_project_url,
                'is_guest_session': True,
                'guest_username': username,
            }

        try:
            # Try to get real project
            from django.contrib.auth.models import User
            user = User.objects.get(username=username)
            project = Project.objects.get(slug=project_slug, owner=user)
            return {
                'project': project,
                'guest_project_url': guest_project_url,
                'is_guest_session': False,
            }
        except (User.DoesNotExist, Project.DoesNotExist):
            pass

    # Provide default project URL

...
```


### `./apps/core_app/dashboard_views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .views import index as dashboard_view


@never_cache
def dashboard_route(request):
    """
    Handle /dashboard/ route - direct access to user dashboard
    """
    if not request.user.is_authenticated:
        # Redirect to login if not authenticated
        return redirect('/login/')
    
    # Call the main dashboard view
    return dashboard_view(request)


@never_cache  
def root_redirect(request):
    """
    Handle root / route - redirect authenticated users to dashboard,
    show landing page for anonymous users
    """
    if request.user.is_authenticated:
        # Redirect authenticated users to dashboard
        return redirect('/dashboard/')
    else:
        # Show landing page for anonymous users
        from .views import landing
        return landing(request)
...
```


### `./apps/core_app/directory_manager.py`

```python
"""
SciTeX Cloud - User Directory Management System

This module handles user-specific directory trees with scientific workflow pattern
supporting both legacy and new structures for backward compatibility.

Scientific Workflow Directory Structure:
/media/users/{user_id}/
├── proj/                           # New scientific workflow structure
│   └── {username}/                 # User's HOME directory
│       ├── proj/                   # Projects directory
│       │   └── {project_name}/     # Individual project
│       │       ├── scripts/        # Analysis scripts
│       │       │   ├── analysis/   # Data analysis scripts
│       │       │   ├── preprocessing/ # Data preprocessing
│       │       │   ├── modeling/   # Machine learning models
│       │       │   ├── visualization/ # Plotting and figures
│       │       │   └── utils/      # Utility functions
│       │       ├── data/           # Data management
│       │       │   ├── raw/        # Original datasets
│       │       │   ├── processed/  # Cleaned data
│       │       │   ├── figures/    # Generated plots
│       │       │   └── models/     # Trained models
│       │       ├── docs/           # Documentation
│       │       │   ├── manuscripts/
│       │       │   ├── notes/
│       │       │   └── references/
│       │       ├── results/        # Analysis results
│       │       │   ├── outputs/
│       │       │   ├── reports/
│       │       │   └── analysis/
│       │       ├── config/         # Configuration files
│       │       └── temp/           # Temporary files
│       │           ├── cache/
│       │           ├── logs/
│       │           └── tmp/
│       ├── scripts/                # User-level scripts
│       ├── data/                   # User-level data
│       ├── docs/                   # User-level documentation
│       ├── configs/                # User configurations
│       └── externals/              # External tools and modules
├── projects/                       # Legacy structure (symlinked)
├── shared/                         # Shared resources
│   ├── templates/
│   ├── libraries/
│   └── resources/
└── temp/                          # Temporary workspace
    ├── uploads/
    ├── cache/
    └── processing/

...
```


### `./apps/core_app/directory_urls.py`

```python
"""
SciTeX Cloud - Directory Management URLs

URL patterns for project directory management and file operations.
"""

from django.urls import path
from . import directory_views

app_name = 'directory'

urlpatterns = [
    # Project directory structure
    path('projects/<int:project_id>/structure/', 
         directory_views.project_structure, 
         name='project_structure'),
    
    # File management
    path('projects/<int:project_id>/files/', 
         directory_views.project_files, 
         name='project_files'),
    
    path('projects/<int:project_id>/upload/', 
         directory_views.upload_file, 
         name='upload_file'),
    
    path('projects/<int:project_id>/download/', 
         directory_views.download_file, 
         name='download_file'),
    
    path('projects/<int:project_id>/delete-file/', 
         directory_views.delete_file, 
         name='delete_file'),
    
    # Directory management
    path('projects/<int:project_id>/create-directory/', 
         directory_views.create_directory, 
         name='create_directory'),
    
    path('projects/<int:project_id>/initialize/', 
         directory_views.initialize_project_directory, 
         name='initialize_project_directory'),
    
    # README management
    path('projects/<int:project_id>/readme/', 
         directory_views.project_readme, 
         name='project_readme'),
    
    path('projects/<int:project_id>/readme/update/', 
         directory_views.update_project_readme, 

...
```


### `./apps/core_app/directory_views.py`

```python
"""
SciTeX Cloud - Directory Management Views

This module provides API views for managing user directory structures,
project files, and directory operations.
"""

from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.shortcuts import get_object_or_404
from django.conf import settings
import json
import os
import mimetypes
import zipfile
import tempfile
from pathlib import Path
from datetime import datetime

from .models import Project
# from apps.document_app  # Removed - document_app not installed.models import Document
from .directory_manager import get_user_directory_manager


@login_required
@require_http_methods(["GET"])
def project_structure(request, project_id):
    """Get the complete directory structure for a project."""
    try:
        project = get_object_or_404(Project, id=project_id, owner=request.user)
        
        # Ensure project directory exists
        project.ensure_directory()
        
        # Get project structure
        structure = project.get_file_structure()
        
        return JsonResponse({
            'status': 'success',
            'project_id': project_id,
            'project_name': project.name,
            'structure': structure,
            'storage_used_mb': project.get_storage_usage_mb(),
            'directory_created': project.directory_created
        })
        
    except Exception as e:

...
```


### `./apps/core_app/github_views.py`

```python
"""
GitHub Integration API Views for SciTeX Cloud
Enhanced GitHub connectivity for seamless version control integration
"""

import json
import requests
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.conf import settings
from django.utils import timezone
from .models import Project, GitFileStatus
import subprocess
import os
from pathlib import Path


# GitHub OAuth Configuration
GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET', '')
GITHUB_REDIRECT_URI = getattr(settings, 'GITHUB_REDIRECT_URI', '')


@login_required
@require_http_methods(["POST"])
def github_oauth_initiate(request):
    """Initiate GitHub OAuth flow"""
    project_id = request.POST.get('project_id')
    if not project_id:
        return JsonResponse({'error': 'Project ID required'}, status=400)
    
    project = get_object_or_404(Project, id=project_id, owner=request.user)
    
    # Store project ID in session for callback
    request.session['github_project_id'] = project_id
    
    # GitHub OAuth URL
    oauth_url = (
        f"https://github.com/login/oauth/authorize"
        f"?client_id={GITHUB_CLIENT_ID}"
        f"&redirect_uri={GITHUB_REDIRECT_URI}"
        f"&scope=repo,user:email"
        f"&state={project_id}"
    )
    
    return JsonResponse({
        'success': True,

...
```


### `./apps/core_app/__init__.py`

```python

...
```


### `./apps/core_app/middleware.py`

```python
"""
Middleware for SciTeX Cloud.
"""

import secrets


class GuestSessionMiddleware:
    """
    Track user state including current/last accessed project.

    For logged-in users:
    - Tracks current project in session
    - Used for smart module navigation

    For anonymous users (no longer used):
    - Previously generated guest session IDs
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Track current project from URL for logged-in users
        if request.user.is_authenticated:
            # Check if URL matches /<username>/<project>/...
            import re
            pattern = r'^/([^/]+)/([^/?]+)/'
            match = re.match(pattern, request.path)

            if match:
                username = match.group(1)
                project_slug = match.group(2)

                # If this is a project page (not 'projects' or other reserved words)
                if project_slug not in ['projects'] and username == request.user.username:
                    # Update session with current project
                    request.session['current_project_slug'] = project_slug
                    request.session.modified = True

        response = self.get_response(request)
        return response

...
```


### `./apps/core_app/model_imports.py`

```python
# Central import file for accessing models from modular apps
# This allows backward compatibility while maintaining modular architecture

# Auth models
try:
    from apps.auth_app.models import UserProfile, EmailVerification
    from apps.auth_app.models import is_japanese_academic_email, JAPANESE_ACADEMIC_DOMAINS
except ImportError:
    # Fallback for development/test environments
    UserProfile = None
    EmailVerification = None
    is_japanese_academic_email = None
    JAPANESE_ACADEMIC_DOMAINS = []

# Document models
try:
    from apps.document_app.models import Document
except ImportError:
    Document = None

# Project models
try:
    from apps.project_app.models import (
        Project, ProjectMembership, Organization, ResearchGroup, 
        ResearchGroupMembership, ProjectPermission
    )
except ImportError:
    Project = None
    ProjectMembership = None
    Organization = None
    ResearchGroup = None
    ResearchGroupMembership = None
    ProjectPermission = None

# Export all models for easy importing
__all__ = [
    'UserProfile', 'EmailVerification', 'is_japanese_academic_email', 'JAPANESE_ACADEMIC_DOMAINS',
    'Document',
    'Project', 'ProjectMembership', 'Organization', 'ResearchGroup', 
    'ResearchGroupMembership', 'ProjectPermission'
]
...
```


### `./apps/core_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
import random
import string
from datetime import timedelta
from django.utils import timezone


# UserProfile model moved to apps.profile_app.models
# Import here for backwards compatibility
from apps.profile_app.models import UserProfile  # noqa

# Japanese Academic utilities moved to apps.profile_app.models
from apps.profile_app.models import JAPANESE_ACADEMIC_DOMAINS, is_japanese_academic_email  # noqa


# Document model moved to apps.document_app.models


class Organization(models.Model):
    """Model for research organizations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(User, through='OrganizationMembership')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.name


class OrganizationMembership(models.Model):
    """Model for organization membership with roles"""
    ROLES = [
        ('admin', 'Administrator'),
        ('member', 'Member'),
        ('viewer', 'Viewer'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    role = models.CharField(max_length=20, choices=ROLES, default='member')
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('user', 'organization')
        
    def __str__(self):
        return f"{self.user.username} - {self.organization.name} ({self.role})"


...
```


### `./apps/core_app/permissions.py`

```python
"""
SciTeX Cloud - Permission Middleware and Decorators

This module provides permission checking middleware and decorators for 
project-based file access control as described in the groups and permissions 
documentation.
"""

from functools import wraps
from django.http import JsonResponse, HttpResponseForbidden
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project


def require_project_permission(permission):
    """
    Decorator to require specific project permission before accessing files.
    
    Usage:
        @require_project_permission('can_read_files')
        def read_file(request, project_id, file_path):
            # Access granted - proceed with file operation
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapper(request, project_id, *args, **kwargs):
            # Get project and check if user has permission
            project = get_object_or_404(Project, id=project_id)
            
            # Check if user has access to the project
            if not project.is_accessible_by(request.user):
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'status': 'error',
                        'message': 'You do not have access to this project'
                    }, status=403)
                else:
                    return HttpResponseForbidden('You do not have access to this project')
            
            # Check specific permission
            if not project.has_permission(request.user, permission):
                permission_name = permission.replace('can_', '').replace('_', ' ')
                if request.headers.get('Accept') == 'application/json':
                    return JsonResponse({
                        'status': 'error',
                        'message': f'You do not have permission to {permission_name} in this project'
                    }, status=403)
                else:

...
```


### `./apps/core_app/services.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Email services for SciTeX Cloud
# ----------------------------------------

from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string
from django.utils.html import strip_tags
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """Service for sending emails including OTP verification"""
    
    @staticmethod
    def send_otp_email(email, otp_code, verification_type='signup'):
        """Send OTP verification email"""
        try:
            # Determine email subject and context based on verification type
            if verification_type == 'signup':
                subject = 'SciTeX - Verify Your Email Address'
                template_name = 'emails/signup_otp.html'
                context = {
                    'otp_code': otp_code,
                    'email': email,
                    'site_name': 'SciTeX',
                    'expires_minutes': 10,
                    'verification_type': 'account registration'
                }
            elif verification_type == 'password_reset':
                subject = 'SciTeX - Reset Your Password'
                template_name = 'emails/password_reset_otp.html'
                context = {
                    'otp_code': otp_code,
                    'email': email,
                    'site_name': 'SciTeX',
                    'expires_minutes': 10,
                    'verification_type': 'password reset'
                }
            elif verification_type == 'email_change':
                subject = 'SciTeX - Verify Your New Email Address'
                template_name = 'emails/email_change_otp.html'
                context = {
                    'otp_code': otp_code,
                    'email': email,
                    'site_name': 'SciTeX',
                    'expires_minutes': 10,

...
```


### `./apps/core_app/signals.py`

```python
"""
SciTeX Cloud - Model Signals for Directory Management

This module contains Django signals to automatically manage user directories
and project directory structures when models are created or updated.
"""

from django.db.models.signals import post_save, post_delete, pre_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Project, UserProfile
# from apps.document_app.models import Document  # Removed - document_app not installed
from .directory_manager import get_user_directory_manager, ensure_project_directory
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def create_user_workspace(sender, instance, created, **kwargs):
    """Create user workspace when a new user is created."""
    if created:
        try:
            # Create user profile if it doesn't exist
            profile, profile_created = UserProfile.objects.get_or_create(user=instance)
            
            # Initialize user workspace
            manager = get_user_directory_manager(instance)
            success = manager.initialize_user_workspace()
            
            if success:
                logger.info(f"User workspace created for {instance.username}")
            else:
                logger.error(f"Failed to create user workspace for {instance.username}")
                
        except Exception as e:
            logger.error(f"Error creating user workspace for {instance.username}: {e}")


@receiver(post_save, sender=Project)
def handle_project_directory(sender, instance, created, **kwargs):
    """Handle project directory creation and updates."""
    try:
        if created and not instance.directory_created:
            # Create project directory for new projects (avoid recursion)
            manager = get_user_directory_manager(instance.owner)
            success, path = manager.create_project_directory(instance)
            if success:
                # Update directory_created flag without triggering signal
                Project.objects.filter(id=instance.id).update(directory_created=True)

...
```


### `./apps/core_app/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, Project
# from apps.document_app  # Removed - document_app not installed.models import Document
from apps.cloud_app.models import SubscriptionPlan, Subscription


class UserProfileTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    def test_profile_creation(self):
        """Test profile creation with get_or_create"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        self.assertEqual(profile.user, self.user)
        self.assertEqual(profile.institution, '')  # Changed from organization
        self.assertTrue(profile.is_public)
    
    def test_profile_update(self):
        """Test updating profile fields"""
        profile, created = UserProfile.objects.get_or_create(user=self.user)
        profile.institution = 'Test University'
        profile.bio = 'Test bio'
        profile.research_interests = 'Computer Science, AI'
        profile.save()
        
        updated_profile = UserProfile.objects.get(user=self.user)
        self.assertEqual(updated_profile.institution, 'Test University')
        self.assertEqual(updated_profile.bio, 'Test bio')
        self.assertEqual(updated_profile.research_interests, 'Computer Science, AI')


class DocumentTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        self.document = Document.objects.create(
            owner=self.user,
            title='Test Document',
            content='Test content',

...
```


### `./apps/core_app/urls.py`

```python
from django.urls import path, include
from . import views
from . import api_views
from . import github_views

app_name = 'core_app'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.index, name='index'),
    path('dashboard/file-manager/', views.dashboard_react_tree, name='dashboard_react_tree'),
    path('documents/', views.document_list, name='document_list'),
    path('projects/', views.project_list, name='project_list'),
    path('profile/', views.profile_view, name='profile'),
    path('settings/profile/', views.profile_edit, name='profile_edit'),
    path('settings/appearance/', views.appearance_settings, name='appearance'),
    path('monitoring/', views.monitoring, name='monitoring'),
    path('monitoring/data/', views.monitoring_data, name='monitoring_data'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_use, name='terms'),
    path('cookies/', views.cookie_policy, name='cookies'),
]

# API URLs
api_urlpatterns = [
    # Document management
    path("api/v1/documents/", api_views.document_api, name="api-documents"),
    path("api/v1/documents/<int:document_id>/", api_views.document_api, name="api-document-detail"),
    
    # Project management
    path("api/v1/projects/", api_views.project_api, name="api-projects"),
    path("api/v1/projects/<int:project_id>/", api_views.project_api, name="api-project-detail"),
    
    # User statistics and profile
    path("api/v1/stats/", api_views.user_stats_api, name="api-user-stats"),
    path("api/v1/profile/", api_views.user_profile_api, name="api-user-profile"),
    
    # Example project creation
    path("api/v1/projects/examples/", views.create_example_project, name="api-create-example-project"),
    path("api/v1/projects/<int:project_id>/copy/", views.copy_project, name="api-copy-project"),
    
    # GitHub Integration APIs
    path("api/v1/github/oauth/initiate/", github_views.github_oauth_initiate, name="api-github-oauth-initiate"),
    path("api/v1/github/oauth/callback/", github_views.github_oauth_callback, name="api-github-oauth-callback"),
    path("api/v1/github/create-repo/", github_views.github_create_repository, name="api-github-create-repo"),
    path("api/v1/github/link-repo/", github_views.github_link_repository, name="api-github-link-repo"),
    path("api/v1/github/projects/<int:project_id>/status/", github_views.github_get_status, name="api-github-status"),
    path("api/v1/github/projects/<int:project_id>/sync/", github_views.github_sync_status, name="api-github-sync"),

...
```


### `./apps/core_app/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from datetime import datetime, timedelta
import random
import json
# from apps.document_app  # Removed - document_app not installed.models import Document
from apps.auth_app.models import UserProfile
from apps.project_app.models import Project
from .directory_manager import get_user_directory_manager


def generate_smart_recommendations(user):
    """Generate personalized recommendations based on user activity."""
    recommendations = []
    
    # Get user's project count
    project_count = Project.objects.filter(owner=user).count()
    
    # Get user's registration date
    days_since_registration = (datetime.now().date() - user.date_joined.date()).days
    
    # Smart recommendations based on user state
    if project_count == 0:
        recommendations.append({
            'type': 'action',
            'title': 'Create Your First Project',
            'description': 'Start organizing your research with a dedicated project workspace',
            'action_url': '/core/project-list/',
            'icon': 'fas fa-plus-circle',
            'priority': 'high'
        })
    
    if days_since_registration <= 7:
        recommendations.append({
            'type': 'explore',
            'title': 'Discover SciTeX Scholar',
            'description': 'Search through millions of scientific papers with our advanced semantic search',
            'action_url': '/scholar/',
            'icon': 'fas fa-search',
            'priority': 'medium'
        })
        
        recommendations.append({
            'type': 'learn',
            'title': 'Try LaTeX Writing',
            'description': 'Write and compile scientific documents with our integrated LaTeX editor',
            'action_url': '/writer/',
            'icon': 'fas fa-edit',

...
```


### `./apps/dev_app/admin.py`

```python
from django.contrib import admin

# Register your models here.

...
```


### `./apps/dev_app/apps.py`

```python
from django.apps import AppConfig


class DevAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.dev_app'
    verbose_name = 'Development Tools'

...
```


### `./apps/dev_app/__init__.py`

```python

...
```


### `./apps/dev_app/models.py`

```python
from django.db import models

# Create your models here.

...
```


### `./apps/dev_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/dev_app/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 01:47:34 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/dev_app/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/dev_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.urls import path

from . import views
from .views import DesignSystemView

app_name = "dev_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("design/", DesignSystemView.as_view(), name="design"),
]

# EOF

...
```


### `./apps/dev_app/views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 01:56:11 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/apps/dev_app/views.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./apps/dev_app/views.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import render
from django.views import View


def index(request):
    """Dev app index page - Developer Tools Hub."""
    return render(request, 'dev_app/index.html')


class DesignSystemView(View):
    """Display the SciTeX design system documentation."""

    template_name = "dev_app/design.html"

    def get(self, request):
        """Render the design system page."""
        return render(request, self.template_name)

# EOF

...
```


### `./apps/docs_app/admin.py`

```python
from django.contrib import admin

# Register your models here.

...
```


### `./apps/docs_app/apps.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/apps.py

from django.apps import AppConfig


class DocsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.docs_app"
    verbose_name = "SciTeX Documentation"

...
```


### `./apps/docs_app/__init__.py`

```python

...
```


### `./apps/docs_app/models.py`

```python
from django.db import models

# Create your models here.

...
```


### `./apps/docs_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/docs_app/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/urls.py

from django.urls import path
from . import views

app_name = "docs"

urlpatterns = [
    # Documentation landing page
    path("", views.docs_index, name="index"),

    # Module-specific documentation
    path("scholar/", views.docs_scholar, name="scholar"),
    path("code/", views.docs_code, name="code"),
    path("viz/", views.docs_viz, name="viz"),
    path("writer/", views.docs_writer, name="writer"),

    # Serve specific documentation pages
    path("<str:module>/<path:page>", views.docs_page, name="page"),
]

...
```


### `./apps/docs_app/views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/docs_app/views.py

from django.shortcuts import render, redirect
from django.http import Http404, HttpResponse
from django.conf import settings
from pathlib import Path
import os


# Documentation paths for each module
# Note: code/scholar are in scitex_repo at repo root level, not in src/scitex
DOC_PATHS = {
    "scholar": "../scitex_repo/docs/_build/html",  # scholar docs in main scitex repo
    "code": "../scitex_repo/docs/_build/html",      # code docs in main scitex repo
    "viz": "../SciTeX-Viz/docs/_build/html",
    "writer": "../neurovista/paper/docs/_build/html",
}


def docs_index(request):
    """Documentation landing page showing all available modules."""
    context = {
        "modules": [
            {
                "name": "Scholar",
                "slug": "scholar",
                "description": "Literature search and reference management",
                "icon": "scitex-scholar-icon.svg",
                "available": _check_docs_available("scholar"),
            },
            {
                "name": "Code",
                "slug": "code",
                "description": "Research computing and analysis utilities",
                "icon": "scitex-code-icon.svg",
                "available": _check_docs_available("code"),
            },
            {
                "name": "Viz",
                "slug": "viz",
                "description": "Publication-quality visualization tools",
                "icon": "scitex-viz-icon.svg",
                "available": _check_docs_available("viz"),
            },
            {
                "name": "Writer",
                "slug": "writer",
                "description": "LaTeX manuscript preparation and management",

...
```


### `./apps/__init__.py`

```python

...
```


### `./apps/integrations_app/admin.py`

```python
from django.contrib import admin
from .models import IntegrationConnection, ORCIDProfile, SlackWebhook, IntegrationLog


@admin.register(IntegrationConnection)
class IntegrationConnectionAdmin(admin.ModelAdmin):
    list_display = ('user', 'service', 'status', 'external_username', 'created_at', 'last_sync_at')
    list_filter = ('service', 'status', 'created_at')
    search_fields = ('user__username', 'external_username', 'external_user_id')
    readonly_fields = ('created_at', 'updated_at', 'last_sync_at')

    fieldsets = (
        ('Basic Info', {
            'fields': ('user', 'service', 'status')
        }),
        ('External Service', {
            'fields': ('external_user_id', 'external_username', 'metadata')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'last_sync_at')
        }),
    )


@admin.register(ORCIDProfile)
class ORCIDProfileAdmin(admin.ModelAdmin):
    list_display = ('orcid_id', 'get_full_name', 'current_institution', 'last_synced_at')
    search_fields = ('orcid_id', 'given_names', 'family_name', 'current_institution')
    readonly_fields = ('last_synced_at',)


@admin.register(SlackWebhook)
class SlackWebhookAdmin(admin.ModelAdmin):
    list_display = ('connection', 'channel', 'is_active', 'notification_count', 'last_notification_at')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'last_notification_at', 'notification_count')
    filter_horizontal = ('project_filter',)


@admin.register(IntegrationLog)
class IntegrationLogAdmin(admin.ModelAdmin):
    list_display = ('connection', 'action', 'success', 'created_at')
    list_filter = ('action', 'success', 'created_at')
    search_fields = ('connection__user__username', 'details', 'error_message')
    readonly_fields = ('created_at',)

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):

...
```


### `./apps/integrations_app/apps.py`

```python
from django.apps import AppConfig


class IntegrationsAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.integrations_app'
    verbose_name = 'Integrations'

...
```


### `./apps/integrations_app/__init__.py`

```python
# Integrations App for SciTeX

...
```


### `./apps/integrations_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import json


class IntegrationConnection(models.Model):
    """Base model for external service integrations"""

    SERVICE_CHOICES = [
        ('orcid', 'ORCID'),
        ('github', 'GitHub'),
        ('gitlab', 'GitLab'),
        ('zotero', 'Zotero'),
        ('overleaf', 'Overleaf'),
        ('slack', 'Slack'),
        ('discord', 'Discord'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('error', 'Error'),
        ('expired', 'Expired'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='integration_connections')
    service = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='inactive')

    # OAuth tokens (encrypted)
    access_token = models.TextField(blank=True, help_text="Encrypted OAuth access token")
    refresh_token = models.TextField(blank=True, help_text="Encrypted OAuth refresh token")
    token_expires_at = models.DateTimeField(null=True, blank=True)

    # API keys (encrypted)
    api_key = models.TextField(blank=True, help_text="Encrypted API key")
    api_secret = models.TextField(blank=True, help_text="Encrypted API secret")

    # Service-specific data
    external_user_id = models.CharField(max_length=255, blank=True, help_text="User ID on external service")
    external_username = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True, help_text="Service-specific metadata")

    # Webhook configuration
    webhook_url = models.URLField(blank=True, help_text="Webhook URL for notifications")
    webhook_secret = models.TextField(blank=True, help_text="Encrypted webhook secret")


...
```


### `./apps/integrations_app/urls.py`

```python
from django.urls import path
from . import views

app_name = 'integrations_app'

urlpatterns = [
    # Dashboard
    path('', views.integrations_dashboard, name='dashboard'),

    # ORCID
    path('orcid/connect/', views.orcid_connect, name='orcid_connect'),
    path('orcid/callback/', views.orcid_callback, name='orcid_callback'),
    path('orcid/disconnect/', views.orcid_disconnect, name='orcid_disconnect'),
    path('orcid/sync/', views.orcid_sync, name='orcid_sync'),

    # BibTeX Export
    path('export/<int:project_id>/bib/', views.export_project_bib, name='export_project_bib'),

    # Slack
    path('slack/configure/', views.slack_configure, name='slack_configure'),
    path('slack/<int:webhook_id>/test/', views.slack_test, name='slack_test'),
    path('slack/<int:webhook_id>/delete/', views.slack_delete, name='slack_delete'),

    # API endpoints
    path('api/status/', views.api_integration_status, name='api_status'),
    path('api/orcid/profile/', views.api_orcid_profile, name='api_orcid_profile'),
]

...
```


### `./apps/integrations_app/views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.conf import settings
import secrets

from .models import IntegrationConnection, ORCIDProfile, SlackWebhook
from .services import ORCIDService, BibExportService, SlackService
from apps.project_app.models import Project


@login_required
def integrations_dashboard(request):
    """Main integrations dashboard"""
    connections = IntegrationConnection.objects.filter(user=request.user)

    context = {
        'connections': connections,
        'orcid_connected': connections.filter(service='orcid', status='active').exists(),
        'slack_connected': connections.filter(service='slack', status='active').exists(),
    }

    return render(request, 'integrations_app/dashboard.html', context)


# ORCID Integration Views

@login_required
def orcid_connect(request):
    """Initiate ORCID OAuth flow"""
    service = ORCIDService(user=request.user)

    # Generate state token for CSRF protection
    state = secrets.token_urlsafe(32)
    request.session['orcid_oauth_state'] = state

    authorization_url = service.get_authorization_url(state=state)
    return redirect(authorization_url)


@login_required
def orcid_callback(request):
    """Handle ORCID OAuth callback"""
    # Verify state token
    state = request.GET.get('state')
    stored_state = request.session.pop('orcid_oauth_state', None)

    if not state or state != stored_state:

...
```


### `./apps/permissions_app/admin.py`

```python
from django.contrib import admin

# Register your models here.

...
```


### `./apps/permissions_app/apps.py`

```python
from django.apps import AppConfig


class PermissionsAppConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.permissions_app"

...
```


### `./apps/permissions_app/decorators.py`

```python
"""
Permission decorators for views.
Clean, simple, readable.
"""

from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404
from apps.project_app.models import Project
from .services import PermissionService


def require_permission(action: str, module: str = None):
    """
    Require specific permission for view.

    Usage:
        @require_permission('write', 'writer')
        def edit_manuscript(request, project_id):
            # User has write permission for writer module
            pass
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            project_id = kwargs.get('project_id')
            if not project_id:
                return HttpResponseForbidden("No project specified")

            project = get_object_or_404(Project, id=project_id)

            # Check permission
            has_perm = PermissionService.check_permission(
                request.user,
                project,
                action,
                module
            )

            if not has_perm:
                return HttpResponseForbidden(f"You don't have {action} permission for this project")

            # Add project to request for convenience
            request.project = project
            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator



...
```


### `./apps/permissions_app/__init__.py`

```python

...
```


### `./apps/permissions_app/models.py`

```python
"""
Permission models for SciTeX.
GitLab-inspired role-based access control.
"""

from django.db import models
from django.contrib.auth.models import User


class Role(models.TextChoices):
    """Project member roles (GitLab-style)."""
    OWNER = 'owner', 'Owner'
    MAINTAINER = 'maintainer', 'Maintainer'
    DEVELOPER = 'developer', 'Developer'
    REPORTER = 'reporter', 'Reporter'
    GUEST = 'guest', 'Guest'


class ProjectMember(models.Model):
    """User's role in a project."""
    project = models.ForeignKey('project_app.Project', on_delete=models.CASCADE, related_name='permission_members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='permission_project_memberships')
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.DEVELOPER)

    # Module permissions (None = use role default)
    can_edit_scholar = models.BooleanField(null=True, blank=True)
    can_edit_code = models.BooleanField(null=True, blank=True)
    can_edit_viz = models.BooleanField(null=True, blank=True)
    can_edit_writer = models.BooleanField(null=True, blank=True)

    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invited_members')
    joined_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['project', 'user']
        ordering = ['joined_at']

    def __str__(self):
        return f"{self.user.username} - {self.get_role_display()}"


class GuestCollaborator(models.Model):
    """Email-based guest access (no account required)."""
    project = models.ForeignKey('project_app.Project', on_delete=models.CASCADE, related_name='guest_collaborators', null=True, blank=True)
    manuscript = models.ForeignKey('writer_app.Manuscript', on_delete=models.CASCADE, related_name='guest_collaborators', null=True, blank=True)

    email = models.EmailField()
    guest_name = models.CharField(max_length=200, blank=True)
    access_token = models.CharField(max_length=64, unique=True, db_index=True)

...
```


### `./apps/permissions_app/README.md`

```markdown
# Permissions App - GitLab-Style Access Control for SciTeX

## Overview

The `permissions_app` provides fine-grained, role-based access control across all SciTeX modules (Scholar, Code, Viz, Writer). Inspired by GitLab's permission system, it enables:

- **Project-level roles** (Owner, Maintainer, Developer, Reporter, Guest)
- **Module-specific permissions** (can edit Writer but not Code)
- **Guest access** (email-based tokens for reviewers)
- **Clean, centralized permission logic**

## Quick Start

### Check Permission in View

```python
from apps.permissions_app.decorators import require_permission, require_role

# Require specific permission
@require_permission('write', 'writer')
def edit_manuscript(request, project_id):
    # User has write permission for Writer module
    pass

# Require minimum role
@require_role('developer')
def run_analysis(request, project_id):
    # User is Developer, Maintainer, or Owner
    pass
```

### Check Permission in Template

```django
{% load permission_tags %}

{# Check if user can edit Writer module #}
{% if user|can:"write:writer:project" %}
    <button class="btn btn-primary">Edit Manuscript</button>
{% else %}
    <span class="text-muted">Read-only access</span>
{% endif %}

{# Get user's role #}
{% user_role user project as role %}
<span>Your role: {{ role }}</span>
```

### Add Member to Project


...
```


### `./apps/permissions_app/services.py`

```python
"""
Permission service - centralized permission logic.
Single source of truth for all authorization decisions.
"""

from typing import Optional
from .models import Role, ProjectMember, GuestCollaborator


class PermissionService:
    """Centralized permission checking."""

    # Role hierarchy (higher number = more permissions)
    ROLE_HIERARCHY = {
        Role.GUEST: 0,
        Role.REPORTER: 1,
        Role.DEVELOPER: 2,
        Role.MAINTAINER: 3,
        Role.OWNER: 4,
    }

    @classmethod
    def get_user_role(cls, user, project) -> Optional[str]:
        """Get user's role in project."""
        # Owner always has owner role
        if project.owner == user:
            return Role.OWNER

        # Check ProjectMember
        try:
            member = ProjectMember.objects.get(project=project, user=user, is_active=True)
            return member.role
        except ProjectMember.DoesNotExist:
            return None

    @classmethod
    def can_read(cls, user, project) -> bool:
        """Can user read project content?"""
        role = cls.get_user_role(user, project)
        return role is not None  # All roles can read

    @classmethod
    def can_write(cls, user, project, module: Optional[str] = None) -> bool:
        """Can user write/edit content?"""
        role = cls.get_user_role(user, project)
        if not role:
            return False

        # Guest and Reporter cannot write
        if role in [Role.GUEST, Role.REPORTER]:

...
```


### `./apps/permissions_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/permissions_app/views.py`

```python
from django.shortcuts import render

# Create your views here.

...
```


### `./apps/profile_app/admin.py`

```python
from django.contrib import admin
from .models import UserProfile


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'institution', 'is_academic_ja', 'profile_visibility', 'created_at')
    list_filter = ('is_academic_ja', 'profile_visibility', 'is_public', 'created_at')
    search_fields = ('user__username', 'user__email', 'institution', 'bio')
    readonly_fields = ('created_at', 'updated_at', 'is_academic_ja')

    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Profile Information', {
            'fields': ('avatar', 'bio', 'location', 'institution', 'research_interests')
        }),
        ('Academic Information', {
            'fields': ('orcid', 'academic_title', 'department', 'is_academic_ja')
        }),
        ('Professional Links', {
            'fields': ('website', 'google_scholar', 'linkedin', 'researchgate', 'twitter')
        }),
        ('Privacy Settings', {
            'fields': ('profile_visibility', 'is_public', 'show_email', 'allow_collaboration', 'allow_messages')
        }),
        ('System', {
            'fields': ('last_active_repository', 'deletion_scheduled_at', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

...
```


### `./apps/profile_app/apps.py`

```python
from django.apps import AppConfig


class ProfileAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.profile_app'
    verbose_name = 'User Profiles'

    def ready(self):
        """Import signals when app is ready"""
        import apps.profile_app.signals  # noqa

...
```


### `./apps/profile_app/__init__.py`

```python
default_app_config = 'apps.profile_app.apps.ProfileAppConfig'

...
```


### `./apps/profile_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User


# Japanese Academic domains to recognize
JAPANESE_ACADEMIC_DOMAINS = [
    # Japanese Academic (.ac.jp) - All academic institutions
    '.ac.jp',
    '.u-tokyo.ac.jp', '.kyoto-u.ac.jp', '.osaka-u.ac.jp',
    '.tohoku.ac.jp', '.nagoya-u.ac.jp', '.kyushu-u.ac.jp',
    '.hokudai.ac.jp', '.tsukuba.ac.jp', '.hiroshima-u.ac.jp',
    '.kobe-u.ac.jp', '.waseda.jp', '.keio.ac.jp',

    # Government Research Institutions (.go.jp)
    '.go.jp',  # Broader government research support
    '.riken.jp', '.aist.go.jp', '.nict.go.jp', '.jaxa.jp',
    '.jst.go.jp', '.nims.go.jp', '.nies.go.jp'
]


def is_japanese_academic_email(email):
    """Check if email belongs to Japanese academic institution"""
    if not email:
        return False
    try:
        domain = email.lower().split('@')[1]
        # Check if domain matches exactly or ends with the academic domain
        for academic_domain in JAPANESE_ACADEMIC_DOMAINS:
            # Remove leading dot for exact matching
            clean_domain = academic_domain.lstrip('.')
            if domain == clean_domain or domain.endswith(academic_domain):
                return True
        return False
    except (IndexError, AttributeError):
        return False


class UserProfile(models.Model):
    """Extended user profile for researchers"""

    VISIBILITY_CHOICES = [
        ('public', 'Public'),
        ('restricted', 'Restricted'),
        ('private', 'Private'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True, help_text="Profile picture")
    bio = models.TextField(max_length=500, blank=True, help_text="Brief description of your research background")
    location = models.CharField(max_length=200, blank=True, help_text="Your current location (e.g., 'Tokyo, Japan')")

...
```


### `./apps/profile_app/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import UserProfile


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create UserProfile when a new User is created"""
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save UserProfile when User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()

...
```


### `./apps/project_app/admin.py`

```python
from django.contrib import admin
from .models import Project, ProjectMembership, Organization, ResearchGroup, ProjectPermission


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ('name', 'website', 'created_at')
    search_fields = ('name', 'description')
    list_filter = ('created_at',)


@admin.register(ResearchGroup)
class ResearchGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'organization', 'leader', 'created_at')
    search_fields = ('name', 'description', 'organization__name')
    list_filter = ('organization', 'created_at')


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'owner', 'progress', 'created_at', 'updated_at')
    search_fields = ('name', 'description', 'owner__username')
    list_filter = ('created_at', 'updated_at', 'organization')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'owner', 'progress')
        }),
        ('Organization', {
            'fields': ('organization', 'research_group'),
            'classes': ('collapse',)
        }),
        ('Research Data', {
            'fields': ('hypotheses', 'source_code_url', 'data_location', 'manuscript_draft'),
            'classes': ('collapse',)
        }),
        ('GitHub Integration', {
            'fields': ('github_integration_enabled', 'github_repo_name', 'github_owner', 'current_branch'),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at', 'last_activity'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectMembership)
class ProjectMembershipAdmin(admin.ModelAdmin):
    list_display = ('project', 'user', 'role', 'permission_level', 'joined_at')

...
```


### `./apps/project_app/apps.py`

```python
from django.apps import AppConfig


class ProjectAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.project_app'
    verbose_name = 'Project Management'
    
    def ready(self):
        """Initialize the app when Django starts."""
        pass

...
```


### `./apps/project_app/decorators.py`

```python
"""
Decorators for project-based access control.
"""

from functools import wraps
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Project


def project_required(view_func):
    """
    Decorator to ensure user has at least one project.

    If user has no projects, redirects to project creation page with helpful message.
    Must be used with @login_required.

    Usage:
        @login_required
        @project_required
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        # Check if user has any projects
        user_projects = Project.objects.filter(owner=request.user)

        if not user_projects.exists():
            messages.warning(
                request,
                'You need to create a project first. Projects help organize your research work across Scholar, Writer, Code, and Viz modules.'
            )
            return redirect('project_app:create')

        return view_func(request, *args, **kwargs)

    return wrapper


def project_access_required(view_func):
    """
    Decorator to check if user has access to a specific project.

    Expects username and slug in kwargs.
    Checks if user is owner or collaborator.

    Usage:
        @login_required

...
```


### `./apps/project_app/__init__.py`

```python

...
```


### `./apps/project_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from datetime import timedelta
from django.utils import timezone


class ProjectMembership(models.Model):
    """Enhanced membership model for project collaboration"""
    
    ROLE_CHOICES = [
        ('owner', 'Owner'),
        ('admin', 'Administrator'),
        ('collaborator', 'Collaborator'),
        ('viewer', 'Viewer'),
    ]
    
    PERMISSION_CHOICES = [
        ('read', 'Read Only'),
        ('write', 'Read/Write'),
        ('admin', 'Full Admin'),
    ]
    
    project = models.ForeignKey('Project', on_delete=models.CASCADE, related_name='memberships')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='project_memberships')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='collaborator')
    permission_level = models.CharField(max_length=20, choices=PERMISSION_CHOICES, default='read')
    joined_at = models.DateTimeField(auto_now_add=True)
    invited_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                 related_name='project_invitations_sent')
    
    class Meta:
        unique_together = ('project', 'user')
        
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.role})"


class Organization(models.Model):
    """Model for research organizations"""
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name


class ResearchGroup(models.Model):
    """Model for research groups/labs within organizations"""

...
```


### `./apps/project_app/tests.py`

```python
from django.test import TestCase

# Create your tests here.

...
```


### `./apps/project_app/urls.py`

```python
from django.urls import path
from . import views

app_name = 'project_app'

urlpatterns = [
    # Legacy routes for backward compatibility - redirect to user_projects namespace
    # These are accessed via /project/ prefix (configured in config/urls.py)
    path('', views.project_list, name='list'),

    # API endpoints (keep numeric IDs for API)
    path('api/list/', views.api_project_list, name='api_list'),
    path('api/create/', views.api_project_create, name='api_create'),
    path('api/<int:pk>/', views.api_project_detail, name='api_detail'),

    # Backward compatibility redirects
    path('project/<slug:slug>/', views.project_detail_redirect, name='slug_redirect'),
    path('id/<int:pk>/', views.project_detail_redirect, name='detail_redirect'),
]
...
```


### `./apps/project_app/user_urls.py`

```python
from django.urls import path
from . import views

app_name = 'user_projects'

# Wrapper view to pass username from URL kwargs to the view
def user_profile_wrapper(request, username):
    return views.user_profile(request, username)

def user_project_list_wrapper(request, username):
    return views.user_project_list(request, username)

def project_detail_wrapper(request, username, slug):
    return views.project_detail(request, username, slug)

def project_edit_wrapper(request, username, slug):
    return views.project_edit(request, username, slug)

def project_create_from_template_wrapper(request, username, slug):
    return views.project_create_from_template(request, username, slug)

def project_delete_wrapper(request, username, slug):
    return views.project_delete(request, username, slug)

def project_collaborate_wrapper(request, username, slug):
    return views.project_collaborate(request, username, slug)

def project_members_wrapper(request, username, slug):
    return views.project_members(request, username, slug)

def github_integration_wrapper(request, username, slug):
    return views.github_integration(request, username, slug)

def project_directory_wrapper(request, username, slug, directory, subpath=None):
    return views.project_directory(request, username, slug, directory, subpath)

urlpatterns = [
    # GitHub-style username URLs
    # /<username>/ - Profile/Overview (with ?tab= query params)
    # /<username>?tab=repositories - Projects list (GitHub pattern)
    # /<username>/<project-slug>/ - Project detail
    path('', user_profile_wrapper, name='user_profile'),  # /<username>/ with ?tab support
    path('<slug:slug>/', project_detail_wrapper, name='detail'),
    path('<slug:slug>/edit/', project_edit_wrapper, name='edit'),
    path('<slug:slug>/delete/', project_delete_wrapper, name='delete'),
    path('<slug:slug>/create-from-template/', project_create_from_template_wrapper, name='create_from_template'),

    # Settings/Management URLs (GitHub-style /settings/ pattern)
    path('<slug:slug>/settings/', project_edit_wrapper, name='settings'),
    path('<slug:slug>/settings/collaboration/', project_collaborate_wrapper, name='collaborate'),

...
```


### `./apps/project_app/views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib import messages
from django.core.paginator import Paginator
from .models import Project, ProjectMembership, Organization, ResearchGroup
from .decorators import project_required, project_access_required
from django.contrib.auth.models import User
import json


@login_required
def project_list(request):
    """Redirect to user's personal project page (GitHub-style)"""
    return redirect(f'/{request.user.username}/?tab=repositories')


def user_profile(request, username):
    """
    User profile page (GitHub-style /<username>/)

    Public view - no login required (like GitHub)

    Supports tabs via query parameter:
    - /<username>/ or /<username>?tab=overview - Overview
    - /<username>?tab=repositories - Projects list
    - /<username>?tab=stars - Starred projects (future)
    """
    user = get_object_or_404(User, username=username)
    tab = request.GET.get('tab', 'repositories')  # Default to repositories

    if tab == 'repositories':
        return user_project_list(request, username)
    else:
        # For now, all tabs show repositories
        # Future: overview, stars, packages, etc.
        return user_project_list(request, username)


def user_project_list(request, username):
    """List a specific user's projects (called from user_profile with tab=repositories)"""
    user = get_object_or_404(User, username=username)

    # For now, show all projects. Later we can add privacy settings
    user_projects = Project.objects.filter(owner=user).order_by('-updated_at')

    # Check if this is the current user viewing their own projects
    is_own_projects = request.user.is_authenticated and request.user == user


...
```


### `./apps/scholar_app/admin.py`

```python
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import (
    Author, Journal, Topic, SearchIndex, AuthorPaper, Citation, SearchQuery,
    SearchResult, SearchFilter, SavedSearch, Collection, UserLibrary,
    LibraryExport, RecommendationLog, Annotation, AnnotationReply, AnnotationVote,
    CollaborationGroup, GroupMembership, AnnotationTag,
    # Repository models
    Repository, RepositoryConnection, Dataset, DatasetFile, DatasetVersion,
    RepositorySync
)


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['last_name', 'first_name', 'orcid', 'affiliation', 'h_index', 'total_citations']
    list_filter = ['created_at', 'h_index']
    search_fields = ['first_name', 'last_name', 'orcid', 'email', 'affiliation']
    ordering = ['last_name', 'first_name']


@admin.register(Journal)
class JournalAdmin(admin.ModelAdmin):
    list_display = ['name', 'abbreviation', 'issn', 'publisher', 'impact_factor', 'open_access']
    list_filter = ['open_access', 'publisher', 'impact_factor']
    search_fields = ['name', 'abbreviation', 'issn', 'publisher']


@admin.register(Topic)
class TopicAdmin(admin.ModelAdmin):
    list_display = ['name', 'parent', 'paper_count']
    list_filter = ['parent']
    search_fields = ['name', 'description']


@admin.register(SearchIndex)
class SearchIndexAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'publication_date', 'citation_count', 'view_count', 'status']
    list_filter = ['document_type', 'status', 'source', 'is_open_access', 'publication_date']
    search_fields = ['title', 'abstract', 'doi', 'pmid', 'arxiv_id']
    date_hierarchy = 'publication_date'
    ordering = ['-publication_date']


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'is_public', 'paper_count_display', 'created_at']
    list_filter = ['is_public', 'created_at']

...
```


### `./apps/scholar_app/api_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# API key management views for Scholar app

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
import json
import logging

from .models import UserPreference

logger = logging.getLogger(__name__)


@login_required
def api_key_management(request):
    """API key management dashboard for users"""
    user_prefs = UserPreference.get_or_create_for_user(request.user)
    
    if request.method == 'POST':
        # Handle API key updates
        source = request.POST.get('source')
        api_key = request.POST.get('api_key', '').strip()
        
        if source == 'unpaywall':
            # Special case for unpaywall (uses email)
            user_prefs.unpaywall_email = api_key
            user_prefs.save()
            messages.success(request, f"Unpaywall email updated successfully!")
        elif source in ['pubmed', 'google_scholar', 'semantic_scholar', 'crossref']:
            if api_key:
                user_prefs.set_api_key(source, api_key)
                messages.success(request, f"{source.replace('_', ' ').title()} API key updated successfully!")
            else:
                # Clear the API key
                user_prefs.set_api_key(source, '')
                messages.info(request, f"{source.replace('_', ' ').title()} API key cleared.")
        else:
            messages.error(request, "Invalid API source specified.")
        
        return redirect('scholar_app:api_keys')
    
    # Get current API key status
    api_status = {
        'pubmed': user_prefs.has_api_key('pubmed'),
        'google_scholar': user_prefs.has_api_key('google_scholar'),

...
```


### `./apps/scholar_app/apps.py`

```python
from django.apps import AppConfig


class ScholarConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.scholar_app'
    verbose_name = 'Scholar'
...
```


### `./apps/scholar_app/bibtex_models.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/bibtex_models.py

"""
BibTeX Enrichment Models

Models for tracking BibTeX file enrichment jobs.
"""

from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class BibTeXEnrichmentJob(models.Model):
    """Track BibTeX enrichment jobs for users."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]

    BROWSER_MODE_CHOICES = [
        ('stealth', 'Stealth Mode'),
        ('interactive', 'Interactive Mode'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bibtex_jobs')

    # Input
    input_file = models.FileField(upload_to='bibtex_uploads/%Y/%m/%d/')
    project_name = models.CharField(max_length=200, blank=True, help_text="Optional project name for organization")

    # Processing parameters
    num_workers = models.IntegerField(default=4, help_text="Number of parallel workers")
    browser_mode = models.CharField(max_length=20, choices=BROWSER_MODE_CHOICES, default='stealth')

    # Output
    output_file = models.FileField(upload_to='bibtex_enriched/%Y/%m/%d/', blank=True, null=True)

    # Progress tracking
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_papers = models.IntegerField(default=0)
    processed_papers = models.IntegerField(default=0)

...
```


### `./apps/scholar_app/bibtex_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# File: /home/ywatanabe/proj/scitex-cloud/apps/scholar_app/bibtex_views.py

"""
BibTeX Enrichment Views

Provides functionality to upload BibTeX files and enrich them with:
- Citation counts from multiple sources
- Journal impact factors
- PDF downloads
- Additional metadata
- Full-text extraction

Uses scitex.scholar.pipelines.ScholarPipelineBibTeX under the hood.
"""

import asyncio
import json
from pathlib import Path
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, FileResponse
from django.views.decorators.http import require_http_methods
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone
from django.conf import settings
from .models import BibTeXEnrichmentJob


@login_required
def bibtex_enrichment(request):
    """BibTeX enrichment landing page - upload and manage enrichment jobs."""

    # Get user's recent enrichment jobs
    recent_jobs = BibTeXEnrichmentJob.objects.filter(
        user=request.user
    ).order_by('-created_at')[:10]

    context = {
        'recent_jobs': recent_jobs,
    }

    return render(request, 'scholar_app/bibtex_enrichment.html', context)


@login_required
@require_http_methods(["POST"])

...
```


### `./apps/scholar_app/default_workspace_views.py`

```python
"""Default workspace views for Scholar app."""
from django.shortcuts import render


def guest_session_view(request, username):
    """Guest session workspace for Scholar."""
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'module_name': 'Scholar',
        'module_icon': 'fa-search',
    }
    return render(request, 'scholar_app/default_workspace.html', context)


def user_default_workspace(request):
    """Default workspace for logged-in users without a specific project."""
    context = {
        'is_guest_session': False,
        'username': request.user.username if request.user.is_authenticated else None,
        'module_name': 'Scholar',
        'module_icon': 'fa-search',
    }
    return render(request, 'scholar_app/default_workspace.html', context)

...
```


### `./apps/scholar_app/doi_services.py`

```python
"""
DOI assignment and metadata management services.
Handles DOI minting, metadata updates, and citation formatting for research outputs.
"""

import requests
import json
import logging
import xml.etree.ElementTree as ET
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.conf import settings
from django.utils import timezone
from django.core.exceptions import ValidationError

from .models import Dataset, SearchIndex, Repository, RepositoryConnection
from .repository_services import RepositoryServiceFactory

logger = logging.getLogger(__name__)


class DOIServiceError(Exception):
    """Base exception for DOI service errors"""
    pass


class DOIMetadataError(DOIServiceError):
    """DOI metadata related errors"""
    pass


class DOIAssignmentError(DOIServiceError):
    """DOI assignment related errors"""
    pass


class DataCiteMetadataBuilder:
    """Builder for DataCite metadata XML"""
    
    def __init__(self):
        self.metadata = {}
    
    def build_dataset_metadata(self, dataset: Dataset) -> str:
        """Build DataCite metadata XML for a dataset"""
        
        # Create root element
        root = ET.Element('resource')
        root.set('xmlns:xsi', 'http://www.w3.org/2001/XMLSchema-instance')
        root.set('xmlns', 'http://datacite.org/schema/kernel-4')
        root.set('xsi:schemaLocation', 'http://datacite.org/schema/kernel-4 http://schema.datacite.org/meta/kernel-4.4/metadata.xsd')

...
```


### `./apps/scholar_app/__init__.py`

```python

...
```


### `./apps/scholar_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from django.contrib.postgres.search import SearchVectorField
from django.contrib.postgres.indexes import GinIndex
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cryptography.fernet import Fernet
from django.conf import settings
import uuid
import base64


class Author(models.Model):
    """Author information for research papers"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    middle_name = models.CharField(max_length=100, blank=True)
    orcid = models.CharField(max_length=19, blank=True, db_index=True)  # ORCID format: 0000-0000-0000-0000
    email = models.EmailField(blank=True)
    affiliation = models.CharField(max_length=500, blank=True)
    h_index = models.IntegerField(null=True, blank=True)
    total_citations = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['last_name', 'first_name']
        indexes = [
            models.Index(fields=['last_name', 'first_name']),
            models.Index(fields=['orcid']),
        ]

    def __str__(self):
        return f"{self.last_name}, {self.first_name}"

    @property
    def full_name(self):
        parts = [self.first_name]
        if self.middle_name:
            parts.append(self.middle_name)
        parts.append(self.last_name)
        return ' '.join(parts)


class Journal(models.Model):
    """Journal metadata"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, unique=True)

...
```


### `./apps/scholar_app/project_views.py`

```python
"""
Project-specific views for Scholar app.
"""

from django.shortcuts import render, get_object_or_404
from apps.project_app.models import Project


def project_search(request, project_id):
    """Scholar search interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    context = {
        'project': project,
    }
    return render(request, 'scholar_app/project_search.html', context)

...
```


### `./apps/scholar_app/repository_services.py`

```python
"""
Repository services for managing connections to research data repositories.
This module provides APIs for interacting with various research data repositories
including Zenodo, Figshare, Dryad, and institutional repositories.
"""

import requests
import json
import logging
import hashlib
import mimetypes
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from .models import Repository, RepositoryConnection, Dataset, DatasetFile, RepositorySync

logger = logging.getLogger(__name__)


class RepositoryServiceError(Exception):
    """Base exception for repository service errors"""
    pass


class AuthenticationError(RepositoryServiceError):
    """Authentication-related errors"""
    pass


class APIError(RepositoryServiceError):
    """API-related errors"""
    pass


class ValidationError(RepositoryServiceError):
    """Data validation errors"""
    pass


class BaseRepositoryService(ABC):
    """Base class for repository service implementations"""
    
    def __init__(self, repository_connection: RepositoryConnection):
        self.connection = repository_connection
        self.repository = repository_connection.repository
        self.logger = logging.getLogger(f"{self.__class__.__name__}")

...
```


### `./apps/scholar_app/repository_views.py`

```python
"""
API views for research data repository management.
Provides endpoints for managing repository connections, datasets, and synchronization.
"""

import json
import logging
from typing import Dict, Any
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404
from django.db import transaction
from django.utils import timezone
from django.conf import settings
from rest_framework import status, viewsets, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import (
    Repository, RepositoryConnection, Dataset, DatasetFile, 
    DatasetVersion, RepositorySync
)
from .repository_services import (
    RepositoryServiceFactory, RepositoryServiceError,
    sync_dataset_with_repository, upload_dataset_to_repository
)

logger = logging.getLogger(__name__)


class RepositoryViewSet(viewsets.ReadOnlyModelViewSet):
    """ViewSet for listing available repositories"""
    
    queryset = Repository.objects.filter(status='active')
    permission_classes = [IsAuthenticated]
    
    def list(self, request):
        """List all available repositories"""
        repositories = self.get_queryset()
        
        data = []
        for repo in repositories:
            data.append({
                'id': str(repo.id),
                'name': repo.name,
                'type': repo.repository_type,

...
```


### `./apps/scholar_app/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import SearchQuery, SearchResult, SearchIndex, Author, Journal


class SearchModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create paper index entries
        from datetime import date
        self.paper1 = SearchIndex.objects.create(
            title='Machine Learning in Science',
            abstract='This paper explores ML applications...',
            publication_date=date(2023, 1, 15),
            doi='10.1234/ml2023',
            relevance_score=1.0
        )
        
        self.paper2 = SearchIndex.objects.create(
            title='Deep Learning for Image Analysis',
            abstract='Deep learning techniques for medical imaging...',
            publication_date=date(2023, 3, 20),
            doi='10.1234/dl2023',
            relevance_score=1.0
        )
    
    def test_paper_index_creation(self):
        """Test paper index creation"""
        self.assertEqual(self.paper1.title, 'Machine Learning in Science')
        self.assertEqual(self.paper1.doi, '10.1234/ml2023')
        self.assertIsNotNone(self.paper1.created_at)
    
    def test_search_query_creation(self):
        """Test search query creation"""
        query = SearchQuery.objects.create(
            user=self.user,
            query_text='machine learning',
            filters={'year': 2023, 'field': 'computer science'}
        )
        
        self.assertEqual(query.user, self.user)
        self.assertEqual(query.query_text, 'machine learning')
        self.assertEqual(query.filters['year'], 2023)
    

...
```


### `./apps/scholar_app/urls.py`

```python
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views, simple_views, repository_views, api_views, bibtex_views, default_workspace_views

app_name = 'scholar_app'

# Repository API Router
router = DefaultRouter()
router.register(r'repositories', repository_views.RepositoryViewSet, basename='repositories')
router.register(r'connections', repository_views.RepositoryConnectionViewSet, basename='connections')
router.register(r'datasets', repository_views.DatasetViewSet, basename='datasets')

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # MVP Simple Interface
    path('', simple_views.index, name='index'),
    path('search/', simple_views.simple_search, name='simple_search'),
    path('project/<int:project_id>/search/', simple_views.project_search, name='project_search'),
    path('project/<int:project_id>/library/', simple_views.project_library, name='project_library'),
    path('library/', simple_views.personal_library, name='personal_library'),
    path('features/', simple_views.features, name='features'),
    path('pricing/', simple_views.pricing, name='pricing'),
    
    # MVP API endpoints
    path('api/save-paper/', simple_views.save_paper, name='save_paper'),
    path('api/upload-file/', simple_views.upload_file, name='upload_file'),
    path('api/get-citation/', simple_views.get_citation, name='get_citation'),
    
    # User Preferences API endpoints
    path('api/preferences/', simple_views.get_user_preferences, name='get_user_preferences'),
    path('api/preferences/save/', simple_views.save_user_preferences, name='save_user_preferences'),
    path('api/preferences/sources/', simple_views.save_source_preferences, name='save_source_preferences'),
    
    # API Key Management endpoints
    path('api-keys/', api_views.api_key_management, name='api_keys'),
    path('api/test-api-key/', api_views.test_api_key, name='test_api_key'),
    path('api/usage-stats/', api_views.api_usage_stats, name='api_usage_stats'),
    
    # Saved Search API endpoints
    path('api/save-search/', simple_views.save_search, name='save_search'),
    path('api/saved-searches/', simple_views.get_saved_searches, name='get_saved_searches'),
    path('api/saved-searches/<uuid:search_id>/delete/', simple_views.delete_saved_search, name='delete_saved_search'),
    path('api/saved-searches/<uuid:search_id>/run/', simple_views.run_saved_search, name='run_saved_search'),
    
    # Progressive search API endpoints
    path('api/search/arxiv/', simple_views.api_search_arxiv, name='api_search_arxiv'),
    path('api/search/pubmed/', simple_views.api_search_pubmed, name='api_search_pubmed'),
    path('api/search/semantic/', simple_views.api_search_semantic, name='api_search_semantic'),

...
```


### `./apps/scholar_app/utils.py`

```python
"""
Utility functions for Scholar module citation export functionality.
"""
import re
from datetime import datetime
from typing import List, Dict, Any
from .models import SearchIndex, Author, LibraryExport


class CitationExporter:
    """Handle citation exports in various formats"""
    
    @staticmethod
    def clean_string(text: str) -> str:
        """Clean string for citation format compatibility"""
        if not text:
            return ""
        # Remove special characters that could break citation formats
        text = re.sub(r'[{}\[\]\\]', '', text)
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        return text
    
    @staticmethod
    def format_authors_bibtex(authors: List[Author]) -> str:
        """Format authors for BibTeX"""
        if not authors:
            return ""
        
        author_strings = []
        for author in authors:
            if author.last_name and author.first_name:
                # BibTeX format: "Last, First Middle"
                name_parts = [author.last_name]
                if author.first_name:
                    name_parts.append(author.first_name)
                if author.middle_name:
                    name_parts.append(author.middle_name)
                author_strings.append(f"{name_parts[0]}, {' '.join(name_parts[1:])}")
            elif author.last_name:
                author_strings.append(author.last_name)
                
        return " and ".join(author_strings)
    
    @staticmethod
    def format_authors_ris(authors: List[Author]) -> List[str]:
        """Format authors for RIS format"""
        if not authors:
            return []
        

...
```


### `./apps/scholar_app/views.py`

```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q, Count, Avg, F, Prefetch
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from django.contrib.postgres.search import SearchVector, SearchQuery, SearchRank
from django.db import transaction
from django.core.cache import cache
from django.views.decorators.cache import cache_page
# from django.utils.cache import make_template_fragment_key  # Removed - not available in newer Django
import json
import csv
import io
import hashlib
from datetime import datetime, timedelta

from .models import (
    SearchIndex, Author, Journal, Topic, Citation,
    SearchQuery, SearchResult, SavedSearch, RecommendationLog,
    AuthorPaper, SearchFilter
)
from . import default_workspace_views
from . import project_views

# Expose default workspace views
guest_session_view = default_workspace_views.guest_session_view
user_default_workspace = default_workspace_views.user_default_workspace

# Expose project views
project_search = project_views.project_search


@login_required
def index(request):
    """Scholar app - redirect to user's projects."""
    messages.info(request, 'Please select or create a project to use Scholar.')
    return redirect('user_projects:user_projects', username=request.user.username)


def features(request):
    """Search features view."""
    return render(request, 'scholar_app/features.html')


def pricing(request):
    """Search pricing view."""
    return render(request, 'scholar_app/pricing.html')

...
```


### `./apps/viz_app/admin.py`

```python

...
```


### `./apps/viz_app/api_views.py`

```python
#!/usr/bin/env python3
"""
API views for SciTeX-Viz visualization platform.
"""

import json
import logging
import threading
import uuid
from typing import Dict, Any, List

from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.db import transaction, models
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils import timezone

from .models import (
    Visualization, VisualizationType, DataSource, Dashboard,
    DashboardVisualization, VisualizationShare, ExportJob,
    ColorScheme, VisualizationTemplate, ChartConfiguration,
    InteractiveElement, VisualizationComment, VisualizationAnalytics
)
from .code_integration import get_viz_data_sources_for_user

logger = logging.getLogger(__name__)


@method_decorator(login_required, name='dispatch')
class VizAPIView(View):
    """Base API view for visualization operations."""
    
    def get_user_visualizations(self):
        return Visualization.objects.filter(owner=self.request.user)


class VisualizationListAPI(VizAPIView):
    """API for listing and creating visualizations."""
    
    def get(self, request):
        """List user's visualizations."""
        try:
            visualizations = self.get_user_visualizations().select_related(
                'visualization_type', 'data_source', 'color_scheme'
            ).order_by('-updated_at')

...
```


### `./apps/viz_app/apps.py`

```python
from django.apps import AppConfig


class VizAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.viz_app'
    verbose_name = 'Viz'
...
```


### `./apps/viz_app/code_integration.py`

```python
#!/usr/bin/env python3
"""
Code-Viz Integration Bridge for SciTeX-Cloud
Connects Code execution results with Viz module data sources.
"""

import json
import uuid
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging

from django.contrib.auth.models import User
from django.utils import timezone
from django.conf import settings

from .models import DataSource, Visualization, VisualizationType
from apps.code_app.models import CodeExecutionJob

logger = logging.getLogger(__name__)


class CodeVizBridge:
    """Bridge between Code execution results and Viz module data sources."""
    
    def __init__(self):
        self.media_root = Path(settings.MEDIA_ROOT)
    
    def create_data_source_from_code_job(self, code_job: CodeExecutionJob) -> Optional[DataSource]:
        """Create a Viz data source from completed code execution job."""
        try:
            if code_job.status != 'completed':
                logger.warning(f"Code job {code_job.job_id} not completed, cannot create data source")
                return None
            
            # Extract data and metadata from code job
            data_source_name = f"Code Execution - {code_job.job_id}"
            
            # Prepare connection config with code job metadata
            connection_config = {
                'code_job_id': str(code_job.job_id),
                'execution_type': code_job.execution_type,
                'created_at': code_job.created_at.isoformat(),
                'completed_at': code_job.completed_at.isoformat() if code_job.completed_at else None,
                'output_files': code_job.output_files,
                'plot_files': code_job.plot_files,
                'source_code_preview': code_job.source_code[:500] + "..." if len(code_job.source_code) > 500 else code_job.source_code,
            }
            
            # Extract data schema if available

...
```


### `./apps/viz_app/default_workspace_views.py`

```python
"""Default workspace views for Viz app."""
from django.shortcuts import render


def guest_session_view(request, username):
    """Guest session workspace for Viz."""
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'module_name': 'Viz',
        'module_icon': 'fa-chart-bar',
    }
    return render(request, 'viz_app/default_workspace.html', context)


def user_default_workspace(request):
    """Default workspace for logged-in users without a specific project."""
    context = {
        'is_guest_session': False,
        'username': request.user.username if request.user.is_authenticated else None,
        'module_name': 'Viz',
        'module_icon': 'fa-chart-bar',
    }
    return render(request, 'viz_app/default_workspace.html', context)

...
```


### `./apps/viz_app/__init__.py`

```python

...
```


### `./apps/viz_app/models.py`

```python
import uuid
from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class VisualizationType(models.Model):
    """Different types of visualizations available in the system"""
    
    CATEGORY_CHOICES = [
        ('basic', 'Basic Charts'),
        ('statistical', 'Statistical Plots'),
        ('scientific', 'Scientific Visualization'),
        ('3d', '3D Visualization'),
        ('network', 'Network Graphs'),
        ('temporal', 'Time Series'),
        ('geospatial', 'Geospatial'),
    ]
    
    name = models.CharField(max_length=100, unique=True)
    display_name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES)
    description = models.TextField()
    icon = models.CharField(max_length=50, blank=True)  # Icon class name
    default_config = models.JSONField(default=dict)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['category', 'display_name']
    
    def __str__(self):
        return self.display_name


class ColorScheme(models.Model):
    """Custom color schemes for visualizations"""
    
    name = models.CharField(max_length=100)
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='color_schemes')
    colors = models.JSONField()  # List of hex colors
    is_public = models.BooleanField(default=False)
    category = models.CharField(max_length=50, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:

...
```


### `./apps/viz_app/project_views.py`

```python
"""
Project-specific views for Viz app.
"""

from django.shortcuts import render, get_object_or_404
from apps.project_app.models import Project


def project_viz(request, project_id):
    """Viz interface for a specific project."""
    project = get_object_or_404(Project, id=project_id)

    context = {
        'project': project,
    }
    return render(request, 'viz_app/project_viz.html', context)

...
```


### `./apps/viz_app/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Visualization, VisualizationTemplate, DataSource, VisualizationType
import json


class VizModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create visualization type first
        self.viz_type, _ = VisualizationType.objects.get_or_create(
            name='line',
            defaults={
                'display_name': 'Line Chart',
                'category': 'basic',
                'description': 'Basic line chart visualization',
                'default_config': {
                    'type': 'object',
                    'properties': {
                        'title': {'type': 'string'},
                        'x_axis': {'type': 'string'},
                        'y_axis': {'type': 'string'}
                    }
                }
            }
        )
        
        # Create visualization template
        self.template = VisualizationTemplate.objects.create(
            name='Line Chart',
            owner=self.user,
            visualization_type=self.viz_type,
            configuration={
                'type': 'object',
                'properties': {
                    'title': {'type': 'string'},
                    'x_axis': {'type': 'string'},
                    'y_axis': {'type': 'string'}
                }
            }
        )
        
        # Create data source
        self.data_source = DataSource.objects.create(

...
```


### `./apps/viz_app/urls.py`

```python
from django.urls import path
from . import views, api_views, default_workspace_views

app_name = 'viz_app'

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # Basic pages
    path('', views.index, name='index'),
    path('features/', views.features, name='features'),
    
    # Main dashboard and visualization management
    path('dashboard/', views.viz_dashboard, name='viz_dashboard'),
    path('create/', views.create_visualization, name='create_visualization'),
    path('edit/<uuid:pk>/', views.edit_visualization, name='edit_visualization'),
    path('view/<uuid:pk>/', views.view_visualization, name='view_visualization'),
    path('view/<uuid:pk>/<str:share_token>/', views.view_visualization, name='view_shared_visualization'),
    path('embed/<uuid:pk>/', views.embedded_view, name='embedded_view'),
    path('embed/<uuid:pk>/<str:embed_token>/', views.embedded_view, name='embedded_view_token'),
    
    # Dashboard management
    path('dashboards/', views.dashboard_list, name='dashboard_list'),
    path('dashboards/create/', views.create_dashboard, name='create_dashboard'),
    path('dashboards/edit/<uuid:pk>/', views.edit_visualization, name='edit_dashboard'),
    
    # Data source management
    path('data-sources/', views.data_source_management, name='data_source_management'),
    
    # Export and sharing
    path('export/<uuid:pk>/', views.export_visualization, name='export_visualization'),
    path('share/<uuid:pk>/', views.share_visualization, name='share_visualization'),
    path('export-status/<uuid:job_id>/', views.export_status, name='export_status'),
    
    # AJAX endpoints
    path('api/update-data/<uuid:pk>/', views.update_visualization_data, name='update_visualization_data'),
    path('api/add-comment/<uuid:pk>/', views.add_comment, name='add_comment'),
    
    # New API endpoints for interactive viz interface
    path('api/visualizations/', api_views.VisualizationListAPI.as_view(), name='api_visualizations'),
    path('api/visualizations/<uuid:viz_id>/', api_views.VisualizationDetailAPI.as_view(), name='api_visualization_detail'),
    path('api/data-sources/', api_views.DataSourceAPI.as_view(), name='api_data_sources'),
    path('api/visualization-types/', api_views.VisualizationTypesAPI.as_view(), name='api_visualization_types'),
    path('api/color-schemes/', api_views.ColorSchemesAPI.as_view(), name='api_color_schemes'),
    path('api/export/<uuid:viz_id>/', api_views.ExportAPI.as_view(), name='api_export'),
    path('api/upload-data/', api_views.upload_data, name='api_upload_data'),
    path('api/export-status/<uuid:job_id>/', api_views.export_job_status, name='api_export_status'),
    path('api/sample-data/', api_views.generate_sample_data, name='api_sample_data'),
    

...
```


### `./apps/viz_app/views.py`

```python
import json
import uuid
import os
from datetime import datetime, timedelta

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
from django.db.models import Q, Count, Avg, Sum, F
from django.core.paginator import Paginator
from django.core.exceptions import PermissionDenied
from django.utils import timezone
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

from .models import (
    Visualization, VisualizationType, DataSource, Dashboard,
    DashboardVisualization, VisualizationShare, ExportJob,
    ColorScheme, VisualizationTemplate, ChartConfiguration,
    InteractiveElement, VisualizationComment, VisualizationAnalytics
)
from . import default_workspace_views
from . import project_views

# Expose default workspace views
guest_session_view = default_workspace_views.guest_session_view
user_default_workspace = default_workspace_views.user_default_workspace

# Expose project views
project_viz = project_views.project_viz


@login_required
def index(request):
    """Viz app - redirect to user's projects."""
    messages.info(request, 'Please select or create a project to use Viz.')
    # Force message to be stored before redirect
    request.session.modified = True
    return redirect('user_projects:user_projects', username=request.user.username)


def features(request):
    """Viz features view."""
    return render(request, 'viz_app/features.html')


...
```


### `./apps/writer_app/admin.py`

```python
from django.contrib import admin
from .models import (
    DocumentTemplate, Manuscript, ManuscriptSection, Figure, Table, Citation,
    CompilationJob, AIAssistanceLog, CollaborativeSession, DocumentChange,
    ManuscriptVersion, ManuscriptBranch, DiffResult, MergeRequest,
    ArxivAccount, ArxivCategory, ArxivSubmission, ArxivSubmissionHistory,
    ArxivValidationResult, ArxivApiResponse
)


# Writer App Admin
@admin.register(DocumentTemplate)
class DocumentTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'journal_name', 'is_public', 'usage_count', 'created_at']
    list_filter = ['template_type', 'is_public', 'created_at']
    search_fields = ['name', 'journal_name', 'description']
    readonly_fields = ['usage_count', 'created_at', 'updated_at']


@admin.register(Manuscript)
class ManuscriptAdmin(admin.ModelAdmin):
    list_display = ['title', 'owner', 'status', 'project', 'is_modular', 'word_count_total', 'updated_at']
    list_filter = ['status', 'is_modular', 'is_public', 'created_at']
    search_fields = ['title', 'abstract', 'keywords']
    readonly_fields = ['slug', 'word_count_total', 'citation_count', 'created_at', 'updated_at', 'last_compiled']
    filter_horizontal = ['collaborators']


@admin.register(ManuscriptSection)
class ManuscriptSectionAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'section_type', 'title', 'order', 'updated_at']
    list_filter = ['section_type', 'created_at']
    search_fields = ['title', 'content']


@admin.register(CompilationJob)
class CompilationJobAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'status', 'compilation_type', 'initiated_by', 'compilation_time', 'created_at']
    list_filter = ['status', 'compilation_type', 'created_at']
    readonly_fields = ['job_id', 'compilation_time', 'page_count', 'created_at', 'started_at', 'completed_at']


@admin.register(AIAssistanceLog)
class AIAssistanceLogAdmin(admin.ModelAdmin):
    list_display = ['manuscript', 'user', 'assistance_type', 'accepted', 'tokens_used', 'created_at']
    list_filter = ['assistance_type', 'accepted', 'created_at']
    readonly_fields = ['response_time', 'created_at']


# arXiv Integration Admin

...
```


### `./apps/writer_app/ai_assistant.py`

```python
"""
AI Writing Assistant for SciTeX Writer.
Context-aware content generation and improvement suggestions.
"""

import os
from typing import Dict, List, Optional
from django.conf import settings


class WriterAI:
    """AI assistant for scientific writing."""

    def __init__(self):
        """Initialize AI client."""
        self.api_key = os.getenv('ANTHROPIC_API_KEY') or os.getenv('OPENAI_API_KEY')
        self.model = 'claude-3-5-sonnet-20241022'  # or 'gpt-4'
        self.use_anthropic = os.getenv('ANTHROPIC_API_KEY') is not None

    def get_suggestion(
        self,
        content: str,
        section_type: str,
        target: str = 'clarity',
        context: Optional[Dict] = None
    ) -> Dict:
        """
        Get AI suggestions for improving text.

        Args:
            content: Current section content
            section_type: Type of section (abstract, introduction, methods, etc.)
            target: Improvement target (clarity, conciseness, academic_style, etc.)
            context: Additional context (other sections, project info)

        Returns:
            Dict with suggested_text, explanation, and changes
        """
        prompt = self._build_improvement_prompt(content, section_type, target, context)

        if self.use_anthropic:
            return self._call_anthropic(prompt)
        else:
            return self._call_openai(prompt)

    def generate_content(
        self,
        section_type: str,
        target_words: int,
        context: Optional[Dict] = None

...
```


### `./apps/writer_app/apps.py`

```python
from django.apps import AppConfig


class WriterAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.writer_app'
    verbose_name = 'Writer'
...
```


### `./apps/writer_app/arxiv_formatters.py`

```python
"""
arXiv Manuscript Formatting Utilities

This module provides specialized formatters for converting SciTeX manuscripts
to arXiv-compatible formats, including LaTeX cleanup, bibliography processing,
and PDF generation with arXiv requirements.
"""

import os
import re
import subprocess
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple

from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import ArxivSubmission, Citation, Figure, Manuscript, Table


class ArxivLatexFormatter:
    """Format LaTeX content for arXiv submission compliance."""
    
    def __init__(self):
        self.arxiv_class_options = {
            'article': r'\documentclass[12pt]{article}',
            'revtex': r'\documentclass[12pt,prd,aps]{revtex4-2}',  # For physics papers
            'neurips': r'\documentclass[final]{neurips_2023}',      # For ML papers
        }
        
        # arXiv-approved packages
        self.approved_packages = {
            'amsmath', 'amsfonts', 'amssymb', 'amsthm',
            'graphicx', 'cite', 'natbib', 'biblatex',
            'hyperref', 'url', 'geometry', 'fancyhdr',
            'array', 'booktabs', 'longtable', 'multirow',
            'algorithm', 'algorithmic', 'algorithm2e',
            'listings', 'xcolor', 'tikz', 'pgfplots',
            'subcaption', 'caption', 'float'
        }
        
        # Packages to remove or replace
        self.problematic_packages = {
            'pstricks': None,  # Not supported on arXiv
            'xy': 'xymatrix',  # Replace with xymatrix
            'pdfpages': None,  # Not allowed
            'epstopdf': None,  # Automatic conversion

...
```


### `./apps/writer_app/arxiv_services.py`

```python
"""
arXiv Integration Services for SciTeX Writer

This module provides services for integrating with arXiv submission system,
including account verification, manuscript formatting, and submission workflow.
"""

import os
import shutil
import tempfile
import zipfile
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union

import requests
from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone
from django.utils.text import slugify

from .models import (
    ArxivAccount, ArxivApiResponse, ArxivCategory, ArxivSubmission,
    ArxivSubmissionHistory, ArxivValidationResult, Manuscript
)


class ArxivAPIException(Exception):
    """Custom exception for arXiv API errors."""
    pass


class ArxivAccountService:
    """Service for managing arXiv account verification and authentication."""
    
    def __init__(self):
        self.base_url = getattr(settings, 'ARXIV_API_BASE_URL', 'https://arxiv.org/api')
        self.submission_url = getattr(settings, 'ARXIV_SUBMISSION_URL', 'https://arxiv.org/submit')
    
    def verify_account(self, arxiv_account: ArxivAccount) -> bool:
        """
        Verify arXiv account credentials by attempting authentication.
        
        Args:
            arxiv_account: ArxivAccount instance to verify
            
        Returns:
            bool: True if verification successful, False otherwise
        """

...
```


### `./apps/writer_app/arxiv_views.py`

```python
"""
arXiv Submission Views for SciTeX Writer

This module provides views for handling arXiv submissions, including account setup,
manuscript submission workflow, status tracking, and submission management.
"""

import json
from datetime import datetime
from typing import Dict, Optional

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ObjectDoesNotExist, PermissionDenied
from django.db import transaction
from django.http import HttpRequest, HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods, require_POST
from django.views.generic import ListView, TemplateView

from .arxiv_services import (
    ArxivAccountService, ArxivAPIException, ArxivCategoryService,
    ArxivIntegrationService, ArxivSubmissionService
)
from .models import (
    ArxivAccount, ArxivCategory, ArxivSubmission, ArxivSubmissionHistory,
    ArxivValidationResult, Manuscript
)


class ArxivDashboardView(TemplateView):
    """Main dashboard for arXiv submissions."""
    template_name = 'writer_app/arxiv/dashboard.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        if self.request.user.is_authenticated:
            integration_service = ArxivIntegrationService()
            context['user_status'] = integration_service.get_user_submission_status(self.request.user)
            context['recent_submissions'] = ArxivSubmission.objects.filter(
                user=self.request.user
            ).order_by('-created_at')[:5]
        
        return context


@login_required

...
```


### `./apps/writer_app/consumers.py`

```python
"""
WebSocket consumers for SciTeX Writer real-time collaboration.
Uses Django 5.2 async ORM for optimal performance.
"""

from channels.generic.websocket import AsyncWebsocketConsumer
import json
from datetime import datetime
from .models import Manuscript, CollaborativeSession, DocumentChange


class WriterConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer for real-time collaborative editing.

    Handles:
    - User presence (join/leave notifications)
    - Section locking
    - Real-time text changes
    - Cursor position broadcasting
    """

    async def connect(self):
        """Handle new WebSocket connection."""
        self.manuscript_id = self.scope['url_route']['kwargs']['manuscript_id']
        self.room_group_name = f'manuscript_{self.manuscript_id}'
        self.user = self.scope['user']

        # Reject anonymous users
        if not self.user.is_authenticated:
            await self.close()
            return

        # Django 5.2 async ORM: Check manuscript access
        try:
            self.manuscript = await Manuscript.objects.select_related('owner', 'project').aget(
                id=self.manuscript_id
            )
        except Manuscript.DoesNotExist:
            await self.close()
            return

        # Check permissions
        has_access = await self.check_access()
        if not has_access:
            await self.close()
            return

        # Join room group
        await self.channel_layer.group_add(

...
```


### `./apps/writer_app/default_workspace_views.py`

```python
"""
Views for default workspace (guest sessions and user default workspace).

Handles:
- /guest-<sessionid>/default/writer/
- /<username>/default/writer/
"""

from django.shortcuts import render
from django.http import JsonResponse


def guest_session_view(request, username):
    """
    Guest session workspace for Writer.

    URL: /guest-<sessionid>/default/writer/

    Provides session-isolated workspace for anonymous users.
    """
    context = {
        'is_guest_session': True,
        'guest_username': username,
        'workspace_type': 'guest',
        'session_id': username.replace('guest-', ''),
    }
    return render(request, 'writer_app/default_workspace.html', context)


def user_default_workspace(request):
    """
    Default workspace for logged-in users without a specific project.

    URL: /writer/workspace/

    Temporary workspace until user creates a project.
    """
    context = {
        'is_guest_session': False,
        'workspace_type': 'default',
        'username': request.user.username if request.user.is_authenticated else None,
    }
    return render(request, 'writer_app/default_workspace.html', context)

...
```


### `./apps/writer_app/__init__.py`

```python

...
```


### `./apps/writer_app/models.py`

```python
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta
import uuid
import os
from pathlib import Path


class DocumentTemplate(models.Model):
    """Templates for different journals and document types."""
    TEMPLATE_TYPES = [
        ('article', 'Journal Article'),
        ('conference', 'Conference Paper'),
        ('thesis', 'Thesis/Dissertation'),
        ('report', 'Technical Report'),
        ('book', 'Book/Chapter'),
        ('preprint', 'Preprint'),
        ('custom', 'Custom Template'),
    ]
    
    name = models.CharField(max_length=200)
    template_type = models.CharField(max_length=20, choices=TEMPLATE_TYPES)
    journal_name = models.CharField(max_length=200, blank=True)
    
    # Template files
    latex_template = models.TextField()
    style_file = models.TextField(blank=True)  # .sty content
    bibliography_style = models.CharField(max_length=50, default='plain')
    
    # Metadata
    description = models.TextField(blank=True)
    thumbnail = models.ImageField(upload_to='doc_templates/', blank=True, null=True)
    is_public = models.BooleanField(default=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='doc_templates')
    
    # Usage tracking
    usage_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.get_template_type_display()})"



...
```


### `./apps/writer_app/operational_transform.py`

```python
"""
Operational Transform (OT) implementation for SciTeX Writer.
Based on proven algorithms from ShareJS and Overleaf.

References:
- https://en.wikipedia.org/wiki/Operational_transformation
- https://github.com/Operational-Transformation/ot.js
"""

from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from enum import Enum


class OpType(Enum):
    """Operation types for text transformation."""
    RETAIN = 'retain'
    INSERT = 'insert'
    DELETE = 'delete'


@dataclass
class Operation:
    """Single operation in an OT sequence."""
    type: OpType
    chars: Optional[str] = None  # For INSERT/DELETE
    count: Optional[int] = None  # For RETAIN/DELETE
    
    def __str__(self):
        if self.type == OpType.RETAIN:
            return f"retain({self.count})"
        elif self.type == OpType.INSERT:
            return f"insert('{self.chars}')"
        elif self.type == OpType.DELETE:
            return f"delete({self.count})"


class TextOperation:
    """
    A sequence of operations that can be applied to a text document.
    
    Example:
        text = "Hello world"
        op = TextOperation([
            Operation(OpType.RETAIN, count=6),  # Keep "Hello "
            Operation(OpType.INSERT, chars="beautiful "),  # Insert "beautiful "
            Operation(OpType.RETAIN, count=5),  # Keep "world"
        ])
        result = op.apply("Hello world")  # "Hello beautiful world"
    """

...
```


### `./apps/writer_app/operational_transforms.py`

```python
"""
Operational Transform implementation for real-time collaborative editing.
Handles conflict resolution when multiple users edit the same document simultaneously.
"""
import json
from typing import Dict, List, Tuple, Any
from datetime import datetime


class Operation:
    """Represents a single operation (insert, delete, replace) on a document."""
    
    def __init__(self, op_type: str, position: int, content: str = "", length: int = 0):
        self.type = op_type  # 'insert', 'delete', 'replace'
        self.position = position
        self.content = content
        self.length = length or len(content)
        self.timestamp = datetime.now()
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert operation to dictionary for JSON serialization."""
        return {
            'type': self.type,
            'position': self.position,
            'content': self.content,
            'length': self.length,
            'timestamp': self.timestamp.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Operation':
        """Create operation from dictionary."""
        return cls(
            op_type=data['type'],
            position=data['position'],
            content=data.get('content', ''),
            length=data.get('length', 0)
        )
    
    def __repr__(self):
        if self.type == 'insert':
            return f"Insert('{self.content}' at {self.position})"
        elif self.type == 'delete':
            return f"Delete({self.length} chars at {self.position})"
        elif self.type == 'replace':
            return f"Replace({self.length} chars at {self.position} with '{self.content}')"
        return f"Operation({self.type}, {self.position})"


class OperationalTransform:

...
```


### `./apps/writer_app/repository_integration.py`

```python
"""
Repository integration for Writer manuscripts.
Integrates manuscript submissions with research data repositories for 
data sharing, supplementary materials, and reproducible research.
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
from django.utils import timezone
from django.core.files.base import ContentFile
from django.db import transaction

from .models import Manuscript, Citation, ArxivSubmission
from apps.scholar_app.models import (
    Dataset, DatasetFile, RepositoryConnection, SearchIndex
)
from apps.scholar_app.repository_services import (
    RepositoryServiceFactory, upload_dataset_to_repository
)

logger = logging.getLogger(__name__)


class ManuscriptRepositoryIntegrator:
    """Service for integrating manuscripts with research data repositories"""
    
    def __init__(self, manuscript: Manuscript, repository_connection: Optional[RepositoryConnection] = None):
        self.manuscript = manuscript
        self.repository_connection = repository_connection or self._get_default_connection()
        
    def _get_default_connection(self) -> Optional[RepositoryConnection]:
        """Get user's default repository connection"""
        return RepositoryConnection.objects.filter(
            user=self.manuscript.owner,
            is_default=True,
            status='active'
        ).first()
    
    def create_supplementary_dataset(self, title: str = None, 
                                   description: str = None,
                                   auto_upload: bool = True) -> Optional[Dataset]:
        """Create a supplementary dataset for the manuscript"""
        
        if not self.repository_connection:
            logger.warning(f"No repository connection available for user {self.manuscript.owner.username}")
            return None
        
        try:

...
```


### `./apps/writer_app/routing.py`

```python
"""
WebSocket URL routing for Writer app.
"""

from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/writer/manuscript/(?P<manuscript_id>\d+)/$', consumers.WriterConsumer.as_asgi()),
]

...
```


### `./apps/writer_app/simple_views.py`

```python
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required


@login_required
def index(request):
    """Writer app - redirect to user's projects."""
    from django.contrib import messages
    messages.info(request, 'Please select or create a project to use Writer.')
    return redirect('user_projects:user_projects', username=request.user.username)


def simple_editor(request):
    """Writer app - direct LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def modular_editor(request):
    """Modular text-based editor with word counts (User Requested Approach)."""
    return render(request, 'writer_app/modular_editor.html')


def simple_editor(request):
    """Simple MVP LaTeX editor interface."""
    return render(request, 'writer_app/simple_editor.html')


def features(request):
    """Writer features view."""
    return render(request, 'writer_app/features.html')


def pricing(request):
    """Writer pricing view."""
    return render(request, 'writer_app/pricing.html')


@require_http_methods(["POST"])
def mock_compile(request):
    """Mock LaTeX compilation endpoint."""
    # Mock successful compilation
    return JsonResponse({
        'status': 'success',
        'pdf_url': '/static/mock/sample.pdf',
        'log': 'LaTeX compilation completed successfully.\nOutput: 2 pages, 45.7 KB',
        'pages': 2,
        'size': '45.7 KB'
    })

...
```


### `./apps/writer_app/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import DocumentTemplate, Manuscript, CompilationJob
import json


class DocModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.template = DocumentTemplate.objects.create(
            name='Research Article',
            template_type='article',
            latex_template='\\documentclass{article}\n\\begin{document}\n{content}\n\\end{document}',
            description='Standard research article template'
        )
        
        self.manuscript = Manuscript.objects.create(
            owner=self.user,
            title='Test Manuscript',
            slug='test-manuscript',
            content='\\section{Introduction}\nThis is a test.',
            abstract='Test abstract'
        )
    
    def test_document_template_creation(self):
        """Test document template creation"""
        self.assertEqual(self.template.name, 'Research Article')
        self.assertEqual(self.template.template_type, 'article')
        self.assertIn('\\documentclass{article}', self.template.latex_template)
    
    def test_compilation_job_creation(self):
        """Test compilation job creation"""
        job = CompilationJob.objects.create(
            manuscript=self.manuscript,
            initiated_by=self.user,
            compilation_type='full',
            status='completed',
            output_path='/media/output/test.pdf',
            log_file='Compilation successful'
        )
        
        self.assertEqual(job.manuscript, self.manuscript)
        self.assertEqual(job.status, 'completed')
        self.assertIsNotNone(job.created_at)

...
```


### `./apps/writer_app/TODO.md`

```markdown
# Writer App Enhancement Plan

**Project**: SciTeX Cloud - Writer App
**Goal**: Integrate neurovista/paper functionality into Django writer_app
**Date**: 2025-10-16

## Overview

Enhance the writer_app to provide a comprehensive web-based LaTeX manuscript preparation system, integrating the modular structure and compilation workflow from `~/proj/neurovista/paper/`.

## Current Status

### ✅ Already Implemented (writer_app)
- Basic manuscript models (Manuscript, ManuscriptSection, Figure, Table, Citation)
- Project-linked manuscripts
- Modular structure creation (`create_modular_structure()`)
- Basic LaTeX compilation with job tracking
- Version control and branching
- Collaborative editing infrastructure
- arXiv submission integration

### 📦 Available in neurovista/paper (External)
- Unified compilation interface (`./compile`)
- Modular document structure (manuscript/supplementary/revision)
- Shared metadata (title, authors, keywords via symlinks)
- Container-based compilation system
- Watch mode for hot-recompiling
- Figure/table auto-conversion
- Mermaid diagram support
- Bibliography analysis tools
- Word count tracking per section

## Core Features to Implement

### 1. Separate TeX File Editing ⭐ HIGH PRIORITY

**Goal**: Allow users to edit individual LaTeX section files through web interface

**Implementation**:
```
Structure:
project/paper/
├── 01_manuscript/
│   └── contents/
│       ├── abstract.tex
│       ├── introduction.tex
│       ├── methods.tex
│       ├── results.tex
│       ├── discussion.tex
│       └── figures/
```

...
```


### `./apps/writer_app/urls.py`

```python
from django.urls import path
from . import views, simple_views, arxiv_views, default_workspace_views

app_name = 'writer'

urlpatterns = [
    # Default workspace for logged-in users without project
    path('workspace/', default_workspace_views.user_default_workspace, name='user_default_workspace'),

    # Project-linked Writer (Primary Interface)
    path('project/<int:project_id>/', views.project_writer, name='project-writer'),
    path('project/<int:project_id>/save-section/', views.save_section, name='save-section'),
    path('project/<int:project_id>/load-latex/', views.load_latex_section, name='load-latex'),
    path('project/<int:project_id>/save-latex/', views.save_latex_section, name='save-latex'),
    path('project/<int:project_id>/compile/', views.compile_modular_manuscript, name='compile-modular'),
    path('project/<int:project_id>/stats/', views.get_manuscript_stats, name='manuscript-stats'),
    path('project/<int:project_id>/toggle-mode/', views.toggle_editing_mode, name='toggle-mode'),
    path('project/<int:project_id>/cloud-compile/', views.cloud_compile_sections, name='cloud-compile-sections'),
    path('project/<int:project_id>/download-paper/', views.download_paper_zip, name='download-paper-zip'),
    path('project/<int:project_id>/pdf/', views.download_compiled_pdf, name='compiled-pdf'),
    
    # Modular Editor Interface (Standalone)
    path('', simple_views.index, name='index'),  # Main writer page with hero section at /writer/
    path('collaborative/<int:manuscript_id>/', views.collaborative_editor, name='collaborative-editor'),  # Collaborative editor
    path('features/', simple_views.features, name='features'),
    path('pricing/', simple_views.pricing, name='pricing'),
    
    # Editor interfaces
    path('modular/', simple_views.modular_editor, name='modular-editor'),  # Modular editor
    path('simple/', simple_views.simple_editor, name='simple-editor'),  # Raw LaTeX editor
    path('advanced/', views.mvp_editor, name='advanced-editor'),  # Overleaf-style editor
    
    # API endpoints - Real compilation
    path('api/compile/', views.quick_compile, name='real-compile'),
    path('api/status/<uuid:job_id>/', views.compilation_status, name='compilation-status'),
    # path('api/test-compilation/', views.test_compilation, name='test-compilation'),  # Temporarily disabled
    path('api/save/', simple_views.mock_save, name='mock-save'),
    
    # Collaborative editing API endpoints
    path('api/collaborate/manuscript/<int:manuscript_id>/sessions/', views.collaborative_sessions, name='collaborative-sessions'),
    path('api/collaborate/manuscript/<int:manuscript_id>/join/', views.join_collaboration, name='join-collaboration'),
    path('api/collaborate/manuscript/<int:manuscript_id>/leave/', views.leave_collaboration, name='leave-collaboration'),
    path('api/collaborate/section/<int:section_id>/lock/', views.lock_section, name='lock-section'),
    path('api/collaborate/section/<int:section_id>/unlock/', views.unlock_section, name='unlock-section'),
    
    # Version control API endpoints
    path('api/version/<int:manuscript_id>/history/', views.version_history, name='version-history'),
    path('api/version/<int:manuscript_id>/create/', views.create_version, name='create-version'),
    path('api/version/<int:manuscript_id>/diff/<uuid:from_version_id>/<uuid:to_version_id>/', views.view_diff, name='view-diff'),
    path('api/version/<int:manuscript_id>/rollback/<uuid:version_id>/', views.rollback_version, name='rollback-version'),

...
```


### `./apps/writer_app/utils.py`

```python
#!/usr/bin/env python3
"""
LaTeX compilation utilities for SciTeX-Cloud Writer module.
"""

import os
import subprocess
import tempfile
import shutil
import time
from pathlib import Path
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile


def compile_latex_document(compilation_job):
    """
    Compile a LaTeX document to PDF.
    
    Args:
        compilation_job: CompilationJob instance
    """
    from .models import CompilationJob
    
    # Update job status
    compilation_job.status = 'running'
    compilation_job.started_at = timezone.now()
    compilation_job.save()
    
    start_time = time.time()
    
    try:
        # Generate LaTeX content
        manuscript = compilation_job.manuscript
        
        # Check if manuscript has generate_latex method, otherwise use simple template
        if hasattr(manuscript, 'generate_latex') and callable(getattr(manuscript, 'generate_latex')):
            latex_content = manuscript.generate_latex()
        else:
            # Fallback to simple LaTeX template
            latex_content = generate_simple_latex_template(manuscript)
        
        # Create temporary directory for compilation
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Write LaTeX file
            tex_file = temp_path / "manuscript.tex"
            with open(tex_file, 'w', encoding='utf-8') as f:

...
```


### `./apps/writer_app/version_control.py`

```python
"""
Version Control System for SciTeX Writer
Advanced diff generation, branching, and merge capabilities for manuscript management.
"""
import difflib
import re
import json
from datetime import datetime, timedelta
from typing import Dict, List, Tuple, Any, Optional
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    Manuscript, ManuscriptVersion, ManuscriptBranch, 
    DiffResult, MergeRequest, ManuscriptSection
)


class DiffEngine:
    """Advanced diff generation for manuscript content."""
    
    def __init__(self):
        self.word_pattern = re.compile(r'\b\w+\b|[^\w\s]')
        self.sentence_pattern = re.compile(r'[.!?]+')
        
    def generate_unified_diff(self, text1: str, text2: str, 
                           context_lines: int = 3) -> Dict[str, Any]:
        """Generate unified diff between two text versions."""
        lines1 = text1.splitlines(keepends=True)
        lines2 = text2.splitlines(keepends=True)
        
        diff = list(difflib.unified_diff(
            lines1, lines2,
            fromfile='Version A',
            tofile='Version B',
            n=context_lines
        ))
        
        # Parse diff into structured format
        changes = []
        current_hunk = None
        
        for line in diff:
            if line.startswith('@@'):
                if current_hunk:
                    changes.append(current_hunk)
                current_hunk = {
                    'header': line.strip(),
                    'lines': []
                }
            elif current_hunk and (line.startswith(' ') or line.startswith('+') or line.startswith('-')):

...
```


### `./CLAUDE.md`

```markdown

See `./docs/SciTeX-Ecosystem-and-Corresponding-Local-Directories.md` as well

## Research proposal for this project, SciTeX
See `./docs/BOOST_応募済み申請書_26151429_oubo_20250626.pdf`
However, we are also thinking monetization strategies. `./docs/MONETIZATION_STRATEGY_IMPLEMENTATION.md`

## External pip packages / shell scripts

Core functionalities should be handled under `./externals` as independent, **static** modules:
./externals/SciTeX-Scholar/
./externals/SciTeX-Code/
./externals/SciTeX-Viz/
./externals/SciTeX-Writer/

**Static** means that these modules does not always have AI integration by themselves. However, by incorporating with AI agents, like cloud code, they will have significant impacts while reducing degree of freedom for expected behaviours. (e.g., agents to use SciTeX-Writer for manuscript preparation)

In this SciTeX-Cloud, we focus on providing web interface for web-based users. So, factor out existing logic to the modules as externals are highly recommended while keeping Django code as a platform.

## Project-centric application
The SciTeX ecosystem is project-centric; scholar, code, viz, writer should be linked to a project of the user or a group. However, basic functionalities should be offered to anonymous users or users with no projects associated.

## API Keys
API keys should be handled with user models through dashboard or user settings.

## No fake data
When error raised, show them as alert on the website. Fake operations will raise critical issues.

## Django Directory Structure
Use `./apps/XXX_app/` format

Do not place any files under project root directory
Instead, place under `./docs`, `./apps`, `./project_management`, `./tests`, `./tmp`, `./data`

## Directory Structure
- `./docs` - Documentation and guidelines
- `./apps` - Django applications
- `./project_management` - Deployment and server management scripts
- `./tests` - Test files
- `./tmp` - Temporary files (logs, cache, etc.)
- `./data` - Persistent data (databases, user data)

## Design Theme of the website
See /design/


...
```


### `./config/asgi.py`

```python
"""
ASGI config for SciTeX Cloud project.

It exposes the ASGI callable as a module-level variable named ``application``.
"""

import os
import django
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

# Import routing after Django setup
from apps.writer_app import routing as writer_routing

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                writer_routing.websocket_urlpatterns
            )
        )
    ),
})
...
```


### `./config/__init__.py`

```python
"""
SciTeX Web - Configuration Module

This module handles loading, processing, and applying configuration
for the SciTeX Web application.
"""

import os
import json
import logging

logger = logging.getLogger(__name__)

# Default configuration
DEFAULT_CONFIG = {
    'server': {
        'port': 3000,
        'host': 'localhost',
        'environment': 'development'
    },
    'api': {
        'baseUrl': '/api',
        'version': 'v1',
        'timeout': 30000
    },
    'auth': {
        'tokenExpiration': 86400,  # 24 hours in seconds
        'refreshTokenExpiration': 604800  # 7 days in seconds
    },
    'features': {
        'enableRealTimeCollaboration': True,
        'enableAI': True,
        'enableVersioning': True
    },
    'storage': {
        'documentPath': './documents',
        'maxUploadSize': 10485760  # 10MB in bytes
    }
}

def loadConfigFiles(config_paths=None):
    """
    Load configuration from JSON files.
    
    Args:
        config_paths (list): List of configuration file paths to load.
            Defaults to ['./config.json', './config.local.json']
            
    Returns:
        dict: Merged configuration from files and defaults

...
```


### `./config/logger.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 05:15:38 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/config/logger.py
# ----------------------------------------
"""
Logger utilities for SciTeX Cloud project.
Simplifies using the application-specific logger.

This module provides a convenient interface for working with Python's logging
module in the context of the SciTeX Cloud project. It includes functions for
getting properly configured loggers, as well as decorators for common logging
patterns like function calls, exceptions, and API requests.
"""

import logging
from functools import wraps
import traceback
import time

# Get logger for our application
logger = logging.getLogger('scitex')

def get_logger(module_name):
    """
    Get a logger for a specific module.
    
    Args:
        module_name (str): Name of the module (typically __name__)
        
    Returns:
        logging.Logger: Logger instance with the module name prefixed with 'scitex.'
    """
    return logging.getLogger(f'scitex.{module_name}')

def log_exception(func):
    """
    Decorator to log exceptions occurring in a function.
    """
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(
                f"Exception in {func.__name__}: {str(e)}",
                exc_info=True,
                extra={
                    'traceback': traceback.format_exc()
                }

...
```


### `./config/README.md`

```markdown
# SciTeX Cloud Configuration

This directory contains all Django configuration files organized for easy environment management.

## Directory Structure

```
config/
├── settings/              # Django settings (organized by environment)
│   ├── __init__.py       # Auto-detects environment
│   ├── base.py           # Shared settings for all environments
│   ├── development.py    # Development-specific settings
│   └── production.py     # Production-specific settings
├── deployment/            # Deployment configurations
│   ├── uwsgi/            # uWSGI configs
│   │   ├── uwsgi.ini
│   │   ├── uwsgi_prod.ini
│   │   └── uwsgi_simple.ini
│   └── nginx/            # Nginx configs
│       └── *.conf
├── asgi.py               # ASGI application
├── wsgi.py               # WSGI application
├── urls.py               # URL configuration
├── routing.py            # WebSocket routing
└── logger.py             # Logging configuration
```

## Environment Switching

### Method 1: Environment Variable (Recommended)

```bash
# Development (default)
export SCITEX_CLOUD_ENV=development
python manage.py runserver

# Production
export SCITEX_CLOUD_ENV=production
gunicorn config.wsgi:application
```

### Method 2: Django Settings Module

```bash
# Development
export DJANGO_SETTINGS_MODULE=config.settings.development

# Production
export DJANGO_SETTINGS_MODULE=config.settings.production
```

...
```


### `./config/routing.py`

```python
"""
WebSocket routing configuration for SciTeX Cloud.
"""
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django.core.asgi import get_asgi_application

import apps.writer_app.routing

application = ProtocolTypeRouter({
    # HTTP protocol
    "http": get_asgi_application(),
    
    # WebSocket protocol 
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter([
                *apps.writer_app.routing.websocket_urlpatterns,
            ])
        )
    ),
})
...
```


### `./config/settings/__init__.py`

```python
"""
Django settings auto-loader for SciTeX Cloud.

This module automatically loads the appropriate settings based on:
1. DJANGO_SETTINGS_MODULE environment variable
2. SCITEX_CLOUD_ENV environment variable
3. Default to development if not specified

Usage:
    Development: export SCITEX_CLOUD_ENV=development (or leave unset)
    Production:  export SCITEX_CLOUD_ENV=production
"""

import os
import sys

# Determine which settings to use
env = os.environ.get('SCITEX_CLOUD_ENV', 'development').lower()

if env == 'production':
    from .settings_prod import *
elif env == 'development':
    from .settings_dev import *
else:
    # Fallback to development
    print(f"Warning: Unknown SCITEX_CLOUD_ENV '{env}', defaulting to development")
    from .settings_dev import *

# Display which settings are loaded (only in development)
if DEBUG:
    print(f" SciTeX Cloud settings loaded: {env.upper()}")

...
```


### `./config/settings/settings_dev.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-21 10:05:45 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/config/settings/development.py
# ----------------------------------------
import os
__FILE__ = (
    "./config/settings/development.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
"""
Development settings for SciTeX Cloud project.
"""

from .settings_shared import *
# LOGGING is now imported from settings_shared.py

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

# Development SECRET_KEY fallback (override from base.py)
if not SECRET_KEY:
    SECRET_KEY = "django-insecure-dev-key-for-testing-only-do-not-use-in-production"

ALLOWED_HOSTS = ["localhost", "127.0.0.1", "0.0.0.0", "172.19.33.56", "[::1]", "testserver"]

# Development-specific apps
DEVELOPMENT_APPS = [
    "django_browser_reload",
    "django_extensions",
]

INSTALLED_APPS += DEVELOPMENT_APPS

# Development middleware
MIDDLEWARE += [
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

# Hot reload settings
INTERNAL_IPS = [
    "127.0.0.1",
]

# Development database (SQLite)
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "scitex_cloud_dev.db",

...
```


### `./config/settings/settings_prod.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 00:35:58 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_prod.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_prod.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from .settings_shared import *  # Import shared settings

# Load environment variables from .env.production if it exists
try:
    from dotenv import load_dotenv

    load_dotenv(os.path.join(BASE_DIR, ".env.production"))
except ImportError:
    pass  # python-dotenv not installed, rely on system environment

"""
Production settings for SciTeX Cloud project.
"""

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# Security - Use environment variable for production
SECRET_KEY = os.environ.get("SCITEX_DJANGO_SECRET_KEY")
if not SECRET_KEY:
    # Fallback secret key for development/testing purposes
    SECRET_KEY = "WlLHhph63BKuRP7W?Z3TszWTltaObIzC-fallback-production-key-change-in-real-deployment"

ALLOWED_HOSTS = [
    "scitex.ai",
    "www.scitex.ai",
    "sciwriter.app",
    "www.sciwriter.app",
    "162.43.35.139",
    "localhost",
    "scitex",
    "airight.app",
]

# Security settings for production - only enable SSL redirects if HTTPS is properly configured
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True

...
```


### `./config/settings/settings_shared.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 00:36:36 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/settings/settings_shared.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/settings/settings_shared.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
Django settings for SciTeX Cloud project.
Base settings shared across all environments.
"""

from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.getenv("SCITEX_DJANGO_SECRET_KEY")

# Application definition
DJANGO_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

THIRD_PARTY_APPS = [
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "channels",
]

# Automatically discover and register all Django apps in ./apps/
def discover_local_apps():
    """Discover all Django apps in the apps directory."""
    apps_path = BASE_DIR / 'apps'
    local_apps = []

    if apps_path.exists():

...
```


### `./config/urls.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-10-16 02:05:02 (ywatanabe)"
# File: /home/ywatanabe/proj/scitex-cloud/config/urls.py
# ----------------------------------------
from __future__ import annotations
import os
__FILE__ = (
    "./config/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

"""
URL Configuration for SciTeX Cloud project.
"""

import hashlib
import json
import time

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.urls import include, path
from django.views.generic import RedirectView


# API Auth functions
def api_register(request):
    """
    API endpoint for user registration.

    Expects:
        username: Desired username
        email: User's email
        password: Desired password
        first_name: (optional) User's first name
        last_name: (optional) User's last name

    Returns:
        JSON response with registration status and user information if successful
    """
    data = json.loads(request.body)

    # Required fields
    username = data.get("username", "")

...
```


### `./config/wsgi.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WSGI config for SciTeX Cloud project.

It exposes the WSGI callable as a module-level variable named ``application``.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

application = get_wsgi_application()

...
```


### `./docs/APP_REORGANIZATION_SUMMARY.md`

```markdown
# SciTeX Cloud App Reorganization Summary

**Date:** 2025-10-16
**Status:** Completed

## Changes Made

### 1. App Cleanup
Removed unnecessary apps to streamline the codebase:
- Removed: engine_app, api, monitoring_app, orcid_app, reference_sync_app, mendeley_app, github_app, collaboration_app, ai_assistant_app, onboarding_app, integrations, document_app

### 2. Current Active Apps

The system now has **11 focused apps**:

1. **auth_app** - Authentication and user management
2. **billing_app** - Pricing, subscriptions, donations
3. **cloud_app** - Landing pages, main website
4. **code_app** - Code execution and analysis
5. **core_app** - Core functionality, projects, user profiles
6. **dev_app** - Development tools (design system)
7. **project_app** - Project management
8. **scholar_app** - Literature discovery
9. **viz_app** - Visualization tools
10. **writer_app** - Scientific writing
11. **__pycache__** - Python cache (not an app)

### 3. Automatic App Discovery

Implemented programmatic app registration in `config/settings/settings_shared.py`:

```python
def discover_local_apps():
    """Discover all Django apps in the apps directory."""
    apps_path = BASE_DIR / 'apps'
    local_apps = []

    if apps_path.exists():
        for item in sorted(apps_path.iterdir()):
            if item.is_dir() and not item.name.startswith('_'):
                if (item / 'apps.py').exists() or (item / '__init__.py').exists():
                    app_name = f"apps.{item.name}"
                    local_apps.append(app_name)

    return local_apps

LOCAL_APPS = discover_local_apps()
```

Benefits:

...
```


### `./docs/BROWSER_REFRESH_NEEDED.md`

```markdown
# Browser Refresh Required

## Current Issue

The browser is showing **cached content** from the old template. The new GitHub-style profile page has been implemented but requires a hard refresh to display.

## How to See the New Layout

### Option 1: Hard Refresh (Recommended)
**Windows/Linux:**
- Press `Ctrl + F5`
- Or press `Ctrl + Shift + R`

**Mac:**
- Press `Cmd + Shift + R`
- Or press `Cmd + Option + R`

### Option 2: Clear Cache
**Chrome:**
1. Press `F12` to open DevTools
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

### Option 3: Incognito/Private Mode
Open the URL in an incognito/private window:
- Chrome: `Ctrl + Shift + N` (Windows) or `Cmd + Shift + N` (Mac)
- Navigate to `http://127.0.0.1:8000/ywatanabe1989/`

## What You Should See

After refreshing, you should see:

### ✅ New GitHub-Style Layout
- **Dark theme** (#0d1117 background)
- **Two-column layout** (296px sidebar + content area)
- **Left sidebar** with:
  - Large circular avatar
  - Full name and username
  - Bio, location, institution
  - Repository count
- **Right content** with:
  - Navigation tabs (Overview, Repositories, Projects, Stars)
  - Repository search bar
  - Clean repository list
  - Language badges and metadata

### ❌ Old Layout (Cached)
If you still see:
- Light colored sections
- Centered header with gradient

...
```


### `./docs/DARK_MODE_IMPLEMENTATION.md`

```markdown
# Dark Mode Implementation - Complete

## Summary

Successfully implemented a comprehensive Light/Dark/System theme system for SciTeX Cloud, matching GitHub's approach with three-way theme switching.

## Features Implemented

### 1. Three Theme Modes ✅

**Light Mode (☀️)**
- Always use light theme
- GitHub Light color palette
- White backgrounds, dark text
- Manual override of system preference

**Dark Mode (🌙)**
- Always use dark theme
- GitHub Dark color palette (#0d1117 background)
- Reduced eye strain for long sessions
- Manual override of system preference

**System Mode (💻)** - Default
- Auto-sync with operating system theme
- Respects user's system-wide preference
- Automatically switches when system theme changes
- Best user experience for most people

### 2. Theme Toggle Button ✅

**Location**: Top-right header (always visible to all users)

**Features:**
- Click to cycle: Light → Dark → System → Light
- Visual indicator: ☀️ / 🌙 / 💻
- Tooltip shows current mode
- Instant switching (no page reload)
- Works on all pages

### 3. Appearance Settings Page ✅

**URL**: `/core/settings/appearance/`

**Features:**
- Three visual cards for each theme mode
- Active theme indicator
- Live preview of theme
- One-click theme switching
- Accessible from:
  - Header dropdown → Appearance

...
```


### `./docs/DATABASE_REFRESH_SUMMARY.md`

```markdown
# Database Refresh Summary

**Date:** 2025-10-16
**Status:** Completed

## Overview

Fresh database created with clean migrations after app cleanup and reorganization.

## Actions Taken

### 1. Database Location Update
- **Old location:** `./scitex_cloud_dev.db` (project root - violates CLAUDE.md guidelines)
- **New location:** `./data/scitex_cloud.db` (proper organization)
- **Configuration:** Updated in `config/settings/settings_shared.py:100`

### 2. Migration Cleanup

Removed all old migrations referencing deleted apps:
- Archived to: `data/migrations_archive_20251016_011323/`
- Backed up to: `data/migrations_backup/`
- Removed problematic migrations referencing `document_app`, `api`, etc.

### 3. Fresh Migrations Created

New migration files created for all active apps:
- `auth_app.0001_initial` - UserProfile, EmailVerification
- `cloud_app.0001_initial` - DonationTier, SubscriptionPlan, APIKey, etc.
- `code_app.0001_initial` - CodeExecutionJob, DataAnalysisJob, Notebook, etc.
- `core_app.0001_initial` - Organization, Project, ResearchGroup, UserProfile, etc.
- `project_app.0001_initial` - Organization, Project, ProjectMembership, etc.
- `scholar_app.0001_initial` - Annotation, Author, Citation, Dataset, etc.
- `viz_app.0001_initial` - Visualization, Dashboard, ColorScheme, etc.
- `writer_app.0001_initial` - Manuscript, ArxivSubmission, DocumentTemplate, etc.

### 4. Database Statistics

**Current database:** `data/scitex_cloud.db` (2.3 MB)

Applied migrations: ~40 migrations across all apps

## Configuration Status

- Database location: `./data/scitex_cloud.db` ✓
- Migrations applied: All ✓
- Configuration valid: Yes (1 minor warning about cloud_app namespace)
- Ready for use: Yes ✓

## Benefits


...
```


### `./docs/DOCUMENTATION_HOSTING_GUIDE.md`

```markdown
# Documentation Hosting Guide

## Overview

SciTeX Cloud now includes integrated Read the Docs-style documentation hosting for all SciTeX modules (Scholar, Code, Viz, Writer).

## Architecture

### Components

- **docs_app**: Django application for serving documentation
  - Location: `apps/docs_app/`
  - URLs: `/docs/`, `/docs/scholar/`, `/docs/code/`, `/docs/viz/`, `/docs/writer/`

### Features

1. **Module Documentation Pages**: Each SciTeX module has its own documentation section
2. **Sphinx Integration**: Serves pre-built Sphinx HTML documentation
3. **Landing Page**: Central hub showing all available documentation modules
4. **Consistent UX**: Uses SciTeX Cloud navigation and styling
5. **Management Command**: Build documentation with `python manage.py build_docs`

## Building Documentation

### Prerequisites

```bash
# Install Sphinx and required extensions
pip install sphinx sphinx-rtd-theme sphinx-autosummary-accessors

# Install SciTeX packages (required for API documentation)
pip install -e externals/SciTeX-Code
pip install -e externals/SciTeX-Scholar
pip install -e externals/SciTeX-Viz
pip install -e externals/SciTeX-Writer
```

### Build Commands

```bash
# Build all documentation
python manage.py build_docs --module=all

# Build specific module
python manage.py build_docs --module=code
python manage.py build_docs --module=scholar
python manage.py build_docs --module=viz
python manage.py build_docs --module=writer

# Clean build (removes old builds first)
```

...
```


### `./docs/GITHUB_LAYOUT_COMPLETE.md`

```markdown
# GitHub-Style Layout Implementation - Complete

## Mission Accomplished

Successfully transformed SciTeX Cloud to use GitHub-style layout while maintaining SciTeX brand identity.

## Critical Fixes Made

### 1. TemplateSyntaxError Fix (CRITICAL)
**Problem**: Django template syntax error preventing page load
```
Could not parse: 'user.username if user.is_authenticated else 'explore''
```

**Solution**: Fixed in `templates/partials/global_header.html`
- Changed from Python ternary operator to Django template tags
- Used `{% if user.is_authenticated %}...{% else %}...{% endif %}`

### 2. Database Migration (CRITICAL)
**Problem**: `OperationalError: no such column: core_app_userprofile.avatar`

**Solution**:
```bash
python manage.py makemigrations core_app
python manage.py migrate core_app
```

Created migration `0002_userprofile_avatar_userprofile_location.py` adding:
- `avatar` field (ImageField)
- `location` field (CharField)

### 3. Authentication Fix
**File**: `apps/project_app/views.py:19`
- Removed `@login_required` decorator from `user_profile` view
- Profiles are now public like GitHub

## Single Source of Truth: Theme System

### Central Color Definition
**File**: `/home/ywatanabe/proj/scitex-cloud/static/css/theme.css`

This is the **ONLY** place where colors should be defined. All other CSS files use CSS variables from this file.

**SciTeX Brand Colors (Bluish Dark Gray):**
```css
--scitex-color-01: #1a2332;  /* Dark Bluish Gray (Primary) */
--scitex-color-01-light: #2d3748;
--scitex-color-01-dark: #0f1419;
--scitex-color-02: #34495e;  /* Medium Bluish Gray */
--scitex-color-03: #506b7a;  /* Light Bluish Gray */
```

...
```


### `./docs/GITHUB_STYLE_COMPLETE.md`

```markdown
# GitHub-Style Transformation - Complete Implementation

## Overview

Successfully transformed SciTeX Cloud to match GitHub's professional design and user experience, including a comprehensive dark mode system with Light/Dark/System preferences.

## Completed Features

### 1. GitHub-Style Global Header ✅

**File**: `templates/partials/global_header.html`

**Features:**
- **Three-section layout**: Logo + Nav | Search | Actions + User
- **Sticky positioning**: Stays at top on scroll
- **Dark theme**: #161b22 background, #21262d border
- **Responsive design**: Adapts to mobile, tablet, desktop

**Components:**
- SciTeX logo with flask icon
- Primary navigation: Repositories, Scholar, Code, Viz, Writer
- Global search bar with icon
- **Theme toggle button** (💻/☀️/🌙)
- "New" repository button (green)
- Notifications icon
- User avatar dropdown menu

**User Dropdown Menu:**
- Your profile
- Your repositories
- New repository
- Settings
- Appearance
- Dashboard
- GitHub link
- Donate
- Sign out

### 2. Public Profile Pages ✅

**File**: `apps/project_app/views.py:19`

**Changes:**
- Removed `@login_required` decorator
- Profiles are now **public** like GitHub
- Anyone can view `/{username}/` without logging in

### 3. Profile Page Layout ✅

**File**: `apps/project_app/templates/project_app/user_project_list.html`

...
```


### `./docs/GITHUB_STYLE_IMPROVEMENTS.md`

```markdown
# GitHub-Style Profile Page Improvements

## Summary

Successfully updated the SciTeX Cloud profile pages to closely match GitHub's design and layout.

## Changes Made

### 1. Authentication Fix
**File**: `apps/project_app/views.py:19`

- **Removed** `@login_required` decorator from `user_profile` view
- Profile pages are now **public** like GitHub (no login required to view)
- Users can view any user's profile at `/{username}/`

### 2. User Profile Model Enhancements
**File**: `apps/core_app/models.py:54-60`

Added new fields to `UserProfile` model:
- `avatar` - ImageField for profile pictures (uploaded to `avatars/`)
- `location` - CharField for user location (e.g., "Tokyo, Japan")
- `bio` - Already existed, for user bio/description

### 3. GitHub-Style Base Template
**File**: `templates/github_base.html` (NEW)

Created dedicated base template with:
- Dark theme (#0d1117 background, #c9d1d9 text)
- GitHub-style header with SciTeX branding
- Minimal, clean navigation
- No footer interference
- Bootstrap 5 and Font Awesome integration

### 4. Profile Page Layout
**File**: `apps/project_app/templates/project_app/user_project_list.html`

Complete redesign with GitHub's layout:

#### Layout Structure
- **Two-column grid**: 296px left sidebar + flexible right content
- **Responsive**: Collapses to single column on mobile

#### Left Sidebar Features
- Large circular avatar (296x296px)
- User's full name and username
- Bio section
- Metadata:
  - Institution with university icon
  - Location with map marker icon
  - Email with envelope icon

...
```


### `./docs/GUEST_PROJECT_NAVIGATION.md`

```markdown
# Guest Project & Navigation Flow

**Created**: 2025-10-16
**Purpose**: Allow anonymous users to try SciTeX features without signup

## Navigation Logic

### Header Module Links Routing

The header Scholar/Code/Viz/Writer buttons route users based on their authentication status:

```
┌─────────────────┬──────────────────────┬────────────────────────────────┐
│ User Status     │ Context              │ Link Destination               │
├─────────────────┼──────────────────────┼────────────────────────────────┤
│ In Project      │ /<user>/<project>/*  │ /<user>/<project>/writer/      │
│ Logged In       │ Not in project       │ /writer/ (landing page)        │
│ Anonymous       │ Anywhere             │ /guest/demo-project/writer/    │
└─────────────────┴──────────────────────┴────────────────────────────────┘
```

### Implementation

**Context Processor** (`apps/core_app/context_processors.py`):
```python
def project_context(request):
    """
    Provides:
    - 'project': Current project if URL matches /<username>/<project>/
    - 'guest_project_url': Always provides '/guest/demo-project'
    """
```

**Header Template** (`templates/partials/global_header.html`):
```html
{% if project %}
  <a href="/{{ project.owner.username }}/{{ project.slug }}/writer/">Writer</a>

{% elif user.is_authenticated %}
  <a href="/writer/">Writer</a>

{% else %}
  <a href="{{ guest_project_url }}/writer/">Writer</a>
{% endif %}
```

## Guest Project Details

**URL**: `/guest/demo-project/`


...
```


### `./docs/IMPLEMENTATION_SUMMARY_WRITER_INTEGRATION.md`

```markdown
# Writer Integration & URL Reorganization - Implementation Summary

**Date**: 2025-10-16
**Status**: ✅ Complete

## What Was Accomplished

### 1. Writer App Integration Planning
- ✅ Created comprehensive plan at `apps/writer_app/TODO.md`
- ✅ Analyzed neurovista/paper structure and features
- ✅ Created SciTeX Writer template at `docs/scitex_writer_template.tar.gz` (15 MB)
- ✅ Documented template usage at `docs/SCITEX_WRITER_TEMPLATE_USAGE.md`

### 2. Complete URL Reorganization (GitHub-Style)

**New URL Structure**:
```
/<username>/                        → User profile
/<username>/projects/               → Projects list
/<username>/<project>/              → Project dashboard
/<username>/<project>/<module>/     → Module workspace
```

**Examples**:
```
/ywatanabe1989/                     → Profile
/ywatanabe1989/projects/            → Your projects
/ywatanabe1989/neurovista/          → Project dashboard
/ywatanabe1989/neurovista/writer/   → Writer workspace
/ywatanabe1989/neurovista/scholar/  → Scholar workspace
```

### 3. Simplified Access Control

**All features require login** (`@login_required`)

**Created Decorators**:
- `@project_required` - Ensures user has at least one project
- `@project_access_required` - Validates project access, provides `request.project`

**Location**: `apps/project_app/decorators.py`

### 4. Context-Aware Navigation

**Smart Header Links**:
- **In project context** → Links to `/<username>/<project>/<module>/`
- **Not in project** → Links to `/<username>/` (select/create project)
- **Anonymous users** → Links to login page

**Implementation**:

...
```


### `./docs/installation.md`

```markdown

./externals/install_externals.sh
python -m venv .env
source .env/bin/activate
pip install -m pip -U
pip install -r ./docs/requirements.txt


...
```


### `./docs/INTEGRATIONS_ACTIVATION_CHECKLIST.md`

```markdown
# SciTeX Integrations - Activation Checklist

## ✅ Already Completed

Your SciTeX system already has automatic discovery enabled:

1. **App Discovery** ✅
   - `config/settings/settings_shared.py:45` has `discover_local_apps()`
   - `integrations_app` is automatically detected and added to `INSTALLED_APPS`
   - No manual configuration needed!

2. **URL Discovery** ✅
   - `config/urls.py:273` has `discover_app_urls()`
   - `integrations_app/urls.py` is automatically registered at `/integrations/`
   - No manual URL configuration needed!

3. **Settings Configuration** ✅
   - ORCID OAuth settings added to `config/settings/settings_shared.py:324`
   - Uses environment variables for credentials
   - Defaults are safe for development

## 🚀 Quick Start (5 minutes)

### Step 1: Install Dependencies

```bash
pip install requests cryptography
```

Or if you have a requirements file:

```bash
# Add to requirements.txt:
requests>=2.31.0
cryptography>=41.0.0
```

### Step 2: Run Migrations

```bash
python manage.py makemigrations integrations_app
python manage.py migrate
```

### Step 3: Set Environment Variables (Optional)

For ORCID integration, create a `.env` file or export:

```bash
# Development (using ORCID sandbox)
```

...
```


### `./docs/INTEGRATIONS_DEPLOYED.md`

```markdown
# SciTeX Integrations - Deployment Complete ✅

## Summary

Successfully deployed three easy-win integrations for SciTeX Cloud:
1. **ORCID OAuth** - Researcher identity integration
2. **BibTeX Export** - Bibliography file generation
3. **Slack Webhooks** - Team notifications

## Deployment Status

### ✅ Completed Actions

1. **Requirements Updated** - `docs/requirements.txt`
   - Added `requests>=2.31.0` for HTTP API calls
   - `cryptography==42.0.5` already present (for token encryption)

2. **Migrations Created & Applied**
   - Created: `apps/integrations_app/migrations/0001_initial.py`
   - Applied: ✅ All 4 models created in database
     - IntegrationConnection
     - ORCIDProfile
     - SlackWebhook
     - IntegrationLog

3. **App Auto-Discovered**
   - `integrations_app` automatically added to INSTALLED_APPS
   - URLs automatically registered at `/integrations/`
   - Settings configured with ORCID environment variables

4. **Models Verified**
   - All models import successfully
   - Database schema created correctly

## Access Points

### Web Interface

```
http://localhost:8000/integrations/              # Dashboard
http://localhost:8000/integrations/orcid/connect/         # ORCID login
http://localhost:8000/integrations/slack/configure/       # Slack setup
http://localhost:8000/integrations/export/<id>/bib/       # BibTeX export
```

### Admin Interface

```
http://localhost:8000/admin/integrations_app/integrationconnection/
http://localhost:8000/admin/integrations_app/orcidprofile/
```

...
```


### `./docs/INTEGRATIONS_IMPLEMENTATION_SUMMARY.md`

```markdown
# SciTeX Integrations Implementation Summary

## Overview

Successfully implemented three easy-win integrations for the SciTeX platform:

1. **ORCID OAuth Integration** - Researcher identity and profile
2. **BibTeX Export** - Bibliography file generation
3. **Slack Webhooks** - Team notifications

## Implementation Details

### Files Created

```
apps/integrations_app/
├── __init__.py
├── apps.py
├── models.py                  # Data models for connections, profiles, webhooks
├── admin.py                   # Django admin configuration
├── views.py                   # Web views and API endpoints
├── urls.py                    # URL routing
├── migrations/
│   └── __init__.py
├── services/
│   ├── __init__.py
│   ├── orcid_service.py       # ORCID OAuth service
│   ├── bib_export_service.py  # BibTeX generation service
│   └── slack_service.py       # Slack webhook service
└── templates/integrations_app/
    ├── dashboard.html         # Main integrations page
    └── slack_configure.html   # Slack setup form

docs/
└── INTEGRATIONS_SETUP.md      # Complete setup guide
```

### Models

**IntegrationConnection**
- Stores user connections to external services
- Encrypted OAuth tokens and API keys
- Status tracking (active, inactive, error, expired)
- Service-specific metadata

**ORCIDProfile**
- Linked to ORCID integration
- Stores researcher profile data
- Affiliation and keyword information
- Auto-synced from ORCID API

...
```


### `./docs/INTEGRATIONS_SETUP.md`

```markdown
# SciTeX Integrations Setup Guide

This guide explains how to set up and configure the SciTeX integrations: ORCID, BibTeX Export, and Slack notifications.

## Installation

### 1. Add app to Django settings

Add `'apps.integrations_app'` to `INSTALLED_APPS` in your Django settings:

```python
INSTALLED_APPS = [
    ...
    'apps.integrations_app',
    ...
]
```

### 2. Install dependencies

```bash
pip install requests cryptography
```

### 3. Run migrations

```bash
python manage.py makemigrations integrations_app
python manage.py migrate
```

### 4. Include URLs

Add to your main `urls.py`:

```python
from django.urls import path, include

urlpatterns = [
    ...
    path('integrations/', include('apps.integrations_app.urls')),
    ...
]
```

## Configuration

### ORCID Integration

#### 1. Register your application with ORCID

...
```


### `./docs/monetization_plans.md`

```markdown


...
```


### `./docs/NAVIGATION_SUMMARY.md`

```markdown
# SciTeX Cloud Navigation Summary

**Updated**: 2025-10-16

## URL Structure

### Anonymous Users (Guests)
```
Click any module link → /guest-<16-random-chars>/default/<module>/

Examples:
/guest-a9Kf3xL8pQ2mN7vR/default/writer/
/guest-a9Kf3xL8pQ2mN7vR/default/scholar/
/guest-a9Kf3xL8pQ2mN7vR/default/code/
/guest-a9Kf3xL8pQ2mN7vR/default/viz/
```

### Logged-in Users (In Project Context)
```
Within project → /<username>/<project>/<module>/

Examples:
/ywatanabe1989/neurovista-analysis/writer/
/ywatanabe1989/neurovista-analysis/scholar/
/ywatanabe1989/neurovista-analysis/code/
/ywatanabe1989/neurovista-analysis/viz/
```

### Logged-in Users (No Project Context)
```
Click module link → /<module>/ (landing page)

Examples:
/writer/  → Writer marketing page
/scholar/ → Scholar marketing page
/code/    → Code marketing page
/viz/     → Viz marketing page
```

## Implementation

**Files Created/Modified**:
1. `apps/core_app/middleware.py` - Guest session ID generation
2. `apps/core_app/context_processors.py` - Project context detection
3. `templates/partials/global_header.html` - Context-aware navigation
4. `apps/project_app/views.py` - Module integration views
5. `config/settings/settings_shared.py` - Middleware registration

**Security**:
- 16-character cryptographically random IDs

...
```


### `./docs/PASSWORD_RESET_IMPLEMENTATION.md`

```markdown
# Password Reset Implementation

## Overview

Complete password reset functionality with email delivery, token validation, and secure password updates.

## Features

- ✅ Email-based password reset
- ✅ Secure token generation (Django's default_token_generator)
- ✅ 24-hour token expiration
- ✅ Real email delivery via scitex.ai mail server
- ✅ Password visibility toggle (eye button)
- ✅ Consistent UI with login page
- ✅ Security best practices (don't reveal if email exists)

## User Flow

```
1. User clicks "Forgot Password" on login page
   ↓
2. Enters email address
   ↓
3. Receives email from agent@scitex.ai
   ↓
4. Clicks reset link (valid 24 hours)
   ↓
5. Enters new password (with visibility toggle)
   ↓
6. Password reset successfully
   ↓
7. Redirected to login page
```

## Technical Implementation

### API Endpoints

**Forgot Password:**
```
POST /api/v1/auth/forgot-password/
Body: { "email": "user@example.com" }
Response: { "success": true, "message": "..." }
```

**Reset Password:**
```
POST /api/v1/auth/reset-password/
Body: {
  "uidb64": "...",
```

...
```


### `./docs/REFACTORING_PLAN_FROM_USER.md`

```markdown

no need for orcid, mendely, github, or reference_sync

  also, we no need complecated implementations yet, consider all implementations are just a blueprint

  create future directory to keep code but actually not use them

  most important parts are

1. Landing page
2. Scholar implementation (~/proj/scitex_repo/src/scitex/scholar) has been significantly upgraded
   3. Also, we are planning to create .exe local executable
3. Write implementation (~/proj/neurovista/paper; as an live example)
4. Organized project for scalability and redability (this app itself will be open sourced; but no backward compatibility needed for now)
   5. See this (/home/ywatanabe/proj/scitex-cloud/docs/REFACTORING_PLAN.md) but do not need to completely follow it as our constraint is not strict


...
```


### `./docs/REFACTORING_PLAN.md`

```markdown
# SciTeX Cloud Refactoring Plan

## Current Issues

### 1. Apps Organization (21 apps!)
- **Too many apps** - 21 Django apps is excessive
- **Empty apps** - Several skeleton apps with no functionality
- **Poor separation** - Overlapping responsibilities
- **Root clutter** - Old apps in root (violates CLAUDE.md)

### 2. Templates Organization (26 template dirs!)
- **Duplicate templates** - `/templates/` AND `/apps/*/templates/`
- **Inconsistent structure** - Some in root, some in apps
- **No partials reuse** - Repeated code across templates
- **Commented-out files** - design_system.html entirely commented

### 3. Static Files
- **Multiple sources** - `/static/`, `/staticfiles/`, `/media/static/staticfiles/`
- **App-specific CSS scattered** - Some in `/static/css/`, some in `apps/*/static/`
- **Legacy files** - Archived but not cleaned up

### 4. Configuration
- **Duplicate settings** - Had 3 settings files (now cleaned)
- **Scripts scattered** - Now organized into dev/prod (✓ DONE)

## Recommended Django Apps Structure

### Core Platform (Keep - 5 apps)

```
apps/
├── core_app/              # Dashboard, shared utilities
├── auth_app/              # Authentication, user profiles
├── project_app/           # Project management (project-centric!)
├── cloud_app/             # Landing, marketing pages
└── api/                   # API endpoints (v1, v2)
```

### SciTeX Modules (Keep - 5 apps)

```
apps/
├── scholar_app/           # Literature management
├── writer_app/            # Scientific writing
├── code_app/              # Data analysis
├── viz_app/               # Visualizations
└── engine_app/            # Emacs integration
```

### Integration Apps (Consolidate - 2 apps)

...
```


### `./docs/REORGANIZATION_COMPLETE.md`

```markdown
# SciTeX Cloud Reorganization - Complete Summary

**Date:** 2025-10-16
**Status:** ✓ Completed and Operational

## Overview

Successfully reorganized SciTeX Cloud with automatic app discovery, clean database, and streamlined architecture.

## Final App Structure

**10 Active Apps** (automatically discovered):

1. **auth_app** - `/auth/` - Authentication and user management
2. **billing_app** - `/billing/` - Pricing and subscriptions
3. **cloud_app** - `/cloud/` - Main website and landing pages
4. **code_app** - `/code/` - Code execution and data analysis
5. **core_app** - `/core/` - Core functionality and projects
6. **dev_app** - `/dev/` - **NEW** Development tools (design system at `/dev/design.html`)
7. **project_app** - `/project/` - Project management
8. **scholar_app** - `/scholar/` - Literature discovery
9. **viz_app** - `/viz/` - Data visualization
10. **writer_app** - `/writer/` - Scientific writing

## Key Features Implemented

### 1. Automatic App Discovery

**File:** `config/settings/settings_shared.py:45-60`

```python
def discover_local_apps():
    """Discover all Django apps in the apps directory."""
    apps_path = BASE_DIR / 'apps'
    local_apps = []

    if apps_path.exists():
        for item in sorted(apps_path.iterdir()):
            if item.is_dir() and not item.name.startswith('_'):
                if (item / 'apps.py').exists() or (item / '__init__.py').exists():
                    app_name = f"apps.{item.name}"
                    local_apps.append(app_name)

    return local_apps
```

**Benefits:**
- No manual app registration needed
- Just create app in `./apps/xxx_app/` and it's auto-registered
- Self-documenting - the filesystem is the source of truth

...
```


### `./docs/SCHOLAR_AUTHENTICATION_ANALYSIS.md`

```markdown
# Scholar Authentication: Deep Analysis & Honest Recommendation

## The Core Problem

**Goal:** Automate paywalled PDF downloads while respecting:
- User privacy and control
- Institutional access rights
- Legal/ethical boundaries
- Your "transparent and open" philosophy

## Options Analysis

### Option 1: Server-Side with Stored Credentials

**How it works:**
```
User enters institutional credentials in Django
  ↓
Django stores (encrypted) in database
  ↓
Server runs browser automation with user's credentials
  ↓
Downloads PDF using institutional access
```

**Pros:**
- ✅ Fully automated (user clicks once)
- ✅ Works on any device
- ✅ Can batch download
- ✅ Consistent experience

**Cons:**
- ❌ **User must trust you with passwords** - This is huge!
- ❌ Violates your "transparent" philosophy
- ❌ Security liability (encrypted doesn't mean safe)
- ❌ User has no visibility into what browser does
- ❌ If compromised, ALL user credentials exposed
- ❌ **Institutional policy violations** - Many universities prohibit password sharing

**My honest take:** This feels wrong for SciTeX. It contradicts "open, transparent, user-controlled."

### Option 2: Browser Extension (Client-Side Downloads)

**How it works:**
```
User installs SciTeX browser extension
  ↓
User is already logged into publishers (their browser)
  ↓
Extension detects PDF availability
```

...
```


### `./docs/SCHOLAR_INTEGRATION_STRATEGY.md`

```markdown
# Scholar Module Integration Strategy for Django Web App

## Current State Analysis

### Scholar Module (`~/proj/scitex_repo/src/scitex/scholar/`)
**Capabilities:**
- Multi-source search (CrossRef, PubMed, OpenAlex, Semantic Scholar, arXiv)
- PDF downloading with institutional authentication
- Metadata enrichment
- Browser automation (Selenium, ZenRows)
- OpenAthens SSO integration
- Local library management
- Export formats (BibTeX, RIS, JSON, Markdown)

**Challenges:**
- ❌ **Browser automation** - Selenium/headless Chrome for authenticated downloads
- ❌ **Authentication complexity** - OpenAthens, institutional SSO
- ❌ **Heavy dependencies** - Browser drivers, authentication systems
- ❌ **Session management** - Cookies, persistent sessions

### Django Scholar App (`apps/scholar_app/`)
**Current Implementation:**
- ✅ Database models (SearchIndex, Author, Journal, Citation)
- ✅ Search interface with PostgreSQL full-text search
- ✅ Paper recommendations and similarity
- ✅ Export functionality (CSV, BibTeX, RIS, JSON)
- ✅ Caching and optimization
- ❌ **NOT connected to actual scitex.scholar module!**

## Integration Challenges

### 1. Browser Automation (Biggest Challenge)
```python
# scitex.scholar uses browser for:
- PDF downloads from paywalled sites
- Institutional authentication
- JavaScript-rendered content
- Cookie/session management
```

**Problem:** Running headless Chrome in Django web app:
- Heavy resource usage (each user needs browser instance)
- Security risks (browser sessions)
- Scalability issues

### 2. Authentication Complexity
```python
# scitex.scholar supports:
- OpenAthens SSO
- University login portals
```

...
```


### `./docs/SCITEX_STANDALONE_PLAN.md`

```markdown
# SciTeX Standalone Application - Implementation Plan

## Vision

**One executable. Complete research workflow. Zero setup.**

```
scitex.exe (Windows) / scitex.app (macOS) / scitex.AppImage (Linux)
  ↓
Double-click
  ↓
Complete research platform running locally at http://localhost:5000
```

## The Complete SciTeX Suite

Based on your code references:

```
SCITEX_SCHOLAR   → Literature management & bulk PDF downloads
SCITEX_WRITER    → Scientific writing (LaTeX + AI)
SCITEX_CODE      → Data analysis workflows
SCITEX_VIZ       → Publication-quality graphics
SCITEX_ENGINE    → Emacs + Claude Code orchestration
SCITEX_CLOUD     → Web platform (companion, not replacement)
```

## Product Strategy

### Primary Product: **scitex.exe** (Local Desktop App)
- Standalone executable
- No installation complexity
- Full automation with user's credentials (local only)
- All research workflow tools
- Runs completely offline

### Secondary Product: **SciTeX Cloud** (Web Companion)
- Marketing & documentation
- Community features
- Optional cloud sync
- Collaboration tools
- Download center for scitex.exe

## Phase 1: Scholar Standalone (MVP)

### Goal
Prove the standalone executable approach with Scholar module.

### Features
```
```

...
```


### `./docs/SCITEX_WRITER_TEMPLATE_USAGE.md`

```markdown
# SciTeX Writer Template Usage

**Template Location**: `/home/ywatanabe/proj/scitex-cloud/docs/scitex_writer_template.tar.gz`

**Original Source**: Cleaned and templated version of `~/proj/neurovista/paper/`

## What's Included

The template contains the complete SciTeX Writer structure:

```
scitex_writer_template/
├── compile                        # Unified compilation script
├── config/                        # YAML configuration files
├── scripts/                       # Shell and Python utilities
│   ├── shell/
│   │   ├── compile_manuscript.sh
│   │   ├── compile_supplementary.sh
│   │   ├── compile_revision.sh
│   │   └── watch_compile.sh
│   └── python/
│       ├── explore_bibtex.py      # Bibliography analysis
│       ├── csv_to_latex.py        # Table conversion
│       └── pptx2tif.py           # Figure conversion
├── shared/                        # Shared metadata and styles
│   ├── title.tex
│   ├── authors.tex
│   ├── keywords.tex
│   ├── journal_name.tex
│   ├── bib_files/
│   │   └── bibliography.bib
│   └── latex_styles/
├── 01_manuscript/
│   ├── base.tex
│   ├── manuscript.tex
│   ├── contents/
│   │   ├── abstract.tex
│   │   ├── introduction.tex
│   │   ├── methods.tex
│   │   ├── results.tex
│   │   ├── discussion.tex
│   │   ├── figures/
│   │   │   └── caption_and_media/
│   │   └── tables/
│   │       └── caption_and_media/
│   ├── logs/
│   └── archive/
├── 02_supplementary/
│   └── [similar structure]
└── 03_revision/
```

...
```


### `./docs/SINGLE_SOURCE_OF_TRUTH.md`

```markdown
# Single Source of Truth - SciTeX Design System

## The Central Color System

**Location**: `/home/ywatanabe/proj/scitex-cloud/static/css/common/colors.css`

This is the **ONLY** place where SciTeX colors are defined. All other files use CSS variables from this file.

## File Structure

```
static/css/common/
├── variables.css          # Main import (imports all modules)
├── colors.css            # ⭐ COLOR DEFINITIONS (single source of truth)
├── typography-vars.css   # Typography variables
├── spacing.css           # Spacing system
├── effects.css           # Shadows, transitions
└── z-index.css           # Z-index layers
```

### How It Works

1. **`colors.css`** defines all colors (SciTeX brand palette)
2. **`variables.css`** imports all modules using `@import`
3. **`global_head_styles.html`** loads `variables.css`
4. All pages get colors automatically

## Color Definition (colors.css)

### SciTeX Brand Colors
```css
--scitex-color-01: #1a2332;  /* Primary dark bluish gray */
--scitex-color-02: #34495e;
--scitex-color-03: #506b7a;
--scitex-color-04: #6c8ba0;  /* Accent color */
--scitex-color-05: #8fa4b0;
--scitex-color-06: #b5c7d1;
--scitex-color-07: #d4e1e8;  /* Lightest */
```

### Semantic Variables (Defined ONCE in colors.css)
```css
/* Light Mode */
:root {
    --color-canvas-default: var(--white);
    --color-fg-default: var(--scitex-color-01);
    --color-accent-fg: var(--scitex-color-02);
    --color-btn-primary-bg: var(--scitex-color-02);
    /* ...etc */
}
```

...
```


### `./docs/TEMPLATE_CLEANUP_PLAN.md`

```markdown
# Repository Template Cleanup Plan

**Goal**: Create a clean, educational boilerplate from scitex_template_research

## Files Analysis

### ✅ KEEP AS-IS (Educational Content)
- `paper/01_manuscript/contents/abstract.tex` - Perfect structure guide with 7-part format
- `paper/01_manuscript/contents/introduction.tex` - Excellent paragraph-by-paragraph guide
- Structure and guidelines in all `.tex` files

### 🔨 CLEAN (Remove Neurovista-Specific Content)

#### 1. Tables
**Location**: `paper/01_manuscript/contents/tables/caption_and_media/`
**Issues**:
- Symlinks to actual neurovista data files
- Neurovista-specific table captions

**Action**:
```bash
# Remove neurovista tables
rm paper/01_manuscript/contents/tables/caption_and_media/*.csv
rm paper/01_manuscript/contents/tables/caption_and_media/*.tex

# Create example table
cat > paper/01_manuscript/contents/tables/caption_and_media/example_table.tex << 'EOF'
%% Table caption template
%% Table ID: 01
%%
%% Guidelines:
%% - Keep captions concise but informative
%% - Define all abbreviations used in the table
%% - Reference the table in text as Table~\ref{tab:example}

\begin{table}[htbp]
\centering
\caption{Example table showing data organization}
\label{tab:example}
\begin{tabular}{lcc}
\hline
Category & Value & Percentage (\%) \\
\hline
Group A & 123 & 45.6 \\
Group B & 98 & 36.3 \\
Group C & 49 & 18.1 \\
\hline
Total & 270 & 100.0 \\
\hline
\end{tabular}
```

...
```


### `./docs/TERMINOLOGY_GITHUB_ALIGNMENT.md`

```markdown
# Terminology: GitHub Alignment

**Decision**: Use GitHub terminology for consistency

## GitHub vs SciTeX

### Current (Mixed)
- ❌ "Project" (generic, unclear)
- ❌ "Workspace" (vague)
- ❌ Mixed terminology

### Proposed (GitHub-aligned)
- ✅ "Repository" (matches GitHub)
- ✅ Clear, familiar to developers and researchers

## Terminology Map

| Concept | SciTeX Term | GitHub Term | **Use** |
|---------|-------------|-------------|---------|
| Research work container | Project | Repository | **Repository** |
| List of repositories | Projects | Repositories | **Repositories** |
| Create new | Create Project | New Repository | **New Repository** |
| Settings | Project Settings | Repository Settings | **Repository Settings** |

## URL Structure

### Before
```
/ywatanabe1989/projects/           → Projects list
/ywatanabe1989/neurovista/         → Project dashboard
```

### After (GitHub-aligned)
```
/ywatanabe1989/?tab=repositories   → Repositories list
/ywatanabe1989/neurovista/         → Repository dashboard
```

## Implementation

### Database
- Keep `Project` model name (internal)
- Update display text to "Repository"

### Templates
- "Projects" → "Repositories"
- "Create Project" → "New Repository"
- "Project Name" → "Repository Name"

### URLs

...
```


### `./docs/to_claude/section_writing_guidelines.json`

```json
{
  "abstract": {
    "title": "Abstract Writing Guide",
    "wordCount": "150-300 words",
    "structure": [
      {
        "title": "Basic Introduction",
        "description": "1-2 sentences providing a basic introduction to the field, comprehensible to scientists in any discipline."
      },
      {
        "title": "Detailed Background",
        "description": "2-3 sentences of more detailed background, comprehensible to scientists in related disciplines."
      },
      {
        "title": "General Problem",
        "description": "1 sentence clearly stating the general problem being addressed by this study."
      },
      {
        "title": "Main Result",
        "description": "1 sentence summarizing the main result using 'here we show' or equivalent."
      },
      {
        "title": "Results with Comparisons",
        "description": "2-3 sentences explaining what the main result reveals compared to previous knowledge. Include specific quantitative results."
      },
      {
        "title": "General Context",
        "description": "1-2 sentences placing your results in a broader context."
      },
      {
        "title": "Broader Perspective",
        "description": "2-3 sentences (optional) providing broader perspective on implications and future impact."
      }
    ],
    "tips": [
      "Write as coherent, cohesive sentences without line breaks",
      "Use present tense for general facts",
      "Use past tense for specific prior research and your results",
      "Include quantitative measurements precisely",
      "Explicitly indicate species with sample sizes"
    ]
  },
  "introduction": {
    "title": "Introduction Writing Guide",
    "wordCount": "1000-2000 words (4-8 paragraphs)",
    "structure": [
      {
        "title": "Problem Statement",
        "description": "Introduce the broad research area, establish importance, provide context with statistics."
      },

...
```


### `./docs/URL_STRUCTURE.md`

```markdown
# SciTeX URL Structure

## Summary

**Problem:** With GitHub-style `/<username>/<project>` URLs, we need to reserve certain paths to prevent conflicts.

**Solution:**
1. Icons made smaller (32px containers with 16px icons)
2. Reserved paths list added to `config/urls.py`
3. Username validator created in `apps/auth_app/validators.py`
4. URLs registered in correct order (apps before username pattern)

## Reserved URL Prefixes

Cannot be used as usernames:

**System Apps:**
`admin`, `auth`, `billing`, `cloud`, `code`, `core`, `dev`, `docs`, `integrations`, `project`, `scholar`, `viz`, `writer`

**Resources:**
`static`, `media`, `api`, `new`

**Common Words:**
`about`, `help`, `support`, `contact`, `terms`, `privacy`, `settings`, `dashboard`, `profile`, `account`, `login`, `logout`, `signup`, `register`, `reset`, `verify`, `confirm`

**Special:**
`guest-*` (reserved for guest sessions), `robots`, `sitemap`, `favicon`

## URL Order (config/urls.py)

```python
# 1. Admin
path("admin/", ...)

# 2. Apps (auto-discovered: /auth/, /integrations/, etc.)
discover_app_urls()

# 3. Reserved paths
path("new/", ...)

# 4. Username pattern (MUST BE LAST)
path("<str:username>/", ...)
```

## Integration URLs

All working at `/integrations/`:
- `/integrations/` - Dashboard ✅
- `/integrations/orcid/connect/` - ORCID OAuth
- `/integrations/slack/configure/` - Slack webhooks

...
```


### `./docs/V1_QUICK_START.md`

```markdown
# SciTeX Cloud V1 - Quick Start Guide

**Version:** 1.0
**Date:** 2025-10-16
**Status:** 🚀 Shipped

## What's Working

### ✓ Core Features
- **Homepage** - `http://scitex.ai/` (200 OK)
- **Design System** - `http://scitex.ai/dev/design.html` (200 OK)
- **Automatic app discovery** - Add apps to `./apps/` and they auto-register
- **Clean database** - Fresh migrations in `./data/scitex_cloud.db`

### 📦 Active Apps (10)
1. auth_app - Authentication
2. billing_app - Subscriptions
3. cloud_app - Landing pages
4. code_app - Code execution
5. core_app - Core functionality
6. dev_app - Design system (NEW)
7. project_app - Project management
8. scholar_app - Literature search
9. viz_app - Visualizations
10. writer_app - Scientific writing

## Quick Commands

### Start Server
```bash
./server.sh
# or
python manage.py runserver
```

### Check Configuration
```bash
python manage.py check
```

### Format Templates
```bash
python scripts/format_templates.py apps/cloud_app/templates/
```

### Create Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

...
```


### `./docs/values_mission_vision_how-to-write.md`

```markdown

Mission Statements
The mission statement defines an organization’s purpose or reason for being. It guides the day-to-day operations of the organization, communicates to external stakeholders the core solutions the organization provides in society and motivates employees toward a common near-to-medium term goal. In short, the mission statement paints a picture of who the company is and what the company does.

A good mission statement should only focus on what is most important to the organization. It should be brief, clear, informative, simple and direct. It should avoid elaborate language, clichés, and generalizations and it should emphasize outcomes and the people the organization is serving.

When writing a mission statement, consider the following questions:

What do we do today?
Who do we serve?
What are we trying to accomplish?
What impact do we want to achieve?
Examples:

LinkedIn: To connect the world’s professionals to make them more productive and successful.
Starbucks: To inspire and nurture the human spirit – one person, one cup and one neighborhood at a time.
Twitter: To give everyone the power to create and share ideas and information, instantly, without barriers.
TripAdvisor: To help people around the world plan and have the perfect trip.
Tesla: To accelerate the world's transition to sustainable energy.
Sweetgreen: To inspire healthier communities by connecting people to real food.
Best Practices Video
Bâton Global's shares our secrets learned from helping organizations worldwide write winning Purpose, Mission, Vision and Value statements.

‍

Download 250 Examples
Interested in viewing examples from other organizations? Download our collection of of 250 purpose, mission, vision, and values statements below:


Vision Statements
The vision statement describes the future of the organization. It reveals what the company aspires to be or hopes to achieve in the long-term. The vision statement is inspirational and motivational but also provides direction, mapping out where the organization is headed. In this regard, it serves as a guide for choosing current and future courses of action.

An effective vision statement should be concise, unambiguous, futuristic, realistic, aspirational and inspirational. It shouldn’t be generic but rather focus on outcomes specific to the organization.

 When writing a vision statement, consider these questions:

Where are we going moving forward?
What do we want to achieve in the future?
What kind of future society do we envision?
Examples:

LinkedIn: To create economic opportunity for every member of the global workforce.
GoDaddy: To radically shift the global economy toward independent entrepreneurial ventures.
Wikimedia Foundation: Imagine a world in which every single human being can freely share in the sum of all knowledge. That’s our commitment.
Habitat for Humanity: A world where everyone has a decent place to live.
SouthwestAirlines: To be the world’s most loved, most efficient, and most profitable airline.
Download 250 Examples
Interested in viewing examples from other organizations? Download our collection of of 250 purpose, mission, vision, and values statements below:



...
```


### `./docs/values_mission_vision.md`

```markdown

SciTeX: Values, Mission, and Vision

🌟 Our Vision
To become the operating system for scientific research—empowering every researcher in the world to focus on discovery, not tools.
We envision a future where:

Research workflows are seamlessly integrated, not fragmented across a dozen tools
Knowledge flows freely between researchers, institutions, and generations
Reproducibility is guaranteed, not aspirational
Every researcher, regardless of resources, has access to world-class research infrastructure
Science accelerates through collaboration, transparency, and shared progress


🎯 Our Mission
To build a 100% open-source platform that transforms how research is conducted, shared, and validated.
We exist to:

Eliminate friction in the research workflow by unifying writing, analysis, literature management, and collaboration
Democratize access to cutting-edge research tools, making them free and accessible to all
Accelerate discovery by helping researchers spend less time on tools and more time on science
Ensure reproducibility by making transparency and openness the default, not the exception
Build community where researchers help each other succeed, sharing knowledge and best practices


💎 Our Core Values
1. Open by Default 🔓

Every line of code is public. Full transparency builds trust and enables reproducibility.
No vendor lock-in. Researchers own their data and workflows, forever.
Community contributions are welcome and celebrated.
Knowledge should be free, shared, and accessible to all.

2. Researchers First 🔬

We are researchers, building for researchers.
Every decision is made with the question: "Does this help researchers do better science?"
We listen deeply to the research community and adapt based on real needs, not trends.
Academic values—transparency, reproducibility, collaboration—guide everything we do.

3. Excellence Through Simplicity ✨

Powerful tools should be intuitive, not complicated.
We remove friction, not features. Complexity is the enemy of productivity.
Five-minute onboarding. No manuals required.
If it takes more than 3 clicks, we've failed.

4. Long-term Thinking 🌱

We optimize for decades, not quarters.

...
```


### `./externals/impact_factor/build.sh`

```bash
rm -rf dist build *egg-info

python3 setup.py sdist bdist_wheel

rm -rf build *egg-info

...
```


### `./externals/impact_factor/README.md`

```markdown
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.7539859.svg)](https://doi.org/10.5281/zenodo.7539859)

[![Downloads](https://pepy.tech/badge/impact-factor)](https://pepy.tech/project/impact-factor)
![PyPI - License](https://img.shields.io/pypi/l/mi?style=plastic)
![PyPI](https://img.shields.io/pypi/v/impact_factor)
![PyPI - Status](https://img.shields.io/pypi/status/impact_factor)


# ***最新SCI期刊影响因子查询系统***
- *已更新 **[2024年数据](https://www.researchgate.net/publication/381580823_Journal_Citation_Reports_JCR_Impact_Factor_2024_PDF_Web_of_Science)***
- *包含JCR分区表数据*

## Installation
```bash
python3 -m pip install -U impact_factor
```

## Use in CMD
```bash
impact_factor -h
```
![](https://suqingdong.github.io/impact_factor/src/help.png)

### `build`
> build/update the database

```bash
# optional, only required when you need build or update the database
impact_factor build -i tests/IF.xlsx

# with a ncbi api_key
impact_factor build -k YOUR_NCBI_API_KEY

# use a new dbfile [*recommend*]
impact_factor -d test.db build -i tests/IF.xlsx

# without nlm_catalog
impact_factor -d test.db build -i tests/IF.xlsx -n
```

### `search`
> search with `journal`, `journal_abbr`, `issn`, `eissn` or `nlm_id`

```bash
impact_factor search nature         # search journal
impact_factor search 'nature c%'    # like search journal
impact_factor search 0028-0836      # search ISSN
impact_factor search 1476-4687      # search eISSN
impact_factor search 0410462        # search nlm_id
impact_factor search nature --color # colorful output
```

...
```


### `./externals/impact_factor/setup.py`

```python
import json
from pathlib import Path
from setuptools import setup, find_packages


BASE_DIR = Path(__file__).resolve().parent
version_info = json.load(BASE_DIR.joinpath('impact_factor', 'version.json').open())

setup(
    name=version_info['prog'],
    version=version_info['version'],
    author=version_info['author'],
    author_email=version_info['author_email'],
    description=version_info['desc'],
    long_description=BASE_DIR.joinpath('README.md').read_text(),
    long_description_content_type='text/markdown',
    url=version_info['url'],
    project_urls={
        'Documentation': 'https://impact_factor.readthedocs.io',
        'Tracker': 'https://github.com/suqingdong/impact_factor/issues',
    },
    license='MIT License',
    install_requires=BASE_DIR.joinpath('requirements.txt').read_text().strip().split(),
    packages=find_packages(),
    include_package_data=True,
    entry_points={'console_scripts': [
        'IF = impact_factor.bin.cli:main',
        'impact_factor = impact_factor.bin.cli:main',
    ]},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3 :: Only',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Topic :: Software Development :: Libraries'
    ]
)

...
```


### `./externals/install_externals.sh`

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-07-01 08:51:23 (ywatanabe)"
# File: ./externals/install_externals.sh

THIS_DIR="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"
LOG_PATH="$THIS_DIR/.$(basename $0).log"
echo > "$LOG_PATH"

BLACK='\033[0;30m'
LIGHT_GRAY='\033[0;37m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo_info() { echo -e "${LIGHT_GRAY}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_warning() { echo -e "${YELLOW}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }
# ---------------------------------------

cd ./externals

# For Scholar
git clone git@github.com:ywatanabe1989/impact_factor

# SciTeX Static Modules
git clone git@github.com:ywatanabe1989/SciTeX-Scholar
git clone git@github.com:ywatanabe1989/SciTeX-Code
git clone git@github.com:ywatanabe1989/SciTeX-Viz
git clone git@github.com:ywatanabe1989/SciTeX-Writer

ln -s SciTeX-Scholar scholar
ln -s SciTeX-Code code
ln -s SciTeX-Viz viz
ln -s SciTeX-Writer writer

cd scholar && git switch develop && cd ..
cd code && git switch develop && cd ..
cd viz && git switch develop && cd ..
cd writer && git switch develop && cd ..

# EOF
...
```


### `./externals/INTEGRATION_COMPLETE.md`

```markdown
# 🎉 SciTeX Ecosystem Integration Complete

## 📋 Summary
Successfully integrated the complete SciTeX ecosystem with cloud-based LaTeX compilation, section-separated processing, and external component management.

## ✅ Completed Features

### 1. **Cloud-Based LaTeX Compilation**
- **Section-separated compilation**: Individual LaTeX sections (abstract, intro, methods, etc.)
- **Cloud resources**: 60-second timeout, asynchronous processing
- **API endpoint**: `/writer/project/{project_id}/cloud-compile/`
- **Status tracking**: Real-time compilation progress

### 2. **SciTeX-Writer Template Integration**
- **Automatic template copying**: From `~/proj/SciTeX-Writer/` → `./externals/SciTeX-Writer/`
- **Complete structure replication**: manuscript/, revision/, scripts/, supplementary/
- **Fallback system**: Graceful degradation if template unavailable
- **Custom compile scripts**: Project-specific compilation workflows

### 3. **External Components Architecture** 
```
./externals/
├── SciTeX-Writer/    ✅ Active (LaTeX templates & compilation)
├── SciTeX-Code/      ✅ Ready (Python scientific framework)
├── SciTeX-Viz/       ✅ Ready (SigmaPlot wrapper)
├── SciTeX-Scholar/   ✅ Ready (Literature search)
└── setup_externals.sh (Automated setup script)
```

### 4. **Dashboard Integration**
- **Writer Button**: Direct access to SciTeX Writer from dashboard
- **Project Selection**: Click project → press "Writer" button or `Ctrl+E`
- **Seamless Workflow**: Dashboard file management → Writer cloud compilation

### 5. **ZIP Download System**
- **Complete paper directories**: Download entire project/paper/ as ZIP
- **SciTeX-Writer compatible**: Ready for local development
- **API endpoint**: `/writer/project/{project_id}/download-paper/`
- **File preservation**: Maintains directory structure and permissions

## 🏗️ Technical Architecture

### Component Status
| Component | Status | Integration | Purpose |
|-----------|--------|-------------|---------|
| **SciTeX-Writer** | 🟢 Active | Template System | LaTeX compilation & templates |
| **SciTeX-Code** | 🟡 Ready | Planned | Python scientific framework |
| **SciTeX-Viz** | 🟡 Ready | Planned | SigmaPlot visualization |
| **SciTeX-Scholar** | 🟡 Ready | Planned | Literature search |
| **SciTeX-Engine** | 🔵 Planned | External | Emacs LLM agent |

...
```


### `./externals/integration_status.json`

```json
{
  "timestamp": "2025-06-29T20:15:52+09:00",
  "components": {
    "SciTeX-Writer": {
      "status": "active",
      "integration": "template_system",
      "description": "LaTeX template system for cloud compilation"
    },
    "SciTeX-Code": {
      "status": "ready", 
      "integration": "planned",
      "description": "Python framework for scientific computation"
    },
    "SciTeX-Viz": {
      "status": "ready",
      "integration": "planned", 
      "description": "SigmaPlot visualization wrapper"
    },
    "SciTeX-Scholar": {
      "status": "ready",
      "integration": "planned",
      "description": "Literature search and analysis"
    },
    "SciTeX-Engine": {
      "status": "planned",
      "integration": "external",
      "description": "Emacs-based LLM agent system"
    }
  }
}

...
```


### `./externals/README.md`

```markdown
# SciTeX External Components

This directory contains the core SciTeX ecosystem components that integrate with the cloud platform.

## Core SciTeX Components

### 🔧 SciTeX-Engine (emacs-claude-code)
- **Purpose**: LLM agent system for Emacs enabling seamless human-AI collaboration
- **Integration**: Code execution and development environment
- **Status**: External component

### 🐍 SciTeX-Code (SciTeX-Code)
- **Purpose**: Standardized Python framework for scientific analysis and computation
- **Integration**: Jupyter notebooks, data analysis workflows
- **Status**: ✅ Cloned (git repository)

### 📊 SciTeX-Viz (SciTeX-Viz)
- **Purpose**: Python wrapper for SigmaPlot enabling programmatic scientific visualization
- **Integration**: Visualization pipeline, figure generation
- **Status**: ✅ Cloned (git repository)

### 🔍 SciTeX-Scholar (SciTeX-Scholar)
- **Purpose**: Literature search, knowledge gap identification, and hypothesis generation
- **Integration**: Paper search and recommendation system
- **Status**: ✅ Cloned (git repository)

### 📝 SciTeX-Writer (SciTeX-Writer)
- **Purpose**: Automated LaTeX compilation system with predefined tex, bibtex, table, and figure files
- **Integration**: Cloud compilation, project templates
- **Status**: ✅ Cloned (git repository)

### 📋 SciTeX-Example-Research-Project
- **Purpose**: Complete research project boilerplate and template
- **Integration**: Project creation template, directory structure
- **Status**: ✅ Cloned (git repository)

### ☁️ SciTeX-Cloud (Current Repository)
- **Purpose**: Cloud platform for the SciTeX ecosystem (https://scitex.ai)
- **Integration**: Django web platform, API endpoints
- **Status**: ✅ Active

## Directory Structure

```
SciTeX-Cloud/
├── externals/
│   ├── SciTeX-Engine/                    (to be cloned)
│   ├── SciTeX-Code/                      ✅ Cloned
│   ├── SciTeX-Viz/                       ✅ Cloned
│   ├── SciTeX-Scholar/                   ✅ Cloned
```

...
```


### `./manage.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-21 10:08:09 (ywatanabe)"
# File: /home/ywatanabe/proj/SciTeX-Cloud/manage.py
# ----------------------------------------
import os
__FILE__ = (
    "./manage.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import sys


def main():
    """Run administrative tasks."""
    # Add base and config directories to Python path
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    sys.path.insert(0, BASE_DIR)  # Add base directory
    sys.path.insert(0, os.path.join(BASE_DIR, "config"))  # Add config directory
    # No need to add src directory anymore as it's been replaced by apps

    # Use new auto-detection settings module
    # Set SCITEX_CLOUD_ENV=production for production, defaults to development
    os.environ.setdefault(
        "DJANGO_SETTINGS_MODULE", "config.settings"
    )
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == "__main__":
    main()

# EOF

...
```


### `./package.json`

```json
{
  "name": "scitex-web",
  "version": "0.1.0",
  "description": "SciTeX Cloud web interface for researchers",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest"
  },
  "keywords": [
    "scitex",
    "research",
    "science",
    "web",
    "django"
  ],
  "author": "ywatanabe",
  "license": "UNLICENSED",
  "dependencies": {
    "express": "^4.17.1"
  },
  "devDependencies": {
    "jest": "^29.7.0",
    "jest-environment-jsdom": "^29.7.0",
    "nodemon": "^2.0.22"
  }
}

...
```


### `./project_management/accessibility-improvements-20250521.md`

```markdown
# SciTeX Web Accessibility and Responsiveness Improvements

This document summarizes the accessibility and responsiveness improvements made to the SciTeX Web legal and contact pages.

## Base Template Improvements

### Keyboard Navigation
- Added a skip-to-content link for keyboard users to bypass repetitive navigation
- Added visible focus styles for all interactive elements
- Added `aria-current="page"` to active navigation links

### Screen Reader Support
- Added `aria-label` attributes to navigation elements
- Added proper `aria-hidden="true"` to decorative icons
- Added descriptive `aria-label` attributes to links that need more context

### Structural Improvements
- Wrapped main content in a semantic `<main>` element with an ID for skip navigation
- Added ARIA attributes to provide better context for interactive elements

## Contact Page Improvements

### Form Accessibility
- Added `aria-required="true"` to required form fields
- Implemented proper error feedback with `aria-invalid` and `aria-describedby`
- Added error messages with `role="alert"` for dynamic validation
- Implemented focus management for validation errors (focus moves to first error)

### Semantic HTML
- Replaced emoji icons with Font Awesome icons
- Used proper `<address>` tags for contact information
- Added `aria-label` attributes to social media links with clear descriptions
- Added `title` and `aria-label` to Google Maps iframe

### Responsive Improvements
- Enhanced mobile layout with reordering of content for better experience

## Privacy Policy and Terms of Use Improvements

### Document Structure
- Added ID attributes to all section headings for better navigation
- Wrapped content in `<article>` tags for better semantics
- Used proper `<address>` tags for contact information
- Used `<time>` element with `datetime` attribute for dates

### Content Readability
- Added role="note" to highlighted information
- Improved heading hierarchy and semantic meaning
- Replaced ALL CAPS text with normal case text in limitation of liability section
- Made email links more accessible with descriptive aria-labels

...
```


### `./project_management/advancement-priorities-20250628.md`

```markdown
# SciTeX Cloud Project Advancement Priorities
**Date**: 2025-06-28  
**Status**: Platform Fully Operational - Ready for Next Phase  

## Current State Assessment
✅ **Production Deployment**: Live at https://scitex.ai with SSL, authentication, and monitoring  
✅ **Core Modules**: Scholar, Writer, Viz, Code all operational with enhanced UX  
✅ **Test Coverage**: All critical tests passing (28/28 core tests)  
✅ **Feature Requests**: Latest user requests implemented (module ordering, live compilation, UX improvements)  
✅ **Platform Stability**: Zero critical bugs, comprehensive error handling  

## 🎯 **Priority 1: User Onboarding & Growth (Immediate - Next 2 weeks)**

### 1.1 Enhanced User Experience
- **Priority**: CRITICAL
- **Description**: Improve first-time user experience and retention
- **Actions**:
  - Create interactive onboarding tutorial
  - Add guided tours for each module
  - Implement progress tracking for user achievements
  - Add sample projects/templates for immediate value

### 1.2 Content & Documentation
- **Priority**: HIGH  
- **Description**: Provide comprehensive user guidance
- **Actions**:
  - Create video tutorials for each module
  - Add API documentation with live examples
  - Implement in-app help system
  - Create scientific use case examples

### 1.3 Performance Optimization
- **Priority**: HIGH
- **Description**: Ensure optimal performance at scale
- **Actions**:
  - Implement Redis caching for Scholar search
  - Optimize database queries with select_related/prefetch_related
  - Add CDN for static assets
  - Implement lazy loading for dashboard components

## 🚀 **Priority 2: Advanced Features (Next 4 weeks)**

### 2.1 Scholar Module Enhancement
- **Priority**: HIGH
- **Description**: Make Scholar the most comprehensive research tool
- **Actions**:
  - Add citation export (BibTeX, EndNote, RIS)
  - Implement paper similarity recommendations
  - Add research trend analysis
  - Create personal research library

...
```


### `./project_management/AGENT_BULLETIN_BOARD.md`

```markdown
# Agent Bulletin Board

Coordination point for Claude Code agents working on SciTeX Cloud.

---

## CLAUDE-2025-10-16-03h (Web Developer & Refactoring)

### Completed
- [x] Shipped V1: Streamlined from 21 → 10 apps with auto-discovery
- [x] Created dev_app with design system at `/dev/design.html`
- [x] Organized templates with `global_*` prefix for shared partials
- [x] Fresh database in `./data/` with clean migrations
- [x] Added all 4 module demos to landing (Scholar, Writer, Code, Viz)
- [x] Created Developer icon (screwdriver SVG)
- [x] Standardized Code features to match other modules
- [x] Added docs_app with Documentation buttons
- [x] Added GitHub fallback for unbuilt Sphinx docs
- [x] Integrated Code demo video (1.4MB)
- [x] Light hero gradient applied
- [x] Balanced icons on demo titles
- [x] Section filtering in design system (default: Colors)

### Stats
- **36 commits** shipped in this session
- **Landing page**: Complete with 4 module demos
- **Design system**: Interactive filtering, Developer icon added
- **Template structure**: Clean skeleton with global partials
- **Auto-discovery**: Apps and URLs auto-register

### Issues Found
- Sphinx docs build failing (autosummary extension errors)
- Viz demo video script created but not executed yet
- Module pages (scholar, code, viz, writer) have 500 errors - need view implementations

### Recommendations
- Build Sphinx docs properly for each module
- Create Viz demo video using `scripts/create_viz_demo_video.sh`
- Fix module landing pages (currently 500 errors)
- Consider adding API documentation
- Test Documentation buttons after Sphinx builds

---

## Next Agent

Please continue with:
1. Fix Sphinx documentation builds for all modules
2. Complete Viz demo video creation
3. Fix 500 errors on module landing pages

...
```


### `./project_management/airight-comparison-20250522.md`

```markdown
# Django Project Structure Comparison with airight

**Date:** May 22, 2025

## Overview

This document compares the structure and setup of the `SciTeX-Cloud` project with the `airight` project to identify best practices for Django application deployment and maintenance.

## Project Structure Analysis

### Common Elements

Both projects follow standard Django conventions:
- Django apps in an `apps` directory
- Configuration settings in a `config` directory
- Static files management with collectstatic
- Template organization in folders by app

### Differences and Learnings

1. **Script Organization**
   - airight: Uses comprehensive start/stop scripts with command-line arguments
   - SciTeX-Cloud: Has a more advanced unified startup script that auto-detects which script to run
   - Learning: SciTeX-Cloud's approach is more user-friendly but could benefit from airight's production deployment logic

2. **Environment Configuration**
   - airight: Uses a simpler settings approach with a single settings.py file
   - SciTeX-Cloud: Uses a split settings approach (base, dev, prod) which is more modular
   - Learning: SciTeX-Cloud's approach is better for larger projects, but we need to ensure consistency

3. **Deployment Configuration**
   - airight: Uses uWSGI directly with custom init file
   - SciTeX-Cloud: Has more comprehensive Nginx configuration
   - Learning: We should integrate airight's uWSGI approach with our Nginx setup

4. **Logging**
   - airight: Simpler logging to a single file
   - SciTeX-Cloud: More detailed logging with separate files for different purposes
   - Learning: SciTeX-Cloud's approach is better but we need to ensure logs are properly rotated

## Script Features to Adopt

From the airight project, we should adopt:

1. **Graceful shutdown in production**
   ```bash
   # Clear socket before starting
   echo "Cleaning up existing socket..."
   sudo rm -f "$APP_HOME/uwsgi.sock"
   sudo pkill -f uwsgi -9
```

...
```


### `./project_management/autonomous-development-final-summary-20250522.md`

```markdown
# SciTeX-Cloud Complete Autonomous Development Session Summary

**Date:** May 22, 2025  
**Mode:** Full Autonomous Development Following TDD Guidelines  
**Session Duration:** ~3 hours  
**Final Test Status:** ✅ **71/71 PASSED** (25 Django + 46 JavaScript)

## 🎯 **Session Achievements Overview**

This autonomous development session has successfully transformed SciTeX-Cloud from a basic Django application into a **production-ready research management platform** with enterprise-grade functionality, comprehensive testing, and excellent user experience.

## 🏆 **Major Systems Implemented**

### 1. **Complete Test-Driven Development Infrastructure** ✅
- **Comprehensive TDD workflow** with Red-Green-Refactor cycle
- **Jest + Django testing integration** with 71 total tests
- **Automated test running** and coverage reporting
- **TDD best practices** following AAA pattern (Arrange-Act-Assert)

### 2. **Document Management System** ✅
**Backend API:**
- `GET/POST /core/api/v1/documents/` - List/Create documents
- `GET/PUT/DELETE /core/api/v1/documents/{id}/` - Individual operations
- Advanced pagination, filtering, search, and validation

**Frontend Features:**
- Interactive forms with real-time validation
- Document type management (Notes, Papers, Projects, Drafts)
- Search and filtering capabilities
- Modal viewing and editing
- Status messages and loading indicators

### 3. **Project Management System** ✅
**Advanced Project Tracking:**
- Full CRUD operations with status management
- Deadline tracking with overdue detection
- Status indicators (Planning, Active, Completed, On Hold)
- Real-time project statistics
- Collaboration support

**Enhanced UI/UX:**
- Visual status indicators with color coding
- Deadline warnings and alerts
- Project filtering and responsive design
- Interactive hover effects

### 4. **User Profile Management System** ✅
**Academic Profile Features:**
- Enhanced profile model with academic fields
- ORCID integration and validation

...
```


### `./project_management/autonomous-development-session-summary-20250522.md`

```markdown
# SciTeX-Cloud Autonomous Development Session Summary

**Date:** May 22, 2025  
**Mode:** Autonomous Development Following TDD Guidelines  
**Session Duration:** ~2 hours  
**Final Test Status:** ✅ 52/52 PASSED (25 Django + 27 JavaScript)

## 🎯 Session Objectives

Following the memorized development guidelines, this autonomous session focused on implementing core functionality for the SciTeX-Cloud research management platform using Test-Driven Development (TDD) principles.

## 🏆 Major Achievements

### 1. Complete Test-Driven Development Infrastructure ✅
- **Established comprehensive TDD workflow** with Red-Green-Refactor cycle
- **JavaScript testing with Jest**: 27 tests covering frontend functionality  
- **Django backend testing**: 25 tests covering API and models
- **Coverage reporting** and automated test running
- **Configuration optimization** for efficient development

### 2. Document Management System ✅
**API Endpoints Implemented:**
- `GET/POST /core/api/v1/documents/` - List/Create documents
- `GET/PUT/DELETE /core/api/v1/documents/{id}/` - Individual operations
- Advanced pagination, filtering, and search functionality

**Frontend Features:**
- Interactive document forms with validation
- Real-time search and type filtering
- Modal viewing with edit/delete actions
- Status messages and loading indicators
- Responsive design with accessibility features

### 3. Project Management System ✅  
**Advanced Project Tracking:**
- Full CRUD operations with status management
- Deadline tracking with overdue detection
- Visual status indicators (Planning, Active, Completed, On Hold)
- Real-time project statistics dashboard
- Collaborative project features

**Enhanced UI/UX:**
- Color-coded status indicators
- Deadline warnings and alerts
- Project filtering and pagination
- Responsive mobile-friendly design

### 4. Enhanced Dashboard ✅
**Real-time Features:**
- Live statistics with auto-refresh every 30 seconds

...
```


### `./project_management/bug-reports/bug-report-dashboard-directory-structure-not-shown.md`

```markdown

# Bug Report: Dashboard Directory Structure Not Shown

## Problem Description
Directory structure is not displayed in the dashboard, preventing users from viewing their project file organization.

## Expected Behavior
Dashboard should show project directory structures, allowing users to:
- View project file trees
- Navigate project directories
- Understand project organization
- Access project files

## Actual Behavior
Directory structure is not visible or not loading in the dashboard interface.

## Environment
- **Platform**: SciTeX-Cloud Dashboard
- **Module**: Core App Dashboard
- **Browser**: [To be determined during investigation]
- **User Type**: Authenticated users with projects

## Bug Fix Progress
- [x] Identify root cause
- [x] Check dashboard template implementation
- [ ] Verify directory manager integration
- [ ] Test project directory creation
- [ ] Fix directory structure display
- [ ] Test directory navigation
- [ ] Verify file listing functionality

## Investigation Plan

### Potential Causes
1. **Template Issue**: Dashboard template missing directory structure component
2. **JavaScript Issue**: Frontend not loading directory data
3. **API Issue**: Backend not providing directory structure data
4. **Permission Issue**: User lacking permissions to view directories
5. **Project Directory Issue**: Projects not properly initializing directories
6. **CSS Issue**: Directory structure hidden by styling

### Investigation Steps
1. Check dashboard template for directory structure components
2. Verify project directory creation in directory manager
3. Test API endpoints for directory structure
4. Check JavaScript for directory loading
5. Verify project permissions and access
6. Test with different user accounts and projects

## Root Cause Analysis

...
```


### `./project_management/bug-reports/bug-report-github-sync-authentication.md`

```markdown
# Bug Report: GitHub Sync Authentication Issue

## Problem Summary
GitHub sync functionality is not working properly. The backend implementation exists but fails during execution.

## Bug Details
- **Status**: Active
- **Priority**: High
- **Reporter**: User feedback: "sync github does not work yet"
- **Affected Component**: GitHub sync functionality in dashboard
- **File**: `apps/core_app/directory_views.py:552-790`

## Root Cause Analysis
The GitHub sync function `sync_with_github` exists with comprehensive implementation including:
- Git command execution via subprocess
- URL validation and security checks
- Proper error handling and timeouts
- Support for init, push, pull, status actions

However, the most likely causes of failure are:

1. **Git Authentication Issues**:
   - Server may not have Git credentials configured
   - SSH keys or personal access tokens not set up
   - Git user configuration missing

2. **Git Installation**:
   - Git may not be installed on the server
   - Git executable not in PATH

3. **File Permissions**:
   - Project directories may have permission issues
   - Web server user may not have write access to project folders

## Technical Implementation
The sync function implements:
- `subprocess.run()` with 30-second timeouts
- Proper working directory handling (`cwd=project_path`)
- Comprehensive error capture and reporting
- Support for multiple Git operations

## Testing Steps
To diagnose the issue:
1. Check if Git is installed: `git --version`
2. Verify Git global configuration: `git config --global --list`
3. Test Git authentication with GitHub
4. Check project directory permissions
5. Verify web server user can execute Git commands

## Suggested Fixes

...
```


### `./project_management/bug-reports/bug-report-github-sync-not-working.md`

```markdown
# Bug Report: GitHub Sync Not Working

## Problem Description
GitHub sync functionality does not work properly, preventing users from connecting their projects to GitHub repositories.

## Expected Behavior
Users should be able to:
- Initialize Git repositories in their projects
- Connect to GitHub repositories
- Push and pull changes
- View Git status and history

## Actual Behavior
GitHub sync operations fail or don't complete successfully.

## Potential Root Causes

### 1. Git Configuration Issues
- Git user.name and user.email not configured on server
- Missing SSH keys or authentication setup
- GitHub authentication not properly configured

### 2. Directory Permissions
- Project directory permissions preventing Git operations
- Server user lacking write permissions for Git files

### 3. Git Installation
- Git not installed on server
- Wrong Git version or missing Git commands

### 4. Authentication Issues
- Missing GitHub personal access tokens
- SSH key authentication not set up
- HTTPS authentication failing

## Investigation Steps

1. **Check Git Installation**
   ```bash
   git --version
   which git
   ```

2. **Check Git Configuration**
   ```bash
   git config --global user.name
   git config --global user.email
   ```

3. **Test Directory Permissions**

...
```


### `./project_management/bug-report-signup-2025-0521.md`

```markdown
# Bug Report: Signup Functionality Not Working

## Issue Description
The "Sign Up" button on the SciTeX website leads to a non-existent page. Although the backend API for registration is implemented, there is no corresponding frontend component to allow users to complete the signup process.

## Severity
**Critical** - New users cannot create accounts, blocking access to the platform's functionality.

## Steps to Reproduce
1. Visit the SciTeX homepage
2. Click on "Sign Up" or "Sign Up Free" button in the header
3. Result: No signup page is displayed, or a 404 error occurs

## Expected Behavior
Clicking the "Sign Up" button should direct users to a registration form where they can enter their information (username, email, password) to create a new account.

## Actual Behavior
The button directs to a URL (/signup) that has no corresponding route defined in the application, resulting in a 404 error or no response.

## Technical Analysis

### Root Causes
1. **Missing URL Route**: No URL path defined for `/signup/` in `urls.py`
2. **Missing View Function**: No view function to render a signup page in `views.py`
3. **Missing Template**: No HTML template for the signup form
4. **Missing Frontend Logic**: No JavaScript code to handle form submission to the API endpoint

### Existing Components
- Backend API for registration exists at `/api/v1/auth/register/` (implemented in `api.py`)
- User authentication system is properly configured in Django settings
- User and UserProfile models are correctly defined

## Proposed Solution

### 1. Create a Signup Template
Create a new template file at `src/scitex_web/templates/scitex_web/signup.html` with a registration form that collects:
- Username
- Email
- Password
- First name (optional)
- Last name (optional)

### 2. Add a View Function
Add the following function to `views.py`:

```python
def signup(request):
    """Signup page view"""
    return render(request, 'scitex_web/signup.html', {
        'title': 'Create an Account',
```

...
```


### `./project_management/BULLETIN-BOARD.md`

```markdown
# BULLETIN BOARD - Agent Communication

This is the central communication board for all agents working on the SciTeX-Cloud project. Please read this before starting work and update when necessary.

## Agent: Publications Content Specialist
Role: Abstract Accuracy & DOI Enhancement
Status: completed
Task: Update publications with accurate abstracts and clickable DOI links
Notes: ✅ **DOI Enhancement**: Added clickable DOI links for Neural Networks 2024 (10.1016/j.neunet.2023.12.009) and JNE 2021 (10.1088/1741-2552/ac3266) papers. ✅ **Abstract Correction**: Updated Neural Networks paper abstract with accurate content from actual publication, including specific performance metrics (balanced accuracies 0.927, 0.805, 0.920) and key findings about MCI pathology detection. ✅ **Scientific Accuracy**: Abstract now properly reflects the research on dementia/MCI detection using deep CNNs while maintaining SciTeX tool integration context. ✅ **User Request Fulfilled**: Publications page now accurately represents published research content as requested by user.
Timestamp: 2025-0628-19:30

---

## 🎯 **CURRENT PLATFORM STATUS - SciTeX Cloud**
**Status**: FULLY OPERATIONAL ✅  
**Last Updated**: 2025-06-29-19:25  
**Live Site**: https://scitex.ai

### **Active Modules**
- 📚 **SciTeX Scholar**: Progressive search from 7 academic sources (arXiv, PMC, Semantic Scholar, DOAJ, bioRxiv, PLOS, PubMed)
- 📝 **SciTeX Writer**: LaTeX editor with real compilation and collaborative features  
- 📊 **SciTeX Viz**: Coming Soon - Professional visualization platform in development
- 🔬 **SciTeX Code**: Coming Soon - Scientific computing environment in development
- 📄 **Publications**: Showcasing 4 real research papers using SciTeX tools

### **Infrastructure**
- ✅ **Production**: uWSGI + Nginx, SSL certified, optimized performance
- ✅ **Authentication**: OTP email verification with 6-digit modern UX
- ✅ **Email System**: Full SMTP integration operational  
- ✅ **Security**: HSTS enabled, password validation, secure user management
- ✅ **Testing**: All Django tests passing, comprehensive error handling
- ✅ **Monitoring**: Real-time analytics and performance tracking active

### **Recent Major Completions**
- **Priority 3.3 AI Assistant**: Full implementation with research question suggestions, literature analysis, and template infrastructure
- **User Onboarding System**: Enhanced 30-day engagement, progress tracking, achievement system, sample projects
- **Design System Consistency**: Unified hero sections across all modules with SciTeX branding
- **Project Management**: Unique project names, GitHub integration, filesystem compatibility
- **Performance Optimization**: Scholar search caching, database query optimization
- **Coming Soon Implementation**: Professional messaging for Code/Viz modules
- **Publications Enhancement**: Added clickable DOI links and accurate abstracts from actual research papers
- **URL Navigation Fix**: Resolved /code/ and /viz/ redirection issues for proper coming soon page display
- **Production Startup Issues**: Fixed RedirectView import, database constraints, missing URL patterns, and template references. Cleaned up verbose logging in start.sh script for production deployment.
- **Writer Hero Section**: Fixed /writer/ URL routing to display proper hero section matching design consistency across all modules.
- **Onboarding System Streamlined**: Removed all unnecessary module tours, simplified onboarding steps to focus on essential actions (welcome, profile setup, first project, first search, first document). Updated models, views, templates, and admin interface accordingly.
- **User Experience Enhanced**: Removed annoying onboarding popup, added clear call-to-action buttons to landing page with personalized messaging for authenticated vs non-authenticated users.
- **Smart Recommendations System**: Implemented contextual recommendations in dashboard based on user activity, project count, and registration date. Removed help button from interface for cleaner UX.

### **Latest Completion** 
**🎉 API Key Management & Impact Factor Integration - COMPLETE** (2025-06-30-02:32)

...
```


### `./project_management/CLAUDE_PLAN.md`

```markdown
# SciTeX Web Project - Claude Plan

## Project Status
| Type | Stat | Description           |
|------|------|-----------------------|
| 🚀   | [ ]  | SciTeX Web Project    |

## Goals, Milestones, and Tasks
#### 🎯 Goal 1: Establish Project Structure and Plan
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [x]  | Establish project structure and planning      |
|      |      | 📌 Essential for organized development        |
|------|------|-----------------------------------------------|
| 🏁   | [x]  | Create project management directory           |
|      |      | 📌 Foundation for tracking progress           |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create USER_PLAN.md template                  |
|      |      | 📌 `/home/ywatanabe/proj/scitex-web/project_management/USER_PLAN.md` |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create CLAUDE_PLAN.md for tracking            |
|      |      | 📌 `/home/ywatanabe/proj/scitex-web/project_management/CLAUDE_PLAN.md` |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Populate USER_PLAN.md with project details    |
|      |      | 📌 Collaboration needed with user             |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create progress tracking visuals with Mermaid |
|      |      | 📌 Required for visual project monitoring     |

#### 🎯 Goal 2: Implement Version Control
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Establish proper git workflow                 |
|      |      | 📌 Following version control guidelines       |
|------|------|-----------------------------------------------|
| 🏁   | [x]  | Resolve current git status issues             |
|      |      | 📌 Unstaged files with cleanup branch         |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create proper branch structure                |
|      |      | 📌 Created feature and checkpoint branches    |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Commit project development                    |
|      |      | 📌 Track initial project structure            |

#### 🎯 Goal 3: Implement Test-Driven Development
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Establish TDD workflow                        |
|      |      | 📌 Following TDD guidelines                   |
|------|------|-----------------------------------------------|

...
```


### `./project_management/cleanup-plan-2025-0521-030635.md`

```markdown
# SciTeX Web Project - Cleanup Plan

## Current State Analysis

### Project Structure Issues
1. Incomplete directory structure lacking standard web project organization
2. Inconsistent git repository state with staged but deleted files
3. Missing source code directories for the web application
4. No testing infrastructure in place

### Git Issues
1. Staged but deleted files in `../literature_review/` directory
2. Unstaged project management files
3. Numerous untracked files and directories
4. Currently on feature branch not following naming convention

## Cleanup Tasks (Prioritized)

### 1. Resolve Git Issues
- [x] Create safety branches (feature/cleanup and checkpoint/before-cleanup)
- [x] Resolve staged but deleted files issue
- [ ] Stage project management files
- [ ] Commit cleanup setup

### 2. Establish Core Directory Structure
- [x] Create standard web application structure:
  - [x] `src/` for application source code
  - [x] `public/` for static assets
  - [x] `tests/` for test files
  - [x] `docs/` for documentation (already exists)
  - [x] `config/` for configuration files
  - [x] `.old/` for safely archived files

### 3. Standardize File Naming
- [x] Review and rename any files with development patterns (-v01, -fix, etc.)
- [x] Apply consistent naming conventions to all files
- [x] Organize files into appropriate directories

### 4. Clean Up Documentation
- [x] Review and organize documentation files
- [x] Ensure all guidelines are properly referenced and available
- [x] Update project management files with cleanup progress

### 5. Clean Up Source Code
- [x] Apply Clean Code principles to any existing source code
- [x] Remove or safely archive obsolete files
- [x] Establish coding standards for the project

### 6. Create Basic Web Application Structure
- [x] Set up Django application structure

...
```


### `./project_management/cleanup-plan-2025-0521-051500.md`

```markdown
# SciTeX Web Cleanup Plan

Date: 2025-05-21

## Issues Identified

1. **Duplicate Configuration Files**:
   - Multiple Django settings files in different locations: `/config/django_settings.py`, `/config/settings/`, and `/settings/`
   
2. **Inconsistent Project Structure**:
   - Mixed JavaScript and Python code in `/src/`
   - Duplicate static files in `/public/` and `/static/`
   
3. **Redundant Files**:
   - Multiple startup scripts: `start_dev.sh`, `start_prod.sh`, `start_dev_server.sh`
   - Duplicate configuration files
   
4. **Unclear Project Organization**:
   - Mixing of frontend and backend code without clear separation
   - Redundant app configuration files

## Cleanup Tasks (Prioritized)

1. **Standardize Django App Structure**:
   - [ ] Consolidate Django settings to a single location
   - [ ] Organize views, models, and templates properly
   - [ ] Ensure URL routing is correct

2. **Organize Static Files**:
   - [ ] Consolidate static files from `/public/` and `/static/` to a single location
   - [ ] Ensure CSS and JS files follow standard naming conventions

3. **Clean Up Configuration**:
   - [ ] Remove redundant configuration files
   - [ ] Standardize environment setup

4. **Standardize Startup Scripts**:
   - [ ] Create a single development startup script
   - [ ] Create a single production startup script

5. **Organize Project Structure**:
   - [ ] Separate frontend and backend code clearly
   - [ ] Ensure proper imports and references

## Acceptance Criteria

- Django app runs successfully after cleanup
- All tests pass after changes
- Project structure follows standard Django conventions
- Clear separation between frontend and backend components

...
```


### `./project_management/cleanup-summary-2025-0521-030635.md`

```markdown
# SciTeX Web Project - Cleanup Summary

## Actions Completed

### 1. Repository Safety Measures
- Created feature branch: `feature/cleanup-2025-0521-030635`
- Created checkpoint branch: `checkpoint/before-cleanup-2025-0521-030635`

### 2. Project Structure Organization
- Created standard web application structure:
  - `src/` for application source code (JavaScript and Django)
  - `public/` for static assets (CSS and JavaScript)
  - `tests/` for test files
  - `config/` for configuration files
  - `.old/` for safely archived files

### 3. Basic Implementation
- Created Django application structure following best practices
- Implemented frontend HTML/CSS/JS templates
- Added sample unit tests
- Created dependency management files (package.json, requirements.txt)

### 4. Project Management
- Updated progress tracking documents
- Created a comprehensive cleanup plan
- Documented project requirements
- Referenced existing documentation

## Current Project Status
The project has been restructured following clean code principles and now has:

1. A clear, standardized directory structure
2. Basic Django web application setup
3. Frontend templates and styling
4. Test framework in place
5. Dependency management established

## Remaining Issues
- Git repository has some configuration issues with the lock file that need to be resolved
- Need to fill in USER_PLAN.md with detailed project requirements
- The project is not yet integrated with other SciTeX components

## Next Steps Recommendation
1. Resolve git configuration issues
2. Create detailed project plan in USER_PLAN.md
3. Implement connection to other SciTeX components
4. Set up CI/CD pipeline for testing
5. Implement user authentication

---

...
```


### `./project_management/cleanup-summary-2025-0521-032740.md`

```markdown
# SciTeX Web Project - Cleanup Summary

## Cleanup Status - 2025-05-21 03:27:40

### Completed Tasks

1. **Project Structure Establishment**
   - Created standard web application structure (`src/`, `public/`, `tests/`, `docs/`, `config/`)
   - Implemented Django application structure under `src/scitex_web/`
   - Set up templates in `src/scitex_web/templates/scitex_web/`

2. **Feature Implementation**
   - Implemented legal pages (Privacy Policy, Terms of Use)
   - Implemented Contact page with form
   - Created base template for inheritance
   - Added URL routing for new pages

3. **Documentation**
   - Established guidelines directory with Django rules
   - Created project management files for tracking progress

### Remaining Tasks

1. **Git Management**
   - Stage project management files
   - Review untracked files and determine which should be added to the repository
   - Commit changes on feature branch
   - Merge feature branch to main/develop when ready

2. **Testing**
   - Test pages for responsiveness and accessibility
   - Implement tests for views and form submissions
   - Ensure test coverage for new features

3. **Django Structure Improvement**
   - Evaluate whether to separate templates into named app directories
   - Consider creating dedicated apps for different functionality (auth, api, etc.)
   - Implement proper form handling with validation

4. **Documentation Updates**
   - Update README.md with project setup instructions
   - Complete progress tracking for feature implementation
   - Document next steps for project development

## Next Steps

1. Complete testing for legal and contact pages
2. Review legal content with stakeholders
3. Prepare pull request for merging feature branch
4. Set up continuous integration for automated testing

...
```


### `./project_management/cleanup-summary-2025-0521-051500.md`

```markdown
# SciTeX Web Cleanup Summary

Date: 2025-05-21

## Changes Made

### 1. Django App Structure

- Consolidated Django settings into a single location: `/src/scitex_web/settings/`
  - Created proper base.py, development.py, and production.py
  - Removed duplicate settings from `/config/django_settings.py` and `/settings/`
  
- Updated imports and paths in:
  - manage.py
  - wsgi.py
  - asgi.py

### 2. Static Files Organization

- Consolidated static files from `/public/` and `/static/` directories into a single `/static/` directory
- Removed duplicate CSS and JS files
- Updated settings to use a single static files location

### 3. Startup Scripts

- Fixed settings module paths in startup scripts
- Added proper environment variable settings
- Updated server commands for production deployment
- Removed redundant server startup script

### 4. Documentation

- Updated README.md with:
  - Clear project structure documentation
  - Setup instructions for development and production
  - Updated technology stack information
  - Better formatting and organization

## Benefits

1. **Simplified Project Structure**: Clearer organization makes it easier for developers to navigate the codebase
2. **Standardized Configuration**: Settings are now in a single location following Django best practices
3. **Reduced Redundancy**: Eliminated duplicate files and configurations
4. **Improved Maintainability**: Better documentation and standardized structure improves long-term maintenance
5. **Better Developer Experience**: Clearer startup processes and documentation

## Next Steps

1. Test the development server with the new configuration
2. Ensure all static files are properly served

...
```


### `./project_management/cloud-integration-roadmap.md`

```markdown
# Cloud Computing Integration Roadmap

**Date**: 2025-05-23
**Status**: Planning Phase

## How Cloud Integration Enhances the Freemium Model

### Integration with Pricing Tiers

| Tier | Local Resources | Cloud Access | Monthly Cloud Credits |
|------|----------------|--------------|---------------------|
| **Open Science** | 2 CPU cores | ❌ | $0 |
| **Researcher** | 4 CPU cores | ✅ Limited | $10 |
| **Team** | 8 CPU cores | ✅ Standard | $50/user |
| **Institution** | Custom | ✅ Unlimited | Custom |

### Quick Start Implementation (3 Months)

#### Month 1: Foundation
- [ ] Install SLURM on existing server
- [ ] Create job submission API
- [ ] Basic web interface
- [ ] User quota system

#### Month 2: AWS Integration
- [ ] AWS Batch setup
- [ ] S3 bucket per user
- [ ] Spot instance support
- [ ] Cost tracking

#### Month 3: Multi-Cloud
- [ ] Add Google Cloud
- [ ] Provider selection logic
- [ ] Unified billing
- [ ] Launch beta

### Revenue Impact

**Additional Revenue Streams:**
- Cloud compute markup: 15-20%
- Priority queue access: $5/job
- Dedicated instances: $100-500/month
- Data transfer: $0.10/GB

**Projected Revenue Increase:**
- Month 1-3: +$5K/month (setup phase)
- Month 4-6: +$20K/month (early adoption)
- Month 7-12: +$50K/month (full adoption)

### Technical Stack

...
```


### `./project_management/color-update-scitex-800-20250523.md`

```markdown
# SciTeX 800 Base Font Color Update

**Date:** 2025-05-23
**Summary:** Updated the entire application to use SciTeX 800 (#1a2332) as the base font color

## Changes Made

### 1. CSS Variable Updates
- Updated `/static/css/common/variables.css`:
  - Confirmed `--text-color` already set to `var(--scitex-color-01)` (SciTeX 800)
  - Added `--body-color: var(--scitex-color-01)` for consistency
  - Added `--bg-color: var(--white)` for background references

### 2. Bootstrap Override Enhancement
- Updated `/static/css/bootstrap-override.css`:
  - Added explicit overrides to ensure Bootstrap doesn't override SciTeX colors
  - Set body, form controls, and text classes to use `var(--text-color)` with `!important`

### 3. Product Pages Color Standardization
- Created `/static/css/products/products-common.css`:
  - Comprehensive CSS file for product pages using SciTeX color variables
  - Replaces hardcoded colors with semantic variables
  
- Updated product templates to use SciTeX color variables:
  - `/apps/cloud_app/templates/cloud_app/products/search.html`
  - `/apps/cloud_app/templates/cloud_app/products/doc.html`
  - `/apps/cloud_app/templates/cloud_app/products/engine.html`

### 4. Color Replacements
Replaced all hardcoded colors with SciTeX variables:
- `#1a2332` → `var(--scitex-color-01)` (SciTeX 800)
- `#34495e` → `var(--scitex-color-02)` (SciTeX 700)
- `#506b7a` → `var(--scitex-color-03)` (SciTeX 600)
- `#8fa4b0` → `var(--scitex-color-05)` (SciTeX 400)
- `#b5c7d1` → `var(--scitex-color-06)` (SciTeX 300)
- `#d4e1e8` → `var(--scitex-color-07)` (SciTeX 200)

## Result
- All text throughout the application now uses SciTeX 800 (#1a2332) as the base color
- Consistent color scheme maintained across all pages
- Better maintainability with centralized color variables
- Preserved semantic color usage (success, error, etc.)

## Verification
- Verified on landing page
- Verified on dashboard/login page
- All text elements properly display in SciTeX 800 color

...
```


### `./project_management/create_cache_table.py`

```python
#!/usr/bin/env python3
"""
Script to create cache table in production database.
Run this on production server to fix cache errors.
"""

import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

def main():
    """Create cache table for database cache."""
    print("Creating cache table...")
    
    try:
        execute_from_command_line(['manage.py', 'createcachetable'])
        print("✅ Cache table created successfully!")
    except Exception as e:
        print(f"❌ Error creating cache table: {e}")

if __name__ == "__main__":
    main()
...
```


### `./project_management/css-refactoring-plan.md`

```markdown
# CSS Refactoring Plan for SciTeX-Cloud

## Current Issues

Based on our analysis, the current CSS organization has several issues:

1. **Duplicate Files**: Multiple versions of the same CSS files exist across directories
2. **Inconsistent Structure**: Mix of CSS file locations, naming conventions, and import patterns
3. **Parallel Structures**: CSS is split between `/static/css/` and `/static/common/css/`
4. **Unclear Entry Points**: Multiple CSS entry files like `index.css`, `main.css`, etc.
5. **Mixed Naming Conventions**: Inconsistent file naming across the codebase

## Refactoring Goals

1. Create a single, clear CSS structure with no duplications
2. Establish consistent naming conventions
3. Set up a clean import hierarchy with one main entry point
4. Organize CSS in a logical, modular way
5. Separate core styles from app-specific styles
6. Ensure backward compatibility with current templates

## Proposed CSS Structure

```
/static/
  /css/
    index.css                  # Single entry point for all CSS
    /base/                     # Global base styles
      _variables.css           # Design tokens and colors
      _reset.css               # CSS reset
      _typography.css          # Typography
      _layout.css              # Layout utilities
      _global.css              # Global styles
    /components/               # Reusable UI components
      _header.css
      _footer.css
      _hero.css
      _features.css
      _cards.css
      _buttons.css
      _forms.css
      _dropdown.css
    /utilities/                # Utility classes
      _spacing.css             # Margin/padding utilities
      _accessibility.css       # Accessibility enhancements
      _darkmode.css            # Dark mode theme
    /pages/                    # Page-specific styles
      _landing.css
      _repository.css
      _design-system.css
```

...
```


### `./project_management/daily-development-summary-20250523.md`

```markdown
# Daily Development Summary - May 23, 2025

## Overview

Comprehensive platform enhancement and assessment session resulting in significant improvements to SciTeX Cloud's production readiness.

## Completed Tasks

### 1. System Requirements Documentation ✅
- Created `/docs/SYSTEM_REQUIREMENTS.md`
- Documented all component dependencies
- Clarified SciTeX-Engine needs Claude Code
- Clarified SciTeX-Viz needs Windows/SigmaPlot
- Outlined Apptainer containerization strategy

### 2. Product Pages Enhancement ✅
- Updated all product pages with system requirements
- Added platform compatibility information
- Included container availability details
- Added licensing information

### 3. Pricing Strategy Development ✅
- Created comprehensive freemium model
- 4 tiers: Open Science (Free), Researcher ($19), Team ($49), Institution (Custom)
- Balanced sustainability with open science promotion
- Clear feature comparison matrix

### 4. Landing Page Improvements ✅
- Added GitHub buttons to all product cards
- Proper styling with hover effects
- Direct repository links for transparency
- Enhanced visual hierarchy

### 5. Code Optimization ✅
- Removed console.log statements from production
- Fixed JavaScript error handling
- Added null checks for missing elements
- Improved code robustness

### 6. SEO Enhancements ✅
- Added Open Graph meta tags
- Added Twitter Card support
- Created robots.txt
- Created XML sitemap
- All images have alt attributes

### 7. Cloud Computing Proposal ✅
- Designed SLURM-like job scheduler
- Multi-cloud integration (AWS, GCP, Azure)
- Cost optimization with spot instances

...
```


### `./project_management/deployment-progress-20250106.md`

```markdown
# SciTeX Cloud Deployment Progress Report

**Date**: 2025-01-06  
**Status**: READY FOR DEPLOYMENT  
**Target**: scitex.ai (162.43.35.139)

## Completed Tasks ✅

### 1. Server Configuration Files
- **Nginx**: `config/nginx_confs/scitex_cloud_simple.conf`
  - Domain: scitex.ai, www.scitex.ai
  - SSL: `/etc/letsencrypt/live/scitex.ai/`
  - Static: `/home/ywatanabe/proj/SciTeX-Cloud/staticfiles/`

- **uWSGI**: `config/uwsgi_simple.ini`
  - Socket: `/home/ywatanabe/proj/SciTeX-Cloud/uwsgi.sock`
  - Workers: 4 processes, 2 threads each
  - Module: `config.wsgi:application`

### 2. Django Configuration
- **Production Settings**: Updated with:
  - Email: mail1030.onamae.ne.jp (port 465, SSL)
  - Secret key from environment
  - Allowed hosts: scitex.ai, www.scitex.ai, 162.43.35.139
  - Admin notifications configured

- **Environment Template**: `.env.production`
  - All required variables documented
  - Email credentials included
  - Database configuration template

### 3. Documentation
- **Deployment Instructions**: Step-by-step guide with rollback plan
- **Production Checklist**: Verification checklist for deployment
- **Requirements.txt**: All Python dependencies listed

## Migration Path

### From AIRight → SciTeX Cloud
| Component | Old (AIRight) | New (SciTeX Cloud) |
|-----------|--------------|-------------------|
| Domain | ai-write.app | scitex.ai |
| Project Path | /home/ywatanabe/proj/airight | /home/ywatanabe/proj/SciTeX-Cloud |
| Nginx Config | /etc/nginx/sites-enabled/airight.conf | Use scitex_cloud_simple.conf |
| Socket | airight/uwsgi.sock | SciTeX-Cloud/uwsgi.sock |

## Required Actions at onamae.com
1. **DNS A Records**:
   - scitex.ai → 162.43.35.139
   - www.scitex.ai → 162.43.35.139

...
```


### `./project_management/deployment-readiness-final-20250523.md`

```markdown
# Deployment Readiness - Final Check ✅

**Date**: 2025-05-23
**Status**: READY FOR DEPLOYMENT

## Final Checklist Results

### ✅ Code Quality
- [x] No console.log statements in production code
- [x] No TODO/FIXME comments in critical files
- [x] JavaScript error handling improved
- [x] All links tested and working

### ✅ Security
- [x] DEBUG = False in production settings
- [x] SECRET_KEY from environment variable
- [x] Security headers configured
- [x] HTTPS enforcement ready
- [x] JWT authentication implemented

### ✅ Documentation
- [x] System requirements documented
- [x] Deployment guide created
- [x] Security checklist prepared
- [x] Environment variables template (.env.example)
- [x] API endpoints documented

### ✅ Dependencies
- [x] requirements.txt created with all dependencies
- [x] Version pinning for stability
- [x] Security tools included (django-axes, CSP)

### ✅ Database
- [x] 21 migration files ready
- [x] PostgreSQL configuration for production
- [x] Database credentials from environment

### ✅ Static Assets
- [x] All images have alt attributes
- [x] CSS optimized (removed console.logs)
- [x] JavaScript error handling fixed
- [x] Favicon configured
- [x] Static file serving configured

### ✅ SEO & Marketing
- [x] Open Graph meta tags
- [x] Twitter Card support
- [x] robots.txt created
- [x] sitemap.xml created
- [x] Proper heading hierarchy

...
```


### `./project_management/deployment-success-20250106.md`

```markdown
# SciTeX-Cloud Production Deployment Success 🎉

**Date**: 2025-01-06  
**Status**: ✅ SUCCESSFULLY DEPLOYED  
**Production URL**: https://scitex.ai

## Deployment Summary

### Infrastructure Stack
- **Web Server**: Nginx with SSL/TLS
- **Application Server**: Gunicorn (3 workers)
- **Framework**: Django 4.2.11
- **Database**: SQLite (development mode)
- **Process Manager**: systemd

### Key Achievements
1. **Migrated from AIRight to SciTeX-Cloud**
   - Replaced ai-write.app with scitex.ai
   - Updated all server configurations
   - Zero downtime migration

2. **SSL Certificate**
   - Let's Encrypt certificate installed
   - Auto-renewal configured
   - HTTPS enforced with redirect

3. **Service Configuration**
   - Systemd service: `scitex.service`
   - Auto-start on boot enabled
   - Process monitoring active

4. **DNS Configuration**
   - A record: scitex.ai → 162.43.35.139
   - MX record: mail1030.onamae.ne.jp
   - SPF record configured

## File Locations

### Configuration Files
- Nginx: `/etc/nginx/sites-available/scitex-https.conf`
- Systemd: `/etc/systemd/system/scitex.service`
- Django: `/home/ywatanabe/proj/SciTeX-Cloud/config/settings/production.py`

### Logs
- Application: `/home/ywatanabe/proj/SciTeX-Cloud/logs/`
- Nginx: `/var/log/nginx/`
- Gunicorn: Check with `sudo journalctl -u scitex`

## Maintenance Commands


...
```


### `./project_management/design-system-enhancement-20250522.md`

```markdown
# Design System Enhancement Report
**Date:** May 22, 2025
**Author:** Claude (with ywatanabe)

## Summary
This document outlines the enhancements made to the SciTeX Cloud design system, including the creation of a comprehensive color palette with transitioning color shades and improvements to the project's UI consistency.

## Changes Implemented

### 1. Color System Enhancement
- Created a complete color system with transitioning shades (100-900) for each color
- Implemented 7 shade gradients for semantic colors
- Added detailed color documentation in CSS variables
- Enhanced the design system to provide more flexibility for UI development

### 2. New Design System Page
- Created a comprehensive design system showcase at `/design/`
- Added visual display of all color transitions 
- Documented components with their color usage
- Included hex codes and variable names for developer reference

### 3. UI Component Improvements
- Enhanced button styles with better hover states
- Improved dropdown menus with subtle animations
- Updated header and footer with the new color system
- Added new border radius and shadow options

### 4. Code Structure Improvements
- Fixed duplicate URL namespace issue (changed from 'cloud' to 'cloud_app' and 'cloud_root')
- Updated template URL references to use correct namespaces
- Followed version control guidelines with proper branching

### 5. Style Guidelines
- Used consistent naming conventions for CSS variables
- Added clear comments for color sections
- Followed semantic naming principles
- Maintained backward compatibility

## Testing Performed
- Visual inspection of all components in the design system page
- Verified responsive behavior on different screen sizes
- Confirmed URL namespace fix by running the development server
- Tested navigation links to ensure proper routing

## Next Steps
1. Consider updating other components to utilize the new color system
2. Add dark mode variants for the transitioning color palette
3. Create more examples in the design system for complex UI patterns
4. Document the design system usage guidelines for developers


...
```


### `./project_management/development-session-20250523-final.md`

```markdown
# SciTeX Cloud Development Session Summary - 2025-05-23

## Overview
This session focused on aligning the Django application with the SciTeX workflow and monetization strategy while fixing UI issues and implementing document management features.

## Completed Tasks

### 1. SciTeX Workflow Analysis and Feedback
- **Analyzed proposed workflow**: User → Project → SciTeX Engine orchestration → Archive
- **Provided comprehensive feedback** on workflow strengths and improvements
- **Created documentation**: `/docs/workflow-feedback.md`
- **Key recommendations**:
  - Add project templates for different research types
  - Implement collaboration framework
  - Add quality assurance pipeline
  - Enhance knowledge gap analysis

### 2. Monetization Strategy Analysis
- **Evaluated proposed freemium model** with detailed analysis
- **Created comprehensive monetization plan**: `/docs/monetization-analysis.md`
- **Refined pricing tiers**:
  - Free tier: 5GB, 2 cores, 1 project
  - Premium A ($49/mo): 100GB, 8 cores, 5 projects
  - Premium B ($99/mo): 500GB, 16 cores, unlimited projects
  - Institutional licensing: $10-50K/year
- **Revenue projections**: $100K (Year 1) → $800K (Year 3)

### 3. Fixed Document Management UI
- **Issue**: Input fields not visible due to undefined CSS variables
- **Solution**: Updated document_list.html to use SciTeX color variables
- **Fixed CSS issues**:
  - Replaced `var(--color-*)` with `var(--scitex-color-*)`
  - Added explicit styles for form inputs
  - Fixed badge colors for new document types

### 4. Enhanced Document Model for SciTeX Workflow
- **Updated document types** to align with research workflow:
  - Hypothesis
  - Literature Review
  - Methodology
  - Results
  - Manuscript
  - Revision
  - General Note
  - Draft
- **Enhanced Project model** with SciTeX integration fields:
  - Required hypotheses field
  - GitHub/GitLab URL support
  - SciTeX Engine status tracking (search, analysis, figures, manuscript)
  - Knowledge gap identification field

...
```


### `./project_management/development-summary-20250523.md`

```markdown
# SciTeX Cloud Development Summary - 2025-05-23

## Completed Tasks

### 1. UI Enhancement - Header Margin
- **Issue:** User icon and username were too close together in the header
- **Solution:** Added Bootstrap `me-2` class to add margin between icon and username
- **Result:** Better visual spacing in the header dropdown toggle

### 2. Base Font Color Update to SciTeX 800
- **Issue:** Ensure consistent use of SciTeX 800 (#1a2332) as base font color
- **Actions Taken:**
  - Updated CSS variables to define `--body-color` as SciTeX 800
  - Enhanced bootstrap-override.css to prevent Bootstrap from overriding colors
  - Created products-common.css for standardized product page styling
  - Replaced all hardcoded colors in templates with SciTeX color variables
- **Result:** Consistent SciTeX 800 color throughout the application

### 3. URL Configuration Fixes
- **Fixed /dashboard/ redirect:**
  - Added RedirectView from /dashboard/ to /core/dashboard/
  - Prevents 404 errors when users access /dashboard/
  
- **Fixed user stats API endpoint:**
  - Updated dashboard.js to use correct API path (/core/api/v1/stats/)
  - Resolved 404 error for user statistics loading

### 4. Product Pages Configuration
- **Issue:** Product page URLs returning 404 errors
- **Solution:**
  - Added URL patterns for all product pages in cloud_app/urls.py
  - Created view functions for each product page
  - Fixed template syntax errors (static tag usage)
- **Result:** All product pages now accessible at /products/{search,engine,code,doc,viz,cloud}/

### 5. Navigation Testing
- **Verified all navigation links are functional:**
  - Header dropdown menus work correctly
  - Product dropdown shows all items with proper spacing
  - All product links navigate to correct pages
  - User dropdown shows all options clearly

## Technical Improvements

1. **Better URL Organization:** Clear separation between core app and product pages
2. **Consistent Styling:** Centralized color system using CSS variables
3. **Improved User Experience:** Fixed broken links and navigation issues
4. **Code Quality:** Proper Django template syntax and static file handling

## Server Status

...
```


### `./project_management/django-dev-session-20250523.md`

```markdown
# Django Development Session - 2025-05-23

## Completed Tasks

### 1. Fixed Missing Static Image
- **Issue:** Missing search-semantic.svg causing 404 error
- **Solution:** Created a professional SVG visualization for semantic search concept
- **File:** `/static/images/search-semantic.svg`
- **Result:** Product search page now displays properly with visual element

### 2. Implemented Comprehensive User Profile System

#### Profile Template
- Created full-featured profile page at `/apps/core_app/templates/core_app/profile.html`
- Features implemented:
  - Profile information display with edit mode
  - User statistics (documents, projects, collaborations)
  - Privacy settings with toggles
  - Account settings section
  - Professional profile avatar with initials
  - Responsive layout with Bootstrap

#### Model Enhancements
- Added new fields to UserProfile model:
  - `is_public` - Make profile public toggle
  - `allow_messages` - Allow messages from other users
  - Properties for statistics (total_documents, total_projects, total_collaborations)

#### API Functionality
- Enhanced UserProfileAPIView with:
  - POST method for full profile updates
  - PATCH method for privacy settings updates
  - Support for all profile fields including academic information
  - Validation for ORCID format
  - Proper handling of boolean fields

#### Database Updates
- Created and applied migration: `0004_userprofile_allow_messages_userprofile_is_public`
- Successfully migrated database schema

## Technical Details

### Frontend Features
- Interactive edit mode toggle
- AJAX-based form submission without page reload
- Real-time privacy settings updates
- Success notifications
- Proper CSRF token handling
- Responsive design using SciTeX color scheme


...
```


### `./project_management/django-structure-implementation-plan.md`

```markdown
# Django Structure Implementation Plan

## Current Status

The feature branch `feature/legal-and-contact-pages` has successfully implemented:
- Base HTML template with header and footer
- Contact page with form
- Privacy Policy page
- Terms of Use page
- URL routing and view functions

## Structure Implementation Steps

### 1. Create Django Apps Directory Structure

```bash
# Create apps directory
mkdir -p /home/ywatanabe/proj/scitex-web/apps/about_app
mkdir -p /home/ywatanabe/proj/scitex-web/apps/core_app

# Initialize Python packages
touch /home/ywatanabe/proj/scitex-web/apps/__init__.py
touch /home/ywatanabe/proj/scitex-web/apps/about_app/__init__.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/__init__.py
```

### 2. Move Templates to App-Specific Directories

```bash
# Create template directories
mkdir -p /home/ywatanabe/proj/scitex-web/apps/about_app/templates/about_app
mkdir -p /home/ywatanabe/proj/scitex-web/apps/core_app/templates/core_app

# Move legal templates to about_app
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/contact.html /home/ywatanabe/proj/scitex-web/apps/about_app/templates/about_app/
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/privacy_policy.html /home/ywatanabe/proj/scitex-web/apps/about_app/templates/about_app/
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/terms_of_use.html /home/ywatanabe/proj/scitex-web/apps/about_app/templates/about_app/

# Move core templates to core_app
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/base.html /home/ywatanabe/proj/scitex-web/apps/core_app/templates/core_app/
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/index.html /home/ywatanabe/proj/scitex-web/apps/core_app/templates/core_app/
cp /home/ywatanabe/proj/scitex-web/src/scitex_web/templates/scitex_web/landing.html /home/ywatanabe/proj/scitex-web/apps/core_app/templates/core_app/
```

### 3. Create App-Specific Files

```bash
# Create about_app files
touch /home/ywatanabe/proj/scitex-web/apps/about_app/admin.py
touch /home/ywatanabe/proj/scitex-web/apps/about_app/apps.py
```

...
```


### `./project_management/feature_requests/feature-request-cloud-computing-integration.md`

```markdown
# Feature Request: Cloud Computing Integration with Job Scheduler

**Date**: 2025-05-23
**Priority**: High
**Category**: Infrastructure & Scalability

## Summary

Implement a job scheduling system (like SLURM) integrated with major cloud computing platforms (AWS, Google Cloud, Azure) to provide scalable computational resources for SciTeX users.

## Current Situation

- Users are limited to local server resources
- No job queuing or resource management system
- Cannot scale for computationally intensive tasks
- No integration with cloud storage services

## Proposed Solution

### 1. Job Scheduling System

Implement a SLURM-like scheduler with Django integration:

```python
# apps/compute_app/models.py
class ComputeJob(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    job_type = models.CharField(max_length=50)  # 'engine', 'code', 'viz'
    status = models.CharField(max_length=20)  # 'queued', 'running', 'completed', 'failed'
    priority = models.IntegerField(default=0)
    
    # Resource requirements
    cpu_cores = models.IntegerField(default=1)
    memory_gb = models.IntegerField(default=4)
    gpu_type = models.CharField(max_length=50, blank=True)
    estimated_hours = models.FloatField(default=1.0)
    
    # Cloud provider
    provider = models.CharField(max_length=20)  # 'local', 'aws', 'gcp', 'azure'
    instance_type = models.CharField(max_length=50, blank=True)
    
    # Job details
    script_path = models.TextField()
    input_data = models.JSONField()
    output_path = models.TextField()
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True)
    completed_at = models.DateTimeField(null=True)
```

...
```


### `./project_management/feature_requests/feature-request-code-enhanced-page.md`

```markdown

# Feature Request: Enhanced Code Page with Sample Features

## Summary
Enhance the Code page with a proper hero section, sample features, and professional presentation for reproducible scientific code organization.

## Feature Request Details

### Problem Statement
- **Issue**: Current Code page only shows "Coming Soon" message
- **Impact**: Users don't understand Code capabilities or see examples  
- **Goal**: Professional showcase of scientific code organization features

### Scope
- **Hero Section**: Professional hero with "SciTeX Code" and "Reproducible, standardized scientific code organization using python scitex package"
- **Sample Features**: Add sample code organization with links (similar to previous implementation)
- **Coming Soon Status**: Maintain "Coming Soon" indication while showing preview capabilities

### Implementation Guidelines
1. **Hero Section**:
   - Title: "SciTeX Code" (keeping SciTeX here as it's the proper module name)
   - Subtitle: "Reproducible, standardized scientific code organization using python scitex package"
   - Use appropriate hero gradient styling

2. **Sample Features**:
   - Add sample scientific code organization examples
   - Include links to examples or demos
   - Showcase typical scientific programming capabilities

3. **Coming Soon Badge**:
   - Maintain "Coming Soon" status
   - Position appropriately with sample content

## Technical Implementation

### Priority: Medium
This improves user understanding of Code capabilities and provides preview of features.

### Areas to Implement:
1. **Code Index Page**:
   - Enhanced hero section with proper branding
   - Sample feature gallery
   - Professional presentation

2. **Sample Content**:
   - Scientific code organization examples
   - SCITEX package integration demonstrations
   - Interactive elements or links where appropriate

3. **Design Consistency**:

...
```


### `./project_management/feature_requests/feature-request-common-css.md`

```markdown
# Feature Request: Common CSS

## Description
Create a modular, reusable CSS architecture for the SciTeX Web application. This should include:

1. A CSS reset/normalize file
2. A common variables file (colors, fonts, spacing)
3. Utility classes for common styling patterns
4. Component-specific styles organized in separate files
5. A build process to combine these into a single minified file

## Justification
- Improved maintainability through modular organization
- Consistent styling across the application
- Reduced duplication of CSS code
- Better performance through minification
- Support for future growth of the application

## Acceptance Criteria
- [ ] Create a `common` directory within `/public/css/`
- [ ] Implement a CSS reset/normalize file
- [ ] Extract variables from existing CSS into a separate file
- [ ] Create utility classes (spacing, typography, colors, etc.)
- [ ] Break down existing CSS into component files
- [ ] Ensure compatibility with existing HTML
- [ ] Document usage of common CSS components

## Progress
- [x] Create feature branch (feature/common-css)
- [x] Set up CSS directory structure
  - Created `/public/css/common` for reusable modules
  - Created `/public/css/components` for component-specific styles
- [x] Extract variables from existing CSS
  - Created `/public/css/common/variables.css` with comprehensive variables
- [x] Create CSS reset/normalize
  - Created `/public/css/common/reset.css`
- [x] Create utility classes
  - Created layout utilities in `/public/css/common/layout.css`
  - Created typography utilities in `/public/css/common/typography.css`
  - Created button styles in `/public/css/common/buttons.css`
  - Created form styles in `/public/css/common/forms.css`
  - Created card styles in `/public/css/common/cards.css`
- [x] Create component CSS files
  - Created header styles in `/public/css/components/header.css`
  - Created footer styles in `/public/css/components/footer.css`
  - Created hero styles in `/public/css/components/hero.css`
  - Created features styles in `/public/css/components/features.css`
- [x] Update build process
  - Created `/public/css/index.css` to import all modules
  - Updated HTML to use the new CSS file

...
```


### `./project_management/feature_requests/feature-request-concept-pages.md`

```markdown
# Feature Request: SciTeX Concept and Vision Pages

## Summary
Create engaging, informative pages that communicate the SciTeX ecosystem's purpose, philosophy, and roadmap to build a strong open science community.

## Request
Add dedicated pages explaining the SciTeX concept, vision, and upcoming features to the web interface with compelling visuals and clear calls to action for community participation.

## Justification
As we embrace an open approach prioritizing scientific advancement over immediate financial returns, clearly communicating our vision and roadmap becomes essential for:

1. Attracting potential collaborators and contributors from diverse backgrounds
2. Setting appropriate expectations for early adopters and research partners
3. Building a vibrant community around shared scientific values and open research principles
4. Establishing SciTeX as a comprehensive scientific research ecosystem rather than just a collection of tools
5. Creating transparency and trust within the scientific community

## Implementation Details

### 1. Concept Explanation Page
Content to include:
- Origins of SciTeX and its name
- The overall ecosystem architecture (Cloud, Code, Doc, Engine, Viz)
- How components interact to create an end-to-end research workflow
- Design philosophy and scientific principles
- Open science commitment

Design elements:
- Interactive ecosystem diagram using Mermaid.js for component relationships
- Animated workflow visualizations showing how components interact in research processes
- Clear, accessible language for both technical and non-technical audiences
- Examples of workflows enabled by the integrated ecosystem
- Code snippets demonstrating integration points between components
- "Try It" interactive elements for simple demonstrations of core concepts

### 2. Vision Page
Content to include:
- Long-term aspirations for SciTeX in advancing scientific research
- How SciTeX addresses current challenges in research workflows
- Open source strategy and community building approach
- Contribution pathways for different stakeholders (researchers, developers, institutions)
- Recognition system for contributors
- Charity initiative - explaining how a portion of any future revenue will support scientific education and research in underserved communities
- Fundraising approach - transparent explanation of how SciTeX seeks funding to sustain development while maintaining scientific integrity and independence

Design elements:
- Timeline visualization for platform evolution
- Testimonials/use cases from early adopters
- Clear articulation of core values
- Impact measurement for charitable initiatives

...
```


### `./project_management/feature_requests/feature-request-default-project-structure-enhancements.md`

```markdown

# Feature Request: Default Project Structure Enhancements

## Summary
Enhance project creation with standardized default structure, copy functionality, directory uploads, and GitHub sync fixes.

## Feature Request Details

### 1. Default Directory Structure
- **Source Template**: Use `~/proj/scitex-cloud/docs/to_claude/examples/example-python-project-scitex/` as the standard template
- **Implementation**: When no projects exist yet, automatically copy this project structure
- **Benefit**: Provides users with immediate working example following SCITEX framework

### 2. Copy Project Functionality in Dashboard
- **Requirement**: Implement copy project button/functionality directly in the dashboard interface
- **Location**: Dashboard project cards should have "Copy Project" action
- **Functionality**: Allow users to duplicate existing projects with their structure and files
- **Use Case**: Users can create variations of successful projects

### 3. Directory Upload Functionality
- **Current State**: Only file upload is available
- **Enhancement**: Add ability to upload entire directories/folders
- **Implementation**: Support drag-and-drop or browse for folder uploads
- **Benefit**: Easier migration of existing project structures

### 4. GitHub Sync Issues
- **Problem**: GitHub sync functionality is not working properly
- **Investigation Needed**: Determine root cause of GitHub integration failures
- **Fix Required**: Restore proper GitHub synchronization functionality

## Technical Implementation

### Priority: High
These features are essential for proper project management and user workflow.

### Implementation Areas:

#### 1. Default Project Structure
- **Files to Modify**:
  - `apps/core_app/views.py` (project creation logic)
  - `apps/core_app/directory_manager.py` (template copying)
  - Dashboard templates

- **Implementation**:
  - Create function to copy example project structure
  - Integrate with project creation workflow
  - Ensure proper file permissions and ownership

#### 2. Dashboard Copy Project
- **Files to Modify**:

...
```


### `./project_management/feature_requests/feature-request-fundraising-page.md`

```markdown
# Feature Request: SciTeX Open Research Sustainability Initiative

## Summary
Create a transparent, ethically-grounded funding approach that supports SciTeX's open science mission while ensuring long-term sustainability and scientific independence.

## Status: ✅ IMPLEMENTED

## Request
Develop a comprehensive sustainability page that clearly communicates SciTeX's funding philosophy, current support status, and opportunities for contribution while emphasizing our commitment to scientific integrity and open access principles.

## Justification
As an open science initiative prioritizing scientific advancement over immediate commercial returns, a transparent approach to sustainability is essential for:

1. Ensuring sustainable development and operations
2. Maintaining transparency with the scientific community
3. Building trust with potential donors, grantors, and supporters
4. Balancing open access with financial sustainability
5. Supporting charitable initiatives for scientific advancement in underserved communities

## Implementation Details

### 1. Open Research Sustainability Philosophy
Content to include:
- Core principles guiding SciTeX's sustainable development approach
- Commitment to maintaining scientific integrity and independence
- Balance between open access and long-term sustainability
- Explanation of how support directly accelerates scientific advancement
- Scientific governance model that protects research integrity
- Mermaid.js diagram visualizing the flow of resources and scientific value in the ecosystem

### 2. Transparent Resource Dashboard
Content to include:
- Interactive visualization of current support and resource allocation
- Source breakdown with ethical filtering (grants, donations, sponsorships, services)
- Progress toward sustainability milestones
- Operating cost transparency with detailed breakdowns
- Development achievements linked to community support
- Real-time updates on resource utilization
- Community-driven prioritization system for resource allocation

### 3. Support Options
Content to include:
- Individual donation options (one-time and recurring)
- Institutional sponsorship tiers and benefits
- Grant partnership opportunities
- In-kind contribution possibilities
- Directed funding for specific features or initiatives
- Corporate sponsorship program with clear ethical guidelines

### 4. Impact Reporting

...
```


### `./project_management/feature_requests/feature-request-github-integration-enhancement.md`

```markdown
# Feature Request: Enhanced GitHub Integration

## Summary
Enhanced GitHub connectivity for seamless version control integration within the SciTeX Cloud platform's file-centric dashboard.

## Current Status
- Basic GitHub sync functionality exists with manual commands
- Repository initialization and syncing available via project settings
- Command-line style GitHub operations supported

## Requested Enhancements

### 1. **One-Click GitHub Integration**
- **GitHub Connect Button**: Direct connection from project header
- **Repository Creation**: Create new GitHub repositories from within SciTeX
- **Automatic Authentication**: OAuth-based GitHub authentication flow
- **Repository Linking**: Link existing GitHub repositories to projects

### 2. **Visual Git Status Integration**
- **File Status Indicators**: Show git status (modified, untracked, staged) in file tree
- **Branch Visualization**: Display current branch in project header
- **Commit History**: Inline commit history for files in preview panel
- **Diff Visualization**: Side-by-side diff view for modified files

### 3. **Streamlined Git Operations**
- **Quick Actions**: Stage, unstage, commit buttons in file context menus
- **Commit Dialog**: Rich commit interface with message templates
- **Push/Pull Indicators**: Visual indicators for sync status
- **Branch Management**: Create, switch, merge branches from UI

### 4. **Collaborative Features**
- **Pull Request Integration**: View and create PRs from within SciTeX
- **Issue Tracking**: Link research tasks to GitHub issues
- **Contributor Activity**: Show team member contributions in dashboard
- **Code Review**: Inline commenting and review capabilities

### 5. **Research-Specific Features**
- **Research Templates**: Pre-configured .gitignore for scientific projects
- **Data Versioning**: Special handling for large data files (LFS integration)
- **Publication Releases**: Tag and release research milestones
- **Citation Integration**: Automatic DOI and citation generation for releases

## Technical Implementation

### Frontend Components
```javascript
// GitHub Integration Widget
<GitHubWidget 
  projectId={project.id}
  repository={project.github_url}
```

...
```


### `./project_management/feature_requests/feature-request-landing-page.md`

```markdown
# Feature Request: Landing Page

## Description
Create a dedicated landing page for SciTeX Web that effectively communicates the platform's value proposition, features, and benefits to researchers. The landing page should be visually appealing, informative, and optimized for conversion.

## Justification
- First impression is critical for user acquisition and retention
- Need to clearly communicate SciTeX's value proposition and features
- Current homepage lacks targeted content for different user segments
- A well-designed landing page will improve conversion rates and user engagement

## Acceptance Criteria
- [ ] Modern, responsive design following our common CSS architecture
- [ ] Clear value proposition and headline above the fold
- [ ] Featured sections on all SciTeX components (Cloud, Code, Doc, Engine, Viz)
- [ ] Benefits section highlighting advantages for researchers
- [ ] Testimonials/use cases section
- [ ] Call-to-action buttons strategically placed throughout the page
- [ ] Pricing tier comparison section
- [ ] FAQ section addressing common questions
- [ ] Integration with analytics to track user behavior
- [ ] SEO optimization

## Progress
- [x] Create feature branch (feature/landing-page)
- [x] Design wireframe/mockup
  - Created comprehensive landing page HTML structure with all required sections
- [x] Implement HTML structure
  - Created `/src/scitex_web/templates/scitex_web/landing.html`
  - Included all required sections (hero, products, benefits, features, testimonials, pricing, FAQ, CTA)
- [x] Apply styling using common CSS
  - Created `/public/css/landing.css` using our common CSS architecture
  - Implemented responsive design for all sections
- [x] Add responsive behavior
  - Added mobile-specific styles for all screen sizes
  - Implemented collapsible mobile navigation
- [x] Integrate with Django templates
  - Updated `/src/scitex_web/views.py` to add landing page view
  - Updated `/src/scitex_web/urls.py` to make landing the default route
- [x] Add interactive elements
  - Created `/public/js/landing.js` for interactive components
  - Implemented smooth scrolling, pricing toggle, FAQ accordion
- [ ] Add analytics tracking
- [ ] Test across browsers and devices
- [ ] Optimize performance
- [ ] Merge feature branch to develop

...
```


### `./project_management/feature_requests/feature-request-legal-and-contact-pages.md`

```markdown
# Feature Request: Legal and Contact Pages

## Description
Create essential pages for the SciTeX Web platform:
1. Contact page with a contact form and company information
2. Privacy Policy page outlining data handling practices
3. Terms of Use page detailing usage terms and conditions

These pages are necessary for legal compliance and providing users with essential information about the platform.

## Justification
- Legal requirement for privacy policy and terms of use for web applications
- Necessary for building user trust and transparency
- Provides users with a clear way to contact the company
- Protects both users and the company by clearly defining rights and responsibilities

## Acceptance Criteria
- [ ] Contact page with:
  - [ ] Contact form with name, email, subject, and message fields
  - [ ] Form validation
  - [ ] Company contact information (email, address)
  - [ ] Links to social media profiles
  - [ ] Map showing company location (optional)

- [ ] Privacy Policy page with:
  - [ ] Clear explanation of data collection practices
  - [ ] Information on cookies and tracking
  - [ ] Third-party service providers
  - [ ] User rights regarding their data
  - [ ] Contact information for privacy concerns
  - [ ] Last updated date

- [ ] Terms of Use page with:
  - [ ] Clear explanation of acceptable use
  - [ ] User responsibilities
  - [ ] Intellectual property rights
  - [ ] Limitations of liability
  - [ ] Dispute resolution process
  - [ ] Modification terms
  - [ ] Last updated date

- [ ] All pages should:
  - [ ] Be responsive and accessible
  - [ ] Use consistent styling with the rest of the site
  - [ ] Be linked in the site footer
  - [ ] Have clear, readable content formatted for easy scanning

## Progress
- [x] Create feature branch (feature/legal-and-contact-pages)
- [x] Design and implement Contact page

...
```


### `./project_management/feature_requests/feature-request-local-html-server.md`

```markdown
# Feature Request: Local HTML Development Server

## Description
Create a local HTML development server for the SciTeX Web project, inspired by the successful implementations in ~/proj/ai_ielts and ~/proj/airight projects. This server should provide rapid development workflow with hot reload, static file serving, and easy setup for local development.

## Justification
- **Faster Development**: Immediate feedback during development without complex setup
- **Consistency**: Match development patterns used successfully in ai_ielts and airight projects
- **Testing**: Easy local testing of HTML, CSS, and JavaScript changes
- **Collaboration**: Simplified onboarding for new developers
- **Standards**: Follow Django best practices established in existing projects

## Reference Implementation Analysis

### AI IELTS Project Approach
- **Framework**: Pure Django with `python manage.py runserver`
- **Static Files**: App-specific static directories with automatic serving
- **Hot Reload**: Built-in Django development server auto-reload
- **Environment**: Python virtual environment with comprehensive requirements.txt

### AIRight Project Approach  
- **Framework**: Django with enhanced development tools
- **Hot Reload**: `django-browser-reload` for automatic browser refresh
- **Scripts**: Custom start/stop scripts (`./scripts/start`)
- **Static Organization**: Structured CSS/JS with component-based architecture
- **Dependencies**: Minimal Node.js + comprehensive Python stack

## Acceptance Criteria

### 1. Development Server Setup
- [ ] Create Django development server configuration
- [ ] Implement hot reload functionality for templates and static files
- [ ] Set up automatic browser refresh on file changes
- [ ] Configure proper static file serving for development

### 2. Project Structure
- [ ] Organize static files following Django best practices:
  ```
  static/
  ├── css/
  │   ├── common/      # Base styles, variables, reset
  │   ├── components/  # Reusable UI components
  │   └── pages/       # Page-specific styles
  ├── js/
  │   ├── common/      # Shared JavaScript utilities
  │   ├── components/  # Component-specific JS
  │   └── pages/       # Page-specific JavaScript
  └── images/          # Static images and assets
  ```


...
```


### `./project_management/feature_requests/feature-request-modularity-messaging.md`

```markdown
# Feature Request: Highlight Modularity and Customization in Messaging

**Date**: 2025-05-23
**Priority**: High
**Category**: Messaging & Marketing

## Summary

Emphasize SciTeX's modular architecture and unlimited customization potential as core differentiators in all messaging and marketing materials.

## Key Concepts to Highlight

### 1. Separation of Concerns (SoC)
Each module handles one specific aspect of the research workflow:
- **Studio**: Development environment
- **Manuscript**: Document preparation
- **Compute**: Data processing
- **Figures**: Visualization
- **Discover**: Literature search
- **Cloud**: Integration layer

### 2. True Modularity Benefits
- **Use only what you need**: Pick and choose modules
- **Replace any component**: Swap in your preferred tools
- **Extend functionality**: Build on top of existing modules
- **Custom workflows**: Combine modules your way

### 3. Open Source Advantage
- **Full transparency**: Inspect and modify any code
- **Community-driven**: Contribute improvements
- **No vendor lock-in**: Fork and self-host if needed
- **Unlimited customization**: Adapt to any research need

## Proposed Messaging Updates

### Landing Page Hero Section

**Current:**
"SciTeX integrates six powerful research modules..."

**Proposed:**
"SciTeX: Modular, Open Source, Infinitely Customizable

Build your perfect research environment with six independent modules that work seamlessly together—or standalone. Every component is fully open source, giving you unlimited freedom to customize, extend, or replace any part of the system."

### New Section: "Modular by Design"

```html
<section class="modularity-section">
  <h2>Modular by Design, Powerful by Nature</h2>
```

...
```


### `./project_management/feature_requests/feature-request-module-card-formatting.md`

```markdown
# Feature Request: Left-Align Module Card Descriptions with Bullet Points

**Date**: 2025-05-23
**Priority**: High
**Category**: UI/UX Improvement

## Summary

Update the module card descriptions on the landing page to use left-aligned bullet points instead of centered text with line breaks. This will improve readability and create a cleaner, more professional appearance.

## Current Issue

The current module descriptions use `<br>` tags and center alignment:
```html
<p>
  Powered by Claude Code agent<br>
  Sets of guidelines and commands<br>
  Human-in-the-loop system on Emacs
</p>
```

This creates:
- Difficult to scan text
- Inconsistent line lengths
- Less professional appearance
- Poor alignment on mobile devices

## Proposed Solution

### HTML Structure Update

Replace paragraph text with unordered lists:

```html
<p>
  AI-powered research environment<br>
  Intelligent coding assistance<br>
  Seamless Emacs integration
</p>

<ul class="module-features">
  <li>AI-powered research environment</li>
  <li>Intelligent coding assistance</li>
  <li>Seamless Emacs integration</li>
</ul>
```

### CSS Styling

```css
```

...
```


### `./project_management/feature_requests/feature-request-module-ordering-and-coming-soon-status.md`

```markdown

# Feature Request: Module Ordering and Coming Soon Status

## Summary
Standardize module ordering across the website and implement "Coming Soon" status for modules that are not yet available.

## Feature Request Details

### Module Ordering
- **Requirement**: All modules should be displayed in the natural scientific project workflow order:
  1. **Scholar** (Literature discovery)
  2. **Viz** (Data visualization) 
  3. **Code** (Analysis and computation)
  4. **Writer** (Manuscript preparation)

- **Scope**: This ordering should be consistent across:
  - Navigation menus
  - Dashboard module cards
  - Landing page sections
  - Footer links
  - Any other module listings

### Coming Soon Status
- **Requirement**: Viz and Code modules should be explicitly marked as "Coming Soon"
- **Implementation**: Clear visual indicators that these modules are in development
- **User Experience**: Users should understand these features are planned but not yet available

### Hero Section Consistency
- **Requirement**: All pages should have hero sections matching the landing page design
- **Exception**: Dashboard page should maintain its current design
- **Scope**: Scholar, Writer, Viz, and Code module pages

## Technical Implementation

### Priority: High
This affects user experience and navigation consistency across the platform.

### Implementation Areas:
1. **Navigation Components**:
   - Update main navigation order
   - Update footer module links
   - Update mobile menu order

2. **Dashboard**:
   - Reorder module cards
   - Add "Coming Soon" badges to Viz and Code cards
   - Ensure consistent ordering in statistics

3. **Landing Page**:
   - Verify module section ordering

...
```


### `./project_management/feature_requests/feature-request-naming-branding-strategy.md`

```markdown
# Feature Request: Naming and Branding Strategy for SciTeX

**Date**: 2025-05-23
**Priority**: High
**Category**: Branding & Identity

## Executive Summary

Develop a cohesive naming and branding strategy for the SciTeX ecosystem that:
- Replaces "products" with research-focused terminology
- Creates consistent naming across all components
- Establishes clear branding guidelines
- Ensures namespace availability across platforms

## Current Situation

### Existing Assets
- **Domain**: scitex.ai ✓
- **Email addresses**: admin@, support@, ywatanabe@, YusukeWatanabe@ ✓
- **GitHub Organization**: https://github.com/SciTeX-AI ✓
- **Twitter/X**: @SciTeX (display name), @SciTeX_AI (handle) ✓

### Current Component Names (Need Revision)
- SciTeX-Engine → Needs clearer name
- SciTeX-Doc → Too generic
- SciTeX-Code → Unclear purpose
- SciTeX-Viz → Good but could be clearer
- SciTeX-Search → Clear and good
- SciTeX-Cloud → Clear and good

## Proposed Solutions

### 1. Replace "Products" Terminology

Instead of "Products," use research-focused terms:

| Current | Proposed Options | Recommendation |
|---------|------------------|----------------|
| Products | Tools, Modules, Components | **Modules** |
| Product Page | Module Overview, Tool Details | **Module Overview** |
| Our Products | Research Modules, SciTeX Suite | **Research Modules** |
| Product Features | Module Capabilities | **Module Capabilities** |

**Rationale**: "Modules" emphasizes the modular, integrated nature of the ecosystem while avoiding commercial connotations.

### 2. Improved Component Naming

#### SciTeX-Engine → **SciTeX Studio**
- **Current**: `~/.emacs.d/lisp/emacs-claude-code`
- **Why**: "Studio" conveys an integrated research environment

...
```


### `./project_management/feature_requests/feature-request-reflect-products.md`

```markdown

Update products pages  to reflect the actual contents implemented in the directories shown below:
- Product pages:
  - http://172.19.33.56:8000/{engine,doc,code,viz,search,cloud}/
- Implementations (under development)
  - SciTeX-Engine (~/.emacs.d/lisp/emacs-claude-code)
  - SciTeX-Doc (~/proj/scitex)
  - SciTeX-Code (~/proj/mngs_repo)
  - SciTeX-Viz (~/proj/scitex/SigMacro)
  - SciTeX-Search (will be implemented)
  - SciTeX-Cloud (~/proj/SciTeX-Cloud; This repo)


...
```


### `./project_management/feature_requests/feature-request-remove-redundant-scitex-branding.md`

```markdown

# Feature Request: Remove Redundant SciTeX Branding

## Summary
Remove redundant "SciTeX" branding from the dashboard and other areas to reduce visual clutter and avoid wasting user attention.

## Feature Request Details

### Problem Statement
- **Issue**: Redundant "SciTeX" branding appears in multiple places, particularly in the dashboard
- **Impact**: Creates visual clutter and wastes user attention
- **Goal**: Clean, focused interface without unnecessary repetition

### Scope
- **Primary Target**: Dashboard page - remove redundant "SciTeX" text/branding
- **Secondary Areas**: Review other pages for similar redundant branding
- **Principle**: No duplication needed - if SciTeX is already clear from context, don't repeat it

### Implementation Guidelines
1. **Dashboard Cleanup**:
   - Remove redundant "SciTeX" text from dashboard elements
   - Keep essential branding only where contextually necessary
   - Maintain clear hierarchy without repetitive labels

2. **Site-wide Review**:
   - Audit all pages for redundant branding
   - Apply consistent "no duplication" principle
   - Focus user attention on functionality, not repetitive branding

3. **Branding Strategy**:
   - Maintain brand identity without over-repetition
   - Use SciTeX branding strategically (header, key locations)
   - Avoid redundant mentions in obvious contexts

## Technical Implementation

### Priority: Medium
This improves user experience by reducing visual noise and focusing attention.

### Areas to Review:
1. **Dashboard**:
   - Module cards - remove redundant "SciTeX" prefixes
   - Statistics sections
   - Welcome messages
   - Navigation elements

2. **Module Pages**:
   - Remove redundant "SciTeX Scholar", "SciTeX Writer" if context is clear
   - Keep branding where it adds value or clarity


...
```


### `./project_management/feature_requests/feature-request-remove-unnecessary-pages.md`

```markdown

# Remove these pages and associated contents

cloud/ -> just keep root
roadmap/ [name='roadmap']
repositories/ [name='repositories']
windows/ [name='windows']
feature-request/ [name='feature-request']

papers/ [name='papers'] -> should be renamed as publications

# remove products layer and adopt better version (e.g., engine/ vs products/engine)
products/engine/ [name='product-engine'] 
products/doc/ [name='product-doc']
products/code/ [name='product-code']
products/viz/ [name='product-viz']
products/search/ [name='product-search']
products/cloud/ [name='product-cloud']


...
```


### `./project_management/feature_requests/feature-request-system-requirements-clarification.md`

```markdown
# Feature Request: Clarify System Requirements for SciTeX Components

**Date**: 2025-05-23
**Priority**: High
**Category**: Documentation & Infrastructure

## Summary

Clarify and document the system requirements for each SciTeX component, particularly addressing:
- SciTeX-Engine's dependency on Claude Code
- SciTeX-Viz's dependency on Windows and SigmaPlot
- Linux compatibility and Apptainer containerization strategy

## Current Situation

The SciTeX ecosystem components have varying system requirements that are not clearly documented:
- Some components require specific proprietary software
- Platform dependencies (Windows vs Linux) are unclear
- Containerization strategy needs definition

## Proposed Changes

### 1. Document Component Requirements

Create clear documentation for each component's dependencies:

#### SciTeX-Engine
- **Requires**: Claude Code (Anthropic's CLI tool)
- **Platform**: Linux/macOS/Windows
- **Integration**: Emacs environment
- **Container Strategy**: Package Claude Code within Apptainer if needed

#### SciTeX-Viz
- **Requires**: Windows OS + SigmaPlot (proprietary software)
- **Current Platform**: Windows only
- **Container Strategy**: 
  - Option A: Wine/Windows compatibility layer in Apptainer
  - Option B: Remote Windows server for SigmaPlot processing
  - Option C: Develop Linux-native alternative visualization backend

#### Other Components
- **SciTeX-Doc**: Pure LaTeX, Linux-native
- **SciTeX-Code**: Python-based, Linux-native
- **SciTeX-Search**: Web-based, Linux-native
- **SciTeX-Cloud**: Django-based, Linux-native

### 2. Containerization Strategy

Implement Apptainer containers for:
- Components with complex dependencies

...
```


### `./project_management/feature_requests/feature-request-viz-enhanced-page.md`

```markdown

# Feature Request: Enhanced Viz Page with Sample Figures

## Summary
Enhance the Viz page with a proper hero section, sample figures, and professional presentation for publication-ready graphing capabilities.

## Feature Request Details

### Problem Statement
- **Issue**: Current Viz page only shows "Coming Soon" message
- **Impact**: Users don't understand Viz capabilities or see examples
- **Goal**: Professional showcase of publication-ready graphing features

### Scope
- **Hero Section**: Professional hero with "SciTeX Viz" and "Publication-ready, high quality graphing"
- **Sample Figures**: Add sample visualizations with links (similar to previous implementation)
- **Coming Soon Status**: Maintain "Coming Soon" indication while showing preview capabilities

### Implementation Guidelines
1. **Hero Section**:
   - Title: "SciTeX Viz" (keeping SciTeX here as it's the proper module name)
   - Subtitle: "Publication-ready, high quality graphing"
   - Use appropriate hero gradient styling

2. **Sample Figures**:
   - Add sample scientific visualizations
   - Include links to examples or demos
   - Showcase typical scientific graphing capabilities

3. **Coming Soon Badge**:
   - Maintain "Coming Soon" status
   - Position appropriately with sample content

## Technical Implementation

### Priority: Medium
This improves user understanding of Viz capabilities and provides preview of features.

### Areas to Implement:
1. **Viz Index Page**:
   - Enhanced hero section with proper branding
   - Sample figure gallery
   - Professional presentation

2. **Sample Content**:
   - Scientific visualization examples
   - Publication-quality figure demonstrations
   - Interactive elements or links where appropriate

3. **Design Consistency**:

...
```


### `./project_management/feature_requests/feature-request-windows-chrome-access.md`

```markdown
# Feature: Windows Chrome Access to Development Server

## Request
Access the development server running in WSL from Google Chrome on Windows for a better visual experience.

## Implementation
We've implemented the following solutions:

### 1. Enhanced Start Script
The existing `start_dev.sh` script now displays the WSL IP address that can be accessed from Windows:

```bash
# Get the WSL IP address for Windows access
WSL_IP=$(ip -4 addr show eth0 | grep -oP '(?<=inet\s)\d+(\.\d+){3}')
echo "🌐 You can access the site from Windows at http://$WSL_IP:8000"
```

### 2. Windows-Specific Script
A new script `start_dev_windows.sh` has been created that:
- Starts the development server
- Prominently displays the Windows access URL
- Provides troubleshooting tips

## Usage Instructions

### Method 1: Using start_dev.sh
1. Start the development server with `./start_dev.sh`
2. Note the Windows access URL displayed in the console
3. Open Chrome in Windows and navigate to that URL

### Method 2: Using Windows-specific script
1. Run `./start_dev_windows.sh`
2. Copy the Windows access URL displayed
3. Paste it into Chrome on Windows

## Troubleshooting

If you cannot access the site from Windows:

1. **Check Windows Firewall**
   - Make sure your Windows Firewall allows connections to WSL
   - Consider temporarily disabling the firewall for testing

2. **WSL Network Reset**
   - Open PowerShell as Administrator in Windows and run:
   ```powershell
   wsl --shutdown
   ```
   - Then restart your WSL terminal and run the development server again


...
```


### `./project_management/fixes-summary-20250522.md`

```markdown
# SciTeX-Cloud Fixes Summary
**Date:** May 22, 2025

## Issues Identified

1. **Settings Configuration Issues:**
   - Development settings file (`config/settings/development.py`) tries to update a LOGGING dictionary that's not defined in that scope
   - Need to properly import the base LOGGING configuration from the main settings file

2. **Incorrect Path References:**
   - The project structure has changed from using `src/` or `_src/` directories to an `apps/` structure
   - References to old directory structures need to be updated

3. **Landing Page Request:**
   - You want to use the landing page from the old codebase (`.old/_src/scitex_cloud/templates/scitex_cloud/landing.html`)
   - Need to adapt it to the new project structure

## Implemented Fixes

1. **Fixed Development Settings:**
   - Added import for LOGGING from the main settings file:
   ```python
   from ..settings import LOGGING
   ```

2. **Next Steps for Incorporating Landing Page:**

   a. **Copy Landing Page HTML:**
   - Copy the silverish landing page from `.old/_src/scitex_cloud/templates/scitex_cloud/landing.html` to `apps/cloud_app/templates/cloud_app/landing.html`
   - Update template references (from `scitex_cloud` to `cloud_app`)
   - Update URL references to use Django's URL naming system

   b. **Adapt CSS Files:**
   - Ensure all referenced CSS files exist in the new structure:
     - `static/css/index.css`
     - `static/css/landing.css`
     - `static/css/header-override.css`
   - Copy missing CSS files from the old structure if needed

   c. **Update Static Files:**
   - Ensure all image files referenced in the landing page are available in the new structure
   - Copy any missing image files from `.old/_src/static/images/` to `static/images/`

   d. **Test Landing Page:**
   - Run the development server to verify the landing page displays correctly
   - Check for any broken links or missing resources

## Running the Application

To run the application with these fixes:

...
```


### `./project_management/github-buttons-landing-page-summary.md`

```markdown
# GitHub Buttons Landing Page Implementation Summary

**Date**: 2025-05-23
**Status**: Completed

## Overview

Successfully added "View on GitHub" buttons to all product cards on the landing page, making it easy for users to access the source code for each SciTeX component directly from the homepage.

## Changes Made

### 1. Updated Landing Page HTML Structure
**File**: `/apps/cloud_app/templates/cloud_app/landing.html`

- Restructured product cards to separate the clickable product link from the GitHub button
- Wrapped product content in `<a class="product-card-link">` for navigation to product pages
- Added `<div class="product-card-actions">` section with GitHub buttons
- Each GitHub button links to the appropriate repository:
  - Engine: https://github.com/ywatanabe1989/emacs-claude-code
  - Doc: https://github.com/ywatanabe1989/scitex
  - Search: https://github.com/ywatanabe1989/SciTeX-Search
  - Code: https://github.com/ywatanabe1989/mngs
  - Viz: https://github.com/ywatanabe1989/SigMacro
  - Cloud: https://github.com/ywatanabe1989/SciTeX-Cloud

### 2. Enhanced CSS Styling
**File**: `/static/css/landing.css`

Added new styles for GitHub buttons:
- `.product-card-actions`: Section with top border to separate from content
- `.btn-github`: Styled button with GitHub icon and hover effects
- `.pricing-link`: Special styling for the pricing link in Cloud card
- Adjusted card structure to accommodate the new button section
- Added `:has()` selector to prevent card hover effects when hovering GitHub button

### 3. Special Features

- GitHub buttons open in new tabs (`target="_blank"`)
- Buttons include Font Awesome GitHub icon
- Cloud card also includes a "View Pricing" link
- Buttons are visually separated from the main card content
- Hover effects provide clear visual feedback

## User Experience Improvements

1. **Clear Separation**: Product information and GitHub access are visually separated
2. **Direct Access**: Users can access source code without navigating to product pages
3. **Visual Consistency**: GitHub buttons match the overall design system
4. **Accessibility**: Buttons are keyboard accessible and have clear focus states


...
```


### `./project_management/git-setup-summary-2025-0522.md`

```markdown
# Git Version Control Setup Summary

## Date: May 22, 2025

## Overview
We have successfully implemented Git version control for the SciTeX-Cloud project following the Version Control Rules outlined in `docs/to_claude/guidelines/IMPORTANT-guidelines-programming-Version-Control-Rules.md`. This document summarizes the steps taken and the current state of the repository.

## Repository Structure
- **Main Branch**: Stable code that has been tested and verified
- **Develop Branch**: Active development branch where feature branches are merged
- **Feature Branches**: Short-lived branches for specific features/fixes (currently none active)

## Tags
- **v0.1.0**: Initial version with logging system

## Workflow Implemented
1. ✅ Initialized Git repository
2. ✅ Created `develop` branch as the main development branch
3. ✅ Made initial commit of the codebase to `develop`
4. ✅ Created feature branch `feature/add-logging-system` for logging enhancements
5. ✅ Committed changes to the feature branch
6. ✅ Merged feature branch back to `develop` after verification
7. ✅ Deleted feature branch after successful merge
8. ✅ Created `main` branch
9. ✅ Merged `develop` into `main`
10. ✅ Tagged the initial version as `v0.1.0`
11. ✅ Switched back to `develop` for future work

## Key Commit Messages
- Initial commit for SciTeX-Cloud project
- Enhance logging system with better documentation and settings

## Status
The repository is now properly set up with version control following the GitFlow-like workflow specified in our guidelines. Developers should:

1. Always work in feature branches branched from `develop`
2. Follow the naming convention `feature/<verb>-<object>` for feature branches
3. Merge back to `develop` when features are complete and tested
4. Delete feature branches after successful merges
5. Only merge to `main` for stable, release-ready code

## Next Steps
For future development:
1. Create dedicated feature branches for new features or bug fixes
2. Implement continuous integration to run tests automatically
3. Consider setting up a remote repository on GitHub

## Command Reference
Basic commands for the established workflow:


...
```


### `./project_management/header-footer-implementation-summary.md`

```markdown
# Header and Footer Implementation Summary

## Implementation Overview

The header and footer have been successfully implemented across all pages of the SciTeX-Cloud project. This involved:

1. Using a common base template with included partials
2. Setting up app-specific base templates
3. Ensuring all page templates extend the correct base template
4. Creating placeholder landing pages for app components that didn't have them

## Template Structure

The implemented template structure follows best practices for Django projects:

```
templates/
├── base.html                   # Main base template for entire site
└── partials/
    ├── header.html            # Common header included in base.html
    └── footer.html            # Common footer included in base.html

apps/
├── cloud_app/templates/
│   └── cloud_app/
│       ├── base.html          # App-specific base (extends main base.html)
│       ├── landing.html       # App pages (extend app-specific base.html)
│       └── ...
├── code_app/templates/
│   └── code_app/
│       ├── base.html
│       └── index.html
└── ...                        # Similar structure for other apps
```

## Implementation Details

### 1. Main Base Template

The main `base.html` includes:
- Common CSS and JavaScript
- Header and footer partials
- Block definitions for content customization

### 2. App-Specific Base Templates

Each app has its own base template that:
- Extends the main base.html
- Defines app-specific meta information
- Contains app-specific block definitions

...
```


### `./project_management/implementation-summary-local-dev-server.md`

```markdown
# Implementation Summary: Local HTML Development Server

## Implementation Complete ✅

The local HTML development server for SciTeX Web has been successfully implemented based on the patterns from ai_ielts and airight projects.

## What Was Implemented

### 1. Django Project Structure
- **Proper Django project layout** with `config/` directory containing project settings
- **Environment-specific settings**: `base.py`, `development.py`, `production.py`
- **Project-level URL configuration** in `config/urls.py`
- **WSGI/ASGI applications** for deployment

### 2. Development Server Features
- **Hot reload functionality** using `django-browser-reload`
- **Automatic browser refresh** on file changes (HTML, CSS, JS)
- **Development middleware** and debugging tools
- **Static file serving** during development

### 3. Static File Organization
- **Structured static files** in `/static/` directory:
  ```
  static/
  ├── css/{common,components,pages}/
  ├── js/{common,components,pages}/
  └── images/
  ```
- **Migrated existing files** from `/public/` to `/static/`
- **Updated templates** to use Django `{% static %}` tags

### 4. Development Scripts
- **`start_dev.sh`**: One-command development server startup
- **`start_prod.sh`**: Production environment setup
- **Automatic virtual environment** creation and management
- **Dependency installation** and database setup

### 5. Requirements Management
- **Split requirements** into `base.txt`, `development.txt`, `production.txt`
- **Development tools**: django-browser-reload, django-extensions, debug-toolbar
- **Production tools**: gunicorn, psycopg2, sentry-sdk

### 6. Template Updates
- **Added Django static file tags** to all templates
- **Maintained existing functionality** while improving Django integration
- **Hot reload support** for all template changes

## Files Created/Modified

### New Files

...
```


### `./project_management/modularity-implementation-summary.md`

```markdown
# Modularity Implementation Summary

**Date**: 2025-05-23
**Status**: Completed

## Overview

Successfully implemented messaging and UI updates to highlight SciTeX's modular architecture and unlimited customization capabilities.

## Key Changes Implemented

### 1. Updated Hero Messaging
**Before**: "Accelerate Your Scientific Research"
**After**: "Modular Science. Unlimited Possibilities."

**New Subtitle**: "Build your perfect research environment with six independent, open-source modules. Use them together or standalone. Customize everything. Own your workflow."

### 2. Added Modularity Section

Created a dedicated section highlighting:
- **Use What You Need**: Independent modules, no bloat
- **Mix and Match**: Combine with existing tools
- **Customize Everything**: 100% open source
- **API-First Design**: Easy integration

### 3. Deployment Options Display

Shows three deployment paths:
1. **Local Installation**: Direct install commands
2. **Containerized**: Docker commands
3. **Cloud Platform**: Integrated web solution

## Messaging Strategy

### Core Principles Emphasized

1. **Separation of Concerns (SoC)**
   - Each module has a single, focused purpose
   - Clean interfaces between modules
   - No unnecessary dependencies

2. **True Modularity**
   - Use modules independently
   - Replace any component
   - Extend functionality
   - Build custom workflows

3. **Open Source Freedom**
   - Full transparency
   - Community-driven development

...
```


### `./project_management/monitoring-system-implementation-20250627.md`

```markdown
# SciTeX Cloud Monitoring System Implementation

**Date**: 2025-06-27  
**Status**: ✅ COMPLETE  
**Priority**: HIGH  

## Overview

Successfully implemented a comprehensive performance monitoring system for SciTeX Cloud platform, providing real-time visibility into system health, user activity, and API performance.

## Key Components Implemented

### 1. Monitoring Models (`apps/monitoring_app/models.py`)
- **SystemMetric**: Tracks response times, endpoint performance, status codes
- **ErrorLog**: Captures and categorizes system errors with severity levels
- **APIUsageMetric**: Monitors external API calls (Scholar, Semantic Scholar, etc.)
- **UserActivity**: Logs user actions and engagement patterns

### 2. Performance Middleware (`apps/monitoring_app/middleware.py`)
- **PerformanceMonitoringMiddleware**: Automatically captures:
  - Request/response times for all endpoints
  - Error exceptions with stack traces
  - User activity patterns
  - IP addresses and user agents
  - HTTP status codes and methods

### 3. Monitoring Dashboard (`/monitoring/`)
- **Real-time metrics display** with auto-refresh every 30 seconds
- **Interactive charts** using Chart.js:
  - Response time trends (line chart)
  - Status code distribution (doughnut chart)
  - User activity patterns (bar chart)
  - Top endpoint usage tables
- **System health indicators** with color-coded status
- **Time range filtering** (1 hour to 1 week)
- **SciTeX design system integration** with brand colors

### 4. Error Management (`/monitoring/errors/`)
- **Error log viewer** with severity categorization
- **Stack trace expansion** for debugging
- **Resolution tracking** with admin controls
- **User and endpoint correlation**

### 5. Admin Interface
- **Full CRUD operations** for all monitoring models
- **Bulk actions** for error resolution
- **Advanced filtering** by time, severity, user, endpoint
- **Search capabilities** across all relevant fields

### 6. Utility Functions (`apps/monitoring_app/utils.py`)

...
```


### `./project_management/naming-quick-reference.md`

```markdown
# SciTeX Naming Quick Reference Guide

## Component Names - At a Glance

| Old Name | New Name | Purpose | Repository |
|----------|----------|---------|------------|
| SciTeX-Engine | **SciTeX Studio** | AI-powered research environment | scitex-studio |
| SciTeX-Doc | **SciTeX Manuscript** | Scientific paper preparation | scitex-manuscript |
| SciTeX-Code | **SciTeX Compute** | Data analysis & computing | scitex-compute |
| SciTeX-Viz | **SciTeX Figures** | Publication graphics | scitex-figures |
| SciTeX-Search | **SciTeX Discover** | Literature discovery | scitex-discover |
| SciTeX-Cloud | **SciTeX Cloud** | Web platform (unchanged) | scitex-cloud |

## Terminology Changes

### ❌ Don't Say → ✅ Do Say
- Products → **Research Modules**
- Product Page → **Module Overview**
- Product Features → **Module Capabilities**
- Customers → **Researchers/Users**
- Buy/Purchase → **Subscribe/Access**
- Demo → **Explore**

## Platform Handles

### Already Secured ✓
- **Domain**: scitex.ai
- **GitHub**: @SciTeX-AI
- **Twitter/X**: @SciTeX_AI
- **Emails**: {admin, support, ywatanabe}@scitex.ai

### To Register
- **LinkedIn**: /company/scitex-ai
- **YouTube**: @SciTeXAI
- **PyPI**: scitex-compute (currently 'mngs')
- **npm**: @scitex scope

## Module Colors

```
Studio    #4169E1 (Royal Blue)
Manuscript #28a745 (Green)
Compute   #fd7e14 (Orange)
Figures   #6f42c1 (Purple)
Discover  #20c997 (Teal)
Cloud     #0d47a1 (Navy)
```

## Taglines


...
```


### `./project_management/navigation-improvements-20250522.md`

```markdown
# Navigation and Pages Improvements
**Date:** May 22, 2025

## Issues Fixed

1. **Missing Design System Page:**
   - Added URL route for `/design/` in `cloud_app/urls.py`
   - Added a view for the design system page in `cloud_app/views.py`
   - The page now properly shows the comprehensive design system with color palettes and components

2. **Missing Features Page:**
   - Created a new `features.html` template
   - Implemented a comprehensive features page showing research management, data analysis, and document creation features
   - Added appropriate styling for feature cards and sections

3. **Improved Navigation:**
   - Updated the header to include dropdown menus for better organization
   - Added an "About" dropdown with links to concept, vision, roadmap, papers, and repositories
   - Added a "Resources" dropdown with links to Windows guide, feature requests, and design system
   - Ensured all URLs in the header have trailing slashes for consistency
   - Improved link organization for better site navigation

4. **Missing Demo Page:**
   - Added URL route for `/demo/`
   - Added a view for the demo page

## Implementation Details

### 1. Design System Page
```python
# views.py
def design_system(request):
    """Design system documentation page."""
    return render(request, 'cloud_app/pages/design_system.html')

# urls.py
path('design/', views.design_system, name='design'),
```

### 2. Features Page
- Created a comprehensive features page with three main sections:
  - Research Management
  - Data Analysis & Visualization
  - Document Creation
- Added styled feature cards with icons, descriptions, and feature lists
- Added a call-to-action section at the bottom

### 3. Header Navigation
- Organized links into logical groups
- Implemented dropdown menus for Products, About, and Resources

...
```


### `./project_management/next_steps-20250521-030455.md`

```markdown
# SciTeX Web Project - Next Steps

## Priority Tasks
1. **Collaborate with user to populate USER_PLAN.md**
   - Need detailed project description
   - Define timeline and milestones
   - Clarify resources and success criteria

2. **Resolve git status issues**
   - Current status shows staged but deleted files in literature_review
   - Determine if these should be committed or removed
   - Implement proper git workflow according to version control guidelines

3. **Render Mermaid diagram**
   - Use `.claude/bin/render_mermaid.sh` to create SVG visualization
   - Create visual progress tracking

4. **Prepare for code organization**
   - Follow Clean Code principles from guidelines
   - Plan directory structure for the project
   - Establish testing methodology

## Questions for User
1. What is the current status of files in "../literature_review/" that appear as staged but deleted?
2. What are the specific goals, timeline, and milestones for the SciTeX Web Project?
3. Should we continue on the current feature branch (feature/SciTeX-PaperReview) or create a new one?

## Git Next Steps
- Once project plan is filled, commit project management files
- Follow version control workflow from guidelines
- Ensure we're working on correct branch (develop → feature branch)

...
```


### `./project_management/optimization-implementation-20250523.md`

```markdown
# Optimization Implementation Summary

**Date**: 2025-05-23
**Status**: Completed

## Optimizations Implemented

### 1. ✅ Removed Console.log Statements
**File**: `/static/js/main.js`
- Removed production console.log statements
- Kept comments for clarity
- No functional changes

### 2. ✅ Fixed JavaScript Error Handling
**File**: `/static/js/landing.js`
- Added null checks for navigation elements
- Fixed smooth scroll to only handle anchor links
- Added check for navLinks length before processing
- Prevented errors when elements don't exist on page

### 3. ✅ Added Open Graph Meta Tags
**File**: `/templates/base.html`
- Added Open Graph tags for Facebook sharing
- Added Twitter Card meta tags
- Made tags customizable with Django template blocks
- Default values provide good fallbacks

### 4. 📝 Empty CSS File (Not Removed)
**File**: `/static/css/header-override.css`
- Identified as empty but referenced in multiple places
- Requires careful removal to avoid breaking imports
- Recommended for future cleanup task

## Code Quality Improvements

### JavaScript Improvements
```javascript
// Before: Could throw errors if elements missing
link.addEventListener('click', (e) => {
  e.preventDefault();
  
// After: Safely handles missing elements
if (targetId && targetId.startsWith('#')) {
  e.preventDefault();
```

### Meta Tags Added
```html
<meta property="og:title" content="{% block og_title %}...{% endblock %}">
<meta property="og:description" content="{% block og_description %}...{% endblock %}">
```

...
```


### `./project_management/optimization-opportunities-20250523.md`

```markdown
# SciTeX Cloud Optimization Opportunities

**Date**: 2025-05-23
**Status**: Analysis Complete

## Current State

The platform is healthy and functioning well, but there are some optimization opportunities identified.

## Optimization Opportunities

### 1. Code Cleanup
- **Empty CSS File**: `/static/css/header-override.css` is empty and can be removed
- **Console Logs**: Production code contains `console.log` statements that should be removed

### 2. JavaScript Optimization
- **Unused Event Handlers**: `landing.js` contains handlers for elements that don't exist on the current landing page:
  - Pricing toggle functionality
  - FAQ accordion functionality
  - These should be conditionally loaded or moved to appropriate pages

### 3. Performance Enhancements
- **CSS Consolidation**: Multiple small CSS files could be combined:
  - `bootstrap-override.css` (87 lines)
  - `main.css` (93 lines)
  - `index.css` (95 lines)
  - Consider combining into a single `core.css` file

### 4. SEO Improvements
- Add Open Graph meta tags for better social media sharing
- Add structured data (JSON-LD) for better search engine understanding
- Consider adding a sitemap.xml

### 5. Accessibility Enhancements
- All images already have alt attributes ✅
- Heading hierarchy is proper ✅
- Consider adding:
  - Skip navigation links
  - ARIA labels for interactive elements
  - Focus indicators for keyboard navigation

### 6. Asset Optimization
- Multiple logo variants exist - consider consolidating to 2-3 versions
- Images could be optimized with modern formats (WebP)
- Consider lazy loading for images below the fold

### 7. Security Headers
- Consider adding security headers:
  - Content-Security-Policy
  - X-Content-Type-Options

...
```


### `./project_management/platform-health-check-20250523.md`

```markdown
# SciTeX Cloud Platform Health Check

**Date**: 2025-05-23
**Status**: All Systems Operational

## Summary

Comprehensive health check of the SciTeX Cloud platform shows all systems functioning correctly.

## Health Check Results

### 1. Navigation & Links ✅
- **22/22** navigation links tested and working
- No broken links detected
- All pages accessible

### 2. Static Assets ✅
- **All product icons present**: Engine, Doc, Search, Code, Viz, Cloud
- **Logo files**: Multiple variants available including transparent PNG
- **Manuscript preview**: PDF and JPG files properly served
- **CSS/JS files**: Loading correctly with proper MIME types

### 3. Server Status ✅
- Development server running on http://localhost:8000
- Homepage loads successfully
- No console errors detected

### 4. API Endpoints ✅
- `/api/v1/` responding with proper authentication requirements
- API structure in place and functional

### 5. New Features ✅
- **System Requirements**: Documented and displayed on all product pages
- **Freemium Pricing**: Comprehensive strategy documented
- **GitHub Buttons**: Successfully added to landing page with proper styling
- **All CSS updates**: Applied and loading correctly

## File Structure Verification

### Key Documentation Files
- ✅ `/docs/SYSTEM_REQUIREMENTS.md`
- ✅ `/docs/FREEMIUM_PRICING_STRATEGY.md`
- ✅ `/project_management/feature_requests/feature-request-system-requirements-clarification.md`

### Updated Templates
- ✅ Landing page with GitHub buttons
- ✅ Product pages with system requirements
- ✅ All CSS files properly linked

## Performance Metrics

...
```


### `./project_management/platform-readiness-assessment-20250523.md`

```markdown
# SciTeX Cloud Platform Readiness Assessment

**Date**: 2025-05-23
**Status**: Production Ready with Minor Enhancements Needed

## Executive Summary

The SciTeX Cloud platform demonstrates excellent technical maturity and is ready for production deployment with minor enhancements. The platform shows strong foundations in all critical areas.

## Assessment Scores

| Category | Score | Status |
|----------|-------|--------|
| **Core Functionality** | 9/10 | ✅ Excellent |
| **Security** | 8/10 | ✅ Good |
| **Performance** | 8/10 | ✅ Good |
| **Monitoring** | 9/10 | ✅ Excellent |
| **Documentation** | 9/10 | ✅ Excellent |
| **Scalability** | 7/10 | ⚠️ Needs Cloud Integration |
| **User Experience** | 8/10 | ✅ Good |
| **SEO/Marketing** | 9/10 | ✅ Excellent |

**Overall Score: 8.4/10** - Production Ready

## Detailed Assessment

### ✅ Strengths

1. **Comprehensive API Structure**
   - Well-organized RESTful API with versioning
   - JWT authentication implemented
   - Modular endpoint structure for each component

2. **Security Features**
   - JWT token-based authentication
   - CSRF protection enabled
   - Security headers configured for production
   - SSL/HTTPS enforcement in production settings

3. **Monitoring & Logging**
   - Beautiful real-time monitoring dashboard
   - Comprehensive logging configuration
   - Separate log files for errors, security, and general activity
   - WebSocket support for real-time updates

4. **Documentation & SEO**
   - System requirements clearly documented
   - Freemium pricing strategy defined
   - Open Graph meta tags implemented
   - Sitemap and robots.txt created

...
```


### `./project_management/pre-deployment-security-checklist.md`

```markdown
# Pre-Deployment Security Checklist

**Date**: 2025-05-23
**Status**: Ready for Review

## Security Configuration ✅

### 1. Django Settings
- [x] **DEBUG = False** in production settings
- [x] **SECRET_KEY** loaded from environment variable
- [x] **ALLOWED_HOSTS** configured for production domains
- [x] **SECURE_SSL_REDIRECT = True** for HTTPS enforcement
- [x] **SECURE_HSTS_SECONDS** set to 31536000 (1 year)
- [x] **SECURE_CONTENT_TYPE_NOSNIFF = True**
- [x] **SECURE_BROWSER_XSS_FILTER = True**
- [x] **CSRF protection** enabled by default

### 2. Authentication & Authorization
- [x] JWT authentication implemented
- [x] Token refresh mechanism in place
- [x] Password hashing (Django default PBKDF2)
- [ ] Two-factor authentication (recommended for future)
- [ ] Rate limiting on login attempts (recommended)

### 3. Database Security
- [x] Database credentials from environment variables
- [x] PostgreSQL configured for production
- [ ] Database connection SSL/TLS (verify with hosting)
- [ ] Regular backup strategy (implement with hosting)

### 4. API Security
- [x] API versioning implemented (v1)
- [x] Authentication required for protected endpoints
- [x] CORS headers configuration needed
- [ ] API rate limiting (recommended)
- [ ] API key management for external access

### 5. Logging & Monitoring
- [x] Comprehensive logging configuration
- [x] Separate security log file
- [x] Error logging with email alerts
- [x] Real-time monitoring dashboard
- [ ] Intrusion detection system (future)

### 6. Static Files & Media
- [x] Static files served separately in production
- [x] Media files directory configured
- [ ] CDN configuration for static assets
- [ ] User upload validation and sanitization


...
```


### `./project_management/progress-development-server-complete.md`

```markdown
# Progress Update: Development Server Implementation Complete

## Status: ✅ COMPLETE

The local HTML development server has been successfully implemented and merged into the develop branch following proper version control workflow.

## Git Workflow Executed

Following the Version Control Rules guidelines:

1. ✅ **Understood current workflow step**: On develop branch with new functionality
2. ✅ **Created feature branch**: `feature/implement-local-dev-server`
3. ✅ **Verified implementation with tests**: Django system checks passed
4. ✅ **Committed with proper testing**: Included test run verification
5. ✅ **Merged to develop**: Fast-forward merge successful
6. ✅ **Cleaned up**: Deleted feature branch for cleanliness

## Implementation Summary

### Major Components Added
- **Django Project Structure**: Proper config/ directory with settings modules
- **Development Server**: Hot reload with django-browser-reload
- **Static File Organization**: Structured CSS/JS in static/ directory
- **Development Scripts**: One-command startup with `./start_dev.sh`
- **Environment Management**: Separate development/production configurations
- **Documentation**: Comprehensive setup and usage guide

### Files Changed/Added
```
39 files changed, 3982 insertions(+), 6 deletions(-)
```

### Core Features
- ✅ One-command development server: `./start_dev.sh`
- ✅ Hot reload functionality for all file types
- ✅ Proper Django static file handling
- ✅ Environment-specific settings
- ✅ Production deployment preparation
- ✅ Virtual environment management

## Testing Results

- ✅ Django system checks: PASSED
- ✅ Development environment setup: PASSED  
- ✅ Static file organization: VERIFIED
- ✅ Template Django tags: UPDATED
- ✅ Hot reload functionality: IMPLEMENTED

## Verification Commands


...
```


### `./project_management/progress-module-ordering-ux-improvements-20250628.md`

```markdown
# Progress Report: Module Ordering & UX Improvements
**Date**: 2025-06-28  
**Session ID**: d376248c-3230-4843-997c-836d3e5dc2f8  
**Status**: ✅ COMPLETED

## Overview
Implemented comprehensive module ordering standardization and Scholar page UX improvements across the SciTeX Cloud platform based on user feature requests.

## 🎯 Completed Tasks

### Module Order Standardization
✅ **Consistent Module Order**: Implemented scholar → viz → code → writer across all templates  
- Landing page ecosystem modules reordered  
- Header navigation tools dropdown updated  
- Footer tools section standardized  
- Reflects natural scientific project progression

✅ **Coming Soon Indicators**: Added proper badges for unavailable modules  
- Viz module: "Coming Soon" badges in header, footer, landing page  
- Code module: "Coming Soon" badges in header, footer, landing page  
- Subscripted papers: "Coming Soon" indicator in Scholar search options

### Scholar Page UX Enhancements
✅ **Subtitle Visibility**: Fixed low contrast issue  
- Added explicit color styling for hero subtitle and description text  
- Improved readability with `opacity: 0.9` and `opacity: 0.8` values

✅ **Search Placeholder**: Reduced visual prominence  
- Changed placeholder color to lighter `#6b7280` with `opacity: 0.7`  
- Maintains usability while reducing visual noise

✅ **Enhanced Search Options**: Added coming soon features  
- "Subscripted papers" checkbox with coming soon indicator  
- Maintains user awareness of planned functionality

### Hero Section Consistency
✅ **About Page Enhancement**: Added hero section with SciTeX gradient  
- Matches landing page design consistency  
- Preserves dashboard exception as requested  
- Uses silverish-ai gradient for scientific sophistication

## 🧪 Quality Assurance

### Test Results
All critical modules tested and verified stable:

**Scholar App**: 7/7 tests passing ✅  
- Search functionality working correctly  
- Database models operational  
- View responses successful  

...
```


### `./project_management/progress-SciTeX-Design-System-20250522.md`

```markdown
# SciTeX Design System Implementation - Progress Report

**Date:** 2025-05-22  
**Status:** ✅ COMPLETED  
**Deployment:** ✅ LIVE at http://localhost:8000

## Summary

Successfully implemented a comprehensive SciTeX bluish dark gray color system with harmonized status colors, achieving complete aesthetic consistency across the SciTeX-Cloud website.

## Key Accomplishments

### 1. SciTeX Color System (7-Color Palette)
- **scitex-color-01**: #1a2332 (Dark Bluish Gray - Primary)
- **scitex-color-02**: #34495e (Medium Bluish Gray - Header)
- **scitex-color-03**: #506b7a (Light Bluish Gray)
- **scitex-color-04**: #6c8ba0 (Lighter Bluish Gray)
- **scitex-color-05**: #8fa4b0 (Very Light Bluish Gray)
- **scitex-color-06**: #b5c7d1 (Pale Bluish Gray)
- **scitex-color-07**: #d4e1e8 (Very Pale Bluish Gray)

### 2. Harmonized Status Colors
Replaced jarring Bootstrap colors with grayish harmonized versions:
- **Success**: #4a9b7e (Grayish Green)
- **Warning**: #b8956a (Grayish Orange)
- **Error**: #a67373 (Grayish Red)
- **Info**: #6b8fb3 (Grayish Blue)

### 3. Design Hierarchy
- **Header**: scitex-color-02 (prominent navigation)
- **Footer**: scitex-color-01-light (subtle base)
- **Content**: Full SciTeX palette for proper visual hierarchy

### 4. Technical Implementation
- Updated `/static/css/common/variables.css` with complete color system
- Eliminated all Bootstrap and framework color dependencies
- Converted all hardcoded hex values to semantic CSS variables
- Updated all component CSS files for consistency
- Proper RGB variants for transparency effects

## Files Updated
- `static/css/common/variables.css` - Core color system
- `static/css/components/header.css` - SciTeX header styling
- `static/css/components/footer.css` - SciTeX footer styling  
- `static/css/common/buttons.css` - Consistent button colors
- `static/css/darkmode.css` - SciTeX dark mode implementation
- `static/css/landing.css` - Removed Bootstrap fallbacks

## Quality Assurance
- ✅ Django server running without errors

...
```


### `./project_management/progress-SciTeX-Web-20250521-030455.md`

```markdown
# SciTeX Web Project Progress

| Type | Stat | Description           |
|------|------|-----------------------|
| 🚀   | [ ]  | SciTeX Web Project    |

## Goals, Milestones, and Tasks
#### 🎯 Goal 1: Establish Project Structure and Plan
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Establish project structure and planning      |
|      |      | 📌 Essential for organized development        |
|------|------|-----------------------------------------------|
| 🏁   | [x]  | Create project management directory           |
|      |      | 📌 Foundation for tracking progress           |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create USER_PLAN.md template                  |
|      |      | 📌 `/home/ywatanabe/proj/scitex-web/project_management/USER_PLAN.md` |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create CLAUDE_PLAN.md for tracking            |
|      |      | 📌 `/home/ywatanabe/proj/scitex-web/project_management/CLAUDE_PLAN.md` |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Populate USER_PLAN.md with project details    |
|      |      | 📌 Collaboration needed with user             |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Create progress tracking visuals with Mermaid |
|      |      | 📌 Required for visual project monitoring     |

#### 🎯 Goal 2: Implement Version Control
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Establish proper git workflow                 |
|      |      | 📌 Following version control guidelines       |
|------|------|-----------------------------------------------|
| 🏁   | [ ]  | Resolve current git status issues             |
|      |      | 📌 Fix staged but deleted files               |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Clarify status of literature_review directory |
|      |      | 📌 Files show as staged but deleted           |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Commit project management setup               |
|      |      | 📌 Track initial project structure            |

## Key Symbols
| Symbol | Meaning       | Status | Meaning |
|--------|---------------|--------|---------|
| 🎯     | Goal          | [ ]    | TODO    |
| 🏁     | Milestone     | [x]    | DONE    |
| 📋     | Task          |        |         |
| 💡     | Suggestion    |        |         |

...
```


### `./project_management/progress-TDD-20250521-031917.md`

```markdown
# SciTeX Web Project - Test-Driven Development Progress

| Type | Stat | Description                |
|------|------|----------------------------|
| 🚀   | [ ]  | SciTeX Web TDD Workflow    |

## Goals, Milestones, and Tasks
#### 🎯 Goal 1: Establish Test-Driven Development Workflow
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Establish TDD workflow                        |
|      |      | 📌 Following TDD guidelines                   |
|------|------|-----------------------------------------------|
| 🏁   | [x]  | Create comprehensive test suite               |
|      |      | 📌 Tests for core functionality               |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Create test runner script                     |
|      |      | 📌 `/run_tests.sh` for executing tests        |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Implement view tests                          |
|      |      | 📌 Tests for Django views                     |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Implement model tests                         |
|      |      | 📌 Tests for Django models                    |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Implement API tests                           |
|      |      | 📌 Tests for REST API endpoints               |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Implement config tests                        |
|      |      | 📌 Tests for application configuration        |
|------|------|-----------------------------------------------|
| 📋   | [x]  | Implement app initialization tests            |
|      |      | 📌 Tests for application setup                |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Run tests to verify failures                  |
|      |      | 📌 Confirm tests fail as expected             |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Commit test files                             |
|      |      | 📌 Following TDD workflow                     |

#### 🎯 Goal 2: Implement Features Based on Tests
| Type | Stat | Description                                   |
|------|------|-----------------------------------------------|
| 🎯   | [ ]  | Implement functionality to pass tests         |
|      |      | 📌 Following TDD workflow                     |
|------|------|-----------------------------------------------|
| 🏁   | [ ]  | Implement Django models                       |
|      |      | 📌 Based on test specifications               |
|------|------|-----------------------------------------------|
| 📋   | [ ]  | Implement UserProfile model                   |

...
```


### `./project_management/project-advancement-priorities.md`

```markdown
# SciTeX Cloud Project Advancement Priorities

## Current Status: PRODUCTION READY ✅
Last Updated: 2025-06-27-21:30

## Priority 1: CRITICAL - API Stability & Performance 🔥

### Scholar Search API Issues (URGENT)
- **Issue**: Semantic Scholar API rate limiting (429 errors)
- **Issue**: DOAJ API endpoint changes (404 errors)
- **Solution**: ✅ Reduced API limits and added error handling
- **Solution**: ✅ Updated DOAJ to v2 API endpoint
- **Solution**: ✅ Added graceful fallbacks between sources

### DNS Configuration (BLOCKING)
- **Issue**: MX records missing for scitex.ai email receiving
- **Impact**: Users cannot send emails to support@scitex.ai
- **Action Required**: Manual DNS configuration in Onamae.com panel
- **Status**: Documentation created, waiting for manual intervention

## Priority 2: HIGH - User Experience 📈

### Test Suite Maintenance
- **Issue**: Scholar test expecting 'Search Papers' text not found
- **Solution**: Update test to match current UI content
- **Status**: In progress

### Scholar Search Enhancement 
- **Achievement**: ✅ Expanded from 15 to 200+ real papers
- **Achievement**: ✅ Added 6 new academic sources (PMC, DOAJ, bioRxiv, PLOS)
- **Achievement**: ✅ Implemented 1-hour caching for performance
- **Next**: Error monitoring and user feedback collection

## Priority 3: MEDIUM - Feature Enhancement 🚀

### Writer Module Improvements
- **Achievement**: ✅ Fixed silverish gradient hero section
- **Achievement**: ✅ Added PDF download and live preview
- **Next**: Real LaTeX compilation backend integration

### User Library System
- **Status**: Basic saving implemented
- **Next**: Full library management, organization, export features

### Advanced Search Features
- **Status**: Basic filtering available
- **Next**: Faceted search, advanced filters, saved searches

## Priority 4: LOW - Long-term Goals 💡


...
```


### `./project_management/revised-english-content.md`

```markdown
# Revised English Content for SciTeX

## Original vs. Revised Versions

### Landing Page Hero Section

**Original:**
"SciTeX consists of modules of Engine, Doc, Search, Code, Viz, and Cloud. All modulesare fully open-sourced on GitHub. For use on Cloud, premium services available."

**Revised:**
"SciTeX integrates six powerful research modules: Studio, Manuscript, Discover, Compute, Figures, and Cloud. All modules are open source and available on GitHub. Premium cloud computing resources available for advanced research needs."

### Module Descriptions

#### SciTeX Studio (formerly Engine)

**Original:**
"Powered by Claude Code agent
Sets of guidelines and commands
Human-in-the-loop system on Emacs"

**Revised:**
"AI-powered research environment
Intelligent coding assistance  
Seamless Emacs integration"

#### SciTeX Manuscript (formerly Doc)

**Original:**
"LLM-assisted paper writing
Organized LaTeX compilation system
Citation management"

**Revised:**
"AI-enhanced scientific writing
Modular LaTeX workflow
Smart citation management"

#### SciTeX Discover (formerly Search)

**Original:**
"Literature review
Knowledge gap identification
Hypotheses generation"

**Revised:**
"Comprehensive literature discovery
Research gap analysis
Hypothesis generation"


...
```


### `./project_management/scitex-color-implementation-summary.md`

```markdown
# SciTeX Color System Implementation Summary

**Date:** May 22, 2025  
**Branch:** feature/refactor  
**Status:** ✅ Complete  

## Overview

Successfully implemented a comprehensive SciTeX color system throughout the entire SciTeX-Cloud platform, ensuring perfect aesthetic consistency using only the bluish dark gray color palette and essential status colors.

## SciTeX Color Palette

### Main Theme Colors
- `--scitex-color-01`: #1a2332 (Dark Bluish Gray - Primary)
- `--scitex-color-02`: #34495e (Medium Bluish Gray) 
- `--scitex-color-03`: #506b7a (Light Bluish Gray)
- `--scitex-color-04`: #6c8ba0 (Lighter Bluish Gray)
- `--scitex-color-05`: #8fa4b0 (Very Light Bluish Gray)
- `--scitex-color-06`: #b5c7d1 (Pale Bluish Gray)
- `--scitex-color-07`: #d4e1e8 (Very Pale Bluish Gray)

### Status Colors (Only exceptions for semantic purposes)
- `--success-color`: #2ecc71 (Green)
- `--warning-color`: #f39c12 (Orange)
- `--error-color`: #e74c3c (Red)
- `--info-color`: #3498db (Blue)

## Implementation Details

### Files Updated

#### 1. Core Variables (`static/css/common/variables.css`)
- ✅ Defined complete SciTeX bluish dark gray color system
- ✅ Created light variations for each color
- ✅ Mapped semantic variables to SciTeX colors
- ✅ Maintained backward compatibility with legacy variable names

#### 2. Component Styles
- ✅ **Header** (`components/header.css`): All buttons use SciTeX colors
- ✅ **Buttons** (`common/buttons.css`): Primary/secondary/hover states use SciTeX palette
- ✅ **Landing Page** (`landing.css`): Replaced Bootstrap fallbacks with SciTeX colors
- ✅ **Dark Mode** (`darkmode.css`): Complete rewrite using only SciTeX colors

#### 3. Color Consistency Fixes
- ✅ Replaced all `color: white` with `color: var(--white)`
- ✅ Replaced all `background-color: white` with `background-color: var(--white)`
- ✅ Removed Bootstrap color fallbacks like `#0056b3`
- ✅ Updated hover states to use SciTeX color variations
- ✅ Fixed hardcoded hex colors in component styles


...
```


### `./project_management/seo-enhancements-20250523.md`

```markdown
# SEO Enhancements Implementation

**Date**: 2025-05-23
**Status**: Completed

## SEO Improvements Implemented

### 1. ✅ Open Graph Meta Tags
**File**: `/templates/base.html`
- Added Open Graph tags for Facebook
- Added Twitter Card tags
- Customizable per page with Django blocks
- Default fallbacks for all pages

### 2. ✅ Robots.txt
**File**: `/static/robots.txt`
- Allows all crawlers to index public pages
- Blocks admin and user-specific areas
- Points to sitemap location
- Includes crawl-delay for considerate crawling

### 3. ✅ XML Sitemap
**File**: `/static/sitemap.xml`
- Includes all public pages
- Proper priority hierarchy (homepage: 1.0, products: 0.9)
- Change frequency indicators
- Last modified dates

## Technical Implementation

### Meta Tags Structure
```html
<meta property="og:type" content="website">
<meta property="og:title" content="SciTeX - Scientific Research Platform">
<meta property="og:description" content="Accelerate your scientific research...">
<meta property="og:image" content="https://scitex.ai/static/images/scitex-og-image.png">

<meta property="twitter:card" content="summary_large_image">
```

### Robots.txt Configuration
```
User-agent: *
Allow: /
Disallow: /admin/
Disallow: /core/dashboard/
Sitemap: https://scitex.ai/sitemap.xml
```

### Sitemap Structure

...
```


### `./project_management/settings-fixes-20250522.md`

```markdown
# SciTeX-Cloud Settings Fixes
**Date:** May 22, 2025

## Issues Fixed

1. **LOGGING Import Issue:**
   - The development settings file was trying to import `LOGGING` from config.settings, but this wasn't defined properly.
   - Solution: Moved the `LOGGING` configuration to `config/settings/base.py` which gets imported by all environment-specific settings files.

2. **URL Namespace Conflict:**
   - There was a duplicate namespace registration for the cloud_app URLs.
   - Solution: Changed the second namespace to "cloud_root" to avoid the conflict:
   ```python
   path("cloud/", include("apps.cloud_app.urls", namespace="cloud")),
   path("", include("apps.cloud_app.urls", namespace="cloud_root")),
   ```

3. **Landing Page Styling:**
   - Added proper styling references to achieve the silverish landing page background.
   - Updated the CSS files to include the required styles for the page.

## Implementation Details

1. **Updated Settings:**
   - Moved the LOGGING configuration from `config/settings.py` to `config/settings/base.py`
   - Updated `config/settings/development.py` to remove the explicit import of LOGGING
   - All environment-specific settings now inherit LOGGING from the base module

2. **URL Configuration:**
   - Fixed URL namespace issue in the main urls.py file
   - Updated URL references in templates to work with both namespaces

3. **Landing Page:**
   - Implemented the silver background theme for the landing page
   - Added the necessary CSS styles to recreate the look from the old version

## Recommendations for Future Development

1. **Settings Organization:**
   - Always keep shared configurations in `base.py` where they can be easily imported or extended
   - Use environment-specific settings files only for overrides or extensions

2. **URL Management:**
   - Be careful with URL namespace duplications and conflicts
   - Use namespaced URLs consistently in templates

3. **Static Files:**
   - Organize CSS files by function and component 
   - Keep global styles in clearly named files (e.g., main.css, index.css)
   - Use component-specific CSS for reusable UI elements

...
```


### `./project_management/stop.sh`

```bash
#!/bin/bash
# SciTeX Cloud Server Stopper - Clean & Simple

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${CYAN}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }

echo_info "🛑 Stopping SciTeX Cloud servers..."

# Stop nginx gracefully first
echo_info "🔸 Reloading nginx (to drop connections)..."
sudo systemctl reload nginx 2>/dev/null || echo_info "  (nginx reload skipped)"

# Kill all uWSGI processes (more comprehensive)
if pgrep -f "uwsgi" > /dev/null; then
    echo_info "🔸 Stopping all uWSGI processes..."
    pkill -f "uwsgi"
    sleep 2
    # Force kill if still running
    pkill -9 -f "uwsgi" 2>/dev/null || true
fi

# Kill Django development servers
if pgrep -f "manage.py runserver" > /dev/null; then
    echo_info "🔸 Stopping Django development servers..."
    pkill -f "manage.py runserver"
    pkill -9 -f "manage.py runserver" 2>/dev/null || true
    sleep 1
fi

# Clean up socket files
echo_info "🔸 Cleaning up socket files..."
rm -f /home/ywatanabe/proj/SciTeX-Cloud/uwsgi.sock
rm -f /home/ywatanabe/proj/SciTeX-Cloud/*.sock
rm -f /tmp/uwsgi*.sock 2>/dev/null || true

# Show remaining processes (for verification)
REMAINING=$(pgrep -f "uwsgi\|manage.py runserver" | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo_success "✅ All SciTeX Cloud servers stopped"
else
    echo_error "⚠️  Some processes may still be running: $REMAINING"
    pgrep -f "uwsgi\|manage.py runserver" || true
fi
...
```


### `./project_management/structure-improvement-plan.md`

```markdown
# Django Project Structure Improvement Plan

## Current Structure Analysis

The current SciTeX Web project structure has some non-standard Django elements and can be improved to better follow Django best practices as defined in our guidelines.

### Current Structure Strengths
- Separation of templates in Django app
- CSS organized in common and component directories
- Project management documentation
- Test files for TDD approach

### Current Structure Issues
- Non-standard Django project structure
- Missing key Django components (manage.py at root, etc.)
- Mixed JS/Django approach without clear separation
- Missing Django app organization (models, forms, etc.)

## Recommended Structure

Based on our Python Django Guidelines, here's the proposed structure:

```
scitex-web/
├── apps/                  # All Django applications
│   ├── about_app/         # Legal and contact pages
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/
│   │   │   └── about_app/
│   │   │       ├── contact.html
│   │   │       ├── privacy_policy.html
│   │   │       └── terms_of_use.html
│   │   ├── tests.py
│   │   ├── urls.py
│   │   └── views.py
│   ├── core_app/          # Core functionality
│   │   ├── admin.py
│   │   ├── apps.py
│   │   ├── __init__.py
│   │   ├── migrations/
│   │   ├── models.py
│   │   ├── templates/
│   │   │   └── core_app/
│   │   │       ├── base.html
│   │   │       ├── index.html
│   │   │       └── landing.html
```

...
```


### `./project_management/system-requirements-implementation-summary.md`

```markdown
# System Requirements Implementation Summary

**Date**: 2025-05-23
**Status**: Completed

## Overview

Successfully clarified and documented system requirements for all SciTeX ecosystem components, with special attention to:
- SciTeX-Engine's dependency on Claude Code
- SciTeX-Viz's dependency on Windows and SigmaPlot
- Linux compatibility and Apptainer containerization strategy

## Completed Tasks

### 1. Created Feature Request Document
- **File**: `/project_management/feature_requests/feature-request-system-requirements-clarification.md`
- **Content**: Comprehensive feature request outlining the need for clear system requirements documentation

### 2. Created System Requirements Documentation
- **File**: `/docs/SYSTEM_REQUIREMENTS.md`
- **Content**: Detailed system requirements for all SciTeX components including:
  - Platform compatibility
  - Dependencies (both open source and proprietary)
  - Container availability (Docker/Apptainer)
  - Licensing information
  - Hardware requirements
  - Support matrix

### 3. Updated Product Pages

#### SciTeX-Engine (`/apps/cloud_app/templates/cloud_app/products/engine.html`)
- Already had system requirements section
- Verified content aligns with new documentation

#### SciTeX-Doc (`/apps/cloud_app/templates/cloud_app/products/doc.html`)
- Already had system requirements section
- Verified content aligns with new documentation

#### SciTeX-Code (`/apps/cloud_app/templates/cloud_app/products/code.html`)
- Added comprehensive system requirements section
- Included platform compatibility, dependencies, container info, and licensing

#### SciTeX-Viz (`/apps/cloud_app/templates/cloud_app/products/viz.html`)
- Added detailed system requirements section
- Clearly stated Windows/SigmaPlot dependency
- Included note about Linux compatibility via Apptainer
- Mentioned future open-source alternative in development

### 4. Created Freemium Pricing Strategy
- **File**: `/docs/FREEMIUM_PRICING_STRATEGY.md`

...
```


### `./project_management/url-namespace-fix-20250522.md`

```markdown
# URL Namespace Fixes

**Date:** May 22, 2025

## Issue

The application was experiencing URL resolution errors with messages like:
```
Reverse for 'design' not found. 'design' is not a valid view function or pattern name.
```

This was caused by URLs in templates not properly using the namespaces defined in the URL configurations.

## Root Cause Analysis

1. **Multiple Namespace Registration**: 
   - The cloud_app URLs were registered in config/urls.py with two different namespaces:
     ```python
     path("cloud/", include("apps.cloud_app.urls", namespace="cloud")),
     path("", include("apps.cloud_app.urls", namespace="cloud_root")),
     ```
   - This means the same URL names were accessible via two different namespaces

2. **Inconsistent Namespace Usage**:
   - Templates were using direct URL names without namespaces
   - Some templates were using the 'cloud' namespace
   - None were using the 'cloud_root' namespace for root-level URLs

3. **Commented Out URLs**:
   - The page-specific URL routes in config/urls.py were commented out
   - These un-namespaced URLs were referenced in templates

## Fixes Applied

1. **Header Template**:
   - Updated all URL references to use correct namespaces
   - About dropdown links now use 'cloud_root:' namespace
   - Resource dropdown links now use 'cloud_root:' namespace
   - Contact link now uses 'cloud_root:' namespace
   - Donate button now uses 'cloud_root:' namespace

2. **Landing Page**:
   - Updated hero section button URLs to use 'cloud_root:' namespace
   - Updated CTA section button URLs to use 'cloud_root:' namespace

3. **Features Page**:
   - Updated CTA section button URLs to use 'cloud_root:' namespace

## Namespace Usage Guide


...
```


### `./project_management/USER_PLAN.md`

```markdown
# SciTeX Web Project - User Plan

## Project Overview
[Brief description of the project purpose and goals]

## Timeline
- **Start Date**: [Date]
- **End Date**: [Date]

## Milestones
1. **Phase 1**: [Description]
   - Task 1: [Description]
   - Task 2: [Description]
   - Deadline: [Date]

2. **Phase 2**: [Description]
   - Task 1: [Description]
   - Task 2: [Description]
   - Deadline: [Date]

3. **Phase 3**: [Description]
   - Task 1: [Description]
   - Task 2: [Description]
   - Deadline: [Date]

## Resources
- Team members: [List of team members and roles]
- Budget: [Budget allocation if applicable]
- Tools: [Required tools/technologies]

## Risks and Mitigation
| Risk | Impact | Likelihood | Mitigation Plan |
|------|--------|------------|-----------------|
| [Risk 1] | High/Medium/Low | High/Medium/Low | [Strategy] |
| [Risk 2] | High/Medium/Low | High/Medium/Low | [Strategy] |

## Communication Plan
- Weekly status meetings: [Day, Time]
- Reporting method: [Email, Project management tool, etc.]
- Key stakeholders: [List names]

## Success Criteria
- [Measurable outcome 1]
- [Measurable outcome 2]
- [Measurable outcome 3]

---
*This plan is a living document and will be updated as the project progresses.*

...
```


### `./README.md`

```markdown

# SciTeX-Cloud

Django-based online platform for accelerating scientific workflows and manuscript preparation.

🌐 **Live Website**: https://scitex.ai

⚠️ **Development Status**: This project is under active development and in a conceptual phase. Some instructions may be outdated or incomplete. Please verify configurations and paths before deployment.

## Quick Start

```bash
# Clone and setup
git clone git@github.com/ywatanabe1989/SciTeX-Cloud
cd SciTeX-Cloud
date && sudo apt-get install -y python3-dev build-essential

# Setup virtual environment
python3 -m venv .env
source .env/bin/activate

# Install dependencies
pip install -r docs/requirements/development.txt

# Initialize Django
python manage.py migrate
python manage.py collectstatic --noinput

# Run development server
./scripts/start_dev.sh

# Run tests
./tests/run_tests.sh --debug
```

## Project Structure

| Directory | Purpose | Key Files |
|-----------|---------|-----------|
| `apps/` | Django applications | cloud_app, search_app, viz_app |
| `config/` | Django settings | settings/, nginx_confs/, uwsgi.ini |
| `static/` | Frontend assets | CSS, JavaScript, images |
| `templates/` | Base HTML templates | base.html, partials/ |
| `tests/` | Test suite | run_tests.sh, test_*.py |
| `scripts/` | Deployment scripts | start_dev.sh, start_prod.sh |
| `docs/` | Documentation | HOW_TO_SETUP.md, components.md |


## Applications


...
```


### `./scripts/build_all_docs.sh`

```bash
#!/bin/bash
# Build Sphinx documentation for all SciTeX modules
# Each module has its own .env that auto-activates on cd

set -e

echo "========================================"
echo "Building SciTeX Documentation"
echo "========================================"

# Code module (includes Scholar)
echo ""
echo "📚 Building Code documentation..."
cd "$HOME/proj/scitex_repo/"
if [ -f "docs/conf.py" ]; then
    sphinx-build -b html docs docs/_build/html 2>&1 | grep -E "build succeeded|warning|error" | tail -5
    if [ -f "docs/_build/html/index.html" ]; then
        echo "  ✓ Code docs built successfully"
    else
        echo "  ✗ Code docs build failed"
    fi
else
    echo "  ! No Sphinx config found at docs/conf.py"
fi

# Writer module
echo ""
echo "📝 Building Writer documentation..."
cd "$HOME/proj/neurovista/paper"
if [ -f "docs/conf.py" ]; then
    sphinx-build -b html docs docs/_build/html 2>&1 | grep -E "build succeeded|warning|error" | tail -5
    if [ -f "docs/_build/html/index.html" ]; then
        echo "  ✓ Writer docs built successfully"
    else
        echo "  ✗ Writer docs build failed"
    fi
else
    echo "  ! No Sphinx config found"
fi

# Viz module
echo ""
echo "📊 Building Viz documentation..."
cd "$HOME/proj/SciTeX-Viz"
if [ -f "docs/conf.py" ]; then
    sphinx-build -b html docs docs/_build/html 2>&1 | grep -E "build succeeded|warning|error" | tail -5
    if [ -f "docs/_build/html/index.html" ]; then
        echo "  ✓ Viz docs built successfully"
    else
        echo "  ✗ Viz docs build failed"

...
```


### `./scripts/build_module_docs.sh`

```bash
#!/bin/bash
# Build Sphinx documentation for SciTeX modules
set -e

echo "Building SciTeX module documentation..."

# Code module (symlinked to scitex_repo)
if [ -d "externals/code" ]; then
    echo "Building Code docs..."
    cd ~/proj/scitex_repo
    if [ -f "docs/conf.py" ]; then
        sphinx-build -b html docs docs/_build/html
        echo "  ✓ Code docs built"
    else
        echo "  ! No Sphinx config found, initializing..."
        cd docs
        sphinx-quickstart -q -p "SciTeX Code" -a "Yusuke Watanabe" -v "2.0" --ext-autodoc --ext-viewcode --makefile --no-batchfile
        sphinx-build -b html . _build/html
        echo "  ✓ Code docs initialized and built"
    fi
    cd -
fi

# Scholar (part of Code)
echo "  → Scholar docs included in Code"

# Writer module
if [ -d "externals/paper" ]; then
    echo "Building Writer docs..."
    cd ~/proj/neurovista/paper
    if [ -f "docs/conf.py" ]; then
        sphinx-build -b html docs docs/_build/html
        echo "  ✓ Writer docs built"
    else
        echo "  ! No Sphinx config - needs setup"
    fi
    cd -
fi

# Viz module
if [ -d "externals/viz" ]; then
    echo "Building Viz docs..."
    cd ~/win/documents/SciTeX-Viz
    if [ -f "docs/conf.py" ]; then
        sphinx-build -b html docs docs/_build/html
        echo "  ✓ Viz docs built"
    else
        echo "  ! No Sphinx config - needs setup"
    fi
    cd -

...
```


### `./scripts/create_viz_demo.sh`

```bash
#!/bin/bash
# Create Viz demo video from GIFs in SciTeX-Viz directory
# Run from: /home/ywatanabe/win/documents/SciTeX-Viz/templates/gif

set -e

# Key plot GIFs to showcase
GIFS=(
  "line-line-line"
  "scatter-scatter"
  "bar-bar-bar"
  "violin-violin"
  "box-box-box"
  "heatmap"
  "polar-polar"
  "contour"
)

# Create temp directory
TMP_DIR="/home/ywatanabe/proj/scitex-cloud/tmp/viz_demo"
mkdir -p "$TMP_DIR"

echo "Extracting frames from GIFs..."
i=0
for pattern in "${GIFS[@]}"; do
  gif=$(ls ${pattern}*_cropped.gif 2>/dev/null | head -1)
  if [ -f "$gif" ]; then
    ffmpeg -i "$gif" -vframes 1 -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2,format=yuv420p" -y "$TMP_DIR/frame_$(printf '%03d' $i).png" 2>&1 | grep -v "^frame=\|^video:"
    echo "  ✓ $(basename $gif)"
    ((i++))
  fi
done

echo "Creating video..."
OUTPUT="/home/ywatanabe/proj/scitex-cloud/static/videos/viz-demo.mp4"
ffmpeg -framerate 1 -i "$TMP_DIR/frame_%03d.png" -c:v libx264 -pix_fmt yuv420p -y "$OUTPUT" 2>&1 | tail -3

echo "✓ Created: $OUTPUT"
ls -lh "$OUTPUT"

# Cleanup
rm -rf "$TMP_DIR"

...
```


### `./scripts/create_viz_demo_video.sh`

```bash
#!/bin/bash
# Create Viz demo video from GIFs

set -e

VIZ_DIR="/home/ywatanabe/win/documents/SciTeX-Viz/templates/gif"
OUTPUT="static/videos/viz-demo.mp4"
TMP_DIR="tmp/viz_frames"

mkdir -p "$TMP_DIR"
mkdir -p static/videos

echo "Converting GIFs to frames..."

# Select key plot types for demo
GIFS=(
  "line-line"
  "scatter-scatter"
  "bar-bar"
  "violin-violin"
  "box-box"
  "heatmap"
  "polar-polar"
  "contour"
)

i=0
for gif_pattern in "${GIFS[@]}"; do
  gif_file=$(find "$VIZ_DIR" -name "${gif_pattern}*_cropped.gif" | head -1)
  if [ -f "$gif_file" ]; then
    # Extract first frame from GIF
    ffmpeg -i "$gif_file" -vframes 1 -y "$TMP_DIR/frame_$(printf "%03d" $i).png" 2>/dev/null
    echo "  ✓ $gif_pattern"
    ((i++))
  fi
done

echo "Creating video from frames..."
ffmpeg -framerate 1 -pattern_type glob -i "$TMP_DIR/frame_*.png" \
  -c:v libx264 -pix_fmt yuv420p -vf "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2" \
  -y "$OUTPUT" 2>/dev/null

# Cleanup
rm -rf "$TMP_DIR"

echo "✓ Viz demo video created: $OUTPUT"
ls -lh "$OUTPUT"

...
```


### `./scripts/demo.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
SciTeX Code Framework Demo
Demonstrates the complete research workflow with automatic session management.
"""

import sys
import matplotlib.pyplot as plt
import scitex as stx

def main(args):
    """Demo of SciTeX capabilities."""

    # 1. Universal I/O - Load data
    print("📂 Loading data...")
    # data = stx.io.load("data.csv")  # Auto-detects format

    # 2. Session management creates organized structure
    print(f"📁 Session directory: {CONFIG['SDIR']}")
    print(f"   ├── logs/ (stdout.log, stderr.log)")
    print(f"   ├── CONFIGS/ (CONFIG.yaml, CONFIG.pkl)")
    print(f"   └── figs/")

    # 3. Statistical testing (23 tests available)
    print("\n📊 Statistical testing...")
    # result = stx.stats.ttest_ind(control, treatment, plot=True)
    print("   - Parametric & non-parametric tests")
    print("   - Effect sizes & power analysis")
    print("   - Export to 9 formats")

    # 4. Machine Learning
    print("\n🧠 ML & AI capabilities...")
    print("   - PyTorch training utilities")
    print("   - GenAI: 7 providers (OpenAI, Anthropic, Google...)")
    print("   - Cost tracking enabled")

    # 5. Publication plots
    print("\n📈 Creating publication-ready plots...")
    fig, ax = plt.subplots()
    ax.plot([1, 2, 3], [1, 4, 9])
    ax.set_title("Sample Plot")
    stx.io.save(fig, "demo_plot.png")  # Auto-saves data as CSV
    print("   ✓ Saved: demo_plot.png + data CSV")

    return 0


def parse_args():
    """Parse command line arguments."""

...
```


### `./scripts/dev/monitor.sh`

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 04:50:00 (ywatanabe)"
# File: ./scripts/monitor.sh

# SciTeX Cloud Server Monitoring Script

APP_HOME="/home/ywatanabe/proj/SciTeX-Cloud"
LOG_DIR="/var/log/scitex-cloud"

# ANSI colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[OK]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

show_header() {
    echo "======================================"
    echo "    SciTeX Cloud Server Monitor"
    echo "======================================"
    echo "Timestamp: $(date)"
    echo ""
}

check_processes() {
    echo_info "Checking running processes..."
    
    # Check Django development server
    if pgrep -f "manage.py runserver" > /dev/null; then
        echo_success "Django development server is running"
        DEV_PID=$(pgrep -f "manage.py runserver")
        echo "  PID: $DEV_PID"
    else
        echo_warning "Django development server is not running"
    fi
    
    # Check uWSGI
    if pgrep -f uwsgi > /dev/null; then
        echo_success "uWSGI is running"
        UWSGI_PIDS=$(pgrep -f uwsgi | tr '\n' ' ')
        echo "  PIDs: $UWSGI_PIDS"
    else
        echo_warning "uWSGI is not running"
    fi

...
```


### `./scripts/dev/start_dev_background.sh`

```bash
#!/bin/bash
# Start Django development server in background with proper environment

# Set the script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"

cd "$PROJECT_ROOT"

# Kill any existing Django servers on port 8000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true

# Set environment variables
export SCITEX_DJANGO_SECRET_KEY='django-insecure-development-key-12345'
export DJANGO_SETTINGS_MODULE=config.settings.development

# Start the server in background
echo "Starting Django development server..."
nohup python manage.py runserver 0.0.0.0:8000 > server.log 2>&1 &
SERVER_PID=$!

echo "Server started with PID: $SERVER_PID"
echo "Logs available at: $PROJECT_ROOT/server.log"

# Wait a moment for server to start
sleep 3

# Check if server is running
if curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/ | grep -q "200\|302"; then
    echo "✅ Server is running at http://localhost:8000/"
    echo "✅ Also accessible at http://172.19.33.56:8000/"
else
    echo "⚠️  Server may have issues. Check server.log for details."
fi
...
```


### `./scripts/dev/start_dev.sh`

```bash
#!/bin/bash
# SciTeX Cloud Development Server Startup Script

set -e  # Exit on any error

echo "🚀 Starting SciTeX Cloud Development Server..."

# Check if virtual environment exists, create if not
if [ ! -d "env" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv env
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source env/bin/activate

# Set Django settings module
export DJANGO_SETTINGS_MODULE=config.settings.development

# Install/upgrade dependencies
echo "📚 Installing development dependencies..."
pip install --upgrade pip
pip install -r docs/requirements/development.txt

# Check if manage.py exists
if [ ! -f "manage.py" ]; then
    echo "❌ manage.py not found! Make sure you're in the correct directory."
    exit 1
fi

# Run Django checks
echo "🔍 Running Django system checks..."
python manage.py check

# Apply database migrations
echo "🗄️  Applying database migrations..."
python manage.py migrate

# Collect static files (for development testing)
echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

# Create superuser if needed (optional)
echo "👤 Creating superuser (optional, press Ctrl+C to skip)..."
python manage.py createsuperuser --noinput --username admin --email admin@scitex.ai || echo "Superuser creation skipped"

echo ""
echo "✅ Setup complete!"
echo ""

...
```


### `./scripts/dev/start_dev_windows.sh`

```bash
#!/bin/bash
# SciTeX Cloud Server Launcher - Simple & Essential

APP_HOME="$(cd $(dirname ${BASH_SOURCE[0]}) && pwd)"

# Colors
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${CYAN}$1${NC}"; }
echo_success() { echo -e "${GREEN}$1${NC}"; }
echo_error() { echo -e "${RED}$1${NC}"; }

# Show help
show_help() {
    echo_info "SciTeX Cloud Server Launcher"
    echo "Usage: ./start.sh [mode]"
    echo ""
    echo "Modes:"
    echo "  dev     - Development server (default)"
    echo "  win     - Development with Windows access"
    echo "  prod    - Production server"
    echo ""
    exit 0
}

# Set mode
MODE="${1:-dev}"
case $MODE in
    dev|win|prod) ;;
    --help|-h) show_help ;;
    *) echo_error "Invalid mode: $MODE"; show_help ;;
esac

# Stop any running servers first
echo_info "🛑 Stopping any running servers..."
"$APP_HOME/stop.sh"

# Load secrets
SECRETS_FILE="/home/ywatanabe/.bash.d/secrets/000_ENV_SCITEX.src"
[ -f "$SECRETS_FILE" ] && source "$SECRETS_FILE"

# Activate virtual environment
if [ -d "$APP_HOME/.env" ]; then
    source "$APP_HOME/.env/bin/activate"
else
    echo_error "Virtual environment not found. Run: python3 -m venv .env"

...
```


### `./scripts/format_django_templates.sh`

```bash
#!/bin/bash
# Auto-format Django templates with djhtml
# Usage: ./scripts/format_django_templates.sh [directory]

set -e

DIR="${1:-.}"

# Check if djhtml is installed
if ! command -v djhtml &> /dev/null; then
    echo "Installing djhtml..."
    pip install djhtml
fi

echo "Formatting Django templates in: $DIR"
djhtml -i -t 2 "$DIR"

echo "✓ Templates formatted with 2-space indentation"

...
```


### `./scripts/format_templates.py`

```python
#!/usr/bin/env python3
"""
Auto-format Django templates with proper indentation.
Usage: python scripts/format_templates.py <file_or_directory>
"""

import re
import sys
from pathlib import Path


def format_django_template(content):
    """Format Django template with proper indentation."""
    lines = content.split('\n')
    formatted = []
    indent_level = 0
    indent_char = '  '  # 2 spaces

    # Block tags that increase indentation
    opening_tags = [
        'block', 'if', 'for', 'with', 'autoescape', 'filter', 'spaceless',
        'verbatim', 'comment', 'blocktrans', 'ifequal', 'ifnotequal',
        'ifchanged', 'regroup'
    ]

    # Block tags that decrease indentation
    closing_tags = [f'end{tag}' for tag in opening_tags]
    middle_tags = ['else', 'elif', 'empty']

    for line in lines:
        stripped = line.strip()

        # Check for closing tags
        if any(f'{{% {tag}' in stripped or f'{{%{tag}' in stripped for tag in closing_tags):
            indent_level = max(0, indent_level - 1)
            formatted.append(indent_char * indent_level + stripped)
            continue

        # Check for middle tags (else, elif, empty)
        if any(f'{{% {tag}' in stripped or f'{{%{tag}' in stripped for tag in middle_tags):
            formatted.append(indent_char * max(0, indent_level - 1) + stripped)
            continue

        # Add current line with current indentation
        if stripped:  # Only add indentation to non-empty lines
            formatted.append(indent_char * indent_level + stripped)
        else:
            formatted.append('')

        # Check for opening tags (increase indentation for next line)

...
```


### `./scripts/prod/deploy_prod.sh`

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-22 04:47:00 (ywatanabe)"
# File: ./scripts/deploy_prod.sh

# SciTeX Cloud Production Deployment Script
# Based on best practices from airight project

set -e  # Exit on any error

APP_HOME="/home/ywatanabe/proj/SciTeX-Cloud"
LOG_DIR="/var/log/scitex-cloud"
RUN_DIR="/var/run/scitex-cloud"
PYTHON_BIN="$APP_HOME/env/bin/python"
MANAGE_PY="$PYTHON_BIN $APP_HOME/manage.py"

# ANSI colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }

usage() {
    echo "SciTeX Cloud Production Deployment"
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -d, --deploy       Full deployment (migrate, static, start)"
    echo "  -m, --migrate      Run database migrations only"
    echo "  -s, --static       Collect static files only"
    echo "  -r, --restart      Restart services only"
    echo "  -c, --check        Check system configuration"
    echo "  -h, --help         Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 -d              # Full deployment"
    echo "  $0 -m -s           # Migrate and collect static"
    echo "  $0 -r              # Restart services"
    exit 1
}

check_dependencies() {
    echo_info "Checking dependencies..."
    

...
```


### `./scripts/prod/monitor_prod.sh`

```bash
#!/bin/bash
# SciTeX Cloud Production Monitoring Script

APP_HOME="/home/ywatanabe/proj/SciTeX-Cloud"
PRODUCTION_URL="https://scitex.ai"

# ANSI colors for output
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

echo_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
echo_success() { echo -e "${GREEN}[OK]${NC} $1"; }
echo_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
echo_error() { echo -e "${RED}[ERROR]${NC} $1"; }
echo_highlight() { echo -e "${CYAN}[METRIC]${NC} $1"; }

show_header() {
    echo "=============================================="
    echo "    SciTeX Cloud Production Monitor"
    echo "=============================================="
    echo "Timestamp: $(date)"
    echo "Production URL: $PRODUCTION_URL"
    echo ""
}

check_production_services() {
    echo_info "Checking production services..."
    
    # Check Nginx
    if systemctl is-active --quiet nginx; then
        echo_success "Nginx service is active"
    else
        echo_error "Nginx service is not active"
    fi
    
    # Check uWSGI processes
    if pgrep -f uwsgi > /dev/null; then
        UWSGI_COUNT=$(pgrep -f uwsgi | wc -l)
        echo_success "uWSGI is running ($UWSGI_COUNT workers)"
        UWSGI_PIDS=$(pgrep -f uwsgi | tr '\n' ' ')
        echo_highlight "uWSGI PIDs: $UWSGI_PIDS"
    else
        echo_error "uWSGI is not running"
    fi
    
    echo ""

...
```


### `./scripts/prod/start_prod.sh`

```bash
#!/bin/bash
# SciTeX Cloud Production Server Startup Script

set -e  # Exit on any error

echo "🏭 Starting SciTeX Cloud Production Server..."

# Load environment variables from centralized secrets
SECRETS_FILE="/home/ywatanabe/.bash.d/secrets/000_ENV_SCITEX.src"
if [ -f "$SECRETS_FILE" ]; then
    echo "🔐 Loading environment variables from centralized secrets..."
    source "$SECRETS_FILE"
else
    echo "⚠️ Centralized secrets file not found: $SECRETS_FILE"
    echo "💡 Using fallback environment settings"
fi

# Activate virtual environment
if [ -d "env" ]; then
    source env/bin/activate
else
    echo "❌ Virtual environment not found! Run start_dev.sh first."
    exit 1
fi

# Set up log directories
LOG_DIR="/var/log/scitex-cloud"
if [ ! -d "$LOG_DIR" ]; then
    echo "📂 Creating log directory at $LOG_DIR..."
    # Use sudo if running as non-root user
    if [ $(id -u) -ne 0 ]; then
        sudo mkdir -p $LOG_DIR
        sudo chmod 755 $LOG_DIR
        sudo chown -R $(whoami):$(whoami) $LOG_DIR
    else
        mkdir -p $LOG_DIR
        chmod 755 $LOG_DIR
    fi
fi

# Install dependencies
echo "📚 Installing dependencies..."
pip install -r requirements.txt

# Set production environment
export DJANGO_SETTINGS_MODULE=config.settings.production

# Run Django checks
echo "🔍 Running Django system checks (production)..."
python manage.py check --deploy

...
```


### `./scripts/scitex_server.sh`

```bash
#!/bin/bash
# -*- coding: utf-8 -*-
# Timestamp: "2025-05-23 07:50:00 (ywatanabe)"
# File: ./scripts/scitex_server.sh
# ----------------------------------------
# SciTeX Cloud Server Management Script
# Following AIRight's best practices for server management

# Script directory - resolve symlinks to get actual location
SOURCE="${BASH_SOURCE[0]}"
while [ -h "$SOURCE" ]; do
  SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
  SOURCE="$(readlink "$SOURCE")"
  [[ $SOURCE != /* ]] && SOURCE="$SCRIPT_DIR/$SOURCE"
done
SCRIPT_DIR="$(cd -P "$(dirname "$SOURCE")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
LOG_DIR="$PROJECT_ROOT/logs"
PID_DIR="$PROJECT_ROOT/run"

# Create directories if they don't exist
mkdir -p "$LOG_DIR" "$PID_DIR"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
WHITE='\033[0;37m'
NC='\033[0m' # No Color

# Helper functions
log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Usage information
show_usage() {
    cat << EOF
SciTeX Cloud Server Management

Usage: $0 [COMMAND] [OPTIONS]

COMMANDS:
    start       Start the server (default: development mode)
    stop        Stop all SciTeX Cloud processes
    restart     Restart the server

...
```


### `./scripts/utils/check_logs.sh`

```bash
#!/bin/bash
# Check and display SciTeX Cloud log files
# Usage: ./scripts/check_logs.sh [log_type] [lines]
#   log_type: app, django, uwsgi, error, all (default: all)
#   lines: number of lines to show (default: 20)

# Log directory
LOG_DIR="/var/log/scitex-cloud"

# Default values
LOG_TYPE=${1:-"all"}
LINES=${2:-20}

# ANSI colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

# Check if log directory exists
if [ ! -d "$LOG_DIR" ]; then
    echo -e "${RED}Error: Log directory $LOG_DIR does not exist!${NC}"
    echo "Are you in development mode? Checking for logs/ directory..."
    
    if [ -d "./logs" ]; then
        LOG_DIR="./logs"
        echo -e "${GREEN}Found local logs directory. Using it instead.${NC}"
    else
        echo -e "${YELLOW}No logs directory found. Attempting to create logs/ directory...${NC}"
        mkdir -p logs
        LOG_DIR="./logs"
        touch $LOG_DIR/app.log $LOG_DIR/django.log $LOG_DIR/error.log
        echo -e "${GREEN}Created logs directory and log files.${NC}"
    fi
fi

function show_log {
    local file=$1
    local title=$2
    local lines=$3
    
    if [ -f "$file" ]; then
        echo -e "\n${BLUE}=== $title (last $lines lines) ===${NC}"
        if [ -s "$file" ]; then
            tail -n $lines "$file"
        else
            echo -e "${YELLOW}Log file is empty.${NC}"

...
```


### `./scripts/utils/create_initial_user.py`

```python
#!/usr/bin/env python
"""
Create initial user for SciTeX Cloud platform
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.core_app.models import UserProfile

def create_initial_user():
    """Create the initial user and profile"""
    username = 'ywatanabe'
    email = 'ywatanabe@unimelb.edu.au'
    password = 'ywatanabe123'
    first_name = 'Yusuke'
    last_name = 'Watanabe'
    
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists.")
        user = User.objects.get(username=username)
        print(f"Existing user: {user.username} ({user.email})")
        return user
    
    # Create the user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password,
        first_name=first_name,
        last_name=last_name,
        is_staff=True,  # Give admin access
        is_superuser=True  # Give superuser access
    )
    
    # Create or update UserProfile
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={
            'academic_title': 'Researcher',
            'affiliation': 'University of Melbourne',
            'is_academic': True,
            'is_academic_ja': False,  # Australian university
            'allow_messages': True,

...
```


### `./scripts/utils/create_user.py`

```python
#!/usr/bin/env python
import os
import django
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User

# Create user account
username = 'ywatanabe'
email = 'ywata1989@gmail.com'
password = 'scitex2025!'  # Temporary password

try:
    # Check if user already exists
    if User.objects.filter(username=username).exists():
        print(f"User '{username}' already exists")
        user = User.objects.get(username=username)
        user.email = email
        user.save()
        print(f"Updated email for user '{username}' to '{email}'")
    else:
        # Create new user
        user = User.objects.create_user(
            username=username,
            email=email,
            password=password,
            first_name='Yusuke',
            last_name='Watanabe'
        )
        print(f"Created user '{username}' with email '{email}'")
        print(f"Temporary password: {password}")
        print("Please change password after first login")
        
    # Make user staff and superuser for admin access
    user.is_staff = True
    user.is_superuser = True
    user.save()
    print(f"User '{username}' now has admin privileges")
    
except Exception as e:
    print(f"Error creating user: {e}")
...
```


### `./scripts/utils/reset_accounts.py`

```python
#!/usr/bin/env python3
"""
Reset all user accounts and clean database for fresh start
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth import get_user_model
from apps.core_app.models import UserProfile, EmailVerification, Project, Organization
from apps.cloud_app.models import Subscription, APIKey, Donation

User = get_user_model()

def safe_delete_model(model_class, model_name):
    """Safely delete all objects from a model, handling table not found errors"""
    try:
        count = model_class.objects.count()
        if count > 0:
            model_class.objects.all().delete()
            print(f"   ✓ {model_name} deleted ({count} items)")
        else:
            print(f"   ✓ {model_name} already empty")
        return True
    except Exception as e:
        print(f"   ⚠️  {model_name} deletion skipped: {str(e)}")
        return False

def reset_all_accounts():
    """Reset all user accounts and related data"""
    print("🔄 Resetting all user accounts...")
    
    # Count existing data safely
    try:
        user_count = User.objects.count()
        print(f"📊 Found {user_count} user accounts")
    except:
        user_count = 0
        print("📊 Unable to count users (table may not exist)")
    
    if user_count == 0:
        print("✅ No user accounts found. Database is already clean.")
        return True
    
    try:
        print("\n🗑️  Deleting user data...")

...
```


### `./scripts/utils/reset_database_with_permissions.py`

```python
#!/usr/bin/env python
"""
Reset Database with Enhanced Group and Permission System

This script will:
1. Delete the existing database
2. Remove all migration files (except __init__.py)
3. Create fresh migrations
4. Apply migrations to create new database schema
5. Create a superuser account

Run this script when you need a clean database with the new permission system.
"""

import os
import sys
import django
from pathlib import Path

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

def reset_database():
    """Reset the database and migrations"""
    print("🔄 Resetting SciTeX Cloud database with new permission system...")
    
    # 1. Remove database file
    db_path = Path('db.sqlite3')
    if db_path.exists():
        print("  ✓ Removing existing database...")
        os.remove(db_path)
    
    # 2. Remove migration files (keep __init__.py)
    apps_to_reset = [
        'apps/core_app/migrations',
        'apps/cloud_app/migrations', 
        'apps/scholar/migrations',
        'apps/writer_app/migrations',
        'apps/viz_app/migrations',
        'apps/code_app/migrations',
        'apps/engine_app/migrations',
        'apps/monitoring_app/migrations'
    ]
    
    for migration_dir in apps_to_reset:
        migration_path = Path(migration_dir)
        if migration_path.exists():
            print(f"  ✓ Cleaning migrations in {migration_dir}...")
            for file in migration_path.glob('*.py'):

...
```


### `./scripts/utils/setup_externals.sh`

```bash
#!/bin/bash
# SciTeX-Cloud External Components Setup Script
# Automatically clones and configures all SciTeX ecosystem components

set -e

EXTERNALS_DIR="$(dirname "$0")/../externals"
cd "$EXTERNALS_DIR"

echo "🚀 Setting up SciTeX External Components..."

# SciTeX component repositories
declare -A COMPONENTS=(
    ["SciTeX-Writer"]="https://github.com/ywatanabe1989/SciTeX-Writer.git"
    ["SciTeX-Code"]="https://github.com/ywatanabe1989/SciTeX-Code.git"
    ["SciTeX-Viz"]="https://github.com/ywatanabe1989/SciTeX-Viz.git"
    ["SciTeX-Scholar"]="https://github.com/ywatanabe1989/SciTeX-Scholar.git"
    ["SciTeX-Example-Research-Project"]="https://github.com/ywatanabe1989/SciTeX-Example-Research-Project.git"
)

# Clone or update each component
for component in "${!COMPONENTS[@]}"; do
    if [ -d "$component" ]; then
        echo "📦 Updating $component..."
        cd "$component"
        git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || echo "⚠️  Could not update $component"
        cd ..
    else
        echo "📥 Cloning $component..."
        git clone "${COMPONENTS[$component]}" "$component"
    fi
done

# Set up SciTeX-Engine (if available)
if [ ! -d "SciTeX-Engine" ]; then
    echo "ℹ️  SciTeX-Engine not available yet (planned component)"
fi

# Create integration status file
cat > integration_status.json << EOF
{
  "timestamp": "$(date -Iseconds)",
  "components": {
    "SciTeX-Writer": {
      "status": "active",
      "integration": "template_system",
      "description": "LaTeX template system for cloud compilation"
    },
    "SciTeX-Code": {
      "status": "ready", 

...
```


### `./scripts/utils/system_validation.py`

```python
#!/usr/bin/env python3
"""
Comprehensive system validation for SciTeX Cloud platform
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth import get_user_model
from django.test import Client
from django.urls import reverse
from apps.core_app.models import UserProfile, EmailVerification
from apps.core_app.services import EmailService
import json

User = get_user_model()

class SystemValidator:
    def __init__(self):
        self.client = Client()
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }
    
    def log_test(self, test_name, passed, message=""):
        status = "PASS" if passed else "FAIL"
        self.results['tests'].append({
            'name': test_name,
            'status': status,
            'message': message
        })
        if passed:
            self.results['passed'] += 1
        else:
            self.results['failed'] += 1
        print(f"[{status}] {test_name}: {message}")
    
    def test_homepage(self):
        """Test homepage accessibility"""
        try:
            response = self.client.get('/')
            self.log_test("Homepage Access", response.status_code == 200, 
                         f"Status: {response.status_code}")
        except Exception as e:

...
```


### `./scripts/utils/update_user_info.py`

```python
#!/usr/bin/env python
"""
Update user information for SciTeX Cloud platform
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
django.setup()

from django.contrib.auth.models import User
from apps.core_app.models import UserProfile

def update_user_info():
    """Update the user with the requested information"""
    username = 'ywatanabe'
    new_email = 'ywatanabe@unimelb.edu.au'
    new_password = 'ywatanabe123'
    first_name = 'Yusuke'
    last_name = 'Watanabe'
    
    try:
        # Get the existing user
        user = User.objects.get(username=username)
        print(f"Found existing user: {user.username}")
        print(f"Current email: {user.email}")
        
        # Update user information
        user.email = new_email
        user.first_name = first_name
        user.last_name = last_name
        user.set_password(new_password)  # This will hash the password properly
        user.is_staff = True
        user.is_superuser = True
        user.save()
        
        print(f"✅ Updated user information:")
        print(f"  Username: {user.username}")
        print(f"  Email: {user.email}")
        print(f"  Name: {user.first_name} {user.last_name}")
        print(f"  Staff: {user.is_staff}")
        print(f"  Superuser: {user.is_superuser}")
        
        # Update or create UserProfile
        profile, created = UserProfile.objects.get_or_create(
            user=user,
            defaults={
                'academic_title': 'Researcher',

...
```


### `./server.sh -> scripts/scitex_server.sh`

```bash

...
```


### `./static/css/README.md`

```markdown
# SciTeX Web - CSS Architecture

This document explains the CSS architecture for the SciTeX Web application.

## Directory Structure

```
css/
├── common/              # Reusable CSS modules
│   ├── variables.css    # CSS variables for colors, fonts, spacing, etc.
│   ├── reset.css        # CSS reset/normalize
│   ├── layout.css       # Layout utilities (grid, flexbox, spacing)
│   ├── typography.css   # Typography styles
│   ├── buttons.css      # Button styles
│   ├── forms.css        # Form styles
│   └── cards.css        # Card styles
├── components/          # Component-specific styles
│   ├── header.css       # Header styles
│   ├── footer.css       # Footer styles
│   ├── hero.css         # Hero section styles
│   └── features.css     # Features section styles
├── index.css            # Main CSS file that imports all other files
└── main.css             # Legacy CSS file (to be removed)
```

## Usage Guide

### 1. CSS Variables

Define all colors, fonts, spacing, etc. as CSS variables in `variables.css`:

```css
:root {
  --primary-color: #2c3e50;
  --spacing-md: 1rem;
  /* etc. */
}
```

To use a variable:

```css
.element {
  color: var(--primary-color);
  padding: var(--spacing-md);
}
```

### 2. Layout Utilities


...
```


### `./static/images/README.md`

```markdown
# SciTeX Image Assets

This directory contains image assets used in the SciTeX website.

## SVG Icons

We use SVG icons for product representation. These follow a consistent design pattern:

- `scitex-cloud-icon.svg` - Cloud storage and platform icon
- `scitex-code-icon.svg` - Code editor and analysis icon
- `scitex-doc-icon.svg` - Document and LaTeX icon
- `scitex-engine-icon.svg` - AI engine icon
- `scitex-viz-icon.svg` - Data visualization icon
- `scitex-search-icon.svg` - Research search icon

All icons follow these design guidelines:
- Primary color: #4a6baf (SciTeX blue)
- Secondary color: #90b1e2 (SciTeX light blue) at 30% opacity for fills
- 64x64 pixel viewBox
- 3px stroke width for primary outlines

## Usage

These icons are used throughout the site, particularly on the landing page to represent different SciTeX products and modules.

Example usage in HTML:
```html
<img src="/static/images/scitex-cloud-icon.svg" alt="SciTeX Cloud" width="64" height="64">
```

## Notes for Designers

When creating new icons, please maintain consistency with the existing design language:
- Use the SciTeX color palette
- Maintain simple, clean lines
- Use consistent stroke widths
- Avoid gradients or complex effects that may not scale well

---

*Last updated: May 21, 2025*

...
```


### `./static/videos/README.md`

```markdown
# SciTeX Video Assets

This directory contains video assets used in the SciTeX website.

## Current Videos

- **SciTeX-Demo-v01.mp4**: Main product demonstration video (5 min, 8x speed).

## Video Guidelines

When adding new videos to this directory, please follow these guidelines:

1. **Naming Convention**: Use descriptive names with version numbers (e.g., `ProductName-Purpose-v01.mp4`).

2. **Optimization**: Videos should be optimized for web delivery:
   - Use H.264 codec for maximum compatibility
   - Compress to a reasonable file size (aim for <100MB if possible)
   - Use appropriate resolution (720p or 1080p recommended)

3. **Documentation**: Update this README when adding new videos.

4. **Thumbnails**: Consider creating thumbnail images for video previews (e.g., `VideoName-thumb.jpg`).

## Implementation Notes

Videos are integrated into the site in the following locations:

- Landing page (`landing.html`) - Demo section with smaller embedded video
- Dedicated demo page (`demo.html`) - Full-featured video viewing experience
 
The embedded videos use the `preload="none"` attribute to prevent automatic downloading on page load, saving bandwidth for users who don't watch the videos.

## License Information

These videos are proprietary to SciTeX and should not be redistributed without permission.

---

*Last updated: May 21, 2025*

...
```


### `./stop.sh`

```bash

...
```


### `./templates/partials/README.md`

```markdown
# SciTeX Template Partials

Reusable template components for consistent UI across the platform.

## Directory Structure

```
partials/
├── forms/              # Form components
│   ├── input_with_icon.html
│   └── password_with_toggle.html
├── cards/              # Card components
│   ├── module_card.html
│   └── feature_card.html
├── sections/           # Page sections
├── header.html         # Site header
└── footer.html         # Site footer
```

## Usage Examples

### Form Components

**Input with Icon:**
```django
{% include 'partials/forms/input_with_icon.html' with
   type='email'
   id='email'
   name='email'
   label='Email Address'
   placeholder='Enter your email'
   icon='fa-envelope'
   required=True
   help_text='We will never share your email'
%}
```

**Password with Toggle:**
```django
{% include 'partials/forms/password_with_toggle.html' with
   id='password'
   name='password'
   label='Password'
   placeholder='Enter password'
   required=True
   help_text='Minimum 8 characters'
   minlength=8
%}
```


...
```


### `./tests/custom/test_citation_export.py`

```python
#!/usr/bin/env python3
"""
Test script for Scholar citation export functionality
"""
import os
import sys
import json

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.test import Client
from django.contrib.auth.models import User

from apps.scholar.models import SearchIndex, Author, Journal, AuthorPaper
from apps.scholar.utils import CitationExporter

def create_test_data():
    """Create test paper data for citation export testing"""
    
    # Create test journal
    journal, created = Journal.objects.get_or_create(
        name="Nature Neuroscience",
        defaults={
            'abbreviation': 'Nat. Neurosci.',
            'issn': '1097-6256',
            'impact_factor': 21.126,
            'publisher': 'Nature Publishing Group'
        }
    )
    
    # Create test authors
    author1, created = Author.objects.get_or_create(
        first_name="John",
        last_name="Smith",
        defaults={
            'orcid': '0000-0000-0000-0001',
            'email': 'john.smith@university.edu',
            'affiliation': 'University of Science'
        }
    )
    
    author2, created = Author.objects.get_or_create(
        first_name="Jane",
        last_name="Doe",
        defaults={
            'orcid': '0000-0000-0000-0002',

...
```


### `./tests/custom/test_otp_email.py`

```python
#!/usr/bin/env python3
"""
Test script for OTP email functionality
"""
import os
import sys
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from apps.core_app.services import EmailService
from apps.core_app.models import EmailVerification
from django.contrib.auth import get_user_model

User = get_user_model()

def test_email_service():
    """Test the email service directly"""
    print("Testing OTP email service...")
    
    # Test with a dummy email
    test_email = "test@example.com"
    test_otp = "123456"
    
    try:
        success, message = EmailService.send_otp_email(
            email=test_email,
            otp_code=test_otp,
            verification_type='signup'
        )
        
        print(f"Email send result: Success={success}, Message={message}")
        return success
        
    except Exception as e:
        print(f"Error testing email service: {str(e)}")
        return False

def test_verification_creation():
    """Test OTP verification creation"""
    print("Testing OTP verification creation...")
    
    try:
        # Create a test verification
        verification = EmailVerification.create_verification(
            email="test@example.com",
            verification_type='signup',
            user=None

...
```


### `./tests/custom/test_simple_citation.py`

```python
"""
Simple test of citation export functionality using Django management command
"""
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

from datetime import date

# Mock paper data for testing
class MockPaper:
    def __init__(self):
        self.title = "Neural mechanisms of visual attention in cortical processing"
        self.abstract = "This study investigates the neural mechanisms underlying visual attention in cortical processing networks."
        self.publication_date = date(2024, 1, 15)
        self.doi = "10.1038/s41593-024-0001-1"
        self.pmid = "38000001"
        self.citation_count = 25
        self.source = "pubmed"
        self.is_open_access = True
        self.journal = MockJournal()
        self.id = "test-paper-id"
    
    def get_authors_display(self):
        return "Smith, John and Doe, Jane"

class MockJournal:
    def __init__(self):
        self.name = "Nature Neuroscience"
        self.abbreviation = "Nat. Neurosci."
        self.issn = "1097-6256"

def test_bibtex_generation():
    """Test BibTeX generation with mock data"""
    paper = MockPaper()
    
    # Generate BibTeX entry manually
    authors = "Smith, John and Doe, Jane"
    year = paper.publication_date.year if paper.publication_date else "2024"
    
    bibtex_key = f"smith{year}neural"
    
    bibtex = f"""@article{{{bibtex_key},
    title={{{paper.title}}},
    author={{{authors}}},
    journal={{{paper.journal.name}}},
    year={{{year}}},
    doi={{{paper.doi}}},
    pmid={{{paper.pmid}}},
    url={{https://pubmed.ncbi.nlm.nih.gov/{paper.pmid}/}},
    abstract={{{paper.abstract}}}

...
```


### `./tests/run_tests.sh`

```bash
#!/bin/bash
# SciTeX Web - Test Runner Script

# Set up environment
export PYTHONPATH="$PYTHONPATH:$(pwd)/src"
export DJANGO_SETTINGS_MODULE="config.settings.development"

# Activate virtual environment if it exists
if [ -d ".env" ]; then
    source .env/bin/activate
fi

# Parse arguments
DEBUG=false
SYNC=false

while [[ "$#" -gt 0 ]]; do
    case $1 in
        --debug) DEBUG=true ;;
        -s|--sync) SYNC=true ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Create log file
LOG_FILE="./.run_tests.sh.log"
> "$LOG_FILE"

# Function to log messages
log_message() {
    echo "$1" | tee -a "$LOG_FILE"
}

log_message "Starting test run at $(date)"

# Sync tests with source if requested
if [ "$SYNC" = true ]; then
    log_message "Synchronizing test and source directories..."
    # This would contain code to validate test structure and embed source code
    # For now, it's a placeholder
    log_message "Synchronization complete."
fi

# Run Django tests
if [ -d "tests" ]; then
    log_message "Running Django tests..."
    
    if [ "$DEBUG" = true ]; then
        python manage.py test tests --verbosity=2 2>&1 | tee -a "$LOG_FILE"

...
```


### `./tests/_test_api_integration.py`

```python
#!/usr/bin/env python3
"""
Test script for API key and impact factor integration
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.development')
sys.path.append('/home/ywatanabe/proj/SciTeX-Cloud')
django.setup()

from apps.scholar_app.models import UserPreference
from django.contrib.auth.models import User

def test_api_key_functionality():
    """Test API key storage and retrieval"""
    print("🧪 Testing API Key functionality...")
    
    # Create or get test user
    user, created = User.objects.get_or_create(
        username='test_user',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    
    # Get user preferences
    prefs = UserPreference.get_or_create_for_user(user)
    
    # Test API key storage
    print("   Testing API key storage...")
    prefs.set_api_key('pubmed', 'test_api_key_12345')
    prefs.unpaywall_email = 'test@unpaywall.org'
    prefs.save()
    
    # Test API key retrieval
    print("   Testing API key retrieval...")
    retrieved_key = prefs.get_api_key('pubmed')
    print(f"   ✓ Retrieved API key: {retrieved_key}")
    
    # Test missing API keys detection
    print("   Testing missing API keys detection...")
    missing_keys = prefs.get_missing_api_keys()
    print(f"   ✓ Missing API keys: {missing_keys}")
    

...
```


### `./tests/_test_api.py`

```python
"""
SciTeX Cloud - API Tests
"""

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
import json


class AuthAPITests(TestCase):
    """Tests for the Authentication API endpoints"""
    
    def setUp(self):
        """Set up test data"""
        self.client = Client()
        
        # API endpoints  
        self.register_url = reverse('api:api-register')
        self.login_url = reverse('api:api-login')
    
    def test_register_new_user(self):
        """Test registering a new user"""
        user_data = {
            'username': 'newuser',
            'email': 'newuser@example.com',
            'password': 'TestPassword123!',
            'first_name': 'Test',
            'last_name': 'User'
        }
        
        response = self.client.post(
            self.register_url,
            data=json.dumps(user_data),
            content_type='application/json'
        )
        
        self.assertEqual(response.status_code, 201)
        
        # Parse response
        data = json.loads(response.content)
        
        # Check response structure for email verification flow
        self.assertTrue(data['success'])
        self.assertIn('message', data)
        self.assertIn('email', data)
        self.assertIn('verification_required', data)
        self.assertEqual(data['email'], 'newuser@example.com')
        self.assertTrue(data['verification_required'])
    

...
```


### `./tests/_test_app.py`

```python
"""
SciTeX Cloud - Application Tests
"""

from django.test import TestCase
from django.conf import settings
from django.urls import reverse


class DjangoConfigTests(TestCase):
    """Tests for Django application configuration"""
    
    def test_django_settings_configured(self):
        """Test that Django settings are properly configured"""
        # Test that basic settings exist
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertTrue(hasattr(settings, 'MIDDLEWARE'))
        self.assertTrue(hasattr(settings, 'ROOT_URLCONF'))
        
    def test_required_apps_installed(self):
        """Test that required apps are installed"""
        # Check that our apps are in INSTALLED_APPS
        installed_apps = settings.INSTALLED_APPS
        
        # Basic Django apps
        self.assertIn('django.contrib.admin', installed_apps)
        self.assertIn('django.contrib.auth', installed_apps)
        self.assertIn('django.contrib.contenttypes', installed_apps)
        self.assertIn('django.contrib.sessions', installed_apps)
        
        # Our custom apps
        self.assertIn('apps.cloud_app', installed_apps)
        
    def test_debug_mode_in_development(self):
        """Test that debug mode is properly configured"""
        # In development, DEBUG should typically be True
        # This test checks that we can access the DEBUG setting
        self.assertIsInstance(settings.DEBUG, bool)


class URLConfigTests(TestCase):
    """Tests for URL configuration"""
    
    def test_basic_urls_configured(self):
        """Test that basic URLs are configured"""
        # Test that we can reverse basic URLs
        try:
            admin_url = reverse('admin:index')
            self.assertTrue(admin_url.startswith('/admin'))
        except:

...
```


### `./tests/_test_config.py`

```python
"""
SciTeX Cloud - Configuration Tests
"""

from django.test import TestCase
from django.conf import settings
import os


class DjangoSettingsTests(TestCase):
    """Tests for Django settings configuration"""
    
    def test_basic_settings_exist(self):
        """Test that basic Django settings are configured"""
        # Test essential settings
        self.assertTrue(hasattr(settings, 'DEBUG'))
        self.assertTrue(hasattr(settings, 'SECRET_KEY'))
        self.assertTrue(hasattr(settings, 'ALLOWED_HOSTS'))
        self.assertTrue(hasattr(settings, 'INSTALLED_APPS'))
        self.assertTrue(hasattr(settings, 'MIDDLEWARE'))
        
    def test_database_configured(self):
        """Test that database is configured"""
        self.assertTrue(hasattr(settings, 'DATABASES'))
        self.assertIn('default', settings.DATABASES)
        
    def test_static_files_configured(self):
        """Test that static files are configured"""
        self.assertTrue(hasattr(settings, 'STATIC_URL'))
        self.assertTrue(hasattr(settings, 'STATIC_ROOT'))
        self.assertTrue(hasattr(settings, 'STATICFILES_DIRS'))
        
    def test_template_configuration(self):
        """Test that templates are configured"""
        self.assertTrue(hasattr(settings, 'TEMPLATES'))
        self.assertIsInstance(settings.TEMPLATES, list)
        self.assertGreater(len(settings.TEMPLATES), 0)


class EnvironmentTests(TestCase):
    """Tests for environment-specific configuration"""
    
    def test_development_settings_loaded(self):
        """Test that development settings are loaded"""
        # In development mode, certain settings should be present
        if hasattr(settings, 'DJANGO_SETTINGS_MODULE'):
            settings_module = os.environ.get('DJANGO_SETTINGS_MODULE', '')
            if 'development' in settings_module:
                # Development-specific tests
                self.assertTrue(settings.DEBUG)

...
```


### `./tests/_test_django_models.py`

```python
"""
SciTeX Cloud - Django Model Tests
"""

from django.test import TestCase
from django.contrib.auth.models import User


class UserModelTests(TestCase):
    """Tests for Django User model functionality"""
    
    def setUp(self):
        """Set up test data"""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpassword123',
            'first_name': 'Test',
            'last_name': 'User'
        }
    
    def test_create_user(self):
        """Test creating a new user"""
        user = User.objects.create_user(**self.user_data)
        
        # Check user properties
        self.assertEqual(user.username, 'testuser')
        self.assertEqual(user.email, 'test@example.com')
        self.assertEqual(user.first_name, 'Test')
        self.assertEqual(user.last_name, 'User')
        self.assertTrue(user.check_password('testpassword123'))
    
    def test_user_str_representation(self):
        """Test string representation of User model"""
        user = User.objects.create_user(**self.user_data)
        self.assertEqual(str(user), 'testuser')
    
    def test_user_is_active_by_default(self):
        """Test that users are active by default"""
        user = User.objects.create_user(**self.user_data)
        self.assertTrue(user.is_active)


class BasicModelTests(TestCase):
    """Tests for basic model functionality"""
    
    def test_django_models_importable(self):
        """Test that Django models can be imported"""
        from django.contrib.auth.models import User
        from django.contrib.auth.models import Group

...
```


### `./tests/test_email.py`

```python
#!/usr/bin/env python3
"""
Test email configuration and send test email.
"""

import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.mail import send_mail
from django.conf import settings


def test_email_config():
    """Test and display email configuration."""
    print("=" * 60)
    print("SciTeX Cloud Email Configuration Test")
    print("=" * 60)
    print()
    print(f"EMAIL_BACKEND: {settings.EMAIL_BACKEND}")
    print(f"EMAIL_HOST: {settings.EMAIL_HOST}")
    print(f"EMAIL_PORT: {settings.EMAIL_PORT}")
    print(f"EMAIL_USE_TLS: {getattr(settings, 'EMAIL_USE_TLS', False)}")
    print(f"EMAIL_USE_SSL: {getattr(settings, 'EMAIL_USE_SSL', False)}")
    print(f"EMAIL_HOST_USER: {settings.EMAIL_HOST_USER}")
    print(f"EMAIL_PASSWORD set: {bool(settings.EMAIL_HOST_PASSWORD)}")
    print(f"DEFAULT_FROM_EMAIL: {settings.DEFAULT_FROM_EMAIL}")
    print()


def send_test_email(recipient_email='ywata1989@gmail.com'):
    """Send a test email."""
    print("=" * 60)
    print(f"Sending test email to: {recipient_email}")
    print("=" * 60)
    print()

    try:
        result = send_mail(
            subject='Test Email from SciTeX Cloud',
            message='''
This is a test email to verify SMTP configuration is working correctly.

If you receive this email, password reset and other email features will work!


...
```


### `./tests/test_forgot_password.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Test forgot password functionality end-to-end.
"""

import argparse
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.test import Client
import json


def create_test_user():
    """Create a test user if it doesn't exist."""
    username = 'ywatanabe'
    email = 'ywata1989@gmail.com'

    user, created = User.objects.get_or_create(
        email=email,
        defaults={'username': username}
    )

    if created:
        user.set_password('testpassword123')
        user.save()
        print(f"[+] Created test user: {username} ({email})")
    else:
        # Update username if needed
        if user.username != username:
            user.username = username
            user.save()
        print(f"[+] Test user already exists: {user.username} ({email})")

    return user


def test_forgot_password_api():
    """Test the forgot password API endpoint."""

...
```


### `./tests/_test_production_login.py`

```python
#!/usr/bin/env python3
"""
Test script for production login functionality.
Run this to verify ywata1989 login works in production.
"""

import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.contrib.auth.models import User
from apps.auth_app.models import UserProfile
from django.contrib.auth import authenticate

def test_production_login():
    print("🔍 Testing Production Login for ywata1989")
    print("=" * 50)
    
    # Check if user exists
    try:
        user = User.objects.get(username='ywata1989')
        print(f"✅ User found: {user.username} (ID: {user.id})")
        print(f"   Email: {user.email}")
        print(f"   Active: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
    except User.DoesNotExist:
        print("❌ User ywata1989 not found in production database")
        return False
    
    # Check UserProfile
    try:
        profile = UserProfile.objects.get(user=user)
        print(f"✅ UserProfile exists (ID: {profile.id})")
        print(f"   Academic verified: {profile.is_academic_verified}")
        print(f"   Profile completed: {profile.profile_completed}")
    except UserProfile.DoesNotExist:
        print("❌ UserProfile missing - this could cause login issues")
        return False
    
    # Test authentication
    auth_user = authenticate(username='ywata1989', password='ywata1989')
    if auth_user:
        print(f"✅ Authentication successful for {auth_user.username}")
    else:
        print("❌ Authentication failed - check password")
        return False

...
```


### `./tests/_test_project_redirects.py`

```python
#!/usr/bin/env python3
"""
Test project redirect functionality
"""
import os
import django
import sys

# Set up Django environment
sys.path.append('/home/ywatanabe/proj/SciTeX-Cloud')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_project_redirects():
    """Test the project redirect functionality"""
    client = Client()
    
    print("Testing Project Redirect Functionality")
    print("=" * 50)
    
    # Test 1: Anonymous user accessing /projects/
    print("1. Testing anonymous user access to /projects/...")
    response = client.get('/projects/', follow=True)
    print(f"   Status: {response.status_code}")
    print(f"   Final URL: {response.request['PATH_INFO']}")
    if 'login' in response.request['PATH_INFO']:
        print("   ✅ Correctly redirected to login page")
    else:
        print("   ❌ Not redirected to login page")
    
    # Test 2: Create a test user and login
    print("\n2. Testing logged-in user access to /projects/...")
    
    # Create or get test user
    try:
        user = User.objects.get(username='ywata1989')
        print(f"   Using existing user: {user.username}")
    except User.DoesNotExist:
        user = User.objects.create_user('testuser', 'test@example.com', 'testpass')
        print(f"   Created test user: {user.username}")
    
    # Login the user
    login_success = client.login(username=user.username, password='admin123' if user.username == 'ywata1989' else 'testpass')
    print(f"   Login successful: {login_success}")
    
    if login_success:
        # Test logged-in user redirect

...
```


### `./tests/_test_views.py`

```python
"""
SciTeX Web - View Tests
"""

from django.test import TestCase, Client
from django.urls import reverse


class IndexViewTests(TestCase):
    """Tests for the index view"""
    
    def setUp(self):
        self.client = Client()
    
    def test_index_view_returns_200(self):
        """Test that the index view returns a 200 OK response"""
        response = self.client.get(reverse('cloud_app:index'))
        self.assertEqual(response.status_code, 200)
    
    def test_index_view_uses_correct_template(self):
        """Test that the index view uses the correct template"""
        response = self.client.get(reverse('cloud_app:index'))
        self.assertTemplateUsed(response, 'cloud_app/landing.html')
    
    def test_index_view_contains_title(self):
        """Test that the index view contains the expected title"""
        response = self.client.get(reverse('cloud_app:index'))
        self.assertContains(response, 'SciTeX')
...
```


### `./tests/_test_web_login.py`

```python
#!/usr/bin/env python3
"""
Test web login functionality
"""
import os
import django
import sys

# Set up Django environment
sys.path.append('/home/ywatanabe/proj/SciTeX-Cloud')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.production')
django.setup()

from django.test import Client
from django.contrib.auth.models import User

def test_web_login():
    """Test the web login functionality"""
    client = Client()
    
    # Test 1: GET login page
    print("Testing GET /login/...")
    response = client.get('/login/')
    print(f"Status: {response.status_code}")
    
    if response.status_code != 200:
        print("❌ Login page failed to load")
        print(f"Response content preview: {response.content[:500]}")
        return False
    
    print("✅ Login page loads successfully")
    
    # Test 2: POST login with valid credentials
    print("\nTesting POST /login/ with valid credentials...")
    response = client.post('/login/', {
        'username': 'ywata1989',
        'password': 'admin123'
    })
    
    print(f"Status: {response.status_code}")
    print(f"Redirect URL: {response.get('Location', 'No redirect')}")
    
    if response.status_code == 302:  # Redirect on successful login
        print("✅ Login successful - redirect detected")
        return True
    elif response.status_code == 200:
        # Check if there are error messages
        content = response.content.decode()
        if 'Invalid username or password' in content:
            print("❌ Login failed - invalid credentials error")

...
```


### `./tmp/create_test_user.py`

```python
#!/usr/bin/env python
"""
Create a test user for SciTeX authentication testing.
Usage: python manage.py shell < tmp/create_test_user.py
"""
from django.contrib.auth.models import User
from apps.auth_app.models import UserProfile

# Test user credentials
username = "testuser"
email = "test@example.com"
password = "TestPass123!"

# Check if user already exists
if User.objects.filter(username=username).exists():
    user = User.objects.get(username=username)
    print(f"✓ User '{username}' already exists")
    print(f"  Email: {user.email}")
    print(f"  Resetting password to: {password}")
    user.set_password(password)
    user.save()
    print(f"  Password updated!")
else:
    # Create new user
    user = User.objects.create_user(
        username=username,
        email=email,
        password=password
    )
    # Create profile
    UserProfile.objects.get_or_create(user=user)
    print(f"✓ Created new user '{username}'")
    print(f"  Email: {email}")
    print(f"  Password: {password}")

print(f"\nYou can now log in with:")
print(f"  Username: {username}")
print(f"  Email: {email}")
print(f"  Password: {password}")

...
```


### `./TODOS/COLLABORATOR_UI.md`

```markdown
# Collaborator Management UI - Next Session

## Backend Complete ✅
- add_collaborator(request, project_id) - Add user by username
- remove_collaborator(request, project_id, collaborator_id) - Remove user

## URLs Needed
Add to apps/writer_app/urls.py:
```python
path('project/<int:project_id>/collaborators/add/', views.add_collaborator, name='add_collaborator'),
path('project/<int:project_id>/collaborators/<int:collaborator_id>/remove/', views.remove_collaborator, name='remove_collaborator'),
```

## UI to Add
In apps/writer_app/templates/writer_app/project_writer.html around line 775:

1. Add "+" button next to "Active Collaborators" header
2. Show all manuscript.collaborators.all (not just online ones)
3. Add modal/form for entering username
4. Add remove buttons for each collaborator

## JavaScript Needed
```javascript
// Add collaborator
document.getElementById('add-collaborator-btn').addEventListener('click', async () => {
    const username = prompt('Enter username to add:');
    if (username) {
        const response = await fetch(`/writer/project/${projectId}/collaborators/add/`, {
            method: 'POST',
            headers: {'Content-Type': 'application/json', 'X-CSRFToken': getCsrfToken()},
            body: JSON.stringify({username})
        });
        const data = await response.json();
        if (data.success) {
            showToast(`Added ${username} as collaborator`, 'success');
            location.reload();
        } else {
            showToast(data.error, 'danger');
        }
    }
});
```

## Quick Fix for Now
Users can add project collaborators from project settings, and they automatically become manuscript collaborators.

...
```


### `./TODOS/FUTURE.md`

```markdown

- [ ] Grant Hunter mode
- [ ] Reproducibility Badge


...
```


### `./TODOS/GITHUB_LAYOUT.md`

```markdown

## Visual check with `cam` MCP server 
- May need to capture screen/windows/apps (chrome) to keep layout

## Design System
Use design system to keep consistent color use
http://127.0.0.1:8000/dev/design/

## Task 2: Home Page:
- [ ] Check the differences between them when logged in:
  - [ ] https://github.com/ <- when logged in
  - [ ] http://127.0.0.1:8000/core/ <- I think we dont need this
    - [ ] Instead, http://127.0.0.1:8000/ywatanabe1989
  - [ ] No need anymore: http://127.0.0.1:8000/ywatanabe1989/projects
  - [ ] No need anymore: /dashboard/
- [ ] Update the scitex_cloud code to be close to github

## Side panel when child directory selected
take screenshot of
https://github.com/ywatanabe1989/SciTeX-Writer/tree/main/docs
http://127.0.0.1:8000/ywatanabe1989/neurovista/config/ 
- [ ] Implement sidebar like in GitHub




our page has 


...
```


### `./TODOS/GUEST_COLLABORATORS.md`

```markdown
# Guest Collaborator System - Email-Based Limited Access

## Problem
Professors/reviewers don't want to create accounts just to review a manuscript.

## Solution: Token-Based Guest Access

### Workflow
1. **Owner invites by email** (no account needed)
   ```
   "Add Collaborator" → Enter email → Send invite
   ```

2. **Guest receives email** with magic link
   ```
   Subject: You've been invited to review "Paper Title"
   Link: https://scitex.ai/writer/guest/abc123token456
   Valid for: 7 days
   ```

3. **Guest accesses via token**
   - No login required
   - Limited to specific manuscript
   - Read + comment permissions
   - Optional: Suggest changes

### Guest Permissions (Limited)

**Can Do:**
- ✅ View manuscript (read-only)
- ✅ View compiled PDF
- ✅ Add comments/suggestions
- ✅ Export PDF
- ✅ View change history

**Cannot Do:**
- ❌ Edit text directly
- ❌ Delete content
- ❌ Invite others
- ❌ Access other projects
- ❌ See user's other manuscripts

### Models Needed

```python
class GuestCollaborator(models.Model):
    """Guest access for reviewers without accounts."""
    manuscript = ForeignKey(Manuscript)
    email = EmailField()
    invited_by = ForeignKey(User)
```

...
```


### `./TODOS/INTEGRATIONS.md`

```markdown

## TODO
We are planning to reduce the barrier for tool switching bidirectionally

### Code Hosting & Version Control
- [ ] GitHub
  - [ ] Import: Sync repository structure, issues/PRs, README/docs, CI configs
  - [ ] Export: Push notebooks, manuscripts, visualizations, auto-commit outputs
  - [ ] Link: OAuth, real-time webhooks, status badges, commit cross-references

- [ ] GitLab
  - [ ] Import: Repository structure, merge requests, wiki pages, pipelines
  - [ ] Export: Code exports, documentation, CI/CD integration
  - [ ] Link: OAuth, webhooks, project mirroring

### Reference Management
- [ ] Zotero
  - [ ] Import: Bibliography with collections/tags, PDF annotations, paper metadata
  - [ ] Export: Manuscripts as preprint entries, project metadata, citation files (.bib, .ris)
  - [ ] Link: Live citation insertion, auto-update on library changes, tagged items

- [ ] Mendeley
  - [ ] Import: Reference library, groups, annotations
  - [ ] Export: Bibliography exports, project citations
  - [ ] Link: Real-time citation sync, collaborative groups

### Writing & Collaboration
- [ ] Overleaf
  - [ ] Import: LaTeX projects, document structure, figures/tables, .bib files
  - [ ] Export: Compile manuscripts to LaTeX, push figures, submission packages
  - [ ] Link: Two-way sync with conflict resolution, collaborator mirroring, real-time preview

- [ ] Google Docs
  - [ ] Import: Document content, comments, suggestions, version history
  - [ ] Export: Formatted manuscripts, collaborative drafts
  - [ ] Link: Real-time collaborative editing, comment synchronization

### Data & Computation
- [ ] Jupyter Hub/Lab
  - [ ] Import: Notebooks, execution history, kernel configurations
  - [ ] Export: SciTeX-Code notebooks as .ipynb, execution environments
  - [ ] Link: Remote kernel connections, live notebook sync

- [ ] Google Colab
  - [ ] Import: Notebooks, cell outputs, runtime configurations
  - [ ] Export: SciTeX notebooks with reproducibility metadata
  - [ ] Link: Cloud compute integration, GPU/TPU access

- [ ] Kaggle
  - [ ] Import: Datasets, notebooks, competition submissions

...
```


### `./TODOS/OUR_CODE_REFERENCES.md`

```markdown

## TODO

#### Writer



## Code references

```
SCITEX_SCHOLAR="$HOME/proj/scitex_repo/src/scitex/scholar"
# https://github.com/ywatanabe1989/scitex
SCITEX_WRITER="$HOME/proj/neurovista/paper"
SCITEX_CODE="$HOME/proj/scitex_repo/src/scitex"
SCITEX_VIZ="$HOME/win/documents/SciTeX-Viz"
SCITEX_ENGINE="$HOME/.emacs.d/lisp/emacs-claude-code"
SCITEX_CLOUD="$HOME/proj/scitex-cloud"

RISE_DIR="$HOME/proj/grant/2025-07-XX---2026-04-2030-03---NN-PERC---500---SMBC-RISE-PROJECT/drafts"

SCITEX_PROPOSAL_JST_BOOST="$RISE_DIR/JST_BOOST_申請書_Human-in-the-Environment 型論文執筆自動化システムの開発_渡邉裕亮.pdf"
SCITEX_PROPOSAL_SMBC_RISE="$RISE_DIR/SMBC_RISE_PROJECT_申請書_論文執筆自動化システム SciTeX の事業化_渡邉裕亮.pdf"
SCITEX_SCHOLAR_CROSSREF_LOCAL="/mnt/nas_ug/crossref_local"
```

## Documentation building
Directories below is associated with `.env` and when cd there, `source .env/bin/activate` called. They are installed via `pip install -e .`
cd $SCITEX_SCHOLAR="$HOME/proj/scitex_repo/src/scitex/scholar"
cd $SCITEX_WRITER="$HOME/proj/neurovista/paper"
cd $SCITEX_CODE="$HOME/proj/scitex_repo/"
cd $SCITEX_VIZ="$HOME/win/documents/SciTeX-Viz"
cd $SCITEX_ENGINE="$HOME/.emacs.d/lisp/emacs-claude-code"
cd $SCITEX_CLOUD="$HOME/proj/scitex-cloud"

We need to prepare docs in docs_app and add link to the landing page: /home/ywatanabe/proj/scitex-cloud/apps/cloud_app/templates/cloud_app/landing_partials/landing_demos.html
Now, the docs of writer and viz are rendered; however, the footer is not in the bottom; the width of the main contents is narrow
Regarding scitex code and scholar; no, they are not rendered.
When side panel contents clicked, the positionnig of the main contents are wrong; they are overlapped with the side bar


...
```


### `./TODOS/PERMISSIONS_SYSTEM.md`

```markdown

# GitLab-Style Permissions System for SciTeX

## Vision
Fine-grained access control across all modules (Scholar, Code, Viz, Writer) with organization support.

---

## Current Situation
- ✅ Projects have owner + collaborators (basic)
- ❌ No role differentiation
- ❌ No module-specific permissions
- ❌ No organization/group support

---

## GitLab Permission Levels

### Repository/Project Roles
| Role           | Can Read | Can Write | Can Delete | Can Manage | Can Admin |
|----------------|----------|-----------|------------|------------|-----------|
| **Guest**      | ✓        | ✗         | ✗          | ✗          | ✗         |
| **Reporter**   | ✓        | ✗         | ✗          | ✗          | ✗         |
| **Developer**  | ✓        | ✓         | ✗          | ✗          | ✗         |
| **Maintainer** | ✓        | ✓         | ✓          | ✓          | ✗         |
| **Owner**      | ✓        | ✓         | ✓          | ✓          | ✓         |

---

## SciTeX Adapted Roles

### Project-Level Roles

**Owner** (Creator)
- Full control over project
- Manage collaborators
- Delete project
- Transfer ownership
- Configure integrations

**Maintainer** (Senior Collaborator)
- Edit all modules (Scholar, Code, Viz, Writer)
- Compile and publish
- Invite collaborators
- Manage settings
- Cannot delete project

**Developer** (Active Collaborator)
- Edit assigned modules
- Run analyses

...
```


### `./TODOS/REPOSITORY.md`

```markdown


- [ ] Repository Management
  - [ ] Branch
  - [ ] Tags
  - [ ] Releases
  - [ ] Issues
  - [ ] Pull Requests
  - [ ] Notification
  - [ ] Fork
  - [ ] Star

- [ ] Consolidate URL rules
  All URLs should follow the github rules


...
```


### `./TODOS/SCHOLAR.md`

```markdown

### Reference Management Integration
see /home/ywatanabe/proj/scitex-cloud/TODOS/INTEGRATIONS.md


...
```


### `./TODOS/SOCIAL.md`

```markdown

#### GitHub for Scientific Research

- [ ] Social Networking
  - [ ] Private/public projects
  - [ ] Follow/Unfollow
  - [ ] Feed
  - [ ] Profile
    - Yusuke Watanabe
    - ywatanabe1989
    - Follow
    - followers • 4 following
    - The University of Melboume I JSPS
    - Overseas Research Fellow
    - Melbourne. Australia
    - 005 - 23h behind
    - https://ai-ielts.app
    - O https://orcidorg/OOOO-0001-9541-6073
  - [ ] Activity Log
  - [ ] Search
  - [ ] Packages
  - [ ] Contributors
  - [ ] Languages


...
```


### `./TODOS/TEMPLATES.md`

```markdown


- [ ] scitex-template-pip
- [ ] Versioning


...
```


### `./TODOS/URL_NAVIGATION.md`

```markdown

##### In GitHub
https://github.com/ywatanabe1989 (overview)
https://github.com/ywatanabe1989?tab=repositories
https://github.com/ywatanabe1989?tab=projects
https://github.com/ywatanabe1989?tab=packages
https://github.com/ywatanabe1989?tab=stars
https://github.com/ywatanabe1989/<project-name>


##### In SciTeX
https://scitex.ai/ywatanabe1989/projects (<- not discriminative from project name)
https://scitex.ai/ywatanabe1989/<project-name>
http://127.0.0.1:8000/ywatanabe1989/neurovista/scholar/ -> should be http://127.0.0.1:8000/ywatanabe1989/neurovista?mode=scholar

Now, please check URL navigaitons
- Links
  - The header buttons are not working well sometimes
  - In this page, we have inline links for the modules
    http://127.0.0.1:8000/ywatanabe1989/neurovista/
  - They should have the same behaviour

We should simplify them
Login required for modules
Repository required for modules
Appropriate guideline messages


...
```


### `./TODOS/WRITER.md`

```markdown

# SciTeX Writer - Improvement Roadmap

## Vision
Create a coordinated ecosystem for scientific writing that excels beyond Overleaf by integrating project management, real-time collaboration, AI assistance, and seamless coordination with Scholar/Code/Viz modules.

**Current Demo:** http://127.0.0.1:8000/ywatanabe1989/neurovista/?mode=writer
**Reference:** ./externals/overleaf

---

## Current Strengths (Already Better Than Overleaf)

✅ **Django 5.2 LTS** - Latest async support for real-time features (upgraded Oct 2025)
✅ **Project-centric design** - Manuscripts linked to research projects
✅ **Comprehensive models** - Version control, branches, merge requests already implemented
✅ **Modular structure** - Sections as separate .tex files (better for collaboration)
✅ **AI integration ready** - AIAssistanceLog model in place
✅ **Scholar integration** - Citation management with BibTeX enrichment
✅ **arXiv pipeline** - Automated submission validation and tracking
✅ **Advanced PDF viewer** - Collapsible outline, zoom, navigation (just implemented!)
✅ **Channels 4.3.1** - Latest WebSocket support for real-time collaboration

---

## Implementation Roadmap

### Phase 1: Real-Time Collaboration (PRIORITY: P0) 🚀
**Goal:** Enable multiple users to edit simultaneously with conflict-free updates
**Timeline:** 2-3 weeks | **Impact:** HIGH | **Effort:** Medium

**Prerequisites:** ✅ Django 5.2 LTS (enhanced async support) | ✅ Channels 4.3.1 installed

#### Sprint 1.1: WebSocket Infrastructure (Week 1) ✅ COMPLETED
- [x] Install Django Channels 4.x + Redis (✅ Channels 4.3.1 ready!)
- [x] Configure Redis channel layer in settings (✅ Already configured!)
- [x] Create `apps/writer_app/consumers.py` for WebSocket handling (✅ Implemented!)
- [x] Implement presence system (show who's online) (✅ Complete!)
- [x] Broadcast user join/leave events (✅ Working!)
- [x] Display active collaborators in sidebar (✅ UI added!)

**Technical (Django 5.2 async features):**
```python
# apps/writer_app/consumers.py
class WriterConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.manuscript_id = self.scope['url_route']['kwargs']['manuscript_id']
        self.room_group_name = f'manuscript_{self.manuscript_id}'

        # Django 5.2: Use async ORM for better performance
```

...
```

