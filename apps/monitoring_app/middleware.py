import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.models import AnonymousUser
from django.core.cache import cache
from .models import SystemMetric, ErrorLog, UserActivity, APIUsageMetric


logger = logging.getLogger(__name__)


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Middleware to track request performance and user activity"""
    
    def process_request(self, request):
        """Start timing the request"""
        request._monitoring_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log performance metrics"""
        if hasattr(request, '_monitoring_start_time'):
            # Calculate response time
            response_time = (time.time() - request._monitoring_start_time) * 1000  # Convert to ms
            
            # Skip monitoring for static files and admin
            if (not request.path.startswith('/static/') and 
                not request.path.startswith('/admin/') and
                not request.path.startswith('/media/')):
                
                try:
                    # Create performance metric
                    SystemMetric.objects.create(
                        metric_type='response_time',
                        endpoint=request.path,
                        value=response_time,
                        status_code=response.status_code,
                        user=request.user if not isinstance(request.user, AnonymousUser) else None,
                        metadata={
                            'method': request.method,
                            'user_agent': request.META.get('HTTP_USER_AGENT', '')[:500],
                            'ip_address': self.get_client_ip(request),
                            'content_length': len(response.content) if hasattr(response, 'content') else 0,
                            'query_params': dict(request.GET),
                        }
                    )
                    
                    # Track API usage separately for better monitoring
                    if request.path.startswith('/api/'):
                        self.track_api_usage(request, response, response_time)
                    
                    # Log user activity for authenticated users
                    if not isinstance(request.user, AnonymousUser):
                        activity_type = self.determine_activity_type(request)
                        module, feature = self.determine_module_feature(request.path)
                        if activity_type:
                            UserActivity.objects.create(
                                user=request.user,
                                activity_type=activity_type,
                                details={
                                    'path': request.path,
                                    'method': request.method,
                                    'status_code': response.status_code,
                                    'response_time_ms': response_time,
                                    'query_params': dict(request.GET),
                                },
                                session_id=request.session.session_key,
                                ip_address=self.get_client_ip(request),
                                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                                duration=int(response_time),
                                module=module,
                                feature=feature,
                                success=200 <= response.status_code < 400,
                            )
                    
                    # Update real-time metrics cache
                    self.update_realtime_cache(response_time, response.status_code)
                
                except Exception as e:
                    logger.error(f"Failed to log performance metric: {e}")
        
        return response
    
    def process_exception(self, request, exception):
        """Log errors and exceptions"""
        try:
            ErrorLog.objects.create(
                severity='high',
                error_type=type(exception).__name__,
                message=str(exception),
                stack_trace=self.format_exception(exception),
                endpoint=request.path,
                user=request.user if not isinstance(request.user, AnonymousUser) else None,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                ip_address=self.get_client_ip(request),
                metadata={
                    'method': request.method,
                    'query_params': dict(request.GET),
                }
            )
        except Exception as e:
            logger.error(f"Failed to log error: {e}")
        
        return None  # Continue with normal exception handling
    
    def get_client_ip(self, request):
        """Get the client's IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def determine_activity_type(self, request):
        """Determine user activity type based on request"""
        path = request.path.lower()
        method = request.method.upper()
        
        if '/login' in path:
            return 'login'
        elif '/logout' in path:
            return 'logout'
        elif '/dashboard' in path:
            return 'dashboard_view'
        elif '/scholar' in path:
            if '/search' in path or method == 'POST':
                return 'scholar_search'
            elif '/save' in path:
                return 'scholar_save'
            return 'feature_use'
        elif '/writer' in path:
            if '/compile' in path:
                return 'writer_compile'
            elif '/template' in path:
                return 'writer_template'
            return 'document_edit'
        elif '/viz' in path:
            if method == 'POST':
                return 'visualization_create'
            elif '/export' in path:
                return 'viz_export'
            return 'feature_use'
        elif '/code' in path:
            if '/run' in path or '/execute' in path:
                return 'code_execute'
            return 'feature_use'
        elif '/documents' in path:
            if method == 'POST':
                return 'document_create'
            elif method in ['PUT', 'PATCH']:
                return 'document_edit'
            return 'feature_use'
        elif '/projects' in path:
            if method == 'POST':
                return 'project_create'
            return 'feature_use'
        
        return 'feature_use'  # Default fallback
    
    def format_exception(self, exception):
        """Format exception for storage"""
        import traceback
        return traceback.format_exc()[:5000]  # Limit length
    
    def determine_module_feature(self, path):
        """Extract module and feature from request path"""
        path_parts = path.strip('/').split('/')
        
        if not path_parts or path_parts[0] == '':
            return 'dashboard', 'home'
        
        module = path_parts[0]
        feature = path_parts[1] if len(path_parts) > 1 else 'main'
        
        # Normalize common modules
        module_mapping = {
            'scholar': 'scholar',
            'writer': 'writer', 
            'viz': 'viz',
            'code': 'code',
            'core': 'dashboard',
            'dashboard': 'dashboard',
            'projects': 'dashboard',
            'documents': 'dashboard',
            'login': 'auth',
            'logout': 'auth',
            'signup': 'auth',
        }
        
        return module_mapping.get(module, module), feature
    
    def track_api_usage(self, request, response, response_time):
        """Track API usage metrics"""
        try:
            # Determine API name from path
            path_parts = request.path.strip('/').split('/')
            api_name = path_parts[1] if len(path_parts) > 1 else 'unknown'
            
            APIUsageMetric.objects.create(
                api_name=api_name,
                endpoint=request.path,
                response_time=response_time,
                status_code=response.status_code,
                success=200 <= response.status_code < 400,
                query_params=dict(request.GET),
                response_size=len(response.content) if hasattr(response, 'content') else 0,
            )
        except Exception as e:
            logger.error(f"Failed to track API usage: {e}")
    
    def update_realtime_cache(self, response_time, status_code):
        """Update real-time metrics in cache for dashboard"""
        try:
            # Update hourly metrics
            current_hour = int(time.time() // 3600)
            cache_key = f"monitoring:hourly:{current_hour}"
            
            hourly_data = cache.get(cache_key, {
                'total_requests': 0,
                'total_response_time': 0,
                'error_count': 0,
                'status_codes': {},
            })
            
            hourly_data['total_requests'] += 1
            hourly_data['total_response_time'] += response_time
            if status_code >= 400:
                hourly_data['error_count'] += 1
            
            status_key = str(status_code)
            hourly_data['status_codes'][status_key] = hourly_data['status_codes'].get(status_key, 0) + 1
            
            cache.set(cache_key, hourly_data, timeout=7200)  # 2 hours
            
            # Update real-time dashboard metrics
            cache.set('monitoring:last_response_time', response_time, timeout=300)
            cache.set('monitoring:last_update', time.time(), timeout=300)
            
        except Exception as e:
            logger.error(f"Cache update error: {e}")