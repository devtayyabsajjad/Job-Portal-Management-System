"""
URL configuration for companies app
"""
from django.urls import path
from . import views

urlpatterns = [
    # Company Registration & Authentication
    path('register/', views.company_register, name='company_register'),
    path('login/', views.company_login, name='company_login'),
    
    # Company Dashboard
    path('dashboard/', views.company_dashboard, name='company_dashboard'),
    path('profile/', views.company_profile, name='company_profile'),
    path('profile/edit/', views.company_profile_edit, name='company_profile_edit'),
    
    # Job Management
    path('jobs/', views.company_job_list, name='company_job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<uuid:pk>/', views.job_detail_company, name='job_detail_company'),
    path('jobs/<uuid:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<uuid:pk>/delete/', views.job_delete, name='job_delete'),
    path('jobs/<uuid:pk>/toggle-status/', views.job_toggle_status, name='job_toggle_status'),
    
    # Application Management
    path('applications/', views.company_applications, name='company_applications'),
    path('applications/<uuid:pk>/', views.application_detail, name='application_detail'),
    path('applications/<uuid:pk>/update-status/', views.application_update_status, name='application_update_status'),
] 
