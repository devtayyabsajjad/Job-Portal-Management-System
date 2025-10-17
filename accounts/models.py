"""
Custom User Model for Job Portal
Supports three user types: Admin, Company, Job Seeker
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
import uuid

class User(AbstractUser):
    """Extended User model with role-based access"""
    
    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('company', 'Company'),
        ('jobseeker', 'Job Seeker'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='jobseeker')
    phone = models.CharField(max_length=15, blank=True)
    profile_image = models.ImageField(upload_to='profiles/', blank=True, null=True)
    email = models.EmailField(unique=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
    
    def __str__(self):
        return f"{self.username} ({self.get_user_type_display()})"
    
    def is_admin(self):
        return self.user_type == 'admin'
    
    def is_company(self):
        return self.user_type == 'company'
    
    def is_jobseeker(self):
        return self.user_type == 'jobseeker'


class JobSeeker(models.Model):
    """Profile for Job Seekers"""
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='jobseeker_profile')
    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    skills = models.TextField(blank=True, help_text="Comma-separated skills")
    education = models.TextField(blank=True)
    experience = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobseekers'
        verbose_name = 'Job Seeker'
        verbose_name_plural = 'Job Seekers'
    
    def __str__(self):
        return self.full_name
