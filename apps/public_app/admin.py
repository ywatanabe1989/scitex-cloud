from django.contrib import admin
from .models import (
    SubscriptionPlan, Subscription, CloudResource,
    APIKey, ServiceIntegration
)

# EmailVerification admin now in apps.auth_app.admin
# Donation, DonationTier admin now in apps.donations_app.admin

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ['name', 'plan_type', 'price_monthly', 'max_projects', 'storage_gb', 'is_featured', 'is_active']
    list_filter = ['plan_type', 'is_featured', 'is_active']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'price_monthly', 'price_yearly', 'is_featured', 'is_active', 'display_order')
        }),
        ('Resource Limits', {
            'fields': ('max_projects', 'storage_gb', 'cpu_cores', 'gpu_vram_gb')
        }),
        ('Feature Flags', {
            'fields': ('has_watermark', 'requires_citation', 'requires_archive', 
                      'has_priority_support', 'has_custom_integrations', 'has_team_collaboration')
        }),
    )

@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'status', 'current_period_start', 'current_period_end']
    list_filter = ['status', 'plan', 'created_at']
    search_fields = ['user__username', 'user__email', 'stripe_subscription_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'

@admin.register(CloudResource)
class CloudResourceAdmin(admin.ModelAdmin):
    list_display = ['user', 'resource_type', 'amount_used', 'unit', 'period_start', 'created_at']
    list_filter = ['resource_type', 'created_at']
    search_fields = ['user__username', 'user__email']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = ['user', 'name', 'prefix', 'is_active', 'last_used', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'name', 'prefix']
    readonly_fields = ['key', 'prefix', 'created_at', 'last_used']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'name', 'key', 'prefix')
        }),
        ('Permissions', {
            'fields': ('can_read', 'can_write', 'can_delete', 'rate_limit_per_hour')
        }),
        ('Status', {
            'fields': ('is_active', 'last_used', 'expires_at')
        }),
    )

@admin.register(ServiceIntegration)
class ServiceIntegrationAdmin(admin.ModelAdmin):
    list_display = ['user', 'integration_type', 'is_active', 'last_synced', 'created_at']
    list_filter = ['integration_type', 'is_active', 'created_at']
    search_fields = ['user__username', 'user__email', 'external_id']
    readonly_fields = ['created_at', 'updated_at']
    exclude = ['access_token', 'refresh_token']  # Hide sensitive fields