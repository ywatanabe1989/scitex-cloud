"""
Gitea API Client for SciTeX Cloud

This module provides a Python wrapper for the Gitea REST API.
"""

import requests
import re
from typing import Dict, List
from django.conf import settings
from .exceptions import (
    GiteaAPIError,
)


def convert_git_url_to_https(git_url: str) -> str:
    """
    Convert Git URL to HTTPS format (required for Gitea migration API)

    Supports:
    - SSH: git@github.com:user/repo.git → https://github.com/user/repo
    - HTTPS: https://github.com/user/repo.git → https://github.com/user/repo
    - HTTPS (no .git): https://github.com/user/repo → https://github.com/user/repo

    Args:
        git_url: Git URL in any format

    Returns:
        HTTPS URL without .git suffix
    """
    git_url = git_url.strip()

    # Pattern 1: SSH format (git@host:user/repo.git)
    ssh_pattern = r"git@([^:]+):(.+?)(?:\.git)?$"
    match = re.match(ssh_pattern, git_url)
    if match:
        host = match.group(1)
        path = match.group(2)
        return f"https://{host}/{path}"

    # Pattern 2: HTTPS format - just remove .git if present
    if git_url.startswith("https://") or git_url.startswith("http://"):
        return git_url.rstrip(".git")

    # If no match, return as-is (might be already correct)
    return git_url


class GiteaClient:
    """
    Client for interacting with Gitea REST API

    Documentation: https://docs.gitea.io/en-us/api-usage/
    """

    def __init__(self, base_url: str = None, token: str = None):
        """
        Initialize Gitea client

        Args:
            base_url: Gitea instance URL (defaults to settings.GITEA_URL)
            token: API token (defaults to settings.GITEA_TOKEN)
        """
        self.base_url = base_url or settings.GITEA_URL
        self.api_url = f"{self.base_url}/api/v1"
        self.token = token or settings.GITEA_TOKEN

        if not self.token:
            raise GiteaAPIError("Gitea API token not configured")

    def _get_headers(self, extra_headers: Dict = None) -> Dict:
        """Build request headers with authentication"""
        headers = {
            "Authorization": f"token {self.token}",
            "Content-Type": "application/json",
        }
        if extra_headers:
            headers.update(extra_headers)
        return headers

    def _request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make HTTP request to Gitea API

        Args:
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint (e.g., '/user/repos')
            **kwargs: Additional arguments for requests

        Returns:
            Response object

        Raises:
            GiteaAPIError: If request fails
        """
        url = f"{self.api_url}{endpoint}"
        headers = self._get_headers(kwargs.pop("headers", None))

        try:
            response = requests.request(
                method=method, url=url, headers=headers, **kwargs
            )
            response.raise_for_status()
            return response
        except requests.HTTPError:
            # Parse error message from Gitea response
            error_msg = f"Gitea API error ({response.status_code})"
            try:
                error_data = response.json()
                if "message" in error_data:
                    error_msg = error_data["message"]
            except (ValueError, requests.RequestException):
                # JSON parsing failed, use response text instead
                if response.text:
                    error_msg = response.text[:200]

            raise GiteaAPIError(error_msg)
        except requests.RequestException as e:
            raise GiteaAPIError(f"Request failed: {e}")

    # ----------------------------------------
    # User Operations
    # ----------------------------------------

    def get_current_user(self) -> Dict:
        """Get current authenticated user info"""
        response = self._request("GET", "/user")
        return response.json()

    def delete_user(self, username: str) -> bool:
        """
        Delete a Gitea user (requires admin token)

        Args:
            username: Username to delete

        Returns:
            True if successful
        """
        self._request("DELETE", f"/admin/users/{username}")
        return True

    # ----------------------------------------
    # Repository Operations
    # ----------------------------------------

    def list_repositories(self, username: str = None) -> List[Dict]:
        """
        List repositories

        Args:
            username: Username to list repos for (defaults to current user)

        Returns:
            List of repository objects
        """
        if username:
            endpoint = f"/users/{username}/repos"
        else:
            endpoint = "/user/repos"

        response = self._request("GET", endpoint)
        return response.json()

    def create_repository(
        self,
        name: str,
        description: str = "",
        private: bool = False,
        auto_init: bool = True,
        gitignores: str = "",
        license: str = "",
        readme: str = "Default",
        owner: str = None,
    ) -> Dict:
        """
        Create a new repository

        Args:
            name: Repository name
            description: Repository description
            private: Make repository private
            auto_init: Initialize with README
            gitignores: Gitignore template (e.g., 'Python')
            license: License template (e.g., 'MIT')
            readme: README template (e.g., 'Default')
            owner: Username to create repo for (requires admin token, defaults to authenticated user)

        Returns:
            Created repository object
        """
        data = {
            "name": name,
            "description": description,
            "private": private,
            "auto_init": auto_init,
        }

        if gitignores:
            data["gitignores"] = gitignores
        if license:
            data["license"] = license
        if readme:
            data["readme"] = readme

        # Use admin endpoint to create repo for specific user
        if owner:
            endpoint = f"/admin/users/{owner}/repos"
        else:
            endpoint = "/user/repos"

        response = self._request("POST", endpoint, json=data)
        return response.json()

    def get_repository(self, owner: str, repo: str) -> Dict:
        """
        Get repository information

        Args:
            owner: Repository owner username
            repo: Repository name

        Returns:
            Repository object
        """
        response = self._request("GET", f"/repos/{owner}/{repo}")
        return response.json()

    def delete_repository(self, owner: str, repo: str) -> bool:
        """
        Delete a repository

        Args:
            owner: Repository owner username
            repo: Repository name

        Returns:
            True if successful
        """
        self._request("DELETE", f"/repos/{owner}/{repo}")
        return True

    # ----------------------------------------
    # Migration/Import Operations
    # ----------------------------------------

    def migrate_repository(
        self,
        clone_addr: str,
        repo_name: str = None,
        service: str = "github",
        auth_token: str = "",
        mirror: bool = False,
        private: bool = False,
        description: str = "",
        wiki: bool = True,
        milestones: bool = True,
        labels: bool = True,
        issues: bool = True,
        pull_requests: bool = True,
        releases: bool = True,
    ) -> Dict:
        """
        Migrate/import repository from external source

        Args:
            clone_addr: Git clone URL (HTTPS or SSH format)
            repo_name: Name for imported repo (extracted from URL if not provided)
            service: Source service ('github', 'gitlab', 'gitea', 'gogs')
            auth_token: Authentication token for private repos
            mirror: Create as mirror (keep synced)
            private: Make repository private
            description: Repository description
            wiki: Import wiki
            milestones: Import milestones
            labels: Import labels
            issues: Import issues
            pull_requests: Import pull requests
            releases: Import releases

        Returns:
            Created repository object
        """
        # Convert SSH URLs to HTTPS (Gitea API requires HTTPS)
        clone_addr = convert_git_url_to_https(clone_addr)

        # Extract repo name from URL if not provided
        # Preserves original name from the source repository
        if not repo_name:
            repo_name = clone_addr.rstrip("/").split("/")[-1]
            # Remove .git suffix while preserving case and other characters
            if repo_name.endswith(".git"):
                repo_name = repo_name[:-4]

        data = {
            "clone_addr": clone_addr,
            "service": service,
            "repo_name": repo_name,
            "mirror": mirror,
            "private": private,
            "description": description or f"Imported from {clone_addr}",
            "wiki": wiki,
            "milestones": milestones,
            "labels": labels,
            "issues": issues,
            "pull_requests": pull_requests,
            "releases": releases,
        }

        if auth_token:
            data["auth_token"] = auth_token

        response = self._request("POST", "/repos/migrate", json=data)
        return response.json()

    # ----------------------------------------
    # File Operations
    # ----------------------------------------

    def get_file_contents(
        self, owner: str, repo: str, filepath: str, ref: str = "main"
    ) -> Dict:
        """
        Get file contents from repository

        Args:
            owner: Repository owner
            repo: Repository name
            filepath: Path to file in repository
            ref: Branch/tag/commit (default: main)

        Returns:
            File content object (base64 encoded)
        """
        response = self._request(
            "GET", f"/repos/{owner}/{repo}/contents/{filepath}", params={"ref": ref}
        )
        return response.json()

    def list_files(
        self, owner: str, repo: str, path: str = "", ref: str = "main"
    ) -> List[Dict]:
        """
        List files in repository directory

        Args:
            owner: Repository owner
            repo: Repository name
            path: Directory path (empty for root)
            ref: Branch/tag/commit (default: main)

        Returns:
            List of file/directory objects
        """
        endpoint = f"/repos/{owner}/{repo}/contents"
        if path:
            endpoint += f"/{path}"

        response = self._request("GET", endpoint, params={"ref": ref})
        return response.json()

    # ----------------------------------------
    # Organization Operations
    # ----------------------------------------

    def create_organization(
        self,
        name: str,
        full_name: str = "",
        description: str = "",
        website: str = "",
        location: str = "",
    ) -> Dict:
        """
        Create an organization

        Args:
            name: Organization username
            full_name: Full organization name
            description: Description
            website: Website URL
            location: Location

        Returns:
            Created organization object
        """
        data = {
            "username": name,
            "full_name": full_name or name,
            "description": description,
            "website": website,
            "location": location,
        }

        response = self._request("POST", "/orgs", json=data)
        return response.json()

    def list_organizations(self) -> List[Dict]:
        """List organizations for current user"""
        response = self._request("GET", "/user/orgs")
        return response.json()

    # ----------------------------------------
    # Fork Operations
    # ----------------------------------------

    def fork_repository(self, owner: str, repo: str, organization: str = None) -> Dict:
        """
        Fork a repository

        Args:
            owner: Original repository owner
            repo: Original repository name
            organization: Organization to fork to (optional)

        Returns:
            Forked repository object
        """
        data = {}
        if organization:
            data["organization"] = organization

        response = self._request("POST", f"/repos/{owner}/{repo}/forks", json=data)
        return response.json()
