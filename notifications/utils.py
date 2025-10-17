"""
Utility functions for notifications
"""
from .models import Notification


def notify_new_application(application):
    """
    Create a notification when a new job application is submitted
    """
    try:
        # Notify the company about the new application
        Notification.objects.create(
            user=application.company.user,
            title='New Job Application',
            message=f'New application received for {application.job.title} from {application.user.username}',
            notification_type='application'
        )
    except Exception as e:
        # Log error but don't raise to prevent application submission from failing
        print(f"Error creating notification: {e}")


def notify_application_status_change(application, old_status, new_status):
    """
    Create a notification when application status changes
    """
    try:
        status_messages = {
            'under_review': 'Your application is now under review',
            'shortlisted': 'Congratulations! You have been shortlisted',
            'interview_scheduled': 'An interview has been scheduled for your application',
            'accepted': 'Congratulations! Your application has been accepted',
            'rejected': 'Unfortunately, your application was not successful this time'
        }

        message = status_messages.get(
            new_status,
            f'Your application status has been updated to {new_status}'
        )

        Notification.objects.create(
            user=application.user,
            title=f'Application Status Updated - {application.job.title}',
            message=message,
            notification_type='status_change'
        )
    except Exception as e:
        print(f"Error creating notification: {e}")


def notify_company_approved(company):
    """
    Create a notification when a company is approved
    """
    try:
        Notification.objects.create(
            user=company.user,
            title='Company Approved',
            message=f'Your company "{company.name}" has been approved! You can now start posting jobs.',
            notification_type='approval'
        )
    except Exception as e:
        print(f"Error creating notification: {e}")


def notify_company_rejected(company, reason=''):
    """
    Create a notification when a company is rejected
    """
    try:
        message = f'Your company registration for "{company.name}" has been rejected.'
        if reason:
            message += f' Reason: {reason}'

        Notification.objects.create(
            user=company.user,
            title='Company Registration Rejected',
            message=message,
            notification_type='rejection'
        )
    except Exception as e:
        print(f"Error creating notification: {e}")


def notify_job_posted(job):
    """
    Create a notification when a job is successfully posted
    """
    try:
        Notification.objects.create(
            user=job.company.user,
            title='Job Posted Successfully',
            message=f'Your job posting "{job.title}" is now live and visible to job seekers.',
            notification_type='job_posted'
        )
    except Exception as e:
        print(f"Error creating notification: {e}")
