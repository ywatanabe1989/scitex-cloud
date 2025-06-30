#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
SciTeX-Cloud Billing Middleware
Feature access control and usage enforcement middleware
"""

from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import messages
from django.shortcuts import render
from django.core.exceptions import PermissionDenied
from django.utils.deprecation import MiddlewareMixin
import json
import time
import threading

from .services import FeatureAccessService, QuotaService, UsageService
from .models import UserSubscription, QuotaLimit
import logging

logger = logging.getLogger(__name__)

# Thread-local storage for request tracking
_thread_locals = threading.local()


class FeatureAccessMiddleware(MiddlewareMixin):
    """
    Middleware to enforce feature access based on subscription tiers
    """
    
    # Define feature-to-URL mappings
    FEATURE_URLS = {
        'unlimited_scholar_searches': ['/scholar/search/', '/api/scholar/'],
        'advanced_writer_features': ['/writer/advanced/', '/writer/templates/', '/api/writer/'],
        'viz_export': ['/viz/export/', '/api/viz/export/'],
        'private_code_repos': ['/code/private/', '/api/code/private/'],
        'ai_assistant': ['/ai/', '/api/ai/'],
        'team_management': ['/team/', '/collaboration/'],
        'advanced_analytics': ['/analytics/', '/dashboard/analytics/'],
        'custom_integrations': ['/integrations/custom/'],
        'priority_support': ['/support/priority/'],
    }
    
    # URLs that require quota checking
    QUOTA_URLS = {
        'project_creations': ['/projects/create/', '/api/projects/'],
        'storage': ['/upload/', '/api/upload/', '/files/upload/'],
        'compute_hours': ['/code/execute/', '/api/code/execute/'],
        'gpu_hours': ['/code/gpu/', '/api/gpu/'],
        'api_calls': ['/api/'],
        'scholar_searches': ['/scholar/search/'],
        'writer_compiles': ['/writer/compile/'],
        'viz_exports': ['/viz/export/'],
    }
    
    def process_request(self, request):
        """Check feature access and quotas before processing request"""
        
        # Skip for unauthenticated users on public endpoints
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin and staff users
        if request.user.is_staff or request.user.is_superuser:
            return None
        
        # Skip for static files and admin
        if request.path.startswith('/static/') or request.path.startswith('/admin/'):
            return None
        
        try:
            # Store request start time for usage tracking
            _thread_locals.start_time = time.time()
            _thread_locals.request = request
            
            # Check feature access
            feature_blocked = self._check_feature_access(request)
            if feature_blocked:
                return feature_blocked
            
            # Check quota limits
            quota_blocked = self._check_quota_limits(request)
            if quota_blocked:
                return quota_blocked
            
        except Exception as e:
            logger.error(f"Error in FeatureAccessMiddleware: {str(e)}")
            # Don't block request on middleware errors
            pass
        
        return None
    
    def process_response(self, request, response):
        """Track usage after request completion"""
        if hasattr(_thread_locals, 'start_time') and request.user.is_authenticated:
            try:
                execution_time = time.time() - _thread_locals.start_time
                
                # Track API usage
                if request.path.startswith('/api/') and response.status_code < 400:
                    UsageService.record_usage(
                        user=request.user,
                        resource_type='api_calls',
                        amount=1,
                        unit='calls',
                        module='api',
                        feature=self._extract_api_feature(request.path),
                        metadata={
                            'endpoint': request.path,
                            'method': request.method,
                            'response_time': execution_time,
                            'status_code': response.status_code
                        }
                    )
                
                # Track compute usage for code execution
                if '/code/execute/' in request.path and response.status_code == 200:
                    # Estimate compute time (could be enhanced with actual metrics)
                    compute_hours = execution_time / 3600
                    UsageService.record_usage(
                        user=request.user,
                        resource_type='compute_hours',
                        amount=compute_hours,
                        unit='hours',
                        module='code',
                        feature='execution',
                        metadata={'execution_time_seconds': execution_time}
                    )
                
            except Exception as e:
                logger.error(f"Error tracking usage: {str(e)}")
        
        return response
    
    def _check_feature_access(self, request):
        """Check if user has access to requested feature"""
        for feature, urls in self.FEATURE_URLS.items():
            for url_pattern in urls:
                if request.path.startswith(url_pattern):
                    if not FeatureAccessService.has_feature_access(request.user, feature):
                        return self._handle_feature_denied(request, feature)
        return None
    
    def _check_quota_limits(self, request):
        """Check if user has sufficient quota for the request"""
        for resource_type, urls in self.QUOTA_URLS.items():
            for url_pattern in urls:
                if request.path.startswith(url_pattern):
                    # Determine required quota amount based on request type
                    required_amount = self._get_required_quota_amount(request, resource_type)
                    
                    has_quota, available = QuotaService.check_quota_availability(
                        request.user, resource_type, required_amount
                    )
                    
                    if not has_quota:
                        return self._handle_quota_exceeded(request, resource_type, available)
        return None
    
    def _get_required_quota_amount(self, request, resource_type):
        """Determine required quota amount for the request"""
        if resource_type == 'storage' and request.method == 'POST':
            # Check file size from request
            file_size = 0
            for file_obj in request.FILES.values():
                file_size += file_obj.size
            return file_size / (1024 * 1024 * 1024)  # Convert to GB
        
        elif resource_type == 'compute_hours':
            # Estimate based on request complexity (could be enhanced)
            return 0.1  # 6 minutes default estimate
        
        elif resource_type == 'gpu_hours':
            return 0.05  # 3 minutes default estimate
        
        else:
            return 1  # Default: 1 unit
    
    def _handle_feature_denied(self, request, feature):
        """Handle feature access denial"""
        tier_info = FeatureAccessService.get_user_tier_info(request.user)
        
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'feature_not_available',
                'message': f'This feature requires a higher subscription tier',
                'feature': feature,
                'current_tier': tier_info['tier'].name if tier_info else 'Free',
                'upgrade_url': reverse('billing:upgrade')
            }, status=403)
        else:
            messages.error(
                request,
                f'This feature requires a higher subscription tier. '
                f'Current tier: {tier_info["tier"].name if tier_info else "Free"}'
            )
            return HttpResponseRedirect(reverse('billing:upgrade'))
    
    def _handle_quota_exceeded(self, request, resource_type, available):
        """Handle quota exceeded"""
        if request.path.startswith('/api/'):
            return JsonResponse({
                'error': 'quota_exceeded',
                'message': f'You have exceeded your {resource_type.replace("_", " ")} quota',
                'resource_type': resource_type,
                'available': float(available),
                'upgrade_url': reverse('billing:upgrade')
            }, status=429)
        else:
            messages.error(
                request,
                f'You have exceeded your {resource_type.replace("_", " ")} quota. '
                f'Available: {available}. Please upgrade your subscription.'
            )
            return HttpResponseRedirect(reverse('billing:upgrade'))
    
    def _extract_api_feature(self, path):
        """Extract API feature name from path"""
        parts = path.strip('/').split('/')
        if len(parts) >= 2:
            return parts[1]  # e.g., /api/scholar/ -> scholar
        return 'unknown'


class WatermarkMiddleware(MiddlewareMixin):
    """
    Middleware to add watermarks for free tier users
    """
    
    def process_response(self, request, response):
        """Add watermark headers or content for free tier users"""
        if (request.user.is_authenticated and 
            response.get('Content-Type', '').startswith('text/html')):
            
            try:
                tier_info = FeatureAccessService.get_user_tier_info(request.user)
                if tier_info and tier_info['tier'].has_watermark:
                    # Add watermark header
                    response['X-SciTeX-Watermark'] = 'true'
                    
                    # For HTML responses, inject watermark
                    if hasattr(response, 'content'):
                        content = response.content.decode('utf-8')
                        watermark_html = '''
                        <div style="position: fixed; bottom: 10px; right: 10px; 
                                   background: rgba(0,0,0,0.8); color: white; 
                                   padding: 5px 10px; border-radius: 3px; 
                                   font-size: 12px; z-index: 9999;">
                            Generated with SciTeX-Cloud Free
                        </div>
                        '''
                        
                        # Insert before closing body tag
                        content = content.replace('</body>', watermark_html + '</body>')
                        response.content = content.encode('utf-8')
                        response['Content-Length'] = len(response.content)
            
            except Exception as e:
                logger.error(f"Error adding watermark: {str(e)}")
        
        return response


class SubscriptionStatusMiddleware(MiddlewareMixin):
    """
    Middleware to check subscription status and handle expiry
    """
    
    # URLs that require active subscription
    SUBSCRIPTION_REQUIRED_URLS = [
        '/projects/premium/',
        '/team/',
        '/analytics/',
        '/integrations/',
        '/export/premium/',
    ]
    
    def process_request(self, request):
        """Check subscription status"""
        if not request.user.is_authenticated:
            return None
        
        # Skip for admin users
        if request.user.is_staff or request.user.is_superuser:
            return None
        
        # Check if URL requires subscription
        requires_subscription = any(
            request.path.startswith(url) for url in self.SUBSCRIPTION_REQUIRED_URLS
        )
        
        if requires_subscription:
            try:
                subscription = UserSubscription.objects.filter(user=request.user).first()
                
                if not subscription or not subscription.is_active():
                    if request.path.startswith('/api/'):
                        return JsonResponse({
                            'error': 'subscription_required',
                            'message': 'Active subscription required for this feature',
                            'subscribe_url': reverse('billing:subscribe')
                        }, status=402)
                    else:
                        messages.warning(
                            request,
                            'This feature requires an active subscription. '
                            'Please subscribe or upgrade your plan.'
                        )
                        return HttpResponseRedirect(reverse('billing:subscribe'))
                
                # Check if subscription is about to expire
                if subscription.days_remaining() <= 7:
                    messages.warning(
                        request,
                        f'Your subscription expires in {subscription.days_remaining()} days. '
                        f'Please renew to continue using premium features.'
                    )
            
            except Exception as e:
                logger.error(f"Error checking subscription status: {str(e)}")
        
        return None


class UsageTrackingMiddleware(MiddlewareMixin):
    """
    Middleware for comprehensive usage tracking
    """
    
    def process_request(self, request):
        """Track request start"""
        if request.user.is_authenticated:
            _thread_locals.start_time = time.time()
            _thread_locals.user = request.user
            _thread_locals.path = request.path
            _thread_locals.method = request.method
    
    def process_response(self, request, response):
        """Track request completion and usage"""
        if (hasattr(_thread_locals, 'start_time') and 
            hasattr(_thread_locals, 'user') and 
            _thread_locals.user.is_authenticated):
            
            try:
                execution_time = time.time() - _thread_locals.start_time
                
                # Track different types of usage based on request
                self._track_module_usage(request, response, execution_time)
                
            except Exception as e:
                logger.error(f"Error in usage tracking: {str(e)}")
        
        return response
    
    def _track_module_usage(self, request, response, execution_time):
        """Track usage by module"""
        if response.status_code >= 400:
            return  # Don't track failed requests
        
        path = request.path.lower()
        user = request.user
        
        # Scholar module
        if '/scholar/' in path:
            if '/search/' in path:
                UsageService.record_usage(
                    user=user,
                    resource_type='scholar_searches',
                    amount=1,
                    unit='searches',
                    module='scholar',
                    feature='search',
                    metadata={'query_time': execution_time}
                )
        
        # Writer module
        elif '/writer/' in path:
            if '/compile/' in path:
                UsageService.record_usage(
                    user=user,
                    resource_type='writer_compiles',
                    amount=1,
                    unit='compiles',
                    module='writer',
                    feature='compile',
                    metadata={'compile_time': execution_time}
                )
        
        # Visualization module
        elif '/viz/' in path:
            if '/create/' in path or '/generate/' in path:
                UsageService.record_usage(
                    user=user,
                    resource_type='viz_exports',
                    amount=1,
                    unit='visualizations',
                    module='viz',
                    feature='creation',
                    metadata={'creation_time': execution_time}
                )
        
        # Code module
        elif '/code/' in path:
            if '/execute/' in path or '/run/' in path:
                compute_hours = execution_time / 3600
                UsageService.record_usage(
                    user=user,
                    resource_type='compute_hours',
                    amount=compute_hours,
                    unit='hours',
                    module='code',
                    feature='execution',
                    metadata={'execution_time': execution_time}
                )
        
        # AI Assistant
        elif '/ai/' in path:
            UsageService.record_usage(
                user=user,
                resource_type='ai_queries',
                amount=1,
                unit='queries',
                module='ai',
                feature='query',
                metadata={'response_time': execution_time}
            )