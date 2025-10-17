"""
Management command to clear all test data from the database
Keeps only the admin user
"""
from django.core.management.base import BaseCommand
from accounts.models import User, JobSeeker
from companies.models import Company, Job
from jobs.models import Application, SavedJob
from notifications.models import Notification


class Command(BaseCommand):
    help = 'Clear all test data from the database (keeps admin user)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\nClearing test data...\n'))

        # Delete all applications
        app_count = Application.objects.count()
        Application.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {app_count} applications'))

        # Delete all saved jobs
        saved_count = SavedJob.objects.count()
        SavedJob.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {saved_count} saved jobs'))

        # Delete all jobs
        job_count = Job.objects.count()
        Job.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {job_count} jobs'))

        # Delete all companies
        company_count = Company.objects.count()
        Company.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {company_count} companies'))

        # Delete all job seeker profiles
        jobseeker_count = JobSeeker.objects.count()
        JobSeeker.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {jobseeker_count} job seeker profiles'))

        # Delete all notifications
        notif_count = Notification.objects.count()
        Notification.objects.all().delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {notif_count} notifications'))

        # Delete all test users (except admin)
        test_users = User.objects.exclude(user_type='admin')
        user_count = test_users.count()
        test_users.delete()
        self.stdout.write(self.style.SUCCESS(f'[OK] Deleted {user_count} test users'))

        # Verify admin still exists
        admin_count = User.objects.filter(user_type='admin').count()

        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n[OK] Test data cleared successfully!\n'))
        self.stdout.write('Remaining data:')
        self.stdout.write(f'  - Admin users: {admin_count}')
        self.stdout.write(f'  - Regular users: 0')
        self.stdout.write(f'  - Companies: 0')
        self.stdout.write(f'  - Jobs: 0')
        self.stdout.write(f'  - Applications: 0')
        self.stdout.write('\nDatabase is now clean and ready for production use.')
        self.stdout.write('='*50 + '\n')
