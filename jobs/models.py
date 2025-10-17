"""
Job Application and Saved Jobs Models
"""
from django.db import models
from accounts.models import User
from companies.models import Job, Company
import uuid

class Application(models.Model):
    """Job applications submitted by job seekers"""
    
    STATUS_CHOICES = (
        ('applied', 'Applied'),
        ('under_review', 'Under Review'),
        ('shortlisted', 'Shortlisted'),
        ('interview_scheduled', 'Interview Scheduled'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='applications')
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='received_applications')
    
    # Application Details
    resume_url = models.FileField(upload_to='application_resumes/', verbose_name='Resume')
    cover_letter = models.TextField(help_text="Why are you interested in this position?")
    
    # Status
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='applied')
    notes = models.TextField(blank=True, help_text="Internal notes from company")
    
    # Timestamps
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'applications'
        verbose_name = 'Application'
        verbose_name_plural = 'Applications'
        ordering = ['-applied_at']
        unique_together = ('job', 'user')  # One application per user per job
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['job']),
            models.Index(fields=['company']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.job.title}"
    
    def update_status(self, new_status):
        """Update application status"""
        self.status = new_status
        self.save(update_fields=['status', 'updated_at'])


class SavedJob(models.Model):
    """Jobs saved/bookmarked by job seekers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_jobs')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='saved_by')
    saved_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'saved_jobs'
        verbose_name = 'Saved Job'
        verbose_name_plural = 'Saved Jobs'
        unique_together = ('user', 'job')  # One save per user per job
        ordering = ['-saved_date']
    
    def __str__(self):
        return f"{self.user.username} saved {self.job.title}"
