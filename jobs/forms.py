"""
Forms for Job Applications
"""
from django import forms
from django.core.exceptions import ValidationError
from jobs.models import Application

class JobApplicationForm(forms.ModelForm):
    """Form for applying to jobs"""
    
    class Meta:
        model = Application
        fields = ['resume_url', 'cover_letter']
        widgets = {
            'resume_url': forms.FileInput(attrs={
                'class': 'form-control', 
                'accept': '.pdf',
                'help_text': 'Upload your resume (PDF only, max 5MB)'
            }),
            'cover_letter': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 6,
                'placeholder': 'Write a compelling cover letter explaining why you are the perfect fit for this position...',
                'minlength': '100'
            }),
        }
        labels = {
            'resume_url': 'Resume (PDF)',
            'cover_letter': 'Cover Letter',
        }
    
    def clean_resume_url(self):
        resume = self.cleaned_data.get('resume_url')
        if resume:
            # Check file size (5MB max)
            if resume.size > 5 * 1024 * 1024:
                raise ValidationError('Resume file size must be under 5MB.')
            
            # Check file extension
            if not resume.name.lower().endswith('.pdf'):
                raise ValidationError('Only PDF files are accepted for resumes.')
        else:
            raise ValidationError('Resume is required.')
        
        return resume
    
    def clean_cover_letter(self):
        cover_letter = self.cleaned_data.get('cover_letter')
        if cover_letter and len(cover_letter) < 100:
            raise ValidationError('Cover letter must be at least 100 characters long.')
        return cover_letter


class ApplicationStatusForm(forms.ModelForm):
    """Form for company to update application status"""
    
    class Meta:
        model = Application
        fields = ['status', 'notes']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'}),
            'notes': forms.Textarea(attrs={
                'class': 'form-control', 
                'rows': 3,
                'placeholder': 'Add internal notes about this application...'
            }),
        }
