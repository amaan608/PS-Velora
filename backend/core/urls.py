"""
URL configuration for core app API endpoints.
"""

from django.urls import path
from core import views

urlpatterns = [
    path('upload/', views.upload_files, name='upload_files'),
    path('optimize/', views.optimize, name='optimize'),
    path('results/', views.get_results, name='get_results'),
    path('health/', views.health_check, name='health_check'),
]
