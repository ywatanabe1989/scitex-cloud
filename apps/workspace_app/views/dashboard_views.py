from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.views.decorators.cache import never_cache
from .core_views import index as dashboard_view


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
        from .core_views import landing
        return landing(request)