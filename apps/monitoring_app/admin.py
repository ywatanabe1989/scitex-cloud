from django.contrib import admin
from .models import SystemMetric, ErrorLog, APIUsageMetric, UserActivity


@admin.register(SystemMetric)
class SystemMetricAdmin(admin.ModelAdmin):
    list_display = ['metric_type', 'endpoint', 'value', 'status_code', 'user', 'timestamp']
    list_filter = ['metric_type', 'status_code', 'timestamp']
    search_fields = ['endpoint', 'user__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(ErrorLog)
class ErrorLogAdmin(admin.ModelAdmin):
    list_display = ['severity', 'error_type', 'message_short', 'endpoint', 'user', 'resolved', 'timestamp']
    list_filter = ['severity', 'error_type', 'resolved', 'timestamp']
    search_fields = ['error_type', 'message', 'endpoint', 'user__username']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    actions = ['mark_resolved']
    
    def message_short(self, obj):
        return obj.message[:100] + ('...' if len(obj.message) > 100 else '')
    message_short.short_description = 'Message'
    
    def mark_resolved(self, request, queryset):
        queryset.update(resolved=True)
        self.message_user(request, f"{queryset.count()} errors marked as resolved.")
    mark_resolved.short_description = "Mark selected errors as resolved"
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(APIUsageMetric)
class APIUsageMetricAdmin(admin.ModelAdmin):
    list_display = ['api_name', 'endpoint', 'response_time', 'status_code', 'success', 'timestamp']
    list_filter = ['api_name', 'success', 'status_code', 'timestamp']
    search_fields = ['api_name', 'endpoint']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request)


@admin.register(UserActivity)
class UserActivityAdmin(admin.ModelAdmin):
    list_display = ['user', 'activity_type', 'session_id', 'ip_address', 'timestamp']
    list_filter = ['activity_type', 'timestamp']
    search_fields = ['user__username', 'user__email', 'session_id', 'ip_address']
    date_hierarchy = 'timestamp'
    readonly_fields = ['timestamp']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')