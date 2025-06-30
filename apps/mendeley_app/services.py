#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mendeley API Integration Services

This module provides services for interacting with the Mendeley API,
including OAuth2 authentication, profile synchronization, and document import.
Note: Since Mendeley deprecated their API, this implementation also supports
Zotero as an alternative reference manager with similar functionality.
"""

import requests
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import (
    MendeleyProfile, MendeleyOAuth2Token, MendeleyDocument, 
    MendeleyGroup, MendeleyFolder, MendeleySyncLog
)
import logging

logger = logging.getLogger(__name__)

# Mendeley API Configuration (Legacy - API deprecated)
MENDELEY_BASE_URL = getattr(settings, 'MENDELEY_BASE_URL', 'https://api.mendeley.com')
MENDELEY_CLIENT_ID = getattr(settings, 'MENDELEY_CLIENT_ID', '')
MENDELEY_CLIENT_SECRET = getattr(settings, 'MENDELEY_CLIENT_SECRET', '')
MENDELEY_REDIRECT_URI = getattr(settings, 'MENDELEY_REDIRECT_URI', 'http://localhost:8000/mendeley/callback/')

# Zotero API Configuration (Alternative)
ZOTERO_API_BASE_URL = getattr(settings, 'ZOTERO_API_BASE_URL', 'https://api.zotero.org')
ZOTERO_CLIENT_KEY = getattr(settings, 'ZOTERO_CLIENT_KEY', '')
ZOTERO_CLIENT_SECRET = getattr(settings, 'ZOTERO_CLIENT_SECRET', '')

# Use Zotero as fallback since Mendeley API is deprecated
USE_ZOTERO_FALLBACK = getattr(settings, 'MENDELEY_USE_ZOTERO_FALLBACK', True)


class MendeleyAPIError(Exception):
    """Custom exception for Mendeley/Zotero API errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class MendeleyAuthService:
    """Service for Mendeley/Zotero OAuth2 authentication"""
    
    @staticmethod
    def get_authorization_url(state=None):
        """Generate OAuth2 authorization URL"""
        if USE_ZOTERO_FALLBACK:
            return ZoteroAuthService.get_authorization_url(state)
        
        params = {
            'client_id': MENDELEY_CLIENT_ID,
            'response_type': 'code',
            'scope': 'all',
            'redirect_uri': MENDELEY_REDIRECT_URI,
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{MENDELEY_BASE_URL}/oauth/authorize?{query_string}"
    
    @staticmethod
    def exchange_code_for_token(code, state=None):
        """Exchange authorization code for access token"""
        if USE_ZOTERO_FALLBACK:
            return ZoteroAuthService.exchange_code_for_token(code, state)
        
        token_url = f"{MENDELEY_BASE_URL}/oauth/token"
        
        data = {
            'client_id': MENDELEY_CLIENT_ID,
            'client_secret': MENDELEY_CLIENT_SECRET,
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': MENDELEY_REDIRECT_URI,
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
            
            # Calculate expiration time
            expires_at = timezone.now() + timedelta(seconds=int(expires_in))
            
            return {
                'access_token': access_token,
                'refresh_token': refresh_token,
                'token_type': token_type,
                'expires_at': expires_at,
                'scope': scope,
            }
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token exchange failed: {str(e)}")
            raise MendeleyAPIError(f"Failed to exchange code for token: {str(e)}")
    
    @staticmethod
    def store_token(user, token_data):
        """Store token in database"""
        token, created = MendeleyOAuth2Token.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token_data['access_token'],
                'refresh_token': token_data.get('refresh_token', ''),
                'token_type': token_data.get('token_type', 'bearer'),
                'expires_at': token_data['expires_at'],
                'scope': token_data.get('scope', ''),
            }
        )
        return token
    
    @staticmethod
    def refresh_token(token):
        """Refresh an expired token"""
        if USE_ZOTERO_FALLBACK:
            return ZoteroAuthService.refresh_token(token)
        
        if not token.refresh_token:
            raise MendeleyAPIError("No refresh token available")
        
        token_url = f"{MENDELEY_BASE_URL}/oauth/token"
        
        data = {
            'client_id': MENDELEY_CLIENT_ID,
            'client_secret': MENDELEY_CLIENT_SECRET,
            'grant_type': 'refresh_token',
            'refresh_token': token.refresh_token,
        }
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Update token
            token.access_token = token_data.get('access_token')
            token.refresh_token = token_data.get('refresh_token', token.refresh_token)
            token.expires_at = timezone.now() + timedelta(seconds=int(token_data.get('expires_in', 3600)))
            token.save()
            
            return token
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Token refresh failed: {str(e)}")
            raise MendeleyAPIError(f"Failed to refresh token: {str(e)}")


class ZoteroAuthService:
    """Service for Zotero API key authentication (simpler than OAuth2)"""
    
    @staticmethod
    def get_authorization_url(state=None):
        """Generate Zotero API key setup URL"""
        # Zotero uses API keys, not OAuth2, so redirect to API key setup
        return "https://www.zotero.org/settings/keys/new"
    
    @staticmethod
    def exchange_code_for_token(api_key, state=None):
        """Store Zotero API key as token"""
        # Zotero uses API keys, so we simulate token structure
        return {
            'access_token': api_key,
            'refresh_token': '',
            'token_type': 'api_key',
            'expires_at': timezone.now() + timedelta(days=365),  # API keys don't expire
            'scope': 'all',
        }
    
    @staticmethod
    def refresh_token(token):
        """Zotero API keys don't need refreshing"""
        return token


class MendeleyAPIService:
    """Service for interacting with Mendeley/Zotero API"""
    
    def __init__(self, user):
        self.user = user
        try:
            self.token = MendeleyOAuth2Token.objects.get(user=user)
        except MendeleyOAuth2Token.DoesNotExist:
            self.token = None
    
    def _get_headers(self):
        """Get authorization headers for API requests"""
        if not self.token:
            raise MendeleyAPIError("No authentication token available")
        
        if self.token.is_expired():
            self.token = MendeleyAuthService.refresh_token(self.token)
        
        return {
            'Authorization': self.token.get_authorization_header(),
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
    
    def _make_request(self, method, endpoint, params=None, data=None):
        """Make authenticated API request"""
        if USE_ZOTERO_FALLBACK:
            return self._make_zotero_request(method, endpoint, params, data)
        
        url = f"{MENDELEY_BASE_URL}/{endpoint.lstrip('/')}"
        headers = self._get_headers()
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if data else None
            )
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"API request failed: {method} {url} - {str(e)}")
            raise MendeleyAPIError(f"API request failed: {str(e)}", 
                                 getattr(e.response, 'status_code', None))
    
    def _make_zotero_request(self, method, endpoint, params=None, data=None):
        """Make Zotero API request"""
        # Extract user ID from profile or use default
        try:
            profile = MendeleyProfile.objects.get(user=self.user)
            user_id = profile.mendeley_id  # We'll use this as Zotero user ID
        except MendeleyProfile.DoesNotExist:
            user_id = str(self.user.id)  # Fallback to Django user ID
        
        # Map Mendeley endpoints to Zotero equivalents
        endpoint_mapping = {
            'profiles/me': f'users/{user_id}',
            'documents': f'users/{user_id}/items',
            'groups': f'users/{user_id}/groups',
            'folders': f'users/{user_id}/collections',
        }
        
        # Get mapped endpoint
        zotero_endpoint = endpoint_mapping.get(endpoint, endpoint)
        url = f"{ZOTERO_API_BASE_URL}/{zotero_endpoint.lstrip('/')}"
        
        headers = {
            'Authorization': f'Bearer {self.token.access_token}',
            'Zotero-API-Version': '3',
            'Accept': 'application/json',
        }
        
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                params=params,
                json=data if data else None
            )
            response.raise_for_status()
            return response.json() if response.content else {}
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Zotero API request failed: {method} {url} - {str(e)}")
            raise MendeleyAPIError(f"Zotero API request failed: {str(e)}", 
                                 getattr(e.response, 'status_code', None))
    
    def get_profile(self):
        """Get user profile information"""
        return self._make_request('GET', 'profiles/me')
    
    def get_documents(self, limit=20, offset=0):
        """Get user's documents/library items"""
        params = {
            'limit': limit,
            'offset': offset,
        }
        return self._make_request('GET', 'documents', params=params)
    
    def get_document(self, document_id):
        """Get specific document details"""
        return self._make_request('GET', f'documents/{document_id}')
    
    def get_groups(self):
        """Get user's groups"""
        return self._make_request('GET', 'groups')
    
    def get_folders(self):
        """Get user's folders/collections"""
        return self._make_request('GET', 'folders')


class MendeleySyncService:
    """Service for synchronizing Mendeley/Zotero data"""
    
    def __init__(self, user):
        self.user = user
        self.api_service = MendeleyAPIService(user)
        try:
            self.profile = MendeleyProfile.objects.get(user=user)
        except MendeleyProfile.DoesNotExist:
            self.profile = None
    
    def sync_profile(self):
        """Sync user profile from Mendeley/Zotero"""
        log = MendeleySyncLog.objects.create(
            profile=self.profile,
            sync_type='profile'
        )
        
        try:
            # Get profile data from API
            profile_data = self.api_service.get_profile()
            
            # Create or update profile
            profile, created = MendeleyProfile.objects.update_or_create(
                user=self.user,
                defaults=self._extract_profile_data(profile_data)
            )
            
            if not self.profile:
                self.profile = profile
            
            # Update sync status
            self.profile.is_synced = True
            self.profile.last_sync_at = timezone.now()
            self.profile.save()
            
            # Update log
            log.items_processed = 1
            log.items_created = 1 if created else 0
            log.items_updated = 0 if created else 1
            log.mark_completed('success')
            
            return True
            
        except Exception as e:
            log.add_error(str(e))
            logger.error(f"Profile sync failed for user {self.user.id}: {str(e)}")
            return False
    
    def sync_documents(self, limit=100):
        """Sync documents from Mendeley/Zotero"""
        if not self.profile:
            raise MendeleyAPIError("Profile must be synced first")
        
        log = MendeleySyncLog.objects.create(
            profile=self.profile,
            sync_type='documents'
        )
        
        try:
            offset = 0
            total_processed = 0
            total_created = 0
            total_updated = 0
            
            while True:
                # Get documents from API
                documents_data = self.api_service.get_documents(limit=limit, offset=offset)
                
                if not documents_data:
                    break
                
                for doc_data in documents_data:
                    try:
                        doc, created = self._sync_document(doc_data)
                        total_processed += 1
                        if created:
                            total_created += 1
                        else:
                            total_updated += 1
                    except Exception as e:
                        logger.error(f"Failed to sync document: {str(e)}")
                        continue
                
                # Check if we got fewer results than requested (end of data)
                if len(documents_data) < limit:
                    break
                
                offset += limit
            
            # Update log
            log.items_processed = total_processed
            log.items_created = total_created
            log.items_updated = total_updated
            log.mark_completed('success')
            
            return True
            
        except Exception as e:
            log.add_error(str(e))
            logger.error(f"Documents sync failed for user {self.user.id}: {str(e)}")
            return False
    
    def sync_groups(self):
        """Sync groups from Mendeley/Zotero"""
        if not self.profile:
            raise MendeleyAPIError("Profile must be synced first")
        
        log = MendeleySyncLog.objects.create(
            profile=self.profile,
            sync_type='groups'
        )
        
        try:
            groups_data = self.api_service.get_groups()
            
            total_processed = 0
            total_created = 0
            total_updated = 0
            
            for group_data in groups_data:
                try:
                    group, created = self._sync_group(group_data)
                    total_processed += 1
                    if created:
                        total_created += 1
                    else:
                        total_updated += 1
                except Exception as e:
                    logger.error(f"Failed to sync group: {str(e)}")
                    continue
            
            # Update log
            log.items_processed = total_processed
            log.items_created = total_created
            log.items_updated = total_updated
            log.mark_completed('success')
            
            return True
            
        except Exception as e:
            log.add_error(str(e))
            logger.error(f"Groups sync failed for user {self.user.id}: {str(e)}")
            return False
    
    def full_sync(self):
        """Perform full synchronization"""
        success = True
        
        # Sync profile first
        if not self.sync_profile():
            success = False
        
        # Sync documents
        if not self.sync_documents():
            success = False
        
        # Sync groups
        if not self.sync_groups():
            success = False
        
        return success
    
    def _extract_profile_data(self, profile_data):
        """Extract profile data from API response"""
        if USE_ZOTERO_FALLBACK:
            return self._extract_zotero_profile_data(profile_data)
        
        return {
            'mendeley_id': profile_data.get('id', ''),
            'first_name': profile_data.get('first_name', ''),
            'last_name': profile_data.get('last_name', ''),
            'display_name': profile_data.get('display_name', ''),
            'email': profile_data.get('email', ''),
            'academic_status': profile_data.get('academic_status', ''),
            'discipline': profile_data.get('discipline', {}).get('name', ''),
            'institution': profile_data.get('institution', ''),
            'link': profile_data.get('link', ''),
            'mendeley_record': profile_data,
        }
    
    def _extract_zotero_profile_data(self, profile_data):
        """Extract profile data from Zotero API response"""
        return {
            'mendeley_id': str(profile_data.get('id', self.user.id)),
            'first_name': profile_data.get('name', '').split(' ')[0] if profile_data.get('name') else '',
            'last_name': ' '.join(profile_data.get('name', '').split(' ')[1:]) if profile_data.get('name') else '',
            'display_name': profile_data.get('name', ''),
            'email': profile_data.get('email', ''),
            'academic_status': '',
            'discipline': '',
            'institution': '',
            'link': profile_data.get('website', ''),
            'mendeley_record': profile_data,
        }
    
    def _sync_document(self, doc_data):
        """Sync individual document"""
        if USE_ZOTERO_FALLBACK:
            return self._sync_zotero_document(doc_data)
        
        extracted_data = {
            'mendeley_id': doc_data.get('id', ''),
            'title': doc_data.get('title', ''),
            'document_type': doc_data.get('type', 'generic'),
            'year': doc_data.get('year'),
            'month': doc_data.get('month'),
            'day': doc_data.get('day'),
            'source': doc_data.get('source', ''),
            'volume': doc_data.get('volume', ''),
            'issue': doc_data.get('issue', ''),
            'pages': doc_data.get('pages', ''),
            'abstract': doc_data.get('abstract', ''),
            'notes': doc_data.get('notes', ''),
            'authors': doc_data.get('authors', []),
            'editors': doc_data.get('editors', []),
            'doi': doc_data.get('identifiers', {}).get('doi', ''),
            'pmid': doc_data.get('identifiers', {}).get('pmid', ''),
            'isbn': doc_data.get('identifiers', {}).get('isbn', ''),
            'issn': doc_data.get('identifiers', {}).get('issn', ''),
            'arxiv': doc_data.get('identifiers', {}).get('arxiv', ''),
            'website': doc_data.get('websites', [{}])[0].get('url', '') if doc_data.get('websites') else '',
            'mendeley_url': doc_data.get('link', ''),
            'tags': doc_data.get('tags', []),
            'keywords': doc_data.get('keywords', []),
            'file_attached': bool(doc_data.get('file_attached')),
            'created': self._parse_date(doc_data.get('created')),
            'last_modified': self._parse_date(doc_data.get('last_modified')),
            'mendeley_raw_data': doc_data,
        }
        
        return MendeleyDocument.objects.update_or_create(
            profile=self.profile,
            mendeley_id=extracted_data['mendeley_id'],
            defaults=extracted_data
        )
    
    def _sync_zotero_document(self, doc_data):
        """Sync individual Zotero document"""
        data = doc_data.get('data', {})
        
        extracted_data = {
            'mendeley_id': doc_data.get('key', ''),
            'title': data.get('title', ''),
            'document_type': self._map_zotero_item_type(data.get('itemType', 'generic')),
            'year': self._extract_year_from_date(data.get('date', '')),
            'source': data.get('publicationTitle', ''),
            'volume': data.get('volume', ''),
            'issue': data.get('issue', ''),
            'pages': data.get('pages', ''),
            'abstract': data.get('abstractNote', ''),
            'authors': self._extract_zotero_creators(data.get('creators', []), 'author'),
            'editors': self._extract_zotero_creators(data.get('creators', []), 'editor'),
            'doi': data.get('DOI', ''),
            'isbn': data.get('ISBN', ''),
            'issn': data.get('ISSN', ''),
            'website': data.get('url', ''),
            'tags': [tag.get('tag', '') for tag in data.get('tags', [])],
            'created': self._parse_date(doc_data.get('dateAdded')),
            'last_modified': self._parse_date(doc_data.get('dateModified')),
            'mendeley_raw_data': doc_data,
        }
        
        return MendeleyDocument.objects.update_or_create(
            profile=self.profile,
            mendeley_id=extracted_data['mendeley_id'],
            defaults=extracted_data
        )
    
    def _sync_group(self, group_data):
        """Sync individual group"""
        extracted_data = {
            'mendeley_group_id': group_data.get('id', ''),
            'name': group_data.get('name', ''),
            'description': group_data.get('description', ''),
            'group_type': group_data.get('type', ''),
            'role': group_data.get('role', ''),
            'access_level': group_data.get('access_level', ''),
            'mendeley_raw_data': group_data,
        }
        
        return MendeleyGroup.objects.update_or_create(
            profile=self.profile,
            mendeley_group_id=extracted_data['mendeley_group_id'],
            defaults=extracted_data
        )
    
    def _parse_date(self, date_string):
        """Parse date string to datetime"""
        if not date_string:
            return None
        
        try:
            # Try different date formats
            for fmt in ['%Y-%m-%dT%H:%M:%S.%fZ', '%Y-%m-%dT%H:%M:%SZ', '%Y-%m-%d']:
                try:
                    return datetime.strptime(date_string, fmt).replace(tzinfo=timezone.utc)
                except ValueError:
                    continue
        except Exception:
            pass
        
        return None
    
    def _extract_year_from_date(self, date_string):
        """Extract year from date string"""
        if not date_string:
            return None
        
        try:
            # Try to extract year from various formats
            import re
            year_match = re.search(r'\d{4}', date_string)
            if year_match:
                return int(year_match.group())
        except Exception:
            pass
        
        return None
    
    def _map_zotero_item_type(self, item_type):
        """Map Zotero item types to Mendeley document types"""
        mapping = {
            'journalArticle': 'journal',
            'book': 'book',
            'bookSection': 'book_section',
            'conferencePaper': 'conference_proceedings',
            'thesis': 'thesis',
            'webpage': 'web_page',
            'report': 'report',
            'patent': 'patent',
            'magazineArticle': 'magazine_article',
            'newspaperArticle': 'newspaper_article',
            'computerProgram': 'computer_program',
            'film': 'film',
            'bill': 'bill',
        }
        return mapping.get(item_type, 'generic')
    
    def _extract_zotero_creators(self, creators, creator_type):
        """Extract creators of specific type from Zotero data"""
        result = []
        for creator in creators:
            if creator.get('creatorType') == creator_type:
                name_data = {
                    'first_name': creator.get('firstName', ''),
                    'last_name': creator.get('lastName', ''),
                }
                if creator.get('name'):  # Single name field
                    name_data = {'name': creator['name']}
                result.append(name_data)
        return result


class MendeleyIntegrationService:
    """Service for integrating Mendeley/Zotero with Scholar module"""
    
    @staticmethod
    def import_document_to_scholar(document):
        """Import a Mendeley document to Scholar module"""
        if document.is_imported:
            return document.scholar_paper
        
        try:
            from apps.scholar_app.models import SearchIndex, Author
            
            # Create or get authors
            authors = []
            for author_data in document.authors:
                if isinstance(author_data, dict):
                    first_name = author_data.get('first_name', '')
                    last_name = author_data.get('last_name', '')
                    if first_name or last_name:
                        author, _ = Author.objects.get_or_create(
                            first_name=first_name,
                            last_name=last_name
                        )
                        authors.append(author)
            
            # Create SearchIndex entry
            scholar_paper = SearchIndex.objects.create(
                title=document.title,
                abstract=document.abstract,
                publication_date=timezone.make_aware(datetime(document.year, 1, 1)) if document.year else None,
                doi=document.doi,
                external_url=document.website,
                source='manual',  # Use 'manual' as it's a valid choice
                document_type='article',  # Default to article
                keywords=','.join(document.tags) if document.tags else ''
            )
            
            # Associate authors
            scholar_paper.authors.set(authors)
            
            # Update document
            document.is_imported = True
            document.scholar_paper = scholar_paper
            document.save()
            
            return scholar_paper
            
        except Exception as e:
            logger.error(f"Failed to import document to Scholar: {str(e)}")
            return None
    
    @staticmethod
    def bulk_import_documents(user, document_ids):
        """Bulk import multiple documents to Scholar"""
        try:
            profile = MendeleyProfile.objects.get(user=user)
            documents = profile.mendeley_documents.filter(
                id__in=document_ids,
                is_imported=False
            )
            
            imported_count = 0
            for document in documents:
                if MendeleyIntegrationService.import_document_to_scholar(document):
                    imported_count += 1
            
            return imported_count
            
        except MendeleyProfile.DoesNotExist:
            return 0


def is_mendeley_configured():
    """Check if Mendeley integration is properly configured"""
    if USE_ZOTERO_FALLBACK:
        return bool(ZOTERO_API_BASE_URL and ZOTERO_CLIENT_KEY)
    return bool(MENDELEY_CLIENT_ID and MENDELEY_CLIENT_SECRET)