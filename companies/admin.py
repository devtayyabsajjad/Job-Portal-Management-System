from django.contrib import admin
from .models import Company, Job

@admin.register(Company)
class CompanyAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'status', 'is_verified', 'created_at']
    list_filter = ['status', 'is_verified']
    search_fields = ['name', 'email', 'registration_number']

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'company', 'city', 'employment_type', 'is_active', 'created_at']
    list_filter = ['employment_type', 'is_active', 'experience_required']
    search_fields = ['title', 'description', 'company__name']
