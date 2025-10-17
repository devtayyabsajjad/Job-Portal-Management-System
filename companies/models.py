"""
Company and Job Models
"""
from django.db import models
from django.utils import timezone
from accounts.models import User
import uuid

class Company(models.Model):
    """Company profile linked to user account"""
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='company_profile')
    admin_id = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='managed_companies', limit_choices_to={'user_type': 'admin'})
    
    # Company Details
    name = models.CharField(max_length=200, verbose_name='Company Name')
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20)
    website = models.URLField(blank=True)
    about = models.TextField(blank=True, verbose_name='About Company')
    address = models.TextField()
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    registration_number = models.CharField(max_length=100, unique=True)
    company_logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    # Approval Status
    is_verified = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_date = models.DateTimeField(auto_now_add=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    rejection_reason = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'companies'
        verbose_name = 'Company'
        verbose_name_plural = 'Companies'
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    def approve(self, admin_user):
        """Approve company registration"""
        self.status = 'approved'
        self.is_verified = True
        self.approved_date = timezone.now()
        self.admin_id = admin_user
        self.save()
    
    def reject(self, reason, admin_user):
        """Reject company registration"""
        self.status = 'rejected'
        self.is_verified = False
        self.rejection_reason = reason
        self.admin_id = admin_user
        self.save()


class Job(models.Model):
    """Job postings by companies"""
    
    JOB_TYPE_CHOICES = (
        ('full-time', 'Full Time'),
        ('part-time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
    )
    
    EXPERIENCE_CHOICES = (
        ('0-1', '0-1 years'),
        ('1-3', '1-3 years'),
        ('3-5', '3-5 years'),
        ('5+', '5+ years'),
    )
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, related_name='jobs')
    approved_by_admin = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                          related_name='approved_jobs')
    
    # Job Details
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, blank=True)
    description = models.TextField()
    requirements = models.TextField(help_text="Job requirements")
    responsibilities = models.TextField(help_text="Job responsibilities")
    
    # Location
    location = models.CharField(max_length=100)
    city = models.CharField(max_length=100)
    
    # Job Type & Category
    employment_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, verbose_name='Job Type')
    category = models.CharField(max_length=100, help_text="e.g., Security Guard, Security Manager")
    
    # Salary
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    
    # Experience & Vacancies
    experience_required = models.CharField(max_length=20, choices=EXPERIENCE_CHOICES)
    vacancies = models.IntegerField(default=1)
    
    # Status
    is_published = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    application_deadline = models.DateField(null=True, blank=True)
    
    # Metadata
    views_count = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'jobs'
        verbose_name = 'Job'
        verbose_name_plural = 'Jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['company']),
            models.Index(fields=['is_active', 'is_published']),
            models.Index(fields=['city']),
            models.Index(fields=['employment_type']),
        ]
    
    def __str__(self):
        return f"{self.title} at {self.company.name}"
    
    def increment_views(self):
        """Increment job view count"""
        self.views_count += 1
        self.save(update_fields=['views_count'])
    
    def is_deadline_passed(self):
        """Check if application deadline has passed"""
        if self.application_deadline:
            return timezone.now().date() > self.application_deadline
        return False
