from django.contrib import admin
from .models import Notification, EmailVerificationToken

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read']
    search_fields = ['title', 'user__username']

@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['purpose', 'user', 'expires_at', 'created_at']
    list_filter = ['purpose']
