"""
Main URL Configuration for Job Portal Project
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
    path('django-admin/', admin.site.urls),

    # Main pages are handled by jobs app (home, job list, about, contact)
    path('', include('jobs.urls')),

    # Account management (login, register, profile, password reset)
    path('', include('accounts.urls')),

    # Company management (dashboard, jobs, applications)
    path('company/', include('companies.urls')),

    # Admin panel (company approval, job moderation, statistics)
    path('admin/', include('admin_panel.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Custom error handlers
handler404 = 'job_portal.views.custom_404'
handler500 = 'job_portal.views.custom_500'
