"""
Notifications Model
"""
from django.db import models
from accounts.models import User
import uuid

class Notification(models.Model):
    """System notifications for users"""
    
    NOTIFICATION_TYPES = (
        ('approval', 'Company Approval'),
        ('rejection', 'Company Rejection'),
        ('application', 'New Application'),
        ('status_change', 'Application Status Change'),
        ('job_posted', 'New Job Posted'),
        ('system', 'System Notification'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    title = models.CharField(max_length=200)
    message = models.TextField()
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])


class EmailVerificationToken(models.Model):
    """Email verification and password reset tokens"""
    
    PURPOSE_CHOICES = (
        ('verify_email', 'Email Verification'),
        ('reset_password', 'Password Reset'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_tokens', 
                            null=True, blank=True)
    company = models.ForeignKey('companies.Company', on_delete=models.CASCADE, 
                                related_name='verification_tokens', null=True, blank=True)
    token = models.CharField(max_length=100, unique=True)
    purpose = models.CharField(max_length=20, choices=PURPOSE_CHOICES)
    expires_at = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'email_verification_tokens'
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
    
    def __str__(self):
        return f"{self.get_purpose_display()} - {self.token[:10]}..."
