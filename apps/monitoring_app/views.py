from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.db.models import Avg, Count, Q, Sum
from django.utils import timezone
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from datetime import timedelta
import time
import json
from .models import SystemMetric, ErrorLog, APIUsageMetric, UserActivity, UserEngagement, FeatureUsage


@staff_member_required
def monitoring_dashboard(request):
    """Main monitoring dashboard view"""
    
    # Get time range (default: last 24 hours)
    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    
    # Basic stats
    context = {
        'hours': hours,
        'total_requests': SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=since
        ).count(),
        'avg_response_time': SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=since
        ).aggregate(avg=Avg('value'))['avg'] or 0,
        'error_count': ErrorLog.objects.filter(timestamp__gte=since).count(),
        'active_users': UserActivity.objects.filter(
            timestamp__gte=since
        ).values('user').distinct().count(),
    }
    
    return render(request, 'monitoring_app/dashboard.html', context)


@staff_member_required
def api_performance_data(request):
    """Get performance data for charts"""
    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    
    # Response time over time (hourly averages)
    response_times = []
    for i in range(hours):
        hour_start = timezone.now() - timedelta(hours=i+1)
        hour_end = timezone.now() - timedelta(hours=i)
        
        avg_time = SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).aggregate(avg=Avg('value'))['avg']
        
        response_times.append({
            'time': hour_start.strftime('%H:%M'),
            'avg_response_time': round(avg_time or 0, 2)
        })
    
    # Most accessed endpoints
    top_endpoints = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=since
    ).values('endpoint').annotate(
        count=Count('id'),
        avg_time=Avg('value')
    ).order_by('-count')[:10]
    
    # Error distribution
    error_types = ErrorLog.objects.filter(
        timestamp__gte=since
    ).values('error_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Status code distribution
    status_codes = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=since
    ).values('status_code').annotate(
        count=Count('id')
    ).order_by('-count')
    
    return JsonResponse({
        'response_times': list(reversed(response_times)),  # Chronological order
        'top_endpoints': list(top_endpoints),
        'error_types': list(error_types),
        'status_codes': list(status_codes),
    })


@staff_member_required
def user_activity_data(request):
    """Get user activity data"""
    hours = int(request.GET.get('hours', 24))
    since = timezone.now() - timedelta(hours=hours)
    
    # Activity by type
    activity_types = UserActivity.objects.filter(
        timestamp__gte=since
    ).values('activity_type').annotate(
        count=Count('id')
    ).order_by('-count')
    
    # Hourly user activity
    hourly_activity = []
    for i in range(hours):
        hour_start = timezone.now() - timedelta(hours=i+1)
        hour_end = timezone.now() - timedelta(hours=i)
        
        activity_count = UserActivity.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        hourly_activity.append({
            'time': hour_start.strftime('%H:%M'),
            'activity_count': activity_count
        })
    
    # Most active users
    active_users = UserActivity.objects.filter(
        timestamp__gte=since
    ).values('user__username').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    return JsonResponse({
        'activity_types': list(activity_types),
        'hourly_activity': list(reversed(hourly_activity)),
        'active_users': list(active_users),
    })


@staff_member_required
def system_health(request):
    """Get current system health status"""
    
    # Recent errors (last hour)
    recent_errors = ErrorLog.objects.filter(
        timestamp__gte=timezone.now() - timedelta(hours=1),
        resolved=False
    ).count()
    
    # Average response time (last hour)
    recent_avg_response = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).aggregate(avg=Avg('value'))['avg'] or 0
    
    # Error rate (last hour)
    total_requests = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=timezone.now() - timedelta(hours=1)
    ).count()
    
    error_rate = (recent_errors / max(total_requests, 1)) * 100
    
    # Determine health status
    if recent_avg_response > 1000 or error_rate > 5:
        health_status = 'critical'
    elif recent_avg_response > 500 or error_rate > 2:
        health_status = 'warning'
    else:
        health_status = 'healthy'
    
    return JsonResponse({
        'health_status': health_status,
        'avg_response_time': round(recent_avg_response, 2),
        'error_rate': round(error_rate, 2),
        'recent_errors': recent_errors,
        'total_requests': total_requests,
    })


@staff_member_required
def error_logs(request):
    """Display recent error logs"""
    
    # Get recent errors
    errors = ErrorLog.objects.filter(
        resolved=False
    ).order_by('-timestamp')[:50]
    
    return render(request, 'monitoring_app/error_logs.html', {
        'errors': errors
    })


@staff_member_required
def real_time_metrics(request):
    """Get real-time metrics with caching"""
    cache_key = 'monitoring:realtime_metrics'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    # Calculate fresh metrics
    now = timezone.now()
    last_hour = now - timedelta(hours=1)
    last_day = now - timedelta(days=1)
    
    # Real-time stats
    metrics = {
        'timestamp': now.isoformat(),
        'current_metrics': {
            'requests_last_hour': SystemMetric.objects.filter(
                metric_type='response_time',
                timestamp__gte=last_hour
            ).count(),
            'avg_response_time': SystemMetric.objects.filter(
                metric_type='response_time',
                timestamp__gte=last_hour
            ).aggregate(avg=Avg('value'))['avg'] or 0,
            'errors_last_hour': ErrorLog.objects.filter(
                timestamp__gte=last_hour
            ).count(),
            'active_users': UserActivity.objects.filter(
                timestamp__gte=last_hour
            ).values('user').distinct().count(),
        },
        'api_performance': list(APIUsageMetric.objects.filter(
            timestamp__gte=last_hour
        ).values('api_name').annotate(
            avg_response_time=Avg('response_time'),
            request_count=Count('id'),
            success_rate=Avg('success') * 100
        ).order_by('-request_count')[:10]),
        'user_activity_trend': get_hourly_activity_trend(24),
        'system_health': get_system_health_status(),
    }
    
    # Cache for 1 minute
    cache.set(cache_key, metrics, timeout=60)
    return JsonResponse(metrics)


@staff_member_required
def feature_analytics(request):
    """Get feature usage analytics"""
    cache_key = 'monitoring:feature_analytics'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    # Feature usage over last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    feature_data = {
        'feature_usage': list(FeatureUsage.objects.all().values(
            'module', 'feature_name', 'usage_count', 'unique_users',
            'success_rate', 'avg_session_time'
        ).order_by('-usage_count')[:20]),
        'module_popularity': list(UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('module').annotate(
            total_uses=Count('id'),
            unique_users=Count('user', distinct=True)
        ).order_by('-total_uses')),
        'user_engagement': get_user_engagement_metrics(),
        'retention_metrics': get_retention_metrics(),
    }
    
    # Cache for 10 minutes
    cache.set(cache_key, feature_data, timeout=600)
    return JsonResponse(feature_data)


@staff_member_required
def performance_trends(request):
    """Get performance trend data"""
    hours = int(request.GET.get('hours', 24))
    cache_key = f'monitoring:performance_trends:{hours}'
    cached_data = cache.get(cache_key)
    
    if cached_data:
        return JsonResponse(cached_data)
    
    since = timezone.now() - timedelta(hours=hours)
    
    trends = {
        'response_time_trend': get_response_time_trend(hours),
        'error_rate_trend': get_error_rate_trend(hours),
        'user_activity_trend': get_hourly_activity_trend(hours),
        'api_usage_trend': get_api_usage_trend(hours),
        'top_endpoints': list(SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=since
        ).values('endpoint').annotate(
            avg_time=Avg('value'),
            request_count=Count('id'),
            error_rate=Count('id', filter=Q(status_code__gte=400)) * 100.0 / Count('id')
        ).order_by('-request_count')[:15]),
    }
    
    # Cache for 5 minutes
    cache.set(cache_key, trends, timeout=300)
    return JsonResponse(trends)


def get_hourly_activity_trend(hours):
    """Get hourly user activity trend"""
    trend_data = []
    now = timezone.now()
    
    for i in range(hours):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        
        activity_count = UserActivity.objects.filter(
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        trend_data.append({
            'hour': hour_start.strftime('%H:%M'),
            'activity_count': activity_count,
            'timestamp': hour_start.isoformat()
        })
    
    return list(reversed(trend_data))


def get_response_time_trend(hours):
    """Get response time trend"""
    trend_data = []
    now = timezone.now()
    
    for i in range(hours):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        
        avg_time = SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).aggregate(avg=Avg('value'))['avg'] or 0
        
        trend_data.append({
            'hour': hour_start.strftime('%H:%M'),
            'avg_response_time': round(avg_time, 2),
            'timestamp': hour_start.isoformat()
        })
    
    return list(reversed(trend_data))


def get_error_rate_trend(hours):
    """Get error rate trend"""
    trend_data = []
    now = timezone.now()
    
    for i in range(hours):
        hour_start = now - timedelta(hours=i+1)
        hour_end = now - timedelta(hours=i)
        
        total_requests = SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=hour_start,
            timestamp__lt=hour_end
        ).count()
        
        error_count = SystemMetric.objects.filter(
            metric_type='response_time',
            timestamp__gte=hour_start,
            timestamp__lt=hour_end,
            status_code__gte=400
        ).count()
        
        error_rate = (error_count / max(total_requests, 1)) * 100
        
        trend_data.append({
            'hour': hour_start.strftime('%H:%M'),
            'error_rate': round(error_rate, 2),
            'timestamp': hour_start.isoformat()
        })
    
    return list(reversed(trend_data))


def get_api_usage_trend(hours):
    """Get API usage trend"""
    since = timezone.now() - timedelta(hours=hours)
    
    return list(APIUsageMetric.objects.filter(
        timestamp__gte=since
    ).values('api_name').annotate(
        request_count=Count('id'),
        avg_response_time=Avg('response_time'),
        success_rate=Avg('success') * 100
    ).order_by('-request_count'))


def get_system_health_status():
    """Get overall system health status"""
    last_hour = timezone.now() - timedelta(hours=1)
    
    # Calculate health metrics
    avg_response_time = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=last_hour
    ).aggregate(avg=Avg('value'))['avg'] or 0
    
    error_count = ErrorLog.objects.filter(
        timestamp__gte=last_hour,
        resolved=False
    ).count()
    
    total_requests = SystemMetric.objects.filter(
        metric_type='response_time',
        timestamp__gte=last_hour
    ).count()
    
    error_rate = (error_count / max(total_requests, 1)) * 100
    
    # Determine health status
    if avg_response_time > 2000 or error_rate > 10:
        status = 'critical'
    elif avg_response_time > 1000 or error_rate > 5:
        status = 'warning'
    else:
        status = 'healthy'
    
    return {
        'status': status,
        'avg_response_time': round(avg_response_time, 2),
        'error_rate': round(error_rate, 2),
        'total_requests': total_requests,
        'uptime_percentage': 100 - error_rate if error_rate < 100 else 0
    }


def get_user_engagement_metrics():
    """Get user engagement analytics"""
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    return {
        'total_active_users': UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('user').distinct().count(),
        'avg_session_duration': UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago,
            duration__isnull=False
        ).aggregate(avg=Avg('duration'))['avg'] or 0,
        'most_used_features': list(UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('activity_type').annotate(
            count=Count('id')
        ).order_by('-count')[:10]),
        'module_adoption': list(UserActivity.objects.filter(
            timestamp__gte=thirty_days_ago
        ).values('module').annotate(
            users=Count('user', distinct=True)
        ).order_by('-users'))
    }


def get_retention_metrics():
    """Get user retention metrics"""
    # Simple retention calculation
    seven_days_ago = timezone.now() - timedelta(days=7)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    
    users_7_days = set(UserActivity.objects.filter(
        timestamp__gte=seven_days_ago
    ).values_list('user', flat=True))
    
    users_30_days = set(UserActivity.objects.filter(
        timestamp__gte=thirty_days_ago
    ).values_list('user', flat=True))
    
    retention_7_day = len(users_7_days & users_30_days) / max(len(users_30_days), 1) * 100
    
    return {
        'weekly_retention_rate': round(retention_7_day, 2),
        'active_users_7d': len(users_7_days),
        'active_users_30d': len(users_30_days),
        'new_users_trend': 'stable'  # Could be calculated based on registration dates
    }