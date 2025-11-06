# Partials Analysis - Phase 4 Complete

**Date:** 2025-11-04
**Total Include Statements:** 121
**Current Partial Directories:** 5 (partials/, browse/partials/, pull_requests/partials/, security/partials/, actions/partials/)

---

## Ownership Mapping

### 1. browse.html → browse_partials/

**From `browse/partials/`:**
- `_project_header.html` → `browse_header.html`
- `_repo_tabs.html` → `browse_tabs.html`
- `_project_toolbar.html` → `browse_toolbar.html`
- `_sidebar.html` → `browse_sidebar.html`
- `_project_empty_state.html` → `browse_empty_state.html`
- `_project_file_browser.html` → `browse_file_browser.html`
- `_project_readme.html` → `browse_readme.html`
- `_project_scripts.html` → `browse_scripts.html`
- `_file_list.html` → `browse_file_list.html`

**Note:** These partials are also used by directory_browser.html, issues_list.html, pr_list.html → Will need to update includes to reference browse_partials/

---

### 2. directory_browser.html → directory_browser_partials/

**Reuses from browse_partials/:**
- All browse partials (will reference `browse_partials/xxx.html`)

---

### 3. create.html → create_partials/

**From `partials/`:**
- `create_breadcrumb.html` → `create_breadcrumb.html` (already prefixed ✓)
- `create_description_field.html` → `create_description_field.html` (already prefixed ✓)
- `create_form_actions.html` → `create_form_actions.html` (already prefixed ✓)
- `create_name_field.html` → `create_name_field.html` (already prefixed ✓)
- `project_create_init_options.html` → `create_init_options.html` (rename)
- `project_create_scripts.html` → `create_scripts.html` (rename)

---

### 4. delete.html → delete_partials/

**From `partials/`:**
- `delete_breadcrumb.html` → `delete_breadcrumb.html` (already prefixed ✓)
- `delete_confirmation_form.html` → `delete_confirmation_form.html` (already prefixed ✓)
- `delete_confirmation_script.html` → `delete_confirmation_script.html` (already prefixed ✓)
- `delete_consequences_list.html` → `delete_consequences_list.html` (already prefixed ✓)
- `delete_project_info.html` → `delete_project_info.html` (already prefixed ✓)
- `delete_warning_box.html` → `delete_warning_box.html` (already prefixed ✓)

---

### 5. edit.html → edit_partials/

**From `partials/`:**
- `edit_breadcrumb.html` → `edit_breadcrumb.html` (already prefixed ✓)
- `edit_description_field.html` → `edit_description_field.html` (already prefixed ✓)
- `edit_form_actions.html` → `edit_form_actions.html` (already prefixed ✓)
- `edit_name_field.html` → `edit_name_field.html` (already prefixed ✓)
- `edit_source_url_field.html` → `edit_source_url_field.html` (already prefixed ✓)

---

### 6. list.html → list_partials/

**From `partials/`:**
- `list_create_form.html` → `list_create_form.html` (already prefixed ✓)
- `list_empty_state.html` → `list_empty_state.html` (already prefixed ✓)
- `list_pagination.html` → `list_pagination.html` (already prefixed ✓)
- `list_project_card.html` → `list_project_card.html` (already prefixed ✓)

---

### 7. settings.html → settings_partials/

**From `partials/`:**
- `settings_navigation.html` → `settings_navigation.html` (already prefixed ✓)
- `settings_general.html` → `settings_general.html` (already prefixed ✓)
- `settings_visibility.html` → `settings_visibility.html` (already prefixed ✓)
- `settings_collaborators.html` → `settings_collaborators.html` (already prefixed ✓)
- `settings_danger_zone.html` → `settings_danger_zone.html` (already prefixed ✓)
- `settings_delete_modal.html` → `settings_delete_modal.html` (already prefixed ✓)

---

### 8. file_view.html → file_view_partials/

**From `partials/`:**
- `_file_view_breadcrumb.html` → `file_view_breadcrumb.html` (remove underscore)
- `_file_view_content_binary.html` → `file_view_content_binary.html` (remove underscore)
- `_file_view_content_code.html` → `file_view_content_code.html` (remove underscore)
- `_file_view_content_image.html` → `file_view_content_image.html` (remove underscore)
- `_file_view_content_markdown.html` → `file_view_content_markdown.html` (remove underscore)
- `_file_view_content_pdf.html` → `file_view_content_pdf.html` (remove underscore)
- `_file_view_content_text.html` → `file_view_content_text.html` (remove underscore)
- `_file_view_header.html` → `file_view_header.html` (remove underscore)
- `_file_view_pdf_scripts.html` → `file_view_pdf_scripts.html` (remove underscore)
- `_file_view_scripts.html` → `file_view_scripts.html` (remove underscore)
- `_file_view_tabs.html` → `file_view_tabs.html` (remove underscore)

**Reuses from browse_partials/:**
- `_sidebar.html` → Will reference `browse_partials/browse_sidebar.html`

---

### 9. file_history.html → file_history_partials/

**From `partials/`:**
- `history_header.html` → `file_history_header.html` (add prefix)
- `history_filter_bar.html` → `file_history_filter_bar.html` (add prefix)
- `commit_list_item.html` → `file_history_commit_item.html` (add prefix)
- `history_pagination.html` → `file_history_pagination.html` (add prefix)

---

### 10. file_directory.html → file_directory_partials/

**From `partials/`:**
- `_breadcrumb.html` → `file_directory_breadcrumb.html` (add prefix, remove underscore)
- `_file_list.html` → `file_directory_file_list.html` (add prefix, remove underscore)
- `_scripts.html` → `file_directory_scripts.html` (add prefix, remove underscore)
- `_sidebar.html` → `file_directory_sidebar.html` (add prefix, remove underscore)
- `_tab_navigation.html` → `file_directory_tabs.html` (add prefix, remove underscore)
- `_toolbar.html` → `file_directory_toolbar.html` (add prefix, remove underscore)

---

### 11. commit_detail.html → commit_detail_partials/

**From `partials/`:**
- `commit_detail_file_diff.html` → `commit_detail_file_diff.html` (already prefixed ✓)
- `commit_detail_header.html` → `commit_detail_header.html` (already prefixed ✓)

---

### 12. pr_detail.html → pr_detail_partials/

**From `pull_requests/partials/`:**
- `_pr_breadcrumb.html` → `pr_detail_breadcrumb.html` (remove underscore, adjust prefix)
- `_pr_header.html` → `pr_detail_header.html` (remove underscore, adjust prefix)
- `_pr_tabs.html` → `pr_detail_tabs.html` (remove underscore, adjust prefix)
- `_pr_sidebar.html` → `pr_detail_sidebar.html` (remove underscore, adjust prefix)
- `_pr_merge_modal.html` → `pr_detail_merge_modal.html` (remove underscore, adjust prefix)
- `pr_conversation.html` → `pr_detail_conversation.html` (adjust prefix)
- `pr_commits.html` → `pr_detail_commits.html` (adjust prefix)
- `pr_diff.html` → `pr_detail_diff.html` (adjust prefix)
- `pr_checks.html` → `pr_detail_checks.html` (adjust prefix)

---

### 13. pr_list.html → pr_list_partials/

**From `pull_requests/partials/`:**
- `_pr_list_empty.html` → `pr_list_empty.html` (remove underscore)
- `_pr_list_filters.html` → `pr_list_filters.html` (remove underscore)
- `_pr_list_items.html` → `pr_list_items.html` (remove underscore)
- `_pr_list_pagination.html` → `pr_list_pagination.html` (remove underscore)
- `_pr_list_search.html` → `pr_list_search.html` (remove underscore)

**Reuses from browse_partials/:**
- `_project_header.html`, `_repo_tabs.html`, `_project_scripts.html` → Will reference `browse_partials/xxx.html`

---

### 14. security_overview.html → security_overview_partials/

**From `security/partials/`:**
- `_security_tabs.html` → `security_overview_tabs.html` (add prefix, remove underscore)
- `_security_alerts_card.html` → `security_overview_alerts_card.html` (add prefix, remove underscore)
- `_security_scans_card.html` → `security_overview_scans_card.html` (add prefix, remove underscore)
- `_security_stats.html` → `security_overview_stats.html` (add prefix, remove underscore)

**Reuses from browse_partials/:**
- `_project_header.html`, `_repo_tabs.html` → Will reference `browse_partials/xxx.html`

---

### 15. security_alerts.html → security_alerts_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`
- `security_overview_partials/security_overview_tabs.html`

---

### 16. security_advisories.html → security_advisories_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`
- `security_overview_partials/security_overview_tabs.html`

---

### 17. security_dependency_graph.html → security_dependency_graph_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`
- `security_overview_partials/security_overview_tabs.html`

---

### 18. security_policy.html → security_policy_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`
- `security_overview_partials/security_overview_tabs.html`

---

### 19. security_alert_detail.html → security_alert_detail_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`

---

### 20. security_scan_history.html → security_scan_history_partials/

**Reuses from:**
- `browse_partials/browse_header.html`, `browse_partials/browse_tabs.html`

---

### 21. user_bio.html → user_bio_partials/

**From `partials/`:**
- `user_bio_header.html` → `user_bio_header.html` (already prefixed ✓)
- `user_bio_projects.html` → `user_bio_projects.html` (already prefixed ✓)

---

### 22. user_projects.html → user_projects_partials/

**From `partials/`:**
- `profile_navigation.html` → `user_projects_navigation.html` (adjust prefix)
- `profile_scripts.html` → `user_projects_scripts.html` (adjust prefix)
- `profile_sidebar.html` → `user_projects_sidebar.html` (adjust prefix)
- `repository_list_item.html` → `user_projects_repo_item.html` (add prefix)

---

### 23. workflow_editor.html → workflow_editor_partials/

**From `actions/partials/`:**
- `_workflow_editor_form.html` → `workflow_editor_form.html` (remove underscore)
- `_workflow_templates_sidebar.html` → `workflow_editor_templates_sidebar.html` (adjust name)

**Reuses from browse_partials/:**
- `_project_header.html`, `_repo_tabs.html` → Will reference `browse_partials/xxx.html`

---

### 24. actions_list.html → actions_list_partials/

**Reuses from browse_partials/:**
- `_project_header.html`, `_repo_tabs.html` → Will reference `browse_partials/xxx.html`

---

### 25. workflow_run_detail.html → workflow_run_detail_partials/

**Reuses from browse_partials/:**
- `_project_header.html`, `_repo_tabs.html` → Will reference `browse_partials/xxx.html`

---

## Summary Statistics

### Templates Analyzed: 42

### Partials to Reorganize:
- **partials/**: 66 files → Distribute to specific xxx_partials/
- **browse/partials/**: 26 files → Rename to browse_partials/
- **pull_requests/partials/**: ~10 files → Distribute to pr_detail_partials/ and pr_list_partials/
- **security/partials/**: ~4 files → Move to security_overview_partials/
- **actions/partials/**: ~2 files → Move to workflow_editor_partials/

### Directories to Create: 25
- browse_partials/
- create_partials/
- delete_partials/
- edit_partials/
- list_partials/
- settings_partials/
- file_view_partials/
- file_history_partials/
- file_directory_partials/
- commit_detail_partials/
- pr_detail_partials/
- pr_list_partials/
- security_overview_partials/
- security_alerts_partials/
- security_advisories_partials/
- security_dependency_graph_partials/
- security_policy_partials/
- security_alert_detail_partials/
- security_scan_history_partials/
- user_bio_partials/
- user_projects_partials/
- workflow_editor_partials/
- directory_browser_partials/
- actions_list_partials/
- workflow_run_detail_partials/

### Directories to Remove After Migration:
- partials/
- browse/partials/
- pull_requests/partials/
- security/partials/
- actions/partials/
- browse/ (empty after migration)
- pull_requests/ (empty after migration)
- security/ (empty after migration)
- actions/ (empty after migration)

---

## Phase 4 Complete ✅

Ready to proceed to Phase 5: Create directories and reorganize partials

<!-- EOF -->
