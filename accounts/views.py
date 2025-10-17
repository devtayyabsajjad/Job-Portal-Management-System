"""
Views for user authentication and profile management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db import transaction
from .forms import JobSeekerRegistrationForm, JobSeekerProfileForm, CustomLoginForm
from .models import User, JobSeeker
from .decorators import jobseeker_required

def user_login(request):
    """Handle user login with role-based redirection"""
    if request.user.is_authenticated:
        # Redirect based on user type
        if request.user.user_type == 'admin':
            return redirect('admin_dashboard')
        elif request.user.user_type == 'company':
            return redirect('company_dashboard')
        else:
            return redirect('home')
    
    if request.method == 'POST':
        form = CustomLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            user = authenticate(username=username, password=password)

            if user is not None:
                login(request, user)

                # Handle remember me
                if not remember_me:
                    request.session.set_expiry(0)  # Session expires on browser close
                else:
                    request.session.set_expiry(1209600)  # 2 weeks

                messages.success(request, f'Welcome back, {user.username}!')

                # Redirect based on user type
                if user.user_type == 'admin':
                    return redirect('admin_dashboard')
                elif user.user_type == 'company':
                    return redirect('company_dashboard')
                else:
                    # Redirect to next parameter or home
                    next_url = request.GET.get('next', 'home')
                    return redirect(next_url)
            else:
                messages.error(request, 'Invalid username or password.')
        else:
            messages.error(request, 'Invalid username or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def jobseeker_register(request):
    """Job seeker registration view"""
    if request.user.is_authenticated:
        return redirect('home')
    
    if request.method == 'POST':
        form = JobSeekerRegistrationForm(request.POST)
        if form.is_valid():
            try:
                with transaction.atomic():
                    user = form.save()
                    login(request, user)
                    messages.success(request, 'Registration successful! Please complete your profile.')
                    return redirect('jobseeker_profile_edit')
            except Exception as e:
                messages.error(request, f'Registration failed: {str(e)}')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobSeekerRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form})


@login_required
@jobseeker_required
def jobseeker_profile(request):
    """View job seeker profile"""
    try:
        profile = request.user.jobseeker_profile
    except JobSeeker.DoesNotExist:
        # Create profile if it doesn't exist
        profile = JobSeeker.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email
        )
        messages.info(request, 'Profile created. Please complete your information.')
        return redirect('jobseeker_profile_edit')
    
    context = {
        'profile': profile,
        'user': request.user
    }
    return render(request, 'accounts/profile.html', context)


@login_required
@jobseeker_required
def jobseeker_profile_edit(request):
    """Edit job seeker profile"""
    try:
        profile = request.user.jobseeker_profile
    except JobSeeker.DoesNotExist:
        profile = JobSeeker.objects.create(
            user=request.user,
            full_name=request.user.get_full_name() or request.user.username,
            email=request.user.email
        )
    
    if request.method == 'POST':
        form = JobSeekerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully!')
            return redirect('jobseeker_profile')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = JobSeekerProfileForm(instance=profile)
    
    context = {
        'form': form,
        'profile': profile
    }
    return render(request, 'accounts/profile_edit.html', context)
