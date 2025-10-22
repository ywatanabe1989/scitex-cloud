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
touch /home/ywatanabe/proj/scitex-web/apps/about_app/models.py
touch /home/ywatanabe/proj/scitex-web/apps/about_app/urls.py
touch /home/ywatanabe/proj/scitex-web/apps/about_app/views.py
touch /home/ywatanabe/proj/scitex-web/apps/about_app/tests.py
mkdir -p /home/ywatanabe/proj/scitex-web/apps/about_app/migrations
touch /home/ywatanabe/proj/scitex-web/apps/about_app/migrations/__init__.py

# Create core_app files
touch /home/ywatanabe/proj/scitex-web/apps/core_app/admin.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/apps.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/models.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/urls.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/views.py
touch /home/ywatanabe/proj/scitex-web/apps/core_app/tests.py
mkdir -p /home/ywatanabe/proj/scitex-web/apps/core_app/migrations
touch /home/ywatanabe/proj/scitex-web/apps/core_app/migrations/__init__.py
```

### 4. Move Views to App-Specific Files

#### About App Views (apps/about_app/views.py)
```python
from django.shortcuts import render
from django.core.mail import send_mail

def contact(request):
    """Contact page view with form handling"""
    form_success = False
    form_error = False
    
    if request.method == 'POST':
        # Get form data
        name = request.POST.get('name', '')
        email = request.POST.get('email', '')
        subject = request.POST.get('subject', '')
        message = request.POST.get('message', '')
        
        # Basic validation
        if name and email and subject and message:
            try:
                # Try to send email
                send_mail(
                    f'Contact Form: {subject}',
                    f'Name: {name}\nEmail: {email}\n\nMessage:\n{message}',
                    email,  # From email
                    ['contact@scitex.ai'],  # To email
                    fail_silently=False,
                )
                form_success = True
            except Exception as e:
                # Log the error (in a real app)
                print(f"Error sending email: {e}")
                form_error = True
        else:
            form_error = True
    
    return render(request, 'about_app/contact.html', {
        'title': 'Contact Us',
        'form_success': form_success,
        'form_error': form_error,
    })

def privacy_policy(request):
    """Privacy Policy page view"""
    return render(request, 'about_app/privacy_policy.html', {
        'title': 'Privacy Policy',
    })

def terms_of_use(request):
    """Terms of Use page view"""
    return render(request, 'about_app/terms_of_use.html', {
        'title': 'Terms of Use',
    })
```

#### Core App Views (apps/core_app/views.py)
```python
from django.shortcuts import render

def index(request):
    """Main page view for SciTeX Web application"""
    return render(request, 'core_app/index.html', {
        'title': 'SciTeX Cloud',
    })

def landing(request):
    """Landing page view for SciTeX Web application"""
    return render(request, 'core_app/landing.html', {
        'title': 'Scientific Research Platform',
    })
```

### 5. Create URL Configurations

#### About App URLs (apps/about_app/urls.py)
```python
from django.urls import path
from . import views

app_name = 'about_app'

urlpatterns = [
    path('contact/', views.contact, name='contact'),
    path('privacy/', views.privacy_policy, name='privacy'),
    path('terms/', views.terms_of_use, name='terms'),
]
```

#### Core App URLs (apps/core_app/urls.py)
```python
from django.urls import path
from . import views

app_name = 'core_app'

urlpatterns = [
    path('', views.landing, name='landing'),
    path('dashboard/', views.index, name='index'),
    path('landing/', views.landing, name='landing_explicit'),
]
```

### 6. Create App Configuration

#### About App (apps/about_app/apps.py)
```python
from django.apps import AppConfig

class AboutAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.about_app'
    verbose_name = 'About & Legal Pages'
```

#### Core App (apps/core_app/apps.py)
```python
from django.apps import AppConfig

class CoreAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.core_app'
    verbose_name = 'Core Application'
```

### 7. Create Project Configuration

#### Project Settings (config/settings/base.py)
Move and enhance existing settings from `config/django_settings.py` to `config/settings/base.py`, adding:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.about_app.apps.AboutAppConfig',
    'apps.core_app.apps.CoreAppConfig',
]

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [os.path.join(BASE_DIR, 'templates')],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (User uploads)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
```

#### Create Project URLs (config/urls.py)
```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core_app.urls')),
    path('', include('apps.about_app.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

### 8. Update Static Files Configuration

```bash
# Create static directory
mkdir -p /home/ywatanabe/proj/scitex-web/static/css
mkdir -p /home/ywatanabe/proj/scitex-web/static/js
mkdir -p /home/ywatanabe/proj/scitex-web/static/images

# Move CSS files
cp -r /home/ywatanabe/proj/scitex-web/public/css/* /home/ywatanabe/proj/scitex-web/static/css/

# Move JS files
cp -r /home/ywatanabe/proj/scitex-web/public/js/* /home/ywatanabe/proj/scitex-web/static/js/
```

### 9. Create manage.py at Root Directory

```python
#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed?"
        ) from exc
    execute_from_command_line(sys.argv)

if __name__ == '__main__':
    main()
```

### 10. Create WSGI and ASGI Files

#### config/wsgi.py
```python
import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
application = get_wsgi_application()
```

#### config/asgi.py
```python
import os
from django.core.asgi import get_asgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.base')
application = get_asgi_application()
```

## Implementation Schedule

1. **Phase 1: Directory Structure (Day 1)**
   - Create app directories
   - Create configuration files
   - Set up manage.py
   
2. **Phase 2: App Configuration (Day 1-2)**
   - Move templates to app-specific directories
   - Implement views and URLs in each app
   - Update template paths in view functions
   
3. **Phase 3: Static Files (Day 2)**
   - Move static files to Django's standard location
   - Update references in templates
   
4. **Phase 4: Testing (Day 3)**
   - Verify templates render correctly
   - Test URL routing
   - Validate form submission
   
5. **Phase 5: Documentation Update (Day 3)**
   - Update README.md with new structure
   - Document development setup process
   - Create missing tests for views and templates

## Expected Outcomes

1. **Improved Codebase Organization**
   - Clear separation of concerns with modular apps
   - Standard Django structure for better maintainability

2. **Better Developer Experience**
   - More intuitive file locations
   - Standard Django tools and commands will work as expected

3. **Simplified Scalability**
   - New features can be added as dedicated apps
   - Clearer boundaries between components

## Additional Recommendations

1. Consider implementing Django forms for the contact form
2. Add model-based contact message storage for later review
3. Implement Django authentication for admin access
4. Add logging configuration for tracking errors in production

---

*This implementation plan follows the guidelines specified in the IMPORTANT-guidelines-programming-Python-Django-Rules.md document.*