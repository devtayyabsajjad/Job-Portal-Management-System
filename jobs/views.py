"""
Views for public job listings and applications
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from companies.models import Job, Company
from companies.forms import JobSearchForm
from .models import Application, SavedJob
from .forms import JobApplicationForm
from accounts.decorators import jobseeker_required, profile_complete_required
from notifications.utils import notify_new_application

def home(request):
    """Homepage with featured jobs"""
    # Get recent and featured jobs
    featured_jobs = Job.objects.filter(
        is_active=True,
        is_published=True,
        company__status='approved'
    ).select_related('company').order_by('-created_at')[:6]
    
    # Get statistics
    total_jobs = Job.objects.filter(is_active=True, is_published=True).count()
    total_companies = Company.objects.filter(status='approved').count()
    
    context = {
        'featured_jobs': featured_jobs,
        'total_jobs': total_jobs,
        'total_companies': total_companies,
    }
    return render(request, 'home.html', context)


def job_list(request):
    """Job listing page with search and filters"""
    jobs = Job.objects.filter(
        is_active=True,
        is_published=True,
        company__status='approved'
    ).select_related('company').annotate(
        application_count=Count('applications')
    )
    
    # Initialize search form
    form = JobSearchForm(request.GET)
    
    # Apply filters
    if form.is_valid():
        # Keyword search
        keyword = form.cleaned_data.get('keyword')
        if keyword:
            jobs = jobs.filter(
                Q(title__icontains=keyword) |
                Q(description__icontains=keyword) |
                Q(category__icontains=keyword) |
                Q(company__name__icontains=keyword)
            )
        
        # Location filter
        location = form.cleaned_data.get('location')
        if location:
            jobs = jobs.filter(
                Q(city__icontains=location) |
                Q(location__icontains=location)
            )
        
        # Job type filter
        employment_type = form.cleaned_data.get('employment_type')
        if employment_type:
            jobs = jobs.filter(employment_type=employment_type)
        
        # Category filter
        category = form.cleaned_data.get('category')
        if category:
            jobs = jobs.filter(category__icontains=category)
        
        # Experience filter
        experience = form.cleaned_data.get('experience')
        if experience:
            jobs = jobs.filter(experience_required=experience)
        
        # Sorting
        sort_by = form.cleaned_data.get('sort_by') or '-created_at'
        jobs = jobs.order_by(sort_by)
    else:
        jobs = jobs.order_by('-created_at')
    
    # Pagination
    paginator = Paginator(jobs, 20)  # 20 jobs per page
    page_number = request.GET.get('page')
    jobs_page = paginator.get_page(page_number)
    
    # Get unique categories for filter
    categories = Job.objects.filter(
        is_active=True
    ).values_list('category', flat=True).distinct()
    
    context = {
        'jobs': jobs_page,
        'form': form,
        'categories': categories,
        'total_results': paginator.count,
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk):
    """Job detail page"""
    job = get_object_or_404(
        Job.objects.select_related('company'),
        pk=pk,
        is_active=True,
        is_published=True
    )
    
    # Increment view count
    job.increment_views()
    
    # Check if user has applied
    has_applied = False
    is_saved = False
    
    if request.user.is_authenticated and request.user.user_type == 'jobseeker':
        has_applied = Application.objects.filter(
            job=job,
            user=request.user
        ).exists()
        
        is_saved = SavedJob.objects.filter(
            job=job,
            user=request.user
        ).exists()
    
    # Get similar jobs
    similar_jobs = Job.objects.filter(
        category=job.category,
        is_active=True,
        is_published=True
    ).exclude(pk=job.pk).select_related('company')[:4]
    
    context = {
        'job': job,
        'company': job.company,
        'has_applied': has_applied,
        'is_saved': is_saved,
        'similar_jobs': similar_jobs,
    }
    return render(request, 'jobs/job_detail.html', context)


@login_required
@jobseeker_required
@profile_complete_required
def job_apply(request, pk):
    """Apply for a job"""
    job = get_object_or_404(Job, pk=pk, is_active=True, is_published=True)
    
    # Check if already applied
    if Application.objects.filter(job=job, user=request.user).exists():
        messages.warning(request, 'You have already applied for this job.')
        return redirect('job_detail', pk=pk)
    
    # Check if deadline passed
    if job.is_deadline_passed():
        messages.error(request, 'The application deadline for this job has passed.')
        return redirect('job_detail', pk=pk)
    
    if request.method == 'POST':
        form = JobApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.user = request.user
            application.company = job.company
            application.save()
            
            # Send notification to company
            notify_new_application(application)
            
            messages.success(request, 'Application submitted successfully!')
            return redirect('my_applications')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pre-fill resume from profile if available
        initial_data = {}
        try:
            profile = request.user.jobseeker_profile
            if profile.resume:
                initial_data['resume_url'] = profile.resume
        except:
            pass
        
        form = JobApplicationForm(initial=initial_data)
    
    context = {
        'form': form,
        'job': job,
        'company': job.company
    }
    return render(request, 'jobs/job_apply.html', context)


@login_required
@jobseeker_required
def my_applications(request):
    """View user's job applications"""
    applications = Application.objects.filter(
        user=request.user
    ).select_related('job', 'company').order_by('-applied_at')
    
    # Filter by status
    status_filter = request.GET.get('status')
    if status_filter:
        applications = applications.filter(status=status_filter)
    
    context = {
        'applications': applications,
        'status_choices': Application.STATUS_CHOICES,
        'current_status': status_filter or '',
    }
    return render(request, 'jobs/my_applications.html', context)


@login_required
@jobseeker_required
def saved_jobs(request):
    """View saved/bookmarked jobs"""
    saved = SavedJob.objects.filter(
        user=request.user
    ).select_related('job', 'job__company').order_by('-saved_date')
    
    context = {
        'saved_jobs': saved,
    }
    return render(request, 'jobs/saved_jobs.html', context)


@login_required
@jobseeker_required
@require_POST
def save_job(request, pk):
    """Save/bookmark a job (AJAX)"""
    job = get_object_or_404(Job, pk=pk)
    
    saved_job, created = SavedJob.objects.get_or_create(
        user=request.user,
        job=job
    )
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'saved': created,
            'message': 'Job saved successfully!' if created else 'Job already saved'
        })
    
    if created:
        messages.success(request, 'Job saved successfully!')
    else:
        messages.info(request, 'Job already saved.')
    
    return redirect('job_detail', pk=pk)


@login_required
@jobseeker_required
@require_POST
def unsave_job(request, pk):
    """Remove job from saved list (AJAX)"""
    job = get_object_or_404(Job, pk=pk)
    
    deleted_count, _ = SavedJob.objects.filter(
        user=request.user,
        job=job
    ).delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({
            'success': True,
            'message': 'Job removed from saved list'
        })
    
    if deleted_count:
        messages.success(request, 'Job removed from saved list.')
    
    return redirect('saved_jobs')


def about(request):
    """About page with statistics"""
    from accounts.models import User

    # Get statistics
    total_jobs = Job.objects.filter(is_active=True, is_published=True).count()
    total_companies = Company.objects.filter(status='approved').count()
    total_users = User.objects.filter(user_type='jobseeker', is_active=True).count()
    total_applications = Application.objects.count()

    context = {
        'total_jobs': total_jobs,
        'total_companies': total_companies,
        'total_users': total_users,
        'total_applications': total_applications,
    }
    return render(request, 'jobs/about.html', context)


def contact(request):
    """Contact page"""
    if request.method == 'POST':
        # Handle contact form submission
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')
        
        # You can send email or save to database here
        messages.success(request, 'Thank you for contacting us! We will get back to you soon.')
        return redirect('contact')
    
    return render(request, 'jobs/contact.html')


def custom_404(request, exception):
    """Custom 404 error page"""
    return render(request, '404.html', status=404)


def custom_500(request):
    """Custom 500 error page"""
    return render(request, '500.html', status=500)
