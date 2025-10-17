"""
Custom decorators for role-based access control
"""
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from django.contrib import messages
from functools import wraps

def user_type_required(user_type):
    """
    Decorator to restrict access based on user type
    Usage: @user_type_required('admin')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            if request.user.user_type == user_type:
                return view_func(request, *args, **kwargs)
            else:
                messages.error(request, 'You do not have permission to access this page.')
                return redirect('home')
        return _wrapped_view
    return decorator


def admin_required(view_func):
    """Shortcut decorator for admin-only views"""
    return user_type_required('admin')(view_func)


def company_required(view_func):
    """Shortcut decorator for company-only views"""
    return user_type_required('company')(view_func)


def jobseeker_required(view_func):
    """Shortcut decorator for jobseeker-only views"""
    return user_type_required('jobseeker')(view_func)


def company_approved_required(view_func):
    """
    Decorator to ensure company is approved before accessing certain views
    """
    @wraps(view_func)
    @login_required
    @company_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            company = request.user.company_profile
            if company.status == 'approved':
                return view_func(request, *args, **kwargs)
            elif company.status == 'pending':
                messages.warning(request, 'Your company registration is pending approval.')
                return redirect('company_dashboard')
            else:  # rejected
                messages.error(request, 'Your company registration was rejected.')
                return redirect('company_dashboard')
        except:
            messages.error(request, 'Company profile not found.')
            return redirect('home')
    return _wrapped_view


def profile_complete_required(view_func):
    """
    Decorator to ensure job seeker has completed their profile before applying
    """
    @wraps(view_func)
    @login_required
    @jobseeker_required
    def _wrapped_view(request, *args, **kwargs):
        try:
            profile = request.user.jobseeker_profile
            if profile.resume:  # Check if resume is uploaded
                return view_func(request, *args, **kwargs)
            else:
                messages.warning(request, 'Please complete your profile and upload resume before applying.')
                return redirect('jobseeker_profile')
        except:
            messages.warning(request, 'Please create your profile first.')
            return redirect('jobseeker_profile')
    return _wrapped_view
