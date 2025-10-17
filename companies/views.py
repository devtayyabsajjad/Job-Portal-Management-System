"""
Views for company dashboard and job management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q
from django.db import transaction
from django.http import JsonResponse
from accounts.decorators import company_required, company_approved_required
from .models import Company, Job
from .forms import CompanyRegistrationForm, CompanyProfileForm, JobForm
from jobs.models import Application
from notifications.utils import notify_new_application

def company_register(request):
    """Company registration view"""
    if request.user.is_authenticated:
        if request.user.user_type == 'company':
            return redirect('company_dashboard')
        return redirect('home')
    
    if request.method == 'POST':
        form = CompanyRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                with transaction.atomic():
                    company = form.save()
                    login(request, company.user)
                    messages.success(request, 'Registration successful! Your application is pending admin approval.')
                    return redirect('company_dashboard')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompanyRegistrationForm()
    
    return render(request, 'companies/register.html', {'form': form})


def company_login(request):
    """Redirect to main login"""
    return redirect('login')


@login_required
@company_required
def company_dashboard(request):
    """Company dashboard with statistics"""
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    
    # Get statistics
    total_jobs = company.jobs.count()
    active_jobs = company.jobs.filter(is_active=True).count()
    total_applications = Application.objects.filter(company=company).count()
    pending_applications = Application.objects.filter(
        company=company, 
        status='applied'
    ).count()
    
    # Recent applications
    recent_applications = Application.objects.filter(
        company=company
    ).select_related('job', 'user').order_by('-applied_at')[:10]
    
    # Recent jobs
    recent_jobs = company.jobs.all().order_by('-created_at')[:5]
    
    context = {
        'company': company,
        'total_jobs': total_jobs,
        'active_jobs': active_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'recent_applications': recent_applications,
        'recent_jobs': recent_jobs,
    }
    return render(request, 'companies/dashboard.html', context)


@login_required
@company_required
def company_profile(request):
    """View company profile"""
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    
    return render(request, 'companies/profile.html', {'company': company})


@login_required
@company_required
def company_profile_edit(request):
    """Edit company profile"""
    try:
        company = request.user.company_profile
    except Company.DoesNotExist:
        messages.error(request, 'Company profile not found.')
        return redirect('home')
    
    if request.method == 'POST':
        form = CompanyProfileForm(request.POST, request.FILES, instance=company)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('company_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CompanyProfileForm(instance=company)
    
    return render(request, 'companies/profile_edit.html', {'form': form, 'company': company})


@login_required
@company_approved_required
def company_job_list(request):
    """List all jobs for the company"""
    company = request.user.company_profile
    jobs = company.jobs.all().annotate(
        application_count=Count('applications')
    ).order_by('-created_at')
    
    return render(request, 'companies/job_list.html', {'jobs': jobs, 'company': company})


@login_required
@company_approved_required
def job_create(request):
    """Create new job posting"""
    company = request.user.company_profile
    
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.company = company
            job.is_published = True
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('company_job_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm()
    
    return render(request, 'companies/job_form.html', {'form': form, 'action': 'Create'})


@login_required
@company_approved_required
def job_edit(request, pk):
    """Edit existing job posting"""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=pk, company=company)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('company_job_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobForm(instance=job)
    
    return render(request, 'companies/job_form.html', {
        'form': form, 
        'action': 'Edit',
        'job': job
    })


@login_required
@company_approved_required
def job_detail_company(request, pk):
    """View job details from company dashboard"""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=pk, company=company)
    
    applications = job.applications.all().select_related('user').order_by('-applied_at')
    
    context = {
        'job': job,
        'applications': applications,
        'total_applications': applications.count()
    }
    return render(request, 'companies/job_detail.html', context)


@login_required
@company_approved_required
def job_delete(request, pk):
    """Delete job posting"""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=pk, company=company)
    
    if request.method == 'POST':
        job_title = job.title
        job.delete()
        messages.success(request, f'Job "{job_title}" deleted successfully!')
        return redirect('company_job_list')
    
    return render(request, 'companies/job_confirm_delete.html', {'job': job})


@login_required
@company_approved_required
def job_toggle_status(request, pk):
    """Toggle job active status"""
    company = request.user.company_profile
    job = get_object_or_404(Job, pk=pk, company=company)
    
    job.is_active = not job.is_active
    job.save()
    
    status = 'activated' if job.is_active else 'deactivated'
    messages.success(request, f'Job "{job.title}" {status} successfully!')
    
    return redirect('company_job_list')


@login_required
@company_approved_required
def company_applications(request):
    """View all applications for company"""
    company = request.user.company_profile
    
    # Filter options
    status_filter = request.GET.get('status', '')
    job_filter = request.GET.get('job', '')
    
    applications = Application.objects.filter(company=company).select_related(
        'job', 'user', 'user__jobseeker_profile'
    )
    
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    if job_filter:
        applications = applications.filter(job_id=job_filter)
    
    applications = applications.order_by('-applied_at')
    
    # Get unique jobs for filter
    jobs = company.jobs.all()
    
    context = {
        'applications': applications,
        'jobs': jobs,
        'status_choices': Application.STATUS_CHOICES,
        'current_status': status_filter,
        'current_job': job_filter,
    }
    return render(request, 'companies/application_list.html', context)


@login_required
@company_approved_required
def application_detail(request, pk):
    """View single application detail"""
    company = request.user.company_profile
    application = get_object_or_404(
        Application.objects.select_related('job', 'user', 'user__jobseeker_profile'),
        pk=pk,
        company=company
    )
    
    context = {
        'application': application,
        'job': application.job,
        'applicant': application.user,
        'profile': application.user.jobseeker_profile
    }
    return render(request, 'companies/application_detail.html', context)


@login_required
@company_approved_required
def application_update_status(request, pk):
    """Update application status (AJAX)"""
    if request.method == 'POST':
        company = request.user.company_profile
        application = get_object_or_404(Application, pk=pk, company=company)
        
        new_status = request.POST.get('status')
        notes = request.POST.get('notes', '')
        
        if new_status in dict(Application.STATUS_CHOICES).keys():
            application.status = new_status
            if notes:
                application.notes = notes
            application.save()
            
            # Send notification to applicant
            from notifications.utils import notify_application_status_change
            notify_application_status_change(application)
            
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'success': True,
                    'message': 'Status updated successfully',
                    'new_status': application.get_status_display()
                })
            else:
                messages.success(request, 'Application status updated successfully!')
                return redirect('application_detail', pk=pk)
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'success': False, 'message': 'Invalid status'})
        else:
            messages.error(request, 'Invalid status')
            return redirect('application_detail', pk=pk)
    
    return redirect('company_applications')