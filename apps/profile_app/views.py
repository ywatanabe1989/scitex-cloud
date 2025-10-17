from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import UserProfile


@login_required
def profile_view(request):
    """User profile view."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
    }

    return render(request, 'profile_app/profile.html', context)


@login_required
def profile_edit(request):
    """Edit user profile (GitHub-style settings page)."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update user basic info
        request.user.first_name = request.POST.get('first_name', '').strip()
        request.user.last_name = request.POST.get('last_name', '').strip()
        request.user.email = request.POST.get('email', '').strip()
        request.user.save()

        # Update profile info
        profile.bio = request.POST.get('bio', '').strip()
        profile.location = request.POST.get('location', '').strip()
        profile.institution = request.POST.get('institution', '').strip()
        profile.website = request.POST.get('website', '').strip()
        profile.orcid = request.POST.get('orcid', '').strip()
        profile.google_scholar = request.POST.get('google_scholar', '').strip()
        profile.twitter = request.POST.get('twitter', '').strip()

        # Handle avatar upload
        if 'avatar' in request.FILES:
            profile.avatar = request.FILES['avatar']

        profile.save()

        messages.success(request, 'Profile updated successfully!')
        return redirect('profile_app:profile_edit')

    context = {
        'profile': profile,
        'user': request.user,
    }

    return render(request, 'profile_app/profile_edit.html', context)


@login_required
def appearance_settings(request):
    """Appearance settings page (GitHub-style /settings/appearance)."""
    context = {
        'user': request.user,
    }
    return render(request, 'profile_app/appearance_settings.html', context)
