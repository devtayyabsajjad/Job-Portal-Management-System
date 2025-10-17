"""
Views for admin dashboard
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.utils import timezone
from accounts.decorators import admin_required
from accounts.models import User, JobSeeker
from companies.models import Company, Job
from jobs.models import Application
from notifications.utils import notify_company_approved, notify_company_rejected

@login_required
@admin_required
def admin_dashboard(request):
    """Main admin dashboard with statistics"""
    # Company statistics
    total_companies = Company.objects.count()
    pending_companies = Company.objects.filter(status='pending').count()
    approved_companies = Company.objects.filter(status='approved').count()
    rejected_companies = Company.objects.filter(status='rejected').count()
    
    # Job statistics
    total_jobs = Job.objects.count()
    active_jobs = Job.objects.filter(is_active=True, is_published=True).count()
    inactive_jobs = Job.objects.filter(is_active=False).count()
    
    # Application statistics
    total_applications = Application.objects.count()
    pending_applications = Application.objects.filter(status='applied').count()
    
    # User statistics
    total_jobseekers = User.objects.filter(user_type='jobseeker').count()
    
    # Recent activities
    recent_companies = Company.objects.all().order_by('-created_at')[:5]
    recent_jobs = Job.objects.select_related('company').order_by('-created_at')[:5]
    recent_applications = Application.objects.select_related(
        'job', 'user', 'company'
    ).order_by('-applied_at')[:10]
    
    context = {
        'total_companies': total_companies,
        'pending_companies': pending_companies,
        'approved_companies': approved_companies,
        'rejected_companies': rejected_companies,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'inactive_jobs': inactive_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'total_jobseekers': total_jobseekers,
        'recent_companies': recent_companies,
        'recent_jobs': recent_jobs,
        'recent_applications': recent_applications,
    }
    return render(request, 'admin_panel/dashboard.html', context)


@login_required
@admin_required
def admin_company_list(request):
    """List all companies with filters"""
    companies = Company.objects.all().select_related('user')
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    if status_filter:
        companies = companies.filter(status=status_filter)
    
    if search_query:
        companies = companies.filter(
            Q(name__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(registration_number__icontains=search_query)
        )
    
    companies = companies.order_by('-created_at')
    
    context = {
        'companies': companies,
        'status_filter': status_filter,
        'search_query': search_query,
        'status_choices': Company.STATUS_CHOICES,
    }
    return render(request, 'admin_panel/company_list.html', context)


@login_required
@admin_required
def admin_company_detail(request, pk):
    """View company details"""
    company = get_object_or_404(Company.objects.select_related('user'), pk=pk)
    
    # Get company statistics
    total_jobs = company.jobs.count()
    active_jobs = company.jobs.filter(is_active=True).count()
    total_applications = Application.objects.filter(company=company).count()
    
    # Get recent jobs
    recent_jobs = company.jobs.all().order_by('-created_at')[:5]
    
    context = {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'admin_panel/company_detail.html', context)


@login_required
@admin_required
def admin_company_approve(request, pk):
    """Approve company registration"""
    if request.method == 'POST':
        company = get_object_or_404(Company, pk=pk)
        
        if company.status == 'approved':
            messages.warning(request, 'Company is already approved.')
        else:
            company.approve(request.user)
            
            # Send notification
            notify_company_approved(company)
            
            messages.success(request, f'Company "{company.name}" approved successfully!')
        
        return redirect('admin_company_detail', pk=pk)
    
    return redirect('admin_company_list')


@login_required
@admin_required
def admin_company_reject(request, pk):
    """Reject company registration"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        reason = request.POST.get('reason', '')
        
        if not reason:
            messages.error(request, 'Please provide a rejection reason.')
            return redirect('admin_company_detail', pk=pk)
        
        if company.status == 'rejected':
            messages.warning(request, 'Company is already rejected.')
        else:
            company.reject(reason, request.user)
            
            # Send notification
            notify_company_rejected(company)
            
            messages.success(request, f'Company "{company.name}" rejected.')
        
        return redirect('admin_company_detail', pk=pk)
    
    return render(request, 'admin_panel/company_reject_form.html', {'company': company})


@login_required
@admin_required
def admin_company_delete(request, pk):
    """Delete company"""
    company = get_object_or_404(Company, pk=pk)
    
    if request.method == 'POST':
        company_name = company.name
        user = company.user
        
        # Delete company (will cascade delete jobs and applications)
        company.delete()
        user.delete()  # Also delete user account
        
        messages.success(request, f'Company "{company_name}" and all related data deleted successfully!')
        return redirect('admin_company_list')
    
    return render(request, 'admin_panel/company_confirm_delete.html', {'company': company})


@login_required
@admin_required
def admin_job_list(request):
    """List all jobs across all companies"""
    jobs = Job.objects.all().select_related('company').annotate(
        application_count=Count('applications')
    )
    
    # Apply filters
    status_filter = request.GET.get('status', '')
    company_filter = request.GET.get('company', '')
    search_query = request.GET.get('search', '')
    
    if status_filter == 'active':
        jobs = jobs.filter(is_active=True)
    elif status_filter == 'inactive':
        jobs = jobs.filter(is_active=False)
    
    if company_filter:
        jobs = jobs.filter(company_id=company_filter)
    
    if search_query:
        jobs = jobs.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(company__name__icontains=search_query)
        )
    
    jobs = jobs.order_by('-created_at')
    
    # Get all companies for filter
    companies = Company.objects.filter(status='approved').order_by('name')
    
    context = {
        'jobs': jobs,
        'companies': companies,
        'status_filter': status_filter,
        'company_filter': company_filter,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/job_list.html', context)


@login_required
@admin_required
def admin_job_detail(request, pk):
    """View job details"""
    job = get_object_or_404(Job.objects.select_related('company'), pk=pk)
    
    # Get applications for this job
    applications = Application.objects.filter(job=job).select_related('user')
    
    context = {
        'job': job,
        'applications': applications,
        'total_applications': applications.count(),
    }
    return render(request, 'admin_panel/job_detail.html', context)


@login_required
@admin_required
def admin_job_deactivate(request, pk):
    """Deactivate/activate job"""
    if request.method == 'POST':
        job = get_object_or_404(Job, pk=pk)
        job.is_active = not job.is_active
        job.save()
        
        status = 'activated' if job.is_active else 'deactivated'
        messages.success(request, f'Job "{job.title}" {status} successfully!')
        
        return redirect('admin_job_detail', pk=pk)
    
    return redirect('admin_job_list')


@login_required
@admin_required
def admin_job_delete(request, pk):
    """Delete job posting"""
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect('admin_job_list')
    
    return render(request, 'admin_panel/job_confirm_delete.html', {'job': job})


@login_required
@admin_required
def admin_user_list(request):
    """List all job seekers"""
    users = User.objects.filter(user_type='jobseeker').select_related('jobseeker_profile')
    
    # Apply search filter
    search_query = request.GET.get('search', '')
    if search_query:
        users = users.filter(
            Q(username__icontains=search_query) |
            Q(email__icontains=search_query) |
            Q(jobseeker_profile__full_name__icontains=search_query)
        )
    
    users = users.order_by('-date_joined')
    
    context = {
        'users': users,
        'search_query': search_query,
    }
    return render(request, 'admin_panel/user_list.html', context)


@login_required
@admin_required
def admin_user_toggle_status(request, pk):
    """Toggle user active status (ban/unban)"""
    if request.method == 'POST':
        user = get_object_or_404(User, pk=pk, user_type='jobseeker')
        user.is_active = not user.is_active
        user.save()
        
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User "{user.username}" {status} successfully!')
        
        return redirect('admin_user_list')
    
    return redirect('admin_user_list')


@login_required
@admin_required
def admin_statistics(request):
    """Detailed statistics and analytics"""
    from datetime import timedelta
    from django.db.models.functions import TruncDate
    
    # Get date range (last 30 days)
    end_date = timezone.now()
    start_date = end_date - timedelta(days=30)
    
    # Applications over time
    applications_by_date = Application.objects.filter(
        applied_at__gte=start_date
    ).annotate(
        date=TruncDate('applied_at')
    ).values('date').annotate(
        count=Count('id')
    ).order_by('date')
    
    # Jobs by category
    jobs_by_category = Job.objects.values('category').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Top companies by applications
    top_companies = Company.objects.annotate(
        app_count=Count('received_applications')
    ).order_by('-app_count')[:10]
    
    context = {
        'applications_by_date': applications_by_date,
        'jobs_by_category': jobs_by_category,
        'top_companies': top_companies,
    }
    return render(request, 'admin_panel/statistics.html', context)
