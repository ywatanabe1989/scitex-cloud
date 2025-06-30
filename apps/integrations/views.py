from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.http import JsonResponse
from django.urls import reverse
from django.utils import timezone
from requests_oauthlib import OAuth2Session
import requests
import json

from .models import ORCIDProfile, ExternalServiceConnection


# ORCID OAuth2 Configuration
ORCID_CLIENT_ID = getattr(settings, 'ORCID_CLIENT_ID', 'your-orcid-client-id')
ORCID_CLIENT_SECRET = getattr(settings, 'ORCID_CLIENT_SECRET', 'your-orcid-client-secret')
ORCID_SANDBOX = getattr(settings, 'ORCID_SANDBOX', True)

if ORCID_SANDBOX:
    ORCID_BASE_URL = 'https://sandbox.orcid.org'
    ORCID_API_URL = 'https://api.sandbox.orcid.org'
else:
    ORCID_BASE_URL = 'https://orcid.org'
    ORCID_API_URL = 'https://api.orcid.org'

ORCID_AUTHORIZATION_URL = f'{ORCID_BASE_URL}/oauth/authorize'
ORCID_TOKEN_URL = f'{ORCID_BASE_URL}/oauth/token'


@login_required
def orcid_connect(request):
    """Initiate ORCID OAuth2 flow"""
    try:
        # Create OAuth2 session
        orcid = OAuth2Session(
            ORCID_CLIENT_ID,
            scope=['/authenticate', '/read-limited'],
            redirect_uri=request.build_absolute_uri(reverse('integrations:orcid_callback'))
        )
        
        authorization_url, state = orcid.authorization_url(ORCID_AUTHORIZATION_URL)
        
        # Store state in session for security
        request.session['oauth_state'] = state
        
        return redirect(authorization_url)
        
    except Exception as e:
        messages.error(request, f'Error connecting to ORCID: {str(e)}')
        return redirect('integrations:profile')


@login_required
def orcid_callback(request):
    """Handle ORCID OAuth2 callback"""
    try:
        # Verify state parameter
        if request.GET.get('state') != request.session.get('oauth_state'):
            messages.error(request, 'Invalid OAuth state parameter')
            return redirect('integrations:profile')
        
        # Get authorization code
        authorization_code = request.GET.get('code')
        if not authorization_code:
            messages.error(request, 'No authorization code received from ORCID')
            return redirect('integrations:profile')
        
        # Exchange authorization code for access token
        orcid = OAuth2Session(
            ORCID_CLIENT_ID,
            redirect_uri=request.build_absolute_uri(reverse('integrations:orcid_callback'))
        )
        
        token = orcid.fetch_token(
            ORCID_TOKEN_URL,
            authorization_response=request.build_absolute_uri(),
            client_secret=ORCID_CLIENT_SECRET
        )
        
        # Extract ORCID ID from token response
        orcid_id = token.get('orcid')
        if not orcid_id:
            messages.error(request, 'No ORCID ID received from authentication')
            return redirect('integrations:profile')
        
        # Fetch user profile data from ORCID API
        profile_data = fetch_orcid_profile(orcid_id, token['access_token'])
        
        # Create or update ORCID profile
        orcid_profile, created = ORCIDProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'orcid_id': orcid_id,
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token', ''),
                'token_expires_at': timezone.now() + timezone.timedelta(
                    seconds=token.get('expires_in', 3600)
                ),
                'given_name': profile_data.get('given_name', ''),
                'family_name': profile_data.get('family_name', ''),
                'email': profile_data.get('email', ''),
                'biography': profile_data.get('biography', ''),
                'last_sync': timezone.now(),
            }
        )
        
        # Create external service connection record
        ExternalServiceConnection.objects.update_or_create(
            user=request.user,
            service='orcid',
            defaults={
                'service_user_id': orcid_id,
                'service_username': profile_data.get('given_name', '') + ' ' + profile_data.get('family_name', ''),
                'access_token': token['access_token'],
                'refresh_token': token.get('refresh_token', ''),
                'token_expires_at': timezone.now() + timezone.timedelta(
                    seconds=token.get('expires_in', 3600)
                ),
                'status': 'active',
                'last_sync': timezone.now(),
                'connection_data': profile_data,
            }
        )
        
        if created:
            messages.success(request, f'Successfully connected to ORCID profile: {orcid_id}')
        else:
            messages.success(request, f'Updated ORCID profile connection: {orcid_id}')
        
        return redirect('integrations:profile')
        
    except Exception as e:
        messages.error(request, f'Error processing ORCID callback: {str(e)}')
        return redirect('integrations:profile')


@login_required
def orcid_disconnect(request):
    """Disconnect ORCID profile"""
    try:
        # Delete ORCID profile
        ORCIDProfile.objects.filter(user=request.user).delete()
        
        # Update external service connection
        ExternalServiceConnection.objects.filter(
            user=request.user,
            service='orcid'
        ).update(status='revoked')
        
        messages.success(request, 'Successfully disconnected from ORCID')
        
    except Exception as e:
        messages.error(request, f'Error disconnecting ORCID: {str(e)}')
    
    return redirect('integrations:profile')


@login_required
def sync_orcid_profile(request):
    """Manually sync ORCID profile data"""
    try:
        orcid_profile = ORCIDProfile.objects.get(user=request.user)
        
        # Check if token is expired
        if orcid_profile.is_token_expired():
            messages.error(request, 'ORCID access token has expired. Please reconnect.')
            return redirect('integrations:profile')
        
        # Fetch updated profile data
        profile_data = fetch_orcid_profile(orcid_profile.orcid_id, orcid_profile.access_token)
        
        # Update profile data
        orcid_profile.given_name = profile_data.get('given_name', '')
        orcid_profile.family_name = profile_data.get('family_name', '')
        orcid_profile.email = profile_data.get('email', '')
        orcid_profile.biography = profile_data.get('biography', '')
        orcid_profile.last_sync = timezone.now()
        orcid_profile.save()
        
        messages.success(request, 'Successfully synced ORCID profile data')
        
    except ORCIDProfile.DoesNotExist:
        messages.error(request, 'No ORCID profile found. Please connect first.')
    except Exception as e:
        messages.error(request, f'Error syncing ORCID profile: {str(e)}')
    
    return redirect('integrations:profile')


@login_required
def integrations_profile(request):
    """View integrations profile and connections"""
    context = {
        'orcid_profile': None,
        'external_connections': []
    }
    
    try:
        context['orcid_profile'] = ORCIDProfile.objects.get(user=request.user)
    except ORCIDProfile.DoesNotExist:
        pass
    
    context['external_connections'] = ExternalServiceConnection.objects.filter(
        user=request.user
    ).order_by('service')
    
    return render(request, 'integrations/profile.html', context)


def fetch_orcid_profile(orcid_id, access_token):
    """Fetch profile data from ORCID API"""
    try:
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Accept': 'application/json'
        }
        
        # Fetch person details
        person_url = f'{ORCID_API_URL}/v3.0/{orcid_id}/person'
        response = requests.get(person_url, headers=headers)
        response.raise_for_status()
        
        person_data = response.json()
        
        # Extract relevant data
        profile_data = {}
        
        if 'name' in person_data:
            name = person_data['name']
            if name and 'given-names' in name:
                profile_data['given_name'] = name['given-names']['value']
            if name and 'family-name' in name:
                profile_data['family_name'] = name['family-name']['value']
        
        if 'biography' in person_data and person_data['biography']:
            profile_data['biography'] = person_data['biography']['content']
        
        # Try to get email (may require additional permissions)
        if 'emails' in person_data and person_data['emails']['email']:
            emails = person_data['emails']['email']
            if emails:
                # Get first verified email or just first email
                primary_email = None
                for email in emails:
                    if email.get('verified'):
                        primary_email = email['email']
                        break
                if not primary_email and emails:
                    primary_email = emails[0]['email']
                if primary_email:
                    profile_data['email'] = primary_email
        
        return profile_data
        
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error fetching ORCID profile: {e}")
        return {}


@login_required
def api_connection_status(request):
    """API endpoint to check connection status"""
    connections = {}
    
    # Check ORCID connection
    try:
        orcid_profile = ORCIDProfile.objects.get(user=request.user)
        connections['orcid'] = {
            'connected': True,
            'orcid_id': orcid_profile.orcid_id,
            'full_name': orcid_profile.full_name,
            'last_sync': orcid_profile.last_sync.isoformat() if orcid_profile.last_sync else None,
            'token_expired': orcid_profile.is_token_expired(),
        }
    except ORCIDProfile.DoesNotExist:
        connections['orcid'] = {'connected': False}
    
    # Check other external connections
    external_connections = ExternalServiceConnection.objects.filter(user=request.user)
    for conn in external_connections:
        connections[conn.service] = {
            'connected': True,
            'status': conn.status,
            'service_username': conn.service_username,
            'last_sync': conn.last_sync.isoformat() if conn.last_sync else None,
        }
    
    return JsonResponse(connections)
