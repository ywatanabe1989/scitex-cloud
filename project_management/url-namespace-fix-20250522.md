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

Moving forward, use these namespaces consistently in templates:

1. **For URLs accessed at the root level** (e.g., /concept/, /contact/):
   ```html
   {% url 'cloud_root:concept' %}
   {% url 'cloud_root:contact' %}
   ```

2. **For URLs accessed under the /cloud/ prefix** (e.g., /cloud/design/):
   ```html
   {% url 'cloud:design' %}
   {% url 'cloud:login' %}
   ```

3. **For direct resource URLs**:
   ```html
   <a href="/static/images/logo.png">Logo</a>
   ```

## Testing

After applying these fixes, all pages should load properly without URL resolution errors. The following pages were tested:

- Homepage (/)
- Design System (/design/)
- All header navigation links

## Recommendations for Future Development

1. **URL Configuration**:
   - Consider consolidating to a single namespace approach
   - Clearly document which namespace should be used for which URLs

2. **Template Development**:
   - Always use the `{% url %}` template tag with the correct namespace
   - Avoid hardcoded URLs when possible

3. **URL Patterns**:
   - Keep URL patterns consistent (with trailing slashes)
   - Group related URLs together in the urlpatterns list