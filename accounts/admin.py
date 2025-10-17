from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, JobSeeker

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'user_type', 'is_active', 'created_at']
    list_filter = ['user_type', 'is_active']
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('user_type', 'phone', 'profile_image')}),
    )

@admin.register(JobSeeker)
class JobSeekerAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'city']
    search_fields = ['full_name', 'email']
