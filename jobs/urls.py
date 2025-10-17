"""
URL configuration for jobs app (public-facing)
"""
from django.urls import path
from . import views

urlpatterns = [
    # Public Pages
    path('', views.home, name='home'),
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/<uuid:pk>/', views.job_detail, name='job_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    
    # Job Application
    path('jobs/<uuid:pk>/apply/', views.job_apply, name='job_apply'),
    path('my-applications/', views.my_applications, name='my_applications'),
    
    # Saved Jobs
    path('saved-jobs/', views.saved_jobs, name='saved_jobs'),
    path('save-job/<uuid:pk>/', views.save_job, name='save_job'),
    path('unsave-job/<uuid:pk>/', views.unsave_job, name='unsave_job'),
]
