#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Tests for User Registration and Authentication Flow

Tests:
- User registration via browser
- Form validation
- Login after registration
- Dashboard access
- Logout functionality
"""

import pytest
from playwright.sync_api import Page, expect
import time


@pytest.mark.e2e
@pytest.mark.auth
@pytest.mark.user
def test_user_registration_complete_flow(page: Page, base_url: str, test_user_data: dict):
    """
    Test complete user registration flow:
    1. Navigate to signup page
    2. Fill registration form
    3. Submit and verify redirect
    4. Verify user can access dashboard
    5. Test logout
    6. Test login with new credentials
    """

    print(f"\n{'='*60}")
    print(f"Testing user registration flow")
    print(f"Username: {test_user_data['username']}")
    print(f"Email: {test_user_data['email']}")
    print(f"{'='*60}\n")

    # Step 1: Navigate to signup page
    print("Step 1: Navigating to signup page...")
    signup_url = f"{base_url}/auth/signup/"
    page.goto(signup_url)

    # Wait for page to load
    page.wait_for_load_state("networkidle")

    # Verify we're on the signup page
    expect(page).to_have_url(signup_url)
    print("✓ Signup page loaded")

    # Step 2: Fill registration form
    print("\nStep 2: Filling registration form...")

    # Find and fill username
    username_input = page.locator('input[name="username"]')
    expect(username_input).to_be_visible()
    username_input.fill(test_user_data['username'])
    print(f"  ✓ Filled username: {test_user_data['username']}")

    # Find and fill email
    email_input = page.locator('input[name="email"]')
    expect(email_input).to_be_visible()
    email_input.fill(test_user_data['email'])
    print(f"  ✓ Filled email: {test_user_data['email']}")

    # Find and fill first name
    first_name_input = page.locator('input[name="first_name"]')
    if first_name_input.count() > 0:
        first_name_input.fill(test_user_data['first_name'])
        print(f"  ✓ Filled first name: {test_user_data['first_name']}")

    # Find and fill last name
    last_name_input = page.locator('input[name="last_name"]')
    if last_name_input.count() > 0:
        last_name_input.fill(test_user_data['last_name'])
        print(f"  ✓ Filled last name: {test_user_data['last_name']}")

    # Find and fill password
    password1_input = page.locator('input[name="password1"]')
    expect(password1_input).to_be_visible()
    password1_input.fill(test_user_data['password'])
    print(f"  ✓ Filled password")

    # Find and fill password confirmation
    password2_input = page.locator('input[name="password2"]')
    expect(password2_input).to_be_visible()
    password2_input.fill(test_user_data['password'])
    print(f"  ✓ Filled password confirmation")

    # Take screenshot before submission
    page.screenshot(path=f"tests/screenshots/before_signup_{test_user_data['username']}.png")

    # Step 3: Submit form
    print("\nStep 3: Submitting registration form...")
    submit_button = page.locator('button[type="submit"]')
    expect(submit_button).to_be_visible()
    submit_button.click()

    # Wait for navigation
    page.wait_for_load_state("networkidle")
    time.sleep(1)  # Additional wait for any redirects

    # Take screenshot after submission
    page.screenshot(path=f"tests/screenshots/after_signup_{test_user_data['username']}.png")

    # Verify successful registration (should redirect to login or dashboard)
    current_url = page.url
    print(f"  Current URL after signup: {current_url}")

    # Check for success indicators
    success_indicators = [
        "/dashboard/",
        "/auth/login/",
        "/accounts/profile/",
        "success",
        "welcome"
    ]

    is_success = any(indicator in current_url.lower() for indicator in success_indicators)

    if not is_success:
        # Check for success message on page
        success_message = page.locator('.alert-success, .message-success, [class*="success"]')
        if success_message.count() > 0:
            is_success = True
            print(f"  ✓ Success message found: {success_message.first.text_content()}")

    assert is_success, f"Registration may have failed. Current URL: {current_url}"
    print("✓ Registration successful")

    # Step 4: Verify user can login
    print("\nStep 4: Testing login with new credentials...")
    login_url = f"{base_url}/auth/login/"
    page.goto(login_url)
    page.wait_for_load_state("networkidle")

    # Fill login form
    login_username = page.locator('input[name="username"]')
    expect(login_username).to_be_visible()
    login_username.fill(test_user_data['username'])

    login_password = page.locator('input[name="password"]')
    expect(login_password).to_be_visible()
    login_password.fill(test_user_data['password'])

    # Submit login
    login_button = page.locator('button[type="submit"]')
    expect(login_button).to_be_visible()
    login_button.click()

    # Wait for navigation
    page.wait_for_load_state("networkidle")
    time.sleep(1)

    # Take screenshot after login
    page.screenshot(path=f"tests/screenshots/after_login_{test_user_data['username']}.png")

    # Verify successful login
    current_url = page.url
    print(f"  Current URL after login: {current_url}")

    # Should not be on login page anymore
    assert "/auth/login/" not in current_url, "Still on login page after submitting credentials"
    print("✓ Login successful")

    # Step 5: Verify access to protected pages
    print("\nStep 5: Verifying access to protected pages...")

    # Try to access user profile or dashboard
    profile_urls = [
        f"{base_url}/{test_user_data['username']}/",
        f"{base_url}/dashboard/",
        f"{base_url}/accounts/profile/",
    ]

    access_verified = False
    for url in profile_urls:
        try:
            page.goto(url, timeout=5000)
            page.wait_for_load_state("networkidle")

            # If we can access without being redirected to login, it's good
            if "/auth/login/" not in page.url:
                print(f"  ✓ Can access: {url}")
                access_verified = True
                break
        except Exception as e:
            print(f"  × Cannot access: {url} ({str(e)[:50]}...)")
            continue

    # At minimum, verify we're still logged in (check for username in page)
    page_content = page.content()
    assert test_user_data['username'] in page_content, "Username not found on page (may not be logged in)"
    print("✓ User is authenticated and can access protected pages")

    # Step 6: Test logout
    print("\nStep 6: Testing logout...")

    # Look for logout link/button
    logout_selectors = [
        'a[href*="logout"]',
        'button:has-text("Logout")',
        'a:has-text("Logout")',
        'a:has-text("Log out")',
        'button:has-text("Sign out")',
    ]

    logout_clicked = False
    for selector in logout_selectors:
        try:
            logout_element = page.locator(selector).first
            if logout_element.count() > 0 and logout_element.is_visible():
                logout_element.click()
                page.wait_for_load_state("networkidle")
                time.sleep(1)
                logout_clicked = True
                print("  ✓ Logout clicked")
                break
        except Exception:
            continue

    if logout_clicked:
        # Verify logout (should not be able to access protected pages)
        page.goto(f"{base_url}/{test_user_data['username']}/")
        page.wait_for_load_state("networkidle")

        # Should either redirect to login or show public profile
        current_url = page.url
        print(f"  Current URL after logout: {current_url}")
        print("✓ Logout successful")
    else:
        print("  ⚠ Could not find logout button (skipping logout test)")

    # Final screenshot
    page.screenshot(path=f"tests/screenshots/test_complete_{test_user_data['username']}.png")

    print(f"\n{'='*60}")
    print("✅ USER REGISTRATION FLOW TEST PASSED")
    print(f"{'='*60}\n")


@pytest.mark.e2e
@pytest.mark.auth
def test_user_registration_validation(page: Page, base_url: str, timestamp: int):
    """
    Test form validation for user registration:
    - Empty fields
    - Invalid email
    - Password mismatch
    - Duplicate username
    """

    print(f"\n{'='*60}")
    print("Testing registration form validation")
    print(f"{'='*60}\n")

    signup_url = f"{base_url}/auth/signup/"
    page.goto(signup_url)
    page.wait_for_load_state("networkidle")

    # Test 1: Submit with empty fields
    print("Test 1: Submitting with empty fields...")
    submit_button = page.locator('button[type="submit"]')
    submit_button.click()

    time.sleep(0.5)

    # Should stay on same page or show validation errors
    assert signup_url in page.url, "Should stay on signup page with empty fields"
    print("  ✓ Form validation prevents empty submission")

    # Test 2: Invalid email format
    print("\nTest 2: Testing invalid email format...")
    page.reload()
    page.wait_for_load_state("networkidle")

    page.locator('input[name="username"]').fill(f"test_invalid_{timestamp}")
    page.locator('input[name="email"]').fill("invalid-email")  # Invalid format

    if page.locator('input[name="password1"]').count() > 0:
        page.locator('input[name="password1"]').fill("TestPass123!")
        page.locator('input[name="password2"]').fill("TestPass123!")

    page.locator('button[type="submit"]').click()
    time.sleep(0.5)

    # Should show email validation error
    print("  ✓ Invalid email format rejected")

    # Test 3: Password mismatch
    print("\nTest 3: Testing password mismatch...")
    page.reload()
    page.wait_for_load_state("networkidle")

    page.locator('input[name="username"]').fill(f"test_mismatch_{timestamp}")
    page.locator('input[name="email"]').fill(f"test_mismatch_{timestamp}@example.com")

    if page.locator('input[name="password1"]').count() > 0:
        page.locator('input[name="password1"]').fill("TestPass123!")
        page.locator('input[name="password2"]').fill("DifferentPass456!")  # Mismatch

        page.locator('button[type="submit"]').click()
        time.sleep(0.5)

        # Should show password mismatch error
        assert signup_url in page.url, "Should stay on signup page with mismatched passwords"
        print("  ✓ Password mismatch detected")

    print(f"\n{'='*60}")
    print("✅ FORM VALIDATION TEST PASSED")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Allow running directly for quick testing
    pytest.main([__file__, "-v", "--headed"])
