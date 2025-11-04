# View Migration Plan - base_views.py Split

## Target Structure (Following writer_app)

```
views/
├── __init__.py                  # Export all views
├── project_views.py            # ~800 lines - Project CRUD + detail
├── collaboration_views.py      # ~400 lines - Invitations, members
├── settings_views.py           # ~600 lines - Settings + POST handlers
├── directory_views.py          # ~800 lines - File browser, commits
├── api_views.py                # ~400 lines - REST APIs
└── legacy_base_views.py        # Keep original for reference
```

## Functions to Move

### collaboration_views.py
- project_collaborate (L1022)
- project_members (1029)
- accept_invitation (2808)
- decline_invitation (2846)

### settings_views.py
- project_settings (L811) - Main settings view + ALL POST handlers

### project_views.py
- project_list (L37)
- user_profile (L42)
- user_project_list (L76)
- user_bio_page (L130)
- project_detail (L159) - LARGE, includes mode routing
- project_create (L366)
- project_create_from_template (L742)
- project_edit (L779)
- project_delete (L982)
- user_overview (L2374)
- user_projects_board (L2408)
- user_stars (L2435)
- project_detail_redirect (L1616)

### directory_views.py
- project_directory_dynamic (L1640)
- project_directory (L2201)
- project_file_view (L1843)
- file_history_view (L2475)
- commit_detail (L2642)
- _detect_language (L1776) - utility

### api_views.py
- api_file_tree (L1096)
- api_check_name_availability (L1177)
- api_project_list (L1256)
- api_project_create (L1266)
- api_concatenate_directory (L1300)
- api_project_detail (L1425)
- api_repository_health (L1443)
- api_repository_cleanup (L1478)
- api_repository_sync (L1521)
- api_repository_restore (L1564)

### integration_views.py (or keep in project_views)
- github_integration (L1075)
- repository_maintenance (L1050)

## Import Strategy

Each new file needs:
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.models import User
from apps.project_app.models import Project, ProjectMembership
from ..decorators import project_access_required, project_required
import logging

logger = logging.getLogger(__name__)
```

## Testing After Each Split

After creating each new view file:
1. Run server - check for import errors
2. Test one view from that file
3. Commit if working
4. Move to next file

<!-- EOF -->
