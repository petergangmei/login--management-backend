from django.contrib import admin
from .models import SubscriptionPlan, UserSubscription, UserSession

# Register your models here.

@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):
    list_display = ('name', 'max_devices', 'description')
    search_fields = ('name',)

@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'plan', 'active', 'created_at', 'updated_at')
    list_filter = ('active', 'plan')
    search_fields = ('user__username',)

@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    list_display = ('user', 'device_info', 'ip_address', 'is_active', 'last_activity', 'created_at')
    list_filter = ('is_active',)
    search_fields = ('user__username', 'device_info', 'ip_address')
