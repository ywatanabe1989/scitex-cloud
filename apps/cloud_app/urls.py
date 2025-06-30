#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Timestamp: "2025-06-29 19:51:04 (ywatanabe)"
# File: /ssh:scitex:/home/ywatanabe/proj/scitex-cloud/apps/cloud_app/urls.py
# ----------------------------------------
import os
__FILE__ = (
    "./apps/cloud_app/urls.py"
)
__DIR__ = os.path.dirname(__FILE__)
# ----------------------------------------

from django.shortcuts import redirect
from django.urls import path

from . import views

app_name = "cloud_app"

urlpatterns = [
    path("", views.index, name="index"),
    path("cloud/", lambda request: redirect("cloud_app:index"), name="cloud"),
    path("premium/", views.premium_subscription, name="premium"),
    # Concept and vision pages
    path("vision/", views.vision, name="vision"),
    path("publications/", views.publications, name="publications"),
    # Support pages
    path("donate/", views.donate, name="donate"),
    path("fundraising/", views.fundraising, name="fundraising"),
    path("verify-email/", views.verify_email, name="verify-email"),
    path(
        "donation-success/<int:donation_id>/",
        views.donation_success,
        name="donation-success",
    ),
    # Legal and contact pages
    path("contact/", views.contact, name="contact"),
    path("privacy/", views.privacy_policy, name="privacy"),
    path("terms/", views.terms_of_use, name="terms"),
    path("cookies/", views.cookie_policy, name="cookies"),
    # Authentication pages
    path("signup/", views.signup, name="signup"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("forgot-password/", views.forgot_password, name="forgot-password"),
    
    # Design System
    path('design/', views.design_system, name='design'),
    
    # Demo page  
    path('demo/', views.demo, name='demo'),
    
    # Missing view functions - add required by URLs
    path('features/', views.features, name='features'),
    path('pricing/', views.pricing, name='pricing'),
    path('concept/', views.concept, name='concept'),
    
    # API Documentation
    path('api-docs/', views.api_docs, name='api-docs'),
]

# EOF
