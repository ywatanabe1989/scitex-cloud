from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from .models import UserProfile, APIKey


@login_required
def profile_view(request):
    """User profile view."""
    profile, created = UserProfile.objects.get_or_create(user=request.user)

    context = {
        'profile': profile,
    }

    return render(request, 'accounts_app/profile.html', context)


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
        profile.timezone = request.POST.get('timezone', '').strip() or 'UTC'
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
        return redirect('accounts_app:profile_edit')

    context = {
        'profile': profile,
        'user': request.user,
    }

    return render(request, 'accounts_app/profile_edit.html', context)


@login_required
def appearance_settings(request):
    """Appearance settings page (GitHub-style /settings/appearance)."""
    context = {
        'user': request.user,
    }
    return render(request, 'accounts_app/appearance_settings.html', context)


@login_required
def ssh_keys(request):
    """SSH key management page."""
    from apps.workspace_app.ssh_manager import SSHKeyManager

    ssh_manager = SSHKeyManager(request.user)
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'generate':
            success, public_key, error = ssh_manager.get_or_create_user_key()
            if success:
                messages.success(request, 'SSH key generated successfully!')
            else:
                messages.error(request, f'Failed to generate SSH key: {error}')

        elif action == 'delete':
            success, error = ssh_manager.delete_user_key()
            if success:
                messages.success(request, 'SSH key deleted successfully!')
            else:
                messages.error(request, f'Failed to delete SSH key: {error}')

        return redirect('accounts_app:ssh_keys')

    # GET request
    context = {
        'ssh_public_key': profile.ssh_public_key,
        'ssh_key_fingerprint': profile.ssh_key_fingerprint,
        'ssh_key_created_at': profile.ssh_key_created_at,
        'ssh_key_last_used_at': profile.ssh_key_last_used_at,
        'has_ssh_key': ssh_manager.has_ssh_key(),
    }
    return render(request, 'accounts_app/ssh_keys.html', context)


@login_required
def api_keys(request):
    """API key management page."""
    user_api_keys = APIKey.objects.filter(user=request.user).select_related('user')

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'create':
            name = request.POST.get('name', '').strip()
            scopes = request.POST.getlist('scopes')

            if not name:
                messages.error(request, 'API key name is required')
            else:
                api_key_obj, full_key = APIKey.create_key(
                    user=request.user,
                    name=name,
                    scopes=scopes or ['*']  # Default: full access
                )
                # Store the full key in session to show once
                request.session['new_api_key'] = full_key
                request.session['new_api_key_name'] = name
                messages.success(request, f'API key "{name}" created successfully!')

        elif action == 'delete':
            key_id = request.POST.get('key_id')
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                key_name = api_key.name
                api_key.delete()
                messages.success(request, f'API key "{key_name}" deleted successfully!')
            except APIKey.DoesNotExist:
                messages.error(request, 'API key not found')

        elif action == 'toggle':
            key_id = request.POST.get('key_id')
            try:
                api_key = APIKey.objects.get(id=key_id, user=request.user)
                api_key.is_active = not api_key.is_active
                api_key.save()
                status = 'activated' if api_key.is_active else 'deactivated'
                messages.success(request, f'API key "{api_key.name}" {status}')
            except APIKey.DoesNotExist:
                messages.error(request, 'API key not found')

        return redirect('accounts_app:api_keys')

    # Get newly created key from session (show once)
    new_api_key = request.session.pop('new_api_key', None)
    new_api_key_name = request.session.pop('new_api_key_name', None)

    context = {
        'api_keys': user_api_keys,
        'new_api_key': new_api_key,
        'new_api_key_name': new_api_key_name,
    }
    return render(request, 'accounts_app/api_keys.html', context)


# API Endpoints
@login_required
@require_http_methods(["POST"])
def api_generate_ssh_key(request):
    """API endpoint to generate SSH key."""
    from apps.workspace_app.ssh_manager import SSHKeyManager

    ssh_manager = SSHKeyManager(request.user)
    success, public_key, error = ssh_manager.get_or_create_user_key()

    if success:
        return JsonResponse({
            'success': True,
            'public_key': public_key
        })
    else:
        return JsonResponse({
            'success': False,
            'error': error
        }, status=400)


@login_required
def git_integrations(request):
    """Git Platform Integration settings page."""
    profile, _ = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Update Git platform tokens
        github_token = request.POST.get('github_token', '').strip()
        gitlab_token = request.POST.get('gitlab_token', '').strip()
        bitbucket_token = request.POST.get('bitbucket_token', '').strip()

        if github_token:
            profile.github_token = github_token
        if gitlab_token:
            profile.gitlab_token = gitlab_token
        if bitbucket_token:
            profile.bitbucket_token = bitbucket_token

        # Update Git hosting profiles (public usernames)
        profile.github_profile = request.POST.get('github_profile', '').strip()
        profile.gitlab_profile = request.POST.get('gitlab_profile', '').strip()
        profile.bitbucket_profile = request.POST.get('bitbucket_profile', '').strip()

        profile.save()
        messages.success(request, 'Git platform integrations updated successfully!')
        return redirect('accounts_app:git_integrations')

    # Helper function to mask tokens
    def mask_token(token):
        if not token or len(token) < 8:
            return None
        return f"{token[:4]}...{token[-4:]}"

    context = {
        'profile': profile,
        'github_token_masked': mask_token(profile.github_token) if profile.github_token else None,
        'gitlab_token_masked': mask_token(profile.gitlab_token) if profile.gitlab_token else None,
        'bitbucket_token_masked': mask_token(profile.bitbucket_token) if profile.bitbucket_token else None,
    }
    return render(request, 'accounts_app/git_integrations.html', context)


@login_required
def account_settings(request):
    """Account settings page (email, password, delete account)."""
    from django.contrib.auth import update_session_auth_hash
    from django.contrib.auth.forms import PasswordChangeForm

    if request.method == 'POST':
        action = request.POST.get('action')

        if action == 'change_email':
            new_email = request.POST.get('new_email', '').strip()
            if new_email:
                if User.objects.filter(email=new_email).exclude(pk=request.user.pk).exists():
                    messages.error(request, 'This email is already in use by another account.')
                else:
                    request.user.email = new_email
                    request.user.save()
                    messages.success(request, 'Email updated successfully!')
            else:
                messages.error(request, 'Please enter a valid email address.')

        elif action == 'change_password':
            current_password = request.POST.get('current_password', '')
            new_password = request.POST.get('new_password', '')
            confirm_password = request.POST.get('confirm_password', '')

            if not request.user.check_password(current_password):
                messages.error(request, 'Current password is incorrect.')
            elif new_password != confirm_password:
                messages.error(request, 'New passwords do not match.')
            elif len(new_password) < 8:
                messages.error(request, 'Password must be at least 8 characters long.')
            else:
                request.user.set_password(new_password)
                request.user.save()
                update_session_auth_hash(request, request.user)  # Keep user logged in
                messages.success(request, 'Password updated successfully!')

        return redirect('accounts_app:account')

    context = {
        'user': request.user,
    }
    return render(request, 'accounts_app/account_settings.html', context)
