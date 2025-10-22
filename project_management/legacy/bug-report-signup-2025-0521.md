# Bug Report: Signup Functionality Not Working

## Issue Description
The "Sign Up" button on the SciTeX website leads to a non-existent page. Although the backend API for registration is implemented, there is no corresponding frontend component to allow users to complete the signup process.

## Severity
**Critical** - New users cannot create accounts, blocking access to the platform's functionality.

## Steps to Reproduce
1. Visit the SciTeX homepage
2. Click on "Sign Up" or "Sign Up Free" button in the header
3. Result: No signup page is displayed, or a 404 error occurs

## Expected Behavior
Clicking the "Sign Up" button should direct users to a registration form where they can enter their information (username, email, password) to create a new account.

## Actual Behavior
The button directs to a URL (/signup) that has no corresponding route defined in the application, resulting in a 404 error or no response.

## Technical Analysis

### Root Causes
1. **Missing URL Route**: No URL path defined for `/signup/` in `urls.py`
2. **Missing View Function**: No view function to render a signup page in `views.py`
3. **Missing Template**: No HTML template for the signup form
4. **Missing Frontend Logic**: No JavaScript code to handle form submission to the API endpoint

### Existing Components
- Backend API for registration exists at `/api/v1/auth/register/` (implemented in `api.py`)
- User authentication system is properly configured in Django settings
- User and UserProfile models are correctly defined

## Proposed Solution

### 1. Create a Signup Template
Create a new template file at `src/scitex_web/templates/scitex_web/signup.html` with a registration form that collects:
- Username
- Email
- Password
- First name (optional)
- Last name (optional)

### 2. Add a View Function
Add the following function to `views.py`:

```python
def signup(request):
    """Signup page view"""
    return render(request, 'scitex_web/signup.html', {
        'title': 'Create an Account',
    })
```

### 3. Add URL Route
Add the following path to `urls.py`:

```python
path('signup/', views.signup, name='signup'),
```

### 4. Add Frontend JavaScript
Create a JavaScript file `static/js/signup.js` to handle form submission via AJAX to the `/api/v1/auth/register/` endpoint.

### 5. Update Navigation Links
Ensure all "Sign Up" buttons link to the correct URL using the Django URL tag:

```html
<a href="{% url 'signup' %}" class="btn btn-sm btn-secondary">Sign Up</a>
```

## Additional Notes
- The backend API for registration appears to be correctly implemented, with proper validation, user creation, and error handling.
- The issue is solely with the frontend implementation.
- We should also create a login page with a similar pattern.

## Related Issues
- "Log In" button may have the same issue (no corresponding page)

## Assigned To
Not yet assigned

## Priority
High - This is a critical user acquisition path

---

Date: May 21, 2025  
Reported by: SciTeX Development Team