"""
Security scanning service for SciTeX projects
Provides vulnerability scanning, secret detection, and dependency analysis
"""

import subprocess
import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SecurityScanner:
    """
    Main security scanner class
    Orchestrates various security checks
    """

    def __init__(self, project):
        self.project = project
        self.project_path = project.get_local_path()

    def run_full_scan(self, user=None) -> Dict:
        """
        Run a complete security scan on the project

        Returns:
            dict: Scan results with alerts and statistics
        """
        from apps.project_app.models.security import SecurityScanResult

        # Create scan result record
        scan = SecurityScanResult.objects.create(
            project=self.project,
            scan_type='full',
            status='running',
            triggered_by=user
        )

        start_time = datetime.now()
        results = {
            'alerts': [],
            'critical': 0,
            'high': 0,
            'medium': 0,
            'low': 0,
            'errors': []
        }

        try:
            # Run dependency vulnerability scan
            dep_results = self.scan_dependencies()
            results['alerts'].extend(dep_results['alerts'])

            # Run secret scanning
            secret_results = self.scan_secrets()
            results['alerts'].extend(secret_results['alerts'])

            # Run code analysis
            code_results = self.scan_code()
            results['alerts'].extend(code_results['alerts'])

            # Count alerts by severity
            for alert in results['alerts']:
                severity = alert.get('severity', 'low')
                if severity == 'critical':
                    results['critical'] += 1
                elif severity == 'high':
                    results['high'] += 1
                elif severity == 'medium':
                    results['medium'] += 1
                elif severity == 'low':
                    results['low'] += 1

            # Save alerts to database
            alerts_created = self._save_alerts(results['alerts'])

            # Complete scan
            duration = (datetime.now() - start_time).total_seconds()
            scan.alerts_created = alerts_created
            scan.critical_count = results['critical']
            scan.high_count = results['high']
            scan.medium_count = results['medium']
            scan.low_count = results['low']
            scan.complete(duration=duration)

            results['scan_id'] = scan.id
            results['duration'] = duration

        except Exception as e:
            logger.error(f"Security scan failed: {e}")
            scan.fail(str(e))
            results['errors'].append(str(e))

        return results

    def scan_dependencies(self) -> Dict:
        """
        Scan Python dependencies for known vulnerabilities
        Uses pip-audit or safety

        Returns:
            dict: Vulnerability results
        """
        results = {'alerts': [], 'errors': []}

        # Check if requirements.txt or pyproject.toml exists
        requirements_file = self.project_path / 'requirements.txt'
        pyproject_file = self.project_path / 'pyproject.toml'

        if not requirements_file.exists() and not pyproject_file.exists():
            logger.info(f"No dependency files found for {self.project.name}")
            return results

        # Try using pip-audit (preferred)
        if self._has_pip_audit():
            results = self._scan_with_pip_audit()
        # Fallback to safety
        elif self._has_safety():
            results = self._scan_with_safety()
        else:
            logger.warning("No security scanning tools available (pip-audit or safety)")
            results['errors'].append("Security scanning tools not installed")

        # Update dependency graph
        self._update_dependency_graph()

        return results

    def _scan_with_pip_audit(self) -> Dict:
        """Scan using pip-audit"""
        results = {'alerts': [], 'errors': []}

        try:
            cmd = [
                'pip-audit',
                '--format', 'json',
                '--requirement', str(self.project_path / 'requirements.txt')
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=300
            )

            if result.returncode == 0:
                # No vulnerabilities found
                return results

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                for vuln in data.get('vulnerabilities', []):
                    alert = {
                        'alert_type': 'dependency',
                        'severity': self._map_severity(vuln.get('severity', 'medium')),
                        'title': vuln.get('description', 'Vulnerability detected'),
                        'description': vuln.get('fix_versions', 'No description available'),
                        'affected_package': vuln.get('name', ''),
                        'affected_version': vuln.get('version', ''),
                        'fixed_version': ', '.join(vuln.get('fix_versions', [])),
                        'cve_id': vuln.get('id', ''),
                        'advisory_url': vuln.get('aliases', [{}])[0].get('url', '') if vuln.get('aliases') else '',
                        'fix_available': bool(vuln.get('fix_versions')),
                    }
                    results['alerts'].append(alert)
            except json.JSONDecodeError:
                logger.error("Failed to parse pip-audit output")
                results['errors'].append("Failed to parse pip-audit output")

        except subprocess.TimeoutExpired:
            logger.error("pip-audit timed out")
            results['errors'].append("Dependency scan timed out")
        except Exception as e:
            logger.error(f"pip-audit failed: {e}")
            results['errors'].append(str(e))

        return results

    def _scan_with_safety(self) -> Dict:
        """Scan using safety"""
        results = {'alerts': [], 'errors': []}

        try:
            cmd = [
                'safety', 'check',
                '--json',
                '--file', str(self.project_path / 'requirements.txt')
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=300
            )

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                for vuln in data:
                    alert = {
                        'alert_type': 'dependency',
                        'severity': self._map_severity('high'),  # safety doesn't provide severity
                        'title': vuln[0],  # Package name
                        'description': vuln[3],  # Vulnerability description
                        'affected_package': vuln[0],
                        'affected_version': vuln[2],
                        'fixed_version': '',  # Not provided by safety
                        'cve_id': vuln[4] if len(vuln) > 4 else '',
                        'fix_available': False,
                    }
                    results['alerts'].append(alert)
            except (json.JSONDecodeError, IndexError, KeyError):
                logger.error("Failed to parse safety output")
                results['errors'].append("Failed to parse safety output")

        except subprocess.TimeoutExpired:
            logger.error("safety check timed out")
            results['errors'].append("Dependency scan timed out")
        except Exception as e:
            logger.error(f"safety check failed: {e}")
            results['errors'].append(str(e))

        return results

    def scan_secrets(self) -> Dict:
        """
        Scan for secrets in code (API keys, passwords, tokens)
        Uses detect-secrets or similar

        Returns:
            dict: Secret detection results
        """
        results = {'alerts': [], 'errors': []}

        if not self._has_detect_secrets():
            logger.info("detect-secrets not available")
            return results

        try:
            # Initialize baseline if not exists
            baseline_file = self.project_path / '.secrets.baseline'

            # Scan for secrets
            cmd = [
                'detect-secrets', 'scan',
                '--baseline', str(baseline_file),
                str(self.project_path)
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=300
            )

            # Parse results
            if result.stdout:
                try:
                    data = json.loads(result.stdout)
                    for file_path, secrets in data.get('results', {}).items():
                        for secret in secrets:
                            alert = {
                                'alert_type': 'secret',
                                'severity': 'critical',  # Secrets are always critical
                                'title': f"Potential secret detected: {secret.get('type', 'unknown')}",
                                'description': f"Potential {secret.get('type', 'secret')} found in {file_path}",
                                'file_path': file_path,
                                'line_number': secret.get('line_number', 0),
                                'fix_available': False,
                            }
                            results['alerts'].append(alert)
                except json.JSONDecodeError:
                    logger.error("Failed to parse detect-secrets output")

        except subprocess.TimeoutExpired:
            results['errors'].append("Secret scan timed out")
        except Exception as e:
            logger.error(f"Secret scan failed: {e}")
            results['errors'].append(str(e))

        return results

    def scan_code(self) -> Dict:
        """
        Static code analysis for security issues
        Uses bandit for Python

        Returns:
            dict: Code analysis results
        """
        results = {'alerts': [], 'errors': []}

        if not self._has_bandit():
            logger.info("bandit not available")
            return results

        try:
            cmd = [
                'bandit',
                '-r', str(self.project_path),
                '-f', 'json',
                '-ll',  # Only report low severity and above
            ]

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=300
            )

            # Parse JSON output
            try:
                data = json.loads(result.stdout)
                for issue in data.get('results', []):
                    alert = {
                        'alert_type': 'code',
                        'severity': self._map_bandit_severity(issue.get('issue_severity', 'LOW')),
                        'title': issue.get('issue_text', 'Security issue detected'),
                        'description': f"{issue.get('issue_text', '')} - {issue.get('issue_cwe', {}).get('link', '')}",
                        'file_path': issue.get('filename', ''),
                        'line_number': issue.get('line_number', 0),
                        'fix_available': False,
                    }
                    results['alerts'].append(alert)
            except json.JSONDecodeError:
                logger.error("Failed to parse bandit output")

        except subprocess.TimeoutExpired:
            results['errors'].append("Code scan timed out")
        except Exception as e:
            logger.error(f"Code scan failed: {e}")
            results['errors'].append(str(e))

        return results

    def check_outdated_dependencies(self) -> Dict:
        """
        Check for outdated dependencies

        Returns:
            dict: Outdated dependency results
        """
        results = {'alerts': [], 'errors': []}

        try:
            cmd = ['pip', 'list', '--outdated', '--format', 'json']

            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                cwd=str(self.project_path),
                timeout=60
            )

            if result.returncode == 0:
                data = json.loads(result.stdout)
                for package in data:
                    alert = {
                        'alert_type': 'outdated',
                        'severity': 'low',
                        'title': f"Outdated dependency: {package['name']}",
                        'description': f"Package {package['name']} is outdated. Current: {package['version']}, Latest: {package['latest_version']}",
                        'affected_package': package['name'],
                        'affected_version': package['version'],
                        'fixed_version': package['latest_version'],
                        'fix_available': True,
                    }
                    results['alerts'].append(alert)

        except Exception as e:
            logger.error(f"Outdated check failed: {e}")
            results['errors'].append(str(e))

        return results

    def _update_dependency_graph(self):
        """Update dependency graph from project dependencies"""
        from apps.project_app.models.security import DependencyGraph

        requirements_file = self.project_path / 'requirements.txt'
        if not requirements_file.exists():
            return

        try:
            # Parse requirements.txt
            with open(requirements_file, 'r') as f:
                for line in f:
                    line = line.strip()
                    if not line or line.startswith('#'):
                        continue

                    # Parse package==version
                    match = re.match(r'([a-zA-Z0-9_-]+)==([0-9.]+)', line)
                    if match:
                        package_name, version = match.groups()

                        # Create or update dependency
                        dep, created = DependencyGraph.objects.update_or_create(
                            project=self.project,
                            package_name=package_name,
                            version=version,
                            defaults={
                                'is_direct': True,
                                'package_type': 'python',
                            }
                        )

        except Exception as e:
            logger.error(f"Failed to update dependency graph: {e}")

    def _save_alerts(self, alerts: List[Dict]) -> int:
        """Save alerts to database"""
        from apps.project_app.models.security import SecurityAlert

        count = 0
        for alert_data in alerts:
            # Check if alert already exists
            existing = SecurityAlert.objects.filter(
                project=self.project,
                title=alert_data['title'],
                affected_package=alert_data.get('affected_package', ''),
                status='open'
            ).first()

            if not existing:
                SecurityAlert.objects.create(
                    project=self.project,
                    **alert_data
                )
                count += 1

        return count

    def _has_pip_audit(self) -> bool:
        """Check if pip-audit is installed"""
        try:
            subprocess.run(['pip-audit', '--version'], capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _has_safety(self) -> bool:
        """Check if safety is installed"""
        try:
            subprocess.run(['safety', '--version'], capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _has_detect_secrets(self) -> bool:
        """Check if detect-secrets is installed"""
        try:
            subprocess.run(['detect-secrets', '--version'], capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    def _has_bandit(self) -> bool:
        """Check if bandit is installed"""
        try:
            subprocess.run(['bandit', '--version'], capture_output=True, timeout=5)
            return True
        except (subprocess.SubprocessError, FileNotFoundError):
            return False

    @staticmethod
    def _map_severity(severity: str) -> str:
        """Map external severity levels to our severity levels"""
        severity = severity.lower()
        if severity in ['critical', 'high', 'medium', 'low']:
            return severity
        if severity in ['error', 'severe']:
            return 'critical'
        if severity in ['warning', 'moderate']:
            return 'medium'
        if severity in ['info', 'minor']:
            return 'low'
        return 'medium'

    @staticmethod
    def _map_bandit_severity(severity: str) -> str:
        """Map bandit severity to our severity levels"""
        severity = severity.upper()
        mapping = {
            'HIGH': 'high',
            'MEDIUM': 'medium',
            'LOW': 'low',
        }
        return mapping.get(severity, 'medium')


class CVELookup:
    """
    Lookup CVE information from external databases
    """

    @staticmethod
    def lookup_cve(cve_id: str) -> Optional[Dict]:
        """
        Look up CVE information from NVD database

        Args:
            cve_id: CVE identifier (e.g., CVE-2024-1234)

        Returns:
            dict: CVE information or None
        """
        try:
            import requests

            url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Extract relevant information
                return {
                    'id': cve_id,
                    'description': data.get('description', ''),
                    'severity': data.get('severity', 'unknown'),
                    'published_date': data.get('publishedDate', ''),
                    'references': data.get('references', []),
                }

        except Exception as e:
            logger.error(f"CVE lookup failed for {cve_id}: {e}")

        return None

    @staticmethod
    def lookup_pypi_vulnerabilities(package_name: str) -> List[Dict]:
        """
        Look up known vulnerabilities for a PyPI package

        Args:
            package_name: Name of the PyPI package

        Returns:
            list: List of vulnerabilities
        """
        vulnerabilities = []

        try:
            import requests

            # Use PyPI JSON API
            url = f"https://pypi.org/pypi/{package_name}/json"
            response = requests.get(url, timeout=10)

            if response.status_code == 200:
                data = response.json()
                # Check for vulnerability information
                # Note: PyPI doesn't directly provide vulnerability data
                # This would need integration with safety-db or similar

        except Exception as e:
            logger.error(f"PyPI lookup failed for {package_name}: {e}")

        return vulnerabilities
