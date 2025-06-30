#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ORCID API Integration Services

This module provides services for interacting with the ORCID API,
including OAuth2 authentication, profile synchronization, and publication import.
"""

import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import OrcidProfile, OrcidOAuth2Token, OrcidPublication, OrcidWork, OrcidSyncLog
import logging

logger = logging.getLogger(__name__)

# ORCID API Configuration
ORCID_BASE_URL = getattr(settings, 'ORCID_BASE_URL', 'https://orcid.org')
ORCID_API_BASE_URL = getattr(settings, 'ORCID_API_BASE_URL', 'https://pub.orcid.org/v3.0')
ORCID_SANDBOX_API_URL = 'https://pub.sandbox.orcid.org/v3.0'
ORCID_CLIENT_ID = getattr(settings, 'ORCID_CLIENT_ID', '')
ORCID_CLIENT_SECRET = getattr(settings, 'ORCID_CLIENT_SECRET', '')
ORCID_REDIRECT_URI = getattr(settings, 'ORCID_REDIRECT_URI', 'http://localhost:8000/orcid/callback/')

# Use sandbox for development
USE_ORCID_SANDBOX = getattr(settings, 'ORCID_USE_SANDBOX', True)
if USE_ORCID_SANDBOX:
    ORCID_API_BASE_URL = ORCID_SANDBOX_API_URL
    ORCID_BASE_URL = 'https://sandbox.orcid.org'


class OrcidAPIError(Exception):
    """Custom exception for ORCID API errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class OrcidAuthService:
    """Service for ORCID OAuth2 authentication"""
    
    @staticmethod
    def get_authorization_url(state=None):
        """Generate ORCID OAuth2 authorization URL"""
        params = {
            'client_id': ORCID_CLIENT_ID,
            'response_type': 'code',
            'scope': '/authenticate /read-limited',
            'redirect_uri': ORCID_REDIRECT_URI,
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{ORCID_BASE_URL}/oauth/authorize?{query_string}"
    
    @staticmethod
    def exchange_code_for_token(code, state=None):
        """Exchange authorization code for access token"""
        token_url = f"{ORCID_BASE_URL}/oauth/token"
        
        data = {
            'client_id': ORCID_CLIENT_ID,
            'client_secret': ORCID_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': ORCID_REDIRECT_URI,
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Extract token information
            access_token = token_data.get('access_token')
            refresh_token = token_data.get('refresh_token', '')
            token_type = token_data.get('token_type', 'bearer')
            expires_in = token_data.get('expires_in', 3600)  # Default 1 hour
            scope = token_data.get('scope', '')
            orcid_id = token_data.get('orcid')
            
            # Calculate expiration time
            expires_at = timezone.now() + timedelta(seconds=int(expires_in))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': token_type,
                'expires_at': expires_at,
                'scope': scope,
                'orcid_id': orcid_id,
            }
            
        except requests.RequestException as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise OrcidAPIError(f"Failed to exchange authorization code: {str(e)}")
    
    @staticmethod
    def refresh_access_token(refresh_token):
        """Refresh an expired access token"""
        token_url = f"{ORCID_BASE_URL}/oauth/token"
        
        data = {
            'client_id': ORCID_CLIENT_ID,
            'client_secret': ORCID_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': refresh_token,
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            access_token = token_data.get('access_token')
            new_refresh_token = token_data.get('refresh_token', refresh_token)
            expires_in = token_data.get('expires_in', 3600)
            expires_at = timezone.now() + timedelta(seconds=int(expires_in))
            
            return {
                'access_token': access_token,
                'refresh_token': new_refresh_token,
                'expires_at': expires_at,
            }
            
        except requests.RequestException as e:
            logger.error(f"Error refreshing token: {e}")
            raise OrcidAPIError(f"Failed to refresh access token: {str(e)}")
    
    @staticmethod
    def store_token(user, token_data):
        """Store or update ORCID token for user"""
        token, created = OrcidOAuth2Token.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'token_type': token_data.get('token_type', 'bearer'),
                'scope': token_data.get('scope', ''),
                'expires_at': token_data['expires_at'],
                'orcid_id': token_data['orcid_id'],
            }
        )
        
        return token
    
    @staticmethod
    def get_valid_token(user):
        """Get a valid access token for user, refreshing if necessary"""
        try:
            token = OrcidOAuth2Token.objects.get(user=user)
            
            if token.is_expired():
                if token.refresh_token:
                    # Try to refresh the token
                    try:
                        new_token_data = OrcidAuthService.refresh_access_token(token.refresh_token)
                        token.access_token = new_token_data['access_token']
                        token.refresh_token = new_token_data['refresh_token']
                        token.expires_at = new_token_data['expires_at']
                        token.save()
                        return token
                    except OrcidAPIError:
                        # Refresh failed, token is invalid
                        return None
                else:
                    # No refresh token, cannot refresh
                    return None
            
            return token
            
        except OrcidOAuth2Token.DoesNotExist:
            return None


class OrcidAPIService:
    """Service for interacting with ORCID API"""
    
    def __init__(self, user=None, access_token=None):
        self.user = user
        self.access_token = access_token
        
        if user and not access_token:
            token = OrcidAuthService.get_valid_token(user)
            if token:
                self.access_token = token.access_token
    
    def _make_request(self, endpoint, orcid_id=None, method='GET', data=None):
        """Make authenticated request to ORCID API"""
        if not self.access_token:
            raise OrcidAPIError("No valid access token available")
        
        if orcid_id:
            url = f"{ORCID_API_BASE_URL}/{orcid_id}/{endpoint}"
        else:
            url = f"{ORCID_API_BASE_URL}/{endpoint}"
        
        headers = {
            'Accept': 'application/json',
            'Authorization': f'Bearer {self.access_token}',
        }
        
        if method == 'POST' and data:
            headers['Content-Type'] = 'application/json'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
            else:
                raise OrcidAPIError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"ORCID API request failed: {e}")
            raise OrcidAPIError(f"API request failed: {str(e)}", 
                              status_code=getattr(e.response, 'status_code', None),
                              response_data=getattr(e.response, 'text', None))
    
    def get_profile(self, orcid_id):
        """Get ORCID profile information"""
        return self._make_request('record', orcid_id=orcid_id)
    
    def get_person(self, orcid_id):
        """Get person information from ORCID"""
        return self._make_request('person', orcid_id=orcid_id)
    
    def get_works(self, orcid_id):
        """Get works summary from ORCID"""
        return self._make_request('works', orcid_id=orcid_id)
    
    def get_work_details(self, orcid_id, put_code):
        """Get detailed information for a specific work"""
        return self._make_request(f'work/{put_code}', orcid_id=orcid_id)
    
    def get_employments(self, orcid_id):
        """Get employment information"""
        return self._make_request('employments', orcid_id=orcid_id)
    
    def get_educations(self, orcid_id):
        """Get education information"""
        return self._make_request('educations', orcid_id=orcid_id)


class OrcidSyncService:
    """Service for synchronizing ORCID data with local database"""
    
    def __init__(self, user):
        self.user = user
        self.api_service = OrcidAPIService(user=user)
        
        # Get or create ORCID profile
        try:
            token = OrcidOAuth2Token.objects.get(user=user)
            self.orcid_profile, created = OrcidProfile.objects.get_or_create(
                user=user,
                defaults={'orcid_id': token.orcid_id}
            )
        except OrcidOAuth2Token.DoesNotExist:
            raise OrcidAPIError("User does not have ORCID authentication")
    
    def sync_profile(self):
        """Sync user's ORCID profile information"""
        sync_log = OrcidSyncLog.objects.create(
            profile=self.orcid_profile,
            sync_type='profile'
        )
        
        try:
            # Get person data from ORCID
            person_data = self.api_service.get_person(self.orcid_profile.orcid_id)
            
            # Extract profile information
            name = person_data.get('name', {})
            bio = person_data.get('biography', {})
            
            # Update profile
            self.orcid_profile.given_name = name.get('given-names', {}).get('value', '')
            self.orcid_profile.family_name = name.get('family-name', {}).get('value', '')
            self.orcid_profile.credit_name = name.get('credit-name', {}).get('value', '') if name.get('credit-name') else ''
            self.orcid_profile.biography = bio.get('content', '') if bio else ''
            
            # Extract researcher URLs
            urls = person_data.get('researcher-urls', {}).get('researcher-url', [])
            self.orcid_profile.researcher_urls = [
                {
                    'name': url.get('url-name'),
                    'url': url.get('url', {}).get('value'),
                }
                for url in urls
            ]
            
            # Extract keywords
            keywords = person_data.get('keywords', {}).get('keyword', [])
            self.orcid_profile.keywords = [kw.get('content') for kw in keywords if kw.get('content')]
            
            # Store raw record
            self.orcid_profile.orcid_record = person_data
            self.orcid_profile.is_synced = True
            self.orcid_profile.last_sync_at = timezone.now()
            self.orcid_profile.save()
            
            sync_log.items_processed = 1
            sync_log.items_updated = 1
            sync_log.mark_completed('success')
            
            logger.info(f"Successfully synced ORCID profile for {self.user.username}")
            return True
            
        except Exception as e:
            sync_log.add_error(f"Profile sync failed: {str(e)}")
            logger.error(f"Failed to sync ORCID profile for {self.user.username}: {e}")
            return False
    
    def sync_works(self):
        """Sync user's ORCID works/publications"""
        sync_log = OrcidSyncLog.objects.create(
            profile=self.orcid_profile,
            sync_type='publications'
        )
        
        try:
            # Get works summary
            works_data = self.api_service.get_works(self.orcid_profile.orcid_id)
            works_group = works_data.get('group', [])
            
            created_count = 0
            updated_count = 0
            processed_count = 0
            
            for group in works_group:
                work_summary = group.get('work-summary', [])
                if work_summary:
                    # Take the first work summary (preferred version)
                    work = work_summary[0]
                    put_code = work.get('put-code')
                    
                    if put_code:
                        processed_count += 1
                        
                        # Get detailed work information
                        try:
                            work_details = self.api_service.get_work_details(
                                self.orcid_profile.orcid_id, 
                                put_code
                            )
                            
                            # Create or update publication
                            pub, created = self._create_or_update_publication(work_details, put_code)
                            
                            if created:
                                created_count += 1
                            else:
                                updated_count += 1
                                
                        except Exception as e:
                            logger.warning(f"Failed to process work {put_code}: {e}")
                            continue
            
            sync_log.items_processed = processed_count
            sync_log.items_created = created_count
            sync_log.items_updated = updated_count
            sync_log.mark_completed('success')
            
            logger.info(f"Successfully synced {processed_count} works for {self.user.username}")
            return True
            
        except Exception as e:
            sync_log.add_error(f"Works sync failed: {str(e)}")
            logger.error(f"Failed to sync ORCID works for {self.user.username}: {e}")
            return False
    
    def _create_or_update_publication(self, work_data, put_code):
        """Create or update a publication from ORCID work data"""
        # Extract basic information
        title = work_data.get('title', {}).get('title', {}).get('value', '')
        work_type = work_data.get('type', 'other')
        
        # Extract publication date
        pub_date = work_data.get('publication-date')
        publication_year = None
        publication_date = None
        
        if pub_date:
            year = pub_date.get('year', {}).get('value')
            month = pub_date.get('month', {}).get('value')
            day = pub_date.get('day', {}).get('value')
            
            if year:
                publication_year = int(year)
                
                if month and day:
                    try:
                        publication_date = datetime(int(year), int(month), int(day)).date()
                    except (ValueError, TypeError):
                        publication_date = None
        
        # Extract journal information
        journal_title = ''
        journal_data = work_data.get('journal-title')
        if journal_data:
            journal_title = journal_data.get('value', '')
        
        # Extract external identifiers
        external_ids = work_data.get('external-ids', {}).get('external-id', [])
        doi = ''
        pmid = ''
        url = ''
        
        for ext_id in external_ids:
            id_type = ext_id.get('external-id-type')
            id_value = ext_id.get('external-id-value')
            
            if id_type == 'doi' and id_value:
                doi = id_value
            elif id_type == 'pmid' and id_value:
                pmid = id_value
            elif id_type == 'uri' and id_value:
                url = id_value
        
        # Extract contributors (authors)
        contributors = work_data.get('contributors', {}).get('contributor', [])
        authors = []
        
        for contrib in contributors:
            credit_name = contrib.get('credit-name')
            if credit_name:
                authors.append({
                    'credit-name': credit_name.get('value', ''),
                    'orcid': contrib.get('contributor-orcid', {}).get('path') if contrib.get('contributor-orcid') else None,
                })
        
        # Create or update publication
        pub, created = OrcidPublication.objects.update_or_create(
            profile=self.orcid_profile,
            orcid_put_code=str(put_code),
            defaults={
                'title': title,
                'publication_type': work_type,
                'publication_year': publication_year,
                'publication_date': publication_date,
                'journal': journal_title,
                'doi': doi,
                'pmid': pmid,
                'url': url,
                'authors': authors,
                'orcid_raw_data': work_data,
            }
        )
        
        return pub, created
    
    def full_sync(self):
        """Perform full synchronization of profile and works"""
        sync_log = OrcidSyncLog.objects.create(
            profile=self.orcid_profile,
            sync_type='full'
        )
        
        try:
            profile_success = self.sync_profile()
            works_success = self.sync_works()
            
            if profile_success and works_success:
                sync_log.mark_completed('success')
                return True
            elif profile_success or works_success:
                sync_log.mark_completed('partial')
                return True
            else:
                sync_log.mark_completed('failed')
                return False
                
        except Exception as e:
            sync_log.add_error(f"Full sync failed: {str(e)}")
            return False


class OrcidIntegrationService:
    """Service for integrating ORCID data with Scholar module"""
    
    @staticmethod
    def import_publication_to_scholar(orcid_publication):
        """Import ORCID publication to Scholar module"""
        from apps.scholar_app.models import SearchIndex, Author, AuthorPaper
        
        if orcid_publication.is_imported:
            return orcid_publication.scholar_paper
        
        try:
            # Create or find existing paper in Scholar
            scholar_paper, created = SearchIndex.objects.get_or_create(
                doi=orcid_publication.doi,
                defaults={
                    'title': orcid_publication.title,
                    'abstract': orcid_publication.abstract,
                    'publication_date': orcid_publication.publication_date,
                    'source': 'orcid',
                    'document_type': 'article' if orcid_publication.publication_type == 'journal-article' else 'other',
                }
            )
            
            # Create journal if needed
            if orcid_publication.journal and not scholar_paper.journal:
                from apps.scholar_app.models import Journal
                journal, _ = Journal.objects.get_or_create(
                    name=orcid_publication.journal,
                    defaults={'abbreviation': orcid_publication.journal[:100]}
                )
                scholar_paper.journal = journal
                scholar_paper.save()
            
            # Create authors
            if orcid_publication.authors:
                for i, author_data in enumerate(orcid_publication.authors):
                    if isinstance(author_data, dict):
                        credit_name = author_data.get('credit-name', '')
                        if credit_name:
                            # Try to parse name
                            name_parts = credit_name.split(' ')
                            given_name = name_parts[0] if name_parts else ''
                            family_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                            
                            author, _ = Author.objects.get_or_create(
                                first_name=given_name,
                                last_name=family_name,
                                defaults={'orcid': author_data.get('orcid', '')}
                            )
                            
                            AuthorPaper.objects.get_or_create(
                                author=author,
                                paper=scholar_paper,
                                defaults={'author_order': i + 1}
                            )
            
            # Link to ORCID publication
            orcid_publication.is_imported = True
            orcid_publication.scholar_paper = scholar_paper
            orcid_publication.save()
            
            logger.info(f"Successfully imported ORCID publication to Scholar: {orcid_publication.title}")
            return scholar_paper
            
        except Exception as e:
            logger.error(f"Failed to import ORCID publication to Scholar: {e}")
            return None
    
    @staticmethod
    def bulk_import_publications(user, publication_ids=None):
        """Import multiple ORCID publications to Scholar"""
        try:
            profile = OrcidProfile.objects.get(user=user)
            
            if publication_ids:
                publications = profile.orcid_publications.filter(id__in=publication_ids)
            else:
                publications = profile.orcid_publications.filter(is_imported=False)
            
            imported_count = 0
            
            for pub in publications:
                if pub.can_import_to_scholar():
                    scholar_paper = OrcidIntegrationService.import_publication_to_scholar(pub)
                    if scholar_paper:
                        imported_count += 1
            
            logger.info(f"Bulk imported {imported_count} publications to Scholar for {user.username}")
            return imported_count
            
        except OrcidProfile.DoesNotExist:
            logger.error(f"No ORCID profile found for user {user.username}")
            return 0
        except Exception as e:
            logger.error(f"Bulk import failed for user {user.username}: {e}")
            return 0


# Utility functions
def is_orcid_configured():
    """Check if ORCID integration is properly configured"""
    return bool(ORCID_CLIENT_ID and ORCID_CLIENT_SECRET)


def validate_orcid_id(orcid_id):
    """Validate ORCID iD format"""
    import re
    pattern = r'^(\d{4}-){3}\d{3}[\dX]$'
    return bool(re.match(pattern, orcid_id))


def format_orcid_id(orcid_id):
    """Format ORCID iD with proper dashes"""
    # Remove any existing formatting
    clean_id = ''.join(c for c in orcid_id if c.isdigit() or c.upper() == 'X')
    
    if len(clean_id) == 16:
        return f"{clean_id[:4]}-{clean_id[4:8]}-{clean_id[8:12]}-{clean_id[12:16]}"
    
    return orcid_id