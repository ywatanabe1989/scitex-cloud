<!-- ---
!-- Timestamp: 2025-11-30 19:13:24
!-- Author: ywatanabe
!-- File: /home/ywatanabe/proj/scitex-cloud/tests/README.md
!-- --- -->

# SciTeX Test Suite

## Directory Structure

```
tests/
├── README.md                    # This file
├── conftest.py                  # Shared fixtures (auth, db, browser)
├── run_tests.sh                 # Test runner script
│
├── e2e/                         # End-to-End Tests (Playwright)
│   ├── conftest.py              # E2E-specific fixtures
│   ├── auth/                    # Authentication flows
│   │   ├── test_signup.py       # User registration + email verification
│   │   ├── test_login.py        # Login/logout flows
│   │   ├── test_password_reset.py
│   │   └── test_account_switch.py
│   ├── project/                 # Project management
│   │   ├── test_project_crud.py # Create, read, update, delete
│   │   ├── test_file_tree.py    # File browser operations
│   │   ├── test_file_edit.py    # File editing via UI
│   │   └── test_collaboration.py
│   ├── scholar/                 # Scholar app
│   │   ├── test_paper_search.py # Search across sources
│   │   ├── test_bibtex_upload.py
│   │   ├── test_bibtex_enrichment.py
│   │   └── test_library.py
│   ├── writer/                  # Writer app
│   │   ├── test_editor.py       # LaTeX editing
│   │   ├── test_compilation.py  # PDF compilation
│   │   └── test_collaboration.py
│   ├── code/                    # Code execution
│   │   ├── test_notebook.py
│   │   └── test_execution.py
│   └── vis/                     # Visualization
│       └── test_graph_editor.py
│
├── api/                         # API Tests (Django REST)
│   ├── conftest.py              # API client fixtures
│   ├── auth/
│   │   ├── test_auth_api.py     # Login, token, verification APIs
│   │   └── test_api_keys.py     # API key management
│   ├── project/
│   │   ├── test_project_api.py  # Project CRUD API
│   │   ├── test_file_api.py     # File operations API
│   │   └── test_git_api.py      # Git operations API
│   ├── scholar/
│   │   ├── test_search_api.py   # Paper search API
│   │   ├── test_bibtex_api.py   # BibTeX upload/enrichment API
│   │   └── test_library_api.py  # Library management API
│   └── permissions/
│       └── test_permissions_api.py
│
├── unit/                        # Unit Tests (Fast, isolated)
│   ├── models/                  # Model validation
│   │   ├── test_user_models.py
│   │   ├── test_project_models.py
│   │   ├── test_scholar_models.py
│   │   └── test_code_models.py
│   ├── forms/                   # Form validation
│   │   ├── test_auth_forms.py
│   │   └── test_project_forms.py
│   ├── utils/                   # Utility functions
│   │   ├── test_bibtex_parser.py
│   │   ├── test_citation_formatter.py
│   │   └── test_git_utils.py
│   └── services/                # Business logic
│       ├── test_gitea_service.py
│       └── test_search_service.py
│
├── integration/                 # Integration Tests
│   ├── conftest.py              # Integration fixtures
│   ├── test_gitea.py            # Gitea API integration
│   ├── test_paper_sources.py    # ArXiv, PubMed, CrossRef
│   ├── test_celery_tasks.py     # Async task execution
│   ├── test_websockets.py       # Real-time features
│   └── test_email.py            # Email service
│
└── fixtures/                    # Test data
    ├── users.json
    ├── projects.json
    ├── sample.bib
    └── sample_paper.json
```

---

## Test Categories & Priority

### Phase 1: Critical Path (Week 1-2)

| Category | Tests | Priority |
|----------|-------|----------|
| `e2e/auth/` | Signup, login, password reset | CRITICAL |
| `api/auth/` | Auth APIs, API keys | CRITICAL |
| `unit/models/test_user_models.py` | User/Profile validation | HIGH |

### Phase 2: Core Features (Week 3-4)

| Category | Tests | Priority |
|----------|-------|----------|
| `e2e/project/` | Project CRUD, file operations | CRITICAL |
| `api/project/` | Project & file APIs | CRITICAL |
| `integration/test_gitea.py` | Gitea sync | HIGH |

### Phase 3: Scholar App (Week 5-6)

| Category | Tests | Priority |
|----------|-------|----------|
| `e2e/scholar/` | Search, BibTeX, library | HIGH |
| `api/scholar/` | Scholar APIs | HIGH |
| `integration/test_paper_sources.py` | External APIs | MEDIUM |

### Phase 4: Advanced Features (Week 7-8)

| Category | Tests | Priority |
|----------|-------|----------|
| `e2e/writer/` | LaTeX editor, compilation | HIGH |
| `e2e/code/` | Notebooks, execution | MEDIUM |
| `integration/test_websockets.py` | Real-time collaboration | MEDIUM |

---

## Running Tests

```bash
# All tests
./tests/run_tests.sh

# E2E tests only (requires running server at 127.0.0.1:8000)
pytest tests/e2e/ -v

# API tests only
pytest tests/api/ -v

# Unit tests only (fast, no server needed)
pytest tests/unit/ -v

# Specific test file
pytest tests/e2e/auth/test_login.py -v

# With coverage
pytest tests/ --cov=apps --cov-report=html
```

---

## Test Fixtures

### Shared Fixtures (conftest.py)

```python
# Authentication
@pytest.fixture
def test_user          # Creates test user
@pytest.fixture
def authenticated_page # Logged-in browser page
@pytest.fixture
def api_client         # Authenticated API client

# Data
@pytest.fixture
def test_project       # Creates test project
@pytest.fixture
def sample_bibtex      # Sample BibTeX content
```

### E2E Fixtures

```python
@pytest.fixture
def page               # Fresh browser page
@pytest.fixture
def logged_in_page     # Page with test-user logged in
```

---

## Writing Tests

### E2E Test Example

```python
# tests/e2e/auth/test_login.py
import pytest
from playwright.sync_api import Page, expect

def test_login_success(page: Page, base_url: str):
    """User can login with valid credentials."""
    page.goto(f"{base_url}/auth/signin/")
    page.fill("#username", "test-user")
    page.fill("#password", "Password123!")
    page.click("button[type='submit']")

    expect(page).to_have_url(f"{base_url}/")
    expect(page.locator("body")).to_have_attribute(
        "data-user-authenticated", "true"
    )
```

### API Test Example

```python
# tests/api/project/test_project_api.py
import pytest
from django.test import Client

def test_create_project(authenticated_client, test_user):
    """API creates project successfully."""
    response = authenticated_client.post(
        "/api/projects/create/",
        {"name": "test-project", "description": "Test"},
        content_type="application/json"
    )
    assert response.status_code == 201
    assert response.json()["name"] == "test-project"
```

### Unit Test Example

```python
# tests/unit/utils/test_bibtex_parser.py
import pytest
from apps.scholar_app.utils.bibtex import parse_bibtex

def test_parse_valid_bibtex():
    """Parser extracts fields from valid BibTeX."""
    content = '@article{key, title={Test}, author={Author}}'
    result = parse_bibtex(content)
    assert result[0]["title"] == "Test"
```

---

## Coverage Targets

| Category | Target | Current |
|----------|--------|---------|
| `auth_app` | 80% | ~20% |
| `accounts_app` | 80% | ~15% |
| `project_app` | 70% | ~5% |
| `scholar_app` | 70% | ~10% |
| `code_app` | 60% | ~5% |
| `writer_app` | 60% | ~5% |
| **Overall** | **70%** | **~10%** |

---

## CI/CD Integration

Tests run automatically on:
- Pull request creation
- Push to `develop` or `main`
- Nightly schedule (full suite)

```yaml
# .github/workflows/tests.yml (example)
- name: Run Unit Tests
  run: pytest tests/unit/ -v --tb=short

- name: Run Integration Tests
  run: pytest tests/integration/ -v --tb=short

- name: Run E2E Tests
  run: pytest tests/e2e/ -v --tb=short
```

---

## Notes

- Files prefixed with `_` (e.g., `_test_api.py`) are **disabled/legacy**
- E2E tests require dev server running: `make ENV=dev restart`
- Test user: `test-user` / `Password123!`
- Environment: `.env.dev` loaded automatically

<!-- EOF -->
