"""
Global state for repository concatenator tool.

In production, this should use Redis/cache instead of module-level dict.
"""

# Store temp paths for cleanup
_temp_repos = {}
