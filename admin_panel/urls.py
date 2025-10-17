"""
URL configuration for admin panel
"""
from django.urls import path
from . import views

urlpatterns = [
    # Admin Dashboard
    path('', views.admin_dashboard, name='admin_dashboard'),
    
    # Company Management
    path('companies/', views.admin_company_list, name='admin_company_list'),
    path('companies/<uuid:pk>/', views.admin_company_detail, name='admin_company_detail'),
    path('companies/<uuid:pk>/approve/', views.admin_company_approve, name='admin_company_approve'),
    path('companies/<uuid:pk>/reject/', views.admin_company_reject, name='admin_company_reject'),
    path('companies/<uuid:pk>/delete/', views.admin_company_delete, name='admin_company_delete'),
    
    # Job Management
    path('jobs/', views.admin_job_list, name='admin_job_list'),
    path('jobs/<uuid:pk>/', views.admin_job_detail, name='admin_job_detail'),
    path('jobs/<uuid:pk>/deactivate/', views.admin_job_deactivate, name='admin_job_deactivate'),
    path('jobs/<uuid:pk>/delete/', views.admin_job_delete, name='admin_job_delete'),
    
    # User Management
    path('users/', views.admin_user_list, name='admin_user_list'),
    path('users/<uuid:pk>/toggle-status/', views.admin_user_toggle_status, name='admin_user_toggle_status'),
    
    # Statistics
    path('statistics/', views.admin_statistics, name='admin_statistics'),
] 
