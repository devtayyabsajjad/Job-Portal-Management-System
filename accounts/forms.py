"""
Forms for user authentication and profiles
"""
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.exceptions import ValidationError
from accounts.models import User, JobSeeker

class UserRegistrationForm(UserCreationForm):
    """Base user registration form"""
    
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    phone = forms.CharField(
        max_length=15,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Phone Number'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phone', 'password1', 'password2']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['password1'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Confirm Password'})
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise ValidationError('This email is already registered.')
        return email


class JobSeekerRegistrationForm(UserRegistrationForm):
    """Job seeker registration form"""
    
    full_name = forms.CharField(
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full Name'})
    )
    
    class Meta(UserRegistrationForm.Meta):
        fields = ['username', 'email', 'phone', 'full_name', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.user_type = 'jobseeker'
        if commit:
            user.save()
            # Create JobSeeker profile
            JobSeeker.objects.create(
                user=user,
                full_name=self.cleaned_data['full_name'],
                email=user.email,
                phone=self.cleaned_data.get('phone', '')
            )
        return user


class JobSeekerProfileForm(forms.ModelForm):
    """Job seeker profile edit form"""
    
    class Meta:
        model = JobSeeker
        fields = ['full_name', 'email', 'phone', 'address', 'city', 'date_of_birth', 
                  'skills', 'education', 'experience', 'resume']
        widgets = {
            'full_name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'date_of_birth': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'skills': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 
                                           'placeholder': 'e.g., Security Management, CCTV Operation, First Aid'}),
            'education': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'experience': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'resume': forms.FileInput(attrs={'class': 'form-control', 'accept': '.pdf'}),
        }
    
    def clean_resume(self):
        resume = self.cleaned_data.get('resume')
        if resume:
            if resume.size > 5 * 1024 * 1024:  # 5MB
                raise ValidationError('Resume file size must be under 5MB.')
            if not resume.name.endswith('.pdf'):
                raise ValidationError('Only PDF files are accepted for resumes.')
        return resume


class CustomLoginForm(AuthenticationForm):
    """Custom login form with Bootstrap styling and remember me"""

    username = forms.CharField(
        label='Username or Email',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your username or email',
            'autofocus': True
        })
    )
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })
    )
    remember_me = forms.BooleanField(
        required=False,
        initial=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
