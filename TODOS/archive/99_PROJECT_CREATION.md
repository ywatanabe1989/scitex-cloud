<!-- ---
!-- Timestamp: 2025-10-18 23:08:50
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/TODOS/PROJECT_CREATION.md
!-- --- -->

## RESOLVED: Template Initialization During Project Creation

### Original Issue
- [x] Created test repository
  - [x] http://127.0.0.1:8000/ywatanabe/test/
  - [x] The README.md mentioned "Create from template" button
  - [x] Button was only available AFTER project creation (in empty project view)
  - [x] Should be available DURING project creation

### Solution Implemented
- [x] Added checkbox option to project creation form
  - Label: "Initialize with SciTeX template structure"
  - Help text explains what the template includes
- [x] Updated `project_create` view to handle template initialization
  - Checks `initialize_template` POST parameter
  - Calls `manager.create_project_from_template(project)` if checked
  - Shows appropriate success/warning messages
- [x] Template initialization now happens during project creation workflow

### UX Flow Now
1. User fills out project creation form
2. User can optionally check "Initialize with SciTeX template structure"
3. If checked, project is created WITH template structure immediately
4. If unchecked, empty project is created (can still use "Create from Template" button later)

### Files Modified
- `/apps/project_app/templates/project_app/project_create.html` - Added checkbox and dynamic template selector
- `/apps/project_app/views.py` - Updated `project_create()` to handle template init and type selection
- `/home/ywatanabe/proj/scitex-code/src/scitex/template/__init__.py` - Added `get_available_templates_info()`
- `/apps/core_app/directory_manager.py` - Added template_type support

## Additional Improvements (2025-10-18)

### Issue 1: Repository Name Validation ✅ FIXED
**Problem:** System created `test_2` instead of showing error for duplicate name
**Solution:**
- Removed auto-suffix behavior in `project_create()` view
- Added duplicate name check before project creation
- Shows error message: "You already have a project named 'X'. Please choose a different name."
- User must manually choose different name

### Issue 2: Template Files Not Created ✅ FIXED
**Problem:** Checkbox checked but files not created
**Root Cause:** View was calling `ensure_project_directory()` (creates empty) then `create_project_from_template()` separately
**Solution:**
- Updated `project_create()` view to pass `template_type` directly to `create_project_directory()`
- Updated `create_project_directory()` method to accept `template_type` parameter
- Now properly uses `_copy_from_example_template(project_path, project, template_type)`
- Template files now created on first project creation

### Feature: Dynamic Template Selection
- Template dropdown populated from `scitex.template.get_available_templates_info()`
- Shows 3 templates: Research, Python Package, Singularity
- Interactive UI showing:
  - Template name and description
  - Use case
  - Features list
  - GitHub repository link
- Automatically updates when new templates added to scitex package

### Feature: Real-Time Name Availability Check ✅
- AJAX endpoint: `/project/api/check-name/`
- Debounced checking (500ms after typing stops)
- Visual feedback:
  - ⏳ "Checking availability..."
  - ✓ "name is available" (green)
  - ✗ "You already have a project named 'X'" (red)
- Prevents duplicate project names before form submission

### Feature: Git Repository Cloning ✅
- New initialization option: "Clone from Git repository"
- Works with any Git hosting service:
  - GitHub: `https://github.com/user/repo.git`
  - GitLab: `https://gitlab.com/user/repo.git`
  - Bitbucket: `https://bitbucket.org/user/repo.git`
  - Self-hosted Git servers
- Supports both HTTPS and SSH URLs
- Automatic SSH key usage if configured
- 5-minute timeout for large repositories

### Feature: SSH Key Management ✅
**Location:** `/settings/ssh-keys/`

**Functionality:**
- Generate 4096-bit RSA SSH keys per user
- Automatic key generation with secure permissions (0o600)
- Display public key with copy button
- Show key fingerprint (SHA256)
- Track creation and last usage timestamps
- Delete and regenerate keys
- Instructions for GitHub/GitLab/Bitbucket integration

**Implementation:**
- Models: `profile_app/models.py` - SSH key fields in UserProfile
- Manager: `core_app/ssh_manager.py` - SSHKeyManager class
- Views: `profile_app/views.py` - ssh_keys() view
- Template: `profile_app/templates/profile_app/ssh_keys.html`
- Integration: Git clone automatically uses SSH if key exists

### Feature: API Key Management ✅
**Location:** `/settings/api-keys/`

**Functionality:**
- Generate secure API keys with `scitex_` prefix
- Keys shown ONCE after creation (security best practice)
- Key format: `scitex_{64-char-hex}`
- Stored as SHA256 hash (never plain text)
- Per-key permissions/scopes:
  - Full Access (*)
  - project:read, project:write
  - scholar:read
- Activate/deactivate keys
- Delete keys
- Track usage with last_used_at timestamps
- Optional expiration dates

**Implementation:**
- Model: `profile_app/models.py` - APIKey model
- Views: `profile_app/views.py` - api_keys() view
- Template: `profile_app/templates/profile_app/api_keys.html`
- Usage examples for curl and Python

### Files Modified/Created (Complete List)
**Models:**
- `apps/profile_app/models.py` - Added SSH fields to UserProfile, created APIKey model

**Managers/Utilities:**
- `apps/core_app/ssh_manager.py` - NEW: SSHKeyManager class
- `apps/core_app/directory_manager.py` - Updated clone_from_git() with SSH support

**Views:**
- `apps/profile_app/views.py` - Added ssh_keys(), api_keys(), api_generate_ssh_key()
- `apps/project_app/views.py` - Updated project_create() with Git cloning, api_check_name_availability()

**URLs:**
- `apps/profile_app/urls.py` - Added /settings/ssh-keys/, /settings/api-keys/
- `apps/project_app/urls.py` - Added /api/check-name/

**Templates:**
- `apps/project_app/templates/project_app/project_create.html` - Added init options, name checking
- `apps/profile_app/templates/profile_app/ssh_keys.html` - NEW
- `apps/profile_app/templates/profile_app/api_keys.html` - NEW

**External:**
- `/home/ywatanabe/proj/scitex-code/src/scitex/template/__init__.py` - Added get_available_templates_info()

**Documentation:**
- `docs/SSH_KEY_MANAGEMENT_DESIGN.md` - NEW: Complete architecture documentation

<!-- EOF -->