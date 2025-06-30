#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
GitHub API Integration Services

This module provides services for interacting with the GitHub API,
including OAuth2 authentication, repository management, and code synchronization.
"""

import requests
import json
import base64
from datetime import datetime, timedelta
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User
from .models import GitHubProfile, GitHubOAuth2Token, GitHubRepository, GitHubConnection, GitHubSyncLog, GitHubCollaborator
import logging

logger = logging.getLogger(__name__)

# GitHub API Configuration
GITHUB_BASE_URL = getattr(settings, 'GITHUB_BASE_URL', 'https://github.com')
GITHUB_API_BASE_URL = getattr(settings, 'GITHUB_API_BASE_URL', 'https://api.github.com')
GITHUB_CLIENT_ID = getattr(settings, 'GITHUB_CLIENT_ID', '')
GITHUB_CLIENT_SECRET = getattr(settings, 'GITHUB_CLIENT_SECRET', '')
GITHUB_REDIRECT_URI = getattr(settings, 'GITHUB_REDIRECT_URI', 'http://localhost:8000/github/callback/')


class GitHubAPIError(Exception):
    """Custom exception for GitHub API errors"""
    def __init__(self, message, status_code=None, response_data=None):
        super().__init__(message)
        self.status_code = status_code
        self.response_data = response_data


class GitHubAuthService:
    """Service for GitHub OAuth2 authentication"""
    
    @staticmethod
    def get_authorization_url(state=None):
        """Generate GitHub OAuth2 authorization URL"""
        params = {
            'client_id': GITHUB_CLIENT_ID,
            'response_type': 'code',
            'scope': 'repo,user:email,read:org',
            'redirect_uri': GITHUB_REDIRECT_URI,
        }
        
        if state:
            params['state'] = state
        
        query_string = '&'.join([f"{k}={v}" for k, v in params.items()])
        return f"{GITHUB_BASE_URL}/login/oauth/authorize?{query_string}"
    
    @staticmethod
    def exchange_code_for_token(code, state=None):
        """Exchange authorization code for access token"""
        token_url = f"{GITHUB_BASE_URL}/login/oauth/access_token"
        
        data = {
            'client_id': GITHUB_CLIENT_ID,
            'client_secret': GITHUB_CLIENT_SECRET,
            'code': code,
            'redirect_uri': GITHUB_REDIRECT_URI,
        }
        
        if state:
            data['state'] = state
        
        headers = {
            'Accept': 'application/json',
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        
        try:
            response = requests.post(token_url, data=data, headers=headers)
            response.raise_for_status()
            
            token_data = response.json()
            
            # Check for errors
            if 'error' in token_data:
                raise GitHubAPIError(f"OAuth error: {token_data.get('error_description', token_data['error'])}")
            
            access_token = token_data.get('access_token')
            token_type = token_data.get('token_type', 'bearer')
            scope = token_data.get('scope', '')
            
            if not access_token:
                raise GitHubAPIError("No access token received from GitHub")
            
            return {
                'access_token': access_token,
                'token_type': token_type,
                'scope': scope,
            }
            
        except requests.RequestException as e:
            logger.error(f"Error exchanging code for token: {e}")
            raise GitHubAPIError(f"Failed to exchange authorization code: {str(e)}")
    
    @staticmethod
    def store_token(user, token_data, github_user_data):
        """Store or update GitHub token for user"""
        token, created = GitHubOAuth2Token.objects.update_or_create(
            user=user,
            defaults={
                'access_token': token_data['access_token'],
                'token_type': token_data.get('token_type', 'bearer'),
                'scope': token_data.get('scope', ''),
                'github_username': github_user_data['login'],
            }
        )
        
        return token
    
    @staticmethod
    def get_valid_token(user):
        """Get a valid access token for user"""
        try:
            token = GitHubOAuth2Token.objects.get(user=user)
            
            # GitHub tokens don't expire, but check if too old for security
            if token.is_expired():
                logger.warning(f"GitHub token for {user.username} is very old, consider re-authentication")
            
            return token
            
        except GitHubOAuth2Token.DoesNotExist:
            return None


class GitHubAPIService:
    """Service for interacting with GitHub API"""
    
    def __init__(self, user=None, access_token=None):
        self.user = user
        self.access_token = access_token
        
        if user and not access_token:
            token = GitHubAuthService.get_valid_token(user)
            if token:
                self.access_token = token.access_token
    
    def _make_request(self, endpoint, method='GET', data=None, params=None):
        """Make authenticated request to GitHub API"""
        if not self.access_token:
            raise GitHubAPIError("No valid access token available")
        
        url = f"{GITHUB_API_BASE_URL}/{endpoint.lstrip('/')}"
        
        headers = {
            'Accept': 'application/vnd.github.v3+json',
            'Authorization': f'Bearer {self.access_token}',
            'User-Agent': 'SciTeX-Cloud/1.0',
        }
        
        if method in ['POST', 'PUT', 'PATCH'] and data:
            headers['Content-Type'] = 'application/json'
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, params=params)
            elif method == 'POST':
                response = requests.post(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == 'PATCH':
                response = requests.patch(url, headers=headers, data=json.dumps(data) if data else None)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise GitHubAPIError(f"Unsupported HTTP method: {method}")
            
            response.raise_for_status()
            
            # Handle empty responses
            if response.status_code == 204 or not response.content:
                return {}
            
            return response.json()
            
        except requests.RequestException as e:
            logger.error(f"GitHub API request failed: {e}")
            error_msg = f"API request failed: {str(e)}"
            
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    if 'message' in error_data:
                        error_msg = f"GitHub API error: {error_data['message']}"
                except:
                    pass
            
            raise GitHubAPIError(error_msg, 
                              status_code=getattr(e.response, 'status_code', None),
                              response_data=getattr(e.response, 'text', None))
    
    def get_user(self):
        """Get authenticated user information"""
        return self._make_request('user')
    
    def get_user_repos(self, per_page=100, page=1):
        """Get user's repositories"""
        params = {
            'per_page': per_page,
            'page': page,
            'sort': 'updated',
            'type': 'all',
        }
        return self._make_request('user/repos', params=params)
    
    def get_repository(self, owner, repo):
        """Get specific repository information"""
        return self._make_request(f'repos/{owner}/{repo}')
    
    def get_repository_contents(self, owner, repo, path='', ref=None):
        """Get repository contents"""
        endpoint = f'repos/{owner}/{repo}/contents/{path}'
        params = {}
        if ref:
            params['ref'] = ref
        return self._make_request(endpoint, params=params)
    
    def get_repository_commits(self, owner, repo, per_page=30, page=1, sha=None, path=None):
        """Get repository commits"""
        endpoint = f'repos/{owner}/{repo}/commits'
        params = {
            'per_page': per_page,
            'page': page,
        }
        if sha:
            params['sha'] = sha
        if path:
            params['path'] = path
        return self._make_request(endpoint, params=params)
    
    def get_repository_branches(self, owner, repo):
        """Get repository branches"""
        return self._make_request(f'repos/{owner}/{repo}/branches')
    
    def get_repository_collaborators(self, owner, repo):
        """Get repository collaborators"""
        return self._make_request(f'repos/{owner}/{repo}/collaborators')
    
    def create_repository_file(self, owner, repo, path, content, message, branch=None):
        """Create a file in repository"""
        endpoint = f'repos/{owner}/{repo}/contents/{path}'
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            'message': message,
            'content': encoded_content,
        }
        
        if branch:
            data['branch'] = branch
        
        return self._make_request(endpoint, method='PUT', data=data)
    
    def update_repository_file(self, owner, repo, path, content, message, sha, branch=None):
        """Update a file in repository"""
        endpoint = f'repos/{owner}/{repo}/contents/{path}'
        
        # Encode content to base64
        encoded_content = base64.b64encode(content.encode('utf-8')).decode('utf-8')
        
        data = {
            'message': message,
            'content': encoded_content,
            'sha': sha,
        }
        
        if branch:
            data['branch'] = branch
        
        return self._make_request(endpoint, method='PUT', data=data)
    
    def delete_repository_file(self, owner, repo, path, message, sha, branch=None):
        """Delete a file from repository"""
        endpoint = f'repos/{owner}/{repo}/contents/{path}'
        
        data = {
            'message': message,
            'sha': sha,
        }
        
        if branch:
            data['branch'] = branch
        
        return self._make_request(endpoint, method='DELETE', data=data)
    
    def create_webhook(self, owner, repo, webhook_url, secret=None, events=None):
        """Create repository webhook"""
        endpoint = f'repos/{owner}/{repo}/hooks'
        
        if events is None:
            events = ['push', 'pull_request']
        
        config = {
            'url': webhook_url,
            'content_type': 'json',
        }
        
        if secret:
            config['secret'] = secret
        
        data = {
            'name': 'web',
            'active': True,
            'events': events,
            'config': config,
        }
        
        return self._make_request(endpoint, method='POST', data=data)


class GitHubSyncService:
    """Service for synchronizing GitHub data with local database"""
    
    def __init__(self, user):
        self.user = user
        self.api_service = GitHubAPIService(user=user)
        
        # Get or create GitHub profile
        try:
            token = GitHubOAuth2Token.objects.get(user=user)
            self.github_profile, created = GitHubProfile.objects.get_or_create(
                user=user,
                defaults={'github_username': token.github_username}
            )
        except GitHubOAuth2Token.DoesNotExist:
            raise GitHubAPIError("User does not have GitHub authentication")
    
    def sync_profile(self):
        """Sync user's GitHub profile information"""
        sync_log = GitHubSyncLog.objects.create(
            profile=self.github_profile,
            sync_type='profile'
        )
        
        try:
            # Get user data from GitHub
            user_data = self.api_service.get_user()
            
            # Update profile
            self.github_profile.github_id = user_data['id']
            self.github_profile.github_username = user_data['login']
            self.github_profile.name = user_data.get('name', '') or ''
            self.github_profile.email = user_data.get('email', '') or ''
            self.github_profile.bio = user_data.get('bio', '') or ''
            self.github_profile.blog = user_data.get('blog', '') or ''
            self.github_profile.location = user_data.get('location', '') or ''
            self.github_profile.company = user_data.get('company', '') or ''
            
            # Update statistics
            self.github_profile.public_repos = user_data.get('public_repos', 0)
            self.github_profile.public_gists = user_data.get('public_gists', 0)
            self.github_profile.followers = user_data.get('followers', 0)
            self.github_profile.following = user_data.get('following', 0)
            
            # Store raw data
            self.github_profile.github_data = user_data
            self.github_profile.is_synced = True
            self.github_profile.last_sync_at = timezone.now()
            self.github_profile.save()
            
            sync_log.items_processed = 1
            sync_log.items_updated = 1
            sync_log.mark_completed('success')
            
            logger.info(f"Successfully synced GitHub profile for {self.user.username}")
            return True
            
        except Exception as e:
            sync_log.add_error(f"Profile sync failed: {str(e)}")
            logger.error(f"Failed to sync GitHub profile for {self.user.username}: {e}")
            return False
    
    def sync_repositories(self):
        """Sync user's GitHub repositories"""
        sync_log = GitHubSyncLog.objects.create(
            profile=self.github_profile,
            sync_type='repositories'
        )
        
        try:
            # Get all repositories
            all_repos = []
            page = 1
            per_page = 100
            
            while True:
                repos = self.api_service.get_user_repos(per_page=per_page, page=page)
                if not repos:
                    break
                all_repos.extend(repos)
                if len(repos) < per_page:
                    break
                page += 1
            
            created_count = 0
            updated_count = 0
            processed_count = len(all_repos)
            
            for repo_data in all_repos:
                repo, created = self._create_or_update_repository(repo_data)
                
                if created:
                    created_count += 1
                else:
                    updated_count += 1
            
            sync_log.items_processed = processed_count
            sync_log.items_created = created_count
            sync_log.items_updated = updated_count
            sync_log.mark_completed('success')
            
            logger.info(f"Successfully synced {processed_count} repositories for {self.user.username}")
            return True
            
        except Exception as e:
            sync_log.add_error(f"Repositories sync failed: {str(e)}")
            logger.error(f"Failed to sync GitHub repositories for {self.user.username}: {e}")
            return False
    
    def _create_or_update_repository(self, repo_data):
        """Create or update a repository from GitHub data"""
        # Parse dates
        created_at = datetime.fromisoformat(repo_data['created_at'].replace('Z', '+00:00'))
        updated_at = datetime.fromisoformat(repo_data['updated_at'].replace('Z', '+00:00'))
        pushed_at = None
        if repo_data.get('pushed_at'):
            pushed_at = datetime.fromisoformat(repo_data['pushed_at'].replace('Z', '+00:00'))
        
        # Create or update repository
        repo, created = GitHubRepository.objects.update_or_create(
            profile=self.github_profile,
            github_id=repo_data['id'],
            defaults={
                'name': repo_data['name'],
                'full_name': repo_data['full_name'],
                'description': repo_data.get('description', '') or '',
                'is_private': repo_data['private'],
                'is_fork': repo_data['fork'],
                'is_archived': repo_data.get('archived', False),
                'is_disabled': repo_data.get('disabled', False),
                'default_branch': repo_data.get('default_branch', 'main'),
                'language': repo_data.get('language', '') or '',
                'topics': repo_data.get('topics', []),
                'size': repo_data.get('size', 0),
                'stargazers_count': repo_data.get('stargazers_count', 0),
                'watchers_count': repo_data.get('watchers_count', 0),
                'forks_count': repo_data.get('forks_count', 0),
                'open_issues_count': repo_data.get('open_issues_count', 0),
                'clone_url': repo_data['clone_url'],
                'ssh_url': repo_data['ssh_url'],
                'git_url': repo_data['git_url'],
                'github_created_at': created_at,
                'github_updated_at': updated_at,
                'github_pushed_at': pushed_at,
                'github_data': repo_data,
            }
        )
        
        return repo, created
    
    def sync_repository_collaborators(self, repository):
        """Sync collaborators for a specific repository"""
        try:
            owner, repo_name = repository.full_name.split('/')
            collaborators_data = self.api_service.get_repository_collaborators(owner, repo_name)
            
            # Clear existing collaborators
            repository.collaborators.all().delete()
            
            # Create new collaborators
            for collab_data in collaborators_data:
                # Try to find matching SciTeX user
                scitex_user = None
                try:
                    github_profile = GitHubProfile.objects.get(github_id=collab_data['id'])
                    scitex_user = github_profile.user
                except GitHubProfile.DoesNotExist:
                    pass
                
                GitHubCollaborator.objects.create(
                    repository=repository,
                    github_id=collab_data['id'],
                    github_username=collab_data['login'],
                    permission=collab_data.get('permissions', {}).get('admin') and 'admin' or 
                              collab_data.get('permissions', {}).get('maintain') and 'maintain' or
                              collab_data.get('permissions', {}).get('push') and 'write' or 'read',
                    scitex_user=scitex_user,
                )
            
            logger.info(f"Successfully synced {len(collaborators_data)} collaborators for {repository.full_name}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to sync collaborators for {repository.full_name}: {e}")
            return False
    
    def full_sync(self):
        """Perform full synchronization of profile and repositories"""
        sync_log = GitHubSyncLog.objects.create(
            profile=self.github_profile,
            sync_type='full'
        )
        
        try:
            profile_success = self.sync_profile()
            repos_success = self.sync_repositories()
            
            if profile_success and repos_success:
                sync_log.mark_completed('success')
                return True
            elif profile_success or repos_success:
                sync_log.mark_completed('partial')
                return True
            else:
                sync_log.mark_completed('failed')
                return False
                
        except Exception as e:
            sync_log.add_error(f"Full sync failed: {str(e)}")
            return False


class GitHubCodeSyncService:
    """Service for synchronizing code between GitHub and SciTeX Code module"""
    
    def __init__(self, connection):
        self.connection = connection
        self.repository = connection.repository
        self.api_service = GitHubAPIService(user=self.repository.profile.user)
    
    def sync_repository_to_code(self):
        """Sync GitHub repository content to Code module"""
        sync_log = GitHubSyncLog.objects.create(
            profile=self.repository.profile,
            repository=self.repository,
            sync_type='code_sync'
        )
        
        try:
            owner, repo_name = self.repository.full_name.split('/')
            
            # Get repository contents
            contents = self.api_service.get_repository_contents(owner, repo_name)
            
            files_synced = 0
            commits_synced = 0
            
            # Sync files (implement based on your Code module structure)
            for item in contents:
                if item['type'] == 'file':
                    success = self._sync_file_to_code(owner, repo_name, item)
                    if success:
                        files_synced += 1
            
            # Get recent commits
            commits = self.api_service.get_repository_commits(owner, repo_name, per_page=10)
            commits_synced = len(commits)
            
            # Update connection
            self.connection.sync_status = 'synced'
            self.connection.last_sync_at = timezone.now()
            self.connection.last_sync_commit = commits[0]['sha'] if commits else ''
            self.connection.successful_syncs += 1
            self.connection.total_syncs += 1
            self.connection.save()
            
            sync_log.files_synced = files_synced
            sync_log.commits_synced = commits_synced
            sync_log.items_processed = len(contents)
            sync_log.mark_completed('success')
            
            logger.info(f"Successfully synced {files_synced} files from {self.repository.full_name}")
            return True
            
        except Exception as e:
            self.connection.sync_status = 'error'
            self.connection.last_error = str(e)
            self.connection.failed_syncs += 1
            self.connection.total_syncs += 1
            self.connection.save()
            
            sync_log.add_error(f"Code sync failed: {str(e)}")
            logger.error(f"Failed to sync code from {self.repository.full_name}: {e}")
            return False
    
    def _sync_file_to_code(self, owner, repo_name, file_item):
        """Sync individual file to Code module"""
        try:
            # Get file content
            file_data = self.api_service.get_repository_contents(owner, repo_name, file_item['path'])
            
            if file_data.get('content'):
                # Decode base64 content
                content = base64.b64decode(file_data['content']).decode('utf-8')
                
                # Here you would integrate with your Code module
                # For now, just log the sync
                logger.info(f"Synced file: {file_item['path']} ({len(content)} chars)")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to sync file {file_item['path']}: {e}")
            return False


# Utility functions
def is_github_configured():
    """Check if GitHub integration is properly configured"""
    return bool(GITHUB_CLIENT_ID and GITHUB_CLIENT_SECRET)


def validate_github_username(username):
    """Validate GitHub username format"""
    import re
    pattern = r'^[a-zA-Z0-9]([a-zA-Z0-9-]*[a-zA-Z0-9])?$'
    return bool(re.match(pattern, username)) and len(username) <= 39


def parse_github_url(url):
    """Parse GitHub repository URL to extract owner and repo"""
    import re
    
    # Match various GitHub URL formats
    patterns = [
        r'https://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
        r'git@github\.com:([^/]+)/([^/]+?)(?:\.git)?$',
        r'git://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$',
    ]
    
    for pattern in patterns:
        match = re.match(pattern, url)
        if match:
            return match.group(1), match.group(2)
    
    return None, None