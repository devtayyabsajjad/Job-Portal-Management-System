"""
Management command to create an admin user
"""
from django.core.management.base import BaseCommand
from accounts.models import User


class Command(BaseCommand):
    help = 'Create an admin user for the job portal'

    def handle(self, *args, **options):
        # Check if admin already exists
        if User.objects.filter(user_type='admin').exists():
            self.stdout.write(
                self.style.WARNING('Admin user already exists!')
            )
            admin = User.objects.filter(user_type='admin').first()
            self.stdout.write(
                self.style.SUCCESS(f'Existing admin: {admin.username}')
            )
            return

        # Create admin user
        admin = User.objects.create_superuser(
            username='admin',
            email='admin@jobportal.com',
            password='admin123',
            user_type='admin'
        )

        self.stdout.write(
            self.style.SUCCESS('Successfully created admin user!')
        )
        self.stdout.write(
            self.style.SUCCESS(f'Username: {admin.username}')
        )
        self.stdout.write(
            self.style.SUCCESS('Password: admin123')
        )
        self.stdout.write(
            self.style.WARNING('\nIMPORTANT: Please change this password after first login!')
        )
