"""
Minimal views to allow the project to start and render a home page,
plus basic error handlers that render existing templates.
"""

from django.shortcuts import render


def home(request):
    return render(request, 'home.html')


def custom_404(request, exception):
    return render(request, '404.html', status=404)


def custom_500(request):
    return render(request, '500.html', status=500)


