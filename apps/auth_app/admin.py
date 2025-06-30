from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .models import UserProfile, EmailVerification


class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fieldsets = (
        ('Profile Information', {
            'fields': ('profession', 'research_field', 'institution', 'bio')
        }),
        ('Verification', {
            'fields': ('is_academic_verified',),
            'classes': ('collapse',)
        }),
        ('Preferences', {
            'fields': ('email_notifications', 'weekly_digest'),
            'classes': ('collapse',)
        }),
        ('Activity', {
            'fields': ('last_login_at', 'total_login_count', 'profile_completed', 'profile_completion_date'),
            'classes': ('collapse',)
        }),
    )
    readonly_fields = ('is_academic_verified', 'profile_completed', 'profile_completion_date', 'last_login_at')


class UserAdmin(BaseUserAdmin):
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super().get_inline_instances(request, obj)


@admin.register(EmailVerification)
class EmailVerificationAdmin(admin.ModelAdmin):
    list_display = ('email', 'code', 'is_verified', 'created_at', 'expires_at')
    list_filter = ('is_verified', 'created_at')
    search_fields = ('email', 'user__username')
    readonly_fields = ('created_at', 'verified_at')
    
    def has_change_permission(self, request, obj=None):
        # Make email verifications read-only after creation
        return False


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, UserAdmin)