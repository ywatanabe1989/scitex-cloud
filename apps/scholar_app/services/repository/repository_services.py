"""
Repository services for managing connections to research data repositories.
This module provides APIs for interacting with various research data repositories
including Zenodo, Figshare, Dryad, and institutional repositories.
"""

import requests
import json
import logging
import hashlib
import mimetypes
from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from ..models import Repository, RepositoryConnection, Dataset, DatasetFile, RepositorySync

logger = logging.getLogger(__name__)


class RepositoryServiceError(Exception):
    """Base exception for repository service errors"""
    pass


class AuthenticationError(RepositoryServiceError):
    """Authentication-related errors"""
    pass


class APIError(RepositoryServiceError):
    """API-related errors"""
    pass


class ValidationError(RepositoryServiceError):
    """Data validation errors"""
    pass


class BaseRepositoryService(ABC):
    """Base class for repository service implementations"""
    
    def __init__(self, repository_connection: RepositoryConnection):
        self.connection = repository_connection
        self.repository = repository_connection.repository
        self.logger = logging.getLogger(f"{self.__class__.__name__}")
        
    @abstractmethod
    def authenticate(self) -> bool:
        """Authenticate with the repository"""
        pass
    
    @abstractmethod
    def create_dataset(self, metadata: Dict) -> Dict:
        """Create a new dataset in the repository"""
        pass
    
    @abstractmethod
    def update_dataset(self, dataset_id: str, metadata: Dict) -> Dict:
        """Update an existing dataset"""
        pass
    
    @abstractmethod
    def upload_file(self, dataset_id: str, file_path: str, file_data: bytes, metadata: Dict = None) -> Dict:
        """Upload a file to a dataset"""
        pass
    
    @abstractmethod
    def get_dataset(self, dataset_id: str) -> Dict:
        """Retrieve dataset metadata"""
        pass
    
    @abstractmethod
    def list_datasets(self, filters: Dict = None) -> List[Dict]:
        """List datasets for the authenticated user"""
        pass
    
    @abstractmethod
    def publish_dataset(self, dataset_id: str) -> Dict:
        """Publish a dataset (make it public)"""
        pass
    
    @abstractmethod
    def get_download_url(self, dataset_id: str, file_id: str) -> str:
        """Get download URL for a file"""
        pass
    
    def _make_request(self, method: str, url: str, headers: Dict = None, 
                     data: Any = None, files: Dict = None, timeout: int = 30) -> requests.Response:
        """Make an HTTP request with proper error handling"""
        try:
            response = requests.request(
                method=method,
                url=url,
                headers=headers,
                data=data,
                files=files,
                timeout=timeout
            )
            
            # Log request for debugging
            self.logger.debug(f"{method} {url} - Status: {response.status_code}")
            
            return response
            
        except requests.exceptions.RequestException as e:
            self.logger.error(f"Request failed: {e}")
            raise APIError(f"Request failed: {e}")
    
    def _handle_api_error(self, response: requests.Response) -> None:
        """Handle API error responses"""
        if response.status_code == 401:
            raise AuthenticationError("Authentication failed")
        elif response.status_code == 403:
            raise AuthenticationError("Access forbidden")
        elif response.status_code == 404:
            raise APIError("Resource not found")
        elif response.status_code >= 400:
            try:
                error_data = response.json()
                error_message = error_data.get('message', f"API error: {response.status_code}")
            except ValueError:
                error_message = f"API error: {response.status_code} - {response.text}"
            raise APIError(error_message)
    
    def sync_dataset_from_repository(self, repository_dataset_id: str) -> Dataset:
        """Sync a dataset from the repository to local database"""
        # Get dataset metadata from repository
        repo_data = self.get_dataset(repository_dataset_id)
        
        # Create or update local dataset
        dataset, created = Dataset.objects.get_or_create(
            repository_connection=self.connection,
            repository_id=repository_dataset_id,
            defaults={
                'title': repo_data.get('title', ''),
                'description': repo_data.get('description', ''),
                'owner': self.connection.user,
                'status': 'published' if repo_data.get('published') else 'draft',
                'repository_url': repo_data.get('url', ''),
                'repository_doi': repo_data.get('doi', ''),
                'version': repo_data.get('version', '1.0'),
                'last_synced': timezone.now()
            }
        )
        
        if not created:
            # Update existing dataset
            dataset.title = repo_data.get('title', dataset.title)
            dataset.description = repo_data.get('description', dataset.description)
            dataset.repository_url = repo_data.get('url', dataset.repository_url)
            dataset.repository_doi = repo_data.get('doi', dataset.repository_doi)
            dataset.version = repo_data.get('version', dataset.version)
            dataset.last_synced = timezone.now()
            dataset.save()
        
        # Sync files
        files_data = repo_data.get('files', [])
        for file_data in files_data:
            self._sync_dataset_file(dataset, file_data)
        
        return dataset
    
    def _sync_dataset_file(self, dataset: Dataset, file_data: Dict) -> DatasetFile:
        """Sync a single file from repository"""
        dataset_file, created = DatasetFile.objects.get_or_create(
            dataset=dataset,
            repository_file_id=file_data.get('id', ''),
            defaults={
                'filename': file_data.get('filename', ''),
                'file_path': file_data.get('path', ''),
                'file_type': self._determine_file_type(file_data.get('filename', '')),
                'file_format': self._get_file_extension(file_data.get('filename', '')),
                'size_bytes': file_data.get('size', 0),
                'checksum_md5': file_data.get('checksum', ''),
                'download_url': file_data.get('download_url', ''),
                'mime_type': mimetypes.guess_type(file_data.get('filename', ''))[0] or '',
            }
        )
        
        if not created:
            # Update existing file
            dataset_file.filename = file_data.get('filename', dataset_file.filename)
            dataset_file.size_bytes = file_data.get('size', dataset_file.size_bytes)
            dataset_file.download_url = file_data.get('download_url', dataset_file.download_url)
            dataset_file.save()
        
        return dataset_file
    
    def _determine_file_type(self, filename: str) -> str:
        """Determine file type based on filename"""
        filename_lower = filename.lower()
        
        if filename_lower in ['readme.md', 'readme.txt', 'readme']:
            return 'readme'
        elif filename_lower.endswith(('.py', '.r', '.m', '.ipynb', '.sh', '.bat')):
            return 'code'
        elif filename_lower.endswith(('.pdf', '.doc', '.docx', '.txt', '.md')):
            return 'documentation'
        elif filename_lower.endswith(('.png', '.jpg', '.jpeg', '.gif', '.svg', '.eps')):
            return 'figure'
        elif filename_lower.endswith(('.csv', '.xlsx', '.json', '.xml', '.h5', '.hdf5', '.nc')):
            return 'data'
        elif filename_lower.startswith('license'):
            return 'license'
        else:
            return 'data'  # Default to data
    
    def _get_file_extension(self, filename: str) -> str:
        """Get file extension"""
        parts = filename.split('.')
        return parts[-1] if len(parts) > 1 else ''


class ZenodoService(BaseRepositoryService):
    """Service for interacting with Zenodo repository"""
    
    def __init__(self, repository_connection: RepositoryConnection):
        super().__init__(repository_connection)
        self.base_url = self.repository.api_base_url.rstrip('/')
        self.sandbox_mode = getattr(settings, 'ZENODO_SANDBOX_MODE', True)
        
        if self.sandbox_mode:
            self.base_url = self.base_url.replace('zenodo.org', 'sandbox.zenodo.org')
    
    def authenticate(self) -> bool:
        """Test authentication with Zenodo"""
        try:
            headers = {'Authorization': f'Bearer {self.connection.api_token}'}
            response = self._make_request('GET', f"{self.base_url}/api/deposit/depositions", headers=headers)
            
            if response.status_code == 200:
                self.connection.status = 'active'
                self.connection.last_verified = timezone.now()
                self.connection.save()
                return True
            else:
                self._handle_api_error(response)
                
        except Exception as e:
            self.logger.error(f"Authentication failed: {e}")
            self.connection.status = 'invalid'
            self.connection.last_error = str(e)
            self.connection.save()
            return False
    
    def create_dataset(self, metadata: Dict) -> Dict:
        """Create a new deposition in Zenodo"""
        headers = {
            'Authorization': f'Bearer {self.connection.api_token}',
            'Content-Type': 'application/json'
        }
        
        # Prepare Zenodo metadata format
        zenodo_metadata = self._format_zenodo_metadata(metadata)
        
        data = json.dumps({'metadata': zenodo_metadata})
        
        response = self._make_request(
            'POST',
            f"{self.base_url}/api/deposit/depositions",
            headers=headers,
            data=data
        )
        
        if response.status_code == 201:
            result = response.json()
            self.logger.info(f"Created Zenodo deposition: {result['id']}")
            return {
                'id': str(result['id']),
                'url': result.get('links', {}).get('html', ''),
                'bucket_url': result.get('links', {}).get('bucket', ''),
                'status': result.get('state', 'draft'),
                'doi': result.get('doi', ''),
                'conceptdoi': result.get('conceptdoi', ''),
                'metadata': result.get('metadata', {})
            }
        else:
            self._handle_api_error(response)
    
    def update_dataset(self, dataset_id: str, metadata: Dict) -> Dict:
        """Update a Zenodo deposition"""
        headers = {
            'Authorization': f'Bearer {self.connection.api_token}',
            'Content-Type': 'application/json'
        }
        
        zenodo_metadata = self._format_zenodo_metadata(metadata)
        data = json.dumps({'metadata': zenodo_metadata})
        
        response = self._make_request(
            'PUT',
            f"{self.base_url}/api/deposit/depositions/{dataset_id}",
            headers=headers,
            data=data
        )
        
        if response.status_code == 200:
            result = response.json()
            self.logger.info(f"Updated Zenodo deposition: {dataset_id}")
            return {
                'id': str(result['id']),
                'url': result.get('links', {}).get('html', ''),
                'status': result.get('state', 'draft'),
                'doi': result.get('doi', ''),
                'metadata': result.get('metadata', {})
            }
        else:
            self._handle_api_error(response)
    
    def upload_file(self, dataset_id: str, file_path: str, file_data: bytes, metadata: Dict = None) -> Dict:
        """Upload a file to a Zenodo deposition"""
        # First, get the bucket URL
        dataset_info = self.get_dataset(dataset_id)
        bucket_url = dataset_info.get('bucket_url')
        
        if not bucket_url:
            raise APIError("No bucket URL found for dataset")
        
        headers = {'Authorization': f'Bearer {self.connection.api_token}'}
        
        # Upload file to bucket
        filename = file_path.split('/')[-1]
        files = {'file': (filename, file_data)}
        
        response = self._make_request(
            'PUT',
            f"{bucket_url}/{filename}",
            headers=headers,
            data=file_data
        )
        
        if response.status_code in [200, 201]:
            result = response.json()
            self.logger.info(f"Uploaded file {filename} to Zenodo deposition {dataset_id}")
            return {
                'file_id': result.get('id'),
                'filename': result.get('filename'),
                'size': result.get('size'),
                'checksum': result.get('checksum'),
                'download_url': result.get('links', {}).get('download', '')
            }
        else:
            self._handle_api_error(response)
    
    def get_dataset(self, dataset_id: str) -> Dict:
        """Get Zenodo deposition information"""
        headers = {'Authorization': f'Bearer {self.connection.api_token}'}
        
        response = self._make_request(
            'GET',
            f"{self.base_url}/api/deposit/depositions/{dataset_id}",
            headers=headers
        )
        
        if response.status_code == 200:
            result = response.json()
            return {
                'id': str(result['id']),
                'title': result.get('metadata', {}).get('title', ''),
                'description': result.get('metadata', {}).get('description', ''),
                'url': result.get('links', {}).get('html', ''),
                'bucket_url': result.get('links', {}).get('bucket', ''),
                'doi': result.get('doi', ''),
                'conceptdoi': result.get('conceptdoi', ''),
                'status': result.get('state', 'draft'),
                'published': result.get('submitted', False),
                'version': result.get('metadata', {}).get('version', '1.0'),
                'files': [
                    {
                        'id': f.get('id'),
                        'filename': f.get('filename'),
                        'size': f.get('size'),
                        'checksum': f.get('checksum'),
                        'download_url': f.get('links', {}).get('download', '')
                    }
                    for f in result.get('files', [])
                ],
                'metadata': result.get('metadata', {})
            }
        else:
            self._handle_api_error(response)
    
    def list_datasets(self, filters: Dict = None) -> List[Dict]:
        """List Zenodo depositions for the authenticated user"""
        headers = {'Authorization': f'Bearer {self.connection.api_token}'}
        
        params = {}
        if filters:
            if 'status' in filters:
                params['status'] = filters['status']
            if 'sort' in filters:
                params['sort'] = filters['sort']
            if 'page' in filters:
                params['page'] = filters['page']
            if 'size' in filters:
                params['size'] = filters['size']
        
        response = self._make_request(
            'GET',
            f"{self.base_url}/api/deposit/depositions",
            headers=headers
        )
        
        if response.status_code == 200:
            results = response.json()
            return [
                {
                    'id': str(result['id']),
                    'title': result.get('metadata', {}).get('title', ''),
                    'description': result.get('metadata', {}).get('description', ''),
                    'url': result.get('links', {}).get('html', ''),
                    'doi': result.get('doi', ''),
                    'status': result.get('state', 'draft'),
                    'published': result.get('submitted', False),
                    'created_at': result.get('created'),
                    'updated_at': result.get('modified'),
                }
                for result in results
            ]
        else:
            self._handle_api_error(response)
    
    def publish_dataset(self, dataset_id: str) -> Dict:
        """Publish a Zenodo deposition"""
        headers = {'Authorization': f'Bearer {self.connection.api_token}'}
        
        response = self._make_request(
            'POST',
            f"{self.base_url}/api/deposit/depositions/{dataset_id}/actions/publish",
            headers=headers
        )
        
        if response.status_code == 202:
            result = response.json()
            self.logger.info(f"Published Zenodo deposition: {dataset_id}")
            return {
                'id': str(result['id']),
                'doi': result.get('doi'),
                'url': result.get('links', {}).get('html', ''),
                'status': result.get('state', 'published')
            }
        else:
            self._handle_api_error(response)
    
    def get_download_url(self, dataset_id: str, file_id: str) -> str:
        """Get download URL for a file in Zenodo"""
        dataset_info = self.get_dataset(dataset_id)
        for file_info in dataset_info.get('files', []):
            if file_info['id'] == file_id:
                return file_info['download_url']
        
        raise APIError(f"File {file_id} not found in dataset {dataset_id}")
    
    def _format_zenodo_metadata(self, metadata: Dict) -> Dict:
        """Format metadata for Zenodo API"""
        zenodo_metadata = {
            'title': metadata.get('title', ''),
            'description': metadata.get('description', ''),
            'upload_type': 'dataset',
            'creators': metadata.get('creators', []),
        }
        
        # Add optional fields
        if 'keywords' in metadata:
            zenodo_metadata['keywords'] = metadata['keywords'].split(',') if isinstance(metadata['keywords'], str) else metadata['keywords']
        
        if 'license' in metadata:
            zenodo_metadata['license'] = metadata['license']
        
        if 'access_right' in metadata:
            zenodo_metadata['access_right'] = metadata['access_right']
        else:
            zenodo_metadata['access_right'] = 'open'  # Default to open access
        
        if 'publication_date' in metadata:
            zenodo_metadata['publication_date'] = metadata['publication_date']
        
        if 'version' in metadata:
            zenodo_metadata['version'] = metadata['version']
        
        if 'related_identifiers' in metadata:
            zenodo_metadata['related_identifiers'] = metadata['related_identifiers']
        
        if 'grants' in metadata:
            zenodo_metadata['grants'] = metadata['grants']
        
        return zenodo_metadata


class RepositoryServiceFactory:
    """Factory for creating repository service instances"""
    
    _services = {
        'zenodo': ZenodoService,
    }
    
    @classmethod
    def create_service(cls, repository_connection: RepositoryConnection) -> BaseRepositoryService:
        """Create a repository service instance"""
        repository_type = repository_connection.repository.repository_type
        
        if repository_type not in cls._services:
            raise RepositoryServiceError(f"Unsupported repository type: {repository_type}")
        
        service_class = cls._services[repository_type]
        return service_class(repository_connection)
    
    @classmethod
    def register_service(cls, repository_type: str, service_class: type):
        """Register a new repository service"""
        cls._services[repository_type] = service_class


def sync_dataset_with_repository(dataset: Dataset) -> RepositorySync:
    """Sync a dataset with its repository"""
    sync_record = RepositorySync.objects.create(
        user=dataset.owner,
        repository_connection=dataset.repository_connection,
        dataset=dataset,
        sync_type='full_sync',
        status='pending'
    )
    
    try:
        sync_record.status = 'running'
        sync_record.started_at = timezone.now()
        sync_record.save()
        
        # Create service instance
        service = RepositoryServiceFactory.create_service(dataset.repository_connection)
        
        # Sync dataset metadata
        repo_data = service.get_dataset(dataset.repository_id)
        
        # Update local dataset
        dataset.title = repo_data.get('title', dataset.title)
        dataset.description = repo_data.get('description', dataset.description)
        dataset.repository_url = repo_data.get('url', dataset.repository_url)
        dataset.repository_doi = repo_data.get('doi', dataset.repository_doi)
        dataset.version = repo_data.get('version', dataset.version)
        dataset.status = 'published' if repo_data.get('published') else 'draft'
        dataset.last_synced = timezone.now()
        dataset.save()
        
        # Sync files
        files_data = repo_data.get('files', [])
        sync_record.total_items = len(files_data)
        
        for i, file_data in enumerate(files_data):
            service._sync_dataset_file(dataset, file_data)
            sync_record.completed_items = i + 1
            sync_record.save()
        
        sync_record.status = 'completed'
        sync_record.completed_at = timezone.now()
        sync_record.result_data = {'synced_files': len(files_data)}
        
    except Exception as e:
        sync_record.status = 'failed'
        sync_record.error_message = str(e)
        sync_record.completed_at = timezone.now()
        logger.error(f"Dataset sync failed: {e}")
    
    sync_record.save()
    return sync_record


def upload_dataset_to_repository(dataset: Dataset, file_paths: List[str] = None) -> RepositorySync:
    """Upload a dataset to its repository"""
    sync_record = RepositorySync.objects.create(
        user=dataset.owner,
        repository_connection=dataset.repository_connection,
        dataset=dataset,
        sync_type='upload',
        status='pending'
    )
    
    try:
        sync_record.status = 'running'
        sync_record.started_at = timezone.now()
        sync_record.save()
        
        # Create service instance
        service = RepositoryServiceFactory.create_service(dataset.repository_connection)
        
        # Prepare metadata
        metadata = {
            'title': dataset.title,
            'description': dataset.description,
            'keywords': dataset.keywords,
            'creators': [{
                'name': dataset.owner.get_full_name() or dataset.owner.username,
                'affiliation': getattr(dataset.owner, 'affiliation', '')
            }],
            'license': dataset.license or 'CC-BY-4.0',
            'version': dataset.version,
        }
        
        # Add collaborators as creators
        for collaborator in dataset.collaborators.all():
            metadata['creators'].append({
                'name': collaborator.get_full_name() or collaborator.username,
                'affiliation': getattr(collaborator, 'affiliation', '')
            })
        
        # Create or update dataset in repository
        if dataset.repository_id:
            repo_data = service.update_dataset(dataset.repository_id, metadata)
        else:
            repo_data = service.create_dataset(metadata)
            dataset.repository_id = repo_data['id']
            dataset.repository_url = repo_data['url']
            dataset.save()
        
        # Upload files
        files_to_upload = dataset.files.all()
        if file_paths:
            files_to_upload = files_to_upload.filter(file_path__in=file_paths)
        
        sync_record.total_items = files_to_upload.count()
        
        for i, dataset_file in enumerate(files_to_upload):
            if dataset_file.local_file:
                with dataset_file.local_file.open('rb') as f:
                    file_data = f.read()
                
                file_result = service.upload_file(
                    dataset.repository_id,
                    dataset_file.file_path or dataset_file.filename,
                    file_data
                )
                
                # Update file information
                dataset_file.repository_file_id = file_result.get('file_id', '')
                dataset_file.download_url = file_result.get('download_url', '')
                dataset_file.save()
            
            sync_record.completed_items = i + 1
            sync_record.save()
        
        sync_record.status = 'completed'
        sync_record.completed_at = timezone.now()
        sync_record.result_data = {
            'repository_id': dataset.repository_id,
            'repository_url': dataset.repository_url,
            'uploaded_files': sync_record.completed_items
        }
        
    except Exception as e:
        sync_record.status = 'failed'
        sync_record.error_message = str(e)
        sync_record.completed_at = timezone.now()
        logger.error(f"Dataset upload failed: {e}")
    
    sync_record.save()
    return sync_record