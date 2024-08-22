"""
This module contains the URL patterns for the filesharing app.

The urlpatterns variable is a list of URL patterns used by Django to route requests to the appropriate view functions.
"""

from django.urls import path
from . import views
#default django login and logout views were used since they provided all the security measures
#such as csrf tokens and password hashing out of the box
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.upload_file, name='upload_file'),
    path('share/', views.share_file, name='share_file'),
    path('download/<int:file_id>/', views.download_file, name='download_file'),
    path('delete_file/<int:file_id>/', views.delete_file, name='delete_file'),
    path('download/shared/<int:shared_file_id>/', views.download_shared_file, name='download_shared_file'),
    path('accounts/login/', auth_views.LoginView.as_view(), name='login'),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('signup/', views.signup_view, name='signup')
]

