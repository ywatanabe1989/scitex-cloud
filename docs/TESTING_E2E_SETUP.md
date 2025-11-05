# E2E Testing Setup with Playwright

## Overview

This document describes the End-to-End (E2E) testing infrastructure for SciTeX Cloud using Playwright.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     E2E Testing Setup                        │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐       ┌──────────────┐                    │
│  │   Host       │       │   Docker     │                    │
│  │   Machine    │       │   Container  │                    │
│  ├──────────────┤       ├──────────────┤                    │
│  │              │       │              │                    │
│  │  pytest      │──────▶│  Django      │                    │
│  │  playwright  │ HTTP  │  Server      │                    │
│  │  (Chromium)  │       │  :8000       │                    │
│  │              │       │              │                    │
│  └──────────────┘       └──────────────┘                    │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

## Quick Start

### 1. Install Dependencies (Host)

```bash
# Activate virtual environment
source .venv/bin/activate

# Install testing dependencies
pip install pytest-playwright pytest-base-url

# Install Playwright browsers
python -m playwright install chromium
```

### 2. Start Development Server

```bash
# Start development environment with Docker
make ENV=dev start
```

### 3. Run E2E Tests

```bash
# Run all E2E tests
pytest tests/e2e/ -v

# Run specific test
pytest tests/e2e/test_user_creation.py -v

# Run with browser visible (headed mode)
pytest tests/e2e/ -v --headed

# Run with slow motion for debugging
pytest tests/e2e/ -v --headed --slowmo 1000
```

## Test Structure

```
tests/
├── conftest.py                    # Pytest configuration and fixtures
├── e2e/
│   ├── __init__.py
│   └── test_user_creation.py      # User registration E2E tests
└── screenshots/                   # Test screenshots (auto-generated)
    ├── before_signup_*.png
    ├── after_signup_*.png
    └── test_complete_*.png
```

## Available Tests

### User Registration Flow (`test_user_creation.py`)

#### 1. Complete Registration Flow
- **Test**: `test_user_registration_complete_flow`
- **Steps**:
  1. Navigate to signup page
  2. Fill registration form
  3. Submit and verify redirect
  4. Test login with new credentials
  5. Verify access to protected pages
  6. Test logout functionality
- **Duration**: ~30-45 seconds

#### 2. Form Validation
- **Test**: `test_user_registration_validation`
- **Steps**:
  1. Test empty fields submission
  2. Test invalid email format
  3. Test password mismatch
- **Duration**: ~15-20 seconds

## Configuration

### pytest.ini

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*

addopts =
    --verbose
    --strict-markers
    --tb=short
    --capture=no
    --headed                        # Show browser
    --browser chromium
    --slowmo 100                    # 100ms delay between actions
    --video retain-on-failure       # Record video on failure
    --screenshot only-on-failure    # Screenshot on failure

markers =
    e2e: End-to-end tests using browser automation
    slow: Tests that take a long time to run
    auth: Authentication and authorization tests
    user: User management tests
    integration: Integration tests
```

### Environment Variables

```bash
# Base URL for tests
BASE_URL=http://127.0.0.1:8000

# Django settings
DJANGO_SETTINGS_MODULE=config.settings.settings_dev
```

## Fixtures

### Available Fixtures

- **`base_url`**: Base URL for the application (default: http://127.0.0.1:8000)
- **`browser_context_args`**: Browser context configuration (viewport, locale, etc.)
- **`context`**: New browser context for each test (isolation)
- **`page`**: New page for each test with console/error logging
- **`test_user_data`**: Generated test user data with unique timestamp
- **`timestamp`**: Unique timestamp for test data generation
- **`cleanup_test_users`**: Auto-cleanup test users after all tests

### Example Usage

```python
def test_example(page: Page, base_url: str, test_user_data: dict):
    """Example test using fixtures."""
    page.goto(f"{base_url}/auth/signup/")
    page.locator('input[name="username"]').fill(test_user_data['username'])
    # ... rest of test
```

## CI/CD Integration

### GitHub Actions Example

```yaml
name: E2E Tests

on: [push, pull_request]

jobs:
  e2e-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          python -m playwright install --with-deps chromium

      - name: Start services
        run: |
          make ENV=dev start
          # Wait for server to be ready
          timeout 60 bash -c 'until curl -f http://127.0.0.1:8000/health; do sleep 1; done'

      - name: Run E2E tests
        run: |
          pytest tests/e2e/ -v --browser chromium

      - name: Upload screenshots
        if: failure()
        uses: actions/upload-artifact@v3
        with:
          name: test-screenshots
          path: tests/screenshots/
```

## Docker Integration (Professional Setup)

For production-quality testing, integrate E2E tests into Docker:

### Option 1: Run Tests from Host (Current Setup)

**Pros:**
- ✅ Fast iteration during development
- ✅ Easy debugging with browser visible
- ✅ No need to rebuild Docker for test changes

**Cons:**
- ❌ Not isolated (depends on host environment)
- ❌ Requires manual dependency installation on each machine

### Option 2: Run Tests in Docker (Recommended for CI/CD)

**Pros:**
- ✅ Completely isolated environment
- ✅ Same environment for all developers and CI/CD
- ✅ Dependencies bundled in Docker image

**Cons:**
- ❌ Slower iteration (need to rebuild for changes)
- ❌ Debugging slightly more complex

### Recommended Hybrid Approach

1. **Development**: Run from host for fast iteration
2. **CI/CD**: Run in Docker for consistency
3. **Pre-commit**: Quick smoke tests from host
4. **Full test suite**: Docker-based in CI/CD pipeline

## Debugging Tips

### 1. Visual Debugging

```bash
# Run with browser visible and slow motion
pytest tests/e2e/ -v --headed --slowmo 1000
```

### 2. Interactive Debugging

```python
# Add breakpoint in test
def test_example(page: Page):
    page.goto("http://127.0.0.1:8000/")
    page.pause()  # Opens Playwright Inspector
    # ... rest of test
```

### 3. Console Logs

The test automatically captures browser console logs:

```python
# In conftest.py
page.on("console", lambda msg: print(f"[BROWSER {msg.type}] {msg.text}"))
page.on("pageerror", lambda err: print(f"[PAGE ERROR] {err}"))
```

### 4. Screenshots

Screenshots are automatically taken:
- Before form submission
- After form submission
- After login
- On test completion
- On test failure (via pytest config)

## Test Data Management

### User Cleanup

Test users are automatically cleaned up after all tests complete:

```python
# Cleanup happens in conftest.py
@pytest.fixture(scope="session", autouse=True)
def cleanup_test_users():
    yield
    # Cleanup test users after tests
    User.objects.filter(username__startswith="test_user_").delete()
```

### Unique Test Data

Each test generates unique data using timestamps:

```python
@pytest.fixture
def test_user_data(timestamp):
    return {
        "username": f"test_user_{timestamp}",
        "email": f"test_{timestamp}@example.com",
        "password": "TestPass123!",
    }
```

## Troubleshooting

### Issue: Tests time out on signup page

**Solution**: Verify Django server is running
```bash
curl http://127.0.0.1:8000/auth/signup/
```

### Issue: Database connection errors

**Cause**: Tests running from host cannot connect to Docker's "db" hostname

**Solution**: Database cleanup is automatically skipped when running from host

### Issue: Browser not found

**Solution**: Install Playwright browsers
```bash
python -m playwright install chromium
```

### Issue: Screenshots not saved

**Solution**: Create screenshots directory
```bash
mkdir -p tests/screenshots
```

## Best Practices

1. **Test Isolation**: Each test gets fresh browser context
2. **Unique Data**: Use timestamps to avoid conflicts
3. **Explicit Waits**: Use `page.wait_for_load_state()` instead of `time.sleep()`
4. **Screenshots**: Take screenshots at key points for debugging
5. **Cleanup**: Always cleanup test data
6. **Error Handling**: Catch and log browser errors
7. **Page Objects**: For larger test suites, use Page Object pattern

## Future Enhancements

- [ ] Add Page Object pattern for better maintainability
- [ ] Add visual regression testing
- [ ] Add performance testing metrics
- [ ] Add API mocking for faster tests
- [ ] Add parallel test execution
- [ ] Add test coverage reporting
- [ ] Integrate with Docker for CI/CD

## Resources

- [Playwright Documentation](https://playwright.dev/python/)
- [pytest Documentation](https://docs.pytest.org/)
- [pytest-playwright Plugin](https://github.com/microsoft/playwright-pytest)
