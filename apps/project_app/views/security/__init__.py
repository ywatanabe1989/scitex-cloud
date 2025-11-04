"""
Security feature views
GitHub-style security features for SciTeX projects
"""

from .overview import security_overview
from .alerts import (
    security_alerts,
    security_alert_detail,
    dismiss_alert,
    reopen_alert,
    create_fix_pr,
)
from .scan import security_scan_history, trigger_security_scan
from .advisories import security_advisories, security_advisory_detail
from .dependency import security_dependency_graph, api_dependency_tree
from .policy import security_policy

__all__ = [
    # Overview
    'security_overview',

    # Alerts
    'security_alerts',
    'security_alert_detail',
    'dismiss_alert',
    'reopen_alert',
    'create_fix_pr',

    # Scan
    'security_scan_history',
    'trigger_security_scan',

    # Advisories
    'security_advisories',
    'security_advisory_detail',

    # Dependency
    'security_dependency_graph',
    'api_dependency_tree',

    # Policy
    'security_policy',
]
