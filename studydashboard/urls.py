"""
URL configuration for studydashboard project.
"""
from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'status': 'ok',
        'message': 'Study Dashboard API is running!',
        'endpoints': {
            'api': '/api/',
            'admin': '/admin/',
        }
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
]
