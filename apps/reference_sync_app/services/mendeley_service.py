"""
Mendeley API service implementation.
Handles authentication and data access for Mendeley reference manager.
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


class MendeleyService(BaseReferenceService):
    """Mendeley API service implementation."""
    
    @property
    def service_name(self) -> str:
        return 'mendeley'
    
    @property
    def base_url(self) -> str:
        return 'https://api.mendeley.com'
    
    @property
    def oauth_config(self) -> Dict[str, str]:
        return {
            'client_id': getattr(settings, 'MENDELEY_CLIENT_ID', ''),
            'client_secret': getattr(settings, 'MENDELEY_CLIENT_SECRET', ''),
            'auth_url': 'https://api.mendeley.com/oauth/authorize',
            'token_url': 'https://api.mendeley.com/oauth/token',
            'scope': 'all',
        }
    
    def get_oauth_url(self, redirect_uri: str, state: str = None) -> str:
        """Generate Mendeley OAuth authorization URL."""
        config = self.oauth_config
        params = {
            'client_id': config['client_id'],
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': config['scope'],
        }
        
        if state:
            params['state'] = state
        
        return f"{config['auth_url']}?{urlencode(params)}"
    
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """Exchange authorization code for access token."""
        config = self.oauth_config
        data = {
            'grant_type': 'authorization_code',
            'code': code,
            'redirect_uri': redirect_uri,
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
        }
        
        try:
            response = requests.post(config['token_url'], data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Update account with token info
            self.account.access_token = token_data['access_token']
            self.account.refresh_token = token_data.get('refresh_token', '')
            
            # Mendeley tokens typically expire in 1 hour
            expires_in = token_data.get('expires_in', 3600)
            self.account.token_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
            self.account.status = 'active'
            self.account.save()
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token exchange failed: {e}")
            raise AuthenticationError(f"Failed to exchange code for token: {e}")
    
    def refresh_access_token(self) -> Dict[str, Any]:
        """Refresh the access token using refresh token."""
        if not self.account.refresh_token:
            raise AuthenticationError("No refresh token available")
        
        config = self.oauth_config
        data = {
            'grant_type': 'refresh_token',
            'refresh_token': self.account.refresh_token,
            'client_id': config['client_id'],
            'client_secret': config['client_secret'],
        }
        
        try:
            response = requests.post(config['token_url'], data=data)
            response.raise_for_status()
            token_data = response.json()
            
            # Update account with new token info
            self.account.access_token = token_data['access_token']
            if 'refresh_token' in token_data:
                self.account.refresh_token = token_data['refresh_token']
            
            expires_in = token_data.get('expires_in', 3600)
            self.account.token_expires_at = timezone.now() + timezone.timedelta(seconds=expires_in)
            self.account.status = 'active'
            self.account.save()
            
            return token_data
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Token refresh failed: {e}")
            self.account.status = 'expired'
            self.account.save()
            raise AuthenticationError(f"Failed to refresh token: {e}")
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get Mendeley user profile information."""
        response = self.make_request('GET', '/profiles/me')
        user_data = response.json()
        
        # Update account metadata
        self.account.external_user_id = user_data.get('id', '')
        self.account.account_email = user_data.get('email', '')
        self.account.account_name = f"{user_data.get('first_name', '')} {user_data.get('last_name', '')}".strip()
        self.account.account_metadata = user_data
        self.account.save()
        
        return user_data
    
    def get_collections(self) -> List[Dict[str, Any]]:
        """Get list of user's Mendeley groups."""
        response = self.make_request('GET', '/groups')
        groups = response.json()
        
        # Add personal library as a collection
        collections = [{
            'id': 'library',
            'name': 'Personal Library',
            'description': 'Your personal Mendeley library',
            'type': 'personal',
            'document_count': 0,  # Will be filled by separate call if needed
            'created': None,
            'modified': None,
        }]
        
        # Add groups as collections
        for group in groups:
            collections.append({
                'id': group['id'],
                'name': group['name'],
                'description': group.get('description', ''),
                'type': 'group',
                'document_count': 0,  # Mendeley doesn't provide this in group list
                'created': group.get('created'),
                'modified': group.get('last_modified'),
            })
        
        return collections
    
    def get_references(self, collection_id: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get list of documents from Mendeley."""
        params = {
            'limit': min(limit, 500),  # Mendeley max is 500
            'offset': offset,
        }
        
        if collection_id and collection_id != 'library':
            # Get documents from a specific group
            endpoint = f'/groups/{collection_id}/documents'
        else:
            # Get documents from personal library
            endpoint = '/documents'
        
        response = self.make_request('GET', endpoint, params=params)
        documents = response.json()
        
        # Normalize document data
        normalized_docs = []
        for doc in documents:
            normalized_docs.append(self.normalize_reference_data(doc))
        
        return normalized_docs
    
    def get_reference(self, reference_id: str) -> Dict[str, Any]:
        """Get detailed information about a specific document."""
        response = self.make_request('GET', f'/documents/{reference_id}')
        document = response.json()
        return self.normalize_reference_data(document)
    
    def create_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new document in Mendeley."""
        # Convert normalized data to Mendeley format
        mendeley_data = self._convert_to_mendeley_format(reference_data)
        
        response = self.make_request('POST', '/documents', json=mendeley_data)
        created_doc = response.json()
        return self.normalize_reference_data(created_doc)
    
    def update_reference(self, reference_id: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing document in Mendeley."""
        # Convert normalized data to Mendeley format
        mendeley_data = self._convert_to_mendeley_format(reference_data)
        
        response = self.make_request('PATCH', f'/documents/{reference_id}', json=mendeley_data)
        updated_doc = response.json()
        return self.normalize_reference_data(updated_doc)
    
    def delete_reference(self, reference_id: str) -> bool:
        """Delete a document from Mendeley."""
        try:
            response = self.make_request('DELETE', f'/documents/{reference_id}')
            return response.status_code == 204
        except Exception as e:
            self.logger.error(f"Failed to delete document {reference_id}: {e}")
            return False
    
    def get_reference_files(self, reference_id: str) -> List[Dict[str, Any]]:
        """Get files attached to a Mendeley document."""
        response = self.make_request('GET', f'/documents/{reference_id}/files')
        files = response.json()
        
        normalized_files = []
        for file_data in files:
            normalized_files.append({
                'id': file_data['id'],
                'filename': file_data['file_name'],
                'mime_type': file_data['mime_type'],
                'size': file_data['size'],
                'download_url': f"{self.base_url}/files/{file_data['id']}",
                'created': file_data.get('created'),
            })
        
        return normalized_files
    
    def upload_file(self, reference_id: str, file_path: str, file_type: str = 'pdf') -> Dict[str, Any]:
        """Upload a file to a Mendeley document."""
        import os
        from mimetypes import guess_type
        
        if not os.path.exists(file_path):
            raise ReferenceServiceException(f"File not found: {file_path}")
        
        filename = os.path.basename(file_path)
        mime_type, _ = guess_type(file_path)
        
        # First, get upload URL
        response = self.make_request('POST', f'/documents/{reference_id}/files', json={
            'file_name': filename,
            'mime_type': mime_type or 'application/pdf',
        })
        
        upload_info = response.json()
        upload_url = upload_info['upload_url']
        
        # Upload the file
        with open(file_path, 'rb') as f:
            files = {'file': (filename, f, mime_type)}
            upload_response = requests.post(upload_url, files=files)
            upload_response.raise_for_status()
        
        return {
            'id': upload_info['id'],
            'filename': filename,
            'mime_type': mime_type,
            'size': os.path.getsize(file_path),
        }
    
    def normalize_reference_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize Mendeley document data to common format."""
        # Extract basic information
        normalized = {
            'id': raw_data.get('id'),
            'title': raw_data.get('title', ''),
            'type': raw_data.get('type', 'journal'),
            'year': raw_data.get('year'),
            'abstract': raw_data.get('abstract', ''),
            'source': raw_data.get('source', ''),  # journal name
            'volume': raw_data.get('volume', ''),
            'issue': raw_data.get('issue', ''),
            'pages': raw_data.get('pages', ''),
            'doi': raw_data.get('doi', ''),
            'pmid': raw_data.get('pmid', ''),
            'url': raw_data.get('link', ''),
            'notes': raw_data.get('notes', ''),
            'created_at': raw_data.get('created'),
            'updated_at': raw_data.get('last_modified'),
        }
        
        # Extract authors
        authors = []
        for author in raw_data.get('authors', []):
            author_name = f"{author.get('first_name', '')} {author.get('last_name', '')}".strip()
            if author_name:
                authors.append(author_name)
        normalized['authors'] = authors
        
        # Extract keywords
        keywords = raw_data.get('keywords', [])
        if isinstance(keywords, list):
            normalized['keywords'] = keywords
        else:
            normalized['keywords'] = []
        
        # Extract tags
        tags = raw_data.get('tags', [])
        if isinstance(tags, list):
            normalized['tags'] = tags
        else:
            normalized['tags'] = []
        
        # Extract identifiers
        identifiers = raw_data.get('identifiers', {})
        if isinstance(identifiers, dict):
            normalized['doi'] = identifiers.get('doi', normalized['doi'])
            normalized['pmid'] = identifiers.get('pmid', normalized['pmid'])
            normalized['isbn'] = identifiers.get('isbn', '')
            normalized['issn'] = identifiers.get('issn', '')
        
        return normalized
    
    def _convert_to_mendeley_format(self, normalized_data: Dict[str, Any]) -> Dict[str, Any]:
        """Convert normalized reference data to Mendeley format."""
        mendeley_data = {
            'title': normalized_data.get('title', ''),
            'type': normalized_data.get('type', 'journal'),
            'year': normalized_data.get('year'),
            'abstract': normalized_data.get('abstract', ''),
            'source': normalized_data.get('journal', normalized_data.get('source', '')),
            'volume': normalized_data.get('volume', ''),
            'issue': normalized_data.get('issue', ''),
            'pages': normalized_data.get('pages', ''),
            'link': normalized_data.get('url', ''),
            'notes': normalized_data.get('notes', ''),
        }
        
        # Convert authors
        authors = []
        for author_name in normalized_data.get('authors', []):
            if isinstance(author_name, str):
                # Simple name splitting - could be improved
                parts = author_name.strip().split()
                if len(parts) >= 2:
                    authors.append({
                        'first_name': ' '.join(parts[:-1]),
                        'last_name': parts[-1]
                    })
                elif len(parts) == 1:
                    authors.append({
                        'first_name': '',
                        'last_name': parts[0]
                    })
        mendeley_data['authors'] = authors
        
        # Add keywords and tags
        if normalized_data.get('keywords'):
            mendeley_data['keywords'] = normalized_data['keywords']
        
        if normalized_data.get('tags'):
            mendeley_data['tags'] = normalized_data['tags']
        
        # Add identifiers
        identifiers = {}
        if normalized_data.get('doi'):
            identifiers['doi'] = normalized_data['doi']
        if normalized_data.get('pmid'):
            identifiers['pmid'] = normalized_data['pmid']
        if normalized_data.get('isbn'):
            identifiers['isbn'] = normalized_data['isbn']
        if normalized_data.get('issn'):
            identifiers['issn'] = normalized_data['issn']
        
        if identifiers:
            mendeley_data['identifiers'] = identifiers
        
        # Remove empty fields
        return {k: v for k, v in mendeley_data.items() if v}
    
    def search_references(self, query: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Search for references in Mendeley catalog."""
        params = {
            'query': query,
            'limit': min(limit, 100),
        }
        
        try:
            response = self.make_request('GET', '/search/catalog', params=params)
            results = response.json()
            
            normalized_results = []
            for result in results:
                normalized_results.append(self.normalize_reference_data(result))
            
            return normalized_results
            
        except Exception as e:
            self.logger.error(f"Search failed: {e}")
            return []
    
    def get_document_details(self, document_id: str) -> Dict[str, Any]:
        """Get detailed document information including files and annotations."""
        # Get basic document info
        doc_response = self.make_request('GET', f'/documents/{document_id}')
        document = doc_response.json()
        
        # Get files
        try:
            files_response = self.make_request('GET', f'/documents/{document_id}/files')
            files = files_response.json()
            document['files'] = files
        except Exception as e:
            self.logger.warning(f"Could not fetch files for document {document_id}: {e}")
            document['files'] = []
        
        # Get annotations (if available)
        try:
            annotations_response = self.make_request('GET', f'/annotations', params={'document_id': document_id})
            annotations = annotations_response.json()
            document['annotations'] = annotations
        except Exception as e:
            self.logger.warning(f"Could not fetch annotations for document {document_id}: {e}")
            document['annotations'] = []
        
        return self.normalize_reference_data(document)