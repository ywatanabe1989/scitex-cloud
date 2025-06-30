"""
Base service class for reference manager integrations.
Defines the common interface that all reference manager services must implement.
"""

import logging
import hashlib
import json
import requests
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from django.utils import timezone
from django.conf import settings


logger = logging.getLogger(__name__)


class ReferenceServiceException(Exception):
    """Base exception for reference service errors."""
    pass


class AuthenticationError(ReferenceServiceException):
    """Raised when authentication fails."""
    pass


class RateLimitError(ReferenceServiceException):
    """Raised when API rate limit is exceeded."""
    pass


class ServiceUnavailableError(ReferenceServiceException):
    """Raised when the service is temporarily unavailable."""
    pass


class BaseReferenceService(ABC):
    """
    Abstract base class for reference manager services.
    All specific service implementations should inherit from this class.
    """
    
    def __init__(self, account):
        """
        Initialize the service with an account.
        
        Args:
            account: ReferenceManagerAccount instance
        """
        self.account = account
        self.session = requests.Session()
        self.logger = logging.getLogger(f"{self.__class__.__module__}.{self.__class__.__name__}")
        
        # Set up session headers
        self.session.headers.update({
            'User-Agent': 'SciTeX-Cloud/1.0',
            'Accept': 'application/json',
            'Content-Type': 'application/json'
        })
    
    @property
    @abstractmethod
    def service_name(self) -> str:
        """Return the name of the service (e.g., 'mendeley', 'zotero')."""
        pass
    
    @property
    @abstractmethod
    def base_url(self) -> str:
        """Return the base URL for the service API."""
        pass
    
    @property
    @abstractmethod
    def oauth_config(self) -> Dict[str, str]:
        """Return OAuth configuration for the service."""
        pass
    
    # Authentication methods
    
    @abstractmethod
    def get_oauth_url(self, redirect_uri: str, state: str = None) -> str:
        """
        Generate OAuth authorization URL.
        
        Args:
            redirect_uri: URI to redirect to after authorization
            state: Optional state parameter for security
            
        Returns:
            Authorization URL string
        """
        pass
    
    @abstractmethod
    def exchange_code_for_token(self, code: str, redirect_uri: str) -> Dict[str, Any]:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Same redirect URI used in authorization
            
        Returns:
            Token information dictionary
            
        Raises:
            AuthenticationError: If token exchange fails
        """
        pass
    
    @abstractmethod
    def refresh_access_token(self) -> Dict[str, Any]:
        """
        Refresh the access token using refresh token.
        
        Returns:
            New token information dictionary
            
        Raises:
            AuthenticationError: If token refresh fails
        """
        pass
    
    def is_authenticated(self) -> bool:
        """
        Check if the service is properly authenticated.
        
        Returns:
            True if authenticated and token is valid
        """
        if not self.account.access_token:
            return False
        
        if not self.account.is_token_valid():
            try:
                self.refresh_access_token()
                return True
            except AuthenticationError:
                return False
        
        return True
    
    # API methods
    
    def make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an authenticated API request.
        
        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (relative to base_url)
            **kwargs: Additional arguments passed to requests
            
        Returns:
            Response object
            
        Raises:
            AuthenticationError: If authentication fails
            RateLimitError: If rate limit is exceeded
            ServiceUnavailableError: If service is unavailable
        """
        if not self.is_authenticated():
            raise AuthenticationError(f"Not authenticated with {self.service_name}")
        
        if not self.account.can_make_api_call():
            raise RateLimitError(f"API rate limit exceeded for {self.service_name}")
        
        # Prepare URL
        url = f"{self.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        
        # Add authorization header
        headers = kwargs.pop('headers', {})
        headers['Authorization'] = f"Bearer {self.account.access_token}"
        
        try:
            response = self.session.request(method, url, headers=headers, **kwargs)
            
            # Update API call count
            self.account.api_calls_today += 1
            self.account.save()
            
            # Handle common HTTP errors
            if response.status_code == 401:
                # Try to refresh token and retry once
                try:
                    self.refresh_access_token()
                    headers['Authorization'] = f"Bearer {self.account.access_token}"
                    response = self.session.request(method, url, headers=headers, **kwargs)
                except AuthenticationError:
                    raise AuthenticationError(f"Authentication failed with {self.service_name}")
            
            elif response.status_code == 429:
                raise RateLimitError(f"Rate limit exceeded for {self.service_name}")
            
            elif response.status_code >= 500:
                raise ServiceUnavailableError(f"{self.service_name} service unavailable")
            
            response.raise_for_status()
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise ReferenceServiceException(f"Request failed: {e}")
    
    # Data access methods - to be implemented by subclasses
    
    @abstractmethod
    def get_user_info(self) -> Dict[str, Any]:
        """
        Get user profile information.
        
        Returns:
            User information dictionary
        """
        pass
    
    @abstractmethod
    def get_collections(self) -> List[Dict[str, Any]]:
        """
        Get list of user's collections/groups.
        
        Returns:
            List of collection dictionaries
        """
        pass
    
    @abstractmethod
    def get_references(self, collection_id: str = None, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """
        Get list of references from a collection or library.
        
        Args:
            collection_id: Optional collection ID to filter by
            limit: Maximum number of references to return
            offset: Number of references to skip
            
        Returns:
            List of reference dictionaries
        """
        pass
    
    @abstractmethod
    def get_reference(self, reference_id: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific reference.
        
        Args:
            reference_id: ID of the reference
            
        Returns:
            Reference dictionary
        """
        pass
    
    @abstractmethod
    def create_reference(self, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new reference.
        
        Args:
            reference_data: Reference data dictionary
            
        Returns:
            Created reference dictionary
        """
        pass
    
    @abstractmethod
    def update_reference(self, reference_id: str, reference_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing reference.
        
        Args:
            reference_id: ID of the reference to update
            reference_data: Updated reference data
            
        Returns:
            Updated reference dictionary
        """
        pass
    
    @abstractmethod
    def delete_reference(self, reference_id: str) -> bool:
        """
        Delete a reference.
        
        Args:
            reference_id: ID of the reference to delete
            
        Returns:
            True if successfully deleted
        """
        pass
    
    @abstractmethod
    def get_reference_files(self, reference_id: str) -> List[Dict[str, Any]]:
        """
        Get files attached to a reference.
        
        Args:
            reference_id: ID of the reference
            
        Returns:
            List of file dictionaries
        """
        pass
    
    @abstractmethod
    def upload_file(self, reference_id: str, file_path: str, file_type: str = 'pdf') -> Dict[str, Any]:
        """
        Upload a file to a reference.
        
        Args:
            reference_id: ID of the reference
            file_path: Path to the file to upload
            file_type: Type of file (pdf, doc, etc.)
            
        Returns:
            File information dictionary
        """
        pass
    
    # Utility methods
    
    def normalize_reference_data(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Normalize reference data to a common format.
        
        This method should be overridden by subclasses to handle
        service-specific data formats.
        
        Args:
            raw_data: Raw reference data from the service
            
        Returns:
            Normalized reference data dictionary
        """
        return {
            'id': raw_data.get('id'),
            'title': raw_data.get('title', ''),
            'authors': self._extract_authors(raw_data),
            'year': self._extract_year(raw_data),
            'journal': raw_data.get('journal', ''),
            'volume': raw_data.get('volume', ''),
            'issue': raw_data.get('issue', ''),
            'pages': raw_data.get('pages', ''),
            'doi': raw_data.get('doi', ''),
            'url': raw_data.get('url', ''),
            'abstract': raw_data.get('abstract', ''),
            'keywords': self._extract_keywords(raw_data),
            'notes': raw_data.get('notes', ''),
            'tags': self._extract_tags(raw_data),
            'created_at': raw_data.get('created', ''),
            'updated_at': raw_data.get('last_modified', ''),
            'type': raw_data.get('type', 'article'),
        }
    
    def _extract_authors(self, data: Dict[str, Any]) -> List[str]:
        """Extract authors from reference data."""
        authors = data.get('authors', [])
        if isinstance(authors, list):
            return [self._format_author_name(author) for author in authors]
        return []
    
    def _format_author_name(self, author: Any) -> str:
        """Format author name consistently."""
        if isinstance(author, dict):
            first = author.get('first_name', author.get('given', ''))
            last = author.get('last_name', author.get('family', ''))
            return f"{first} {last}".strip()
        return str(author)
    
    def _extract_year(self, data: Dict[str, Any]) -> Optional[int]:
        """Extract publication year from reference data."""
        year = data.get('year')
        if year:
            try:
                return int(year)
            except (ValueError, TypeError):
                pass
        
        # Try to extract from date fields
        for field in ['published', 'created', 'date']:
            date_str = data.get(field, '')
            if date_str:
                try:
                    # Try various date formats
                    import dateutil.parser
                    date_obj = dateutil.parser.parse(date_str)
                    return date_obj.year
                except (ValueError, TypeError):
                    continue
        
        return None
    
    def _extract_keywords(self, data: Dict[str, Any]) -> List[str]:
        """Extract keywords from reference data."""
        keywords = data.get('keywords', [])
        if isinstance(keywords, str):
            return [k.strip() for k in keywords.split(',') if k.strip()]
        elif isinstance(keywords, list):
            return [str(k).strip() for k in keywords if str(k).strip()]
        return []
    
    def _extract_tags(self, data: Dict[str, Any]) -> List[str]:
        """Extract tags from reference data."""
        tags = data.get('tags', [])
        if isinstance(tags, str):
            return [t.strip() for t in tags.split(',') if t.strip()]
        elif isinstance(tags, list):
            return [str(t).strip() for t in tags if str(t).strip()]
        return []
    
    def calculate_data_hash(self, data: Dict[str, Any]) -> str:
        """
        Calculate a hash of the reference data for change detection.
        
        Args:
            data: Reference data dictionary
            
        Returns:
            SHA-256 hash string
        """
        # Normalize and sort data for consistent hashing
        normalized = self.normalize_reference_data(data)
        
        # Remove fields that don't affect content hash
        for field in ['id', 'created_at', 'updated_at']:
            normalized.pop(field, None)
        
        # Create deterministic JSON string
        json_str = json.dumps(normalized, sort_keys=True, separators=(',', ':'))
        
        # Calculate hash
        return hashlib.sha256(json_str.encode('utf-8')).hexdigest()
    
    def validate_reference_data(self, data: Dict[str, Any]) -> Tuple[bool, List[str]]:
        """
        Validate reference data.
        
        Args:
            data: Reference data to validate
            
        Returns:
            Tuple of (is_valid, list_of_errors)
        """
        errors = []
        
        # Check required fields
        if not data.get('title'):
            errors.append("Title is required")
        
        # Check authors format
        authors = data.get('authors', [])
        if not isinstance(authors, list):
            errors.append("Authors must be a list")
        
        # Check year format
        year = data.get('year')
        if year is not None:
            try:
                year_int = int(year)
                if year_int < 1000 or year_int > 3000:
                    errors.append("Year must be between 1000 and 3000")
            except (ValueError, TypeError):
                errors.append("Year must be a valid integer")
        
        # Check DOI format (basic validation)
        doi = data.get('doi', '')
        if doi and not doi.startswith('10.'):
            errors.append("DOI must start with '10.'")
        
        return len(errors) == 0, errors
    
    def __str__(self):
        return f"{self.service_name.title()} Service ({self.account.account_name})"