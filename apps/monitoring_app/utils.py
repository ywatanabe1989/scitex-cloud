import time
import logging
from .models import APIUsageMetric, ErrorLog, SystemMetric

logger = logging.getLogger(__name__)


def log_api_usage(api_name, endpoint, response_time, status_code, success=True, 
                  query_params=None, response_size=None):
    """
    Utility function to log API usage metrics
    
    Args:
        api_name (str): Name of the API (e.g., 'semantic_scholar', 'arxiv')
        endpoint (str): API endpoint URL
        response_time (float): Response time in milliseconds
        status_code (int): HTTP status code
        success (bool): Whether the request was successful
        query_params (dict): Query parameters sent to API
        response_size (int): Response size in bytes
    """
    try:
        APIUsageMetric.objects.create(
            api_name=api_name,
            endpoint=endpoint,
            response_time=response_time,
            status_code=status_code,
            success=success,
            query_params=query_params or {},
            response_size=response_size
        )
    except Exception as e:
        logger.error(f"Failed to log API usage: {e}")


def log_error(severity, error_type, message, endpoint=None, user=None, 
              stack_trace=None, metadata=None):
    """
    Utility function to log errors
    
    Args:
        severity (str): Error severity ('low', 'medium', 'high', 'critical')
        error_type (str): Type of error
        message (str): Error message
        endpoint (str): Endpoint where error occurred
        user: User object (optional)
        stack_trace (str): Stack trace (optional)
        metadata (dict): Additional error context
    """
    try:
        ErrorLog.objects.create(
            severity=severity,
            error_type=error_type,
            message=message,
            endpoint=endpoint,
            user=user,
            stack_trace=stack_trace,
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Failed to log error: {e}")


def log_system_metric(metric_type, value, endpoint=None, user=None, 
                      status_code=None, metadata=None):
    """
    Utility function to log system metrics
    
    Args:
        metric_type (str): Type of metric ('response_time', 'api_call', etc.)
        value (float): Metric value
        endpoint (str): Associated endpoint
        user: User object (optional)
        status_code (int): HTTP status code (optional)
        metadata (dict): Additional metric context
    """
    try:
        SystemMetric.objects.create(
            metric_type=metric_type,
            value=value,
            endpoint=endpoint,
            user=user,
            status_code=status_code,
            metadata=metadata or {}
        )
    except Exception as e:
        logger.error(f"Failed to log system metric: {e}")


class APIMonitor:
    """Context manager for monitoring API calls"""
    
    def __init__(self, api_name, endpoint, query_params=None):
        self.api_name = api_name
        self.endpoint = endpoint
        self.query_params = query_params or {}
        self.start_time = None
        self.response_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.start_time:
            self.response_time = (time.time() - self.start_time) * 1000  # Convert to ms
            
            # Determine success and status code
            success = exc_type is None
            status_code = getattr(exc_val, 'response', {}).get('status_code', 500) if exc_val else 200
            
            # Log the API usage
            log_api_usage(
                api_name=self.api_name,
                endpoint=self.endpoint,
                response_time=self.response_time,
                status_code=status_code,
                success=success,
                query_params=self.query_params
            )
            
            # Log error if exception occurred
            if exc_type and exc_val:
                log_error(
                    severity='medium',
                    error_type=exc_type.__name__,
                    message=str(exc_val),
                    endpoint=self.endpoint,
                    metadata={
                        'api_name': self.api_name,
                        'query_params': self.query_params,
                        'response_time': self.response_time
                    }
                )
        
        # Don't suppress the exception
        return False


def get_system_health_summary():
    """
    Get a summary of system health metrics
    
    Returns:
        dict: Health summary with key metrics
    """
    from django.utils import timezone
    from datetime import timedelta
    from django.db.models import Avg, Count
    
    # Last hour metrics
    since = timezone.now() - timedelta(hours=1)
    
    # Error count
    error_count = ErrorLog.objects.filter(
        timestamp__gte=since,
        resolved=False
    ).count()
    
    # Average response time
    avg_response_time = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=since
    ).aggregate(avg=Avg('value'))['avg'] or 0
    
    # Total requests
    total_requests = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=since
    ).count()
    
    # API success rate
    api_metrics = APIUsageMetric.objects.filter(timestamp__gte=since)
    total_api_calls = api_metrics.count()
    successful_api_calls = api_metrics.filter(success=True).count()
    api_success_rate = (successful_api_calls / max(total_api_calls, 1)) * 100
    
    # Determine overall health
    if error_count > 10 or avg_response_time > 1000 or api_success_rate < 90:
        health_status = 'critical'
    elif error_count > 5 or avg_response_time > 500 or api_success_rate < 95:
        health_status = 'warning'
    else:
        health_status = 'healthy'
    
    return {
        'health_status': health_status,
        'error_count': error_count,
        'avg_response_time': round(avg_response_time, 2),
        'total_requests': total_requests,
        'api_success_rate': round(api_success_rate, 2),
        'total_api_calls': total_api_calls,
    }