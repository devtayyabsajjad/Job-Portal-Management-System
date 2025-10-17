"""
Management command to create test data for the job portal
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from accounts.models import User, JobSeeker
from companies.models import Company, Job
from jobs.models import Application, SavedJob


class Command(BaseCommand):
    help = 'Create test data for the job portal (companies, jobs, users, applications)'

    def handle(self, *args, **options):
        self.stdout.write(self.style.WARNING('\nCreating test data...\n'))

        # Create test job seekers
        self.stdout.write('Creating job seekers...')
        jobseekers = []
        for i in range(1, 6):
            try:
                user = User.objects.create_user(
                    username=f'jobseeker{i}',
                    email=f'jobseeker{i}@test.com',
                    password='test123',
                    user_type='jobseeker'
                )
                profile = JobSeeker.objects.create(
                    user=user,
                    full_name=f'Job Seeker {i}',
                    email=user.email,
                    phone=f'+1234567890{i}',
                    city='New York',
                    address='123 Test Street',
                    skills='Python, Django, JavaScript, React',
                    education='Bachelor in Computer Science',
                    experience='2 years of experience in web development'
                )
                jobseekers.append(user)
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created jobseeker{i}'))
            except:
                user = User.objects.get(username=f'jobseeker{i}')
                jobseekers.append(user)
                self.stdout.write(self.style.WARNING(f'  - jobseeker{i} already exists'))

        # Create test companies
        self.stdout.write('\nCreating companies...')
        companies = []
        company_names = ['Tech Corp', 'Digital Solutions', 'Innovation Labs', 'Future Systems']

        for i, name in enumerate(company_names, 1):
            try:
                user = User.objects.create_user(
                    username=f'company{i}',
                    email=f'company{i}@test.com',
                    password='test123',
                    user_type='company'
                )
                company = Company.objects.create(
                    user=user,
                    name=name,
                    email=user.email,
                    phone=f'+1987654321{i}',
                    website=f'https://www.{name.lower().replace(" ", "")}.com',
                    about=f'{name} is a leading technology company focusing on innovation and excellence.',
                    address=f'{100+i} Business Avenue',
                    city='San Francisco',
                    state='CA',
                    registration_number=f'REG{1000+i}',
                    status='approved',  # Auto-approve for testing
                    is_verified=True
                )
                companies.append(company)
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created {name}'))
            except:
                user = User.objects.get(username=f'company{i}')
                company = Company.objects.get(user=user)
                companies.append(company)
                self.stdout.write(self.style.WARNING(f'  - {name} already exists'))

        # Create test jobs
        self.stdout.write('\nCreating jobs...')
        jobs_data = [
            {
                'title': 'Senior Python Developer',
                'category': 'Software Development',
                'employment_type': 'full-time',
                'location': 'San Francisco, CA',
                'city': 'San Francisco',
                'experience_required': '3-5',
                'salary_min': 80000,
                'salary_max': 120000,
                'vacancies': 2,
            },
            {
                'title': 'Frontend React Developer',
                'category': 'Software Development',
                'employment_type': 'full-time',
                'location': 'Remote',
                'city': 'Remote',
                'experience_required': '1-3',
                'salary_min': 60000,
                'salary_max': 90000,
                'vacancies': 3,
            },
            {
                'title': 'DevOps Engineer',
                'category': 'IT',
                'employment_type': 'full-time',
                'location': 'New York, NY',
                'city': 'New York',
                'experience_required': '3-5',
                'salary_min': 90000,
                'salary_max': 130000,
                'vacancies': 1,
            },
            {
                'title': 'Junior Full Stack Developer',
                'category': 'Software Development',
                'employment_type': 'full-time',
                'location': 'Austin, TX',
                'city': 'Austin',
                'experience_required': '0-1',
                'salary_min': 50000,
                'salary_max': 70000,
                'vacancies': 5,
            },
            {
                'title': 'Product Manager',
                'category': 'Management',
                'employment_type': 'full-time',
                'location': 'Seattle, WA',
                'city': 'Seattle',
                'experience_required': '5+',
                'salary_min': 100000,
                'salary_max': 150000,
                'vacancies': 1,
            },
            {
                'title': 'UI/UX Designer',
                'category': 'Design',
                'employment_type': 'contract',
                'location': 'Los Angeles, CA',
                'city': 'Los Angeles',
                'experience_required': '1-3',
                'salary_min': 55000,
                'salary_max': 85000,
                'vacancies': 2,
            },
        ]

        jobs_list = []
        for i, job_data in enumerate(jobs_data):
            company = companies[i % len(companies)]
            try:
                job = Job.objects.create(
                    company=company,
                    title=job_data['title'],
                    slug=job_data['title'].lower().replace(' ', '-') + f'-{i}',
                    description=f"We are looking for a talented {job_data['title']} to join our team. This is an exciting opportunity to work with cutting-edge technologies and make a real impact.",
                    requirements=f"- {job_data['experience_required']} years of experience\n- Strong communication skills\n- Team player\n- Problem-solving abilities",
                    responsibilities="- Develop and maintain applications\n- Collaborate with team members\n- Write clean, maintainable code\n- Participate in code reviews",
                    category=job_data['category'],
                    employment_type=job_data['employment_type'],
                    location=job_data['location'],
                    city=job_data['city'],
                    experience_required=job_data['experience_required'],
                    salary_min=job_data['salary_min'],
                    salary_max=job_data['salary_max'],
                    vacancies=job_data['vacancies'],
                    is_published=True,
                    is_active=True,
                    application_deadline=timezone.now() + timedelta(days=30)
                )
                jobs_list.append(job)
                self.stdout.write(self.style.SUCCESS(f'  [OK] Created {job.title}'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'  - Error creating job: {str(e)}'))

        # Create some applications
        self.stdout.write('\nCreating job applications...')
        app_count = 0
        for i, jobseeker in enumerate(jobseekers[:3]):  # First 3 job seekers
            for j, job in enumerate(jobs_list[:2]):  # Apply to first 2 jobs each
                try:
                    application = Application.objects.create(
                        job=job,
                        user=jobseeker,
                        company=job.company,
                        cover_letter=f"I am very interested in the {job.title} position. I believe my skills and experience make me a great fit for this role.",
                        status=['applied', 'under_review', 'shortlisted'][j % 3]
                    )
                    app_count += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {app_count} applications'))

        # Create some saved jobs
        self.stdout.write('\nCreating saved jobs...')
        saved_count = 0
        for jobseeker in jobseekers[:2]:
            for job in jobs_list[2:4]:
                try:
                    SavedJob.objects.create(
                        user=jobseeker,
                        job=job
                    )
                    saved_count += 1
                except:
                    pass

        self.stdout.write(self.style.SUCCESS(f'  [OK] Created {saved_count} saved jobs'))

        # Summary
        self.stdout.write('\n' + '='*50)
        self.stdout.write(self.style.SUCCESS('\n[OK] Test data created successfully!\n'))
        self.stdout.write('Summary:')
        self.stdout.write(f'  - Job Seekers: {len(jobseekers)}')
        self.stdout.write(f'  - Companies: {len(companies)}')
        self.stdout.write(f'  - Jobs: {len(jobs_list)}')
        self.stdout.write(f'  - Applications: {app_count}')
        self.stdout.write(f'  - Saved Jobs: {saved_count}')
        self.stdout.write('\nTest Credentials:')
        self.stdout.write('  Admin: admin / admin123')
        self.stdout.write('  Job Seekers: jobseeker1-5 / test123')
        self.stdout.write('  Companies: company1-4 / test123')
        self.stdout.write('='*50 + '\n')
