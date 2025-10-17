from django.contrib import admin
from .models import Application, SavedJob

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'company', 'status', 'applied_at']
    list_filter = ['status', 'applied_at']
    search_fields = ['user__username', 'job__title', 'company__name']

@admin.register(SavedJob)
class SavedJobAdmin(admin.ModelAdmin):
    list_display = ['user', 'job', 'saved_date']
    search_fields = ['user__username', 'job__title']
