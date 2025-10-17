"""
Forms for Company and Job Management
"""
from django import forms
from django.core.exceptions import ValidationError
from companies.models import Company, Job
from accounts.models import User

class CompanyRegistrationForm(forms.ModelForm):
    """Company registration form"""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'})
    )
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'})
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Confirm Password'})
    )
    
    class Meta:
        model = Company
        fields = ['name', 'registration_number', 'email', 'phone', 'website', 
                  'address', 'city', 'state', 'about', 'company_logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Company Name'}),
            'registration_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Registration Number'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Company Email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'}),
            'website': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.example.com'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'state': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State/Province'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell us about your company...'}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
        }
    
    def clean_username(self):
        username = self.cleaned_data.get('username')
        if User.objects.filter(username=username).exists():
            raise ValidationError('This username is already taken.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if Company.objects.filter(email=email).exists():
            raise ValidationError('A company with this email already exists.')
        return email
    
    def clean_registration_number(self):
        reg_num = self.cleaned_data.get('registration_number')
        if Company.objects.filter(registration_number=reg_num).exists():
            raise ValidationError('This registration number is already registered.')
        return reg_num
    
    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('password1')
        password2 = cleaned_data.get('password2')
        
        if password1 and password2 and password1 != password2:
            raise ValidationError('Passwords do not match.')
        
        if password1 and len(password1) < 8:
            raise ValidationError('Password must be at least 8 characters long.')
        
        return cleaned_data
    
    def save(self, commit=True):
        # Create user account
        user = User.objects.create_user(
            username=self.cleaned_data['username'],
            email=self.cleaned_data['email'],
            password=self.cleaned_data['password1'],
            user_type='company'
        )
        
        # Create company profile
        company = super().save(commit=False)
        company.user = user
        
        if commit:
            company.save()
        
        return company


class CompanyProfileForm(forms.ModelForm):
    """Form for editing company profile"""
    
    class Meta:
        model = Company
        fields = ['name', 'email', 'phone', 'website', 'address', 'city', 
                  'state', 'about', 'company_logo']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'state': forms.TextInput(attrs={'class': 'form-control'}),
            'about': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'company_logo': forms.FileInput(attrs={'class': 'form-control'}),
        }


class JobForm(forms.ModelForm):
    """Form for creating and editing job postings"""
    
    class Meta:
        model = Job
        fields = ['title', 'description', 'requirements', 'responsibilities', 
                  'location', 'city', 'employment_type', 'category', 
                  'salary_min', 'salary_max', 'experience_required', 
                  'vacancies', 'application_deadline', 'is_active']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Security Guard'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 
                                                 'placeholder': 'Detailed job description...'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 
                                                  'placeholder': 'Required qualifications and skills...'}),
            'responsibilities': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 
                                                      'placeholder': 'Key responsibilities...'}),
            'location': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Address'}),
            'city': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City'}),
            'employment_type': forms.Select(attrs={'class': 'form-select'}),
            'category': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g., Security Guard, Manager'}),
            'salary_min': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Minimum Salary'}),
            'salary_max': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Maximum Salary'}),
            'experience_required': forms.Select(attrs={'class': 'form-select'}),
            'vacancies': forms.NumberInput(attrs={'class': 'form-control', 'min': '1', 'value': '1'}),
            'application_deadline': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        salary_min = cleaned_data.get('salary_min')
        salary_max = cleaned_data.get('salary_max')
        
        if salary_min and salary_max and salary_min > salary_max:
            raise ValidationError('Minimum salary cannot be greater than maximum salary.')
        
        return cleaned_data


class JobSearchForm(forms.Form):
    """Advanced job search and filter form"""
    
    keyword = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Job title, keywords...'})
    )
    location = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City or location'})
    )
    employment_type = forms.ChoiceField(
        required=False,
        choices=[('', 'All Job Types')] + list(Job.JOB_TYPE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    category = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Category'})
    )
    experience = forms.ChoiceField(
        required=False,
        choices=[('', 'Any Experience')] + list(Job.EXPERIENCE_CHOICES),
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    sort_by = forms.ChoiceField(
        required=False,
        choices=[
            ('-created_at', 'Newest First'),
            ('created_at', 'Oldest First'),
            ('title', 'Title A-Z'),
            ('-title', 'Title Z-A'),
        ],
        widget=forms.Select(attrs={'class': 'form-select'})
    )
