"""
Zotero API service implementation.
Handles authentication and data access for Zotero reference manager.
"""

import json
import requests
from typing import Dict, List, Optional, Any
from urllib.parse import urlencode, quote
from django.conf import settings
from django.utils import timezone

from .base_service import (
    BaseReferenceService,
    AuthenticationError,
    RateLimitError,
    ServiceUnavailableError,
    ReferenceServiceException
)


class ZoteroService(BaseReferenceService):
    """Zotero API service implementation."""
    
    @property
    def service_name(self) -> str:
        return 'zotero'
    
    @property
    def base_url(self) -> str:
        return 'https://api.zotero.org'
    
    @property
    def oauth_config(self) -> Dict[str, str]:
        return {
            'client_id': getattr(settings, 'ZOTERO_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'ZOTERO_CLIENT_SECRET', ''),
            'auth_url': 'https://www.zotero.org/oauth/authorize',
            'token_url': 'https://www.zotero.org/oauth/access',
            'request_token_url': 'https://www.zotero.org/oauth/request',
        }
    
    def get_oauth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Zotero OAuth authorization URL (OAuth 1.0)."""
        # Zotero uses OAuth 1.0, which requires a request token first
        # This is a simplified implementation - in production, you'd need to handle the full OAuth 1.0 flow
        config = self.oauth_config
        params = {
            'library_access': '1',
            'notes_access': '1',
            'write_access': '1',
            'all_groups': 'read',
        }
        
        if state:
            params['state'] = state
        
        # In a real implementation, you'd first get a request token, then redirect
        return f"{config['auth_url']}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token (OAuth 1.0 flow)."""
        # This is a simplified implementation
        # Zotero uses OAuth 1.0, which has a more complex flow than OAuth 2.0
        
        # For now, assume the 'code' is actually the API key from Zotero
        api_key = code
        
        # Validate the API key by making a test request
        test_url = f"{self.base_url}/users/{self.account.external_user_id or 'current'}"
        headers = {
            'Authorization': f'Bearer {api_key}',
            'Zotero-API-Version': '3'
        }
        
        try:
            response = requests.get(test_url, headers=headers)
            if response.status_code == 200:
                user_data = response.json()
                
                # Update account with API key
                self.account.access_token = api_key
                self.account.external_user_id = str(user_data['userID'])
                self.account.account_name = user_data.get('username', 'Zotero User')
                self.account.status = 'active'
                # Zotero API keys don't expire
                self.account.token_expires_at = None
                self.account.save()
                
                return {
                    'access_token': api_key,
                    'user_id': user_data['userID'],
                    'username': user_data.get('username', ''),
                }
            else:
                raise AuthenticationError("Invalid Zotero API key")
                
        except requests.exceptions.RequestException as e:
            raise AuthenticationError(f"Failed to validate Zotero API key: {e}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Zotero API keys don't expire, so no refresh needed."""
        if not self.account.access_token:
            raise AuthenticationError("No API key available")
        
        # Test if the key is still valid
        try:
            user_info = self.get_user_info()
            return {'access_token': self.account.access_token}
        except Exception as e:
            self.account.status = 'error'
            self.account.save()
            raise AuthenticationError(f"API key is no longer valid: {e}")
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """Make an authenticated API request to Zotero."""
        if not self.account.access_token:
            raise AuthenticationError("No API key available")
        
        if not self.account.can_make_api_call():
            raise RateLimitError(f"API rate limit exceeded for {self.service_name}")
        
        # Prepare URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Add Zotero-specific headers
        headers = kwargs.pop('headers', {})
        headers.update({
            'Authorization': f'Bearer {self.account.access_token}',
            'Zotero-API-Version': '3',
            'User-Agent': 'SciTeX-Cloud/1.0',
        })
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            
            # Update API call count
            self.account.api_calls_today += 1
            self.account.save()
            
            # Handle Zotero-specific errors
            if response.status_code == 403:
                if 'Invalid API key' in response.text:
                    raise AuthenticationError("Invalid API key")
                else:
                    raise RateLimitError("API access forbidden")
            
            elif response.status_code == 429:
                raise RateLimitError("Rate limit exceeded")
            
            elif response.status_code >= 500:
                raise ServiceUnavailableError("Zotero service unavailable")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Zotero API request failed: {e}")
            raise ReferenceServiceException(f"Request failed: {e}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get Zotero user information."""
        if not self.account.external_user_id:
            # Try to get current user info
            endpoint = '/users/current'
        else:
            endpoint = f'/users/{self.account.external_user_id}'
        
        response = self.make_request('GET', endpoint)
        user_data = response.json()
        
        # Update account metadata
        self.account.external_user_id = str(user_data['userID'])
        self.account.account_name = user_data.get('username', 'Zotero User')
        self.account.account_metadata = user_data
        self.account.save()
        
        return user_data
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get list of user's Zotero collections."""
        user_id = self.account.external_user_id
        if not user_id:
            user_info = self.get_user_info()
            user_id = user_info['userID']
        
        # Get personal library collections
        response = self.make_request('GET', f'/users/{user_id}/collections')
        collections_data = response.json()
        
        collections = [{
            'id': 'library',
            'name': 'My Library',
            'description': 'Your personal Zotero library',
            'type': 'personal',
            'parent': None,
            'document_count': 0,
            'created': None,
            'modified': None,
        }]
        
        # Add collections
        for coll in collections_data:
            collections.append({
                'id': coll['key'],
                'name': coll['data']['name'],
                'description': coll['data'].get('description', ''),
                'type': 'collection',
                'parent': coll['data'].get('parentCollection'),
                'document_count': 0,  # Would need separate API call
                'created': coll['meta'].get('createdDate'),
                'modified': coll['meta'].get('lastModified'),
            })
        
        # Get group libraries
        try:
            groups_response = self.make_request('GET', f'/users/{user_id}/groups')
            groups_data = groups_response.json()
            
            for group in groups_data:
                collections.append({
                    'id': f"group-{group['id']}",
                    'name': f"Group: {group['data']['name']}",
                    'description': group['data'].get('description', ''),
                    'type': 'group',
                    'parent': None,
                    'document_count': 0,
                    'created': group['meta'].get('createdDate'),
                    'modified': group['meta'].get('lastModified'),
                })
        except Exception as e:
            self.logger.warning(f"Could not fetch groups: {e}")
        
        return collections
    
    def get_references(self, collection_id: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of items from Zotero."""
        user_id = self.account.external_user_id
        if not user_id:
            user_info = self.get_user_info()
            user_id = user_info['userID']
        
        params = {
            'limit': min(limit, 100),  # Zotero max is 100
            'start': offset,
            'format': 'json',
            'include': 'data,meta',
        }
        
        if collection_id and collection_id != 'library':
            if collection_id.startswith('group-'):
                # Group library
                group_id = collection_id.replace('group-', '')
                endpoint = f'/groups/{group_id}/items'
            else:
                # Collection within personal library
                endpoint = f'/users/{user_id}/collections/{collection_id}/items'
        else:
            # Personal library
            endpoint = f'/users/{user_id}/items'
        
        response = self.make_request('GET', endpoint, params=params)
        items = response.json()
        
        # Normalize items
        normalized_items = []
        for item in items:
            # Skip notes, attachments, etc. - only process bibliographic items
            if item['data'].get('itemType') in ['note', 'attachment']:
                continue
            
            normalized_items.append(self.normalize_reference_data(item))
        
        return normalized_items
    
    def get_reference(self, reference_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific Zotero item."""
        user_id = self.account.external_user_id
        
        response = self.make_request('GET', f'/users/{user_id}/items/{reference_id}')
        item = response.json()
        return self.normalize_reference_data(item)
    
    def create_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new item in Zotero."""
        user_id = self.account.external_user_id
        
        # Convert normalized data to Zotero format
        zotero_data = self._convert_to_zotero_format(reference_data)
        
        response = self.make_request('POST', f'/users/{user_id}/items', json=[zotero_data])
        created_items = response.json()
        
        if created_items['success']:
            # Get the created item
            item_key = list(created_items['success'].keys())[0]
            created_item = self.get_reference(item_key)
            return created_item
        else:
            raise ReferenceServiceException(f"Failed to create item: {created_items}")
    
    def update_reference(self, reference_id: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing item in Zotero."""
        user_id = self.account.external_user_id
        
        # Get current item to get version
        current_item = self.get_reference(reference_id)
        
        # Convert normalized data to Zotero format
        zotero_data = self._convert_to_zotero_format(reference_data)
        zotero_data['key'] = reference_id
        zotero_data['version'] = current_item.get('version', 0)
        
        response = self.make_request('PUT', f'/users/{user_id}/items/{reference_id}', json=zotero_data)
        
        # Return updated item
        return self.get_reference(reference_id)
    
    def delete_reference(self, reference_id: str) -> bool:
        """Delete an item from Zotero."""
        user_id = self.account.external_user_id
        
        try:
            # Get current item version
            current_item = self.get_reference(reference_id)
            version = current_item.get('version', 0)
            
            headers = {'If-Unmodified-Since-Version': str(version)}
            response = self.make_request('DELETE', f'/users/{user_id}/items/{reference_id}', headers=headers)
            return response.status_code == 204
        except Exception as e:
            self.logger.error(f"Failed to delete item {reference_id}: {e}")
            return False
    
    def get_reference_files(self, reference_id: str) -> List[Dict[str, Any]]:
        """Get attachments for a Zotero item."""
        user_id = self.account.external_user_id
        
        response = self.make_request('GET', f'/users/{user_id}/items/{reference_id}/children')
        children = response.json()
        
        files = []
        for child in children:
            if child['data'].get('itemType') == 'attachment':
                attachment = child['data']
                files.append({
                    'id': child['key'],
                    'filename': attachment.get('filename', attachment.get('title', '')),
                    'mime_type': attachment.get('contentType', ''),
                    'size': 0,  # Zotero doesn't provide file size in metadata
                    'download_url': attachment.get('url', ''),
                    'created': child['meta'].get('createdDate'),
                })
        
        return files
    
    def upload_file(self, reference_id: str, file_path: str, file_type: str = 'pdf') -> Dict[str, Any]:
        """Upload a file attachment to a Zotero item."""
        import os
        from mimetypes import guess_type
        
        if not os.path.exists(file_path):
            raise ReferenceServiceException(f"File not found: {file_path}")
        
        user_id = self.account.external_user_id
        filename = os.path.basename(file_path)
        mime_type, _ = guess_type(file_path)
        
        # Create attachment item
        attachment_data = {
            'itemType': 'attachment',
            'parentItem': reference_id,
            'linkMode': 'imported_file',
            'title': filename,
            'filename': filename,
            'contentType': mime_type or 'application/pdf',
        }
        
        # Create the attachment item first
        response = self.make_request('POST', f'/users/{user_id}/items', json=[attachment_data])
        created = response.json()
        
        if not created['success']:
            raise ReferenceServiceException(f"Failed to create attachment: {created}")
        
        attachment_key = list(created['success'].keys())[0]
        
        # Upload the file (this would require multipart upload in real implementation)
        # For now, we'll just return the attachment info
        return {
            'id': attachment_key,
            'filename': filename,
            'mime_type': mime_type,
            'size': os.path.getsize(file_path),
        }
    
    def normalize_reference_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Zotero item data to common format."""
        data = raw_data.get('data', {})
        meta = raw_data.get('meta', {})
        
        normalized = {
            'id': raw_data.get('key'),
            'title': data.get('title', ''),
            'type': self._map_zotero_type(data.get('itemType', 'journalArticle')),
            'abstract': data.get('abstractNote', ''),
            'year': self._extract_year_from_date(data.get('date', '')),
            'journal': data.get('publicationTitle', data.get('journalAbbreviation', '')),
            'volume': data.get('volume', ''),
            'issue': data.get('issue', ''),
            'pages': data.get('pages', ''),
            'doi': data.get('DOI', ''),
            'url': data.get('url', ''),
            'notes': data.get('extra', ''),
            'created_at': meta.get('createdDate'),
            'updated_at': meta.get('lastModified'),
            'version': meta.get('version'),
        }
        
        # Extract authors
        authors = []
        for creator in data.get('creators', []):
            if creator.get('creatorType') in ['author', 'editor']:
                if 'name' in creator:
                    authors.append(creator['name'])
                else:
                    first = creator.get('firstName', '')
                    last = creator.get('lastName', '')
                    if first or last:
                        authors.append(f"{first} {last}".strip())
        normalized['authors'] = authors
        
        # Extract tags as keywords
        tags = [tag['tag'] for tag in data.get('tags', [])]
        normalized['keywords'] = tags
        normalized['tags'] = tags
        
        return normalized
    
    def _convert_to_zotero_format(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert normalized reference data to Zotero format."""
        zotero_data = {
            'itemType': self._map_to_zotero_type(normalized_data.get('type', 'article')),
            'title': normalized_data.get('title', ''),
            'abstractNote': normalized_data.get('abstract', ''),
            'publicationTitle': normalized_data.get('journal', ''),
            'volume': normalized_data.get('volume', ''),
            'issue': normalized_data.get('issue', ''),
            'pages': normalized_data.get('pages', ''),
            'date': str(normalized_data.get('year', '')),
            'DOI': normalized_data.get('doi', ''),
            'url': normalized_data.get('url', ''),
            'extra': normalized_data.get('notes', ''),
        }
        
        # Convert authors
        creators = []
        for author_name in normalized_data.get('authors', []):
            if isinstance(author_name, str):
                parts = author_name.strip().split()
                if len(parts) >= 2:
                    creators.append({
                        'creatorType': 'author',
                        'firstName': ' '.join(parts[:-1]),
                        'lastName': parts[-1]
                    })
                elif len(parts) == 1:
                    creators.append({
                        'creatorType': 'author',
                        'name': parts[0]
                    })
        zotero_data['creators'] = creators
        
        # Convert tags
        tags = []
        for tag in normalized_data.get('keywords', []):
            tags.append({'tag': tag})
        for tag in normalized_data.get('tags', []):
            tags.append({'tag': tag})
        zotero_data['tags'] = tags
        
        # Remove empty fields
        return {k: v for k, v in zotero_data.items() if v}
    
    def _map_zotero_type(self, zotero_type: str) -> str:
        """Map Zotero item type to normalized type."""
        mapping = {
            'journalArticle': 'article',
            'book': 'book',
            'bookSection': 'chapter',
            'conferencePaper': 'conference',
            'thesis': 'thesis',
            'report': 'report',
            'preprint': 'preprint',
            'dataset': 'dataset',
        }
        return mapping.get(zotero_type, 'article')
    
    def _map_to_zotero_type(self, normalized_type: str) -> str:
        """Map normalized type to Zotero item type."""
        mapping = {
            'article': 'journalArticle',
            'book': 'book',
            'chapter': 'bookSection',
            'conference': 'conferencePaper',
            'thesis': 'thesis',
            'report': 'report',
            'preprint': 'preprint',
            'dataset': 'dataset',
        }
        return mapping.get(normalized_type, 'journalArticle')
    
    def _extract_year_from_date(self, date_str: str) -> Optional[int]:
        """Extract year from Zotero date string."""
        if not date_str:
            return None
        
        # Zotero dates can be in various formats
        import re
        year_match = re.search(r'\b(19|20)\d{2}\b', date_str)
        if year_match:
            return int(year_match.group())
        
        return None
    
    def search_catalog(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search Zotero's public catalog (not available in API)."""
        # Zotero doesn't have a public catalog search API like Mendeley
        # This would need to be implemented differently or use web scraping
        self.logger.warning("Zotero catalog search not available via API")
        return []